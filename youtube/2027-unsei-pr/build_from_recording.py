"""収録した音声から、テロップとページを合わせた動画を作る。

使い方: python3 build_from_recording.py 録音ファイル [出力ファイル]

録音は台本の文を順番に読み、文と文のあいだに1秒ほど間をあけたもの。
無音の区切りと各文の文字数から、どこからどこまでがどの文かを推定する。
"""
import os
import re
import subprocess
import sys
import wave

import numpy as np

from build_video import SCENES, SR, TAIL
from build_video_wipe import HERE, render

LEAD = 0.6          # 最初の声までの間
SILENCE_MIN = 0.35  # この長さ以上の無音を区切りの候補にする


def prepare(src, dst):
    """モノラル48kHzにし、低音のノイズを切って音量をそろえる。"""
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(SR),
         "-af", "highpass=f=80,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11", dst],
        check=True)
    with wave.open(dst) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return x.astype(np.float32) / 32768


def speech_segments(audio):
    """声のある区間を探す。無音の基準は、録音ごとの雑音と声の大きさから決める。"""
    hop = SR // 50  # 20ミリ秒ごと
    n = len(audio) // hop
    frames = audio[:n * hop].reshape(n, hop)
    db = 20 * np.log10(np.sqrt(np.mean(frames ** 2, axis=1)) + 1e-9)
    floor, voice = np.percentile(db, 10), np.percentile(db, 95)
    th = floor + (voice - floor) * 0.3
    loud = db > th
    segs, i = [], 0
    min_gap = int(SILENCE_MIN * 50)
    while i < n:
        if not loud[i]:
            i += 1
            continue
        j = i
        quiet = 0
        while j < n and quiet < min_gap:
            quiet = quiet + 1 if not loud[j] else 0
            j += 1
        segs.append([i / 50, (j - quiet) / 50])
        i = j
    # 息やクリックのような短すぎる音は捨てる
    return [s for s in segs if s[1] - s[0] >= 0.25]


def split_longest(segs, audio):
    """区切りが文の数より少ないとき、いちばん長い区間をいちばん静かな所で分ける。"""
    i = max(range(len(segs)), key=lambda k: segs[k][1] - segs[k][0])
    a, b = segs[i]
    lo, hi = int((a + (b - a) * 0.3) * SR), int((a + (b - a) * 0.7) * SR)
    hop = SR // 50
    rms = [np.sqrt(np.mean(audio[j:j + hop] ** 2)) for j in range(lo, hi - hop, hop)]
    cut = (lo + int(np.argmin(rms)) * hop) / SR
    segs[i:i + 1] = [[a, cut], [cut, b]]


def align(segs, chars):
    """各文に連続した区間を割り当てる。文字数から見込んだ長さに近くなるように選ぶ。"""
    n, m = len(chars), len(segs)
    total = sum(b - a for a, b in segs)
    rate = total / sum(chars)
    inf = float("inf")
    cost = np.full((n + 1, m + 1), inf)
    back = np.zeros((n + 1, m + 1), dtype=int)
    cost[0][0] = 0
    for i in range(1, n + 1):
        for j in range(i, m - (n - i) + 1):
            for k in range(i - 1, j):
                if cost[i - 1][k] == inf:
                    continue
                d = segs[j - 1][1] - segs[k][0]
                c = cost[i - 1][k] + ((d - chars[i - 1] * rate) / (chars[i - 1] * rate)) ** 2
                if c < cost[i][j]:
                    cost[i][j], back[i][j] = c, k
    spans, j = [], m
    for i in range(n, 0, -1):
        k = back[i][j]
        spans.append((segs[k][0], segs[j - 1][1]))
        j = k
    return spans[::-1]


def main():
    src = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        HERE, "2027年運勢鑑定_紹介動画_収録音声版.mp4")
    work = os.path.join(HERE, "out", "recording.wav")
    raw = prepare(src, work)
    dur = len(raw) / SR

    lines = [(si, sub) for si, (_, _, ls) in enumerate(SCENES) for sub, _ in ls]
    chars = [len(re.sub(r"[、。「」（）\s]", "", sub)) for _, sub in lines]
    segs = speech_segments(raw)
    if not segs:
        sys.exit("声が見つかりませんでした。録音の音量を確認してください。")
    while len(segs) < len(lines):
        split_longest(segs, raw)
    spans = align(segs, chars)

    # 最初の声の前と、最後の声のあとの間をそろえる
    offset = max(0.0, spans[0][0] - LEAD)
    end = min(dur, spans[-1][1] + 0.3)
    audio = np.concatenate([raw[int(offset * SR):int(end * SR)],
                            np.zeros(int(TAIL * SR), np.float32)])
    spans = [(a - offset, b - offset) for a, b in spans]
    voice = os.path.join(HERE, "out", "recording_trimmed.wav")
    with wave.open(voice, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())

    subs = [(a, b, sub) for (a, b), (_, sub) in zip(spans, lines)]
    total = len(audio) / SR
    scene_times = []
    for si, (page, label, _) in enumerate(SCENES):
        idx = [k for k, (s, _) in enumerate(lines) if s == si]
        t0 = 0.0 if si == 0 else spans[idx[0]][0] - 0.3
        scene_times.append([t0, None, page, label])
    for si in range(len(scene_times)):
        scene_times[si][1] = scene_times[si + 1][0] if si + 1 < len(scene_times) else total

    report = os.path.join(HERE, "out", "テロップの時刻.txt")
    with open(report, "w") as f:
        for k, (a, b, sub) in enumerate(subs, 1):
            f.write(f"{k:2d}  {a:6.2f} - {b:6.2f}  {sub}\n")
    print(open(report).read())

    render(voice, audio, subs, [tuple(s) for s in scene_times], out_path)


if __name__ == "__main__":
    main()
