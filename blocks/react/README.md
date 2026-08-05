---
id: blocks/react/index
type: index
targets: [react]
status: draft
verified: 2026-08-04
sources: []
---

# blocks/react/

Blocks specific to React on the web: `targets: [react]`.

**Not yet written.** No block exists here.

## Belongs here

- Artifacts that assume React and a web runtime (DOM, bundler, browser APIs).

## Does NOT belong here

- Anything that also holds for React Native — put it in `blocks/_shared/` and declare
  `targets: [react, react-native]` instead of duplicating it.
- Full app scaffolds or multi-block compositions — those are `templates/`.
- Rationale and evidence — that is `theory/`.

## Frontmatter contract

```yaml
---
id: blocks/react/<slug>
type: block
targets: [react]
status: draft
verified: 2026-08-04
sources: []
---
```

State the contract (Assumes / Exposes / Targets / Excludes) in the file body. Duplicating a
block across `react/` and `react-native/` is a smell: move it to `_shared/` with both
targets listed.
