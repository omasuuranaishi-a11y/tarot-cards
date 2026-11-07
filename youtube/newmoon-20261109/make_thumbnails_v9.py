"""11/9 蠍座新月のサムネイル案 第9弾：文字が画面からはみ出しそうな特大の型（1280×720）。

型：左右に特大の1文字（白・極太明朝）、その手前の真ん中に絵、下の段は横幅いっぱいに詰めた極太の言葉で
1語だけ赤、画面の下の端に少しかかる。左上に小さな赤い札で日付。
絵：P 能面（紫の水面）／M 愛染明王（紅）／Q 明治の写真の女性（藍）。どれも Met のパブリックドメイン。
    python3 make_thumbnails_v9.py
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_thumbnails_v6 as v6  # noqa: E402
import make_thumbnails_v7 as v7  # noqa: E402

FONTS = os.path.join(HERE, "..", "fonts")
PD = os.path.join(HERE, "public_domain")
OUT = os.path.join(HERE, "thumbnails")
W, H = 1280, 720
OLDM = os.path.join(FONTS, "ZenOldMincho-Black.ttf")
SANS = os.path.join(FONTS, "ZenKakuGothicNew-Black.ttf")
RED = (214, 20, 30)
GOLD = (236, 196, 110)


def glyph(ch, size, fill=(255, 255, 255), condense=1.0, stroke=0, stroke_fill=(0, 0, 0)):
    f = ImageFont.truetype(OLDM, size)
    pad = stroke + 20
    tmp = Image.new("RGBA", (int(size * 1.4) + pad * 2, int(size * 1.5) + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((pad, pad), ch, font=f, fill=fill + (255,), stroke_width=stroke,
                             stroke_fill=stroke_fill + (255,))
    tmp = tmp.crop(tmp.getbbox())
    if condense != 1.0:
        tmp = tmp.resize((int(tmp.width * condense), tmp.height), Image.LANCZOS)
    return tmp


def put_shadow(img, layer, x, y, blur=10, alpha=0.6, off=(8, 10)):
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sh.putalpha(layer.split()[3].point(lambda v: int(v * alpha)))
    big = Image.new("RGBA", img.size, (0, 0, 0, 0))
    big.alpha_composite(sh, (int(x + off[0]), int(y + off[1])))
    img.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)))
    img.alpha_composite(layer, (int(x), int(y)))


def giant_pair(img, left, right, height=500, top=-14, fill=(255, 255, 255)):
    """左右の特大の1文字。高さ height にそろえ、画面の端すれすれに置く。"""
    for ch, side in ((left, "l"), (right, "r")):
        g = glyph(ch, 600, fill)
        g = g.resize((int(g.width * height / g.height), height), Image.LANCZOS)
        x = -6 if side == "l" else W - g.width + 6
        put_shadow(img, g, x, top, blur=12, alpha=0.55, off=(10, 12))


def bottom_line(img, parts, y=500, height=230, margin=14):
    """下の段：横幅いっぱい（左右 margin まで）に詰めた極太の言葉。parts = [(文字, 赤か)]
    1文字ずつ同じ幅のマスに置く（かなの小さい字や濁点がとなりの字にぶつからないように）。"""
    size, stroke = 300, 9
    f = ImageFont.truetype(OLDM, size)
    chars = [(ch, red) for s_, red in parts for ch in s_]
    cell = int(size * 0.98)
    row = Image.new("RGBA", (cell * len(chars) + stroke * 4, int(size * 1.3)), (0, 0, 0, 0))
    d = ImageDraw.Draw(row)
    for i, (ch, red) in enumerate(chars):
        fill = RED if red else (16, 12, 14)
        d.text((stroke * 2 + i * cell + cell / 2, size * 0.62), ch, font=f, fill=fill + (255,), anchor="mm",
               stroke_width=stroke, stroke_fill=(255, 255, 255, 255))
    row = row.crop(row.getbbox())
    row = row.resize((W - margin * 2, height), Image.LANCZOS)
    put_shadow(img, row, margin, y, blur=8, alpha=0.6, off=(6, 8))


def date_tag(img, s="11.9 新月", xy=(472, 18)):
    f = ImageFont.truetype(SANS, 44)
    d = ImageDraw.Draw(img)
    w = d.textlength(s, font=f)
    x, y = xy
    d.rectangle((x, y, x + w + 32, y + 66), fill=RED + (255,))
    d.text((x + 16, y + 33), s, font=f, fill=(255, 255, 255, 255), anchor="lm")


# ---- P 能面 ----
def make_p9():
    img = v7.violet_water(5)
    giant_pair(img, "蠍", "座")
    v7.floating_mask(img, 640, 30, 520, waterline=0.72, seed=3)
    bottom_line(img, [("仮面を外すと", False), ("関係が動く", True)])
    date_tag(img)
    return img


# ---- M 愛染明王 ----
def make_m9():
    img = v6.paper((70, 12, 18), 91, grain=5, vign=0.45)
    cx, cy, R = 640, 268, 248
    d = ImageDraw.Draw(img)
    for k in range(72):
        a = 2 * math.pi * k / 72
        r0, r1 = R + 18, R + (130 if k % 2 == 0 else 80)
        d.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
               fill=(120, 30, 34, 255), width=3)
    giant_pair(img, "蠍", "座")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((cx - R - 40, cy - R - 40, cx + R + 40, cy + R + 40), fill=(255, 120, 80, 110))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30)))
    ai = Image.open(os.path.join(PD, "aizen_circle.png")).convert("RGBA").resize((R * 2, R * 2), Image.LANCZOS)
    a_ = ai.split()[3]
    rgb = ImageOps.autocontrast(ai.convert("RGB"), cutoff=1, preserve_tone=True)
    rgb = ImageEnhance.Brightness(ImageEnhance.Color(rgb).enhance(1.2)).enhance(1.12)
    ai = rgb.convert("RGBA")
    ai.putalpha(a_)
    put_shadow(img, ai, cx - R, cy - R, blur=16, alpha=0.6, off=(10, 14))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2), outline=GOLD + (255,), width=6)
    bottom_line(img, [("愛と執着の先で", False), ("縁が動く", True)])
    date_tag(img)
    return img


# ---- Q 明治の女性 ----
def make_q9():
    img = v6.paper((22, 36, 74), 95, grain=5, vign=0.4)   # 藍
    giant_pair(img, "蠍", "座")
    ph = Image.open(os.path.join(PD, "woman_1870s.jpg")).crop((420, 480, 1680, 2100))
    ph = v7.sepia_keep_red(ph)
    ph = ph.resize((int(ph.width * 560 / ph.height), 560), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", ph.size, 0)
    ImageDraw.Draw(m).ellipse((ph.width * 0.04, ph.height * 0.02, ph.width * 0.96, ph.height * 1.2), fill=255)
    ph.putalpha(m.filter(ImageFilter.GaussianBlur(26)))
    put_shadow(img, ph, (W - ph.width) // 2, 6, blur=20, alpha=0.5, off=(0, 10))
    br = v6.branch(seed=7, scale=0.8)
    img.alpha_composite(br.transpose(Image.FLIP_LEFT_RIGHT), (680, 200))
    bottom_line(img, [("あの人との縁が", False), ("深まる", True)])
    date_tag(img)
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for key, fn in (("P", make_p9), ("M", make_m9), ("Q", make_q9)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第9弾{key}_11月9日蠍座新月.png"))
        ims.append(im)
    sm = Image.new("RGB", (3 * 380, 230), (255, 255, 255))
    for i, im in enumerate(ims):
        sm.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    sm.save(os.path.join(OUT, "第9弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 3))
    for i, im in enumerate(ims):
        big.paste(im, (0, i * 720))
    big.resize((960, 1620)).save(os.path.join(OUT, "第9弾_3案まとめ.png"))
    print("ok")
