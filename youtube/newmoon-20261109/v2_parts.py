"""ブラッシュアップ版（v2）の部品：水彩風の背景、いらすとやの絵（シール風）、大きな要点の言葉、図解。"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ILLUST = os.path.join(HERE, "illust")  # 画像は tools/fetch_illust.py で取得する（GitHub には入れない）
W, H = 1920, 1080
SANS_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SERIF_B = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
GLYPH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (226, 186, 110)
INK = (52, 48, 62)


def font(path, size):
    return ImageFont.truetype(path, size, index=0) if path.endswith(".ttc") else ImageFont.truetype(path, size)


# 章ごとの空の色（上・下・にじみの色）
PALETTES = {
    "night": ((22, 26, 64), (66, 44, 96), [(90, 70, 150), (40, 90, 140), (120, 80, 140)]),
    "dawn": ((52, 48, 102), (232, 160, 150), [(250, 200, 160), (180, 120, 170), (120, 110, 190)]),
    "sunset": ((70, 40, 80), (240, 150, 90), [(255, 190, 110), (220, 110, 100), (150, 80, 120)]),
    "lavender": ((60, 56, 120), (190, 170, 220), [(230, 200, 240), (150, 140, 220), (200, 170, 210)]),
    "teal": ((24, 60, 80), (110, 170, 170), [(150, 210, 200), (70, 130, 160), (180, 220, 210)]),
    "gold": ((50, 40, 70), (230, 190, 130), [(255, 220, 160), (200, 150, 120), (170, 140, 190)]),
}


def watercolor_bg(name, seed=0):
    """水彩でにじませたような空。上から下へのグラデーションに、ぼかした色のしみと紙の質感を重ねる。"""
    top, bottom, blots = PALETTES[name]
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, H)[:, None, None]
    base = np.array(top)[None, None, :] * (1 - y) + np.array(bottom)[None, None, :] * y
    img = np.repeat(base, W, axis=1).astype(np.float32)
    small = Image.new("RGB", (W // 4, H // 4))
    layer = np.zeros((H // 4, W // 4, 3), np.float32)
    alpha = np.zeros((H // 4, W // 4), np.float32)
    for _ in range(14):
        c = np.array(blots[rng.integers(len(blots))], np.float32)
        cx, cy = rng.uniform(0, W // 4), rng.uniform(0, H // 4)
        r = rng.uniform(60, 180)
        yy, xx = np.mgrid[0:H // 4, 0:W // 4]
        m = np.exp(-(((xx - cx) ** 2) / (r * r * rng.uniform(0.6, 1.8)) + ((yy - cy) ** 2) / (r * r))) * rng.uniform(0.25, 0.5)
        layer = layer * (1 - m[..., None]) + c * m[..., None]
        alpha = np.maximum(alpha, m)
    blot = Image.fromarray(np.clip(layer, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30))
    a = Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30))
    a = np.asarray(a, np.float32)[..., None] / 255
    img = img * (1 - a) + np.asarray(blot, np.float32) * a
    # 紙の質感
    noise = rng.normal(0, 5, (H // 2, W // 2)).astype(np.float32)
    noise = np.asarray(Image.fromarray(noise).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    img = np.clip(img + noise, 0, 255).astype(np.uint8)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    for _ in range(160):
        x, yv = rng.integers(0, W), rng.integers(0, int(H * 0.7))
        r = rng.choice([1, 1, 1, 2, 2, 3])
        b = int(rng.integers(170, 255))
        d.ellipse((x - r, yv - r, x + r, yv + r), fill=(b, b, min(255, b + 10)))
    return im


_sticker = {}


def sticker(name, height):
    """いらすとやの絵を、白いふちどりと影のついたシール風にする。"""
    key = (name, height)
    if key in _sticker:
        return _sticker[key]
    path = os.path.join(ILLUST, name + ".png")
    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()
    im = im.crop(bbox)
    s = height / im.height
    im = im.resize((max(1, int(im.width * s)), height), Image.LANCZOS)
    pad = 26
    canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = im.split()[3]
    a_big = Image.new("L", canvas.size, 0)
    a_big.paste(a, (pad, pad))
    outline = a_big.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(1.5))
    shadow = a_big.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(12))
    sh = Image.new("RGBA", canvas.size, (20, 10, 40, 0))
    sh.putalpha(shadow.point(lambda v: v * 0.45))
    canvas.alpha_composite(sh, (6, 10))
    white = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    white.putalpha(outline)
    canvas.alpha_composite(white)
    canvas.alpha_composite(im, (pad, pad))
    _sticker[key] = canvas
    return canvas


def phrase_layer(text, size=74, color=(255, 255, 255), max_w=1500):
    """大きな要点の言葉（明朝・白・やわらかい影）。改行は \\n で指定する。"""
    f = font(SERIF_B, size)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines = text.split("\n")
    lw = [tmp.textlength(l, font=f) for l in lines]
    w = int(min(max_w, max(lw))) + 80
    lh = int(size * 1.35)
    h = lh * len(lines) + 60
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        y = 30 + lh * i + lh / 2
        gd.text((w / 2, y + 4), l, font=f, fill=(20, 10, 40, 200), anchor="mm")
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    for i, l in enumerate(lines):
        y = 30 + lh * i + lh / 2
        d.text((w / 2, y), l, font=f, fill=color, anchor="mm")
    glow.alpha_composite(im)
    return glow


def card(w, h, fill=(255, 252, 246, 238), radius=36, border=GOLD):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sh).rounded_rectangle((8, 14, w - 8, h - 2), radius, fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    shadow = Image.new("RGBA", (w, h), (20, 10, 40, 0))
    shadow.putalpha(sh)
    im.alpha_composite(shadow)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, w - 10, h - 14), radius, fill=fill, outline=border, width=4)
    return im


def text_center(d, xy, text, f, fill):
    d.text(xy, text, font=f, fill=fill, anchor="mm")


# ---- 図解 ----
def diagram_before_after(p):
    """前回の新月 → 今回の新月"""
    im = Image.new("RGBA", (1700, 560), (0, 0, 0, 0))
    left = card(740, 500)
    right = card(740, 500, border=(240, 150, 170))
    im.alpha_composite(left, (0, 30))
    im.alpha_composite(right, (960, 30))
    d = ImageDraw.Draw(im)
    fl, fb, fs = font(SANS_B, 34), font(SERIF_B, 56), font(SANS_B, 40)
    text_center(d, (370, 110), "前回　10/11 天秤座の新月", fl, (110, 100, 130))
    text_center(d, (370, 250), "関係を大切にする気持ちと", fs, INK)
    text_center(d, (370, 310), "自分の動き方を", fs, INK)
    text_center(d, (370, 400), "結び直す", fb, (90, 80, 160))
    text_center(d, (1330, 110), "今回　11/9 蠍座の新月", fl, (190, 90, 120))
    text_center(d, (1330, 250), "見直してきた関係を", fs, INK)
    text_center(d, (1330, 310), "今度は、もう一度", fs, INK)
    text_center(d, (1330, 400), "動かし始める", fb, (200, 80, 120))
    # 矢印
    ax = 790 + int(20 * math.sin(p * math.pi * 2))
    d.polygon([(ax, 250), (ax + 110, 280), (ax, 310)], fill=GOLD)
    d.rectangle((ax - 40, 268, ax, 292), fill=GOLD)
    return im


def diagram_three_points(n_shown):
    im = Image.new("RGBA", (1760, 600), (0, 0, 0, 0))
    items = [("①", "蠍座で重なる\n太陽と月", ["scorpio"]), ("②", "11/14 金星と水星が順行へ\n金星と火星の60度", ["venus", "mercury"]),
             ("③", "蠍座17度の\nサビアン", ["butterfly"])]
    for i, (num, text, ills) in enumerate(items):
        x = i * 590
        shown = i < n_shown
        im.alpha_composite(card(560, 580, fill=(255, 252, 246, 238) if shown else (255, 252, 246, 120)), (x, 0))
        d = ImageDraw.Draw(im)
        text_center(d, (x + 280, 70 if shown else 290), num, font(SERIF_B, 64 if shown else 110),
                    (190, 140, 60) if shown else (190, 160, 120, 200))
        if not shown:
            continue
        k = 0
        for name in ills:
            st = sticker(name, 170)
            ox = x + 280 - (len(ills) * (st.width - 20)) // 2 + k * (st.width - 20)
            im.alpha_composite(st, (int(ox), 120))
            k += 1
        for j, line in enumerate(text.split("\n")):
            text_center(d, (x + 280, 380 + j * 62), line, font(SANS_B, 40 if len(line) < 12 else 34), INK)
    return im


def diagram_new_moon():
    """新月：太陽・月・地球が一直線に並ぶ"""
    im = Image.new("RGBA", (1500, 520), (0, 0, 0, 0))
    im.alpha_composite(card(1500, 520), (0, 0))
    d = ImageDraw.Draw(im)
    # 太陽
    for r, a in ((140, 60), (115, 120), (95, 255)):
        d.ellipse((240 - r, 250 - r, 240 + r, 250 + r), fill=(255, 190, 80, a))
    text_center(d, (240, 420), "太陽", font(SANS_B, 40), INK)
    # 光の線
    for yy in (200, 250, 300):
        d.line((360, yy, 700, yy), fill=(255, 200, 100, 160), width=4)
    # 月（新月：地球側が暗い）
    d.ellipse((700, 190, 820, 310), fill=(60, 60, 80, 255))
    d.pieslice((700, 190, 820, 310), 90, 270, fill=(240, 230, 200, 255))
    text_center(d, (760, 420), "月", font(SANS_B, 40), INK)
    # 地球
    d.ellipse((1080, 160, 1260, 340), fill=(90, 150, 220, 255))
    d.ellipse((1120, 200, 1190, 260), fill=(110, 180, 110, 255))
    d.ellipse((1170, 260, 1230, 310), fill=(110, 180, 110, 255))
    text_center(d, (1170, 420), "地球", font(SANS_B, 40), INK)
    d.line((830, 250, 1070, 250), fill=(180, 170, 200, 255), width=3)
    text_center(d, (950, 110), "太陽と月が同じ方向に重なる＝新月", font(SANS_B, 40), (190, 90, 120))
    return im


def diagram_houses():
    """角度はどこでも同じ／ハウスは見る場所で変わる"""
    im = Image.new("RGBA", (1600, 560), (0, 0, 0, 0))
    a = card(760, 540)
    b = card(760, 540, border=(240, 150, 170))
    im.alpha_composite(a, (0, 0))
    im.alpha_composite(b, (820, 0))
    d = ImageDraw.Draw(im)
    text_center(d, (380, 80), "どこから見ても同じ", font(SANS_B, 44), (90, 80, 160))
    for j, l in enumerate(["新月の時刻", "星どうしの角度"]):
        text_center(d, (380, 220 + j * 90), "✓ " if False else l, font(SERIF_B, 54), INK)
    text_center(d, (1200, 80), "見る場所で変わる", font(SANS_B, 44), (200, 80, 120))
    text_center(d, (1200, 240), "ハウス", font(SERIF_B, 64), INK)
    text_center(d, (1200, 350), "この図は「東京」で切り取った図", font(SANS_B, 34), (110, 100, 130))
    text_center(d, (1200, 410), "皆さんの出生図とは別のもの", font(SANS_B, 34), (110, 100, 130))
    return im


def diagram_retrograde(p):
    """逆行：地球から見ると、星が後ろに下がって見える（見かけの通り道のループ）"""
    im = Image.new("RGBA", (1560, 680), (0, 0, 0, 0))
    im.alpha_composite(card(1560, 680), (0, 0))
    d = ImageDraw.Draw(im)
    text_center(d, (780, 70), "逆行＝地球から見ると、後ろに進んでいるように見える", font(SANS_B, 40), (190, 90, 120))
    pts = []
    for i in range(241):
        u = -1 + 2 * i / 240
        x = 780 + 560 * u - 420 * math.sin(math.pi * u)
        y = 400 - 140 * math.cos(math.pi * u)
        pts.append((x, y))
    d.line(pts, fill=(150, 140, 200, 255), width=8, joint="curve")
    for k in range(20, 240, 30):  # 進む向きの矢印
        (x0, y0), (x1, y1) = pts[k], pts[k + 4]
        a = math.atan2(y1 - y0, x1 - x0)
        d.polygon([(x1 + 14 * math.cos(a), y1 + 14 * math.sin(a)),
                   (x1 + 14 * math.cos(a + 2.4), y1 + 14 * math.sin(a + 2.4)),
                   (x1 + 14 * math.cos(a - 2.4), y1 + 14 * math.sin(a - 2.4))], fill=(150, 140, 200, 255))
    k = int(p * 240)
    x, y = pts[min(240, k)]
    st = sticker("venus", 100)
    im.alpha_composite(st, (int(x - st.width / 2), int(y - st.height / 2)))
    f = font(SANS_B, 34)
    text_center(d, (230, 600), "前へ進む", f, INK)
    text_center(d, (780, 200), "後ろに下がって見える（逆行）", font(SANS_B, 36), (190, 90, 120))
    text_center(d, (1330, 600), "また前へ（順行）", f, INK)
    text_center(d, (780, 620), "10/3 逆行スタート → 11/14 順行へ", font(SERIF_B, 40), (90, 80, 160))
    return im


def diagram_aspects():
    """前回の90度と、今回の60度"""
    im = Image.new("RGBA", (1600, 600), (0, 0, 0, 0))
    for i, (title, ang, col, note) in enumerate([("前回　90度", 90, (210, 90, 90), "ぶつかりやすい"),
                                                 ("今回　60度", 60, (70, 120, 220), "助け合いやすい")]):
        x = i * 820
        im.alpha_composite(card(780, 600, border=col), (x, 0))
        d = ImageDraw.Draw(im)
        text_center(d, (x + 390, 70), title, font(SERIF_B, 52), col)
        cx, cy, r = x + 390, 330, 160
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(200, 190, 210, 255), width=4)
        a0 = math.radians(200)
        a1 = a0 - math.radians(ang)
        p0 = (cx + r * math.cos(a0), cy - r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cy - r * math.sin(a1))
        d.line((cx, cy, *p0), fill=(200, 190, 210, 255), width=3)
        d.line((cx, cy, *p1), fill=(200, 190, 210, 255), width=3)
        d.line((*p0, *p1), fill=col + (255,), width=10)
        v, m = sticker("venus", 96), sticker("mars", 96)
        im.alpha_composite(v, (int(p0[0] - v.width / 2), int(p0[1] - v.height / 2)))
        im.alpha_composite(m, (int(p1[0] - m.width / 2), int(p1[1] - m.height / 2)))
        f2 = font(SANS_B, 30)
        text_center(d, (int(p0[0]), int(p0[1]) + 70), "金星", f2, INK)
        text_center(d, (int(p1[0]) + 75, int(p1[1])), "火星", f2, INK)
        text_center(d, (x + 390, 545), note, font(SANS_B, 44), INK)
    return im


def sabian_card(degree, quote, ill, sub):
    im = Image.new("RGBA", (1300, 620), (0, 0, 0, 0))
    im.alpha_composite(card(1300, 620, fill=(255, 250, 240, 245)), (0, 0))
    d = ImageDraw.Draw(im)
    st = sticker(ill, 300)
    im.alpha_composite(st, (60, int(300 - st.height / 2)))
    text_center(d, (840, 120), degree, font(SANS_B, 44), (190, 140, 60))
    lines = quote.split("\n")
    for j, l in enumerate(lines):
        text_center(d, (840, 250 + j * 84), l, font(SERIF_B, 62), INK)
    text_center(d, (840, 250 + len(lines) * 84 + 40), sub, font(SANS_B, 34), (110, 100, 130))
    return im


def calendar_diagram(n_shown):
    items = [("11/9", "蠍座の新月", "scorpio"), ("11/10", "金星と火星の60度がぴったり", "venus"),
             ("11/14", "水星と金星が順行へ", "mercury"), ("11/16", "火星と木星が重なる", "jupiter"),
             ("11/22", "太陽が射手座へ", None), ("11/24", "双子座の満月", None)]
    im = Image.new("RGBA", (1500, 720), (0, 0, 0, 0))
    im.alpha_composite(card(1500, 720), (0, 0))
    d = ImageDraw.Draw(im)
    text_center(d, (750, 70), "新月からの2週間", font(SERIF_B, 52), (90, 80, 160))
    for i, (date, text, ill) in enumerate(items[:n_shown]):
        y = 150 + i * 92
        d.rounded_rectangle((80, y, 260, y + 70), 18, fill=(250, 236, 210, 255))
        text_center(d, (170, y + 35), date, font(SANS_B, 40), (160, 110, 50))
        d.text((300, y + 35), text, font=font(SANS_B, 42), fill=INK, anchor="lm")
        if ill:
            st = sticker(ill, 78)
            im.alpha_composite(st, (1300, int(y + 35 - st.height / 2)))
    return im


def question_card(num, question, ill, sub):
    """問いのカード。question は \n で2行に分けられる"""
    im = Image.new("RGBA", (1500, 620), (0, 0, 0, 0))
    im.alpha_composite(card(1500, 620, fill=(255, 250, 244, 245), border=(240, 150, 170)), (0, 0))
    d = ImageDraw.Draw(im)
    st = sticker(ill, 420)
    im.alpha_composite(st, (40, int(310 - st.height / 2)))
    cx = 520 + (1500 - 520) // 2
    text_center(d, (cx, 110), f"問い {num}", font(SANS_B, 44), (200, 90, 130))
    lines = question.split("\n")
    for j, l in enumerate(lines):
        text_center(d, (cx, 250 + j * 90), l, font(SERIF_B, 64), INK)
    text_center(d, (cx, 250 + len(lines) * 90 + 50), sub, font(SANS_B, 36), (110, 100, 130))
    return im


if __name__ == "__main__":
    out = []
    bg = watercolor_bg("night", 1)
    f1 = bg.copy().convert("RGBA")
    f1.alpha_composite(phrase_layer("大切な人とは、\nもう一歩深く関わりたい"), (210, 60))
    st = sticker("couple", 480)
    f1.alpha_composite(st, (W // 2 - st.width // 2, 360))
    out.append(f1)
    for name, fn in [("dawn", lambda: diagram_retrograde(0.4)), ("sunset", diagram_aspects),
                     ("lavender", lambda: sabian_card("蠍座17度", "自分の子どもの\n父親である女性", "sprout", "待つより、自分の中で育てたものを、自分で形に")),
                     ("teal", lambda: calendar_diagram(6)), ("gold", lambda: question_card(1, "この関係を、\nもう一歩深めるとしたら？", "imagine", "蠍座の新月の問い")),
                     ("night", lambda: diagram_three_points(3)), ("night", diagram_new_moon)]:
        f = watercolor_bg(name, 2).convert("RGBA")
        g = fn()
        f.alpha_composite(g, ((W - g.width) // 2, 60))
        out.append(f)
    sheet = Image.new("RGB", (960 * 2, 540 * 4))
    for i, im in enumerate(out):
        sheet.paste(im.convert("RGB").resize((960, 540)), ((i % 2) * 960, (i // 2) * 540))
    sheet.save(os.path.join(HERE, "v2_parts_check.png"))
