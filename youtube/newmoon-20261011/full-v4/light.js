/* 全編 v4 の明るいデザイン（試作）。挿絵・図の中に直接書いてある暗い色を、明るい背景で見える色に置き換える。
   ページの組み立て（E.build）より前に読み込む。CSS で変えられる色は light.css。 */
(function () {
  const MAP = [
    ['rgba(250,248,244,', 'rgba(59,44,66,'], ['#FAF8F4', '#3B2C42'],          // 白い線・文字 → 濃い紫
    ['rgba(14,11,24,', 'rgba(255,255,255,'], ['#0e0b18', '#FFFFFF'], ['#110d1c', '#FFFFFF'],
    ['#1d1530', '#F7F1E8'], ['#1a1426', '#FFFFFF'], ['#2a2034', '#EDE3EF'], ['#2a2136', '#EDE3EF'],
    ['rgba(68,48,73,.95)', 'rgba(232,220,238,.9)'],
    ['#BB965B', '#A47B3A'], ['rgba(187,150,91,', 'rgba(164,123,58,'],              // 金は少し濃く
    ['#f3d9a4', '#D49A3A'], ['#f0d69a', '#D9A441'], ['#ece5d6', '#D2C3A6'],
  ];
  const swap = v => { if (typeof v !== 'string') return v; for (const [a, b] of MAP) v = v.split(a).join(b).split(a.toLowerCase()).join(b); return v; };
  const set = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function (k, v) { return set.call(this, k, /^(fill|stroke|stop-color|style|color)$/.test(k) ? swap(v) : v); };
  const css = Object.getOwnPropertyDescriptor(CSSStyleDeclaration.prototype, 'cssText');
  Object.defineProperty(CSSStyleDeclaration.prototype, 'cssText', { set(v) { css.set.call(this, swap(v)); }, get() { return css.get.call(this); } });
  // innerHTML で作られた図（グラデーションなど）は、組み立てのあとにまとめて置き換える
  window.lightFix = () => document.querySelectorAll('#stage *').forEach(el => {
    for (const k of ['fill', 'stroke', 'stop-color', 'style']) { const v = el.getAttribute(k); if (v) el.setAttribute(k, v); }
  });
})();
