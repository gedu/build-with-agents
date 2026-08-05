---
id: theory/llm/index
type: index
targets: [any]
status: draft
verified: 2026-08-05
sources: []
---

# theory/llm/

How language models behave as a substrate: context windows, tokenization, sampling,
prompt sensitivity, degradation at length, and observable failure modes.

Files are not enumerated here; the directory carries the truth and `MAP.md` carries the count.

## Belongs here

- Measurable model behavior, with the measurement or the citation attached.
- Version- or vendor-bound behavior, explicitly labelled as such in the file body.

## Does NOT belong here

- Agent architecture (`theory/agents/`) or coordination (`theory/orchestration/`).
- Benchmark screenshots without a reproducible source.
- Anything you have not verified. Draft it, mark it, leave it uncited.

## Frontmatter contract

```yaml
---
id: theory/llm/<slug>
type: theory
targets: [any]
status: draft
verified: 2026-08-05
sources: []
---
```

`targets` is almost always `[any]` here — model behavior rarely depends on the app stack.
Non-empty `sources` is required before `status: validated`.
