---
id: journal/2026-08-04-repo-skeleton-design
type: journal
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---

# 2026-08-04 — Design conversation that produced the repo skeleton

Raw material. Not citable as authority; citable as provenance. Produced ADRs 0001–0007.

## 1. Purpose established

Five goals for the repo: capture verified AI/agent practices; hold reusable lego-style
blocks and templates portable to other projects; analyze existing projects against those
practices and find gaps; test `gentle-ai` / `engram` / `gga` and file upstream bugs; record
reasoning, decisions and SDD cycles.

## 2. Rejected: a `CLAUDE.md`-rooted design

The initial design put a `CLAUDE.md` at the root. Eduardo corrected it: that couples the
repo to one AI tool. He pointed at `/Users/eduardo.graciano/Documents/mine/prowler`, which
already does the tool-neutral thing.

Adopted instead: `AGENTS.md` as the single source of truth, `skills/` at the repo root
rather than `.claude/skills/`, and tool-specific entrypoints as generated symlinks that are
never committed — symlinks rather than copies, because copies drift. Generalized corollary:
knowledge lives outside the executor; the executor is a thin wrapper. → ADR 0001

## 3. Two failures observed in prowler

- Hand-maintained skill tables went stale. → rule: every table is generated or does not exist.
- Its own `skill-creator` template omitted `metadata.scope` and `metadata.auto_invoke`, the
  very fields its generator depends on, so skills written from that template were silently
  skipped. → rule: a schema and its documentation are one artifact.

Both fed ADR 0004.

## 4. Directory layout and citability

Layout agreed: `skills/`, `theory/{llm,agents,orchestration,loops}/`, `research/`,
`decisions/`, `journal/`, `blocks/{_shared,react,react-native}/`, `templates/`, `sdd/`,
`upstream/`, plus `AGENTS.md`, `MAP.md`, `setup.sh`, `.gitignore`.

`journal/` records all conversations and brainstorms — cheap and valuable — but without an
explicit citability boundary an AI would later cite a discarded brainstorm as a settled
decision. Only `decisions/` and `theory/` are truth. → ADR 0002

Open question, not resolved: `engram` already stores session history, so `journal/` risks
being a second source of truth. Working split — engram is the AI's fast recall, `journal/`
is the auditable, human-readable, shareable record.

## 5. blocks/ vs templates/

A block is a minimal piece with a contract (assumes / exposes / targets); a template is a
composition of blocks ready to copy. Without the split, everything becomes a template and
nothing gets reused. → ADR 0003

## 6. Frontmatter as a query interface

Fields: `id`, `type`, `targets`, `status`, `verified`, `sources`. The point is not tidiness:
an AI must answer "give me validated blocks for react-native" in one query instead of
reading the whole repo, since good folders with no metadata still force blind grep. → ADR 0004

## 7. Rejected: SDD for the skeleton

Using SDD to build the skeleton was considered and rejected for three reasons: the spec was
already settled in conversation, so proposal/spec/design/tasks for four files is ceremony
rather than engineering; SDD pays when requirements are uncertain and none were; and it is
circular, because `sdd/` is itself part of the skeleton, so SDD had nowhere to write its
artifacts. Applying SDD to everything devalues it. Criterion adopted: use SDD when
requirements are genuinely uncertain. First real cycle reserved for the project-evaluator.
→ ADR 0005

## 8. Rejected: starting with all five techs at once

Starting with five techs at once dilutes. Starting with Go or Python was also rejected:
with little experience in them it is impossible to tell "the repo is badly designed" from
"I don't understand the tech". Adopted: validate the structure with React and React Native,
techs already commanded, then use Go or Python as the first real learn-from-zero case, which
is where the repo proves its actual value. Later order: Node, Python, Go, then
Android/Kotlin + Kotlin Multiplatform, then iOS/Swift.

Two corrections recorded in the same discussion: "backend" is a domain, not a tech — it
overlaps the Node/Python/Go already listed, so it belongs in `theory/backend/` plus a
concrete target, never as a `blocks/` directory. Kotlin Multiplatform is one target covering
Android and iOS, not two. → ADR 0006

## 9. Implementation, same day

The skeleton was written: `AGENTS.md`, `MAP.md`, `setup.sh`, `.gitignore`, and README index
stubs. Knowledge directories were left as stubs with `status: draft` and explicit
"Not yet written" notes, on the constraint that inventing plausible technical content would
poison a repo whose purpose is verified knowledge.

Three additions to the specified `type` enum were needed and made: `index` for directory
READMEs, `skill` for `skills/*/SKILL.md`, and `template` split out of `block` so that a
query for validated blocks does not return whole compositions. The last one fed ADR 0003.

A risk review of `setup.sh` confirmed its clobber-avoidance but found three defects, all
fixed: an unguarded `mkdir -p` that aborted the whole script under `set -euo pipefail` when
a path component was a regular file or dangling symlink; no validation of the intermediate
directory, so a symlinked `.claude` would have planted links outside the repo boundary; and
unanchored `.gitignore` basenames that would silently untrack any committed file named
`CLAUDE.md` or `GEMINI.md` at any depth.

## 10. Schema conflict found while writing the ADRs

`AGENTS.md` required non-empty `sources` for `status: validated`, but four of the six ADRs
were ratified in conversation with no citable artifact behind them, and ADR 0002 declared
`journal/` not citable — so the ADRs could not cite their own origin. The conflict was
reported rather than patched.

Resolved by splitting citability instead of weakening the rule: `journal/` is not citable as
authority but is citable as provenance. Citing a law versus citing a witness. A decision with
no traceable origin is an opinion with a serial number, so the non-empty `sources`
requirement stands. → ADR 0007
