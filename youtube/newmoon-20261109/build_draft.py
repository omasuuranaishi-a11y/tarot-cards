"""11/9 蠍座の新月：録音前の仮の動画（テロップは台本どおり・仮のタイミング・無音）。

左に新月の図、右に見出しと1行ずつ増える要点、下にテロップ、右下にアイコンのワイプ。
録音が届いたら、units.json の各テロップを声の時刻に合わせ直す（build_final.py）。
"""
import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2027-unsei-pr"))
import build_video_wipe as bw  # noqa: E402
import astro_view as av  # noqa: E402
import chart_draw  # noqa: E402

W, H, FPS = 1920, 1080, 30
SANS_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SERIF_B = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
BG = (250, 248, 244)
INK = (52, 48, 62)
NAVY = (34, 44, 82)
TEAL = (70, 112, 120)
GOLD = (190, 148, 70)
MUTED = (120, 114, 130)

SCRIPT = os.path.join(HERE, "録音台本_20261109蠍座新月.md")
CHARS_PER_SEC = 5.5
OPENING = 4.0
TITLE_CARD = 2.4
END_HOLD = 2.5

PANEL_X, PANEL_W = 960, 900
TELOP_X0, TELOP_X1, TELOP_CY = 40, 1530, 975


def font(path, size):
    return ImageFont.truetype(path, size, index=0)


# 章ごとの画面。panels は順に切り替わる（2つ目以降は at の文で切り替え）
# bullets は (表示する文, この言葉を含む文が始まったら出す)
CHAPTERS = {
    "01": dict(chart=dict(), panels=[dict(
        title="蠍座の新月", sub="2026年11月9日（月）16:02",
        bullets=[("前回の新月の「続き」", "その続きなんです"),
                 ("① 蠍座で重なる太陽と月", "一つ目は"),
                 ("② 11/14 金星と水星が順行へ", "二つ目は"),
                 ("③ 蠍座17度のサビアン", "三つ目は")])]),
    "02": dict(chart=dict(highlight=("sun", "moon"), house_fill=7), panels=[dict(
        title="蠍座16度53分の新月", sub="11月9日（月）16時2分",
        bullets=[("蠍座＝深く、長く関わることを大切にする", "蠍座は、水"),
                 ("新月は、種をまくとき", "種をまくとき"),
                 ("東京の図では第7ハウス（人との関係）", "第7ハウスにいます"),
                 ("大切な人との関係を、もう一歩深める", "もう一歩深めていく")])]),
    "03": dict(chart=dict(highlight=("venus", "mercury")), panels=[dict(
        title="11/14 金星と水星が順行へ", sub="見直してきたことが、少しずつ前へ",
        bullets=[("金星：10/3から逆行 → 11/14の朝に順行", "金星は、10月3日"),
                 ("水星：10/24から逆行 → 11/14の夜中に順行", "水星も"),
                 ("金星は、この図の主役（ASC 牡牛座の支配星）", "牡牛座の支配星も"),
                 ("14日のあとは、一つずつ試していく", "一つずつ試していく")])]),
    "04": dict(chart=dict(highlight=("venus", "mars", "jupiter"), lines=[("venus", "mars")]), panels=[dict(
        title="金星と火星の60度", sub="ずれは0度38分・11/10の午後にぴったり",
        bullets=[("前回は90度でぶつかっていた", "90度でぶつかっていた"),
                 ("今回は60度＝助け合いやすい角度", "助け合いやすい角度"),
                 ("「一緒にこうしてみない？」と提案する", "自分から提案してみる"),
                 ("火星と木星が獅子座で重なる（11/16）", "火星のすぐそばには")])]),
    "05": dict(chart=dict(highlight=("sun", "moon", "venus")), panels=[dict(
        title="サビアンシンボル", sub="太陽と月：蠍座17度　金星：天秤座24度",
        bullets=[("蠍座17度「自分の子どもの父親である女性」", "蠍座17度は"),
                 ("待つより、自分の中で育てたものを自分で形に", "誰かに与えてもらう"),
                 ("天秤座24度「蝶の左側にある、3枚目の羽」", "天秤座24度です"),
                 ("よくある形に合わせなくていい", "よくある形に合わせなくていい")])]),
    "06": dict(chart=dict(), panels=[
        dict(title="新月からの2週間", sub="11/9 〜 11/24",
             bullets=[("11/9　蠍座の新月", "新月は、11月9日"),
                      ("11/10　金星と火星の60度がぴったり", "翌日の10日"),
                      ("11/14　水星と金星が順行へ", "14日に、水星と金星"),
                      ("11/16　火星と木星が重なる", "16日に"),
                      ("11/22　太陽が射手座へ", "22日には"),
                      ("11/24　双子座の満月", "24日の夜")]),
        dict(at="三つの問いにしてみました", title="三つの問い", sub="新月からの2週間で",
             bullets=[("① この関係を、もう一歩深めるとしたら？", "一つ目は"),
                      ("② 見直して、分かったことは何？", "二つ目は"),
                      ("③ 自分から、どんな提案ができる？", "三つ目は")])]),
    "07": dict(chart=dict(), panels=[dict(
        title="まとめ", sub="11/9 蠍座の新月",
        bullets=[("見直してきた関係を", "見直してきた関係を"),
                 ("自分らしい形で育てていく", "見直してきた関係を"),
                 ("コメント欄で「一緒にやってみたいこと」を教えてください", "コメント欄で")])]),
}


# ---- 図の上の印（丸・矢印・拡大）----
VIEW_X, VIEW_Y, VIEW_S = 40, 20, 860
SM, VMe, MJ = "sun_moon", "venus_mercury", "mars_jupiter"
VM_LINE = ("venus", "mars", "60°（ずれ0°38′）", (-230, -40))


def F(circles=(), arrows=(), lines=(), house=None):
    return dict(circles=list(circles), arrows=list(arrows), lines=list(lines), house=house)


# (この言葉を含む文が始まったら, 拡大（中心, 倍率）または None で全体, 重ねる印)
FOCUS = {
    "01": [(None, None, F()),
           ("一つ目は", None, F(["sun", "moon"], [(SM, "太陽と月\n蠍座で重なる", (-300, -170))])),
           ("二つ目は", None, F(["venus", "mercury"], [(VMe, "金星と水星\n11/14 順行へ", (-330, 40))])),
           ("そして、金星と火星", None, F(["venus", "mars"], lines=[VM_LINE])),
           ("三つ目は", (SM, 1.8), F(["sun", "moon"], [(SM, "蠍座17度の\nサビアン", (-300, -160))])),
           ("最後に", None, F())],
    "02": [(None, None, F()),
           ("今回の新月は", (SM, 1.9), F(["sun", "moon"], [(SM, "太陽と月\n蠍座16°53′", (-320, -170))])),
           ("蠍座は、水のサイン", ((1210, 730), 1.7), F(["scorpio"], [("scorpio", "蠍座", (-260, -170))])),
           ("新月は、月の満ち欠け", (SM, 1.9), F(["sun", "moon"])),
           ("今日も、東京で作った図", None, F()),
           ("第7ハウスにいます", None, F(["sun", "moon"], [(SM, "第7ハウス\n人との関係", (-300, -260))], house=7)),
           ("ここは大事なので", None, F()),
           ("蠍座の新月が、第7ハウス", None, F(["sun", "moon"], house=7))],
    "03": [(None, None, F()),
           ("金星は、10月3日", ("venus", 1.9), F(["venus"], [("venus", "金星　天秤座23°19′\n逆行中 → 11/14 順行へ", (-330, 150))])),
           ("水星も", ("mercury", 1.9), F(["mercury"], [("mercury", "水星　蠍座6°51′\n逆行中 → 11/14 順行へ", (-420, 45))])),
           ("逆行というのは", (VMe, 1.4), F(["venus", "mercury"])),
           ("上昇点", ("asc_view", 1.6), F(["asc"], [("asc", "ASC（上昇点）\n牡牛座6°00′", (300, -200))])),
           ("牡牛座の支配星も", None, F(["asc", "venus"], [("asc", "ASC 牡牛座", (180, -150)),
                                                         ("venus", "支配星の金星", (-200, 150))])),
           ("順行に戻ってすぐは", None, F(["venus", "mercury"]))],
    "04": [(None, None, F(["venus", "mars"])),
           ("金星は天秤座の23度19分", None, F(["venus", "mars"], [("venus", "金星　天秤座23°19′", (-230, -200)),
                                                                ("mars", "火星　獅子座22°40′", (-320, -130))])),
           ("二つの差は", ("sextile_view", 1.5), F(["venus", "mars"], lines=[VM_LINE])),
           ("前回の新月を覚えて", None, F(["venus", "mars"], lines=[VM_LINE])),
           ("それが今回は、60度", ("sextile_view", 1.5), F(["venus", "mars"], lines=[VM_LINE])),
           ("前回は、たとえば頼まれごと", None, F(["venus", "mars"], lines=[VM_LINE])),
           ("火星のすぐそばには", (MJ, 2.0), F(["mars", "jupiter"], [(MJ, "火星と木星\n獅子座で重なる（11/16）", (-330, -260))]))],
    "05": [(None, None, F()),
           ("蠍座の16度53分", (SM, 1.9), F(["sun", "moon"], [(SM, "16°53′ → 蠍座17度", (-330, -160))])),
           ("主役の金星", ("venus", 1.9), F(["venus"], [("venus", "23°19′ → 天秤座24度", (-320, 140))])),
           ("関係の形も", None, F(["sun", "moon", "venus"]))],
    "06": [(None, None, F()),
           ("新月は、11月9日の夕方", None, F(["sun", "moon"])),
           ("翌日の10日", None, F(["venus", "mars"], lines=[VM_LINE])),
           ("14日に、水星と金星", None, F(["mercury", "venus"])),
           ("16日に", (MJ, 1.6), F(["mars", "jupiter"])),
           ("24日の夜", None, F()),
           ("一つ目は", None, F(["sun", "moon"], house=7)),
           ("二つ目は", None, F(["venus", "mercury"])),
           ("三つ目は", None, F(["venus", "mars"], lines=[VM_LINE]))],
    "07": [(None, None, F()),
           ("ここまでのお話は", None, F(["sun", "moon"])),
           ("第7ハウス", None, F(["sun", "moon"], house=7)),
           ("金星と水星", None, F(["venus", "mercury"])),
           ("金星と火星の60度", None, F(["venus", "mars"], lines=[VM_LINE])),
           ("見直してきた関係を", None, F())],
}
CAM_MOVE = 0.9


def parse_script():
    src = open(SCRIPT).read()
    chap = re.split(r"^## (\d\d)｜(.*)$", src, flags=re.M)
    out = []
    for i in range(1, len(chap), 3):
        num, title, body = chap[i], chap[i + 1].strip(), chap[i + 2]
        main = body.split("**画面に出す要点**")[0]
        paras = [p.strip() for p in main.strip().split("\n\n")
                 if p.strip() and not p.strip().startswith("【") and p.strip() != "---"]
        out.append((num, title, paras))
    return out


TELOP_FONT = font(SANS_B, 46)
_measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
TELOP_MAX = (TELOP_X1 - TELOP_X0) - 90


def telop_units(para):
    """段落を、テロップ1枚（2行まで）ずつに分ける。"""
    sents = [s for s in re.split(r"(?<=。)|(?<=？)(?!」)", para) if s and s.strip()]
    units = []
    for s in sents:
        stack = [s]
        while stack:
            t = stack.pop(0)
            lines = bw.wrap(t, TELOP_FONT, TELOP_MAX, _measure)
            if len(lines) <= 2 and all(_measure.textlength(l, font=TELOP_FONT) <= TELOP_MAX for l in lines):
                units.append(t)
                continue
            # 真ん中に近い読点で分ける
            cuts = [m.end() for m in re.finditer("、", t)]
            cut = min(cuts, key=lambda c: abs(c - len(t) / 2)) if cuts else len(t) // 2
            stack[:0] = [t[:cut], t[cut:]]
    return units


def schedule(script):
    t = OPENING
    chapters, units = [], []
    for num, title, paras in script:
        c0 = t
        t += TITLE_CARD
        for pi, para in enumerate(paras):
            for u in telop_units(para):
                n = len(re.sub(r"[、。「」（）？\s]", "", u))
                d = max(1.6, n / CHARS_PER_SEC)
                units.append(dict(chapter=num, para=pi, text=u, start=round(t, 2), end=round(t + d, 2)))
                t += d + 0.35
            t += 0.6
        chapters.append(dict(num=num, title=title, start=round(c0, 2), end=round(t, 2)))
    return chapters, units, t + END_HOLD


def trigger_time(units, chapter, key):
    for u in units:
        if u["chapter"] == chapter and key in u["text"]:
            return u["start"]
    raise ValueError(f"{chapter}: 「{key}」を含む文がありません")


def build_timeline(chapters, units):
    """章ごとに、画面の切り替え（パネル）と要点が出る時刻を決める。"""
    for c in chapters:
        cfg = CHAPTERS[c["num"]]
        panels = []
        for k, p in enumerate(cfg["panels"]):
            t0 = c["start"] if k == 0 else trigger_time(units, c["num"], p["at"])
            panels.append(dict(p, t0=t0,
                               reveal=[trigger_time(units, c["num"], key) for _, key in p["bullets"]]))
        c["panels"] = panels
        ev = []
        for trig, cam, foc in FOCUS[c["num"]]:
            t = c["start"] if trig is None else trigger_time(units, c["num"], trig)
            ev.append((t, av.cam_for(cam), foc))
        c["focus"] = sorted(ev, key=lambda e: e[0])  # 同じ時刻なら、リストで後のものが勝つ


# ---- 描画 ----
def star_bg():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(11)
    for _ in range(90):
        x, y, r = rng.integers(0, W), rng.integers(0, H), rng.integers(1, 3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(232, 226, 214))
    return im


BG_IMG = star_bg()
_chart_cache = {}


def chart_img(cfg):
    key = json.dumps(cfg, sort_keys=True)
    if key not in _chart_cache:
        _chart_cache[key] = chart_draw.draw(size=820, **cfg)
    return _chart_cache[key]


def gradient_box(w, h, c0, c1, radius=26):
    g = Image.new("RGB", (w, 1))
    for x in range(w):
        a = x / max(1, w - 1)
        g.putpixel((x, 0), tuple(int(c0[i] + (c1[i] - c0[i]) * a) for i in range(3)))
    g = g.resize((w, h))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
    return g, mask


def panel_layers(p):
    """パネルの見出しと、要点1つずつの画像（位置つき）を作る。"""
    box_h = 150
    g, m = gradient_box(PANEL_W, box_h, NAVY, TEAL)
    d = ImageDraw.Draw(g)
    ft, fs = font(SANS_B, 52), font(SANS, 30)
    d.text((PANEL_W // 2, 60), p["title"], font=ft, fill=(255, 255, 255), anchor="mm")
    d.text((PANEL_W // 2, 115), p["sub"], font=fs, fill=(226, 232, 238), anchor="mm")
    head = (g, m, (PANEL_X, 60))
    bullets = []
    y = 60 + box_h + 34
    many = len(p["bullets"]) > 4
    fb = font(SANS_B, 36 if many else 38)
    lh, gap = (50, 8) if many else (54, 22)
    for text, _ in p["bullets"]:
        lines = bw.wrap(text, fb, PANEL_W - 80, _measure)
        h = lh * len(lines) + 10
        im = Image.new("RGBA", (PANEL_W, h), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        dd.ellipse((14, 18, 32, 36), fill=GOLD)
        for k, ln in enumerate(lines):
            dd.text((52, 4 + lh * k), ln, font=fb, fill=INK)
        bullets.append((im, (PANEL_X, y)))
        y += h + gap
    if y > bw.WIPE_Y - 10:
        print("注意：要点が下まではみ出しています", p["title"])
    return head, bullets


_telop_cache = {}


def telop_layer(text):
    if text not in _telop_cache:
        lines = bw.wrap(text, TELOP_FONT, TELOP_MAX, _measure)
        w = TELOP_X1 - TELOP_X0
        lh = 66
        h = lh * len(lines) + 40
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=(52, 50, 54, 248))
        for k, ln in enumerate(lines):
            d.text((w / 2, 20 + lh * k + lh / 2), ln, font=TELOP_FONT, fill=(255, 255, 255), anchor="mm")
        _telop_cache[text] = im
    return _telop_cache[text]


def opening_frame():
    im = Image.new("RGB", (W, H), (18, 24, 48))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(5)
    for _ in range(400):
        x, y = rng.integers(0, W), rng.integers(0, H)
        r = rng.choice([1, 1, 1, 2, 3])
        b = int(rng.integers(120, 255))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(b, b, min(255, b + 20)))
    # 細い新月（黒い円に光の縁）
    cx, cy, R = 1500, 300, 120
    d.ellipse((cx - R - 6, cy - R - 6, cx + R + 6, cy + R + 6), fill=(80, 90, 130))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(18, 24, 48))
    d.text((W // 2, 360), "2026年11月9日（月）", font=font(SERIF_B, 56), fill=(226, 214, 180), anchor="mm")
    d.text((W // 2, 500), "蠍座の新月", font=font(SERIF_B, 150), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, 660), "見直してきた関係を、自分らしい形で育てる", font=font(SANS_B, 48),
           fill=(232, 236, 244), anchor="mm")
    d.text((W // 2, 760), "星よみ専門家 おます", font=font(SANS, 34), fill=(190, 196, 214), anchor="mm")
    return im


def title_card(base, num, title):
    im = base.filter(ImageFilter.GaussianBlur(8))
    im = Image.blend(im, Image.new("RGB", (W, H), (250, 248, 244)), 0.55)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 430), f"第{int(num)}章", font=font(SERIF_B, 48), fill=GOLD, anchor="mm")
    d.text((W // 2, 540), title, font=font(SERIF_B, 76), fill=NAVY, anchor="mm")
    d.line((W // 2 - 180, 620, W // 2 + 180, 620), fill=GOLD, width=3)
    return im


_view_mask = Image.new("L", (VIEW_S, VIEW_S), 0)
ImageDraw.Draw(_view_mask).rounded_rectangle((0, 0, VIEW_S - 1, VIEW_S - 1), 28, fill=255)


def paste_view(frame, img):
    frame.paste(img, (VIEW_X, VIEW_Y), _view_mask)
    ImageDraw.Draw(frame).rounded_rectangle((VIEW_X, VIEW_Y, VIEW_X + VIEW_S - 1, VIEW_Y + VIEW_S - 1), 28,
                                            outline=(222, 210, 180), width=3)


def viewport(ch, t, vcache):
    """その時刻の図（拡大・印つき）。拡大の切り替えは CAM_MOVE 秒でなめらかに動かす。"""
    ev = ch["focus"]
    i = max((k for k, e in enumerate(ev) if e[0] <= t), default=0)
    t0, cam, foc = ev[i]
    prev = ev[i - 1][1] if i > 0 else cam
    p = min(1.0, max(0.0, (t - t0) / CAM_MOVE))
    e = p * p * (3 - 2 * p)
    cur = tuple(prev[j] + (cam[j] - prev[j]) * e for j in range(3))
    pulse = int((t * 0.8 % 1) * 6) / 6
    if p >= 1:
        key = (ch["num"], i, pulse)
        if key not in vcache:
            vcache[key] = av.view(VIEW_S, cur, foc, pulse)
        return vcache[key]
    return av.view(VIEW_S, cur, foc, pulse)


def compose(chapter, panel_idx, n_bullets, show_title=False):
    frame = BG_IMG.copy()
    p = chapter["panels"][panel_idx]
    head, bullets = panel_layers(p)
    g, m, pos = head
    frame.paste(g, pos, m)
    for im, pos in bullets[:n_bullets]:
        frame.paste(im, pos, im)
    if show_title:
        paste_view(frame, av.view(VIEW_S, av.FULL, {}))
        frame = title_card(frame, chapter["num"], chapter["title"])
    return frame


def render(chapters, units, total, out_path, audio_path=None, levels=None, draft=True):
    """audio_path と levels（コマごとの口の開き 0〜1）を渡すと、本番の声で書き出す。"""
    nframes = int(total * FPS)
    cache, wipe_cache, vcache = {}, {}, {}
    cur_ch = None
    opening = opening_frame()
    rng = np.random.default_rng(3)
    blinks, t = set(), 1.5
    while t < total:
        blinks.update(range(int(t * FPS), int(t * FPS) + 4))
        t += rng.uniform(2.5, 4.5)
    if levels is None:
        # 仮の口の動き：テロップが出ている間だけ、話しているように動かす
        levels = np.zeros(nframes)
        for u in units:
            for f in range(int(u["start"] * FPS), min(nframes, int(u["end"] * FPS))):
                levels[f] = abs(np.sin(f * 0.9) * np.sin(f * 0.37)) * 0.9
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio_path:
        cmd += ["-i", audio_path, "-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", out_path]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    label_font = font(SANS_B, 24)
    for fi in range(nframes):
        t = fi / FPS
        if t < OPENING:
            frame = opening.copy()
            if t > OPENING - 0.5:
                nxt = state_frame(chapters[0], t, cache, vcache)
                frame = Image.blend(frame, nxt, (t - (OPENING - 0.5)) / 0.5)
        else:
            ch = next((c for c in chapters if c["start"] <= t < c["end"]), chapters[-1])
            if ch["num"] != cur_ch:
                vcache.clear()
                cur_ch = ch["num"]
            frame = state_frame(ch, t, cache, vcache)
        u = next((u for u in units if u["start"] - 0.05 <= t <= u["end"] + 0.25), None)
        if u and t >= OPENING:
            layer = telop_layer(u["text"])
            frame.paste(layer, (TELOP_X0, TELOP_CY - layer.height // 2), layer)
        if t >= OPENING - 0.5:
            key = (round(float(levels[fi]) * 5) / 5, fi in blinks)
            if key not in wipe_cache:
                wipe_cache[key] = bw.wipe_image(*key)
            wp = wipe_cache[key]
            bob = int(round(np.sin(t * 2.2) * 3 - float(levels[fi]) * 4))
            frame.paste((120, 110, 95), (bw.WIPE_X - 40, bw.WIPE_Y - 30 + bob), bw.WIPE_SHADOW)
            frame.paste(wp, (bw.WIPE_X - 10, bw.WIPE_Y - 10 + bob), wp)
            frame.paste(bw.NAME, (bw.WIPE_X + (bw.WIPE_D - bw.NAME.width) // 2,
                                  bw.WIPE_Y + bw.WIPE_D - 14 + bob), bw.NAME)
        if draft:
            ImageDraw.Draw(frame).text((W - 30, 24), "仮の動画（録音前・仮のタイミング）",
                                       font=label_font, fill=(200, 80, 80), anchor="ra")
        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    ff.wait()


def state_frame(ch, t, cache, vcache):
    if t < ch["start"] + TITLE_CARD and ch["num"] != "01":
        key = (ch["num"], "title")
        if key not in cache:
            cache[key] = compose(ch, 0, 0, show_title=True)
        base = cache[key]
        # 章タイトルから本編へ、最後の0.4秒で切り替える
        if t > ch["start"] + TITLE_CARD - 0.4:
            nxt = state_frame(ch, ch["start"] + TITLE_CARD + 0.01, cache, vcache)
            return Image.blend(base, nxt, (t - (ch["start"] + TITLE_CARD - 0.4)) / 0.4)
        return base.copy()
    pi = max(k for k, p in enumerate(ch["panels"]) if p["t0"] <= t + 1e-6) if ch["panels"][0]["t0"] <= t else 0
    p = ch["panels"][pi]
    n = sum(1 for r in p["reveal"] if r <= t)
    key = (ch["num"], pi, n)
    if key not in cache:
        cache[key] = compose(ch, pi, n)
    frame = cache[key]
    # 新しく出た要点は0.4秒でふわっと出す
    if n > 0 and t - p["reveal"][n - 1] < 0.4:
        prev_key = (ch["num"], pi, n - 1)
        if prev_key not in cache:
            cache[prev_key] = compose(ch, pi, n - 1)
        frame = Image.blend(cache[prev_key], frame, (t - p["reveal"][n - 1]) / 0.4)
    else:
        frame = frame.copy()
    paste_view(frame, viewport(ch, t, vcache))
    return frame


def main():
    script = parse_script()
    chapters, units, total = schedule(script)
    build_timeline(chapters, units)
    json.dump(dict(units=units, chapters=[{k: c[k] for k in ("num", "title", "start", "end")} for c in chapters]),
              open(os.path.join(HERE, "units_draft.json"), "w"), ensure_ascii=False, indent=1)
    print(f"テロップ {len(units)}枚・長さ {total / 60:.1f}分")
    if "--check" in sys.argv:
        vc = {}
        for c in chapters:
            for k, (t0, _, _) in enumerate(c["focus"]):
                state_frame(c, max(t0, c["start"] + TITLE_CARD) + 1.2, {}, vc).save(
                    os.path.join(HERE, f"check_{c['num']}_{k}.png"))
        return
    render(chapters, units, total, os.path.join(HERE, "11月9日蠍座新月_仮の動画.mp4"))


if __name__ == "__main__":
    main()
