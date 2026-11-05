"""アイコンが話して鑑定書を紹介するサンプル動画を作る。

open_jtalk で文ごとに音声を作り、音量に合わせて口を動かす。
"""
import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ICON = os.path.join(HERE, "assets", "icon.png")  # おますさんのアイコン（非公開リポジトリにある）
VOICE = os.path.join(HERE, "htsvoice-tohoku-f01", "tohoku-f01-happy.htsvoice")
DIC = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

W, H, FPS = 1920, 1080, 30
SR = 48000
CREAM = (246, 242, 235)
TEAL = (110, 135, 132)
INK = (60, 58, 62)
LINE = (103, 100, 85)
FACE = (255, 255, 251)
GOLD = (176, 146, 92)

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size, index=0)


# (表示するページ, ページの見出し, [(字幕, 読み上げ用の文), ...])
# 読み上げ用の文は、合成音声が読み間違えやすい語をかなにしている。
SCENES = [
    (1, "表紙", [
        ("こんにちは。星よみ専門家の、おますです。",
         "こんにちは。ほしよみ専門家の、おますです。"),
        ("今日は、2027年の運勢鑑定をご紹介します。",
         "今日は、にせんにじゅうななねんの、運勢鑑定をご紹介します。"),
        ("生年月日と、生まれた時間、生まれた場所から、あなたの2027年を読み解きます。",
         "生年月日と、生まれた時間、生まれた場所から、あなたの、にせんにじゅうななねんを読み解きます。"),
        ("それを、一冊の鑑定書にしてお届けします。",
         "それを、一冊の鑑定書にして、お届けします。"),
    ]),
    (2, "一年のテーマと流れ", [
        ("はじめのページでは、一年のテーマと、だいたいの流れをお伝えします。",
         "はじめのページでは、一年のテーマと、だいたいの流れをお伝えします。"),
        ("何月ごろは休んで、何月ごろから動くとよさそうか。",
         "何月ごろは休んで、何月ごろから動くとよさそうか。"),
        ("先に分かると、予定が立てやすくなります。",
         "先に分かると、予定が立てやすくなります。"),
    ]),
    (3, "星を、ふだんの言葉で", [
        ("占星術を知らなくても大丈夫です。",
         "占星術を知らなくても、大丈夫です。"),
        ("星のことは、「毎日の仕事」や「休む時間」のように、ふだんの言葉で書いています。",
         "星のことは、毎日の仕事や、休む時間のように、ふだんの言葉で書いています。"),
    ]),
    (5, "サビアンの場面", [
        ("サビアンという、星の位置を短い場面で表したものも使います。",
         "サビアンという、星の位置を、短い場面で表したものも使います。"),
        ("迷ったときの考え方のヒントとして、暮らしでの使い方までお伝えします。",
         "迷ったときの考え方のヒントとして、暮らしでの使い方まで、お伝えします。"),
    ]),
    (6, "仕事とお金", [
        ("仕事とお金のページは、続けるか変えるかで迷ったときのためのページです。",
         "仕事とお金のページは、続けるか、変えるかで迷ったときのための、ページです。"),
        ("何から考えるとよいかを、具体的にまとめました。",
         "何から考えるとよいかを、具体的にまとめました。"),
    ]),
    (8, "恋愛・パートナーシップ", [
        ("恋愛とパートナーシップは、二つに分けて書いています。",
         "恋愛とパートナーシップは、二つに分けて書いています。"),
        ("パートナーがいる方と、これから出会いを考える方です。",
         "パートナーがいる方と、これから出会いを考える方です。"),
        ("気持ちを伝えるときの、言い方の例も入れました。",
         "気持ちを伝えるときの、言い方の例も、入れました。"),
    ]),
    (9, "家族と、自分の気持ち", [
        ("家族のことや、自分の気持ちとの付き合い方も、時期ごとにお伝えします。",
         "家族のことや、自分の気持ちとの付き合い方も、時期ごとに、お伝えします。"),
    ]),
    (14, "カードからのメッセージ", [
        ("最後は、オラクルカードからのメッセージで、一年を締めくくります。",
         "最後は、オラクルカードからのメッセージで、一年を締めくくります。"),
    ]),
    ("price", "お申し込み", [
        ("お申し込みは、概要欄のリンクからどうぞ。",
         "お申し込みは、概要欄のリンクから、どうぞ。"),
        ("迷ったときに開ける一冊として、そばに置いていただけたらうれしいです。",
         "迷ったときに開ける一冊として、そばに置いていただけたら、うれしいです。"),
    ]),
]

GAP_SENT = 0.35   # 文と文のあいだ
GAP_SCENE = 0.6   # 場面の切り替え
LEAD = 0.6        # 冒頭
TAIL = 1.8        # 最後


def synth(text, path):
    subprocess.run(
        ["open_jtalk", "-x", DIC, "-m", VOICE, "-r", "1.05", "-fm", "1",
         "-jf", "1.3", "-ow", path],
        input=text.encode("utf-8"), check=True)
    with wave.open(path) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    x = x.astype(np.float32) / 32768
    # 48kHz にそろえる（線形補間）
    t = np.arange(int(len(x) * SR / sr)) * sr / SR
    return np.interp(t, np.arange(len(x)), x).astype(np.float32)


def build_audio():
    """音声をつなぎ、字幕と場面の時刻表を返す。"""
    chunks = [np.zeros(int(LEAD * SR), np.float32)]
    t = LEAD
    subs, scenes = [], []
    n = 0
    for si, (page, label, lines) in enumerate(SCENES):
        start = t
        for li, (sub, say) in enumerate(lines):
            a = synth(say, os.path.join(OUT, f"line{n:02d}.wav"))
            n += 1
            subs.append((t, t + len(a) / SR, sub))
            chunks.append(a)
            t += len(a) / SR
            gap = GAP_SENT if li < len(lines) - 1 else (
                GAP_SCENE if si < len(SCENES) - 1 else TAIL)
            chunks.append(np.zeros(int(gap * SR), np.float32))
            t += gap
        scenes.append((start, t, page, label))
    audio = np.concatenate(chunks)
    audio = audio / max(1e-6, np.abs(audio).max()) * 0.85
    with wave.open(os.path.join(OUT, "voice.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())
    return audio, subs, scenes


def mouth_levels(audio, nframes):
    hop = SR // FPS
    lv = np.zeros(nframes)
    for i in range(nframes):
        seg = audio[i * hop:(i + 1) * hop]
        lv[i] = np.sqrt(np.mean(seg ** 2)) if len(seg) else 0
    lv = lv / max(1e-6, np.percentile(lv[lv > 0], 95))
    lv = np.clip(lv, 0, 1)
    # 少しなめらかにして、ぱくぱくが細かくなりすぎないようにする
    out = lv.copy()
    for i in range(1, nframes):
        out[i] = max(lv[i], out[i - 1] * 0.55)
    return out


# ---- アイコン ----
BASE_ICON = Image.open(ICON).convert("RGB")
EYES = [(442, 503), (589, 503)]
MOUTH = (505, 585)


def icon_frame(level, blink):
    im = BASE_ICON.copy()
    d = ImageDraw.Draw(im)
    if blink:
        for cx, cy in EYES:
            d.ellipse((cx - 26, cy - 21, cx + 26, cy + 23), fill=FACE)
            d.arc((cx - 22, cy - 14, cx + 22, cy + 14), 20, 160, fill=LINE, width=9)
    # 元の口（点）を消して、開き具合に合わせて描き直す
    mx, my = MOUTH
    d.ellipse((mx - 14, my - 10, mx + 14, my + 10), fill=FACE)
    if level < 0.12:
        d.ellipse((mx - 8, my - 5, mx + 8, my + 5), fill=LINE)
    else:
        h = 9 + level * 36
        w = 12 + level * 9
        d.ellipse((mx - w, my - h / 2, mx + w, my + h / 2), fill=(70, 62, 66),
                  outline=LINE, width=4)
    return im


ICON_SIZE = 520


def icon_card(level, blink):
    im = icon_frame(level, blink).resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, ICON_SIZE - 1, ICON_SIZE - 1), 48, fill=255)
    return im, mask


# ---- ページ ----
PDF_PAGE_H = 940


def load_page(page):
    im = Image.open(os.path.join(HERE, f"page-{page:02d}.png")).convert("RGB")
    w = int(im.width * PDF_PAGE_H / im.height)
    return im.resize((w, PDF_PAGE_H), Image.LANCZOS)


def price_card():
    w, h = int(PDF_PAGE_H * 0.707), PDF_PAGE_H
    im = Image.new("RGB", (w, h), (24, 34, 54))
    cover = load_page(1)
    im.paste(cover.crop((0, 0, w, int(h * 0.62))).filter(ImageFilter.GaussianBlur(1)), (0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, int(h * 0.55), w, h), fill=CREAM)
    cx = w // 2
    y = int(h * 0.60)
    for text, f, col in [
        ("2027年 運勢鑑定", font(46, True), INK),
        ("PDFでお届けします", font(30), LINE),
        ("お申し込みは概要欄のリンクから", font(28), INK),
    ]:
        tw = d.textlength(text, font=f)
        d.text((cx - tw / 2, y), text, font=f, fill=col)
        y += f.size + 34
    return im


def wrap(text, f, maxw, d):
    """行の長さをそろえ、できるだけ読点や句点のあとで改行する。"""
    total = d.textlength(text, font=f)
    if total <= maxw:
        return [text]
    n = int(np.ceil(total / maxw))
    lines, rest = [], text
    for k in range(n - 1, 0, -1):
        target = d.textlength(rest, font=f) / (k + 1)
        best, best_score = None, None
        for i in range(1, len(rest)):
            wl = d.textlength(rest[:i], font=f)
            if wl > maxw:
                break
            if rest[i] in "、。」）ぁぃぅぇぉっゃゅょー":
                continue  # 行頭に来てほしくない文字
            score = abs(wl - target)
            if rest[i - 1] in "、。":
                score -= target * 0.5
            elif rest[i - 1] == "」":
                score -= target * 0.15
            if best_score is None or score < best_score:
                best, best_score = i, score
        lines.append(rest[:best])
        rest = rest[best:]
    lines.append(rest)
    return lines


PAGE_X = 110
RIGHT_X0, RIGHT_X1 = 900, 1830
RIGHT_CX = (RIGHT_X0 + RIGHT_X1) // 2


def scene_background(page, label):
    bg = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(bg)
    # 薄い星
    rng = np.random.default_rng(7)
    for _ in range(60):
        x, y = rng.integers(0, W), rng.integers(0, H)
        r = rng.integers(1, 3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(226, 218, 202))
    pg = price_card() if page == "price" else load_page(page)
    py = (H - PDF_PAGE_H) // 2 + 10
    shadow = Image.new("L", (pg.width + 40, pg.height + 40), 0)
    ImageDraw.Draw(shadow).rectangle((20, 20, pg.width + 20, pg.height + 20), fill=70)
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    bg.paste((200, 190, 175), (PAGE_X - 14, py - 8), shadow)
    bg.paste(pg, (PAGE_X, py))
    # ページの見出しタグ
    f = font(26, True)
    tw = d.textlength(label, font=f)
    d.rounded_rectangle((PAGE_X, py - 0 - 2, PAGE_X + tw + 36, py + 44), 10, fill=TEAL)
    d.text((PAGE_X + 18, py + 4), label, font=f, fill=(255, 255, 255))
    # 右上のタイトル
    f2 = font(26)
    t2 = "2027年運勢鑑定のご紹介"
    d.text((RIGHT_X1 - d.textlength(t2, font=f2), 34), t2, font=f2, fill=LINE)
    return bg


def subtitle_layer(text):
    layer = Image.new("RGBA", (RIGHT_X1 - RIGHT_X0, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(44, True)
    lines = wrap(text, f, layer.width - 80, d)
    d.rounded_rectangle((0, 0, layer.width - 1, layer.height - 1), 28, fill=(255, 255, 255, 235),
                        outline=(220, 210, 192, 255), width=2)
    # 吹き出しのしっぽはアイコン側（上）に
    lh = 66
    y = (layer.height - lh * len(lines)) // 2
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text(((layer.width - tw) / 2, y), ln, font=f, fill=INK)
        y += lh
    return layer


def main():
    audio, subs, scenes = build_audio()
    dur = len(audio) / SR
    nframes = int(dur * FPS)
    levels = mouth_levels(audio, nframes)
    rng = np.random.default_rng(3)
    blink_frames = set()
    t = 1.5
    while t < dur:
        f0 = int(t * FPS)
        blink_frames.update(range(f0, f0 + 4))
        t += rng.uniform(2.5, 4.5)

    backgrounds = {i: scene_background(p, l) for i, (_, _, p, l) in enumerate(scenes)}
    sub_layers = {i: subtitle_layer(s[2]) for i, s in enumerate(subs)}
    card_cache = {}

    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", os.path.join(OUT, "voice.wav"),
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-shortest",
         os.path.join(HERE, "2027年運勢鑑定_紹介動画_サンプル.mp4")],
        stdin=subprocess.PIPE)

    fade = 0.35
    for fi in range(nframes):
        t = fi / FPS
        si = next(i for i, s in enumerate(scenes) if t < s[1] or i == len(scenes) - 1)
        frame = backgrounds[si]
        if si > 0 and t - scenes[si][0] < fade:
            a = (t - scenes[si][0]) / fade
            frame = Image.blend(backgrounds[si - 1], backgrounds[si], a)
        else:
            frame = frame.copy()

        lv = round(levels[fi] * 5) / 5
        bl = fi in blink_frames
        key = (lv, bl)
        if key not in card_cache:
            card_cache[key] = icon_card(lv, bl)
        card, mask = card_cache[key]
        bob = int(round(np.sin(t * 2.2) * 5 - levels[fi] * 6))
        frame.paste(card, (RIGHT_CX - ICON_SIZE // 2, 90 + bob), mask)
        d = ImageDraw.Draw(frame)
        name = "星よみ専門家　おます"
        fn = font(28)
        d.text((RIGHT_CX - d.textlength(name, font=fn) / 2, 90 + ICON_SIZE + 18), name,
               font=fn, fill=LINE)

        for i, (s0, s1, _) in enumerate(subs):
            if s0 - 0.05 <= t <= s1 + 0.25:
                frame.paste(sub_layers[i], (RIGHT_X0, 700), sub_layers[i])
                break

        if t > dur - TAIL + 0.3:
            fc = font(18)
            credit = "音声：HTS voice tohoku-f01（東北大学 伊藤・能勢研究室, CC BY 4.0）"
            d.text((RIGHT_X1 - d.textlength(credit, font=fc), H - 40), credit, font=fc,
                   fill=(150, 146, 136))

        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    ff.wait()
    print("duration", round(dur, 1), "frames", nframes)


if __name__ == "__main__":
    main()
