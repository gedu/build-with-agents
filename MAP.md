---
id: map
type: index
targets: [any]
status: validated
verified: 2026-08-13
sources: ["decisions/0001-agents-md-as-single-source-of-truth.md", "decisions/0004-mandatory-frontmatter-as-query-interface.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0011-rig-produces-evidence-not-truth.md", "journal/2026-08-04-repo-skeleton-design.md"]
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
| `MAP.md` | This index — where knowledge lives | Yes | active |
| `OPERATIONS.md` | What to run and when — gates, rig, review lifecycle. Points at `--help` rather than duplicating flags | Yes | active |
| `ASK.md` | For the human: what these skills let you ask for, in your own words. The only file here not addressed to an executor | Yes | draft, 5 entries |
| `BACKLOG.md` | Candidate practices and downstream deliverables, recorded with a named unblock condition and never built ahead of it | Yes | draft, 2 entries |
| `setup.sh` | Generates per-tool symlinks and installs git hooks; committed, output is not | Yes | active |
| `hooks/` | Committed git hooks. `pre-commit` is the ADR 0009 redaction gate | Yes | 1 hook (`pre-commit`) |
| `skills/` | Tool-neutral skills, one dir per skill (`SKILL.md` + optional `assets/`, `references/`) | Yes, when `validated` | 5 skills (`checkout-isolation` draft, `context-checkpoint` draft, `hypothesis-cycle` draft, `project-gap-analysis` draft, `source-verdict` validated) |
| `theory/llm/` | How models behave: context, tokens, sampling, failure modes | Yes, when `validated` | 1 doc (`context-degradation-at-length`, validated) |
| `theory/agents/` | Single-agent design: tools, memory, context isolation | Yes, when `validated` | 3 docs (`capability-load-cost`, `instruction-provenance`, `tool-surface-design`) |
| `theory/orchestration/` | Multi-agent coordination, delegation, handoffs | Yes, when `validated` | 1 doc (`delegation-and-context-boundaries`, validated) |
| `theory/loops/` | Iteration shapes: plan/act/verify, review loops, termination | Yes, when `validated` | 2 docs (`verifier-availability`, `reading-and-running-find-different-defects`) |
| `research/` | Received links, contrasted against evidence, each with a verdict | Verdict only, as evidence | 11 verdicts (3 `supported`, 5 `partially supported`, 3 `unverifiable`) |
| `decisions/` | Numbered ADRs (`NNNN-slug.md`) — the WHY | Yes | `0001`–`0013`, `0015` ratified (`0014` renumbered to `0015` in PR7D after colliding with `main`'s own `0014`, not yet merged here) |
| `hypotheses/` | Falsifiable claims with a declared test, registered before the run that could settle them | **No — zero citability** (ADR 0012). Not even as evidence | 3 open |
| `gaps/` | Gap analyses of other projects against validated practice — goal (c), and the demand signal for `blocks/` | **Evidence only, and only in aggregate.** One record is one project, never a general claim | 2 records; private projects de-identified, public sources named |
| `journal/` | Dated conversations and brainstorms | **Never as authority**; valid as provenance (ADR 0007) | 11 entries (2026-08-04, 2026-08-05 ×7, 2026-08-10 ×2, 2026-08-13) |
| `blocks/_shared/` | Target-agnostic minimal blocks with a contract | Yes, when `validated` | empty |
| `blocks/react/` | React-specific blocks | Yes, when `validated` | empty |
| `blocks/react-native/` | React Native-specific blocks | Yes, when `validated` | empty |
| `templates/` | Compositions of blocks, ready to copy | Yes, when `validated` | empty |
| `sdd/` | SDD cycles: proposal, spec, design, tasks, verification | No — process record | 1 cycle (`measurement-rig`), verified **PARTIAL** — verified cost instrument, unverified quality instrument |
| `rig/` | Measurement harness: fixtures, runner, analyser. Raw captures are gitignored | Code yes; **output is evidence only**, citable once promoted to `theory/` with scope and spread (ADR 0011) | 2 experiments (`tool-surface-v1`, `failure-flood-v1`), both in progress |
| `upstream/` | Experiments against `gentle-ai` / `engram` / `gga` / `claude-code`, staged bug reports | No — experiments | `gentle-ai`: `0001` filed as [#2478](https://github.com/Gentleman-Programming/gentle-ai/issues/2478), `0002` and `0004` staged, `0003` **rejected** (resolved on 2.3.0 before filing). `claude-code`: `0001` staged |

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
| "What are we still unsure about?" | `hypotheses/` — open claims with their tests. Never citable |
| "What do real projects actually lack?" | `gaps/` — and a demand needs two independent records before it builds anything |
| "What can I actually ask for?" | `ASK.md` — the five skills in plain request form. The only file written for the human |
| "Which tool entrypoints exist?" | `setup.sh --help`; nothing generated is committed |
| "What do I run, and when?" | `OPERATIONS.md` |

Every table in this repo is either generated or does not exist. This file is the one
hand-maintained index, and it holds only pointers and status — never data that already
lives in frontmatter.
