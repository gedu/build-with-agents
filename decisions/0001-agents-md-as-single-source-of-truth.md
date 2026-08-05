---
id: decisions/0001-agents-md-as-single-source-of-truth
type: decision
targets: [any]
status: validated
verified: 2026-08-05
sources: ["journal/2026-08-04-repo-skeleton-design.md"]
---

# 0001 — AGENTS.md is the single source of truth; skills/ lives at the repo root

## Context

A `CLAUDE.md` at the root couples the repo to one AI tool. The same coupling applies to
skills: anything kept in `.claude/skills/` is owned by one executor.

The pattern was verified against a private repository outside this one, which does exactly
this. That repository is not citable here — it resolves on a single machine, so naming it would
buy no auditability — and the auditable record of the observation is the design conversation in
`journal/2026-08-04-repo-skeleton-design.md`.

## Decision

`AGENTS.md` is the single source of truth, `skills/` lives at the **repo root**, and every
tool-specific entrypoint is a generated symlink that is never committed.

Corollary that generalizes beyond this repo: **knowledge lives outside the executor; the
executor is a thin wrapper.**

## Consequences

| Consequence | Detail |
|---|---|
| Zero drift | Entrypoints are symlinks, not copies. A copy would drift from the source. |
| `./setup.sh` after cloning | Everyone runs it; without it a tool sees no instructions. |
| Nothing tool-specific committed | Generated paths are gitignored under a managed block. |
| Root-level `skills/` | Putting it at the root instead of `.claude/skills/` is the single choice that makes the skills tool-neutral. |

## Alternatives

| Rejected | Reason |
|---|---|
| `CLAUDE.md` as the source of truth | Couples the repo to one AI tool. |
| `skills/` under `.claude/skills/` | Owned by one executor; not tool-neutral. |
| Copying `AGENTS.md` per tool instead of symlinking | Copies drift; symlinks cannot. |
