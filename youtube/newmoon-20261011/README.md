# 2026年10月11日 天秤座新月｜解説動画 v1（無音・仮タイミング）

星よみ専門家 おます の新月解説動画です。制作の基準は「満月の解説動画の指示書」と同じにしています。
**音声はまだありません。見本動画は無音・仮タイミングで、音声同期済みの完成版ではありません。**

## ファイル

| ファイル | 内容 |
|---|---|
| `01_チャートデータと出典.md` | 天体の位置、ハウス、アスペクトとオーブ、支配星、逆行の日時、サビアン、出典、検証方法 |
| `02_録音台本.md` | 13章・約7,300字（毎分330字で約22分）。読む本文だけ |
| `03_編集表.md` | 全編の場面ごとの「読む内容／絵／動き／注目対象／長さ」。見本の範囲は実際の時刻つき |
| `04_素材出典と利用条件.md` | 使った素材、利用条件、未検証の項目 |
| `sample/newmoon-sample-v1.mp4` | 第5章冒頭〜第6章の見本（3:59、1920×1080、30fps、無音） |
| `sample/sample.html` | 見本の作り。ブラウザで開くと再生できる（`?t=秒` で止めて表示） |
| `chart/newmoon-chart.png` | 新月のチャート（2000×2000、計算値から作図、承認前） |
| `thumbnail/thumbnail.png` | サムネイル案（1280×720） |
| `lib/` | チャートの作図（`chart.js`）、計算値（`chart-data.js`）、色と文字（`style.css`） |
| `data/calc_chart.py` | チャートの計算（Swiss Ephemeris）→ `data/chart.json` |
| `tools/render.mjs` | HTMLを静止画・MP4に書き出す（Playwright＋FFmpeg） |

## 書き出し方

```
pip install pyswisseph
python data/calc_chart.py          # 値を変えたとき。lib/chart-data.js は chart.json から作り直す
npm install playwright
node tools/render.mjs still chart/chart.html chart/newmoon-chart.png 2000 2000
node tools/render.mjs still thumbnail/thumbnail.html thumbnail/thumbnail.png 1280 720
node tools/render.mjs video sample/sample.html sample/newmoon-sample-v1.mp4 1920 1080 30
```

- Windowsでは、`FFMPEG` にffmpegのパスを指定します。
- Google Fontsに接続できない環境では、`LOCAL_FONTS` に `@fontsource` のフォルダを指定します。

## 録音後の合わせ方

1. `sample/sample.html` の `UNITS` は、単位ごとに読む文を持っています。各単位の長さを、録音した音声の長さに置き換えます。画面の動きは、各文の開始時刻（`SS(単位, 文)`）に合わせてあるので、一緒に動きます。
2. ワイプの仮アイコンを本人のアイコンに差し替え、口の動きと瞬きを音声に合わせます（録音後）。
3. 全編のデコード、尺、最後のコマ、章の位置を確認してから渡します。
