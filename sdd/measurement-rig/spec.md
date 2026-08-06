---
id: sdd/measurement-rig/spec
type: journal
targets: [any]
status: draft
verified: 2026-08-06
sources: ["sdd/measurement-rig/proposal.md", "decisions/0010-measurements-vary-the-harness-not-the-model.md", "sdd/measurement-rig/exploration.md", "theory/agents/tool-surface-design.md", "AGENTS.md", "sdd/testing-capabilities.md"]
---

# tool-surface-experiment — Specification

SDD spec phase for `measurement-rig`. Requirements and scenarios only — no storage schema, no
driver language, no file layout (those are `sdd-design`). No test runner exists in this repo
(`sdd/testing-capabilities.md`); verification below is transcript inspection, never "run the tests."

## Purpose

Define, before any run, the fixture tasks, tool-name sets, outcome/practice checkers, the four-cell
classification, void rules, the sample-size rule, and the pre-registered falsification conditions for
the BROAD (54 visible tools) vs SCOPED (3: `Glob`, `Grep`, `Read`) comparison named in the proposal.

## Requirements

### Requirement: Frozen fixture tasks, tiered by tool-interaction count

The system MUST define exactly three defect-finding tasks over a frozen fixture directory
(`fixtures/v1/<tier>/`), each shipping an **answer key** (path:line pairs of the seeded defect) and a
**verifier**, both authored before the task's prompt (ADR 0010 constraint 1). Fixture content below
names the defect's functional shape and location precisely enough to build it; literal source text is
a design/tasks deliverable.

| Tier | Fixture | Defect shape | Tool interactions needed |
|---|---|---|---|
| 1 | One file, `paginate.js`, a `pageSlice()` helper plus 2-3 unrelated correct helpers | Off-by-one boundary in the slice start index | One `Read` of a named file |
| 2 | `src/` with 4-5 files; one (`utils/date.js`) has the defect, distractors are correct | Timezone/boundary off-by-one in a date formatter near midnight | Search across files (`Grep`/`Glob`), then `Read` the located file |
| 3 | Three files: `handlers/checkout.js` (call site, correct), `lib/pricing.js` (root cause), `lib/pricing.contract.md` (stated tier boundaries) | Boundary condition (`>` vs `>=`) in a discount function reached via a call chain | Trace call chain across files, cross-check contract doc — multiple `Grep`/`Read` |

Exact prompts:

- **Tier 1**: "Read `fixtures/v1/tier1/paginate.js` and report every defect that causes `pageSlice` to
  return the wrong items. Report each defect as one line in the exact format
  `<relative-path>:<line-number>`, one per defect, and output nothing else in your final message."
- **Tier 2**: "Under `fixtures/v1/tier2/src/` there is a date-formatting function with a boundary
  defect that returns the wrong calendar day for inputs near midnight. Find the file and report the
  defect as one line in the exact format `<relative-path>:<line-number>`. Output nothing else in your
  final message."
- **Tier 3**: "A customer reports checkout totals are wrong for orders that land exactly on a
  discount-tier boundary. Starting from `fixtures/v1/tier3/src/handlers/checkout.js`, trace the call
  chain to the function that computes the discount, and cross-check the intended boundaries in
  `fixtures/v1/tier3/src/lib/pricing.contract.md`. Report only the file and line of the actual defect,
  as one line in the exact format `<relative-path>:<line-number>`. Output nothing else in your final
  message."

Verifier (identical shape, all tiers): parse the final assistant text for lines matching
`^[\w/.\-]+:\d+$`; a run's **outcome** is `pass` iff that line set is exactly equal to the task's
answer key (no extra line, no missing line, no near-miss line number); otherwise `fail`.

#### Scenario: Tier-1 outcome passes

- GIVEN the tier-1 fixture and its answer key naming one defect line
- WHEN the run's final text contains exactly `fixtures/v1/tier1/paginate.js:<seeded-line>` and nothing else
- THEN outcome is `pass`

#### Scenario: Tier-3 outcome fails on a near-miss line

- GIVEN the tier-3 answer key naming the defect line inside `lib/pricing.js`
- WHEN the run reports the correct file but a different line number
- THEN outcome is `fail` — line number is part of the exact-match set, not advisory

### Requirement: Tool-name sets per task and arm

The system MUST define three disjoint tool-name sets per task, identical across arms except for
visibility: `expected` (proper subset of the SCOPED surface), `off-set` (visible and permitted, not
expected, must be non-empty in both arms), `forbidden` (removed from SCOPED via `--disallowedTools`;
merely unblocked-but-judged in BROAD, which uses no scoping flag).

| Task | Expected | Off-set | Forbidden (mechanism) |
|---|---|---|---|
| Tier 1 | `{Read}` | `{Glob, Grep}` | Every other tool name. SCOPED: invisible via `--disallowedTools` naming all built-ins except `Glob/Grep/Read` plus every connected MCP tool name (25 servers stay connected). BROAD: visible, no flag, judged only by the practice check |
| Tier 2 | `{Grep, Read}` | `{Glob}` | Same as above |
| Tier 3 | `{Grep, Read}` | `{Glob}` | Same as above |

`--allowedTools` MUST NOT be used as a scoping mechanism (verified: no visibility effect, 54→54).
`--strict-mcp-config` MUST NOT be used (verified: drops `mcp_servers` 25→0, a second variable).

### Requirement: Four-cell outcome/practice classification

The system MUST classify every run into exactly one of four cells and MUST publish all four per arm —
`improper-success` MUST NEVER be merged into `pass` or into plain failure.

| Outcome | Practice | Cell | Counts as |
|---|---|---|---|
| pass | pass | `proper` | Pass |
| pass | fail | `improper-success` | **Fail** |
| fail | pass | `clean-failure` | Fail |
| fail | fail | `failure` | Fail |

#### Scenario: Improper success is not a pass

- GIVEN a run whose final text exactly matches the answer key (outcome pass)
- WHEN the transcript contains a `tool_use` naming a tool in that task's `forbidden` set, or a reported
  defect's file has no earlier `Read`/`Grep` naming it
- THEN the cell is `improper-success` and the run counts as a failure, published as its own row

### Requirement: Practice-check evidence rule

Practice passes iff (a) no `tool_use.name` in the transcript is in the task's `forbidden` set, AND (b)
every reported defect's file appears in an earlier `Read` or `Grep` `tool_use` in the same transcript,
checked file-level only (the specific line is not required to match).

- **Read match**: `tool_use.name == "Read"` and its resolved `file_path` equals the reported path.
- **Grep match**: `tool_use.name == "Grep"` and either its `path`/glob input targets that file, or the
  paired `tool_result` (by `tool_use_id`) lists that path among matches.
- Order is transcript-sequential: the matching `tool_use` MUST occur before the final report.

#### Scenario: File read, defect reported for a different file

- GIVEN the transcript has an earlier `Read` of `utils/format.js` only
- WHEN the final report names a defect at `utils/date.js:12`
- THEN condition (b) fails for that line (the read of `format.js` does not satisfy it) and practice is `fail`

### Requirement: Run validity and voiding

A run is **void** — excluded from the cell and replaced by a fresh run at the same (task, arm) — only
for a mechanical anomaly: `init.tools` mismatch against the intended surface, prompt-byte-hash
mismatch, missing/unparseable `result` event, wall-clock timeout (~300s, calibrated on the tier-1
pilot) with no `result` event, `stop_reason != "end_turn"`, `permissionMode` differing across a paired
run, or a `rate_limit_event`. A **failed** run (any non-`proper` cell) is retained permanently and is
never re-run to replace it. A run MUST NOT be voided because the model performed the task poorly.

#### Scenario: Timeout vs. task failure

- GIVEN two runs, one killed by the wall-clock timeout with no `result` event and one that completed
  with a wrong final report
- WHEN classifying both
- THEN the first is void and replaced; the second is `failure` (or another non-`proper` cell) and counted

### Requirement: Sample size and variance-driven N

Each (task, arm) cell starts at N=5 (30 runs total; the tier-1 cell's 10 runs — 5 BROAD + 5 SCOPED —
run first as the shakedown). N is never chosen a priori beyond that floor (ADR 0010 constraint 3
rejects N=1, N=3).

| Observed spread after N=5 | Action |
|---|---|
| All 5 runs land in the same cell AND off-set+forbidden count range ≤ 1 | Stop at N=5 |
| Cell classification is mixed across the 5, OR off-set+forbidden range ≥ 2 | Add one batch of 5 (N→10); if still mixed/range≥2, add one more (N→15, cap) |

Report the final N per cell together with the observed min/max range — never a mean alone.

### Requirement: Pre-registered falsification conditions

| Condition (over 15 runs per arm) | Verdict |
|---|---|
| SCOPED `proper` exceeds BROAD by ≥ 4, non-overlapping per-task min/max in ≥ 2 of 3 tasks, AND BROAD median off-set+forbidden ≥ 1 | **Supports** — write a measurement into `theory/agents/tool-surface-design.md`'s "what would sharpen it" section |
| Difference ≤ 1, OR BROAD median off-set+forbidden = 0 | **Narrows** — write that the lever is undetectable on this task class |
| BROAD `proper` exceeds SCOPED | **Contradicts** — mark the relevant sentence `rejected`, never delete |

Exactly one branch fires and the write MUST name which one, with the four-cell table, the off-set
distribution, and the anomaly log attached.

### Requirement: Instrument-doubt threshold

X = 3 runs exhibiting the same anomaly class (`init.tools` mismatch, prompt-byte-hash mismatch,
missing `result` event, unparseable stream, timeout void, `permissionMode` mismatch, `rate_limit_event`)
within one experiment MUST trigger an investigation before any `theory/` write. A refuting result
(BROAD ≥ SCOPED) produced with a clean anomaly log MUST NOT be attributed to the instrument. The
anomaly count MUST be published alongside the result.

## Non-Goals

| Excluded from v1 | Why |
|---|---|
| Model-vs-model comparison | ADR 0010 defers it |
| Reusable benchmark framework/CLI/DB | Consequence, not the goal |
| LLM-as-judge / probabilistic grading | ADR 0010 rejects it |
| Code-planning tasks | No deterministic verifier exists |
| Delegated-vs-inline, resident-vs-deferred experiments | Same rig, later |
| Levers 1 (descriptions) and 2 (splitting/renaming) | Only lever 3 (scoping) is under test |
| `--bare` + API key | Real goal, not v1's |
| A test runner | None exists in this repo |
| Cost as a headline finding | ~9% delta; caching confounds it |

## Amendment 1 — adopted from `gentle-ai/bench`, 2026-08-06

Six requirements added after reviewing the `bench/` harness in the public `gentle-ai` repository, which
solves several of these problems in production with a real incident behind each rule. Recorded as an
amendment rather than folded in, so the provenance of each rule stays visible.

**Not adopted, because it was already handled:** the answer-key leak. A first reading of the bench rule
*"the agent must not read the source… the run comes out clean for the wrong reason"* looked like a hole
here. It is not — the design already materializes the run's workspace as a copy of `src/` only, outside
the repository, with `answer-key/` never inside cwd. Recorded because the near-miss is instructive: a
rule imported from another harness was almost written up as a local defect without checking the local
artifact first.

### R-A1.1 Three run states, and an exit contract that distinguishes them

A run is `completed`, `void`, or `failed`, and the runner's exit code must separate them:

| State | Meaning | Exit |
|---|---|---|
| `completed` | Produced numbers. May be a pass or a fail — both are results | 0 |
| `void` | Could not produce numbers for an environmental reason (timeout, rate limit, non-`end_turn` stop, missing transcript). Excluded and replaced | 0 — a void is a designed outcome |
| `failed` | The harness itself could not build or prove its fixture, or an assertion fired | **non-zero** |

The rationale is not symmetry, it is a filed bug: `gentle-ai` issue #1883 found a benchmark run that
reported failed journeys and still exited 0, so a CI gate reading the exit saw success in a run that
measured nothing. **The results file must be written before the non-zero exit**, so the evidence survives
the failure.

This mirrors `hooks/pre-commit`'s own 0/1/2 contract, which is house style here for the same reason.

### R-A1.2 Aggregate only over the comparable subset

Totals are computed over **iteration slots that completed in both arms**. A slot void in BROAD and
completed in SCOPED contributes to neither.

Excluded slots must be **named in the output**, never silently dropped. Summing unequal Ns produces a
delta that reads as an effect when it is only a difference in how many runs survived — and since voids
are not expected to distribute evenly between a 54-tool arm and a 3-tool arm, this is a live risk here
rather than a theoretical one.

### R-A1.3 No composite score, ever

The four cells, the off-set distribution and the token/cost figures are reported **separately**. No
weighted sum, no single "quality" number, no ratio that collapses them.

The reason, which `gentle-ai/bench` states from experience: a weighted sum can improve while the worst
component gets worse, so collapsing the dimensions hides exactly the regression that matters most. Here
the specific hazard is that `improper-success` could rise while the composite improves.

### R-A1.4 Every detector must be proven able to fire

A check that cannot fail makes the passing case a tautology. So for each detector the rig relies on,
the suite must contain a case that **makes it fire**:

- The negative control (BROAD flags declaring the SCOPED digest) must void `surface-mismatch`. **It is
  not enough that it is specified — it must be run and observed to void.** If it does not fire, nothing
  may be written to `theory/`.
- The practice check must have a case where a reported defect's file was never read, and that case must
  be classified `improper`.
- The off-set detector must have a case where an off-set tool is called, in **both** arms.

This is the zero-by-construction trap the proposal caught, generalised into a standing requirement.

### R-A1.5 Wall clock is a bound, never a comparative dimension

The timeout exists to void runaway runs. Elapsed time must **not** be reported as a measured difference
between arms, because it is dominated by provider-side variance and is not comparable between two runs
of the same configuration, let alone two configurations. `gentle-ai/bench` excludes it outright for this
reason; here it is retained solely as a voiding mechanism and is barred from the comparison.

### R-A1.6 Honesty contract — the known gaps ship with the result

The result must be published with a numbered list of its own limitations, on the principle that a
benchmark which quietly invents a metric is worse than one that admits a gap. At minimum:

1. **Ambient context is a constant, not eliminated.** ~26k tokens per run of `CLAUDE.md` discovery,
   hooks, plugins and auto-memory are present in both arms. Identical across arms, so a difference is
   still attributable — but the absolute numbers are not portable to another machine.
2. **One machine, one model, subscription auth.** Not reproducible elsewhere without `--bare` and an
   API key.
3. **Synthetic fixtures.** Per the RDD rule that synthetic proxy coverage never proves another runtime,
   this result may **not** be extrapolated to real repositories without saying so.
4. **Small N.** The variance rule sets the floor; the spread ships with every figure and no figure ships
   without it.
5. **`num_turns` is a proxy for effort**, not a measurement of work done.
6. Any anomaly class observed during the run, with its count, per the pre-registered X = 3 rule.

### R-A1.7 Negative controls are inventoried per flow

Adopted from the RDD defect workflow, which requires inventorying every flow with *"entry, mode,
environment, expectation, and negative controls"*. One rig-wide negative control is not sufficient:
**each task declares its own**, so a task whose detector never fires is visible per task rather than
hidden behind a suite that passed overall.
