---
id: decisions/0003-blocks-and-templates-are-separate
type: decision
targets: [any]
status: validated
verified: 2026-08-04
sources: ["journal/2026-08-04-repo-skeleton-design.md"]
---

# 0003 — blocks/ and templates/ are separate, with separate `type` values

## Context

A block is a minimal piece with a contract: what it assumes, what it exposes, which targets
it applies to. A template is a composition of blocks, ready to copy.

Without the split, everything becomes a template and nothing gets reused.

## Decision

Keep `blocks/` and `templates/` as separate directories **and** as separate frontmatter
`type` values: `type: block` and `type: template`.

## Consequences

| Consequence | Detail |
|---|---|
| Blocks must state a contract | Assumes / exposes / targets. A piece that cannot state one is not a block yet. |
| The blocks query stays clean | `type: block` + `targets` + `status: validated` returns pieces, not compositions. |
| Two artifacts to maintain per pattern | A block and, when it composes with others, a template referencing it by `id`. |

## Alternatives

| Rejected | Reason |
|---|---|
| One directory for both | Everything becomes a template and nothing gets reused. |
| Templates reuse `type: block` | The query "give me validated blocks for react-native" would return whole compositions, defeating the schema's purpose (see ADR 0004). |
