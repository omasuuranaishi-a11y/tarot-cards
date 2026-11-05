"""新月の図（東京・プラシーダス）を描く。注目する星に丸印、強調する角度に太い線をつけられる。"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "chart.json")))
GLYPH_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
JP_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

SIGN_GLYPHS = "♈♉♊♋♌♍♎♏♐♑♒♓"
PLANET_GLYPHS = {"sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀", "mars": "♂",
                 "jupiter": "♃", "saturn": "♄", "uranus": "♅", "neptune": "♆", "pluto": "♇"}
# 火・地・風・水
ELEMENT_FILL = [(251, 232, 226), (236, 240, 226), (247, 243, 222), (226, 238, 245)]
ELEMENT_INK = [(196, 92, 70), (110, 130, 70), (176, 140, 40), (60, 120, 170)]
INK = (62, 58, 72)
LINE = (190, 184, 200)
GOLD = (196, 150, 60)
ROSE = (214, 96, 128)
ASPECTS = [(60, (84, 140, 204)), (90, (214, 84, 84)), (120, (84, 140, 204)), (180, (214, 84, 84))]

SS = 2  # 描いてから縮小して、線をなめらかにする


def _font(path, size):
    return ImageFont.truetype(path, size, index=0) if path.endswith(".ttc") else ImageFont.truetype(path, size)


def _xy(cx, cy, r, lon):
    th = math.radians(180 + (lon - DATA["asc"]))
    return cx + r * math.cos(th), cy - r * math.sin(th)


def _spread(items, min_gap):
    """近すぎる星の表示位置を少しずらす（実際の度数はそのまま）。"""
    items = sorted(items, key=lambda x: x[1])
    pos = [lon for _, lon in items]
    for _ in range(50):
        moved = False
        for i in range(len(pos)):
            j = (i + 1) % len(pos)
            d = (pos[j] - pos[i]) % 360
            if d < min_gap:
                push = (min_gap - d) / 2
                pos[i] -= push
                pos[j] += push
                moved = True
        if not moved:
            break
    return {k: p for (k, _), p in zip(items, pos)}


def draw(size=820, highlight=(), lines=(), house_fill=None):
    """size: 直径。highlight: 丸をつける星のキー。lines: 強調する角度 [(星1, 星2)]。house_fill: 薄く塗るハウス番号"""
    S = size * SS
    pad = 70 * SS
    im = Image.new("RGBA", (S + pad * 2, S + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = S / 2 + pad
    R_out, R_sign, R_house, R_aspect = S / 2, S / 2 * 0.86, S / 2 * 0.56, S / 2 * 0.40
    R_p, R_label = S / 2 * 0.765, S / 2 * 0.645

    d.ellipse((cx - R_out, cy - R_out, cx + R_out, cy + R_out), fill=(255, 255, 255, 255))
    # 星座の帯
    for i in range(12):
        a0 = 180 + (i * 30 - DATA["asc"])
        d.pieslice((cx - R_out, cy - R_out, cx + R_out, cy + R_out), -(a0 + 30), -a0,
                   fill=ELEMENT_FILL[i % 4])
    d.ellipse((cx - R_sign, cy - R_sign, cx + R_sign, cy + R_sign), fill=(255, 255, 255, 255))
    # ハウスを薄く塗る
    cusps = DATA["cusps"]
    if house_fill:
        a = cusps[house_fill - 1]
        b = cusps[house_fill % 12]
        span = (b - a) % 360
        n = max(8, int(span))
        pts = [_xy(cx, cy, R_sign, a + span * k / n) for k in range(n + 1)]
        pts += [_xy(cx, cy, R_aspect, a + span * k / n) for k in range(n, -1, -1)]
        d.polygon(pts, fill=(250, 238, 214, 255))
        d.ellipse((cx - R_aspect, cy - R_aspect, cx + R_aspect, cy + R_aspect), fill=(255, 255, 255, 255))
    for r in (R_out, R_sign, R_house, R_aspect):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=LINE, width=2 * SS)
    gf = _font(GLYPH_FONT, int(S * 0.045))
    for i in range(12):
        x0, y0 = _xy(cx, cy, R_out, i * 30)
        x1, y1 = _xy(cx, cy, R_sign, i * 30)
        d.line((x0, y0, x1, y1), fill=LINE, width=2 * SS)
        gx, gy = _xy(cx, cy, (R_out + R_sign) / 2, i * 30 + 15)
        d.text((gx, gy), SIGN_GLYPHS[i], font=gf, fill=ELEMENT_INK[i % 4], anchor="mm")
    # ハウスの線と番号
    nf = _font(GLYPH_FONT, int(S * 0.026))
    for i, c in enumerate(cusps):
        x0, y0 = _xy(cx, cy, R_sign, c)
        x1, y1 = _xy(cx, cy, R_aspect, c)
        axis = i in (0, 3, 6, 9)
        d.line((x0, y0, x1, y1), fill=INK if axis else LINE, width=(4 if axis else 2) * SS)
        mid = c + ((cusps[(i + 1) % 12] - c) % 360) / 2
        hx, hy = _xy(cx, cy, (R_house + R_aspect) / 2, mid)
        d.text((hx, hy), str(i + 1), font=nf, fill=(150, 144, 160), anchor="mm")
    lf = _font(GLYPH_FONT, int(S * 0.028))
    for lon, label in ((DATA["asc"], "ASC"), (DATA["mc"], "MC")):
        x, y = _xy(cx, cy, R_out + 36 * SS, lon)
        d.text((x, y), label, font=lf, fill=INK, anchor="mm")

    planets = DATA["planets"]
    # 角度の線（オーブ6度まで。合は描かない）
    keys = list(planets)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            diff = abs((planets[a]["lon"] - planets[b]["lon"] + 180) % 360 - 180)
            for ang, col in ASPECTS:
                if abs(diff - ang) <= 6:
                    strong = (a, b) in lines or (b, a) in lines
                    xa, ya = _xy(cx, cy, R_aspect, planets[a]["lon"])
                    xb, yb = _xy(cx, cy, R_aspect, planets[b]["lon"])
                    if strong:
                        d.line((xa, ya, xb, yb), fill=col, width=10 * SS)
                    else:
                        c = tuple(int(v + (255 - v) * 0.55) for v in col)
                        d.line((xa, ya, xb, yb), fill=c, width=2 * SS)
    # 星
    disp = _spread([(k, p["lon"]) for k, p in planets.items()], 9)
    pf = _font(GLYPH_FONT, int(S * 0.055))
    df = _font(GLYPH_FONT, int(S * 0.022))
    for k, p in planets.items():
        # 実際の位置に小さな目盛り
        tx0, ty0 = _xy(cx, cy, R_sign, p["lon"])
        tx1, ty1 = _xy(cx, cy, R_sign - 12 * SS, p["lon"])
        d.line((tx0, ty0, tx1, ty1), fill=INK, width=3 * SS)
        x, y = _xy(cx, cy, R_p, disp[k])
        if k in highlight:
            rr = S * 0.045
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 241, 214), outline=GOLD, width=7 * SS)
        d.text((x, y), PLANET_GLYPHS[k], font=pf, fill=ROSE if k in highlight else INK, anchor="mm")
        deg = p["lon"] % 30
        t = round(deg * 60)
        label = f"{t // 60}°{t % 60:02d}′" + (" R" if p["retro"] else "")
        lx, ly = _xy(cx, cy, R_label, disp[k])
        d.text((lx, ly), label, font=df, fill=(120, 114, 130), anchor="mm")
    return im.resize(((S + pad * 2) // SS, (S + pad * 2) // SS), Image.LANCZOS)


if __name__ == "__main__":
    draw(highlight=("venus", "mars", "jupiter"), lines=[("venus", "mars")], house_fill=7).save(
        os.path.join(HERE, "chart_test.png"))
