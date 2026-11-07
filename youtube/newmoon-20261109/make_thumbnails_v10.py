"""11/9 蠍座新月のサムネイル案 第10弾：特大の迫力はそのままに、おますさんの型にする（1280×720）。

第9弾は「左右に特大2文字・真ん中に絵・下に横長の一行・紺白赤」が現実主義タロットさんの型と同じだったので、
次の4つを変える：左右対称をやめて片側に縦の大きな文字の列／絵は真ん中ではなく画面の端からはみ出す／
横長の帯の一行は使わず、縦の札か大きな落款／色は和紙・墨・朱、文字は筆文字。
  R 縦の筆文字：左に愛染明王の円が画面からはみ出し、右に縦一列の特大の筆文字、間に朱の縦の札。
  S 大きな落款：墨の地に、右半分いっぱいの朱の落款「蠍座／新月」。左に能面、下に筆文字の言葉。
  T 言葉が主役：左に明治の写真の女性、右に縦の特大の朱の筆文字「縁が動く」。
    python3 make_thumbnails_v10.py
"""
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
BRUSH = os.path.join(FONTS, "YujiSyuku-Regular.ttf")
OLDM = os.path.join(FONTS, "ZenOldMincho-Black.ttf")
SANS = os.path.join(FONTS, "ZenKakuGothicNew-Black.ttf")

WASHI = (236, 226, 206)
SUMI = (24, 20, 22)
SHU = (200, 40, 30)
CREAM = (248, 238, 220)


def F(path, size):
    return ImageFont.truetype(path, size)


def vcol(img, x, y, s, size, fill, step, font=BRUSH, stroke=0, stroke_fill=None, shadow=0.0):
    """縦書きの列。x は文字の中心。"""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = F(font, size)
    for i, ch in enumerate(s):
        d.text((x, y + i * step), ch, font=f, fill=fill + (255,), anchor="mt", stroke_width=stroke,
               stroke_fill=(stroke_fill or fill) + (255,))
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(lay.split()[3].point(lambda v: int(v * shadow)))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (6, 9))
    img.alpha_composite(lay)


def rough(mask, seed=0, amount=0.5):
    """ふちを少しかすれさせる（朱肉・墨のにじみ）"""
    rng = np.random.default_rng(seed)
    a = np.asarray(mask).astype(np.float32)
    h, w = a.shape
    n = rng.random((h // 3 + 1, w // 3 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC), np.float32)
    edge = (a > 20) & (a < 235)
    a = np.where(edge & (n < amount), a * 0.2, a)
    speck = rng.random(a.shape) < 0.004
    a = np.where(speck & (a > 200), 60, a)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def big_seal(size, rows, color=SHU, text=CREAM, seed=3, font=OLDM):
    """大きな落款（白文印：朱の地に文字を抜く）。rows = ["蠍座", "新月"]"""
    S = 2
    n = size * S
    m = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, n - 1, n - 1), int(n * 0.04), fill=255)
    letters = Image.new("L", (n, n), 0)
    dl = ImageDraw.Draw(letters)
    cs = int(n * 0.43)
    f = F(font, cs)
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            cx = n * (0.27 + 0.46 * c)
            cy = n * (0.27 + 0.46 * r)
            dl.text((cx, cy), ch, font=f, fill=255, anchor="mm")
    seal_a = rough(m.resize((size, size), Image.LANCZOS), seed, 0.45)
    let_a = rough(letters.resize((size, size), Image.LANCZOS), seed + 1, 0.3)
    out = Image.new("RGBA", (size, size), color + (255,))
    # 朱肉のむら
    rng = np.random.default_rng(seed)
    g = rng.random((size // 6, size // 6)).astype(np.float32)
    g = np.asarray(Image.fromarray(g).resize((size, size), Image.BICUBIC), np.float32)[..., None]
    arr = np.asarray(out).astype(np.float32)
    arr[..., :3] = arr[..., :3] * (0.88 + 0.18 * g)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    out.putalpha(seal_a)
    t = Image.new("RGBA", (size, size), text + (255,))
    t.putalpha(let_a)
    out.alpha_composite(t)
    return out


def small_seal(text, d=110, color=SHU):
    im = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    m = Image.new("L", (d * 2, d * 2), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d * 2 - 1, d * 2 - 1), fill=255)
    lt = Image.new("L", (d * 2, d * 2), 0)
    ImageDraw.Draw(lt).text((d, d * 0.98), text, font=F(BRUSH, int(d * 0.62)), fill=255, anchor="mm")
    im = Image.new("RGBA", (d, d), color + (255,))
    im.putalpha(rough(m.resize((d, d), Image.LANCZOS), 9, 0.4))
    t = Image.new("RGBA", (d, d), CREAM + (255,))
    t.putalpha(lt.resize((d, d), Image.LANCZOS))
    im.alpha_composite(t)
    return im


def aizen(R):
    ai = Image.open(os.path.join(PD, "aizen_circle.png")).convert("RGBA").resize((R * 2, R * 2), Image.LANCZOS)
    a_ = ai.split()[3]
    rgb = ImageOps.autocontrast(ai.convert("RGB"), cutoff=1, preserve_tone=True)
    rgb = ImageEnhance.Brightness(ImageEnhance.Color(rgb).enhance(1.2)).enhance(1.12)
    ai = rgb.convert("RGBA")
    ai.putalpha(a_)
    return ai


# ---- R 縦の筆文字 ----
def make_r():
    img = v6.paper(WASHI, 111, grain=6, vign=0.18)
    R = 430
    ai = aizen(R)
    cx, cy = 300, 330  # 左と上下にはみ出す
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    s_ = Image.new("RGBA", ai.size, (40, 10, 10, 0))
    s_.putalpha(ai.split()[3].point(lambda v: int(v * 0.5)))
    sh.alpha_composite(s_, (cx - R + 14, cy - R + 16))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(ai, (cx - R, cy - R))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(196, 150, 70, 255), width=6)
    # 朱の縦の札（上から下まで）
    d.rectangle((790, -10, 930, H + 10), fill=SHU + (255,))
    d.line((800, 0, 800, H), fill=CREAM + (200,), width=2)
    d.line((920, 0, 920, H), fill=CREAM + (200,), width=2)
    vcol(img, 860, 70, "縁が動く", 128, CREAM, step=136, font=BRUSH)
    # 右：縦一列の特大の筆文字（上下の端にかかる）
    vcol(img, 1112, -8, "蠍座新月", 190, SUMI, step=180, font=BRUSH, stroke=2, stroke_fill=SUMI)
    img.alpha_composite(small_seal("星読", 78), (936, 626))
    ImageDraw.Draw(img).text((860, 640), "11.9", font=F(SANS, 30), fill=CREAM + (255,), anchor="mm")
    return img


# ---- S 大きな落款 ----
def make_s():
    img = v6.paper(SUMI, 112, grain=5, vign=0.35)
    # 左：能面に上から光
    light = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(light).ellipse((-40, -80, 640, 660), fill=(120, 100, 90, 90))
    img.alpha_composite(light.filter(ImageFilter.GaussianBlur(60)))
    mk = v7.mask_img()
    mh = 600
    mk = mk.resize((int(mk.width * mh / mk.height), mh), Image.LANCZOS)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    s_ = Image.new("RGBA", mk.size, (0, 0, 0, 0))
    s_.putalpha(mk.split()[3].point(lambda v: int(v * 0.7)))
    sh.alpha_composite(s_, (60 + 16, 10 + 20))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    img.alpha_composite(mk, (60, 10))
    # 右：特大の落款（上下にはみ出す）
    seal = big_seal(760, ["蠍座", "新月"], seed=5).rotate(-3, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(seal, (W - seal.width + 70, (H - seal.height) // 2))
    # 下：筆文字の言葉（能面の下にかかる）
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((40, 420), "本音で、", font=F(BRUSH, 110), fill=CREAM + (255,), stroke_width=3, stroke_fill=SUMI + (255,))
    d.text((30, 520), "縁が動く", font=F(BRUSH, 148), fill=(255, 92, 70, 255), stroke_width=4, stroke_fill=SUMI + (255,))
    sh2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh2.putalpha(lay.split()[3].point(lambda v: int(v * 0.8)))
    img.alpha_composite(sh2.filter(ImageFilter.GaussianBlur(10)), (5, 8))
    img.alpha_composite(lay)
    ImageDraw.Draw(img).text((520, 30), "11.9", font=F(SANS, 36), fill=CREAM + (255,), anchor="ra")
    return img


# ---- T 言葉が主役 ----
def make_t():
    img = v6.paper(WASHI, 113, grain=6, vign=0.2)
    ph = Image.open(os.path.join(PD, "woman_1870s.jpg")).crop((300, 420, 1800, 2400))
    ph = v7.sepia_keep_red(ph)
    ph = ph.resize((int(ph.width * 780 / ph.height), 780), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", ph.size, 255)
    grad = np.linspace(255, 0, 140)
    a = np.asarray(m).astype(np.float32)
    a[:, -140:] = grad[None, :]
    m = Image.fromarray(a.astype(np.uint8))
    ph.putalpha(m)
    base = np.asarray(img).astype(np.float32)
    sub = np.asarray(ph).astype(np.float32)
    x0, y0 = -40, -40
    hh, ww = sub.shape[:2]
    ys, xs = slice(0, min(H, y0 + hh)), slice(0, min(W, x0 + ww))
    sy, sx = slice(-y0, -y0 + ys.stop), slice(-x0, -x0 + xs.stop)
    al = sub[sy, sx, 3:4] / 255
    lay = sub[sy, sx, :3] * al + 255 * (1 - al)
    base[ys, xs, :3] = base[ys, xs, :3] * lay / 255
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    vcol(img, 1120, -10, "縁が動く", 190, SHU, step=180, font=BRUSH, stroke=2, stroke_fill=SHU)
    vcol(img, 900, 40, "あの人との", 112, SUMI, step=118, font=BRUSH)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 330, 70), fill=SUMI + (255,))
    d.text((24, 35), "11.9 蠍座新月", font=F(SANS, 40), fill=CREAM + (255,), anchor="lm")
    img.alpha_composite(small_seal("星読", 100), (860, 600))
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for key, fn in (("R", make_r), ("S", make_s), ("T", make_t)):
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第10弾{key}_11月9日蠍座新月.png"))
        ims.append(im)
    sm = Image.new("RGB", (3 * 380, 230), (255, 255, 255))
    for i, im in enumerate(ims):
        sm.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    sm.save(os.path.join(OUT, "第10弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 3))
    for i, im in enumerate(ims):
        big.paste(im, (0, i * 720))
    big.resize((960, 1620)).save(os.path.join(OUT, "第10弾_3案まとめ.png"))
    print("ok")
