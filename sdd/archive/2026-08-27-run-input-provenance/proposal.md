---
id: sdd/run-input-provenance/proposal
type: journal
targets: [any]
status: draft
verified: 2026-08-19
sources: ["sdd/run-input-provenance/exploration.md", "sdd/archive/2026-08-18-failure-flood-triage/verify-report.md", "sdd/archive/2026-08-18-failure-flood-triage/tasks.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "rig/derive.py", "rig/run-pipeline.sh", "rig/check.sh", "rig/README.md", "skills/hypothesis-cycle/SKILL.md"]
---

# run-input-provenance — proposal: a row must carry what it was scored against

SDD proposal phase for `run-input-provenance`. Intent, scope, approach. No spec, no design, no code.

## The boundary this change inherits, stated before anything else

The `failure-flood-triage` cycle delivered **an instrument and a FAILED ratio target — never a
comparative result.** Every row in `rig/results/failure-flood-v1/runs.jsonl` is `state=void,
void_reason=shakedown`. **N = 0 countable rows.** Verified in the file, not accepted from the report.

Nothing in this cycle may imply a comparative result exists, is pending, or is nearly available. The
defects below are harmless **today precisely because there is no number to be wrong**, and serious the
moment there is one. That is not "early results" and must never be softened into it.

## Intent

`rig/derive.py` reads four inputs from the **live tree at derive time** rather than from the run being
derived. A row therefore cannot say what it was actually scored against. Verified at `a2cbd6f`:

| Face | Live read | Drives | Severity |
|---|---|---|---|
| **A — answer key** | `load_failure_flood_answer_keys()` (`:646`), `ak` (`:963`) | `suite_state_cause` **and a state flip to void** (`:975-978`), `verdict`/`integrity_guard_pass` (`:980-982`), `causes_claimed`/`causes_correct` (`:996-998`), `causes_present` (`:1071`) | **Scoring.** No digest of the answer key exists on any row (`:1000-1074`) |
| **C — surface preimage** | `load_surface()`/`surface_harness()` (`:96`, `:102`) → `:849`, compared at `:855` | the `surface-mismatch` void | Comparand only; the run already captures its own `surface_sha256` |
| **B — `fixture_digest`** | `fixture_digest_at()` (`:611`) → `:1016` | `fixture_digest` | Identity only. The field **is** the live read |

Re-measuring an answer key silently rescores every already-recorded row, and **no field exists that
could ever reveal it happened.** Task 7.15 names only Face B. Closing it verbatim marks the class done
while leaving the only face that can change a number open under a green checkbox — the specific failure
this re-scope exists to prevent (verify round 4: *"It names one field. The class is at least three
fields wide."*).

Two consequences the report must then state honestly: R-F5.3 checks **deriver** drift, never **fixture**
drift, because the re-derive re-reads the same live manifest and agrees with itself; and `:855`'s
`is not None` guard means a preimage that loses its tool lines **silently stops the surface-mismatch
void firing**, which is the only thing standing between a destroyed capture and a countable green row.

## Settled decisions, folded in

| # | Decision | Rejected alternative |
|---|---|---|
| 1 | **Goal is DETECTION, not re-scoring.** A run records a digest of the answer key it was scored against, reusing the existing `prereg_digest`/`fixture_digest`/`case_table_digest` convention. Drift becomes detectable, and the row untrustworthy | Carrying a full copy of R0/S0/F0 into the run directory — duplicates fixture bytes into gitignored captures |
| 2 | **The three recorded rows are marked pre-scheme**, via an explicit field or `anomaly_class`. All three are `state=void, void_reason=shakedown`; nothing numeric depends on them | Deleting and re-recording — spends runs and discards shakedown evidence that already found real defects |
| 3 | **Task 7.15 is RETIRED and replaced**, with the retirement reason recorded. Three sibling tasks, ordered by blast radius | Keeping 7.15's wording — its title already demonstrably induced the error verify round 4 caught |
| 4 | **On mismatch the row voids with its OWN dedicated `void_reason`**, distinct from `surface-mismatch`, preserving `derive.py`'s downgrade-only discipline and its total-function property | Refusing to derive at all — blocks the whole report over one row |

## Scope

### In scope

- **Face A** — a per-run answer-key digest, recorded at run time, compared at derive time. Highest blast
  radius: it is the only face that changes verdicts and can flip row state.
- **WARNING-14's `None`-vs-`False` read-back half**, closed **together with Face A**. Both downgrades are
  written `is False` (`:859`, `:883`); `None` — what a destroyed, truncated or never-captured stream
  leaves behind — passes silently. Face C's `is not None` guard is what currently substitutes for it, so
  the two are load-bearing for each other.
- **Face C** — freeze the comparand per run. Cheapest: the run already carries its side.
- **Face B** — the run's own fixture digest, recorded at run time, plus the honest R-F5.3 claim boundary.
- The unguarded subscripts `ak["F0"]["failures"]` (`:981`) and `ak["R0"]` (`:1071`), which raise
  `KeyError` mid-derive instead of voiding — a total function that stops being total.
- A schema bump and full re-derive, under the existing no-migrations rule.

### Out of scope

| Not doing | Why |
|---|---|
| **Face D — `CHECKER_DIGEST` (`:82`)** | Declared, not a defect: R-F5.3's own scenario excludes it. Named so its absence is not read as an oversight |
| `rig/check.sh` does not compose `rig/run-pipeline.sh --self-test` | Real adjacent gap: `check_component_self_test()` runs `python3 <script> --self-test` and has **no bash arm**. Named, not fixed here |
| Re-scoring or re-deriving the three rows into countability | They stay `void`; decision 2 marks them, nothing promotes them |
| Any comparative result, table or ratio | N = 0. Out of scope by arithmetic, not by choice |

## Capabilities

This repo uses no `openspec/specs/` tree, so these name spec-phase deliverables.

**New** — `run-input-provenance`: which inputs a run must record, the digest fields and their recording
point, the comparison rule at derive time, the dedicated mismatch `void_reason`, the pre-scheme marker,
and the `None`-as-not-proven read-back rule.

**Modified** — `rig/derive.py` row schema (one additive bump, re-derived over existing rows);
`rig/run-pipeline.sh` (records the digests); `rig/README.md` if the row-shape description moves.

## Approach

Three sibling tasks, ordered by blast radius. The order is the deliverable, not an implementation note.

| Order | Sibling | Closes | Why here |
|---|---|---|---|
| 1 | **Face A + WARNING-14** | the scoring path, and the read-back gap that depends on it | Only face that can change a number; provenance exists from zero. The two are load-bearing for each other, so splitting them leaves each propped on the other |
| 2 | **Face C** | the surface comparand | Cheapest — freeze a comparand, add no capture. Once A lands, C's `is not None` guard stops being load-bearing and can be tightened safely |
| 3 | **Face B** | `fixture_digest` identity, and the R-F5.3 claim boundary | Identity only. Forces the report to state that R-F5.3 never checked fixture drift |

Each digest reuses the existing `*_digest` convention rather than inventing a mechanism. Mismatch
downgrades to `void` with its own reason — never an upgrade, never a refusal to derive.

## Affected areas

| Area | Impact | What changes |
|---|---|---|
| `rig/derive.py` | Modified | Digest comparisons, the new `void_reason`, `None`-as-not-proven at `:859`/`:883`, `.get()` at `:981`/`:1071`, schema bump |
| `rig/run-pipeline.sh` | Modified | Records the answer-key, surface-preimage and fixture digests at run time |
| `rig/results/failure-flood-v1/runs.jsonl` | Modified | Re-derived; three rows gain the pre-scheme marker and stay `void` |
| `rig/check.sh` | Unchanged | Its self-test composition gap is named, not fixed |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| An artifact implies a comparative result exists | Medium | The boundary section leads this proposal and must lead every downstream artifact. N = 0 is arithmetic, not framing |
| Face B lands first and the class is declared closed | Medium | Ordering is a deliverable; 7.15 is retired precisely because its wording induced this |
| The new detector is never proven able to fire | Medium | `--self-test` per ADR 0013, the pattern already load-bearing in `derive.py` |
| Splitting Face A from WARNING-14 leaves each propped on the other | Medium | They ship as one sibling, stated above |
| The re-derive is not byte-identical for the three rows beyond the intended marker | Low | Re-derive is the verification; any other delta is a defect, not an expected diff |
| The retirement of 7.15 is read as the task being done | Low | Retirement reason recorded with the three replacements named |

## Rollback

Nothing in `theory/` changes — no number exists to promote (ADR 0011). Rollback is reverting the schema
bump and the runner edit; rows re-derive from raw captures unchanged, the property the prior cycle
verified. The three shakedown rows are `void` before and after, so no committed truth is touched. The
sealed archive at `sdd/archive/2026-08-18-failure-flood-triage/` is never edited.

## Success criteria

- [ ] A row carries a digest of the answer key it was scored against, and drift is detectable
- [ ] Provenance mismatch voids the row with its own dedicated `void_reason`, never `surface-mismatch`
- [ ] `derive.py` stays total: no answer-key shape raises `KeyError` mid-derive
- [ ] A `None` read-back is treated as not-proven, not as proven-right, at both `:859` and `:883`
- [ ] Each new detector is proven able to fire, via `--self-test`
- [ ] The three recorded rows are marked pre-scheme, remain `state=void`, and are not deleted
- [ ] Task 7.15 is retired with its reason recorded, replaced by the three named siblings
- [ ] The report states that R-F5.3 checks deriver drift and not fixture drift
- [ ] No artifact in this cycle implies a comparative result exists or is pending

## Open questions for the spec phase

1. **The exact `void_reason` string and the pre-scheme marker's form** — a dedicated field, or a member
   of the existing `anomaly_classes` list (today `[]` on all three rows).
2. **Recording point for the answer-key digest** — one digest over the whole `answer-key/` set, or one
   per consumed key. Per-key is more precise; set-wide is cheaper and matches `case_table_digest`.
3. **Whether `check.sh`'s missing bash self-test arm is registered as a follow-up task here** or left to
   its own cycle. Named as out of scope either way.
