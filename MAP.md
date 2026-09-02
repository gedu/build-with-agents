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
| `check.sh` | Structural invariants: the frontmatter schema, and every `skills/` directory having an `ASK.md` entry. Redaction is not its job | Yes | active |
| `open-work.sh` | The generated index of open work. Enumerates six structural sources and reports its own coverage; prints to stdout and writes nothing | Yes | active, ADR 0016 **draft** |
| `hooks/` | Committed git hooks. `pre-commit` and `commit-msg` are the ADR 0009 redaction gates, over files and over the message | Yes | 2 hooks + `redaction-patterns.sh`, the list both read |
| `.github/` | Would hold CI workflows — the layer a fresh clone gets without installing anything. Today it holds only the gitignored Copilot entrypoint `setup.sh --copilot` generates | Yes | **no workflow.** ADR 0014 decided one and records why it is deferred |
| `skills/` | Tool-neutral skills, one dir per skill (`SKILL.md` + optional `assets/`, `references/`) | Yes, when `validated` | 5 skills (`checkout-isolation` draft, `context-checkpoint` draft, `hypothesis-cycle` draft, `project-gap-analysis` draft, `source-verdict` validated) |
| `theory/llm/` | How models behave: context, tokens, sampling, failure modes | Yes, when `validated` | 1 doc (`context-degradation-at-length`, validated) |
| `theory/agents/` | Single-agent design: tools, memory, context isolation | Yes, when `validated` | 3 docs (`capability-load-cost`, `instruction-provenance`, `tool-surface-design`) |
| `theory/orchestration/` | Multi-agent coordination, delegation, handoffs | Yes, when `validated` | 1 doc (`delegation-and-context-boundaries`, validated) |
| `theory/loops/` | Iteration shapes: plan/act/verify, review loops, termination | Yes, when `validated` | 2 docs (`verifier-availability`, `reading-and-running-find-different-defects`) |
| `research/` | Received links, contrasted against evidence, each with a verdict | Verdict only, as evidence | 11 verdicts (3 `supported`, 5 `partially supported`, 3 `unverifiable`) |
| `decisions/` | Numbered ADRs (`NNNN-slug.md`) — the WHY | Yes | `0001`–`0013` and `0015` ratified; `0014`, `0016` and `0017` **draft** — `0014` and `0016` implemented and not ratified, `0017` decided and not yet used. A `0014` on an earlier branch was renumbered to `0015` after colliding with `main`'s, which was already public |
| `hypotheses/` | Falsifiable claims with a declared test, registered before the run that could settle them | **No — zero citability** (ADR 0012). Not even as evidence | 3 open |
| `gaps/` | Gap analyses of other projects against validated practice — goal (c), and the demand signal for `blocks/` | **Evidence only, and only in aggregate.** One record is one project, never a general claim | 3 records; private projects de-identified, public sources named |
| `journal/` | Dated conversations and brainstorms | **Never as authority**; valid as provenance (ADR 0007) | 14 entries (2026-08-04, 2026-08-05 ×7, 2026-08-10 ×2, 2026-08-13 ×2, 2026-08-17, 2026-08-19) |
| `blocks/_shared/` | Target-agnostic minimal blocks with a contract | Yes, when `validated` | empty |
| `blocks/react/` | React-specific blocks | Yes, when `validated` | empty |
| `blocks/react-native/` | React Native-specific blocks | Yes, when `validated` | empty |
| `templates/` | Compositions of blocks, ready to copy | Yes, when `validated` | empty |
| `sdd/` | SDD cycles: proposal, spec, design, tasks, verification. Closed cycles move to `sdd/archive/` | No — process record | 3 cycles. `measurement-rig`, verified **PARTIAL** — verified cost instrument, unverified quality instrument. `archive/2026-08-18-failure-flood-triage`, archived after 4 verification rounds — an instrument plus a **failed** ratio target, never a comparative result: zero countable runs. `archive/2026-08-27-run-input-provenance`, archived after 2 verification rounds, PASS WITH WARNINGS (0 CRITICAL, 6 WARNING, 9 SUGGESTION) — a run's own record of what it was scored against (answer-key digest, fixture digest, surface-preimage digest), closing the archived cycle's own R-F5.3 gap (a re-derive verifies deriver drift only, never fixture drift); the same instrument, still an instrument plus a **failed** ratio target, never a comparative result: zero countable runs, and `STEP_TIMEOUT_S`/`SUITE_TIMEOUT_S` remain placeholders (`rig/run-pipeline.sh:85`) so this archive does not found the first countable run |
| `rig/` | Measurement harness: fixtures, runner, analyser. Raw captures are gitignored | Code yes; **output is evidence only**, citable once promoted to `theory/` with scope and spread (ADR 0011) | 2 experiments (`tool-surface-v1`, `failure-flood-v1`), both in progress |
| `upstream/` | Experiments against `gentle-ai` / `engram` / `gga` / `claude-code`, staged bug reports | No — experiments | `gentle-ai`: `0001` filed as [#2478](https://github.com/Gentleman-Programming/gentle-ai/issues/2478), `0002` and `0004` staged, `0003` **rejected** (resolved on 2.3.0 before filing). `claude-code`: `0001` staged |

**Correction** (`run-input-provenance` archive, 2026-08-27): the `sdd/` row previously described this
cycle as "applied (not yet verified)". It has since been verified (second pass, PASS WITH WARNINGS —
0 CRITICAL, 6 WARNING, 9 SUGGESTION) and archived to `sdd/archive/2026-08-27-run-input-provenance/`.
Named as a correction rather than silently overwritten, per this file's own record-not-erase
discipline. `sdd/` now holds 1 open cycle (`measurement-rig`) and 2 archived cycles; the total count
of 3 is unchanged by archiving. See `sdd/archive/2026-08-27-run-input-provenance/archive-report.md`
for the full closure record, including the six WARNING and nine SUGGESTION findings and where each
was carried forward.

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
| "What is open right now?" | `./open-work.sh` — generated, never hand-maintained. Read its COVERAGE block too: it states what the index cannot see |
| "What are we still unsure about?" | `hypotheses/` — open claims with their tests. Never citable |
| "What do real projects actually lack?" | `gaps/` — and a demand needs two independent records before it builds anything |
| "What can I actually ask for?" | `ASK.md` — the five skills in plain request form. The only file written for the human |
| "Which tool entrypoints exist?" | `setup.sh --help`; nothing generated is committed |
| "Does this repo still match its own rules?" | `./check.sh` for structure, `./hooks/pre-commit --all` for redaction. Both are local and must be run by hand — nothing runs them for you (ADR 0014) |
| "What do I run, and when?" | `OPERATIONS.md` |

Every table in this repo is either generated or does not exist. This file is the one
hand-maintained index, and it holds only pointers and status — never data that already
lives in frontmatter.
