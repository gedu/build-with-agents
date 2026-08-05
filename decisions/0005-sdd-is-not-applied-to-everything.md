---
id: decisions/0005-sdd-is-not-applied-to-everything
type: decision
targets: [any]
status: validated
verified: 2026-08-04
sources: ["journal/2026-08-04-repo-skeleton-design.md"]
---

# 0005 — SDD is not applied to everything

## Context

This skeleton was built **without** SDD, deliberately, for three reasons:

| Reason | Detail |
|---|---|
| The spec was already settled | It was settled in conversation. Writing proposal/spec/design/tasks for four files is ceremony, not engineering. |
| No uncertainty to resolve | SDD pays when requirements are uncertain; here none were. |
| It is circular | `sdd/` is itself part of the skeleton, so SDD had nowhere to write its artifacts. |

Applying SDD to everything devalues it.

## Decision

Use SDD when requirements are genuinely uncertain.

## Consequences

| Consequence | Detail |
|---|---|
| SDD keeps its signal | A cycle in `sdd/` means the requirements were actually unclear. |
| The first real cycle is reserved | The project-evaluator, where the uncertain requirements are. |
| The skeleton has no SDD trail | Its rationale lives here in `decisions/` instead. |

## Alternatives

| Rejected | Reason |
|---|---|
| Apply SDD to everything, including this skeleton | Ceremony for four already-specified files; nothing uncertain to resolve; circular, since `sdd/` did not exist yet. Applying it everywhere devalues it. |
