"""11/9 蠍座新月のサムネイル案 第13弾：コラージュの背景の上に、画面いっぱいの文字（1280×720）。

参考（おますさんが見せてくれた中国風のコラージュ）の「感じ」だけを借りる：
白っぽい紙・細い縦線・丸窓の山水画・赤い円・黒い雲・縦の札・屋根の角。絵柄や配置はまねず、素材は
メトロポリタン美術館のパブリックドメイン（CC0）：
  山水＝王原祁「江國花時（Fishing in River Country at Blossom Time）」1709年（49186）
  女性＝改琦「緑珠小像」1823年（737733）の顔だけを3本の帯に切って、少しずらして貼る
赤い円は太陽で、そこに墨の月が重なる＝新月（太陽と月が同じところにある）。屋根と雲は線で描く。
  W 横一列：「蠍座新月」を横幅いっぱいに
  X 2段ずらし：左上に「蠍座」、右下に「新月」、あいたところに縦の札と落款
    python3 make_thumbnails_v13.py
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_thumbnails_v11 as v11  # noqa: E402
from make_thumbnails_v10 import small_seal, vcol  # noqa: E402
from make_thumbnails_v12 import scorpius  # noqa: E402

PD = os.path.join(HERE, "public_domain")
OUT = os.path.join(HERE, "thumbnails")
W, H = 1280, 720
F, BRUSH, SANS = v11.F, v11.BRUSH, v11.SANS
OLDM = os.path.join(HERE, "..", "fonts", "ZenOldMincho-Black.ttf")
PAPER = (236, 234, 228)
INK = (28, 28, 32)
VERM = (204, 52, 36)
TAN = (214, 190, 150)
CREAM = v11.CREAM


def paper_bg(seed=0):
    rng = np.random.default_rng(seed)
    img = np.ones((H, W, 3), np.float32) * np.array(PAPER, np.float32)
    n = rng.normal(0, 4, (H // 2, W // 2)).astype(np.float32)
    img += np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    fib = rng.normal(0, 2.5, (H, W // 6)).astype(np.float32)   # 縦の紙すき目
    img += np.asarray(Image.fromarray(fib).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def thin_lines(img, xs, color=(150, 150, 150), alpha=170):
    d = ImageDraw.Draw(img)
    for x in xs:
        d.line((x, 0, x, H), fill=color + (alpha,), width=1)


def panel(img, box, color=(222, 222, 220)):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rectangle(box, fill=color + (255,))
    img.alpha_composite(lay)


def landscape_circle(R, crop=(250, 0, 1130, 880)):
    """丸窓の山水。色を少し落ち着かせ、紙になじませる。"""
    s = Image.open(os.path.join(PD, "wang_yuanqi_landscape.jpg")).convert("RGB").crop(crop)
    s = s.resize((R * 2, R * 2), Image.LANCZOS)
    s = ImageEnhance.Color(s).enhance(0.8)
    arr = np.asarray(s).astype(np.float32)
    arr = arr * 0.9 + np.array([236, 236, 230], np.float32) * 0.1
    s = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (R * 4, R * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, R * 4 - 1, R * 4 - 1), fill=255)
    s.putalpha(m.resize((R * 2, R * 2), Image.LANCZOS))
    return s


def new_moon(img, cx, cy, r, seed=4):
    """赤い太陽に墨の月が重なる＝新月。右下に細い赤い縁が残る。"""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((cx - r * 1.5, cy - r * 1.5, cx + r * 1.5, cy + r * 1.5), fill=(240, 90, 60, 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(r * 0.4)))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=VERM + (255,))
    # 墨の月（少しにじみのある濃淡）
    rng = np.random.default_rng(seed)
    mr = int(r * 0.96)
    ox, oy = -r * 0.12, -r * 0.1
    S = mr * 2 + 8
    n = Image.fromarray((rng.random((S, S)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(S / 14))
    n = np.asarray(n, np.float32)
    n = (n - n.mean()) / (n.std() + 1e-6)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    rr = np.hypot(xx - S / 2, yy - S / 2) / mr
    tone = 34 + 7 * n + 16 * rr ** 2
    a = np.clip((1.0 - rr) * 60, 0, 1) * 255
    moon = np.dstack([tone, tone, tone + 6, a]).astype(np.uint8)
    img.alpha_composite(Image.fromarray(moon, "RGBA"), (int(cx + ox - S / 2), int(cy + oy - S / 2)))


def face_strips(img, x, y, width=400, cuts=((95, 180), (252, 312), (318, 392)), shifts=(0, 34, -22), gap=26):
    """改琦の女性の顔を横の帯に切って、少しずつずらして貼る。"""
    face = Image.open(os.path.join(PD, "luzhu_face.jpg")).convert("RGB")
    k = width / 300
    yy = y
    for (t, b), sx in zip(cuts, shifts):
        st = face.crop((30, t, 330, b)).resize((width, int((b - t) * k)), Image.LANCZOS)
        st = ImageEnhance.Contrast(st).enhance(1.08).convert("RGBA")
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle((x + sx + 6, yy + 8, x + sx + width + 6, yy + st.height + 8), fill=(0, 0, 0, 70))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
        img.alpha_composite(st, (int(x + sx), int(yy)))
        ImageDraw.Draw(img).rectangle((x + sx, yy, x + sx + width - 1, yy + st.height - 1), outline=(70, 66, 60, 255), width=2)
        yy += st.height + gap


def eave(img, x0, y0, scale=1.0, color=(46, 46, 52)):
    """左上の屋根の角（反りあがった軒）。瓦の筋、瓦の端の丸、先に小さな鈴。"""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    s = scale
    N = 80

    def edge(t):   # 軒の線：左から右へゆるく下がり、先で反りあがる
        y = 70 + 80 * t - 260 * max(0.0, t - 0.7) ** 2 * 3.4
        return x0 + t * 440 * s, y0 + y * s
    low = [edge(i / N) for i in range(N + 1)]
    top = (x0 - 80 * s, y0 - 200 * s)
    # 屋根の面（上は画面の外まで）
    d.polygon([(x0 - 80 * s, y0 - 400), (low[-1][0] - 60 * s, y0 - 400)] + low[::-1], fill=color + (255,))
    # 瓦の筋（軒から奥へ、少し明るい灰）
    for i in range(2, N - 2, 4):
        px, py = low[i]
        d.line((px, py - 14 * s, px - 110 * s, py - 260 * s), fill=(78, 78, 86, 255), width=max(3, int(7 * s)))
    # 軒の板（少し明るい帯）
    d.line(low, fill=(70, 70, 78, 255), width=int(16 * s), joint="curve")
    # 瓦の端の丸
    for i in range(2, N - 3, 4):
        px, py = low[i]
        r = 11 * s
        d.ellipse((px - r, py - r, px + r, py + r), fill=(64, 64, 72, 255), outline=(108, 108, 116, 255), width=2)
    # 先の反りと鈴
    tx, ty = low[-1]
    d.line((low[-6][0], low[-6][1], tx + 30 * s, ty - 34 * s), fill=color + (255,), width=int(18 * s))
    bx, by = tx + 18 * s, ty + 4 * s
    d.line((bx, by, bx, by + 30 * s), fill=(60, 60, 66, 255), width=2)
    d.polygon([(bx - 10 * s, by + 52 * s), (bx - 6 * s, by + 30 * s), (bx + 6 * s, by + 30 * s), (bx + 10 * s, by + 52 * s)],
              fill=(150, 120, 70, 255))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(lay.split()[3].point(lambda v: int(v * 0.35)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (0, 0))
    img.alpha_composite(lay)


def ink_clouds(img, cx, cy, scale=1.0, seed=2, dark=(46, 46, 52)):
    """墨の雲（丸いふくらみが重なり、中に白い渦の線）"""
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    bumps = []
    for i in range(7):
        bx = cx + (i - 3) * 62 * scale + rng.uniform(-10, 10) * scale
        by = cy + rng.uniform(-18, 18) * scale - (30 if i in (2, 3, 4) else 0) * scale
        br = rng.uniform(42, 62) * scale
        bumps.append((bx, by, br))
    for bx, by, br in bumps:
        d.ellipse((bx - br, by - br, bx + br, by + br), fill=dark + (255,))
    for bx, by, br in bumps:
        pts = []
        for k in range(90):
            t = k / 90 * 2.6 * math.pi
            rr = br * 0.82 * (1 - t / (2.9 * math.pi))
            pts.append((bx + rr * math.cos(t + 1.4), by + rr * math.sin(t + 1.4)))
        d.line(pts, fill=(200, 200, 204, 230), width=max(2, int(3 * scale)))
    # 下はぼかして紙にとける
    a = np.asarray(lay.split()[3]).astype(np.float32)
    yy = np.arange(H, dtype=np.float32)[:, None]
    fade = np.clip(1 - (yy - (cy + 30 * scale)) / (50 * scale), 0, 1)
    lay.putalpha(Image.fromarray((a * fade).astype(np.uint8)))
    img.alpha_composite(lay)


def tag(img, box, text, size, color=TAN, font=BRUSH, ink=INK, step=None):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), fill=(0, 0, 0, 80))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    rng = np.random.default_rng(7)
    w, h = x1 - x0, y1 - y0
    n = rng.normal(0, 6, (h // 3 + 1, w // 3 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC), np.float32)[..., None]
    arr = np.ones((h, w, 3), np.float32) * np.array(color, np.float32) + n
    img.alpha_composite(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA"), (x0, y0))
    vcol(img, (x0 + x1) // 2, y0 + 18, text, size, ink, step=step or int(size * 1.02), font=font)


def small_vtext(img, x, y, lines, size=17, color=(90, 86, 80), step=None, colgap=24):
    f = F(OLDM, size)
    d = ImageDraw.Draw(img)
    for j, s in enumerate(lines):
        for i, ch in enumerate(s):
            d.text((x - j * colgap, y + i * (step or size + 3)), ch, font=f, fill=color + (255,), anchor="mt")


def giant(text, size, fill=INK, stroke=10, stroke_fill=PAPER, font=BRUSH, cell=None):
    """特大の文字の列（横）。1文字ずつ同じ幅のマスに置く。"""
    f = F(font, size)
    cell = cell or int(size * 1.0)
    lay = Image.new("RGBA", (cell * len(text) + stroke * 4, int(size * 1.35)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, ch in enumerate(text):
        d.text((stroke * 2 + i * cell + cell / 2, size * 0.66), ch, font=f, fill=fill + (255,), anchor="mm",
               stroke_width=stroke, stroke_fill=stroke_fill + (255,))
    return lay.crop(lay.getbbox())


def put(img, layer, x, y, shadow=0.35, blur=10, off=(6, 9)):
    if shadow:
        sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        sh.putalpha(layer.split()[3].point(lambda v: int(v * shadow)))
        big = Image.new("RGBA", img.size, (0, 0, 0, 0))
        big.paste(sh, (int(x + off[0]), int(y + off[1])), sh)
        img.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)))
    big = Image.new("RGBA", img.size, (0, 0, 0, 0))
    big.paste(layer, (int(x), int(y)), layer)
    img.alpha_composite(big)


def collage(cx=600, cy=360, R=330, moon=(0.42, -0.42), strips=None, eave_xy=(-30, 30), clouds=None, seed=0):
    img = paper_bg(seed)
    panel(img, (cx - R - 70, 40, cx + R + 40, H - 30))
    thin_lines(img, [cx - R - 120, cx - R - 96, cx + R + 70, cx + R + 140, 1180])
    lc = landscape_circle(R)
    put(img, lc, cx - R, cy - R, shadow=0.18, blur=14, off=(0, 8))
    ImageDraw.Draw(img).ellipse((cx - R, cy - R, cx + R, cy + R), outline=(120, 120, 116, 255), width=2)
    new_moon(img, int(cx + moon[0] * R), int(cy + moon[1] * R), int(R * 0.3))
    if clouds:
        ink_clouds(img, *clouds)
    if strips:
        face_strips(img, *strips)
    if eave_xy:
        eave(img, *eave_xy)
    return img


# ---- W 横一列 ----
def make_w():
    img = collage(cx=640, cy=360, R=340, moon=(0.45, -0.5), strips=(150, 452, 330), clouds=(560, 560, 1.15),
                  eave_xy=(-40, 20))
    small_vtext(img, 1230, 60, ["蠍座の新月は、", "深いところで", "縁を結び直す合図。"], size=19)
    g = giant("蠍座新月", 330, cell=318, stroke=12)
    g = g.resize((W - 24, int(g.height * (W - 24) / g.width)), Image.LANCZOS)
    put(img, g, 12, 180, shadow=0.4)
    tag(img, (1090, 470, 1170, 712), "縁が動く", 54)
    d = ImageDraw.Draw(img)
    d.rectangle((26, 640, 186, 700), fill=VERM + (255,))
    d.text((106, 670), "11.9", font=F(SANS, 40), fill=CREAM + (255,), anchor="mm")
    img.alpha_composite(small_seal("星読", 92), (1176, 600))
    return img


# ---- X 2段ずらし ----
def make_x():
    img = collage(cx=660, cy=370, R=320, moon=(0.5, -0.38), strips=(820, 70, 300, ((95, 180), (252, 312)), (0, 30)),
                  clouds=(470, 640, 1.0), eave_xy=(-40, 10))
    a = giant("蠍座", 380, stroke=12)
    put(img, a, 10, -30, shadow=0.4)
    b = giant("新月", 380, stroke=12)
    put(img, b, W - b.width - 10, H - b.height + 24, shadow=0.4)
    tag(img, (1150, 30, 1240, 340), "縁が動く", 64)
    small_vtext(img, 120, 430, ["蠍座の新月は、", "深いところで", "縁を結び直す合図。"], size=19)
    d = ImageDraw.Draw(img)
    d.rectangle((150, 640, 310, 700), fill=VERM + (255,))
    d.text((230, 670), "11.9", font=F(SANS, 40), fill=CREAM + (255,), anchor="mm")
    img.alpha_composite(small_seal("星読", 92), (36, 610))
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for key, fn in (("W", make_w), ("X", make_x)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第13弾{key}_11月9日蠍座新月.png"))
        ims.append(im)
    sm = Image.new("RGB", (2 * 380, 230), (255, 255, 255))
    for i, im in enumerate(ims):
        sm.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    sm.save(os.path.join(OUT, "第13弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 2))
    for i, im in enumerate(ims):
        big.paste(im, (0, i * 720))
    big.resize((960, 1080)).save(os.path.join(OUT, "第13弾_2案まとめ.png"))
    print("ok")
