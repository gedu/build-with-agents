---
id: sdd/failure-flood-triage/proposal
type: journal
targets: [any]
status: draft
verified: 2026-08-11
sources: ["decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0012-a-hypothesis-is-never-citable.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "sdd/failure-flood-triage/exploration.md", "sdd/measurement-rig/proposal.md", "sdd/measurement-rig/spec.md", "sdd/measurement-rig/verify.md", "rig/README.md", "rig/run.sh", "rig/derive.py", "hypotheses/README.md", "theory/llm/context-degradation-at-length.md", "OPERATIONS.md", "skills/hypothesis-cycle/SKILL.md", "skills/source-verdict/SKILL.md"]
---

# failure-flood-triage — proposal: which lever owns the runway

SDD proposal phase for `failure-flood-triage`. Intent, scope, approach. No spec, no design, no code.

Bounded by ADR 0010 (five non-negotiable constraints), ADR 0011 (evidence, not truth), ADR 0012
(pre-registration), ADR 0013 (a committed executable carries its own test), and by
`sdd/failure-flood-triage/exploration.md`.

## Intent

An engineer spent more than 90% of a token budget trying to fix roughly three thousand failing tests
one at a time. A colleague proposed a cheaper model tier as the remedy. Both moves are guesses, and
this repo has no evidence that decides between them.

The two explanations are not variations on a theme — they name different levers and imply opposite
fixes.

| Explanation | Implied fix | What it costs if wrong |
|---|---|---|
| The tokens went into **context**: a failure flood read serially, re-sent every turn | Change the harness shape — cluster first, diagnose from clusters, apply mechanically | A team re-architects its workflow for nothing |
| The tokens went into **price per token**: the model tier was too expensive | Switch tier | A team keeps the shape that burns the budget and buys a cheaper way to burn it |

The second explanation cannot be right about the quantity that actually ran out. A tier change lowers
cost per token; it does not lower how many tokens enter context. `theory/llm/context-degradation-at-length.md`
is `status: validated` here and states the mechanism — an attention budget spent as context grows —
so occupancy is not only a spending question, it is a quality question. That makes the harness
explanation testable and the tier explanation, as stated, close to a category error.

Three business costs follow from not knowing.

| Cost today | Consequence |
|---|---|
| The advice given in the moment was "change the model" | The most expensive kind of wrong answer: plausible, cheap to say, and it leaves the burn in place |
| Nobody can say *by how much* a triage harness helps | An unquantified recommendation is discounted to taste, or applied where it does nothing |
| The prior rig cycle closed `PARTIAL` — cost verified, quality never shown to work | `sdd/measurement-rig/verify.md`: *"the rig is a verified cost instrument and an unverified quality instrument"*. That gap is recorded and open |

That last row is why this experiment is worth funding rather than merely interesting. `verify.md` names
exactly what would close it: *"One fixture generation in which a completed run can fail cleanly — a
task class with no single right answer, where recall and precision can genuinely diverge between
arms."* A broken-test flood with several root causes is that class, because **partial credit exists**:
four of six clusters fixed is a real, deterministic, intermediate outcome. Every fixture the rig has
run so far had one right answer and classified `proper` 12 of 12 in both arms. This is the first task
class that can produce a clean failure at all.

## The single question v1 answers

> **On one failure flood, with the model held fixed, does splitting triage into collect → diagnose →
> apply change how correctly the root causes are identified, how much of the suite is restored to
> green, the peak context occupancy a run reaches, and the cumulative tokens it consumes — compared
> with one agent doing all three serially?**

One variable: the **harness shape** — how many model invocations there are and what each one is shown.
Everything else is held fixed and recorded.

| | Arm MONOLITHIC | Arm PIPELINE |
|---|---|---|
| Model invocations | 1 | 2 — diagnostician, then applier |
| Non-model steps | none | collector, plain code, zero model tokens, invoked K times |
| What sees raw suite output | the single agent, directly | nothing. Only normalized clusters with counts and one representative per cluster |
| Intermediate artifact | none | one fix-plan file on disk, written by the diagnostician, read by the applier |
| Model id | fixed | identical |
| Visible tool surface | one committed preimage | **the same preimage, for every role** |
| Fixture bytes | frozen v1, MANIFEST-checked | identical |
| Prompt bytes | frozen, hashed | frozen, hashed per role |
| Test files | read-only substrate, hash-checked | identical rule |

**The tool surface must be identical across arms and across roles.** Narrowing the applier's tools
would be a second variable and would confound this with the scoping experiment the repo already ran.
The pipeline's advantage, if it exists, must come from *what is placed into context*, not from a
smaller toolset.

Both arms need `Bash` (to run the suite) and a write tool (to fix code). `rig/run.sh` disallows `Bash`
in **both** arms unconditionally, and its stated reason is local to its own experiment: `Bash` subsumes
`Glob`/`Grep`, and those tasks only *reported* defects. Here execution is the point. A new surface
preimage must therefore be captured and committed under `rig/surfaces/`, per the standing rule that
the disallow list is a committed file and never a constructed string.

### The zero-by-construction guard

PIPELINE's peak occupancy is low **by construction** — the diagnostician is defined as never seeing the
raw flood. That floor is not a finding and must not be reported as one. This is the same trap the
sibling proposal caught with `--allowedTools`: a design that cannot fail in the direction it wants.

The non-trivial quantities are: what MONOLITHIC's peak actually reaches (not fixed by construction),
whether PIPELINE's green-restore holds up *despite* the narrower view, and whether PIPELINE's extra
invocations and re-collections make its **cumulative** total worse even while its peak is better.

## Two deterministic checkers, stated before the prompt (ADR 0010 constraint 1)

The operator's ruling: **both** outcome channels are checked, as separate tables. Diagnostic quality is
the primary channel; green-restore is a mandatory companion. The reasoning is the point, so it is
recorded rather than summarised:

| Why both | Detail |
|---|---|
| The expensive checker had to be written anyway | Cluster attribution against the measured answer key **is** the diagnostic checker. It is required whichever channel leads, so it is not a marginal cost |
| Green-restore is a near-free byproduct | The collector already produces the pass/fail counts. The marginal cost is the comparison, not a new instrument |
| Proving green-restore can fire is free too | Hardening item 4 already mandates validating that every injection produces its expected signature. That validation **is** the `R-A1.4` proof that the green channel can fail cleanly |
| The deciding factor is this change's own risk 1 | `rig/derive.py` discarded per-turn usage, and that turned out to be the primary runway metric. **A channel not recorded cannot be retro-derived without the raw captures.** Record both now |

Neither "restored to green" nor "diagnosed correctly" is self-evident, and a loose reading of either
would hand the run several ways to cheat. Both checkers are authored and committed **before** the
prompts — provable from commit order, the convention the prior cycle already established.

**Measured baselines, frozen into `answer-key/`.** Not the declared injection list:

1. `C` — the collected test identifier set on the **clean** fixture, which must have **zero**
   failures. A non-zero clean baseline voids the fixture, not the run.
2. `F0` — the observed failure set after injection, normalized. Measured, then frozen.
3. `S0` — the suite state after injection: `ran`, `did-not-start`, or `partial`.
4. `R0` — the root-cause label attached to every member of `F0`, established by the per-injection
   isolation validation (item 4) rather than asserted. This is what makes `F0` a **clustered** key,
   and it is what makes the diagnostic channel measurable at all.

### Primary channel — diagnostic attribution

Both arms MUST emit a root-cause report in a strict line format alongside their fixes, or the channel
is unmeasurable in the arm that has no fix-plan artifact. The exact format is a spec deliverable; the
requirement is that it be exact-match parseable — the same device the prior experiment used to make its
verifier deterministic.

Scored against `R0`, per run: **precision** = correctly attributed causes ÷ causes claimed;
**recall** = correctly attributed causes ÷ causes present in `F0`. Reported as the pair, never as an
F-score — a single blended figure is exactly the composite `R-A1.3` forbids.

**Why this is not the code planning ADR 0010 forecloses.** Constraint 1 excludes planning because
*"there is no deterministic grader for a plan."* This does not grade a plan's quality; it compares a
claimed cause set against a **measured** key by exact match. That is the same shape as the prior
experiment's `<path>:<line>` set equality, and it is deterministic for the same reason. Grading whether
the fix-plan was *well written* stays excluded.

### Companion channel — green-restore

**Post-run verdict**, four values, no composite:

| Verdict | Condition |
|---|---|
| `green` | suite `ran`, observed failures empty, and the integrity guard passes |
| `partial` | observed failures a strict, non-empty subset of `F0`, no regression |
| `no-progress` | observed failure set equals or exceeds `F0` |
| `regressed` | any test failing that passed in `C`, or the integrity guard fails |

**The integrity guard is the load-bearing half.** It fails if the collected identifier set differs from
`C` (a test was deleted, renamed or skipped) or if any test file's bytes changed. Test files are
read-only substrate; `rig/run.sh` already carries a verified instrument for exactly this — a file-list
hash taken before and after, with mutation forced to state `failed` — and that instrument is reused
rather than reinvented. Source files, unlike in the prior experiment, must be writable.

Partial credit is what makes this the first task class the quality channel can actually exercise.

## Metric channels, and the rule that they are never summed

Five recorded channels on three axes. Several are primary, and that is the repo's existing shape rather
than an evasion — `R-A2.2` already established that two channels may both be primary and that neither
may be demoted once the result is known.

| Channel | Axis | Definition | Status |
|---|---|---|---|
| **Diagnostic attribution** | outcome | precision and recall of claimed causes against `R0` | **Primary.** The channel `verify.md` says has never been able to fail cleanly |
| Green-restore | outcome | the four-value verdict above, per arm, as a distribution | Mandatory companion, always published |
| **Peak occupancy** | runway | per invocation turn, `input + cache_read + cache_creation` tokens; the run's value is the **max** over turns | **Primary** on the runway axis |
| **Cumulative tokens** | runway | the **sum** of the same quantity over all turns, plus output | Primary, distinct from peak |
| Dollar cost | cost | `total_cost_usd` | Secondary. Never the headline |

**The two axes are what stop a degenerate win from hiding.** A pipeline that lowers occupancy by giving
up early produces a good runway table and a bad outcome table, and that disagreement stays visible
precisely because the tables are never collapsed into one score.

The two runway channels share a unit, which is precisely why summing them is tempting and wrong:
one catastrophic early read can poison every later turn (high peak, and cumulative inflated by
re-sending it), while many small turns give a low peak and a high cumulative. They are different
failure modes. No composite score, ever — the standing rule, `R-A1.3`.

**Peak occupancy is a measured proxy, not a direct read.** The CLI exposes no "context window used"
field. The window is a constant across arms, so a delta is attributable; the absolute number is a
proxy and ships labelled as one.

**Verified, not assumed:** the current row schema keeps only the final `result` event's four usage
fields, so peak occupancy is **not derivable from `runs.jsonl` today**. It *is* derivable from the raw
capture: a sampled existing run carries 14 `assistant` events and 15 occurrences of
`cache_read_input_tokens`, i.e. per-turn usage is present and `rig/derive.py` currently walks those
events for tool calls while discarding their usage. Consequence: the peak-occupancy detector can be
proven able to fire (`R-A1.4`) by retro-deriving it over the 42 already-paid-for captures of the first
experiment, **before a single failure-flood run is funded**. That work is a schema addition to the
existing experiment and is independent of everything else here.

## Two pre-registered hypotheses (ADR 0012)

One per primary channel — two, not one composite, because the channels are separately falsifiable.
Both are **statistical** in form, so per `skills/hypothesis-cycle` no single pair supports or refutes
either; they need N and spread. The files are a later phase's deliverable; they must exist before any
run.

**`hypotheses/0002-pipeline-shape-lowers-peak-occupancy.md`**

- Claim: on a failure flood, the three-role pipeline reaches a lower peak per-turn occupancy than one
  agent doing the same work serially.
- Support: over stage-2 completed pairs, median PIPELINE peak ≤ 0.5 × median MONOLITHIC peak, with
  non-overlapping min/max ranges between arms.
- Refute: the ranges overlap, or PIPELINE's median peak is ≥ MONOLITHIC's.

**`hypotheses/0003-serial-triage-compounds-cumulative-tokens.md`**

- Claim: serial triage consumes more cumulative tokens than the pipeline, because an early flood read
  is re-sent on every subsequent turn.
- Support: median PIPELINE cumulative ≤ 0.6 × MONOLITHIC's, ranges non-overlapping.
- Refute: PIPELINE's median ≥ MONOLITHIC's — a live possibility, since the pipeline pays for its own
  re-collections and for threading a plan.

Neither outcome channel is a third hypothesis. Diagnostic attribution and green-restore are the
deterministic verdicts ADR 0010 constraint 1 requires, and both are published as companion tables with
either resolution. That is what stops a degenerate win — a pipeline that lowers occupancy by giving up
early — from hiding inside an `AND`.

**Detectable at the affordable N?** (`skills/hypothesis-cycle` Step 1, check 4.) A 2× peak ratio is
comfortably above the run-to-run spread the first experiment observed; a ratio under about 1.3× is
**not testable at this budget** and must be reported that way rather than as a number. The 0.6
cumulative constant is the weaker of the two and should be re-derived from the stage-1 shakedown
**whose rows are excluded from the stage-2 test** — that exclusion is declared here, now, so the
re-derivation is not post-hoc metric selection.

## The seven hardening requirements, checked against the repo

The exploration agent could not retrieve these. Each is checked below rather than restated as settled.
Two conflict with existing convention and are corrected.

| # | Requirement | Repo coverage | What follows |
|---|---|---|---|
| 1 | Breakage must be baked in as ordinary code; no reachable ground truth, or the agent reads a diff instead of diagnosing | **Already covered.** The runner materializes a flat copy of `src/` contents into a temp directory outside the repo — no `.git`, no `answer-key/`, nothing to walk up to | Reproduce that materialization exactly. **It re-opens if the applier is given `git apply`**: a repo implies history. Applier edits files directly; no patches, no git |
| 2 | Ground truth = **measured** observable failures, never the declared injection list | **Partially covered.** The freeze machinery and the answer-key-before-prompt commit order hold a measured key exactly as well as a declared one, but nothing in the convention *requires* the key be measured | New spec rule. Measure, then freeze, then author the prompt — order preserved, so constraint 1 still holds |
| 3 | Collector needs three states: tests failed / suite did not start / partial run | **Partially covered, and it collides.** `R-A1.1`'s three run states (`completed`/`void`/`failed`) are a proven precedent, but that is the *run* axis, not the *suite* axis. A config injection deliberately produces "suite did not start" — which the void machinery would discard as environmental, throwing away the interesting case | Spec must separate them explicitly: a non-start **caused by the frozen injection** is a measurement; one caused by a missing toolchain is a void. Telling them apart is the collector's job |
| 4 | No injection enters the corpus until validated in isolation against the clean fixture | **Already covered in principle.** This is `R-A1.4` — *"every detector must be proven able to fire"* — applied to injections. The repo has already applied it recursively | Restate in the injection domain. Note the "drop a required prop" vector is moot: fixture v1 has no React Native, per settled scope |
| 5 | Clean fixture must be zero-failure; the normalizer must be deterministic and **"needs its own tests"** | **Conflicts.** There is no test runner here **by decision** (ADR 0013, `OPERATIONS.md`). "Its own tests" cannot mean a suite | ADR 0013 supplies the shape: `--self-test` as a flag on the normalizer itself, the pattern already load-bearing in `derive.py`. The zero-failure precondition is a fixture-freeze gate, not a test |
| 6 | Per-role token cost, and success as a **double criterion**: green AND applier under budget | **Partially covered, and the double criterion must be rejected as stated.** Per-run token recording is constraint 5 and exists; per-*role* within one run is new. But ANDing green with a budget into one success flag is a composite score, which `R-A1.3` forbids and which the primary-metric split independently forbids | Keep the intent, drop the `AND`. Report green-restore, peak, and cumulative as three separate channels. A row becomes per-pipeline-run with per-invocation sub-records |
| 7 | The plan ages at the first fix; the applier must re-collect after each cluster | **Open.** Nothing in the repo addresses it | Specify before the run, never adapt mid-flight. Note re-collection *is* the quantity under test: it grows the applier's context. Do **not** hold collector-invocation count equal across arms — that count is part of the harness, and the harness is the variable |

No item conflicts with ADR 0010's five constraints. Items 5 and 6 conflict with **other** repo
conventions (ADR 0013; `R-A1.3`), and both are resolved above in the repo's favour.

## Scope

### In scope

- `rig/fixtures/failure-flood/v1/` — frozen, MANIFEST-hashed, additively versioned. Jest + TypeScript,
  no React Native. The donor audit bounds feasibility: 138 RN-free cases against a 50-case stage-2
  target, ~2.7× headroom.
- Both arms emit a root-cause report in a strict, exact-match line format, so the primary channel is
  measurable in the arm that has no fix-plan artifact.
- Staged: **stage 1** = 10 failing cases from 3 root causes, shakedown, rows excluded from the stage-2
  test. **Stage 2** = 50 failing cases from 6 root causes, the actual comparison.
- A **sibling runner**, e.g. `rig/run-pipeline.sh`, alongside `rig/run.sh`. `run.sh` is **not**
  refactored: its cost instrument is verified, and refactoring risks invalidating that verification.
  Decision 1 is also confirmed by evidence — `run.sh`'s unconditional `Bash` disallow is load-bearing
  for its own experiment and must not move.
- A collector and a signature normalizer, in `python3`, each carrying `--self-test` per ADR 0013.
- `derive.py` and `report.py` parameterized **only** as far as needed to read both experiments, plus
  the peak-occupancy and cumulative channels and the four-value verdict.
- Two hypothesis files, registered before any run.
- Domain-neutral schemas: `failure`, `signature`, `cluster`, `fix-plan`. No tool name in a schema name.
- One `OPERATIONS.md` prerequisites entry for the new toolchain.

### The fixture carries real, author-authorized code

The committed fixture **may** contain real donor module code. The operator is the author and owner of
that code and authorized copying it here, after being shown the cost in plain terms: private-project
code becomes public, the product domain becomes visible from it, and **the irreversible point is the
push, not the commit.** That authorization is on record.

It covers the operator's own source code and nothing else. Every other part of ADR 0009 still binds
without exception — no absolute path, no project name, no client or employer name, no person's name, no
token, no hostname. The gate cannot pattern-match the bare-word class, so that half stays a judgment
call regardless of a clean run.

### Out of scope — named as clearly as the goals

| Not doing | Why |
|---|---|
| A React Native component fixture (v2) | Additive versioning exists for exactly this. v1 first |
| A `tsc` or lint collector | The next collector, documented, not built. Schemas stay domain-neutral so it costs almost nothing later |
| Varying the applier's model tier | ADR 0010 holds the model fixed. This is the second experiment, same rig, different fixed value |
| Refactoring `rig/run.sh` | Its verification is the asset. A generalized runner is deferred until two experiments exist and the shared shape is actually known, rather than guessed from one |
| Validating against a real project checkout | Staged deliberately: the frozen-fixture comparison first. If it happens later the workspace path is read from local config and never committed — the source-code authorization does not touch the no-absolute-path rule |
| A repo-level test runner | ADR 0013 decided against one. The fixture ships its own suite; that suite is fixture content, not this repo's runner |
| Dollar cost as the headline | Secondary by decision. Reported, never the lead |
| A composite success score | `R-A1.3`. Three channels, three tables |

## Capabilities

This repo uses no `openspec/specs/` tree, so these name spec-phase deliverables.

**New** — `failure-flood-experiment`: arms, roles, fixture and injection contract, the measured
answer-key rule, the three suite states, the four-value verdict and its integrity guard, the two
occupancy channels, per-invocation records, void rules, staging.

**Modified** — `rig/README.md` (a second experiment; the layout's experiment axis becomes real),
`MAP.md` (experiment count), `OPERATIONS.md` (prerequisites), the existing row schema (one additive
bump for the occupancy channels, re-derived over existing rows unchanged).

## Approach

Six chained PRs, approved by the operator in this order, which puts the cheapest thing that could
invalidate everything first.

| # | Slice | Why here |
|---|---|---|
| 1 | Peak-occupancy retro-derive over the 42 already-paid-for captures | Risk 1 proved the primary runway metric was **not** derivable from `runs.jsonl`. This proves the detector can fire on data already paid for, before funding any new run. If it cannot be derived, nothing else has been spent |
| 2 | Collector + signature normalizer, each with `--self-test` | The normalizer's determinism gates every cluster count downstream, and the collector's pass/fail counts are what make green-restore near-free |
| 3a | Clean fixture, proven zero-failure | A non-zero clean baseline corrupts all scoring. Prove it before injecting anything |
| 3b | Injections, each validated in isolation, then the measured `F0`/`R0`/`S0` key, then the freeze | Item 4's validation is simultaneously the `R-A1.4` proof that the green channel can fail cleanly |
| 4 | `rig/run-pipeline.sh` plus the new committed surface preimage under `rig/surfaces/` | Both arms need `Bash` and a write tool, which `run.sh` disallows unconditionally and must keep disallowing |
| 5 | The two hypothesis files, the `OPERATIONS.md` prerequisites edit, and the report changes | Pre-registration and the reporting tables land together, before the first countable run |

**A pre-registration guard, because this ordering makes it non-obvious.** ADR 0012 requires the
hypotheses to exist before any run that could settle them, and they land in slice 5 — after the runner.
That is compliant only because nothing before it produces a countable row: slices 1–3 measure existing
captures and the fixture itself, and slice 4's shakedown runs under `--dirty-ok`, which stamps
`void_reason=dirty-tree` and is structurally uncountable. **No countable run may execute before slice 5
lands.** Stated here so the constraint is mechanical rather than remembered.

## The toolchain gap, and whether it needs an ADR

Node, npm and Jest are authorized **nowhere**. `OPERATIONS.md`'s prerequisites table names `bash`/`git`,
`python3`, the `claude` CLI, and `gentle-ai`; ADR 0011's boundary section names `python3` and a
GNU-compatible `timeout` as the rig-only exemptions from the hook's "installed nothing" contract. (The
table omits `timeout` entirely — a small pre-existing gap, worth fixing in the same edit.)

Proposed resolution: **two** `OPERATIONS.md` prerequisites rows in one edit, in slice 5. Node and npm,
needed for `rig/fixtures/failure-flood/*`, **rig-only and fixture-only**, with `node_modules/` installed
on demand and already covered by the existing blanket ignore, so no `.gitignore` change — plus the
GNU-compatible `timeout` row the table has been missing all along.

**Does it need an ADR? Probably yes, and one narrow one.** Not for "may we install Node" — that is a
prerequisites row. The ADR-shaped question is the one a table cannot answer: **a rig fixture may carry
its own runtime and its own test runner, and that does not make it a runner for this repo.** ADR 0013
decided this repo has no test runner; a fixture shipping Jest looks exactly like that decision being
quietly reversed, and the distinction will not survive six months as a table row. ADR 0013 also names
its own supersession trigger — *"when a third executable needs a test"* — and this change adds a
runner, a collector and a normalizer. Either the ADR states the fixture/repo boundary, or ADR 0013 is
amended. Recommend deciding it before slice 3a, not while holding a half-built fixture. **This one was
not ruled on** and is the only governance item still outstanding.

## Review-budget forecast — resolved

`delivery_strategy` resolved to **chained PRs**, approved on this exact shape. Budget is 400 changed
lines per slice; roughly 1,850 lines total across six. **`size:exception` is NOT taken** — every slice
fits inside the budget on its own.

| Slice | Authored lines | Verification |
|---|---|---|
| 1 — peak-occupancy retro-derive | ~150 | `python3 -m py_compile`; the 42 existing rows re-derive byte-identical |
| 2 — collector + normalizer | ~300 | `--self-test` on each; `python3 -m py_compile` |
| 3a — clean fixture | ~400 | the fixture's own suite reports zero failures |
| 3b — injections + measured answer key | ~400 | per-injection signature proof; MANIFEST freeze |
| 4 — `run-pipeline.sh` + surface preimage | ~350 | `bash -n`; a `--dirty-ok` shakedown run |
| 5 — hypotheses + `OPERATIONS.md` + report | ~250 | `./hooks/pre-commit --all` |

Every slice has an autonomous scope, a stated verification, and a clean rollback. 3a and 3b sit **at**
the budget rather than under it, so fixture content is where the estimate is least certain; if 3a
overruns, splitting it again is preferred to taking an exception.

**Decision needed before apply: No — resolved to chained PRs. Chained PRs recommended: Yes.
400-line budget risk: Low per slice, High only if the slices are collapsed into one change.**

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| PIPELINE's low peak is read as a finding when it is true by construction | High | Named above as the guard. The reported quantities are MONOLITHIC's actual peak, PIPELINE's green-restore under a narrower view, and PIPELINE's cumulative |
| The agent cheats: deletes, skips, or edits tests to reach green | High | The integrity guard — collected-identifier equality plus test-file byte equality — reusing the runner's verified mutation instrument. `regressed`, not `green` |
| An injection produces no observable failure | Medium | No injection enters the corpus unvalidated (item 4). Measured `F0`, never the declared list |
| A cause masks another, so `F0` is smaller than the injection count | Medium | Expected, not a defect: `F0` is measured after injection precisely so scoring cannot punish an invisible cause |
| Suite-did-not-start voided as environmental when it is the measurement | Medium | Item 3, now an explicit **spec obligation**: the spec MUST settle the run-axis / suite-axis separation before any run, and may not defer it to the runner |
| The root-cause report format is loose enough to need a judgment call | Medium | Exact-match parseable, frozen into the fixture, authored before the prompt. A format settled after seeing an answer is the fault ADR 0012 exists to prevent |
| Pre-registration lands in slice 5, after the runner exists | Medium | The guard above: no countable run before slice 5, and slice 4's shakedown is `--dirty-ok` and therefore structurally uncountable |
| The fixture's real code makes the product domain public, irreversibly | Certain | Accepted. Authorized by the code's author and owner, on record, after the cost was stated plainly. The irreversible point is the push. ADR 0009 still binds on paths, names, tokens and hostnames |
| The normalizer is non-deterministic across runs (paths, worker count, ordering) | Medium | `--self-test` on the normalizer, per ADR 0013. Non-determinism here corrupts every cluster count downstream |
| The pipeline loses on cumulative tokens even while winning on peak | Medium | This is `hypotheses/0003`'s refute branch firing. A result, not a failure |
| Node/Jest arrives as an undocumented dependency, or reads as reversing ADR 0013 | Medium | Prerequisites row plus the narrow ADR proposed above, decided before slice 3 |
| Scope grows into a generalized multi-experiment rig and no number lands | Medium | Sibling runner, not a refactor. Generalization deferred until two experiments exist |
| The stage-1 shakedown's data is used to set the stage-2 thresholds | Medium | The exclusion is pre-registered here. Stage-1 rows never enter the stage-2 test |
| Effect smaller than the affordable N can distinguish | Medium | Declared now: under ~1.3× peak ratio is **not testable at this budget**, and that is the honest reported outcome |
| The fixture's own suite is mistaken for this repo's test runner | Low | Stated in the prerequisites entry and in the proposed ADR |

## Rollback plan

Nothing in `theory/` changes until a result exists, so rollback before that point is deleting the new
fixture directory, the sibling runner, the collector and the normalizer — no committed truth is
touched. Slice 1's schema bump is reverted by reverting one commit; existing rows re-derive from the
raw captures unchanged, which is the property the prior cycle verified. After a `theory/` write, revert
that single commit; the ADRs, this proposal and the exploration stay, because the attempt is
provenance. A refuted hypothesis is kept with `status: rejected`, never deleted. Fixtures are additively
versioned, so rollback never mutates a frozen version.

## Success criteria

- [ ] Peak and cumulative occupancy are derivable, proven on already-paid-for captures before any new run
- [ ] Both hypothesis files exist, with exact support **and** refute conditions, before the first
      countable run
- [ ] The clean fixture is proven zero-failure, and every injection is proven to produce its signature
- [ ] The answer key is **measured** after injection — `F0`, `R0` and `S0` — frozen, and committed
      before its prompt
- [ ] Both arms emit a root-cause report in the frozen exact-match format, so precision and recall are
      computed identically in both
- [ ] Diagnostic precision and recall are reported as a pair, never blended into one figure
- [ ] The four-value verdict fires at least once as `partial` — the first clean partial credit the
      quality channel has ever produced
- [ ] The integrity guard is proven able to fire, on a case that deletes or edits a test
- [ ] Diagnostic attribution, green-restore, peak occupancy and cumulative tokens are published as
      four separate tables
- [ ] Dollar cost appears, and is not the headline
- [ ] The tool surface is identical across both arms and every role, read back per invocation
- [ ] Delivery is chained across the six approved slices, with `size:exception` not taken

## Open questions the spec phase must settle

Two remain. Both are recorded as inputs to `sdd-spec`, not as blockers on this proposal.

1. **Does the applier get a repository in its workspace at all?** This decides whether `git apply` is
   available as the application mechanism. Forbidding git keeps hardening item 1's protection free;
   allowing it re-opens the diff-reading shortcut and needs a compensating control.
2. **Is 50 failing cases from 6 root causes the right flood ratio?** The real incident was thousands of
   cases from few causes, so the ratio may matter more than the count, and the stage-2 target may be
   measuring a different shape than the one that actually hurt.

Two earlier questions are now settled and folded in above: the outcome channel is **both**, with
diagnostic attribution primary, and the fixture's source authorization is on record. A third — whether
the fixture/repo runner boundary needs its own ADR — was not ruled on and is flagged in the toolchain
section.
