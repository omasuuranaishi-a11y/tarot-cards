/* 全編の仮編集エンジン
   台本の「単位」ごとに読む文を持ち、画面の動き（cue）を各文の開始時刻に結びつける。
   単位の長さ = 文字数 ÷ 5.5字/秒（毎分330字）＋ 図を見せる間（pad）。録音後は dur を実測に置き換える。
   window.render(t) で任意の時刻の1コマを描く（tools/render.mjs で書き出す）。 */
(function () {
  const W = 1920, H = 1080, NS = 'http://www.w3.org/2000/svg';
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const ease = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  const easeOut = x => 1 - Math.pow(1 - x, 3);
  const prog = (t, a, d) => d <= 0 ? (t >= a ? 1 : 0) : clamp((t - a) / d);
  const lerp = (a, b, p) => a + (b - a) * p;
  const win = (t, a, b, fi = .6, fo = .6) => (t < a || t > b) ? 0 : Math.min(ease(clamp((t - a) / fi)), ease(clamp((b - t) / fo)));
  function rise(node, v, dy = 12) {
    node.style.opacity = v.toFixed(3);
    node.style.transform = `translateY(${((1 - easeOut(v)) * dy).toFixed(2)}px)`;
    node.style.visibility = v > 0 ? 'visible' : 'hidden';
  }
  function svgEl(tag, attrs = {}, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function div(cls, html, parent, style) {
    const d = document.createElement('div');
    if (cls) d.className = cls;
    if (html) d.innerHTML = html;
    if (style) d.style.cssText = style;
    if (parent) parent.appendChild(d);
    return d;
  }
  function drawable(node) { const len = node.getTotalLength(); node.style.strokeDasharray = `${len} ${len}`; node.style.strokeDashoffset = len; node._len = len; return node; }
  function draw(node, p) { node.style.strokeDashoffset = (node._len * (1 - p)).toFixed(2); }
  const U = { clamp, ease, easeOut, prog, lerp, win, rise, svgEl, div, drawable, draw, W, H };

  const E = { RATE: 5.5, LEAD: .35, units: [], chapters: [], cues: [], scenes: {}, sceneCues: [], charts: {}, U };
  window.E = E;

  /* ---------- 時間 ---------- */
  function len(s) { return s.replace(/\s/g, '').length; }
  function mkT(u, ch) {
    const idx = k => k < 0 ? u.ss.length + k : k;
    return {
      a: u.start, b: u.end, chA: ch.start, chB: ch.end,
      s: k => u.ss[idx(k)], e: k => u.se[idx(k)],
      at: (k, f) => u.ss[idx(k)] + (u.se[idx(k)] - u.ss[idx(k)]) * f,
      u: off => { const v = ch.units[u.idx + off]; return v ? mkT(v, ch) : null; },
    };
  }
  E.build = function (chapters) {
    let t = 0;
    chapters.forEach(ch => {
      ch.start = t;
      ch.units.forEach((u, i) => {
        u.sent = u.text.split(/(?<=。)/).filter(s => s.trim());
        u.start = t; u.speech = len(u.text) / E.RATE;
        u.dur = E.LEAD + u.speech + (u.pad ?? 1.2); u.end = t + u.dur; t = u.end;
        let s0 = u.start + E.LEAD; u.ss = []; u.se = [];
        u.sent.forEach(s => { u.ss.push(s0); s0 += len(s) / E.RATE; u.se.push(s0); });
        u.ch = ch; u.idx = i; E.units.push(u);
      });
      ch.end = t;
    });
    E.DURATION = t; window.DURATION = t;
    E.chapters = chapters;
    chapters.forEach(ch => ch.units.forEach(u => (u.cues ? u.cues(mkT(u, ch)) : []).forEach(c => { c._u = u; E.cues.push(c); })));
    init();
  };

  /* ---------- チャート ---------- */
  const HOME = { fx: 0, fy: 0, s: .94, sx: 760, sy: 505 };
  E.HOME = HOME;
  function makeChart(id, data, layer, home) {
    const API = Chart.make(data);
    const svg = svgEl('svg', { class: 'full', viewBox: `0 0 ${W} ${H}` }, layer);
    const defs = svgEl('defs', {}, svg);
    defs.innerHTML = `<marker id="ah-${id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#BB965B"/></marker>`;
    const cam = svgEl('g', {}, svg);
    const base = svgEl('g', {}, cam), under = svgEl('g', {}, cam), ov = svgEl('g', {}, cam);
    const refs = API.build(base);
    base.insertBefore(under, base.querySelector('.houses')); // 塗りはハウス線の下
    const scr = svgEl('svg', { class: 'full', viewBox: `0 0 ${W} ${H}` }, layer);
    const html = div('overlay', '', layer);
    const inst = { id, API, svg, cam, ov, under, refs, scr, html, home: home || HOME, shots: [], items: [], panels: [], camNow: null };
    E.charts[id] = inst;
    return inst;
  }
  function lonKey(API, k) {
    const b = API.C.bodies;
    if (k === 'ic') return (b.mc.lon + 180) % 360;
    if (k === 'dsc') return (b.asc.lon + 180) % 360;
    return b[k].lon;
  }
  function resolve(inst, spec, rDef) {
    const { API, refs } = inst, R = API.R, r0 = rDef ?? R.asp;
    if (spec === 'center') return [0, 0];
    if (Array.isArray(spec)) return spec;
    if (typeof spec === 'string') return API.pt(lonKey(API, spec), r0);
    if (spec.g) return [refs.planet[spec.g].gx, refs.planet[spec.g].gy];
    if (spec.key) return API.pt(lonKey(API, spec.key), spec.r ?? r0);
    if (spec.lon !== undefined) return API.pt(spec.lon, spec.r ?? r0);
    return [0, 0];
  }
  function shotOf(inst, sh) {
    if (!sh || sh === 'home') return { ...inst.home };
    if (sh.focus) {
      const pts = sh.focus.map(k => inst.refs.planet[k] ? [inst.refs.planet[k].gx, inst.refs.planet[k].gy] : resolve(inst, k, inst.API.R.out));
      const fx = pts.reduce((s, p) => s + p[0], 0) / pts.length, fy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
      return { fx: fx + (sh.dx || 0), fy: fy + (sh.dy || 0), s: sh.s || 1.3, sx: sh.sx ?? 700, sy: sh.sy ?? 500 };
    }
    return { ...inst.home, ...sh };
  }
  function camAt(inst, t) {
    let c = { ...inst.home };
    for (const [a, d, tg] of inst.shots) {
      if (t < a) break;
      const p = ease(prog(t, a, d));
      c = { fx: lerp(c.fx, tg.fx, p), fy: lerp(c.fy, tg.fy, p), s: lerp(c.s, tg.s, p), sx: lerp(c.sx, tg.sx, p), sy: lerp(c.sy, tg.sy, p) };
    }
    return c;
  }
  const COLORS = { gold: '#BB965B', white: '#FAF8F4', purple: '#443049', dim: 'rgba(250,248,244,.55)' };
  function addChartCue(inst, c) {
    const { API } = inst, R = API.R, el = (t, a, p) => svgEl(t, a, p || inst.ov);
    const fo = c.fo ?? .6, fi = c.fi ?? .5;
    const vis = t => win(t, c.a, c.b, fi, fo);
    switch (c.k) {
      case 'cam': inst.shots.push([c.a, c.d ?? 2, shotOf(inst, c.shot)]); inst.shots.sort((x, y) => x[0] - y[0]); return;
      case 'halo': inst.items.push({ up: (t, acc) => c.keys.forEach(k => acc.halo[k] = Math.max(acc.halo[k] || 0, vis(t) * (c.v ?? 1))) }); return;
      case 'seg': inst.items.push({ up: (t, acc) => c.signs.forEach(i => acc.seg[i] = Math.max(acc.seg[i] || 0, vis(t) * (c.v ?? .75))) }); return;
      case 'house': {
        const cu = API.C.cusps, n = c.n;
        const p = el('path', { d: API.arcPath(R.asp, R.signIn, cu[n - 1], cu[n % 12]), fill: COLORS.purple, opacity: 0 }, inst.under);
        inst.items.push({ up: t => p.setAttribute('opacity', (vis(t) * (c.v ?? .55)).toFixed(3)) }); return;
      }
      case 'wedge': {
        const p = el('path', { d: API.arcPath(c.r1, c.r2, c.l1, c.l2), fill: COLORS[c.fill || 'gold'] || c.fill, opacity: 0 }, c.below ? inst.under : inst.ov);
        if (c.stroke) { p.setAttribute('stroke', COLORS[c.stroke] || c.stroke); p.setAttribute('stroke-width', 1.5); p.setAttribute('stroke-dasharray', '5 5'); }
        inst.items.push({ up: t => p.setAttribute('opacity', (vis(t) * (c.v ?? .8)).toFixed(3)) }); return;
      }
      case 'line': {
        const a = resolve(inst, c.p1, c.r), b = resolve(inst, c.p2, c.r);
        let d = `M${a[0]},${a[1]} L${b[0]},${b[1]}`;
        if (c.curve) { const mx = (a[0] + b[0]) / 2 * c.curve, my = (a[1] + b[1]) / 2 * c.curve; d = `M${a[0]},${a[1]} Q${mx},${my} ${b[0]},${b[1]}`; }
        const p = el('path', { d, fill: 'none', stroke: COLORS[c.color || 'gold'] || c.color, 'stroke-width': c.w ?? 3, 'stroke-linecap': 'round' });
        if (c.arrow) p.setAttribute('marker-end', `url(#ah-${inst.id})`);
        drawable(p);
        if (c.dash) { p.style.strokeDasharray = c.dash; p._dash = true; }
        let glow = null;
        if (c.glow) glow = el('path', { d, fill: 'none', stroke: COLORS.gold, 'stroke-width': (c.w ?? 3) * 3.2, 'stroke-linecap': 'round', opacity: 0 });
        inst.items.push({ up: t => {
          const v = vis(t);
          if (!p._dash) draw(p, ease(prog(t, c.a, c.draw ?? 1.2)));
          p.style.opacity = (p._dash ? v * ease(prog(t, c.a, .6)) : (t < c.a || t > c.b ? 0 : Math.min(1, win(t, c.a, c.b, .05, fo)))) * (c.op ?? 1);
          if (glow) glow.setAttribute('opacity', (win(t, c.glow[0], c.glow[1], .6, .6) * .28).toFixed(3));
        } });
        return;
      }
      case 'arc': {
        const p = el('path', { d: API.ringArc(c.r, c.l1, c.l2), fill: 'none', stroke: COLORS[c.color || 'gold'], 'stroke-width': c.w ?? 3 });
        drawable(p);
        let tx = null;
        if (c.label) {
          const mid = c.l1 + ((((c.l2 - c.l1) % 360) + 540) % 360 - 180) / 2;
          const [x, y] = API.pt(mid, c.r + (c.lr ?? 34));
          tx = el('text', { x, y, class: 'deg-label', 'text-anchor': 'middle', 'dominant-baseline': 'central' });
          tx.style.fontSize = (c.fs ?? 26) + 'px'; if (c.lc) tx.style.fill = COLORS[c.lc]; tx.textContent = c.label;
        }
        inst.items.push({ up: t => {
          const v = vis(t); draw(p, ease(prog(t, c.a, c.draw ?? 1))); p.style.opacity = v;
          if (tx) tx.setAttribute('opacity', (v * ease(prog(t, c.a + (c.draw ?? 1) * .7, .5))).toFixed(3));
        } });
        return;
      }
      case 'text': {
        const [x, y] = resolve(inst, c.p, c.r);
        const tx = el('text', { x, y, class: 'deg-label', 'text-anchor': c.anchor || 'middle', 'dominant-baseline': 'central', opacity: 0 });
        tx.style.fontSize = (c.fs ?? 26) + 'px'; if (c.color) tx.style.fill = COLORS[c.color] || c.color; tx.textContent = c.txt;
        inst.items.push({ up: t => tx.setAttribute('opacity', vis(t).toFixed(3)) }); return;
      }
      case 'poly': {
        const pts = c.pts.map(s => resolve(inst, s, c.r));
        const p = el('path', { d: 'M' + pts.map(q => q.join(',')).join('L') + 'Z', fill: COLORS[c.fill || 'gold'], stroke: 'none', opacity: 0 }, c.below ? inst.under : inst.ov);
        inst.items.push({ up: t => p.setAttribute('opacity', (vis(t) * (c.v ?? .18)).toFixed(3)) }); return;
      }
      case 'callout': {
        const box = div('callout', c.html, inst.html);
        const ld = svgEl('line', { stroke: COLORS.gold, 'stroke-width': 1.5, opacity: 0 }, inst.scr);
        const dot = svgEl('circle', { r: 5, fill: COLORS.gold, opacity: 0 }, inst.scr);
        inst.items.push({ up: (t, acc, proj) => {
          const v = vis(t); rise(box, v, 10);
          box.style.left = c.x + 'px'; box.style.top = c.y + 'px';
          if (v <= 0) { ld.setAttribute('opacity', 0); dot.setAttribute('opacity', 0); return; }
          if (c.anchor == null) { ld.setAttribute('opacity', 0); dot.setAttribute('opacity', 0); return; }
          const [ax, ay] = proj(resolve(inst, c.anchor, c.r));
          const w = box.offsetWidth, h = box.offsetHeight;
          const bx = ax < c.x ? c.x : ax > c.x + w ? c.x + w : ax, by = ay < c.y ? c.y : ay > c.y + h ? c.y + h : c.y + h / 2;
          ld.setAttribute('x1', ax); ld.setAttribute('y1', ay); ld.setAttribute('x2', bx); ld.setAttribute('y2', by);
          ld.setAttribute('opacity', v * .9); dot.setAttribute('cx', ax); dot.setAttribute('cy', ay); dot.setAttribute('opacity', v);
        } });
        return;
      }
      case 'panel': {
        const pn = div('panel', `<div class="ph"></div>`, inst.html, c.style || '');
        const ph = pn.querySelector('.ph'); ph.innerHTML = c.title || '';
        const rows = (c.rows || []).map(([html, at, until]) => [div('row', html, pn), at, until]);
        const ctx = c.build ? c.build(pn, inst) : null;
        inst.panels.push(pn);
        inst.items.push({ up: t => {
          const v = win(t, c.a, c.b, .6, .5); pn.style.opacity = v.toFixed(3); pn.style.visibility = v > 0 ? 'visible' : 'hidden';
          if (v <= 0) return;
          rows.forEach(([r, at, until]) => rise(r, win(t, at, until ?? c.b, .7, .5)));
          if (c.titleAt) ph.innerHTML = c.titleAt(t);
          if (c.frame) c.frame(t, ctx, pn);
        } });
        return;
      }
    }
  }

  function chartFrame(inst, t) {
    const cam = camAt(inst, t); inst.camNow = cam;
    inst.cam.setAttribute('transform', `translate(${cam.sx},${cam.sy}) scale(${cam.s}) translate(${-cam.fx},${-cam.fy})`);
    const proj = ([x, y]) => [cam.sx + cam.s * (x - cam.fx), cam.sy + cam.s * (y - cam.fy)];
    const acc = { halo: {}, seg: {} };
    for (const it of inst.items) it.up(t, acc, proj);
    for (const k in inst.refs.planet) {
      const v = acc.halo[k] || 0, h = inst.refs.planet[k].halo;
      h.setAttribute('stroke-opacity', v.toFixed(3)); h.setAttribute('fill-opacity', (v * .6).toFixed(3));
    }
    inst.refs.signSeg.forEach((sg, i) => sg.setAttribute('fill-opacity', ((acc.seg[i] || 0) * .75).toFixed(3)));
    const pOn = Math.max(0, ...inst.panels.map(p => +p.style.opacity || 0));
    if (!inst.noMask) {
      const mx = lerp(2400, 1190, clamp(pOn * 1.4));
      inst.svg.style.webkitMaskImage = inst.svg.style.maskImage = `linear-gradient(90deg,#000 0,#000 ${mx}px,transparent ${mx + 110}px)`;
    }
  }
  E.chartFrame = chartFrame;
  E.makeChart = makeChart;
  E.addChartCue = addChartCue;

  /* ---------- 画面の組み立て ---------- */
  let stage, mainLayer, layers = [];
  function init() {
    stage = document.getElementById('stage');
    mainLayer = div('scene', '', stage);
    mainLayer.style.opacity = 1;
    makeChart('nm', window.CHARTS.nm, mainLayer, HOME);
    // 場面（挿絵・比較図）
    E.cues.filter(c => c.k === 'scene').forEach(c => {
      const layer = div('scene', '', stage);
      const obj = E.scenes[c.name](layer, c.p || {}, c) || {};
      layers.push({ c, layer, obj });
    });
    // チャートへの cue
    E.cues.filter(c => c.k !== 'scene').forEach(c => addChartCue(E.charts[c.on || 'nm'], c));
    // 共通の表示
    const hd = div('', `<span class="no"></span><span class="tt"></span><span class="rule"></span>`, stage); hd.id = 'heading';
    const bd = div('', '無音・仮タイミング ｜ 全編 v1', stage); bd.id = 'badge';
    const sb = div('', `<div id="subtext"></div>`, stage); sb.id = 'sub';
    // ワイプ：本人のアイコン（1080x1080）の顔まわりを丸く切り出し、口と目だけを重ねて動かす
    const FACE = '#FFFFFB', LINE = '#645F54', DARK = '#3D3C42';
    const wp = div('', `<div class="ring"><svg viewBox="290 205 500 500">
      <image href="${E.ICON || '../lib/icon.png'}" x="0" y="0" width="1080" height="1080"/>
      <g id="blink" opacity="0">
        <ellipse cx="442" cy="504" rx="26" ry="21" fill="${FACE}"/><ellipse cx="590" cy="503" rx="27" ry="22" fill="${FACE}"/>
        <path d="M419,509 Q442,522 465,509 M566,508 Q590,521 614,508" fill="none" stroke="${LINE}" stroke-width="7" stroke-linecap="round"/>
      </g>
      <ellipse cx="505" cy="584.5" rx="13" ry="10" fill="${FACE}"/>
      <ellipse id="mouth" cx="505" cy="585" rx="8" ry="4.5" fill="${LINE}"/>
      <ellipse id="mouthIn" cx="505" cy="586" rx="4.5" ry="0" fill="${DARK}"/>
    </svg></div><div class="nm">おます</div><div class="ph">口の動きは仮（音声未収録）</div>`, stage);
    wp.id = 'wipe';
  }

  window.render = function (t) {
    // 場面の見え方（0.8秒のクロスフェード）
    let maxV = 0, hideWipe = 0;
    for (const L of layers) {
      const v = win(t, L.c.a - .4, L.c.b + .4, .8, .8);
      L.layer.style.opacity = v.toFixed(3); L.layer.style.visibility = v > 0 ? 'visible' : 'hidden';
      if (v > 0 && L.obj.frame) L.obj.frame(t, v);
      maxV = Math.max(maxV, v);
      if (!(L.c.p && L.c.p.wipe)) hideWipe = Math.max(hideWipe, v);
    }
    const mv = clamp(1 - maxV);
    mainLayer.style.opacity = mv.toFixed(3); mainLayer.style.visibility = mv > 0 ? 'visible' : 'hidden';
    if (mv > 0) chartFrame(E.charts.nm, t);

    // 見出し
    const ch = E.chapters.find(c => t < c.end) || E.chapters[E.chapters.length - 1];
    const hd = document.getElementById('heading');
    hd.querySelector('.no').textContent = ch.no; hd.querySelector('.tt').textContent = ch.title;
    rise(hd, Math.min(ease(prog(t, ch.start + .1, .8)), 1 - ease(prog(t, ch.end - .5, .5)) * (ch === E.chapters[E.chapters.length - 1] ? 0 : 1)), 8);

    // 字幕（仮）
    let st = '';
    for (const u of E.units) {
      if (t < u.start - .1 || t >= u.end) continue;
      u.sent.forEach((s, k) => { if (t >= u.ss[k] - .05 && t < (u.sent[k + 1] ? u.ss[k + 1] : u.end) - .05) st = s; });
    }
    document.getElementById('subtext').textContent = st;

    // ワイプ：挿絵・比較図の場面では下げる
    const wv = clamp(1 - hideWipe * 1.2), wp = document.getElementById('wipe');
    wp.style.opacity = wv.toFixed(3); wp.style.transform = `translateY(${((1 - wv) * 16).toFixed(1)}px)`;
    // 口：読んでいる文の間だけ開閉（仮。録音後は音声の大きさで動かす）
    let speaking = 0;
    for (const u of E.units) {
      if (t < u.start || t > u.end) continue;
      u.ss.forEach((a, k) => { speaking = Math.max(speaking, Math.min(clamp((t - a) / .12), clamp((u.se[k] - .05 - t) / .12))); });
    }
    const syl = Math.max(0, .55 * Math.sin(2 * Math.PI * 4.1 * t) + .35 * Math.sin(2 * Math.PI * 6.7 * t + 1.3) + .2 * Math.sin(2 * Math.PI * 2.3 * t + .4));
    const open = clamp(speaking * syl);
    document.getElementById('mouth').setAttribute('ry', (4.5 + open * 6).toFixed(2));
    document.getElementById('mouth').setAttribute('rx', (8 + open * 1.5).toFixed(2));
    document.getElementById('mouthIn').setAttribute('ry', Math.max(0, open * 6 - 1.5).toFixed(2));
    // 瞬き：3〜5秒ごとに0.15秒
    const k = Math.floor(t / 4.1), bt = k * 4.1 + 1.6 + 1.2 * Math.sin(k * 1.7);
    document.getElementById('blink').setAttribute('opacity', (t >= bt && t < bt + .15) ? 1 : 0);
  };

  E.scene = (name, fn) => { E.scenes[name] = fn; };
})();
