---
id: sdd/failure-flood-triage/spec
type: journal
targets: [any]
status: draft
verified: 2026-08-11
sources: ["sdd/failure-flood-triage/proposal.md", "sdd/failure-flood-triage/exploration.md", "sdd/measurement-rig/spec.md", "decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0012-a-hypothesis-is-never-citable.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "skills/hypothesis-cycle/SKILL.md", "skills/source-verdict/SKILL.md"]
---

# failure-flood-triage — Specification

SDD spec phase. Requirements and scenarios only — no storage schema, no driver language, no file
layout (those are `sdd-design`). No test runner exists in this repo by decision (ADR 0013);
verification below is transcript/artifact inspection and `--self-test` flags, never "run the tests."
Requirement IDs use prefix `R-F` (this experiment) to stay distinct from `sdd/measurement-rig/spec.md`'s
`R-A` series, which this spec cites by ID rather than restates where the rule is repo-wide.

## Purpose

Settle, before any prompt exists: the measured-baseline contract (`C`/`F0`/`S0`/`R0`), the run-axis vs.
suite-axis separation, the frozen root-cause report format, the workspace/repository boundary, the
outcome and runway channels and their non-composite reporting, sampling, pre-registration, and the
stage-2 flood ratio — the three obligations the orchestrator named as non-deferrable, plus the five
standing hardening requirements (corrected where they conflicted with repo convention), ADR 0010's
five constraints, and (added after `sdd-design`'s code-verified corrections and two operator decisions)
the amplified flood-ratio target, the fixture/repo-runtime-boundary ADR, and five requirement fixes
verified against `rig/run.sh`, `derive.py`, and `hooks/pre-commit`.

## Two open product questions — settled here

### Decision A — No repository, in any role, in either arm, ever

The applier does **not** get a repository in its workspace. Every workspace, for every role in both
arms, is materialized as a flat file copy with no `.git`, identical to `rig/run.sh`'s existing
materialization — extended to cover the applier, not only the diagnostician. `git apply` is therefore
not offered as an application mechanism in either arm; the sole mechanism is direct file edits via the
write tool, uniform across arms so this is not a second variable.

Rationale: hardening item 1 (no reachable ground truth) is protected for free only if no role, at any
point, can run `git diff`/`git log` against injected breakage. Allowing a repo for the applier alone
would still let a compromised or exploratory tool call read history the diagnostician was denied,
which defeats the guard through a side door. The cost — losing `git apply` as a convenience — is
accepted; a write tool can apply any edit a patch could.

### Decision B — Stage-2 flood ratio is amplified to incident order-of-magnitude (operator decision; supersedes an earlier donor-headroom-ceiling draft)

**Ratio, not count, is what kills the serial approach**: unchanged reasoning. A donor-headroom ceiling
(≤138 real cases, `exploration.md` §6) caps the achievable ratio at roughly 20:1–23:1. That was this
spec's first resolution, and the operator rejected it on a concrete threat: the CLI reports
`contextWindow: 1000000`, so at 138 total cases MONOLITHIC may never be meaningfully stressed and the
experiment returns a null — the same failure mode that left `sdd/measurement-rig` at PARTIAL with a
detector that never fired.

**Resolution: table-driven parameterization, not more donor modules or more root causes.** The same 6
root causes get parameterized case tables on their host modules — e.g. `applyKeypadInput`'s 15 cases
become on the order of 660–765 rows, `confirmSeed`'s 12 become on the order of 528–612 — so the achieved
case:cause ratio reaches the incident's order of magnitude (~433–500:1), not the donor ceiling's
~20:1–23:1.

**The multiplier is ~44–51×, and the base is 59, both corrected 2026-08-12.** This figure was wrong twice
before, the same way each time: it was derived from a host set that had not been selected yet.

| Draft | Base assumed | Multiplier | Aggregate | Ratio |
|---|---|---|---|---|
| first | unstated | ~30–35× | ~2,500–3,000 claimed | ≈415–500:1 claimed |
| second | 65 | ~40–46× | ~2,600–3,000 | ~430–500:1 |
| **current** | **59, measured** | **~44–51×** | **~2,600–3,000** | **~433–500:1** |

The first draft's multiplier and aggregate were mutually inconsistent. The second fixed that but assumed
65 base cases, a total that still counted `parseTokenAmount`'s 13 — the module disqualified below as a
masking pair. Its best available replacements sum to 23, not 13, so the real six-module total is
15+12+9+8+8+7 = **59**. That figure is not an estimate: the v2 fixture's own Jest baseline reports exactly
59 tests passing, so the base is measured before the multiplier is chosen.

**The aggregate and ratio columns above are TARGETS, not measurements, and one of them is very likely
wrong by roughly eight times — recorded 2026-08-12.** The multiplier and the generated-case count are
now measured facts (2,823 generated). The *ratio* is not, because the ratio the experiment cares about
is **failing** cases per cause, and a generated case only fails if it exercises an injected path. Two
independent measurements put that yield near 12%: `v1/answer-key/s1.json` records 4 failures out of 36
tests, and task 3.3's own R-F9.1 check recorded 49 failures out of 392 generated cases. At that yield
2,823 generated cases give roughly 340 failures, i.e. ~57:1 rather than ~433–500:1. Per R-F9.2 the
achieved ratio must be measured and never assumed, so the generator's `--self-test` was changed to stop
printing a ratio it cannot know, and task 4.3's measurement of v2's `F0` is what settles this. If the
gap is real, closing it means either concentrating the axis tables on the injected paths — still real
failures of real logic, so R-F9.1 holds — or generating more rows. That decision waits for the number.

The correction costs one number in the generator's axis table and nothing else. Generated rows are never
committed (design Decision 9a), and the collector's report ceiling is 64 MB against a 5–20 MB expected
report, so the larger corpus needs no change there either. R-F9.2 still binds regardless: the achieved
ratio is measured per run, never assumed from this table.

**One host module named in the earlier draft is disqualified.** `parseTokenAmount` ranked second by case
count but its test file imports `formatTokenAmount` for a round-trip assertion, which makes the pair a
masking risk under R-F1.1. It is excluded from the host set. The exclusion was found at
fixture-authoring time from the test file's own imports, before any injection existed — which is where
masking risk is cheapest to find.

**Amplified cases MUST remain real failures of real logic.** Parameterization is additional input rows
exercised through the same donor module and the same injected root cause — never a synthetic assertion
authored only to resemble a failure. This is the line that keeps the fixture honest, stated normatively
in R-F9.1.

### Decision C — approved: a narrow ADR states the fixture/repo runtime boundary, written before slice 3a

A third, separate operator decision (not one of the proposal's two open questions): a narrow ADR MUST
be written and ratified before slice 3a, stating that a rig fixture may carry its own runtime and test
runner (Node/npm/Jest, scoped to `rig/fixtures/failure-flood/*`) without reversing ADR 0013's
repo-level "no test runner" decision. The trigger is textual, not conditional on this fixture question:
ADR 0013 names its own supersession trigger, *"when a third executable needs a test,"* and this change
commits three — `rig/run-pipeline.sh`, the collector, and the normalizer's `--self-test` surface
(R-F1.3, R-F11.2). That trigger fires whether or not the fixture/repo boundary question is asked; the
ADR is required on ADR 0013's own terms.

## Requirements

### R-F1 — Ground truth is measured, frozen before the prompt

**R-F1.1** The system MUST establish four baselines — `C` (clean-fixture identifier set, zero
failures), `F0` (measured, normalized failure set after injection), `S0` (suite state after injection:
`ran`/`did-not-start`/`partial`, with its normalized signature), `R0` (root-cause label per member of
`F0`, from isolation validation) — and MUST freeze all four before authoring the corresponding prompt.
The declared injection list MUST NEVER be used as ground truth.

#### Scenario: A masked cause is not scored as missed

- GIVEN two injections where one shadows the other in the same test's first-reported error
- WHEN `F0` is measured after injection
- THEN `F0` and `R0` reflect only the observable cause, and the masked cause is absent from the
  scoring key, not present-but-missed

**R-F1.2** No injection MUST enter the corpus until validated in isolation against the clean fixture,
proven to produce its expected, frozen signature (`R-A1.4` applied to injections).

#### Scenario: An injection with no observable effect is rejected

- GIVEN an injection that, run alone against the clean fixture, produces zero new failures
- WHEN isolation validation runs
- THEN the injection is rejected from the corpus before any prompt exists

**R-F1.3** The clean fixture MUST be proven zero-failure before each injection. The signature
normalizer MUST be deterministic across runs (paths, worker count, ordering) and MUST expose that
determinism via a `--self-test` flag on the normalizer itself, per ADR 0013 — not a test suite. The
flag-gated shape follows `hooks/pre-commit --self-test` — the correct precedent, since its self-test
runs only when the flag is passed; `derive.py`'s self-test is unconditional inside `main()` and is a
different pattern, not the one being reused here.

#### Scenario: Normalizer self-test catches non-determinism

- GIVEN the normalizer run twice over the same raw suite output
- WHEN `--self-test` compares both outputs byte-for-byte
- THEN a mismatch fails the flag before the normalizer is trusted for any run

#### Scenario: Self-test also requires discrimination, not only repetition

- GIVEN a normalizer that always returns one constant signature, which passes the repetition check
  above trivially
- WHEN `--self-test` additionally feeds it two inputs a human would judge as different failures
- THEN the flag MUST fail unless the two inputs normalize to two DIFFERENT signatures — determinism
  alone does not prove the normalizer discriminates anything

**R-F1.4** (added by measurement, PR4-signature-scope-fix) The signature MUST be computed over the
matcher-shaped head **and** the failing test's file, never the head alone. R-F1.3's own discrimination
scenario proved the normalizer distinguishes two DIFFERENT heads; it never exercised two DIFFERENT
causes sharing the SAME head in two different modules, which is exactly what `answer-key/s1.json`'s
stage-1 measurement (task 4.2) hit: three unrelated causes in `applyKeypadInput.test.ts`,
`confirmSeed.test.ts` and `parseTransfers.test.ts` all normalized to Jest's generic
`expect(received).toBe(expected) // Object.is equality` head, with nothing distinguishing before the
Expected:/Received: cut, and collapsed into one cluster. R-F1.1's own masking scenario ("A masked cause
is not scored as missed") does not cover this mode either — it describes one cause shadowing another
inside the SAME test, not three unrelated causes across three different tests. This requirement corrects
the head-only rule's scope; it does NOT reverse it — see the discrimination note below.

#### Scenario: Distinct causes in distinct modules do not collapse

- GIVEN two failures whose normalized matcher-shaped heads are byte-identical
- WHEN they come from two different test files
- THEN their signatures MUST differ, so two unrelated causes across two modules are never reported as
  one cluster

#### Scenario: One cause within one module still clusters together

- GIVEN two failures whose normalized matcher-shaped heads are byte-identical
- WHEN they come from the SAME test file
- THEN their signatures MUST match — this is the property R-F1.3's head-only rule protects (a
  table-driven cause producing many cases within one module must still report as one cluster,
  R-F9.1/9.2), and it MUST survive this correction, not merely be assumed to

**Scope limit, stated rather than assumed.** This correction is measured safe against the opposite
failure (one real cause legitimately producing failures in two different files, over-split by a
file-scoped signature) only because this fixture's host modules are import-free by construction — no
injected cause in `failure-flood/v1` or `v2` can span two test files. A fixture whose modules import
each other could hit that case; `R0`'s many-to-one cluster-to-cause-site mapping (already required,
see the design's own "the key absorbs it, the algorithm does not change" reasoning) is what would
absorb it, not a further change to this requirement.

### R-F2 — Run-axis and suite-axis are independent (hard obligation 1)

**R-F2.1** The system MUST record two independent fields per run: `run_state`
(`completed`/`void`/`failed` — the harness could execute the invocation at all, `R-A1.1` vocabulary
reused) and `suite_state` (`ran`/`did-not-start`/`partial` — whether the injected fixture's own suite
executed). Neither MUST be derived from the other.

**R-F2.2** A third field, `suite_state_cause` (`injection`/`environment`), MUST be set mechanically:
`injection` iff the observed `suite_state` and its normalized signature exactly match the frozen `S0`
recorded during isolation validation before any prompt; `environment` otherwise. `environment` MUST
force `run_state=void`, `void_reason=suite-state-mismatch`, excluded and replaced. `injection` MUST be
scored, even when `suite_state != ran`.

#### Scenario: Deliberate config breakage is measured, not discarded

- GIVEN an injection whose frozen `S0` is `did-not-start` with signature `X`
- WHEN a run reproduces `did-not-start` with signature `X`
- THEN `suite_state_cause=injection`, the run is scored, and the diagnostic report is graded against
  `R0` for this injection

#### Scenario: An unrelated environment failure is voided, not scored

- GIVEN the same injection, whose frozen `S0` signature is `X`
- WHEN a run instead produces `did-not-start` with a different signature (missing `node_modules`)
- THEN `suite_state_cause=environment`, the run is `void`, and it is replaced by a fresh run

**R-F2.3** When `suite_state != ran`, the collector MUST still emit a `failure` record (domain-neutral
schema) keyed to a synthetic identifier (`__suite__`) carrying the normalized signature, so `F0`/`R0`
scoring never special-cases the suite axis.

### R-F3 — Root-cause report format, frozen before any prompt (hard obligation 2)

**R-F3.1** Both arms MUST write a file `root-cause-report.txt` to the run workspace root before
completion, in this exact format, authored and frozen before either prompt is written:

```
ROOT-CAUSE-REPORT v1
<relative-path>:<line-number>
<relative-path>:<line-number>
```

Line 1 is the literal sentinel. Every following non-blank line MUST match `^[\w/.\-]+:\d+$` and name
the file:line of a claimed root-cause location. Any other content anywhere in the file makes the whole
file malformed. This reuses the `<path>:<line>` exact-match device `sdd/measurement-rig/spec.md`
already verified deterministic, applied to root-cause locations instead of defect locations.

**R-F3.2** Scoring MUST be: `claimed` = deduplicated set of valid lines (∅ if malformed/missing);
`correct` = `claimed ∩ RC_true` where `RC_true` is the frozen file:line set from `R0`; `precision` =
`|correct| / |claimed|` (reported `n/a` when `claimed` is empty, never silently 0); `recall` =
`|correct| / |RC_true|`. Both arms MUST be scored by this identical function.

#### Scenario: A malformed report scores as no claims, not a crash

- GIVEN a report file containing prose instead of `path:line` lines
- WHEN scoring runs
- THEN `claimed = ∅`, `precision = n/a`, `recall = 0`, and no exception is raised

#### Scenario: Freezing after seeing a result is the fault this avoids

- GIVEN this exact format is committed before either the diagnostician or applier prompt exists
- WHEN any later phase proposes loosening the regex or adding a field
- THEN that change requires a new spec revision, per ADR 0012's rule against choosing a reporting
  channel after data is visible

### R-F4 — Outcome channels, both primary, never composited

**R-F4.1** Diagnostic attribution (R-F3.2's precision/recall pair) is the primary outcome channel and
MUST be reported as a pair, never blended into an F-score or any other single figure.

**R-F4.2** Green-restore MUST be published as a mandatory companion, four values, no composite:
`green` (suite `ran`, failures empty, integrity guard passes), `partial` (observed failures a strict
non-empty subset of `F0`, no regression), `no-progress` (observed failures ≥ `F0`), `regressed` (any
test failing that passed in `C`, or the integrity guard fails). The integrity guard MUST reuse the
runner's verified file-hash mutation check (test files read-only substrate; source files writable).

#### Scenario: Partial credit fires at least once

- GIVEN a run that fixes 4 of 6 injected root causes with no regression
- WHEN green-restore is classified
- THEN the verdict is `partial` — the first clean partial-credit outcome this quality channel has
  produced

#### Scenario: Deleting a test is caught, not rewarded

- GIVEN a run that deletes a failing test instead of fixing it
- WHEN the integrity guard compares the post-run identifier set to `C`
- THEN the verdict is `regressed`, never `green`

**R-F4.3** Neither channel MUST ever be summed, weighted, or ANDed into a single success flag
(`R-A1.3`). This corrects hardening item 6 as originally stated ("tests green AND applier under
budget"): the conjunction is dropped; green-restore, peak occupancy, and cumulative tokens are three
separate published channels.

### R-F5 — Runway channels

**R-F5.1** Peak occupancy MUST be recorded as, per model **turn** — deduplicated by `message.id`,
because several `assistant` stream events share one `message.id` with byte-identical `usage` (one
verified capture showed 14 `assistant` events collapsing to 4 turns; summing per event rather than per
deduplicated turn over-counts roughly 3.5×) — `input + cache_read_input + cache_creation_input`
tokens; the run's value is the **max** over deduplicated turns. Labelled as a measured proxy, never a
direct context-window read. The CLI-reported `contextWindow: 1000000` MUST be recorded per run and
used as the denominator whenever peak or cumulative occupancy is reported as a ratio.

**R-F5.2** Cumulative tokens MUST be recorded as the **sum**, over deduplicated turns, of the same
quantity, plus output tokens. Corrected finding: `result.usage` on the committed row is already an
aggregate **over all turns**, not the final turn (verified arithmetically on two existing captures:
141134 = 16602+39942+40854+43736; 97170 = 16602+39833+40735) — so cumulative occupancy is **already
derivable from the existing committed row schema**, with no new capture needed. Only peak occupancy
requires new per-turn extraction from the raw captures.

**R-F5.3** Before any new failure-flood run is funded, the **peak**-occupancy detector only —
cumulative is already available per R-F5.2 — MUST be proven able to fire (`R-A1.4`) by retro-deriving
it, with `message.id` deduplication, over the 42 already-paid-for captures of the first experiment.
This is independent of every other slice and gates nothing else.

#### Scenario: Detector proven on existing data before spending, deduplicated correctly

- GIVEN the 42 existing raw captures, each carrying per-turn `assistant` events with
  `cache_read_input_tokens`, several sharing one `message.id` per turn
- WHEN the retro-derive schema bump runs
- THEN every existing row's pre-existing fields re-derive as a **byte-identical projection** excluding
  `schema_version`, `checker_digest`, and any newly added key — `derive.py`'s `CHECKER_DIGEST` hashes
  the deriver's own bytes and necessarily changes on any edit to `derive.py`, so true byte-identity
  across all fields is not the achievable claim — and each row also gains a non-null, deduplicated
  peak-occupancy value

**R-F5.4** No composite runway score. Peak and cumulative are reported as two separate tables; a
degenerate low-peak/high-cumulative or high-peak/low-cumulative result MUST remain visible, never
collapsed.

### R-F6 — Harness, roles, workspace

**R-F6.1** No role, in either arm, at any point in a run, MUST have access to a `.git` directory or
any version-control history over the fixture. (Decision A.)

**R-F6.2** The tool surface (committed preimage under `rig/surfaces/`) MUST be identical across both
arms and every role. Narrowing any role's tools is a second variable and MUST NOT be introduced.

**R-F6.3** The applier's fix-plan MUST be treated as valid only against the workspace snapshot at plan
time. The applier contract MUST re-collect (re-run the collector) after applying each cluster's fix,
before applying the next. Applying all fixes blind against a stale snapshot MUST NOT occur.

#### Scenario: A stale plan does not clobber a later fix

- GIVEN a fix-plan naming 6 clusters, and cluster 2's fix incidentally also resolves cluster 4
- WHEN the applier re-collects after cluster 2
- THEN cluster 4 is observed already resolved and is not blindly re-applied

**R-F6.4** A sibling runner (e.g. `rig/run-pipeline.sh`) MUST implement the multi-invocation pipeline.
`rig/run.sh` MUST NOT be refactored; its cost instrument is verified and refactoring risks invalidating
that verification. Both arms MUST allow `Bash` and a write tool (unlike `run.sh`'s unconditional `Bash`
disallow, which stays local to that experiment).

### R-F7 — Sampling and recording (ADR 0010 constraints 2, 3, 5)

**R-F7.1** Per run: model id (fixed across arms, ADR 0010), harness/arm id, fixture version, a hash of
each role's exact prompt bytes, a hash of the tool surface. One variable — harness shape — with
everything else recorded fixed.

**R-F7.2** Each (fixture-version, arm) cell starts at N=5. If all 5 land in the same green-restore
verdict AND attribution precision/recall range ≤ one correctly-attributed cause, stop at N=5.
Otherwise add one batch of 5 (N→10), then one more if still mixed (N→15, cap). Report final N with the
observed min/max range, never a mean alone. Stage-1 shakedown rows are excluded from this rule (R-F8).

**R-F7.3** Per role, per turn: input, output, `cache_read_input`, and `cache_creation_input` tokens
recorded separately (never a single total), plus tool-call count and names. Aggregated per role and
per run.

**R-F7.4** `permission_mode` MUST be explicitly declared per run — a named argument on the sibling
runner — and MUST be recorded on the row; it MUST NEVER be left to whatever the invoking environment
happens to inherit. Corrected finding: all 42 existing rows carry an inherited
`permission_mode: "bypassPermissions"` that `rig/run.sh` never passed as a flag, harmless there because
no arm had a write tool. Here permission mode decides whether `Bash` and the write tool execute at all,
so an inherited value would make both arms non-reproducible from a plain terminal.

#### Scenario: A run without an explicit permission mode is rejected before it starts

- GIVEN `rig/run-pipeline.sh` invoked with no permission-mode argument
- WHEN the runner's preflight checks its arguments
- THEN the run refuses to start rather than silently inheriting ambient permission state

### R-F8 — Pre-registration guard

**R-F8.1** No countable run MUST execute before both hypothesis files
(`hypotheses/0002-*`, `hypotheses/0003-*`) exist, each with exact support and refute conditions
written before any run that could settle it (ADR 0012).

**R-F8.2** The sibling runner MUST expose a dedicated `--shakedown` flag, distinct from `--dirty-ok`,
that stamps `void_reason=shakedown` **unconditionally** on every row it produces, regardless of tree
state. Named failure mode this replaces: `rig/run.sh`'s `--dirty-ok` only stamps a void when the tree
is genuinely dirty at invocation time (`[ "$DIRTY_OK" -eq 1 ] && [ -n "$DIRTY" ]`); slice 4's shakedown
runs after slice 4 itself is committed, when the tree is clean, so `--dirty-ok` alone stamps nothing
and the row is fully countable — the exact ADR 0012 violation this guard exists to prevent. A
runner-level preflight MUST refuse to run slice 4's shakedown without `--shakedown` set.

#### Scenario: A shakedown on a clean tree cannot leak into the result

- GIVEN slice 4 is committed and the tree is clean
- WHEN the shakedown run is invoked with `--shakedown`
- THEN the row is stamped `void_reason=shakedown` unconditionally and excluded from every count and
  every hypothesis test, regardless of `--dirty-ok`'s tree-state check

#### Scenario: The failure mode this replaces

- GIVEN the same clean-tree shakedown invoked with only `--dirty-ok` (no `--shakedown`)
- WHEN dirty-tree detection finds nothing dirty
- THEN the row would be fully countable and leak into N, spread, and both hypothesis tests — which is
  why `--dirty-ok` alone MUST NOT be relied on for slice 4

### R-F9 — Staging and flood ratio (Decision B)

**R-F9.1** Stage 1 = 10 failing cases / 3 root causes, shakedown, excluded from the stage-2 test.
Stage 2 MUST hold exactly 6 root causes. The stage-2 flood ratio (failing cases : root causes) target
is **order-of-magnitude comparable to the real incident (~500:1), not a fixed case count** — achieved
by table-driven parameterization of the donor modules that host each of the 6 root causes (additional
real input rows through the same module and the same injected cause), never by adding more donor
modules or more root causes. Amplified cases MUST be real failures of real logic: parameterization
MUST NOT introduce synthetic assertions authored only to resemble a failure without exercising the
injected cause through genuine module logic.

**R-F9.2** The achieved stage-2 ratio MUST be measured and recorded per run
(`total_failing_cases / 6`) and reported alongside the result — never assumed from the
parameterization design. Whatever ratio is actually achieved MUST ship with a stated comparison to the
real incident's ~500:1, and no conclusion MUST be extrapolated beyond the measured ratio without saying
so (mirrors `R-A1.6`'s honesty-contract discipline). Exact per-module table sizes are a design/tasks
deliverable; the achievable ratio remains unverified — and the risk that it undershoots ~500:1 is
larger here than under the donor-headroom-ceiling reading, because amplification has no audited upper
bound the way the donor case count did — until that selection is made and measured.

### R-F10 — Domain-neutral schema

**R-F10.1** Schema and field names (`failure`, `signature`, `cluster`, `fix-plan`) MUST NOT name a
tool (no `jest-*` field). A future `tsc` or lint collector MUST be able to populate the same schema
with no rename.

#### Scenario: A second collector needs no schema change

- GIVEN the frozen `failure`/`signature`/`cluster` schema built for the Jest collector
- WHEN a hypothetical `tsc` collector is documented (not built, out of scope) as populating the same
  schema
- THEN no field in the schema names Jest, and none would need renaming

### R-F11 — Fixture/repo runtime boundary ADR (Decision C)

**R-F11.1** A narrow ADR MUST be written and ratified before slice 3a, stating that a rig fixture
(here, `rig/fixtures/failure-flood/*`) may carry its own runtime and test runner without reversing
ADR 0013's repo-level "no test runner" decision. It MUST name the boundary explicitly: the fixture's
own suite is fixture content, never this repo's runner.

**R-F11.2** The ADR MUST record that ADR 0013's own stated supersession trigger — *"when a third
executable needs a test"* — fires here regardless of the fixture question, because this change commits
three executables carrying their own test surface: `rig/run-pipeline.sh`, the collector, and the
signature normalizer's `--self-test` flag (R-F1.3). The ADR MUST either amend ADR 0013 or explicitly
affirm it still holds with the fixture boundary stated.

#### Scenario: The ADR lands before any fixture content is committed

- GIVEN slice 3a is about to commit the clean fixture
- WHEN the ADR does not yet exist
- THEN slice 3a MUST NOT proceed — Decision C's ordering is a precondition, not a parallel task

## ADR 0010 constraint mapping

| Constraint | Requirements | Satisfaction |
|---|---|---|
| 1. Deterministic checker, before prompt | R-F1.1, R-F1.2, R-F3.1–3.2, R-F4.1–4.2 | Both checkers are exact-match/set-equality over frozen `R0`/`F0`/`C`; commit order proves checker-before-prompt |
| 2. One variable, two hashes | R-F6.2, R-F7.1, R-F7.4 | Harness shape is the sole variable; prompt-byte hash per role, tool-surface hash, and an explicitly declared (never inherited) permission mode recorded per run |
| 3. N per cell, spread | R-F7.2 | Variance-driven N=5→10→15 per (fixture, arm), min/max range reported |
| 4. One category, staged not tiered | R-F9.1 | Single fixture/category; two stages (shakedown, comparison), no taxonomy expansion |
| 5. Recorded fields | R-F5.1–5.4, R-F7.3 | Input/output/cache tokens separate, per-turn and aggregated; tool calls per role; two deterministic verdicts |

## Non-Goals

| Excluded from v1 | Why |
|---|---|
| Model-tier variation | ADR 0010 holds the model fixed; a separate future experiment |
| Refactoring `rig/run.sh` | Its cost instrument is verified; a sibling runner is used instead |
| A `tsc`/lint collector | Documented as the next collector; schema stays domain-neutral for it |
| Validating against a real project checkout | Frozen-fixture comparison first; staged deliberately |
| Dollar cost as headline | Secondary, always published, never the lead |
| A composite success score | `R-A1.3`; three channels, three tables |
| React Native fixture content | v1 has none; additive versioning covers a future v2 |
| A repo-level test runner | ADR 0013 still holds; R-F11 states the fixture-runtime boundary instead |

## Key Learnings

1. The `suite_state_cause` mechanism (comparing observed `suite_state` against the frozen `S0`) still
   resolves the run-axis/suite-axis conflict mechanically, unchanged by this revision.
2. A donor-headroom ceiling (~20:1–23:1) could not reach incident scale; table-driven parameterization
   of real modules replaces case-selection-only scaling, but the achieved ratio is now a design-phase
   unknown that must be measured, not assumed — the risk this creates is larger than the one it fixed.
3. `result.usage` on a committed row already aggregates over all turns, not the final turn — cumulative
   occupancy needed no new capture; only peak occupancy did, and only after deduplicating by
   `message.id`.
4. A void-stamping mechanism gated on "if the tree happens to be dirty" silently stops protecting
   anything the moment the tree it inspects becomes clean — exactly the state a post-commit shakedown
   run is in.
5. ADR 0013's supersession trigger is textual ("a third executable needs a test") and fires
   independent of any other design question, once this change is counted.
