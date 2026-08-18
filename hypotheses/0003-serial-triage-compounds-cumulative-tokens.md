---
id: hypotheses/0003-serial-triage-compounds-cumulative-tokens
type: research
targets: [any]
status: draft
verified: 2026-08-13
sources: ["sdd/failure-flood-triage/spec.md", "sdd/failure-flood-triage/design.md", "rig/run-pipeline.sh", "hypotheses/0002-pipeline-shape-lowers-peak-occupancy.md", "decisions/0012-a-hypothesis-is-never-citable.md"]
---

# 0003 — Serial triage does not compound cumulative tokens past a single continuous conversation

**Registered before the stage-2 (`s2`) comparison run that could settle it.** Nothing here may be
cited — see ADR 0012. Naming `hypotheses/0002` as a companion below is testing it, not citing it.

## Logical form: STATISTICAL

Same declaration discipline as `hypotheses/0002`: no single run refutes or supports this claim; only N
with spread (spec R-F7.2) settles it.

## Filename names the risk, not the predicted direction — stated up front so it cannot be read backwards

This file's title is the **fear** this hypothesis exists to check, not the claim it predicts will hold.
`hypotheses/0002` argues PIPELINE resets context per step, which should lower its **peak**. The obvious
worry that raises: if PIPELINE must re-establish context at the start of each of its two model steps
(`02-diagnose`, `03-apply`), does that repeated re-establishment **compound** — add up to more total
("cumulative", spec R-F5.2: the sum over deduplicated turns) tokens than MONOLITHIC's one continuous
conversation spends? If yes, 0002's peak win would come at a real cumulative-token cost, and the two
channels would trade off rather than both favouring PIPELINE.

**The claim registered here is the optimistic reading, not the fear**: that despite the per-step
re-establishment cost, PIPELINE's *total* cumulative tokens across both of its model steps still land
materially below MONOLITHIC's. The mechanism: a single continuous conversation resends its entire growing
history on every turn (R-F5.2's "already an aggregate over all turns, not the final turn" finding from the
tool-surface-v1 captures), so a long MONOLITHIC conversation's cumulative total grows compounding-like on
its own turn count — two separate, individually shorter PIPELINE conversations may avoid paying that same
compounding tax twice, even after their own re-establishment overhead is added in.

## Claim

For the failure-flood-triage comparison (`task_id: s2`, `failure-flood/v2` fixture), the **PIPELINE**
arm's cumulative occupancy — summed over all deduplicated turns across both of its model steps — is
**materially lower** than the **MONOLITHIC** arm's cumulative occupancy. The named risk (that splitting
work into serial stages compounds cumulative cost beyond one continuous conversation) does **not**
materialise at the measured scale.

## The test

Stage 2 (`task_id: s2`, both arms), N per cell per R-F7.2's variance rule. Every row already carries
`cumulative_occupancy_tokens` (`rig/derive.py`; R-F5.2 notes it requires no new capture, only summation),
so no new instrumentation is needed — only the comparison.

| Observation | Verdict |
|---|---|
| Median PIPELINE cumulative ≤ **0.6×** median MONOLITHIC cumulative, AND the two arms' observed ranges do not overlap | **Supported** — the named risk did not materialise |
| PIPELINE's median cumulative ≥ MONOLITHIC's median cumulative | **Refuted** — the named risk (serial triage compounding cumulative tokens past one continuous conversation) is a **live possibility**, stated as such rather than assumed away, and this is the observation that would confirm it |
| Neither condition is reached (ranges overlap without PIPELINE's median exceeding MONOLITHIC's, or PIPELINE sits between 0.6× and 1.0×) | **Not testable at this budget** — reported with the actual medians and ranges |

Both `min`/`max` per (task_id, arm) MUST ship with the median, and excluded (`void`) rows are never part
of either distribution, matching `hypotheses/0002`'s own guard.

**No composite with `hypotheses/0002`.** Peak and cumulative are reported as two separate tables
(`rig/report.py`, spec R-F5.4); this file's verdict never gets averaged, weighted or ANDed with 0002's.
A degenerate outcome — 0002 supported while this file is refuted, or the reverse — MUST remain visible
as two separate published results, not collapsed into one "pipeline is better/worse" line.

## What it would change

| If | Then |
|---|---|
| Supported | A new `theory/` file on the measured evidence: serial triage lowers both peak and total cumulative token cost relative to one continuous conversation, at the measured scale |
| Refuted | The same `theory/` write must state the trade-off explicitly if 0002 is also supported: lower peak occupancy purchased at the cost of higher cumulative tokens — never silently reported as "pipeline is better" |
| Not testable at this budget | Stays open, with the medians, ranges and the N that would need to grow (R-F7.2's escalation path) to resolve it |

## Status

**Registered 2026-08-13**, before any `s2` comparison run exists. Open.
