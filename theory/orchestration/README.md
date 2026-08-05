---
id: theory/orchestration/index
type: index
targets: [any]
status: draft
verified: 2026-08-05
sources: []
---

# theory/orchestration/

Multi-agent coordination: when delegation pays for itself, handoff formats, parallelism,
context inflation, and the cost/quality tradeoffs of splitting work.

Files are not enumerated here; the directory carries the truth and `MAP.md` carries the count.

## Belongs here

- Claims about coordination between two or more agents, with observed outcomes.
- Cost or latency measurements that back a delegation rule.

## Does NOT belong here

- Single-agent design (`theory/agents/`).
- Loop shape and termination (`theory/loops/`).
- Orchestrator prompts as artifacts — those are `blocks/` or `templates/`.

## Frontmatter contract

```yaml
---
id: theory/orchestration/<slug>
type: theory
targets: [any]
status: draft
verified: 2026-08-05
sources: []
---
```

Non-empty `sources` is required before `status: validated`. One claim per file.
