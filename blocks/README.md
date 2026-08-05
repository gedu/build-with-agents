---
id: blocks/index
type: index
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---

# blocks/

Lego pieces. A block is a **minimal** artifact covering one concern, carrying an explicit
contract, and portable into another project untouched.

**Not yet written.** Every subdirectory is an empty stub.

## Subdirectories

| Path | Scope |
|------|-------|
| `_shared/` | Target-agnostic blocks (`targets: [any]`) |
| `react/` | React-specific blocks |
| `react-native/` | React Native-specific blocks |

Node, Python, Go, Kotlin/KMP and Swift are planned. Do not create their directories until
there is validated content for them.

## Contract — mandatory in every block

| Field | Meaning |
|-------|---------|
| Assumes | What must already be true in the host project |
| Exposes | The surface the host project consumes |
| Targets | Which stacks it applies to; must match frontmatter `targets` |
| Excludes | What this block deliberately does not do |

A block that cannot state its contract is not a block yet. Keep it in `draft`.
A block is minimal and referenced; a template is a composition and copied — see `AGENTS.md`.

## Frontmatter contract

```yaml
---
id: blocks/<area>/<slug>
type: block
targets: [react]
status: draft
verified: 2026-08-04
sources: []
---
```
