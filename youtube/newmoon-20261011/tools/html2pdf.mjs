// HTML を PDF に書き出す（Playwright）。 node tools/html2pdf.mjs <in.html> <out.pdf>
import { chromium } from 'playwright';
import path from 'path';
const [src, out] = process.argv.slice(2);
const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const page = await browser.newPage();
await page.goto('file://' + path.resolve(src));
await page.evaluate(() => document.fonts.ready);
await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
await browser.close();
