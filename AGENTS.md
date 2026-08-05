---
id: agents/root
type: index
targets: [any]
status: validated
verified: 2026-08-05
sources: ["decisions/0001-agents-md-as-single-source-of-truth.md", "decisions/0004-mandatory-frontmatter-as-query-interface.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "journal/2026-08-04-repo-skeleton-design.md"]
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
| Redaction | This repo is **public**. No committed file may contain a home-directory path, a private project or client name, a token, or a hostname — in prose, in frontmatter, or in a commit message. See below. |

## Redaction

Every committed file is published the moment it is pushed, and pushing is not reversible in any
way that matters. Applies repo-wide, to every directory and every `status`. ADR 0009 carries the
reasoning.

Half of this is enforced. `hooks/pre-commit` blocks a commit containing an absolute home path or a
known secret shape — install it with `./setup.sh --hooks`, audit the whole tree with
`./hooks/pre-commit --all`. The other half, a private name written as a bare word, **cannot** be
pattern-matched and stays a judgment call. A clean check is not evidence about that half.

| Never commit | Write instead |
|---|---|
| `/Users/<name>/…`, `/home/<name>/…`, `C:\Users\<name>\…` | `<repo>` for this repository root, `~` or `<home>` for a home directory |
| The name of a private repository, project or client | A description of its role. Do not name it |
| Tokens, credentials, API keys, session identifiers | Nothing. There is no safe abbreviation |
| Hostnames, machine names, internal URLs a reader cannot resolve | Omit, or describe the class of host |
| A machine-local path cited as evidence | A repo-relative path, a URL, or a `journal/` entry recording what was observed |

Two rules that are not obvious and both cost something already:

- **A citation must resolve for a reader who has only this repo.** A path that works on one machine
  is decorative, and `decisions/` is citable as truth unconditionally.
- **Never paste a real value in order to describe how to find it.** Redaction patterns, search
  commands and incident write-ups describe the *shape* of a forbidden string and never contain an
  instance of it. A file explaining a redaction is the likeliest place in the repo to reintroduce
  what it redacts.

Not covered: a bare first name. Authorship is already public through the remote and the commit
trailer. This rule targets machine paths, private names and secrets.

### Shared material — ask before writing, then remember the answer

A path does not say whether what it points at is public. A directory under a home directory may be
a clone of a public repository, a client's private code, or a scratch copy — and the three have
different handling with identical-looking paths. **An agent cannot classify it by looking.**

So when the operator shares a repository, document or path from outside this project:

1. **Ask how to refer to it, before writing it anywhere** — before a doc, an ADR, a journal entry, a
   commit message or a `sources` field. Asking is not optional and does not wait for a draft.
2. **Never write the full path**, whatever the answer is.
3. Once the answer is known, use it in this form:

| Where it lives | How to refer to it |
|---|---|
| Outside this project, and the operator confirmed the name is public | The repository or document name alone. No path |
| Outside this project, and the name is private or unconfirmed | Its role, described. No name, no path |
| Inside this project | A project-relative path |

4. **Record the answer** so it is not asked twice and so later documents stay consistent with the
   earlier ones. A classification given once governs every subsequent mention.

Why asking is the rule rather than defaulting to redaction: a blanket "never name it" throws away
citable evidence when the source is public, and a public source that cannot be named cannot be
checked by a reader. Redaction and citability pull in opposite directions here, and only the
operator knows which applies.

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
