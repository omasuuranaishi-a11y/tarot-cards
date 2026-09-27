# 2026年10月11日 天秤座新月｜解説動画 v1（無音・仮タイミング）

星よみ専門家 おます の新月解説動画です。制作の基準は「満月の解説動画の指示書」と同じにしています。
**音声はまだありません。見本動画は無音・仮タイミングで、音声同期済みの完成版ではありません。**

## ファイル

| ファイル | 内容 |
|---|---|
| `01_チャートデータと出典.md` | 天体の位置、ハウス、アスペクトとオーブ、支配星、逆行の日時、サビアン、出典、検証方法 |
| `02_録音台本.md` | 13章・約7,300字（毎分330字で約22分）。読む本文だけ |
| `03_編集表.md` | 全編 v1 の94場面ごとの「時刻／長さ／画面／注目対象／動き／読む文」 |
| `04_素材出典と利用条件.md` | 使った素材、利用条件、未検証の項目 |
| `full/newmoon-full-v1.mp4` | **全編の仮編集**（約25分30秒、1920×1080、30fps、無音・仮タイミング） |
| `full/review.html` | 全編レビュー。動画と、章ごと・場面ごとの読む文を並べて確認できる |
| `full/index.html`、`full/chapters.js` | 全編の作り。`chapters.js` に13章・94場面の読む文と画面の動きがある |
| `full/timeline.json` | 場面ごとの時刻（`review.html` と `03_編集表.md` の元データ） |
| `sample/newmoon-sample-v1.mp4` | 第5章冒頭〜第6章の最初の見本（3:59）。全編 v1 に置き換わった |
| `sample/sample.html` | 見本の作り。ブラウザで開くと再生できる（`?t=秒` で止めて表示） |
| `chart/newmoon-chart.png` | 新月のチャート（2000×2000、計算値から作図、承認前） |
| `thumbnail/thumbnail.png` | サムネイル案（1280×720） |
| `lib/` | チャートの作図（`chart.js`）、計算値（`chart-data.js`）、全編の仕組み（`engine.js`）、挿絵・図解（`scenes.js`）、色と文字（`style.css`） |
| `data/calc_chart.py`、`data/make_chart_data.py` | チャートの計算（Swiss Ephemeris）。新月・前回の満月・同じ瞬間のロンドンの図の値を `lib/chart-data.js` に書き出す |
| `tools/check_text.py` | `chapters.js` の読む文が `02_録音台本.md` と一字一句同じか確かめる |
| `tools/export_units.mjs`、`tools/make_review.py`、`tools/make_edit_table.py` | `full/timeline.json` を書き出し、`review.html` と `03_編集表.md` を作り直す |
| `tools/render.mjs` | HTMLを静止画・MP4に書き出す（Playwright＋FFmpeg） |

## 書き出し方

```
pip install pyswisseph
python data/calc_chart.py          # 新月の表と data/chart.json
python data/make_chart_data.py     # lib/chart-data.js（新月・前回の満月・ロンドン）
npm install playwright
node tools/render.mjs still chart/chart.html chart/newmoon-chart.png 2000 2000
node tools/render.mjs still thumbnail/thumbnail.html thumbnail/thumbnail.png 1280 720
node tools/render.mjs video sample/sample.html sample/newmoon-sample-v1.mp4 1920 1080 30
# 全編（開始秒・終了秒で区切って並行に書き出し、ffmpeg の concat でつなぐ）
CRF=21 node tools/render.mjs video full/index.html full/part0.mp4 1920 1080 30 0 401.9
```

- Windowsでは、`FFMPEG` にffmpegのパスを指定します。
- Google Fontsに接続できない環境では、`LOCAL_FONTS` に `@fontsource` のフォルダを指定します。

## 録音後の合わせ方

1. `full/chapters.js` は、場面（単位）ごとに読む文を持っています。各単位の長さを録音した音声の長さに置き換えます。画面の動きは、各文の開始時刻（`T.s(k)`）に結びつけてあるので、一緒に動きます。
2. ワイプの仮アイコンを本人のアイコンに差し替え、口の動きと瞬きを音声に合わせます（録音後）。
3. 全編のデコード、尺、最後のコマ、章の位置を確認してから渡します。
