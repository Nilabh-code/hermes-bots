# Repo rules (for every agent and human working here)

## Push rule — a visible change ships a visible image

Any commit that changes something a human can look at (README, UI, dashboard, bot roster, numbers, docs screenshots) must include a regenerated visual in the same commit:

```bash
node tools/hero.mjs --config tools/hero.json --out assets/hero.png     # repo card
node tools/shot.mjs --url http://localhost:PORT --out assets/<page>.png # real UI
```

- Read the image back before committing. If it is clipped, stale, or shows data that no longer exists, regenerate it.
- Target under 400 KB per PNG; 1280×640 for the hero, 1440×900 (or taller) for app screenshots.
- Alt text is mandatory and describes the content: `![Hero: reviewer-gated crew](assets/hero.png)`, never `![image](assets/hero.png)`.

## Redaction rule

Never publish a screenshot, card, log, or fixture containing a real name, email, absolute home path, hostname, tenant/customer identifier, token, or API key. Re-render redacted instead of blurring badly. `bash scripts/redact-check.sh` must pass before every push.

## Commit rule

Conventional commits, one logical change each, message states what changed **and why**. No secrets, no `node_modules`, no build output, no `.env`.

## Verification rule

A push is done when the remote shows the commit — verify with `git ls-remote origin <branch>` or `gh api repos/<owner>/<repo>/commits/<sha>`, not with local git output.
