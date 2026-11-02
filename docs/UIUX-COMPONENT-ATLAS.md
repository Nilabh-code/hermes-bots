# UI/UX Component Atlas — corpus evidence

Source: every clone in the local `Wesbite_Source` corpus (18 sites with parseable
markup, ~2.9 MB of HTML/CSS read, `node_modules` excluded). Every number below is
measured from the corpus, not asserted from taste. Regenerate with
`tools/uiux-scan.py` if the corpus changes.

## 1. What the corpus actually is

| Site | Files | KB | @keyframes | Reads as |
|---|---:|---:|---:|---|
| meticulai | 164 | 1393 | 117 | WebGL game portal — card deck, stage HUD, overlay panels |
| cityrt | 236 | 1179 | 88 | Illustrated, hand-drawn product UI (`--pz-hand`) |
| reactbits | 910 | 8095 | 599 | Component catalogue (the motion vocabulary) |
| sweet tape | 22 | 157 | 2 | Editorial e-commerce, physical-material interactions |
| squaredmedia | 7 | 63 | 7 | Dark agency site: mega-nav, service cards, case grid |
| samaymaurya-replica | 22 | 123 | 0 | Editorial portfolio: serif/sans, grain, lightbox, annotations |
| businesslyft | 18 | 68 | 16 | shadcn-style form/marketing system |
| seovyn | 16 | 37 | 0 | Conversion forms: hairline borders, focus rings |
| ThinkBid | 6 | 27 | 0 | Legal/utility pages, 404, nav |
| igloo.io | 3 | 27 | 0 | Product HUD: readout rows, cube info card |
| cornrevolution / cityskyhigh | 2/9 | 21/26 | 0 | Live-data dashboards, monospace, status dots |
| shelbykho.com | 8 | 57 | 21 | Personal brand, Framer-built, pill components |

## 2. Measured token distributions

**Easing (full corpus, all sites, bounded scan).** Three curves cover the entire
corpus; the first is the default UI curve, the second is the playful signature,
the third is the editorial/agency settle:

| Curve | Uses | Job |
|---|---:|---|
| `cubic-bezier(.22,1,.36,1)` | 186 | the default UI curve — fast out, long settle |
| `cubic-bezier(.34,1.56,.64,1)` | 129 | overshoot/back — playful affordances only |
| `cubic-bezier(.16,1,.3,1)` | 116 | expo-out — editorial and agency reveals |
| `cubic-bezier(.2,.8,.2,1)` | 71 | neutral ease-out |
| `cubic-bezier(.4,0,.2,1)` | 36 | material standard |
| `cubic-bezier(.2,1.6,.4,1)` | 28 | strong overshoot (badges, chips) |

**Durations.** `.3s` (315), `240ms` (274), `.2s` (263), `.15s` (191), `.4s` (149),
`.5s` (129), `.16s` (119). `6s` (149) is ambient/loop animation. Nothing in the
corpus animates a control longer than `0.5s`; `0ms` (187) is the reduced-motion
branch doing its job.

**Radii.** Observed values: `2 4 5 6 8 9 10 11 12 14 15 16 18 20 22 34 999 50%`.
Pills (`999px`) appear in 11 of 18 sites; `50%` is avatars/dots. The productive
pair is **one surface radius + one pill radius**, with nested radii derived by
subtraction (`inner = outer − padding`).

**Type pairings.** Recurring pattern: a display face + a neutral sans + a mono
for data.

| Role | Faces seen |
|---|---|
| Display / editorial | Fraunces, Cormorant Garamond, Instrument Serif, Futura PT Condensed, Lora |
| UI sans | Outfit, DM Sans, Inter (variable), Archivo, Figtree, AFACAD, Bricolage Grotesque |
| Data / mono | JetBrains Mono, Geist Mono, ui-monospace |

**Palettes.** Two families, both with a single saturated accent:

- *Warm paper*: `#f3ede0`, `#f5f5f1`, `#f6eddd` ground; `#2a2320`, `#1f1b28`,
  `#2f293a` ink; one accent — terracotta `#b35a3c`, flame `#ff4500`, purple
  `#a855f7`, acid `#b6fe00`, electric `#1d00ff`.
- *Near-black*: `#0c0c0b`, `#0a0a0a`, `#07090e` ground; `#161614`, `#141412`
  surface; `#eeece7`, `#e0e8ef` text; muted `#9a9791`, `#8a96aa`, `#b7afc4`.

Muted text never falls below ~`#8a96aa` on dark or `#6b6d64` on paper — both sit
above 4.5:1 on their ground.

## 3. Component taxonomy (what actually recurs)

### 3.1 Structure
Section band → content column → row/grid → card. Measured container widths land
at `max-w` 640 / 768 / 1120 / 1280 with an 8px-derived gutter set.

### 3.2 The nine surfaces every site needs
1. **Nav** — logo mark + ≤6 links + one primary CTA; sticky variant with
   backdrop blur and a `-1px` hairline; mobile: full-height panel, focus trapped,
   `Esc` closes, scroll locked.
2. **Hero** — claim (≤12 words), one supporting paragraph (≤2 sentences), one
   primary + one secondary action, one proof element (logo strip, metric,
   screenshot). Background layer optional and always non-interactive.
3. **Proof band** — logo strip or metric row; hairline separators, no boxes.
4. **Feature/service grid** — 2–4 cards, icon + label + one sentence; equal
   heights, no drop shadows beyond one elevation token.
5. **Work/case grid** — media, title, 1–2 tags; hover lifts media, not the card
   frame; always a real `alt`.
6. **Editorial band** — pull quote, annotation, or long-form text at `68ch`.
7. **Conversion block** — one form, visible labels, inline validation, one button,
   no more than 5 fields.
8. **Footer** — grouped links, legal row, one status/locale detail; `nav` landmark.
9. **Utility pages** — 404, legal, consent; same nav/footer shell as the product
   (ThinkBid is the model: `nf`, `legal-body`, `updated`).

### 3.3 Interactive components (state model, from businesslyft + seovyn forms)
`button, input, textarea, select, checkbox, radio, switch, chip, tag, badge,
tooltip, popover, dropdown, accordion, tabs, modal/dialog, drawer, toast, alert,
table, pagination, breadcrumb, avatar, skeleton, empty state, stepper, progress,
slider, segmented control, command palette`.

Required states for every one: **default, hover, active/pressed, focus-visible,
disabled, loading, error/invalid, empty, success**. Valid/invalid is styled off a
data attribute (`data-[invalid=true]`), never off `:invalid` alone, so an unfilled
optional field never screams red on load.

### 3.4 Motion vocabulary (reactbits catalogue, 599 keyframes)
- **Text**: split-character reveal (`clip` + `char` spans, staggered 20–40 ms),
  blur-in, decrypt/scramble, circular text, depth text.
- **Background**: canvas shaders (Aurora gradient ramp in oklab, AeroShards glass
  field, Beams rays, DarkVeil, Dither, ColorBends), always `aria-hidden`,
  `pointer-events:none`, and paused under `prefers-reduced-motion`.
- **Scroll**: GSAP ScrollTrigger `clip-path: inset(100% 0 0 0) → inset(0)`,
  `power4.inOut`, `once:true` (never replay on scroll-up), `scrub` only for
  pinned scenes; Lenis wrapper coordinated with a `.6s` canvas opacity fade.
- **Pointer**: blob cursor, click spark, grid cursor — marketing only, never on
  form-heavy or data surfaces.
- **Sticky/peel material**: sweet tape's `peel`, `peel-face`, `peel-flap`,
  `giant-pinning`, `transform-style: preserve-3d` paper physics.

## 4. The failures the corpus teaches you to avoid

- Canvas background behind body text with no scrim → contrast collapse.
- Animated entrance on content that also has to be readable instantly (LCP text
  faded from `opacity:0`).
- `overflow-x` leaks from marquees and 3D canvases on mobile.
- One accent used for both decoration and state (then "active" means nothing).
- Modal without focus trap, `Esc`, or scroll lock.
- Placeholder-as-label; error text that only turns the border red.
- Dropdowns/tooltips clipped by an `overflow:hidden` ancestor.
- Framer/GSAP scroll sections that never resolve when JS fails — every section
  must render readable with JS disabled.
- Fake metrics, invented testimonials, logo walls for customers that do not exist.
