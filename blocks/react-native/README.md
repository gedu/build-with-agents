---
id: blocks/react-native/index
type: index
targets: [react-native]
status: draft
verified: 2026-08-04
sources: []
---

# blocks/react-native/

Blocks specific to React Native: `targets: [react-native]`.

**Not yet written.** No block exists here.

## Belongs here

- Artifacts that assume the React Native runtime: native modules, Metro, platform splits,
  device or simulator constraints.

## Does NOT belong here

- Anything that also holds for React on the web — put it in `blocks/_shared/` and declare
  `targets: [react, react-native]`.
- Full app scaffolds or multi-block compositions — those are `templates/`.
- Rationale and evidence — that is `theory/`.

## Frontmatter contract

```yaml
---
id: blocks/react-native/<slug>
type: block
targets: [react-native]
status: draft
verified: 2026-08-04
sources: []
---
```

State the contract (Assumes / Exposes / Targets / Excludes) in the file body, and name the
platforms it was verified on.
