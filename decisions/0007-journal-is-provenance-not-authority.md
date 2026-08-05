---
id: decisions/0007-journal-is-provenance-not-authority
type: decision
targets: [any]
status: validated
verified: 2026-08-04
sources: ["journal/2026-08-04-repo-skeleton-design.md"]
---

# 0007 — journal/ is citable as provenance, not as authority

## Context

`AGENTS.md` requires non-empty `sources` for `status: validated`. ADR 0002 declared
`journal/` not citable. Four of ADRs 0001–0006 were ratified in conversation with no citable
artifact behind them, so they could not record their own origin without violating one rule or
the other.

ADR 0002's statement that `journal/` is "not citable" was ambiguous, and that ambiguity is
what produced the conflict.

## Decision

Split citability: `journal/` is **not citable as authority** — nothing may justify a decision
on the grounds that a journal entry says so, and only `decisions/` and `theory/` carry
authority — but `journal/` **is citable as provenance**, valid evidence of *where* a decision
came from, belonging in the `sources` of a doc that supersedes it.

The distinction is between citing a law and citing a witness.

The non-empty `sources` requirement for `status: validated` is **not** weakened.

## Consequences

| Consequence | Detail |
|---|---|
| A conversation-ratified ADR can satisfy the schema | It cites the journal entry recording the conversation, without any rule being relaxed. This is the whole point of the split. |
| ADR 0002's intent is preserved | A discarded brainstorm can never become a settled decision, because provenance carries no authority. |
| `sources` stays load-bearing | A decision with no traceable origin is an opinion with a serial number. |
| Ratifying a decision now has a prerequisite | The conversation must be recorded in `journal/` before the ADR can cite it. |
| Two places state the split | `AGENTS.md` and `journal/README.md`. Both must change together. |

## Alternatives

| Rejected | Reason |
|---|---|
| Weaken the non-empty `sources` rule for `validated`, or exempt `type: decision` | That rule is load-bearing; a decision with no traceable origin is an opinion with a serial number. |
| Leave `journal/` flatly non-citable and accept ADRs with empty `sources` | Satisfies neither rule; the ADRs would still contradict the schema. |
