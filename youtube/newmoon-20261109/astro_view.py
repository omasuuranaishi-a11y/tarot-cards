"""おますさんの astro.com の新月チャートの上に、丸印・矢印・拡大・ハウスの塗り・角度の線を重ねる。

座標は元画像（1350×1465）のピクセル。星の記号の位置は画像で測った値。
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = Image.open(os.path.join(HERE, "astro", "chart_astro.jpg")).convert("RGB")
DATA = json.load(open(os.path.join(HERE, "chart.json")))
BGC = (255, 254, 233)
CX, CY = 665, 777          # 円の中心
R_INNER, R_ZODIAC = 270, 575  # 角度の線の円 / 星座の帯の内側
HALF = 665                 # 全体を映すときの半分の幅

# 星の記号の位置（画像で測った値）
POINTS = {
    "sun": (1158, 640), "moon": (1162, 690), "mercury": (1188, 752), "venus": (1175, 885),
    "mars": (808, 1288), "jupiter": (866, 1268), "saturn": (198, 535), "neptune": (232, 487),
    "uranus": (198, 1020), "pluto": (690, 258), "asc": (52, 777), "mc": (800, 232),
    "scorpio": (1275, 777), "sextile": (832, 932),
    "sun_moon": (1160, 665), "venus_mercury": (1180, 818), "mars_jupiter": (838, 1278),
    "sextile_view": (990, 1080), "asc_view": (260, 777),
}

# 上に重ねて、拡大していないときも少し大きく見せるための補正
SANS_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
RING = (232, 150, 40)
ARROW = (220, 64, 104)
HOUSE = (255, 196, 90)

PADDED = Image.new("RGB", (SRC.width + 1400, SRC.height + 1400), BGC)
_clean = SRC.copy()
ImageDraw.Draw(_clean).rectangle((0, 0, 230, 225), fill=BGC)  # 左上の日時の文字（右の見出しに出すので消す）
PADDED.paste(_clean, (700, 700))
OFF = 700


def lon_xy(lon, r):
    th = math.radians(180 + (lon - DATA["asc"]))
    return CX + r * math.cos(th), CY - r * math.sin(th)


def resolve(p):
    return POINTS[p] if isinstance(p, str) else p


def font(size):
    return ImageFont.truetype(SANS_B, size, index=0)


def view(size, cam, focus, pulse=0.0):
    """size: 出力の一辺。cam: (中心x, 中心y, 拡大率)。focus: 重ねるもの。pulse: 0〜1（丸の脈打ち）"""
    cx, cy, z = cam
    h = HALF / z
    box = (int(cx - h + OFF), int(cy - h + OFF), int(cx + h + OFF), int(cy + h + OFF))
    im = PADDED.crop(box).resize((size, size), Image.LANCZOS).convert("RGBA")
    s = size / (box[2] - box[0])

    def sc(p):
        x, y = p
        return ((x + OFF - box[0]) * s, (y + OFF - box[1]) * s)

    over = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    # ハウスを塗る
    if focus.get("house"):
        n = focus["house"]
        cusps = DATA["cusps"]
        a, b = cusps[n - 1], cusps[n % 12]
        span = (b - a) % 360
        k = max(10, int(span))
        pts = [sc(lon_xy(a + span * i / k, R_ZODIAC)) for i in range(k + 1)]
        pts += [sc(lon_xy(a + span * i / k, R_INNER)) for i in range(k, -1, -1)]
        d.polygon(pts, fill=HOUSE + (90,), outline=HOUSE + (255,))
        d.line(pts + [pts[0]], fill=(230, 150, 40, 255), width=max(3, int(4 * s)))
    # 角度の線
    for p1, p2, label, (ldx, ldy) in focus.get("lines", []):
        a = sc(lon_xy(DATA["planets"][p1]["lon"], R_INNER))
        b = sc(lon_xy(DATA["planets"][p2]["lon"], R_INNER))
        d.line((a, b), fill=(84, 140, 230, 120), width=max(16, int(26 * s)))
        d.line((a, b), fill=(40, 100, 220, 255), width=max(7, int(10 * s)))
        if label:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            _label(d, (mx + ldx * s / 0.647, my + ldy * s / 0.647), label, size, anchor="mm")
    # 丸印（少し脈打つ）
    rr = max(28, 34 * s) * (1 + 0.06 * math.sin(pulse * 2 * math.pi))
    for p in focus.get("circles", []):
        x, y = sc(resolve(p))
        d.ellipse((x - rr - 6, y - rr - 6, x + rr + 6, y + rr + 6), outline=(255, 220, 150, 140), width=10)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=RING + (255,), width=7)
    # 矢印と説明
    for p, text, (dx, dy) in focus.get("arrows", []):
        tx, ty = sc(resolve(p))
        lx, ly = tx + dx, ty + dy
        lx = min(max(lx, 20), size - 20)
        ly = min(max(ly, 40), size - 40)
        box_ = _label(d, (lx, ly), text, size, anchor="mm")
        # 説明の箱の端から、丸の手前まで矢印
        bx = min(max(tx, box_[0]), box_[2])
        by = min(max(ty, box_[1]), box_[3])
        ang = math.atan2(ty - by, tx - bx)
        ex, ey = tx - math.cos(ang) * (rr + 10), ty - math.sin(ang) * (rr + 10)
        d.line((bx, by, ex, ey), fill=ARROW + (255,), width=8)
        hl = 30
        p1 = (ex - hl * math.cos(ang - 0.45), ey - hl * math.sin(ang - 0.45))
        p2 = (ex - hl * math.cos(ang + 0.45), ey - hl * math.sin(ang + 0.45))
        d.polygon([(ex + 6 * math.cos(ang), ey + 6 * math.sin(ang)), p1, p2], fill=ARROW + (255,))
    im = Image.alpha_composite(im, over)
    return im.convert("RGB")


def _label(d, pos, text, size, anchor="mm"):
    f = font(34)
    lines = text.split("\n")
    w = max(d.textlength(l, font=f) for l in lines) + 40
    h = 48 * len(lines) + 20
    x, y = pos
    if anchor == "mm":
        x0, y0 = x - w / 2, y - h / 2
    else:
        x0, y0 = x, y - h / 2
    x0 = min(max(x0, 10), size - w - 10)
    y0 = min(max(y0, 10), size - h - 10)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 16, fill=(255, 255, 255, 240), outline=ARROW + (255,), width=4)
    for i, l in enumerate(lines):
        d.text((x0 + w / 2, y0 + 10 + 48 * i + 24), l, font=f, fill=(60, 40, 60), anchor="mm")
    return (x0, y0, x0 + w, y0 + h)


FULL = (CX, CY, 1.0)


def cam_for(spec):
    if not spec:
        return FULL
    p, z = spec
    x, y = resolve(p)
    return (x, y, z)


if __name__ == "__main__":
    tests = [
        (cam_for(("sun_moon", 2.0)), dict(circles=["sun", "moon"], arrows=[("sun_moon", "太陽と月\n蠍座16°53′", (-330, -150))])),
        (FULL, dict(house=7, circles=["sun", "moon"], arrows=[("sun_moon", "第7ハウス", (-260, -250))])),
        (FULL, dict(circles=["venus", "mars"], lines=[("venus", "mars", "60°（ずれ0°38′）", (-230, -40))])),
        (cam_for(("mars_jupiter", 2.0)), dict(circles=["mars", "jupiter"], arrows=[("mars_jupiter", "火星と木星\n獅子座で重なる", (-300, -260))])),
    ]
    sheet = Image.new("RGB", (1720, 1720), "white")
    for i, (cam, f) in enumerate(tests):
        sheet.paste(view(860, cam, f, 0.25), ((i % 2) * 860, (i // 2) * 860))
    sheet.save(os.path.join(HERE, "astro_test.png"))
