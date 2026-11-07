"""11/9 蠍座新月のサムネイル案 第5弾：中国・台湾・韓国のいまのグラフィックの雰囲気（1280×720）。

おますさんの好み（心理学・心理占星術・仏教・台湾/韓国デザイン、エンジェル系でも浮世絵でもない）と、
参考にした雰囲気（2〜3色の重ね刷り、巨大な宋体の漢字、1色のモチーフ、はんこと小さな英文、台湾・香港のレトロなラベル）から。
  J 蛍光ピンク×青：生成りの紙に、網点の青い新月と、重ね刷りのピンクの縦書き「蠍座新月」
  K 黒×蛍光グリーン：黒の地に緑の網点の蓮、ピンクの縦書き「動き出す」、大きな日付
  L 台湾レトロのラベル：生成りに朱の1色、二重の枠、真ん中に蓮の紋章、丸の中の1文字
色の重なりは「乗算」で、版ずれ（数ピクセルのずれ）とインクのムラもつける。
    python3 make_thumbnails_v5.py
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_thumbnails_v2 import lotus  # noqa: E402
from make_thumbnails_v4 import moon  # noqa: E402

FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "thumbnails")
W, H = 1280, 720
SONG = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc"   # 宋体の極太
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
OLDM = os.path.join(FONTS, "ZenOldMincho-Black.ttf")
DELA = os.path.join(FONTS, "DelaGothicOne-Regular.ttf")

PAPER = (241, 236, 224)
PINK = (255, 72, 176)       # 蛍光ピンク
BLUE = (0, 120, 191)        # リソの青
GREEN = (0, 222, 120)       # 蛍光グリーン
BLACK = (24, 22, 26)
SHU = (214, 46, 38)


def F(path, size, idx=0):
    return ImageFont.truetype(path, size, index=idx) if path.endswith(".ttc") else ImageFont.truetype(path, size)


# ---- 紙とインク ----
class Print:
    """紙の上に、インクを乗算で重ねていく。"""

    def __init__(self, paper_color, seed=0):
        rng = np.random.default_rng(seed)
        base = np.ones((H, W, 3), np.float32) * np.array(paper_color, np.float32)
        n = rng.normal(0, 5, (H // 2, W // 2)).astype(np.float32)
        n = np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC), np.float32)[..., None]
        self.img = np.clip(base + n, 0, 255)
        self.rng = rng

    def ink(self, mask, color, offset=(0, 0), grain=0.12, opacity=0.95):
        """mask: L画像（255=インク）。乗算で重ねる。offset で版ずれ。"""
        m = np.asarray(mask, np.float32) / 255
        if offset != (0, 0):
            m = np.roll(m, offset[1], axis=0)
            m = np.roll(m, offset[0], axis=1)
        if grain:  # インクのムラ
            g = self.rng.random((H // 3, W // 3)).astype(np.float32)
            g = np.asarray(Image.fromarray(g).resize((W, H), Image.BICUBIC), np.float32)
            m = m * (1 - grain + grain * g)
        m = (m * opacity)[..., None]
        c = np.array(color, np.float32) / 255
        self.img = self.img * (1 - m + m * c)

    def image(self):
        return Image.fromarray(np.clip(self.img, 0, 255).astype(np.uint8)).convert("RGBA")


def blank():
    return Image.new("L", (W, H), 0)


def text_mask(s, font, xy, anchor="la", vertical=False, step=None, condense=1.0):
    m = blank()
    if not vertical:
        if condense == 1.0:
            ImageDraw.Draw(m).text(xy, s, font=font, fill=255, anchor=anchor)
            return m
        tmp = Image.new("L", (int(font.size * len(s) * 1.3), int(font.size * 1.6)), 0)
        ImageDraw.Draw(tmp).text((font.size * 0.1, font.size * 0.1), s, font=font, fill=255)
        tmp = tmp.crop(tmp.getbbox())
        tmp = tmp.resize((int(tmp.width * condense), tmp.height), Image.LANCZOS)
        x, y = xy
        if anchor == "ra":
            x -= tmp.width
        elif anchor == "ma":
            x -= tmp.width // 2
        m.paste(tmp, (int(x), int(y)))
        return m
    step = step or font.size
    d = ImageDraw.Draw(m)
    for i, ch in enumerate(s):
        d.text((xy[0], xy[1] + i * step), ch, font=font, fill=255, anchor="mt")
    return m


def halftone(gray, cell=9, angle=22, gamma=1.0):
    """グレーの画像（0=白〜255=濃い）を、網点のマスクにする。"""
    g = np.asarray(gray.convert("L").resize((W, H)), np.float32) / 255
    g = g ** gamma
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(angle)
    u = (xx * math.cos(a) + yy * math.sin(a)) / cell
    v = (-xx * math.sin(a) + yy * math.cos(a)) / cell
    du, dv = u - np.round(u), v - np.round(v)
    dist = np.sqrt(du * du + dv * dv)           # 0〜0.707
    r = np.sqrt(g / math.pi) * 1.05             # 濃さ → 点の半径
    m = np.clip((r - dist) * cell * 1.5 + 0.5, 0, 1)
    return Image.fromarray((m * 255).astype(np.uint8))


def place(layer, x, y):
    """RGBA や L の画像を、画面サイズの L マスクに置く"""
    m = blank()
    src = layer.split()[3] if layer.mode == "RGBA" else layer
    m.paste(src, (int(x), int(y)))
    return m


def moon_gray(d, cx, cy):
    """新月の球をグレーにして（影ほど濃い＝インクが多い）、画面の位置に置く"""
    mo = moon(d)
    a = np.asarray(mo.split()[3], np.float32) / 255
    lum = np.asarray(mo.convert("L"), np.float32) / 255
    dark = (1 - lum) * a                     # 影ほど濃く
    rim = np.clip(lum - 0.55, 0, 1) * a     # 光るふちは白く抜く
    # 網点に表情を出す：右上（光の来る側）ほど点を小さく、ふちは白く抜く
    h_, w_ = a.shape
    yy, xx = np.mgrid[0:h_, 0:w_].astype(np.float32)
    shade = 0.35 + 0.65 * np.clip(1 - (xx / w_ - 0.15) * 0.9 + (yy / h_ - 0.5) * 0.5, 0, 1)
    val = np.clip(dark * shade - rim * 2.5, 0, 1)
    g = Image.fromarray((val * 255).astype(np.uint8))
    canvas = blank()
    canvas.paste(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
    return canvas


def circle_seal(text, d, font_path=SONG, ring=True):
    """丸い印章（白抜きの文字）。L マスクで返す。"""
    S = 3
    m = Image.new("L", (d * S, d * S), 0)
    dr = ImageDraw.Draw(m)
    dr.ellipse((0, 0, d * S - 1, d * S - 1), fill=255)
    if ring:
        dr.ellipse((d * S * 0.07, d * S * 0.07, d * S * 0.93, d * S * 0.93), outline=0, width=int(d * S * 0.03))
    n = len(text)
    if n == 1:
        f = F(font_path, int(d * S * 0.58))
        dr.text((d * S / 2, d * S / 2), text, font=f, fill=0, anchor="mm")
    else:  # 2文字は縦、4文字は2×2
        f = F(font_path, int(d * S * (0.34 if n == 2 else 0.3)))
        pos = [(0.5, 0.32), (0.5, 0.68)] if n == 2 else [(0.66, 0.33), (0.66, 0.67), (0.34, 0.33), (0.34, 0.67)]
        for ch, (px, py) in zip(text, pos):
            dr.text((d * S * px, d * S * py), ch, font=f, fill=0, anchor="mm")
    return m.resize((d, d), Image.LANCZOS)


def rules(mask, lines, width=2):
    d = ImageDraw.Draw(mask)
    for l in lines:
        d.line(l, fill=255, width=width)
    return mask


def small_block(mask, x, y, lines, size=16, gap=1.35, font=SANS):
    d = ImageDraw.Draw(mask)
    f = F(font, size)
    for i, s in enumerate(lines):
        d.text((x, y + i * size * gap), s, font=f, fill=255)
    return mask


# ---- J 蛍光ピンク×青 ----
def make_j():
    p = Print(PAPER, 81)
    # 青：網点の新月（大きく、右寄り）
    p.ink(halftone(moon_gray(560, 820, 360), cell=10, angle=18, gamma=0.8), BLUE, grain=0.15)
    # 青：細い罫線と小さな英文
    info = blank()
    rules(info, [((40, 60), (1240, 60)), ((40, 662), (1240, 662))], 3)
    small_block(info, 40, 24, ["SCORPIO  NEW  MOON   2026.11.09  16:02  JST   ·   PSYCHOLOGICAL ASTROLOGY"], 22)
    small_block(info, 40, 674, ["VENUS & MERCURY STATION DIRECT  11.14   ·   天蠍座新月   ·   星読み おます"], 22)
    p.ink(info, BLUE, grain=0.05)
    # ピンク：巨大な縦書き「蠍座新月」（重ね刷り）
    big = text_mask("蠍座新月", F(SONG, 150), (230, 78), vertical=True, step=146)
    p.ink(big, PINK, offset=(3, -2), grain=0.1)
    # ピンク：右の言葉
    t1 = text_mask("関係が、", F(SONG, 104), (1240, 120), anchor="ra", condense=0.9)
    t2 = text_mask("動き出す", F(SONG, 150), (1240, 430), anchor="ra", condense=0.88)
    p.ink(t1, BLACK, grain=0.06)
    p.ink(t2, PINK, offset=(2, 2), grain=0.08)
    # はんこ
    p.ink(place(circle_seal("星読", 118), 468, 520), PINK, grain=0.2)
    return p.image()


# ---- K 黒×蛍光グリーン ----
def make_k():
    p = Print((26, 26, 30), 82)
    img = p.image()
    # 黒地なので、インクは「加算」に近い見え方にしたい → 明るい色を上に重ねる（通常の合成）
    base = img.convert("RGB")

    def lay(mask, color, offset=(0, 0), alpha=1.0):
        nonlocal base
        m = mask if offset == (0, 0) else Image.fromarray(np.roll(np.roll(np.asarray(mask), offset[1], 0), offset[0], 1))
        col = Image.new("RGB", (W, H), color)
        base = Image.composite(col, base, m.point(lambda v: int(v * alpha)))

    lo = lotus(760, color=(255, 255, 255, 255), lw=10)
    lo_l = lo.split()[3]
    fill = Image.new("L", lo.size, 0)
    # 蓮を網点で塗る：花びらの中を、上ほど薄いグラデーションに
    g = Image.linear_gradient("L").resize(lo.size).point(lambda v: 60 + v * 0.7)
    fill.paste(g, (0, 0), lo_l.filter(ImageFilter.MaxFilter(9)))
    gm = blank()
    gm.paste(fill, (520, 200))
    lay(halftone(gm.filter(ImageFilter.GaussianBlur(3)), cell=8, angle=30), GREEN, alpha=0.9)
    lay(place(lo, 520, 200), GREEN)
    # 月（緑の線の輪）
    ring = blank()
    ImageDraw.Draw(ring).ellipse((780, 40, 1020, 280), outline=255, width=8)
    lay(ring, GREEN)
    # ピンクの縦書き「動き出す」
    lay(text_mask("動き出す", F(SONG, 168), (1170, 40), vertical=True, step=164), PINK, offset=(3, 0))
    # 大きな日付（緑）
    lay(text_mask("11.09", F(DELA, 190), (36, 20)), GREEN)
    lay(text_mask("蠍座新月", F(SONG, 120), (40, 250)), (255, 255, 255))
    lay(text_mask("関係が、", F(SONG, 84), (44, 400)), (255, 255, 255))
    info = blank()
    small_block(info, 44, 520, ["SCORPIO NEW MOON / 16:02 JST", "VENUS & MERCURY DIRECT 11.14", "天蠍座新月 · 心理占星術 · 星読み"], 26, 1.5)
    lay(info, GREEN)
    lay(place(circle_seal("星読", 104), 420, 396), PINK)
    return base.convert("RGBA")


# ---- L 台湾レトロのラベル ----
def make_l():
    p = Print(PAPER, 83)
    red = blank()
    d = ImageDraw.Draw(red)
    d.rectangle((20, 20, W - 20, H - 20), outline=255, width=8)
    d.rectangle((36, 36, W - 36, H - 36), outline=255, width=3)
    # 真ん中の紋章：光の筋と蓮と月
    cx, cy = 640, 322
    for k in range(36):
        a = 2 * math.pi * k / 36
        r0, r1 = 150, 228 if k % 2 == 0 else 204
        d.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a)), fill=255, width=6)
    d.ellipse((cx - 150, cy - 150, cx + 150, cy + 150), outline=255, width=8)
    d.ellipse((cx - 70, cy - 120, cx + 70, cy + 20), outline=255, width=6)   # 新月の輪
    lo = lotus(250, color=(255, 255, 255, 255), lw=6)
    red.paste(255, (cx - lo.width // 2, cy - 10), lo.split()[3])
    # 左右：丸の中の1文字（金・水・順・行）
    for i, ch in enumerate("金水"):
        red.paste(255, (70, 90 + i * 170), circle_seal(ch, 150, ring=True))
    for i, ch in enumerate("順行"):
        red.paste(255, (W - 70 - 150, 90 + i * 170), circle_seal(ch, 150, ring=True))
    # 上と下の文字
    big = text_mask("蠍座新月", F(SONG, 96), (W / 2, 28), anchor="ma", condense=1.0)
    red = Image.fromarray(np.maximum(np.asarray(red), np.asarray(big)))
    band = blank()
    ImageDraw.Draw(band).rectangle((36, 560, W - 36, 684), fill=255)
    p.ink(red, SHU, grain=0.12)
    p.ink(band, SHU, grain=0.08)
    img = p.image()
    d2 = ImageDraw.Draw(img)
    d2.text((W / 2, 600), "関係が、動き出す", font=F(SONG, 76), fill=PAPER + (255,), anchor="mm")
    d2.text((W / 2, 660), "2026.11.09 16:02  SCORPIO NEW MOON  ·  11.14 VENUS & MERCURY DIRECT", font=F(SANS, 22),
            fill=PAPER + (255,), anchor="mm")
    d2.text((90, 450), "天蠍座", font=F(SONG, 30), fill=SHU + (255,))
    d2.text((W - 90, 450), "星読み", font=F(SONG, 30), fill=SHU + (255,), anchor="ra")
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    outs = []
    for key, fn in (("J", make_j), ("K", make_k), ("L", make_l)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第5弾{key}_11月9日蠍座新月.png"))
        outs.append(im)
    sm = Image.new("RGB", (3 * 380, 230), (255, 255, 255))
    for i, im in enumerate(outs):
        sm.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    sm.save(os.path.join(OUT, "第5弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 3))
    for i, im in enumerate(outs):
        big.paste(im, (0, i * 720))
    big.resize((960, 1620)).save(os.path.join(OUT, "第5弾_3案まとめ.png"))
    print("ok")
