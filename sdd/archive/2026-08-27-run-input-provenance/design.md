---
id: sdd/run-input-provenance/design
type: journal
targets: [any]
status: draft
verified: 2026-08-19
sources: ["sdd/run-input-provenance/proposal.md", "sdd/run-input-provenance/exploration.md", "sdd/archive/2026-08-18-failure-flood-triage/design.md", "rig/derive.py", "rig/run-pipeline.sh", "rig/check.sh", "rig/README.md", "rig/results/failure-flood-v1/runs.jsonl", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "decisions/0015-a-fixtures-runtime-is-substrate-not-this-repos-runner.md", "MAP.md", "skills/hypothesis-cycle/SKILL.md"]
---

# run-input-provenance — design: a row records what it was scored against, and absence is never consent

SDD design phase for `run-input-provenance`. Architecture and decisions only. No spec, no task
breakdown, no implementation. `spec.md` is authored in parallel and is not touched here.

## The boundary, before anything else

The `failure-flood-triage` cycle delivered **an instrument and a FAILED ratio target — never a
comparative result.** Re-verified in the file, not accepted from any report: every row in
`rig/results/failure-flood-v1/runs.jsonl` carries `state: "void"`, `void_reason: "shakedown"`,
`anomaly_classes: []`, `schema_version: 3`. Three rows. **N = 0 countable rows.**

No decision, diagram or field below implies a comparative result exists, is pending, or is nearly
available. Every defect this design closes is harmless **today precisely because there is no number
to be wrong**, and serious the moment there is one. The data flow at the end of this document
terminates at `runs.jsonl` for that reason: there is nothing downstream of it to draw.

## Technical approach

**One rule, applied at three sites, adding no new mechanism.**

> A run records a digest of every input it was scored against, at the moment it is scored against
> it. The deriver compares the recorded digest to the live one. Disagreement voids that row.
> Absence of a recorded digest is treated as not-proven, never as agreement.

The change is confined to `build_row_failure_flood` (`rig/derive.py:793`) and to
`rig/run-pipeline.sh`'s existing recording sites. `build_row` — `tool-surface-v1`'s row builder at
`rig/derive.py:410` — gains no line, and its registry entry (`:1079-1089`) gains no key. Section 7
states how that is guaranteed mechanically rather than promised.

Three faces, from the proposal, in its settled order: **Face A + WARNING-14 → Face C → Face B.**

## 1. Where each digest is recorded, and why one of them is not in `arm.json`

**The rule: record at the granularity of the comparison the value feeds, at the site that already
reads the thing being digested.**

| Value | Artifact | Recording site | Why there |
|---|---|---|---|
| `recorded_answer_key_digest` | `arm.json` | immediately after the MANIFEST gate (`run-pipeline.sh:645-649`) | One fixture root per arm; the deriver consumes one key per row. The gate has just proved these bytes match the frozen manifest, so the digest is taken over bytes already proven frozen |
| `recorded_fixture_digest` | `arm.json` | same block | Arm-level identity. Sits beside `case_table_digest` and `prereg_digest` (`:1086-1088`), which are already carried this way |
| `recorded_surface_preimage_sha256` | **per-step `status.json`** | `run_model_step`'s existing preimage check (`:857-860`) | **The only one that is not arm-level.** It is the comparand for a *per-step* comparison against `surface_sha256`, which `write_step_status` already writes per step (`:810`) and which `derive.py:851-855` already compares per step. A three-step arm has three invocations and the preimage file can change between them |
| `input_provenance_version` | `arm.json` | the arm.json writer (`:1080-1102`) | It describes the capture scheme of the run as a whole, not one step |

`arm.json` is assembled once at the end of the arm (`run-pipeline.sh:1103`), so the two arm-level
digests are held in shell variables from preflight until then — the exact lifetime `PREREG_DIGEST`,
`CASE_TABLE_DIGEST` and `LOCKFILE_SHA256` already have. A run that aborts before that write has no
`arm.json`; `build_row_failure_flood:799-806` reads `arm_data = {}` and the row is already `void`, so
the provenance gate never fires against it. No new abort path.

### Two of the three faces add no new digest algorithm

| Face | Runner side | Deriver side |
|---|---|---|
| **B — fixture** | `sha256` of `MANIFEST.sha256`'s bytes, using the one-liner idiom already at `run-pipeline.sh:677` | `fixture_digest_at()` (`derive.py:611`) — unchanged, already this exact value |
| **A — answer key** | the answer-key relpaths from `compute_manifest` (`:168` already walks `answer-key`), piped into the existing `hash_paths` (`:215`) | a new `answer_key_set_digest(root)` helper mirroring `fixture_digest_at`'s shape, reproducing `hash_paths`' convention |
| **C — surface preimage** | a new `preimage_digest()` function, reproducing `load_surface`+`surface_digest` (`derive.py:89-99`) | `surface_digest(load_surface(...))` — unchanged, already computed at `:848-849` |

**Exactly one genuinely new algorithm is introduced (`preimage_digest`), and exactly two
cross-language digest agreements are created** (answer-key set; surface preimage). Section 6 says how
each is pinned. This is precedent, not invention: `read_back_init` and `surface_digest` are already
such a pair, pinned by a shared constant at `run-pipeline.sh:424-430`.

### Face A is not redundant with Face B, and the reason is sharp

`answer-key/` is inside the manifest (`run-pipeline.sh:168`), so a matching `recorded_fixture_digest`
looks like it should already prove the answer keys are unchanged. It does not.
`fixture_digest_at()` hashes **the `MANIFEST.sha256` file** — a *claim about* the fixture bytes. The
recompute-compare that verifies the claim against the actual files runs in `run-pipeline.sh:645-649`
and **only at run time**; the deriver never re-verifies it. An answer-key file edited together with
its manifest line would leave `fixture_digest` moving (caught), but an answer-key file edited while
the `MANIFEST.sha256` bytes are held fixed is invisible to Face B at derive time.

So Face A's digest must be taken over **the actual answer-key file bytes**, on both sides. That is
what justifies the second cross-language implementation, and it is why Face A cannot be folded into
Face B for cheapness.

## 2. Answer-key digest granularity: set-wide per fixture root, not per consumed key

The proposal left this open. The deciding constraint is not cost — it is that
`load_failure_flood_answer_keys()` (`derive.py:646-668`) **merges every fixture root into one dict**,
while a run only ever ran against one root. A set-wide digest computed by the runner over its own
root is not comparable to a digest over the merged set.

| Option | Tradeoff | Decision |
|---|---|---|
| One digest over the merged answer-key set | Not computable by a runner, which sees one root. The comparison would be structurally impossible | Rejected |
| One digest per consumed key | Most precise. But the runner must resolve *which* file carries this `task_id` before the deriver does, duplicating the `task_id`-not-filename rule (`:665-667`) in bash | Rejected — a second place for one rule to drift |
| **Set-wide, per fixture root** | Voids on a change to a key the row did not consume | **Chosen** |

It mirrors `digests["fixture"]` exactly: a `{version: digest}` map built per root in `main()`
(`:1473-1476`), indexed by the row's own `fixture_version` (`:985`). Today the two options coincide —
`FAILURE_FLOOD_FIXTURE_VERSIONS` (`:633`) maps `s1→v1` and `s2→v2`, one task per root — so the
over-voiding is currently empty. It only appears if a root ever gains a second task's key, and then
it errs toward `void`, which is the safe direction under downgrade-only discipline.

## 3. Totality is preserved by keeping two failure surfaces apart

`derive.py` has **two distinct refusal modes and this design merges neither.**

| Surface | Meaning | Effect | Where |
|---|---|---|---|
| `run_self_tests(answer_keys)` returns false | **The deriver is unproven** — a detector cannot be shown to fire | `main()` returns 1, **no rows are written at all** | `:1468-1470`, untouched |
| A provenance comparison disagrees | **One observation is untrustworthy** | that row alone downgrades to `void`; every other row is still written | new, inside `build_row_failure_flood` |

The provenance gate never raises, never returns non-zero, never upgrades a state, and never
short-circuits the run loop at `:1481-1484`. `build_row_failure_flood` remains a total function from
run directories to rows. Collapsing the two would mean one drifted fixture blocks the entire report —
the alternative the proposal already rejected.

### The unguarded subscripts, fixed to the existing precedent rather than a new one

`ak["F0"]["failures"]` (`:981`) and `len(ak["R0"])` (`:1071`) raise `KeyError` mid-derive. The
existing precedent for an unscoreable row is already stated at `:987-994`: when no answer key exists,
`verdict`, `integrity_guard_pass`, `causes_claimed` and `causes_correct` stay `None` and the row is
**not** voided. A *malformed* answer key follows the same precedent — `.get()` throughout, scored
fields left `None`, no new void vocabulary.

One precision that is not cosmetic: `causes_present` must become `None` when `R0` is absent, never
`0`. `len(ak.get("R0", []))` would publish `0`, which is a claim that this task has zero causes.
Absence is not a count. The rule is `len(ak["R0"]) if ak and "R0" in ak else None`.

**Explicitly not decided here:** whether a `complete` row with null scored fields is countable. That
predates this change and the proposal does not scope it. Recorded as an open question rather than
settled in passing.

## 4. Two void reasons, three anomaly classes, and why that split is not over-engineering

The settled decision is one dedicated `void_reason` for mismatch. Absence needs its own, and the
justification is measured rather than aesthetic.

| `void_reason` | Fires when |
|---|---|
| `input-provenance-mismatch` | a recorded digest is present and disagrees with the live value |
| `input-provenance-missing` | the row cannot say what it was scored against at all |

Collapsing the second into the first would produce **a correct refusal carrying a false stated
cause**. That is not hypothetical: `exploration.md` §2 records it as the *third* occurrence of that
exact shape in this rig — most recently a `check_prereg` guard removal that still exited 2 while the
next guard relabelled it `tracked_but_dirty`, leaving the refusal correct and its reason wrong. A
design that manufactures a fourth occurrence to save one string is not minimal.

`anomaly_classes` carries the diagnosis, at no cost to the state machine (it is already a sorted list
on every row, `:1073`):

| Class | Meaning |
|---|---|
| `answer-key-drift` / `fixture-drift` / `surface-preimage-drift` | which face disagreed, under the single `input-provenance-mismatch` reason |
| `pre-scheme-provenance` | `input_provenance_version` absent — the capture predates this scheme |
| `provenance-capture-incomplete` | version present, a digest `null` — the capture claimed to record and did not |

Rejected: a per-face `void_reason`. The face belongs in the diagnosis, not the state.

**Corrected during gatekeeping — this decision stands, its original justification does not.** The
argument first given here was that three reasons "inflate the vocabulary every consumer must implement,
and `report.py` already names voids by reason." That was listed in this design's own risk section as
asserted-not-verified, and verification refuted it: `rig/report.py` is **reason-agnostic**. It collects
whatever string a row carries (`classes.add(r["void_reason"])`, `:125-126`) and interpolates it (`:163`,
`:335`). There is no enum, no hardcoded list, no per-reason branch, so three reasons would have cost
`report.py` nothing.

The decision survives on a stronger argument that neither this design nor `spec.md` originally stated:
`answer-key/` sits inside `compute_manifest()`'s walked set, so a single edit to
`answer-key/prereg.json` disagrees on the answer-key digest **and** the fixture digest at once. A
per-face reason forces the one `void_reason` slot to choose between two true findings, which means
defining a precedence rule and discarding the loser. One reason plus `answer-key-drift` / `fixture-drift`
records both, and the outcome stops depending on which check ran first. `spec.md` R-P2.2/R-P2.2a carry
this, and R-P2.2a explicitly forbids reintroducing a per-face reason plus a precedence rule to arbitrate
it.

## 5. Backward compatibility: `input_provenance_version` is the positive marker, and this is where WARNING-14 could reappear

**The hazard, named first.** WARNING-14 is `None` read as consent. A provenance scheme that infers
"this run predates the scheme" from *the same absence* a destroyed capture leaves behind commits that
identical error one layer up — and would do it while claiming to fix it.

The distinction must therefore be carried by something **positive**, written by a runner that has the
scheme. `input_provenance_version: 1` in `arm.json` is that marker, the same shape `schema_version`
already has on the row.

| Observed | Diagnosis | State effect |
|---|---|---|
| `input_provenance_version` absent | pre-scheme capture. `pre-scheme-provenance` | if `complete` → `void: input-provenance-missing`. Already-`void` rows keep their reason |
| version present, digest `null` | capture destroyed / truncated / never written. `provenance-capture-incomplete` | same |
| version present, digests present, disagree | drift. `<face>-drift` | `void: input-provenance-mismatch` |
| version present, digests present, agree | provenance proven | no change |

Neither absence is consent: both reach `void`. They differ in `anomaly_classes`, which is exactly the
"correct refusal, correct stated cause" property section 4 exists to protect.

### What this does to the three recorded rows

Nothing to their state, by construction. The gate runs inside the existing `if state == "complete":`
block (`:850`), and all three rows are already `void` with `void_reason: "shakedown"` before it is
reached. They gain `pre-scheme-provenance` in `anomaly_classes` and the new fields as `null`. They are
never deleted, never re-stamped, never promoted. Settled decision 2, satisfied without a special case
in the code.

## 6. Ordering inside the deriver, and how Face C's guard is retired

The provenance gate runs **first**, before the per-step read-back loop at `:851-886`.

The argument is the same one as section 4. If the comparands are untrustworthy, then the
`surface-mismatch` verdict computed *from* them is untrustworthy too, and stamping `surface-mismatch`
on a row whose preimage provenance is broken is once again a correct refusal with a false cause.

This is what lets Face C's guard be tightened safely, and the ordering constraint in the proposal
(Face A + WARNING-14 must land before Face C) becomes mechanical rather than a convention:

| Before | After |
|---|---|
| `if ff_surface_digest is not None and step_surface != ff_surface_digest` (`:855`) — a live-tree `None` silently disables the whole surface-mismatch void | unconditional comparison against `step["recorded_surface_preimage_sha256"]`. A `null` recorded preimage is `provenance-capture-incomplete` and was already voided by the earlier gate, so the loop is never reached with a missing comparand |

The `is not None` guard is **deleted, not weakened**. Its job has been taken over by a check that runs
earlier and states its own cause. The live preimage digest is still computed, but only as the
provenance comparand, never as the step comparand — which is what "freeze the comparand per run"
means in code.

### WARNING-14's read-back half

Both downgrades are written `is False` (`:859`, `:883`). The rule becomes **not-`True` is
not-proven**: a read-back that is `None` voids with its existing reason
(`permission-mode-mismatch` / `model-mismatch`), because a capture that cannot show the mode or the
model matched has not shown it.

**This inverts a committed test row, and that row must be inverted rather than left standing.**
`_self_test_build_row_model_mismatch` case 3 (`derive.py:1260-1270`) asserts
`model_matches_declared: None` → `state == "complete"`, labelled *"old capture → never falsely
voids"*. Under this design that assertion pins the defect as intended behaviour. It is rewritten,
not deleted: with no `input_provenance_version` the same fixture must reach
`void: input-provenance-missing`, and a **new** case with provenance intact and
`model_matches_declared: None` must reach `void: model-mismatch`. Those two cases together are the
WARNING-14 proof.

## 7. `tool-surface-v1` non-regression, guaranteed mechanically

The prior cycle's own constraint was that `build_row` is *"not restructured, not renamed, not
re-signatured"* (`derive.py:606-609`). Three properties keep that true, each checkable by reading the
diff rather than by trusting this document.

| Property | Evidence |
|---|---|
| `build_row` reads only two keys of `digests` | `:529-530` — `digests["fixture"]` and `digests["checker"]`. Adding a third key is invisible to it |
| The new digest is built only when an experiment declares it | `main()` builds `digests["answer_key"]` behind `reg.get("answer_key_digest")` (`:1473-1476`). The `tool-surface-v1` registry entry (`:1079-1089`) gains **no key** and is byte-unchanged |
| Every new comparison lives inside `build_row_failure_flood` | `:793-1075`. No shared helper on the `build_row` path is modified; `surface_digest`, `load_surface` and `fixture_digest_at` keep their signatures and behaviour |

**The honest caveat, which the proposal's risk table understates.** `checker_digest` is
`sha256` of `derive.py`'s own bytes (`:82`) and is stamped on every row of **both** experiments
(`:530`, `:1017`). Editing `derive.py` therefore *necessarily* rewrites `checker_digest` on all 42
`tool-surface-v1` rows and on the three `failure-flood-v1` rows. "Byte-identical beyond the intended
marker" is unachievable and would send the verification phase chasing a phantom — the same correction
the prior cycle recorded as its correction 5. The verifiable claims are projections:

> **`tool-surface-v1`:** re-derive; project out `checker_digest`. Every remaining byte is identical
> across all 42 rows. `schema_version` stays 3.
>
> **`failure-flood-v1`:** re-derive; project out `schema_version`, `checker_digest`, the four new
> fields and `anomaly_classes`. Every remaining byte is identical across all three rows, and each
> still reads `state: "void"`, `void_reason: "shakedown"`.

## 8. The schema bump, and what re-deriving must produce

`FAILURE_FLOOD_SCHEMA_VERSION` goes **3 → 4** (`:621`). `tool-surface-v1`'s schema is untouched — the
two-schema rule in `rig/README.md` is what makes that possible, and it is the reason a shared superset
schema was rejected by the prior cycle.

**No migrations.** The prior cycle's rule (its Decision 8, restated in the comment at `:630-631`) is
that re-deriving rewrites every existing row with the new version and the new fields. There is no
upgrade path, no dual-read, and no code that understands a v3 row. Rows are rebuilt from raw captures,
which is the property that makes a bump a rebuild rather than a migration.

Re-deriving the three existing rows must produce exactly:

| Field | Value |
|---|---|
| `schema_version` | `4` |
| `input_provenance_version` | `null` |
| `recorded_answer_key_digest` / `recorded_fixture_digest` | `null` |
| each model step's `recorded_surface_preimage_sha256` | `null` (steps are copied through by `step_out = dict(step)` at `:899`, so this needs no deriver code) |
| `anomaly_classes` | `["pre-scheme-provenance"]` |
| `checker_digest` | a new value — expected, see section 7 |
| `state` / `void_reason` | `"void"` / `"shakedown"` — unchanged |
| everything else | byte-identical |

Any other delta is a defect, not an expected diff.

**`rig/README.md` is stale and must be corrected as part of this.** It states `failure-flood-v1`'s
`schema_version` is **1**; the code has said **3** since the CRITICAL-1/-2 bump. The bump to 4 lands
in the same edit, and the staleness is named rather than quietly overwritten.

## 9. Proving each new detector can fire (ADR 0013)

Every detector reuses machinery that already exists: `derive.py --self-test` (roster at `:1420-1428`)
and `run-pipeline.sh --self-test` (`:353`), the latter added at `a2cbd6f`.

### `derive.py --self-test` — one new function, registered in the roster

Built on `_self_test_make_ff_run_dir` (`:1216-1235`), which already synthesises an `arm.json` +
`status.json` + one model step and calls `build_row_failure_flood` directly. It gains the provenance
fields; its three existing callers gain them too, which is intended — it forces every existing
detector fixture to carry provenance and proves the new gate **composes** with the old ones rather
than sitting beside them.

| # | Case | Why it exists |
|---|---|---|
| 1 | all digests agree → `state: "complete"` | **The negative control. A gate that always voids passes every other case here.** This is the one that gets skipped |
| 2–4 | answer-key / fixture / preimage digest differs → `void: input-provenance-mismatch` with `answer-key-drift` / `fixture-drift` / `surface-preimage-drift` | one per face |
| 5 | `input_provenance_version` absent → `void: input-provenance-missing`, `pre-scheme-provenance` | section 5 |
| 6 | version present, a digest `null` → `void: input-provenance-missing`, `provenance-capture-incomplete` | section 5. Cases 5 and 6 must reach **different** anomaly classes, or the two absences have been conflated after all |
| 7 | provenance broken **and** a genuine surface mismatch → stamps `input-provenance-mismatch`, never `surface-mismatch` | **The ordering proof (section 6), and the other case that gets skipped.** Without it, the correct-refusal-wrong-cause regression is undetectable |
| 8 | provenance intact, `permission_mode_matches_declared` / `model_matches_declared` `None` → voids | WARNING-14, both sites |
| 9 | `ak` missing `F0` and `R0` → no exception; `verdict` `None`, `causes_present` `None` (**not** `0`) | totality, section 3 |
| 10 | an already-`void` shakedown row with no provenance → keeps `void_reason: "shakedown"`, gains `pre-scheme-provenance` | the three committed rows, proven rather than asserted |

### `run-pipeline.sh --self-test` — the new extractable function

`preimage_digest` is the only new algorithm, and ADR 0013's rule as restated in this file's own header
(`run-pipeline.sh:333`) is that *every* extractable function belongs in the suite.

| # | Case |
|---|---|
| a | dedupe + sort, `# harness:` header and blank lines excluded, against a **pinned constant** |
| b | a preimage with no tool lines yields an *absent* digest, not an empty string that reads like a value — WARNING-14's shape at the recording end. `read_back_init`'s empty-field cases (`:432-443`) are the existing precedent |
| c | a missing preimage file still reaches `missing-surface-preimage` (`:857-860`); provenance never masks that abort |

### The cross-language pins, and their hazard

Two digests are implemented twice, in two languages. Each is pinned by **the same literal constant
over the same synthetic input, asserted in both self-tests** — the mechanism already used for
`surface_digest` at `run-pipeline.sh:424-430`. It proves agreement only while both sides pin the same
pair; editing one side alone makes the other fail, which is the point. **Whoever hits that failure
must not "fix" the failing side to match — the disagreement is the finding.**

### The honest weakness in this proof

`rig/check.sh`'s `check_component_self_test()` runs `python3 <script> --self-test` and **has no bash
arm**, so `run-pipeline.sh --self-test` is never composed by the repo gate. The bash cases above are
therefore proven able to fire but run only by hand. The proposal names this as out of scope and this
design does not fix it — it states the consequence rather than letting a green `check.sh` imply
coverage it does not have.

## The ADR question — answered, and the numbering hazard named explicitly

**Recommendation: no new ADR. The decision this change implements is already ratified.**

ADR 0011 (`decisions/0011-rig-produces-evidence-not-truth.md`) settles that raw captures stay local,
and accepts that consequence on one stated ground: *"the row carries the digests that prove which
configuration produced it"*. For the answer key, the surface comparand and the run's own fixture
identity, **that sentence is currently false** — which is precisely what this change repairs. Writing
a new ADR to decide something an existing ratified ADR already decided would be a record of work, not
a decision.

The two neighbouring ADRs are also already sufficient: 0013 supplies the `--self-test` obligation
section 9 discharges, and 0015 fixes the fixture/repo boundary this change does not move.

**If the operator wants "absence of provenance is never consent" ratified as a repo-wide rule**, that
is a genuinely new claim, wider than `rig/`, and it deserves its own cycle rather than being smuggled
in as a side effect of a schema bump. It is recorded here as a candidate, not reserved.

### The numbering hazard, stated rather than assumed

Verified by listing `decisions/` on this branch: `0001`–`0015` exist. `MAP.md:43` records `0001`–`0013`
and `0015` ratified, `0014` draft. **The next free number on this branch is `0016`.**

That number must not be reserved now, and the risk is documented history rather than caution:
`rig/README.md:77-78` records that this cycle's predecessor ratified an ADR as `0014`, collided with
`main`'s own already-public `0014`, and had to renumber to `0015` in PR7D — a full verification round
spent unwinding it. `main` is checked out in a **separate worktree** and another session is working on
`feat/open-work-index`, so `decisions/` can gain a `0016` under this branch at any time.

**If an ADR is written at all, the number is claimed in the same commit that writes the file, after
re-listing `decisions/` in the `main` worktree — never assigned during design.**

## Data flow

Only the provenance path is drawn. Nothing downstream of `runs.jsonl` appears, because nothing
downstream of it exists to draw: N = 0.

```
rig/fixtures/failure-flood/<version>/
   MANIFEST.sha256 · answer-key/*.json · (src tests runtime tools prompts)
        │
        │  run-pipeline.sh preflight
        │    MANIFEST recompute-compare ──► exit 2 on mismatch          [:645-649]
        │    ▼ bytes now proven frozen
        │    recorded_fixture_digest      = sha256(MANIFEST.sha256)      [idiom at :677]
        │    recorded_answer_key_digest   = hash_paths(answer-key/*)     [:215]
        │
rig/surfaces/failure-flood.txt
        │    per model step, at the existing existence check             [:857-860]
        │    recorded_surface_preimage_sha256 = preimage_digest(file)   ──► steps/<n>/status.json
        ▼
rig/runs/failure-flood-v1/<run_id>/            (gitignored — ADR 0011)
   arm.json : input_provenance_version=1, recorded_answer_key_digest,
              recorded_fixture_digest, + case_table/prereg digests      [:1080-1104]
   steps/<n>/status.json : surface_sha256 (observed) + recorded_surface_preimage_sha256
        ▼
rig/derive.py --experiment failure-flood-v1
   run_self_tests() false ──► NO ROWS AT ALL, exit 1   (the deriver is unproven) [:1468-1470]
        │                     ── never merged with the row-level gate below ──
        ▼
   build_row_failure_flood, inside `if state == "complete":`             [:850]
        1. provenance gate FIRST
             version absent          ──► void: input-provenance-missing  + pre-scheme-provenance
             digest null             ──► void: input-provenance-missing  + provenance-capture-incomplete
             recorded != live        ──► void: input-provenance-mismatch + <face>-drift
        2. per-step read-back loop, now with a frozen comparand          [:851-886]
             surface_sha256 != recorded preimage ──► void: surface-mismatch
             mode/model read-back not True       ──► void: <existing reason>
        3. scoring, with .get() throughout; causes_present null when R0 absent
        ▼
rig/results/failure-flood-v1/runs.jsonl   schema_version 4
   3 rows · state=void · void_reason=shakedown · anomaly_classes=[pre-scheme-provenance]
   N = 0 countable rows
```

## File changes

| File | Action | Description |
|---|---|---|
| `rig/run-pipeline.sh` | Modify | `preimage_digest()` + its self-test cases; the two arm-level digests recorded after the MANIFEST gate; `recorded_surface_preimage_sha256` into `write_step_status`; `input_provenance_version` into the `arm.json` writer |
| `rig/derive.py` | Modify | `answer_key_set_digest()`; `digests["answer_key"]` behind `reg.get(...)`; the provenance gate ahead of the read-back loop; `:855`'s guard deleted; `is False` → not-`True` at `:859`/`:883`; `.get()` at `:981`/`:1071` with `causes_present` null-not-zero; schema 3 → 4; one new self-test function plus the inverted case 3 |
| `rig/results/failure-flood-v1/runs.jsonl` | Modify | Re-derived. Three rows, still `void: shakedown`, marked `pre-scheme-provenance` |
| `rig/README.md` | Modify | The stale `schema_version 1` corrected to `4`; the row-shape description gains the provenance fields |
| `rig/check.sh` | **Unchanged** | Its missing bash self-test arm is named in section 9, not fixed here |
| `rig/run.sh`, `rig/report.py`, `rig/collect.py` | **Unchanged** | `tool-surface-v1`'s path is not touched; `report.py` already names voids by reason and needs no new vocabulary |
| `decisions/` | **No new file** | See the ADR section. If one is written, its number is claimed at write time |
| `theory/` | **Unchanged** | No number exists to promote (ADR 0011) |
| `sdd/archive/2026-08-18-failure-flood-triage/**` | **Never edited** | Sealed |

## Verification strategy

No test runner, by decision (ADR 0013, upheld by 0015). The surface is what exists.

| Layer | What | How |
|---|---|---|
| Syntax | `rig/run-pipeline.sh` | `bash -n` |
| Syntax | `rig/derive.py` | `python3 -m py_compile` |
| Structure | frontmatter, six-key schema | `./check.sh` |
| Redaction | every committed file including `runs.jsonl` | `./hooks/pre-commit --all`. The digests-and-integers row shape keeps this passing by construction (ADR 0009) |
| New detectors | can each one fire? | `rig/derive.py --self-test` cases 1–10; cases **1** and **7** are the ones that get skipped |
| New algorithm | `preimage_digest` | `rig/run-pipeline.sh --self-test` cases a–c, run by hand (section 9's stated weakness) |
| Cross-language agreement | two digests, two languages | the shared pinned constants, asserted on both sides |
| `tool-surface-v1` non-regression | 42 rows | re-derive; project out `checker_digest`; every remaining byte identical; `schema_version` still 3 |
| `failure-flood-v1` re-derive | 3 rows | the projection in section 8; still `void: shakedown`; `anomaly_classes` exactly `["pre-scheme-provenance"]` |
| Deriver idempotence | the existing property | derive twice; `runs.jsonl` byte-identical |
| Totality | no `KeyError` mid-derive | self-test case 9, plus a malformed answer key exercised against a real run directory |

## Rollback

Revert the schema bump and the runner edit; rows re-derive from raw captures unchanged — the property
the prior cycle verified. The three shakedown rows are `void` before and after, so no committed truth
is touched. Nothing in `theory/` changes, because no number exists to promote (ADR 0011). No fixture
version is mutated: fixtures are additively versioned and this change writes none.

## Open questions

- [ ] **Is a `complete` row with null scored fields countable?** Pre-dates this change (`:987-994`'s
      precedent). Section 3 preserves the existing behaviour and explicitly declines to decide it.
- [ ] **Does `report.py` need to name the two new void reasons?** It already excludes voids and names
      them by reason, so probably not — but that is asserted from the prior cycle's description of it,
      not re-verified against `report.py` in this phase. Verify before the tasks phase closes.
- [ ] **Should `pre-scheme-provenance` count toward the X = 3 instrument-doubt threshold?** It is an
      anomaly on rows that are structurally uncountable, so counting it would trip a threshold using
      rows that can never contribute a number. Flagged, not decided.
- [ ] **The `check.sh` bash self-test arm.** Named out of scope by the proposal; section 9 states the
      resulting coverage gap. Whether it is registered as a follow-up here or gets its own cycle is
      still the proposal's open question 3.
- [ ] **This document exceeds the generic 800-word design budget.** Deliberate, and the same flag the
      prior cycle's design carried: the repo's own precedent for a measurement design is a decision
      record of this size. Flagged rather than silently ignored.
