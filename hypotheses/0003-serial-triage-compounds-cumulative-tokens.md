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

## Result — 2026-10-17

**Refuted. The named risk materialised: serial triage costs 2.95× the cumulative tokens of one continuous conversation on this fixture and task.**

Stage 2 (`task_id: s2`, `failure-flood/v2`), N=5 per arm. All ten rows `state=complete`, `void_reason=null`. Excluded rows named, never silently dropped (this file's own guard, matching `hypotheses/0002`'s): `s1-monolithic-01`, `s1-monolithic-9054`, `s2-pipeline-9054` — all `void`, `void_reason=shakedown`, none entering either distribution.

| cumulative occupancy tokens, N=5 | MONOLITHIC | PIPELINE |
|---|---|---|
| min / max / **median** | 841,922 / 1,728,216 / **908,026** | 2,609,460 / 2,936,808 / **2,682,256** |

PIPELINE median ÷ MONOLITHIC median = **2.9539**. The `Supported` threshold was ≤ **0.6×**, i.e. a median at or below 544,816 — PIPELINE landed 4.9× above the number it had to beat.

**The row that fired, quoted from this file's own pre-registered table:**

> | PIPELINE's median cumulative ≥ MONOLITHIC's median cumulative | **Refuted** — the named risk (serial triage compounding cumulative tokens past one continuous conversation) is a **live possibility**, stated as such rather than assumed away, and this is the observation that would confirm it |

PIPELINE's median is **2.9539×** MONOLITHIC's, so the clause fires outright. The `Supported` row cannot apply even partially: its ratio clause fails, and while its "ranges do not overlap" clause is technically satisfied (PIPELINE's min 2,609,460 exceeds MONOLITHIC's max 1,728,216), the ranges are separated **in the direction opposite to the claim**. The third row cannot apply either — there is no ambiguity to report; PIPELINE sits far above 1.0×, not between 0.6× and 1.0×. Separation in the wrong direction is the cleanest possible refutation, and it is reported as that rather than softened into "not testable".

### The mechanism, measured rather than narrated

The file registered the optimistic reading — that two individually shorter conversations might dodge the compounding tax *even after* paying their own re-establishment overhead. They do not, because the overhead is not small and the conversations are not short:

| per-role cumulative occupancy, N=5 | min / max / median |
|---|---|
| `02-diagnose` | 606,931 / 1,256,013 / **1,126,306** |
| `03-apply` | 1,555,950 / 2,013,380 / **1,680,795** |
| MONOLITHIC's single `01-monolith` | 841,922 / 1,728,216 / **908,026** |

Each step is its own fresh `claude -p` invocation with no session carry, so **each re-pays the fixed prompt and the collected failure context from zero**. Verified arithmetic, not inference: in all ten runs the sum of the model steps' `cumulative_occupancy_tokens` equals the run's figure exactly, so the run total *is* the two conversations added together. At the median, **the single `02-diagnose` step (1,126,306) costs more cumulative tokens than an entire MONOLITHIC run (908,026)** — a step that makes no edit at all, and which has to re-read the failure context MONOLITHIC already had in hand. Stated at the median because it does not hold run-by-run: `02-diagnose` exceeds MONOLITHIC's 908,026 in **3 of 5** pipeline runs, falling below it in the two cheapest (856,941 and 606,931). Arms are separate runs, so only the two distributions are comparable; no same-run cross-arm pairing exists. (Summing the two per-role *medians* gives 2,807,101 against a run-level median of 2,682,256 — median-of-sums is not sum-of-medians, which is why both are quoted rather than one standing in for the other.)

MONOLITHIC's own turn count is what the hypothesis bet against, and the bet was wrong: a single conversation's repeated history resend costs less than two conversations each paying the prompt twice over. At this task size the prompt is the expensive part, not the history.

### What that does and does not license

Refuted means: **on this fixture and task class, PIPELINE's cumulative token cost is materially higher, and the re-establishment cost dominates.** It does **not** license a general "pipelining always costs more": the ratio here is a property of a task whose fixed prompt is large relative to the per-step work. It also does not license the reverse reading of `hypotheses/0002`.

**No composite, per this file's own prohibition.** `hypotheses/0002`'s peak channel came back **1.0141×** — flat, no reduction. The anticipated degenerate pair (0002 supported while 0003 refuted, or the reverse) did not occur: **both are refuted, for two unrelated reasons** — peak because the two steps end at nearly the same level so a reset bounds nothing, cumulative because each fresh invocation re-pays a fixed prompt. Neither finding explains the other, neither is evidence about the other, and they ship as two published results and never as one "pipeline is worse" line.

A third channel moves the same way and is named for completeness only, **not as part of this verdict's evidence**: wall-clock-billed cost per run, read from each step's `result.total_cost_usd`, has median $0.5001 MONOLITHIC (min $0.4689, max $0.6864) against median $1.1980 PIPELINE (min $1.1118, max $1.2512). Peak, cumulative and dollars are reported separately, never blended — the R-F5.4 rule, extended to the channel this file did not register.

### Disclosures that ship with this verdict

- **A pre-campaign direction existed and was withheld until the campaign closed**, per the operator's decision recorded in `odd/tasks/verified-agent-delivery.md` L21, so N=1 cannot be read as having shaped how N=5 was read. The disclosure arrives here, with the countable numbers, as L21 promised.
- **The N=5 stop was decided under a reading of R-F7.2 this repo does not implement.** `sdd/archive/2026-08-18-failure-flood-triage/verify-report.md` records R-F7.2 as *"Not implemented / not yet applicable… nothing enforces or reports it"*, so its `attribution precision/recall range ≤ one correctly-attributed cause` had no code to disambiguate it and the reading is mine: **recall primary, precision published alongside rather than decided between**. Both readings agree here — ranges are 0.1667 for MONOLITHIC (`causes_present: 6`, one cause of six, from one run scoring 5/6) and 0.0000 for PIPELINE — so no tie-break was needed and the stop holds either way. Green-restore condition holds too: 5/5 `green` in both arms, no partial, no-progress, regressed or unscored.
- **Reproducibility boundary.** The published 13-row golden `rig/results/failure-flood-v1/runs.jsonl` derives from captures under gitignored `rig/runs/` (`.gitignore:40`, zero tracked files there). A fresh clone and CI cannot re-derive these medians; they reproduce only in a checkout holding the captures. `tool-surface-v1` publishes 42 rows the same way, and `.github/workflows/verify.yml` records that a clean checkout makes `rig/check.sh` truncate both goldens to zero bytes. Existing rig condition, stated so the figure is not mistaken for clone-reproducible.

## Status

**Registered 2026-08-13**, before any `s2` comparison run existed.

**Closed for this fixture and task class on 2026-10-17: refuted.** The file's own title named the fear it existed to check, and the fear is the finding: measured 2.9539× against a claim of ≤ 0.6×. Deliberately **not** `rejected` — this is a refutation of the optimistic reading **for this fixture and task class**, not proof that serial triage always compounds past a continuous conversation; the ratio is a function of fixed-prompt size relative to per-step work, which this design varies nowhere. `status: draft` is kept because ADR 0012 gives a hypothesis zero citability whatever its verdict.

**No `theory/` file is owed to this result, and that is the registered consequence, not an omission.** This file's `Refuted` row conditions a `theory/` write on 0002 being supported (a trade-off to state explicitly); 0002 was **not** supported, so the condition never arose and no trade-off line is licensed. Checked rather than assumed: `theory/agents/tool-surface-design.md` makes no claim about harness shape. **15 terms searched over the whole file, 13 return zero hits** — `pipeline`, `pipelining`, `peak`, `cumulative`, `occupancy`, `reset context`, `context reset`, `invocation`, `separate model`, `triage`, `serial`, `stage`, `step`. The two that do hit are about **tool-surface residency**, not about splitting a task: `harness` once ("one harness, one model, one session", a limit on its own observation) and `shape` twice (the *shape of a hypothesis* and of a recommendation). So there is no existing claim there for this result to amend. The population being counted is named because an empty grep is not evidence until you know what you searched: a first pass over 12 terms reported "zero hits" for the file as a whole and was wrong — `harness` and `shape` were in that same list and are not zero.

Frontmatter `verified:` **stays at 2026-08-13**, the registration date. Bumping it would move a pre-registration; the date of this result lives in the heading above. Precedent: `hypotheses/0001` does exactly this.
