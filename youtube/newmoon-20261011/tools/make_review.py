"""full/timeline.json から、動画と台本を並べて確認するページ full/review.html を作る。

    python tools/make_review.py
"""
import html
import json
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(root, "full", "timeline.json"), encoding="utf-8"))


def mmss(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


total = data[-1]["end"]
nav = "".join(f'<button data-time="{c["start"]:.2f}">{c["no"]}　{mmss(c["start"])}</button>' for c in data)
secs = []
for c in data:
    rows = "".join(
        f'<tr><td><a href="#" data-time="{u["start"]:.2f}">{mmss(u["start"])}</a></td>'
        f'<td class="sc">{html.escape(u["scene"])}</td><td>{html.escape(u["text"])}</td></tr>'
        for u in c["units"])
    secs.append(f'<section id="ch{c["no"]}"><h2><span>{c["no"]}</span>{html.escape(c["title"])}'
                f'<small>{mmss(c["start"])}〜{mmss(c["end"])}・{len(c["units"])}場面</small></h2>'
                f'<table><thead><tr><th>時刻</th><th>画面</th><th>読む文</th></tr></thead><tbody>{rows}</tbody></table></section>')

page = f"""<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>天秤座新月 全編レビュー</title>
<style>
body{{margin:0;background:#17151e;color:#f7f3ec;font-family:'Noto Sans JP',Meiryo,sans-serif;line-height:1.8}}
main{{max-width:1180px;margin:auto;padding:32px}}h1{{font-family:'Noto Serif JP',serif;font-weight:600;font-size:30px;margin:0 0 6px}}
p.lead{{color:#c7c0cc;margin:0 0 18px}}video{{width:100%;background:#000;border:1px solid #3a3040}}
nav{{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 8px;position:sticky;top:0;background:#17151e;padding:10px 0;z-index:2}}
button{{border:1px solid #76644c;color:#e0caa3;background:#29222f;padding:8px 14px;cursor:pointer;font-size:14px}}
section{{border-top:1px solid #504353;padding:18px 0}}h2{{font-family:'Noto Serif JP',serif;font-weight:600;font-size:22px;margin:0 0 10px}}
h2 span{{color:#BB965B;margin-right:12px}}h2 small{{font-family:sans-serif;font-size:13px;color:#a79fb0;margin-left:14px;font-weight:400}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border-bottom:1px solid #2e2733;padding:6px 8px;vertical-align:top;text-align:left}}
th{{color:#a79fb0;font-weight:500}}td:first-child{{white-space:nowrap}}td.sc{{color:#BB965B;white-space:nowrap}}a{{color:#dfc799}}
@media(max-width:650px){{main{{padding:16px}}td.sc{{white-space:normal}}}}
</style>
<main>
<h1>2026年10月11日 天秤座新月　全編 v1</h1>
<p class="lead">全編の仮編集｜約{mmss(total)}・無音・仮タイミング。章ボタンや各場面の時刻で移動できます。
字幕は読む文の仮表示です。録音後に、単位ごとの長さを実際の音声に合わせて組み直します。</p>
<video id="film" controls preload="metadata" src="newmoon-full-v1.mp4"></video>
<nav>{nav}</nav>
{''.join(secs)}
</main>
<script>
const v=document.getElementById('film');
document.querySelectorAll('[data-time]').forEach(b=>b.addEventListener('click',e=>{{e.preventDefault();v.currentTime=+b.dataset.time;v.play();v.scrollIntoView({{behavior:'smooth',block:'center'}});}}));
</script>
</html>
"""
open(os.path.join(root, "full", "review.html"), "w", encoding="utf-8").write(page)
print("ok", len(page))
