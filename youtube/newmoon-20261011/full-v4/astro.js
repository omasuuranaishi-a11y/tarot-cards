/* 全編 v4：新月（東京）のチャートを、ご本人が使っている astro.com（Astrodienst）の図そのものにする。
   画像は ../astro/astro-chart@3x.png（ご本人がチャットで渡した図 astro-chart.png（568x604）を、拡大してもぼやけにくいよう3倍に高画質化したもの。Astrodienst の図なので GitHub には入れない）。
   自作の円・記号・度数は隠し、金の丸・線・帯などの強調だけを図の上に重ねる。
   図の中心・輪の半径・天体記号の位置は、画像を測って決めた（中心 279.4,337.3／黄道帯の外 227.5・内 186／アスペクトの円 138）。
   アスペクト線の端（半径138）は、計算した黄経の位置と図の線の端が一致することを確かめてある。
   ../lib/chart.js の後、../full/chapters.js より前に読み込む（chapters.js が Chart.make(CHARTS.nm) の半径を使うため）。 */
(function () {
  const IMG = { src: (window.E && E.ASTRO_SRC) || '../astro/astro-chart@3x.png', w: 568, h: 604, cx: 279.42, cy: 337.33, out: 227.5, signIn: 186, asp: 138, disk: 260 };
  // astro.com の図の中の天体記号の中心（画像の座標）。太陽と月・金星と水星は図の中で少しずらして描かれている
  const GLYPH = { sun: [206, 491.5], moon: [191.5, 481], mercury: [269, 506], venus: [249, 502], mars: [111, 313.5],
    jupiter: [107.5, 353.5], saturn: [375, 197.5], uranus: [221.5, 176], neptune: [397.5, 215], pluto: [444.5, 374.5] };
  const k = 430 / IMG.out; // 自作の図の黄道帯の外側（R.out = 430）に合わせる
  const NS = 'http://www.w3.org/2000/svg';
  let uid = 0;
  const make = Chart.make;
  // astro.com の図と同じ色（画像から測った値）。前回の満月・ロンドンの図（自作）も、この色にそろえる
  const AC = { disk: '#D9FFFF', band: '#FFFFF0', planet: '#F0FFFF', inner: '#FFFFF0', line: '#1a1a1a',
    elem: ['#F81213', '#35D631', '#FF772F', '#083AFF'] }; // 火・地・風・水
  function astroLike(A, g, refs) {
    const R = A.R, base = g.querySelector('.chart-base');
    const bg = base.querySelector('circle'); // いちばん下の円
    bg.setAttribute('r', R.out + (IMG.disk - IMG.out) * k); bg.style.fill = AC.disk;
    const fills = [[R.out, AC.band], [R.signIn, AC.planet], [R.asp, AC.inner]].map(([r, c]) => {
      const e = document.createElementNS(NS, 'circle'); e.setAttribute('r', r); e.style.fill = c; e.style.stroke = 'none'; return e;
    });
    fills.reverse().forEach(e => bg.after(e));
    base.querySelectorAll('circle:not([r="' + bg.getAttribute('r') + '"]), line, path').forEach(e => {
      if (refs.signSeg.includes(e) || fills.includes(e)) return;
      e.style.stroke = AC.line; e.style.strokeOpacity = e.tagName === 'path' ? .7 : 1;
    });
    base.querySelectorAll('text.sign-glyph').forEach((t, i) => { t.style.fill = AC.elem[i % 4]; });
    refs.signSeg.forEach(s => { s.style.mixBlendMode = 'multiply'; });
    // アスペクト線（astro.com の図と同じ色：90°・180° は赤、60°・120° は青、150° は緑の点線）。オーブは 60〜180° が6°以内、150° は3°以内
    const keys = Object.keys(refs.planet), lon = k2 => A.C.bodies[k2].lon, aspG = document.createElementNS(NS, 'g');
    fills.find(e => +e.getAttribute('r') === R.asp).after(aspG); // いちばん内側の塗りの上に描く
    keys.forEach((a, i) => keys.slice(i + 1).forEach(b => {
      const d = Math.abs(((lon(a) - lon(b) + 540) % 360) - 180);
      const hit = [[60, '#1E50FF', 6], [90, '#E00000', 6], [120, '#1E50FF', 6], [180, '#E00000', 6], [150, '#2DB42D', 3]].find(([ang, , orb]) => Math.abs(d - ang) <= orb);
      if (!hit) return;
      const [x1, y1] = A.pt(lon(a), R.asp), [x2, y2] = A.pt(lon(b), R.asp);
      const ln = document.createElementNS(NS, 'line');
      for (const [q, v] of Object.entries({ x1, y1, x2, y2 })) ln.setAttribute(q, v);
      ln.style.stroke = hit[1]; ln.style.strokeWidth = 2.2; if (hit[0] === 150) ln.style.strokeDasharray = '9 7';
      aspG.appendChild(ln);
    }));
    g.querySelectorAll('.houses line').forEach(e => { e.style.stroke = AC.line; e.style.strokeOpacity = e.getAttribute('stroke-width') === '2' ? 1 : .75; });
    g.querySelectorAll('.houses text').forEach(e => { e.style.fill = '#333'; });
    for (const key in refs.planet) {
      const P = refs.planet[key];
      P.glyph.style.fill = '#111';
      [...P.g.querySelectorAll('line')].forEach(e => { e.style.stroke = '#222'; });
      P.label.querySelectorAll('text').forEach(e => { e.style.fill = '#222'; e.style.stroke = AC.planet; });
      P.label.querySelectorAll('tspan').forEach(e => { e.style.fill = '#C00'; });
      P.halo.style.mixBlendMode = 'multiply';
    }
  }
  Chart.make = data => {
    const A = make(data);
    if (data !== window.CHARTS.nm) {
      const build0 = A.build;
      A.build = (g, opt) => { const refs = build0(g, opt); astroLike(A, g, refs); return refs; };
      return A;
    }
    Object.assign(A.R, { signIn: IMG.signIn * k, tick: IMG.signIn * k, asp: IMG.asp * k, planet: 172 * k });
    const build = A.build;
    A.build = (g, opt) => {
      const refs = build(g, opt);
      const base = g.querySelector('.chart-base');
      [...base.children].forEach(el => { if (!refs.signSeg.includes(el)) el.style.display = 'none'; });
      g.querySelector('.houses').style.display = 'none';
      for (const key in refs.planet) {
        const P = refs.planet[key], [px, py] = GLYPH[key];
        [...P.g.children].forEach(el => { if (el !== P.halo) el.style.display = 'none'; });
        P.gx = (px - IMG.cx) * k; P.gy = (py - IMG.cy) * k;
        P.halo.setAttribute('cx', P.gx); P.halo.setAttribute('cy', P.gy); P.halo.setAttribute('r', 26);
        P.halo.style.mixBlendMode = 'multiply';
      }
      refs.signSeg.forEach(s => { s.style.mixBlendMode = 'multiply'; });
      const id = 'astroClip' + (uid++);
      const defs = document.createElementNS(NS, 'defs');
      defs.innerHTML = `<clipPath id="${id}"><circle cx="0" cy="0" r="${IMG.disk * k}"/></clipPath>`;
      const img = document.createElementNS(NS, 'image');
      for (const [a, v] of Object.entries({ href: IMG.src, x: -IMG.cx * k, y: -IMG.cy * k, width: IMG.w * k, height: IMG.h * k, 'clip-path': `url(#${id})`, preserveAspectRatio: 'none' })) img.setAttribute(a, v);
      g.insertBefore(img, g.firstChild); g.insertBefore(defs, img);
      return refs;
    };
    return A;
  };
})();
