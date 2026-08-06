---
id: research/agent-loop-oracle
type: research
targets: [any]
status: validated
verified: 2026-08-06
sources: ["https://blogs.oracle.com/developers/what-is-the-ai-agent-loop-the-core-architecture-behind-autonomous-ai-systems", "research/agent-loop-termination-kinney.md", "research/llm-as-code-agentic-programming.md", "theory/loops/verifier-availability.md"]
---

# What Is the AI Agent Loop? (Oracle)

## Claim

That the agent loop — an LLM invoking tools inside an iterative perceive → reason → plan → act →
observe cycle — is the single architectural difference between a chatbot and an agent; that every
major AI organisation has converged on it; and that taking it to production is dominated by two
constraints, **cost** (roughly 4x tokens for a single agent, up to 15x multi-agent) and
**observability**.

## Source

Casius Lee, AI Developer Advocate, Oracle. Published 2026-03-16.

**Provenance note, recorded because it changes what this entry rests on.** The URL returns **HTTP 403**
to automated access; it was adjudicated on 2026-08-06 from **text supplied by the operator**, not from
a fetch. Nothing suggests the text is anything other than the article, but this entry cannot claim to
have verified the page itself, and the quotes below are only as good as that transcript. A later reader
with browser access should confirm the figures if any of them becomes load-bearing.

Oracle sells the database positioned in the piece's implementation section. By `skills/source-verdict`
test 6 that is the incentive, and it is worth noting that **none of the technical claims depend on it** —
the architecture section would read identically with the vendor removed.

## Contrast

### The finding that matters most, and it is about the corpus rather than this source

Two of this piece's headline figures are **the same unsourced figures already recorded in
`research/agent-loop-termination-kinney.md`**, attributed to the same third party by both:

| Figure | Oracle's attribution | Kinney's attribution |
|---|---|---|
| ~4x tokens single-agent, ~15x multi-agent | *"Anthropic's internal data"* | *"Anthropic published internal data"* |
| Multi-agent beat single-agent by **90.2%** | *"internal research evaluations"* | *"Anthropic's internal evaluations"* |

Neither source discloses a method. Neither gives a denominator for 90.2%. And critically: **their
agreement is not corroboration.** Two documents quoting one unsourced vendor figure is one unsourced
vendor figure appearing twice. It reads like independent confirmation and carries no additional weight
whatsoever.

This is the concrete instance of a bias this repo had already reasoned about abstractly — that a corpus
of *shared* sources selects for what circulates, which is the thing being filtered for. Seeing the same
two numbers arrive from an independent author and a vendor advocate, three months apart, in pieces with
no other overlap, is what that bias looks like from the inside.

**The operational rule this produces**, which `skills/source-verdict` test 2 does not currently state:
when a figure with no disclosed method appears in N sources, check whether the N attributions resolve
to the same origin **before** treating repetition as weight. If they do, N is 1.

### Where it genuinely corroborates, independently

**Stopping conditions.** Oracle names *"maximum iteration limits, no-progress detection (exiting when
repeated iterations produce no new information), and token/cost budgets as hard guardrails"*, and adds
goal-achievement checks in its FAQ. That is the same layered set as Kinney's, arrived at without either
citing the other, and both frame a maximum-iteration cap as **one guardrail among several rather than
the stopping mechanism.**

This is real convergence rather than a shared citation, because it is design guidance rather than a
number — nobody is quoting anybody. It independently supports the section already promoted into
`theory/loops/verifier-availability.md`, and Oracle's "no new information" phrasing is a slightly
sharper statement of no-progress detection than Kinney's fingerprint mechanism, which detects only
*identical* repetition.

Its illustration of the failure is handled more honestly than Kinney's, and the difference is worth
recording: Oracle explicitly frames its runaway-loop example as *"The following scenario illustrates"*
— a constructed case, labelled. Kinney's *"one production system saw the same answer repeated 58
times"* is presented as an observation with no attribution. **Same rhetorical function, and only one of
them tells you it is not data.**

**When not to use a loop at all.** *"Workflows that follow a fixed, predictable sequence of steps are
better served by deterministic pipelines"*, and single-step tasks do not justify the overhead. That is
the boundary condition of `research/llm-as-code-agentic-programming.md` approached from the opposite
side: the paper says program-controlled flow wins *"when a workflow has a known structure"*; Oracle says
a known structure should not be an agent loop in the first place. Two sources, opposite starting points,
same line drawn in the same place.

**A first-party Anthropic quote**, usable as such: agents are *"typically just LLMs using tools based on
environmental feedback in a loop."*

### One new checkable number

*"The original paper (Kim et al., ICML 2024) reports a 3.6x speedup over sequential ReAct-style
execution"* for LLMCompiler's DAG-parallel plan-and-execute. Cited to a named paper at a named venue —
the strongest provenance tier in this piece and new to this repo. Not verified against the original
here.

Note what it measures: **speed, not reliability.** It is adjacent to LLM-as-Code's argument that control
flow belongs in the program, and it is not evidence for it. Do not merge them.

The ReAct figures (*"34% improvement on ALFWorld and 10% on WebShop"*, Yao et al. 2022) are cited and
checkable. The 34% also appears in Kinney — but both trace to the same named public paper, which is the
legitimate case: a shared citation to a *checkable* origin is fine, because the origin can be attacked.

### Where it is not evidence

The six-organisation convergence table and the five-stage loop are **taxonomy**. By test 1 no
observation would contradict them, so they are vocabulary and a map, not claims. Useful for talking;
they would not change a design decision here.

*"Cost-per-task will replace cost-per-token as the primary efficiency metric"* is a prediction, and its
supporting argument — an agent costing 15x tokens is cheaper if it avoids a human escalation — is
sound reasoning with no accompanying measurement of escalation rates or costs.

**Local reproduction: not run.** The runnable notebook Oracle publishes was not executed, and no Oracle
database exists here.

## Verdict

**`partially supported`.**

- **Supported** for the layered stopping-condition guidance, independently converging with a second
  source on design rather than on a shared citation. This is the piece's real contribution.
- **Supported** for the boundary condition — fixed sequences belong in deterministic pipelines — which
  agrees with an adjudicated paper reasoning from the opposite direction.
- **Supported as vocabulary** for the five-stage loop and the cross-vendor convergence table, with the
  note that a taxonomy is not a claim.
- **Not supported** for its two headline figures. The 4x/15x token multipliers and the 90.2%
  multi-agent result have no disclosed method, and their presence in a second source adds **no** weight
  because both attributions resolve to the same unsourced origin. This repo must not cite either.
- **Unverified** for the 3.6x LLMCompiler speedup — well-cited, not checked here, and about speed
  rather than reliability.

## Follow-up

**A method change, which is the most valuable thing this source produced.** `skills/source-verdict`
test 2 grades a number by its provenance tier but says nothing about **repetition across sources**. This
piece plus the Kinney entry demonstrate the gap concretely: the same two unsourced figures, two authors,
three months apart, no overlap otherwise, reading as consensus. Test 2 should require resolving
attributions to their origin before counting agreement, and should state that repetition of an
unsourced figure is not evidence.

**No new `theory/` file.** The stopping-condition convergence strengthens a section already promoted
into `theory/loops/verifier-availability.md`; the right change there is to record that the layered-set
guidance now has two independent sources rather than one, and to adopt Oracle's "no new information"
framing alongside the narrower identical-fingerprint mechanism.

`research/agent-loop-termination-kinney.md` should carry a pointer to the shared-figure problem, so
neither entry is read alone and its numbers mistaken for independently attested.
