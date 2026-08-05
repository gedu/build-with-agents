---
id: templates/index
type: index
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---

# templates/

Compositions of `blocks/`, ready to copy into a project as-is.

**Not yet written.** No template exists here.

## Required shape

| Section | Content |
|---------|---------|
| Composes | The blocks used, by `id` — never inlined copies |
| Targets | Stacks the composition applies to; must match frontmatter `targets` |
| Copy procedure | Exact steps to install it in a host project |
| Verification | How to confirm it works after copying |

## Rules

- A template **references** blocks by `id`; it does not duplicate their content. Duplicated
  block content drifts, and the copy always wins by accident.
- If a template composes exactly one block, it is not a template. Ship the block.
- If a block only ever appears inside one template, question whether the block boundary is
  real.
- Minimal single-concern pieces belong in `blocks/`; rationale in `theory/` and `decisions/`.

## Frontmatter contract

```yaml
---
id: templates/<slug>
type: template
targets: [react-native]
status: draft
verified: 2026-08-04
sources: []
---
```

`type: template` is distinct from `type: block` on purpose: a query for validated blocks
must not return compositions. Promotion to `validated` requires having copied the template
into a real project, recorded in `sources`.
