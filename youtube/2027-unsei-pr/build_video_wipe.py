"""鑑定書を主役にし、アイコンを右下の丸いワイプで話させる版。

音声・字幕・口の動きは build_video.py のものを使う。
"""
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from build_video import (CREAM, FPS, GOLD, H, HERE, INK, LINE, OUT, SR, TAIL, TEAL,
                         W, build_audio, font, icon_frame, mouth_levels, price_card, wrap)

PAGE_W = 1180          # スクロール表示するページの幅
FIT_H = 850           # 表紙・申し込み画面は全体を見せる
TOP_PAD = 40
WIPE_D = 300           # ワイプの直径
WIPE_X, WIPE_Y = W - WIPE_D - 50, H - WIPE_D - 46
SUB_X0, SUB_X1 = 290, 1530
SUB_Y = 906


def load_hi(page, width):
    im = Image.open(os.path.join(HERE, f"hi-{page:02d}.png")).convert("RGB")
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)


def page_shadow(w, h):
    sh = Image.new("L", (w + 60, h + 60), 0)
    ImageDraw.Draw(sh).rectangle((30, 30, w + 30, h + 30), fill=80)
    return sh.filter(ImageFilter.GaussianBlur(16))


def star_bg():
    bg = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(bg)
    rng = np.random.default_rng(7)
    for _ in range(70):
        x, y = rng.integers(0, W), rng.integers(0, H)
        r = rng.integers(1, 3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(226, 218, 202))
    return bg


BG = star_bg()


class Scene:
    """1場面ぶんの鑑定書。長いページは上から下へゆっくり送る。"""

    def __init__(self, page, label, t0, t1):
        self.label, self.t0, self.t1 = label, t0, t1
        if page in (1, "price"):
            pg = price_card() if page == "price" else load_hi(1, int(FIT_H * 0.707))
            pg = pg.resize((int(FIT_H * pg.width / pg.height), FIT_H), Image.LANCZOS)
            self.page, self.scroll = pg, 0
        else:
            self.page = load_hi(page, PAGE_W)
            # 下端の余白（フッター）までは送らない
            visible = H - TOP_PAD
            full = self.page.height - visible - 60
            self.scroll = min(full, (t1 - t0) * 70)
        self.x = (W - self.page.width) // 2 - 60
        self.shadow = page_shadow(self.page.width, self.page.height)

    def render(self, t):
        frame = BG.copy()
        p = np.clip((t - self.t0 - 0.8) / max(0.1, self.t1 - self.t0 - 1.6), 0, 1)
        ease = p * p * (3 - 2 * p)
        y = 44 if self.scroll == 0 and self.page.height <= H \
            else TOP_PAD - int(self.scroll * ease)
        frame.paste((205, 195, 180), (self.x - 24, y - 18), self.shadow)
        frame.paste(self.page, (self.x, y))
        d = ImageDraw.Draw(frame)
        f = font(28, True)
        tw = d.textlength(self.label, font=f)
        d.rounded_rectangle((36, 30, 36 + tw + 40, 82), 12, fill=TEAL)
        d.text((56, 36), self.label, font=f, fill=(255, 255, 255))
        return frame


# ---- ワイプ ----
FACE_BOX = (112, 40, 992, 920)   # 元アイコンから顔のまわりを切り出す範囲


def wipe_image(level, blink):
    src = icon_frame(level, blink)
    ImageDraw.Draw(src).rectangle((0, 830, 1080, 1080), fill=TEAL)  # 署名はワイプでは隠す
    im = src.crop(FACE_BOX).resize((WIPE_D, WIPE_D), Image.LANCZOS)
    size = WIPE_D + 20
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.ellipse((0, 0, size - 1, size - 1), fill=(255, 255, 255, 255))
    d.ellipse((4, 4, size - 5, size - 5), outline=GOLD + (255,), width=3)
    mask = Image.new("L", (WIPE_D, WIPE_D), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, WIPE_D - 1, WIPE_D - 1), fill=255)
    out.paste(im, (10, 10), mask)
    return out


WIPE_SHADOW = Image.new("L", (WIPE_D + 80, WIPE_D + 80), 0)
ImageDraw.Draw(WIPE_SHADOW).ellipse((30, 34, WIPE_D + 50, WIPE_D + 54), fill=90)
WIPE_SHADOW = WIPE_SHADOW.filter(ImageFilter.GaussianBlur(12))


def name_tag():
    f = font(22, True)
    text = "おます"
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = int(tmp.textlength(text, font=f))
    im = Image.new("RGBA", (tw + 40, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, 39), 20, fill=TEAL + (255,))
    d.text((20, 4), text, font=f, fill=(255, 255, 255))
    return im


NAME = name_tag()


def subtitle_layer(text):
    w = SUB_X1 - SUB_X0
    f = font(42, True)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines = wrap(text, f, w - 90, tmp)
    lh = 62
    h = lh * len(lines) + 44
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # 濃いグレーの帯に白文字。下の鑑定書の文字が透けないよう不透明度を高めにする
    d.rounded_rectangle((0, 0, w - 1, h - 1), 24, fill=(52, 50, 54, 250))
    y = 20
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text(((w - tw) / 2, y), ln, font=f, fill=(255, 255, 255))
        y += lh
    return layer


def render(voice_path, audio, subs, scene_times, out_path, credit=None, tail=TAIL):
    """音声と、字幕・場面の時刻表から動画を書き出す。"""
    dur = len(audio) / SR
    nframes = int(dur * FPS)
    levels = mouth_levels(audio, nframes)
    rng = np.random.default_rng(3)
    blinks, t = set(), 1.5
    while t < dur:
        f0 = int(t * FPS)
        blinks.update(range(f0, f0 + 4))
        t += rng.uniform(2.5, 4.5)

    scenes = [Scene(p, l, t0, t1) for t0, t1, p, l in scene_times]
    sub_layers = [subtitle_layer(s[2]) for s in subs]
    wipe_cache = {}
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", voice_path,
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-shortest", out_path],
        stdin=subprocess.PIPE)

    fade = 0.4
    for fi in range(nframes):
        t = fi / FPS
        si = next(i for i, s in enumerate(scenes) if t < s.t1 or i == len(scenes) - 1)
        frame = scenes[si].render(t)
        if si > 0 and t - scenes[si].t0 < fade:
            prev = scenes[si - 1].render(t)
            frame = Image.blend(prev, frame, (t - scenes[si].t0) / fade)

        for i, (s0, s1, _) in enumerate(subs):
            if s0 - 0.05 <= t <= s1 + 0.25:
                layer = sub_layers[i]
                frame.paste(layer, (SUB_X0, SUB_Y + (150 - layer.height) // 2 + 10), layer)
                break

        key = (round(levels[fi] * 5) / 5, fi in blinks)
        if key not in wipe_cache:
            wipe_cache[key] = wipe_image(*key)
        wp = wipe_cache[key]
        bob = int(round(np.sin(t * 2.2) * 3 - levels[fi] * 4))
        frame.paste((120, 110, 95), (WIPE_X - 40, WIPE_Y - 30 + bob), WIPE_SHADOW)
        frame.paste(wp, (WIPE_X - 10, WIPE_Y - 10 + bob), wp)
        frame.paste(NAME, (WIPE_X + (WIPE_D - NAME.width) // 2, WIPE_Y + WIPE_D - 14 + bob), NAME)

        if credit and t > dur - tail + 0.3:
            d = ImageDraw.Draw(frame)
            d.text((40, H - 34), credit, font=font(18), fill=(150, 146, 136))

        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    ff.wait()
    print("duration", round(dur, 1), "->", out_path)


def main():
    audio, subs, scene_times = build_audio()
    render(os.path.join(OUT, "voice.wav"), audio, subs, scene_times,
           os.path.join(HERE, "2027年運勢鑑定_紹介動画_ワイプ版.mp4"),
           credit="音声：HTS voice tohoku-f01（東北大学 伊藤・能勢研究室, CC BY 4.0）")


if __name__ == "__main__":
    main()
