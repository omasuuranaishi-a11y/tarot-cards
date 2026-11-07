"""11/9 蠍座新月のサムネイル案 第3弾：中華街・台湾の寺院のような、仏像寄りのデザイン（1280×720）。

  D 中華街の円窓：朱の地に金の回紋の枠、真ん中に金の円窓と金色の大仏・新月の光の輪、左右に金の極太文字、上に中華提灯
  E 春聯（対聯）：漆黒の地に、左右の赤い縦の札に金の文字、真ん中に光背つきの金の大仏、上に横の札
  F 台湾の翡翠色：翡翠の緑に朱と金、寺院の屋根のような上の飾り、雷紋の丸枠の中に大仏
大仏と雷紋の丸枠は、いらすとや（大仏は金色に塗り直している）。ほかの模様はこのスクリプトで描く。
    python3 make_thumbnails_v3.py
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
ILL = os.path.join(HERE, "illust")
OUT = os.path.join(HERE, "thumbnails")
W, H = 1280, 720

DELA = os.path.join(FONTS, "DelaGothicOne-Regular.ttf")
OLDM = os.path.join(FONTS, "ZenOldMincho-Black.ttf")
TOKU = os.path.join(FONTS, "KaiseiTokumin-ExtraBold.ttf")
SYUKU = os.path.join(FONTS, "YujiSyuku-Regular.ttf")
KAKU = os.path.join(FONTS, "ZenKakuGothicNew-Black.ttf")

CINNABAR = (176, 28, 30)
DEEPRED = (120, 14, 18)
GOLD = (232, 186, 92)
JADE = (18, 98, 88)
INKBLACK = (22, 16, 18)


def F(path, size):
    return ImageFont.truetype(path, size)


def paper(color, seed, grain=6):
    rng = np.random.default_rng(seed)
    base = np.ones((H, W, 3), np.float32) * np.array(color, np.float32)
    n = rng.normal(0, grain, (H // 2, W // 2)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    vign = 1 - 0.22 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return Image.fromarray(np.clip((base + n) * vign[..., None], 0, 255).astype(np.uint8)).convert("RGBA")


def gold_text(img, xy, s, font, anchor="la", stroke=8, edge=(90, 20, 10), shadow=True):
    """金のグラデーションの文字。濃い色のふちどりと影つき。"""
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((xy[0] + 5, xy[1] + 8), s, font=font, fill=(0, 0, 0, 170), anchor=anchor,
                                stroke_width=stroke + 3, stroke_fill=(0, 0, 0, 170))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    e = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(e).text(xy, s, font=font, fill=(0, 0, 0, 0), anchor=anchor, stroke_width=stroke,
                           stroke_fill=edge + (255,))
    img.alpha_composite(e)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).text(xy, s, font=font, fill=255, anchor=anchor)
    bb = mask.getbbox()
    if not bb:
        return
    grad = np.zeros((H, W, 4), np.uint8)
    for y in range(bb[1], bb[3] + 1):
        a = (y - bb[1]) / max(1, bb[3] - bb[1])
        if a < 0.45:
            c = (255, int(246 - 40 * a), int(200 - 120 * a))
        elif a < 0.55:
            c = (250, 214, 120)
        else:
            c = (int(240 - 40 * (a - 0.55)), int(176 - 50 * (a - 0.55)), int(70 - 30 * (a - 0.55)))
        grad[y, bb[0]:bb[2] + 1] = c + (255,)
    g = Image.fromarray(grad)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(g, (0, 0), mask)
    img.alpha_composite(out)


def text(img, xy, s, font, fill, stroke=0, stroke_fill=None, anchor="la"):
    ImageDraw.Draw(img).text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke,
                             stroke_fill=stroke_fill or fill)


def vtext(img, x, y, s, font, step, fn, **kw):
    """縦書き（1文字ずつ下へ）"""
    for i, ch in enumerate(s):
        fn(img, (x, y + i * step), ch, font, anchor="mt", **kw)


def meander_band(d, x0, y0, x1, y1, color, unit=None):
    """回紋（四角い渦）を横に並べた帯"""
    h = y1 - y0
    u = unit or h
    lw = max(3, int(u / 9))
    x = x0
    while x + u <= x1 + 1:
        # 四角い渦：外側から内側へ
        pts = [(x, y1), (x, y0), (x + u, y0), (x + u, y1 - u * 0.25), (x + u * 0.25, y1 - u * 0.25),
               (x + u * 0.25, y0 + u * 0.25), (x + u * 0.75, y0 + u * 0.25), (x + u * 0.75, y0 + u * 0.55),
               (x + u * 0.5, y0 + u * 0.55)]
        d.line(pts, fill=color, width=lw, joint="curve")
        d.line((x + u, y1, x + u + u * 0.0, y1), fill=color, width=lw)
        x += u
    d.line((x0, y1, x1, y1), fill=color, width=lw)


def meander_frame(img, inset, unit, color):
    d = ImageDraw.Draw(img)
    meander_band(d, inset, inset, W - inset, inset + unit, color, unit)
    band = Image.new("RGBA", (W, unit + 8), (0, 0, 0, 0))
    meander_band(ImageDraw.Draw(band), inset, 2, W - inset, unit + 2, color, unit)
    img.alpha_composite(band.rotate(180), (0, H - inset - unit - 4))
    d.rectangle((inset - 6, inset - 6, W - inset + 6, H - inset + 6), outline=color, width=4)


def xiangyun(w, color=GOLD, fill=None, lw=5):
    """祥雲（中華の雲の模様）：渦を巻く丸をつないだ形"""
    S = 2
    h = int(w * 0.45)
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = color + (255,)
    circles = [(0.22, 0.62, 0.20), (0.45, 0.42, 0.25), (0.70, 0.58, 0.20), (0.88, 0.70, 0.12)]
    for cx, cy, r in circles:
        X, Y, R = cx * w * S, cy * h * S, r * w * S * 0.9
        if fill:
            d.ellipse((X - R, Y - R, X + R, Y + R), fill=fill + (255,))
    for cx, cy, r in circles:
        X, Y, R = cx * w * S, cy * h * S, r * w * S * 0.9
        pts = []
        for i in range(120):
            t = i / 119
            a = math.radians(200) + t * math.radians(560)
            rr = R * (1 - 0.72 * t)
            pts.append((X + rr * math.cos(a), Y + rr * math.sin(a)))
        d.line(pts, fill=col, width=lw * S, joint="curve")
    d.line((0.05 * w * S, 0.86 * h * S, 0.98 * w * S, 0.86 * h * S), fill=col, width=lw * S)
    return im.resize((w, h), Image.LANCZOS)


def lantern(h, seed=0):
    """中華提灯（赤い楕円・金の上下・房）"""
    S = 2
    w = int(h * 0.8)
    im = Image.new("RGBA", (w * S, int(h * 1.5) * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = im.width / 2
    top, bot = 0.18 * h * S, 1.0 * h * S
    d.line((cx, 0, cx, top), fill=(60, 30, 20, 255), width=3 * S)
    d.rounded_rectangle((cx - w * 0.22 * S, top, cx + w * 0.22 * S, top + 0.08 * h * S), 6 * S, fill=GOLD + (255,))
    d.ellipse((cx - w * 0.5 * S, top + 0.04 * h * S, cx + w * 0.5 * S, bot), fill=(214, 36, 32, 255))
    for k in (-0.32, -0.12, 0.12, 0.32):  # 骨
        d.arc((cx + (k - 0.2) * w * S, top + 0.04 * h * S, cx + (k + 0.2) * w * S, bot), 270, 90 if k > 0 else 270,
              fill=(150, 16, 18, 255), width=2 * S)
    for k in (-0.3, -0.1, 0.1, 0.3):
        x = cx + k * w * S
        d.line((x, top + 0.1 * h * S, x, bot - 0.06 * h * S), fill=(170, 20, 22, 200), width=2 * S)
    d.ellipse((cx - w * 0.34 * S, top + 0.18 * h * S, cx - w * 0.08 * S, top + 0.5 * h * S), fill=(255, 120, 90, 70))
    d.rounded_rectangle((cx - w * 0.22 * S, bot - 0.04 * h * S, cx + w * 0.22 * S, bot + 0.04 * h * S), 6 * S, fill=GOLD + (255,))
    for k in range(-3, 4):  # 房
        x = cx + k * 3 * S
        d.line((x, bot + 0.04 * h * S, x, bot + 0.42 * h * S), fill=(220, 40, 36, 255), width=2 * S)
    d.ellipse((cx - 7 * S, bot + 0.02 * h * S, cx + 7 * S, bot + 0.1 * h * S), fill=GOLD + (255,))
    im = im.resize((im.width // S, im.height // S), Image.LANCZOS)
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    glow.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.5)))
    g2 = Image.new("RGBA", im.size, (255, 150, 60, 0))
    g2.putalpha(glow.split()[3])
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(g2)
    out.alpha_composite(im)
    return out


_buddha = None


def gold_buddha(height):
    """いらすとやの大仏を、金色の仏像に塗り直す（線は濃い茶色のまま）。"""
    global _buddha
    if _buddha is None:
        im = Image.open(os.path.join(ILL, "daibutsu.png")).convert("RGBA")
        im = im.crop(im.getbbox())
        a = np.asarray(im).astype(np.float32)
        lum = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]) / 255
        lo, hi = np.percentile(lum[a[..., 3] > 200], 5), np.percentile(lum[a[..., 3] > 200], 95)
        t = np.clip((lum - lo) / max(1e-3, hi - lo), 0, 1)[..., None]
        dark = np.array([96, 54, 18], np.float32)
        mid = np.array([214, 158, 60], np.float32)
        light = np.array([255, 232, 160], np.float32)
        col = np.where(t < 0.5, dark + (mid - dark) * (t / 0.5), mid + (light - mid) * ((t - 0.5) / 0.5))
        yy = np.linspace(0, 1, a.shape[0])[:, None, None]
        col = col * (1.08 - 0.16 * yy)  # 上を明るく
        out = np.concatenate([np.clip(col, 0, 255), a[..., 3:4]], axis=2).astype(np.uint8)
        _buddha = Image.fromarray(out)
    b = _buddha
    return b.resize((int(b.width * height / b.height), height), Image.LANCZOS)


def halo(d_size, color=GOLD, rays=True):
    """光背：金の同心円と光の筋"""
    S = 2
    im = Image.new("RGBA", (d_size * S, d_size * S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    c = d_size * S / 2
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((c * 0.2, c * 0.2, c * 1.8, c * 1.8), fill=(255, 214, 140, 150))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30 * S)))
    if rays:
        for k in range(48):
            a = 2 * math.pi * k / 48
            r0, r1 = c * 0.62, c * (0.95 if k % 2 == 0 else 0.84)
            dr.line((c + r0 * math.cos(a), c + r0 * math.sin(a), c + r1 * math.cos(a), c + r1 * math.sin(a)),
                    fill=color + (200,), width=2 * S)
    for r, w_ in ((0.6, 5), (0.52, 2), (0.98, 3)):
        dr.ellipse((c - c * r, c - c * r, c + c * r, c + c * r), outline=color + (255,), width=w_ * S)
    return im.resize((d_size, d_size), Image.LANCZOS)


def recolor(path, color, size):
    im = Image.open(path).convert("RGBA")
    a = im.split()[3]
    out = Image.new("RGBA", im.size, color + (255,))
    out.putalpha(a)
    return out.resize((size, size), Image.LANCZOS)


# ---- D 中華街の円窓 ----
def make_d():
    img = paper(CINNABAR, 41)
    meander_frame(img, 14, 22, GOLD + (255,))
    cx, cy, R = 640, 330, 230
    sky = paper((22, 20, 50), 42, grain=5)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((cx - R, cy - R, cx + R, cy + R), fill=255)
    rng = np.random.default_rng(5)
    sd = ImageDraw.Draw(sky)
    for _ in range(90):
        x, y = rng.integers(cx - R, cx + R), rng.integers(cy - R, cy + R)
        r = rng.choice([1, 1, 2])
        sd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 240, 210, 255))
    img.paste(sky, (0, 0), m)
    # 新月の光の輪（仏の後ろ）
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((cx - 120, cy - 190, cx + 120, cy + 50), fill=(255, 220, 150, 160))
    ring = ring.filter(ImageFilter.GaussianBlur(26))
    rm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rm.paste(ring, (0, 0), m)
    img.alpha_composite(rm)
    d = ImageDraw.Draw(img)
    d.ellipse((cx - 100, cy - 170, cx + 100, cy + 30), fill=(18, 16, 40, 255), outline=(255, 232, 180, 255), width=4)
    bud = gold_buddha(330)
    bm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bm.alpha_composite(bud, (cx - bud.width // 2, cy + R - bud.height + 10))
    clip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    clip.paste(bm, (0, 0), m)
    img.alpha_composite(clip)
    rim = recolor(os.path.join(ILL, "raimon_circle.png"), GOLD, R * 2 + 70)
    img.alpha_composite(rim, (cx - rim.width // 2, cy - rim.height // 2))
    d.ellipse((cx - R - 4, cy - R - 4, cx + R + 4, cy + R + 4), outline=GOLD + (255,), width=6)
    for x in (120, 1160):
        la = lantern(130)
        img.alpha_composite(la, (x - la.width // 2, 34))
    big = F(OLDM, 128)
    gold_text(img, (60, 190), "蠍座", big)
    gold_text(img, (60, 340), "新月", big)
    r = F(OLDM, 100)
    gold_text(img, (1222, 190), "金星水星", F(OLDM, 76), anchor="ra")
    gold_text(img, (1222, 290), "順行へ", r, anchor="ra")
    d = ImageDraw.Draw(img)
    d.rectangle((40, 586, W - 40, 676), fill=INKBLACK + (255,))
    d.rectangle((40, 586, W - 40, 676), outline=GOLD + (255,), width=3)
    text(img, (W // 2, 631), "関係が、動き出す2週間", F(DELA, 64), (255, 236, 190), anchor="mm")
    text(img, (60, 500), "11.9  16:02", F(KAKU, 40), (255, 230, 190), 4, DEEPRED)
    return img


# ---- E 春聯（対聯） ----
def make_e():
    img = paper(INKBLACK, 51, grain=4)
    d = ImageDraw.Draw(img)
    cx, cy = 640, 360
    hl = halo(560)
    img.alpha_composite(hl, (cx - hl.width // 2, cy - hl.height // 2 - 30))
    bud = gold_buddha(420)
    img.alpha_composite(bud, (cx - bud.width // 2, 236))
    for x0 in (60, 1280 - 60 - 220):  # 左右の赤い札
        d.rectangle((x0, 60, x0 + 220, 690), fill=CINNABAR + (255,))
        d.rectangle((x0 + 10, 70, x0 + 210, 680), outline=GOLD + (255,), width=3)
    vf = F(OLDM, 124)
    vtext(img, 170, 96, "蠍座新月", vf, 140, gold_text, stroke=6)
    vtext(img, 1280 - 170, 96, "動き出す", vf, 140, gold_text, stroke=6)
    # 上の横の札
    d.rectangle((380, 30, 900, 120), fill=CINNABAR + (255,))
    d.rectangle((388, 38, 892, 112), outline=GOLD + (255,), width=3)
    gold_text(img, (640, 76), "見直した関係が", F(OLDM, 54), anchor="mm", stroke=4)
    cl = xiangyun(280, GOLD)  # 仏さまの台座の左右に祥雲
    img.alpha_composite(cl, (300, 540))
    img.alpha_composite(cl.transpose(Image.FLIP_LEFT_RIGHT), (700, 540))
    d = ImageDraw.Draw(img)
    d.rectangle((300, 664, 980, 708), fill=CINNABAR + (255,))
    d.rectangle((306, 670, 974, 702), outline=GOLD + (255,), width=2)
    text(img, (640, 686), "11.9 16:02 ／ 11/14 金星・水星 順行へ", F(KAKU, 30), (255, 236, 200), anchor="mm")
    return img


# ---- F 台湾の翡翠色 ----
def make_f():
    img = paper(JADE, 61, grain=6)
    d = ImageDraw.Draw(img)
    # 上：寺院の屋根のような朱の帯と金の線
    d.polygon([(0, 0), (W, 0), (W, 70), (W - 60, 96), (60, 96), (0, 70)], fill=CINNABAR + (255,))
    meander_band(d, 80, 30, W - 80, 64, GOLD + (255,), 34)
    d.line((60, 96, W - 60, 96), fill=GOLD + (255,), width=4)
    cx, cy, R = 930, 400, 230
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(240, 228, 200, 255))
    hl = halo(R * 2 - 20, color=(214, 150, 60), rays=False)
    img.alpha_composite(hl, (cx - hl.width // 2, cy - hl.height // 2))
    bud = gold_buddha(360)
    img.alpha_composite(bud, (cx - bud.width // 2, cy + R - bud.height - 6))
    rim = recolor(os.path.join(ILL, "raimon_circle.png"), CINNABAR, R * 2 + 64)
    img.alpha_composite(rim, (cx - rim.width // 2, cy - rim.height // 2))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2), outline=GOLD + (255,), width=5)
    text(img, (60, 130), "11.9 16:02", F(KAKU, 44), (255, 236, 200), 4, (10, 50, 44))
    gold_text(img, (50, 180), "蠍座新月", F(OLDM, 132), edge=(10, 40, 34))
    text(img, (56, 360), "関係が、", F(DELA, 96), (255, 255, 255), 8, (10, 40, 34))
    text(img, (56, 480), "動き出す", F(DELA, 110), (255, 120, 100), 8, (90, 14, 14))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((56, 626, 600, 690), 32, fill=CINNABAR + (255,), outline=GOLD + (255,), width=3)
    text(img, (328, 658), "11/14 金星・水星 順行へ", F(KAKU, 36), (255, 240, 210), anchor="mm")
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    outs = []
    for key, fn in (("D", make_d), ("E", make_e), ("F", make_f)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第3弾{key}_11月9日蠍座新月.png"))
        outs.append(im)
    small = Image.new("RGB", (3 * 380, 230), (255, 255, 255))
    for i, im in enumerate(outs):
        small.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    small.save(os.path.join(OUT, "第3弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 3))
    for i, im in enumerate(outs):
        big.paste(im, (0, i * 720))
    big.resize((960, 1620)).save(os.path.join(OUT, "第3弾_3案まとめ.png"))
    print("ok")
