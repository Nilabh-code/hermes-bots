#!/usr/bin/env node
// Render a 1280x640 repository hero card to PNG.
// Usage: node tools/hero.mjs [--config tools/hero.json] [--out assets/hero.png]
import { readFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { loadPlaywright } from './_pw.mjs';

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, cur, i, arr) => {
    if (cur.startsWith('--')) acc.push([cur.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true]);
    return acc;
  }, [])
);

const configPath = resolve(args.config || 'tools/hero.json');
const out = resolve(args.out || 'assets/hero.png');
const spec = JSON.parse(readFileSync(configPath, 'utf8'));

const {
  title = 'Project',
  subtitle = '',
  kicker = '',
  chips = [],
  tokens = [],
  footer = '',
  accent = '#8B5CF6',
  accent2 = '#2E9E7B',
  theme = 'dark',
} = spec;

const dark = theme !== 'light';
const bg = dark ? '#0B0B10' : '#F7F7FB';
const fg = dark ? '#F4F4F8' : '#12121A';
const muted = dark ? 'rgba(244,244,248,0.62)' : 'rgba(18,18,26,0.62)';
const card = dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)';
const line = dark ? 'rgba(255,255,255,0.10)' : 'rgba(0,0,0,0.10)';

const chip = (t, i) => `<span class="chip" style="--d:${(i * 0.06).toFixed(2)}s">${t}</span>`;
const token = (t, i) => `<span class="token" style="--d:${(i * 0.06 + 0.2).toFixed(2)}s">${t}</span>`;

const html = `<!doctype html>
<html><head><meta charset="utf-8">
<style>
  @page { margin: 0 }
  * { box-sizing: border-box }
  html, body { margin: 0; width: 1280px; height: 640px; overflow: hidden }
  body {
    background:
      radial-gradient(900px 480px at 12% -10%, ${accent}33, transparent 62%),
      radial-gradient(760px 420px at 96% 112%, ${accent2}2E, transparent 60%),
      ${bg};
    color: ${fg};
    font-family: "Segoe UI", "Inter", system-ui, -apple-system, sans-serif;
    display: flex; flex-direction: column; justify-content: space-between;
    padding: 64px 72px 48px; position: relative;
  }
  .grid {
    position: absolute; inset: 0; pointer-events: none; opacity: ${dark ? 0.16 : 0.09};
    background-image: linear-gradient(${line} 1px, transparent 1px), linear-gradient(90deg, ${line} 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: radial-gradient(900px 560px at 70% 30%, #000 20%, transparent 78%);
  }
  .kicker { display: inline-flex; align-items: center; gap: 10px; font-size: 15px; letter-spacing: .16em; text-transform: uppercase; color: ${muted} }
  .dot { width: 9px; height: 9px; border-radius: 50%; background: ${accent2}; box-shadow: 0 0 18px ${accent2} }
  h1 { margin: 18px 0 10px; font-size: 84px; line-height: .96; letter-spacing: -.03em; font-weight: 800 }
  h1 .accent { background: linear-gradient(92deg, ${accent}, ${accent2}); -webkit-background-clip: text; background-clip: text; color: transparent }
  p.sub { margin: 0; font-size: 26px; color: ${muted}; max-width: 900px }
  .chips { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 30px }
  .chip {
    font-size: 16px; padding: 9px 16px; border: 1px solid ${line}; border-radius: 999px;
    background: ${card}; color: ${fg}; animation: rise .6s var(--d) both;
  }
  .footer { display: flex; align-items: center; justify-content: space-between; gap: 24px; margin-top: 34px; padding-top: 22px; border-top: 1px solid ${line} }
  .tokens { display: flex; flex-wrap: wrap; gap: 8px }
  .token {
    font-size: 12.5px; letter-spacing: .1em; padding: 6px 11px; border-radius: 7px;
    color: ${muted}; border: 1px solid ${line}; background: ${card};
    animation: rise .6s var(--d) both;
  }
  .url { font-size: 15px; color: ${muted}; font-variant-numeric: tabular-nums }
  @keyframes rise { from { opacity: 0; transform: translateY(8px) } to { opacity: 1; transform: none } }
</style></head>
<body>
  <div class="grid"></div>
  <div>
    <div class="kicker"><span class="dot"></span>${kicker}</div>
    <h1>${title.replace(/\s+(\S+)$/, ' <span class="accent">$1</span>')}</h1>
    <p class="sub">${subtitle}</p>
    <div class="chips">${chips.map(chip).join('')}</div>
  </div>
  <div class="footer">
    <div class="tokens">${tokens.map(token).join('')}</div>
    <div class="url">${footer}</div>
  </div>
</body></html>`;

const { chromium } = loadPlaywright();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 640 }, deviceScaleFactor: 2 });
await page.setContent(html, { waitUntil: 'load' });
await page.waitForTimeout(900);
mkdirSync(dirname(out), { recursive: true });
await page.screenshot({ path: out, type: 'png' });
await browser.close();

const { statSync } = await import('node:fs');
console.log(`hero -> ${out} (${(statSync(out).size / 1024).toFixed(0)} KB, 1280x640 @2x)`);
