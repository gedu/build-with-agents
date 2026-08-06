---
id: decisions/0010-measurements-vary-the-harness-not-the-model
type: decision
targets: [any]
status: validated
verified: 2026-08-06
sources: ["theory/agents/capability-load-cost.md", "theory/agents/tool-surface-design.md", "theory/orchestration/delegation-and-context-boundaries.md", "theory/loops/reading-and-running-find-different-defects.md", "research/harness-over-model-databricks.md", "research/agent-harness-explainer-cluster.md", "journal/2026-08-05-knowledge-base-handoff.md"]
---

# 0010 — Measurements vary the harness, with the model held fixed

## Context

Every `theory/` file in this repo ends with a section naming a measurement nobody ran. The three
named in `journal/2026-08-05-knowledge-base-handoff.md` §4 — delegated versus inline on the same task,
resident versus deferred tool sets on the same task, retrieval precision at 500K–1M — are **the same
harness three times.** Building it once unblocks all of them.

It also unblocks the operator's goal (2), an auditor answering *"is this project AI-ready, and what are
the gaps"*. That is blocked on a written definition of AI-ready, the definition is the `theory/`
content, and the content is currently reasoning without numbers. An auditor that says *"you have 90
tools resident, that is a lot"* is giving an opinion. One that says *"90 resident tools cost N tokens
per session and M wrong-tool calls against a scoped surface"* is reporting a gap.

**Harness**, as used here and as converged on by three independent sources in
`research/agent-harness-explainer-cluster.md`: everything around the model that is not the model. The
model decides; the harness executes and constrains. Concretely — which tools are visible, how their
descriptions are written, whether schemas are resident or deferred, the instruction files, whether work
is delegated or inline, the loop's stopping conditions, the gates.

Ratified by the operator on 2026-08-06.

## Decision

**A measurement in this repo holds the model fixed and varies the harness.** Model-versus-model
comparison is explicitly out of scope for v1.

Two reasons, and the second is the one that decides it.

**The open questions are harness questions.** Does deferral change selection reliability or only token
cost? Does delegation beat inline on the same task? Does scoped tool access reduce wrong-tool calls?
Nobody outside is measuring these, and they are the questions this repo already wrote down and could
not answer.

**Harness findings outlive model releases.** A model-versus-model table is a leaderboard: the vendor
changes the model underneath it and the number expires. A finding about *structure* stays true across
model generations, which is the only kind of number worth the cost of producing it here.

Model-versus-model becomes nearly free once the harness exists — it is the same rig with a different
fixed value. It is deferred, not rejected.

### Five constraints, non-negotiable, because each one is a way this fails silently

**1. Every task carries a deterministic pass/fail, and the checker is written before the prompt.**

Not *"did it write good code"* — do these tests pass, does this file exist with this content, does this
command exit 0, does this JSON match this schema. If the verifier cannot be written first, the task does
not enter the suite.

This is the constraint that keeps the whole thing honest, and the reason is local: token counts are
trivial and deterministic, quality is not. A rig that measures cost precisely and quality loosely will
produce conclusions about cost and present them as conclusions about quality. This repo refused a vendor
figure for a structurally identical fault — see `research/harness-over-model-databricks.md`, where the
one number offered could not isolate the one variable it was offered to prove. The same standard applies
inward or the refusal was hypocrisy.

It follows that **code planning cannot be in v1.** There is no deterministic grader for a plan. Recorded
now rather than discovered after fifteen tasks are written.

**2. One variable per run, with everything held fixed recorded.**

Per run: model id, harness version, task id, a hash of the exact prompt bytes, a hash of the tool
surface. The two hashes are the immutable-target-identity idea from the review lifecycle applied here,
and they exist so a later reader can prove two runs differed in exactly one thing.

**3. N runs per cell, reporting spread and not only a mean.**

One run per (task, harness) measures sampling noise. Models are stochastic; a single-run difference is
not a finding. Without repeats and a reported spread, every conclusion is noise rendered as a chart —
which is the most common way a homemade benchmark lies.

**4. One category first, three difficulty tiers, three tasks.**

Categories — coding, planning, GitHub, tools, bugs — are a taxonomy, and a taxonomy is not a claim. Five
categories times three tiers is fifteen tasks each needing a deterministic verifier, which guarantees
either a fuzzy grader or an unfinished suite. Start with one category whose outcomes are checkable, get
the rig honest on three tasks, then expand.

**5. What is recorded per run**, chosen because the existing `theory/` files say these are the axes that
matter:

| Recorded | Why it is in the list |
|---|---|
| Input, output and **cached** tokens, separately | Cached and uncached differ by roughly an order of magnitude in price; a single total hides it |
| Turns / loop iterations | The cost axis in `theory/agents/capability-load-cost.md` is per-turn |
| Wall clock | Not a proxy for cost, and needed to notice a rig that got slower |
| Tool calls: count, which tools, and **wrong-tool calls** | `theory/agents/tool-surface-design.md` names selection reliability as the axis nobody measures. This is that number |
| Deterministic verdict | Constraint 1. The only quality signal admitted in v1 |

## Consequences

| Consequence | Detail |
|---|---|
| Three named experiments become one build | Delegated-vs-inline, resident-vs-deferred, and scoped-vs-broad are all the same rig with a different pair of harnesses |
| `theory/` gains its own numbers | Each result replaces a "what would sharpen it" section with a measurement, scoped to the rig that produced it |
| The auditor becomes specifiable | Goal (2) can name measured dimensions instead of asserting them |
| A measured result is citable as truth; the rig therefore needs its own review | Once this exists, whatever it emits gets promoted. The harness that produces numbers is itself a verifier, and `theory/loops/reading-and-running-find-different-defects.md` applies to it — including that its own test fixtures can lie about what they ran |
| Wrong-tool calls need a definition before they can be counted | "Wrong" requires a per-task expected-tool set, written with the verifier. Not yet specified |
| Model-versus-model is deferred, not rejected | Same rig, different fixed value, once the harness comparisons are trustworthy |
| The install command is unaffected | Goal (1) is mechanical and independent; `setup.sh` already does part of it |

## Alternatives

| Rejected | Reason |
|---|---|
| Model versus model as v1 | A leaderboard. Expires when the vendor ships, answers no question this repo has open, and the vendor's own release notes move under the measurement |
| LLM-as-judge for quality scoring | Puts a probabilistic grader at the centre of the one thing the rig exists to make objective. Model-based graders need calibration and this repo has none. Reconsider only with a deterministic set to calibrate against |
| Write an adapter into `perf-vibe` | Its data model is mobile performance markers from Maestro flows and Flashlight metrics; agent-run records are a different domain and would be forced into a schema built for another. **Take its discipline instead** — local SQLite, per-commit baselines, repeated iterations, regression/stable classification, JSON with `schema_version`, and above all the `<sha>-dirty` tag that refuses to write a baseline from a dirty tree. That last one is the same problem as freezing a review target, solved the same way |
| Start with all five categories | Fifteen tasks needing fifteen deterministic verifiers before the first number exists. Guarantees the grader gets relaxed |
| Skip the ADR and start coding | This decides how the repo produces the numbers it will later cite as truth. A rig with no recorded rationale gets its constraints relaxed by the first person who finds them inconvenient — most likely its author, in a hurry |
