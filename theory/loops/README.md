---
id: theory/loops/index
type: index
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---

# theory/loops/

Iteration shapes: plan/act/verify cycles, review and correction loops, budgets,
convergence, and termination conditions that prevent infinite or wasteful loops.

**Not yet written.** No verified claim has been recorded here.

## Belongs here

- Claims about loop structure and what changed when the structure changed.
- Termination and budget rules with the evidence that motivated them.

## Does NOT belong here

- Who runs the loop — that is `theory/orchestration/`.
- A concrete reusable loop implementation — that is `blocks/` or `templates/`.
- SDD cycle records — those live in `sdd/`.

## Frontmatter contract

```yaml
---
id: theory/loops/<slug>
type: theory
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---
```

Non-empty `sources` is required before `status: validated`. One claim per file.
