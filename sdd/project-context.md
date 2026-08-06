---
id: sdd/project-context
type: journal
targets: [any]
status: draft
verified: 2026-08-06
sources: ["AGENTS.md", "MAP.md", "journal/2026-08-05-redaction-gate-and-2478-on-224.md", "decisions/0005-sdd-is-not-applied-to-everything.md"]
---

# SDD Project Context — build-with-agents

First SDD init cycle for this repo. `sdd/` was empty before this.

## What this project is

A public knowledge-base repository laboratory for AI/agent engineering practice — not an
application. No app source tree, no package-manager manifest. Content is `theory/`,
`research/`, `decisions/` (ADRs), `journal/`, `skills/` (tool-neutral `SKILL.md` files),
`blocks/` and `templates/` (currently empty), plus `hooks/` (one committed pre-commit hook)
and `setup.sh`. Start at `MAP.md`; `AGENTS.md` is the single source of truth for rules.

## Real stack

- Bash: `hooks/pre-commit`, `setup.sh`. Both pass `bash -n`.
- Markdown: everything else (62 files at last count) — theory, research, decisions, journal,
  skill definitions, README indexes.
- No other language present. No Node/Python/Go/Rust manifest anywhere in the tree.

## Persistence mode

`hybrid`, per session preflight: artifacts live both under `sdd/` in the repo (this repo's own
layout, described in `sdd/README.md` — not an `openspec/` tree, since this project is not using
that convention) and as Engram topic keys under project `build-with-agents`.

- Execution mode: `interactive`
- Chained PR strategy: `ask-always`
- Review budget: 400 changed lines (authored additions + deletions)

## Conventions later SDD phases must obey

1. **Frontmatter contract** (`AGENTS.md`): every content file starts with
   `id / type / targets / status / verified / sources`. `type` enum is
   `theory | block | template | decision | research | journal | skill | index` — no `config`
   or other invented type. New SDD artifacts here use `type: journal` (process narrative) or
   `type: decision` (a design record that settles something), per `sdd/README.md`.
2. **Redaction** (`AGENTS.md` §Redaction): this repo is public. Never write an absolute
   home-directory path, a private project/client name, a token, or a hostname into any
   committed file. Refer to this repository's root as `<repo>`. The repo root's actual
   absolute path is deliberately not recorded in this file or anywhere else committed.
3. **Citability** (`MAP.md`): `decisions/` and `theory/` (when `validated`) carry authority.
   `research/` is evidence via its verdict only. `journal/` is provenance, never authority.
   `sdd/` itself is a process record, not citable as truth.
4. **Tables are generated or absent** — never hand-maintain a table duplicating frontmatter
   data.
5. **Testing** — see `sdd/testing-capabilities.md`. No test runner exists; do not schedule one.

## Enforced verification that exists today

- `./hooks/pre-commit` — staged-diff redaction gate (exit 0/1/2 contract).
- `./hooks/pre-commit --all` — whole-tree redaction audit.
- `bash -n` — shell syntax check for `hooks/pre-commit` and `setup.sh`.

No other automated gate is committed.

## Skills available to this repo

Two project-level skills, both real (not registry placeholders):

| Skill | Status | Path |
| --- | --- | --- |
| `context-checkpoint` | draft — design rationale strengthened but not yet run end-to-end enough times to promote | `skills/context-checkpoint/SKILL.md` |
| `source-verdict` | validated | `skills/source-verdict/SKILL.md` |

Plus globally available skills resolved through the standard scan paths (opencode, Claude,
Copilot skill directories). Full index: `.atl/skill-registry.md` (gitignored, machine-local —
regenerate per machine with `gentle-ai skill-registry refresh --force`; not re-created by this
init since it already exists and is current as of today).

## Governing decision on when to use SDD at all

`decisions/0005-sdd-is-not-applied-to-everything.md` (validated): SDD applies only when
requirements are genuinely uncertain — not ceremony for already-settled work. It explicitly
reserves "the project-evaluator" as this repo's first real SDD cycle, where the uncertain
requirements actually live. A later `sdd-explore`/`sdd-new` invocation should pick a target with
real uncertainty rather than retrofitting SDD onto already-decided work (e.g. an ADR, a journal
entry, or a one-line fix).

## Open items carried into this cycle

- `journal/2026-08-05-redaction-gate-and-2478-on-224.md` §7 lists unresolved items (no test for
  `hooks/pre-commit`, an `all_tracked_lines` fail-open, an abandoned review lineage). These are
  pre-existing and out of scope for SDD init; noted here so a later `sdd-explore`/`sdd-new`
  cycle can pick one up deliberately rather than rediscovering it.
