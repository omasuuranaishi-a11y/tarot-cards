"""11/9 蠍座新月のサムネイル案 第12弾：第11弾の蠍（青銅の写真）が「こわい」ので、星座の蠍座にする（1280×720）。

蠍座の星（おおよその赤経・赤緯から形を作る）を金の細い線でつなぎ、心臓の星アンタレスだけ赤く光らせる。
女性は改琦「緑珠小像」（1823年、Met のパブリックドメイン）。
  U2 灰青の空：女性の上の空に大きな蠍座
  V2 生成りの紙：女性の手元（緑の玉）から、空へ蠍座が広がる
    python3 make_thumbnails_v12.py
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_thumbnails_v11 as v11  # noqa: E402
from make_thumbnails_v10 import small_seal, vcol  # noqa: E402

OUT = os.path.join(HERE, "thumbnails")
W, H = 1280, 720
F, BRUSH, SANS = v11.F, v11.BRUSH, v11.SANS
CREAM, VERM, INK, DUSTY, SAGE = v11.CREAM, v11.VERM, v11.INK, v11.DUSTY, v11.SAGE

# 蠍座の主な星：名前, 赤経(時), 赤緯(度), 明るさ（大きいほど明るい）
STARS = {
    "beta": (16.09, -19.8, 2.6), "delta": (16.01, -22.6, 2.3), "pi": (15.98, -26.1, 2.9), "rho": (15.95, -29.2, 3.9),
    "sigma": (16.35, -25.6, 2.9), "alpha": (16.49, -26.4, 1.0), "tau": (16.60, -28.2, 2.8),
    "epsilon": (16.84, -34.3, 2.3), "mu": (16.86, -38.0, 3.0), "zeta": (16.91, -42.4, 3.6), "eta": (17.20, -43.2, 3.3),
    "theta": (17.62, -43.0, 1.9), "iota": (17.79, -40.1, 3.0), "kappa": (17.71, -39.0, 2.4),
    "lambda": (17.56, -37.1, 1.6), "upsilon": (17.51, -37.3, 2.7),
}
LINES = [("beta", "delta"), ("delta", "pi"), ("pi", "rho"), ("delta", "sigma"), ("sigma", "alpha"), ("alpha", "tau"),
         ("tau", "epsilon"), ("epsilon", "mu"), ("mu", "zeta"), ("zeta", "eta"), ("eta", "theta"), ("theta", "iota"),
         ("iota", "kappa"), ("kappa", "lambda"), ("lambda", "upsilon")]


def scorpius(width, line=(232, 198, 120), star=(255, 248, 226), antares=(255, 96, 60)):
    """蠍座の星座の絵（透明の背景）。南の空を見上げた向き（東が左）。"""
    pts = {k: (-ra * 15, -dec) for k, (ra, dec, _) in STARS.items()}
    xs, ys = [p[0] for p in pts.values()], [p[1] for p in pts.values()]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    s = (width - 80) / (x1 - x0)
    h = int((y1 - y0) * s) + 80
    P = {k: ((x - x0) * s + 40, (y - y0) * s + 40) for k, (x, y) in pts.items()}
    S = 2
    im = Image.new("RGBA", (width * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for a, b in LINES:
        d.line((P[a][0] * S, P[a][1] * S, P[b][0] * S, P[b][1] * S), fill=line + (210,), width=3 * S)
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for k, (x, y) in P.items():
        mag = STARS[k][2]
        r = (11 - 2.2 * mag) * S
        col = antares if k == "alpha" else star
        gd.ellipse((x * S - r * 3, y * S - r * 3, x * S + r * 3, y * S + r * 3), fill=col + (90,))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8 * S)))
    for k, (x, y) in P.items():
        mag = STARS[k][2]
        r = (11 - 2.2 * mag) * S
        col = antares if k == "alpha" else star
        if k == "alpha":
            r *= 1.5
        d.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=col + (255,))
        if mag < 2.5:  # 明るい星は十字の光
            L = r * 2.6
            d.line((x * S - L, y * S, x * S + L, y * S), fill=col + (200,), width=S)
            d.line((x * S, y * S - L, x * S, y * S + L), fill=col + (200,), width=S)
    return im.resize((width, h), Image.LANCZOS)


def make_u2():
    img = v11.watercolor(DUSTY, [(CREAM, 760, 560, 360, 170, 0.75), (CREAM, 1080, 600, 240, 110, 0.4),
                                 ((196, 210, 214), 420, 260, 300, 150, 0.45), (SAGE, 980, 650, 300, 120, 0.5)], seed=21)
    v11.birds(img, 5, seed=5)
    v11.place(img, v11.woman(960), 360, 30, shadow=0.28)
    sc = scorpius(430)
    img.alpha_composite(sc, (650, 10))
    vcol(img, 150, -6, "蠍座新月", 186, CREAM, step=176, font=BRUSH, stroke=5, stroke_fill=(52, 64, 80), shadow=0.45)
    d = ImageDraw.Draw(img)
    d.rectangle((1124, -10, 1262, H + 10), fill=VERM + (255,))
    d.line((1134, 0, 1134, H), fill=CREAM + (200,), width=2)
    d.line((1252, 0, 1252, H), fill=CREAM + (200,), width=2)
    vcol(img, 1193, 60, "縁が動く", 124, CREAM, step=134, font=BRUSH)
    d.text((1193, 650), "11.9", font=F(SANS, 30), fill=CREAM + (255,), anchor="mm")
    img.alpha_composite(small_seal("星読", 86), (1020, 610))
    return img


def make_v2():
    img = v11.watercolor(CREAM, [((40, 52, 78), 960, 160, 420, 230, 0.85), (SAGE, 1030, 470, 330, 300, 0.5),
                                 (DUSTY, 1180, 650, 200, 130, 0.35)], seed=22)
    v11.place(img, v11.woman(1000), 800, 10, shadow=0.25)
    sc = scorpius(380)
    img.alpha_composite(sc, (560, -10))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((22, -40), "蠍座", font=F(BRUSH, 290), fill=INK + (255,), stroke_width=3, stroke_fill=INK + (255,))
    d.text((22, 230), "新月", font=F(BRUSH, 290), fill=INK + (255,), stroke_width=3, stroke_fill=INK + (255,))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    d.rectangle((-10, 566, 800, H + 10), fill=VERM + (255,))
    d.line((0, 576, 800, 576), fill=CREAM + (200,), width=2)
    d.text((26, 646), "縁が、動き出す", font=F(BRUSH, 98), fill=CREAM + (255,), anchor="lm")
    d.text((786, 700), "11.9", font=F(SANS, 28), fill=CREAM + (255,), anchor="rs")
    img.alpha_composite(small_seal("星読", 96), (612, 446))
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for key, fn in (("U", make_u2), ("V", make_v2)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第12弾{key}_11月9日蠍座新月.png"))
        ims.append(im)
    sm = Image.new("RGB", (2 * 380, 230), (255, 255, 255))
    for i, im in enumerate(ims):
        sm.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    sm.save(os.path.join(OUT, "第12弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 2))
    for i, im in enumerate(ims):
        big.paste(im, (0, i * 720))
    big.resize((960, 1080)).save(os.path.join(OUT, "第12弾_2案まとめ.png"))
    print("ok")
