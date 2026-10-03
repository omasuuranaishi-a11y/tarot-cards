/* 挿絵・図解の場面。どれも自作（SVG/HTML）で、実写や外部素材は使っていない。
   各場面は E.scene(名前, (layer, p) => ({ frame(t) })) で登録し、p に時刻（秒・全編の絶対時刻）を受け取る。 */
(function () {
  const { svgEl, div, rise, win, prog, ease, easeOut, lerp, clamp, drawable, draw } = E.U;
  const GOLD = '#BB965B', WHITE = '#FAF8F4', PURPLE = '#443049';
  const full = layer => svgEl('svg', { class: 'full', viewBox: '0 0 1920 1080' }, layer);
  // 文字：[要素, 出る時刻, 消える時刻]
  function texts(layer, list) {
    return list.map(([html, a, b, style, cls]) => [div('stext ' + (cls || ''), html, layer, style || ''), a, b]);
  }
  function showTexts(t, arr, end) { arr.forEach(([el, a, b]) => rise(el, win(t, a, b ?? end, .7, .5))); }
  function bg(svg, id, stops, angle) {
    const d = svgEl('defs', {}, svg);
    d.innerHTML = `<linearGradient id="${id}" x1="0" y1="0" x2="${angle ? 1 : 0}" y2="${angle ? 0 : 1}">${stops.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join('')}</linearGradient>`;
    svgEl('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: `url(#${id})` }, svg);
  }
  // 人物のシルエット（頭と肩）
  function person(g, x, y, s = 1, face = 0) {
    const p = svgEl('g', { transform: `translate(${x},${y}) scale(${s})` }, g);
    svgEl('circle', { cx: face * 4, cy: -150, r: 38, fill: '#2a2034', stroke: GOLD, 'stroke-width': 2 }, p);
    svgEl('path', { d: 'M-78,0 C-76,-62 -48,-96 0,-98 C48,-96 76,-62 78,0 Z', fill: '#2a2034', stroke: GOLD, 'stroke-width': 2 }, p);
    return p;
  }
  let uid = 0;

  /* 夜空（あいさつ・締め）：新月の暗い円に細い光の縁 */
  E.scene('sky', (layer, p) => {
    const svg = full(layer), id = 'sky' + (uid++);
    const d = svgEl('defs', {}, svg);
    d.innerHTML = `<linearGradient id="${id}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0916"/><stop offset=".6" stop-color="#1c1430"/><stop offset="1" stop-color="#2a1d36"/></linearGradient>
      <radialGradient id="${id}h" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#BB965B" stop-opacity=".22"/><stop offset="1" stop-color="#BB965B" stop-opacity="0"/></radialGradient>`;
    svgEl('rect', { width: 1920, height: 1080, fill: `url(#${id}g)` }, svg);
    const moonG = svgEl('g', {}, svg);
    svgEl('circle', { cx: 1400, cy: 330, r: 260, fill: `url(#${id}h)` }, moonG);
    svgEl('circle', { cx: 1400, cy: 330, r: 92, fill: '#0e0b18', stroke: 'rgba(187,150,91,.55)', 'stroke-width': 1.5 }, moonG);
    svgEl('path', { d: 'M1400,238 A92,92 0 0 1 1400,422 A70,92 0 0 0 1400,238 Z', fill: 'rgba(240,214,154,.10)' }, moonG);
    const hills = svgEl('path', { d: 'M0,860 C220,800 420,820 640,790 C860,760 1060,812 1280,800 C1500,788 1700,760 1920,790 L1920,1080 L0,1080 Z', fill: '#0c0a14' }, svg);
    svgEl('path', { d: 'M0,920 C300,880 520,900 780,880 C1040,860 1300,905 1560,890 C1720,880 1840,870 1920,880 L1920,1080 L0,1080 Z', fill: '#08070e' }, svg);
    const T = texts(layer, p.texts || []);
    return { frame(t) {
      const k = (t - (p.a || 0));
      moonG.setAttribute('transform', `translate(${(-k * 3).toFixed(1)},${(k * 1.2).toFixed(1)})`);
      hills.setAttribute('transform', `translate(${(-k * 1.2).toFixed(1)},0)`);
      showTexts(t, T, p.b);
    } };
  });

  /* 表紙（冒頭）：サムネイルと同じ画面。チャートは計算値から作図（thumbnail/thumbnail.html と同じ配置を 1920x1080 に拡大） */
  E.scene('cover', (layer, p) => {
    div('', '', layer, `position:absolute;inset:0;background:radial-gradient(ellipse 60% 80% at 78% 55%, rgba(68,48,73,.95) 0%, rgba(68,48,73,0) 70%),radial-gradient(ellipse 90% 100% at 20% 40%, #1d1530 0%, #0e0b18 100%)`);
    const svg = full(layer);
    const API = Chart.make(window.CHARTS.nm);
    const wrap = svgEl('g', {}, svg), g = svgEl('g', {}, wrap), a = svgEl('g', {}, wrap);
    const refs = API.build(g);
    const [vx, vy] = API.pt(API.lonOf('venus'), API.R.asp), [mx, my] = API.pt(API.lonOf('mars'), API.R.asp);
    const ln = drawable(svgEl('line', { x1: vx, y1: vy, x2: mx, y2: my, stroke: GOLD, 'stroke-width': 6, 'stroke-linecap': 'round' }, a));
    const dots = [[vx, vy], [mx, my]].map(([x, y]) => svgEl('circle', { cx: x, cy: y, r: 9, fill: GOLD, opacity: 0 }, a));
    const box = div('cover-copy', `<div class="cv-date">10.11<small>（日）0:50</small></div><div class="cv-title"><span>天秤座</span>新月</div>
      <div class="cv-rule"></div><div class="cv-tag">関係を、結び直す。</div><div class="cv-chip">金星逆行 <span class="g">♀□♂</span> 0°12′</div>`, layer);
    const parts = ['.cv-date', '.cv-title', '.cv-tag', '.cv-chip'].map(q => box.querySelector(q));
    const rule = box.querySelector('.cv-rule');
    const at = p.at || {}, sf = p.soft; // soft：{ date, title, rule, tag, chip }（出るのにかける秒）。あれば、ゆっくりふんわり出す
    if (sf) parts.forEach(el => { el.style.transformOrigin = '0 50%'; });
    // ふんわり出す：薄く・ぼんやり・少し小さい → くっきり・等倍（上下にはほとんど動かさない）
    const bloom = (el, q) => {
      const v = .5 - .5 * Math.cos(Math.PI * q), o = 1 - Math.pow(1 - q, 3);
      el.style.opacity = v.toFixed(3); el.style.visibility = v > 0 ? 'visible' : 'hidden';
      el.style.filter = q < 1 ? `blur(${(12 * (1 - q) * (1 - q)).toFixed(2)}px)` : 'none';
      el.style.transform = `translateY(${((1 - o) * 8).toFixed(2)}px) scale(${(.965 + .035 * o).toFixed(4)})`;
    };
    return { frame(t) {
      const k = t - p.a;
      const s = 1.2 + k * .004;
      wrap.setAttribute('transform', `translate(1602,543) scale(${s.toFixed(4)})`);
      const hl = ease(prog(t, at.halo ?? p.a + 1, 1));
      ['sun', 'moon', 'venus', 'mars'].forEach(q => { refs.planet[q].halo.setAttribute('stroke-opacity', hl.toFixed(3)); refs.planet[q].halo.setAttribute('fill-opacity', (hl * .6).toFixed(3)); });
      refs.signSeg[6].setAttribute('fill-opacity', (.7 * hl).toFixed(3));
      draw(ln, ease(prog(t, at.line ?? p.a + 1.6, 1.2)));
      dots.forEach((d, i) => d.setAttribute('opacity', ease(prog(t, (at.line ?? p.a + 1.6) + i * 1, .35)).toFixed(3)));
      [at.date ?? p.a + .2, at.title ?? p.a + .5, at.tag ?? p.a + 1.2, at.chip ?? p.a + 1.8].forEach((a0, i) => {
        if (sf) bloom(parts[i], prog(t, a0, sf[['date', 'title', 'tag', 'chip'][i]]));
        else rise(parts[i], ease(prog(t, a0, .8)), 14);
      });
      rule.style.transform = `scaleX(${ease(sf ? prog(t, at.rule, sf.rule) : prog(t, (at.tag ?? p.a + 1.2) - .3, .9)).toFixed(3)})`;
    } };
  });

  /* 太陽・地球・月の並び（新月＝同じ方向／満月＝180°） */
  E.scene('align', (layer, p) => {
    const svg = full(layer), id = 'al' + (uid++);
    const d = svgEl('defs', {}, svg);
    d.innerHTML = `<radialGradient id="${id}s"><stop offset="0" stop-color="#f3d9a4"/><stop offset=".25" stop-color="#BB965B" stop-opacity=".9"/><stop offset="1" stop-color="#BB965B" stop-opacity="0"/></radialGradient>
      <linearGradient id="${id}m" x1="0" x2="1"><stop offset=".5" stop-color="#FAF8F4"/><stop offset=".5" stop-color="#2a2034"/></linearGradient>`;
    const SX = 330, SY = 520, EX = 1180, EY = 520, RO = 210;
    svgEl('circle', { cx: SX, cy: SY, r: 230, fill: `url(#${id}s)` }, svg);
    svgEl('circle', { cx: SX, cy: SY, r: 70, fill: '#f0d69a' }, svg);
    svgEl('circle', { cx: EX, cy: EY, r: RO, fill: 'none', stroke: 'rgba(250,248,244,.25)', 'stroke-dasharray': '4 8' }, svg);
    const sightS = svgEl('line', { x1: EX, y1: EY, x2: SX + 90, y2: SY, stroke: GOLD, 'stroke-width': 2, 'stroke-dasharray': '8 8' }, svg);
    const sightM = svgEl('line', { x1: EX, y1: EY, x2: EX, y2: EY, stroke: WHITE, 'stroke-width': 2 }, svg);
    const angArc = svgEl('path', { fill: 'none', stroke: GOLD, 'stroke-width': 3 }, svg);
    const angTx = svgEl('text', { class: 'deg-label', 'text-anchor': 'middle' }, svg); angTx.style.fontSize = '34px';
    svgEl('circle', { cx: EX, cy: EY, r: 44, fill: '#2c3a5c', stroke: WHITE, 'stroke-width': 2 }, svg);
    const moon = svgEl('circle', { r: 34, fill: `url(#${id}m)`, stroke: 'rgba(250,248,244,.6)', 'stroke-width': 1.5 }, svg);
    const lab = (x, y, s) => { const e = svgEl('text', { x, y, class: 'deg-label', 'text-anchor': 'middle' }, svg); e.style.fontSize = '26px'; e.textContent = s; return e; };
    lab(SX, SY + 140, '太陽'); lab(EX, EY + 90, '地球');
    const mLab = lab(0, 0, '月');
    const T = texts(layer, p.texts || []);
    return { frame(t) {
      const K = p.keys || [[p.a, 0]];
      let th = K[0][1];
      for (let i = 1; i < K.length; i++) if (t >= K[i - 1][0]) th = lerp(K[i - 1][1], K[i][1], ease(prog(t, K[i - 1][0], K[i][0] - K[i - 1][0])));
      const r = th * Math.PI / 180;
      const mx = EX - RO * Math.cos(r), my = EY - RO * Math.sin(r);
      moon.setAttribute('cx', mx); moon.setAttribute('cy', my);
      mLab.setAttribute('x', mx); mLab.setAttribute('y', my + (Math.sin(r) > .3 ? -52 : 70));
      sightM.setAttribute('x2', EX + (mx - EX) * 1.0); sightM.setAttribute('y2', EY + (my - EY) * 1.0);
      const a1 = Math.PI, a2 = Math.PI + r; // 太陽の方向から月の方向へ
      const rr = 90, x1 = EX + rr * Math.cos(a1), y1 = EY + rr * Math.sin(a1), x2 = EX + rr * Math.cos(a2), y2 = EY + rr * Math.sin(a2);
      angArc.setAttribute('d', th < 1 ? '' : `M${x1},${y1} A${rr},${rr} 0 ${th > 180 ? 1 : 0} 1 ${x2},${y2}`);
      angTx.setAttribute('x', EX - 150); angTx.setAttribute('y', EY - 120);
      angTx.textContent = `太陽と月の差 ${Math.round(th)}°`;
      showTexts(t, T, p.b);
    } };
  });

  /* 月の満ち欠けの輪 */
  function phasePath(cx, cy, r, f) {
    const k = Math.cos(2 * Math.PI * f), rx = Math.abs(r * k);
    const right = f < .5;
    if (f < .001 || f > .999) return '';
    const s1 = right ? 1 : 0;
    const bulgeOut = (right && f < .25) || (!right && f > .75);
    const s2 = bulgeOut ? (right ? 0 : 1) : (right ? 1 : 0);
    return `M${cx},${cy - r} A${r},${r} 0 0 ${s1} ${cx},${cy + r} A${rx},${r} 0 0 ${s2} ${cx},${cy - r} Z`;
  }
  E.scene('cycle', (layer, p) => {
    const svg = full(layer), CX = 960, CY = 520, RR = 300;
    svgEl('circle', { cx: CX, cy: CY, r: RR, fill: 'none', stroke: 'rgba(187,150,91,.35)', 'stroke-width': 2 }, svg);
    for (let i = 0; i < 8; i++) {
      const f = i / 8, a = -Math.PI / 2 + f * 2 * Math.PI, x = CX + RR * Math.cos(a), y = CY + RR * Math.sin(a);
      svgEl('circle', { cx: x, cy: y, r: 30, fill: '#1a1426', stroke: 'rgba(250,248,244,.35)', 'stroke-width': 1.2 }, svg);
      if (i === 4) svgEl('circle', { cx: x, cy: y, r: 30, fill: '#ece5d6' }, svg);
      else svgEl('path', { d: phasePath(x, y, 30, f), fill: '#ece5d6' }, svg);
    }
    const trail = svgEl('path', { d: `M${CX},${CY - RR} A${RR},${RR} 0 0 1 ${CX},${CY + RR}`, fill: 'none', stroke: GOLD, 'stroke-width': 5 }, svg);
    drawable(trail);
    const dot = svgEl('circle', { r: 12, fill: '#f3d9a4' }, svg);
    const ring = svgEl('circle', { cx: CX, cy: CY - RR, r: 48, fill: 'none', stroke: GOLD, 'stroke-width': 2.5 }, svg);
    const T = texts(layer, p.texts || []);
    return { frame(t) {
      const q = ease(prog(t, p.moveA, p.moveB - p.moveA));
      draw(trail, q);
      const a = -Math.PI / 2 + q * Math.PI;
      dot.setAttribute('cx', CX + RR * Math.cos(a)); dot.setAttribute('cy', CY + RR * Math.sin(a));
      ring.setAttribute('stroke-opacity', (.6 + .4 * Math.sin(t * 2)).toFixed(2));
      showTexts(t, T, p.b);
    } };
  });

  /* 天秤と二人（役割の釣り合い） */
  E.scene('balance', (layer, p) => {
    const svg = full(layer);
    const g = svgEl('g', {}, svg);
    svgEl('line', { x1: 420, y1: 860, x2: 1500, y2: 860, stroke: GOLD, 'stroke-width': 2 }, g);
    person(g, 560, 860, 1.25, 1); person(g, 1360, 860, 1.25, -1);
    const PX = 960, PY = 300;
    svgEl('line', { x1: PX, y1: PY, x2: PX, y2: 640, stroke: GOLD, 'stroke-width': 3 }, g);
    svgEl('path', { d: `M${PX - 70},650 L${PX + 70},650`, stroke: GOLD, 'stroke-width': 3 }, g);
    const beam = svgEl('g', {}, g);
    svgEl('line', { x1: -260, y1: 0, x2: 260, y2: 0, stroke: GOLD, 'stroke-width': 4, 'stroke-linecap': 'round' }, beam);
    svgEl('circle', { cx: 0, cy: 0, r: 10, fill: GOLD }, beam);
    const panL = svgEl('g', {}, g), panR = svgEl('g', {}, g);
    [panL, panR].forEach(pg => {
      svgEl('path', { d: 'M-70,110 L0,0 L70,110', fill: 'none', stroke: 'rgba(187,150,91,.7)', 'stroke-width': 1.5 }, pg);
      svgEl('path', { d: 'M-80,110 Q0,150 80,110 Z', fill: '#2a2034', stroke: GOLD, 'stroke-width': 2 }, pg);
    });
    const tagL = div('tag-s', p.tagL || '調整役', layer), tagR = div('tag-s', p.tagR || '決める', layer);
    const T = texts(layer, p.texts || []);
    return { frame(t) {
      const tilt0 = p.tilt ?? 14;
      const tilt = lerp(0, tilt0, ease(prog(t, p.tiltA, 1.6))) * (1 - ease(prog(t, p.levelA, 2.2)));
      const r = tilt * Math.PI / 180;
      beam.setAttribute('transform', `translate(${PX},${PY}) rotate(${tilt})`);
      const lx = PX - 260 * Math.cos(r), ly = PY - 260 * Math.sin(r), rx = PX + 260 * Math.cos(r), ry = PY + 260 * Math.sin(r);
      panL.setAttribute('transform', `translate(${lx},${ly})`); panR.setAttribute('transform', `translate(${rx},${ry})`);
      tagL.style.left = (lx - 70) + 'px'; tagL.style.top = (ly + 58) + 'px'; rise(tagL, win(t, p.tagLA, p.b, .6, .5), 8);
      tagR.style.left = (rx - 70) + 'px'; tagR.style.top = (ry + 58) + 'px'; rise(tagR, win(t, p.tagRA, p.b, .6, .5), 8);
      showTexts(t, T, p.b);
    } };
  });

  /* 二人の会話（ふだんのやりとり） */
  E.scene('talk', (layer, p) => {
    const svg = full(layer), id = 'tk' + (uid++);
    const d = svgEl('defs', {}, svg);
    d.innerHTML = `<radialGradient id="${id}w" cx=".5" cy=".4" r=".6"><stop offset="0" stop-color="#BB965B" stop-opacity="${p.warm ? .32 : .16}"/><stop offset="1" stop-color="#BB965B" stop-opacity="0"/></radialGradient>`;
    svgEl('rect', { x: 760, y: 150, width: 400, height: 320, fill: '#161022', stroke: 'rgba(187,150,91,.5)', 'stroke-width': 2 }, svg);
    svgEl('line', { x1: 960, y1: 150, x2: 960, y2: 470, stroke: 'rgba(187,150,91,.4)' }, svg);
    svgEl('line', { x1: 760, y1: 310, x2: 1160, y2: 310, stroke: 'rgba(187,150,91,.4)' }, svg);
    svgEl('circle', { cx: 960, cy: 560, r: 520, fill: `url(#${id}w)` }, svg);
    const g = svgEl('g', {}, svg);
    svgEl('path', { d: 'M470,820 L1450,820', stroke: GOLD, 'stroke-width': 2 }, g);
    person(g, 640, 820, 1.2, 1); person(g, 1280, 820, 1.2, -1);
    svgEl('rect', { x: 900, y: 790, width: 38, height: 28, rx: 3, fill: 'none', stroke: GOLD, 'stroke-width': 1.5 }, g);
    svgEl('path', { d: 'M990,818 L1000,782 L1030,782 L1022,818 Z', fill: 'none', stroke: GOLD, 'stroke-width': 1.5 }, g);
    const dots = [0, 1, 2].map(i => svgEl('circle', { cx: 920 + i * 40, cy: 640, r: 7, fill: WHITE }, svg));
    const T = texts(layer, p.texts || []);
    return { frame(t) {
      dots.forEach((dt, i) => dt.setAttribute('opacity', (.25 + .6 * Math.max(0, Math.sin(t * 2.4 - i * .8))).toFixed(2)));
      showTexts(t, T, p.b);
    } };
  });

  /* 窓明かり（家庭・居場所） */
  E.scene('window', (layer, p) => {
    const svg = full(layer), id = 'wd' + (uid++);
    const d = svgEl('defs', {}, svg);
    d.innerHTML = `<radialGradient id="${id}l"><stop offset="0" stop-color="#f3d9a4" stop-opacity=".55"/><stop offset="1" stop-color="#BB965B" stop-opacity="0"/></radialGradient>`;
    svgEl('path', { d: 'M0,880 L1920,880 L1920,1080 L0,1080 Z', fill: '#0b0912' }, svg);
    svgEl('path', { d: 'M660,880 L660,520 L960,300 L1260,520 L1260,880 Z', fill: '#120e1a', stroke: 'rgba(187,150,91,.6)', 'stroke-width': 2 }, svg);
    const glow = svgEl('circle', { cx: 960, cy: 620, r: 300, fill: `url(#${id}l)` }, svg);
    svgEl('rect', { x: 880, y: 560, width: 160, height: 130, fill: '#e9c98c', opacity: .85 }, svg);
    svgEl('path', { d: 'M960,560 L960,690 M880,625 L1040,625', stroke: '#6b5234', 'stroke-width': 4 }, svg);
    svgEl('rect', { x: 720, y: 700, width: 90, height: 180, fill: 'none', stroke: 'rgba(187,150,91,.5)', 'stroke-width': 2 }, svg);
    const T = texts(layer, p.texts || []);
    return { frame(t) { glow.setAttribute('r', (300 + 8 * Math.sin(t * 1.3)).toFixed(1)); showTexts(t, T, p.b); } };
  });

  /* 古い写真や手紙を見返す */
  E.scene('letters', (layer, p) => {
    const svg = full(layer);
    const cards = [[-220, 40, -10], [-60, -20, -3], [110, 30, 6], [260, -10, 12]].map(([dx, dy, r], i) => {
      const g = svgEl('g', {}, svg);
      svgEl('rect', { x: -130, y: -95, width: 260, height: 190, fill: '#1b1428', stroke: GOLD, 'stroke-width': 2 }, g);
      if (i % 2 === 0) { svgEl('path', { d: 'M-110,60 L-40,-10 L10,40 L50,5 L110,60 Z', fill: 'none', stroke: 'rgba(250,248,244,.45)', 'stroke-width': 2 }, g); svgEl('circle', { cx: 60, cy: -45, r: 16, fill: 'none', stroke: 'rgba(250,248,244,.45)', 'stroke-width': 2 }, g); }
      else for (let k = 0; k < 5; k++) svgEl('line', { x1: -100, y1: -55 + k * 26, x2: 100 - (k === 4 ? 70 : 0), y2: -55 + k * 26, stroke: 'rgba(250,248,244,.4)', 'stroke-width': 2 }, g);
      return { g, dx, dy, r, hl: svgEl('rect', { x: -138, y: -103, width: 276, height: 206, fill: 'none', stroke: '#f3d9a4', 'stroke-width': 3, opacity: 0 }, g) };
    });
    const T = texts(layer, p.texts || []);
    return { frame(t) {
      const k = (t - p.a);
      cards.forEach((c, i) => {
        const sp = ease(prog(t, p.a + .3 + i * .25, 1.2));
        c.g.setAttribute('transform', `translate(${760 + c.dx * sp},${520 + c.dy * sp - 6 * Math.sin(k * .6 + i)}) rotate(${c.r * sp})`);
        const hi = (Math.floor(k / 2.2) % 4 === i) && k > 2 ? 1 : 0;
        c.hl.setAttribute('opacity', hi ? .9 : 0);
      });
      showTexts(t, T, p.b);
    } };
  });

  /* 金星の公転と、地球から見た見かけの逆行 */
  E.scene('orbit', (layer, p) => {
    const svg = full(layer), CX = 700, CY = 540, RV = 190, RE = 263, RB = 470;
    svgEl('circle', { cx: CX, cy: CY, r: RB, fill: 'none', stroke: 'rgba(187,150,91,.35)', 'stroke-width': 16 }, svg);
    svgEl('circle', { cx: CX, cy: CY, r: RV, fill: 'none', stroke: 'rgba(250,248,244,.25)', 'stroke-dasharray': '4 6' }, svg);
    svgEl('circle', { cx: CX, cy: CY, r: RE, fill: 'none', stroke: 'rgba(250,248,244,.25)', 'stroke-dasharray': '4 6' }, svg);
    svgEl('circle', { cx: CX, cy: CY, r: 30, fill: '#f0d69a' }, svg);
    const trace = svgEl('path', { fill: 'none', stroke: '#BB965B', 'stroke-width': 6, 'stroke-linecap': 'round' }, svg);
    const traceR = svgEl('path', { fill: 'none', stroke: '#FAF8F4', 'stroke-width': 6, 'stroke-linecap': 'round' }, svg);
    const ray = svgEl('line', { stroke: 'rgba(243,217,164,.8)', 'stroke-width': 2, 'stroke-dasharray': '6 6' }, svg);
    const ven = svgEl('circle', { r: 14, fill: '#FAF8F4' }, svg), ear = svgEl('circle', { r: 18, fill: '#6f86b8' }, svg);
    const hit = svgEl('circle', { r: 11, fill: '#f3d9a4' }, svg);
    const lab = (s) => { const e = svgEl('text', { class: 'deg-label', 'text-anchor': 'middle' }, svg); e.style.fontSize = '24px'; e.textContent = s; return e; };
    const lv = lab('金星'), le = lab('地球'), ls = lab('太陽'); ls.setAttribute('x', CX); ls.setAttribute('y', CY + 62);
    const lb = lab('見かけの位置'); lb.style.fill = GOLD;
    const key = div('stext s', '<span style="color:#BB965B">━</span> 前へ進んで見える　<span style="color:#FAF8F4">━</span> 後ろへ戻って見える', layer, 'left:120px;top:960px;opacity:1;visibility:visible;font-size:22px');
    const pos = tau => {
      const th0 = -Math.PI / 2 - .9;
      const aV = th0 + 2 * Math.PI * tau / 224.7, aE = th0 + 2 * Math.PI * tau / 365.25;
      const V = [CX + RV * Math.cos(aV), CY + RV * Math.sin(aV)], Ep = [CX + RE * Math.cos(aE), CY + RE * Math.sin(aE)];
      const dx = V[0] - Ep[0], dy = V[1] - Ep[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L;
      const fx = Ep[0] - CX, fy = Ep[1] - CY, b = fx * ux + fy * uy, c = fx * fx + fy * fy - RB * RB, s = -b + Math.sqrt(b * b - c);
      return { V, E: Ep, H: [Ep[0] + ux * s, Ep[1] + uy * s] };
    };
    const T = texts(layer, p.texts || []);
    return { frame(t) {
      const q = prog(t, p.a + .4, (p.b - p.a) - 1.2);
      const tau = lerp(-52, 52, q);
      const cur = pos(tau);
      let dP = '', dR = '', prevA = null, prevP = null;
      for (let k = 0; k <= 90; k++) {
        const tt = lerp(-52, tau, k / 90), H = pos(tt).H, ang = Math.atan2(H[1] - CY, H[0] - CX), rr = RB - 36 + 72 * (tt + 52) / 104;
        const P = [CX + rr * Math.cos(ang), CY + rr * Math.sin(ang)];
        if (prevP) { const back = ((ang - prevA + 3 * Math.PI) % (2 * Math.PI)) - Math.PI < 0; const seg = `M${prevP[0].toFixed(1)},${prevP[1].toFixed(1)}L${P[0].toFixed(1)},${P[1].toFixed(1)}`; if (back) dR += seg; else dP += seg; }
        prevA = ang; prevP = P;
      }
      trace.setAttribute('d', dP); traceR.setAttribute('d', dR);
      if (prevP) { hit.setAttribute('cx', prevP[0]); hit.setAttribute('cy', prevP[1]); }
      ven.setAttribute('cx', cur.V[0]); ven.setAttribute('cy', cur.V[1]); ear.setAttribute('cx', cur.E[0]); ear.setAttribute('cy', cur.E[1]);
      ray.setAttribute('x1', cur.E[0]); ray.setAttribute('y1', cur.E[1]); ray.setAttribute('x2', cur.H[0]); ray.setAttribute('y2', cur.H[1]);
      lv.setAttribute('x', cur.V[0]); lv.setAttribute('y', cur.V[1] - 26); le.setAttribute('x', cur.E[0]); le.setAttribute('y', cur.E[1] + 44);
      lb.setAttribute('x', +hit.getAttribute('cx') - 40); lb.setAttribute('y', +hit.getAttribute('cy') - 30);
      showTexts(t, T, p.b);
    } };
  });

  /* 水と火（蠍座の金星／獅子座の火星）、湖面の月 */
  function lakeParts(svg, cx, horizon, w, id) {
    const d = svgEl('defs', {}, svg);
    d.innerHTML = `<radialGradient id="${id}g"><stop offset="0" stop-color="#FAF8F4" stop-opacity=".38"/><stop offset=".3" stop-color="#FAF8F4" stop-opacity=".09"/><stop offset="1" stop-color="#FAF8F4" stop-opacity="0"/></radialGradient>
      <radialGradient id="${id}f" cx=".42" cy=".4" r=".7"><stop offset="0" stop-color="#fffdf7"/><stop offset=".7" stop-color="#ece5d6"/><stop offset="1" stop-color="#d9d0bd"/></radialGradient>
      <radialGradient id="${id}r" cx=".5" cy=".15" r=".8"><stop offset="0" stop-color="#FAF8F4" stop-opacity=".09"/><stop offset=".5" stop-color="#FAF8F4" stop-opacity=".03"/><stop offset="1" stop-color="#FAF8F4" stop-opacity="0"/></radialGradient>`;
    svgEl('circle', { cx, cy: horizon - 300, r: 260, fill: `url(#${id}g)` }, svg);
    svgEl('circle', { cx, cy: horizon - 300, r: 54, fill: `url(#${id}f)` }, svg);
    svgEl('line', { x1: cx - w / 2, y1: horizon, x2: cx + w / 2, y2: horizon, stroke: 'rgba(250,248,244,.18)' }, svg);
    const glow = svgEl('ellipse', { cx, cy: horizon + 180, rx: 170, ry: 280, fill: `url(#${id}r)` }, svg);
    const g = svgEl('g', {}, svg), R = [];
    let sd = 7 + uid; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
    for (let i = 0; i < 46; i++) {
      const k = i / 46, y = horizon + 12 + k * k * 360 + rnd() * 6;
      R.push({ y, k, w: 10 + rnd() * (18 + k * 70), off: (rnd() - .5) * (30 + k * 110), ph: rnd() * 6, jit: (rnd() - .5), n: svgEl('line', { y1: y, y2: y, stroke: '#FAF8F4', 'stroke-width': 1 + k * 1.6, 'stroke-linecap': 'round' }, g) });
    }
    return (t, amp = 1) => {
      R.forEach(r => {
        const spread = 1 + (amp - 1) * 2.2;
        const s = Math.sin(t * (.8 + amp * .6) + r.ph) * (4 + r.k * 10) * amp + r.jit * 160 * Math.max(0, amp - 1);
        const w = r.w * (.75 + .25 * Math.sin(t * .6 + r.ph * 2));
        r.n.setAttribute('x1', cx + r.off * spread - w / 2 + s); r.n.setAttribute('x2', cx + r.off * spread + w / 2 + s);
        r.n.setAttribute('stroke-opacity', ((.55 - r.k * .4) * (.6 + .4 * Math.sin(t * 1.3 + r.ph * 3)) / Math.max(1, amp * .8)).toFixed(3));
      });
      glow.setAttribute('opacity', clamp(1.4 - amp * .5).toFixed(2));
    };
  }
  function fireParts(svg, cx, base, id) {
    const d = svgEl('defs', {}, svg);
    d.innerHTML = `<radialGradient id="${id}fg"><stop offset="0" stop-color="#e7b56a" stop-opacity=".75"/><stop offset=".3" stop-color="#BB965B" stop-opacity=".35"/><stop offset="1" stop-color="#443049" stop-opacity="0"/></radialGradient>
      <linearGradient id="${id}fl" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#f3d7a0"/><stop offset=".5" stop-color="#d9a55c"/><stop offset="1" stop-color="#BB965B" stop-opacity="0"/></linearGradient>`;
    const fg = svgEl('circle', { cx, cy: base - 90, r: 340, fill: `url(#${id}fg)` }, svg);
    const FL = [[0, 150, 1], [-46, 110, .8], [48, 118, .85], [-18, 80, .6], [22, 86, .6]].map(([dx, h, o], i) => ({ dx, h, ph: i * 1.7, n: svgEl('path', { fill: `url(#${id}fl)`, 'fill-opacity': o }, svg) }));
    const EM = []; for (let i = 0; i < 18; i++) EM.push({ x0: cx + ((i * 73) % 160) - 80, sp: 40 + (i * 37) % 50, ph: (i * .618) % 1, n: svgEl('circle', { r: 2 + (i % 3), fill: '#e7c48a' }, svg) });
    return t => {
      FL.forEach(f => { const k = 1 + .05 * Math.sin(t * 5.1 + f.ph) + .03 * Math.sin(t * 8.3 + f.ph * 2), h = f.h * k, x = cx + f.dx, y = base;
        f.n.setAttribute('d', `M${x - h * .32},${y} C${x - h * .36},${y - h * .5} ${x - h * .06},${y - h * .7} ${x},${y - h} C${x + h * .06},${y - h * .7} ${x + h * .36},${y - h * .5} ${x + h * .32},${y} Z`); });
      fg.setAttribute('r', (340 + 14 * Math.sin(t * 3.3)).toFixed(1));
      EM.forEach(e => { const q = (t * e.sp / 500 + e.ph) % 1; e.n.setAttribute('cx', e.x0 + Math.sin(q * 6 + e.ph * 9) * 18); e.n.setAttribute('cy', base - 20 - q * 520); e.n.setAttribute('opacity', (Math.sin(q * Math.PI) * .8).toFixed(3)); });
    };
  }
  E.scene('elem', (layer, p) => {
    const svg = full(layer), id = 'el' + (uid++);
    bg(svg, id + 'b', [[0, '#15142b'], [.55, '#1f1c3a'], [1, '#0c0b18']]);
    svgEl('rect', { x: 960, y: 0, width: 960, height: 1080, fill: '#150f18' }, svg);
    const lake = lakeParts(svg, 700, 600, 960, id + 'l');
    const fire = fireParts(svg, 1440, 780, id);
    svgEl('line', { x1: 960, y1: 120, x2: 960, y2: 960, stroke: GOLD, 'stroke-width': 1.5, 'stroke-opacity': .8 }, svg);
    svgEl('rect', { x: 936, y: 516, width: 48, height: 48, fill: '#120e1c', stroke: GOLD, 'stroke-width': 1.5 }, svg);
    const tx = svgEl('text', { x: 960, y: 541, 'text-anchor': 'middle', 'dominant-baseline': 'central', class: 'deg-label' }, svg); tx.style.fontSize = '20px'; tx.textContent = '90°';
    const T = texts(layer, p.texts || []);
    return { frame(t) { lake(t, 1); fire(t); showTexts(t, T, p.b); } };
  });
  E.scene('lake', (layer, p) => {
    const svg = full(layer), id = 'lk' + (uid++);
    bg(svg, id + 'b', [[0, '#12112a'], [.55, '#1e1b38'], [1, '#0a0914']]);
    const lake = lakeParts(svg, p.cx ?? 960, 600, 1920, id);
    const T = texts(layer, p.texts || []);
    return { frame(t) {
      let amp = 1;
      if (p.amp) { amp = p.amp[0][1]; for (let i = 1; i < p.amp.length; i++) { const [ta, va] = p.amp[i - 1], [tb, vb] = p.amp[i]; if (t >= ta) amp = lerp(va, vb, ease(prog(t, ta, tb - ta))); } }
      lake(t, amp); showTexts(t, T, p.b);
    } };
  });
  E.scene('hearth', (layer, p) => {
    const svg = full(layer), id = 'ht' + (uid++);
    bg(svg, id + 'b', [[0, '#1a1220'], [1, '#0d0910']]);
    const fire = fireParts(svg, 1300, 800, id);
    const T = texts(layer, p.texts || []);
    return { frame(t) { fire(t); showTexts(t, T, p.b); } };
  });

  /* サビアンの挿絵：天秤座18度（二人が灯りの下で説明する）、牡羊座4度（小道を歩く二人） */
  function menScene(g, cx, s) {
    const lamp = svgEl('path', { d: `M${cx - 240 * s},${820 * s + 0} L${cx - 40 * s},${250} L${cx + 40 * s},${250} L${cx + 240 * s},${820}`, fill: 'rgba(243,217,164,.08)' }, g);
    svgEl('line', { x1: cx, y1: 150, x2: cx, y2: 240, stroke: GOLD, 'stroke-width': 2 }, g);
    svgEl('path', { d: `M${cx - 44},250 L${cx + 44},250 L${cx + 26},224 L${cx - 26},224 Z`, fill: '#2a2034', stroke: GOLD, 'stroke-width': 2 }, g);
    person(g, cx - 110 * s, 820, 1.05 * s, 1); person(g, cx + 110 * s, 820, 1.05 * s, -1);
    svgEl('path', { d: `M${cx - 330 * s},820 L${cx + 330 * s},820`, stroke: GOLD, 'stroke-width': 2 }, g);
    return lamp;
  }
  function loversScene(g, cx, s) {
    svgEl('path', { d: `M${cx - 60 * s},820 C${cx - 20 * s},700 ${cx + 40 * s},640 ${cx + 10 * s},520`, fill: 'none', stroke: 'rgba(187,150,91,.5)', 'stroke-width': 40 * s, 'stroke-linecap': 'round', opacity: .35 }, g);
    for (const [dx, h] of [[-250, 260], [-190, 200], [210, 240], [270, 300]]) {
      svgEl('path', { d: `M${cx + dx * s},820 L${cx + dx * s},${820 - h * .4 * s} M${cx + dx * s - 50 * s},${820 - h * .4 * s} L${cx + dx * s},${820 - h * s} L${cx + dx * s + 50 * s},${820 - h * .4 * s} Z`, fill: '#1c2a24', stroke: 'rgba(187,150,91,.6)', 'stroke-width': 2 }, g);
    }
    person(g, cx - 45 * s, 800, .78 * s, 1); person(g, cx + 45 * s, 800, .78 * s, -1);
    svgEl('path', { d: `M${cx - 330 * s},820 L${cx + 330 * s},820`, stroke: GOLD, 'stroke-width': 2 }, g);
  }
  E.scene('sabian', (layer, p) => {
    const svg = full(layer); const g = svgEl('g', {}, svg);
    if (p.kind === 'lovers') loversScene(g, p.cx ?? 700, 1); else menScene(g, p.cx ?? 700, 1);
    const T = texts(layer, p.texts || []);
    return { frame(t) { showTexts(t, T, p.b); } };
  });
  E.scene('pair', (layer, p) => {
    const svg = full(layer), id = 'pr' + (uid++);
    svgEl('line', { x1: 960, y1: 140, x2: 960, y2: 900, stroke: GOLD, 'stroke-width': 1.5, 'stroke-opacity': .7 }, svg);
    const left = svgEl('g', { transform: 'translate(480,90) scale(.8) translate(-480,0)' }, svg);
    const right = svgEl('g', { transform: 'translate(1440,90) scale(.8) translate(-480,0)' }, svg);
    let lakeFn = null;
    const put = (g, kind) => {
      if (kind === 'lovers') loversScene(g, 480, 1);
      else if (kind === 'men') menScene(g, 480, 1);
      else if (kind === 'lake') lakeFn = lakeParts(g, 480, 560, 1000, id);
    };
    put(left, p.left); put(right, p.right);
    const T = texts(layer, p.texts || []);
    return { frame(t) { if (lakeFn) lakeFn(t, 1); showTexts(t, T, p.b); } };
  });

  /* 手帳：書き出す問い・言い直し */
  E.scene('memo', (layer, p) => {
    const svg = full(layer);
    svgEl('rect', { x: 330, y: 150, width: 1260, height: 760, fill: '#1a1426', stroke: 'rgba(187,150,91,.6)', 'stroke-width': 2 }, svg);
    for (let i = 0; i < 9; i++) svgEl('line', { x1: 400, y1: 300 + i * 70, x2: 1520, y2: 300 + i * 70, stroke: 'rgba(250,248,244,.1)' }, svg);
    svgEl('line', { x1: 470, y1: 170, x2: 470, y2: 890, stroke: 'rgba(187,150,91,.35)' }, svg);
    const ttl = div('memo-t', p.title || '', layer, 'left:500px;top:190px');
    const L = (p.lines || []).map(ln => {
      const row = div('memo-l ' + (ln.cls || ''), `<span class="gl">${ln.glyph || ''}</span><span class="tx"><span class="in">${ln.text}</span></span>`, layer, `left:400px;top:${ln.y}px`);
      return { row, ln, inner: row.querySelector('.tx') };
    });
    return { frame(t) {
      rise(ttl, win(t, p.titleA ?? p.a, p.b, .7, .5));
      L.forEach(({ row, ln, inner }) => {
        const v = win(t, ln.a, ln.until ?? p.b, .4, .5); row.style.opacity = v.toFixed(3); row.style.visibility = v > 0 ? 'visible' : 'hidden';
        inner.style.clipPath = `inset(0 ${(100 - 100 * ease(prog(t, ln.a, ln.d ?? 2))).toFixed(1)}% 0 0)`;
        if (ln.strikeA) row.classList.toggle('struck', t >= ln.strikeA);
      });
    } };
  });

  /* スマホの画面（日常の例） */
  E.scene('phone', (layer, p) => {
    const ph = div('', `<div class="top">${p.who || '身近な人'}</div><div class="msgs"></div><div class="input"><span class="typed"></span><span class="cursor"></span></div>`, layer); ph.className = 'phone';
    const box = ph.querySelector('.msgs'), typed = ph.querySelector('.typed'), cur = ph.querySelector('.cursor');
    const M = (p.msgs || []).map(m => [div('msg ' + m.side, m.text, box, `top:${m.top}px`), m]);
    const G = (p.tags || []).map(tg => [div('tag', `<div class="gl">${tg.glyph}</div><div class="tx"><div class="a">${tg.head}</div><div class="b">${tg.body}</div></div>`, layer, `top:${tg.top}px`), tg]);
    let memo = null;
    if (p.memo) memo = div('memo', `<div class="t">${p.memo.title}</div><div class="l">${p.memo.line}<span class="u"></span></div>`, layer, `top:${p.memo.top || 600}px`);
    const note = div('note', '日常の例です。配置が出来事を決めるわけではありません。', layer);
    return { frame(t) {
      M.forEach(([e, m]) => rise(e, win(t, m.at, p.b + 1, .5, .1)));
      G.forEach(([e, tg]) => rise(e, win(t, tg.a, tg.b ?? p.b, .7, .5)));
      let s = '';
      for (const ty of (p.typing || [])) {
        if (t < ty.a || t >= ty.b) continue;
        const n = Math.floor((t - ty.a) * (ty.cps || 7));
        s = ty.erase ? ty.text.slice(0, Math.max(0, ty.text.length - n)) : ty.text.slice(0, Math.min(ty.text.length, n));
        typed.style.fontWeight = ty.bold ? 700 : 400;
      }
      typed.textContent = s;
      cur.style.opacity = (Math.floor(t * 2) % 2 === 0) ? 1 : .15;
      if (memo) { memo.style.opacity = win(t, p.memo.a, p.memo.b ?? p.b, .7, .5).toFixed(3); memo.querySelector('.u').style.width = (ease(prog(t, p.memo.a + .6, 1.6)) * 100) + '%'; }
      note.style.opacity = win(t, p.a + .6, p.b, .8, .5).toFixed(3);
    } };
  });

  /* 時間軸（日付・時刻・期間） */
  E.scene('timeline', (layer, p) => {
    const svg = full(layer), X0 = p.x0 ?? 200, X1 = p.x1 ?? 1720;
    const X = v => X0 + (v - p.from) / (p.to - p.from) * (X1 - X0);
    const axes = (p.axes || [{ y: 560 }]).map(ax => {
      const ln = svgEl('line', { x1: X0, y1: ax.y, x2: X0, y2: ax.y, stroke: GOLD, 'stroke-width': 2.5 }, svg);
      const lab = ax.label ? div('tl-axis', ax.label, layer, `left:${X0}px;top:${ax.y - 58}px`) : null;
      return { ax, ln, lab };
    });
    const ticks = (p.ticks || []).map(tk => {
      const y = tk.y ?? (p.axes ? p.axes[0].y : 560);
      const l = svgEl('line', { x1: X(tk.v), y1: y - 10, x2: X(tk.v), y2: y + 10, stroke: GOLD, 'stroke-width': 2, opacity: 0 }, svg);
      const d = div('tl-tick', tk.label, layer, `left:${X(tk.v) - 100}px;top:${y + 20}px`);
      return { tk, l, d };
    });
    const ranges = (p.ranges || []).map(r => {
      const y = r.y;
      const rect = svgEl('rect', { x: X(r.v0), y: y - 8, width: 0, height: 16, fill: r.color || 'rgba(187,150,91,.45)' }, svg);
      const d = div('tl-range', r.label, layer, `left:${X(r.v0)}px;top:${y - 50}px`);
      return { r, rect, d };
    });
    const evs = (p.events || []).map(ev => {
      const y = ev.y ?? 560;
      const c = svgEl('circle', { cx: X(ev.v), cy: y, r: 0, fill: ev.gold === false ? WHITE : '#f3d9a4', stroke: '#0e0b18', 'stroke-width': 3 }, svg);
      const d = div('tl-ev' + (ev.below ? ' below' : ''), `<div class="d">${ev.label}</div><div class="s">${ev.sub || ''}</div>`, layer, `left:${X(ev.v) - 120}px;top:${ev.below ? y + 26 + (ev.drop || 0) : y - 118 - (ev.lift || 0)}px`);
      // ラベルを上下にずらしたときの引き出し線（ラベルと一緒に出す）
      const ln = (ev.lift || ev.drop) ? svgEl('line', { x1: X(ev.v), y1: y, x2: X(ev.v), y2: ev.below ? y + 26 + ev.drop : y - 30 - ev.lift, stroke: 'rgba(187,150,91,.5)', 'stroke-dasharray': '3 4', opacity: 0 }, svg) : null;
      return { ev, c, d, ln };
    });
    const T = texts(layer, p.texts || []);
    return { frame(t) {
      axes.forEach(({ ax, ln, lab }) => { const q = ease(prog(t, ax.at ?? p.a, 1.2)); ln.setAttribute('x2', X0 + (X1 - X0) * q); if (lab) rise(lab, win(t, ax.at ?? p.a, p.b, .6, .5)); });
      ticks.forEach(({ tk, l, d }) => { const v = win(t, tk.at ?? p.a + .6, p.b, .5, .5); l.setAttribute('opacity', v); rise(d, v, 6); });
      ranges.forEach(({ r, rect, d }) => { const q = ease(prog(t, r.at, 1.2)); rect.setAttribute('width', Math.max(0, (X(r.v1) - X(r.v0)) * q)); rect.setAttribute('opacity', win(t, r.at, r.until ?? p.b, .3, .5)); rise(d, win(t, r.at + .4, r.until ?? p.b, .6, .5)); });
      evs.forEach(({ ev, c, d, ln }) => { const v = win(t, ev.at, ev.until ?? p.b, .4, .5); c.setAttribute('r', (11 * easeOut(v)).toFixed(1)); rise(d, v, 10); d.classList.toggle('hl', ev.hlA !== undefined && t >= ev.hlA); if (ln) ln.setAttribute('opacity', v.toFixed(3)); });
      showTexts(t, T, p.b);
    } };
  });

  /* 期間の長さのイメージ（横棒） */
  E.scene('bars', (layer, p) => {
    const svg = full(layer);
    const B = p.bars.map((b, i) => {
      const y = 330 + i * 190;
      const r = svgEl('rect', { x: 420, y: y - 14, width: 0, height: 28, fill: b.color || GOLD, opacity: .85 }, svg);
      const d = div('bar-l', `<div class="a">${b.label}</div><div class="b">${b.sub || ''}</div>`, layer, `left:420px;top:${y - 116}px`);
      return { b, r, d };
    });
    const T = texts(layer, p.texts || []);
    return { frame(t) {
      B.forEach(({ b, r, d }) => { r.setAttribute('width', (b.w * ease(prog(t, b.at, 1.6))).toFixed(1)); rise(d, win(t, b.at, p.b, .6, .5)); if (b.pulse) r.setAttribute('opacity', (.6 + .35 * Math.sin(t * 3)).toFixed(2)); });
      showTexts(t, T, p.b);
    } };
  });

  /* 複数のチャートを並べる（満月との比較、東京とロンドン） */
  E.scene('charts', (layer, p) => {
    const insts = p.charts.map(c => {
      const inst = E.makeChart(c.id, window.CHARTS[c.data], layer, c.home);
      inst.noMask = !!p.noMask;
      return inst;
    });
    const T = texts(layer, p.texts || []);
    T.forEach(([el]) => { if (!/right:0/.test(el.style.cssText)) el.classList.add('bgd'); });
    return { frame(t) { insts.forEach(i => E.chartFrame(i, t)); showTexts(t, T, p.b); } };
  });
})();
