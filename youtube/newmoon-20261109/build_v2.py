"""11/9 蠍座の新月：ブラッシュアップ版（v2）。今の録音をそのまま使い、画面を作り直す。

場面は5種類：挿絵（水彩の空＋いらすとや＋大きな要点）、チャート（今の図の場面）、図解、章タイトル、冒頭。
山羊のキャラクターは astro/goat.png があれば出す（吹き出しつき）。
使い方: python3 build_v2.py 出力.mp4 [--until 秒]
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_draft as bd  # noqa: E402
import build_final as bf  # noqa: E402
import v2_parts as vp  # noqa: E402
import build_video_wipe as bw  # noqa: E402

W, H, FPS = 1920, 1080, 30
WORK = os.path.join(HERE, "final_work")
GOAT = os.path.join(HERE, "astro", "goat.png")
FADE = 0.5
PALETTE = {"01": "night", "02": "night", "03": "dawn", "04": "sunset", "05": "lavender", "06": "teal", "07": "gold"}


def S(unit, kind, **kw):
    return dict(unit=unit, kind=kind, **kw)


# (この番号のテロップが始まる所から, 場面の種類, 中身)
SCENES = [
    S(0, "illust", phrase="11月9日　蠍座の新月", st=[("scorpio", 440, (960, 600))], goat=("こんにちは！\n一緒に読んでいこう", "hello")),
    S(3, "illust", phrase="大切な人とは、\nもう一歩深く関わりたい", st=[("couple", 470, (960, 610))]),
    S(6, "illust", phrase="「ここまで言って\n大丈夫かな」", st=[("gaman", 440, (960, 620))]),
    S(8, "diagram", make=lambda c: vp.diagram_before_after(c["p"])),
    S(13, "diagram", make=lambda c: vp.diagram_three_points(c["reveal"](["一つ目は", "二つ目は", "三つ目は"])), goat=("見るのは\n三つだよ", "point")),
    S(19, "chart"),
    S(21, "illust", phrase="蠍座は、深く、\n長く関わるサイン", st=[("scorpio", 360, (700, 610)), ("couple", 360, (1240, 620))]),
    S(25, "diagram", make=lambda c: vp.diagram_new_moon(), extra=[("seed_girl", 240, (170, 745))]),
    S(27, "chart"),
    S(30, "diagram", make=lambda c: vp.diagram_houses(), goat=("ここ、大事だよ！", "surprise")),
    S(35, "illust", phrase="大切な人との関係を、\nもう一歩深める種まき", st=[("seed_girl", 400, (760, 620)), ("couple", 380, (1240, 630))]),
    S(38, "illust", phrase="11/14\n金星と水星が順行へ", st=[("venus", 300, (760, 620)), ("mercury", 260, (1180, 640))]),
    S(42, "chart"),
    S(44, "diagram", make=lambda c: vp.diagram_retrograde(c["p"]), goat=("後ろに進んで\n見えるだけだよ", "think")),
    S(48, "illust", phrase="関係のことも、言葉のことも、\n少しずつ前へ", st=[("talk", 440, (960, 620))]),
    S(51, "chart"),
    S(54, "illust", phrase="止まっていた車が、\nゆっくり動き出す", st=[("drive", 420, (960, 620))], goat=("一つずつ\n試していこう", "broom")),
    S(59, "chart"),
    S(62, "diagram", make=lambda c: vp.diagram_aspects(), goat=("前回は90度\nだったね", "surprise")),
    S(68, "illust", phrase="「一緒にこうしてみない？」", st=[("talk", 460, (960, 610))]),
    S(73, "chart"),
    S(76, "illust", phrase="自分らしく動くことに、\n後押しがある", st=[("leo", 380, (760, 620)), ("jupiter", 280, (1200, 620))]),
    S(79, "illust", phrase="サビアン＝\n度数ごとのイメージ", st=[("scorpio", 300, (700, 620)), ("libra", 300, (1220, 620))]),
    S(81, "chart"),
    S(83, "diagram", make=lambda c: vp.sabian_card("蠍座17度", "自分の子どもの\n父親である女性", "sprout", "待つより、自分の中で育てたものを、自分で形に"), goat=("サビアンを\n読んでみよう", "readbook")),
    S(87, "illust", phrase="待つより、\n自分で形にしていく", st=[("waiting", 420, (960, 620))]),
    S(89, "illust", phrase="自分の言葉で伝えて、\n自分で動く", st=[("seed_girl", 420, (960, 620))]),
    S(91, "chart"),
    S(93, "diagram", make=lambda c: vp.sabian_card("天秤座24度", "蝶の左側にある、\n3枚目の羽", "butterfly", "ほかの人と同じ形じゃなくていい")),
    S(98, "illust", phrase="二人の間だけの、\nちょうどいい形", st=[("couple", 440, (960, 620))]),
    S(102, "diagram", make=lambda c: vp.calendar_diagram(c["reveal"](["新月は、11月9日", "翌日の10日", "14日に", "16日に", "22日には", "24日の夜"])), goat=("カレンダーで\n確かめよう", "lantern")),
    S(108, "diagram", make=lambda c: vp.question_card(1, "この関係を、\nもう一歩深めるとしたら？", "imagine", "蠍座の新月の問い"), goat=("思い浮かべて\nみてね", "sparkle")),
    S(112, "diagram", make=lambda c: vp.question_card(2, "見直して、\n分かったことは何？", "calendar", "順行に戻る金星と水星の問い")),
    S(115, "diagram", make=lambda c: vp.question_card(3, "自分から、\nどんな提案ができる？", "talk", "金星と火星の60度・蠍座17度の問い")),
    S(118, "chart"),
    S(121, "illust", phrase="見直してきた関係を、\n自分らしい形で育てる", st=[("sprout", 360, (760, 620)), ("couple", 400, (1240, 630))], goat=("自分らしく\nいこうね", "heart")),
    S(123, "illust", phrase="コメント欄で\n教えてくださいね", st=[("smartphone", 440, (960, 620))], goat=("またね！", "hello")),
]

TITLE_GOAT = {"02": "次は、新月の時刻と\n蠍座のお話だよ", "03": "いちばん大事な\n流れのお話だよ", "04": "金星と火星の\n角度を見てみよう",
              "05": "サビアンの\nイメージを見るよ", "06": "2週間の使い方を\nまとめるよ", "07": "最後に\nおさらいしよう"}
TITLE_POSE = {"02": "magic", "03": "point", "04": "broom", "05": "book", "06": "lantern", "07": "smile"}
TITLE_ICON = {"02": "scorpio", "03": "venus", "04": "mars", "05": "butterfly", "06": "calendar", "07": "sprout"}


def load():
    tl = json.load(open(os.path.join(WORK, "timeline.json")))
    units, total = tl["units"], tl["total"]
    script = bd.parse_script()
    chapters, _, _ = bd.schedule(script)
    for c, f in zip(chapters, tl["chapters"]):
        c["start"], c["end"] = f["start"], f["end"]
    bd.build_timeline(chapters, units)
    return chapters, units, total


def scene_times(chapters, units, total):
    scenes = []
    for k, s in enumerate(SCENES):
        u = units[s["unit"]]
        ch = next(c for c in chapters if c["num"] == u["chapter"])
        t0 = max(u["start"] - 0.35, ch["start"] + (bd.TITLE_CARD if ch["num"] != "01" else 0))
        if k == 0:
            t0 = bd.OPENING
        scenes.append(dict(s, t0=t0, chapter=ch))
    for k, s in enumerate(scenes):
        s["t1"] = scenes[k + 1]["t0"] if k + 1 < len(scenes) else total
    return scenes


_goat_cache = {}


def goat_layer(text, pose="hello", height=330):
    """案内役の山羊（おますさんの山羊。goat_src/poses から選んだ astro/goat_<ポーズ>.png）と吹き出し。text は \n で改行。"""
    path = os.path.join(HERE, "astro", f"goat_{pose}.png")
    if not os.path.exists(path):
        return None
    key = (text, pose, height)
    if key in _goat_cache:
        return _goat_cache[key]
    g = Image.open(path).convert("RGBA")
    g = g.resize((int(g.width * height / g.height), height), Image.LANCZOS)
    f = vp.font(vp.SANS_B, 38)
    lines = text.split("\n")
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    bw_ = int(max(tmp.textlength(l, font=f) for l in lines)) + 64
    bh = 54 * len(lines) + 40
    w = max(g.width, bw_) + 20
    h = bh + 40 + g.height
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gx = (w - g.width) // 2
    sh = Image.new("RGBA", g.size, (20, 10, 40, 0))
    sh.putalpha(g.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 0.4))
    im.alpha_composite(sh, (gx + 6, h - g.height + 10))
    im.alpha_composite(g, (gx, h - g.height))
    d = ImageDraw.Draw(im)
    bx, by = (w - bw_) // 2, 4
    d.rounded_rectangle((bx, by, bx + bw_, by + bh), 28, fill=(255, 255, 255, 248), outline=(226, 186, 110, 255), width=4)
    tx = w // 2 + 30
    d.polygon([(tx - 26, by + bh - 4), (tx + 6, by + bh + 34), (tx + 20, by + bh - 4)], fill=(255, 255, 255, 248))
    d.line([(tx - 26, by + bh), (tx + 6, by + bh + 34), (tx + 20, by + bh)], fill=(226, 186, 110, 255), width=4)
    for i, l in enumerate(lines):
        d.text((bx + bw_ / 2, by + 20 + 54 * i + 27), l, font=f, fill=vp.INK, anchor="mm")
    _goat_cache[key] = im
    return im


class Renderer:
    def __init__(self, chapters, units, total):
        self.chapters, self.units, self.total = chapters, units, total
        self.scenes = scene_times(chapters, units, total)
        self.bg_cache, self.cache, self.vcache, self.title_cache = {}, {}, {}, {}

    def reveal_fn(self, ch, t):
        def f(keys):
            return sum(1 for k in keys if bd.trigger_time(self.units, ch["num"], k) <= t)
        return f

    def bg(self, name, seed):
        key = (name, seed)
        if key not in self.bg_cache:
            self.bg_cache[key] = vp.watercolor_bg(name, seed).convert("RGBA")
        return self.bg_cache[key]

    def scene_frame(self, k, t):
        s = self.scenes[k]
        ch = s["chapter"]
        if s["kind"] == "chart":
            return bd.state_frame(ch, t, self.cache, self.vcache).convert("RGBA")
        lt = t - s["t0"]
        frame = self.bg(PALETTE[ch["num"]], k).copy()
        if s["kind"] == "illust":
            for i, (name, hgt, (cx, cy)) in enumerate(s["st"]):
                st = vp.sticker(name, hgt)
                dy = int(8 * math.sin(t * 1.6 + i * 1.3))
                frame.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2 + dy)))
            key = ("phrase", k)
            if key not in self.cache:
                self.cache[key] = vp.phrase_layer(s["phrase"])
            ph = self.cache[key]
            a = min(1.0, lt / 0.6)
            if a < 1:
                ph = ph.copy()
                ph.putalpha(ph.split()[3].point(lambda v: int(v * a)))
            frame.alpha_composite(ph, ((W - ph.width) // 2, 70))
        else:
            p = min(1.0, max(0.0, lt / max(1.0, s["t1"] - s["t0"] - 1.0)))
            ctx = dict(p=p, reveal=self.reveal_fn(ch, t))
            key = ("diagram", k, json.dumps(ctx["reveal"]([]) if False else None), round(p, 2) if "p" in s["make"].__code__.co_names or True else 0)
            g = s["make"](ctx)
            if s.get("goat"):
                left = 400
                avail = W - left - 40
                if g.width > avail:
                    g = g.resize((avail, int(g.height * avail / g.width)), Image.LANCZOS)
                x, y = left + (avail - g.width) // 2, max(40, (870 - g.height) // 2)
            else:
                x, y = (W - g.width) // 2, max(40, (870 - g.height) // 2)
            frame.alpha_composite(g, (x, y))
            for name, hgt, (cx, cy) in s.get("extra", []):
                st = vp.sticker(name, hgt)
                frame.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2)))
        if s.get("goat") and lt < 7:
            gl = goat_layer(*s["goat"])
            if gl is not None:
                slide = min(1.0, lt / 0.5, (7 - lt) / 0.5)
                hop = int(abs(math.sin(lt * 3.0)) * 10) if lt < 2 else 0
                frame.alpha_composite(gl, (int(20 - (1 - slide) * 420), 885 - gl.height - hop))
        return frame

    def title_frame(self, ch):
        if ch["num"] not in self.title_cache:
            frame = self.bg(PALETTE[ch["num"]], 100 + int(ch["num"])).copy()
            d = ImageDraw.Draw(frame)
            d.text((W // 2, 400), f"第{int(ch['num'])}章", font=vp.font(vp.SERIF_B, 56), fill=vp.GOLD, anchor="mm")
            d.text((W // 2, 520), ch["title"], font=vp.font(vp.SERIF_B, 84), fill=(255, 255, 255), anchor="mm")
            d.line((W // 2 - 220, 610, W // 2 + 220, 610), fill=vp.GOLD, width=3)
            icon = TITLE_ICON.get(ch["num"])
            if icon:
                st = vp.sticker(icon, 200)
                frame.alpha_composite(st, (W - 420, 160))
            gl = goat_layer(TITLE_GOAT.get(ch["num"], ""), TITLE_POSE.get(ch["num"], "point"), 340)
            if gl is not None:
                frame.alpha_composite(gl, (60, 1000 - gl.height))
            self.title_cache[ch["num"]] = frame
        return self.title_cache[ch["num"]]

    def frame(self, t):
        if t < bd.OPENING:
            op = self.opening.convert("RGBA")
            if t > bd.OPENING - 0.5:
                return Image.blend(op, self.scene_frame(0, bd.OPENING), (t - (bd.OPENING - 0.5)) / 0.5), True
            return op, True
        ch = next((c for c in self.chapters if c["start"] <= t < c["end"]), self.chapters[-1])
        if ch["num"] != "01" and t < ch["start"] + bd.TITLE_CARD:
            tf = self.title_frame(ch)
            if t > ch["start"] + bd.TITLE_CARD - 0.4:
                k = next(i for i, s in enumerate(self.scenes) if s["chapter"] is ch)
                nxt = self.scene_frame(k, ch["start"] + bd.TITLE_CARD)
                return Image.blend(tf, nxt, (t - (ch["start"] + bd.TITLE_CARD - 0.4)) / 0.4), True
            return tf.copy(), True
        k = max(i for i, s in enumerate(self.scenes) if s["t0"] <= t)
        frame = self.scene_frame(k, t)
        s = self.scenes[k]
        if k > 0 and t - s["t0"] < FADE and self.scenes[k - 1]["chapter"] is s["chapter"]:
            prev = self.scene_frame(k - 1, t)
            frame = Image.blend(prev, frame, (t - s["t0"]) / FADE)
        return frame, False

    def render(self, out_path, audio_path, levels, until=None):
        total = min(self.total, until) if until else self.total
        nframes = int(total * FPS)
        self.opening = bd.opening_frame()
        rng = np.random.default_rng(3)
        blinks, t = set(), 1.5
        while t < total:
            blinks.update(range(int(t * FPS), int(t * FPS) + 4))
            t += rng.uniform(2.5, 4.5)
        visible = [u for u in self.units if not u.get("hidden")]
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-i", audio_path, "-t", f"{total:.2f}", "-c:a", "aac", "-b:a", "160k",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", out_path]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        wipe_cache, cur_ch = {}, None
        for fi in range(nframes):
            t = fi / FPS
            ch = next((c for c in self.chapters if c["start"] <= t < c["end"]), self.chapters[-1])
            if ch["num"] != cur_ch:
                self.vcache.clear()
                cur_ch = ch["num"]
            frame, is_title = self.frame(t)
            frame = frame.convert("RGB")
            u = next((u for u in visible if u["start"] - 0.05 <= t <= u["end"] + 0.25), None)
            if u and not is_title:
                layer = bd.telop_layer(u["text"])
                frame.paste(layer, (bd.TELOP_X0, bd.TELOP_CY - layer.height // 2), layer)
            if t >= bd.OPENING - 0.5:
                key = (round(float(levels[fi]) * 5) / 5, fi in blinks)
                if key not in wipe_cache:
                    wipe_cache[key] = bw.wipe_image(*key)
                wp = wipe_cache[key]
                bob = int(round(np.sin(t * 2.2) * 3 - float(levels[fi]) * 4))
                frame.paste((120, 110, 95), (bw.WIPE_X - 40, bw.WIPE_Y - 30 + bob), bw.WIPE_SHADOW)
                frame.paste(wp, (bw.WIPE_X - 10, bw.WIPE_Y - 10 + bob), wp)
                frame.paste(bw.NAME, (bw.WIPE_X + (bw.WIPE_D - bw.NAME.width) // 2, bw.WIPE_Y + bw.WIPE_D - 14 + bob), bw.NAME)
            ff.stdin.write(frame.tobytes())
        ff.stdin.close()
        ff.wait()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    until = float(sys.argv[sys.argv.index("--until") + 1]) if "--until" in sys.argv else None
    if until:
        args = [a for a in args if a != str(sys.argv[sys.argv.index("--until") + 1])]
    chapters, units, total = load()
    r = Renderer(chapters, units, total)
    voice = os.path.join(WORK, "voice.wav.final.wav")
    import wave
    with wave.open(voice) as w:
        audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    levels = bf.mouth(audio, int(total * FPS))
    if "--check" in sys.argv:
        for k, s in enumerate(r.scenes):
            f, _ = r.frame(min(s["t1"] - 0.5, s["t0"] + 3.0))
            f.convert("RGB").resize((960, 540)).save(os.path.join(HERE, f"v2chk_{k:02d}.png"))
        return
    r.render(args[0], voice, levels, until)


if __name__ == "__main__":
    main()
