"""2026年10月11日 天秤座新月のチャート計算（東京・トロピカル・プラシーダス）

    pip install pyswisseph
    python calc_chart.py            # 表を表示し、chart.json を書き出す

- 暦：Swiss Ephemeris（pyswisseph、組み込みのMoshier暦）
- 場所：東京 北緯35°42′ 東経139°46′。満月チャート（9/27 01:49）の承認済みの値を
  この座標で分単位まで再現できることを確認済み（ASC 獅子座16°48′、MC 牡牛座9°55′）
- 表示：分は四捨五入（astro.com などの一般的な表示に合わせる。2026-10-03 にご本人の指定で切り捨てから変更）
"""
import itertools
import json
import os

import swisseph as swe

swe.set_ephe_path(None)
FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED
SIGNS = ["牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
         "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"]
LAT, LON = 35 + 42 / 60, 139 + 46 / 60
JD = swe.julday(2026, 10, 10, 15 + 50 / 60)  # UT。日本時間 2026-10-11 00:50

PLANETS = [("太陽", swe.SUN), ("月", swe.MOON), ("水星", swe.MERCURY), ("金星", swe.VENUS),
           ("火星", swe.MARS), ("木星", swe.JUPITER), ("土星", swe.SATURN),
           ("天王星", swe.URANUS), ("海王星", swe.NEPTUNE), ("冥王星", swe.PLUTO)]
ASPECTS = [(0, "合"), (60, "セクスタイル"), (90, "スクエア"), (120, "トライン"), (180, "オポジション")]


def dm(x):
    """度と分（分は四捨五入）"""
    t = round(x * 60)
    return t // 60, t % 60


def fmt(lon):
    t = round((lon % 360) * 60) % (360 * 60)  # 四捨五入で 30° に届いたら次のサインにする
    return f"{SIGNS[t // 1800]}{t % 1800 // 60}°{t % 60:02d}′"


def fmt_orb(x):
    d, m = dm(abs(x))
    return f"{d}°{m:02d}′"


cusps, ascmc = swe.houses(JD, LAT, LON, b"P")


def house(lon):
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360 < (b - a) % 360:
            return i + 1


pos = {}
for name, pid in PLANETS:
    x, _ = swe.calc_ut(JD, pid, FLAGS)
    pos[name] = {"lon": x[0], "speed": x[3]}
pos["ASC"] = {"lon": ascmc[0], "speed": 0}
pos["MC"] = {"lon": ascmc[1], "speed": 0}

print("== 天体")
for name, p in pos.items():
    lon = p["lon"]
    if name in ("ASC", "MC"):
        print(f"{name}\t{fmt(lon)}\t数え{int(lon % 30) + 1}度")
        continue
    h = house(lon)
    to_next = (cusps[h % 12] - lon) % 360
    p["house"] = h
    print(f"{name}\t{fmt(lon)}\t{h}H\t{'R' if p['speed'] < 0 else ''}\t"
          f"数え{int(lon % 30) + 1}度\t次のカスプまで{fmt_orb(to_next)}")

print("== カスプ")
for i, c in enumerate(cusps):
    print(i + 1, fmt(c))

print("== アスペクト（オーブ6°以内）")
rows = []
for a, b in itertools.combinations(pos, 2):
    if {a, b} == {"ASC", "MC"}:
        continue
    la, lb = pos[a]["lon"], pos[b]["lon"]
    d = abs((la - lb + 180) % 360 - 180)
    for ang, nm in ASPECTS:
        orb = abs(d - ang)
        if orb <= 6:
            # 0.01日後の角度で接近／分離を判定
            la2 = la + pos[a]["speed"] * 0.01
            lb2 = lb + pos[b]["speed"] * 0.01
            d2 = abs((la2 - lb2 + 180) % 360 - 180)
            rows.append((orb, a, b, nm, ang, d, "接近" if abs(d2 - ang) < orb else "分離"))
for orb, a, b, nm, ang, d, app in sorted(rows):
    print(f"{a}-{b}\t{nm}{ang}°\t実角度{fmt_orb(d)}\tオーブ{fmt_orb(orb)}\t{app}")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chart.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump({"datetime_jst": "2026-10-11T00:50", "lat": LAT, "lon": LON, "house_system": "Placidus",
               "bodies": pos, "cusps": list(cusps)}, f, ensure_ascii=False, indent=1)
