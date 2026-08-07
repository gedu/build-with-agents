---
id: hypotheses/0001-broad-surface-degrades-output-not-selection
type: research
targets: [any]
status: draft
verified: 2026-08-07
sources: ["rig/results/tool-surface-v1/runs.jsonl", "theory/agents/tool-surface-design.md", "sdd/measurement-rig/spec.md", "research/claude-certified-architect-exam-guide.md"]
---

# 0001 — A broad tool surface degrades output quality, not tool selection

**Registered before the tier-3 runs that could settle it.** Nothing here may be cited. See ADR 0012.

## Logical form: STATISTICAL

Declared per `skills/hypothesis-cycle` step 0, and it was **missing from the first draft of this file** —
found by the skill's first application to it. The omission mattered: without a declared form, the file's
test table could be read as accepting a single counterexample, which for a statistical claim proves
nothing.

**Consequences of the form, and they bind:**

- **No single run refutes this.** "I found a case where BROAD answered correctly" is one draw from a
  distribution. The claim never said *always*.
- **No single run supports it either.** The t1 pair below is one observation and is offered as the
  reason to test, never as evidence.
- Only **N with spread** settles it.

## Claim

A broad visible tool surface degrades an agent's **output quality** — precision, restraint, false
positives — **independently of whether it changes which tools the agent calls.**

If true, the mechanism named in `theory/agents/tool-surface-design.md` is wrong in its channel. That
file says selection reliability degrades because selection happens over resident names. This says the
names cost something even when selection is unaffected, which points at context dilution rather than
decision complexity.

Note what this is **not**: it is not a claim that surface size is harmless, and not a claim that the
existing theory file is wrong to care about surface size. Both would still be about surface size. The
disagreement is entirely about **through what**.

## Why it is plausible

One observation, and it is one observation. The first real run pair of the measurement rig, task t1,
BROAD 31 visible tools versus SCOPED 3:

| | BROAD | SCOPED |
|---|---|---|
| tool calls | `Glob`, `Read` | `Glob`, `Read` |
| off-set calls | 1 | 1 |
| forbidden calls | 0 | 0 |
| answer | `paginate.js:24` **and** `paginate.js:23` | `paginate.js:24` |
| cell | `clean-failure` | `proper` |

**Identical tool calls. Different answers.** BROAD added a line that is a function signature, not a
defect. The answer key names one defect.

The obvious reading is that tier 1 is too small to permit tool variation, so an effect surfaces
elsewhere — which is the reading that motivated running tier 3. This hypothesis is the **other**
reading, written down so that reading tier 3's result cannot be a choice made after seeing it.

Independent reason to take it seriously: the first-party guidance this repo already adjudicated
attributes the problem to *"increasing decision complexity"*
(`research/claude-certified-architect-exam-guide.md`), which is a claim about the **decision**. If the
decision is provably unchanged and the output still degrades, that attribution does not survive as
stated.

## The test

Tier 3, both arms, N per cell per the spec's variance rule. Every run's transcript already carries the
tool-call list and the classification, so no new instrumentation is needed.

**Partition every completed pair by whether the tool-call multiset differed between arms.**

| Observation | Verdict |
|---|---|
| Arms differ in **tool calls** AND in outcome, and outcome tracks tool-call divergence | **Refuted.** The channel is selection, as `tool-surface-design.md` says |
| Arms produce **identical tool-call multisets** AND BROAD's `proper` rate is materially lower | **Supported.** The effect exists where selection is provably unchanged |
| Arms differ in tool calls **and** identical-call pairs also show the outcome gap | **Both channels are live.** Neither claim is complete; the theory file gains a second mechanism |
| No material `proper`-rate gap in either partition | **Null.** Neither this nor the existing claim is supported at this contrast, and the theory file narrows |

"Materially lower" is not decided here on purpose — the spec's variance rule sets what counts, and
fixing a threshold now with n=1 visible would be choosing it against a number already seen.

**Pre-registered guard.** The identical-call partition must be **non-empty** for a `supported` verdict.
If every pair differs in tool calls, this hypothesis is untestable by that run and the verdict is
"not tested" — never "refuted". A hypothesis that cannot fire is not evidence against itself.

### Power: what N can actually resolve, computed before the run

`skills/hypothesis-cycle` step 1 check 4 asks whether the affordable sample could distinguish the
claimed effect from noise. Computed here rather than assumed, one-sided Fisher exact at p ≤ 0.05 over
independent runs:

| N per arm | Smallest gap reaching significance |
|---|---|
| 5 | 5/5 vs 1/5 — **80 percentage points** |
| 10 | 10/10 vs 6/10 — 40 points |
| 15 | 15/15 vs 11/15 — 27 points |
| 30 | 30/30 vs 25/30 — 17 points |

**The spec's N=5 floor can only detect a near-total effect.** A 30-point difference — large, real and
worth knowing — is invisible at N=5 and still invisible at N=10.

**And Amendment 2's partition makes this strictly worse.** Splitting completed pairs into identical-calls
and differing-calls divides the sample: 10 pairs splitting 6/4 leaves n=6 in the partition that carries
this hypothesis, not 10. The partition is epistemically necessary and statistically expensive, and that
cost was not priced when it was introduced.

**Pre-registered consequence, declared now so it cannot be chosen later:**

| Observed in the identical-calls partition | Verdict |
|---|---|
| Gap ≥ the significance threshold for that partition's actual n | **Supported**, with the n and the threshold stated |
| Gap below that threshold, in either direction | **Not testable at this budget.** NOT a weak positive, NOT a refutation |
| Partition empty | **Not tested** |

A gap that looks like a trend and does not reach its threshold is the single most likely outcome of an
under-powered run, and reporting it as a finding is how an under-powered experiment produces a
confident wrong answer.

## What it would change

| If | Then |
|---|---|
| Supported | `theory/agents/tool-surface-design.md` keeps its advice and loses its mechanism. "Selection happens over resident names" narrows to "resident names cost something", and the levers section needs re-deriving — scoping would still help, but not for the stated reason |
| Refuted | That file's mechanism gains its first direct evidence, which it currently lacks entirely |
| Both | The file gains a second mechanism and must say which lever addresses which |
| Null | The claim narrows to the contrast actually tested, 31 versus 3 with MCP excluded, and says so |

In every branch the honesty contract from the spec ships with the result, and per ADR 0011 the number
is citable only once promoted into `theory/` with its scope and spread.

## Status

**open** — registered 2026-08-07, before any tier-3 run exists.

Amended the same day by the first application of `skills/hypothesis-cycle`, which found the logical form
undeclared and the planned N under-powered. Both were fixed before any tier-3 run, which is the only
moment either fix is worth anything.
