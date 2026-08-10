---
id: sdd/index
type: index
targets: [any]
status: validated
verified: 2026-08-10
sources: ["sdd/measurement-rig/verify.md", "decisions/0011-rig-produces-evidence-not-truth.md"]
---

# sdd/

Spec-Driven Development cycles run in or from this repo. Process records, not truth.

## Recorded cycles

| Cycle | Phases present | Verdict |
|---|---|---|
| `measurement-rig/` | exploration → proposal → spec → design → tasks → verify | **PARTIAL** — verified cost instrument, unverified quality instrument. See `measurement-rig/verify.md`. |

A cycle is recorded here once it has a `verify.md`. A partial verdict is a recorded outcome, not an
unfinished cycle: the verification ran, and it concluded that one channel of the instrument has
never been shown to work. Closing a cycle means stating what it established *and* what it did not.

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
