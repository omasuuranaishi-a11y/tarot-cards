# 2026年10月11日 天秤座新月｜解説動画 v2（無音・仮タイミング）

星よみ専門家 おます の新月解説動画です。制作の基準は「満月の解説動画の指示書」と同じにしています。
**音声はまだありません。見本動画は無音・仮タイミングで、音声同期済みの完成版ではありません。**

いまの版は **全編 v2**（`full-v2/`）です。v1（`full/`）は残してあります。v2 は、参考動画の分析（`reference/参考動画の分析.md`）をもとに、字幕・章タイトル・冒頭と締めの画面・チャートの印を直した版です。

## ファイル

| ファイル | 内容 |
|---|---|
| `01_チャートデータと出典.md` | 天体の位置、ハウス、アスペクトとオーブ、支配星、逆行の日時、サビアン、出典、検証方法 |
| `02_録音台本.md` | 13章・約7,300字（毎分330字で約22分）。読む本文だけ |
| `03_編集表.md` | 全編 v2 の94場面ごとの「時刻／長さ／画面／注目対象／動き／読む文」と、v2 で変えたこと・章タイトルの時刻 |
| `04_素材出典と利用条件.md` | 使った素材、利用条件、未検証の項目 |
| `full-v2/newmoon-full-v2.mp4` | **全編の仮編集 v2**（約26分01秒、1920×1080、30fps、無音・仮タイミング） |
| `full-v2/review.html` | 全編 v2 のレビュー。動画と、章ごと・場面ごとの読む文を並べて確認できる |
| `full-v2/index.html`、`full-v2/v2.js`、`full-v2/full.css` | v2 の作り。読む文と画面の動きは v1 と同じ `full/chapters.js` を使い、`v2.js` で冒頭と締めの画面を差し替え、`full.css` で字幕などを変えている |
| `full-v2/timeline.json` | v2 の場面ごとの時刻（`review.html` と `03_編集表.md` の元データ） |
| `reference/参考動画の分析.md` | 参考動画（Maya Arikaの覚醒channel ほか）の分析と、取り入れる点。別のセッションでストーリーボード・自動字幕・メタデータから確かめた |
| `full/newmoon-full-v1.mp4` | 全編の仮編集 v1（約25分30秒）。v2 の前の版として残している |
| `full/review.html` | 全編 v1 のレビュー |
| `full/index.html`、`full/chapters.js` | 全編 v1 の作り。`chapters.js` に13章・94場面の読む文と画面の動きがある（v2 も同じものを使う） |
| `full/timeline.json` | v1 の場面ごとの時刻 |
| `sample/newmoon-sample-v1.mp4` | 第5章冒頭〜第6章の最初の見本（3:59）。全編 v1 に置き換わった |
| `sample/sample.html` | 見本の作り。ブラウザで開くと再生できる（`?t=秒` で止めて表示） |
| `chart/newmoon-chart.png` | 新月のチャート（2000×2000、計算値から作図、承認前） |
| `thumbnail/thumbnail.png` | サムネイル案（1280×720） |
| `lib/` | チャートの作図（`chart.js`）、計算値（`chart-data.js`）、全編の仕組み（`engine.js`。v2 の字幕・章タイトル・印は `E.opts` で切り替え、指定しなければ v1 と同じ動き）、挿絵・図解（`scenes.js`）、色と文字（`style.css`） |
| `data/calc_chart.py`、`data/make_chart_data.py` | チャートの計算（Swiss Ephemeris）。新月・前回の満月・同じ瞬間のロンドンの図の値を `lib/chart-data.js` に書き出す |
| `tools/check_text.py` | `chapters.js` の読む文が `02_録音台本.md` と一字一句同じか確かめる |
| `tools/export_units.mjs`、`tools/make_review.py`、`tools/make_edit_table.py` | `timeline.json` を書き出し、`review.html` と `03_編集表.md` を作り直す（版のフォルダを引数で渡す） |
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
# 全編 v2（開始秒・終了秒で区切って並行に書き出し、ffmpeg の concat でつなぐ）
CRF=21 node tools/render.mjs video full-v2/index.html full-v2/part0.mp4 1920 1080 30 0 390.3667
# 場面の表・レビューの作り直し
node tools/export_units.mjs full-v2/index.html full-v2/timeline.json
python tools/make_review.py full-v2
python tools/make_edit_table.py full-v2
python tools/check_text.py         # 読む文が録音台本と一字一句同じか
```

- Windowsでは、`FFMPEG` にffmpegのパスを指定します。
- Google Fontsに接続できない環境では、`LOCAL_FONTS` に `@fontsource` のフォルダを指定します。

## 録音後の合わせ方

1. `full/chapters.js` は、場面（単位）ごとに読む文を持っています（v1・v2 共通）。各単位の長さを録音した音声の長さに置き換えます。v2 の章タイトル（2.6秒）は、録音の章の間に合わせて長さを変えられます（`full-v2/index.html` の `card`）。画面の動きは、各文の開始時刻（`T.s(k)`）に結びつけてあるので、一緒に動きます。
2. ワイプはご本人のアイコン（`lib/icon.png`）で、口の開き方はいまは読む文の時刻に合わせた仮です。録音後は、音声の大きさで口を動かします（`lib/engine.js` の「口」の部分）。
3. 全編のデコード、尺、最後のコマ、章の位置を確認してから渡します。
