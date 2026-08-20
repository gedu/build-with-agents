---
id: gaps/0003-prowler
type: research
targets: [any]
status: validated
verified: 2026-08-20
sources: ["skills/project-gap-analysis/SKILL.md", "gaps/0001-rn-expo-wallet-timeboxed.md", "gaps/0002-expensify-app.md", "https://github.com/prowler-cloud/prowler", "theory/agents/capability-load-cost.md", "theory/agents/instruction-provenance.md", "theory/agents/tool-surface-design.md", "theory/llm/context-degradation-at-length.md", "theory/loops/reading-and-running-find-different-defects.md", "theory/loops/verifier-availability.md", "theory/orchestration/delegation-and-context-boundaries.md"]
---

# 0003 — Prowler

Third run of `skills/project-gap-analysis`. **Named**, under the public-source exception the skill
states: the practice analysed here is already published, and de-identifying it would make every claim
below uncheckable while the class description would identify it anyway.

Chosen for a property neither earlier run had: a project whose agent practice is **mature**. Runs 1
and 2 measured a timeboxed solo build and a large community app. This one already does most of what
this repo documents, which makes its two remaining gaps worth more than a project's first ten.

`targets: [any]` rather than `[react]`, departing from runs 1 and 2. None of the seven checks reads
application source, and none of the findings below depends on the stack. The React/Next UI is what
places the project inside this repo's declared scope; it is not what the record is about.

## Project class

Open-source cloud security platform. Monorepo, ~11,700 tracked files, ~8,900 commits, continuous since
2016-06. Python-majority (~6,700 files) with a React 19 / Next 16 UI, plus an API, an MCP server and
documentation, each its own component.

**Scope of this analysis: the agent-practice surface only** — the six `AGENTS.md` files, 37 skill
directories, the MCP declaration, 51 CI workflows, and the pre-commit configuration. Application
source was not read, because none of the seven checks asks about it. Check 3 was **sampled, not
enumerated**: 4 skills of 37.

## Checks

| # | Check | Verdict |
|---|---|---|
| 1 | Resident capability cost | `present` |
| 2 | Instruction provenance | `present` |
| 3 | Tool surface as prose | `present` — and a worked pattern |
| 4 | Reset practice | **`absent`** |
| 5 | Both defect channels | `present`, review depth unestablished |
| 6 | Verifier availability | **`partial`** |
| 7 | Delegation boundaries | `present` — and a worked pattern |

### 1. Resident capability cost — `present`
`theory/agents/capability-load-cost.md`

One MCP server declared, over HTTP, with its credential taken from user config. Not a set of servers
connected eagerly against future need. The 37 skills are on-demand bodies behind resident names and
descriptions, which is the shape the doc argues for.

The real resident cost is instruction prose — the root file is ~190 lines and the documentation
component's is ~640. Component nesting is the mitigation: only the file governing the edited path
loads.

### 2. Instruction provenance — `present`
`theory/agents/instruction-provenance.md`

The root instructions state precedence **and** location together: component files exist, they are
named by path, and they override the root where guidance conflicts. The failure mode the doc names is
precedence documented without provenance, and that is not what happens here.

The generated-block case the check calls out specifically is present and comes out *better* than the
doc's worry. One CI workflow is compiled from a source file beside it and stamped do-not-edit, and its
header carries the source hashes, the compiler version, and a manifest pinning every action SHA and
container digest. Drift is detectable and the source is editable. What cannot be reconciled locally is
the artifact's content — see check 6.

### 3. Tool surface as prose — `present`, and a worked pattern
`theory/agents/tool-surface-design.md`

Sampled 4 of 37. Every one carries a prose description with an explicit trigger clause, auto-invoke
phrases, and a scope list naming the components it applies to; one adds an allowed-tools list. One
description **cross-references a sibling skill**, telling the model when to prefer the neighbour
instead.

That last part goes past what this repo's own theory doc asks for. The doc argues that selection
happens in names and descriptions rather than in schemas; this project uses that surface for
disambiguation *between* skills, not only for selection of one.

### 4. Reset practice — `absent`
`theory/llm/context-degradation-at-length.md`

Swept every instruction file and every skill for the vocabulary of session length, compaction,
clearing and handoff. Nothing describes ending or resetting a session.

**One near-miss, recorded so it is not miscounted later.** One skill uses "checkpoints" extensively,
and they are well designed — a checkpoint is a hard stop to ask the user a question, and the skill
states that a confirmation is scoped to a single checkpoint and does not transfer to later ones. But
that is turn-taking, not context management. Counting it would be reading the word rather than the
practice.

This is `absent` in the plain sense, not the second failure direction: there is no reset practice at
all, rather than one wrongly triggered by a token count.

### 5. Both defect channels — `present`, review depth unestablished
`theory/loops/reading-and-running-find-different-defects.md`

Execution against hostile input is unusually well covered: static analysis on three components,
dedicated security workflows on four, a secret scanner, an end-to-end browser suite, and a workflow
that audits the project's own CI configuration.

Reading is routed — code ownership rules and a pull-request template both exist.

Same limit run 1 recorded, and it is a property of repositories rather than of this project: ownership
rules prove a review is *routed*, not that a diff was *read*. Recorded `present` with the unestablished
part named, and resolved by assumption in neither direction.

Worth noting: this project ships checks that audit *other* repositories for exactly this property. The
practice is productised, not merely adopted.

### 6. Verifier availability — `partial`
`theory/loops/verifier-availability.md`

Across the CI workflows and the pre-commit configuration: 24 `continue-on-error: true`, 43 `|| true`,
19 redirections of stderr, and no `|| :`.

**The aggregate is misleading and is not reportable alone.** Split by file, a single generated workflow
holds 47 of the combined `continue-on-error`/`|| true` occurrences. Every hand-written workflow sits in
the 2-4 range. The concentration is in a compiled artifact the project does not hand-write.

Evidence the project reasons about this class at all — a comment in the pre-commit configuration
records that one auditing tool "trips exit 3 (no audit was performed)" on broader paths, and scopes the
hook's file pattern so the tool never lands in its own no-audit state. That is exactly the
could-not-run-versus-passed distinction, spotted and designed around.

`partial` and not `present`: no gate here is shown distinguishing its own could-not-run from a pass,
and the swallow count stays high after discounting the generated file. `partial` and not `absent`: the
comment above, and the low per-file counts on hand-written workflows, are evidence of attention.

**Not established, and it would need running rather than reading:** whether any of those guards sits on
a step whose failure would matter. The check asks whether the shape exists. Which instance is
load-bearing is a different and more expensive question, and
`theory/loops/reading-and-running-find-different-defects.md` is the reason it cannot be settled by
reading.

### 7. Delegation boundaries — `present`, and a worked pattern
`theory/orchestration/delegation-and-context-boundaries.md`

One CI workflow delegates issue triage to a coding agent and writes its constraints down rather than
assuming them. The blast radius is bounded on five independent axes: a wall-clock timeout, a per-user
rate limit over a window, per-issue concurrency with cancellation, an all-read permission set, and a
network allow-list naming the few hosts it may reach. A runner-hardening step with an egress policy
runs first, and the agent's prompt is a separate imported file rather than inline prose.

The doc's failure mode is a delegation that inherits nothing and silently drops every constraint the
parent never wrote down. A reader who had not been in the conversation could reconstruct this boundary
from the file alone.

The workflow's own description prefixes it "[Experimental]", which is the project's scoping and is
reported as stated rather than flattened.

## Unstatable findings

**Zero.** Everything above is stateable from a public repository, using only what that repository
already publishes.

## Demand

| From | Capability that would close it | Occurrences |
|---|---|---|
| Check 4 `absent` | A session-reset practice keyed to a **behavioural** trigger — re-deriving a settled fact, contradicting an earlier decision, losing the verified/assumed split — rather than to a token count | **Third**. Runs 1 and 2 already carried it to two, where the rule fired and resolved to `skills/context-checkpoint` |
| Check 6 `partial` | A gate convention that separates *could not run* from *passed*, and a way to see which swallowed status is load-bearing | **First** as a `partial` |

The third occurrence of check 4 re-licenses nothing — two had already licensed the demand, and it
resolved to an existing draft skill rather than to a new block. What it adds is the datum that makes it
worth reading: this is the first project in the series whose agent practice is otherwise mature, and it
still has no reset practice. The absence is not a symptom of a project that skipped agent discipline.

Per `gaps/README.md`, one record never justifies building anything, and two occurrences license the
demand rather than a general claim about projects of this kind.

## What this record supplies rather than asks for

Three patterns worth extracting **from here** if a block is ever built, rather than designed from a
complaint — the difference between a block that has been run and one that has been imagined:

1. **Skill descriptions that disambiguate between siblings**, not only select one. Directly relevant to
   this repo's own `ASK.md` problem: a description written for a model does not tell a human what
   exists. This project writes both audiences into one block.
2. **Bounded delegation on five explicit axes** — time, rate, concurrency, permission, network.
3. **Compiling an agent workflow from a versioned source** with content hashes and a pinned dependency
   manifest, instead of hand-writing the artifact.
