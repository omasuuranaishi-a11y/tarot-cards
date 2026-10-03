"""本人の録音（ナレーション）から、全編 v4 の時刻・口の動き・音声トラックを作る。

録音は narration/ に置く（GitHub には入れない）。章ごとに 01.m4a 〜 13.m4a が基本だが、
何本に分かれていても、ファイル名の順に読んだものとしてつなげて扱う（1本にまとめた録音でもよい）。

    python tools/build_narration.py stt              # 1. 文字起こし（fal の ElevenLabs、言葉ごとの時刻つき。結果は narration/stt/ に保存）
    python tools/build_narration.py align            # 2. 台本の各文が録音のどこかを決める → full-v4/narration.js と narration/clips.json
    node tools/export_layout.mjs                     # 3. v4 のページから、各文を置く時刻を書き出す → narration/layout.json
    python tools/build_narration.py mix              # 4. 各文を置いた音声 narration/narration.wav と、口の開き full-v4/mouth.js
    （全編を tools/render.mjs で書き出してから）
    python tools/build_narration.py mux <映像.mp4> <出力.mp4>   # 5. 音を整えて（約 −16 LUFS）重ね、AAC にする

読み間違えて読み直した文は、後の読み直し（最後に読んだほう）を使う。
文の間は録音の間を 0.25〜0.9 秒に収めて使い、単位の終わりの「図を見せる間」（pad）と章タイトル（2.6 秒）は v3 と同じ。
"""
import base64
import glob
import json
import os
import re
import subprocess
import sys
import unicodedata

import numpy as np

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAR = os.environ.get('NARRATION_DIR') or os.path.join(root, 'narration')
SR = 16000      # 対応づけ（無音の判定）に使う。軽くて十分
SR_MIX = 48000  # 音声トラック（mix）はこちら。録音の音質を落とさない
sys.path.insert(0, os.path.join(root, 'tools'))


# ---------- 台本の文（engine.js と同じ切り方） ----------
def script_units():
    js = open(os.path.join(root, 'full', 'chapters.js'), encoding='utf-8').read()
    parts = re.split(r"ch\('(\d\d)'", js)[1:]
    units = []
    for i in range(0, len(parts), 2):
        for k, text in enumerate(re.findall(r"\{ text: '([^']*)', pad", parts[i + 1])):
            units.append({'id': f'{parts[i]}-{k + 1}', 'sent': [s for s in re.split(r'(?<=。)', text) if s.strip()]})
    return units


# ---------- 文字のそろえ方（表記ゆれを吸収してから比べる） ----------
KJ = '〇一二三四五六七八九'


def kanji_num(n):
    if n == 0:
        return '零'
    s = ''
    for v, u in ((1000, '千'), (100, '百'), (10, '十')):
        q, n = divmod(n, v)
        if q:
            s += ('' if q == 1 else KJ[q]) + u
    return s + (KJ[n] if n else '')


# 英字の略語は、カタカナで書き起こされても同じになるように英字にそろえる
ABBR = {'えーえすしー': 'asc', 'えむしー': 'mc', 'あいしー': 'ic', 'てぃー': 't'}
SKIP = set(' \u3000、。，．,.!！?？「」『』（）()・：:―ー-〜')


def norm_seq(chars):
    """文字の並びをそろえる。返り値は（そろえた文字, 元の最初の位置, 元の最後の位置）の並び（時刻を引き継ぐため）。"""
    c = [unicodedata.normalize('NFKC', x).lower() for x in chars]
    c = [''.join(chr(ord(y) - 0x60) if 'ァ' <= y <= 'ヶ' else y for y in x) for x in c]  # カタカナ → ひらがな
    c = [x.replace('°', '度').replace('′', '分') for x in c]
    out, i = [], 0
    while i < len(c):
        if c[i].isdigit():
            j = i
            while j < len(c) and c[j].isdigit():
                j += 1
            out += [(y, i, j - 1) for y in kanji_num(int(''.join(c[i:j])))]
            i = j; continue
        rest = ''.join(c[i:i + 8])
        k = next((k for k in ABBR if rest.startswith(k)), None)
        if k:
            out += [(y, i, i + len(k) - 1) for y in ABBR[k]]; i += len(k); continue
        out += [(y, i, i) for y in c[i] if y not in SKIP]
        i += 1
    return out


def norm(s):
    return ''.join(x[0] for x in norm_seq(list(s)))


# ---------- 録音 ----------
def recordings():
    fs = sorted(f for f in glob.glob(os.path.join(NAR, '*')) if os.path.isfile(f)
                and re.search(r'\.(m4a|mp3|wav|aac|caf|flac|ogg|mp4|mov)$', f, re.I))
    if not fs:
        sys.exit('narration/ に録音がありません')
    return fs


def load(f, sr=SR):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def stt():
    import fal_client as F
    os.makedirs(os.path.join(NAR, 'stt'), exist_ok=True)
    for f in recordings():
        out = os.path.join(NAR, 'stt', os.path.basename(f) + '.json')
        if os.path.exists(out):
            print('済み', os.path.basename(f)); continue
        # 送る前に 16kHz・モノラルの小さい m4a にする（文字起こしには十分）
        tmp = os.path.join(NAR, 'stt', '_send.m4a')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-ac', '1', '-ar', '16000', '-c:a', 'aac', '-b:a', '48k', tmp], check=True)
        r = F.run('fal-ai/elevenlabs/speech-to-text', {'audio_url': F.data_uri(tmp), 'language_code': 'jpn',
                                                         'diarize': False, 'tag_audio_events': True}, limit=1800)
        os.remove(tmp)
        json.dump(r, open(out, 'w'), ensure_ascii=False)
        print('文字起こし', os.path.basename(f), len(r.get('words', [])), '語')


# ---------- 台本と録音の対応 ----------
def stream():
    """全録音の文字起こしを1本の文字列にし、各文字の（ファイル番号, 開始, 終了）を持つ。"""
    raw, inf = [], []
    for fi, f in enumerate(recordings()):
        for x in json.load(open(os.path.join(NAR, 'stt', os.path.basename(f) + '.json')))['words']:
            if x['type'] != 'word':
                continue
            for c in x['text']:
                raw.append(c); inf.append((fi, x['start'], x['end']))
    seq = norm_seq(raw)
    # 数字や略語をまとめて置き換えた文字は、まとめた範囲の最初から最後までの時刻を持つ
    return ''.join(c for c, _, _ in seq), [(inf[i][0], inf[i][1], inf[j][2]) for _, i, j in seq]


def best_match(pat, text, c0, W):
    """text[c0:c0+W] の中で pat に近い部分（編集距離）を探す。よい候補のうち、いちばん後ろのもの（読み直し）を返す。"""
    T = text[c0:c0 + W]
    n, m = len(pat), len(T)
    prev = np.zeros(m + 1, np.int32); start = np.arange(m + 1, dtype=np.int32)
    for i in range(1, n + 1):
        cur = np.empty(m + 1, np.int32); cs = np.empty(m + 1, np.int32)
        cur[0] = i; cs[0] = 0
        for j in range(1, m + 1):
            a = prev[j - 1] + (pat[i - 1] != T[j - 1]); b = prev[j] + 1; c = cur[j - 1] + 1
            if a <= b and a <= c:
                cur[j] = a; cs[j] = start[j - 1]
            elif b <= c:
                cur[j] = b; cs[j] = start[j]
            else:
                cur[j] = c; cs[j] = cs[j - 1]
        prev, start = cur, cs
    best = int(prev[1:].min())
    # 前後より小さい（その位置で終わるのがいちばん合う）ところだけを候補にする
    ok = [j for j in range(1, m + 1) if prev[j] <= best + max(1, n // 12) and prev[j] <= prev[j - 1] and (j == m or prev[j] < prev[j + 1])]
    j = max(ok)
    return c0 + int(start[j]), c0 + j, int(prev[j])


def refine(x, a, b, pre=.12, post=.28):
    """文字起こしの時刻を、音の大きさで整える（頭と尻の無音を詰め、語尾の減衰は残す）。"""
    fr = int(SR * .01)
    A, B = max(0, int((a - pre) * SR)), min(len(x), int((b + post) * SR))
    seg = x[A:B]
    if len(seg) < fr * 3:
        return a, b
    rms = np.sqrt(np.convolve(seg ** 2, np.ones(fr) / fr, 'same'))
    th = max(rms.max() * .04, np.percentile(np.sqrt(np.convolve(x ** 2, np.ones(fr) / fr, 'same')), 20) * 2.5)
    on = np.nonzero(rms > th)[0]
    if not len(on):
        return a, b
    s = (A + max(0, on[0] - int(.04 * SR))) / SR
    e = (A + min(len(seg), on[-1] + int(.08 * SR))) / SR
    return min(s, a), max(e, min(b, e + .3))


def align():
    U = script_units()
    text, info = stream()
    X = [load(f) for f in recordings()]
    clips, c0, worst = [], 0, []
    for u in U:
        for k, s in enumerate(u['sent']):
            p = norm(s)
            i, j, d = best_match(p, text, c0, 3 * len(p) + 150)
            fi = info[i][0]
            a, b = info[i][1], info[j - 1][2]
            if info[j - 1][0] != fi:  # ファイルの境目をまたいだら、前のファイルで終える
                j2 = max(q for q in range(i, j) if info[q][0] == fi) + 1; b = info[j2 - 1][2]
            a, b = refine(X[fi], a, b)
            score = 1 - d / max(1, len(p))
            clips.append({'unit': u['id'], 'k': k, 'text': s, 'file': os.path.basename(recordings()[fi]), 'fi': fi,
                          'a': round(a, 3), 'b': round(b, 3), 'score': round(score, 3), 'heard': text[i:j]})
            if score < .85:
                worst.append(clips[-1])
            c0 = j
    os.makedirs(NAR, exist_ok=True)
    json.dump(clips, open(os.path.join(NAR, 'clips.json'), 'w'), ensure_ascii=False, indent=1)
    # v4 のページに渡す：各文の長さと、同じ単位の中の文と文の間
    units, q = [], 0
    for u in U:
        cs = clips[q:q + len(u['sent'])]; q += len(u['sent'])
        g = []
        for x, y in zip(cs, cs[1:]):
            gap = y['a'] - x['b'] if x['fi'] == y['fi'] and 0 <= y['a'] - x['b'] < 2.5 else .45
            g.append(round(min(.9, max(.25, gap)), 3))
        units.append({'d': [round(c['b'] - c['a'], 3) for c in cs], 'g': g})
    with open(os.path.join(root, 'full-v4', 'narration.js'), 'w', encoding='utf-8') as f:
        f.write('/* 全編 v4 の実測の時刻（tools/build_narration.py align が作る）。声そのものは含まない。\n'
                '   d：各文の長さ（秒）、g：同じ単位の中の文と文の間（秒）。単位は full/chapters.js の順。 */\n')
        f.write('window.NARRATION = ' + json.dumps({'card': 2.6, 'units': units}, ensure_ascii=False) + ';\n')
    print(f'{len(clips)}文を対応づけました。合計 {sum(c["b"] - c["a"] for c in clips) / 60:.1f}分')
    for c in worst:
        print(f'  要確認 {c["unit"]} 文{c["k"] + 1}（一致 {c["score"]:.0%}）：{c["text"][:30]} ／ 聞こえ：{c["heard"][:30]}')


# ---------- 音声トラックと口 ----------
def mix():
    clips = json.load(open(os.path.join(NAR, 'clips.json')))
    lay = json.load(open(os.path.join(NAR, 'layout.json')))
    X, R = {}, SR_MIX
    out = np.zeros(int((lay['duration'] + 1) * R), np.float32)
    starts = [s for u in lay['units'] for s in u['ss']]
    assert len(starts) == len(clips), '文の数が合いません'
    for c, t in zip(clips, starts):
        if c['fi'] not in X:
            X[c['fi']] = load(os.path.join(NAR, c['file']), R)
        seg = X[c['fi']][int(c['a'] * R):int(c['b'] * R)].copy()
        f = min(len(seg), int(.015 * R))  # つなぎ目のプチッを防ぐ
        if f:
            seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        p = int(t * R); out[p:p + len(seg)] += seg
    out = out[:int(lay['duration'] * R)]
    wav = os.path.join(NAR, 'narration.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(R), '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le', wav],
                   input=out.tobytes(), check=True)
    # 口の開き：30fps ごとの音の大きさ（dB）を 0〜255 に。開くのは速く、閉じるのはゆっくり
    fps, hop = 30, R // 30
    n = len(out) // hop
    db = 20 * np.log10(np.sqrt((out[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-6)
    top = np.percentile(db[db > -60], 95) if (db > -60).any() else -20
    v = np.clip((db - (top - 30)) / 26, 0, 1)
    sm = np.zeros_like(v)
    for i in range(1, n):
        sm[i] = v[i] if v[i] > sm[i - 1] else sm[i - 1] * .55 + v[i] * .45
    data = (np.clip(sm, 0, 1) * 255).astype(np.uint8)
    with open(os.path.join(root, 'full-v4', 'mouth.js'), 'w') as f:
        f.write('/* 口の開き（tools/build_narration.py mix が作る。声から作るので GitHub には入れない） */\n')
        f.write(f'window.MOUTH = {{ fps: {fps}, b64: "{base64.b64encode(data.tobytes()).decode()}" }};\n')
    print('narration.wav', round(len(out) / R, 2), '秒（48kHz）、mouth.js', n, 'コマ')


def mux(video, out):
    wav = os.path.join(NAR, 'narration.wav')
    pre = 'highpass=f=80,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=2:attack=10:release=150:makeup=2'
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', wav, '-af', pre + ',loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-af', pre + ',' + ln + ',aresample=48000', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                    '-shortest', '-movflags', '+faststart', out], check=True)
    print('できました', out)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'stt': stt()
    elif cmd == 'align': align()
    elif cmd == 'mix': mix()
    elif cmd == 'mux': mux(sys.argv[2], sys.argv[3])
    else: print(__doc__)
