---
id: sdd/index
type: index
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---

# sdd/

Spec-Driven Development cycles run in or from this repo. Process records, not truth.

No cycle recorded yet.

## Layout

`sdd/<change-slug>/` holding the artifacts of one cycle:

| File | Phase |
|------|-------|
| `proposal.md` | Intent, scope, approach |
| `spec.md` | Requirements and scenarios |
| `design.md` | Technical design and chosen approach |
| `tasks.md` | Ordered implementation checklist |
| `verify.md` | Validation of implementation against spec and design |

One directory per change. Completed cycles keep their artifacts in place.

## Citability

Not citable as truth. An SDD artifact records what was planned and verified for one change.
A conclusion worth reusing gets promoted to `theory/` or ratified in `decisions/`.

## Does NOT belong here

- Reusable practice — that is `theory/`, `blocks/`, `templates/`.
- Brainstorms preceding the proposal — those are `journal/`.

## Frontmatter contract

Use the repo schema with the phase's own type: `type: decision` for design records that
settle a question, otherwise `type: journal` for process narrative. Keep `status: draft`
until the cycle is verified.
