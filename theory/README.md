---
id: theory/index
type: index
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---

# theory/

Verified understanding of how models, agents and orchestration actually behave. Together
with `decisions/`, this is the only place in the repo that can be cited as truth — and
only for files with `status: validated`.

**Not yet written.** Every subdirectory is an empty stub.

## Subdirectories

| Path | Scope |
|------|-------|
| `llm/` | Model behavior: context windows, tokens, sampling, attention limits, failure modes |
| `agents/` | Single-agent design: tool surfaces, memory, context isolation, instruction shape |
| `orchestration/` | Multi-agent coordination: delegation, handoffs, parallelism, cost |
| `loops/` | Iteration shapes: plan/act/verify, review loops, termination and budget |

## Belongs here

- A claim, the evidence for it, and the conditions under which it holds.
- Refuted claims kept as `status: rejected` — the refutation is the value.

## Does NOT belong here

- Anything unverified. If there is no source, it stays `draft` and is not citable.
- Opinions, vibes, or restated vendor marketing.
- Code. Executable artifacts go to `blocks/` and `templates/`.
- Conversations. Those go to `journal/`, which is never citable.

## Frontmatter contract

`type: theory`. `sources` must be non-empty before `status: validated`. `verified` records
the last real check, not the creation date. One claim per file; `id` mirrors the path,
e.g. `theory/agents/subagent-context-isolation`.
