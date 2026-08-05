---
id: decisions/index
type: index
targets: [any]
status: draft
verified: 2026-08-05
sources: []
---

# decisions/

Numbered ADRs. This is the **WHY** of the repo, and it is citable as truth.

`0001`–`0007` record the decisions that shaped the repo skeleton; `0008` onward record decisions taken while using it. Read them in order before
proposing structural changes. No list of them is kept here — the files are the index, and a
hand-maintained table would go stale (ADR 0004).

## Naming

`NNNN-slug.md`, zero-padded to four digits, monotonically increasing, never renumbered.
Example: `0001-agents-md-as-single-source-of-truth.md`.

## Required sections

| Section | Content |
|---------|---------|
| Context | The forces in play, including the constraint that made this urgent |
| Decision | One sentence, imperative, unambiguous |
| Consequences | What this makes easy, what it makes hard, what it forbids |
| Alternatives | Options rejected, and the specific reason each was rejected |

## Rules

- A superseded ADR is never deleted or edited into agreement. Set `status: rejected`, and
  reference the ADR that replaced it. The history is the value.
- No ADR without a decision. If the question is still open, it is `journal/` material.
- Rationale that only exists in a conversation does not exist. Promote it here.

## Frontmatter contract

```yaml
---
id: decisions/NNNN-<slug>
type: decision
targets: [react, react-native, any]
status: validated
verified: 2026-08-05
sources: []
---
```

A ratified ADR is `status: validated` on the day it is accepted; `sources` may point at the
`journal/` entry or `research/` verdict behind it.
