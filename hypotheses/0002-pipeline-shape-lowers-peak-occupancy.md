---
id: hypotheses/0002-pipeline-shape-lowers-peak-occupancy
type: research
targets: [any]
status: draft
verified: 2026-08-13
sources: ["sdd/failure-flood-triage/spec.md", "sdd/failure-flood-triage/design.md", "rig/run-pipeline.sh", "decisions/0012-a-hypothesis-is-never-citable.md"]
---

# 0002 — Splitting a task into a pipeline of separate model invocations lowers peak occupancy

**Registered before the stage-2 (`s2`) comparison run that could settle it.** Nothing here may be
cited — see ADR 0012. Naming it here is testing it, not citing it.

## Logical form: STATISTICAL

Declared per `skills/hypothesis-cycle` step 0, matching `hypotheses/0001`'s own precedent. No single run
refutes or supports this claim; only N with spread (spec R-F7.2) settles it.

## Claim

For the failure-flood-triage comparison (`task_id: s2`, `failure-flood/v2` fixture), the **PIPELINE**
arm's peak occupancy — the max token count over any single deduplicated turn, across all of its model
steps (`02-diagnose`, `03-apply`) — is **materially lower** than the **MONOLITHIC** arm's peak occupancy,
because PIPELINE resets context at the start of each model step while MONOLITHIC carries one continuous,
ever-growing conversation across collection, diagnosis and repair.

## Why it is plausible

Not a measured number — none exists yet, which is the entire point of registering this before the run —
but a structural fact about the harness itself, verified by reading `rig/run-pipeline.sh`:

Pointer correction 2026-10-14: the four `path:line` cites below were re-anchored after `rig/run-pipeline.sh`
grew. **`verified` is deliberately left at 2026-08-13** — re-dating it would move the pre-registration,
and this edit checked locators, not the claim. The three structural facts it depends on were re-read and
still hold (`case "$ARM"` is top-level, `run_model_step()` issues one fresh invocation, `--resume` appears
zero times in the file). One pointer was not merely stale: the PIPELINE cite below said `:346`, which at
`4eddfe9` was MONOLITHIC's line, so it was **wrong the day it was written**.

- MONOLITHIC's `STEPS` array (`run-pipeline.sh:733`) is a single model step (`01-monolith`). Its
  transcript must carry the collector's findings, the diagnostic reasoning and the fix, all in one
  conversation, so its occupancy grows monotonically toward the end of the run — already observed on the
  unrelated tool-surface-v1 captures (spec R-F5.3's own scenario: "Both sampled captures were monotone,
  making peak the final turn").
- PIPELINE's `STEPS` array (`run-pipeline.sh:734`) alternates code steps (`01-collect`, `99-verify`) with
  **two separate** model steps (`02-diagnose`, `03-apply`). Each model step is launched by
  `run_model_step()` (`run-pipeline.sh:987`) as its own fresh `claude -p "$prompt_text"` invocation
  (`run-pipeline.sh:1044`) — there is no `--resume` or session-carry between steps. Each step's occupancy
  therefore resets near zero at its own start, so PIPELINE's **peak** (the max across both of its
  independent, shorter conversations) is bounded by whichever single step grows the most — never by the
  sum of both.

If that mechanism holds, PIPELINE's peak should sit well below MONOLITHIC's, independent of whether
PIPELINE's *total* work is more or less than MONOLITHIC's (that is `hypotheses/0003`'s question, not
this one — the two are deliberately separate channels, per R-F5.4's "no composite runway score").

## The test

Stage 2 (`task_id: s2`, both arms), N per cell per R-F7.2's variance rule (start at 5, escalate to 10 or
15 on mixed results). Every row already carries `peak_occupancy_tokens` (`rig/derive.py`), so no new
instrumentation is needed — only the comparison.

| Observation | Verdict |
|---|---|
| Median PIPELINE peak ≤ **0.5×** median MONOLITHIC peak, AND the two arms' observed ranges do not overlap | **Supported** |
| The two arms' ranges overlap, OR PIPELINE's median peak ≥ MONOLITHIC's median peak | **Refuted** |
| Neither condition is reached (e.g. PIPELINE median sits between 0.5× and 1.0× MONOLITHIC's, or ranges overlap only partially in a way neither clause above covers) | **Not testable at this budget** — reported with the actual medians and ranges, never rounded into one of the two boxes above |

Both `min`/`max` per (task_id, arm) MUST ship with the median (R-F7.2's own reporting rule; a mean alone
is never sufficient), and the excluded-slot list (voids, shakedowns) MUST be named per the same discipline
`rig/report.py` already applies to tool-surface-v1.

**Pre-registered guard.** A `void` row (any `void_reason`, including `no-preregistration` or
`surface-mismatch`) never enters either arm's distribution — the same exclusion rule task 5.7 proved live
against `rig/report.py`'s own `state=="complete"` filter.

## What it would change

| If | Then |
|---|---|
| Supported | A new `theory/` file on the measured evidence: splitting a task into separately-invoked model steps bounds single-turn context growth, independent of total task size |
| Refuted | The mechanism named above does not hold at the measured scale — `theory/agents/tool-surface-design.md` and any future runway advice must not assume pipelining lowers peak occupancy without re-deriving why |
| Not testable at this budget | Stays open, with the medians, ranges and the N that would need to grow (R-F7.2's own escalation path) to resolve it |

## Result — 2026-10-17

**Refuted on the fixture and task class tested. PIPELINE's peak is not lower — it is the same height, 1.4 per cent above.**

Stage 2 (`task_id: s2`, `failure-flood/v2`), N=5 per arm. All ten rows `state=complete`, `void_reason=null`. Excluded rows named, never silently dropped (this file's own pre-registered guard, and `rig/report.py`'s reporting rule): `s1-monolithic-01`, `s1-monolithic-9054`, `s2-pipeline-9054` — all `void`, `void_reason=shakedown`, none entering either distribution.

| peak occupancy tokens, N=5 | MONOLITHIC | PIPELINE |
|---|---|---|
| min / max / **median** | 83,420 / 92,813 / **85,224** | 82,834 / 89,242 / **86,423** |

PIPELINE median ÷ MONOLITHIC median = **1.0141** against the **0.5×** threshold, and the observed ranges **overlap** (82,834–89,242 against 83,420–92,813).

**The row that fired, quoted from this file's own pre-registered table:**

> | The two arms' ranges overlap, OR PIPELINE's median peak ≥ MONOLITHIC's median peak | **Refuted** |

**Both disjuncts hold at once** — the ranges overlap *and* PIPELINE's median is the higher one — so the verdict does not depend on which side of the disjunction is read. The third row cannot apply: the ratio is not between 0.5× and 1.0×, and the overlap is total rather than partial.

### Why the mechanism did not show up, measured rather than narrated

The claimed mechanism (per-step context reset bounds the max turn) is arithmetically real and simply had nothing to bound. PIPELINE's two model steps **finish at nearly the same level as each other**:

| per-step peak, N=5 | min / max / median |
|---|---|
| `02-diagnose` | 81,372 / 89,242 / **86,423** |
| `03-apply` | 81,966 / 84,474 / **82,834** |

The run-level peak is whichever step ends higher, and that is not stable — `02-diagnose` holds it in 3 of 5 runs, `03-apply` in 2. Every row in both arms carries `occupancy_is_monotone: true`, so a run's peak is where its longest step *finished*, never an intermediate spike. A reset buys nothing when neither stage grows its context much: this task ends near 85k tokens by either harness shape, and MONOLITHIC gets there in one conversation. The prediction was not wrong about the mechanism; it was wrong that the mechanism was **load-bearing at this task size**.

### What that does and does not license

Refuted means: **at this task size, on this fixture, splitting into two separately-invoked steps produced no peak reduction the design could detect.** R-F7.2 stopped the cell at N=5, so no larger N was purchased and none is claimed. It does **not** mean pipelining never bounds peak occupancy: the design never tests a task where one stage grows context far past where the other ends, which is precisely the regime where the mechanism would bite. Saying otherwise would be the over-reach this file was written to prevent.

### Disclosures that ship with this verdict

- **A pre-campaign direction existed and was withheld until the campaign closed**, per the operator's decision recorded in `odd/tasks/verified-agent-delivery.md` L21, so no reader can mistake N=1 for having shaped how N=5 was read. The disclosure of having seen it arrives here, with the countable numbers, as L21 promised.
- **The N=5 stop was decided under a reading of R-F7.2 that this repo does not implement.** `sdd/archive/2026-08-18-failure-flood-triage/verify-report.md` records R-F7.2 as *"Not implemented / not yet applicable… nothing enforces or reports it"*, so the requirement's `attribution precision/recall range ≤ one correctly-attributed cause` had no code to disambiguate it and the reading is mine: **recall taken as primary, precision published alongside rather than decided between**. Here they coincide exactly — both ranges are 0.1667 for MONOLITHIC (`causes_present: 6`, so one cause of six) and 0.0000 for PIPELINE — so no tie-break was needed and the stop holds under either reading. The green-restore condition also holds: 5/5 `green` in both arms.
- **Reproducibility boundary.** The published 13-row golden `rig/results/failure-flood-v1/runs.jsonl` is derived from captures under gitignored `rig/runs/` (`.gitignore:40`, zero tracked files there). A fresh clone and CI therefore cannot re-derive these medians; they reproduce only in a checkout holding the captures. `tool-surface-v1` already publishes 42 rows the same way, and `.github/workflows/verify.yml` records that a clean checkout makes `rig/check.sh` truncate both goldens to zero bytes. This is the rig's existing condition, not a new defect — stated so the figure is not mistaken for a clone-reproducible one.

The companion `hypotheses/0003` is reported separately, with its own mechanism and its own verdict. Per R-F5.4 and that file's own prohibition, the two are never composited into one "pipeline is better/worse" line; **this file licenses nothing about cumulative token cost.**

## Status

**Registered 2026-08-13**, before any `s2` comparison run existed.

**Closed for this fixture and task class on 2026-10-17: refuted** — predicted a materially lower peak (≤ 0.5×), measured 1.0141× with overlapping ranges. Deliberately **not** `rejected`: a null at one task size on one fixture is not a refutation of the general mechanism, and `status: draft` is kept because ADR 0012 gives a hypothesis zero citability whatever its verdict. Promotion to `theory/` is the only route this figure becomes citable, and this result does not support one — the mechanism was found inert here, not bounded elsewhere.

It remains open for the regime the design cannot reach: a task whose stages grow context by different amounts. Testing that is a different fixture and a different change.

Frontmatter `verified:` **stays at 2026-08-13**, the registration date. Bumping it would move a pre-registration; the date of this result lives in the heading above. Precedent: `hypotheses/0001` does exactly this.
