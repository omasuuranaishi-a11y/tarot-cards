"""11/9 蠍座新月のサムネイル案 第2弾（1280×720）。

参考にした型：極太の明朝・ゴシック、左右に文字を分けて真ん中に大きな絵、下に帯、1語だけ色を変える。
おますさんらしさ：心理学・心理占星術・仏教・台湾や韓国のデザイン（エンジェル系にはしない）。
  A 台湾の朱色：朱の地に、生成りの円と筆の円相（新月）、左右に極太の文字、下に黒い帯
  B 韓国風ミニマル：生成りの紙に、極太の黒い文字と1語の色、右に大きな円相
  C 夜と蓮：藍の地に金の極太明朝、新月の下に蓮の線画、下に帯
書体は youtube/fonts/（どれも SIL Open Font License。商用可）。
    python3 make_thumbnails_v2.py
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "thumbnails")
ICON = os.path.join(HERE, "..", "2027-unsei-pr", "assets", "icon.png")
W, H = 1280, 720

DELA = os.path.join(FONTS, "DelaGothicOne-Regular.ttf")         # 極太ゴシック
OLDM = os.path.join(FONTS, "ZenOldMincho-Black.ttf")            # 極太明朝
TOKU = os.path.join(FONTS, "KaiseiTokumin-ExtraBold.ttf")       # 特徴のある明朝
KAKU = os.path.join(FONTS, "ZenKakuGothicNew-Black.ttf")        # 黒いゴシック（小さい文字用）


def F(path, size):
    return ImageFont.truetype(path, size)


def paper(color, seed, grain=7):
    rng = np.random.default_rng(seed)
    base = np.ones((H, W, 3), np.float32) * np.array(color, np.float32)
    n = rng.normal(0, grain, (H // 2, W // 2)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    fib = rng.normal(0, grain * 0.6, (H // 6, W)).astype(np.float32)  # 横に流れる紙の繊維
    fib = np.asarray(Image.fromarray(fib).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    vign = 1 - 0.18 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img = np.clip((base + n + fib) * vign[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(img).convert("RGBA")


def enso(d, color=(28, 24, 26), seed=3, gap=40):
    """筆で一気に描いた円相。太く入って、細くかすれて抜ける。"""
    S = 2
    R = d * S / 2
    im = Image.new("RGBA", (int(d * S + 80 * S), int(d * S + 80 * S)), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    cx = cy = im.width / 2
    a0 = math.radians(-60)
    span = math.radians(360 - gap)
    steps = 900
    wobble = rng.normal(0, 1, 8)
    for i in range(steps):
        t = i / steps
        a = a0 + span * t
        r = R * (1 + 0.025 * sum(wobble[k] * math.sin((k + 1) * a + k) for k in range(4)) / 4)
        w = S * (d * 0.11) * (1.0 - 0.75 * t) * (0.9 + 0.2 * math.sin(t * 9))
        if t < 0.03:
            w *= 0.6 + t / 0.03 * 0.4
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        # かすれ：太さの中で、筆の毛のすじを何本か
        for k in range(14):
            off = (k / 13 - 0.5) * w
            if rng.random() < (0.12 + 0.6 * t ** 1.6):
                continue
            px, py = x + off * math.cos(a), y + off * math.sin(a)
            rr = S * (1.6 + rng.random() * 1.8)
            alpha = int(255 * (0.85 + 0.15 * rng.random()))
            dr.ellipse((px - rr, py - rr, px + rr, py + rr), fill=color + (alpha,))
    im = im.filter(ImageFilter.GaussianBlur(1.2 * S))
    a = np.asarray(im.split()[3]).astype(np.float32)
    a = np.clip(a * 1.35, 0, 255).astype(np.uint8)
    im.putalpha(Image.fromarray(a))
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)


def lotus(w, color=(232, 196, 120, 255), lw=4):
    """蓮の花の線画"""
    S = 3
    im = Image.new("RGBA", (w * S, int(w * 0.62) * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, base = im.width / 2, im.height * 0.92

    def petal(ang, length, width):
        pts = []
        for i in range(41):
            t = i / 40
            x = width * math.sin(math.pi * t) * (1 if i <= 20 else 1)
            y = length * t
            pts.append((x, y))
        left = [(-x, y) for x, y in pts]
        shape = pts + left[::-1]
        ca, sa = math.cos(ang), math.sin(ang)
        return [(cx + x * ca - (-y) * sa, base + x * sa + (-y) * ca) for x, y in shape]

    L = im.height * 0.82
    for ang, ln, wd in ((-1.15, 0.62, 0.13), (1.15, 0.62, 0.13), (-0.75, 0.8, 0.15), (0.75, 0.8, 0.15),
                        (-0.38, 0.95, 0.16), (0.38, 0.95, 0.16), (0, 1.0, 0.17)):
        d.line(petal(ang, L * ln, L * wd) + [petal(ang, L * ln, L * wd)[0]], fill=color, width=lw * S, joint="curve")
    d.arc((cx - L * 0.9, base - L * 0.12, cx + L * 0.9, base + L * 0.12), 0, 180, fill=color, width=lw * S)
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)


def text(img, xy, s, font, fill, stroke=0, stroke_fill=None, anchor="la", shadow=True):
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((xy[0] + 5, xy[1] + 7), s, font=font, fill=(0, 0, 0, 150), anchor=anchor,
                                stroke_width=stroke, stroke_fill=(0, 0, 0, 150))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(img).text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke,
                             stroke_fill=stroke_fill or fill)


def runs(img, x, y, parts, font, stroke=0, stroke_fill=None, shadow=True):
    d = ImageDraw.Draw(img)
    for s, col in parts:
        text(img, (x, y), s, font, col, stroke, stroke_fill, shadow=shadow)
        x += d.textlength(s, font=font)
    return x


def icon_small(img, size=104, margin=18):
    ic = Image.open(ICON).convert("RGBA").resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    x, y = W - size - margin, H - size - margin
    ImageDraw.Draw(img).ellipse((x - 5, y - 5, x + size + 4, y + size + 4), fill=(255, 255, 255, 255))
    img.paste(ic, (x, y), m)


# ---- A 台湾の朱色 ----
def make_a():
    img = paper((178, 38, 36), 11, grain=6)
    d = ImageDraw.Draw(img)
    # 真ん中：生成りの円（紙の月）と筆の円相
    cx, cy, R = 640, 300, 250
    disk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(disk).ellipse((cx - R - 14, cy - R - 14, cx + R + 14, cy + R + 14), fill=(0, 0, 0, 90))
    img.alpha_composite(disk.filter(ImageFilter.GaussianBlur(16)))
    cream = paper((242, 232, 212), 12, grain=5)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((cx - R, cy - R, cx + R, cy + R), fill=255)
    img.paste(cream, (0, 0), m)
    e = enso(380, seed=5)
    img.alpha_composite(e, (cx - e.width // 2, cy - e.height // 2))
    text(img, (cx, cy + 6), "新月", F(TOKU, 54), (178, 38, 36), anchor="mm", shadow=False)
    # 左：蠍座／新月　右：金星／水星／順行へ
    big = F(DELA, 150)
    text(img, (40, 30), "蠍座", big, (255, 248, 232), 10, (70, 10, 10))
    text(img, (40, 210), "新月", big, (255, 248, 232), 10, (70, 10, 10))
    r = F(DELA, 108)
    text(img, (1240, 30), "金星", r, (255, 248, 232), 9, (70, 10, 10), anchor="ra")
    text(img, (1240, 160), "水星", r, (255, 248, 232), 9, (70, 10, 10), anchor="ra")
    text(img, (1240, 300), "順行へ", F(DELA, 96), (255, 214, 64), 9, (70, 10, 10), anchor="ra")
    # 下の帯
    d.rectangle((0, 560, W, H), fill=(22, 18, 20, 255))
    d.rectangle((0, 552, W, 560), fill=(214, 172, 80, 255))
    x = runs(img, 40, 572, [("関係が", (255, 255, 255)), ("動き出す", (255, 214, 64))], F(OLDM, 112), shadow=False)
    text(img, (x + 10, 640), "2週間", F(OLDM, 64), (255, 255, 255), shadow=False)
    text(img, (40, 470), "11.9 16:02", F(KAKU, 46), (255, 236, 200), 4, (70, 10, 10))
    return img


# ---- B 韓国風ミニマル ----
def make_b():
    img = paper((238, 232, 222), 21, grain=5)
    d = ImageDraw.Draw(img)
    INKC = (30, 28, 32)
    TEAL = (26, 92, 96)
    CORAL = (214, 84, 70)
    e = enso(520, color=INKC, seed=8, gap=34)
    ex, ey = 960, 340
    img.alpha_composite(e, (ex - e.width // 2, ey - e.height // 2))
    d.ellipse((ex - 16, ey - 16, ex + 16, ey + 16), fill=(196, 150, 70, 255))  # 新月の金の点
    # ラベル
    lab = "11.9  16:02  蠍座新月"
    lf = F(KAKU, 40)
    lw = d.textlength(lab, font=lf)
    d.rounded_rectangle((44, 50, 44 + lw + 48, 120), 35, fill=TEAL + (255,))
    d.text((44 + 24, 85), lab, font=lf, fill=(255, 255, 255), anchor="lm")
    big = F(DELA, 168)
    text(img, (34, 150), "関係が、", big, INKC, shadow=False)
    text(img, (34, 360), "動き出す", big, CORAL, shadow=False)
    d.line((44, 600, 640, 600), fill=INKC + (255,), width=3)
    text(img, (44, 618), "金星・水星　11/14 順行へ", F(KAKU, 46), INKC, shadow=False)
    text(img, (ex, ey + 300), "心理占星術で読む", F(TOKU, 34), (90, 84, 90), anchor="mm", shadow=False)
    icon_small(img, 96)
    return img


# ---- C 夜と蓮 ----
def make_c():
    img = paper((26, 28, 62), 31, grain=6)
    rng = np.random.default_rng(4)
    d = ImageDraw.Draw(img)
    for _ in range(160):
        x, y = rng.integers(0, W), rng.integers(0, 540)
        r = rng.choice([1, 1, 2])
        b = int(rng.integers(150, 255))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(b, b, min(255, b + 15), 255))
    GOLD = (236, 200, 120, 255)
    cx, cy, R = 640, 230, 150
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((cx - R - 50, cy - R - 50, cx + R + 50, cy + R + 50), fill=(255, 220, 150, 120))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(36)))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(18, 18, 40, 255), outline=GOLD, width=5)
    lo = lotus(460)
    img.alpha_composite(lo, (cx - lo.width // 2, 360))
    big = F(OLDM, 160)
    gold_fill = (240, 206, 128)
    text(img, (36, 20), "蠍座", big, gold_fill, 6, (80, 50, 20))
    text(img, (36, 210), "新月", big, gold_fill, 6, (80, 50, 20))
    r = F(OLDM, 104)
    text(img, (1244, 40), "見直した", r, (255, 255, 255), 6, (30, 20, 60), anchor="ra")
    text(img, (1244, 170), "関係を", r, (255, 255, 255), 6, (30, 20, 60), anchor="ra")
    text(img, (1244, 300), "育てる", F(OLDM, 118), (255, 150, 170), 6, (30, 20, 60), anchor="ra")
    d = ImageDraw.Draw(img)
    d.rectangle((0, 580, W, H), fill=(120, 34, 72, 255))
    d.rectangle((0, 574, W, 580), fill=GOLD)
    x = runs(img, 40, 592, [("11/14 ", (255, 255, 255)), ("金星・水星", (255, 214, 64)), (" 順行へ", (255, 255, 255))],
             F(DELA, 84), shadow=False)
    text(img, (40, 480), "11.9 16:02", F(KAKU, 44), (236, 220, 200), shadow=False)
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    outs = []
    for key, fn in (("A", make_a), ("B", make_b), ("C", make_c)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第2弾{key}_11月9日蠍座新月.png"))
        outs.append(im)
    small = Image.new("RGB", (3 * 380, 230), (255, 255, 255))
    for i, im in enumerate(outs):
        small.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    small.save(os.path.join(OUT, "第2弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 3))
    for i, im in enumerate(outs):
        big.paste(im, (0, i * 720))
    big.resize((960, 1620)).save(os.path.join(OUT, "第2弾_3案まとめ.png"))
    print("ok")
