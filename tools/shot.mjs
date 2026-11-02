#!/usr/bin/env node
// Screenshot a running dashboard/page, or a local HTML file.
// Usage:
//   node tools/shot.mjs --url http://localhost:8321 --out assets/dashboard.png [--width 1440] [--height 900] [--full-page]
//   node tools/shot.mjs --html docs/mock.html --out assets/preview.png
import { mkdirSync, statSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { loadPlaywright } from './_pw.mjs';

const argv = process.argv.slice(2);
const args = {};
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (!a.startsWith('--')) continue;
  const key = a.slice(2);
  const next = argv[i + 1];
  if (next && !next.startsWith('--')) {
    args[key] = next;
    i++;
  } else {
    args[key] = true;
  }
}

const url = args.url;
const html = args.html;
if (!url && !html) {
  console.error('Need --url <http(s)://...> or --html <file>');
  process.exit(2);
}

const out = resolve(args.out || 'assets/screenshot.png');
const width = Number(args.width || 1440);
const height = Number(args.height || 900);
const fullPage = Boolean(args['full-page']);
const waitMs = Number(args.wait || 1200);

const { chromium } = loadPlaywright();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 2 });

const target = url || pathToFileURL(resolve(html)).href;
const response = url ? await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 }) : await page.goto(target, { waitUntil: 'load' });
if (response && !response.ok() && url) {
  console.error(`HTTP ${response.status()} for ${url}`);
  await browser.close();
  process.exit(1);
}
await page.waitForTimeout(waitMs);
mkdirSync(dirname(out), { recursive: true });
await page.screenshot({ path: out, type: 'png', fullPage });
await browser.close();

const kb = (statSync(out).size / 1024).toFixed(0);
console.log(`shot -> ${out} (${kb} KB, ${width}x${height}${fullPage ? ', full page' : ''})`);
if (Number(kb) > 400) console.warn('warning: over 400 KB — resize or crop before committing');
