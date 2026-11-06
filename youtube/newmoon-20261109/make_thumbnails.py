"""11/9 蠍座新月のサムネイル案（3パターン、1280×720）。

型（サムネイル調査 2026-11-06 から）：上段に日付・時刻と出来事、真ん中に大きく「見る人に起きること」の言葉
（1語だけ色を変える）、右におますさんのアイコンを大きく（山羊の画像は荒いので使わない）。
    python3 make_thumbnails.py   # thumbnails/サムネイル案A〜C.png と、スマホで見たときの大きさの見本
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v2_parts as vp  # noqa: E402

W, H = 1280, 720
OUT = os.path.join(HERE, "thumbnails")
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
ICON = os.path.join(HERE, "..", "2027-unsei-pr", "assets", "icon.png")


def font(path, size):
    return ImageFont.truetype(path, size, index=0)


def gold(img, xy, text, f, anchor="la", stroke=8):
    """金のグラデーションの文字（濃い影と茶色のふちどり）"""
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + 5, xy[1] + 8), text, font=f, fill=(10, 0, 30, 230), anchor=anchor,
                            stroke_width=stroke + 4, stroke_fill=(10, 0, 30, 230))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    edge = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(edge).text(xy, text, font=f, fill=(0, 0, 0, 0), anchor=anchor, stroke_width=stroke,
                              stroke_fill=(96, 52, 24, 255))
    img.alpha_composite(edge)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=f, fill=255, anchor=anchor)
    bb = mask.getbbox()
    grad = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(bb[1], bb[3] + 1):
        a = (y - bb[1]) / max(1, bb[3] - bb[1])
        c = (255, int(250 - 60 * a), int(215 - 130 * a), 255) if a < 0.55 else (int(250 - 30 * a), int(200 - 40 * a), int(110 - 40 * a), 255)
        gd.line((bb[0], y, bb[2], y), fill=c)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    img.alpha_composite(out)


def plain(img, xy, text, f, fill, stroke_fill, stroke=9, anchor="la"):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + 4, xy[1] + 7), text, font=f, fill=(10, 0, 30, 200), anchor=anchor,
                            stroke_width=stroke + 3, stroke_fill=(10, 0, 30, 200))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(img).text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


def phrase(img, x, y, parts, size):
    """parts = [(文字, 色)] を1行に並べる（1語だけ色を変える用）"""
    f = font(SANS, size)
    d = ImageDraw.Draw(img)
    cx = x
    for text, col in parts:
        plain(img, (cx, y), text, f, col, (52, 22, 70, 255), stroke=10)
        cx += d.textlength(text, font=f)


def goat(name, height):
    g = Image.open(os.path.join(HERE, "goat_src", "poses", name + ".png")).convert("RGBA")
    g = g.resize((int(g.width * height / g.height), height), Image.LANCZOS)
    g = g.filter(ImageFilter.UnsharpMask(radius=3, percent=80, threshold=2))
    pad = 14
    canvas = Image.new("RGBA", (g.width + pad * 2, g.height + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", canvas.size, 0)
    a.paste(g.split()[3], (pad, pad))
    sh = Image.new("RGBA", canvas.size, (10, 0, 30, 0))
    sh.putalpha(a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.55)))
    canvas.alpha_composite(sh, (6, 10))
    rim = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    rim.putalpha(a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(1)))
    canvas.alpha_composite(rim)
    canvas.alpha_composite(g, (pad, pad))
    return canvas


def icon_badge(size=120):
    ic = Image.open(ICON).convert("RGBA").resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size + 12, size + 12), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, size + 11, size + 11), fill=(255, 255, 255, 255), outline=(206, 164, 82, 255), width=4)
    out.paste(ic, (6, 6), m)
    return out


def background(palette, seed, moon=False):
    bg = vp.watercolor_bg(palette, seed).convert("RGBA").resize((W, H), Image.LANCZOS)
    if moon:  # 新月：右上に、光の輪だけの新月
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((930, 30, 1230, 330), fill=(255, 224, 170, 110))
        bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(36)))
        ImageDraw.Draw(bg).ellipse((960, 60, 1200, 300), fill=(34, 28, 64, 255), outline=(255, 230, 180, 255), width=5)
    return bg


def header(img, date="11月9日 16:02", title="蠍座新月"):
    plain(img, (48, 34), date, font(SANS, 54), (255, 255, 255), (52, 22, 70, 255), stroke=7)
    gold(img, (40, 92), title, font(SERIF, 150), stroke=9)
    ImageDraw.Draw(img).text((620, 140), "♏", font=font(vp.GLYPH, 96), fill=(255, 230, 170, 255),
                             stroke_width=4, stroke_fill=(96, 52, 24, 255))


def make_a():
    """A：待ってても 変わらない"""
    img = background("night", 21)
    header(img)
    phrase(img, 48, 300, [("待ってても", (255, 255, 255))], 120)
    phrase(img, 48, 450, [("変わらない", (255, 120, 170))], 136)
    return img


def make_b():
    """B：関係が、動き出す"""
    img = background("dawn", 33)
    header(img)
    phrase(img, 48, 290, [("関係が、", (255, 255, 255))], 124)
    phrase(img, 48, 430, [("動き出す", (255, 232, 90))], 140)
    plain(img, (56, 628), "11/14 金星と水星が順行へ", font(SANS, 40), (255, 255, 255), (52, 22, 70, 255), stroke=6)
    return img


def make_c():
    """C：本音で、もう一歩"""
    img = background("lavender", 45)
    header(img)
    phrase(img, 48, 290, [("本音で、", (255, 255, 255))], 124)
    phrase(img, 48, 430, [("もう一歩", (255, 140, 180))], 140)
    plain(img, (56, 628), "大切な人と深まる2週間", font(SANS, 40), (255, 255, 255), (52, 22, 70, 255), stroke=6)
    return img


def big_icon(img, cx=1010, cy=420, d=440):
    """おますさんのアイコンを大きく、金のふちと光の輪をつけて置く（山羊の画像は荒いので使わない）"""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((cx - d / 2 - 60, cy - d / 2 - 60, cx + d / 2 + 60, cy + d / 2 + 60), fill=(255, 224, 170, 150))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    b = icon_badge(d)
    ImageDraw.Draw(img).ellipse((cx - d / 2 - 16, cy - d / 2 - 16, cx + d / 2 + 16, cy + d / 2 + 16), outline=(255, 230, 180, 255), width=5)
    img.alpha_composite(b, (int(cx - b.width / 2), int(cy - b.height / 2)))


def finish(img):
    big_icon(img)
    st = vp.sticker("scorpio", 160)  # アイコンのサインにかからないよう、右下のすみに
    img.alpha_composite(st, (W - st.width + 8, H - st.height + 6))
    return img.convert("RGB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    outs = []
    for key, fn in (("A", make_a), ("B", make_b), ("C", make_c)):
        im = finish(fn())
        im.save(os.path.join(OUT, f"サムネイル案{key}_11月9日蠍座新月.png"))
        outs.append(im)
    # スマホの一覧で見たときの大きさ（横360ピクセル）
    small = Image.new("RGB", (3 * 380, 230), (255, 255, 255))
    for i, im in enumerate(outs):
        small.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    small.save(os.path.join(OUT, "スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 3))
    for i, im in enumerate(outs):
        big.paste(im, (0, i * 720))
    big.resize((960, 1620)).save(os.path.join(OUT, "3案まとめ.png"))
    print("ok")
