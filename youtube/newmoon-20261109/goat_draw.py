"""案内役の山羊のキャラクターを描く（おますさんの山羊のデザインをもとにした絵）。

魔女の帽子（金の帯・三日月の飾り）、巻いた茶色の角、クリーム色のふわふわの顔、垂れ耳、金の留め具のマント。
ポーズ：hello（手をふる）、point（星の杖で指す）、surprise（びっくり）、book（本を読む）、heart（にっこり・ハート）、think（考える）
    python3 goat_draw.py            # astro/goat_<ポーズ>.png と見本の goat_sheet.png を作る
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "astro")

LINE = (88, 60, 52, 255)
CREAM = (252, 246, 234, 255)
CREAM2 = (240, 228, 210, 255)
HAT = (58, 44, 66, 255)
HAT2 = (78, 62, 88, 255)
GOLD = (206, 164, 82, 255)
HORN = (168, 112, 64, 255)
HORN2 = (130, 84, 48, 255)
CAPE = (62, 46, 64, 255)
PINK = (246, 170, 178, 200)
EYE = (52, 36, 40, 255)
LW = 7


def star(cx, cy, r, rot=0):
    pts = []
    for i in range(10):
        a = math.radians(rot - 90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def heart(cx, cy, s):
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s, cy - y * s))
    return pts


def horn(d, x0, y0, side):
    """巻いた角。side = -1（左）/ 1（右）"""
    pts = []
    for i in range(60):
        t = i / 59
        a = math.radians(-100 + side * 0) + side * t * math.radians(330)
        r = 30 + 70 * t
        pts.append((x0 + side * 30 + r * math.cos(a) * side * -1 * -1, y0 + 20 + r * math.sin(a)))
    # 太さを変えながら丸を並べる
    for i, (x, y) in enumerate(pts):
        w = 44 - i * 0.45
        d.ellipse((x - w / 2 - LW / 2, y - w / 2 - LW / 2, x + w / 2 + LW / 2, y + w / 2 + LW / 2), fill=LINE)
    for i, (x, y) in enumerate(pts):
        w = 44 - i * 0.45
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=HORN)
    for i in range(6, 58, 7):  # 角の筋
        x, y = pts[i]
        w = (44 - i * 0.45) / 2
        d.line((x - w * 0.6, y - w * 0.6, x + w * 0.6, y + w * 0.6), fill=HORN2, width=4)


def draw(pose="hello", flip=False):
    S = 2
    W, H = 1100, 1150
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def P(*pts):
        return [(x * S, y * S) for x, y in pts]

    def E(x0, y0, x1, y1, **kw):
        if "width" in kw:
            kw["width"] *= S
        d.ellipse((x0 * S, y0 * S, x1 * S, y1 * S), **kw)

    def L(pts, **kw):
        kw["width"] = kw.get("width", LW) * S
        d.line([(x * S, y * S) for x, y in pts], **kw)

    cx = 550
    # しっぽ（ふわふわ）
    for (x, y, r) in ((780, 1000, 60), (830, 960, 50), (860, 1010, 44)):
        E(x - r - 4, y - r - 4, x + r + 4, y + r + 4, fill=LINE)
    for (x, y, r) in ((780, 1000, 60), (830, 960, 50), (860, 1010, 44)):
        E(x - r, y - r, x + r, y + r, fill=CREAM2)
    # マント
    d.polygon(P((370, 740), (730, 740), (820, 1080), (280, 1080)), fill=CAPE, outline=LINE, width=LW * S)
    E(280, 1030, 820, 1110, fill=CAPE, outline=LINE, width=LW)
    # 胸のふわふわ
    E(cx - 130, 760, cx + 130, 1040, fill=CREAM, outline=LINE, width=LW)
    # 足
    for x in (cx - 90, cx + 90):
        E(x - 60, 1030, x + 60, 1100, fill=CREAM, outline=LINE, width=LW)
    # 留め具
    E(cx - 30, 730, cx + 30, 790, fill=GOLD, outline=LINE, width=5)
    E(cx - 12, 744, cx + 18, 776, fill=CAPE)

    # 手（ポーズごと）
    def paw(x, y, r=46):
        E(x - r, y - r, x + r, y + r, fill=CREAM, outline=LINE, width=LW)

    front = []
    if pose == "hello":
        front.append("hello")
        paw(cx - 150, 930)
    elif False:
        L([(cx + 150, 860), (cx + 260, 720)], fill=CAPE, width=60)
        paw(cx + 270, 700)
        for k in range(3):
            a = math.radians(-60 + k * 30)
            L([(cx + 270 + 80 * math.cos(a), 700 + 80 * math.sin(a)), (cx + 270 + 115 * math.cos(a), 700 + 115 * math.sin(a))],
              fill=GOLD, width=8)
        paw(cx - 150, 930)
    elif pose == "point":
        L([(cx + 140, 880), (cx + 250, 800)], fill=CAPE, width=60)
        L([(cx + 250, 800), (cx + 420, 620)], fill=(120, 80, 50, 255), width=16)
        paw(cx + 260, 795)
        d.polygon(P(*star(cx + 440, 600, 62, 15)), fill=(255, 214, 90, 255), outline=LINE, width=6 * S)
        for (x, y, r) in ((cx + 520, 540, 16), (cx + 380, 520, 12), (cx + 520, 680, 10)):
            d.polygon(P(*star(x, y, r)), fill=(255, 236, 160, 255))
        paw(cx - 150, 930)
    elif pose == "book":
        d.polygon(P((cx - 190, 860), (cx, 890), (cx + 190, 860), (cx + 190, 1000), (cx, 1030), (cx - 190, 1000)),
                  fill=(150, 96, 58, 255), outline=LINE, width=LW * S)
        d.polygon(P((cx - 170, 870), (cx, 900), (cx + 170, 870), (cx + 170, 985), (cx, 1012), (cx - 170, 985)),
                  fill=(252, 244, 222, 255))
        L([(cx, 900), (cx, 1012)], fill=LINE, width=5)
        for k in range(3):
            L([(cx - 140, 905 + k * 28), (cx - 30, 925 + k * 28)], fill=(200, 180, 150, 255), width=4)
            L([(cx + 30, 925 + k * 28), (cx + 140, 905 + k * 28)], fill=(200, 180, 150, 255), width=4)
        paw(cx - 200, 950)
        paw(cx + 200, 950)
    elif pose == "think":
        front.append("think")
        paw(cx - 150, 930)
    else:
        paw(cx - 150, 930)
        paw(cx + 150, 930)

    # 垂れ耳
    for side in (-1, 1):
        ear = Image.new("RGBA", (300 * S, 160 * S), (0, 0, 0, 0))
        ed = ImageDraw.Draw(ear)
        ed.ellipse((10 * S, 10 * S, 290 * S, 150 * S), fill=CREAM, outline=LINE, width=LW * S)
        ed.ellipse((60 * S, 45 * S, 250 * S, 115 * S), fill=(248, 200, 196, 255))
        ear = ear.rotate(-28 * side, expand=True, resample=Image.BICUBIC)
        x = cx + side * 250 - ear.width / S / 2
        im.alpha_composite(ear, (int(x * S), int(520 * S)))
    # 顔（ふわふわの輪郭）
    for k in range(18):
        a = 2 * math.pi * k / 18
        x, y = cx + 235 * math.cos(a), 600 + 175 * math.sin(a)
        E(x - 44, y - 44, x + 44, y + 44, fill=LINE)
    for k in range(18):
        a = 2 * math.pi * k / 18
        x, y = cx + 235 * math.cos(a), 600 + 175 * math.sin(a)
        E(x - 38, y - 38, x + 38, y + 38, fill=CREAM)
    E(cx - 240, 430, cx + 240, 770, fill=CREAM)
    # 前髪のふわふわ
    for k, x in enumerate(range(cx - 160, cx + 170, 64)):
        E(x - 46, 455 - (k % 2) * 8, x + 46, 545 - (k % 2) * 8, fill=CREAM2)
    # 角（顔の横で、外へ向かって下に巻く）
    for side in (-1, 1):
        pts = []
        for i in range(80):
            t = i / 79
            a0 = math.radians(-70) if side < 0 else math.radians(-110)
            a = a0 - t * math.radians(300) if side < 0 else a0 + t * math.radians(300)
            r = 88 - 58 * t
            pts.append((cx + side * 268 + r * math.cos(a), 520 + r * math.sin(a)))
        for i, (x, y) in enumerate(pts):
            w = 66 - i * 0.55
            E(x - w / 2 - 6, y - w / 2 - 6, x + w / 2 + 6, y + w / 2 + 6, fill=LINE)
        for i, (x, y) in enumerate(pts):
            w = 66 - i * 0.55
            E(x - w / 2, y - w / 2, x + w / 2, y + w / 2, fill=HORN)
        for i in range(3, 72, 7):
            x, y = pts[i]
            w = (66 - i * 0.55) / 2.3
            (xn, yn) = pts[min(79, i + 1)]
            ang = math.atan2(yn - y, xn - x) + math.pi / 2
            L([(x - w * math.cos(ang), y - w * math.sin(ang)), (x + w * math.cos(ang), y + w * math.sin(ang))], fill=HORN2, width=5)
    # 表情
    ex = (cx - 95, cx + 95)
    ey = 625
    face = {"hello": "smile", "point": "open", "surprise": "surprise", "book": "open", "heart": "smile", "think": "up"}[pose]
    for i, x in enumerate(ex):
        if face == "smile" or (face == "open" and False):
            L([(x - 30, ey + 6), (x, ey - 18), (x + 30, ey + 6)], fill=EYE, width=9, joint="curve")
        elif face == "surprise":
            E(x - 24, ey - 30, x + 24, ey + 30, fill=EYE)
            E(x - 10, ey - 20, x + 4, ey - 6, fill=(255, 255, 255, 255))
        else:
            dy = -12 if face == "up" else 0
            E(x - 26, ey - 34 + dy, x + 26, ey + 30 + dy, fill=EYE)
            E(x - 12, ey - 24 + dy, x + 4, ey - 8 + dy, fill=(255, 255, 255, 255))
            E(x + 4, ey + 4 + dy, x + 12, ey + 12 + dy, fill=(255, 255, 255, 200))
    for x in (cx - 170, cx + 170):
        E(x - 40, ey + 40, x + 40, ey + 72, fill=PINK)
    if face == "surprise":
        E(cx - 18, ey + 56, cx + 18, ey + 96, fill=(150, 70, 70, 255), outline=LINE, width=4)
    else:
        L([(cx - 26, ey + 62), (cx - 13, ey + 74), (cx, ey + 62), (cx + 13, ey + 74), (cx + 26, ey + 62)], fill=LINE, width=6)
    # 帽子
    d.polygon(P((cx - 190, 420), (cx - 110, 250), (cx - 30, 130), (cx + 60, 60), (cx + 160, 50), (cx + 120, 90),
                (cx + 70, 170), (cx + 60, 280), (cx + 130, 420)), fill=HAT, outline=LINE, width=LW * S)
    d.polygon(P((cx - 168, 375), (cx + 112, 375), (cx + 126, 418), (cx - 188, 418)), fill=GOLD, outline=LINE, width=5 * S)
    E(cx - 285, 385, cx + 285, 475, fill=HAT, outline=LINE, width=LW)
    E(cx - 258, 398, cx + 258, 455, fill=HAT2)
    # 帽子の星と三日月の飾り
    d.polygon(P(*star(cx + 20, 300, 24)), fill=GOLD)
    L([(cx + 215, 455), (cx + 222, 505)], fill=GOLD, width=4)
    E(cx + 196, 500, cx + 250, 554, fill=GOLD, outline=LINE, width=4)
    E(cx + 212, 496, cx + 258, 542, fill=CREAM)
    # 帽子のまわりのアクセント
    if pose == "surprise":
        d.polygon(P((cx + 330, 200), (cx + 370, 200), (cx + 360, 330), (cx + 340, 330)), fill=(232, 80, 80, 255), outline=LINE, width=5 * S)
        E(cx + 334, 345, cx + 366, 377, fill=(232, 80, 80, 255), outline=LINE, width=5)
    if pose == "heart":
        d.polygon(P(*heart(cx + 330, 300, 4.2)), fill=(246, 120, 150, 255), outline=LINE, width=5 * S)
        d.polygon(P(*heart(cx + 410, 200, 2.4)), fill=(250, 170, 190, 255))
    if pose == "think":
        for k, (x, y, r) in enumerate(((cx + 280, 330, 14), (cx + 320, 270, 20), (cx + 380, 190, 30))):
            E(x - r, y - r, x + r, y + r, fill=(255, 255, 255, 255), outline=LINE, width=4)
    if pose in ("hello", "point"):
        for (x, y, r) in ((cx - 330, 300, 18), (cx - 280, 200, 11)):
            d.polygon(P(*star(x, y, r)), fill=(255, 226, 140, 255))

    if "hello" in front:
        L([(cx + 170, 860), (cx + 300, 690)], fill=CAPE, width=64)
        L([(cx + 170, 860), (cx + 300, 690)], fill=CAPE, width=56)
        paw(cx + 310, 670)
        for k in range(3):
            a = math.radians(-70 + k * 30)
            L([(cx + 310 + 70 * math.cos(a), 670 + 70 * math.sin(a)), (cx + 310 + 105 * math.cos(a), 670 + 105 * math.sin(a))],
              fill=GOLD, width=8)
    if "think" in front:
        L([(cx + 130, 920), (cx + 170, 780)], fill=CAPE, width=60)
        paw(cx + 175, 760)
    im = im.resize((W, H), Image.LANCZOS)
    im = im.crop(im.getbbox())
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im


POSES = ["hello", "point", "surprise", "book", "heart", "think"]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    tiles = []
    for p in POSES:
        g = draw(p)
        g.save(os.path.join(OUT, f"goat_{p}.png"))
        tiles.append(g)
    sheet = Image.new("RGBA", (6 * 360, 400), (246, 240, 232, 255))
    for i, g in enumerate(tiles):
        t = g.copy()
        t.thumbnail((340, 380))
        sheet.alpha_composite(t, (i * 360 + (360 - t.width) // 2, 10 + (380 - t.height)))
    sheet.convert("RGB").save(os.path.join(HERE, "goat_sheet.png"))
    print("ok")
