---
id: sdd/run-input-provenance/spec
type: journal
targets: [any]
status: draft
verified: 2026-08-19
sources: ["sdd/run-input-provenance/proposal.md", "sdd/run-input-provenance/exploration.md", "rig/derive.py", "rig/run-pipeline.sh", "sdd/archive/2026-08-18-failure-flood-triage/spec.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0013-a-committed-executable-carries-its-own-test.md"]
---

# run-input-provenance — Specification

SDD spec phase. Requirements and scenarios only — no storage schema, no field layout, no code (those
are `sdd-design`). Requirement IDs use prefix **`R-P`** (Provenance), chosen to stay distinct from
`sdd/archive/2026-08-18-failure-flood-triage/spec.md`'s `R-F` series and `sdd/measurement-rig/spec.md`'s
`R-A` series. No `R-P` prefix exists anywhere in this repo today (verified by search). Line anchors below
are cited against `rig/derive.py` and re-verified directly against the file in this phase, not accepted
from the proposal.

## The boundary this spec leads with, and does not soften

The `failure-flood-triage` cycle delivered **an instrument and a FAILED ratio target — never a
comparative result.** Verified directly in `rig/results/failure-flood-v1/runs.jsonl`: exactly three
rows, every one `state=void, void_reason=shakedown, anomaly_classes=[]`. **N = 0 countable rows.**

No requirement or scenario below may imply a comparative result exists, is pending, or is nearly
available. This change's own success is measured entirely in code paths and self-tests, not in any
number `theory/` could cite (`decisions/0011-rig-produces-evidence-not-truth.md`).

## A distinction that must not be read as a contradiction

`rig/derive.py:1468-1470` already refuses to run at all when `run_self_tests()` fails: it prints
*"Self-test FAILED — a detector cannot be proven to fire. Refusing to derive rows."* and exits 1. This
spec's own requirements (R-P3, R-P4) instead void a single row on provenance mismatch and let every
other row derive normally. These are not competing answers to the same question:

- The existing refusal (`:1468-1470`) fires when **the deriver itself is unproven** — no detector in
  the whole file can be trusted to fire correctly, so nothing it produces is trustworthy either.
- This spec's mismatch void fires when **the deriver is proven and one row's own inputs disagree** with
  what that row was originally scored against — every other row's inputs are unaffected and their
  derivation proceeds.

R-P12 states this explicitly with a falsifiable scenario pair, so no later reader mistakes "refuse
entirely" and "void one row" as inconsistent positions on the same failure.

## Decisions this phase owns, and the reasoning (proposal's three open questions)

### Decision 1 — `void_reason` string and pre-scheme marker form

**The dedicated `void_reason` for a Face A provenance mismatch is `"answer-key-mismatch"`.** It follows
the file's own existing `<face>-mismatch` naming convention (`surface-mismatch`, `permission-mode-mismatch`,
`model-mismatch`, `suite-state-mismatch` — all verified present at `rig/derive.py:473-474`, `:856-857`,
`:860-861`, `:884-885`, `:977-978`), stays visually and lexically distinct from `surface-mismatch` per
settled decision 4, and every existing mismatch reason in this file is *also* added to `anomaly_classes`
as the same string (verified: every `void_reason = "...-mismatch"` assignment in `derive.py` is paired
with an `anomaly_classes.add(...)` of the identical string). `"answer-key-mismatch"` follows that same
paired convention rather than inventing a new one.

**The pre-scheme marker is an `anomaly_classes` member, not a dedicated field or a `void_reason`
override: `"pre-scheme-provenance"`.** The three existing rows' `void_reason` slot is already occupied
by `shakedown` and rollback explicitly requires it stays that way ("the three shakedown rows are void
before and after, so no committed truth is touched"). `anomaly_classes` already accumulates multiple
orthogonal conditions on one row (it is a set, not a single value) with no schema-additive field needed,
so recording "this row predates the provenance-digest scheme entirely" there costs nothing new and reads
naturally beside `shakedown`.

**Reconciled spelling with `design.md`.** This spec's first pass wrote the marker string as
`"pre-provenance-scheme"`; `sdd/run-input-provenance/design.md` independently settled on
`"pre-scheme-provenance"` and threads it through its re-derive projection, its `--self-test` case list,
and its data-flow diagram. Changing design would cost more for no gain, so this spec aligns to design's
spelling rather than the reverse. One string, one spec, one design.

**A second, general `void_reason` also exists and is distinct from `"answer-key-mismatch"`.**
`"answer-key-mismatch"` (above) is scoped to Face A specifically: a row whose recorded answer-key digest
disagrees with the live one. `"input-provenance-missing"` (R-P5) is the reason for a different, broader
condition: an otherwise-`complete` row that cannot say what it was scored against **at all**, because it
carries no positive marker that it was captured under this scheme in the first place, or because that
marker is present but the digest it promised is `null`. The two reasons are never conflated: one names a
detected disagreement, the other names the absence of anything to compare.

### Decision 2 — Answer-key digest recording point

**Set-wide per fixture root, not per consumed key.** Reconciled with `design.md` section 2, which
reached the opposite conclusion from this spec's first draft. Design's argument is the deciding one and
it is architectural, not economic: the runner is bash and sees exactly **one** fixture root, while
`load_failure_flood_answer_keys()` (`derive.py:646-668`) merges every root into one dict. A per-consumed-key
digest would force the runner to resolve *which file carries this `task_id`* before the deriver does,
reimplementing in bash the `task_id`-not-filename rule that lives in Python at `derive.py:665-667`. One
rule in two languages is a drift surface, and this rig has already paid for that class of duplication.

**This spec's original objection is answered, not overruled.** The first draft rejected set-wide because
it would drag `answer-key/prereg.json` into the digest and need an exclusion rule. Verified against the
fixtures: `answer-key/prereg.json` and `answer-key/case-table.sha256` are **already covered by
`MANIFEST.sha256`** (`rig/fixtures/failure-flood/v2/MANIFEST.sha256` lines 1-3), therefore already
covered by `fixture_digest` and Face B. Including them in the answer-key digest is redundant, never a
gap, so no exclusion rule is required for correctness — only for diagnostic precision, which R-P2.2
handles. `rig/fixtures/failure-flood/v1/answer-key/` holds `s1.json` alone and has no `prereg.json` at
all, so v1 is unaffected either way.

The over-voiding design names — a change to a key the row did not consume — is **currently empty**:
`FAILURE_FLOOD_FIXTURE_VERSIONS` (`derive.py:633`) maps `s1→v1` and `s2→v2`, one task per root. It can
only appear if a root ever gains a second task's key, and it then errs toward `void`, the safe direction
under this file's downgrade-only discipline.

### Decision 3 — `rig/check.sh`'s missing bash self-test arm

**Left to its own cycle, not registered as a follow-up requirement here.** The proposal's own Out-of-scope
table already names it ("Real adjacent gap... Named, not fixed here"). It is a `rig/check.sh` composition
gap unrelated to what a run records about its own inputs, not a member of the provenance class this
change closes. Creating an `R-P` requirement for it would blur this spec's scope for no benefit the
proposal's own Non-Goals section doesn't already provide. It is named in Non-Goals below so its absence
reads as a decision, not an oversight.

## Requirements

### R-P1 — The boundary invariant survives this change unchanged

**R-P1.1** After every requirement in this spec is implemented and `rig/results/failure-flood-v1/runs.jsonl`
is re-derived, all three existing rows MUST remain `state=void`. No requirement in this spec MUST cause
any row in that file to become `state=complete`, and no report or artifact produced under this change
MUST present a comparative result, ratio, or count derived from it.

#### Scenario: N stays zero through the re-derive this spec requires

- GIVEN the three rows in `rig/results/failure-flood-v1/runs.jsonl`, each `void_reason=shakedown` today
- WHEN the schema bump and full re-derive required by R-P11 runs
- THEN all three rows remain `state=void`; none acquire `state=complete`; the only permitted changes are
  the pre-scheme marker (R-P8), new digest fields, and the schema version

### R-P2 — Face A: a run records what answer key it was scored against

**R-P2.1** At run time, the system MUST compute and record a digest over the `answer-key/` directory of
**the one fixture root that run ran against** — same convention as the existing
`prereg_digest`/`case_table_digest`/`fixture_digest` fields (computed at run time by the runner, read
back unchanged by `derive.py`). The runner MUST NOT resolve which file carries the row's `task_id`; that
rule stays in `derive.py:665-667` and in no second place (Decision 2).

**R-P2.2** Because the recorded set overlaps `MANIFEST.sha256`'s own coverage of `answer-key/`, a single
edit to `answer-key/prereg.json` or `answer-key/case-table.sha256` mismatches **both** the answer-key
digest (R-P3) and the fixture digest (R-P7). The spec MUST therefore define a deterministic reason
precedence and the implementation MUST follow it, so the same edit never produces a different
`void_reason` depending on check order. **Fixture-digest mismatch takes precedence**, because it names
the broader condition — the fixture as a whole moved — and the answer-key digest mismatch is then a
consequence of it rather than an independent finding. This is the same downgrade-only, first-check-wins
discipline R-P3.2 states; naming the order here is what keeps it from being an accident of line order.

#### Scenario: A run's recorded digest covers its own fixture root only

- GIVEN a run of task `s1`, which runs against fixture root `rig/fixtures/failure-flood/v1`
- WHEN the run completes
- THEN the run's own record carries a digest computed over `v1/answer-key/`, and no file under
  `rig/fixtures/failure-flood/v2/answer-key/` contributes to it

#### Scenario: One edit does not produce two different reasons depending on check order

- GIVEN a run recorded against fixture root `v2`, whose `answer-key/prereg.json` is edited afterwards
- WHEN the row is re-derived, so that both the fixture digest and the answer-key digest mismatch
- THEN `void_reason` is the fixture-digest reason, deterministically, and never varies with the order
  the two checks happen to run in

### R-P3 — Face A: a drifted answer key voids the row, it is never silently rescored as trustworthy

**R-P3.1** At derive time, the system MUST recompute the digest of the current on-disk
`answer-key/<task_id>.json` for a row's `task_id` and compare it to the digest recorded on that row per
R-P2. A mismatch MUST set `state=void, void_reason="answer-key-mismatch"` (Decision 1) and add
`"answer-key-mismatch"` to `anomaly_classes` — never `"surface-mismatch"`, and never a refusal to derive
the whole file (that distinction is R-P12's). This check MUST run before `verdict`, `integrity_guard_pass`,
`causes_claimed`, and `causes_correct` are computed from the (potentially drifted) answer key, so a
mismatched row's scoring fields are never populated from an untrusted key and reported as if trustworthy
— the same before-scoring ordering `suite_state_cause == "environment"` already uses at
`rig/derive.py:976-982`.

**R-P3.2** The mismatch check MUST be downgrade-only: it MUST NOT run, and MUST NOT fire, against a row
whose `state` an earlier check has already set to `void` for a different reason. This is the same
discipline every existing read-back check in `derive.py` already follows (`:839-841`, `:850-862`,
`:976-978`).

#### Scenario: The detector fires — a drifted answer key voids a row that was otherwise complete

- GIVEN a run recorded with a digest of `answer-key/s1.json` as it existed at run time
- WHEN `answer-key/s1.json`'s on-disk bytes change before the next derive, and the row would otherwise
  be `state=complete`
- THEN the re-derive produces `state=void, void_reason="answer-key-mismatch"`, and
  `"answer-key-mismatch"` is in `anomaly_classes`

#### Scenario: An unrelated answer key changing does not touch this row

- GIVEN a run of task `s1`, recorded with a digest of `answer-key/s1.json`
- WHEN `answer-key/s2.json` (a different task's key) changes on disk and `answer-key/s1.json` does not
- THEN the `s1` row's digest comparison still matches and the row is unaffected

#### Scenario: A row already void for another reason is not double-processed

- GIVEN a row already `state=void, void_reason="surface-mismatch"` from an earlier check
- WHEN the answer-key digest comparison runs
- THEN `void_reason` MUST remain `"surface-mismatch"`, never overwritten by `"answer-key-mismatch"`

### R-P4 — `derive.py` stays a total function: no answer-key shape may raise mid-derive

**R-P4.1** `ak["F0"]["failures"]` (`rig/derive.py:981`) and `ak["R0"]` (`rig/derive.py:1071`) MUST NOT
be direct subscripts. An answer key missing either `F0.failures` or `R0` MUST be treated as a scoring
input this deriver cannot trust, not as a crash: the row MUST void with `void_reason="answer-key-mismatch"`
(the same reason as R-P3 — a malformed or incomplete answer key IS an instance of "this row's inputs do
not match a scoreable answer key," not a separate class needing its own reason) rather than raise
`KeyError`.

#### Scenario: A malformed answer key voids the row instead of crashing the whole derive

- GIVEN an answer key file for `task_id=s1` whose JSON is missing the `R0` key entirely
- WHEN derive runs over a run directory for `s1`
- THEN the `s1` row is produced with `state=void, void_reason="answer-key-mismatch"`, no exception
  propagates, and every other run directory's row is still derived and written to the output file

### R-P5 — WARNING-14: two absences, distinguished by a positive marker, neither one forgiven

Corrected in this round. The first pass deferred to a committed self-test asserting
`model_matches_declared: None → state == "complete"` as behavior to preserve. That test does not pin a
constraint — it pins the defect (WARNING-14's own point 1: *"declared X, got nothing" stays open*), and a
spec that defers to a committed assertion **because** it is committed inherits the bug the assertion
happens to encode. Both this section and R-P10 correct that.

**R-P5.1 — a positive marker, not the shared absence, decides "pre-scheme" versus "incomplete".** The
system MUST record `input_provenance_version` (or an equivalent positively-written marker) at run time,
meaning "this run was captured under the provenance scheme this spec introduces." Its absence and a
`None`/`null` value read back from within a scheme-aware capture MUST NOT be conflated: they are
different facts and MUST reach outcomes that differ in `anomaly_classes`, never in whether they are
addressed at all.

**R-P5.2 — pre-scheme capture: no `input_provenance_version` at all.** On an otherwise-`complete` row
whose capture carries no `input_provenance_version`, the row MUST void with `void_reason=
"input-provenance-missing"` and `anomaly_classes` MUST gain `"pre-scheme-provenance"`. A row already
`void` for another reason (including the three existing shakedown rows, R-P8) MUST NOT have its
`void_reason` changed by this rule; it MUST still gain `"pre-scheme-provenance"` in `anomaly_classes` if
it lacks the marker, since that annotation is independent of the state transition (downgrade-only
discipline: the state change requires `state == "complete"`; the annotation does not).

**R-P5.3 — provenance-incomplete capture: marker present, an expected digest recorded as `null`.** On an
otherwise-`complete` row whose capture DOES carry `input_provenance_version` but whose recorded
answer-key, fixture, or surface-preimage digest (R-P2, R-P6, R-P7) is `null`, the row MUST void with the
same `void_reason="input-provenance-missing"`, but `anomaly_classes` MUST gain `"provenance-capture-incomplete"`
instead of `"pre-scheme-provenance"`. The two conditions MUST remain distinguishable by anomaly class —
collapsing them would repeat the exact shape `sdd/run-input-provenance/exploration.md` §2 already records
as the *third* occurrence in this rig of a correct refusal carrying a false stated cause.

**R-P5.4 — the read-back rule itself: not-`True` is not-proven.** At both `rig/derive.py:859`
(`permission_mode_matches_declared`) and `:883` (`model_matches_declared`), the condition MUST change
from "value `is False`" to "value is not `True`", so that a `None` read back from a **scheme-aware**
capture (`input_provenance_version` present) also voids the row, with the existing reason
(`"permission-mode-mismatch"` / `"model-mismatch"` respectively) — because a capture that cannot show
the mode or the model matched has not shown it, and treating that silence as agreement is exactly the
shape this rule exists to remove.

**R-P5.5 — pre-scheme rows are not double-punished by R-P5.4.** For a row with no `input_provenance_version`
at all, R-P5.2's gate MUST run before R-P5.4's read-back check and MUST already have voided the row with
`void_reason="input-provenance-missing"`; R-P5.4's own check MUST NOT be what voids a pre-scheme row, and
MUST NOT independently re-void it under a different reason. Both absences still reach a truthful, voided
outcome; they differ in which gate caught them and in `anomaly_classes`, never in one of them being
silently forgiven.

**R-P5.6** This closes together with R-P2/R-P3 (Face A), per the proposal's ordering: splitting the
read-back distinction from the digest work that motivates it would leave each incomplete without the
other's context.

#### Scenario: A pre-scheme capture voids on the marker's absence, never silently passes

- GIVEN an otherwise-complete run whose capture carries no `input_provenance_version`
- WHEN derive runs
- THEN the row is `state=void, void_reason="input-provenance-missing"`, and `anomaly_classes` contains
  `"pre-scheme-provenance"`

#### Scenario: A scheme-aware capture with a null digest voids, distinguishably from pre-scheme

- GIVEN an otherwise-complete run whose capture carries `input_provenance_version` but whose recorded
  answer-key digest is `null`
- WHEN derive runs
- THEN the row is `state=void, void_reason="input-provenance-missing"`, and `anomaly_classes` contains
  `"provenance-capture-incomplete"`, never `"pre-scheme-provenance"`

#### Scenario: A scheme-aware capture with a `None` read-back now voids, closing WARNING-14's open half

- GIVEN a run whose capture carries `input_provenance_version` and whose
  `permission_mode_matches_declared` reads back `None` (not `False`, not `True`)
- WHEN derive runs
- THEN the row is `state=void, void_reason="permission-mode-mismatch"` — the previously-open "declared X,
  got nothing" case now reaches the same void a "declared X, got Y" mismatch already did

#### Scenario: A pre-scheme row is caught once, by the marker-absence gate, not twice

- GIVEN an otherwise-complete run with no `input_provenance_version` and, incidentally, a `None`
  `model_matches_declared` read-back
- WHEN derive runs
- THEN the row voids exactly once, with `void_reason="input-provenance-missing"` from R-P5.2 — R-P5.4's
  read-back check MUST NOT be what fires, and MUST NOT overwrite that reason with `"model-mismatch"`

#### Scenario: The three existing shakedown rows gain the marker without a state or reason change

- GIVEN the three rows in `rig/results/failure-flood-v1/runs.jsonl`, each `state=void,
  void_reason=shakedown`, none carrying `input_provenance_version`
- WHEN derive runs
- THEN each gains `"pre-scheme-provenance"` in `anomaly_classes`, and each keeps
  `state=void, void_reason=shakedown` unchanged — R-P5.2's void transition never fires against a row
  that is not `state=complete` when the gate is reached

### R-P6 — Face C: the surface comparand is frozen per run, not read live at derive time

**R-P6.1** The value `ff_surface_digest` (`rig/derive.py:849`), compared against each step's own
`surface_sha256` at `:855`, MUST be frozen per run at run time rather than recomputed from the live
`rig/surfaces/` preimage at derive time. The run already carries its own side of this comparison
(`step["surface_sha256"]`); this requirement freezes the comparand, adding no new capture.

**R-P6.2** The `if ff_surface_digest is not None and ...` guard's current behavior — silently not firing
the `surface-mismatch` void when the live preimage cannot be read — MUST NOT persist unchanged once the
comparand is frozen per run: a frozen comparand recorded at run time is either present (from that run's
own recording) or its absence is itself informative, and MUST NOT be conflated with "the comparison was
attempted and passed."

#### Scenario: A frozen comparand still detects surface drift after this change

- GIVEN a run recorded with a frozen surface-preimage digest matching the preimage at run time
- WHEN the live `rig/surfaces/failure-flood.txt` preimage changes before the next derive
- THEN the frozen comparand (not the live, now-different one) is what the row's own `surface_sha256` is
  compared against, and the row's classification is unaffected by the unrelated live-file change

### R-P7 — Face B: identity only, plus the honest claim boundary this forces

**R-P7.1** `fixture_digest` (`rig/derive.py:611-617`, `:1016`) MUST be recorded at run time as the run's
own digest of the fixture manifest it ran against, rather than remaining the present-derived value
re-read from the live tree on every derive.

**R-P7.2** Any report or artifact under this change that cites R-F5.3 (from the archived
`failure-flood-triage` spec) MUST state explicitly that R-F5.3's byte-identical re-derive check verifies
**deriver drift**, never **fixture drift** — because a re-derive re-reads the same live manifest and
necessarily agrees with itself. This is a documentation obligation forced by Face B's identity-only
nature, not a code behavior change beyond R-P7.1.

#### Scenario: The report cannot claim R-F5.3 covers fixture drift

- GIVEN a report artifact produced under this change that references R-F5.3
- WHEN it describes what R-F5.3 verifies
- THEN it MUST name deriver-drift verification only, and MUST NOT describe or imply fixture-drift
  coverage

### R-P8 — The three existing rows are marked pre-scheme, never deleted or promoted

**R-P8.1** After the full re-derive this change requires, all three rows currently in
`rig/results/failure-flood-v1/runs.jsonl` MUST gain `"pre-scheme-provenance"` in `anomaly_classes`
(Decision 1). Their `state` MUST remain `void` and their `void_reason` MUST remain `shakedown`,
unchanged.

**R-P8.2** No mechanism introduced by this change MUST delete, re-record, or promote any of the three
rows toward `state=complete`. They predate every digest this spec introduces; there is nothing to compare
them against, and voiding them under a Face A/B/C mismatch reason would misrepresent absence-of-provenance
as detected drift.

#### Scenario: The three rows gain the marker and nothing else changes about their state

- GIVEN the three existing rows, each `state=void, void_reason=shakedown`
- WHEN the full re-derive required by R-P11 runs
- THEN each of the three rows carries `"pre-scheme-provenance"` in `anomaly_classes`, and each remains
  `state=void, void_reason=shakedown`

### R-P9 — Task 7.15 is retired; three ordered siblings replace it

**R-P9.1** Task 7.15, as registered in the archived `failure-flood-triage` cycle, MUST be retired with
its retirement reason recorded (its wording named only the identity field and verify round 4 judged that
registration inadequate). It MUST be replaced by exactly three sibling tasks/deliverables covering,
respectively: Face A together with the WARNING-14 read-back distinction (R-P2, R-P3, R-P4, R-P5); Face C
(R-P6); and Face B together with the R-F5.3 claim-boundary statement (R-P7).

**R-P9.2** The three siblings MUST be delivered in this order: **Face A + WARNING-14, then Face C, then
Face B.** The ordering is itself a requirement of this spec, not an implementation note, because a
delivery that reaches Face B first and stops there reproduces exactly the failure this re-scope exists
to correct (closing the identity-only field while the scoring-path face stays open under a green
checkmark).

#### Scenario: Declaring Face B done first does not close the class

- GIVEN a delivery that implements only R-P7 (Face B) and none of R-P2/R-P3/R-P4/R-P5 (Face A +
  WARNING-14) or R-P6 (Face C)
- WHEN that delivery is checked against this spec
- THEN it MUST NOT be reported as satisfying this spec's requirements, and R-P9.2's ordering MUST be
  cited as the reason

### R-P10 — Each new detector MUST be proven able to fire, not merely proven not to break

**R-P10.1** Per ADR 0013 and the existing `derive.py` self-test precedent, every detector this spec
introduces or changes (R-P3's answer-key-mismatch void, R-P4's malformed-answer-key void, R-P5's `None`
distinction, R-P6's frozen-comparand mismatch) MUST have a `--self-test` case that constructs an input
proving the detector actually fires on a deliberately mismatched/malformed input — not only a case
showing it passes on clean input. This mirrors the existing `_self_test_build_row_model_mismatch()`
pattern (`rig/derive.py:1238-1275`), which proves both the mismatch case AND the no-false-positive case
for an old capture.

#### Scenario: The answer-key-mismatch detector is proven to fire, not just proven silent on clean input

- GIVEN a self-test case constructing a run whose recorded digest deliberately does not match the
  current on-disk answer key
- WHEN `--self-test` runs
- THEN it asserts `state == "void"` and `void_reason == "answer-key-mismatch"` for that constructed case,
  and FAILS the self-test if the detector does not produce that outcome

**R-P10.2** `_self_test_build_row_model_mismatch()`'s case 3 (`rig/derive.py:1260-1270`) — currently
labelled `"model_matches_declared absent/None (old capture) -> never falsely voids"` and asserting
`state == "complete"` — asserted the pre-R-P5 behavior directly. It MUST be **rewritten, not deleted**:
deleting it would erase the evidence that "absence is consent" was ever asserted as intended behavior;
rewriting it records the inversion R-P5 makes. Its rewritten form MUST construct the same fixture with no
`input_provenance_version` and assert `state == "void", void_reason == "input-provenance-missing"`
(R-P5.2). A **new**, additional case MUST be added covering a provenance-**intact** run (
`input_provenance_version` present) whose `model_matches_declared` reads back `None`, asserting
`state == "void", void_reason == "model-mismatch"` (R-P5.4). Together the rewritten case and the new
case are the WARNING-14 proof: the same `None` read-back reaches a different, correctly-distinguished
void depending on whether the marker is present, and neither path silently passes.

#### Scenario: The inverted self-test proves both halves of WARNING-14, not just one

- GIVEN the rewritten case 3 (no `input_provenance_version`, `model_matches_declared=None`) and the new
  provenance-intact case (`input_provenance_version` present, `model_matches_declared=None`)
- WHEN `--self-test` runs both
- THEN the rewritten case asserts `void_reason == "input-provenance-missing"` and the new case asserts
  `void_reason == "model-mismatch"` — a self-test that only kept one of the two would leave the other
  half of WARNING-14 unproven

### R-P11 — Schema bump and full re-derive, no-migrations rule

**R-P11.1** The new fields this spec requires (the recorded digests from R-P2/R-P6/R-P7, and any
`anomaly_classes` additions) MUST land as an additive schema-version bump, following the same
no-migrations rule already established for `derive.py`'s prior version bumps (v2→v3): re-deriving
rewrites every existing row with the new schema version and the new fields; nothing reads the old
`schema_version` value to special-case a row's treatment.

**R-P11.2** Corrected in this round: a single "every existing row" projection is not achievable, because
`checker_digest` (`rig/derive.py:82`) is `sha256` of `derive.py`'s own bytes and is stamped on the rows of
**both** experiments this file derives — `tool-surface-v1` (`:530`) and `failure-flood-v1` (`:1017`). Any
edit to `derive.py` necessarily changes `checker_digest` on all 42 `tool-surface-v1` rows as well as the
three `failure-flood-v1` rows, so the guarantee MUST be stated as two separate, explicit projections, one
per experiment/dataset, rather than one ambiguous claim scoped to "every row":

- **`tool-surface-v1` (42 rows):** re-deriving MUST produce a byte-identical projection of every row's
  fields, excluding only `checker_digest`. `schema_version` MUST remain unchanged (this spec touches no
  key `build_row`'s registry entry reads). Any other delta is a defect, not an expected difference.
- **`failure-flood-v1` (3 rows):** re-deriving MUST produce a byte-identical projection of every row's
  fields, excluding `schema_version` (the bump this spec requires), `checker_digest`, `anomaly_classes`
  (gains `"pre-scheme-provenance"` per R-P5.2/R-P8), and the fields this spec newly adds (R-P2, R-P6,
  R-P7, R-P5's marker). Any other delta is a defect, not an expected difference.

Neither projection is weakened by naming `checker_digest`'s exclusion; naming it precisely is what makes
the remaining guarantee verifiable instead of aspirational.

#### Scenario: The re-derive changes only what this spec says it may change, per experiment

- GIVEN the 42 `tool-surface-v1` rows and the 3 `failure-flood-v1` rows, all fully re-derived under the
  new schema version
- WHEN each dataset's fields are compared against its own pre-change values, using that dataset's own
  named projection above
- THEN every remaining field in both datasets is byte-identical to its pre-change value, and
  `tool-surface-v1`'s `schema_version` is unchanged

### R-P12 — Refusal-to-derive and per-row voiding are distinct, non-conflicting behaviors

**R-P12.1** The existing self-test-failure refusal at `rig/derive.py:1468-1470` MUST remain an
all-or-nothing refusal: when `run_self_tests()` fails, no rows MUST be derived for any run, because no
detector in the file can be trusted. This spec MUST NOT weaken or bypass that refusal.

**R-P12.2** A Face A/B/C provenance mismatch on one row MUST NOT trigger that same all-or-nothing
refusal. It MUST void only the affected row (R-P3, R-P6) while every other run directory's row derives
normally, per `derive.py`'s existing total-function contract.

#### Scenario: An unproven deriver still refuses everything, unrelated to any single row's provenance

- GIVEN a deliberately broken detector such that `run_self_tests()` fails
- WHEN `derive.py` runs, regardless of whether any run's answer-key digest matches or mismatches
- THEN the run exits 1 with the self-test-failure message and writes no rows at all

#### Scenario: A single row's provenance mismatch derives everything else normally

- GIVEN one run directory whose recorded answer-key digest mismatches the current on-disk key, and three
  other run directories whose digests all match
- WHEN `derive.py` runs and `run_self_tests()` passes
- THEN the mismatched run's row is `state=void, void_reason="answer-key-mismatch"`, and the three other
  rows derive to whatever state their own inputs produce, unaffected

## Non-Goals

| Excluded from this spec | Why |
|---|---|
| Face D — `CHECKER_DIGEST` (`rig/derive.py:82`) | Declared, not a defect: R-F5.3's own scenario already excludes it from the byte-identity projection |
| `rig/check.sh` composing `rig/run-pipeline.sh --self-test` | Real adjacent gap (`check_component_self_test()` has no bash arm), named per Decision 3, left to its own cycle |
| Re-scoring or re-deriving the three existing rows into countability | R-P8 marks them; nothing promotes them |
| Any comparative result, table, or ratio | N = 0 by arithmetic (R-P1), not by choice |
| A test framework or `tests/` directory | `decisions/0013-a-committed-executable-carries-its-own-test.md` still holds; every new detector self-tests via the existing `--self-test` flag (R-P10) |

## Key Learnings

1. Every existing mismatch `void_reason` in `derive.py` is paired with an identical `anomaly_classes`
   member — `"answer-key-mismatch"` (Decision 1) follows that same pairing rather than inventing a new
   convention.
2. **Corrected during gatekeeping.** The first pass chose a per-consumed-key digest on precision
   grounds. The deciding constraint is not precision but where a rule lives: the runner is bash and sees
   one fixture root, so per-key would reimplement `derive.py:665-667`'s `task_id`-not-filename rule in a
   second language. The precision objection it was chosen for turned out to be already answered —
   `answer-key/prereg.json` and `answer-key/case-table.sha256` are covered by `MANIFEST.sha256` and
   therefore by Face B already, so a set-wide digest is redundant there rather than blind.
3. **Corrected in this round.** The first pass treated the committed self-test
   (`"model_matches_declared absent/None (old capture) -> never falsely voids"`, `rig/derive.py:1260-1270`)
   as a constraint to preserve, which meant deferring to a committed assertion because it was committed —
   the same failure mode this cycle exists to correct, since the assertion pins "absence is consent" as
   intended behavior rather than naming it as the defect. The read-back gap at `:859`/`:883` is
   resolvable without either forgiving `None` forever or voiding every old capture: a positive marker
   (`input_provenance_version`) distinguishes "predates the scheme" from "captured under the scheme but
   incomplete," and both absences now void — differing in `anomaly_classes`, not in whether either is
   addressed (R-P5).
4. "Refuse to derive" (`:1468-1470`) and "void one row" (this spec's mismatch handling) answer different
   questions — whether the deriver itself is trustworthy, versus whether one row's own inputs are — and
   are not in conflict once stated that way.
5. `checker_digest` is stamped on **both** experiments' rows from one shared constant
   (`rig/derive.py:82`, read at `:530` and `:1017`), so "byte-identical beyond the intended fields" is
   only a verifiable claim when stated as two separate per-experiment projections (R-P11.2) — one
   ambiguous "every row" projection would have sent verification chasing a delta `checker_digest` was
   always going to produce.
