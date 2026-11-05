"""録音台本（md）から、スマホで読みやすいページ（html）を作る。スタイルは前回のページを使う。"""
import html, re, sys
src_md, style_from, out_path, title, h1, sub = sys.argv[1:7]
src = open(src_md).read()
style = re.search(r'<link rel="preconnect".*?</style>', open(style_from).read(), re.S).group(0)
table = {m.group(1): (m.group(3).strip(), m.group(4)) for m in
         re.finditer(r'^\| (\d\d) \| ([^|]+) \| ([^|]+) \| (\d:\d\d) \|', src, re.M)}
total = re.search(r'合計（([\d,]+)字） \| \| ([^|]+) \|', src)
how_items = re.findall(r'^\d\. (.*)$', re.search(r'## 録音のしかた\n(.*?)\n---', src, re.S).group(1), re.M)
def inline(t):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html.escape(t))
chap = re.split(r'^## (\d\d)｜(.*)$', src, flags=re.M)
chapters = []
for i in range(1, len(chap), 3):
    num, t, body = chap[i], chap[i + 1].strip(), chap[i + 2]
    main, _, pts = body.partition('**画面に出す要点**')
    blocks = []
    for para in [p.strip() for p in main.strip().split('\n\n') if p.strip() and p.strip() != '---']:
        if para.startswith('【アドリブ欄】'):
            blocks.append(f'<div class="adlib"><span class="adlib-tag">アドリブ</span><span>{inline(para[7:])}</span></div>')
        else:
            blocks.append('<p>' + '<br>'.join(inline(l) for l in para.split(chr(10))) + '</p>')
    chapters.append((num, t, *table[num], blocks, re.findall(r'^- (.*)$', pts, re.M)))
nav = ''.join(f'<a href="#c{n}"><span class="nav-num">{n}</span>{html.escape(re.split("[（：]", t)[0])}</a>' for n, t, *_ in chapters)
secs = []
for k, (n, t, page, dur, blocks, points) in enumerate(chapters):
    last = k == len(chapters) - 1
    pause = '<p class="pause end">おわり</p>' if last else '<p class="pause">ここで3秒あける（章ごとにファイルを分ける場合は不要）</p>'
    secs.append(f'''<section class="chapter" id="c{n}">
  <header class="ch-head"><span class="ch-num">{n}</span><div class="ch-title-wrap"><h2>{html.escape(t)}</h2>
  <p class="ch-meta"><span>映す画面：{html.escape(page)}</span><span>目安 {dur}</span></p></div></header>
  <div class="script">{''.join(blocks)}</div>
  <details class="points"><summary>画面に出す要点</summary><ul>{''.join(f"<li>{inline(p)}</li>" for p in points)}</ul></details>
  {pause}
</section>''')
out = f'''<title>{html.escape(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
{style}
<div class="wrap">
  <header class="top"><h1>{h1}</h1><p class="sub">{html.escape(sub)}</p>
  <span class="total">全{len(chapters)}章・{total.group(1)}字・{html.escape(total.group(2).strip())}</span></header>
  <details class="how"><summary>録音のしかた</summary><ol>{''.join(f"<li>{inline(x)}</li>" for x in how_items)}</ol>
  <p>テロップは、各章の「画面に出す要点」を表示します。話す言葉と一字一句そろえなくて大丈夫です。</p></details>
  <nav class="jump" aria-label="章へ移動">{nav}</nav>
  {''.join(secs)}
</div>
'''
open(out_path, 'w').write(out)
print(len(chapters), len(out))
