// 全編 v4 のページから、各文を置く時刻（実測の narration.js を当てたもの）を書き出す。
//   node tools/export_layout.mjs [page.html] [out.json]   既定：full-v4/index.html → narration/layout.json
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
const [src = 'full-v4/index.html', out = 'narration/layout.json'] = process.argv.slice(2);
const b = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
p.on('pageerror', e => console.error('pageerror:', e.message));
await p.goto('file://' + path.resolve(src));
const lay = await p.evaluate(() => ({
  narration: !!window.NARRATION, duration: window.DURATION,
  chapters: E.chapters.map(c => ({ no: c.no, title: c.title, start: c.start, end: c.end })),
  units: E.units.map(u => ({ id: `${u.ch.no}-${u.idx + 1}`, start: u.start, end: u.end, ss: u.ss, se: u.se })),
}));
if (!lay.narration) console.error('注意：narration.js が読み込まれていません（仮の時刻です）');
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify(lay));
console.log(`${out}：${lay.units.length}単位、${(lay.duration / 60).toFixed(2)}分`);
await b.close();
