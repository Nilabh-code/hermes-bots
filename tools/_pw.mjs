// Resolve Playwright without requiring it as a dependency of this repo.
// Order: $PLAYWRIGHT_PATH -> ./node_modules -> a few well-known sibling projects -> global.
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { existsSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { homedir } from 'node:os';

export function loadPlaywright(extra = []) {
  const candidates = [
    process.env.PLAYWRIGHT_PATH,
    resolve(process.cwd(), 'node_modules', 'playwright'),
    ...extra,
  ].filter(Boolean);

  for (const base of candidates) {
    const req = createRequire(pathToFileURL(base.endsWith('/') ? base : base + '/'));
    try {
      return req('playwright');
    } catch {
      /* try next */
    }
  }

  // Sibling projects that commonly have it installed (dev machines only).
  const home = homedir();
  const hints = process.env.PW_HINTS ? process.env.PW_HINTS.split(';') : [];
  for (const h of hints) {
    const p = join(home, h, 'node_modules', 'playwright');
    if (existsSync(p)) {
      try {
        return createRequire(pathToFileURL(p + '/'))('playwright');
      } catch {
        /* ignore */
      }
    }
  }

  try {
    return createRequire(pathToFileURL(process.cwd() + '/'))('playwright');
  } catch {
    throw new Error(
      'Playwright not found. Install it (`npm i -D playwright && npx playwright install chromium`) ' +
        'or point PLAYWRIGHT_PATH at a directory that has node_modules/playwright.'
    );
  }
}
