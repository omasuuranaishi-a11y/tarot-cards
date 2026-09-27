/* ホロスコープの作図（SVG）。座標はチャート中心を原点にした値。
   天体・カスプの値は chart-data.js（Swiss Ephemeris の計算値）だけを使い、手で描き直さない。 */
(function () {
  const C = window.CHART;
  const ASC = C.bodies.asc.lon;
  const NS = 'http://www.w3.org/2000/svg';
  const R = { out: 430, signIn: 370, tick: 370, planet: 330, label: 270, house: 213, asp: 200 };

  const SIGNS = ['牡羊座','牡牛座','双子座','蟹座','獅子座','乙女座','天秤座','蠍座','射手座','山羊座','水瓶座','魚座'];
  const SIGN_GLYPH = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'].map(g => g + '︎');
  const PLANETS = [
    { key: 'sun', glyph: '☉', name: '太陽' },
    { key: 'moon', glyph: '☽', name: '月' },
    { key: 'mercury', glyph: '☿', name: '水星' },
    { key: 'venus', glyph: '♀', name: '金星' },
    { key: 'mars', glyph: '♂', name: '火星' },
    { key: 'jupiter', glyph: '♃', name: '木星' },
    { key: 'saturn', glyph: '♄', name: '土星' },
    { key: 'uranus', glyph: '♅', name: '天王星' },
    { key: 'neptune', glyph: '♆', name: '海王星' },
    { key: 'pluto', glyph: '♇', name: '冥王星' },
  ];

  const phi = lon => Math.PI + (lon - ASC) * Math.PI / 180;
  const pt = (lon, r) => { const a = phi(lon); return [r * Math.cos(a), -r * Math.sin(a)]; };
  const lonOf = key => C.bodies[key].lon;

  /* 分未満は切り捨て（承認済みチャートと同じ表記） */
  function dm(x) { const d = Math.floor(x + 1e-9); return [d, Math.floor((x - d) * 60 + 1e-9)]; }
  function fmtDeg(lon) { const [d, m] = dm(((lon % 30) + 30) % 30); return `${d}°${String(m).padStart(2, '0')}′`; }
  function fmtPos(lon) { return SIGNS[Math.floor(lon / 30)] + fmtDeg(lon); }
  function fmtOrb(x) { const [d, m] = dm(Math.abs(x)); return `${d}°${String(m).padStart(2, '0')}′`; }
  function sep(a, b) { return Math.abs(((a - b + 540) % 360) - 180); }

  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function arcPath(r1, r2, lon1, lon2) {
    const [x1, y1] = pt(lon1, r2), [x2, y2] = pt(lon2, r2), [x3, y3] = pt(lon2, r1), [x4, y4] = pt(lon1, r1);
    const large = ((lon2 - lon1 + 360) % 360) > 180 ? 1 : 0;
    // 黄経が増える向きは画面上で反時計回り（SVGの sweep=0）
    return `M${x1},${y1} A${r2},${r2} 0 ${large} 0 ${x2},${y2} L${x3},${y3} A${r1},${r1} 0 ${large} 1 ${x4},${y4} Z`;
  }
  function ringArc(r, lon1, lon2) {
    const [x1, y1] = pt(lon1, r), [x2, y2] = pt(lon2, r);
    const d = ((lon2 - lon1) % 360 + 360) % 360;
    const ccw = d <= 180;
    return `M${x1},${y1} A${r},${r} 0 0 ${ccw ? 0 : 1} ${x2},${y2}`;
  }

  /* 天体記号が重ならないよう、表示角度だけを最小11°ずつ離す（真の位置は目盛りの刻みで示す） */
  function displayLons(minSep = 11) {
    const items = PLANETS.map(p => ({ key: p.key, lon: lonOf(p.key), d: lonOf(p.key) }));
    items.sort((a, b) => a.lon - b.lon);
    for (let iter = 0; iter < 200; iter++) {
      let moved = false;
      for (let i = 0; i < items.length; i++) {
        const a = items[i], b = items[(i + 1) % items.length];
        const gap = ((b.d - a.d) % 360 + 360) % 360;
        if (gap < minSep) { const push = (minSep - gap) / 2 + 0.01; a.d -= push; b.d += push; moved = true; }
      }
      if (!moved) break;
    }
    const out = {}; items.forEach(i => out[i.key] = i.d); return out;
  }

  function build(g, opt = {}) {
    const refs = { signSeg: [], planet: {}, cusp: [], axis: {} };
    const gold = 'var(--gold)', white = 'var(--white)';
    const base = el('g', { class: 'chart-base' }, g);
    el('circle', { r: R.out + 6, fill: 'rgba(14,11,24,.72)', stroke: 'none' }, base);

    // サインの帯（強調用の塗りを持つ）
    for (let i = 0; i < 12; i++) {
      const seg = el('path', { d: arcPath(R.signIn, R.out, i * 30, i * 30 + 30), fill: 'var(--purple)', 'fill-opacity': 0, stroke: 'none' }, base);
      refs.signSeg.push(seg);
    }
    el('circle', { r: R.out, fill: 'none', stroke: gold, 'stroke-width': 1.6 }, base);
    el('circle', { r: R.signIn, fill: 'none', stroke: gold, 'stroke-width': 1.2, 'stroke-opacity': .8 }, base);
    el('circle', { r: R.asp, fill: 'none', stroke: gold, 'stroke-width': 1, 'stroke-opacity': .55 }, base);
    for (let i = 0; i < 12; i++) {
      const [x1, y1] = pt(i * 30, R.signIn), [x2, y2] = pt(i * 30, R.out);
      el('line', { x1, y1, x2, y2, stroke: gold, 'stroke-width': 1.1, 'stroke-opacity': .75 }, base);
      const [gx, gy] = pt(i * 30 + 15, (R.signIn + R.out) / 2);
      const t = el('text', { x: gx, y: gy, class: 'glyph sign-glyph', 'text-anchor': 'middle', 'dominant-baseline': 'central' }, base);
      t.textContent = SIGN_GLYPH[i];
    }
    // 1°ごとの目盛り（5°・10°は長く）
    let dTicks = '';
    for (let l = 0; l < 360; l++) {
      const len = l % 10 === 0 ? 12 : l % 5 === 0 ? 8 : 4;
      const [x1, y1] = pt(l, R.tick), [x2, y2] = pt(l, R.tick - len);
      dTicks += `M${x1.toFixed(2)},${y1.toFixed(2)}L${x2.toFixed(2)},${y2.toFixed(2)}`;
    }
    el('path', { d: dTicks, stroke: gold, 'stroke-width': .9, 'stroke-opacity': .6, fill: 'none' }, base);

    // ハウス
    const houses = el('g', { class: 'houses' }, g);
    C.cusps.forEach((c, i) => {
      const isAxis = i % 3 === 0;
      const [x1, y1] = pt(c, R.asp), [x2, y2] = pt(c, isAxis ? R.signIn : R.signIn - 14);
      const ln = el('line', { x1, y1, x2, y2, stroke: isAxis ? gold : white, 'stroke-width': isAxis ? 2 : 1, 'stroke-opacity': isAxis ? .9 : .32 }, houses);
      refs.cusp.push(ln);
      if (isAxis) { // サインの帯の上は通さず、外側だけ伸ばす
        const [ox1, oy1] = pt(c, R.out), [ox2, oy2] = pt(c, R.out + 28);
        el('line', { x1: ox1, y1: oy1, x2: ox2, y2: oy2, stroke: gold, 'stroke-width': 2, 'stroke-opacity': .9 }, houses);
      }
      const next = C.cusps[(i + 1) % 12];
      const mid = c + (((next - c) % 360 + 360) % 360) / 2;
      const [hx, hy] = pt(mid, R.house);
      const ht = el('text', { x: hx, y: hy, class: 'house-num', 'text-anchor': 'middle', 'dominant-baseline': 'central' }, houses);
      ht.textContent = i + 1;
    });
    const axisLabels = [['ASC', 0], ['IC', 3], ['DSC', 6], ['MC', 9]];
    axisLabels.forEach(([lab, i]) => {
      const [x, y] = pt(C.cusps[i], R.out + 50);
      const t = el('text', { x, y, class: 'axis-label', 'text-anchor': 'middle', 'dominant-baseline': 'central' }, houses);
      t.textContent = lab;
      refs.axis[lab] = t;
    });

    // 天体
    const disp = displayLons(opt.minSep || 11);
    const planets = el('g', { class: 'planets' }, g);
    PLANETS.forEach(p => {
      const lon = lonOf(p.key), dl = disp[p.key];
      const grp = el('g', { class: 'planet', 'data-key': p.key }, planets);
      const [tx1, ty1] = pt(lon, R.tick), [tx2, ty2] = pt(lon, R.tick - 12);
      el('line', { x1: tx1, y1: ty1, x2: tx2, y2: ty2, stroke: white, 'stroke-width': 2 }, grp);
      if (Math.abs(dl - lon) > 0.5) { // 表示位置をずらした天体は、真の位置から細い線でつなぐ
        const [cx1, cy1] = pt(lon, R.tick - 12), [cx2, cy2] = pt(dl, R.planet + 20);
        el('line', { x1: cx1, y1: cy1, x2: cx2, y2: cy2, stroke: white, 'stroke-width': 1, 'stroke-opacity': .5 }, grp);
      }
      const [gx, gy] = pt(dl, R.planet);
      const halo = el('circle', { cx: gx, cy: gy, r: 30, fill: 'var(--purple)', 'fill-opacity': 0, stroke: gold, 'stroke-width': 2, 'stroke-opacity': 0 }, grp);
      const gt = el('text', { x: gx, y: gy, class: 'glyph planet-glyph', 'text-anchor': 'middle', 'dominant-baseline': 'central' }, grp);
      gt.textContent = p.glyph;
      // 度数は2行（上に度、下に分）。どの位置でも上から読める向きにする
      const lt = el('g', { class: 'deg-stack' }, grp);
      const [dd, mm] = dm(((lon % 30) + 30) % 30);
      const [lx, ly] = pt(dl, R.label);
      const t1 = el('text', { x: lx, y: ly - 12, class: 'deg-label', 'text-anchor': 'middle', 'dominant-baseline': 'central' }, lt);
      t1.textContent = dd + '°';
      const t2 = el('text', { x: lx, y: ly + 12, class: 'deg-label', 'text-anchor': 'middle', 'dominant-baseline': 'central' }, lt);
      t2.textContent = String(mm).padStart(2, '0') + '′';
      if (C.bodies[p.key].retro) {
        const r = el('tspan', { class: 'retro' }, t2); r.textContent = 'R';
      }
      refs.planet[p.key] = { g: grp, halo, glyph: gt, label: lt, gx, gy, lon, dispLon: dl };
    });
    return refs;
  }

  window.Chart = { C, R, SIGNS, SIGN_GLYPH, PLANETS, phi, pt, lonOf, fmtDeg, fmtPos, fmtOrb, sep, el, arcPath, ringArc, build, NS };
})();
