# Architecture — why this crew is shaped this way

## The problem with a single agent

A single session that plans, executes, and then "reviews" its own work has three structural failure modes:

1. **Self-consistency bias.** The context contains the author's reasoning, so the review inherits the author's assumptions. It defends the plan instead of attacking it.
2. **No falsifiable stop.** "Looks good" is not a token; without one, the loop ends when the model feels finished, not when the evidence exists.
3. **No memory of the decision.** Six turns later nobody can say why the wall is 2 mm, which means nobody can change it safely.

This repo fixes each one mechanically:

| Failure | Mechanism here |
|---|---|
| self-consistency bias | Reviewer is a **separate profile**, run as a separate process, given only the written artifacts — never the orchestrator's internal reasoning |
| no falsifiable stop | **Verdict tokens** (`APPROVE / APPROVE WITH CHANGES / REJECT / SHIP / FIX / ROLLBACK`); prose approval does not count |
| no decision memory | **Decision ledger** in `PLAN.md`; every material choice carries chosen / why / why-not / size / fit / cost / reversibility |

## Why separate processes and not "one more paragraph in the prompt"

Independence is the product. If the reviewer shares the author's context, it will pattern-match to the author's conclusion. Spawning `hermes -p reviewer chat -q "<gate prompt>"` gives it:

- a fresh context window (no anchoring on the plan's own justification),
- its own tools and budget (it can re-run commands, which the author might have faked),
- an artifact boundary (`PRE-REVIEW.md`) that the orchestrator is forbidden to edit.

The cost is one extra model session per gate. That is the price of an opinion that is worth something.

## Risk tiers — gate depth scales with blast radius

| Tier | What it covers | Mandatory gates | Extra |
|---|---|---|---|
| T0 | read-only answer, explanation, a file read | pre-flight (3 lines) + POST light | none |
| T1 | workspace edits, local script, local build | PRE + POST | rollback described in the plan |
| T2 | `git push`, deploy, send, delete, install, publish | PRE + POST | explicit rollback + blast-radius audit |
| T3 | money, credentials, production data, destructive/legal | PRE + POST | **stop** and show the decision ledger to the human |

The point is not maximum ceremony. A 40-line script should not pay for a 12-minute review; a push to a shared repo should. Tier selection is stated in `TASK.md`, so the choice is auditable too.

## Loop bounds (the part most agent systems get wrong)

Unbounded verification is just expensive stalling. Hard limits, written into the SOULs:

| Bound | Value | Why |
|---|---|---|
| Gate rounds | 2 per gate | a third round means the scope is wrong, not the wording |
| Fix cycles after POST | 2 | after that the honest answer is "largest verified slice + what is broken" |
| Dispatch attempts per step | 3 | distinguishes "flaky" from "cannot work" |
| 3D visual iterations | 2 | a render is a perception check, not a design method; geometry checks settle ambiguity |
| Research saturation | 2 consecutive queries returning only known sources | prevents infinite widening |

Ambiguity is settled by a **deterministic check** — re-run the command, read the schema, measure the mesh, query the API — never by re-reading your own prose. That rule alone removes most runaway loops.

## Artifact protocol

```
<workspace>/.orchestrator/<task-slug>/
  TASK.md   PLAN.md   PRE-REVIEW.md   EXECUTION.md   POST-REVIEW.md   DELIVERY.md
```

- **Append, never rewrite.** A corrected wrong decision is more valuable than a clean file that hides it.
- **Verbatim execution logs.** Paraphrasing a specialist's output destroys the audit trail that makes POST mode possible.
- **One artifact per gate, written by the gate.** The orchestrator may not edit `PRE-REVIEW.md` or `POST-REVIEW.md`. Editing a verdict is the one unrecoverable sin.

## Degraded mode

If the crew cannot run a gate — no reviewer profile, no session budget, two reviewer crashes — the orchestrator writes `DEGRADED:` as the first line of the delivery, runs the same battery itself in a separate pass, and names which gate was self-run. Silently dropping a gate is forbidden; announcing it is allowed. That asymmetry is deliberate: a known weak review can be discounted, a hidden one cannot.

## Extending

1. `cp -r bots/reviewer bots/<yours>` (any bot folder is a template).
2. Rewrite `SOUL.md` keeping the three-part skeleton: **invariant** (the one rule that outranks everything) → **procedure** (numbered, with its own effort floor and ceiling) → **closing gate** (checkboxes that can actually fail).
3. Give it an evidence block format, so POST mode can audit it without re-reading the whole transcript.
4. `python install.py --bots <yours>`.
5. Add a row to the orchestrator's crew table so it gets dispatched.

Rules that keep the crew honest: whoever executes is never whoever approves; every specialist produces evidence a stranger can re-run; every bot has a numeric ceiling as well as an effort floor.

## Cost notes

- A T1 task typically costs 3 sessions: orchestrator + reviewer (PRE) + specialist + reviewer (POST) — four if you count the final write-up.
- The gates are cheapest on paper: reviewing a plan costs a fraction of debugging a wrong execution.
- If you want to halve the cost, run the same reviewer profile twice rather than skipping a gate, and keep T0 tasks on the light path.
