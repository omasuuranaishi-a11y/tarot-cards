"""録音を区間に分けて文字起こしし、区間と文字ごとの時刻を JSON に書く。"""
import json, sys, wave
import numpy as np
import sherpa_onnx

model_dir, wav_path, out_path = sys.argv[1:4]
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{model_dir}/encoder-epoch-99-avg-1.onnx",
    decoder=f"{model_dir}/decoder-epoch-99-avg-1.onnx",
    joiner=f"{model_dir}/joiner-epoch-99-avg-1.onnx",
    tokens=f"{model_dir}/tokens.txt", num_threads=4, decoding_method="greedy_search")
w = wave.open(wav_path); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
hop = sr // 50; n = len(x) // hop
db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
fl, vo = np.percentile(db, 10), np.percentile(db, 95); loud = db > fl + (vo - fl) * 0.3
# 0.3秒以上の無音で区切り、長い区間は15秒までにまとめる
segs, i = [], 0
while i < n:
    if not loud[i]: i += 1; continue
    j, q = i, 0
    while j < n and q < 15:
        q = q + 1 if not loud[j] else 0; j += 1
    segs.append([max(0, i - 10), min(n, j - q + 10)]); i = j
MAXF = 500  # 1区間は10秒まで。長い区間は、なるべく静かな所で切る
def split(a, b):
    if b - a <= MAXF:
        return [[a, b]]
    lo, hi = a + (b - a) // 3, a + 2 * (b - a) // 3
    cut = lo + int(np.argmin(db[lo:hi]))
    return split(a, cut) + split(cut, b)
chunks = []
for a, b in segs:
    for c in split(a, b):
        if chunks and c[1] - chunks[-1][0] <= MAXF and c[0] - chunks[-1][1] < 40:
            chunks[-1][1] = c[1]
        else:
            chunks.append(c)
out = []
for a, b in chunks:
    s = rec.create_stream(); s.accept_waveform(sr, x[a * hop:b * hop]); rec.decode_stream(s)
    r = s.result
    out.append({"start": a / 50, "end": b / 50, "text": r.text,
                "tokens": list(r.tokens), "times": [a / 50 + t for t in r.timestamps]})
    print(f"{a/50:7.1f}-{b/50:7.1f} {r.text}", flush=True)
json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=1)
