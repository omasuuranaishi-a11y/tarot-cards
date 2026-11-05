"""録音（章ごとのファイル、または1本）から、本番の動画を作る。

1. 録音をつなぎ、音量をそろえる
2. 文字起こし（ReazonSpeech、文字ごとの時刻つき）
3. 台本のテロップ1枚ずつを、文字起こしのどこに当たるか対応づけて、声の時刻に合わせる
   読み直しや言いかえ、アドリブがあっても、合っている部分を手がかりにする
4. 仮の動画と同じ画面で、声に合わせて書き出す

使い方: python3 build_final.py 出力.mp4 録音1 [録音2 ...]
"""
import difflib
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_draft as bd  # noqa: E402

# 文字起こしのモデル（約700MB、GitHub には入れない）。HANDOFF.md の手順で youtube/asr_model/ に置く
ASR_MODEL = os.environ.get("ASR_MODEL", os.path.join(HERE, "..", "asr_model",
                                                     "sherpa-onnx-zipformer-ja-reazonspeech-2024-08-01"))
TRANSCRIBE = os.path.join(HERE, "..", "tools", "transcribe.py")
SR = 48000
LEAD = 0.5

DIGITS = "〇一二三四五六七八九"


def kanji_num(n):
    """123 → 百二十三（文字起こしの書き方にそろえる）"""
    if n == 0:
        return "〇"
    out = ""
    for unit, name in ((1000, "千"), (100, "百"), (10, "十")):
        q, n = divmod(n, unit)
        if q:
            out += ("" if q == 1 else DIGITS[q]) + name
    return out + (DIGITS[n] if n else "")


def norm(text):
    text = re.sub(r"\d+", lambda m: kanji_num(int(m.group())) if len(m.group()) < 5 else m.group(), text)
    return re.sub(r"[、。，．・「」『』（）()？！?!\s〜～：:／/＝=ー―…]", "", text)


def prepare(paths, out_wav):
    """録音をつないで48kHzモノラルにし、音量をそろえる。ファイルの境目も返す。"""
    parts, bounds, t = [], [], 0.0
    for p in paths:
        tmp = out_wav + ".part.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p, "-ac", "1", "-ar", str(SR),
                        "-af", "highpass=f=80,afftdn=nf=-25", tmp], check=True)
        with wave.open(tmp) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        parts += [x, np.zeros(int(0.8 * SR), np.float32)]
        bounds.append(t)
        t += len(x) / SR + 0.8
        os.remove(tmp)
    joined = os.path.join(os.path.dirname(out_wav), "joined_raw.wav")
    _write(joined, np.concatenate(parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined,
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), out_wav], check=True)
    with wave.open(out_wav) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x, bounds


def _write(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def transcribe(wav48, work):
    w16 = os.path.join(work, "rec16k.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav48, "-ac", "1", "-ar", "16000", w16], check=True)
    out = os.path.join(work, "transcript.json")
    with open(os.path.join(work, "transcript.txt"), "w") as f:
        subprocess.run([sys.executable, "-I", TRANSCRIBE, ASR_MODEL, w16, out], check=True, stdout=f,
                       stderr=subprocess.DEVNULL)
    return json.load(open(out))


def char_stream(chunks):
    """文字起こしを、1文字ずつ（正規化後）の時刻の列にする。"""
    chars, times = [], []
    for c in chunks:
        ts = list(c["times"])
        # 区間の最初の文字には、実際より前の時刻がつくことがある（その間の言葉は拾えていない）
        if len(ts) > 1 and ts[1] - ts[0] > 0.8:
            ts[0] = ts[1] - 0.15
        for tok, t in zip(c["tokens"], ts):
            for ch in norm(tok):
                chars.append(ch)
                times.append(t)
    return "".join(chars), times


def align(units, asr_text, asr_times, lead_time=0.0):
    """台本の各テロップが、録音のいつに当たるかを決める。
    台本と文字起こしで一致した所の時刻を手がかりにし、その間は時刻の上で比例で割り振る
    （文字起こしで拾えなかった言葉があっても、その時間に文が入るようにするため）。"""
    script = "".join(norm(u["text"]) for u in units)
    sm = difflib.SequenceMatcher(None, script, asr_text, autojunk=False)
    # 一致した区間の中で時刻が1秒以上飛ぶ所は区切る（抜けた言葉をまたいで偶然一致していることがある）。
    # 3文字未満のかけら（「です」など）は、離れた所と偶然一致しやすいので使わない
    Block = difflib.Match
    blocks = []
    for b in sm.get_matching_blocks():
        k0 = 0
        for k in range(1, b.size + 1):
            if k == b.size or asr_times[b.b + k] - asr_times[b.b + k - 1] > 1.0:
                if k - k0 >= 3:
                    blocks.append(Block(b.a + k0, b.b + k0, k - k0))
                k0 = k
    sp, tp = [0.0], [lead_time]
    for b in blocks:
        sp += [b.a + 1e-3, b.a + b.size - 1e-3]
        tp += [asr_times[b.b], asr_times[b.b + b.size - 1] + 0.18]
    sp.append(len(script) + 1e-3)
    tp.append(max(asr_times[-1] + 0.5, tp[-1]))
    tp = list(np.maximum.accumulate(tp))
    order = np.argsort(sp, kind="stable")
    sp, tp = [sp[k] for k in order], [tp[k] for k in order]

    def to_time(i):
        return float(np.interp(i, sp, tp))

    pos = 0
    for u in units:
        n = len(norm(u["text"]))
        matched = sum(max(0, min(b.a + b.size, pos + n) - max(b.a, pos)) for b in blocks)
        u["start"], u["end"] = to_time(pos), to_time(pos + n) + 0.25
        u["match"] = round(matched / max(1, n), 2)
        pos += n
    return units


SPOKEN = 0.2  # 台本と一致した文字の割合がこれ未満なら、読まれなかった文とみなす


def speech_mask(audio):
    """20ミリ秒ごとに、声が入っているかどうか。"""
    hop = SR // 50
    n = len(audio) // hop
    db = 20 * np.log10(np.sqrt((audio[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    fl, vo = np.percentile(db, 10), np.percentile(db, 95)
    return db > fl + (vo - fl) * 0.3


def mark_spoken(units, audio):
    """文字起こしで拾えなかっただけの文を、読まれた文として扱い直す。
    その時間に声が入っていて、長さも文に見合っていれば、読まれたとみなす。"""
    loud = speech_mask(audio)
    for u in units:
        if u["match"] >= SPOKEN:
            continue
        a, b = int(u["start"] * 50), int(u["end"] * 50)
        speech = loud[a:b].mean() if b > a else 0
        expected = len(norm(u["text"])) / 5.5
        if speech >= 0.4 and (u["end"] - u["start"]) >= 0.4 * expected:
            u["match"] = max(u["match"], SPOKEN)
            u["asr_missed"] = True


def take_from_neighbor(units, audio):
    """読まれなかったと判定された文でも、となりの文の時間が長すぎるときは、
    文字起こしがひとまとめにしただけとみなして、その時間を分けてもらう。"""
    for i, u in enumerate(units):
        if u["match"] >= SPOKEN:
            continue
        need = len(norm(u["text"])) / 5.5
        for j, at_start in ((i + 1, True), (i - 1, False)):
            if not 0 <= j < len(units) or units[j]["match"] < SPOKEN:
                continue
            v = units[j]
            have = v["end"] - v["start"]
            v_need = len(norm(v["text"])) / 5.5
            if u["end"] - u["start"] < 0.5 and have >= 1.5 * v_need and have - v_need >= 0.7 * need:
                if at_start:
                    u["start"], u["end"] = v["start"], v["start"] + need * 1.1
                    v["start"] = u["end"] + 0.1
                else:
                    u["start"], u["end"] = v["end"] - need * 1.1, v["end"]
                    v["end"] = u["start"] - 0.1
                u["match"] = SPOKEN
                u["asr_missed"] = True
                break


def snap_to_onsets(units, audio):
    """文字起こしとの一致が弱い文は、前の文が終わったあとの、声の出だしに合わせる。"""
    loud = speech_mask(audio)
    onsets = [k / 50 for k in range(15, len(loud)) if loud[k] and not loud[k - 15:k].any()]
    prev_end = 0.0
    for i, u in enumerate(units):
        if u["match"] < SPOKEN:
            continue
        nxt = next((v["start"] for v in units[i + 1:] if v["match"] >= SPOKEN), 1e9)
        if u["match"] < 0.6:
            cand = [o for o in onsets if max(u["start"] - 1.2, prev_end - 0.1) <= o <= min(u["start"] + 3.5, nxt - 1.0)]
            if cand:
                shift = cand[0] - u["start"]
                u["start"] += shift
                u["end"] = max(u["end"] + shift, u["start"] + 1.2)
        prev_end = u["end"] - 0.25


def fix_timing(units, total):
    """読まれなかった文は表示せず、時刻は次に読まれた文にそろえる（要点の出るタイミング用）。
    読まれた文は、重ならないように整え、短すぎるものは少し延ばす。"""
    spoken = [u for u in units if u["match"] >= SPOKEN]
    for i, u in enumerate(units):
        u["hidden"] = u["match"] < SPOKEN
        if u["hidden"]:
            nxt = next((v for v in units[i + 1:] if v["match"] >= SPOKEN), None)
            u["start"] = u["end"] = nxt["start"] if nxt else total
    for i, u in enumerate(spoken):
        nxt = spoken[i + 1]["start"] if i + 1 < len(spoken) else total
        u["end"] = min(max(u["end"], u["start"] + 1.2), nxt - 0.05)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_path, rec = args[0], args[1:]
    work = os.path.join(HERE, "final_work")
    os.makedirs(work, exist_ok=True)
    voice = os.path.join(work, "voice.wav")
    audio, _ = prepare(rec, voice)
    cached = os.path.join(work, "transcript.json")
    chunks = json.load(open(cached)) if "--reuse" in sys.argv and os.path.exists(cached) else transcribe(voice, work)
    asr_text, asr_times = char_stream(chunks)

    script = bd.parse_script()
    chapters, units, _ = bd.schedule(script)
    loud = speech_mask(audio)
    first_voice = float(np.argmax(loud)) / 50
    units = align(units, asr_text, asr_times, lead_time=first_voice)
    mark_spoken(units, audio)
    take_from_neighbor(units, audio)
    snap_to_onsets(units, audio)
    total = len(audio) / SR + bd.END_HOLD
    fix_timing(units, total)

    # 冒頭のタイトル（4秒）のぶん、声を後ろへずらす
    shift = bd.OPENING
    for u in units:
        u["start"] += shift
        u["end"] += shift
    audio = np.concatenate([np.zeros(int(shift * SR), np.float32), audio,
                            np.zeros(int(bd.END_HOLD * SR), np.float32)])
    _write(voice + ".final.wav", audio)
    total = len(audio) / SR

    # 自動で決めきれなかった文は、音声を見て時刻を手で指定する（動画の時刻。冒頭のタイトル込み）
    overrides = json.load(open(os.path.join(HERE, "overrides.json"))) if os.path.exists(
        os.path.join(HERE, "overrides.json")) else {}
    for i, u in enumerate(units):
        if u["text"] in overrides:
            u["start"], u["end"] = overrides[u["text"]]
            u["hidden"] = False
            u["match"] = max(u["match"], SPOKEN)
            if i + 1 < len(units) and units[i + 1]["start"] < u["end"] + 0.05:
                units[i + 1]["start"] = u["end"] + 0.1

    # 章の区切り：その章の最初のテロップの少し前に、章タイトル（2.4秒）を重ねて出す
    for k, c in enumerate(chapters):
        first = next((u for u in units if u["chapter"] == c["num"] and not u["hidden"]),
                     next(u for u in units if u["chapter"] == c["num"]))
        c["start"] = shift if k == 0 else first["start"] - bd.TITLE_CARD - 0.2
    for k, c in enumerate(chapters):
        c["end"] = chapters[k + 1]["start"] if k + 1 < len(chapters) else total
    bd.build_timeline(chapters, units)

    with open(os.path.join(work, "テロップの時刻.txt"), "w") as f:
        for u in units:
            flag = ("　← 読まれなかった文（表示しない）" if u["hidden"] else
                    "　← 文字起こしで抜けていたが、声は入っている" if u.get("asr_missed") else
                    ("" if u["match"] >= 0.6 else "　← 要確認"))
            f.write(f"{u['start']:7.2f}-{u['end']:7.2f}  一致{u['match']:.0%}  {u['text']}{flag}\n")
    weak = [u for u in units if SPOKEN <= u["match"] < 0.6]
    print(f"テロップ {len(units)}枚、表示しない {sum(u['hidden'] for u in units)}枚、要確認 {len(weak)}枚")

    json.dump(dict(units=units, chapters=[{k: c[k] for k in ("num", "title", "start", "end")} for c in chapters],
                   total=total), open(os.path.join(work, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    if "--plan" in sys.argv:
        return
    levels = mouth(audio, int(total * bd.FPS))
    bd.render(chapters, [u for u in units if not u["hidden"]], total, out_path,
              audio_path=voice + ".final.wav", levels=levels, draft=False)


def mouth(audio, nframes):
    hop = SR // bd.FPS
    lv = np.array([np.sqrt(np.mean(audio[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(audio) else 0
                   for i in range(nframes)])
    lv = np.clip(lv / max(1e-6, np.percentile(lv[lv > 0], 95)), 0, 1)
    for i in range(1, nframes):
        lv[i] = max(lv[i], lv[i - 1] * 0.55)
    return lv


if __name__ == "__main__":
    main()
