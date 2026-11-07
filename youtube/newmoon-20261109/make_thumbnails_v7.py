"""11/9 蠍座新月のサムネイル案 第7弾：妖怪系／女性のポートレート（1280×720、文字は特大）。

参考にした雰囲気（いま活躍中の作家さんの絵なので、絵柄はまねない）を、パブリックドメインの本物の素材で作る：
  P 妖怪系：能面「小面」（18世紀、メトロポリタン美術館）を紫の水面に3つ浮かべ、水の中はゆらゆらゆがむ。
    「本音で話したい」という台本の入口から、「仮面を外す」。
  Q 女性：明治初めの手彩色写真の女性（鈴木真一、1870年代）。セピアにして帯の赤だけ残し、
    墨の枝と朱の実を重ねたコラージュ。毎回この女性を「顔」にすると、シリーズの印になる。
    python3 make_thumbnails_v7.py
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_thumbnails_v6 import branch, paper, vtext  # noqa: E402

FONTS = os.path.join(HERE, "..", "fonts")
PD = os.path.join(HERE, "public_domain")
OUT = os.path.join(HERE, "thumbnails")
W, H = 1280, 720
NO_TEXT = False  # True のときは文字・印を入れない（第8弾で上から大きな文字をかぶせるため）
OLDM = os.path.join(FONTS, "ZenOldMincho-Black.ttf")
SANS = os.path.join(FONTS, "ZenKakuGothicNew-Black.ttf")
BRUSH = os.path.join(FONTS, "YujiSyuku-Regular.ttf")


def F(path, size):
    return ImageFont.truetype(path, size)


# ---- P 妖怪系 ----
def violet_water(seed=1):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (xx / W * 0.6 + yy / H * 0.4)
    c0, c1 = np.array([118, 74, 246], np.float32), np.array([48, 22, 168], np.float32)
    img = c0 * (1 - t[..., None]) + c1 * t[..., None]
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 4, (H // 2, W // 2)).astype(np.float32)
    img += np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def ripples(img, cx, cy, rx, n=5, color=(176, 150, 255)):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(n):
        r = rx * (1.0 + 0.28 * k)
        a = int(170 * (1 - k / n))
        d.ellipse((cx - r, cy - r * 0.22, cx + r, cy + r * 0.22), outline=color + (a,), width=3)
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))


_mask = None


def mask_img():
    """能面。目と口の穴（背景の灰色が見えている所）は、暗く塗る。"""
    global _mask
    if _mask is None:
        m = Image.open(os.path.join(PD, "ko_omote_cut.png")).convert("RGBA")
        a = np.asarray(m).astype(np.float32)
        sat = a[..., :3].max(2) - a[..., :3].min(2)
        br = a[..., :3].mean(2)
        h = a.shape[0]
        yy = np.mgrid[0:h, 0:a.shape[1]][0]
        hole = (sat < 16) & (br > 70) & (br < 190) & (a[..., 3] > 200) & (yy > h * 0.45)
        a[hole, :3] = [24, 10, 34]
        _mask = Image.fromarray(a.astype(np.uint8))
    return _mask


def floating_mask(img, cx, top, height, waterline=0.62, tint=(96, 60, 230), seed=0):
    """水面に半分沈んだ能面。水の中の部分は横にゆらぎ、紫に染まって透ける。"""
    m = mask_img().resize((int(mask_img().width * height / mask_img().height), height), Image.LANCZOS)
    w, h = m.size
    wl = int(h * waterline)
    arr = np.asarray(m).astype(np.float32)
    out = arr.copy()
    rng = np.random.default_rng(seed)
    ph = rng.random() * 6
    for y in range(wl, h):
        depth = (y - wl) / max(1, h - wl)
        amp = 6 + 26 * depth
        shift = int(amp * math.sin(y * 0.09 + ph) + amp * 0.4 * math.sin(y * 0.23 + ph * 2))
        out[y] = np.roll(arr[y], shift, axis=0)
        k = 0.45 + 0.35 * depth
        out[y, :, :3] = out[y, :, :3] * (1 - k) + np.array(tint, np.float32) * k
        out[y, :, 3] *= (0.85 - 0.6 * depth)
    sub = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    x0 = int(cx - w / 2)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    s_ = Image.new("RGBA", sub.size, (20, 6, 60, 0))
    s_.putalpha(sub.split()[3].point(lambda v: int(v * 0.45)))
    sh.alpha_composite(s_, (x0 + 14, top + 18))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(sub, (x0, top))
    ripples(img, cx, top + wl, w * 0.55, n=4)
    hl = Image.new("RGBA", img.size, (0, 0, 0, 0))  # 水面の境目の光
    ImageDraw.Draw(hl).ellipse((x0 + w * 0.02, top + wl - 7, x0 + w * 0.98, top + wl + 7), outline=(226, 214, 255, 210), width=3)
    img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(1.5)))


def make_p():
    img = violet_water(3)
    floating_mask(img, 640, 60, 330, waterline=0.58, seed=1)
    floating_mask(img, 1150, 90, 300, waterline=0.6, seed=2)
    floating_mask(img, 880, 170, 520, waterline=0.66, seed=3)
    # 特大の文字（縦書き2列）
    vtext(img, 140, 20, "蠍座新月", 172, (255, 246, 232), step=170, stroke=8, stroke_fill=(30, 8, 70))
    vtext(img, 352, 40, "仮面を", 150, (255, 86, 70), step=148, stroke=8, stroke_fill=(30, 8, 70))
    vtext(img, 352, 40 + 148 * 3, "外す", 120, (255, 86, 70), step=118, stroke=7, stroke_fill=(30, 8, 70))
    if not NO_TEXT:
        ImageDraw.Draw(img).text((1250, 690), "11.9 16:02", font=F(SANS, 30), fill=(230, 220, 255, 255), anchor="rs")
    return img


# ---- Q 女性のポートレート ----
def sepia_keep_red(im):
    """セピアにして、赤い所（帯・唇）だけ色を残す"""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    lum = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2])[..., None]
    sep = np.concatenate([lum * 1.07 + 6, lum * 0.95, lum * 0.78 - 4], axis=2)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = np.clip((r - np.maximum(g, b) - 40) / 50, 0, 1)[..., None]
    out = sep * (1 - red) + a * red
    out = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    out = ImageEnhance.Contrast(out).enhance(1.35)
    return out


def make_q():
    img = paper((226, 210, 180), 101, grain=6, vign=0.28)
    ph = Image.open(os.path.join(PD, "woman_1870s.jpg"))
    ph = ph.crop((380, 520, 1720, 2250))
    ph = sepia_keep_red(ph)
    ph = ph.resize((int(ph.width * 800 / ph.height), 800), Image.LANCZOS)
    # 写真のふちを紙になじませる（だ円のぼかし）
    m = Image.new("L", ph.size, 0)
    ImageDraw.Draw(m).ellipse((ph.width * 0.06, ph.height * 0.02, ph.width * 0.94, ph.height * 1.15), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(40))
    phr = ph.convert("RGBA")
    phr.putalpha(m)
    # 紙と写真を「乗算」で重ねる
    base = np.asarray(img).astype(np.float32)
    lay = np.zeros_like(base)
    lay[..., :3] = 255
    x0, y0 = 690, -30
    sub = np.asarray(phr).astype(np.float32)
    hh, ww = sub.shape[:2]
    ys, xs = slice(max(0, y0), min(H, y0 + hh)), slice(max(0, x0), min(W, x0 + ww))
    sy, sx = slice(ys.start - y0, ys.stop - y0), slice(xs.start - x0, xs.stop - x0)
    al = sub[sy, sx, 3:4] / 255
    lay[ys, xs, :3] = sub[sy, sx, :3] * al + 255 * (1 - al)
    base[..., :3] = base[..., :3] * lay[..., :3] / 255
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    # 墨の枝と朱の実（写真の上にも少しかかる）
    br = branch(seed=7, scale=1.25)
    img.alpha_composite(br.transpose(Image.FLIP_LEFT_RIGHT), (W - br.width + 40, 260))
    # 特大の筆文字（縦書き）
    vtext(img, 150, 14, "蠍座新月", 176, (26, 20, 20), step=172, stroke=2, stroke_fill=(26, 20, 20), shadow=False)
    lay2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    vtext(lay2, 380, 40, "縁が", 160, (184, 30, 30), step=158, stroke=1, stroke_fill=(184, 30, 30), shadow=False)
    vtext(lay2, 380, 40 + 158 * 2, "動く", 160, (184, 30, 30), step=158, stroke=1, stroke_fill=(184, 30, 30), shadow=False)
    img.alpha_composite(lay2)
    if NO_TEXT:
        return img
    # 朱の印と日付
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((520, 600, 600, 690), 8, fill=(196, 42, 34, 255))
    d.text((560, 645), "星読", font=F(BRUSH, 34), fill=(250, 236, 220, 255), anchor="mm")
    d.text((620, 690), "11.9 16:02", font=F(SANS, 30), fill=(70, 50, 40, 255), anchor="ls")
    return img


if __name__ == "__main__":
    import make_thumbnails_v6 as v6
    v6.OLDM = BRUSH  # Q の縦書きは筆文字にする（P は明朝のまま、下で戻す）
    os.makedirs(OUT, exist_ok=True)
    outs = []
    v6.OLDM = OLDM
    outs.append(("P", make_p()))
    v6.OLDM = BRUSH
    outs.append(("Q", make_q()))
    v6.OLDM = OLDM
    ims = []
    for key, im in outs:
        im = im.convert("RGB")
        im.save(os.path.join(OUT, f"サムネイル第7弾{key}_11月9日蠍座新月.png"))
        ims.append(im)
    sm = Image.new("RGB", (2 * 380, 230), (255, 255, 255))
    for i, im in enumerate(ims):
        sm.paste(im.resize((360, 203), Image.LANCZOS), (10 + i * 380, 14))
    sm.save(os.path.join(OUT, "第7弾_スマホで見たときの大きさ.png"))
    big = Image.new("RGB", (1280, 720 * 2))
    for i, im in enumerate(ims):
        big.paste(im, (0, i * 720))
    big.resize((960, 1080)).save(os.path.join(OUT, "第7弾_2案まとめ.png"))
    print("ok")
