---
id: theory/loops/verifier-availability
type: theory
targets: [any]
status: validated
verified: 2026-08-06
sources: ["journal/2026-08-05-first-commit-gate-bypass.md", "journal/2026-08-05-second-gate-bypass-agent-conflict.md", "journal/2026-08-05-redaction-gate-and-2478-on-224.md", "decisions/0008-review-lenses-may-use-subagents.md", "research/claude-certified-architect-exam-guide.md", "research/gentle-orchestrator-anatomy-guide.md", "research/llm-as-code-agentic-programming.md", "research/agent-loop-termination-kinney.md"]
---

# A verifier that cannot run is not a weak gate — it is an absent gate that reports "not run"

**The claim.** In any loop — act, observe, **check**, repeat — the check is the only component that
distinguishes a loop from a script. When the check becomes *unavailable* rather than *failing*, the
loop silently degrades into a script while every surface still describes it as gated. The dangerous
state is not a verifier that says no. It is a verifier that says nothing.

## The distinction that carries the weight

Three states are routinely collapsed into one, and they are not the same:

| State | What it reports | What it means |
|---|---|---|
| Verifier ran, passed | `pass` | Evidence exists |
| Verifier ran, failed | `fail` | Evidence exists, and it is negative |
| **Verifier could not run** | `not run` / gate skipped | **No evidence, and no negative signal either** |

The third row is the one that ships unverified work. It produces no alarm, because nothing failed.
`fail` is loud and blocks. `not run` is quiet and is trivially rationalised — each individual
instance has a reason, and the reasons are usually true.

## The evidence

Three commits shipped without a review receipt on 2026-08-05, all in one working day, on a toolchain
whose delivery gates are designed to **fail closed**.

Fail-closed behaved correctly throughout. That is the uncomfortable part: nothing malfunctioned in
the gate. What was missing was any reachable path to satisfy it.

| Bypass | Cause | Could a release fix it? |
|---|---|---|
| 1 | The tool's own lifecycle could not reach a receipt; the next transition required a maintainer authorization an orchestrator may not construct | Possibly — filed upstream |
| 2 | The selected lens runs as a sub-agent; an active session directive forbade sub-agents | **No** |
| 3 | Same as 2 | **No** |

In bypasses 2 and 3 the review *started* successfully: it froze a target, classified risk as medium,
selected one lens, and opened a correction budget of 200 lines. Then it stopped, because the
verifier itself was unreachable. **A started-and-unfinishable review is indistinguishable from no
review at commit time**, except that it leaves a lineage in `reviewing` state that a later session
can mistake for a blocker.

## Two failure modes this produces

**Deadlock converting into habit.** An unsatisfiable fail-closed gate leaves exactly two options:
stall indefinitely, or ship and document. Documenting is correct once. By the third time in one day,
the audit trail has become a list of excuses, and — this is the measurable part — **a bypass that is
always taken carries zero information.** Its presence in the log no longer distinguishes risky
changes from safe ones.

**Misdiagnosis of the gate's strength.** From the outside, "the gate is failing closed" reads as a
strict gate doing its job. It was in fact an absent verifier. Strictness and availability are
independent properties, and conflating them produces false confidence in exactly the direction that
matters.

The resolution required an authority decision
(`decisions/0008-review-lenses-may-use-subagents.md`), not a tooling fix. Worth noting for loop
design generally: **verifier availability is a configuration property, not a code property**, so it
will not appear in tests of the verifier itself.

## Bounded correction as a termination rule

The same toolchain supplies a loop-termination mechanism worth recording separately, because it
answers a question most act-check-repeat loops leave open — when does the fix loop stop?

```
correction_budget = min(200, ceil(original_changed_lines / 2))
```

Observed frozen at review start alongside the risk tier. Two properties:

- **Termination by budget, not by convergence.** The loop cannot iterate until the checker is
  satisfied. It gets a bounded allowance, and exhausting it escalates instead of continuing. A loop
  that terminates only on convergence has no upper bound when convergence never arrives.
- **Effort tied to scope.** Derived from the size of the change under review and capped absolutely,
  so a large change cannot authorize unbounded automated rewriting of itself.

This bounds the blast radius of an automated fix loop. It is a different question from verifier
availability, and it is recorded here because both are properties of the check, not of the action.

**A correction, because an earlier draft of this file praised the budget without qualification.**
Anthropic's architect guide lists, among agentic-loop anti-patterns, *"setting arbitrary iteration
caps as the primary stopping mechanism"*, alongside parsing natural language to decide termination
and checking assistant text for completion
(`research/claude-certified-architect-exam-guide.md`). A cap is therefore not a virtue by itself.

The distinction that makes the budget defensible: it is a **backstop, not the primary signal**. The
primary signal is whether the frozen finding set clears; the budget bounds how much rewriting may be
spent trying. A cap used as the *primary* termination condition hides the absence of a real
completion test — which is the same failure this file is about, arriving from the other direction: a
loop that stops on a counter has no verifier either, it just fails less visibly.

### What the primary signal can be, when convergence is not observable

The paragraph above says a cap must not be the primary termination condition and does not say what
may be. An independent synthesis outside this vendor closes that gap with concrete detectors, and it
reaches the same rule first: *"Max iterations alone isn't enough; you need loop fingerprinting **and**
cost budgets **and** no-progress detection"* (`research/agent-loop-termination-kinney.md`).

| Detector | Mechanism | What it actually tests |
|---|---|---|
| Repetition fingerprint | Hash each iteration's `(tool_name, result_preview)`; stop after N identical hashes in a row | The loop is cycling rather than progressing |
| No-progress detection | Compare observable state between iterations, not model text | Something in the world changed |
| Cost ceiling | Hard spend cap per run | Bounded blast radius, independent of correctness |
| Wall-clock ceiling | Elapsed-time cap | Catches slow steps that a step count does not |

Two things about this list matter more than the list.

**Every entry tests state or resource consumption, and none tests the model's account of itself.**
That is what separates them from the anti-patterns the same guidance rejects — parsing natural
language for completion, or checking assistant text. A fingerprint over tool results is a fact about
what the loop did; "the agent said it was done" is a fact about what it emitted.

**They are conjunctive, not alternatives.** Each catches a different way a loop fails to end, so
picking one and calling the loop bounded reproduces the original defect at a smaller scale. The
repetition detector misses a loop that varies its calls while accomplishing nothing; no-progress
detection misses a loop that is progressing expensively; a cost ceiling misses a cheap infinite loop.

Scope, because the source does not carry it: these are **design mechanisms, not measured results.**
Every figure on that page is second-hand and two of its most quotable numbers have no disclosed
method — see the verdict. The detectors are worth adopting because their logic is inspectable, not
because anyone measured them.

## Deterministic enforcement versus prompt instruction

The same first-party guidance separates **programmatic enforcement** (hooks, prerequisite gates) from
**prompt-based guidance**, and states that where deterministic compliance is required, prompt
instructions alone carry a non-zero failure rate.

This matters for verifier design specifically. A verifier expressed as an instruction — "always run
the review before committing" — is probabilistic, and its failure mode is indistinguishable from the
`not run` state above: nothing reports, nothing blocks. A verifier expressed as a gate that the
delivery path must physically pass through is deterministic, and when it cannot run it produces a
visible stop rather than a silent omission.

The local evidence is consistent with this: the gate that failed closed was programmatic, and its
unavailability was *loud* — it blocked, and the bypass had to be taken deliberately and documented
three times. A prompt-level verifier would have produced the same three unverified commits with no
artifact at all.

### Three layers, and a fourth state worse than "not run"

Gentle AI's orchestrator guide refines the two-way split into three, for the same toolchain this
repo uses (`research/gentle-orchestrator-anatomy-guide.md`):

| Layer | Decides | Force |
|---|---|---|
| Prompt policy | What should be requested, and how to use the result | Guides the model. Nothing more |
| Runtime permission | Whether the agent has the tool or delegation configured | The runtime enforces it |
| Native code / CLI | Executes the operation and validates its internal invariants | Checks are the binary's, not the text's |

And it states the consequence directly: although the orchestrator prompt uses words like `MANDATORY`
and `hard gate`, **those remain prompt instructions unless another layer implements an equivalent
check**, and must not be described as carrying the force of a runtime denial.

That yields a state worse than any row in the table above — **a gate that was never a gate.** It
reports nothing, blocks nothing, and produces no artifact, because it was only ever a sentence
asserting its own authority. Ranked by how detectable the failure is:

| State | Detectable? |
|---|---|
| Ran, failed | Immediately — it blocks |
| Ran, passed | Yes — evidence exists |
| Could not run | Only if someone notices the absence |
| **Never was a gate** | **Not at all** — and its wording actively suggests the opposite |

The last row is the dangerous one precisely because emphatic language is negatively correlated with
enforcement: a check implemented in code does not need to shout, while a prompt instruction has
nothing but volume available to it. **Capitalised insistence is weak evidence of enforcement, and
mild evidence against it.**

The practical test is not to read the rule but to ask which layer implements it. If the answer is
"the instruction says so", there is no gate — there is a request with confident typography.

### The same conclusion, measured, from outside any vendor

Everything above is normative: two vendors' guidance plus local incidents. An academic result now
supports the load-bearing part of it, and it is worth separating because it is the first **measured**
evidence this file has (`research/llm-as-code-agentic-programming.md`).

arXiv:2606.15874 argues that token explosion, control-flow hallucination and unreliable completion
are **architectural consequences** of assigning the deterministic work of looping, branching and
sequencing to a probabilistic system — not implementation bugs — and states the corollary bluntly:
*"A better prompt or a stronger model cannot guarantee the reliability of the LLM agent."*

That is the three-layer table's conclusion reached independently. The layers say emphatic prompt
wording does not create enforcement; the paper says the class of work being delegated is the problem,
so no improvement within the prompt layer fixes it. Normative and empirical derivations agreeing is
much better evidence than either alone, and neither derivation knew about the other.

Its measurement, on GUI automation over OSWorld: the program-controlled design reached **86.8%
overall success in 15 steps** against leaderboard baselines running up to 100 steps, the best of which
was 80.4%.

**Scope, stated because this number will otherwise be quoted as a law.** One model, one benchmark,
GUI/computer-use tasks. The baselines were **taken from a public leaderboard, not re-run**, so a
single comparison mixes an author-measured figure with cited ones — disclosed by the authors, which
removes the charge of concealment but not the confound. The authors also bound their own claim:
the approach *"does not subsume fully exploratory tasks"* and is effective *"when a workflow has a
known structure."*

What survives every objection is the **step-count gap**, not the success rate. 15 versus up to 100 is
too large for leaderboard noise to explain, and a step budget is bounded by construction rather than
measured. Cite that. Do not cite this as evidence that program-controlled agents beat frameworks in
general — that sentence is wider than the evidence, and the loop-design claim does not need it.

## Scope

One toolchain, one day, three instances. The distinction between `fail` and `not run` is general and
is the transferable part. The specific budget formula is one implementation's choice, cited as an
existence proof that bounded-correction termination is practical — **not** as a recommended
constant.

## What would sharpen it

Instrument the difference: make `not run` as loud as `fail` in the local workflow, and record whether
bypass frequency drops. That converts the claim from an observation into a measurement.
