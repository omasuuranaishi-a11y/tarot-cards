"""比較用も含めたチャートデータを計算し、lib/chart-data.js を書き出す。

    python data/make_chart_data.py

- nm：新月 2026-10-11 00:50 JST 東京（本編のチャート）
- fm：前回の満月 2026-09-27 01:49 JST 東京（承認済みチャートと分単位で一致することを確認済み）
- nmLondon：新月と同じ瞬間のロンドン（ハウスが場所で変わることの説明用）
"""
import json
import os

import swisseph as swe

swe.set_ephe_path(None)
FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED
KEYS = [("sun", swe.SUN), ("moon", swe.MOON), ("mercury", swe.MERCURY), ("venus", swe.VENUS),
        ("mars", swe.MARS), ("jupiter", swe.JUPITER), ("saturn", swe.SATURN),
        ("uranus", swe.URANUS), ("neptune", swe.NEPTUNE), ("pluto", swe.PLUTO)]
TOKYO = (35 + 42 / 60, 139 + 46 / 60)
LONDON = (51 + 30 / 60, -(7 / 60))


def chart(y, m, d, hour_ut, lat, lon, label):
    jd = swe.julday(y, m, d, hour_ut)
    bodies = {}
    for k, pid in KEYS:
        x, _ = swe.calc_ut(jd, pid, FLAGS)
        bodies[k] = {"lon": round(x[0], 6), "retro": x[3] < 0}
    cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    bodies["asc"] = {"lon": round(ascmc[0], 6), "retro": False}
    bodies["mc"] = {"lon": round(ascmc[1], 6), "retro": False}
    return {"label": label, "bodies": bodies, "cusps": [round(c, 6) for c in cusps]}


charts = {
    "nm": chart(2026, 10, 10, 15 + 50 / 60, *TOKYO, "新月 2026/10/11 00:50 JST 東京"),
    "fm": chart(2026, 9, 26, 16 + 49 / 60, *TOKYO, "満月 2026/9/27 01:49 JST 東京"),
    "nmLondon": chart(2026, 10, 10, 15 + 50 / 60, *LONDON, "新月と同じ瞬間 ロンドン"),
}
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(root, "lib", "chart-data.js"), "w", encoding="utf-8") as f:
    f.write("// data/make_chart_data.py で生成（Swiss Ephemeris の計算値）\n")
    f.write("window.CHARTS = " + json.dumps(charts, ensure_ascii=False, indent=1) + ";\n")
    f.write("window.CHART = window.CHARTS.nm;\n")
for k, c in charts.items():
    b = c["bodies"]
    print(k, "ASC", round(b["asc"]["lon"], 2), "MC", round(b["mc"]["lon"], 2), "Sun", round(b["sun"]["lon"], 2), "Moon", round(b["moon"]["lon"], 2))
