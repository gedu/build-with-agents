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

- MONOLITHIC's `STEPS` array (`run-pipeline.sh:346`) is a single model step (`01-monolith`). Its
  transcript must carry the collector's findings, the diagnostic reasoning and the fix, all in one
  conversation, so its occupancy grows monotonically toward the end of the run — already observed on the
  unrelated tool-surface-v1 captures (spec R-F5.3's own scenario: "Both sampled captures were monotone,
  making peak the final turn").
- PIPELINE's `STEPS` array (`run-pipeline.sh:346`) alternates code steps (`01-collect`, `99-verify`) with
  **two separate** model steps (`02-diagnose`, `03-apply`). Each model step is launched by
  `run_model_step()` (`run-pipeline.sh:563`) as its own fresh `claude -p "$prompt_text"` invocation
  (`run-pipeline.sh:614`) — there is no `--resume` or session-carry between steps. Each step's occupancy
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

## Status

**Registered 2026-08-13**, before any `s2` comparison run exists. Open.
