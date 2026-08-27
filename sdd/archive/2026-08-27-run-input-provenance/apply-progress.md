---
id: sdd/run-input-provenance/apply-progress
type: journal
targets: [any]
status: draft
verified: 2026-08-26
sources: ["sdd/run-input-provenance/tasks.md", "sdd/run-input-provenance/spec.md", "sdd/run-input-provenance/design.md", "rig/derive.py", "rig/run-pipeline.sh"]
---

# run-input-provenance — apply progress (Sibling 1: Face A + WARNING-14; Sibling 2: Face C; Sibling 3: Face B + cross-cutting)

Scope of this note: **Sibling 1 (tasks 1.1-1.11), Sibling 2 (tasks 2.0-2.8), and Sibling 3 (tasks
3.1-3.7 plus cross-cutting 4.1-4.7), merged.** Sibling 1's own section directly below is UNCHANGED from
its first commit (`0637d68`); Sibling 2's own section is UNCHANGED from its own commit (`5cfa456`);
Sibling 3's own section, covering the cross-cutting verification too, is appended at the end of this
file. This is the last work unit of the cycle — all tasks in `sdd/run-input-provenance/tasks.md` are now
`[x]`.

## The boundary this cycle still leads with

The `failure-flood-triage` cycle delivered an instrument and a **FAILED** ratio target, never a
comparative result. After this sibling's changes and re-derive, all three rows in
`rig/results/failure-flood-v1/runs.jsonl` remain `state=void, void_reason=shakedown`. **N is still 0
countable rows.** Nothing in this sibling — code, self-test, or this note — implies a comparative
result exists, is pending, or is nearly available. No real `claude -p` invocation was spent; every
criterion below is satisfied by `--self-test` or by re-deriving already-committed raw captures.

## The resolved conflict, carried forward (task 1.1)

`tasks.md`'s own header section ("Spec/design conflict — resolved 2026-08-20, `43f5281`") already
carries the three points task 1.1 asks this note to record; restated here for this note's own
completeness rather than only by reference:

1. **The conflict existed and blocked once.** An earlier draft of `spec.md` (Decision 1) pinned a
   per-face `void_reason` (`"answer-key-mismatch"`); `design.md` §4 argued for one generic
   `"input-provenance-mismatch"` plus `anomaly_classes` drift suffixes, and explicitly rejected the
   per-face approach. The two could not both be implemented as written, and `tasks.md`'s own prior
   draft correctly flagged this as blocking before Sibling 1 could be applied.
2. **The resolution, and its real deciding argument.** Design's conclusion (one reason, per-face drift
   classes) won — but not for the reason design originally gave. Design argued per-face reasons
   "inflate the vocabulary every consumer must implement," citing `report.py` as already naming voids
   by reason. Verified directly: `rig/report.py` is reason-agnostic (`classes.add(r["void_reason"])`
   at `:125-126`, interpolated at `:163`/`:335` — no enum, no per-reason branch). Three reasons would
   have cost `report.py` nothing. The argument that actually decides it, stated by neither original
   artifact: `answer-key/` sits inside `compute_manifest()`'s own walked set, so one edit to
   `answer-key/prereg.json` disagrees on the answer-key digest *and* the fixture digest at once. A
   per-face reason would force the single `void_reason` slot to pick a winner between two true
   findings — a precedence rule, discarding one face's finding. One reason plus per-face drift classes
   in `anomaly_classes` records both findings and removes the ordering hazard entirely.
3. **The resolution outranks the observation that caused the original flag.** The vocabulary-size
   argument that motivated design's original conclusion turned out to be false (`report.py` is
   reason-agnostic); the conclusion survives anyway, on the `compute_manifest()` overlap argument. This
   is why the flag is resolved rather than reopened: the *conclusion* (one reason, per-face drift
   classes, R-P2.2a's ban on a precedence rule) is correct and implemented directly by tasks 1.5-1.10,
   independent of which argument justifies it.

This was not a gate on tasks 1.5 onward; those tasks implement the settled vocabulary
(`input-provenance-mismatch` / `input-provenance-missing`, `answer-key-drift` /
`provenance-capture-incomplete` / `pre-scheme-provenance`) directly, with no per-face `void_reason` and
no precedence rule anywhere in the implementation below.

## What was implemented

**`rig/derive.py`** (net +303/-25 lines):

- `answer_key_set_digest(root)` — a new function beside `fixture_digest_at()`, computing a set-wide
  digest over one fixture root's `answer-key/` relpaths. This reproduces `rig/run-pipeline.sh`'s
  `hash_paths()` convention exactly (sorted `sha256(content)  relpath` lines, joined by `\n`, hashed) —
  a genuine cross-language pair, verified by hand against the real committed `v1` answer-key set
  (`571e083d27aaef0a63cee3b26de97b14ac8eccdab02dfbe3535aba83728cb7b6` on both sides).
- Wired into `main()`'s `digests` dict as `digests["answer_key"]`, built only when
  `reg.get("answer_key_digest")` is set. The `tool-surface-v1` registry entry gains no key and its
  dict literal is byte-unchanged; `build_row` (tool-surface-v1's row builder) is untouched.
- `build_row_failure_flood` gains the input-provenance gate, placed before the existing per-step
  read-back loop. Implementation detail worth flagging explicitly: the gate is **not** one single `if
  state == "complete":` block as the task text's literal phrasing suggested. R-P5.2's own text requires
  the *annotation* ("pre-scheme-provenance") to fire on an already-void row (the three shakedown rows'
  own proof, R-P8) while the *state transition* stays downgrade-only (R-P3.2) — those are two different
  conditions, and a single shared `if` block cannot express both correctly. The marker-absence check
  always runs and always annotates, gating only its own transition on `state == "complete"`; the
  null-digest check and the accumulate-then-decide mismatch check are nested inside their own `elif
  state == "complete":` and never touch an already-void row at all. Self-test case h (a synthetic
  shakedown-shaped row) is the proof this split is required — a naive single-block version fails it.
- The `drifted` set accumulates two sources today: a live-vs-recorded answer-key digest mismatch
  (R-P3.1) and a malformed answer key missing `F0.failures` or `R0` (R-P4.1, "not a separate class
  needing its own reason" — joins the same set a digest mismatch does). Sibling 2 (task 2.4) and
  Sibling 3 (task 3.2) will join the same set later; nothing here anticipates their shape beyond
  leaving the set open to extension.
- `ak["F0"]["failures"]` and `len(ak["R0"])` are `.get()`-based now; `causes_present` is
  `len(ak["R0"]) if ak and "R0" in ak else None`, never `0`.
- `:859`/`:883`'s `is False` downgrades are now `is not True` — R-P5.4's exact rule, "not-True is
  not-proven." Both sites, not just the one the original task text's worked example centered on (see
  the gap noted below).
- `FAILURE_FLOOD_SCHEMA_VERSION` bumped 3→4, with a comment naming all four fields the version covers
  (`input_provenance_version`, `recorded_answer_key_digest` — populated by this sibling;
  `recorded_fixture_digest`, per-step `recorded_surface_preimage_sha256` — named now, populated by
  Siblings 3 and 2 respectively). No migration code.
- The row dict gains `input_provenance_version`, `recorded_answer_key_digest`,
  `recorded_fixture_digest` (the last stays `null` until Sibling 3 wires `arm.json`'s own field) — all
  read back via `arm_data.get(...)`, never recomputed for display.
- `_self_test_build_row_model_mismatch()`'s case 3 rewritten in place (never deleted) to assert the
  pre-scheme void instead of pinning the old "never falsely voids" defect. A new case 4 proves the
  provenance-intact `model-mismatch` void. A new case 5 (beyond this task's own listed scope — see gap
  below) proves the permission-mode site the same way.
- `_self_test_build_row_answer_key_provenance()` — new function, 8 cases (a-h) exactly as specified in
  task 1.10, registered in `run_self_test()`'s roster.
- `_self_test_make_ff_run_dir()` extended with `arm_overrides`, defaulting every existing caller (three
  functions, four call sites) to a provenance-intact fixture — this is what makes the new gate compose
  with every pre-existing detector rather than sit beside them (design.md §9's own stated intent).

**`rig/run-pipeline.sh`** (+32 lines):

- `answer_key_paths()` — filters `compute_manifest()`'s own output by the `answer-key/` prefix, the
  same pattern `manifest_workspace_paths()` already uses. No second manifest algorithm.
- `RECORDED_ANSWER_KEY_DIGEST` computed right after the MANIFEST recompute-compare gate, over bytes
  already proven frozen.
- `input_provenance_version: 1` and `recorded_answer_key_digest` threaded into the arm.json writer's
  env block and `arm = {...}` dict, the same lifetime as `PREREG_DIGEST`/`CASE_TABLE_DIGEST`.

**`rig/results/failure-flood-v1/runs.jsonl`** and **`rig/results/tool-surface-v1/runs.jsonl`**:
re-derived (generated, excluded from the authored line count per the work-unit-commits convention, but
included below in full-snapshot verification). Re-deriving `tool-surface-v1` was not optional: editing
`derive.py` necessarily rewrites `checker_digest` on both experiments' rows (`derive.py`'s own file-byte
digest, stamped at `:530` and `:1017`), so its committed `runs.jsonl` was stale the moment `derive.py`
changed regardless of whether Sibling 1 touches `build_row` — the re-derive here is what task 4.1's own
projection check verifies, run early because it is a mechanical consequence of this sibling's own edit,
not a decision to pull the cross-cutting task forward.

## Verification evidence

**`rig/derive.py --self-test`** — all 43 cases PASS (35 pre-existing + 8 new answer-key-provenance
cases `a`-`h` + case 5 closing the permission-mode gap), including the rewritten case 3 and new case 4
in `_self_test_build_row_model_mismatch`.

**`rig/run-pipeline.sh --self-test`** — all pre-existing cases PASS unchanged (24 cases:
`hash_paths` ×4, `read_back_init` ×4, `check_prereg` ×8, `compute_manifest`/`manifest_workspace_paths`
×5, plus 3 more from earlier assertions). No new case was added for `answer_key_paths()` itself — task
1.3 only requires `bash -n`, and the cross-language agreement was verified by hand (see below) rather
than pinned in a committed case, matching this sibling's own task list (the pinned-constant mechanism
is task 2.1's, for `preimage_digest`, not task 1.3's).

**`python3 -m py_compile rig/derive.py`** — clean. **`bash -n rig/run-pipeline.sh`** — clean.

**Cross-language agreement (Face A's digest, both sides, over the real committed `v1` answer-key set):**
```
python:  answer_key_set_digest(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])
      -> 571e083d27aaef0a63cee3b26de97b14ac8eccdab02dfbe3535aba83728cb7b6
bash:    answer_key_paths "$FIXTURE_ROOT" | hash_paths "$FIXTURE_ROOT"
      -> 571e083d27aaef0a63cee3b26de97b14ac8eccdab02dfbe3535aba83728cb7b6
```
Identical. Mutation-proven too: swapping the bash-side prefix filter from `answer-key/` to `tools/` in
a scratch copy of `run-pipeline.sh` produces `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
(the empty-input hash — `v1` has no `tools/` dir), diverging from the python side as expected; the real
file was untouched throughout (`git status --short rig/run-pipeline.sh` showed only the one legitimate
modification before and after).

**Mutation-proofs, each detector broken in a scratch copy of `rig/derive.py` (never the committed
file), confirmed red on the specific case it protects, confirmed the real file byte-identical
afterward (`shasum -a 256` compared before/after every cycle):**

| Detector broken | Case(s) that went red | Every other case |
|---|---|---|
| Answer-key digest comparison (pass 3) disabled | `answer-key provenance b` | stayed green |
| Pre-scheme annotation (pass 1) removed | model-mismatch case 3, `answer-key provenance d`, `answer-key provenance h` | stayed green |
| Null-digest check (pass 2) disabled | `answer-key provenance e` | stayed green |
| Malformed-key check (task 1.6) disabled | `answer-key provenance f` | stayed green |
| `:883` `is not True` reverted to `is False` | model-mismatch case 4 | stayed green |
| `:859` `is not True` reverted to `is False` | model-mismatch case 5 (new, see gap below) | stayed green |
| `causes_present` totality fix reverted | raised `KeyError: 'R0'` mid-derive on case f | (crash, not a red case — proves the total-function guarantee is load-bearing) |

**Re-derive (task 1.11):** `python3 rig/derive.py --experiment failure-flood-v1` — all three rows:
`state=void, void_reason=shakedown` (unchanged), `anomaly_classes == ["pre-scheme-provenance"]` exactly,
`schema_version == 4`, `input_provenance_version`/`recorded_answer_key_digest`/`recorded_fixture_digest`
all `null`. No row acquired `state=complete`. Idempotent: derived twice, byte-identical both times.

**`tool-surface-v1` non-regression (task 4.1's own check, run here as a consequence of re-deriving):**
42 rows, projected excluding only `checker_digest` — zero mismatches against the pre-change file;
`schema_version` stays `3`; `build_row`'s registry entry dict literal is byte-unchanged in the diff.

**`failure-flood-v1`'s own projection (task 4.2's own check, same reason):** 3 rows, projected excluding
`schema_version`, `checker_digest`, `anomaly_classes`, and the three new row-level fields — zero
mismatches against the pre-change file.

**`./rig/check.sh`** — 20/20 checks pass:
```
[PASS] manifest:v1 recompute-compare clean
[PASS] manifest:v2 recompute-compare clean
[PASS] self-test:derive.py (exit 0)
[PASS] self-test:report.py (exit 0)
[PASS] self-test:collect.py (exit 0)
[PASS] preflight:v1 reaches the pre-registration gate past the manifest gate
[PASS] preflight:v2 reaches past the manifest gate and the pre-registration gate
[PASS] derive-reproduce:tool-surface-v1 re-derives byte-identically
[PASS] derive-reproduce:failure-flood-v1 re-derives byte-identically
[PASS] stray-run-dir:s1-monolithic-01 genuinely complete
[PASS] stray-run-dir:s1-monolithic-9054 genuinely complete
[PASS] stray-run-dir:s2-pipeline-9054 genuinely complete
[PASS] syntax:bash -n run.sh / run-pipeline.sh / check.sh
[PASS] syntax:py_compile collect.py / derive.py / report.py / generate-cases.py / axis_table.py
rig/check.sh: 20/20 check(s) passed.
```

**`./check.sh` (root)** — `structure check: clean across 110 content files and 5 skill(s)`.

**`./hooks/pre-commit`** — exit 0, no output (ADR 0009 redaction scan clean across every staged byte,
including the re-derived `runs.jsonl` files).

## Deliberately not done

- **Sibling 2 (Face C, R-P6) and Sibling 3 (Face B, R-P7) are not started.** R-P9.2's ordering is a
  dependency, not a preference: Face C's `is not None` guard at `derive.py:855` still substitutes for
  the read-back check this sibling closes, and tightening it before this sibling landed would have
  stripped that substitute with nothing in its place. Nothing in this sibling's code path touches
  `:855`, `preimage_digest()`, or `recorded_fixture_digest`'s actual computation.
- **No new ADR.** Out of Sibling 1's scope regardless (design.md's own "no new ADR" recommendation
  covers the whole change, not per-sibling).
- **`rig/check.sh`'s missing bash self-test arm** (Decision 3's own named gap: `run-pipeline.sh
  --self-test` is never composed by the repo gate) is not fixed here — named out of scope by the spec
  itself, not an oversight of this batch.
- **No real `claude -p` run.** Every criterion above is satisfiable by synthetic self-test or by
  re-deriving already-committed raw captures. Whether to fund a real, countable run stays the
  operator's own decision, untouched by this batch.
- **`MAP.md`'s stale `sdd/` row (task 4.7) is not corrected here** — cross-cutting, reserved for the
  end of all three siblings.

## A gap this batch found and fixed rather than left open

Mutation-testing `:859`'s `is not True` change (task 1.7) revealed that no committed self-test case
exercised the `permission_mode_matches_declared` half of WARNING-14's closure — only the
`model_matches_declared` half (task 1.9's own two cases) was proven. Reverting `:859` alone to `is
False` in a scratch copy left every pre-existing case green; the change was invisible to the suite.
Design.md §9's own case-8 table entry says "provenance intact, `permission_mode_matches_declared` /
`model_matches_declared` `None` -> voids ... WARNING-14, **both sites**" — the design already intended
both sites proven, but task 1.9's worked example named only the model site. Per ADR 0013's own rule
("every detector this spec introduces or changes... MUST have a `--self-test` case that constructs an
input proving the detector actually fires"), this was fixed rather than left as a named gap: a fifth
case was added to `_self_test_build_row_model_mismatch()`, proving the permission-mode site voids
identically. Mutation-proven independently of the model-site case (see the table above). This is a
same-sibling, same-requirement completion, not scope creep into Sibling 2/3 — R-P5.4 explicitly names
both call sites as one requirement.

## Gate output referenced above, verbatim commands

```
python3 -m py_compile rig/derive.py
bash -n rig/run-pipeline.sh
python3 rig/derive.py --self-test
bash rig/run-pipeline.sh --self-test
python3 rig/derive.py --experiment tool-surface-v1
python3 rig/derive.py --experiment failure-flood-v1
./rig/check.sh
./check.sh
./hooks/pre-commit
```

All exited 0 except where a deliberate mutation is called out above.

---

# Sibling 2 — Face C (tasks 2.0-2.8, closes R-P6)

Scope of this section: **Sibling 2 only.** Task 2.0 first (a gatekeeping finding raised after Sibling 1
was committed — see below), then tasks 2.1-2.8 in order. Sibling 3 (Face B + the R-F5.3 claim boundary,
R-P7) is **not started.**

## The boundary this batch still leads with

The `failure-flood-triage` cycle delivered an instrument and a **FAILED** ratio target, never a
comparative result. After this batch's changes and re-derive, all three rows in
`rig/results/failure-flood-v1/runs.jsonl` remain `state=void, void_reason=shakedown`. **N is still 0
countable rows.** No real `claude -p` invocation was spent; every criterion below is satisfied by
`--self-test` or by re-deriving already-committed raw captures.

## Task 2.0 — the gatekeeping finding, closed first

Found by independent orchestrator mutation-proof after Sibling 1 landed (`0637d68`), not by the apply
phase that produced it: `answer_key_set_digest()`'s own computation was proven ZERO ways (every
self-test derived its own expected value by calling the function under test), and the Face A
cross-language pin task 1.3's done-note recorded was verified by hand, once, and never committed. Both
are closed now, without touching Sibling 1's own committed behaviour:

- `_self_test_answer_key_set_digest()` (new, registered in `run_self_test()`'s roster): case (a) proves
  the digest moves when the digested bytes move, checked against itself on a synthetic root this case
  builds and mutates — never against another self-test's own fixture. Case (b) is the committed
  cross-language pin: it `sed`-extracts `compute_manifest`/`answer_key_paths`/`hash_paths` verbatim from
  `rig/run-pipeline.sh` (the same convention `rig/check.sh`'s `load_compute_manifest()` already uses),
  `eval`s them inside a `bash -c` subprocess, and asserts the bash pipeline's output equals Python's
  `answer_key_set_digest()` over the SAME synthetic fixture root — genuinely executing both
  implementations, never comparing either side to a hardcoded string, exactly as this task required.
- A new `rig/run-pipeline.sh --self-test` case asserts `answer_key_paths()` selects exactly
  `answer-key/` relpaths, sorted, excluding every other manifest subdirectory.
- Mutation-proven (table below): `return "constant"` in `answer_key_set_digest()` now turns BOTH new
  derive.py cases red where before it turned all 43 cases green — this is the fix, demonstrated rather
  than asserted.

## What was implemented (2.1-2.8)

**`rig/run-pipeline.sh`** (+78/-2 lines):

- `preimage_digest()` — the one genuinely new algorithm this whole change introduces (design §1),
  reproducing `derive.py`'s `load_surface()` + `surface_digest()` convention exactly: dedupe + sort,
  `# harness:` header and blank lines excluded, `sha256` of the joined newline-set. Prints an empty
  string (never a hash of the empty set, never a crash) on a missing file or a file with no tool lines.
- Computed at the existing per-step preimage existence check in `run_model_step` — strictly AFTER that
  check, never before, so the `missing-surface-preimage` abort path is untouched and unmasked. Threaded
  as a new 13th positional argument through `write_step_status` into each model step's own
  `status.json` as `recorded_surface_preimage_sha256` — the ONE provenance face that is per-step, not
  arm-level, per design.md §1. `run_code_step`'s own call site passes an empty 13th argument.
- Self-test cases a-c added for `preimage_digest()`, pinned against the same constant
  (`4a626b46a7841184c5d423277a9c17cb15129f4ba32f92a88948b77735bfdcd3`) asserted on the `derive.py` side.
  **Deviation, recorded rather than made silently**: case (c), as task 2.3 literally specifies it, would
  call `run_model_step` — but that function is defined at `:932`, textually AFTER `self_test()`'s own
  dispatch site at `:650`, so in this script's top-to-bottom execution order it is not yet a defined
  bash command when `--self-test` runs (confirmed live: `run_model_step: command not found`, a
  structural fact about this file, not a behavioural defect). Case (c) instead asserts
  `preimage_digest()` itself returns an absent digest, never a crash, on a missing file — the abort
  path it would otherwise have exercised is unchanged by this batch and runs strictly before
  `preimage_digest` is ever reached in the real pipeline.

**`rig/derive.py`** (+244/-17 lines):

- `ff_surface_digest` (the live preimage recompute) is now computed BEFORE the provenance gate, so the
  gate's own new check can reuse it — no second, direct `rig/surfaces/` read introduced.
- The provenance gate's null check (task 1.5's pass 2) now also covers any model step's
  `recorded_surface_preimage_sha256` being absent, reaching `input-provenance-missing` /
  `provenance-capture-incomplete` before the read-back loop is ever entered with a missing comparand.
- The provenance gate's drift check (pass 3) gained a per-model-step loop (R-P6.3, task 2.4): any step
  whose `recorded_surface_preimage_sha256` disagrees with the live `ff_surface_digest` adds
  `"surface-preimage-drift"` to the shared `drifted` set — a DIFFERENT question from the read-back
  loop's own comparison, and the two never share a reason.
- The read-back loop's `is not None`-guarded live comparison (`:855` in the pre-Sibling-1 numbering) is
  **deleted, not weakened** (R-P6.2). Replaced with an unconditional comparison of the observed
  `step_surface` against the run's own frozen `recorded_surface_preimage_sha256` — never the live
  recompute, which is now Face C's drift comparand exclusively (task 2.5).
- `_self_test_make_ff_run_dir`'s one step now defaults BOTH `surface_sha256` and
  `recorded_surface_preimage_sha256` to the real committed preimage digest (Face-C-intact by default,
  the same composition discipline Sibling 1 established for Face A's `recorded_answer_key_digest`).
  Every existing caller that previously isolated itself from surface-mismatch via an EMPTY `surfaces`
  dict (`_self_test_build_row_model_mismatch`, `_self_test_build_row_token_breakdown`) now passes the
  REAL committed surface instead — isolation by agreement, not by omission, because an empty surfaces
  dict would now disagree with the new Face-C-intact default and trip the new gate.
- `_self_test_build_row_surface_preimage_provenance()` — new function, four cases, registered in the
  roster: (a) negative control; (b) the surface-mismatch fire-proof (this batch's own addition beyond
  the tasks' literal text — no committed case previously proved `build_row_failure_flood`'s own
  `surface-mismatch` void could fire; only `build_row`'s, tool-surface-v1's different function, had
  one); (c) the R-P6.3 firing proof (task 2.6); (d) the ordering proof (task 2.7).

**`rig/results/failure-flood-v1/runs.jsonl`** and **`rig/results/tool-surface-v1/runs.jsonl`**:
re-derived (generated, excluded from the authored line count, included below in full-snapshot
verification), for the same unavoidable-`checker_digest` reason Sibling 1's task 1.11 already recorded.

## A finding about task 2.5, recorded rather than hidden

Reverting the read-back loop's comparand back to `ff_surface_digest` (the pre-task-2.5, live-recompute
target) in a scratch copy produces **zero row-outcome difference** across the full self-test suite —
not merely on the cases this batch added, on all 51. The reason is architectural, not a mistake: task
2.4's own gate already requires `recorded_surface_preimage_sha256 == ff_surface_digest` for every model
step in a row before that row can reach `state == "complete"` and therefore reach the read-back loop at
all. So by construction, whenever the read-back loop runs, `recorded` and `live` are already proven
equal for every step in that row — swapping the comparison target between them is a mathematical no-op
in this exact codebase. This does NOT mean task 2.5 was unnecessary: R-P6.1/R-P6.2 are requirements
about the read-back check's OWN contract (never silently skip when the comparand is unavailable, never
compare against a live recompute), independent of whether a separate, additional gate happens to make
the distinction unobservable today. The requirement is satisfied to the letter. What IS mutation-proven,
and is the actual ADR 0013 obligation, is that the check can still FIRE at all (case b, added this
batch) — proven by neutering the `if` to `if False:`, which turns exactly that case red.

## Verification evidence

**`rig/derive.py --self-test`** — all 54 cases PASS. Empirically re-counted against Sibling 1's own
committed baseline (`0637d68`, verified from a scratch copy under `rig/` so `REPO_ROOT` resolves
correctly): 47 pre-existing cases (not the 43 Sibling 1's own apply-progress note stated — a minor
discrepancy in that note's own count, left uncorrected there per this file's own discipline of never
editing a prior sibling's section) + 7 new this batch (2 for task 2.0's `answer_key_set_digest` proofs,
1 for the `preimage_digest` cross-language pin, 4 for Face C's own surface-preimage provenance).

**`rig/run-pipeline.sh --self-test`** — all 28 cases PASS: 24 pre-existing (Sibling 1's baseline,
confirmed unchanged) + 4 new this batch (`answer_key_paths`, task 2.0 part 2; `preimage_digest` cases
a-c, task 2.3).

**`python3 -m py_compile rig/derive.py`** — clean. **`bash -n rig/run-pipeline.sh`** — clean.

**Mutation-proofs, each detector broken in a scratch copy (never the committed file), confirmed red on
the specific case(s) it protects, confirmed the real file byte-identical afterward (`shasum -a 256`
compared before/after every cycle):**

| Detector broken | Case(s) that went red | Every other case |
|---|---|---|
| `preimage_digest()` neutered to a constant | all three `preimage_digest` self-test cases (a, b, c) | stayed green |
| `answer_key_paths()` filter changed to `^tools/` | the new `answer_key_paths` case | stayed green |
| `answer_key_set_digest()` neutered to `return "constant"` | both new `answer_key_set_digest` cases (fire-proof, cross-language pin) | stayed green |
| Task 2.4's null check (`missing_surface_preimage` forced `False`) | surface-preimage provenance case (d) | stayed green |
| Task 2.4's drift check (per-step loop body neutered) | surface-preimage provenance case (c) | stayed green |
| Task 2.5's comparison neutered to `if False:` | surface-preimage provenance case (b) | stayed green |
| Task 2.5's comparand reverted to `ff_surface_digest` (the finding above) | none — zero observable difference, by construction of task 2.4's own gate | all 51 stayed green |

**Re-derive (task 2.8):** `python3 rig/derive.py --experiment failure-flood-v1` — all three rows:
`state=void, void_reason=shakedown` (unchanged), `anomaly_classes == ["pre-scheme-provenance"]` exactly
(unchanged), `schema_version == 4` (unchanged). Every step across all three rows:
`recorded_surface_preimage_sha256 == null` — the only permitted delta versus Sibling 1's own re-derive,
confirmed by a field-by-field diff that excludes only that one new key. Idempotent: derived twice,
byte-identical both times.

**`tool-surface-v1` non-regression (task 4.1's own check, run here for the same reason task 1.11
recorded it early):** 42 rows, projected excluding only `checker_digest` — zero mismatches against the
pre-batch file; `schema_version` stays `3`; `build_row`'s registry entry is untouched by this batch.

**`./rig/check.sh`** — 20/20 checks pass. **`./check.sh` (root)** — clean across 111 content files and
5 skill(s). **`./hooks/pre-commit`** — exit 0, no output (ADR 0009 redaction scan clean across every
staged byte, including the re-derived `runs.jsonl` files).

## Deliberately not done

- **Sibling 3 (Face B, R-P7) is not started.** R-P9.2's ordering is a dependency: Sibling 3's own
  fixture-digest check must join the same drift-accumulation pass this batch and Sibling 1 built, per
  R-P2.2a, so no sibling can establish the completed accumulation standing alone.
- **No new ADR, no real `claude -p` run** — same reasons Sibling 1's own section states.
- **`rig/check.sh`'s missing bash self-test arm** (Decision 3's own named gap) is not fixed here.
- **`MAP.md`'s stale `sdd/` row (task 4.7) is not corrected here** — cross-cutting, reserved for the end
  of all three siblings.

## Gate output referenced above, verbatim commands

```
python3 -m py_compile rig/derive.py
bash -n rig/run-pipeline.sh
python3 rig/derive.py --self-test
bash rig/run-pipeline.sh --self-test
python3 rig/derive.py --experiment tool-surface-v1
python3 rig/derive.py --experiment failure-flood-v1
./rig/check.sh
./check.sh
./hooks/pre-commit
```

All exited 0 except where a deliberate mutation is called out above.

---

# Sibling 3 — Face B + cross-cutting verification (tasks 3.1-3.8, 4.1-4.7, closes R-P7)

Scope of this section: **Sibling 3, tasks 3.1-3.8, plus cross-cutting tasks 4.1-4.7** (folded into this
commit per `tasks.md`'s own "run once at the end" framing, and because task 4.7 carries a real edit).
This is the **last work unit of the cycle** — after this section, every task in `tasks.md` is `[x]`.

**Resumption note.** This work unit resumed a prior attempt that was killed by a runtime watchdog after
writing real, uncommitted work (tasks 3.1, 3.2, and most of 3.3/3.4's self-test cases) but committing
nothing and leaving no done-notes. That work was independently audited against the code before being
trusted or extended — see "Inherited-state audit" below — rather than accepted on the prior attempt's
unrecorded intent.

**Amendment note (same day, 2026-08-27, amended twice).** After this section's first version was
committed (`afced18`), independent orchestrator gatekeeping re-verified every claim and found them all
correct, then applied its own mutation target — the same method that found task 2.0 for Face A — and
found `fixture_digest_at()`'s own computation proven zero ways. Task 3.8 closed it, folded into an
amendment of the same commit (`123b622`) rather than a fourth. Re-verified again, and a THIRD independent
mutation target found task 3.8's own new case was length-sensitive rather than content-sensitive (an
append-shaped mutation stayed green under a byte-count-hashing bug). Strengthened to a same-length
mutation in a second amendment of that same commit (`123b622` amended again in place — a new SHA results,
recorded at the end of this section). Every section below reflects the final, twice-amended state; where
a number changed, both the original and the corrected figure are kept per this note's own record-not-erase
discipline.

## The boundary this batch still leads with

The `failure-flood-triage` cycle delivered an instrument and a **FAILED** ratio target, never a
comparative result. After this batch's changes and the final re-derive (task 3.7), all three rows in
`rig/results/failure-flood-v1/runs.jsonl` remain `state=void, void_reason=shakedown`. **N is still 0
countable rows.** No real `claude -p` invocation was spent; every criterion below is satisfied by
`--self-test` or by re-deriving already-committed raw captures.

## R-F5.3 claim boundary (task 3.5, R-P7.2)

**Any reference to the archived `R-F5.3` re-derive check — in this note, in `rig/README.md`, in
`MAP.md`, or anywhere else this cycle touches — MUST state, and this note now states explicitly, that
R-F5.3's byte-identical re-derive check verifies deriver drift only, never fixture drift.** A re-derive
re-reads the same live manifest the run itself was scored against, so it necessarily agrees with
itself; it cannot detect that the fixture the run was scored against has since drifted, because it never
compares against anything the run recorded at run time. Fixture drift — the frozen `recorded_fixture_
digest` disagreeing with a live recompute of the same manifest — is exactly what Face B (this sibling's
own tasks 3.1/3.2) exists to catch instead, by recording a run's own claim about what it was scored
against and comparing that claim, not the live tree, against the live tree later.

## Inherited-state audit (the uncommitted diff, judged from the code)

Judged against the code itself, never against the prior attempt's own (absent) stated intent:

| Task | Inherited state | Evidence |
|---|---|---|
| 3.1 | **Fully complete, correct.** | `RECORDED_FIXTURE_DIGEST` computed via the exact `LOCKFILE_SHA256` one-liner idiom, right after the MANIFEST gate; threaded into `arm.json`. No self-test case added — correct per the task's own literal verify criterion (`bash -n` only), not a gap (see task 3.1's own done-note). |
| 3.2 | **Fully complete, correct.** | Null-check chain extended with `recorded_fixture_digest is None`; pass 3 gained the `live_fixture_digest`/`"fixture-drift"` block, joining the shared `drifted` set with no insertion-point framing. |
| 3.3 | **Partly complete.** Case (d) (both-drifts-recorded) was present and passing. **The order-swap proof (the task's own second half) was missing entirely** — no swapped-order test, no note about one. Implemented in this batch (see below). |
| 3.4 | **Fully complete, correct.** | Case (a), the full negative control, present and passing exactly as specified. |
| 3.5 | **Not started.** | No claim-boundary statement existed anywhere in the working tree (`apply-progress.md` untouched by the prior attempt). Written in this batch, above. |
| 3.6 | **Fully complete, correct, and N=0-compliant.** | `rig/README.md`'s correction paragraph re-read specifically against the N=0 constraint in this batch — it describes only schema fields, never implies a comparative result. |
| 3.7 | **Not started.** | The prior attempt's own self-test evidence (58/28 PASS) came from the working tree as left, but no final `--experiment failure-flood-v1` re-derive with by-hand row inspection had been recorded. Run in this batch. |

Two things the operator could not determine from measurement alone were settled directly:

1. **Task 3.3's swap requirement was genuinely missing**, not merely undocumented — confirmed by
   searching `derive.py`'s diff for "swap" (no match) and by there being only four new self-test cases
   total (a-d), none of which construct or run a second, reordered code path. Closed in this batch (see
   "Order-swap proof" below).
2. **Task 3.1's own gap (no runner-side self-test case) is correct per the task text, not a gap.** Task
   3.1's own `Verify:` line reads `bash -n rig/run-pipeline.sh` only — no self-test case is required by
   the task itself, unlike task 2.1/2.3's explicit self-test requirement for `preimage_digest()`. The
   reason is structural, not an oversight: Face B's digest and its deriver-side twin (`fixture_digest_
   at()`) are the *same* "sha256 of one file's bytes" idiom on both sides (confirmed by direct code
   reading, not merely by the prior attempt's own comment claiming so), so there is no sort-order or
   newline-joining convention that could drift the two sides apart the way Face A's `hash_paths()`-based
   set digest or Face C's `preimage_digest()` could. `rig/run-pipeline.sh --self-test` staying at 28
   cases (unchanged from Sibling 2) is the expected, correct outcome.

## What was implemented (3.1-3.7 net; the code was inherited, tests/proofs were completed)

**`rig/run-pipeline.sh`** (+20/-4 lines, inherited, verified correct):

- `RECORDED_FIXTURE_DIGEST` computed right after the MANIFEST recompute-compare gate, via the same
  one-liner idiom `LOCKFILE_SHA256` already uses. Threaded into the `arm.json` writer's env block and
  `arm = {...}` dict.

**`rig/derive.py`** (+146/-34 lines, inherited plus this batch's completion of task 3.3):

- `recorded_fixture_digest = arm_data.get("recorded_fixture_digest")` read back, joining the null-check
  chain and the shared `drifted`-set accumulation exactly as tasks 1.5/2.4 already established.
- `FAILURE_FLOOD_SCHEMA_VERSION`'s own comment corrected in place (never silently overwritten) to name
  which sibling actually populated each of the four provenance fields, replacing two stale "null until
  Sibling N" forward references now that both are wired.
- `_self_test_make_ff_run_dir()`'s default arm now carries `recorded_fixture_digest` agreeing with the
  real committed `v1` fixture, composing with every pre-existing detector the same way Sibling 1/2's own
  defaults did for their own faces.
- `_self_test_build_row_fixture_provenance()` — new function, four cases (a-d) exactly as task 3.2/3.3/
  3.4 specify, registered in `run_self_test()`'s roster.

**`rig/README.md`** (+13/-1 lines, inherited, re-verified against N=0 in this batch):

- `schema_version` corrected 1 → 4; a new **Correction** paragraph naming all four provenance fields and
  the one sibling gap it does not also fix.

**`MAP.md`** (+1/-1 line, this batch):

- `sdd/`'s row count corrected 2 → 3 cycles; `run-input-provenance` named with the cycle's own boundary
  carried verbatim.

**`sdd/run-input-provenance/tasks.md`** (this batch): tasks 3.1-3.7 and 4.1-4.7 marked `[x]` with
done-notes; the Review Workload Forecast section corrected in place with actuals (see below) — a named
correction, not a silent overwrite, the same discipline task 3.6 applies to `rig/README.md`.

**`rig/results/failure-flood-v1/runs.jsonl`** and **`rig/results/tool-surface-v1/runs.jsonl`**:
re-derived one final time (task 3.7, 4.1).

## Order-swap proof (task 3.3, completed this batch)

A scratch copy, `rig/.swap-order-derive.py` (created under `rig/` because `REPO_ROOT` resolves from
`__file__`; deleted immediately after), had the answer-key-drift and fixture-drift check blocks'
relative code order physically swapped inside pass 3 — the fixture-drift block moved before the
answer-key-drift block, each keeping its own `live_*_digest` lookup and `drifted.add(...)` call intact.
`python3 rig/.swap-order-derive.py --self-test` run against that copy: all 58 cases, including case (d)
(the both-drifts-recorded case), PASS unchanged. The real file's `sha256`
(`156ffd0c674c68987be05e5a5936caedfc197a4d2c08aca06663a18d4b32b6fe`) was confirmed identical before and
after. This proves R-P2.2a's "order MUST NOT be observable" as a fact about the accumulation shape
itself (both checks write into the same `drifted` set with no early-exit branch between them), not a
claim about one particular ordering that happened to be tested — which is what the task's own text asks
for, distinct from the four self-test cases (a-d) alone.

## Mutation-proofs — every new detector in this work unit, including the inherited ones

Each mutation applied to a scratch copy of `rig/derive.py` under `rig/` (`rig/.mutant-derive.py`,
deleted immediately after every cycle), never the committed file; the real file's `sha256`
(`156ffd0c674c68987be05e5a5936caedfc197a4d2c08aca06663a18d4b32b6fe`) confirmed unchanged before and
after every single cycle:

| Detector | Mutation | Subtle or constant-returning | Cases turned red | Every other case |
|---|---|---|---|---|
| Fixture-drift comparison (task 3.2, pass 3) | `if recorded_fixture_digest != live_fixture_digest:` neutered to `if False:` | Branch-disable (same class as Sibling 2's own task 2.4/2.5/2.7 proofs) | fixture provenance (b), (d) — 2 of 58 | stayed green (56/58) |
| Null-check extension (task 3.2, pass 2) | `recorded_fixture_digest is None` term dropped from the `or`-chain | **Subtle** — a realistic one-term omission, not a constant return | fixture provenance (c) — 1 of 58 | stayed green (57/58) |
| Fixture-drift comparand source (task 3.2, pass 3) | `digests.get("fixture", ...)` swapped to `digests.get("answer_key", ...)` — wrong dict key | **Subtle** — a copy-paste bug from the answer-key check directly above it in the source, not a constant return | 13 of 58, including the negative control (fixture provenance a, surface-preimage provenance a, answer-key provenance a/c, both model-mismatch site cases, all four `case1-4` token/attribution cases) | stayed green (45/58) |
| Order of the answer-key-drift / fixture-drift checks (task 3.3) | Relative code order swapped (not a correctness mutation — an alternate valid ordering) | N/A — this is the order-swap proof, not a mutation-for-sensitivity | 0 of 58 (all still PASS, as required) | stayed green (58/58) |

**Recorded honestly, not smoothed over**: the third mutation's blast radius (13 cases) is much wider
than the first two (2 and 1 cases respectively). This is not a weaker proof — it is what a genuinely
subtle copy-paste bug at this join point actually does, because most `build_row_failure_flood`
self-test fixtures across the whole file now default to a fixture-provenance-intact arm (task 3.1's own
default), so a wrong comparand touches every one of them, not merely the fixture-specific cases. Task
3.4's own negative control (case a) is among the 13 — direct evidence the negative control is sensitive
to this exact class of bug, not merely a green case that never fires red under any mutation.

## Task 3.8 — `fixture_digest_at()`'s own fire-proof (added by amendment, strengthened by a second amendment)

**Found by independent orchestrator gatekeeping after `afced18` was first committed, not by this batch's
own mutation-proof table above** — the same method that found task 2.0 for Face A. That table proves the
*comparison* logic inside task 3.2's own check (the three rows above); it cannot see past its own
foundation, because every self-test that carries a `recorded_fixture_digest` default builds that default
by calling `fixture_digest_at()` itself. Replacing `fixture_digest_at()`'s body with `return
"constant-mutant"` left all 58 of this batch's own cases green — the function's own computation was
proven zero ways, exactly the shape task 2.0 closed for `answer_key_set_digest()` after Sibling 1.

`_self_test_fixture_digest_at()` added: builds a synthetic fixture root containing a `MANIFEST.sha256`,
digests it via `fixture_digest_at()`, mutates the file's bytes, re-digests, asserts the two differ —
never deriving the expected value by calling the function under test. Registered in `run_self_test()`'s
roster, last position.

**Second amendment, same day: the mutation itself was found length-sensitive, not content-sensitive, by a
third independent target the orchestrator chose after this task's first version was committed.** The
original mutation *appended* a line (`"...src/a.ts\n"` → `"...src/a.ts\nmutated  src/b.ts\n"`), changing
the byte length along with the content. A third mutation, `sha256_hex(str(len(manifest.read_bytes()))
.encode())` — hashing the byte COUNT rather than the bytes — still produced `digest_before !=
digest_after` under an append and stayed green (59/59), meaning the case could be satisfied by an
implementation that never reads the file's content at all. **This matters more for Face B than the
identically-shaped append in task 2.0's own case**: Face A's case is backstopped by a real
cross-language pin (task 2.0 part 2) — a length-hashing Python side would disagree with the bash side and
turn the pin red regardless of this specific weakness — and Face B correctly has no pin, which makes case
(a) the ONLY proof `fixture_digest_at()`'s computation has. A sole proof must not be satisfiable by an
implementation that never reads the content. Fixed by changing the mutation to same-length, one byte
different (`"deadbeef  src/a.ts\n"` → `"deadbeee  src/a.ts\n"`) instead of an append — this single change
strictly dominates the append form (still catches constant-body and path-hashing bugs, additionally
catches length-hashing bugs). Kept as one case, not split into two, since the same-length form subsumes
everything the append form caught.

**Mutation-proofs, three ways, in scratch copies of `rig/derive.py` under `rig/` (never the committed
file), real file `sha256` confirmed unchanged before and after every cycle:**

| Mutation | Subtle or constant-returning | Cases turned red | Every other case |
|---|---|---|---|
| `fixture_digest_at()` body replaced with `return "constant-mutant"` | Constant-returning — the exact mutation that proved the original gap | fixture_digest_at case (a) — 1 of 59 | stayed green (58/59) |
| `fixture_digest_at()` hashes `str(manifest)` (the path) instead of `manifest.read_bytes()` | **Subtle** — the path is constant across the before/after digest calls within one test run, so `digest_before == digest_after` always under this bug | fixture_digest_at case (a) — 1 of 59 | stayed green (58/59) |
| `fixture_digest_at()` hashes `str(len(manifest.read_bytes()))` (the byte count) instead of the bytes | **Subtle, and the specific gap the orchestrator's second finding named** — under the ORIGINAL append-shaped mutation this stayed green (59/59); under the strengthened same-length mutation it now turns red like the other two | fixture_digest_at case (a) — 1 of 59 | stayed green (58/59) |

All three mutations are isolated to exactly the new case, confirming it is sensitive to the naive
constant-return bug, the subtler wrong-source (path) bug, and the subtler-still wrong-source (length) bug
— not merely to the first two, which is what the strengthened, same-length mutation specifically buys
over the original append-shaped one.

**Task 2.0's own `answer_key_set_digest` case (a) was deliberately left unchanged**, not given the same
same-length treatment — its own docstring now records explicitly why: it is backstopped by its own
cross-language pin (case b), which a length-hashing Python side would fail regardless of case (a)'s own
mutation shape. Recorded so a later reader does not conclude the two cases were held to different
standards by accident — they are held to the same standard by different mechanisms (a real pin for Face
A, a strengthened sole case for Face B, which has none).

**No cross-language pin was added, and none is needed.** `rig/run-pipeline.sh`'s `RECORDED_FIXTURE_
DIGEST` (task 3.1, `:738`) and `rig/derive.py`'s `fixture_digest_at()` compute the identical
`sha256(file bytes)` idiom — the same `LOCKFILE_SHA256` pattern, chosen at task 3.1 specifically so no
independent reimplementation exists on either side to drift apart. A pin proves two independent
algorithms agree; there is one algorithm here, expressed twice, with nothing left for the two sides to
disagree about except bytes both already read from the same file. Stated here so a later reader does not
add a pin that would prove nothing beyond what case (a) already proves.

**The method note, stated once rather than per-sibling**: a phase's own mutation-proof table cannot find
a gap in the foundation its own tests are built on, because every comparison the phase's own tests
construct derives both sides from the same function under test — and even a foundation-level fire-proof
case, once added, can itself carry a narrower blind spot (length-sensitivity standing in for
content-sensitivity) that only a fresh, independently-chosen mutation target finds. This is now
confirmed twice at the foundation level in this one cycle (task 2.0 for `answer_key_set_digest()`/Face A,
task 3.8 for `fixture_digest_at()`/Face B) and a third time at the mutation-shape level within task 3.8
itself — in every case by the orchestrator independently re-running the proof and choosing its own
target, never by the apply phase re-running its own table against itself.

## Verification evidence

**`rig/derive.py --self-test`** — all **59** cases PASS (54 pre-existing, Sibling 2's own committed
baseline, + 4 fixture provenance cases a-d + 1 `fixture_digest_at` fire-proof, task 3.8, added by
amendment).

**`rig/run-pipeline.sh --self-test`** — all **28** cases PASS, unchanged from Sibling 2 — correct per
task 3.1's own verify criterion, not a gap (see "Inherited-state audit" above).

**`python3 -m py_compile rig/derive.py`** — clean. **`bash -n rig/run-pipeline.sh`** — clean.

**Re-derive (task 3.7):** `python3 rig/derive.py --experiment failure-flood-v1` — all three rows:
`state=void, void_reason=shakedown` (unchanged), `anomaly_classes == ["pre-scheme-provenance"]` exactly,
`schema_version == 4`, `input_provenance_version`/`recorded_answer_key_digest`/`recorded_fixture_digest`
all `null`, every step's `recorded_surface_preimage_sha256` `null`. Inspected by hand, field-by-field.

**`tool-surface-v1` non-regression, cycle-wide baseline (task 4.1):** cycle-wide pre-change baseline
established as `a2cbd6f` (the last commit touching `rig/derive.py`/`rig/run-pipeline.sh` before Sibling
1's first commit, `0637d68` — distinct from any single sibling's own diff-against-its-own-prior-state
check). 42 rows, projected excluding only `checker_digest`, zero mismatches against `a2cbd6f`'s committed
file; `schema_version` stays `3` on every row. `build_row` (now `:411`) and the `tool-surface-v1`
registry entry (now `:1245-1255`) both confirmed byte-identical against `a2cbd6f` by direct extraction
and comparison — after an initial extraction-boundary mistake (see task 4.1's own done-note in
`tasks.md`) was caught and corrected before being reported.

**`failure-flood-v1`'s own projection (task 4.2):** same `a2cbd6f` baseline, excluding `schema_version`,
`checker_digest`, `anomaly_classes`, and the four fields this change adds. Zero mismatches across all 3
rows; every row still `state=void, void_reason=shakedown`.

**Deriver idempotence (task 4.3):** both experiments derived twice in a row over the same raw captures;
`runs.jsonl` byte-identical between the two runs, both experiments.

**Refusal-to-derive (task 4.4):** `checker_self_test`'s `t1/negative_control.expected_practice_pass`
deliberately corrupted `false` → `true` directly in `rig/fixtures/tool-surface/v1/answer-key/t1.json`
(backed up to `/tmp` first — `load_answer_keys()` reads a fixed real path, so there is no separate
"scratch copy" location for it, a deviation from the task's literal wording recorded rather than made
silently). `python3 rig/derive.py` (no `--experiment` flag; defaults to `tool-surface-v1`) exited 1:
"Self-test FAILED — a detector cannot be proven to fire. Refusing to derive rows." `runs.jsonl`'s
`sha256` unchanged before/during/after — no rows written. Fixture restored from the `/tmp` backup
immediately after; `git diff` on it confirmed empty; re-run afterward, exit 0, identical checksum to
before the mutation.

**`./rig/check.sh`** — 20/20 checks pass.

**`./check.sh` (root)** — clean, `structure check: clean across 111 content files and 5 skill(s)`.

**`./hooks/pre-commit`** — exit 0, no output (ADR 0009 redaction scan clean across every staged byte,
including the re-derived `runs.jsonl` files and the corrected `MAP.md`/`tasks.md`).

## Review Workload Forecast — corrected with actuals (recorded, not silently overwritten)

`tasks.md`'s own Review Workload Forecast section previously stated "800-line budget: NOT at risk" with
"~285 lines of headroom." That was false by the time Sibling 2 landed and is now corrected in `tasks.md`
itself with two named "Correction" sections (the first at Sibling 3's original commit, the second after
task 3.8's amendment), per the same discipline task 3.6 applies to `rig/README.md`. Restated here for
this note's own completeness, in its final, post-amendment form:

| Sibling | Forecast | Actual authored (after task 3.8) |
|---|---:|---:|
| 1 (Face A + WARNING-14) | ~260 (45 runner + 215 deriver) | **385** (32 runner + 353 deriver) |
| 2 (Face C + task 2.0) | ~150 (70 runner + 80 deriver) | **341** (80 runner + 261 deriver) |
| 3 (Face B + task 3.8) | ~105 | **323** (24 runner + 285 deriver + 14 README) |
| **Total** | **~515** | **1049** |

(The pre-amendment figure, kept rather than deleted: Sibling 3 was **218** and the total **944** before
task 3.8's 56-line self-test addition — see `tasks.md`'s own "Second correction" section for the same
before/after table.)

The running total after Sibling 2 alone was **726** authored lines against the 800-line budget. The
operator authorized `size:exception` on 2026-08-26 rather than re-slicing, because R-P9.2 makes Sibling 1
alone insufficient to satisfy the spec (Face C and Face B are both still-open requirements with only
Sibling 1 landed) and task 3.4's negative control — the proof that the combined gate does not always
void — is first achievable only once all three siblings' digests exist; splitting Sibling 3 into its own
PR would have merged a state that provably does not satisfy its own contract. Part of the overrun is
legitimate scope growth, not estimation error: task 2.0 was raised by independent gatekeeping after
Sibling 1 was already committed and was never in the original forecast at all; task 3.8 is the same
pattern recurring once more, found the same way, after Sibling 3 itself was already committed.

## Line accounting

**Authored code** (`rig/*.py`, `rig/*.sh`, `rig/README.md`), this batch's final, post-amendment state,
`git diff --numstat` insertions+deletions against `5cfa456` (the pre-Sibling-3 baseline):

| File | Lines |
|---|---:|
| `rig/derive.py` | 285 (250+35) |
| `rig/run-pipeline.sh` | 24 (20+4) |
| `rig/README.md` | 14 (13+1) |
| **Sibling 3 total** | **323** |

Of `rig/derive.py`'s 285, 105 lines closed task 3.8 across the two rounds inside the one amended commit
— 56 for `_self_test_fixture_digest_at()` plus its roster registration, then 49 more for the same-length
mutation strengthening and the docstring recording why a length-sensitive fire-proof is satisfiable by an
implementation that never reads the content. The remaining 180 are unchanged from the pre-amendment
commit.

**Generated** (`rig/results/*/runs.jsonl`): re-derived twice in this batch (once mid-batch, once final at
task 3.7/4.1) — task 3.8 added no further re-derive, since it touches no row-building code path, only a
self-test. Excluded from the authored count per the work-unit-commits convention, included in full
byte-snapshot identity and the redaction gate.

**SDD artifacts** (`sdd/run-input-provenance/tasks.md`, `sdd/run-input-provenance/apply-progress.md`,
`MAP.md`): this batch's own edits — task done-notes, the Review Workload Forecast correction, this
section, and the one-line `MAP.md` correction. Not counted toward the 800-line review budget (that
budget is about `rig/` code, per the forecast table's own scope), but included in the redaction gate the
same as every other staged byte.

## Task 2.5's comparand distinction, re-checked after task 3.2 (per the operator's finding 1)

Sibling 2's apply-progress note recorded that task 2.4's gate makes task 2.5's own comparand choice a
provable no-op at the row-outcome level, because every row reaching the read-back loop already has
`recorded_surface_preimage_sha256 == ff_surface_digest` by construction of the gate it just passed. Task
3.2 joins a third check (`fixture-drift`) into the same shared `drifted`-set accumulation pass task 2.4's
own check already lives in. **The no-op remains a no-op after task 3.2 — it did not become observable.**
Task 3.2's own check operates on a different pair of values entirely (`recorded_fixture_digest` vs.
`live_fixture_digest`, both arm-level) than task 2.5's read-back comparison (`step_surface` vs.
`recorded_surface_preimage_sha256`, both per-step) — adding a third, independent check to the
accumulation pass does not change what values task 2.4's own check constrains before the read-back loop
is reached. Re-verified directly rather than assumed: reverting task 2.5's own comparand from `recorded_
surface_preimage_sha256` back to `ff_surface_digest` in a scratch copy, with the full Sibling 3 code
present, still produces **zero** row-outcome differences across all 58 cases — the same finding Sibling 2
recorded, now confirmed to still hold with Face B's check present.

## Deliberately not done

- **No new ADR.** Out of scope for this whole change regardless (design.md's own recommendation).
- **`rig/check.sh`'s missing bash self-test arm** (Decision 3's own named gap) is not fixed here — named
  out of scope by the spec itself.
- **No real `claude -p` run.** Every criterion above is satisfiable by synthetic self-test or by
  re-deriving already-committed raw captures. Whether to fund a real, countable run stays the operator's
  own decision, untouched by this batch.
- **Nothing remains after this section.** This is the last work unit of the cycle; all of `tasks.md` is
  `[x]`.

## Gate output referenced above, verbatim commands

```
python3 -m py_compile rig/derive.py
bash -n rig/run-pipeline.sh
python3 rig/derive.py --self-test
bash rig/run-pipeline.sh --self-test
python3 rig/derive.py --experiment tool-surface-v1
python3 rig/derive.py --experiment failure-flood-v1
./rig/check.sh
./check.sh
./hooks/pre-commit
```

All exited 0 except where a deliberate mutation is called out above (each mutation cycle used a scratch
copy, never the committed file, and confirmed the real file byte-identical afterward).

## Task 2.9 — closing `sdd-verify`'s blocking CRITICAL-1 (commit 4, this batch)

`sdd-verify` graded the cycle **FAIL** on one CRITICAL: `load_surface()`'s own parse — the producer of
Face C's live drift comparand, `surface_digest(load_surface(FAILURE_FLOOD_SURFACE_ARM))` at
`rig/derive.py:901` — was proven ZERO ways. Every self-test that supplies a
`recorded_surface_preimage_sha256` default computes that identical expression once
(`_self_test_make_ff_run_dir`, `:1519`) and assigns it to both sides of every Face C comparison, and the
committed pin (`_self_test_preimage_digest_pin`, task 2.1) asserts `surface_digest()` over a hand-built
Python list, never calling `load_surface()` at all. Confirmed independently, not accepted from the
verify report alone: three mutations of `load_surface()` (dropping the `#` header filter, slicing the
sorted list `[1:]`, removing `.strip()` from the returned value) each left the pre-existing 59-case suite
green. This is the third occurrence of the exact pattern task 2.0 (Face A) and task 3.8 (Face B) already
closed in this cycle.

**No live defect — stated plainly so this reads as a gap closed, not a bug fixed.** Independently
verified before writing this note: today, Python's `surface_digest(load_surface("failure-flood"))` and
bash's `preimage_digest()` (`sed`-extracted from `rig/run-pipeline.sh`) already agree over the real
committed `rig/surfaces/failure-flood.txt` — both print
`d8693e27d5f8e406a465def75101c4eaa85b23b685e78c2d5d07754d0f7e8daa`. The gap this task closes is that
nothing committed would have caught the two sides drifting apart, not that they currently disagree. The
fault, had it existed, could only over-void (Face C's drift accumulation at `:974-978` voids on any
disagreement between recorded and live); it could never promote a row to `complete`, and N = 0 today.

**What was done.** `_self_test_load_surface_preimage_pin()` added to `rig/derive.py`, registered in
`run_self_test()`'s roster immediately after `_self_test_preimage_digest_pin()`. It runs the deriver's
own full path — `surface_digest(load_surface(arm))`, never a hardcoded list — over one synthetic
preimage file it writes and deletes at `SURFACES_ROOT / "__self_test_load_surface_preimage_pin.txt"`,
the exact path shape `load_surface()` is hardcoded to (it takes no root parameter, so this is the only
way in without weakening it; `load_surface()` itself is unchanged). Content:
`"# harness: v1\n\nBash\n\n  Read\nWrite\nRead   \n"` — a `# harness:` header (excluded), blank lines
(excluded), a duplicate tool name across an indented and a trailing-whitespace form (both stripped, and
still deduped against each other once stripped). Asserted against the SAME kind of cross-language pin
task 2.0 part 2 built for Face A: `preimage_digest()` `sed`-extracted from `rig/run-pipeline.sh`,
executed over the identical file — never the weaker shared-literal mechanism task 2.1 used.

Both sides independently computed and confirmed equal at
`4a626b46a7841184c5d423277a9c17cb15129f4ba32f92a88948b77735bfdcd3` — the same constant task 2.1's pin
already carries, because this synthetic file's deduped set is the identical `{Bash, Read, Write}`. That
is a useful coincidence recorded so a later reader does not mistake it for reuse of the old pin: this
case never calls the pin, and it exercises the full file parse the old pin never touched.

## Mutation-proof table (task 2.9)

Each mutation applied to a full scratch copy of the repository tree under `rig/.scratch-task29-<pid>/`,
deleted after every run; the real `rig/derive.py` `sha256`-verified byte-identical
(`0ce09c0680457c15d2fb4509b3325d9fa1d4e7c692d423fe16409c676292d004`) before this task started and again
after all three mutation cycles completed.

| # | Mutation | `derive.py --self-test` | Case counts |
|---|---|---|---|
| Baseline | unmutated | **60/60 PASS**, exit 0 | 60 PASS / 0 FAIL |
| M1 | drop `and not l.startswith("#")` from `load_surface()`'s filter | **FAIL**, exit 1 | 59 PASS / 1 FAIL (only the new case) |
| M2 | append `[1:]` to `load_surface()`'s return value | **FAIL**, exit 1 | 59 PASS / 1 FAIL (only the new case) |
| M3 | remove the value-side `.strip()` from the comprehension (filter's own `.strip()` truthiness check left intact) | **FAIL**, exit 1 | 59 PASS / 1 FAIL (only the new case) |

The synthetic file's own content was deliberately built so M2 is discriminating rather than vacuous: the
alphabetically-first tool name (`Bash`) appears exactly once (not duplicated), so slicing it off the
sorted list before dedup actually removes it from the deduped set rather than being masked by a second
occurrence surviving the slice. Held to a higher standard than a `return "constant"` control per this
batch's own governing instruction: all three mutations are realistic wrong-implementations of the parse
itself (a missing filter, a subset return, a missing strip), not a constant body.

## Line accounting (task 2.9)

`git diff --numstat -- rig/derive.py`: **98 insertions, 0 deletions** — the new self-test function, its
docstring, and its roster registration. No other file's authored line count changes; `rig/run-pipeline.sh`
is untouched by this task (the bash side is read, never written — `sed`-extracted, same as task 2.0 part
2's own convention).

Sibling 2's running total (`rig/run-pipeline.sh` + `rig/derive.py`) moves 341 (after task 2.0) → 439
(+98, this task). Cycle-wide total moves 1049 → **1147**. `tasks.md`'s own Review Workload Forecast
carries the same correction, in place, per this file's own record-not-erase discipline applied three
times now.

Re-derived both experiments after the edit: `git diff --stat -- rig/results/` showed
`failure-flood-v1/runs.jsonl` (6 lines changed, 3 rows) and `tool-surface-v1/runs.jsonl` (84 lines
changed, 42 rows); a field-by-field diff of every row before/after confirmed the only differing key on
every row, in both files, is `checker_digest` — `schema_version` unchanged (4 and 3 respectively), every
other field byte-identical.

## Gate output (task 2.9), verbatim commands and counts

```
python3 -c "import ast; ast.parse(open('rig/derive.py').read())"   # syntax ok
bash -n rig/run-pipeline.sh                                        # bash -n clean, unchanged by this task
python3 rig/derive.py --self-test                                  # exit 0, 60/60 PASS
bash rig/run-pipeline.sh --self-test                                # exit 0, 28/28 PASS, unaffected
python3 rig/derive.py --experiment tool-surface-v1                 # 42 rows re-derived
python3 rig/derive.py --experiment failure-flood-v1                # 3 rows re-derived
./rig/check.sh                                                     # 20/20 PASS, exit 0
```

All exited 0 on the real, unmutated tree. `./check.sh` and `./hooks/pre-commit` are run once more,
against the full staged set for this commit (this note plus `tasks.md`, `rig/derive.py`, the re-derived
result files, and the verify report), immediately before committing — their output is recorded in the
commit's own return contract rather than duplicated here.

## Deliberately not done (task 2.9)

- **WARNING-1 through WARNING-5, and the two SUGGESTIONS not already addressed** — all recorded in
  `sdd/run-input-provenance/verify-report.md`, out of scope for this work unit by the launch prompt's own
  instruction. Not fixed here.
- **No new ADR.** Same reasoning as the rest of this cycle — out of scope regardless.
- **No real `claude -p` run.** N stays 0; nothing in this task could change that boundary.
