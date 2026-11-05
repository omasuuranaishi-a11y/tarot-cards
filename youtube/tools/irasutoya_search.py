"""いらすとやを検索して、記事の題・ページ・画像のURL（大きいサイズ）を並べる。"""
import html, json, os, re, sys, urllib.parse, urllib.request
OUT = sys.argv[1]
db = json.load(open(OUT)) if os.path.exists(OUT) else {}
for q in sys.argv[2:]:
    url = "https://www.irasutoya.com/search?q=" + urllib.parse.quote(q) + "&max-results=16"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    posts = []
    for m in re.finditer(r'<a href="(https://www\.irasutoya\.com/\d{4}/\d\d/[^"]+\.html)"[^>]*>\s*<script[^>]*>\s*document\.write\(bp_thumbnail_resize\("([^"]+)","([^"]*)"', body):
        page, img, title = m.group(1), m.group(2), html.unescape(m.group(3))
        posts.append(dict(title=title, page=page, img=img.replace("/s72-c/", "/s800/")))
    if not posts:  # 形が違うときは、画像と題だけ拾う
        for m in re.finditer(r'bp_thumbnail_resize\("([^"]+)","([^"]*)"', body):
            posts.append(dict(title=html.unescape(m.group(2)), page="", img=m.group(1).replace("/s72-c/", "/s800/")))
    db[q] = posts
    print(f"== {q} ({len(posts)})")
    for p in posts[:10]:
        print("  ", p["title"], "|", p["page"].replace("https://www.irasutoya.com", ""))
json.dump(db, open(OUT, "w"), ensure_ascii=False, indent=1)
