// 全編のページから場面ごとの時刻・画面・注目対象を timeline.json に書き出す。
//   node tools/export_units.mjs full/index.html full/timeline.json
//   node tools/export_units.mjs full-v2/index.html full-v2/timeline.json
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
const [src, out] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto('file://' + path.resolve(src));
const data = await p.evaluate(() => {
  const names = { cover: '表紙（サムネイルと同じ画面）', sky: '挿絵：夜空', align: '図解：太陽・地球・月', phone: '挿絵：スマホ（日常の例）', charts: '比較図', timeline: '図解：時間軸', cycle: '図解：月の満ち欠け', balance: '挿絵：天秤と二人', talk: '挿絵：二人の会話', window: '挿絵：窓明かり', letters: '挿絵：写真と手紙', orbit: '図解：金星の公転と見かけの逆行', elem: '挿絵：水と火', lake: '挿絵：湖面の月', hearth: '挿絵：火', sabian: '挿絵：サビアン', pair: '挿絵：二つのシンボル', memo: '挿絵：手帳', bars: '図解：期間の長さ' };
  return E.chapters.map(ch => ({ no: ch.no, title: ch.title, start: ch.start, end: ch.end, card: ch.cardA !== undefined ? [ch.cardA, ch.cardB] : null, units: ch.units.map(u => {
    const sc = E.cues.filter(c => c.k === 'scene' && c.a <= u.start + .5 && c.b >= u.end - .5).map(c => names[c.name] || c.name);
    const own = E.cues.filter(c => c._u === u && c.k !== 'scene');
    const kinds = new Set(own.map(c => c.k));
    const JP = { sun: '太陽', moon: '月', mercury: '水星', venus: '金星', mars: '火星', jupiter: '木星', saturn: '土星', uranus: '天王星', neptune: '海王星', pluto: '冥王星', asc: 'ASC', mc: 'MC', ic: 'IC', dsc: 'DSC' };
    const SG = ['牡羊座','牡牛座','双子座','蟹座','獅子座','乙女座','天秤座','蠍座','射手座','山羊座','水瓶座','魚座'];
    const focus = new Set();
    own.forEach(c => { if (c.k === 'halo') c.keys.forEach(k => focus.add(JP[k])); if (c.k === 'seg') c.signs.forEach(i => focus.add(SG[i])); if (c.k === 'house') focus.add(`第${c.n}ハウス`);
      if (c.k === 'line') [c.p1, c.p2].forEach(p => { const k = typeof p === 'string' ? p : (p && (p.key || p.g)); if (k && JP[k]) focus.add(JP[k]); }); });
    const lab = own.filter(c => c.k === 'arc' && c.label).map(c => c.label).concat(own.filter(c => c.k === 'text').map(c => c.txt));
    return { start: u.start, end: u.end, text: u.text, scene: sc[0] || 'チャート', parts: [...kinds], focus: [...focus], labels: lab };
  }) }));
});
fs.writeFileSync(out, JSON.stringify(data, null, 1));
await b.close();
