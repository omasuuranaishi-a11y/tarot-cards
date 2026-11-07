"""11/9 蠍座新月のサムネイル案 第8弾：大きな文字を画面いっぱいにかぶせる（インパクト重視、1280×720）。

参考：文字が絵の上に大きくかぶさり、グラデーションの文字に白い内ふち・濃い外ふち・まわりの光、3段の配置。
絵は第6弾M（愛染明王）・第7弾P（能面）・Q（明治の写真の女性）から、文字を抜いたものを使う。
    python3 make_thumbnails_v8.py
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_thumbnails_v6 as v6  # noqa: E402
import make_thumbnails_v7 as v7  # noqa: E402

FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "thumbnails")
W, H = 1280, 720
OLDM = os.path.join(FONTS, "ZenOldMincho-Black.ttf")


def impact_text(img, xy, s, size, grad, inner=(255, 255, 255), outer=(12, 14, 60), glow=(120, 180, 255),
                inner_w=None, outer_w=None, anchor="la", condense=0.92, max_w=None):
    """グラデーションの文字＋白い内ふち＋濃い外ふち＋まわりの光。grad は上から下への色のリスト。"""
    f = ImageFont.truetype(OLDM, size)
    iw = inner_w or max(4, size // 18)
    ow = outer_w or max(8, size // 9)
    pad = ow + 30
    tmp = Image.new("L", (int(size * len(s) * 1.2) + pad * 2, int(size * 1.5) + pad * 2), 0)
    ImageDraw.Draw(tmp).text((pad, pad), s, font=f, fill=255)
    bb = tmp.getbbox()
    tmp = tmp.crop((bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad))
    nw = int(tmp.width * condense)
    if max_w and nw > max_w:
        nw = max_w
    tmp = tmp.resize((nw, tmp.height), Image.LANCZOS)
    a = np.asarray(tmp) > 128
    core = Image.fromarray((a * 255).astype(np.uint8))
    white = core.filter(ImageFilter.MaxFilter(iw * 2 + 1))
    dark = core.filter(ImageFilter.MaxFilter(ow * 2 + 1)) if ow * 2 + 1 <= 61 else \
        core.filter(ImageFilter.GaussianBlur(ow)).point(lambda v: 255 if v > 18 else 0)
    w, h = core.size
    x, y = xy
    if anchor[0] == "r":
        x -= w
    elif anchor[0] == "m":
        x -= w // 2
    x, y = int(x), int(y)
    # まわりの光
    g = Image.new("RGBA", (w, h), glow + (0,))
    g.putalpha(dark.filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.6)))
    img.alpha_composite(g, (x, y))
    for m, col in ((dark, outer), (white, inner)):
        l_ = Image.new("RGBA", (w, h), col + (255,))
        l_.putalpha(m.filter(ImageFilter.GaussianBlur(0.8)))
        img.alpha_composite(l_, (x, y))
    # グラデーションの塗り
    bbc = core.getbbox()
    ys = np.linspace(0, 1, h)[:, None]
    t0, t1 = bbc[1] / h, bbc[3] / h
    t = np.clip((ys - t0) / max(1e-3, t1 - t0), 0, 1)
    stops = np.array(grad, np.float32)
    k = t * (len(stops) - 1)
    i0 = np.clip(np.floor(k).astype(int), 0, len(stops) - 2)
    fr = k - i0
    col = stops[i0[:, 0]] * (1 - fr) + stops[i0[:, 0] + 1] * fr
    fill = np.repeat(col[:, None, :], w, axis=1)
    fl = Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8)).convert("RGBA")
    fl.putalpha(core.filter(ImageFilter.GaussianBlur(0.6)))
    img.alpha_composite(fl, (x, y))
    return w, h


BLUE_GRAD = [(214, 232, 255), (60, 120, 255), (24, 40, 200), (120, 70, 255)]
PINK_GRAD = [(255, 236, 255), (236, 120, 255), (150, 60, 255), (60, 200, 255)]
GOLD_GRAD = [(255, 250, 220), (255, 214, 90), (230, 140, 30), (255, 220, 120)]
RED_GRAD = [(255, 236, 220), (255, 90, 70), (190, 20, 30), (255, 140, 80)]


def _no_text():
    """第6・7弾の絵の中の文字を消す"""
    v6.NO_TEXT = v7.NO_TEXT = True
    v6.vtext = v7.vtext = lambda *a, **k: None


def make_p8():
    _no_text()
    img = v7.violet_water(3)  # 能面は大きく、文字の後ろに見えるように置き直す
    v7.floating_mask(img, 330, 40, 420, waterline=0.6, seed=1)
    v7.floating_mask(img, 1110, 30, 400, waterline=0.6, seed=2)
    v7.floating_mask(img, 730, 70, 600, waterline=0.66, seed=3)
    impact_text(img, (24, 6), "11/9 蠍座新月", 96, BLUE_GRAD, outer=(14, 10, 70), glow=(140, 190, 255))
    impact_text(img, (1262, 196), "仮面を外したら", 112, BLUE_GRAD, outer=(14, 10, 70), glow=(140, 190, 255),
                anchor="ra")
    impact_text(img, (W // 2, 392), "関係が動き出す", 196, PINK_GRAD, outer=(30, 6, 70), glow=(200, 150, 255),
                anchor="ma", max_w=1250)
    return img


def make_q8():
    _no_text()
    img = v7.make_q()
    impact_text(img, (24, 6), "11/9 蠍座新月", 96, GOLD_GRAD, outer=(60, 18, 10), glow=(255, 200, 120))
    impact_text(img, (24, 196), "あの人との縁", 116, GOLD_GRAD, outer=(60, 18, 10), glow=(255, 200, 120))
    impact_text(img, (W // 2, 392), "もう一歩深まる", 196, RED_GRAD, outer=(50, 6, 10), glow=(255, 160, 120),
                anchor="ma", max_w=1250)
    return img


def make_m8():
    _no_text()
    img = v6.make_m(cx=920, cy=330, R=330)  # 明王の顔が文字にかからないよう右に寄せる
    impact_text(img, (24, 6), "11/9 蠍座新月", 96, GOLD_GRAD, outer=(40, 4, 8), glow=(255, 150, 100))
    impact_text(img, (24, 196), "愛と執着の先で", 104, GOLD_GRAD, outer=(40, 4, 8), glow=(255, 150, 100))
    impact_text(img, (W // 2, 392), "縁が動き出す", 206, RED_GRAD, outer=(40, 4, 8), glow=(255, 170, 120),
                anchor="ma", max_w=1250)
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for key, fn in (("P", make_p8), ("Q", make_q8), ("M", make_m8)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第8弾{key}_11月9日蠍座新月.png"))
        ims.append(im)
    sm = Image.new("RGB", (3 * 380, 230), (255, 255, 255))
    for i, im in enumerate(ims):
        sm.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    sm.save(os.path.join(OUT, "第8弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 3))
    for i, im in enumerate(ims):
        big.paste(im, (0, i * 720))
    big.resize((960, 1620)).save(os.path.join(OUT, "第8弾_3案まとめ.png"))
    print("ok")
