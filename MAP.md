---
id: map
type: index
targets: [any]
status: validated
verified: 2026-08-05
sources: ["decisions/0001-agents-md-as-single-source-of-truth.md", "decisions/0004-mandatory-frontmatter-as-query-interface.md", "journal/2026-08-04-repo-skeleton-design.md"]
---

# MAP.md — start here

This repo is a laboratory for AI/agent practices. It captures **verified** practices about
LLMs, agents and orchestration; holds reusable lego-style `blocks/` and copy-ready
`templates/` portable to other projects; provides the baseline to analyze an existing
project against those practices and find gaps; hosts experiments against `gentle-ai`,
`engram` and `gga` plus staged upstream bug reports; and records the reasoning, the
decisions and the SDD cycles behind all of it. Knowledge is tool-neutral: `AGENTS.md` is
the single source of truth, `skills/` lives at the repo root, and every tool-specific
entrypoint is a generated symlink produced by `./setup.sh`.

Read `AGENTS.md` for the rules and the frontmatter contract. Read this table to know
where to look and what you are allowed to trust.

## Areas

| Area | What belongs there | Citable as truth | Status |
|------|--------------------|------------------|--------|
| `AGENTS.md` | Root instructions, rules, frontmatter schema | Yes | active |
| `MAP.md` | This index | Yes | active |
| `setup.sh` | Generates per-tool symlinks; committed, output is not | Yes | active |
| `skills/` | Tool-neutral skills, one dir per skill (`SKILL.md` + optional `assets/`, `references/`) | Yes, when `validated` | 2 skills (`context-checkpoint` draft, `source-verdict` validated) |
| `theory/llm/` | How models behave: context, tokens, sampling, failure modes | Yes, when `validated` | 1 doc (`context-degradation-at-length`, validated) |
| `theory/agents/` | Single-agent design: tools, memory, context isolation | Yes, when `validated` | 2 docs (`capability-load-cost`, `instruction-provenance`) |
| `theory/orchestration/` | Multi-agent coordination, delegation, handoffs | Yes, when `validated` | 1 doc (`delegation-and-context-boundaries`, validated) |
| `theory/loops/` | Iteration shapes: plan/act/verify, review loops, termination | Yes, when `validated` | 1 doc (`verifier-availability`, validated) |
| `research/` | Received links, contrasted against evidence, each with a verdict | Verdict only, as evidence | 6 verdicts (2 `supported`, 2 `partially supported`, 2 `unverifiable`) |
| `decisions/` | Numbered ADRs (`NNNN-slug.md`) — the WHY | Yes | `0001`–`0008` ratified |
| `journal/` | Dated conversations and brainstorms | **Never as authority**; valid as provenance (ADR 0007) | 6 entries (2026-08-04, 2026-08-05 ×5) |
| `blocks/_shared/` | Target-agnostic minimal blocks with a contract | Yes, when `validated` | empty |
| `blocks/react/` | React-specific blocks | Yes, when `validated` | empty |
| `blocks/react-native/` | React Native-specific blocks | Yes, when `validated` | empty |
| `templates/` | Compositions of blocks, ready to copy | Yes, when `validated` | empty |
| `sdd/` | SDD cycles: proposal, spec, design, tasks, verification | No — process record | empty |
| `upstream/` | Experiments against `gentle-ai` / `engram` / `gga`, staged bug reports | No — experiments | 4 reports (`gentle-ai`); `0001` filed as [#2478](https://github.com/Gentleman-Programming/gentle-ai/issues/2478), `0002`–`0004` staged |

## Target coverage

| Target | State |
|--------|-------|
| `react` | in scope |
| `react-native` | in scope |
| `any` | in scope (target-agnostic content) |
| Node | planned — directory not created yet |
| Python | planned — directory not created yet |
| Go | planned — directory not created yet |
| Kotlin / KMP | planned — directory not created yet |
| Swift | planned — directory not created yet |

Do not create a target directory before there is validated content to put in it.

## How to query this repo

| Question | Where to look |
|----------|---------------|
| "What are the rules here?" | `AGENTS.md`, then the nearest nested `AGENTS.md` |
| "Give me validated blocks for react-native" | frontmatter query: `type: block`, `targets` contains `react-native`, `status: validated` |
| "Why is it done this way?" | `decisions/` |
| "Is this claim backed?" | the artifact's `sources` field; empty means not verified |
| "What was discussed about X?" | `journal/` — context and provenance only, never authority |
| "Which tool entrypoints exist?" | `setup.sh --help`; nothing generated is committed |

Every table in this repo is either generated or does not exist. This file is the one
hand-maintained index, and it holds only pointers and status — never data that already
lives in frontmatter.
