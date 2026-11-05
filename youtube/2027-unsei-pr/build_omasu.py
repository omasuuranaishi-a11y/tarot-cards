"""おますさんの録音（2027年運勢鑑定のご紹介）に合わせて動画を作る。

章の区切りと要点テロップの時刻は、録音の文字起こし（rec/transcript.txt）から決めた。
使い方: python3 build_omasu.py 録音ファイル 出力ファイル
"""
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image

import build_video_wipe as bw
from build_video import SR

TAIL = 1.5

# (開始秒, 映すページ, 左上の見出し)
SCENES = [
    (0.0, 1, "はじめに"),
    (100.4, 2, "一年のテーマと流れ"),
    (160.3, 3, "誕生日から始まる一年（太陽回帰）"),
    (224.5, 4, "心の変化（プログレス）"),
    (271.0, 5, "サビアン"),
    (336.0, 6, "仕事"),
    (390.0, 7, "お金と働き方"),
    (442.2, 8, "恋愛・パートナーシップ"),
    (498.8, 9, "家族"),
    (515.6, 10, "自分の気持ち"),
    (545.2, 11, "注目したい三つの時期"),
    (556.6, 13, "今からできる準備"),
    (573.2, 14, "カードからのメッセージ"),
    (603.8, "price", "おわりに"),
]

# (表示を始める秒, 要点)。次の要点か次の章が始まる少し前まで出す
POINTS = [
    (0.8, "2027年運勢鑑定のご案内"),
    (32.6, "生年月日・生まれた時間・生まれた場所から読みます"),
    (39.9, "あなたの一年を、一冊の鑑定書に"),
    (57.8, "この鑑定書を作ったきっかけ"),
    (73.2, "一年の流れを早めに知ると、予定が組みやすい"),
    (85.0, "やりたかったことを、始める時期も決めておける"),
    (103.0, "一年のテーマと、だいたいの流れ"),
    (115.5, "1〜7月中旬は落ち着いて／7月下旬から試す"),
    (132.0, "9〜10月に見直し／11月下旬から動く"),
    (147.9, "先にわかると、予定が立てやすい"),
    (167.4, "太陽回帰＝誕生日から、次の誕生日までのテーマ"),
    (180.5, "星のことは、ふだんの言葉で"),
    (209.2, "「今日はここまでで十分」を先に決めておく"),
    (225.1, "プログレス＝年齢とともに変わる、気持ちや関心"),
    (235.3, "時期ごとに分けてお伝え"),
    (257.6, "気持ちの変化を知ると、自分を責めずにすむ"),
    (271.4, "サビアン＝星の位置を、短い場面で表したもの"),
    (281.3, "例：「顔をしかめる道化師」"),
    (305.3, "力が入りすぎたら、少し肩の力を抜いてみる"),
    (322.3, "ふだんの場面での使い方まで"),
    (336.3, "「仕事の内容」と「働き方」を分けて考える"),
    (351.2, "変える前に、相談できることもある"),
    (371.9, "疲れた日の気持ちだけで、大きな決断をしない"),
    (383.4, "動く時期の目安もお伝え"),
    (398.9, "収入を増やしたいとき、何から考える？"),
    (408.2, "「何円増えたら、どんな不安が減るか」から"),
    (423.4, "金額だけでなく、かかる時間もあわせて"),
    (443.0, "パートナーがいる方／これから出会いを考える方"),
    (463.7, "気持ちを伝えるときの、言い方の例つき"),
    (480.3, "出会いを広げやすい時期も"),
    (499.5, "家族との時間と、自分の時間"),
    (515.9, "自分の気持ちとの付き合い方"),
    (529.1, "「返事がない」と「嫌われた」は別のこと"),
    (545.6, "特に注目したい、三つの時期"),
    (556.9, "2026年のうちにできる準備"),
    (566.2, "届いたその日から使える"),
    (573.7, "オラクルカードからのメッセージ"),
    (582.3, "サンプルの方は「CHANGE」"),
    (585.5, "気持ちが変わったら、選び直していい"),
    (604.4, "迷ったときに、また開ける一冊"),
    (614.9, "占星術を知らなくても読めます"),
    (624.6, "くわしい内容は概要欄から"),
]


def prepare(src, dst):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(SR),
         "-af", "highpass=f=80,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11", dst], check=True)
    with wave.open(dst) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return x.astype(np.float32) / 32768


class ZoomScene(bw.Scene):
    """表紙や申し込み画面のように動かないページは、ゆっくり寄せて見せる。"""

    def __init__(self, *a):
        super().__init__(*a)
        self.cache = {}

    def render(self, t):
        if self.scroll:
            return super().render(t)
        p = np.clip((t - self.t0) / max(1, self.t1 - self.t0), 0, 1)
        z = round(1 + 0.06 * p, 3)
        if z not in self.cache:
            w, h = self.page.size
            self.cache[z] = self.page.resize((int(w * z), int(h * z)), Image.LANCZOS)
        base, pg = self.page, self.cache[z]
        self.page = pg
        x0 = self.x
        self.x = x0 - (pg.width - base.width) // 2
        frame = super().render(t)
        self.page, self.x = base, x0
        return frame


def main():
    src, out_path = sys.argv[1], sys.argv[2]
    voice = os.path.join(bw.HERE, "out", "omasu_voice.wav")
    raw = prepare(src, voice)
    audio = np.concatenate([raw, np.zeros(int(TAIL * SR), np.float32)])
    with wave.open(voice, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())
    total = len(audio) / SR

    scene_times = []
    for i, (t0, page, label) in enumerate(SCENES):
        t1 = SCENES[i + 1][0] if i + 1 < len(SCENES) else total
        scene_times.append((t0, t1, page, label))
    starts = sorted([s[0] for s in SCENES] + [total])
    subs = []
    for i, (t0, text) in enumerate(POINTS):
        nxt = POINTS[i + 1][0] if i + 1 < len(POINTS) else total
        scene_end = min(s for s in starts if s > t0)
        subs.append((t0, min(nxt, scene_end) - 0.4, text))

    bw.Scene = ZoomScene
    bw.render(voice, audio, subs, scene_times, out_path, credit=None, tail=TAIL)


if __name__ == "__main__":
    main()
