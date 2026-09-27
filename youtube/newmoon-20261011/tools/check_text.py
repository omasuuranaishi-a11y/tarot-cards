"""full/chapters.js の読む文が、02_録音台本.md と一字一句同じかを確かめる。

    python tools/check_text.py
"""
import os
import re
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script = open(os.path.join(root, "02_録音台本.md"), encoding="utf-8").read()
js = open(os.path.join(root, "full", "chapters.js"), encoding="utf-8").read()

chapters = {}
for m in re.finditer(r"^## (\d\d)｜[^\n]*\n(.*?)(?=^## |\Z)", script, re.S | re.M):
    chapters[m.group(1)] = re.sub(r"\s", "", m.group(2))

ok = True
parts = re.split(r"ch\('(\d\d)'", js)[1:]
for i in range(0, len(parts), 2):
    no, body = parts[i], parts[i + 1]
    units = re.findall(r"\{ text: '([^']*)', pad", body)
    joined = re.sub(r"\s", "", "".join(units))
    if joined != chapters.get(no):
        ok = False
        a, b = joined, chapters.get(no, "")
        k = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        print(f"{no}: 不一致 at {k}\n  定義: …{a[max(0,k-20):k+30]}\n  台本: …{b[max(0,k-20):k+30]}")
    else:
        print(f"{no}: OK（{len(units)}単位、{len(joined)}字）")
sys.exit(0 if ok else 1)
