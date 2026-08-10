---
id: sdd/measurement-rig/verify
type: journal
targets: [any]
status: validated
verified: 2026-08-10
sources: ["sdd/measurement-rig/spec.md", "sdd/measurement-rig/design.md", "sdd/measurement-rig/tasks.md", "decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0012-a-hypothesis-is-never-citable.md", "theory/agents/tool-surface-design.md", "hypotheses/0001-broad-surface-degrades-output-not-selection.md"]
---

# verify — measurement-rig

Validation of the implementation against `spec.md` and `design.md`.

**Verdict: PARTIAL.** The instrument is built and one channel produced a promoted figure. The other
channel has never been shown to work, and one spec requirement is unsatisfied because of it. This
cycle does not verify clean, and recording it as clean would be the exact failure `decisions/0011`
exists to prevent.

## Task ledger

51 done, 5 cancelled, 0 open, as of 2026-08-10. The last open item — 6.3, the derived timeout not
applied to `rig/run.sh` — was closed the same day. Every cancellation is named in Amendment 2 with
its reason; none is a silent drop.

## What is verified

**The cost channel.** One figure was promoted to `theory/agents/tool-surface-design.md` carrying its
scope and the honesty contract: **≈224 tokens per resident tool entry**, from 12 pairs at 32 versus 3
tools, median 6,489 extra cache-creation tokens for 29 extra names. Positive 12 of 12, sign test
p=0.000244, Mann-Whitney on the 9 same-order pairs p=0.000021. This satisfies the promotion rule in
`decisions/0011`: the rig produced evidence, and the figure became citable only by promotion.

**The safety contract holds, and was proven rather than asserted.** The MANIFEST guard was verified
live in both directions on the `v2` fixture — accept before the freeze, exit 2 on a post-freeze byte
tamper (8b.5). The three-state exit contract (R-A1.1) is implemented and exercised. `derive.py` is
idempotent: two runs are byte-identical, and the 15 pre-existing rows re-derive unchanged across the
schema-2 bump (8b.4). A schema change that leaves old rows intact is the only kind that can be
trusted afterwards.

**The instrument-doubt threshold did its job.** X=3 tripped, was investigated rather than waved
through, and was cleared by the deliberate-versus-spontaneous split (9.2). A threshold that has
never fired is not evidence that a system is sound; this one fired and resolved.

**R-A1.3 held under pressure.** `defects_found` / `defects_missed` / `defects_extra` ship as three
separate counts and are never summed into a score, including in the `v2` work where a composite
would have been convenient.

## What is NOT verified, and why the verdict is PARTIAL

**R-A1.4 — "Every detector must be proven able to fire" — is unsatisfied for the quality detector.**

Across both fixture generations, every completed run classified `proper`: 12 of 12, in both arms,
zero defects missed, zero invented. Neither deliberately planted near-miss was ever reported by any
run. The `v2` fixture was built specifically to fix this — three real defects instead of one, two
near-misses, no bolding, no steering sentence, a prompt naming only the entry point (8b.2, 8b.3) —
and it still did not discriminate (8b.6).

So the quality channel has never produced a completed run that failed cleanly. A detector that has
never fired cannot distinguish "the arms are equivalent" from "this instrument cannot see a
difference." Per R-A2.3 that is **not tested**, never a verdict.

**Consequence for the falsification table.** Task 9.3 recorded exactly one verdict: **not supported**
for defect-reporting tasks, and deliberately **not** `rejected`. That is the correct call and it is
worth stating why — a null on one task class does not refute the general claim. `hypotheses/0001`
stays open, and per `decisions/0012` it stays non-citable while open.

**Consequence for the design.** The limitation is not in the runner, the analyser or the checker;
all three work. It is in the task class. A defect-reporting task over a frozen fixture has a single
correct answer, so it can only expose cost differences, not quality ones. Answering
`hypotheses/0001` needs a task class without one right answer. That is a fixture-design problem, not
a bug, and it is the real blocker in front of Phases 6, 7 and 9 being worth funding live.

## Honesty contract (R-A1.6) — the gaps that ship with the result

1. The quality channel has never discriminated, on either fixture generation.
2. The promoted figure is a cost measurement only. Nothing in this cycle licenses a claim about
   output quality.
3. Sample size stayed at pilot scale — 3 pairs per generation, below `hypotheses/0001`'s own
   pre-registered power table. No conclusion was drawn from it, and none may be.
4. One anomaly is on the record rather than dismissed: `t3v2-broad-00` voided `surface-mismatch` on a
   cold start (31 tools against a 32-tool preimage) immediately before three consecutive matching
   runs. A single flake, published because the alternative is a clean log that lies.
5. Two flags found after this cycle closed, both relevant and neither invalidating: `--tools` is the
   documented way to restrict the built-in set, which this rig does by hand with `--disallowedTools`;
   and `--bare` is the recommended mode for scripted calls. Every committed row verified its achieved
   surface against a preimage, so no result is void — but both belong in any revision.

## What would move this to a clean verdict

One fixture generation in which a completed run can fail cleanly — a task class with no single right
answer, where recall and precision can genuinely diverge between arms. Until then the rig is a
verified cost instrument and an unverified quality instrument, and it should be described that way
everywhere it is cited.
