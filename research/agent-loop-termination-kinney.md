---
id: research/agent-loop-termination-kinney
type: research
targets: [any]
status: validated
verified: 2026-08-06
sources: ["https://stevekinney.com/writing/agent-loops", "theory/loops/verifier-availability.md", "research/claude-certified-architect-exam-guide.md"]
---

# Agent Loops (Steve Kinney)

## Claim

Two things, and they need separating because they carry different weight.

1. **A structural claim**: the agent loop is a `while` over LLM-call → tool-call → append-results,
   terminating when the model returns text instead of tool calls. *"A text-only response is the
   termination signal… Tool calls are the continuation signal."*
2. **A design claim about termination**: an iteration cap is not sufficient as a stopping mechanism.
   *"Max iterations alone isn't enough; you need loop fingerprinting **and** cost budgets **and**
   no-progress detection."*

The second is the one worth having.

## Source

`https://stevekinney.com/writing/agent-loops`, accessed 2026-08-06. Independent author; a courses
page and a newsletter exist on the same site, but the piece carries no pitch and its claims are
attributed rather than asserted.

## Contrast

**The termination claim independently corroborates a first-party anti-pattern this repo already
carries.** `research/claude-certified-architect-exam-guide.md` records Anthropic listing *"setting
arbitrary iteration caps as the primary stopping mechanism"* as a loop-termination anti-pattern, and
that claim forced a correction to `theory/loops/verifier-availability.md`, which had praised a bounded
correction budget without distinguishing a backstop from a primary signal.

This piece arrives at the same rule from outside the vendor, and it adds the part the guide does not:
**concrete detectors.** Fingerprint each iteration's `(tool_name, result_preview)` tuple and stop on
three identical fingerprints in a row; a wall-clock ceiling; a spend ceiling. Those are mechanisms a
`theory/` file can name, where "do not rely on a cap" is only a prohibition.

It also supplies the failure mode in observed form: *"one production system saw the same answer
repeated 58 times before anyone intervened."* Anecdotal, unattributed, and useful only as an
illustration of the shape — not as a measurement.

**Where its numbers do not survive.** The piece is dense with figures and almost none of them are the
author's. Sampling by `skills/source-verdict` test 2:

| Figure | Provenance tier |
|---|---|
| 74–76.8% on SWE-bench Verified for a ~100-line agent | Cited to a named public repository. Checkable |
| 34% improvement on ALFWorld | Cited to ReAct (Yao et al., 2022). Checkable |
| ~30% fewer steps for code-as-action | Cited to a named paper. Checkable |
| Tool responses = 67.6% of tokens; system prompt 3.4% | Attributed to the Manus team's published findings. Second-hand |
| 1x / 4x / 15x tokens for chat / single-agent / multi-agent | Attributed to Anthropic, **no method disclosed** |
| Multi-agent beat single-agent by 90.2% | Attributed to Anthropic internal evals, **no method** |
| Same answer repeated 58 times | **No attribution** |

Nothing here is measured by the author. That is not dishonest — the piece is a synthesis and it names
its sources — but it means the correct citation for any of these is the original, not this page. The
90.2% in particular is a bare percentage with no disclosed denominator, and this repo should not
repeat it.

**The 67.6% figure is interesting for a different reason**: it says tool *responses*, not tool
*schemas*, dominate context. `theory/agents/capability-load-cost.md` measured schemas and conversation
separately and found conversation at 91.8%. The two are consistent and describe different slices —
worth noting so nobody reads them as contradictory later.

## Verdict

**`partially supported`.**

- **Supported** for the termination design claim: an iteration cap is a backstop, not a stopping
  signal, and progress/cost/repetition detectors are the real mechanism. Independently corroborated
  by first-party guidance already adjudicated here, and it adds implementable detail that guidance
  lacks.
- **Supported** for the loop skeleton and the text-vs-tool-call termination signal, as vocabulary. It
  is definitional, so it is not evidence of anything.
- **Not supported as a source for numbers.** Every figure is second-hand; two of the most quotable
  (1x/4x/15x, 90.2%) have no disclosed method and one has no attribution at all. Go to the originals
  or do not cite the number.

## Follow-up

The termination detectors belong in `theory/loops/verifier-availability.md`, whose bounded-budget
section already distinguishes backstop from primary signal but names no alternative. Adding
fingerprinting, no-progress detection and cost ceilings makes that section actionable instead of
merely corrective.

Do **not** promote any figure from this page. If the SWE-bench or ALFWorld numbers matter later, the
originals are named and reachable.
