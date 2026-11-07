"""11/9 蠍座新月のサムネイル案 第11弾：中国の美人画の女性と蠍（1280×720）。

参考の雰囲気（いま活躍中の作家さんの絵なので、絵柄はまねない）：くすんだ灰青・セージグリーン・生成り・朱、
水彩のにじみ、白い鳥や雲。素材はメトロポリタン美術館のパブリックドメイン（CC0）：
  女性＝改琦「緑珠小像」（1823年、清。緑の衣に白い鶴の模様）
  蠍＝モチェ文化の青銅の蠍（6〜7世紀、緑青の青緑）
文字は特大の筆文字と朱の札・落款（おますさんの印）。
  U 灰青の空：雲の中に女性、右上から青銅の蠍が近づく、左に縦の特大の筆文字、右に朱の札。
  V 生成りの紙：右に女性、手元へ這いのぼる蠍、左に特大の筆文字「蠍座／新月」、下に朱の帯。
    python3 make_thumbnails_v11.py
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_thumbnails_v10 import small_seal, vcol  # noqa: E402

FONTS = os.path.join(HERE, "..", "fonts")
PD = os.path.join(HERE, "public_domain")
OUT = os.path.join(HERE, "thumbnails")
W, H = 1280, 720
BRUSH = os.path.join(FONTS, "YujiSyuku-Regular.ttf")
SANS = os.path.join(FONTS, "ZenKakuGothicNew-Black.ttf")

DUSTY = (118, 146, 168)
SAGE = (150, 172, 152)
CREAM = (242, 234, 216)
VERM = (204, 62, 42)
INK = (34, 32, 36)


def F(path, size):
    return ImageFont.truetype(path, size)


def watercolor(base, blots, seed=0, grain=5):
    """水彩のにじみ：地の色に、やわらかい色のしみと、紙の目。blots = [(色, 中心x, 中心y, 半径x, 半径y, 濃さ)]"""
    rng = np.random.default_rng(seed)
    img = np.ones((H, W, 3), np.float32) * np.array(base, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for col, cx, cy, rx, ry, k in blots:
        n = rng.random((H // 40 + 1, W // 40 + 1)).astype(np.float32)
        n = np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC), np.float32)
        r = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 + (n - 0.5) * 0.9
        m = np.clip(1.2 - r, 0, 1) ** 1.4 * k
        edge = np.exp(-((r - 1.0) ** 2) / 0.01) * 0.12 * k   # にじみのふちが少し濃くなる
        m = np.clip(m + edge, 0, 1)[..., None]
        img = img * (1 - m) + np.array(col, np.float32) * m
    n = rng.normal(0, grain, (H // 2, W // 2)).astype(np.float32)
    img += np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    fib = rng.normal(0, grain * 0.5, (H // 8, W)).astype(np.float32)
    img += np.asarray(Image.fromarray(fib).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def place(img, layer, x, y, shadow=0.35, blur=16, off=(10, 14)):
    if shadow:
        sh = Image.new("RGBA", layer.size, (20, 20, 30, 0))
        sh.putalpha(layer.split()[3].point(lambda v: int(v * shadow)))
        big = Image.new("RGBA", img.size, (0, 0, 0, 0))
        big.alpha_composite(sh, (int(x + off[0]), int(y + off[1])))
        img.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)))
    big = Image.new("RGBA", img.size, (0, 0, 0, 0))
    big.alpha_composite(layer, (int(x), int(y))) if x >= 0 and y >= 0 else None
    if x < 0 or y < 0:
        big.paste(layer, (int(x), int(y)), layer)
    img.alpha_composite(big)


def woman(height):
    w = Image.open(os.path.join(PD, "luzhu_cut.png")).convert("RGBA")
    return w.resize((int(w.width * height / w.height), height), Image.LANCZOS)


def scorpion(height, angle=0, flip=False):
    s = Image.open(os.path.join(PD, "bronze_scorpion_cut.png")).convert("RGBA")
    s = s.resize((int(s.width * height / s.height), height), Image.LANCZOS)
    if flip:
        s = s.transpose(Image.FLIP_LEFT_RIGHT)
    # 写真の青銅を、絵になじむようにする：色を少し落ち着かせ、細かい凹凸をならし、紙の目を重ねる
    a_ = s.split()[3]
    rgb = s.convert("RGB").filter(ImageFilter.MedianFilter(5))
    arr = np.asarray(rgb).astype(np.float32)
    lum = arr.mean(2, keepdims=True)
    arr = lum + (arr - lum) * 0.8
    arr = arr * 0.92 + np.array([236, 226, 206], np.float32) * 0.08
    rng = np.random.default_rng(1)
    n = rng.normal(0, 6, arr.shape[:2]).astype(np.float32)[..., None]
    rgb = Image.fromarray(np.clip(arr + n, 0, 255).astype(np.uint8))
    s = rgb.convert("RGBA")
    s.putalpha(a_)
    return s.rotate(angle, expand=True, resample=Image.BICUBIC)


def birds(img, n=7, seed=3, color=(250, 246, 238)):
    """遠くを飛ぶ白い鳥（細い筆の「く」の字）"""
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y, s = rng.uniform(520, 1150), rng.uniform(40, 300), rng.uniform(10, 22)
        d.line([(x - s, y - s * 0.35), (x - s * 0.3, y - s * 0.1), (x, y + s * 0.15)], fill=color + (230,), width=3)
        d.line([(x, y + s * 0.15), (x + s * 0.3, y - s * 0.1), (x + s, y - s * 0.4)], fill=color + (230,), width=3)
    img.alpha_composite(lay)


# ---- U 灰青の空 ----
def make_u():
    img = watercolor(DUSTY, [(CREAM, 760, 560, 360, 170, 0.75), (CREAM, 1100, 140, 260, 110, 0.55),
                             ((196, 210, 214), 420, 260, 300, 150, 0.45), (SAGE, 980, 650, 300, 120, 0.5)], seed=21)
    birds(img, 6, seed=5)
    wm = woman(960)
    place(img, wm, 360, 30, shadow=0.28)
    sc = scorpion(430, angle=-38)
    place(img, sc, 760, -40, shadow=0.45, blur=12, off=(12, 18))
    vcol(img, 150, -6, "蠍座新月", 186, CREAM, step=176, font=BRUSH, stroke=5, stroke_fill=(52, 64, 80), shadow=0.45)
    d = ImageDraw.Draw(img)
    d.rectangle((1124, -10, 1262, H + 10), fill=VERM + (255,))
    d.line((1134, 0, 1134, H), fill=CREAM + (200,), width=2)
    d.line((1252, 0, 1252, H), fill=CREAM + (200,), width=2)
    vcol(img, 1193, 60, "縁が動く", 124, CREAM, step=134, font=BRUSH)
    d.text((1193, 650), "11.9", font=F(SANS, 30), fill=CREAM + (255,), anchor="mm")
    img.alpha_composite(small_seal("星読", 86), (1020, 610))
    return img


# ---- V 生成りの紙 ----
def make_v():
    img = watercolor(CREAM, [(SAGE, 1030, 380, 330, 380, 0.55), ((196, 212, 206), 700, 120, 260, 120, 0.4),
                             (DUSTY, 1180, 650, 200, 130, 0.35)], seed=22)
    birds(img, 5, seed=9, color=(255, 255, 255))
    wm = woman(1000)
    place(img, wm, 800, 10, shadow=0.25)
    sc = scorpion(360, angle=28, flip=True)
    place(img, sc, 560, 250, shadow=0.45, blur=12, off=(12, 16))
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
    for key, fn in (("U", make_u), ("V", make_v)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第11弾{key}_11月9日蠍座新月.png"))
        ims.append(im)
    sm = Image.new("RGB", (2 * 380, 230), (255, 255, 255))
    for i, im in enumerate(ims):
        sm.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    sm.save(os.path.join(OUT, "第11弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 2))
    for i, im in enumerate(ims):
        big.paste(im, (0, i * 720))
    big.resize((960, 1080)).save(os.path.join(OUT, "第11弾_2案まとめ.png"))
    print("ok")
