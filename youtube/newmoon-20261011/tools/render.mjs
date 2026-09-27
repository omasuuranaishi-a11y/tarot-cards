// HTMLのページを静止画・動画に書き出す。
//   node tools/render.mjs still <page.html> <out.png> <幅> <高さ> [秒]
//   node tools/render.mjs video <page.html> <out.mp4> <幅> <高さ> [fps] [開始秒] [終了秒]
// ページ側は window.DURATION（秒）と window.render(t) を用意する（静止画のみのページは不要）。
// 環境変数：
//   FFMPEG        ffmpeg の実行ファイル（既定 ffmpeg）
//   CHROMIUM_PATH Chromium の実行ファイル（既定は Playwright 付属）
//   LOCAL_FONTS   @fontsource のフォルダ。指定するとGoogle Fontsの代わりに読み込む（オフライン環境用）
//   CRF           画質（既定 18。小さいほど高画質・大きいファイル）
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

const [mode, src, out, w, h, ...rest] = process.argv.slice(2);
const W = +w, H = +h;
const abs = path.resolve(src);

let url = 'file://' + abs;
const LOCAL = process.env.LOCAL_FONTS;
if (LOCAL) {
  const css = ['noto-serif-jp/500.css', 'noto-serif-jp/600.css', 'noto-serif-jp/700.css',
    'noto-sans-jp/400.css', 'noto-sans-jp/500.css', 'noto-sans-jp/700.css']
    .map(f => `<link rel="stylesheet" href="file://${path.join(LOCAL, f)}">`).join('\n');
  const html = fs.readFileSync(abs, 'utf8')
    .replace(/<link[^>]*fonts\.googleapis[^>]*>/g, '')
    .replace('<head>', `<head>\n<base href="file://${path.dirname(abs)}/">\n${css}`);
  const tmp = path.join(path.dirname(abs), `.render-tmp-${process.pid}.html`);
  fs.writeFileSync(tmp, html);
  url = 'file://' + tmp;
  process.on('exit', () => { try { fs.unlinkSync(tmp); } catch {} });
}

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('pageerror', e => console.error('pageerror:', e.message));
page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
await page.goto(url);
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);

if (mode === 'still') {
  const t = rest[0] !== undefined ? +rest[0] : null;
  if (t !== null) await page.evaluate(t => window.render(t), t);
  await page.screenshot({ path: out });
} else if (mode === 'video') {
  const fps = +(rest[0] || 30);
  const dur = await page.evaluate(() => window.DURATION);
  const t0 = +(rest[1] || 0), t1 = rest[2] !== undefined ? +rest[2] : dur;
  const n = Math.round((t1 - t0) * fps);
  const ff = spawn(process.env.FFMPEG || 'ffmpeg', ['-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', process.env.CRF || '18', '-pix_fmt', 'yuv420p', '-r', String(fps),
    '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const started = Date.now();
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.render(t), t0 + i / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % (fps * 10) === 0) console.log(`frame ${i}/${n}  ${((Date.now() - started) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  const code = await new Promise(r => ff.on('close', r));
  console.log('ffmpeg exit', code, 'frames', n);
  if (code !== 0) process.exitCode = 1;
}
await browser.close();
