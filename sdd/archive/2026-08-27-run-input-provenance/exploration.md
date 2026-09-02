---
id: sdd/run-input-provenance/exploration
type: journal
targets: [any]
status: draft
verified: 2026-08-19
sources: ["rig/derive.py", "rig/run-pipeline.sh", "rig/check.sh", "rig/README.md", "BACKLOG.md", "MAP.md", "sdd/archive/2026-08-18-failure-flood-triage/tasks.md", "sdd/archive/2026-08-18-failure-flood-triage/verify-report.md", "sdd/archive/2026-08-18-failure-flood-triage/archive-report.md"]
---

# run-input-provenance — exploration

SDD exploration for the change `run-input-provenance`: closing the class of `rig/derive.py` inputs
that are read from the **live tree at derive time** rather than from a run's own capture, together
with the read-back gap that is load-bearing for one of its faces. Investigation only. No proposal,
no design, no code.

## Why this change exists at all

The `failure-flood-triage` cycle archived on 2026-08-18 with two open tasks. Task 7.10
(`rig/run-pipeline.sh --self-test`) was closed on 2026-08-19 in commit `a2cbd6f`. Task 7.15 was
deliberately left open because verify round 4 judged its registration **inadequate**, in its own
words: *"It names one field. The class is at least three fields wide… 7.15 should be re-scoped to
the class, or two sibling tasks registered beside it."*

This exploration is that re-scope, carried out against the code rather than against the report.

**The boundary this change inherits and must not blur:** the `failure-flood-triage` cycle delivered
an instrument and a **failed** ratio target. It never produced a comparative result. Every row in
`rig/results/failure-flood-v1/runs.jsonl` is `state=void`. **N = 0 countable rows.** Nothing in this
change may imply otherwise; the defects below are harmless *today* precisely because there is no
number to be wrong, and serious the moment there is one.

## 1. The class, verified in code

Everything below is read from the live tree when `derive.py` runs, not from the run being derived.
Line numbers are `rig/derive.py` at `a2cbd6f`.

### Face A — the answer key. The worst face, and the one task 7.15 does not name

`load_failure_flood_answer_keys()` (`:646`) globs `<fixture-root>/answer-key/*.json` off disk at
derive time. `ak = answer_keys.get(task_id)` (`:963`) then drives **five** outputs, one of which is
not a field at all but the row's state:

| Answer-key input | Line | Drives |
|---|---|---|
| `ak.get("S0")` | `:975` | `suite_state_cause` — and an `"environment"` result sets `state="void", void_reason="suite-state-mismatch"` (`:976-978`) |
| `ak["F0"]["failures"]` | `:980-982` | `verdict`, `integrity_guard_pass` via `green_restore_verdict()` |
| `ak.get("R0")` | `:996-998` | `causes_claimed`, `causes_correct` via `score_diagnostic_attribution()` |
| `len(ak["R0"])` | `:1071` | `causes_present` |

**No row carries any digest of the answer key it was scored against.** The row dict (`:1000-1074`)
carries `fixture_digest`, `checker_digest`, `prereg_digest` and `case_table_digest` — and nothing
for the answer key. So re-measuring an answer key silently rescores every already-recorded row, and
**no field exists that could ever reveal it happened.**

This is strictly worse than what task 7.15 names. `fixture_digest` is an identity field; these are
the scored outputs. A drifting answer key does not merely mislabel a row, it changes the row's
verdict and can flip it between `complete` and `void`.

Incidental, and unguarded: `ak["F0"]["failures"]` (`:981`) and `ak["R0"]` (`:1071`) are subscripts,
not `.get()`. An answer key that loses either key raises `KeyError` mid-derive rather than voiding
the row — a total function that stops being total.

### Face B — `fixture_digest`. What task 7.15 actually names. Identity only

`fixture_digest_at()` (`:611`) hashes `<fixture-root>/MANIFEST.sha256` at derive time; the value
lands in `fixture_digest` (`:1016`). The field **is** the present-derived value, overwritten in
place on every re-derive. This is what let a manifest re-freeze rewrite the field on three
already-recorded runs, which is how the defect was found.

Second-order consequence, and the more dangerous half (verify round 4's own finding): the R-F5.3
byte-identical re-derive check **can never detect that a fixture moved under recorded rows**,
because it re-reads the same live manifest and agrees with itself. R-F5.3 is a real check against
*deriver* drift and not a check against *fixture* drift; today's report reads as though it were
both.

### Face C — the surface preimage. The cheapest fix, because half of it is already captured

`load_surface()` / `surface_harness()` (`:96`, `:102`) produce `ff_surface_digest` (`:849`), which
`:855` compares against the run's **own** captured `step["surface_sha256"]`. So the run already
carries its side of this comparison; only the comparand comes from the present. The fix is to freeze
the preimage digest per run, not to add a new capture.

Note `:855`'s guard: `if ff_surface_digest is not None and step_surface != ff_surface_digest`. If
the live preimage loses its tool lines, `ff_surface_digest` becomes `None` and the whole
surface-mismatch void **silently stops firing**. That conditional is exactly what verify round 4
demonstrated WARNING-14 depends on, which is why the two are load-bearing for each other and should
be closed together rather than separately.

### Face D — `CHECKER_DIGEST` (`:82`). Declared, not a defect

R-F5.3's own scenario excludes it from the byte-identity projection. Named here only so a future
reader does not mistake its absence from the fix for an oversight.

## 2. The read-back half (WARNING-14), and why it belongs in this change

`derive.py` distinguishes "proven wrong" from everything else and never distinguishes "proven right"
from "not proven at all". Both read-back downgrades are written `is False` (`:859`, `:883`) — there
are exactly two in the file. `None`, the value a destroyed, truncated or never-captured stream
leaves behind, passes silently.

Verify round 4 demonstrated this is not hypothetical: an artifact in this repository reached exactly
that shape, and a scratch-copy experiment showed that promoting the same directory to `complete`
yields `state=complete, verdict=green` when the live surface preimage carries no tool lines. The
only thing standing between "capture destroyed" and "a countable green row" is Face C's live-tree
dependency.

A second, independent instance of the same shape was found on 2026-08-19 while building
`run-pipeline.sh --self-test` (task 7.10): removing `check_prereg`'s untracked guard leaves the
refusal exiting 2 — `git status --porcelain` reports `?? path`, so the *next* guard catches it and
relabels it `tracked_but_dirty`. **The refusal stays correct while its stated cause becomes false.**
An exit-code assertion is blind to it; only a reason-level assertion sees it. That is now a
committed test case, and it is the third recorded occurrence of accidental-catch-with-a-wrong-reason
in this rig.

## 3. Three shapes, not one — and why the shape decides the fix

The four faces are not four instances of one bug. They differ in what the run already captured:

| Face | What the run captures today | What a fix must add |
|---|---|---|
| A — answer key | **nothing** | provenance from zero: a per-run record of the scored inputs |
| B — `fixture_digest` | nothing; the field *is* the live read | the run's own digest, recorded at run time |
| C — surface preimage | its own `surface_sha256` per step | freeze the *comparand*, not a new capture |
| D — `CHECKER_DIGEST` | n/a | nothing; declared out of scope |

A batch that closes task 7.15 as written fixes **Face B**, marks the task done, and leaves the
scoring path — the only face that can change a number — open underneath a green checkbox. That is
the specific failure this re-scope exists to prevent.

## 4. Ordering, by blast radius

1. **Face A** — changes verdicts and can flip row state; no provenance exists at all.
2. **WARNING-14's read-back half** — closed with A; C's `is not None` guard is what currently
   substitutes for it.
3. **Face C** — cheapest; half the mechanism is already in the capture.
4. **Face B** — identity only, plus the R-F5.3 claim boundary it forces the report to state honestly.

## 5. Where this had to live, and why `sdd/` is the answer

`MAP.md` provides no register for an actionable open task from a **closed** cycle:

- `BACKLOG.md` is explicitly *"candidate practices and downstream deliverables, recorded with a named
  unblock condition and never built ahead of it"*, and its own "does not belong here" section rules
  out anything without a named trigger. This work is actionable now; it is neither.
- `gaps/` holds gap analyses of *other* projects.
- `sdd/archive/2026-08-18-failure-flood-triage/tasks.md` is a sealed record of a closed cycle.

`sdd/` is where task-bearing work lives in this repo, which is why this is a new cycle rather than an
edit to an archived artifact.

## 6. Open questions for the proposal phase

These change the spec and are not resolvable from the code:

1. **Granularity of provenance for Face A** — a digest per answer key, or a full copy of the scored
   inputs carried into the run directory?
2. **Retroactivity** — must already-recorded `void` rows become immutable under the new scheme, or is
   the guarantee forward-only from the first countable run?
3. **One task or three siblings** — does task 7.15's identity survive as the Face B sibling, or is it
   retired and replaced?
4. **Failure mode on drift** — when provenance disagrees, does the row void with a new dedicated
   reason, or does `derive.py` refuse to derive at all?

## Key Learnings

1. The present-derived class in `rig/derive.py` is four members in three distinct shapes, and the
   shape determines the fix rather than the field name.
2. The answer-key face drives five scored outputs and can flip a row between complete and void, while
   no row carries any digest of the answer key it was scored against.
3. Task 7.15 as written names only the identity field, so closing it verbatim would mark the class
   done while leaving the scoring path open.
4. The surface-mismatch void is conditional on a live preimage still carrying tool lines, which makes
   the present-derived class and the None-versus-False read-back gap load-bearing for each other.
5. A guard removed from `check_prereg` still exits 2 because the next guard relabels the failure, so
   only a reason-level assertion detects that the stated cause became false.
