---
id: decisions/0008-review-lenses-may-use-subagents
type: decision
targets: [any]
status: validated
verified: 2026-08-05
sources: ["journal/2026-08-05-second-gate-bypass-agent-conflict.md", "journal/2026-08-05-first-commit-gate-bypass.md", "research/claude-certified-architect-exam-guide.md"]
---

# 0008 — Review lenses may use sub-agents

## Context

A bounded review selects one or more **lenses** and each lens runs as a sub-agent. An active
session-level directive forbade calling the Agent tool unless the operator requested it
explicitly.

The two rules were individually reasonable and jointly unsatisfiable. The observable result: a
bounded review could be **started but never finished**. `review start` succeeded, froze a target,
selected a lens and opened a correction budget — and then had no permitted way to run the lens,
so no result could be captured, no receipt could be created, and every delivery gate failed
closed. Three commits shipped as documented bypasses on 2026-08-05.

Two properties of the conflict made it worse than an ordinary misconfiguration:

- **It was undiscoverable.** The prohibition's origin was searched for in `AGENTS.md`, project and
  user `settings.json`, the files `gentle-ai` generates, and the `engram` plugin. It was in none of
  them. A rule that cannot be located cannot be reconciled, only obeyed or broken.
- **It was misattributed.** It was initially assumed to be a `gentle-ai` defect awaiting an
  upstream fix. It is not. No release changes it, and there was nothing to file.

Ratified by the operator on 2026-08-05, resolving the open item recorded in
`journal/2026-08-05-second-gate-bypass-agent-conflict.md`.

## Decision

**Review lenses may use sub-agents.** Delegation to a review lens is standing authorization, not a
per-invocation request, and it does not require the operator to ask for it each time.

The reason is not convenience, and it is not deference to the tool's contract. **A lens's value is
context isolation, not its checklist.** A reviewer that shares the implementer's conversation
inherits the reasoning that produced the code, and therefore inherits its blind spots — it has
already been persuaded. Running a lens inline is not a cheaper version of the same check; it is a
materially weaker one that reports the same confidence.

So "just review it inline" was never the fallback it appeared to be. The isolation *is* the
mechanism.

## Consequences

| Consequence | Detail |
|---|---|
| Bounded review can complete | A receipt becomes reachable, and the delivery gates can pass instead of failing closed. |
| Bypasses stop being routine | Three in one day was a signal that the gate was unsatisfiable, not that the work was risky. A bypass returns to meaning something. |
| The verifier becomes real | A gate that cannot run is not a weak gate, it is an absent one that reports as "not run". See `theory/loops/` — this is the failure mode worth writing up. |
| Cost is accepted deliberately | Lenses consume tokens and wall-clock. That is the price of a review that was not convinced in advance. |
| The prohibition still has no located source | It was resolved by operator ratification, not by finding and editing the emitting file. If it reappears, this ADR is the authority to override it. |
| Scope is narrow on purpose | This authorizes sub-agents **for review lenses**. It is not a general grant for all delegation. |

## Alternatives

| Rejected | Reason |
|---|---|
| Run the lens inline in the implementer's conversation | Destroys the context isolation that is the entire point of an adversarial lens, while still reporting a verdict. Worse than no review, because it manufactures confidence. |
| Keep bypassing and document each one | Already tried, three times in one day. The audit trail becomes a list of excuses, and a bypass that is always taken stops carrying information. |
| Declare the review gate formally out of use | Honest, and better than pretending. Rejected because the gate is wanted; the conflict was mechanical, not a judgment that review has no value. |
| Wait for an upstream fix | Rests on a misattribution. The conflict is local. No `gentle-ai` release resolves it. |
