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

  // 締め（最後の単位）：問いかけとコメント欄への誘い（読む文の2文目に合わせて出す）と、チャンネル登録のひとこと（文字だけ）。
  // 次回の告知（「次は、10月26日の牡牛座の満月でお会いしましょう。」）は、次回を出せるかわからないので台本から外した（2026-10-03 ご本人の指定）。
  // チャンネル登録のひとことは、その告知の画面から、ここ（名前の下）に移した
  const uEnd = C[12].units[C[12].units.length - 1], fEnd = uEnd.cues;
  if (!uEnd.text.startsWith('最後まで')) throw new Error('v2: 締めの単位が見つかりません');
  uEnd.cues = T => fEnd(T).map(c => {
    if (c.k === 'scene') c.p.texts = [...(c.p.texts || []),
      tx('<div class="q">あなたがこの関係で、守りたいものは何ですか？</div>', T.s(1) + .2, T.b + 2, 'left:120px;top:450px'),
      tx('よければ、コメント欄で一言教えてください', T.s(1) + 1.0, T.b + 2, 'left:124px;top:520px', 's'),
      tx('<div class="cta">よろしければ、チャンネル登録をお願いします</div>', T.s(2) + 1.0, T.b + 2, 'left:124px;top:720px')];
    return c;
  });
})();
