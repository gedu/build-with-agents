---
id: blocks/_shared/index
type: index
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---

# blocks/_shared/

Blocks that do not depend on the host stack: `targets: [any]`.

**Not yet written.** No block exists here.

## Belongs here

- Artifacts that work regardless of framework: instruction fragments, review checklists,
  commit and PR conventions, agent prompt units, tool-neutral configuration shapes.

## Does NOT belong here

- Anything importing or assuming React or React Native — use `blocks/react/` or
  `blocks/react-native/`.
- Anything that only makes sense once composed with other blocks — that is `templates/`.
- Explanations of why the block works — that is `theory/`.

## Frontmatter contract

```yaml
---
id: blocks/_shared/<slug>
type: block
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---
```

State the contract (Assumes / Exposes / Targets / Excludes) in the file body. Promotion to
`status: validated` requires having used the block in at least one real project, recorded
in `sources`.
