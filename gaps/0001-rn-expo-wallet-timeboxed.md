---
id: gaps/0001-rn-expo-wallet-timeboxed
type: research
targets: [react-native]
status: validated
verified: 2026-08-11
sources: ["skills/project-gap-analysis/SKILL.md", "theory/agents/capability-load-cost.md", "theory/agents/instruction-provenance.md", "theory/agents/tool-surface-design.md", "theory/llm/context-degradation-at-length.md", "theory/loops/reading-and-running-find-different-defects.md", "theory/loops/verifier-availability.md", "theory/orchestration/delegation-and-context-boundaries.md"]
---

# 0001 — React Native mobile wallet, timeboxed, agent-built

First run of `skills/project-gap-analysis`.

## Project class

A React Native + Expo mobile cryptocurrency wallet. Roughly 200 tracked files and 20 commits, every
one landed through a numbered pull request. TypeScript in strict mode, a vendor SDK for wallet
operations, Jest with co-located tests. Single developer, built end to end with AI assistance.

**Declared scope: a fixed 48-hour assessment**, stated in the project's own agent instructions. This
is load-bearing for reading the results — several absences below are budget decisions rather than
oversights, and the project applies its stated scope consistently rather than selectively.

## Checks

| # | Check | Verdict | Source |
|---|---|---|---|
| 1 | Resident capability cost | `present` | `theory/agents/capability-load-cost.md` |
| 2 | Instruction provenance | `partial` | `theory/agents/instruction-provenance.md` |
| 3 | Tool surface as prose | `present` | `theory/agents/tool-surface-design.md` |
| 4 | Reset practice | `absent` | `theory/llm/context-degradation-at-length.md` |
| 5 | Both defect channels | `present` | `theory/loops/reading-and-running-find-different-defects.md` |
| 6 | Verifier availability | `absent` | `theory/loops/verifier-availability.md` |
| 7 | Delegation boundaries | `n-a` | `theory/orchestration/delegation-and-context-boundaries.md` |

### 1 — `present`

One editor plugin enabled and no MCP servers configured, alongside three project-local skills. The
resident surface is small and nothing is connected speculatively.

### 2 — `partial`

Two agent-instruction entry points exist: a long one read by one vendor's tool, and a short one at
the tool-neutral filename read by everything else. The long file names the short one and states its
role; the short one does not point back.

An executor entering at the tool-neutral file — which is the entire reason that filename convention
exists — receives a few lines on one narrow topic and nothing about the project's mandatory design
gate, its test-first requirement, its type-strictness rule, or where its decisions live. Nothing at
that entry point signals that the other file exists.

The project's most recent commit corrects stale version and documentation references in exactly this
material, so drift here has already occurred once rather than being hypothetical.

### 3 — `present`

Skill descriptions are written to be read and carry explicit triggers rather than terse labels, and
the main instruction file additionally indexes them in a trigger/purpose/when table. Bytes are spent
on the part a model reads while choosing.

One inconsistency: that index lists two skills while three exist on disk — the same one-directional
drift as check 2, in a reader-facing table.

### 4 — `absent`

No session-reset or context practice in any instruction file or document: neither a behavioural
trigger nor a token-count one.

Precision matters here. The absence of a token threshold is **correct** — no published measurement
supports one. What is missing is the other half: a behavioural trigger such as re-deriving a settled
fact, contradicting an earlier decision, or losing the verified-versus-assumed distinction. Within a
48-hour box this is defensible; it becomes load-bearing the moment the project outlives its box,
because the failure is silent.

### 5 — `present`

The execution channel is genuinely exercised rather than nominal. Around two dozen co-located test
files, and the adversarial cases sit on the parsing and validation functions where hostile input
actually matters — one address validator carries eight cases of which six are rejections covering
length, missing prefix, non-hex characters, empty input and a bare prefix. Seed import, seed
confirmation and keypad input are covered in the same shape.

The reading channel exists in form: every commit landed via a pull request. Its **depth is not
establishable from the repository alone**, and on a single-developer timebox self-merge is likely.
Recorded as unestablished rather than assumed in either direction.

### 6 — `absent`

**The highest-value finding of this analysis.**

Four checks exist as declared scripts — lint, typecheck, test, and a formatting check. There is no
CI configuration and no installed git hook, only the stock placeholder git ships with. Nothing
invokes any of them at any obligatory point.

What makes this a finding rather than a complaint: the repository contains **zero fail-open shapes**
— no swallowed exit statuses, no discarded stderr on a checked command, no continue-on-error, no
pass-with-no-tests. When these checks run, they report honestly.

So this is not a gate that lies. It is a loop with no check step: every surface describes the project
as having linting, strict types and tests, and nothing guarantees any of them ran before a commit
landed. Strict typing and a real test suite are both defeated by the same missing invocation.

### 7 — `n-a`

No subagent, task or job definitions. The check does not apply to work that is not delegated.

## Unstatable findings

None. Every finding above states without any identifier this repository may not carry.

## Demand

| From | Capability wanted | Occurrences |
|---|---|---|
| Check 6 | A minimal enforcement gate for a React Native project: run the checks the project already declares, at a point that cannot be skipped by accident, distinguishing *could not run* from *passed* | 1 |
| Check 2 | A bidirectional instruction-provenance pattern: whichever entry file an executor reads, it names the others and their roles | 1 |
| Check 4 | A behavioural session-reset trigger, never a token threshold | 1 |

**Nothing is built from this record.** Every demand stands at one occurrence, and `gaps/README.md`
requires two independent records — different projects, different owners — before a block exists.

Check 4's demand maps onto `skills/context-checkpoint`, already in the repo at `status: draft`,
rather than onto a new block. A demand whose answer is already half-built is worth noting separately
from a demand with nothing behind it.
