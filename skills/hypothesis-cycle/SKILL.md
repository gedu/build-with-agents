---
id: skills/hypothesis-cycle
type: skill
targets: [any]
status: draft
verified: 2026-08-07
sources: ["decisions/0012-a-hypothesis-is-never-citable.md", "decisions/0008-review-lenses-may-use-subagents.md", "theory/loops/verifier-availability.md", "theory/loops/reading-and-running-find-different-defects.md", "theory/orchestration/delegation-and-context-boundaries.md", "skills/source-verdict/SKILL.md", "research/claude-certified-architect-exam-guide.md"]
---

# hypothesis-cycle

Take a hypothesis from "someone said it out loud" to a verdict that `theory/` can hold, without spending
more than it is worth and without the loop running forever.

**`status: draft`.** Its promotion criterion is end-to-end runs, not better citations — the same rule
`skills/context-checkpoint` is held to. Promoting a method before using it is the failure ADR 0012
forbids for hypotheses, applied to skills.

## Step 0 — Classify the claim's logical form. Nothing else works until you do

**A claim's form determines what can refute it.** Skipping this is why hypothesis work goes in circles:
people argue about evidence while disagreeing about what evidence would even count.

| Form | Example | One real counterexample | One real supporting example |
|---|---|---|---|
| **Universal** — "always", "every", "never" | "A broad surface *always* costs more tokens" | **Refutes it. Done.** Modus tollens | Proves nothing. There could be a thousand exceptions |
| **Existential** — "there is a case where" | "There is a task where scoping changes the answer" | Proves nothing | **Supports it. Done** |
| **Statistical** — "on average", "more often", "degrades" | "A broad surface degrades output quality" | **Refutes nothing.** It is one draw from a distribution | Proves nothing, for the same reason |

Two consequences worth internalising:

**A universal claim is cheap to kill and impossible to confirm.** Surviving N attempts is not proof — it
is a survival count, and a `supported` verdict on a universal claim must state **how many attempts it
survived**, never that it "held". This is why `research/` verdicts carry their scope: the same asymmetry.

**A statistical claim cannot be settled by examples at all.** No counterexample refutes it and no example
supports it. It needs N and spread, and if the operator says "I found a case where it did not happen",
the correct answer is *"that is one draw, and the claim never said always"* — not a retraction.

**A hypothesis whose form is not declared has no test**, and therefore does not belong in `hypotheses/`.
Send it back before spending anything.

## Step 1 — Absurdity screen. Four cheap checks, in order

Run before any delegation. Each one kills the hypothesis outright, and they are ordered by cost.

| # | Check | Kill condition |
|---|---|---|
| 1 | **Falsifiable?** | No observation could contradict it → it is a position, not a claim (`source-verdict` test 1) |
| 2 | **Tautological?** | It is true by the definitions of its own terms — "runs with more tools have more tools" |
| 3 | **Already settled?** | Something already measured in this repo contradicts or trivially implies it. Search before delegating |
| 4 | **Detectable at the available N?** | The effect it claims is smaller than what the affordable sample could distinguish from noise |

**Check 4 is the one nobody runs and it wastes the most.** A claim about a 2% difference tested at N=5
is theatre: the run cannot come back with an answer either way, and it will come back with a number
anyway. Ask *before* spending: **what is the smallest effect this design could distinguish from noise,
and is the claimed effect bigger than that?** If not, the honest verdict is **"not testable at this
budget"**, which is a real result and costs nothing.

## Step 2 — Try to kill it first, and only if that is cheap

For **universal** claims only: one real counterexample ends the cycle. Look for it before spending on
support. This is the highest-value-per-token step that exists and it is skipped constantly, because
looking for support feels like progress.

**The counterexample must be real and measured.** A conceivable counterexample refutes nothing —
"a model *could* behave differently" is not an observation. If it is not a number you produced or an
artifact you read, it does not count.

For **statistical** claims, skip this step. There is nothing a single case can do.

## Step 3 — Delegate, adversarially, with the bias named

Delegate the investigation. Two rules that are not optional:

**At least one agent is tasked to refute, not to investigate.** An agent asked to "investigate whether X"
returns support for X far more readily than one asked to "find the case that breaks X". This is the
`review-refuter` shape and ADR 0008's reasoning: the value of a fresh instance is that it has not been
persuaded, and a neutral-sounding prompt gives that away for free.

**Give it the artifacts, not your reasoning.** Per `theory/orchestration/delegation-and-context-boundaries.md`,
a delegation is only as good as its mission, and a mission that includes why you believe the hypothesis
has already lost the independence it was for.

Use the repo's own instruments where they apply — `rig/run.sh` for anything about agent behaviour under
a varied harness. A hypothesis testable by the rig should be tested by the rig, not argued about.

## Step 4 — Double-check against artifacts, never against your expectation

The report comes back. **It is a claim, not evidence** — the rule this repo has re-learned in every
register (`theory/orchestration/delegation-and-context-boundaries.md`).

Verify: the files it names exist and say what it says; the commands it ran produce that output when you
run them; the numbers appear in the artifacts rather than only in the prose.

**The trap specific to this step:** you proposed the hypothesis, so you are checking work against your
own prior. Check it against the artifact — and note that a report *agreeing* with you deserves the same
scrutiny as one disagreeing. It will not feel like it does.

Confirm what produced the result was what you meant to test. A fixture that silently reverted the code
under test and reported every fix as failed is a recorded incident here, not a hypothetical
(`theory/loops/reading-and-running-find-different-defects.md`).

## Step 5 — Corner cases, then one more round if and only if they changed something

Ask what input nobody chose for it: empty, hostile, non-ASCII, binary, concurrent, interrupted. This is
where the fifth and sixth real defects in this repo came from, after four reasoning passes found none.

**Then the termination rule, and it is not a counter.**

> **Stop when a round produces no observation that changes the verdict.**

Not "stop after 3 rounds". Anthropic's guidance lists *"setting arbitrary iteration caps as the primary
stopping mechanism"* as an anti-pattern, and `theory/loops/verifier-availability.md` records the
correction: a cap is a **backstop**, never the signal.

The signal here is **no new information**: a round that surfaces nothing which could move the verdict
means the cycle has converged, whether the verdict is supported, refuted or not-testable.

| Backstop | Value | What it means when hit |
|---|---|---|
| Rounds | 3 | Not convergence. Stop and record what remains unresolved |
| Budget | Declared before round 1 | Same. An exhausted budget is an outcome, not a failure |

An exhausted backstop is **never** a verdict. "We ran out" resolves to **open**, and the hypothesis
stays open with what was learned recorded.

## Step 6 — Write the verdict where it belongs

| Verdict | Where it goes |
|---|---|
| Refuted | The hypothesis file stays, `status: rejected`, with the counterexample or the distribution. **Never deleted** — the refutation is the value |
| Supported | A **new** `theory/` file, on the evidence, with scope and spread. The hypothesis file records where it resolved. Per ADR 0012 the theory file cites the **measurement**, never the prediction |
| Not testable at this budget | Stays open, with the reason and the N that would settle it. A real outcome |
| Both / narrowed | The `theory/` file it targeted gains a second mechanism or a narrower claim, and says which |

**Nothing cites the hypothesis file itself.** Zero citability, ADR 0012. You may point at it to say what
is being tested; never to say why something is true.

## The failure modes this cycle exists to prevent

| Failure | Where it is caught |
|---|---|
| Arguing about evidence while disagreeing what would count | Step 0 |
| Spending a real budget on something no sample could resolve | Step 1, check 4 |
| Looking for support when one counterexample would have ended it | Step 2 |
| A delegate that returns the answer its prompt implied | Step 3 |
| Believing a report because it agrees with you | Step 4 |
| A loop that runs until someone gets bored | Step 5 |
| A prediction becoming evidence for itself | Step 6 and ADR 0012 |
