"""11/9 蠍座新月のサムネイル案 第6弾：テーマに合った神仏＋大きな文字（1280×720）。

神仏はメトロポリタン美術館のパブリックドメイン（CC0）の作品（public_domain/sources.json）。
  M 愛染明王（14世紀の仏画）：愛や執着を悟りの力に変える明王＝蠍座の深い情。赤い円光を丸く切り取り、
    左右に縦書きの極太の文字。
  N 如意輪観音（1693年の像）：頬に手を当てて考える姿＝「見直す」新月。生成りの和紙に暗い赤の円（新月）、
    細い縦の線、ミニマルなポスターの雰囲気。
  O すだれと後ろ姿の雰囲気：すだれの質感の上に、観音の形を錆朱の1色（細い横じまの質感）で。赤い実の枝。
    python3 make_thumbnails_v6.py
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
PD = os.path.join(HERE, "public_domain")
OUT = os.path.join(HERE, "thumbnails")
W, H = 1280, 720
OLDM = os.path.join(FONTS, "ZenOldMincho-Black.ttf")
SANS = os.path.join(FONTS, "ZenKakuGothicNew-Black.ttf")

GOLD = (236, 196, 110)
CRIMSON = (150, 20, 28)
RUST = (140, 58, 34)
MAROON = (98, 22, 26)
INK = (30, 24, 24)
WASHI = (236, 226, 206)
SHU = (204, 52, 36)


def F(path, size):
    return ImageFont.truetype(path, size)


def paper(color, seed, grain=6, vign=0.2):
    rng = np.random.default_rng(seed)
    base = np.ones((H, W, 3), np.float32) * np.array(color, np.float32)
    n = rng.normal(0, grain, (H // 2, W // 2)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    fib = rng.normal(0, grain * 0.5, (H // 8, W)).astype(np.float32)
    fib = np.asarray(Image.fromarray(fib).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - vign * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return Image.fromarray(np.clip((base + n + fib) * v[..., None], 0, 255).astype(np.uint8)).convert("RGBA")


def shadowed(img, layer, xy, blur=14, alpha=0.5, off=(8, 12)):
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sh.putalpha(layer.split()[3].point(lambda v: int(v * alpha)))
    big = Image.new("RGBA", img.size, (0, 0, 0, 0))
    big.alpha_composite(sh, (int(xy[0] + off[0]), int(xy[1] + off[1])))
    img.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)))
    img.alpha_composite(layer, (int(xy[0]), int(xy[1])))


def vtext(img, x, y, s, size, fill, step=None, stroke=0, stroke_fill=None, shadow=True):
    """縦書き（1文字ずつ下へ）。x は文字の中心。"""
    f = F(OLDM, size)
    step = step or int(size * 0.98)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, ch in enumerate(s):
        d.text((x, y + i * step), ch, font=f, fill=fill, anchor="mt", stroke_width=stroke,
               stroke_fill=stroke_fill or fill)
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(layer.split()[3].point(lambda v: int(v * 0.6)))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (6, 10))
    img.alpha_composite(layer)


def htext(img, xy, s, size, fill, anchor="la", stroke=0, stroke_fill=None, font=OLDM, shadow=False, condense=1.0):
    f = F(font, size)
    if condense == 1.0 and not shadow:
        ImageDraw.Draw(img).text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke,
                                 stroke_fill=stroke_fill or fill)
        return
    tmp = Image.new("RGBA", (int(size * len(s) * 1.3 + stroke * 4), int(size * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((size * 0.1 + stroke, size * 0.1), s, font=f, fill=fill, stroke_width=stroke,
                             stroke_fill=stroke_fill or fill)
    tmp = tmp.crop(tmp.getbbox())
    tmp = tmp.resize((int(tmp.width * condense), tmp.height), Image.LANCZOS)
    x, y = xy
    if anchor[0] == "r":
        x -= tmp.width
    elif anchor[0] == "m":
        x -= tmp.width // 2
    if shadow:
        shadowed(img, tmp, (x, y), blur=6, alpha=0.45, off=(4, 6))
    else:
        img.alpha_composite(tmp, (int(x), int(y)))


# ---- M 愛染明王 ----
def make_m():
    img = paper((70, 12, 18), 91, grain=5, vign=0.45)
    d = ImageDraw.Draw(img)
    cx, cy, R = 640, 350, 300
    for k in range(72):  # 円光のまわりの光の筋
        a = 2 * math.pi * k / 72
        r0, r1 = R + 18, R + (120 if k % 2 == 0 else 70)
        d.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
               fill=(120, 30, 34, 255), width=3)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((cx - R - 40, cy - R - 40, cx + R + 40, cy + R + 40), fill=(255, 120, 80, 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30)))
    ai = Image.open(os.path.join(PD, "aizen_circle.png")).convert("RGBA").resize((R * 2, R * 2), Image.LANCZOS)
    a_ = ai.split()[3]  # 古い絵の暗さを少し持ち上げて、赤をはっきりさせる
    rgb = ImageOps.autocontrast(ai.convert("RGB"), cutoff=1, preserve_tone=True)
    rgb = ImageEnhance.Color(rgb).enhance(1.2)
    rgb = ImageEnhance.Brightness(rgb).enhance(1.12)
    ai = rgb.convert("RGBA")
    ai.putalpha(a_)
    img.alpha_composite(ai, (cx - R, cy - R))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2), outline=GOLD + (255,), width=6)
    d.ellipse((cx - R - 16, cy - R - 16, cx + R + 16, cy + R + 16), outline=GOLD + (200,), width=2)
    vtext(img, 160, 30, "蠍座新月", 166, (255, 250, 240), step=164, stroke=6, stroke_fill=(40, 6, 8))
    vtext(img, 1120, 30, "縁が", 166, (255, 250, 240), step=164, stroke=6, stroke_fill=(40, 6, 8))
    vtext(img, 1120, 362, "動く", 166, (255, 208, 70), step=164, stroke=6, stroke_fill=(40, 6, 8))
    # 下：小さな札
    d = ImageDraw.Draw(img)
    d.rectangle((cx - 230, 664, cx + 230, 708), fill=(30, 6, 8, 230), outline=GOLD + (255,), width=2)
    htext(img, (cx, 686), "愛染明王　11.9 16:02", 30, GOLD + (255,), anchor="mm", font=SANS)
    return img


# ---- N 如意輪観音 ----
def make_n():
    img = paper(WASHI, 92, grain=6, vign=0.15)
    d = ImageDraw.Draw(img)
    cx, cy, R = 930, 300, 250
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=MAROON + (255,))      # 新月（暗い赤の円）
    d.line((cx, 0, cx, cy - R), fill=INK + (255,), width=2)                 # 細い縦の線
    ka = Image.open(os.path.join(PD, "nyoirin_kannon_cut.png")).convert("RGBA")
    kh = 560
    ka = ka.resize((int(ka.width * kh / ka.height), kh), Image.LANCZOS)
    shadowed(img, ka, (cx - ka.width // 2 + 10, H - kh + 6), blur=16, alpha=0.45, off=(14, 10))
    htext(img, (60, 54), "11.9 16:02　蠍座新月", 40, RUST + (255,), font=SANS)
    d = ImageDraw.Draw(img)
    d.line((60, 112, 560, 112), fill=RUST + (255,), width=3)
    htext(img, (52, 140), "見直した", 140, INK + (255,), condense=0.92)
    htext(img, (52, 300), "関係が", 140, INK + (255,), condense=0.92)
    htext(img, (46, 462), "動き出す", 168, SHU + (255,), condense=0.9)
    # 作品の名札（美術館の札のように縦に小さく）
    f = F(SANS, 24)
    for i, ch in enumerate("如意輪観音"):
        ImageDraw.Draw(img).text((1236, 420 + i * 28), ch, font=f, fill=RUST + (255,), anchor="mt")
    return img


# ---- O すだれ ----
def sudare(seed=93):
    img = paper((232, 212, 184), seed, grain=4, vign=0.12)
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(img)
    y = 0
    while y < H:  # 竹ひごの細い横線
        h = rng.integers(3, 6)
        c = int(rng.integers(196, 214))
        d.line((0, y, W, y + rng.integers(-1, 2)), fill=(c + 8, c - 14, c - 46, 255), width=1)
        if rng.random() < 0.25:
            d.line((0, y + 1, W, y + 1), fill=(c - 10, c - 34, c - 66, 150), width=1)
        y += h
    for x in (300, 700, 1080):  # 編み糸（縦）
        for yy in range(0, H, 6):
            d.line((x + rng.integers(-1, 2), yy, x + rng.integers(-1, 2), yy + 4), fill=(150, 104, 70, 255), width=2)
    return img


def striped_silhouette(alpha, color, line=(108, 40, 24), seed=0):
    """形を1色で塗り、細い横じま（織物のような質感）を入れる"""
    w, h = alpha.size
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), np.float32) * np.array(color, np.float32)
    y = 0
    while y < h:
        t = int(rng.integers(1, 3))
        k = rng.uniform(0.3, 0.7)
        base[y:y + t] = base[y:y + t] * k + np.array(line, np.float32) * (1 - k)
        y += int(rng.integers(3, 7))
    n = rng.normal(0, 6, (h, w, 1)).astype(np.float32)
    img = Image.fromarray(np.clip(base + n, 0, 255).astype(np.uint8)).convert("RGBA")
    img.putalpha(alpha)
    return img


def branch(seed=4, scale=1.0):
    """赤い実の枝（細い墨の枝に、朱の小さな実）"""
    S = 2
    w, h = int(520 * scale), int(560 * scale)
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    berries = []

    def grow(x, y, ang, length, width, depth):
        if depth == 0 or length < 8:
            return
        x2, y2 = x + length * math.cos(ang), y + length * math.sin(ang)
        mx, my = (x + x2) / 2 + rng.normal(0, length * 0.06), (y + y2) / 2 + rng.normal(0, length * 0.06)
        d.line([(x * S, y * S), (mx * S, my * S), (x2 * S, y2 * S)], fill=(52, 34, 30, 255), width=max(1, int(width * S)), joint="curve")
        if depth <= 2:
            for _ in range(int(rng.integers(1, 3))):
                t = rng.random()
                bx, by = x + (x2 - x) * t + rng.normal(0, 10), y + (y2 - y) * t + rng.normal(0, 10)
                berries.append((bx, by, rng.uniform(4.5, 7.5)))
        n = 2 if depth > 2 else int(rng.integers(1, 3))
        for _ in range(n):
            grow(x2, y2, ang + rng.normal(0, 0.55), length * rng.uniform(0.6, 0.8), width * 0.66, depth - 1)

    grow(w * 0.1, h * 0.95, -0.95, 170 * scale, 5.5, 6)
    for bx, by, r in berries:
        d.line((bx * S, by * S, (bx + rng.normal(0, 3)) * S, (by - r * 1.6) * S), fill=(52, 34, 30, 255), width=S)
        d.ellipse(((bx - r) * S, (by - r) * S, (bx + r) * S, (by + r) * S), fill=(176, 30, 30, 255))
        d.ellipse(((bx - r * 0.45) * S, (by - r * 0.55) * S, (bx - r * 0.05) * S, (by - r * 0.15) * S), fill=(236, 120, 100, 200))
    return im.resize((w, h), Image.LANCZOS)


def make_o():
    img = sudare()
    ka = Image.open(os.path.join(PD, "nyoirin_kannon_cut.png")).convert("RGBA")
    kh = 640
    a = ka.split()[3].resize((int(ka.width * kh / ka.height), kh), Image.LANCZOS)
    sil = striped_silhouette(a, (156, 66, 38), seed=3)
    br = branch(scale=1.05)
    img.alpha_composite(br, (230, 40))
    shadowed(img, sil, (40, H - kh + 10), blur=10, alpha=0.25, off=(10, 6))
    d = ImageDraw.Draw(img)
    d.ellipse((1060, 50, 1220, 210), fill=(46, 34, 34, 255))                  # 新月
    d.ellipse((1052, 42, 1228, 218), outline=(46, 34, 34, 255), width=2)
    htext(img, (1230, 250), "蠍座新月", 120, INK + (255,), anchor="ra", condense=0.92)
    htext(img, (1230, 392), "縁が、", 124, INK + (255,), anchor="ra", condense=0.92)
    htext(img, (1236, 530), "動き出す", 150, (176, 30, 30, 255), anchor="ra", condense=0.88)
    htext(img, (1046, 108), "11.9  16:02", 34, INK + (255,), anchor="ra", font=SANS)
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    outs = []
    for key, fn in (("M", make_m), ("N", make_n), ("O", make_o)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第6弾{key}_11月9日蠍座新月.png"))
        outs.append(im)
    sm = Image.new("RGB", (3 * 380, 230), (255, 255, 255))
    for i, im in enumerate(outs):
        sm.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    sm.save(os.path.join(OUT, "第6弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 3))
    for i, im in enumerate(outs):
        big.paste(im, (0, i * 720))
    big.resize((960, 1620)).save(os.path.join(OUT, "第6弾_3案まとめ.png"))
    print("ok")
