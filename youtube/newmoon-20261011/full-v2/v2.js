/* 全編 v2：v1 の章・読む文（../full/chapters.js）を使い、冒頭と締めの画面だけを差し替える。
   参考動画の分析（reference/参考動画の分析.md）の 7・8・10 に対応。 */
(function () {
  const C = window.CHAPTERS;
  const tx = (html, a, b, style, cls) => [html, a, b, style, cls];

  // 01-1〜01-2：サムネイルと同じ表紙の画面で、あいさつと今回のテーマ
  const [u1, u2] = C[0].units;
  u1.cues = T => {
    const U = T.u(1);
    return [{ k: 'scene', name: 'cover', a: T.a - .5, b: U.b, p: { a: T.a, b: U.b, wipe: true,
      at: { date: T.a + .3, title: T.a + .6, tag: T.a + 1.4, halo: U.at(0, .5), line: U.at(0, .72), chip: U.at(0, .72) } } }];
  };
  u2.cues = null;

  // 13-3：次回の告知に、チャンネル登録のひとこと（文字だけ）
  const u133 = C[12].units[2], f133 = u133.cues;
  u133.cues = T => f133(T).map(c => {
    if (c.k === 'scene') c.p.texts = [...(c.p.texts || []), tx('<div class="cta">よろしければ、チャンネル登録をお願いします</div>', T.s(0) + 2.4, T.b, 'left:124px;top:300px')];
    return c;
  });
  // 13-4：締めの問いかけとコメント欄への誘い（読む文の2文目に合わせて出す）
  const u134 = C[12].units[3], f134 = u134.cues;
  u134.cues = T => f134(T).map(c => {
    if (c.k === 'scene') c.p.texts = [...(c.p.texts || []),
      tx('<div class="q">あなたがこの関係で、守りたいものは何ですか？</div>', T.s(1) + .2, T.b + 2, 'left:120px;top:450px'),
      tx('よければ、コメント欄で一言教えてください', T.s(1) + 1.0, T.b + 2, 'left:124px;top:520px', 's')];
    return c;
  });
})();
