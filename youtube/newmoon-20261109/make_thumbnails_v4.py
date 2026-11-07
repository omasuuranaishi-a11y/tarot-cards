"""11/9 蠍座新月のサムネイル案 第4弾：新聞の見出しのような極太明朝（1280×720）。

おますさんが一番参考にしたい雰囲気（極太の明朝が画面いっぱい、白・赤・黒に黄の差し色、真ん中に月）から
「型の考え方」だけを借り、見た目はおますさんの印に置きかえる（まねにならないように）：
  破れた紙 → 筆の円相、真っ白 → 生成りの和紙、真っ赤 → 朱、写真の人物 → 使わない、
  下の帯の決まり文句 → 使わない、かわりに朱の落款「星読」。
  G 和紙：左に黒の「蠍座／新月」、右に朱の札に白の「動き／出す」、真ん中に円相と新月
  H 朱：上いっぱいに白の「蠍座新月」、下に円相と新月、右に「関係が／動き出す」
  I 墨：左に朱の札の「蠍座」、右に生成りの文字（12星座別のシリーズにも使える型）
    python3 make_thumbnails_v4.py
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_thumbnails_v2 import enso, paper  # noqa: E402

FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "thumbnails")
W, H = 1280, 720
MIN = os.path.join(FONTS, "ZenOldMincho-Black.ttf")
KAKU = os.path.join(FONTS, "ZenKakuGothicNew-Black.ttf")
SYUKU = os.path.join(FONTS, "YujiSyuku-Regular.ttf")

WASHI = (240, 232, 214)
SUMI = (24, 20, 20)
SHU = (196, 44, 32)
YAMABUKI = (248, 196, 40)


def headline(s, size, color, condense=0.82, stroke=0, stroke_color=None, vertical=False, gap=0.92):
    """極太明朝の見出し。横を少し詰めた（長体）文字の画像を返す。"""
    f = ImageFont.truetype(MIN, size)
    chars = s if vertical else [s]
    tiles = []
    for c in chars:
        tmp = Image.new("RGBA", (int(size * (len(c) + 1) * 1.1), int(size * 1.6)), (0, 0, 0, 0))
        if not stroke:  # 同じ色のふちで、もうひと回り太くする（見出しの極太の感じ）
            stroke, stroke_color = max(2, size // 38), color
        ImageDraw.Draw(tmp).text((size * 0.2, size * 0.2), c, font=f, fill=color + (255,), stroke_width=stroke,
                                 stroke_fill=(stroke_color or color) + (255,))
        tmp = tmp.crop(tmp.getbbox())
        tmp = tmp.resize((max(1, int(tmp.width * condense)), tmp.height), Image.LANCZOS)
        tiles.append(tmp)
    if not vertical:
        return tiles[0]
    w = max(t.width for t in tiles)
    step = int(size * gap)
    out = Image.new("RGBA", (w, step * (len(tiles) - 1) + tiles[-1].height), (0, 0, 0, 0))
    for i, t in enumerate(tiles):
        out.alpha_composite(t, ((w - t.width) // 2, i * step))
    return out


def ink_rough(im, seed=0, amount=0.03):
    """インクのかすれ：文字のふちを少しだけ荒らして、印刷のような質感にする"""
    rng = np.random.default_rng(seed)
    a = np.asarray(im.split()[3]).astype(np.float32)
    n = rng.random(a.shape).astype(np.float32)
    a = np.where((a > 0) & (a < 250) & (n < 0.5), a * (1 - amount * 4), a)
    a = np.where((a >= 250) & (n < amount * 0.15), 150, a)
    im = im.copy()
    im.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
    return im


def moon(d, phase="new", seed=7):
    """月の球（新月：ほとんど影で、ふちだけ光る）。表面の模様はノイズで描く。"""
    rng = np.random.default_rng(seed)
    S = 2
    n = d * S
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    cx = cy = n / 2
    r = n / 2 - 2
    dx, dy = (xx - cx) / r, (yy - cy) / r
    rr = dx * dx + dy * dy
    inside = rr <= 1
    nz = np.sqrt(np.clip(1 - rr, 0, 1))
    tex = np.zeros((n, n), np.float32)
    for k, amp in ((8, 0.5), (24, 0.3), (64, 0.2)):
        g = rng.random((k, k)).astype(np.float32)
        tex += amp * np.asarray(Image.fromarray(g).resize((n, n), Image.BICUBIC), np.float32)
    for _ in range(40):  # クレーター
        x0, y0, rad = rng.random() * n, rng.random() * n, rng.random() * n * 0.06 + n * 0.01
        m = ((xx - x0) ** 2 + (yy - y0) ** 2) < rad ** 2
        tex = np.where(m, tex * 0.85, tex)
    lx, ly, lz = 0.85, -0.25, -0.45  # 光は奥（新月：太陽は月の向こう側）
    lam = np.clip(dx * lx + dy * ly + nz * lz, 0, 1)
    rim = np.clip((rr - 0.82) / 0.18, 0, 1) ** 2 * np.clip(dx * 0.7 - dy * 0.3 + 0.4, 0, 1)
    earthshine = 0.10 + 0.05 * nz
    base = (earthshine + 0.9 * lam) * (0.75 + 0.5 * tex)
    col = np.stack([base * 190 + rim * 255, base * 196 + rim * 226, base * 214 + rim * 170], -1)
    col = np.clip(col, 0, 255)
    a = (inside * 255).astype(np.uint8)
    img = Image.fromarray(np.concatenate([col.astype(np.uint8), a[..., None]], -1))
    img = img.resize((d, d), Image.LANCZOS)
    glow = Image.new("RGBA", (d + 120, d + 120), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((60, 60, d + 60, d + 60), fill=(255, 226, 170, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    glow.alpha_composite(img, (60, 60))
    return glow


def seal(w=96, h=158, color=SHU, seed=2):
    """朱の落款（陰刻）：「星読」"""
    S = 3
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), 10 * S, fill=color + (255,))
    f = ImageFont.truetype(SYUKU, int(w * 0.78 * S))
    for i, c in enumerate("星読"):
        d.text((w * S / 2, h * S * (0.28 + 0.46 * i)), c, font=f, fill=(0, 0, 0, 0), anchor="mm")
    a = np.asarray(im.split()[3]).astype(np.float32)
    rng = np.random.default_rng(seed)
    n = np.asarray(Image.fromarray((rng.random((h, w)) * 255).astype(np.uint8)).resize((w * S, h * S), Image.BICUBIC), np.float32)
    a = np.where(n < 30, a * 0.3, a)  # 朱肉のかすれ
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im.resize((w, h), Image.LANCZOS).rotate(-3, expand=True, resample=Image.BICUBIC)


def small(img, xy, s, size, color, anchor="la"):
    ImageDraw.Draw(img).text(xy, s, font=ImageFont.truetype(KAKU, size), fill=color + (255,), anchor=anchor)


def put(img, im, x, y, anchor="la"):
    if anchor == "ra":
        x -= im.width
    elif anchor == "ma":
        x -= im.width // 2
    img.alpha_composite(im, (int(x), int(y)))


def enso_moon(img, cx, cy, d, ink=SUMI, seed=5, moon_scale=0.62):
    m = moon(int(d * moon_scale))
    put(img, m, cx - m.width / 2, cy - m.height / 2)
    e = enso(d, color=ink, seed=seed, gap=38)
    put(img, e, cx - e.width / 2, cy - e.height / 2)


def make_g():
    img = paper(WASHI, 71, grain=6)
    put(img, ink_rough(headline("蠍座", 270, SUMI), 1), 26, 8)
    put(img, ink_rough(headline("新月", 270, SUMI), 2), 26, 300)
    d = ImageDraw.Draw(img)
    d.rectangle((900, 0, W, 560), fill=SHU + (255,))
    put(img, headline("動き", 230, (255, 250, 240)), 1090, 26, "ma")
    put(img, headline("出す", 230, (255, 250, 240)), 1090, 290, "ma")
    enso_moon(img, 660, 300, 330)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 580, W, H), fill=SUMI + (255,))
    rel = headline("見直した関係が", 104, (255, 250, 240), condense=0.86)
    put(img, rel, 34, 600)
    small(img, (1250, 612), "11.9 16:02", 40, YAMABUKI, "ra")
    small(img, (1250, 664), "11/14 金星・水星 順行へ", 30, (255, 250, 240), "ra")
    put(img, seal(), 772, 424)
    return img


def make_h():
    img = paper(SHU, 72, grain=7)
    head = headline("蠍座新月", 250, (255, 250, 240), condense=0.8)
    put(img, ink_rough(head, 3), W / 2, 6, "ma")
    cream = paper(WASHI, 73, grain=5)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((90, 290, 500, 700), fill=255)
    img.paste(cream, (0, 0), m)
    enso_moon(img, 295, 495, 380)
    put(img, headline("関係が", 150, SUMI, condense=0.84), 1240, 300, "ra")
    y2 = headline("動き出す", 170, YAMABUKI, condense=0.8, stroke=12, stroke_color=SUMI)
    put(img, y2, 1244, 470, "ra")
    small(img, (560, 318), "11.9 16:02", 38, (255, 236, 200))
    put(img, seal(84, 138, color=(255, 246, 232)), 556, 380)
    return img


def make_i():
    img = paper(SUMI, 74, grain=5)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 430, H), fill=SHU + (255,))
    put(img, headline("蠍座", 300, (255, 250, 240), vertical=True, gap=0.95, condense=0.95), 215, 20, "ma")
    small(img, (470, 46), "11.9 16:02  新月", 44, YAMABUKI)
    put(img, headline("見直した", 150, WASHI, condense=0.82), 466, 120)
    put(img, headline("関係が", 150, WASHI, condense=0.82), 466, 290)
    put(img, headline("動き出す", 170, YAMABUKI, condense=0.8), 466, 470)
    enso_moon(img, 1110, 210, 250, ink=(240, 232, 214), seed=9)
    put(img, seal(80, 132), 1170, 560)
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    outs = []
    for key, fn in (("G", make_g), ("H", make_h), ("I", make_i)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第4弾{key}_11月9日蠍座新月.png"))
        outs.append(im)
    smallsheet = Image.new("RGB", (3 * 380, 230), (255, 255, 255))
    for i, im in enumerate(outs):
        smallsheet.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    smallsheet.save(os.path.join(OUT, "第4弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 3))
    for i, im in enumerate(outs):
        big.paste(im, (0, i * 720))
    big.resize((960, 1620)).save(os.path.join(OUT, "第4弾_3案まとめ.png"))
    print("ok")
