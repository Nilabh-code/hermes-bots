# One gated run, start to finish

A realistic T1 task, abbreviated to show what the gates actually catch. Names and paths are placeholders.

**Ask:** "Add retries to the image fetcher. It keeps dying on flaky hosts."

---

## TASK.md (written by Orchestrator)

```
Tier: T1 (local edits, reversible via git)
AC1  fetcher retries transient failures (timeouts, 5xx, connection resets) and not 4xx
AC2  attempts are bounded; total wall time bounded
AC3  existing single-fetch behaviour unchanged for a healthy host
AC4  a test exists that fails on the old code and passes on the new
Assumption: "flaky hosts" means transient network errors, not rate limiting (rate limiting
would need a different backoff shape) — stated here so Reviewer can reject it.
```

## PLAN.md — decision ledger (excerpt)

| # | Decision | Chosen | Why | Why not | Cost | Reversible |
|---|---|---|---|---|---|---|
| D1 | retry count | 3 attempts | 2 fails on double-flake runs seen ~1 in 40; 4 adds 7 s of tail latency for ~0.2% more successes | 2: too fragile; 4: tail latency beats the benefit | +6 s worst case | yes |
| D2 | backoff | exponential 1→2→4 s, ±20% jitter, cap 8 s | jitter prevents retry herds from N workers | fixed 2 s: thundering herd; no cap: 30 s tail | — | yes |
| D3 | retry on 429 | no, surface it | rate limiting needs `Retry-After` handling and a shared budget, out of scope for this ask | retrying 429 blindly makes the ban worse | — | yes |
| D4 | test seam | inject `sleep` and `fetch` | makes the test deterministic in <1 s | sleeping for real: 7 s test, flaky CI | 2 params | yes |

**Sizing check:** worst case = 3 attempts + 1+2+4 s backoff ≈ 7.4 s + fetch time. If the caller's own timeout is 5 s, retries are invisible — verified: caller timeout is 60 s.

## PRE-REVIEW.md (GATE 1, excerpt)

```
Verdict: APPROVE WITH CHANGES

Gaps
- Battery 5 (fit): D2 caps backoff at 8 s but planning never checked the caller's timeout
  above the retry loop. 3 attempts + max backoff can exceed a 10 s wrapper elsewhere in the
  pipeline. Must change: pass a deadline through, stop retrying when it is near.
- Battery 4 (size): D1 says "3 attempts" — why 3 and not 5? The 1-in-40 number is asserted,
  not measured. Either measure it over the last 500 log lines, or restate as an assumption.
- Battery 7 (failure): retry storm when 50 workers hit one dead host. Jitter is +-20%; the
  cap makes it worse (all workers converge at 8 s). Must change: full jitter (rand(0, delay))
  or a per-host circuit breaker.
- Battery 8 (security): retrying an authenticated request on connection reset can duplicate a
  side effect if the request was not idempotent. Must change: retry only GET/HEAD, or require
  an idempotency key.
- Battery 10 (evidence): AC4 says "a test that fails on old code" — the plan never states how
  that is demonstrated. Must change: include the red run's output in EXECUTION.md.

Must change before execution: 1) deadline propagation, 2) full jitter, 3) idempotency guard,
4) prove the test is red first. 5) restate D1's justification as measured-or-assumed.
```

The plan shipped with **four things it would have taken to production**: a hidden timeout collision, a retry storm, duplicated writes on non-idempotent requests, and a test that was never proven to fail. None of them are visible in a code diff; all of them are visible in a plan that is read adversarially.

## EXECUTION.md (excerpt)

```
## Step 1 — codewriter — 14:22
...changed fetcher.py (retry helper), added tests/test_retry.py (5 cases)...
$ python -m pytest tests/test_retry.py -q
5 passed in 0.41s

## Step 2 — red-run proof (AC4) — 14:26
$ git stash && python -m pytest tests/test_retry.py -q ; git stash pop
4 failed, 1 passed in 0.38s
```

## POST-REVIEW.md (GATE 2, excerpt)

```
Verdict: SHIP

AC1 retries transient only        — PASS   re-ran 5 tests; 429/404 cases assert no retry
AC2 bounded attempts and time     — PASS   deadline test: 3 attempts, 2.9 s max, wrapper respected
AC3 healthy path unchanged        — PASS   single-fetch test 0.003 s, one call (asserted by call count)
AC4 red test proven               — PASS   reproduced the 4-failed run from the stash
Fabrication check: none — every quoted number reproduced
Blast radius: fetcher.py + tests/test_retry.py only; no dependency added; no state mutated
Rollback: `git revert <sha>` — clean, no migration
Not verified: behaviour under a real dead host (simulated only)
Minor: retry log line has no attempt counter — fix when touché next
```

## Delivery

Shipped: bounded retries with full jitter, a deadline that propagates, an idempotency guard, and a test proven red before green.
Gate 1: `APPROVE WITH CHANGES` — 4 must-changes, all applied and re-checked.
Gate 2: `SHIP` — all four acceptance criteria re-run by the reviewer itself.
Residual risk: real-host behaviour unverified; 429 handling deliberately out of scope.
