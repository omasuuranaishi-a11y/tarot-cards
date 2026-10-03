"""02_録音台本.md から、スマホで読みやすい録音用の台本（大きな文字・1文1行・章ごとに改ページ）を作る。

    python tools/make_teleprompter.py          # recording/台本_録音用.html
    node tools/html2pdf.mjs recording/台本_録音用.html recording/台本_録音用.pdf
"""
import html
import os
import re

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(root, '02_録音台本.md'), encoding='utf-8').read()
chs = re.findall(r'^## (\d\d)｜([^\n]*)\n(.*?)(?=^## |\Z)', src, re.S | re.M)

out = []
for no, title, body in chs:
    paras = [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip() and not p.strip().startswith('---')]
    n = len(re.sub(r'\s', '', ''.join(paras)))
    blocks = []
    for p in paras:
        lines = [s for s in re.split(r'(?<=。)', p.replace('\n', '')) if s.strip()]
        blocks.append('<div class="p">' + ''.join(f'<div class="s">{html.escape(s)}</div>' for s in lines) + '</div>')
    out.append(f'<section><div class="no">第{int(no)}章 ／ ファイル名「{no}」</div><h2>{html.escape(title)}</h2>'
               f'<div class="meta">{n}字 ・ 目安 {n / 330:.1f}分</div>{"".join(blocks)}'
               f'<div class="end">― 第{int(no)}章 おわり ―</div></section>')

page = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>録音用の台本</title>
<style>
@page {{ size: A5; margin: 12mm 11mm; }}
body {{ margin: 0; font-family: "IPAPGothic", "Hiragino Sans", "Noto Sans JP", sans-serif; color: #222; background: #fff; }}
.cover {{ page-break-after: always; padding-top: 10mm; }}
.cover h1 {{ font-size: 24pt; margin: 0 0 6mm; }} .cover p, .cover li {{ font-size: 12.5pt; line-height: 1.75; }}
section {{ page-break-before: always; }}
.no {{ font-size: 11pt; color: #8a5a9e; }} h2 {{ font-size: 19pt; margin: 1mm 0 1mm; line-height: 1.4; }}
.meta {{ font-size: 10pt; color: #888; margin-bottom: 5mm; }}
.p {{ margin: 0 0 6mm; }} .s {{ font-size: 17pt; line-height: 1.7; margin: 0 0 1.5mm; }}
.end {{ text-align: center; color: #999; font-size: 11pt; margin-top: 6mm; }}
</style></head><body>
<div class="cover"><h1>録音用の台本</h1>
<p>2026年10月11日 天秤座新月の解説 ／ 全13章・7,345字</p>
<ul>
<li>中身は <b>02_録音台本.md</b> と同じです（1文ごとに改行しています）。</li>
<li><b>章ごとに1つのファイル</b>で録音してください。ファイル名は章の番号（01〜13）にします。</li>
<li>段落の間（行が空いているところ）は <b>1〜2秒</b> あけてください。</li>
<li>読み間違えたら、止めずに <b>その文の頭から</b> 読み直してください。後の読み直しのほうを使います。</li>
<li>動画に合わせる必要はありません。自然なペースで読んでください。画面の動きはあとで声に合わせます。</li>
</ul></div>
{"".join(out)}
</body></html>'''
os.makedirs(os.path.join(root, 'recording'), exist_ok=True)
open(os.path.join(root, 'recording', '台本_録音用.html'), 'w', encoding='utf-8').write(page)
print(len(chs), 'chapters')
