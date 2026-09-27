/* 全13章の単位と画面の動き。読む文は 02_録音台本.md と一字一句同じ（tools/check_text.py で照合）。
   T.s(k)：その単位の k 文目を読み始める時刻、T.e(k)：読み終わる時刻、T.at(k, f)：k 文目の途中（f = 0〜1）。 */
(function () {
  const NM = Chart.make(CHARTS.nm), R = NM.R, B = CHARTS.nm.bodies, CU = CHARTS.nm.cusps;
  const L = k => B[k].lon;
  const { svgEl, div, rise, win, prog, ease, lerp, drawable, draw } = E.U;
  // cue を作る小さな関数
  const S = (name, a, b, p = {}) => ({ k: 'scene', name, a, b, p: Object.assign({ a, b }, p) });
  const cam = (a, shot, d = 2) => ({ k: 'cam', a, d, shot });
  const halo = (keys, a, b, o = {}) => Object.assign({ k: 'halo', keys, a, b }, o);
  const seg = (signs, a, b, o = {}) => Object.assign({ k: 'seg', signs, a, b }, o);
  const house = (n, a, b, o = {}) => Object.assign({ k: 'house', n, a, b }, o);
  const line = (p1, p2, a, b, o = {}) => Object.assign({ k: 'line', p1, p2, a, b }, o);
  const arc = (r, l1, l2, a, b, o = {}) => Object.assign({ k: 'arc', r, l1, l2, a, b }, o);
  const wedge = (r1, r2, l1, l2, a, b, o = {}) => Object.assign({ k: 'wedge', r1, r2, l1, l2, a, b }, o);
  const text = (p, txt, a, b, o = {}) => Object.assign({ k: 'text', p, txt, a, b }, o);
  const poly = (pts, a, b, o = {}) => Object.assign({ k: 'poly', pts, a, b }, o);
  const co = (html, anchor, x, y, a, b, o = {}) => Object.assign({ k: 'callout', html, anchor, x, y, a, b }, o);
  const panel = (title, rows, a, b, o = {}) => Object.assign({ k: 'panel', title, rows, a, b }, o);
  const tx = (html, a, b, style, cls) => [html, a, b, style, cls];
  const on = (id, list) => list.map(c => Object.assign(c, { on: id }));
  const g = s => `<span class="g hl">${s}</span>`;
  const cb = (n, v, s) => `<div class="n">${n}</div>` + (v ? `<div class="v">${v}</div>` : '') + (s ? `<div class="s">${s}</div>` : '');
  const arcO = (l1, l2, a, b, label, o = {}) => arc(R.out + 12, l1, l2, a, b, Object.assign({ label, lr: 36, fs: 24, w: 4 }, o));
  const tick = (l, a, b, o = {}) => wedge(R.signIn - 16, R.signIn, l, l + 1, a, b, Object.assign({ v: .9 }, o));
  const HOME = E.HOME;
  const VM = { fx: -175, fy: 120, s: 1.34, sx: 700, sy: 520 };
  const PANEL_HOME = { fx: 0, fy: 0, s: .94, sx: 760, sy: 505 };
  const signMid = i => ({ lon: i * 30 + 15, r: R.signIn - 4 });
  const ICO = {
    talk: '<svg class="ico" viewBox="0 0 40 40"><path d="M5 8h30v18H17l-7 7v-7H5z" fill="none" stroke="#BB965B" stroke-width="2"/></svg>',
    people: '<svg class="ico" viewBox="0 0 40 40"><circle cx="14" cy="13" r="5" fill="none" stroke="#BB965B" stroke-width="2"/><circle cx="27" cy="13" r="5" fill="none" stroke="#BB965B" stroke-width="2"/><path d="M5 33c1-7 5-11 9-11s8 4 9 11M18 33c1-7 5-11 9-11s8 4 9 11" fill="none" stroke="#BB965B" stroke-width="2"/></svg>',
    book: '<svg class="ico" viewBox="0 0 40 40"><path d="M20 10c-5-3-10-3-15-1v23c5-2 10-2 15 1 5-3 10-3 15-1V9c-5-2-10-2-15 1zm0 0v23" fill="none" stroke="#BB965B" stroke-width="2"/></svg>',
    road: '<svg class="ico" viewBox="0 0 40 40"><path d="M8 36C14 26 26 22 20 14S24 5 32 4" fill="none" stroke="#BB965B" stroke-width="2"/><circle cx="32" cy="4" r="2" fill="#BB965B"/></svg>',
    work: '<svg class="ico" viewBox="0 0 40 40"><path d="M6 36V12h28v24M15 12V6h10v6M6 22h28" fill="none" stroke="#BB965B" stroke-width="2"/></svg>',
    home: '<svg class="ico" viewBox="0 0 40 40"><path d="M5 20L20 7l15 13M10 17v18h20V17" fill="none" stroke="#BB965B" stroke-width="2"/><rect x="17" y="24" width="6" height="11" fill="none" stroke="#BB965B" stroke-width="2"/></svg>',
    hidden: '<svg class="ico" viewBox="0 0 40 40"><path d="M4 20s6-9 16-9 16 9 16 9-6 9-16 9S4 20 4 20z" fill="none" stroke="#BB965B" stroke-width="2"/><path d="M8 32L32 8" stroke="#BB965B" stroke-width="2"/></svg>',
  };
  // オーブの物差し（中心 0〜3°、補足 3〜5°）
  function orbScale(max, val, label, at) {
    return {
      build(pn) {
        const s = svgEl('svg', { width: 600, height: 170, viewBox: '0 0 600 170' }); pn.appendChild(s);
        const X = v => 20 + v / max * 560;
        svgEl('rect', { x: X(0), y: 60, width: X(3) - X(0), height: 22, fill: 'rgba(187,150,91,.55)' }, s);
        svgEl('rect', { x: X(3), y: 60, width: X(5) - X(3), height: 22, fill: 'rgba(187,150,91,.22)' }, s);
        svgEl('rect', { x: X(5), y: 60, width: X(max) - X(5), height: 22, fill: 'rgba(250,248,244,.06)' }, s);
        for (let i = 0; i <= max; i++) { const t = svgEl('text', { x: X(i), y: 110, 'text-anchor': 'middle', class: 'deg-label' }, s); t.style.fontSize = '20px'; t.textContent = i + '°'; }
        [['中心', 1.5], ['補足', 4]].forEach(([w, v]) => { const t = svgEl('text', { x: X(v), y: 48, 'text-anchor': 'middle', class: 'deg-label' }, s); t.style.fontSize = '20px'; t.style.fill = '#BB965B'; t.textContent = w; });
        const mk = svgEl('g', { opacity: 0 }, s);
        svgEl('path', { d: `M${X(val)},56 L${X(val) - 9},40 L${X(val) + 9},40 Z`, fill: '#FAF8F4' }, mk);
        svgEl('line', { x1: X(val), y1: 56, x2: X(val), y2: 86, stroke: '#FAF8F4', 'stroke-width': 3 }, mk);
        const lt = svgEl('text', { x: X(val), y: 150, 'text-anchor': 'middle', class: 'deg-label' }, mk); lt.style.fontSize = '26px'; lt.textContent = label;
        return { mk };
      },
      frame(t, ctx) { ctx.mk.setAttribute('opacity', ease(prog(t, at, .6))); },
    };
  }

  const chapters = [];
  const ch = (no, title, units) => chapters.push({ no, title, units });

  /* ======================= 01 導入 ======================= */
  ch('01', '導入', [
    { text: 'こんにちは。星よみ専門家のおますです。', pad: 1.0,
      cues: T => [S('sky', T.a, T.b, { wipe: true, texts: [tx('<div class="h">星よみ専門家　おます</div>', T.s(1), T.b, 'left:120px;top:420px')] })] },
    { text: '今回は、2026年10月11日に迎える、天秤座の新月を読んでいきます。', pad: 1.8,
      cues: T => [S('align', T.a, T.b, { keys: [[T.a, 50], [T.e(0) - .6, 0]], texts: [
        tx('<div class="h">2026年10月11日　天秤座新月</div>', T.a + .5, T.b, 'left:120px;top:140px'),
        tx('太陽と月が、同じ方向に重なる', T.e(0) - .4, T.b, 'left:124px;top:222px', 'gd')] })] },
    { text: '大切な人との関係を、壊したくない。だから、言いたいことを飲み込んでしまう。でも、飲み込んだ気持ちは消えずに残っていて、ある日ふとした一言で、強く出てしまう。そんな経験はないでしょうか。', pad: 1.6,
      cues: T => [S('phone', T.a, T.b, {
        msgs: [{ side: 'in', text: '今度の日曜、<br>また手伝ってもらえる？', at: T.s(0) + .3, top: 0 },
               { side: 'out', text: 'うん、大丈夫', at: T.s(1) + 3.1, top: 110 },
               { side: 'in', text: 'じゃあ来週もお願いね', at: T.s(2) + .8, top: 190 }],
        typing: [{ a: T.s(0) + 1.2, b: T.s(1) + .7, text: 'ちょっと疲れてて…', cps: 7 },
                 { a: T.s(1) + .7, b: T.s(1) + 1.9, text: 'ちょっと疲れてて…', erase: true, cps: 9 },
                 { a: T.s(1) + 1.9, b: T.s(1) + 3.1, text: 'うん、大丈夫', cps: 7 },
                 { a: T.s(2) + 3.4, b: T.b + 1, text: 'いいかげんにして', cps: 8, bold: true }],
        tags: [{ glyph: '1', head: '言いたいこと', body: '「ちょっと疲れてて…」', a: T.s(0) + 1.2, top: 170 },
               { glyph: '2', head: '飲み込む', body: '「うん、大丈夫」', a: T.s(1) + 1.9, top: 330 },
               { glyph: '3', head: 'ある日、強く出る', body: '「いいかげんにして」', a: T.s(2) + 3.4, top: 490 }] })] },
    { text: '前回、9月27日の満月では、自分の本音と、人とのつながりをどう両立させるか、というお話をしました。今回の新月は、その続きです。関係を大切にしたい気持ちと、自分がどう動くか。その二つを、どう結び直すかを考えていきます。', pad: 1.8,
      cues: T => [S('charts', T.a, T.b, { noMask: true,
        charts: [{ id: 'c1F', data: 'fm', home: { fx: 0, fy: 0, s: .56, sx: 500, sy: 560 } }, { id: 'c1N', data: 'nm', home: { fx: 0, fy: 0, s: .56, sx: 1420, sy: 560 } }],
        texts: [tx('<div class="m">9月27日　牡羊座満月</div>', T.a + .3, T.b, 'left:250px;top:180px;width:500px;text-align:center'),
                tx('<div class="m">10月11日　天秤座新月</div>', T.s(1), T.b, 'left:1170px;top:180px;width:500px;text-align:center'),
                tx('自分の本音 ⇄ 人とのつながり', T.at(0, .5), T.b, 'left:200px;top:870px;width:600px;text-align:center', 'gd'),
                tx('気持ちと動き方を、結び直す', T.s(3), T.b, 'left:1120px;top:870px;width:600px;text-align:center', 'gd')] }),
        ...on('c1F', [halo(['sun', 'moon'], T.a + .8, T.b), line('moon', 'sun', T.a + 1.4, T.b, { draw: 1.4 }), text('center', '180°', T.a + 2.6, T.b, { fs: 36, color: 'gold' })]),
        ...on('c1N', [halo(['sun', 'moon'], T.s(1) + .3, T.b), halo(['venus', 'mars'], T.s(2), T.b), line('venus', 'mars', T.s(2) + .6, T.b, { w: 4 })])] },
    { text: '今回も、「関係を大切にしましょう」で終わらせず、なぜそう読むのかを、度数と角度で確かめながらお話しします。', pad: 1.8,
      cues: T => [halo(['sun', 'moon'], T.a, T.b), tick(197, T.a + .8, T.b),
        co(cb('度数', '天秤座 17°21′'), { g: 'sun' }, 48, 640, T.at(0, .5), T.b),
        line('venus', 'mars', T.at(0, .6), T.b, { w: 4 }), halo(['venus', 'mars'], T.at(0, .6), T.b),
        arc(78, L('mars'), L('venus'), T.at(0, .7), T.b, { label: '90°12′', lr: 18 }),
        co(cb('角度', '90°12′'), 'center', 48, 150, T.at(0, .75), T.b)] },
    { text: '見ていくポイントは三つです。まず、天秤座17度21分で重なる太陽と月。次に、新月の支配星である金星が逆行中で、火星とほぼぴったりの角度を作っていること。そして、天秤座18度のサビアンシンボルです。最後に、新月からの2週間で試せることへつなげます。', pad: 1.6,
      cues: T => [panel('今回の三つのポイント', [
          [`<div class="mid">① ${g('☉☽')} 天秤座17°21′で重なる太陽と月</div>`, T.s(1)],
          [`<div class="mid">② ${g('♀')} 金星（逆行中）と ${g('♂')} 火星　□ 0°12′</div>`, T.s(2)],
          [`<div class="mid">③ 天秤座18度のサビアンシンボル</div>`, T.s(3)],
          [`<div class="sub">最後に：新月からの2週間で試せること</div>`, T.s(4)]], T.a + .3, T.b),
        halo(['sun', 'moon'], T.s(1), T.s(2) + .3), halo(['venus', 'mars'], T.s(2), T.s(3) + .3),
        line('venus', 'mars', T.s(2) + .8, T.s(3) + .3, { w: 4 }), seg([6], T.s(1), T.s(2)),
        tick(197, T.s(3), T.b), text({ lon: 197.5, r: R.signIn + 44 }, '18度', T.s(3) + .4, T.b, { fs: 24, color: 'gold' })] },
    { text: '初めての方も、画面で丸をつけた場所を、一緒に追ってみてください。', pad: 1.4,
      cues: T => [halo(['sun', 'moon'], T.a + .3, T.b), co(cb('丸をつけた場所', null, 'いま話している天体・度数'), { g: 'sun' }, 48, 640, T.a + .6, T.b)] },
  ]);

  /* ======================= 02 新月の時刻と前提 ======================= */
  ch('02', '新月の時刻と、このチャートの前提', [
    { text: '今回の新月は、日本時間の10月11日、日曜日の午前0時50分です。10日の土曜日の夜から、日付が変わってすぐですね。世界時では10月10日なので、海外の情報で10日の新月と書かれていても、同じ新月を指しています。', pad: 1.6,
      cues: T => [S('timeline', T.a, T.b, { from: -6, to: 3,
        axes: [{ y: 470, label: '日本時間', at: T.a + .2 }, { y: 790, label: '世界時（UT）', at: T.s(2) }],
        ticks: [{ v: -6, label: '10/10（土）18:00', y: 470 }, { v: -3, label: '21:00', y: 470 }, { v: 0, label: '10/11（日）0:00', y: 470, at: T.s(1) }, { v: 3, label: '3:00', y: 470 },
                { v: -6, label: '10/10　9:00', y: 790, at: T.s(2) + .6 }, { v: -3, label: '12:00', y: 790, at: T.s(2) + .6 }, { v: 0, label: '15:00', y: 790, at: T.s(2) + .6 }, { v: 3, label: '18:00', y: 790, at: T.s(2) + .6 }],
        events: [{ v: 50 / 60, y: 470, label: '0:50　新月', sub: '10月11日（日）', at: T.s(0) + 1.2, hlA: T.s(0) + 1.2 },
                 { v: 0, y: 470, label: '日付が変わる', sub: '', at: T.s(1) + .3, gold: false, below: true, drop: 40 },
                 { v: 50 / 60, y: 790, label: '15:50　新月', sub: '10月10日（同じ瞬間）', at: T.s(2) + 1.4, hlA: T.s(2) + 1.4 }] })] },
    { text: '新月とは、地球から見た太陽と月の黄経が、同じになる瞬間です。前回の満月では、太陽と月が180度向かい合っていました。今回は、その差が0度。', pad: 1.4,
      cues: T => [S('align', T.a, T.b, { keys: [[T.a, 0], [T.s(1), 0], [T.s(1) + 2.2, 180], [T.s(2), 180], [T.s(2) + 2, 0]], texts: [
        tx('<div class="m">新月＝太陽と月の黄経が同じ</div>', T.a + .4, T.s(1), 'left:120px;top:140px'),
        tx('<div class="m">前回の満月＝180°向かい合う</div>', T.s(1) + .2, T.s(2), 'left:120px;top:140px'),
        tx('<div class="m">今回の新月＝0°</div>', T.s(2) + 1.6, T.b, 'left:120px;top:140px')] })] },
    { text: '太陽も月も、天秤座17度21分にあります。', pad: 1.6,
      cues: T => [cam(T.a - .4, { focus: ['sun', 'moon'], s: 1.8, sx: 760, sy: 440 }, 1.8), halo(['sun', 'moon'], T.a, T.b + .6), tick(197, T.a + .6, T.b + .6),
        co(cb('☉☽ 太陽・月', '天秤座 17°21′', '差 0°00′'), { g: 'moon' }, 48, 150, T.a + .8, T.b)] },
    { text: '今日も、東京で作成した、トロピカル方式、プラシーダスのチャートを使います。前回と同じ設定です。', pad: 1.6,
      cues: T => [cam(T.a, 'home', 1.6), panel('このチャートの設定', [
          ['<div class="mid">場所：東京</div><div class="sub">北緯35°42′ 東経139°46′</div>', T.at(0, .1)],
          ['<div class="mid">黄道の区切り方：トロピカル</div>', T.at(0, .45)],
          ['<div class="mid">ハウス：プラシーダス</div>', T.at(0, .75)],
          ['<div class="sub">前回の満月と同じ設定です</div>', T.s(1)]], T.a + .2, T.b),
        line({ key: 'asc', r: R.signIn }, { key: 'dsc', r: R.signIn }, T.at(0, .75), T.b, { w: 3 }),
        line({ key: 'mc', r: R.signIn }, { key: 'ic', r: R.signIn }, T.at(0, .8), T.b, { w: 3 })] },
    { text: '大切なので、もう一度確認しておきます。新月の時刻や、天体同士の角度は、どこから見ても同じです。でも、ハウスは場所によって変わります。この図の第3ハウスが、そのまま皆さん全員の出生図の第3ハウスになる、ということではありません。', pad: 1.6,
      cues: T => [S('charts', T.a, T.b, { noMask: true,
        charts: [{ id: 'c2T', data: 'nm', home: { fx: 0, fy: 0, s: .56, sx: 500, sy: 560 } }, { id: 'c2L', data: 'nmLondon', home: { fx: 0, fy: 0, s: .56, sx: 1420, sy: 560 } }],
        texts: [tx('<div class="m">東京</div>', T.a + .3, T.b, 'left:250px;top:180px;width:500px;text-align:center'),
                tx('<div class="m">ロンドン（同じ瞬間）</div>', T.a + .6, T.b, 'left:1170px;top:180px;width:500px;text-align:center'),
                tx('天体どうしの角度は同じ', T.s(1) + .8, T.s(2), 'left:0;right:0;top:872px;text-align:center', 'gd'),
                tx('ASC・MCとハウスは場所で変わる', T.s(2) + .6, T.b, 'left:0;right:0;top:872px;text-align:center', 'gd')] }),
        ...['c2T', 'c2L'].flatMap(id => on(id, [halo(['sun', 'moon', 'venus', 'mars'], T.s(1), T.s(2) + .5), line('venus', 'mars', T.s(1) + .4, T.b, { w: 5 }),
          line({ key: 'asc', r: R.signIn }, { key: 'dsc', r: R.signIn }, T.s(2) + .3, T.b, { w: 6 }), line({ key: 'mc', r: R.signIn }, { key: 'ic', r: R.signIn }, T.s(2) + .5, T.b, { w: 6 }),
          house(3, T.s(3), T.b, { v: .8 })]))] },
    { text: '今回も、新月の瞬間を東京で切り取った図として読んでいきます。', pad: 1.2,
      cues: T => [cam(T.a - .6, 'home', .1), co(cb('東京で切り取った図', '2026/10/11 0:50'), { key: 'asc', r: R.out }, 48, 640, T.a + .3, T.b)] },
  ]);

  /* ======================= 03 天秤座で重なる太陽と月 ======================= */
  ch('03', '天秤座17度21分で重なる太陽と月', [
    { text: 'では、太陽と月が重なっている、天秤座を見ていきます。', pad: 1.2,
      cues: T => [cam(T.a, { focus: ['sun', 'moon'], s: 1.35, sx: 760, sy: 420 }, 2), seg([6], T.a + .6, T.b + .5), halo(['sun', 'moon'], T.a + .6, T.b + .5)] },
    { text: '天秤座は、風のサインで、活動宮です。風は、言葉や考え方、人との情報の交換。活動宮は、物事を動かし始める性質です。天秤座は、人との関わり、比べること、釣り合いを取ることと結びつけて読みます。', pad: 1.6,
      cues: T => [cam(T.a, 'home', 1.8), seg([2, 6, 10], T.s(0) + .3, T.e(1) + .4), seg([0, 3, 6, 9], T.s(2), T.e(2) + .4), seg([6], T.a, T.b),
        poly([signMid(2), signMid(6), signMid(10)], T.s(1), T.e(1) + .4, { v: .16 }), poly([signMid(0), signMid(3), signMid(6), signMid(9)], T.s(2), T.e(2) + .4, { v: .12 }),
        panel('天秤座', [
          ['<div class="mid">風のサイン</div><div class="sub">言葉・考え方・情報の交換</div>', T.s(1)],
          ['<div class="mid">活動宮</div><div class="sub">物事を動かし始める</div>', T.s(2)],
          ['<div class="mid">人との関わり ・ 比べる ・ 釣り合い</div>', T.s(3)]], T.s(0) + .5, T.b)] },
    { text: '前回の満月で、天秤座にあったのは太陽だけでした。月は向かい側の牡羊座にいて、「私はこうしたい」という気持ちと、「相手はどう思う？」という視点を、両方見る配置でした。', pad: 2.2,
      cues: T => [S('charts', T.a, T.b, { noMask: true, charts: [{ id: 'c3F', data: 'fm', home: HOME }],
        texts: [tx('<div class="m">前回　9月27日の満月</div>', T.a + .3, T.b, 'left:1240px;top:150px')] }),
        ...on('c3F', [halo(['sun'], T.a + .6, T.b), seg([6], T.a + .6, T.b), halo(['moon'], T.s(1), T.b), seg([0], T.s(1), T.b),
          line({ g: 'moon' }, { g: 'sun' }, T.s(1) + .8, T.b, { w: 4, draw: 1.6 }), text('center', '180°', T.s(1) + 2, T.b, { fs: 34, color: 'gold' }),
          co(cb('☽ 牡羊座の月　3°37′', '「私はこうしたい」'), { g: 'moon' }, 1240, 260, T.at(1, .35), T.b),
          co(cb('☉ 天秤座の太陽　3°37′', '「相手はどう思う？」'), { g: 'sun' }, 48, 640, T.at(1, .7), T.b)])] },
    { text: '今回は、太陽も月も天秤座にあります。自分がはっきりさせたいことと、自然に湧いてくる気持ちが、同じ場所を向いている。関係のことを考えるのに、気持ちが向きやすい新月だと読めます。', pad: 1.6,
      cues: T => [cam(T.a - .6, { focus: ['sun', 'moon'], s: 1.5, sx: 640, sy: 420 }, .1), halo(['sun', 'moon'], T.a, T.b), seg([6], T.a, T.b), tick(197, T.a + .4, T.b),
        panel('太陽と月が重なる', [
          [`<div class="mid">${g('☉')} 太陽　はっきりさせたいこと</div>`, T.s(1)],
          [`<div class="mid">${g('☽')} 月　自然に湧いてくる気持ち</div>`, T.at(1, .5)],
          ['<div class="mid">どちらも天秤座17°21′（関係）を向く</div>', T.s(2)]], T.a + .4, T.b)] },
    { text: '新月は、月の満ち欠けのサイクルの始まりです。何かが完成する時期ではなく、種をまく時期として読みます。', pad: 1.8,
      cues: T => [S('cycle', T.a, T.b, { moveA: T.s(0) + .8, moveB: T.s(1) + 1.6, texts: [
        tx('<div class="m">新月　種をまく</div>', T.s(1) + .2, T.b, 'left:1040px;top:140px'),
        tx('<div class="m">満月　実り・気づき</div>', T.s(1) + 1.6, T.b, 'left:1040px;top:830px'),
        tx('約2週間', T.s(1) + 1.2, T.b, 'left:1300px;top:500px', 'gd')] })] },
    { text: '例えば、職場でも家族でも、いつのまにか役割が固定している関係があるとします。いつも自分が調整役になっている。いつも相手が決めている。新月は、それを一気に変える日ではなく、「この関係の釣り合いを、少し見直したい」と、自分の中で意図を持つ始まりになります。', pad: 1.8,
      cues: T => [S('balance', T.a, T.b, { tiltA: T.s(1), tagLA: T.s(1), tagRA: T.s(2), levelA: T.at(3, .55), texts: [
        tx('役割が固定した関係', T.s(0) + .5, T.s(3), 'left:120px;top:150px', 'm'),
        tx('一気に変えるのではなく', T.s(3), T.b, 'left:120px;top:150px', 'm'),
        tx('「釣り合いを、少し見直したい」という意図', T.at(3, .55), T.b, 'left:120px;top:220px', 'gd'),
        tx('日常の例です。配置が出来事を決めるわけではありません。', T.a + .5, T.b, 'left:64px;top:944px;font-size:20px', 's')] })] },
    { text: 'ただし、天秤座の太陽は、伝統的な占星術ではフォール、減衰とされる位置です。これは悪いという意味ではなく、太陽の「自分で決めて、自分を主張する」働きが、相手を意識するぶん出しにくい、ということ。だからこそ、自分の意図を言葉にしておくことが助けになります。', pad: 1.8,
      cues: T => [cam(T.a - .6, 'home', .1), halo(['sun'], T.a, T.b),
        seg([4], T.at(0, .15), T.e(0) + .3), seg([0], T.at(0, .35), T.e(0) + .3), seg([10], T.at(0, .55), T.e(0) + .3), seg([6], T.at(0, .75), T.b, { v: 1 }),
        panel('太陽の品位（伝統的な占星術）', [
          ['<div class="mid">獅子座　ドミサイル<span class="sub">（本来の場所）</span></div>', T.at(0, .15)],
          ['<div class="mid">牡羊座　イグザルテーション<span class="sub">（高揚）</span></div>', T.at(0, .35)],
          ['<div class="mid">水瓶座　デトリメント<span class="sub">（反対側）</span></div>', T.at(0, .55)],
          ['<div class="mid hl">天秤座　フォール<span class="sub">（減衰）← 今回</span></div>', T.at(0, .75)],
          ['<div class="sub">悪いではなく「自分を主張しにくい」</div>', T.s(1)],
          ['<div class="mid">だから、意図を言葉にしておく</div>', T.s(2)]], T.a + .2, T.b)] },
  ]);

  /* ======================= 04 第3ハウス ======================= */
  const C3 = CU[2], C4 = CU[3];
  ch('04', '第3ハウスの新月と、チャートの支配星', [
    { text: '次に、ハウスです。東京図では、太陽と月は第3ハウスにあります。第3ハウスの入口は天秤座6度26分。新月は、そこから11度ほど入ったところです。次の第4ハウスの入口までは21度33分あるので、5度前ルールを考える必要もありません。', pad: 2.4,
      cues: T => [cam(T.a, { fx: -150, fy: 250, s: 1.55, sx: 760, sy: 420 }, 2), house(3, T.s(1), T.b + .6, { v: .6 }), halo(['sun', 'moon'], T.s(1), T.b),
        line({ lon: C3, r: R.asp }, { lon: C3, r: R.signIn }, T.s(2), T.b, { w: 5 }),
        co(cb('第3ハウスの入口', '天秤座 6°26′'), { lon: C3, r: R.signIn }, 48, 150, T.s(2) + .3, T.b),
        arcO(C3, L('sun'), T.s(3), T.b, '10°55′'),
        arcO(L('sun'), C4, T.s(4), T.b, '21°33′'),
        wedge(R.asp, R.signIn - 14, C4 - 5, C4, T.at(4, .55), T.b, { v: .5, fill: 'rgba(187,150,91,.25)', stroke: 'gold' }),
        text({ lon: C4 - 2.5, r: R.asp + 30 }, '5度前', T.at(4, .6), T.b, { fs: 22, color: 'gold' })] },
    { text: '第3ハウスは、言葉、身近な人との行き来、学び、日常の移動の場所として読みます。遠くの大きな目標より、毎日のやりとりの場所ですね。', pad: 1.6,
      cues: T => [cam(T.a - .2, 'home', 1.6), house(3, T.a, T.b, { v: .6 }),
        panel('第3ハウス', [
          [`<div class="mid">${ICO.talk}言葉・メッセージ</div>`, T.at(0, .12)],
          [`<div class="mid">${ICO.people}身近な人との行き来</div>`, T.at(0, .32)],
          [`<div class="mid">${ICO.book}学び</div>`, T.at(0, .52)],
          [`<div class="mid">${ICO.road}日常の移動</div>`, T.at(0, .66)],
          ['<div class="mid hl">毎日のやりとりの場所</div>', T.s(1) + .4]], T.a + .2, T.b)] },
    { text: '天秤座の新月が第3ハウスにあると、関係の見直しは、特別な話し合いの場より、ふだんの会話や、メッセージのやりとりの中から始まる、という読みができます。', pad: 1.6,
      cues: T => [S('talk', T.a, T.b, { texts: [tx('特別な話し合いの場より', T.at(0, .3), T.b, 'left:120px;top:150px', 'm'), tx('ふだんの会話・メッセージから', T.at(0, .6), T.b, 'left:120px;top:220px', 'gd')] })] },
    { text: 'もう一つ、この図のASC、上昇点は、獅子座15度59分です。獅子座の支配星は太陽なので、この図全体の支配星は太陽。つまり、新月を作っている太陽そのものが、チャートの主役ということになります。', pad: 1.8,
      cues: T => [co(cb('ASC（上昇点）', '獅子座 15°59′'), { key: 'asc', r: R.out }, 48, 150, T.s(0) + .8, T.b), line({ key: 'asc', r: R.signIn }, { key: 'asc', r: R.out + 28 }, T.s(0) + .6, T.b, { w: 5 }),
        seg([4], T.s(1), T.b), line({ key: 'asc', r: R.asp }, { g: 'sun' }, T.s(1) + .8, T.b, { curve: .45, arrow: true, w: 3 }),
        text({ lon: 170, r: 150 }, '獅子座の支配星', T.s(1) + 1.6, T.b, { fs: 24, color: 'gold' }), halo(['sun'], T.s(1) + 1.8, T.b),
        co(cb('チャート全体の支配星', '☉ 太陽', '新月そのもの'), { g: 'sun' }, 48, 640, T.s(2), T.b)] },
    { text: 'さらに、太陽と月は、そのASCと約60度、セクスタイルの角度で結ばれています。実際の角度差は61度21分で、オーブは1度21分です。', pad: 2.2,
      cues: T => [halo(['sun', 'moon'], T.a, T.b + .6), line('asc', 'sun', T.s(0) + .8, T.b + .6, { color: 'white', w: 3 }),
        arc(78, L('asc'), L('sun'), T.s(1), T.b + .6, { label: '61°21′', lr: 20 }),
        panel('セクスタイル（60°）', [
          ['<div class="mid">実際の角度差　<b class="big" style="font-size:40px">61°21′</b></div>', T.s(1)],
          ['<div class="mid">60°との差</div>', T.at(1, .5)],
          ['<div class="big">オーブ <span class="hl" style="font-size:60px">1°21′</span></div>', T.at(1, .65)]], T.a + .4, T.b)] },
    { text: 'ASCは、この図の「表に出る姿勢」を表す場所です。自分らしさを表に出すことが、関係の見直しを後押しする。この新月には、そういう配置が見えます。', pad: 1.6,
      cues: T => [line('asc', 'sun', T.a - .6, T.b, { color: 'white', w: 3, draw: .01 }), halo(['sun', 'moon'], T.a, T.b),
        co(cb('ASC', '「表に出る姿勢」'), { key: 'asc', r: R.out }, 48, 150, T.a + .4, T.b),
        panel('ASCと新月', [['<div class="mid">自分らしさを表に出す</div>', T.s(1)], ['<div class="mid hl">→ 関係の見直しを後押し</div>', T.at(1, .5)]], T.a + .6, T.b)] },
  ]);

  /* ======================= 05 支配星の金星 ======================= */
  const V0 = 218.48, VN = L('venus'), V25 = 210, VD = 202.85;
  ch('05', '支配星の金星は、逆行中', [
    { text: 'ここからは、新月の支配星を追っていきます。新月が起きたのは天秤座17度21分。天秤座を担当する天体、支配星は金星です。その金星は、いま蠍座7度25分にあります。', pad: 1.2,
      cues: T => [cam(T.a, 'home', .1), halo(['sun', 'moon'], T.s(1), T.s(3) + 1), co(cb('新月', '天秤座 17°21′', '太陽と月が 0°00′'), { g: 'sun' }, 48, 640, T.s(1) + .2, T.s(2) + .3),
        seg([6], T.s(2), T.s(3) + .6), co(cb('天秤座の支配星', '♀ 金星'), { lon: 195, r: (R.signIn + R.out) / 2 }, 48, 640, T.s(2) + .5, T.s(3) + .1),
        line({ g: 'sun' }, { g: 'venus' }, T.s(2) + 1.2, T.s(3) + .6, { curve: .7, arrow: true }),
        halo(['venus'], T.s(3), T.b + .8), co(cb('♀ 金星', '蠍座 7°25′ R', '逆行中'), { g: 'venus' }, 48, 640, T.s(3) + .3, T.b)] },
    { text: '10月3日に、蠍座8度29分で逆行を始めたばかりです。ここから少しずつ度数を戻して、10月25日には天秤座へ戻り、11月14日に天秤座22度51分で順行に戻ります。', pad: 2.4,
      cues: T => [cam(T.a, { fx: -110, fy: 300, s: 1.75, sx: 640, sy: 360 }, 2), halo(['venus'], T.a, T.b),
        arc(R.out + 16, V0, VD, T.s(1), T.b, { draw: 4, w: 6, label: '', }),
        line({ lon: 210, r: R.signIn }, { lon: 210, r: R.out + 30 }, T.at(1, .35), T.b, { w: 4 }),
        panel('金星の逆行の道のり', [], T.a + .3, T.b, { build(pn) {
          const s = svgEl('svg', { width: 600, height: 330, viewBox: '0 0 600 330' }); pn.appendChild(s);
          const X = lon => 40 + (lon - 200) / 20 * 520;
          svgEl('line', { x1: X(200), y1: 160, x2: X(220), y2: 160, stroke: '#BB965B', 'stroke-width': 2 }, s);
          for (let l = 200; l <= 220; l++) svgEl('line', { x1: X(l), y1: 160 - (l % 5 ? 6 : 12), x2: X(l), y2: 160, stroke: '#BB965B' }, s);
          [[200, '天秤座20°'], [210, '蠍座0°'], [220, '蠍座10°']].forEach(([l, w]) => { const t = svgEl('text', { x: X(l), y: 196, 'text-anchor': 'middle', class: 'deg-label' }, s); t.style.fontSize = '20px'; t.textContent = w; });
          const M = [[V0, '10/3 逆行開始', '蠍座8°29′', 70], [VN, '10/11 新月', '蠍座7°25′', 250], [V25, '10/25', '天秤座へ', 70], [VD, '11/14 順行へ', '天秤座22°51′', 250]].map(([l, a, b, y]) => {
            const gg = svgEl('g', { opacity: 0 }, s);
            svgEl('line', { x1: X(l), y1: 160, x2: X(l), y2: y < 160 ? y + 30 : y - 34, stroke: 'rgba(250,248,244,.5)', 'stroke-dasharray': '3 4' }, gg);
            const t1 = svgEl('text', { x: X(l), y, 'text-anchor': 'middle', class: 'deg-label' }, gg); t1.style.fontSize = '22px'; t1.textContent = a;
            const t2 = svgEl('text', { x: X(l), y: y + 26, 'text-anchor': 'middle', class: 'deg-label' }, gg); t2.style.fontSize = '20px'; t2.style.fill = '#BB965B'; t2.textContent = b;
            return gg;
          });
          const dot = svgEl('circle', { r: 10, cy: 160, fill: '#FAF8F4' }, s);
          const trail = svgEl('line', { y1: 160, y2: 160, stroke: '#f3d9a4', 'stroke-width': 6 }, s);
          return { X, M, dot, trail };
        }, frame(t, c) {
          const k = [[T.s(0), V0], [T.s(0) + 2, VN], [T.s(1), VN], [T.at(1, .4), V25], [T.at(1, .8), VD]];
          let l = k[0][1]; for (let i = 1; i < k.length; i++) if (t >= k[i - 1][0]) l = lerp(k[i - 1][1], k[i][1], ease(prog(t, k[i - 1][0], k[i][0] - k[i - 1][0])));
          c.dot.setAttribute('cx', c.X(l)); c.trail.setAttribute('x1', c.X(V0)); c.trail.setAttribute('x2', c.X(l));
          [T.s(0), T.s(0) + 1.8, T.at(1, .38), T.at(1, .78)].forEach((a, i) => c.M[i].setAttribute('opacity', ease(prog(t, a, .5))));
        } })] },
    { text: '逆行は、地球から見たときに、天体が後ろへ進んでいるように見える現象です。実際に天体が戻っているわけではありません。占星術では、その天体のテーマを「見直す」「振り返る」時期として読みます。', pad: 2.0,
      cues: T => [S('orbit', T.a, T.b, { texts: [
        tx('地球から見た方向が、<br>後ろへ戻って見える', T.at(0, .5), T.b, 'left:1250px;top:220px', 'm'),
        tx('実際は、金星も地球も<br>前へ進んでいる', T.s(1), T.b, 'left:1250px;top:400px', 'gd'),
        tx('占星術では<br>「見直す」「振り返る」時期', T.s(2), T.b, 'left:1250px;top:580px', 'm')] })] },
    { text: '金星は、何を大切にしたいか、何を心地よいと感じるか、人やものとの関係を表す天体です。その金星が逆行するので、新しい関係を広げるより、これまでの関係で何を大切にしてきたかを見直す。そういう時期だと考えます。', pad: 1.6,
      cues: T => [S('letters', T.a, T.b, { texts: [
        tx(`<span class="g gd">♀</span> 金星　大切にしたいもの・心地よさ・関係`, T.at(0, .2), T.b, 'left:120px;top:150px', 'm'),
        tx('新しく広げるより、これまでを見直す', T.s(1) + .4, T.b, 'left:120px;top:830px', 'gd')] })] },
    { text: '蠍座は、水のサインで、不動宮。深く、長く関わることを大切にするサインです。伝統的には、金星にとって蠍座はデトリメント、本来の場所の反対側とされます。軽やかに楽しむ金星の働きが、ここでは深く、重く、じっくりしたものになりやすい、と読めます。', pad: 1.8,
      cues: T => [cam(T.a - .6, 'home', .1), halo(['venus'], T.a, T.b), seg([7], T.a + .3, T.b, { v: 1 }), seg([3, 11], T.a + .5, T.e(1)),
        poly([signMid(3), signMid(7), signMid(11)], T.a + .6, T.e(1), { v: .14 }),
        seg([1, 6], T.s(2), T.b, { v: .6 }),
        line(signMid(1), signMid(7), T.at(2, .4), T.b, { color: 'white', dash: '8 8', w: 2 }), line(signMid(6), signMid(0), T.at(2, .5), T.b, { color: 'white', dash: '8 8', w: 2 }),
        panel('金星と蠍座', [
          ['<div class="mid">蠍座　水のサイン・不動宮</div><div class="sub">深く、長く関わる</div>', T.s(0) + .3],
          ['<div class="mid">金星の本来の場所　牡牛座・天秤座</div>', T.s(2)],
          ['<div class="mid hl">その反対側＝デトリメント　蠍座・牡羊座</div>', T.at(2, .5)],
          ['<div class="mid">軽やかに → 深く、重く、じっくり</div>', T.s(3)]], T.a + .2, T.b)] },
    { text: 'そして東京図では、金星は第3ハウスの終わり、第4ハウスの入口まで1度29分のところにいます。第4ハウスの入口は、ICとも呼ばれる、図のいちばん下の点です。家庭や、心のよりどころ、自分の土台を表します。5度前ルールを使うなら、金星は第4ハウスとしても読めます。', pad: 2.0,
      cues: T => [cam(T.a, { fx: -40, fy: 320, s: 2.0, sx: 700, sy: 380 }, 2), halo(['venus'], T.a, T.b + .6),
        line({ lon: C4, r: R.asp }, { lon: C4, r: R.out + 28 }, T.s(0) + .8, T.b + .6, { w: 5 }),
        arcO(VN, C4, T.at(0, .6), T.b + .6, '1°29′'),
        co(cb('IC（第4ハウスの入口）', '蠍座 8°55′'), { lon: C4, r: R.out }, 1240, 180, T.s(1), T.s(2)),
        co(cb('IC', '家庭・心のよりどころ・土台'), { lon: C4, r: R.out }, 1240, 180, T.s(2) + .1, T.b),
        wedge(R.asp, R.signIn - 14, C4 - 5, C4, T.s(3), T.b + .6, { v: .5, fill: 'rgba(187,150,91,.25)', stroke: 'gold' }),
        text({ lon: C4 - 2.5, r: R.asp + 34 }, 'IC手前5°', T.s(3) + .4, T.b + .6, { fs: 20, color: 'gold' }), house(4, T.at(3, .5), T.b + .6, { v: .5 })] },
    { text: '関係の見直しが、家族や、いちばん身近な居場所のことにも及びやすい配置です。', pad: 1.6,
      cues: T => [S('window', T.a, T.b, { texts: [tx('家族・いちばん身近な居場所', T.a + .6, T.b, 'left:120px;top:150px', 'm')] })] },
  ]);

  /* ======================= 06 金星と火星のスクエア ======================= */
  const RANK = [['太陽 ☌ 月', 0, 0], ['金星 □ 火星', 0, 12], ['海王星 ✶ 冥王星', 0, 28], ['太陽・月 ✶ ASC', 1, 21], ['金星 ☍ MC', 1, 29], ['火星 □ MC', 1, 41]];
  const sqMid = (() => { const a = NM.pt(L('venus'), R.asp), b = NM.pt(L('mars'), R.asp), mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, d = Math.hypot(mx, my); return [mx - mx / d * 80 + 30, my - my / d * 80]; })();
  ch('06', '金星と火星、0°12′のスクエア', [
    { text: 'そして、この金星と、ほぼぴったりの角度を作っている天体があります。獅子座の火星です。', pad: 1.2,
      cues: T => [cam(T.a + .2, VM, 2.4), halo(['venus'], T.a, T.u(4).b + .5), halo(['mars'], T.s(1) - .2, T.u(4).b + .5),
        co(cb('♀ 金星', '蠍座 7°25′ R', '10/3から逆行中'), { g: 'venus' }, 48, 640, T.a, T.u(1).a + .3),
        co(cb('♂ 火星', '獅子座 7°13′', '第12ハウス'), { g: 'mars' }, 48, 150, T.s(1), T.u(1).a + .3)] },
    { text: '金星が蠍座7度25分、火星が獅子座7度13分。サインは違いますが、度数はほとんど同じですね。', pad: 1.6,
      cues: T => [tick(217, T.s(1) - .2, T.u(1).b), tick(127, T.s(1) - .2, T.u(1).b),
        panel('度数を比べる', [
          [`<div class="big">${g('♀')} 金星 <span class="sub">蠍座</span> <span class="d7">7°</span>25′</div>`, T.s(0)],
          [`<div class="big">${g('♂')} 火星 <span class="sub">獅子座</span> <span class="d7">7°</span>13′</div>`, T.s(0) + 1.6],
          ['<div class="sub">サインは違っても、度数はほぼ同じ</div>', T.s(1) + .4]], T.a, T.b,
          { frame(t, c, pn) { pn.querySelectorAll('.d7').forEach(e => e.style.color = t >= T.s(1) ? '#BB965B' : ''); } })] },
    { text: '二つの差は90度12分です。90度、スクエアからのずれは、わずか12分。', pad: 2.4,
      cues: T => [line('center', { key: 'venus', r: R.signIn }, T.a + .1, T.b + .6, { color: 'white', w: 1.6, draw: 1 }), line('center', { key: 'mars', r: R.signIn }, T.a + .4, T.b + .6, { color: 'white', w: 1.6, draw: 1 }),
        arc(78, L('mars'), L('venus'), T.a + 1.2, T.b + .6, { label: '90°12′', lr: 18, draw: 1.4 }),
        line('venus', 'mars', T.s(1), T.chB, { w: 4, draw: 1.4, glow: [T.u(3).s(2) + 2, T.u(3).b] }),
        panel('角度とオーブ', [
          ['<div class="mid">実際の角度差　<b class="big" style="font-size:42px">90°12′</b></div>', T.a + .8],
          ['<div class="mid">スクエア　90°00′ との差</div>', T.s(1)],
          ['<div class="big">オーブ <span class="hl" style="font-size:64px">0°12′</span></div>', T.s(1) + 1.4]], T.a + .2, T.b)] },
    { text: '今回のチャートで、太陽と月の重なりの次に正確な角度です。', pad: 3.4,
      cues: T => [text(sqMid, '□ 0°12′', T.a - 1, T.u(1).b, { fs: 28 }),
        panel('オーブの小さい順', [['<div class="sub">今回は3°以内を中心、5°までを補足として扱います</div>', T.a + 3]], T.a, T.b, {
          build(pn) {
            const box = document.createElement('div'); pn.insertBefore(box, pn.children[1]);
            return RANK.map(([n, d, m], i) => {
              const hl = i === 1, r = div('row', `<div style="display:flex;align-items:center;height:52px"><div style="width:230px;font-family:var(--gothic);font-size:24px;font-weight:${hl ? 700 : 500};color:${hl ? 'var(--gold)' : 'var(--white)'}">${n}</div>
                <div style="position:relative;width:250px;height:14px"><div class="bar" style="position:absolute;left:0;top:0;height:14px;width:0;background:${hl ? 'var(--gold)' : 'rgba(250,248,244,.45)'}"></div></div>
                <div style="width:120px;text-align:right;font-family:var(--gothic);font-size:26px;font-weight:700;color:${hl ? 'var(--gold)' : 'var(--white)'}">${d}°${String(m).padStart(2, '0')}′</div></div>`, box);
              return { r, bar: r.querySelector('.bar'), w: (d + m / 60) / 3 * 250, a: T.a + .4 + i * .35 };
            });
          }, frame(t, B) { B.forEach(b => { rise(b.r, win(t, b.a, T.b, .5, .5)); b.bar.style.width = (b.w * ease(prog(t, b.a + .2, .9))).toFixed(1) + 'px'; }); } })] },
    { text: 'しかも、金星は逆行で度数を戻し、火星は前へ進んでいます。二つは近づいていく途中で、この角度は、新月から約5時間半後の、10月11日の朝6時31分ごろに、ぴったり90度になります。', pad: 2.4,
      cues: T => [panel('近づいていく途中の角度', [], T.a, T.b, {
        build(pn) {
          const rs = svgEl('svg', { width: 610, height: 480, viewBox: '0 0 610 480' }); pn.appendChild(rs);
          const ruler = (y, sign, glyph) => {
            const gg = svgEl('g', {}, rs);
            svgEl('line', { x1: 60, y1: y, x2: 540, y2: y, stroke: '#BB965B', 'stroke-width': 2 }, gg);
            for (let m = 0; m <= 60; m += 5) {
              const x = 60 + m * 8, big = m % 30 === 0;
              svgEl('line', { x1: x, y1: y - (big ? 14 : 7), x2: x, y2: y, stroke: '#BB965B', 'stroke-width': big ? 2 : 1 }, gg);
              if (big) { const t = svgEl('text', { x, y: y + 30, 'text-anchor': 'middle', class: 'deg-label' }, gg); t.style.fontSize = '20px'; t.textContent = m === 60 ? '8°00′' : `7°${String(m).padStart(2, '0')}′`; }
            }
            const lab = svgEl('text', { x: 0, y: y - 96, class: 'deg-label' }, gg); lab.style.fontSize = '24px'; lab.textContent = sign;
            const mk = svgEl('g', {}, gg);
            svgEl('line', { x1: 0, y1: y - 30, x2: 0, y2: y + 4, stroke: '#FAF8F4', 'stroke-width': 3 }, mk);
            const gt = svgEl('text', { x: 0, y: y - 48, 'text-anchor': 'middle', class: 'glyph', fill: '#FAF8F4' }, mk); gt.style.fontSize = '34px'; gt.textContent = glyph;
            const vt = svgEl('text', { x: 0, y: y + 58, 'text-anchor': 'middle', class: 'deg-label' }, mk); vt.style.fontSize = '24px'; vt.style.fill = '#BB965B';
            return { mk, vt };
          };
          const rV = ruler(130, '蠍座（金星・逆行中）', '♀'), rM = ruler(330, '獅子座（火星・順行）', '♂');
          const aV = svgEl('text', { class: 'deg-label' }, rs); aV.style.fontSize = '26px'; aV.textContent = '←';
          const aM = svgEl('text', { class: 'deg-label' }, rs); aM.style.fontSize = '26px'; aM.textContent = '→';
          const ex = svgEl('line', { x1: 228, y1: 86, x2: 228, y2: 340, stroke: '#BB965B', 'stroke-width': 2, 'stroke-dasharray': '6 6', opacity: 0 }, rs);
          const ck = svgEl('text', { x: 305, y: 436, 'text-anchor': 'middle', class: 'deg-label' }, rs); ck.style.fontSize = '30px';
          const cs = svgEl('text', { x: 305, y: 468, 'text-anchor': 'middle', class: 'deg-label' }, rs); cs.style.fontSize = '22px'; cs.style.fill = '#BB965B';
          return { rV, rM, aV, aM, ex, ck, cs };
        }, frame(t, c) {
          const mv = ease(prog(t, T.s(1) + .5, 7.5)), v = lerp(25, 21, mv), m = lerp(13, 21, mv);
          c.rV.mk.setAttribute('transform', `translate(${60 + v * 8},0)`); c.rM.mk.setAttribute('transform', `translate(${60 + m * 8},0)`);
          c.rV.vt.textContent = `7°${String(Math.ceil(v - 1e-6)).padStart(2, '0')}′`; c.rM.vt.textContent = `7°${String(Math.floor(m + 1e-6)).padStart(2, '0')}′`;
          const av = win(t, T.s(0) + .4, T.s(1) + 7.8, .5, .5);
          c.aV.setAttribute('x', 60 + v * 8 - 44); c.aV.setAttribute('y', 139); c.aV.setAttribute('opacity', av);
          c.aM.setAttribute('x', 60 + m * 8 + 16); c.aM.setAttribute('y', 339); c.aM.setAttribute('opacity', av);
          c.ex.setAttribute('opacity', win(t, T.s(1) + 7.8, T.b, .6, .5));
          const mins = Math.floor(lerp(50, 391, mv) + 1e-6);
          c.ck.textContent = `10/11　${Math.floor(mins / 60)}:${String(mins % 60).padStart(2, '0')}`;
          c.cs.textContent = mv < .02 ? '新月の瞬間' : mv >= 1 ? 'ぴったり 90°00′' : '';
        } })] },
    { text: '蠍座と獅子座は、どちらも不動宮です。不動宮は、一度決めたことや、大切にしているものを、簡単には手放さないサインです。牡牛座、獅子座、蠍座、水瓶座の四つがあり、今回はそのうち二つが、90度でぶつかっています。', pad: 2.0,
      cues: T => [cam(T.a + .1, 'home', 2.2), seg([4, 7], T.a + .3, T.b), seg([1], T.s(2), T.s(2) + 4.5), seg([10], T.s(2) + 2.3, T.s(2) + 4.5),
        ...[[1, 4], [4, 7], [7, 10], [10, 1]].map(([i, j], k) => line(signMid(i), signMid(j), T.s(2) + 2.6 + k * .3, T.s(2) + 5, { w: 1.6, draw: .5 })),
        panel('不動宮', [
          ['<div class="mid">牡牛座 ・ 獅子座 ・ 蠍座 ・ 水瓶座</div>', T.s(1) - .4],
          ['<div class="sub">一度決めたこと、大切にしているものを<br>簡単には手放さない</div>', T.s(1) + 1.2],
          ['<div class="mid"><span class="hl">蠍座の金星</span> と <span class="hl">獅子座の火星</span><br>が 90° で向き合う</div>', T.s(2) + 4.5]], T.s(1) - .6, T.b)] },
    { text: '金星は、何を大切にしたいか、何を受け取りたいか。火星は、それをどう求めて、どう行動に移すか。この二つが90度で結ばれると、欲しいものと、そのための動き方が、かみ合いにくいという読みができます。', pad: 1.6,
      cues: T => [cam(T.a + .1, VM, 2), panel('金星と火星の働き', [
          [`<div class="mid">${g('♀')} 金星　何を大切にしたいか<br><span style="padding-left:2.1em">何を受け取りたいか</span></div>`, T.s(0)],
          [`<div class="mid">${g('♂')} 火星　それをどう求め<br><span style="padding-left:2.1em">どう行動に移すか</span></div>`, T.s(1)],
          ['<div class="mid" style="padding-top:14px;border-top:1px solid rgba(187,150,91,.4)"><span class="hl">90°</span>　欲しいものと動き方が<br>かみ合いにくい</div>', T.s(2) + 1]], T.a + .6, T.b)] },
    { text: '蠍座の金星は、深く、静かに、関係を守りたい。獅子座の火星は、堂々と、表に出して動きたい。どちらも譲りにくいサイン同士なので、自分の中で引っ張り合いが起きやすいんですね。', pad: 1.8,
      cues: T => [S('elem', T.a, T.b, { texts: [
        tx('<div class="a"><span class="g gd">♀</span> 蠍座の金星</div><div class="gd" style="font-size:26px;margin-top:6px">水のサイン ・ 不動宮</div><div class="m" style="margin-top:26px">深く、静かに、<br>関係を守りたい</div>', T.s(0) - .2, T.b + .4, 'left:120px;top:150px', 'el'),
        tx('<div class="a"><span class="g gd">♂</span> 獅子座の火星</div><div class="gd" style="font-size:26px;margin-top:6px">火のサイン ・ 不動宮</div><div class="m" style="margin-top:26px">堂々と、表に出して<br>動きたい</div>', T.s(1) - .2, T.b + .4, 'left:1080px;top:150px', 'el'),
        tx('<div class="m">譲りにくいサイン同士 ─ 自分の中の引っ張り合い</div>', T.s(2), T.b + .4, 'left:0;right:0;top:838px;text-align:center;padding:14px 0 18px;background:linear-gradient(90deg,rgba(14,11,24,0),rgba(14,11,24,.82) 25%,rgba(14,11,24,.82) 75%,rgba(14,11,24,0))')] })] },
    { text: 'さらに、支配星をたどってみます。天秤座の太陽と月の支配星は、金星。蠍座にある金星の支配星は、火星。獅子座にある火星の支配星は、太陽。そして太陽は天秤座にいるので、また金星へ戻ってきます。', pad: 2.4,
      cues: T => {
        const T10 = T.u(1), st = [T.s(1), T.s(2), T.s(3)];
        return [cam(T.a - .8, 'home', .1), halo(['sun', 'moon'], st[0], T10.b), halo(['venus'], st[0] + .8, T10.b), halo(['mars'], st[1] + .8, T10.b),
          seg([6], st[0], T10.b, { v: .6 }), seg([7], st[1], T10.b, { v: .6 }), seg([4], st[2], T10.b, { v: .6 }),
          panel('支配星の輪', [['<div class="mid">輪の中で <span class="g hl">♀ □ ♂</span> <b class="hl">0°12′</b></div><div class="sub">ここが、今回の新月の中心</div>', T10.s(2) - .2]], T.s(0) + .3, T10.b, {
            titleAt: t => t < T10.s(2) ? '支配星の輪' : '今回の新月の中心',
            build(pn) {
              const ls = svgEl('svg', { width: 610, height: 470, viewBox: '0 0 610 470' }); pn.insertBefore(ls, pn.children[1]);
              ls.innerHTML = `<defs><marker id="ah2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#BB965B"/></marker></defs>`;
              const N = { a: [305, 110, '☉☽', '天秤座 17°21′'], b: [505, 340, '♀', '蠍座 7°25′R'], c: [105, 340, '♂', '獅子座 7°13′'] }, ne = {};
              for (const k in N) {
                const [x, y, gl, lab] = N[k], gg = svgEl('g', { opacity: 0 }, ls);
                svgEl('circle', { cx: x, cy: y, r: 46, fill: '#1b1428', stroke: '#BB965B', 'stroke-width': 2 }, gg);
                const gt = svgEl('text', { x, y, 'text-anchor': 'middle', 'dominant-baseline': 'central', class: 'glyph', fill: '#FAF8F4' }, gg); gt.style.fontSize = gl.length > 1 ? '30px' : '38px'; gt.textContent = gl;
                const st2 = svgEl('text', { x, y: k === 'a' ? y - 68 : y + 74, 'text-anchor': 'middle', class: 'deg-label' }, gg); st2.style.fontSize = '24px'; st2.textContent = lab;
                ne[k] = gg;
              }
              const A = [['a', 'b', '天秤座の支配星'], ['b', 'c', '蠍座の支配星'], ['c', 'a', '獅子座の支配星']].map(([p, q, lab]) => {
                const P = N[p], Q = N[q], dx = Q[0] - P[0], dy = Q[1] - P[1], d = Math.hypot(dx, dy), ux = dx / d, uy = dy / d, bend = -100;
                const a = [P[0] + ux * 58, P[1] + uy * 58], b = [Q[0] - ux * 58, Q[1] - uy * 58], cx = (a[0] + b[0]) / 2 - uy * bend, cy = (a[1] + b[1]) / 2 + ux * bend;
                const dd = `M${a[0]},${a[1]} Q${cx},${cy} ${b[0]},${b[1]}`;
                const pth = svgEl('path', { d: dd, fill: 'none', stroke: '#BB965B', 'stroke-width': 3, 'marker-end': 'url(#ah2)' }, ls); drawable(pth);
                const fl = svgEl('path', { d: dd, fill: 'none', stroke: '#FAF8F4', 'stroke-width': 3, 'stroke-dasharray': '3 20', opacity: 0 }, ls);
                const t2 = svgEl('text', { x: (a[0] + b[0]) / 2 - uy * bend * .55, y: (a[1] + b[1]) / 2 + ux * bend * .55, 'text-anchor': 'middle', 'dominant-baseline': 'central', class: 'deg-label', opacity: 0 }, ls);
                t2.style.fontSize = '22px'; t2.style.fill = '#BB965B'; t2.textContent = lab;
                return { pth, fl, t2 };
              });
              const sq = svgEl('line', { x1: 447, y1: 340, x2: 163, y2: 340, stroke: '#BB965B', 'stroke-width': 4 }, ls); drawable(sq);
              const sqt = svgEl('text', { x: 305, y: 318, 'text-anchor': 'middle', class: 'deg-label', opacity: 0 }, ls); sqt.style.fontSize = '28px'; sqt.textContent = '□ 0°12′';
              return { ne, A, sq, sqt };
            }, frame(t, c) {
              const non = { a: st[0] - .4, b: st[0] + .8, c: st[1] + .8 };
              for (const k in non) c.ne[k].setAttribute('opacity', ease(prog(t, non[k], .6)));
              c.A.forEach((w, i) => { draw(w.pth, ease(prog(t, st[i] + .4, 1.4))); w.t2.setAttribute('opacity', ease(prog(t, st[i] + 1.2, .6)));
                w.fl.setAttribute('opacity', win(t, T.s(4), T10.b, .8, .5) * .9); w.fl.style.strokeDashoffset = (-t * 36).toFixed(1); });
              draw(c.sq, ease(prog(t, T10.s(1) + .3, 1.2))); c.sqt.setAttribute('opacity', ease(prog(t, T10.s(1) + 1.2, .6)));
            } })];
      } },
    { text: '太陽、金星、火星が、ひとつの輪でつながっているんですね。その輪の中で、金星と火星が、12分のスクエアを作っている。ここが、今回の新月の中心だと私は考えています。', pad: 2.0,
      cues: T => [text(sqMid, '□ 0°12′', T.s(1), T.b, { fs: 28 })] },
    { text: '例えば、身近な人から、今週もまた頼みごとをされたとき。関係を大切にしたいから、「大丈夫だよ」と引き受ける。でも本当は、自分の時間がほしい。その気持ちを飲み込み続けると、ある日、思っていたより強い言い方で出てしまう。', pad: 2.0,
      cues: T => {
        const U12 = T.u(1), U13 = T.u(2), tp1 = T.s(1) + .8, harsh = 'もう無理。';
        return [S('phone', T.a, U13.b, {
          msgs: [{ side: 'in', text: '今週の土曜も、<br>お願いできる？', at: T.s(0) + .6, top: 0 }, { side: 'out', text: '大丈夫だよ', at: tp1 + 1.2, top: 96 },
                 { side: 'in', text: '来週もいい？', at: T.s(3) + .4, top: 176 }, { side: 'out', text: '今週は難しいけれど、<br>来週の日曜なら行けるよ', at: U13.s(1) + 4.8, top: 272 }],
          typing: [{ a: tp1, b: tp1 + 1.2, text: '大丈夫だよ', cps: 6 }, { a: T.s(3) + 2.6, b: U12.a + 1.8, text: harsh, cps: 7, bold: true },
                   { a: U12.a + 1.8, b: U13.s(1), text: harsh, erase: true, cps: 3, bold: true }, { a: U13.s(1), b: U13.s(1) + 4.6, text: '今週は難しいけれど、来週の日曜なら行けるよ', cps: 5 }],
          tags: [{ glyph: '♀', head: '金星', body: '関係を大切にしたい', a: T.s(1) + .4, b: T.b, top: 170 }, { glyph: '♂', head: '火星', body: '本当は、自分の時間がほしい', a: T.s(2), b: T.b, top: 330 },
                 { glyph: '□', head: 'スクエア', body: '飲み込んだ気持ちが、強く出る', a: T.s(3) + 2.2, b: T.b, top: 490 },
                 { glyph: '♀', head: '金星　逆行中', body: 'これまでの関係を、見直す', a: U12.a + .3, b: U12.b, top: 170 },
                 { glyph: '♂', head: '火星', body: 'はっきり、でも穏やかに', a: U13.a + .3, b: U13.b, top: 330 },
                 { glyph: '♀♂', head: '結び直す', body: '断ることと、大切にすることは<br>両立できる', a: U13.s(2), b: U13.b, top: 490 }],
          memo: { title: '守りたいもの', line: '土曜の午前は、自分の時間', a: U12.s(1) - .2, b: U13.b, top: 640 } })];
      } },
    { text: '金星が逆行している間は、新しく何かを始めるより、これまでの関係の中で、自分が何を大切にしてきたかを見直すことに向いています。言葉にする前に、守りたいものを一つ確かめる。', pad: 1.6 },
    { text: 'それから、火星の力で、はっきり、でも穏やかに伝えてみる。「今週は難しいけれど、来週の日曜なら行けるよ」。断ることと、関係を大切にすることは、両立できます。', pad: 2.4 },
    { text: '支配星の金星が逆行し、火星とスクエア。今回の新月は、関係を大切にする気持ちと、自分の動き方を、結び直すところから始まります。', pad: 2.4,
      cues: T => [cam(T.a - .8, 'home', .1), halo(['venus', 'mars'], T.a, T.b), text(sqMid, '□ 0°12′', T.a, T.b, { fs: 28 }),
        panel('まとめ', [
          [`<div class="mid">新月の支配星　${g('♀')} 金星<br><span class="sub">蠍座7°25′・逆行中</span></div>`, T.a + .6],
          [`<div class="mid">${g('♀ □ ♂')}　オーブ 0°12′<span class="sub">（接近）</span></div>`, T.a + 1.6],
          ['<div class="mid">太陽 → 金星 → 火星 → 太陽</div>', T.a + 2.6],
          ['<div class="mid"><span class="hl">関係を大切にする気持ち</span>と<br><span class="hl">自分の動き方</span>を、結び直す</div>', T.s(1)]], T.a + .4, T.b)] },
  ]);

  /* ======================= 07 東京図の補足 ======================= */
  ch('07', '東京図の補足：火星とMC・IC', [
    { text: 'ここで、東京図だけの補足をします。場所によって変わる、MCとICの話です。', pad: 1.4,
      cues: T => [cam(T.a, 'home', 1.6), line({ key: 'mc', r: R.out + 28 }, { key: 'ic', r: R.out + 28 }, T.s(1), T.u(4).b, { w: 3, draw: 1.6 })] },
    { text: 'MC、図のいちばん上の点は、牡牛座8度55分。その真向かいのICは、蠍座8度55分です。先ほどの金星は、このICと1度29分の近さにあります。そして火星は、MCと約90度で、オーブは1度41分です。', pad: 2.4,
      cues: T => [co(cb('MC', '牡牛座 8°55′'), { key: 'mc', r: R.out + 28 }, 1150, 150, T.s(0) + .3, T.b), co(cb('IC', '蠍座 8°55′'), { key: 'ic', r: R.out + 28 }, 1150, 760, T.s(1) + .3, T.b),
        halo(['venus'], T.s(2), T.u(2).b), arcO(VN, C4, T.s(2) + .5, T.b, '1°29′'),
        halo(['mars'], T.s(3), T.u(2).b), line('mars', 'mc', T.s(3) + .4, T.u(2).b, { color: 'white', w: 3 }),
        arc(70, L('mc'), L('mars'), T.at(3, .5), T.b, { label: '88°18′', lr: 22, fs: 24 }), text({ lon: 83, r: 150 }, 'オーブ 1°41′', T.at(3, .8), T.b, { fs: 24, color: 'gold' })] },
    { text: '金星と火星のスクエアに、MCとICの軸が重なると、火星を頂点にした、Tの字のような形が見えます。Tスクエアと呼ばれる形です。', pad: 2.4,
      cues: T => [line('venus', 'mars', T.a, T.u(2).b, { w: 4 }), line('venus', 'mc', T.a + 1.2, T.u(2).b, { w: 4 }), line('mars', 'mc', T.a + 2.4, T.u(2).b, { w: 4 }),
        poly(['venus', 'mars', 'mc'], T.s(1), T.u(2).b, { v: .16 }), co(cb('Tスクエア', '火星が頂点'), { g: 'mars' }, 48, 150, T.s(1) + .2, T.u(2).b)] },
    { text: 'MCは、社会での役割や、外から見える立場。ICは、家庭や、自分の土台。火星は、第12ハウスにあります。人目につきにくい場所で、力をためている火星とも読めます。', pad: 1.8,
      cues: T => [house(12, T.s(2), T.b, { v: .6 }), panel('軸と第12ハウス', [
          [`<div class="mid">${ICO.work}MC　社会での役割・外から見える立場</div>`, T.s(0)],
          [`<div class="mid">${ICO.home}IC　家庭・自分の土台</div>`, T.s(1)],
          [`<div class="mid">${ICO.hidden}火星　第12ハウス</div><div class="sub">人目につきにくい場所で、力をためる</div>`, T.s(2)]], T.a + .2, T.b)] },
    { text: 'ここから、仕事や外での役割と、家庭や自分の休む場所の間で、動き方を調整する必要が出てくる、という読みができます。', pad: 1.4,
      cues: T => [line('venus', 'mars', T.a - .6, T.b, { w: 4, draw: .01 }), line('venus', 'mc', T.a - .6, T.b, { w: 4, draw: .01 }), line('mars', 'mc', T.a - .6, T.b, { w: 4, draw: .01 }), halo(['mars'], T.a, T.b),
        panel('動き方を調整する', [[`<div class="mid">${ICO.work}仕事・外での役割</div>`, T.a + .3], ['<div class="big hl" style="text-align:center;width:420px">⇅</div>', T.a + .8], [`<div class="mid">${ICO.home}家庭・休む場所</div>`, T.a + 1.2]], T.a, T.b)] },
    { text: 'ただ、これはMCとICが関わる話なので、東京で見た図としての補足です。金星と火星のスクエアそのものは、どこから見ても同じです。この区別は、分けておきたいと思います。', pad: 2.0,
      cues: T => [S('charts', T.a, T.b, { noMask: true,
        charts: [{ id: 'c7T', data: 'nm', home: { fx: 0, fy: 0, s: .56, sx: 500, sy: 560 } }, { id: 'c7L', data: 'nmLondon', home: { fx: 0, fy: 0, s: .56, sx: 1420, sy: 560 } }],
        texts: [tx('<div class="m">東京　MC 牡牛座8°55′</div>', T.a + .3, T.b, 'left:200px;top:180px;width:600px;text-align:center'),
                tx('<div class="m">ロンドン　MC 射手座17°43′</div>', T.a + .6, T.b, 'left:1120px;top:180px;width:600px;text-align:center'),
                tx('Tスクエアは東京図だけ', T.at(0, .5), T.s(1), 'left:0;right:0;top:872px;text-align:center', 'gd'),
                tx('金星□火星 0°12′ はどこでも同じ', T.s(1) + .4, T.b, 'left:0;right:0;top:872px;text-align:center', 'gd')] }),
        ...on('c7T', [line({ key: 'mc', r: R.signIn }, { key: 'ic', r: R.signIn }, T.a + .6, T.b, { w: 6 }), poly(['venus', 'mars', 'mc'], T.a + 1, T.s(1), { v: .2 })]),
        ...on('c7L', [line({ key: 'mc', r: R.signIn }, { key: 'ic', r: R.signIn }, T.a + .9, T.b, { w: 6 })]),
        ...['c7T', 'c7L'].flatMap(id => on(id, [halo(['venus', 'mars'], T.s(1), T.b), line('venus', 'mars', T.s(1) + .2, T.b, { w: 6 })]))] },
  ]);

  /* ======================= 08 外惑星の小三角 ======================= */
  const midOf = (a, b, off = 0) => { const p = NM.pt(L(a), R.asp), q = NM.pt(L(b), R.asp), mx = (p[0] + q[0]) / 2, my = (p[1] + q[1]) / 2, d = Math.hypot(mx, my) || 1; return [mx - mx / d * off, my - my / d * off]; };
  const WIDE = { fx: 0, fy: 0, s: .9, sx: 760, sy: 510 };
  ch('08', '満月から続く、外惑星の小三角', [
    { text: '今度は、チャートを少し引いて、ゆっくり動く三つの天体を見ます。牡羊座2度35分の海王星、双子座5度19分の天王星、水瓶座3度04分の冥王星です。', pad: 1.6,
      cues: T => [cam(T.a, WIDE, 1.6), halo(['neptune'], T.at(1, .05), T.u(2).b), halo(['uranus'], T.at(1, .38), T.u(2).b), halo(['pluto'], T.at(1, .7), T.u(2).b),
        panel('ゆっくり動く三つの天体', [[`<div class="mid">${g('♆')} 海王星　牡羊座 2°35′</div>`, T.at(1, .05)], [`<div class="mid">${g('♅')} 天王星　双子座 5°19′</div>`, T.at(1, .38)], [`<div class="mid">${g('♇')} 冥王星　水瓶座 3°04′</div>`, T.at(1, .7)]], T.s(1) - .3, T.b)] },
    { text: '海王星と冥王星は約60度で、オーブは28分。天王星と冥王星は約120度で、オーブ2度15分。天王星と海王星は約60度で、オーブ2度43分。三辺とも3度以内です。', pad: 2.4,
      cues: T => [line('neptune', 'pluto', T.s(0) + .3, T.u(1).b, { color: 'white', w: 3 }), text(midOf('neptune', 'pluto', -40), '✶ 0°28′', T.s(0) + 1.4, T.u(1).b, { fs: 26 }),
        line('uranus', 'pluto', T.s(1) + .3, T.u(1).b, { w: 4 }), text(midOf('uranus', 'pluto', 30), '△ 2°15′', T.s(1) + 1.4, T.u(1).b, { fs: 26, color: 'gold' }),
        line('uranus', 'neptune', T.s(2) + .3, T.u(1).b, { color: 'white', w: 3 }), text(midOf('uranus', 'neptune', -40), '✶ 2°43′', T.s(2) + 1.4, T.u(1).b, { fs: 26 }),
        panel('三辺のオーブ', [[`<div class="mid">${g('♆✶♇')} 60°　オーブ 0°28′</div>`, T.s(0) + .6], [`<div class="mid">${g('♅△♇')} 120°　オーブ 2°15′</div>`, T.s(1) + .6], [`<div class="mid">${g('♅✶♆')} 60°　オーブ 2°43′</div>`, T.s(2) + .6], ['<div class="mid hl">三辺とも 3° 以内</div>', T.s(3)]], T.a, T.b)] },
    { text: '120度の両端から、それぞれ60度で結ばれる天体がある。この三角形を、小三角と呼ぶことがあります。', pad: 1.8,
      cues: T => [line('uranus', 'pluto', T.a, T.a + 3, { w: 4, draw: .01, glow: [T.a, T.a + 2.6] }), poly(['neptune', 'uranus', 'pluto'], T.s(0) + 1.4, T.b, { v: .2 }),
        panel('小三角', [['<div class="mid">120°の両端（天王星・冥王星）</div>', T.a + .3], ['<div class="mid">から60°で結ばれる海王星</div>', T.at(0, .5)], ['<div class="big hl">＝ 小三角</div>', T.s(1) + .3]], T.a, T.b)] },
    { text: '実は前回の満月でも、この三つの天体は、ほぼ同じ形を作っていました。そして前回は、天秤座3度37分の太陽と、牡羊座3度37分の月が、この構造に加わって、カイトという形になっていました。', pad: 2.8,
      cues: T => [S('charts', T.a, T.b, { noMask: true, charts: [{ id: 'c8F', data: 'fm', home: WIDE }], texts: [tx('<div class="m">前回　9月27日の満月</div>', T.a + .3, T.b, 'left:1240px;top:150px')] }),
        ...on('c8F', [line('neptune', 'pluto', T.s(0) + .5, T.b, { color: 'white', w: 2.5 }), line('uranus', 'pluto', T.s(0) + 1.1, T.b, { color: 'white', w: 2.5 }), line('uranus', 'neptune', T.s(0) + 1.7, T.b, { color: 'white', w: 2.5 }),
          halo(['sun'], T.at(1, .15), T.b), line('sun', 'uranus', T.at(1, .2), T.b, { w: 4 }), line('sun', 'pluto', T.at(1, .3), T.b, { w: 4 }),
          co(cb('グランドトライン', '太陽・天王星・冥王星'), { g: 'sun' }, 48, 640, T.at(1, .35), T.at(1, .62)),
          halo(['moon'], T.at(1, .5), T.b), line('moon', 'sun', T.at(1, .55), T.b, { w: 4 }), line('moon', 'uranus', T.at(1, .62), T.b, { color: 'white', w: 3 }), line('moon', 'pluto', T.at(1, .68), T.b, { color: 'white', w: 3 }),
          poly(['moon', 'uranus', 'sun', 'pluto'], T.at(1, .78), T.b, { v: .16 }), co(cb('月が加わると', 'カイト'), { g: 'moon' }, 1240, 260, T.at(1, .8), T.b)])] },
    { text: '今回の太陽と月は、天秤座17度台です。この外惑星の三角形とは、度数が離れています。つまり、今回の新月は、前回の満月ほど、この長い背景と直接結びついてはいない、と読めます。', pad: 1.8,
      cues: T => [cam(T.a - .6, 'home', .1), line('neptune', 'pluto', T.a - .6, T.b, { color: 'white', w: 2, draw: .01, op: .5 }), line('uranus', 'pluto', T.a - .6, T.b, { color: 'white', w: 2, draw: .01, op: .5 }), line('uranus', 'neptune', T.a - .6, T.b, { color: 'white', w: 2, draw: .01, op: .5 }),
        halo(['sun', 'moon'], T.a, T.b), tick(183, T.s(1), T.b, { v: .5 }), text({ lon: 183.6, r: R.signIn + 44 }, '前回の太陽 3°37′', T.s(1), T.b, { fs: 22, color: 'gold' }),
        arcO(183.62, L('sun'), T.s(1) + .8, T.b, '約14°'),
        co(cb('今回の太陽・月', '天秤座 17°21′', '三角形（2〜5°）から離れている'), { g: 'sun' }, 48, 150, T.s(0) + .3, T.b)] },
    { text: 'ここは、とても大事な違いです。天王星、海王星、冥王星の関係は、何年もかけてゆっくり続く背景です。前回の満月は、その背景に太陽と月が直接触れていた。今回は、背景は続いているけれど、新月そのものの焦点は、金星と火星の、もっと身近な関係のほうにある。', pad: 1.8,
      cues: T => [S('bars', T.a, T.b, { bars: [
          { label: '天王星・海王星・冥王星の関係', sub: '何年もかけて続く背景', w: 1200, at: T.s(1) },
          { label: '金星の逆行', sub: '10/3〜11/14（約6週間）', w: 330, at: T.s(3) },
          { label: '新月の瞬間', sub: '10/11 0:50', w: 26, at: T.s(3) + 1.2, pulse: true, color: '#f3d9a4' }], texts: [
          tx('長さのイメージ（縮尺は正確ではありません）', T.a + .3, T.b, 'left:420px;top:150px', 's'),
          tx('満月：背景に直接触れていた', T.s(2), T.s(3), 'left:420px;top:880px', 'gd'),
          tx('新月：焦点は金星と火星の身近な関係', T.s(3) + 1.8, T.b, 'left:420px;top:880px', 'gd')] })] },
    { text: '大きな流れを感じ取ることも大切ですが、今回の新月では、その大きな話より、目の前の関係と、自分の動き方に焦点を合わせてみてください。', pad: 1.8,
      cues: T => [cam(T.a - .6, 'home', .1), cam(T.a + .6, VM, 2.2), line('uranus', 'pluto', T.a - .6, T.a + 2.5, { color: 'white', w: 2, draw: .01, op: .4 }),
        halo(['venus', 'mars'], T.a + 1, T.b), line('venus', 'mars', T.a + 1.2, T.b, { w: 4, glow: [T.a + 2, T.b] }),
        co(cb('目の前の関係と、自分の動き方', '♀ □ ♂  0°12′'), { g: 'mars' }, 48, 150, T.a + 2.2, T.b)] },
  ]);

  /* ======================= 09 ASCと木星 ======================= */
  const ASCV = { fx: -250, fy: 40, s: 1.4, sx: 760, sy: 520 };
  ch('09', 'ASCと木星', [
    { text: '次は、ASCの近くを見てみます。', pad: 1.0,
      cues: T => [cam(T.a, ASCV, 2), line({ key: 'asc', r: R.signIn }, { key: 'asc', r: R.out + 28 }, T.a + .6, T.u(1).b, { w: 5 })] },
    { text: '獅子座の木星は、21度15分にあります。第1ハウスの中で、ASCからは5度15分離れています。今回の基準では、ASCとの合として数えるには少し広いので、第1ハウスの木星として見ていきます。', pad: 2.2,
      cues: T => [halo(['jupiter'], T.a, T.b), co(cb('♃ 木星', '獅子座 21°15′', '第1ハウス'), { g: 'jupiter' }, 1250, 640, T.a + .3, T.b),
        arcO(L('asc'), L('jupiter'), T.s(1), T.b, '5°15′'),
        wedge(R.signIn - 70, R.signIn - 14, L('asc'), L('asc') + 5, T.at(1, .7), T.b, { v: .5, fill: 'rgba(187,150,91,.25)', stroke: 'gold' }),
        text({ lon: L('asc') + 2.5, r: R.signIn - 90 }, '5°', T.at(1, .75), T.b, { fs: 22, color: 'gold' }), house(1, T.s(2), T.b, { v: .5 }),
        co(cb('ASCとの合には広い', '第1ハウスの木星として読む'), null, 1250, 150, T.s(2), T.b)] },
    { text: 'そして、新月の太陽と月は、この木星とも約60度で結ばれています。実際の角度差は56度6分で、オーブは3度53分。今回の基準では、3度から5度の補足にあたります。ただ、この角度は接近中で、これから正確になっていく方向です。', pad: 2.2,
      cues: T => [cam(T.a, 'home', 1.8), halo(['sun', 'moon', 'jupiter'], T.a, T.b), line('jupiter', 'sun', T.s(0) + .8, T.b, { color: 'white', dash: '10 8', w: 3 }),
        arc(78, L('jupiter'), L('sun'), T.s(1), T.b, { label: '56°06′', lr: 20 }),
        Object.assign(panel('補足の角度', [['<div class="mid">60° との差　オーブ <b class="hl">3°53′</b></div>', T.s(1) + .4], ['<div class="mid">3〜5° ＝ 補足</div>', T.s(2)], ['<div class="mid hl">接近中：これから正確になる</div>', T.s(3)]], T.a + .6, T.b), orbScale(6, 3 + 53 / 60, '3°53′', T.s(1) + 1.2))] },
    { text: '木星は、広げる、育てる、信頼する働きとして読む天体です。獅子座は、自分らしさを表現し、心から楽しむことを大切にするサインです。', pad: 1.8,
      cues: T => [S('hearth', T.a, T.b, { texts: [
        tx(`<span class="g gd">♃</span> 木星<div class="m" style="margin-top:10px">広げる・育てる・信頼する</div>`, T.s(0), T.b, 'left:120px;top:200px', 'm'),
        tx(`<span class="g gd">♌</span> 獅子座<div class="m" style="margin-top:10px">自分らしさを表現する・心から楽しむ</div>`, T.s(1), T.b, 'left:120px;top:460px', 'm')] })] },
    { text: '先ほどの火星も獅子座でした。獅子座にある火星と木星。そしてチャート全体の支配星も、獅子座の支配星である太陽です。この図は、獅子座の「自分らしく表現する」テーマが、何度も出てきます。', pad: 1.8,
      cues: T => [cam(T.a - .6, 'home', .1), seg([4], T.a, T.b, { v: .9 }), halo(['mars'], T.s(0), T.b), halo(['jupiter'], T.s(1), T.b),
        line({ key: 'asc', r: R.asp }, { g: 'sun' }, T.s(2) + .3, T.b, { curve: .45, arrow: true }), halo(['sun'], T.s(2) + 1, T.b),
        panel('獅子座が何度も出てくる', [[`<div class="mid">${g('♂')} 獅子座の火星</div>`, T.s(0)], [`<div class="mid">${g('♃')} 獅子座の木星</div>`, T.s(1)], [`<div class="mid">ASC 獅子座 → 支配星 ${g('☉')} 太陽</div>`, T.s(2) + .3], ['<div class="mid hl">＝ 自分らしく表現する</div>', T.s(3)]], T.a + .2, T.b)] },
    { text: '関係を大切にするために、自分を消す必要はない。むしろ、自分らしくいることが、関係を育てる力になる。木星とのセクスタイルは補足の角度ですが、そういう方向を後押ししてくれる配置として読めます。', pad: 1.6,
      cues: T => [S('talk', T.a, T.b, { warm: true, texts: [tx('自分を消さなくていい', T.s(0) + .4, T.b, 'left:120px;top:150px', 'm'), tx('自分らしさが、関係を育てる', T.s(1) + .3, T.b, 'left:120px;top:222px', 'gd')] })] },
  ]);

  /* ======================= 10 土星との距離と補足 ======================= */
  const OPP = (L('sun') + 180) % 360;
  ch('10', '土星との距離と、補足のアスペクト', [
    { text: 'ここで、あえて取り上げない配置についても、お話ししておきます。', pad: 1.0,
      cues: T => [cam(T.a, 'home', 1.6), halo(['saturn'], T.a + 1, T.u(1).b)] },
    { text: '牡羊座には土星があります。10度49分です。天秤座の新月の、ちょうど向かい側のサインですね。でも、新月の17度21分とは、6度32分離れています。今回は3度以内を中心、5度までを補足としているので、土星とのオポジションとしては扱いません。', pad: 2.4,
      cues: T => [co(cb('♄ 土星', '牡羊座 10°49′ R'), { g: 'saturn' }, 1250, 150, T.s(0), T.s(4)), seg([0, 6], T.s(2), T.b, { v: .6 }), halo(['sun', 'moon'], T.s(2), T.b),
        line('sun', { lon: OPP, r: R.asp }, T.s(3), T.b, { color: 'white', dash: '10 8', w: 3 }), tick(OPP - .5, T.s(3) + .4, T.b, { v: .7 }),
        text({ lon: OPP, r: R.signIn + 44 }, '新月の真向かい 17°21′', T.s(3) + .6, T.b, { fs: 20, color: 'gold' }),
        arcO(L('saturn'), OPP, T.at(3, .5), T.b, '6°32′'),
        Object.assign(panel('オーブの基準', [['<div class="mid">180° からのずれ　<b class="hl">6°32′</b></div>', T.s(4)], ['<div class="mid">5° の外 → オポジションとして扱わない</div>', T.at(4, .5)]], T.s(4) - .2, T.b), orbScale(7, 6 + 32 / 60, '6°32′', T.s(4) + .6))] },
    { text: '前回の満月で、月と土星の距離が8度17分だったときにも、同じようにお話ししました。同じサインや向かい側のサインにあるからといって、角度があると決めない。度数で確かめてから、優先順位をつけます。', pad: 1.8,
      cues: T => [S('charts', T.a, T.b, { noMask: true, charts: [{ id: 'c10F', data: 'fm', home: { fx: 200, fy: -230, s: 1.45, sx: 640, sy: 600 } }], texts: [
          tx('<div class="m">前回　9月27日の満月</div>', T.a + .3, T.b, 'left:1240px;top:150px'),
          tx('同じサイン ＝ 角度がある、とは限らない', T.s(1), T.b, 'left:1240px;top:260px;width:620px', 'gd'),
          tx('度数で確かめて、優先順位をつける', T.s(2), T.b, 'left:1240px;top:400px;width:620px')] }),
        ...on('c10F', [halo(['moon', 'saturn', 'neptune'], T.a + .6, T.b), arcO(3.62, 11.91, T.s(0) + 1, T.b, '8°17′')])] },
    { text: '一方で、補足として見ておきたい角度もあります。金星と冥王星は約90度で、オーブ4度20分。前回の満月では4度31分だったので、少し近づいています。火星と土星は約120度で3度35分。火星と冥王星は約180度で4度8分です。', pad: 2.2,
      cues: T => [cam(T.a - .6, 'home', .1), halo(['venus', 'pluto'], T.s(1), T.u(1).b), line('venus', 'pluto', T.s(1) + .3, T.u(1).b, { color: 'white', dash: '10 8', w: 2.5 }),
        halo(['mars', 'saturn'], T.s(3), T.u(1).b), line('mars', 'saturn', T.s(3) + .3, T.u(1).b, { color: 'white', dash: '10 8', w: 2.5 }),
        line('mars', 'pluto', T.s(4) + .3, T.u(1).b, { color: 'white', dash: '4 8', w: 2 }),
        panel('補足の角度（3〜5°）', [
          [`<div class="mid">${g('♀□♇')} 90°　オーブ 4°20′</div>`, T.s(1) + .3],
          ['<div class="sub">前回 4°31′ → 今回 4°20′（少し近づく）</div><div style="position:relative;height:30px;margin-top:6px"><div style="position:absolute;left:0;top:4px;height:8px;width:301px;background:rgba(250,248,244,.35)"></div><div style="position:absolute;left:0;top:16px;height:8px;width:289px;background:#BB965B"></div></div>', T.s(2)],
          [`<div class="mid">${g('♂△♄')} 120°　オーブ 3°35′</div>`, T.s(3) + .3],
          [`<div class="mid">${g('♂☍♇')} 180°　オーブ 4°08′</div>`, T.s(4) + .3]], T.s(0) + .4, T.b)] },
    { text: '金星と冥王星は、前回もお話ししたように、大切にしたい関係に、どれくらい強く関わろうとしているかを見る補助線にします。火星と土星のトラインは、勢いだけでなく、時間をかけて形にする力として読めます。', pad: 1.6,
      cues: T => [line('venus', 'pluto', T.s(0), T.s(1), { w: 5, draw: .6, glow: [T.s(0), T.s(1)] }), line('mars', 'saturn', T.s(1), T.b, { w: 5, draw: .6, glow: [T.s(1), T.b] }),
        panel('補足の読み方', [[`<div class="mid">${g('♀□♇')} 大切な関係に、どれくらい強く関わるか</div>`, T.s(0) + .3], [`<div class="mid">${g('♂△♄')} 勢いだけでなく、時間をかけて形にする</div>`, T.s(1) + .3]], T.a, T.b)] },
    { text: 'それから、冥王星は10月16日に順行に戻ります。ゆっくり動く天体なので、これで何かが急に変わるわけではありませんが、新月から数日のうちに、止まって見えていた冥王星が向きを変える、ということも、背景として知っておいてください。', pad: 1.6,
      cues: T => [S('timeline', T.a, T.b, { from: 10, to: 27,
        ticks: [10, 15, 20, 25].map(d => ({ v: d, label: `10/${d}` })),
        events: [{ v: 11.03, label: '10/11 新月', at: T.a + .4 }, { v: 16, label: '10/16', sub: '冥王星 順行へ', at: T.s(0) + .8, hlA: T.s(0) + .8, below: true }],
        texts: [tx('ゆっくり動く天体：急な変化ではなく、背景', T.s(1) + .4, T.b, 'left:200px;top:760px', 'gd')] })] },
  ]);

  /* ======================= 11 サビアン ======================= */
  ch('11', 'サビアン：天秤座18度と蠍座8度', [
    { text: 'ここまで、度数と角度から読んできました。次は、サビアンシンボルという、度数ごとのイメージから見てみます。', pad: 1.2,
      cues: T => [cam(T.a, { focus: ['sun', 'moon'], s: 1.5, sx: 760, sy: 560 }, 2), halo(['sun', 'moon'], T.a + .6, T.u(1).b)] },
    { text: 'サビアンは、黄道の一度ごとに対応するイメージを使う方法です。今回の太陽と月は天秤座17度21分。0度台を1度と数えるので、読むのは天秤座18度です。前回と同じく、四捨五入ではありません。', pad: 2.2,
      cues: T => [cam(T.a, { fx: -170, fy: 300, s: 2.3, sx: 620, sy: 330 }, 2), tick(197, T.s(1), T.b, { v: 1 }),
        panel('数え度数', [['<div class="sub">前回：3°37′ → 牡羊座・天秤座の 4度</div>', T.s(3)]], T.a + .4, T.b, {
          build(pn) {
            const s = svgEl('svg', { width: 600, height: 250, viewBox: '0 0 600 250' }); pn.insertBefore(s, pn.children[1]);
            const X = d => 40 + (d - 15) / 5 * 520;
            for (let d = 15; d < 20; d++) {
              const r = svgEl('rect', { x: X(d) + 2, y: 60, width: 520 / 5 - 4, height: 70, fill: 'rgba(250,248,244,.06)', stroke: 'rgba(187,150,91,.5)' }, s); r.dataset.d = d;
              const t = svgEl('text', { x: X(d + .5), y: 102, 'text-anchor': 'middle', class: 'deg-label' }, s); t.style.fontSize = '24px'; t.textContent = `${d + 1}度`;
              const u = svgEl('text', { x: X(d), y: 160, 'text-anchor': 'middle', class: 'deg-label' }, s); u.style.fontSize = '18px'; u.textContent = `${d}°`;
            }
            const mk = svgEl('g', { opacity: 0 }, s);
            svgEl('path', { d: `M${X(17 + 21 / 60)},56 L${X(17 + 21 / 60) - 9},36 L${X(17 + 21 / 60) + 9},36 Z`, fill: '#FAF8F4' }, mk);
            const lt = svgEl('text', { x: X(17 + 21 / 60), y: 26, 'text-anchor': 'middle', class: 'deg-label' }, mk); lt.style.fontSize = '24px'; lt.textContent = '17°21′';
            const res = svgEl('text', { x: 300, y: 222, 'text-anchor': 'middle', class: 'deg-label', opacity: 0 }, s); res.style.fontSize = '30px'; res.style.fill = '#BB965B'; res.textContent = '17°台 → 天秤座18度';
            return { s, mk, res, rect: s.querySelectorAll('rect')[2] };
          }, frame(t, c) { c.mk.setAttribute('opacity', ease(prog(t, T.s(1) + .3, .6))); const on2 = t >= T.s(2) + .6; c.rect.setAttribute('fill', on2 ? 'rgba(187,150,91,.55)' : 'rgba(250,248,244,.06)'); c.res.setAttribute('opacity', ease(prog(t, T.s(2) + .8, .6))); } })] },
    { text: '天秤座18度は、「逮捕された二人の男」というシンボルです。', pad: 2.0,
      cues: T => [S('sabian', T.a, T.u(1).b, { kind: 'men', cx: 640, texts: [
        tx('<div class="gd" style="font-size:28px">天秤座18度</div><div class="h" style="margin-top:8px">「逮捕された二人の男」</div><div class="s" style="margin-top:10px">Two men placed under arrest</div>', T.a + .3, T.u(1).b, 'left:1080px;top:170px'),
        tx('予告ではなく、象徴', T.u(1).s(1), T.u(1).b, 'left:1080px;top:420px', 'm'),
        tx('キーワード　<span class="gd">CONSEQUENCE（結果）</span><div class="s">M.E.ジョーンズ</div>', T.u(1).s(2), T.u(1).b, 'left:1080px;top:510px'),
        tx('行動　→　結果　→　<span class="gd">説明する</span>', T.u(1).s(3), T.u(1).b, 'left:1080px;top:650px', 'm')] })] },
    { text: '少しどきっとする言葉ですよね。でも、これは誰かが実際に逮捕される、という予告ではありません。サビアンを体系化したマーク・エドモンド・ジョーンズは、この度数のキーワードを「コンシクエンス」、結果、としています。自分がしてきたことの結果を引き受けて、周りに対して説明する。そういう場面の象徴として読まれています。', pad: 1.6 },
    { text: 'ここで私が注目したいのは、「二人」という点です。前回の満月の月、牡羊座4度も、二人の恋人のシンボルでした。今回も二人。関係の中で、自分がしてきたことを、自分の言葉で説明する。天秤座らしい、関係のなかの責任の話です。', pad: 1.6,
      cues: T => [S('pair', T.a, T.b, { left: 'lovers', right: 'men', texts: [
        tx('<div class="gd" style="font-size:24px">前回　牡羊座4度</div><div class="m" style="font-size:30px">人目から離れた小道を歩く二人の恋人</div>', T.s(1), T.b, 'left:60px;top:150px;width:840px;text-align:center'),
        tx('<div class="gd" style="font-size:24px">今回　天秤座18度</div><div class="m" style="font-size:30px">逮捕された二人の男</div>', T.s(2), T.b, 'left:1020px;top:150px;width:840px;text-align:center'),
        tx('<div class="m">関係の中で、自分の言葉で説明する</div>', T.s(3), T.b, 'left:0;right:0;top:860px;text-align:center')] })] },
    { text: '例えば、「相手のためを思って黙っていた」ことも、関係に影響を与えている行動の一つです。言わなかったことにも、結果はある。それを責めるのではなく、「私はこうしてきた。これからはこうしたい」と、自分の行動として説明し直す。天秤座18度は、そういう誠実さを求める度数だと、私は受け取っています。', pad: 1.6,
      cues: T => [S('memo', T.a, T.b, { title: '言い直すメモ', titleA: T.a + .3, lines: [
        { text: '相手のためを思って、黙っていた', a: T.s(0) + .4, y: 290, cls: 'faded', d: 1.8 },
        { text: '→ 言わなかったことにも、結果はある', a: T.s(1), y: 370, cls: 'small', d: 1.6 },
        { text: '「私はこうしてきた。」', a: T.at(2, .35), y: 500, glyph: '♎', d: 1.4 },
        { text: '「これからは、こうしたい。」', a: T.at(2, .55), y: 580, d: 1.4 },
        { text: '責めるのではなく、説明し直す', a: T.s(3), y: 710, cls: 'small', d: 1.4 }] })] },
    { text: 'もう一つ、支配星の金星のサビアンも見ておきます。金星は蠍座7度25分なので、蠍座8度。', pad: 1.4,
      cues: T => [cam(T.a - .6, { fx: -40, fy: 320, s: 2.2, sx: 640, sy: 360 }, .1), halo(['venus'], T.a, T.b + .5), tick(217, T.s(1), T.b + .5, { v: 1 }),
        co(cb('♀ 金星', '蠍座 7°25′', '7°台 → 蠍座8度'), { g: 'venus' }, 1250, 170, T.s(1) + .3, T.b)] },
    { text: '「湖面を照らす月」というシンボルです。キーワードは「ラポール」、心が通い合うこと。', pad: 1.4,
      cues: T => [S('lake', T.a, T.u(1).b, { amp: [[T.a, 1.6], [T.u(1).s(1), 1.6], [T.u(1).s(1) + 3, .5]], texts: [
        tx('<div class="gd" style="font-size:26px">蠍座8度</div><div class="h" style="margin-top:6px">「湖面を照らす月」</div><div class="s" style="margin-top:8px">The moon shining across a lake</div>', T.a + .3, T.u(1).b, 'left:120px;top:150px'),
        tx('キーワード　<span class="gd">RAPPORT（ラポール）</span>　心が通い合う', T.s(1), T.u(1).b, 'left:124px;top:380px'),
        tx('水面が穏やかなほど、月はきれいに映る', T.u(1).s(1) + .6, T.u(1).b, 'left:124px;top:460px', 'gd')] })] },
    { text: '静かな湖に、月の光がまっすぐ映っている風景です。水面が穏やかなときほど、月はきれいに映ります。', pad: 1.8 },
    { text: '天秤座18度が、外に向かって説明する場面なら、蠍座8度は、言葉にしなくても通じ合う、静かな場面です。私はこの二つを、どちらか一方ではなく、組み合わせて読みたいと思います。', pad: 1.6,
      cues: T => [S('pair', T.a, T.b, { left: 'men', right: 'lake', texts: [
        tx('<div class="gd" style="font-size:24px">天秤座18度</div><div class="m" style="font-size:30px">外に向かって説明する</div>', T.at(0, .1), T.b, 'left:60px;top:150px;width:840px;text-align:center'),
        tx('<div class="gd" style="font-size:24px">蠍座8度</div><div class="m" style="font-size:30px">言葉にしなくても通じ合う</div>', T.at(0, .55), T.b, 'left:1020px;top:150px;width:840px;text-align:center'),
        tx('<div class="m">どちらか一方ではなく、組み合わせて読む</div>', T.s(1), T.b, 'left:0;right:0;top:860px;text-align:center')] })] },
    { text: '心が通じていると感じる関係ほど、言わなくてもわかってくれるはず、と思ってしまう。でも、湖面に映る月は、水面が揺れれば崩れてしまいます。静かに通じ合う関係を大切にしたいからこそ、言葉にして説明する。金星が逆行している今は、その言葉を、急がずに選べる時期でもあります。', pad: 2.0,
      cues: T => [S('lake', T.a, T.b, { amp: [[T.a, .5], [T.s(1), .5], [T.s(1) + 1.6, 2.8], [T.s(2), 2.8], [T.s(2) + 2.4, .5]], texts: [
        tx('「言わなくても、わかってくれるはず」', T.s(0) + .5, T.s(1) + .5, 'left:120px;top:150px', 'm'),
        tx('水面が揺れると、月は崩れる', T.s(1) + .8, T.s(2), 'left:120px;top:150px', 'm'),
        tx('だからこそ、言葉にして説明する', T.s(2) + .4, T.b, 'left:120px;top:150px', 'm'),
        tx('金星逆行中：言葉を、急がずに選ぶ', T.s(3) + .4, T.b, 'left:124px;top:230px', 'gd')] })] },
  ]);

  /* ======================= 12 新月からの2週間 ======================= */
  const EV = (T, U2) => [
    { v: 11.03, label: '10/11 新月', at: U2.s(0) + .2 }, { v: 11.27, label: '6:31', sub: '金星□火星 0°00′', at: U2.s(1) + .2, below: true },
    { v: 16, label: '10/16', sub: '冥王星 順行へ', at: U2.s(2) + .2 }, { v: 23.77, label: '10/23', sub: '太陽 蠍座へ', at: U2.s(3) + .2, below: true },
    { v: 24.67, label: '10/24', sub: '水星 逆行開始', at: U2.s(4) + .2, lift: 110 }, { v: 25.75, label: '10/25', sub: '金星 天秤座へ', at: U2.at(5, .1), below: true, drop: 110 },
    { v: 26.55, label: '10/26', sub: '牡牛座 満月', at: U2.at(5, .55) }];
  ch('12', '新月からの2週間を、日常で使う', [
    { text: '最後に、新月からの2週間の流れと、試してみたいことをまとめます。', pad: 1.0,
      cues: T => [S('timeline', T.a, T.u(1).b, { from: 10, to: 27, x0: 180, x1: 1740, ticks: [10, 15, 20, 25].map(d => ({ v: d, label: `10/${d}` })), events: EV(T, T.u(1)) })] },
    { text: '新月は10月11日。その朝、金星と火星のスクエアがぴったりになります。16日に冥王星が順行へ。23日の夕方に、太陽が蠍座に入ります。24日には水星も逆行を始めます。25日に金星が天秤座へ戻り、26日の午後、牡牛座で満月を迎えます。', pad: 2.0 },
    { text: '今回の配置を、三つの問いにしてみます。', pad: 1.0,
      cues: T => {
        const U4 = T.u(1), U5 = T.u(2), U6 = T.u(3);
        return [S('memo', T.a, U6.b, { title: '三つの問い', titleA: T.a + .3, lines: [
          { glyph: '♀', text: 'この関係で、私が守りたいものは何？', a: U4.s(0) + .3, y: 280, d: 2 },
          { text: '相手に合わせてきたことの中で、一つだけ言葉に', a: U4.s(2), y: 350, cls: 'small', d: 1.6 },
          { glyph: '♂', text: 'それを、どう伝えたら動ける？', a: U5.s(0) + .3, y: 450, d: 2 },
          { text: '我慢か、ぶつかるか、ではなく →「今週はここまで」「来週ならできる」', a: U5.s(2), y: 520, cls: 'small', d: 2.4 },
          { glyph: '♎', text: '言わずにいたことは、どんな結果を生んでいる？', a: U6.s(0) + .3, y: 620, d: 2 },
          { text: '責めるためではなく、選び直すために', a: U6.s(2), y: 690, cls: 'small', d: 1.6 }] })];
      } },
    { text: '一つ目は、「この関係で、私が守りたいものは何？」です。金星の問いですね。相手に合わせてきたことの中で、本当に自分が大切にしたいものを、一つだけ言葉にしてみます。', pad: 1.4 },
    { text: '二つ目は、「それを、どう伝えたら動ける？」です。こちらは火星の問いです。我慢するか、ぶつかるか、の二択ではなく、「今週はここまで」「来週ならできる」と、具体的な形にしてみます。', pad: 1.4 },
    { text: '三つ目は、「言わずにいたことは、どんな結果を生んでいる？」です。天秤座18度の問いです。自分を責めるためではなく、これからどうしたいかを選び直すために、振り返ってみます。', pad: 1.6 },
    { text: '新しい約束や申し込みは、水星が逆行を始める24日より前に進めておくと、確認がしやすいと思います。ただ、金星は逆行中なので、新しい関係を急いで広げるより、今ある関係を整えることを優先してみてください。', pad: 1.8,
      cues: T => [S('timeline', T.a, T.b, { from: 10, to: 27, x0: 180, x1: 1740, axes: [{ y: 560 }],
        ticks: [10, 15, 20, 25].map(d => ({ v: d, label: `10/${d}` })),
        events: [{ v: 24.67, label: '10/24', sub: '水星 逆行開始', at: T.a + .6, hlA: T.a + .6 }],
        ranges: [{ v0: 11.03, v1: 24.6, y: 440, label: '新しい約束・申し込みは、24日より前に', at: T.s(0) + .6 },
                 { v0: 10, v1: 27, y: 700, label: '金星 逆行中（10/3〜11/14）：今ある関係を整える', at: T.s(1) + .3, color: 'rgba(68,48,73,.9)' }] })] },
  ]);

  /* ======================= 13 まとめ ======================= */
  ch('13', 'まとめ', [
    { text: 'ここまでの話は、天秤座17度21分で重なる太陽と月、第3ハウスという場所、支配星の金星の逆行と、火星との12分のスクエア、太陽・金星・火星の支配星の輪、そして天秤座18度と蠍座8度のサビアンを重ねて考えたものです。', pad: 2.2,
      cues: T => [cam(T.a - .6, 'home', .1), halo(['sun', 'moon'], T.at(0, .076), T.b), house(3, T.at(0, .248), T.b, { v: .5 }), halo(['venus'], T.at(0, .352), T.b),
        line('venus', 'mars', T.at(0, .457), T.b, { w: 4 }), halo(['mars'], T.at(0, .457), T.b), seg([6, 7, 4], T.at(0, .571), T.b, { v: .5 }),
        tick(197, T.at(0, .714), T.b), tick(217, T.at(0, .74), T.b),
        panel('ここまでの根拠', [
          [`<div class="mid">${g('☉☽')} 天秤座17°21′で重なる</div>`, T.at(0, .076)], ['<div class="mid">第3ハウス</div>', T.at(0, .248)],
          [`<div class="mid">${g('♀')} 支配星の金星　逆行中</div>`, T.at(0, .352)], [`<div class="mid">${g('♀□♂')} 0°12′</div>`, T.at(0, .457)],
          ['<div class="mid">太陽 → 金星 → 火星 → 太陽</div>', T.at(0, .571)], ['<div class="mid">天秤座18度 ・ 蠍座8度</div>', T.at(0, .714)]], T.a + .3, T.b)] },
    { text: '関係を大切にしたい気持ちと、自分がどう動くか。その二つを、どちらか一方に決めるのではなく、結び直してみる。今回の新月を、そんなふうに始めるきっかけにしていただけたらと思います。', pad: 1.8,
      cues: T => [cam(T.a, VM, 2), halo(['venus'], T.a + .3, T.b), halo(['mars'], T.at(0, .5), T.b), line('venus', 'mars', T.a - .6, T.b, { w: 3, draw: .01, op: .6 }),
        line({ g: 'venus' }, { g: 'mars' }, T.s(1) + .4, T.b, { curve: .15, w: 5, draw: 2.2, glow: [T.s(1) + 2.4, T.b] }),
        panel('結び直す', [[`<div class="mid">${g('♀')} 関係を大切にしたい気持ち</div>`, T.a + .3], [`<div class="mid">${g('♂')} 自分がどう動くか</div>`, T.at(0, .5)], ['<div class="mid hl">どちらか一方ではなく、結び直す</div>', T.s(1) + .4]], T.a, T.b)] },
    { text: '次は、10月26日の牡牛座の満月でお会いしましょう。', pad: 1.6,
      cues: T => [S('align', T.a, T.b, { keys: [[T.a, 0], [T.a + .6, 0], [T.b - .4, 180]], texts: [tx('<div class="h">次回　10月26日</div><div class="m" style="margin-top:8px">牡牛座の満月</div>', T.a + .5, T.b, 'left:120px;top:140px')] })] },
    { text: '最後までご覧いただき、ありがとうございました。星よみ専門家のおますでした。', pad: 3.0,
      cues: T => [S('sky', T.a, T.b + 2, { wipe: true, texts: [tx('<div class="m">ご覧いただき、ありがとうございました</div>', T.a + .5, T.b + 2, 'left:120px;top:380px'), tx('<div class="h">星よみ専門家　おます</div>', T.s(1), T.b + 2, 'left:120px;top:470px')] })] },
  ]);

  window.CHAPTERS = chapters;
})();
