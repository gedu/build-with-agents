---
id: journal/2026-08-10-measurement-rig-handoff
type: journal
targets: [any]
status: draft
verified: 2026-08-10
sources: ["skills/context-checkpoint/SKILL.md", "rig/results/tool-surface-v1/runs.jsonl", "decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0012-a-hypothesis-is-never-citable.md"]
---

# 2026-08-10 — handoff: the rig produced its first result

Second end-to-end run of `skills/context-checkpoint`. Record whether it worked on resume — that is its
promotion criterion, not better citations.

Written for a reader with none of the conversation.

## 1. Where we stopped — the next action

**Write the fifth upstream report**, `upstream/gentle-ai/0005-*`, on undocumented Claude Code CLI
behaviour. Five findings, each verified by direct probe, each of which silently invalidated a design
here before it was caught.

| # | Finding | Evidence |
|---|---|---|
| 1 | `--allowedTools` has **no effect on the visible surface** | Baseline and `--allowedTools Read` both return 54 tools and identical cost to the cent. It is a permission filter |
| 2 | `--disallowedTools` **does** remove names from visibility, and the surface is **not monotonic** | Disallowing `Bash` alone took the count from 54 to **55** |
| 3 | **`Bash` subsumes `Glob` and `Grep`** | While `Bash` is available the surface hides both; removing it exposes them. Net −1 +2 |
| 4 | The surface depends on **MCP connection race timing** | Two identical invocations seconds apart returned 55 and 82 tools when a `pending` server finished connecting |
| 5 | `ListAgents` is **intermittently absent** within one CLI version | Three runs under 2.1.224 saw 31 tools where the preimage said 32 |

Why this is the recommended next action: it is the only open item that helps anyone outside this repo,
it serves goal (3), and the evidence is already collected and reproducible.

**Filing is a human act.** It publishes under a GitHub identity and cannot be cleanly withdrawn.

## 2. Versions and identifiers, all verified 2026-08-10

| Item | Value |
|---|---|
| Repo | `gedu/build-with-agents`, **PUBLIC** |
| `origin/main` == `main` | `4feac42`, clean tree |
| Claude Code CLI | **2.1.224** — was 2.1.223 earlier in the session; the update broke every preimage |
| Model | `claude-opus-5[1m]` |
| `gentle-ai` | 2.2.4 — stay here; upstream's own note says revert to it while rc.2 is prepared |
| Upstream #2478 | `OPEN`, 0 comments, confirmed to reproduce on 2.2.4 |

## 3. Verified versus assumed

The section a summary always drops.

### Verified first-hand this session

- **≈224 tokens per resident tool entry.** 12 comparable pairs, 32 tools versus 3, median 6,489 extra
  cache-creation tokens for 29 extra names. Positive in 12 of 12; sign test p=0.000244, Mann-Whitney on
  the 9 same-order pairs p=0.000021.
- **The run-ordering confound was ruled out**, not assumed away: 3 pairs run scoped-first give a median
  delta of 6,511 against broad-first's 6,467.
- **The selection-reliability claim found nothing.** 12/12 `proper` in *both* arms, zero defects missed,
  zero invented, neither planted near-miss ever reported.
- All five CLI behaviours above, each by direct probe.
- The negative control voids in **both** directions, and `control-did-not-fire` was itself proven able
  to fire.
- `derive.py` re-derives byte-identically across two independent processes.
- Redaction gate clean across 107 tracked files; no home path in the committed `runs.jsonl`.

### Assumed, inherited, or explicitly not verified — do not promote these

- **The cause of `ListAgents` intermittency.** Observed three times; *why* is unknown. Do not write a
  mechanism into the upstream report — report the observation.
- **Whether a plain terminal yields the same surface as a session-nested invocation.** A sub-agent once
  reported 33 tools where the main session consistently reported 54. Never tested from a real terminal
  outside any Claude Code session, and it should be before the report claims a general shape.
- **`sdd/measurement-rig/tasks.md` is stale.** It shows 17 open items; 9.1–9.4 are done, 9.0 is
  unblocked by ADR 0011, 7.x was cancelled, 6.x was superseded. Reconcile before trusting it.
- **`hooks/pre-commit:133` still carries a fail-open**: `grep -a -nH '' -- "$f" 2>/dev/null || :`
  swallows per-file status, so an unreadable tracked file is silently skipped in `--all`. Found by a
  validator, never fixed.
- **`TIMEOUT_S=300` in `run.sh` is still the provisional pilot bound.** Observed runs take 25–52s.
- **Upstream reports 0002–0004 remain unfiled**, and the 2.1.224 confirmation on #2478 is unposted.

## 4. Open, deliberately

- **Tier 1 and tier 2 cells will not be run.** The null is established for this task class at 12 pairs
  with zero separation; more tiers add breadth to a null. If the effect exists it is in tasks with **no
  single correct answer**, which is a different fixture and a different change.
- **`hypotheses/0001` is closed as *not supported* for defect-reporting tasks and deliberately NOT
  `rejected`.** A null on one task class does not refute the general claim.
- **No performance/efficiency review lens exists.** None of the 4R covers it — flagged once, deferred by
  the operator, not re-argued.
- **No committed test for `hooks/pre-commit`.** Recorded three times now as ADR-shaped: where do tests
  live in this repo.

## 5. What the conversation established that no file records

- **Harder tasks produced *more* agreement, not less.** The only over-report ever observed came from the
  *simplest* task — tier 1, identical tool calls, broad arm added a false positive. Twelve harder pairs
  produced nothing. A task with a clearly correct answer appears to invite care in both arms. This runs
  opposite to the assumption the whole experiment was designed on, and it is why two independent
  fixture-hardening passes both returned null.
- **The recurring correction, six times in four days: a reducer applied to one arm is a confound;
  applied to both arms it is a constant.** `Bash` and `--strict-mcp-config` were both first forbidden,
  then required in both arms. When a knob moves more than the quantity under study, set it identically
  everywhere and record it as a fixed input.
- **Reading produced confident wrong conclusions and cheap probes corrected them, every time.** Auth,
  the turn-count field, the scoping mechanism, the surface's monotonicity, the arms' capability
  symmetry. Two probes under a dollar beat four reasoning passes on each.
- **The instrument-doubt threshold nearly disabled the experiment by working.** Deliberate controls
  tripped X=3 and blocked the `theory/` write; the fix was to separate deliberate from spontaneous, and
  the load-bearing half is the inversion — a control that does *not* fire is the real alarm.
- **A verification that ran once is not a verification that keeps running.** The stream-flush assertion
  was retained after being proven, precisely because proving it once proves it for one version.
