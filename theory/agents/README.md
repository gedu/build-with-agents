---
id: theory/agents/index
type: index
targets: [any]
status: draft
verified: 2026-08-05
sources: []
---

# theory/agents/

Single-agent design: tool surface shape, memory and retrieval, context isolation,
instruction precedence, and how an agent's own scaffolding changes its behavior.

Files are not enumerated here; the directory carries the truth and `MAP.md` carries the count.

## Belongs here

- Claims about one agent's design and the consequences observed when it changes.
- Evidence from real runs in this repo or in an analyzed project.

## Does NOT belong here

- Coordination between multiple agents (`theory/orchestration/`).
- Loop and termination design (`theory/loops/`).
- Vendor-specific configuration. Knowledge stays outside the executor.

## Frontmatter contract

```yaml
---
id: theory/agents/<slug>
type: theory
targets: [any]
status: draft
verified: 2026-08-05
sources: []
---
```

Non-empty `sources` is required before `status: validated`. One claim per file.
