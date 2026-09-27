/* 実写の場面（全編 v3 から）。素材は Mixkit の動画を tools/fetch_stock.sh で 30fps の JPEG 連番（1920x1080）にしたもの。
   Chromium は H.264 を再生できず、<video> のシークも1コマずつの書き出しでは不確実なので、時刻から番号を決めて <img> を差し替える。
   frame() は画像の読み込み（img.decode()）の Promise を返し、window.render(t) がそれを待つ。
   p.clip：stock/manifest.js の素材名／p.texts：挿絵と同じ文字（実写の上にそのまま出す）
   素材より場面が長いときは、最後のコマで止める（ゆっくり再生は fetch_stock.sh の speed で作っておく）。 */
(function () {
  const { div, rise, win, prog, lerp } = E.U;
  const BASE = E.STOCK_DIR || '../stock/frames/';
  E.scene('footage', (layer, p, c) => {
    const S = (window.STOCK || {})[p.clip];
    if (!S) console.error('footage: 素材がありません（tools/fetch_stock.sh を先に実行）', p.clip);
    const wrap = div('ft-wrap', '', layer);
    const img = document.createElement('img'); img.className = 'ft-img'; img.alt = ''; wrap.appendChild(img);
    div('ft-shade', '', layer);
    const tag = div('ft-tag', 'イメージ', layer);
    const T = (p.texts || []).map(([html, a, b, style, cls]) => [div('stext ' + (cls || ''), html, layer, style || ''), a, b]);
    const a0 = c.a - .4, a1 = c.b + .4; // 場面が見え始めてから消えるまで
    let cur = -1;
    return { frame(t) {
      const k = prog(t, a0, a1 - a0);
      wrap.style.transform = `scale(${lerp(1, 1.05, k).toFixed(4)})`;
      rise(tag, win(t, c.a, c.b, .6, .4), 0);
      T.forEach(([el, a, b]) => rise(el, win(t, a, b ?? p.b, .7, .5)));
      if (!S) return;
      const i = Math.min(S.n - 1, Math.max(0, Math.floor((t - a0) * 30 + 1e-6)));
      if (i === cur) return;
      cur = i;
      img.src = `${BASE}${p.clip}/${String(i).padStart(5, '0')}.jpg`;
      return img.decode().catch(e => console.error('footage: 読み込めません', img.src, e.message));
    } };
  });
})();
