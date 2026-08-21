---
id: sdd/run-input-provenance/apply-progress
type: journal
targets: [any]
status: draft
verified: 2026-08-21
sources: ["sdd/run-input-provenance/tasks.md", "sdd/run-input-provenance/spec.md", "sdd/run-input-provenance/design.md", "rig/derive.py", "rig/run-pipeline.sh"]
---

# run-input-provenance — apply progress (Sibling 1: Face A + WARNING-14)

Scope of this note: **Sibling 1 only** — tasks 1.1-1.11, closing R-P2, R-P3, R-P4, R-P5. Sibling 2
(Face C, R-P6) and Sibling 3 (Face B + the R-F5.3 claim boundary, R-P7) are **not started** — the
ordering in `tasks.md` (R-P9.2) is a dependency, not a preference, and this note makes no claim about
either sibling.

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
