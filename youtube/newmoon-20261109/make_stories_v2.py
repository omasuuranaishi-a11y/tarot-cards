"""11/9 蠍座新月：インスタのストーリーズ 2枚（1080×1920）・おますさんのインスタの世界観に合わせた版。

おますさんのいつものストーリーズ（Canva で作っているもの）に合わせる：
  生成り・うすいセージの地、濃いグレーの丸ゴシック（字間広め）、くすんだ赤の差し色と下線、
  上に小さな金の三日月と星、細い内枠、うすいベージュの札、点線の区切り、余白たっぷり、
  お知らせのときは、うすい方眼のセージの地に白い波形のカードとアイコン。
（make_stories.py のレトロなポスター風は「インスタの雰囲気ではない」とのことでやめた）
  1枚目（昼）：生成りの地＋細い内枠
  2枚目（20時）：セージの方眼＋白い波形のカード＋アイコン
矢印の下は、インスタのリンクスタンプを置く場所としてあけてある。
    python3 make_stories_v2.py
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
MARU_B = os.path.join(FONTS, "ZenMaruGothic-Bold.ttf")
MARU_M = os.path.join(FONTS, "ZenMaruGothic-Medium.ttf")
ICON = os.path.join(HERE, "..", "2027-unsei-pr", "assets", "icon.png")
OUT = os.path.join(HERE, "stories")
W, H = 1080, 1920

CREAM_BG = (243, 240, 232)
SAGE_BG = (222, 228, 220)
CARD = (251, 250, 246)
TEXT = (62, 60, 58)
SUB = (118, 113, 106)
ACCENT = (178, 82, 72)
GOLD = (200, 165, 92)
PILL = (234, 228, 216)
LINE = (214, 208, 196)


def F(path, size):
    return ImageFont.truetype(path, size)


# ---- 地 ----
def soft_bg(base, blobs=(), seed=0, grain=2.5):
    """やわらかい地：うっすらとした色のにじみと、ごく細かい紙の目"""
    rng = np.random.default_rng(seed)
    img = np.ones((H, W, 3), np.float32) * np.array(base, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for col, cx, cy, r, k in blobs:
        m = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))[..., None] * k
        img = img * (1 - m) + np.array(col, np.float32) * m
    img += rng.normal(0, grain, (H, W)).astype(np.float32)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def grid(img, step=28, col=(212, 219, 210)):
    d = ImageDraw.Draw(img)
    for x in range(0, W, step):
        d.line((x, 0, x, H), fill=col + (255,), width=1)
    for y in range(0, H, step):
        d.line((0, y, W, y), fill=col + (255,), width=1)


def inner_frame(img, m=56, col=LINE):
    ImageDraw.Draw(img).rounded_rectangle((m, m, W - m, H - m), radius=10, outline=col + (255,), width=2)


def scallop_card(img, box, r=34, col=CARD):
    """ふちが波形の白いカード"""
    x0, y0, x1, y1 = box
    S = 2
    m = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(m)
    d.rectangle((x0 * S, y0 * S, x1 * S, y1 * S), fill=255)
    nx = max(2, round((x1 - x0) / (r * 1.7)))
    ny = max(2, round((y1 - y0) / (r * 1.7)))
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * i / nx
        for y in (y0, y1):
            d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=255)
    for j in range(ny + 1):
        y = y0 + (y1 - y0) * j / ny
        for x in (x0, x1):
            d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=255)
    m = m.resize((W, H), Image.LANCZOS)
    sh = Image.new("RGBA", (W, H), (120, 130, 120, 0))
    sh.putalpha(m.point(lambda v: int(v * 0.18)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (0, 4))
    lay = Image.new("RGBA", (W, H), col + (255,))
    lay.putalpha(m)
    img.alpha_composite(lay)


# ---- 飾り ----
def crescent(img, cx, cy, r, col=GOLD):
    """小さな金の三日月と、そばの星"""
    S = 4
    size = int(r * 2.6)
    m = Image.new("L", (size * S, size * S), 0)
    d = ImageDraw.Draw(m)
    c = size * S / 2
    R = r * S
    d.ellipse((c - R, c - R, c + R, c + R), fill=255)
    d.ellipse((c - R * 0.62, c - R * 1.12, c + R * 1.28, c + R * 0.78), fill=0)
    m = m.rotate(-18, resample=Image.BICUBIC).resize((size, size), Image.LANCZOS)
    lay = Image.new("RGBA", (size, size), col + (255,))
    lay.putalpha(m)
    img.alpha_composite(lay, (int(cx - size / 2), int(cy - size / 2)))
    dd = ImageDraw.Draw(img)
    star(dd, cx + r * 1.15, cy - r * 0.95, r * 0.22, col)
    for dx, dy, s in ((-1.5, -0.7, 3), (1.6, 0.5, 2.5), (-1.2, 1.1, 2)):
        x, y = cx + dx * r, cy + dy * r
        dd.ellipse((x - s, y - s, x + s, y + s), fill=col + (170,))


def star(d, x, y, s, col):
    k = s * 0.22
    d.polygon([(x, y - s), (x + k, y - k), (x + s, y), (x + k, y + k), (x, y + s), (x - k, y + k), (x - s, y), (x - k, y - k)],
              fill=col + (255,))


def icon_circle(d_px):
    im = Image.open(ICON).convert("RGBA").crop((190, 90, 890, 790)).resize((d_px, d_px), Image.LANCZOS)
    m = Image.new("L", (d_px * 4, d_px * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d_px * 4 - 1, d_px * 4 - 1), fill=255)
    im.putalpha(m.resize((d_px, d_px), Image.LANCZOS))
    return im


# ---- 文字 ----
def text_line(img, y, segs, size, font=MARU_B, track=0.08, anchor_y="m"):
    """1行を真ん中にそろえて書く。segs = [(文字, 色, 下線するか)]。字間は size*track。"""
    d = ImageDraw.Draw(img)
    f = F(font, size)
    gap = size * track
    chars = [(ch, col, ul) for s, col, ul in segs for ch in s]
    widths = [d.textlength(ch, font=f) for ch, _, _ in chars]
    total = sum(widths) + gap * (len(chars) - 1)
    vis = total
    if chars and chars[-1][0] in "、。，．":   # 最後の句読点は数えずに中心をとる（見た目の中心をそろえる）
        vis -= widths[-1] * 0.55 + gap
    x = W / 2 - vis / 2
    spans = []
    for (ch, col, ul), w in zip(chars, widths):
        d.text((x, y), ch, font=f, fill=col + (255,), anchor="l" + anchor_y)
        if ul:
            spans.append((x, x + w))
        x += w + gap
    if spans:   # 下線（つながった文字ごとに1本）
        x0, x1 = spans[0][0], spans[0][1]
        for a, b in spans[1:]:
            if a - x1 <= gap * 1.5:
                x1 = b
            else:
                d.line((x0, y + size * 0.62, x1, y + size * 0.62), fill=ACCENT + (255,), width=max(3, size // 18))
                x0, x1 = a, b
        d.line((x0, y + size * 0.62, x1, y + size * 0.62), fill=ACCENT + (255,), width=max(3, size // 18))
    return total


def play_line(img, y, before, word, after, size, col_word=ACCENT, col=TEXT, track=0.04):
    """再生ボタンのしるし＋「YouTube」で、YouTube だとひと目でわかる行。全体を真ん中にそろえる。"""
    d = ImageDraw.Draw(img)
    f = F(MARU_B, size)
    gap = size * track
    segs = [(before, col), (word, col_word), (after, col)]
    chars = [(ch, c) for t, c in segs for ch in t]
    widths = [d.textlength(ch, font=f) for ch, _ in chars]
    tw = sum(widths) + gap * (len(chars) - 1)
    bw, bh = int(size * 1.25), int(size * 0.88)
    total = bw + size * 0.3 + tw
    x = W / 2 - total / 2
    d.rounded_rectangle((x, y - bh / 2, x + bw, y + bh / 2), radius=int(bh * 0.28), fill=col_word + (255,))
    cx, cy, t = x + bw / 2 + bw * 0.04, y, bh * 0.24
    d.polygon([(cx - t * 0.8, cy - t), (cx - t * 0.8, cy + t), (cx + t * 1.0, cy)], fill=CARD + (255,))
    x += bw + size * 0.3
    for (ch, c), w in zip(chars, widths):
        d.text((x, y), ch, font=f, fill=c + (255,), anchor="lm")
        x += w + gap


def label(img, y, s, size=30, col=SUB, line_len=70):
    """— 小さな見出し —"""
    w = text_line(img, y, [(s, col, False)], size, font=MARU_M, track=0.12)
    d = ImageDraw.Draw(img)
    for sgn in (-1, 1):
        x = W / 2 + sgn * (w / 2 + 24)
        d.line((x, y, x + sgn * line_len, y), fill=col + (200,), width=2)


def pill(img, y, s, size=38, fill=PILL, col=TEXT, padx=40, pady=18):
    d = ImageDraw.Draw(img)
    f = F(MARU_B, size)
    w = sum(d.textlength(ch, font=f) for ch in s) + size * 0.08 * (len(s) - 1)
    d.rounded_rectangle((W / 2 - w / 2 - padx, y - size / 2 - pady, W / 2 + w / 2 + padx, y + size / 2 + pady),
                        radius=int(size / 2 + pady), fill=fill + (255,))
    text_line(img, y, [(s, col, False)], size)


def dotted(img, y, x0=200, x1=880, col=LINE):
    d = ImageDraw.Draw(img)
    x = x0
    while x < x1:
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=col + (255,))
        x += 14


def thin(img, y, x0=180, x1=900, col=LINE):
    ImageDraw.Draw(img).line((x0, y, x1, y), fill=col + (255,), width=2)


def chevron(img, y, col=SUB, s=18):
    d = ImageDraw.Draw(img)
    for k in range(2):
        yy = y + k * s * 0.9
        d.line([(W / 2 - s, yy), (W / 2, yy + s * 0.8), (W / 2 + s, yy)], fill=col + (255 - k * 90,), width=4, joint="curve")


def ellipsis(img, y, col=SUB):
    d = ImageDraw.Draw(img)
    for k in (-1, 0, 1):
        x = W / 2 + k * 18
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=col + (200,))


# ---- 1枚目（昼）：生成り＋細い内枠 ----
# 画面の上 200px（名前の欄）には大事なものを置かない。矢印の下はリンクスタンプの場所として大きくあける。
# 文字は「もう少し大きく」（2026-11-08）で、見出し90・本文46・赤の行58・札と案内44。
def story1():
    """見出し90・100、日付と参加人数なし。行間はいつものストーリーズのようにゆったり（本文は字の約2倍）。
    矢印の下 y=1350〜 をリンクスタンプのためにあける。"""
    img = soft_bg(CREAM_BG, [((236, 222, 210), 880, 520, 260, 0.5), ((226, 232, 222), 200, 1500, 300, 0.5)], seed=1)
    inner_frame(img)
    crescent(img, W / 2, 250, 40)
    text_line(img, 380, [("明日は", TEXT, False)], 90, track=0.06)
    text_line(img, 512, [("蠍座の新月", TEXT, True)], 100, track=0.05)
    text_line(img, 680, [("いつもストーリーズでお届けしている", SUB, False)], 42, font=MARU_M, track=0.04)
    text_line(img, 762, [("新月のお話、今回は", SUB, False)], 42, font=MARU_M, track=0.04)
    play_line(img, 880, "", "YouTube", "で", 84)
    thin(img, 980)
    text_line(img, 1066, [("リンクは今夜20時、", TEXT, False)], 50, track=0.06)
    text_line(img, 1150, [("一斉配信チャンネル", TEXT, True), ("でお届け", TEXT, False)], 50, track=0.05)
    text_line(img, 1262, [("参加はこちらから", SUB, False)], 40, font=MARU_M)
    chevron(img, 1302, s=22)
    return img


# ---- 2枚目（20時）：セージの方眼＋白い波形のカード＋アイコン ----
def story2():
    """1枚目と同じく行間をゆったり。矢印の下 y=1410〜1740 をリンクスタンプのためにあける。"""
    img = soft_bg(SAGE_BG, seed=2, grain=1.5)
    grid(img)
    scallop_card(img, (100, 140, 980, 1780))
    img.alpha_composite(icon_circle(140), (W // 2 - 70, 150))
    label(img, 336, "11/9 蠍座新月", size=36, line_len=60)
    play_line(img, 442, "", "YouTube", "を", 88, col_word=ACCENT)
    text_line(img, 570, [("公開しました", ACCENT, False)], 88, track=0.06)
    pill(img, 710, "「あなたの縁が動き出す」", 46)
    for i, t in enumerate(["見直してきた関係を、", "自分らしい形で育てていく。", "そんな新月のお話です。"]):
        text_line(img, 828 + i * 78, [(t, SUB, False)], 42, font=MARU_M, track=0.05)
    dotted(img, 1062, 220, 860)
    text_line(img, 1140, [("一斉配信チャンネル", TEXT, True), ("に", TEXT, False)], 52, track=0.06)
    text_line(img, 1224, [("リンクをお送りしました", TEXT, False)], 52, track=0.05)
    text_line(img, 1326, [("まだの方はこちらから", SUB, False)], 40, font=MARU_M)
    chevron(img, 1366, s=22)
    return img


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
