"""11/9 蠍座新月：インスタのストーリーズ 2枚（1080×1920）。

おますさんが自分で作ったサムネイルの雰囲気に合わせる：レトロな中華ポスター風。
紫の星空・黒い新月に金のふちと蠍座の記号・生成りの特大文字に朱と焦げ茶のふち・朱の雲形の札・金の星・
生成りの紙のふち・印刷のざらつき。蠍座の星（金の線）も入れる。
  1枚目（昼）：明日の新月／今回は YouTube で／リンクは今夜20時に一斉配信チャンネルへ／参加はここから
  2枚目（20時）：YouTube 公開しました／あなたの縁が動き出す／リンクは一斉配信チャンネルへ
下のほう（矢印の下）は、インスタのリンクスタンプを置く場所としてあけてある。
    python3 make_stories.py
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_thumbnails_v12 import scorpius  # noqa: E402

FONTS = os.path.join(HERE, "..", "fonts")
KAISEI = os.path.join(FONTS, "KaiseiTokumin-ExtraBold.ttf")
GOTHIC = os.path.join(FONTS, "ZenKakuGothicNew-Black.ttf")
GLYPH = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"   # ♏ の字形
OUT = os.path.join(HERE, "stories")
W, H = 1080, 1920

CREAM = (246, 231, 200)
PAPER = (238, 222, 188)
RED = (190, 40, 30)
DEEPRED = (120, 22, 20)
BROWN = (58, 26, 18)
GOLD = (236, 184, 84)
PURPLE = (52, 30, 74)
TEAL = (30, 62, 70)


def F(path, size):
    return ImageFont.truetype(path, size)


# ---- 背景 ----
def sky(seed=1, keep_out=()):
    """keep_out = [(y0, y1)]：大きな星を置かない帯（文字のところ）"""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W / 2) / W, (yy - H * 0.55) / H)
    base = np.array(PURPLE, np.float32)
    img = base * (1.15 - 0.7 * r[..., None])
    n = rng.normal(0, 9, (H // 3, W // 3)).astype(np.float32)
    img += np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    speck = rng.random((H, W)) < 0.012    # 細かい星くず
    img[speck] += np.array([70, 60, 50], np.float32) * rng.random((speck.sum(), 1)).astype(np.float32)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for _ in range(26):
        x, y, s = rng.uniform(70, W - 70), rng.uniform(80, H - 80), rng.uniform(8, 30)
        if any(a - 30 <= y <= b + 30 for a, b in keep_out):
            continue
        sparkle(d, x, y, s, GOLD if rng.random() < 0.8 else CREAM)
    for _ in range(90):
        x, y, s = rng.uniform(40, W - 40), rng.uniform(40, H - 40), rng.uniform(1.5, 3.5)
        d.ellipse((x - s, y - s, x + s, y + s), fill=CREAM + (200,))
    return im


def sparkle(d, x, y, s, col, alpha=255):
    """4つの角の星"""
    k = s * 0.2
    d.polygon([(x, y - s), (x + k, y - k), (x + s, y), (x + k, y + k), (x, y + s), (x - k, y + k), (x - s, y), (x - k, y - k)],
              fill=col + (alpha,))


def grain(img, seed=5, amount=10):
    rng = np.random.default_rng(seed)
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    a += rng.normal(0, amount, a.shape[:2]).astype(np.float32)[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return out


def paper_frame(img, m=34, seed=3):
    """生成りの紙のふち（すこし欠けた感じ）と、内側の細い金の線"""
    rng = np.random.default_rng(seed)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rectangle((0, 0, W, H), fill=255)
    md.rounded_rectangle((m, m, W - m, H - m), radius=26, fill=0)
    n = rng.random((H // 6, W // 6)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC), np.float32)
    a = np.asarray(mask.filter(ImageFilter.GaussianBlur(3))).astype(np.float32)
    a = np.where((a > 30) & (a < 230), np.where(n > 0.5, 255, 0), a)
    mask = Image.fromarray(a.astype(np.uint8))
    tex = rng.normal(0, 7, (H, W)).astype(np.float32)
    p = np.ones((H, W, 3), np.float32) * np.array(PAPER, np.float32) + tex[..., None]
    paper = Image.fromarray(np.clip(p, 0, 255).astype(np.uint8)).convert("RGBA")
    paper.putalpha(mask)
    img.alpha_composite(paper)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((m + 14, m + 14, W - m - 14, H - m - 14), radius=20, outline=GOLD + (200,), width=3)


# ---- 部品 ----
def cloud_plaque(w, h, fill=CREAM, line=RED, bumps=3):
    """左右の端が雲のようにふくらんだ札"""
    S = 2
    im = Image.new("RGBA", ((w + 80) * S, (h + 40) * S), (0, 0, 0, 0))
    m = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(m)
    ox, oy = 40 * S, 20 * S
    d.rounded_rectangle((ox, oy, ox + w * S, oy + h * S), radius=h * S // 3, fill=255)
    r = h * S / (bumps + 0.6)
    for i in range(bumps):
        cy = oy + h * S * (i + 0.5) / bumps
        d.ellipse((ox - r * 0.9, cy - r, ox + r * 1.1, cy + r), fill=255)
        d.ellipse((ox + w * S - r * 1.1, cy - r, ox + w * S + r * 0.9, cy + r), fill=255)
    outer = m.filter(ImageFilter.MaxFilter(9))
    col = Image.new("RGBA", im.size, line + (255,))
    col.putalpha(outer)
    im.alpha_composite(col)
    inner = Image.new("RGBA", im.size, fill + (255,))
    inner.putalpha(m)
    im.alpha_composite(inner)
    # 内側の細い線
    ring = m.filter(ImageFilter.MinFilter(15))
    ring2 = ring.filter(ImageFilter.MinFilter(5))
    rl = Image.fromarray((np.asarray(ring).astype(np.int16) - np.asarray(ring2)).clip(0, 255).astype(np.uint8))
    lc = Image.new("RGBA", im.size, line + (255,))
    lc.putalpha(rl)
    im.alpha_composite(lc)
    return im.resize((w + 80, h + 40), Image.LANCZOS)


def red_panel(w, h, seed=2):
    """題字の下の朱の板：ふちが波打ち、うしろに放射の光"""
    S = 2
    m = Image.new("L", (w * S, h * S), 0)
    d = ImageDraw.Draw(m)
    pad = 30 * S
    d.rounded_rectangle((pad, pad, w * S - pad, h * S - pad), radius=60 * S, fill=255)
    rng = np.random.default_rng(seed)
    for t in np.linspace(0, 1, 26):     # 波打つふち（雲）
        for (x, y) in ((pad + t * (w * S - 2 * pad), pad), (pad + t * (w * S - 2 * pad), h * S - pad),
                       (pad, pad + t * (h * S - 2 * pad)), (w * S - pad, pad + t * (h * S - 2 * pad))):
            r = rng.uniform(22, 34) * S
            d.ellipse((x - r, y - r, x + r, y + r), fill=255)
    m = m.resize((w, h), Image.LANCZOS)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out = Image.new("RGBA", (w, h), BROWN + (255,))
    out.putalpha(m.filter(ImageFilter.MaxFilter(7)))
    im.alpha_composite(out)
    body = Image.new("RGBA", (w, h), RED + (255,))
    rays = ImageDraw.Draw(body)
    cx, cy = w * 0.5, h * 1.05
    for k in range(36):
        a0 = math.pi + k * math.pi / 36
        a1 = a0 + math.pi / 72
        R = max(w, h) * 1.6
        col = (214, 74, 38) if k % 2 == 0 else RED
        rays.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))],
                     fill=col + (255,))
    body.putalpha(m)
    im.alpha_composite(body)
    return im


def retro_text(text, size, font=KAISEI, fill=CREAM, mid=RED, outer=BROWN, s_mid=None, s_out=None, spacing=0):
    """生成りの文字に朱のふち、その外に焦げ茶のふち、右下に影（サムネと同じ重ね方）"""
    f = F(font, size)
    s_mid = s_mid if s_mid is not None else max(4, size // 18)
    s_out = s_out if s_out is not None else s_mid + max(4, size // 22)
    pad = s_out * 2 + 20
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    bb = tmp.textbbox((0, 0), text, font=f)
    w, h = bb[2] - bb[0] + pad * 2 + spacing * len(text), bb[3] - bb[1] + pad * 2
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))

    def draw(dx, dy, col, sw):
        d = ImageDraw.Draw(im)
        x = pad - bb[0] + dx
        if spacing:
            for ch in text:
                d.text((x, pad - bb[1] + dy), ch, font=f, fill=col + (255,), stroke_width=sw, stroke_fill=col + (255,))
                x += tmp.textlength(ch, font=f) + spacing
        else:
            d.text((x, pad - bb[1] + dy), text, font=f, fill=col + (255,), stroke_width=sw, stroke_fill=col + (255,))
    draw(int(size * 0.05) + 2, int(size * 0.06) + 2, (24, 10, 10), s_out)   # 影
    draw(0, 0, outer, s_out)
    draw(0, 0, mid, s_mid)
    draw(0, 0, fill, 0)
    return im.crop(im.getbbox())


def plain_text(img, xy, text, size, fill=TEAL, font=KAISEI, anchor="mm", parts=None):
    """parts=[(文字, 色)] で一部の色を変える"""
    d = ImageDraw.Draw(img)
    f = F(font, size)
    if not parts:
        d.text(xy, text, font=f, fill=fill + (255,), anchor=anchor)
        return
    total = sum(d.textlength(s, font=f) for s, _ in parts)
    x = xy[0] - total / 2
    for s, col in parts:
        d.text((x, xy[1]), s, font=f, fill=col + (255,), anchor="lm")
        x += d.textlength(s, font=f)


def new_moon(img, cx, cy, r, seed=8):
    """黒い新月に金のふちの光と、蠍座の記号"""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40), fill=(255, 196, 110, 150))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(34)))
    rng = np.random.default_rng(seed)
    S = r * 2
    n = Image.fromarray((rng.random((S, S)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
    n2 = Image.fromarray((rng.random((S, S)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    a = np.asarray(n, np.float32)
    b = np.asarray(n2, np.float32)
    tone = 40 + (a - a.mean()) * 0.9 + (b - b.mean()) * 0.25
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    rr = np.hypot(xx - r, yy - r) / r
    tone = tone - 18 * rr ** 2
    moon = np.dstack([tone + 4, tone, tone - 2]).clip(0, 255).astype(np.uint8)
    m = Image.new("L", (S * 2, S * 2), 0)
    ImageDraw.Draw(m).ellipse((0, 0, S * 2 - 1, S * 2 - 1), fill=255)
    mi = Image.fromarray(moon).convert("RGBA")
    mi.putalpha(m.resize((S, S), Image.LANCZOS))
    img.alpha_composite(mi, (cx - r, cy - r))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 214, 140, 255), width=4)
    d.text((cx - 4, cy + 6), "♏", font=F(GLYPH, int(r * 0.95)), fill=CREAM + (255,), anchor="mm")
    sparkle(d, cx + r * 0.52, cy - r * 0.42, r * 0.16, CREAM)


def arrow_down(img, cx, y, size=70, col=CREAM):
    d = ImageDraw.Draw(img)
    for k in range(2):
        yy = y + k * size * 0.55
        d.line([(cx - size * 0.6, yy), (cx, yy + size * 0.5), (cx + size * 0.6, yy)], fill=col + (255 - k * 90,), width=12,
               joint="curve")


def put(img, layer, cx, y):
    img.alpha_composite(layer, (int(cx - layer.width / 2), int(y)))


def footer_count(img, y, text="いま117名が参加中"):
    plain_text(img, (W // 2, y), text, 40, fill=CREAM, font=GOTHIC)


# ---- 1枚目（昼） ----
# 画面の上 200px（名前・進みぐあいの線）と下 230px（返信の欄）には大事なものを置かない。
# 矢印の下 y=1560〜1690 は、インスタのリンクスタンプを置く場所としてあけておく。
def story1():
    img = sky(1, keep_out=[(1080, 1540)])
    sc = scorpius(340, line=GOLD, star=CREAM, antares=(255, 110, 70))
    img.alpha_composite(sc, (590, 820))
    put(img, cloud_plaque(600, 100), W / 2, 196)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 266), "11月9日（月）16:02", font=F(KAISEI, 58), fill=DEEPRED + (255,), anchor="mm")
    put(img, red_panel(860, 540), W / 2, 330)
    put(img, retro_text("蠍座", 215), W / 2, 368)
    put(img, retro_text("新月", 215), W / 2, 594)
    new_moon(img, 330, 965, 118)
    put(img, cloud_plaque(860, 230, bumps=4), W / 2, 1104)
    plain_text(img, (W // 2, 1170), "", 52, parts=[("今回の新月のお話は ", TEAL), ("YouTube", RED), (" で", TEAL)])
    plain_text(img, (W // 2, 1242), "リンクは今夜20時、", 52, fill=TEAL)
    plain_text(img, (W // 2, 1314), "", 52, parts=[("一斉配信チャンネル", RED), ("にお届け", TEAL)])
    plain_text(img, (W // 2, 1408), "いま117名が参加中", 40, fill=CREAM, font=GOTHIC)
    put(img, retro_text("参加はここから", 74, s_mid=4, s_out=9), W / 2, 1440)
    arrow_down(img, W // 2, 1540 - 2, 44)
    paper_frame(img)
    return grain(img, 5, 7)


# ---- 2枚目（20時） ----
def story2():
    img = sky(2, keep_out=[(1080, 1540)])
    sc = scorpius(360, line=GOLD, star=CREAM, antares=(255, 110, 70))
    img.alpha_composite(sc, (80, 830))
    put(img, cloud_plaque(560, 100), W / 2, 196)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 266), "11月9日 蠍座新月", font=F(KAISEI, 58), fill=DEEPRED + (255,), anchor="mm")
    put(img, red_panel(920, 520), W / 2, 330)
    put(img, retro_text("YouTube", 186), W / 2, 380)
    put(img, retro_text("公開しました", 140), W / 2, 600)
    new_moon(img, 760, 970, 124)
    put(img, cloud_plaque(860, 120, bumps=3), W / 2, 1110)
    plain_text(img, (W // 2, 1190), "", 68, parts=[("あなたの", TEAL), ("縁", RED), ("が動き出す", TEAL)])
    plain_text(img, (W // 2, 1340), "", 52, parts=[("リンクは", CREAM), ("一斉配信チャンネル", GOLD), ("へ", CREAM)])
    put(img, retro_text("まだの方はここから", 70, s_mid=4, s_out=9), W / 2, 1420)
    arrow_down(img, W // 2, 1530, 44)
    paper_frame(img)
    return grain(img, 6, 7)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    a, b = story1().convert("RGB"), story2().convert("RGB")
    a.save(os.path.join(OUT, "ストーリーズ1_昼_11月9日蠍座新月.png"))
    b.save(os.path.join(OUT, "ストーリーズ2_20時_11月9日蠍座新月.png"))
    both = Image.new("RGB", (W * 2 + 40, H), (255, 255, 255))
    both.paste(a, (0, 0))
    both.paste(b, (W + 40, 0))
    both.resize((both.width // 2, H // 2)).save(os.path.join(OUT, "ストーリーズ_2枚まとめ.png"))
    print("ok")
