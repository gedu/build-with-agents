---
id: sdd/measurement-rig/proposal
type: journal
targets: [any]
status: draft
verified: 2026-08-06
sources: ["decisions/0010-measurements-vary-the-harness-not-the-model.md", "sdd/measurement-rig/exploration.md", "theory/agents/tool-surface-design.md", "theory/agents/capability-load-cost.md", "sdd/testing-capabilities.md", "AGENTS.md"]
---

# measurement-rig — proposal: one number for the scoping lever

SDD proposal phase for `measurement-rig`. Intent, scope, approach. No spec, no design, no code.

Bounded by `decisions/0010-measurements-vary-the-harness-not-the-model.md` (five non-negotiable
constraints) and by `sdd/measurement-rig/exploration.md` (instrumentation, including its supersession
notice — the corrections win).

## Intent

`theory/agents/tool-surface-design.md` is `status: validated` and tells a reader to **scope by role
first**, on the grounds that scoping is the only lever that reduces candidate count. The same file
states plainly: *"Nothing here is evidence that a scoped surface outperforms a broad one."* The repo's
strongest tool-surface recommendation rests on vendor normative guidance with no disclosed method.

Three costs follow, and they are business costs, not aesthetic ones.

| Cost today | Consequence |
|---|---|
| Goal (c), the project auditor, cannot name a gap | It says *"90 resident tools is a lot"* — an opinion. It cannot say *"and it costs M wrong-tool calls"* |
| A recommendation with no magnitude cannot survive a client asking *"by how much"* | The advice gets discounted to taste, or worse, applied where it does nothing |
| This repo has a history of naming experiments and not running them | Every `theory/` file ends with an unrun measurement. Credibility of the whole knowledge base is the asset at risk |

The repo already refused a vendor figure for exactly this fault — `research/harness-over-model-databricks.md`,
where the one number offered could not isolate the one variable it was offered to prove. Applying that
standard inward is the point of this change.

## The single question v1 answers

> **On one task class, does reducing the visible tool surface from 54 names to 3 change how often the
> task is completed properly, and how often the model reaches for a tool outside the task's expected
> set?**

Exact comparison. Model fixed, prompt bytes fixed, fixture fixed; one variable — the visible surface,
read back from `init.tools` rather than asserted.

| | Arm BROAD | Arm SCOPED |
|---|---|---|
| Visible tools | 54 | 3 — `Glob`, `Grep`, `Read` |
| Mechanism | default surface, no scoping flag | `--disallowedTools` |
| Sufficient to complete the task | Yes | Yes — by construction (see below) |

`--allowedTools` is **not** the mechanism and must never appear as one: the exploration measured 54 → 54
tools and byte-identical cost. An arm built on it would measure nothing and would look like it worked.

**Task class**: defect-finding over a frozen synthetic fixture. Three tasks, one per difficulty tier
(ADR constraint 4). Each task names seeded defects, so the answer key exists before the prompt exists
(ADR constraint 1). The agent reports findings as its final text in a strict line format
(`<relative-path>:<line>`), so the 3-tool surface is genuinely sufficient and no write tool is needed in
either arm.

**N = 5 runs per (task, arm) cell** → 30 runs, plus re-runs for voids (ADR constraint 3: report spread,
not only a mean).

## Outcome definition and classification

Two deterministic checks per run, both written before the prompt:

| Check | Definition |
|---|---|
| **Outcome achieved** | Final text parses in the required format and names exactly the seeded defect set for that task |
| **Practice respected** | (a) no call to a tool in the task's **forbidden** set, and (b) every reported defect's file appears in an earlier `Read`/`Grep` `tool_use` in the same transcript |

Check (b) is the load-bearing half. It is violable in **both** arms, which is what stops the practice
check from collapsing into a restatement of the surface.

Three tool-name sets per task, and the distinction is deliberate:

| Set | Meaning | Effect |
|---|---|---|
| **Expected** | `{Grep, Read}` — a *proper subset* of the SCOPED surface | Baseline for counting |
| **Off-set** | Any call whose `name` is outside Expected (e.g. `Glob`) | Counted and graded. Does **not** alone fail the run |
| **Forbidden** | Any write/execute/MCP tool | Fails the practice check |

### The four cells, and the interesting one

| Outcome | Practice | Classification | Counts as |
|---|---|---|---|
| pass | pass | `proper` | **Pass** |
| pass | fail | `improper-success` | **Fail** — the interesting cell |
| fail | pass | `clean-failure` | Fail |
| fail | fail | `failure` | Fail |

**A run that produced the right artifact by calling the wrong tools did not do it properly, so it does
not pass.** That is the operator's refinement and it is binding.

The resolution the binary would destroy is preserved three ways, all mandatory in the published result:
the four-cell table per arm is always reported (`improper-success` is never merged into either pass or
plain failure); the **off-set + forbidden call count per run** is reported as a distribution, not a mean;
and `permission_denials` plus `tool_result.is_error` are reported as independent corroborating signals.

- **Primary metric**: `proper` rate per arm — 15 runs each, plus the per-task breakdown with min/max.
- **Graded companion metric**: off-set + forbidden calls per run.

### The tautology guard

In the SCOPED arm a forbidden tool is not visible, so its forbidden count is **zero by construction**.
That floor is not a finding and must not be reported as one. The non-trivial quantities are: how often
the BROAD arm reaches off Expected at all, and whether the `proper` rates differ. This is stated here
because it is precisely the shape of the `--allowedTools` trap — a design that cannot fail in the
direction it wants.

## Pre-registered falsification

Registered before any run. Whichever branch fires, it fires.

| Result | Verdict on `theory/agents/tool-surface-design.md` |
|---|---|
| SCOPED `proper` exceeds BROAD by ≥ 4 of 15 runs, with non-overlapping per-task min/max in ≥ 2 of 3 tasks, **and** BROAD median off-set+forbidden ≥ 1 per run | **Supports** the scoping lever. The "what would sharpen it" section is replaced by the measurement, scoped to this rig and task class |
| Difference ≤ 1 of 15 runs, **or** BROAD median off-set+forbidden = 0 | **Narrows.** The scoping lever is undetectable on this task class at this contrast; the file says so, naming the class |
| BROAD `proper` exceeds SCOPED | **Contradiction.** The relevant sentence is marked `rejected` and kept — never deleted (`AGENTS.md` working agreement 5) |

### Instrument doubt — pre-registered threshold X = 3

Instrument doubt is a declared threshold, not something reached for when a result is unwelcome.

**X = 3 runs exhibiting the same anomaly class within one experiment** triggers a mandatory instrument
investigation, and no result may be written to `theory/` until it closes. Anomaly classes:
`init.tools` mismatch against the intended surface, prompt-byte-hash mismatch, missing `result` event,
unparseable stream, void by timeout, `permissionMode` differing across a pair, `rate_limit_event`.

Why 3: with N = 5 per cell, one anomaly is sampling, two is a coincidence two people can argue about,
three of the *same kind* is a pattern. Below 5 it is still cheap to re-run; at 3 the cell's spread is
already compromised.

**The asymmetry rule, which is the whole reason X is written down:** instrument doubt is triggered by
**mechanical anomalies only**. A refuting result produced with a clean anomaly log may **not** be
attributed to the instrument. The anomaly count is published alongside the result so the threshold is
checked mechanically rather than felt.

## Scope

### In scope

- Three defect-finding tasks (three tiers) over a **frozen, versioned synthetic fixture directory** with
  seeded defects. Frozen means: never edited after freeze; a change is a new version directory.
- A deterministic outcome checker and practice checker per task, **written before the prompt**.
- Two arms, N = 5, 30 runs, driven headless with `--output-format stream-json` (plain `json` gives only
  the final aggregate and no transcript).
- Per-run record: ADR 0010's five recorded items, plus surface identity read back from `init.tools`,
  prompt-byte hash, fixture version, model id, `permissionMode`, `permission_denials`, `stop_reason`.
- **One number reaching `theory/`** — a measurement, a narrowing, or a rejection.

### Out of scope — non-goals, named as clearly as the goals

| Not doing | Why |
|---|---|
| A reusable benchmark framework, schema, CLI, or database | The operator chose one question answered end to end over infrastructure first, on the stated grounds of this repo's unrun-experiment history. A reusable rig is a **consequence**, not the goal |
| Model versus model | ADR 0010 defers it: same rig, different fixed value |
| LLM-as-judge or any probabilistic grader | ADR 0010 rejects it outright |
| Code-planning tasks | No deterministic grader exists. ADR 0010 forecloses it for v1 |
| Delegated-vs-inline and resident-vs-deferred | The other two named experiments. Same rig later, not now |
| Levers 1 and 2 (descriptions, splitting/renaming) | Only lever 3, scoping, is under test |
| `--bare` plus an API key | Buys off-machine reproducibility for real money. A real goal, not the first one |
| This repo's real files, or an external repo, as substrate | Substrate must not change under the experiment |
| Eliminating or measuring the ~26k ambient context | It is a **constant** across arms; it does not invalidate an A/B difference |
| Cost as a headline finding | ~9% between 54 and 3 tools, and two same-config runs returned byte-identical costs — caching is doing work these deltas cannot separate |
| A test runner | None exists in this repo (`sdd/testing-capabilities.md`). Do not schedule one |

## Capabilities

This repo does not use an `openspec/specs/` tree (`sdd/project-context.md`), so these name the
spec-phase deliverables rather than spec file paths.

### New

- `tool-surface-experiment`: the v1 comparison — arms, tasks, fixture contract, per-run record, the two
  checkers, the four-cell classification, the void rules.

### Modified

- `theory/agents/tool-surface-design.md`: its "what would sharpen it" section becomes a measurement, a
  narrowed claim, or a `rejected` marking. Which one is decided by the pre-registered table, not later.

## Approach

A thin driver (language is a `sdd-design` decision; only Bash exists in this repo today) that per
`(task, arm, iteration)` persists the exact prompt bytes and the full `stream-json` capture
**incrementally**, validates `init.tools` against the intended surface and voids on mismatch, runs both
checkers, and classifies into one of four cells. One aggregation pass emits the per-arm four-cell table
and the off-set distribution. One write reaches `theory/`.

Delivery is staged deliberately: the **tier-1 cell (10 runs) completes end to end first** as a rig
shakedown, and only then do tiers 2 and 3 run. That is what makes "a number exists" reachable before
scope can grow.

Two open items the spec phase must settle, both surfaced by the exploration rather than assumed here:

- **The run bound.** This CLI version exposes no `--max-turns`. Proposed: an external wall-clock timeout
  (~300 s) plus a post-hoc void on `num_turns` or `total_cost_usd` ceilings, calibrated on the tier-1
  pilot. Implication: a killed run must still yield its transcript, which is why the stream is persisted
  incrementally.
- **How SCOPED reaches 3 without a second variable.** Preferred: `--disallowedTools` covers MCP tool
  names too, so `mcp_servers` stays connected in both arms and the only `init` delta is `tools`.
  Verified fallback: `--strict-mcp-config` plus disallowed built-ins, which also drops 25 servers to 0 —
  a real second variable, to be recorded as a named confound bounded by the ~9% cost delta.

## Affected areas

| Area | Impact | Description |
|---|---|---|
| `sdd/measurement-rig/` | Modified | Spec, design, tasks follow this proposal |
| A new rig directory under `<repo>` | New | Driver, checkers, frozen fixtures, run records |
| `theory/agents/tool-surface-design.md` | Modified | Measurement, narrowing, or `rejected` marking |
| `theory/agents/capability-load-cost.md` | Possibly modified | Only if the cost split contradicts it |
| `decisions/` | Possibly new | If the rig's own constraints need ratifying |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The design cannot fail in the direction it wants (SCOPED's forbidden count is 0 by construction) | High | Expected set is a proper subset of the SCOPED surface; primary metric is `proper` rate; the floor is explicitly not reported as a finding |
| BROAD never reaches off-set — the extra 51 names are simply unattractive here | Medium | This **is** the pre-registered narrowing branch. Not a rig failure |
| `--disallowedTools` may not remove MCP names | Medium | Verified fallback exists; the confound is recorded, not hidden |
| Ambient config drift between arms (`permissionMode: bypassPermissions` arrived uninvited) | Medium | `init` recorded per run; a differing pair is voided |
| Subscription rate limits mid-experiment | Medium | `rate_limit_event` is an anomaly class; affected runs are voided and re-run |
| The frozen fixture leaks its answer through pattern familiarity | Medium | Practice check (b) requires the file to have been read before it is reported |
| Scope creeps into a framework and no number ever lands | Medium | Staged delivery: tier-1 cell to `theory/` before expansion |
| The rig becomes citable and is itself unverified | Medium | ADR 0010 already names this; `theory/loops/reading-and-running-find-different-defects.md` applies to the rig, including that its fixtures can lie about what they ran |
| Undocumented on-disk transcript format used as the source | Low | `stream-json` is the contract; the on-disk transcript is a cross-check only |

## Tradeoffs rejected

| Rejected | Reason |
|---|---|
| `--allowedTools` as the scoping mechanism | Measures nothing and looks like it worked: 54 → 54 names, identical cost to the cent |
| `--output-format json` | Final aggregate only. Wrong-tool counting needs the per-call transcript |
| Practice as advisory only | Rejected by the operator: misuse must count toward failure |
| Practice folded entirely into one binary | Destroys the resolution the experiment exists to produce. Both demands are met by the four-cell table plus the graded count |
| Build the reusable rig first | The failure mode this repo already has |
| N = 1 or N = 3 per cell | ADR 0010 constraint 3. A single-run difference is noise rendered as a chart |
| Five categories × three tiers | Fifteen deterministic verifiers before the first number. Guarantees a relaxed grader |
| Wall clock as a cost proxy | Recorded to notice a rig that got slower. Never a cost figure |
| An adapter into an existing performance tool | Different domain. Take its discipline, not its schema |

## Rollback plan

Nothing in `theory/` changes until a result exists, so rollback before that point is deleting the new
rig directory — no committed truth is touched. After the `theory/` write, revert that single commit;
the ADR, this proposal and the exploration stay, because the attempt is provenance. Fixtures are
additively versioned, so rollback never mutates a frozen version.

## Success criteria

- [ ] A number exists for the single question above, with spread, and it is written into `theory/`
- [ ] The four-cell table and the off-set-call distribution are published per arm — not a single mean
- [ ] The pre-registered branch that fired is stated explicitly, including if it narrowed or rejected
- [ ] The instrument-anomaly log is published with the result, with X = 3 shown as not breached
- [ ] Every run record carries prompt-byte hash, `init.tools` read back from the run, and fixture version
- [ ] No arm used `--allowedTools` as a scoping mechanism
- [ ] Both checkers were written before their prompts, and it is provable from commit order
