/* 全編 v4：新月（東京）のチャートを、ご本人が使っている astro.com（Astrodienst）の図そのものにする。
   画像は ../astro/astro-chart.png（ご本人がチャットで渡した図。568x604。Astrodienst の図なので GitHub には入れない）。
   自作の円・記号・度数は隠し、金の丸・線・帯などの強調だけを図の上に重ねる。
   図の中心・輪の半径・天体記号の位置は、画像を測って決めた（中心 279.4,337.3／黄道帯の外 227.5・内 186／アスペクトの円 138）。
   アスペクト線の端（半径138）は、計算した黄経の位置と図の線の端が一致することを確かめてある。
   ../lib/chart.js の後、../full/chapters.js より前に読み込む（chapters.js が Chart.make(CHARTS.nm) の半径を使うため）。 */
(function () {
  const IMG = { src: (window.E && E.ASTRO_SRC) || '../astro/astro-chart.png', w: 568, h: 604, cx: 279.42, cy: 337.33, out: 227.5, signIn: 186, asp: 138, disk: 260 };
  // astro.com の図の中の天体記号の中心（画像の座標）。太陽と月・金星と水星は図の中で少しずらして描かれている
  const GLYPH = { sun: [206, 491.5], moon: [191.5, 481], mercury: [269, 506], venus: [249, 502], mars: [111, 313.5],
    jupiter: [107.5, 353.5], saturn: [375, 197.5], uranus: [221.5, 176], neptune: [397.5, 215], pluto: [444.5, 374.5] };
  const k = 430 / IMG.out; // 自作の図の黄道帯の外側（R.out = 430）に合わせる
  const NS = 'http://www.w3.org/2000/svg';
  let uid = 0;
  const make = Chart.make;
  Chart.make = data => {
    const A = make(data);
    if (data !== window.CHARTS.nm) return A;
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
