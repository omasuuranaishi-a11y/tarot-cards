/* 全編 v4：線画の挿絵を、いらすとやのイラストに置き換える（または、スマホ・手帳の場面に添える）。
   画像は ../illust/ に置く（tools/fetch_illust.sh で取得。一覧は tools/illust.tsv。いらすとやの規約で再配布できないので GitHub には入れない）。
   いらすとやの商用利用は1つの制作物につき20点まで（同じイラストの重複は1点）。いまは15点。いらすとんは点数の上限なし（いまは2点）。
   イラストナビは30点以上使う商用デザインだと有償（いまは3点）。
   p.imgs：[{ src, x, y, w, a, b, night, mul, clip }]（a・b は出る時刻と消える時刻。省略すると場面と同じ。night は夜の色合い。
           src は拡張子なしなら .png。いらすとんの絵は白い背景の jpg なので mul（乗算で白を背景になじませる）をつける。
           clip は CSS の clip-path（1枚に2つの絵が並んでいるときに片方だけ見せる、絵の中の文字を隠す、など）。x・y・w は画像全体の位置と幅）
           { moon: true, x, y, r, rx, ry } は月（と水面に映る月）を描く。p.amp があれば水面の揺れに合わせて映る月を崩す。 */
(function () {
  const { div, rise, win, prog, ease, lerp } = E.U;
  const DIR = E.ILLUST_DIR || '../illust/';

  // 文字だけの場面。絵は下の共通の仕組みで重ねる
  E.scene('illust', (layer, p) => {
    const T = (p.texts || []).map(([html, a, b, style, cls]) => [div('stext ' + (cls || ''), html, layer, style || ''), a, b]);
    return { frame(t) { T.forEach(([el, a, b]) => rise(el, win(t, a, b ?? p.b, .7, .5))); } };
  });

  // 水面の揺れの大きさ（lake の場面と同じ決め方）
  function ampAt(p, t) {
    if (!p.amp) return 1;
    let amp = p.amp[0][1];
    for (let i = 1; i < p.amp.length; i++) { const [ta, va] = p.amp[i - 1], [tb, vb] = p.amp[i]; if (t >= ta) amp = lerp(va, vb, ease(prog(t, ta, tb - ta))); }
    return amp;
  }

  // どの場面でも p.imgs があればイラストを重ねる
  Object.keys(E.scenes).forEach(name => {
    const make = E.scenes[name];
    E.scenes[name] = (layer, p, c) => {
      const obj = make(layer, p, c) || {};
      if (!p.imgs) return obj;
      const items = p.imgs.map((m, i) => {
        if (m.moon) {
          const moon = div('il-moon', '', layer, `left:${m.x - m.r}px;top:${m.y - m.r}px;width:${m.r * 2}px;height:${m.r * 2}px`);
          const refl = m.ry ? div('il-refl', '', layer, `left:${m.rx - m.r}px;top:${m.ry - m.r * .35}px;width:${m.r * 2}px;height:${m.r * .7}px`) : null;
          return { m, i, els: [moon, refl].filter(Boolean), moon, refl };
        }
        const img = document.createElement('img');
        img.className = 'il'; img.alt = ''; img.src = DIR + (m.src.includes('.') ? m.src : m.src + '.png');
        img.style.cssText = `left:${m.x}px;top:${m.y}px;width:${m.w}px`;
        if (m.night) img.classList.add('night'); // 昼の湖を、月夜の色合いにする
        if (m.mul) img.classList.add('mul');
        if (m.clip) img.style.clipPath = m.clip;
        layer.appendChild(img);
        return { m, i, els: [img], img };
      });
      const frame = obj.frame;
      obj.frame = t => {
        const pend = [];
        items.forEach(({ m, i, els, img, refl }) => {
          const v = win(t, m.a ?? p.a + .2, m.b ?? p.b, .7, .5);
          els.forEach(el => { el.style.opacity = v.toFixed(3); el.style.visibility = v > 0 ? 'visible' : 'hidden'; });
          if (img) {
            img.style.transform = `translateY(${((1 - ease(v)) * 16 + Math.sin(t * 1.1 + i * 1.7) * 4).toFixed(1)}px)`;
            if (v > 0 && !img.complete) pend.push(img.decode().catch(() => {}));
          }
          if (refl) { // 水面が揺れるほど、映る月は横に崩れて薄くなる
            const a = ampAt(p, t), w = Math.sin(t * 2.3) * .5 + Math.sin(t * 3.7 + 1) * .5;
            refl.style.transform = `scaleX(${(1 + .12 * a + .05 * a * w).toFixed(3)}) skewX(${(a * 6 * w).toFixed(2)}deg)`;
            refl.style.opacity = (v * Math.max(.25, 1 - .22 * a)).toFixed(3);
          }
        });
        const r = frame && frame(t);
        if (r && typeof r.then === 'function') pend.push(r);
        return pend.length ? Promise.all(pend) : undefined;
      };
      return obj;
    };
  });

  // [章, 単位（1から）, 元の場面, 置き換えるか（false なら添える）, 絵, 読む文の書き出し（取り違えの確認用）]
  const SET = [
    [1, 3, 'phone', false, T => [{ src: 'phone_sad', x: 70, y: 330, w: 340 }], '大切な人との関係は'],
    [3, 6, 'balance', true, T => [{ src: 'scales', x: 960, y: 270, w: 760 }, { src: 'gaman', x: 150, y: 330, w: 520, a: T.s(1) }], 'たとえば、職場でも'],
    [5, 4, 'letters', true, T => [{ src: 'album', x: 300, y: 300, w: 600 }, { src: 'letter', x: 1120, y: 230, w: 440, a: T.s(0) + 1 }], '金星は、何を大切に'],
    [6, 8, 'elem', true, T => [{ src: 'scorpio', x: 330, y: 430, w: 400 }, { src: 'leo', x: 1300, y: 450, w: 420, a: T.s(1) }], '蠍座の金星は'],
    [6, 11, 'phone', false, T => {
      const U12 = T.u(1), U13 = T.u(2);
      return [{ src: 'headache', x: 70, y: 340, w: 340, b: U12.a + .3 },
              { src: 'imagine', x: 40, y: 300, w: 400, a: U12.a, b: U13.a + .3 },
              { src: 'phone_smile', x: 70, y: 330, w: 340, a: U13.a }];
    }, 'たとえば、身近な人から'],
    [11, 3, 'sabian', true, T => [{ src: 'arrest', x: 260, y: 200, w: 540 }], '天秤座18度は'],
    [11, 5, 'pair', true, T => [{ src: 'couple', x: 250, y: 300, w: 450, a: T.s(1) }, { src: 'arrest', x: 1220, y: 300, w: 420, a: T.s(2) }], 'ここで私が注目'],
    [11, 6, 'memo', false, T => [{ src: 'write', x: 1610, y: 430, w: 270 }], 'たとえば、「相手のため'],
    [11, 10, 'pair', true, T => [{ src: 'arrest', x: 270, y: 300, w: 420 }, { src: 'lake', x: 1180, y: 330, w: 520, a: T.at(0, .55), night: true },
      { moon: true, x: 1560, y: 372, r: 30, rx: 1440, ry: 560, a: T.at(0, .55) }], '天秤座18度が、外に'],
    [11, 11, 'lake', true, T => [{ src: 'lake', x: 900, y: 200, w: 700, night: true }, { moon: true, x: 1430, y: 262, r: 40, rx: 1250, ry: 600 }], '心が通じていると'],
    [12, 3, 'memo', false, T => [{ src: 'write_smile', x: 1610, y: 430, w: 270 }], '今回の配置を'],
    // いらすとん（水彩のやわらかい絵）：絵のなかった図解の場面に添える
    [3, 5, 'cycle', false, T => [{ src: 'dandelion.jpg', x: 170, y: 330, w: 380, a: T.s(1), mul: true }], '新月は、月の満ち欠け'],
    [8, 6, 'bars', false, T => [{ src: 'milkyway.jpg', x: 1240, y: 520, w: 560, a: T.s(1), mul: true }], 'ここは、とっても大事な違いです'],
    // イラストナビ：年表の場面の空いているところに添える
    [10, 6, 'timeline', false, T => [{ src: 'thinking', x: 1260, y: 96, w: 725, a: T.s(1) }], 'それから、冥王星は'],
    // 案内する女性。右上の「ドーン」の文字は clip で隠す（手にはかからない）
    [12, 1, 'timeline', false, T => [{ src: 'guide', x: 470, y: 140, w: 620, b: T.b + .3,
      clip: 'polygon(-10% -10%, 63.2% -10%, 63.2% 52.4%, 78.2% 52.4%, 78.2% -10%, 110% -10%, 110% 110%, -10% 110%)' }], '最後に、新月からの'],
    // 主線ありとなしの2枚が並んだ絵なので、右（主線なし）だけを見せる
    [12, 7, 'timeline', false, T => [{ src: 'laptop_memo', x: 1194, y: 36, w: 700, a: T.s(0) + .8, clip: 'inset(-10% -10% -10% 49.7%)' }], '新しい約束や申し込みは'],
  ];
  const C = window.CHAPTERS;
  // 01-1 表紙：題の文字を、ゆっくりふんわり出す（ご本人の希望。速く出ると違和感があるため）
  const u11 = C[0].units[0], f11 = u11.cues;
  u11.cues = T => f11(T).map(c => {
    if (c.k === 'scene' && c.name === 'cover') {
      Object.assign(c.p.at, { date: T.a + .2, title: T.a + .8, rule: T.a + 1.9, tag: T.a + 2.3 });
      c.p.soft = { date: 1.6, title: 2.2, rule: 1.6, tag: 2.0, chip: 1.8 };
    }
    return c;
  });
  SET.forEach(([ch, no, from, replace, imgs, head]) => {
    const u = C[ch - 1].units[no - 1], f = u.cues;
    if (!u.text.startsWith(head) || !f) throw new Error(`v4: ${ch}-${no} が見つかりません`);
    u.cues = T => f(T).map(c => {
      if (c.k === 'scene' && c.name === from) { if (replace) { c.name = 'illust'; c.p.was = from; } c.p.imgs = imgs(T); }
      return c;
    });
  });
})();
