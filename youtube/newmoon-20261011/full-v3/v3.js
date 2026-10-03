/* 全編 v3：v2 の画面のうち、いくつかの挿絵を実写素材（Mixkit）に差し替える。読む文・時刻・文字はそのまま。
   素材の一覧は tools/stock.tsv、取得と連番の作り直しは tools/fetch_stock.sh、場面は lib/footage.js。
   実写は当日の空や本人の体験ではなく「イメージ」として扱い、画面の左上に「イメージ」と入れる。 */
(function () {
  const C = window.CHAPTERS;
  // [章, 単位（1から）, 元の挿絵, 素材名, 読む文の書き出し（取り違えの確認用）]
  const SWAP = [
    [4, 3, 'talk', 'talk04', '天秤座の新月が第3ハウス'],   // 二人の会話 → カフェで一緒にスマホを見る二人
    [5, 7, 'window', 'home05', '関係の見直しが、家族'],     // 窓明かり → 湯気の立つカップ（日常の場面）
    [9, 4, 'hearth', 'fire09', '木星は、広げる'],           // 火 → 焚き火
    [9, 6, 'talk', 'talk09', '関係を大切にするために'],     // 二人の会話 → 灯りの下で話す二人
    [11, 8, 'lake', 'sea11', '「湖面を照らす月」'],         // 湖面の月（11-8〜11-9）→ 海に映る月。11-11 は図解なので挿絵のまま
    [13, 4, 'sky', 'moon13', '最後まで'],       // 夜空 → 月
  ];
  SWAP.forEach(([ch, no, from, clip, head]) => {
    const u = C[ch - 1].units[no - 1], f = u.cues;
    if (!u.text.startsWith(head) || !f) throw new Error(`v3: ${ch}-${no} が見つかりません`);
    u.cues = T => f(T).map(c => {
      if (c.k === 'scene' && c.name === from) { c.name = 'footage'; c.p.clip = clip; c.p.was = from; }
      return c;
    });
  });
})();
