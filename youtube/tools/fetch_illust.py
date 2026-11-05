"""新月動画 v2 のイラスト（いらすとや 18点＋使っていない1点）を取得して illust/ に置く。

    python3 youtube/tools/fetch_illust.py youtube/newmoon-20261109/illust

一覧は illust/sources.json（名前・題・ページ・画像のURL）。
いらすとやの規約：商用は1つの制作物につき20点まで（同じ絵の重複は1点）、クレジット不要、素材の再配布は禁止。
そのため画像は GitHub に入れない（.gitignore 済み）。このスクリプトで取り直す。
ネットワークの許可に www.irasutoya.com と blogger.googleusercontent.com が必要。
"""
import json
import os
import sys
import urllib.request

out = sys.argv[1]
src = json.load(open(os.path.join(out, "sources.json")))
for name, p in src.items():
    path = os.path.join(out, name + ".png")
    if os.path.exists(path):
        continue
    req = urllib.request.Request(p["img"], headers={"User-Agent": "Mozilla/5.0"})
    open(path, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    print("取得", name, p["title"])
print("ok", len(src), "点")
