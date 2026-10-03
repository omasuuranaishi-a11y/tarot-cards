"""読み替え辞書。読み上げ（TTS）に渡す文だけを置き換える。台本・字幕は変えない。

方針（video-lecture-maker の READINGS に合わせる）
- 実際に読み間違えた語・読みを固定したい語だけを足す。先回りの全ひらがな化はしない。
- 長い語（複合語）を先に置き換える。
- 度数・時刻の数字は、度・分・時の前だけ読みを固定する（例：17度21分 → 十七度二十一分）。

    python tools/readings.py "天秤座17度21分で重なる太陽と月。"
"""
import re
import sys

# 語の置き換え（長いものから順に当てる）
WORDS = {
    'ASC': 'エーエスシー',
    'MC': 'エムシー',
    'IC': 'アイシー',
    'Tスクエア': 'ティースクエア',
    'Tの字': 'ティーの字',
    '5度前ルール': '五度前ルール',
}

KANJI = '〇一二三四五六七八九'
KANA = ['れい', 'いち', 'に', 'さん', 'よん', 'ご', 'ろく', 'なな', 'はち', 'きゅう']
FUN = {0: 'れいふん', 1: 'いっぷん', 2: 'にふん', 3: 'さんぷん', 4: 'よんぷん', 5: 'ごふん', 6: 'ろっぷん',
       7: 'ななふん', 8: 'はっぷん', 9: 'きゅうふん'}


def kanji_num(n):
    """0〜999 を漢数字に（例：21 → 二十一、180 → 百八十、0 → 零）。"""
    if n == 0:
        return '零'
    s = ''
    for v, u in ((100, '百'), (10, '十')):
        q, n = divmod(n, v)
        if q:
            s += ('' if q == 1 else KANJI[q]) + u
    return s + (KANJI[n] if n else '')


def kana_num(n):
    if n == 0:
        return 'れい'
    s = ''
    h, n = divmod(n, 100)
    if h:
        s += {1: 'ひゃく', 3: 'さんびゃく', 6: 'ろっぴゃく', 8: 'はっぴゃく'}.get(h, KANA[h] + 'ひゃく')
    t, n = divmod(n, 10)
    if t:
        s += ('' if t == 1 else KANA[t]) + 'じゅう'
    return s + (KANA[n] if n else '')


def kana_fun(n):
    t, o = divmod(n, 10)
    if o == 0 and t:
        return ('' if t == 1 else KANA[t]) + 'じゅっぷん'
    return (('' if t == 1 else KANA[t]) + 'じゅう' if t else '') + FUN[o]


GATSU = {4: 'しがつ', 7: 'しちがつ', 9: 'くがつ'}
NICHI = {1: 'ついたち', 2: 'ふつか', 3: 'みっか', 4: 'よっか', 5: 'いつか', 6: 'むいか', 7: 'なのか', 8: 'ようか',
         9: 'ここのか', 10: 'とおか', 14: 'じゅうよっか', 17: 'じゅうしちにち', 19: 'じゅうくにち', 20: 'はつか',
         24: 'にじゅうよっか', 27: 'にじゅうしちにち', 29: 'にじゅうくにち'}


def date_kana(text):
    """年・月・日をひらがなに（例：2026年10月11日 → にせんにじゅうろくねん、じゅうがつ、じゅういちにち）。
    年のあとに読点を入れて、つながりを滑らかにする。"""
    def year(n):
        th, n = divmod(n, 1000)
        return {1: 'せん', 2: 'にせん', 3: 'さんぜん'}[th] + kana_num(n) + 'ねん'
    gatsu = lambda n: GATSU.get(n, kana_num(n) + 'がつ')
    nichi = lambda n: NICHI.get(n, kana_num(n) + 'にち')
    text = re.sub(r'(\d{4})年', lambda m: year(int(m.group(1))) + '、', text)
    text = re.sub(r'(\d+)月(\d+)日', lambda m: gatsu(int(m.group(1))) + nichi(int(m.group(2))), text)
    text = re.sub(r'(\d+)月', lambda m: gatsu(int(m.group(1))), text)
    text = re.sub(r'(\d+)日(?!曜|間)', lambda m: nichi(int(m.group(1))), text)
    return text.replace('、、', '、')


def apply(text, mode='kanji', name=None):
    """mode：'kanji'（十七度二十一分）／'kana'（じゅうななど にじゅういっぷん）／'none'（数字は変えない）。"""
    for k in sorted(WORDS, key=len, reverse=True):
        text = text.replace(k, WORDS[k])
    if name:
        text = text.replace('おます', name)
    text = date_kana(text)
    if mode == 'none':
        return text
    if mode == 'kanji':
        text = re.sub(r'(\d+)(?=度|分|時)', lambda m: kanji_num(int(m.group(1))), text)
    else:
        text = re.sub(r'(\d+)分', lambda m: kana_fun(int(m.group(1))), text)
        text = re.sub(r'(\d+)(?=度|時)', lambda m: kana_num(int(m.group(1))), text)
    return text


if __name__ == '__main__':
    for s in sys.argv[1:]:
        print(apply(s, 'kanji'))
        print(apply(s, 'kana'))
