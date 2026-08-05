---
id: decisions/0002-journal-is-raw-material-not-citable
type: decision
targets: [any]
status: validated
verified: 2026-08-04
sources: ["journal/2026-08-04-repo-skeleton-design.md"]
---

# 0002 — journal/ is raw material and is NOT citable

## Context

The repo intentionally records all conversations and brainstorms: it is cheap and valuable.
But without an explicit citability boundary, an AI will later cite a discarded brainstorm as
a settled decision.

## Decision

`journal/` is raw material and is **not citable**. Only `decisions/` and `theory/` are truth.

Refined by ADR 0007, which resolves an ambiguity in the word "citable": `journal/` is not
citable **as authority**, but is citable **as provenance**. The original wording above is
left unedited; the refinement is in 0007.

## Consequences

| Consequence | Detail |
|---|---|
| `journal/` is append-only and unreviewed | No promotion happens by editing a journal entry. |
| Promotion costs a file | Moving anything out of `journal/` requires writing a decision or theory doc. |
| Open question — not resolved here | `engram` already stores session history, so `journal/` risks being a second source of truth. Current working split: **engram = the AI's fast recall**, **`journal/` = the auditable, human-readable, shareable record.** This remains open. |

## Alternatives

| Rejected | Reason |
|---|---|
| Treat `journal/` as citable | A discarded brainstorm gets cited later as a settled decision. |
| Do not record conversations at all | Recording them is cheap and valuable. |
