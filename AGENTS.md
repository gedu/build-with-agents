---
id: agents/root
type: index
targets: [any]
status: validated
verified: 2026-08-04
sources: ["decisions/0001-agents-md-as-single-source-of-truth.md", "decisions/0004-mandatory-frontmatter-as-query-interface.md", "journal/2026-08-04-repo-skeleton-design.md"]
---

# AGENTS.md — root instructions

Single source of truth for every AI executor working in this repo. Tool-specific
entrypoints (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.claude/skills`, …)
are **generated symlinks** produced by `./setup.sh`. Never commit them, never edit them.

Start at `MAP.md`. It is the index of what exists, where it lives, and whether it is truth.

## Purpose

A laboratory for AI/agent practices:

| # | Goal |
|---|------|
| a | Capture **verified** AI/agent practices |
| b | Hold reusable lego-style `blocks/` + `templates/` portable to other projects |
| c | Analyze existing projects against those practices and find gaps |
| d | Test `gentle-ai` / `engram` / `gga` and stage upstream bug reports |
| e | Record reasoning, decisions and SDD cycles |

Scope today: **React** and **React Native** only. See `MAP.md` for planned targets.

## Non-negotiable rules

| Rule | Detail |
|------|--------|
| Language | All artifacts in **English**: headings, prose, comments, identifiers, filenames. |
| Precedence | A nested `AGENTS.md` overrides this root file wherever guidance conflicts. Closest file to the edited path wins. |
| Tool-neutral | Knowledge lives outside the executor. `skills/` sits at the **repo root**, never in `.claude/skills/`. The executor is a thin wrapper. |
| Nothing tool-specific committed | Run `./setup.sh --<tool>` after cloning. Generated paths are gitignored under a managed block. |
| No invented knowledge | Do not write a practice you have not verified. Unverified content stays `status: draft` with sources empty and an explicit "Not yet written" note. |
| Tables are generated or absent | Never hand-maintain a table that duplicates data already living in frontmatter. Stale hand-written indexes are worse than no index. |
| Schema = doc | If a schema is documented, the doc and the schema are one artifact. Changing the fields tooling reads means changing this file in the same commit. |

## Citability

| Directory | Citable as truth? | Why |
|-----------|-------------------|-----|
| `decisions/` | **Yes** | Ratified ADRs. The WHY. |
| `theory/` | **Yes**, when `status: validated` | Verified practice backed by `sources`. |
| `blocks/`, `templates/` | Yes, when `status: validated` | Executable artifacts with a contract. |
| `research/` | Only as **evidence**, never as conclusion | A link plus a contrast plus a verdict. Cite the verdict, not the link. |
| `journal/` | **Never as authority**, always valid as **provenance** | Raw material. See the split below. |
| `sdd/`, `upstream/` | No | Process records and experiments. |

`journal/` is **not citable as authority**: nothing may justify a decision on the grounds
that a journal entry says so. Only `decisions/` and `theory/` carry authority. Rationale,
stated explicitly so nobody relaxes it later: a brainstorm contains discarded options that
sounded good at the time, and if journal entries carried authority a rejected idea would
eventually be quoted as a settled decision.

`journal/` **is citable as provenance**: it is valid evidence of *where* a decision came
from, and belongs in the `sources` of a doc that supersedes it.

The distinction is between citing a law and citing a witness. See ADR 0007.

## Frontmatter contract

Every content file starts with this block. No exceptions, including `README.md` index files.

```yaml
---
id: agents/subagent-context-isolation   # path-like, stable, unique; never renamed once referenced
type: theory | block | template | decision | research | journal | skill | index
targets: [react, react-native, any]     # list; `any` = target-agnostic
status: draft | validated | rejected
verified: 2026-08-04                    # ISO date of last verification
sources: []                             # URLs or repo-relative file paths backing this
---
```

| Field | Rules |
|-------|-------|
| `id` | Path-like and stable. Mirrors location but does not have to equal it. Renaming breaks references — don't. |
| `type` | `index` covers navigational entrypoints: `README.md` files that describe a directory, plus this file and `MAP.md`; `skill` for `skills/*/SKILL.md`; `template` for `templates/` compositions. `block` and `template` stay distinct so a query for blocks does not return compositions. |
| `targets` | Always a list. `[any]` when the content does not depend on the stack. |
| `status` | `draft` = unverified, not citable. `validated` = verified, has sources. `rejected` = kept as a warning, never deleted silently. |
| `verified` | ISO date of the last time a human or agent actually checked the claim. Not the creation date. |
| `sources` | Required non-empty for `status: validated`. Empty list is allowed only for `draft`. |

Why this schema exists: an agent must be able to answer *"give me the validated blocks
for react-native"* with one structured query over frontmatter, instead of reading the
whole repo. Every field above exists to serve that query. Do not add fields tooling
does not read.

## blocks/ vs templates/

| | `blocks/` | `templates/` |
|---|-----------|--------------|
| Size | Minimal, one concern | Composition of blocks |
| Has a contract | **Required**: assumptions, exposed surface, applicable `targets` | Inherited from its blocks |
| Use | Referenced and combined | Copied into a project as-is |

Keep the split. Without it every block grows into a template, nothing composes, and
nothing gets reused. A block that cannot state its contract is not a block yet.

## Working agreements

1. Read `MAP.md` before searching the filesystem.
2. New content starts as `status: draft`. Promotion to `validated` requires sources.
3. Record the conversation in `journal/` **first**, then record the WHY in `decisions/` as a
   numbered ADR (`NNNN-slug.md`) citing that entry as provenance. A `validated` ADR needs
   non-empty `sources`, so the journal entry is a prerequisite, not an afterthought.
4. One concern per file. Long prose is a smell — prefer tables.
5. Never delete a `rejected` artifact. The refutation is the value.
