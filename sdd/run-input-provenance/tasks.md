---
id: sdd/run-input-provenance/tasks
type: journal
targets: [any]
status: draft
verified: 2026-08-20
sources: ["sdd/run-input-provenance/proposal.md", "sdd/run-input-provenance/spec.md", "sdd/run-input-provenance/design.md", "sdd/archive/2026-08-18-failure-flood-triage/tasks.md", "rig/derive.py", "rig/run-pipeline.sh", "rig/check.sh", "rig/README.md"]
---

# Tasks: run-input-provenance

The `failure-flood-triage` cycle delivered **an instrument and a FAILED ratio target — never a
comparative result.** Every row in `rig/results/failure-flood-v1/runs.jsonl` is
`state=void, void_reason=shakedown`. **N = 0 countable rows.** No task, verification criterion, or
done-note below may imply a comparative result exists, is pending, or is nearly available. Every
criterion here is satisfied by `--self-test` or by re-deriving already-committed raw captures under
`rig/runs/` — **no task spends a real `claude -p` invocation.** Whether to fund a real, countable run
stays the operator's own decision, untouched by this cycle.

## Spec/design conflict — resolved 2026-08-20, `43f5281`

The prior draft of this file flagged a real conflict as blocking: `spec.md` Decision 1/R-P3.1 pinned a
per-face `void_reason` (`"answer-key-mismatch"`); `design.md` §4 argued for one generic
`"input-provenance-mismatch"` + `anomaly_classes` drift suffixes and explicitly rejected the per-face
approach. That flag was correct — the two could not both be implemented as written — and gatekeeping
has since resolved it in the source artifacts, not in this file. Both `spec.md` and `design.md` now
agree on the settled vocabulary below; **tasks in this revision implement that vocabulary directly, with
no reconciliation step remaining.**

**Design's conclusion won, but not for design's stated reason** — worth keeping visible rather than
collapsed into "design was right." Design argued per-face reasons "inflate the vocabulary every
consumer must implement, and `report.py` already names voids by reason." Verified and refuted:
`rig/report.py` is reason-agnostic (`classes.add(r["void_reason"])` at `:125-126`, interpolated at
`:163`/`:335` — no enum, no per-reason branch). Three reasons would have cost `report.py` nothing. The
argument that actually decides it, stated by neither original artifact: `answer-key/` sits inside
`compute_manifest()`'s walked set, so one edit to `answer-key/prereg.json` disagrees on the answer-key
digest **and** the fixture digest at once. A per-face reason forces the single `void_reason` slot to
pick a winner between two true findings — which means a precedence rule, and a precedence rule means
discarding one face's finding. One reason plus per-face drift classes in `anomaly_classes` records
**both** findings and removes the ordering hazard entirely, rather than resolving it with a rule.

### The settled vocabulary (spec.md Decision 1, design.md §4, now identical)

| `void_reason` | Fires when |
|---|---|
| `input-provenance-mismatch` | a recorded digest is present and disagrees with the live value |
| `input-provenance-missing` | the row cannot say what it was scored against at all |

| `anomaly_classes` member | Meaning |
|---|---|
| `answer-key-drift` / `fixture-drift` / `surface-preimage-drift` | which face disagreed |
| `pre-scheme-provenance` | `input_provenance_version` absent — capture predates the scheme |
| `provenance-capture-incomplete` | version present, a promised digest `null` |

**Every task below accumulates drifted faces before voiding, rather than branching on the first
mismatch found** — this is what makes R-P2.2a's "order MUST NOT be observable" true by construction: a
row is checked against every digest face its sibling(s)-to-date have wired in, every disagreement adds
its own `<face>-drift` member, and exactly one `void_reason="input-provenance-mismatch"` fires only
after that full pass, carrying every drifted face at once. There is no early-exit branch left to put in
a particular order.

Face C keeps its existing, unchanged `"surface-mismatch"` reason for its own, different condition (the
observed tool surface disagreeing with the frozen comparand) **and gains** the new
`"surface-preimage-drift"` class for a different condition (the frozen comparand itself disagreeing
with a live recompute) — R-P6.3, task 2.4 below. The two are not the same finding and do not share a
reason.

## Retirement of Task 7.15

Per R-P9.1: Task 7.15 (`sdd/archive/2026-08-18-failure-flood-triage/tasks.md:1867-1877`, "`fixture_digest`
records the present, not the run") is **retired**, never edited in the sealed archive file. Its own
wording named only the identity field (`fixture_digest`); verify round 4 judged that registration
inadequate — *"It names one field. The class is at least three fields wide"* (proposal, quoting the
round-4 finding). It is replaced by exactly three sibling tasks, in this file:

| Retired task | Replaced by | Closes |
|---|---|---|
| 7.15 | **Sibling 1** (tasks 1.x) | Face A + WARNING-14 — R-P2, R-P3, R-P4, R-P5 |
| 7.15 | **Sibling 2** (tasks 2.x) | Face C — R-P6 |
| 7.15 | **Sibling 3** (tasks 3.x) | Face B (7.15's own original scope) + the R-F5.3 claim boundary — R-P7 |

## Ordering — a dependency, not a note (R-P9.2)

```
Sibling 1 (Face A + WARNING-14)  ──blocks──▶  Sibling 2 (Face C)  ──blocks──▶  Sibling 3 (Face B)
   R-P2, R-P3, R-P4, R-P5                        R-P6                            R-P7
```

Sibling 2 depends on Sibling 1 because Face C's `is not None` guard at `rig/derive.py:855` currently
substitutes for the read-back check WARNING-14 closes; tightening it before Sibling 1 lands would strip
that substitute with nothing yet in its place. Sibling 3 depends on Sibling 2 because R-P9.2 forbids
declaring the class closed at Face B while Face A/C remain open, and because Sibling 3's own
fixture-digest check (task 3.2) must be added into the same drift-accumulation pass Sibling 1 built —
per R-P2.2a, that check joins the pass rather than being inserted at a particular point in it, so no
sibling can establish the completed accumulation standing alone. **A delivery that reaches Sibling 3
first and stops there MUST NOT be reported as satisfying this spec — R-P9.2 names the reason.**

---

## Sibling 1 — Face A + WARNING-14 (closes R-P2, R-P3, R-P4, R-P5)

Depends on: nothing. Blocks: Sibling 2, Sibling 3.

- [x] 1.1 **Record the resolved void_reason conflict, rewritten rather than deleted** — the same
      "record the inversion, don't erase the evidence" discipline task 1.9 applies to the committed
      self-test. This file's own prior draft correctly flagged spec.md and design.md as disagreeing and
      blocking; that flag has since been resolved upstream (`43f5281`, see the section above) in favor
      of design's conclusion but for a different, verified reason than design originally gave. Record,
      in this file's apply-progress note: (a) the conflict existed and blocked this file once, (b) the
      resolution and its real deciding argument (the `compute_manifest()` answer-key/fixture overlap,
      not the vocabulary-size argument either artifact first gave), (c) that the resolution outranks
      the observation that caused the original flag. This is no longer a gate on tasks 1.5 onward —
      those tasks already implement the settled vocabulary directly.
      Verify: structural readback — the three points above are present in the apply-progress note.
      Done: recorded in `sdd/run-input-provenance/apply-progress.md`'s "The resolved conflict, carried
      forward" section — all three points present.

- [x] 1.2 Add `answer_key_set_digest(root)` to `rig/derive.py`, mirroring `fixture_digest_at()`'s shape
      (`rig/derive.py:611-617`) — a digest over the answer-key relpaths under one fixture root only,
      never the merged `load_failure_flood_answer_keys()` dict (`:646-668`). Wire it into `main()`'s
      `digests` block (`:1473-1476`) as `digests["answer_key"]`, built **only when an experiment
      declares it** via `reg.get("answer_key_digest")` — the `tool-surface-v1` registry entry
      (`:1079-1089`) gains no key.
      Verify: `python3 -m py_compile rig/derive.py`; the `tool-surface-v1` registry entry is
      byte-unchanged (`git diff` against that dict literal is empty).
      Done: `answer_key_set_digest()` added next to `fixture_digest_at()`, reproducing `hash_paths()`'s
      convention (sorted "sha256(content)  relpath" lines, joined, hashed). Wired via a new
      `"answer_key_digest"` key on the `FAILURE_FLOOD_EXPERIMENT` registry entry only; `main()` builds
      `digests["answer_key"]` behind `reg.get("answer_key_digest")`. `py_compile` clean;
      `tool-surface-v1`'s registry dict literal byte-unchanged (verified by diff).

- [x] 1.3 In `rig/run-pipeline.sh`, after the MANIFEST recompute-compare gate (`:645-649`) — bytes now
      proven frozen — compute `recorded_answer_key_digest`: pipe the answer-key relpaths from
      `compute_manifest`'s own output (`:168` already walks `answer-key`) through the existing
      `hash_paths()` (`:215`), the same pattern `manifest_workspace_paths()` (`:189-191`) already uses
      to filter `compute_manifest`'s output by prefix. The runner MUST NOT resolve which file carries
      the row's `task_id` (R-P2.1) — it hashes the whole `answer-key/` set for its one fixture root.
      Hold the result in a shell variable with the same lifetime as `PREREG_DIGEST`/`CASE_TABLE_DIGEST`
      (until the `arm.json` write at `:1103`).
      Verify: `bash -n rig/run-pipeline.sh`.
      Done: new `answer_key_paths()` helper added beside `manifest_workspace_paths()` (same
      filter-by-prefix pattern); `RECORDED_ANSWER_KEY_DIGEST` computed right after the MANIFEST gate via
      `answer_key_paths "$FIXTURE_ROOT" | hash_paths "$FIXTURE_ROOT"`. `bash -n` clean. Cross-language
      agreement verified by hand: python's `answer_key_set_digest(v1)` and this bash pipeline both
      produce `571e083d27aaef0a63cee3b26de97b14ac8eccdab02dfbe3535aba83728cb7b6` over the real committed
      v1 answer-key set.

- [x] 1.4 Add `input_provenance_version: 1` and `recorded_answer_key_digest` to the `arm.json` writer's
      env-threading block (`:1060-1068`) and its `arm = {...}` dict (`:1080-1102`), the same way
      `PREREG_DIGEST`/`CASE_TABLE_DIGEST` are already threaded.
      Verify: `bash -n rig/run-pipeline.sh`.
      Done: `RECORDED_ANSWER_KEY_DIGEST` threaded into the arm.json writer's env block; `arm = {...}`
      gains `"input_provenance_version": 1` and `"recorded_answer_key_digest"`. `bash -n` clean.

- [x] 1.5 In `build_row_failure_flood`, insert the provenance gate **before** the existing per-step
      read-back loop (`:851-886`), inside the `if state == "complete":` block (`:850`), as three
      sequential passes (R-P5.5, downgrade-only — pass 1 must fully resolve before pass 2 is reached,
      and pass 2 before pass 3; **within pass 3, check order is never observable in the outcome**,
      R-P2.2a):
      1. `input_provenance_version` absent on `arm_data` → `void, void_reason="input-provenance-missing"`,
         `anomaly_classes` gains `"pre-scheme-provenance"` (R-P5.2). Row is done; passes 2–3 never run.
      2. version present, `recorded_answer_key_digest` is `None` → same `void_reason`, `anomaly_classes`
         gains `"provenance-capture-incomplete"` instead (R-P5.3). Row is done; pass 3 never runs.
      3. version present, digest present: build a `drifted = set()`. If `answer_key_set_digest(root)`
         recomputed live disagrees with the recorded value, add `"answer-key-drift"` to `drifted`
         (R-P3.1) — **do not void yet.** After this sibling's own check, and any check a later sibling
         adds to the same `drifted` set (tasks 2.4, 3.2), if `drifted` is non-empty: `void,
         void_reason="input-provenance-mismatch"`, `anomaly_classes |= drifted`. An empty `drifted` set
         means provenance is proven; the row is untouched by this gate. This accumulate-then-decide
         shape is what makes R-P2.2a's "order MUST NOT be observable" true by construction — there is
         no early-exit branch order to matter.
      Must run before `verdict`/`integrity_guard_pass`/`causes_claimed`/`causes_correct` are computed
      (mirrors the existing `suite_state_cause == "environment"` ordering at `:976-982`). This gate MUST
      NOT run, and MUST NOT fire, against a row an earlier check already voided (R-P3.2) — same
      discipline as the existing checks at `:839-841`, `:850-862`, `:976-978`.
      Verify: `python3 -m py_compile rig/derive.py`.
      Done, with one deliberate deviation from this task's literal wording, recorded rather than
      silently made: R-P5.2's own text requires the **pre-scheme annotation** (`"pre-scheme-provenance"`)
      to fire on an already-void row (proven by the three shakedown rows, R-P8) while the **state
      transition** stays downgrade-only — that is a stricter rule than "insert everything inside one
      `if state == 'complete':` block." Implemented as: the marker-absence check always runs and always
      annotates, gating only its own state transition on `state == "complete"`; the null-digest check
      (pass 2) and the accumulate-then-decide mismatch check (pass 3) are nested inside their own
      `elif state == "complete":`, so they never annotate or transition an already-void row (R-P3.2).
      This is a stricter, not a looser, reading of the task — self-test case h (task 1.10) is the proof
      this split is required: a naive single-block version fails it.

- [x] 1.6 Fix the two unguarded subscripts (R-P4.1): `ak["F0"]["failures"]` (`:981`) and `len(ak["R0"])`
      (`:1071`) become `.get()`-based, following the existing precedent at `:987-994` (no answer key →
      scored fields stay `None`, row not voided). A malformed key (missing `F0.failures` or `R0`) adds
      `"answer-key-drift"` to task 1.5's `drifted` set, reaching the same
      `void_reason="input-provenance-mismatch"` as a digest mismatch — per R-P4.1's own text, "not a
      separate class needing its own reason." `causes_present` MUST become
      `len(ak["R0"]) if ak and "R0" in ak else None`, never `0` — absence is not a count (design §3).
      Verify: `python3 -m py_compile rig/derive.py`.
      Done: both subscripts are `.get()`-based now (`ak.get("F0", {}).get("failures", [])`,
      `len(ak["R0"]) if ak and "R0" in ak else None`); a malformed key (missing `F0.failures` or `R0`)
      joins task 1.5's `drifted` set inside the provenance gate. Mutation-proven: disabling this check
      in a scratch copy reverts to the direct `ak["R0"]` subscript and raises `KeyError` mid-derive on
      self-test case f — confirming the totality fix is load-bearing, not decorative.

- [x] 1.7 Change the `is False` downgrades to not-`True` at `:859` (`permission_mode_matches_declared`)
      and `:883` (`model_matches_declared`) — R-P5.4. A `None` read back from a row whose
      `input_provenance_version` is present now voids with the existing reason
      (`"permission-mode-mismatch"` / `"model-mismatch"`). Task 1.5's gate already voided any row with
      no `input_provenance_version` before this loop is reached, so this change cannot double-punish a
      pre-scheme row (R-P5.5) — it fires only for a scheme-aware capture.
      Verify: `python3 -m py_compile rig/derive.py`.
      Done: both sites changed to `is not True`. Mutation-proven for BOTH sites individually — reverting
      either one alone to `is False` in a scratch copy turns exactly one self-test case red (the
      model-mismatch case for `:883`, and a newly-added case for `:859` — see task 1.9/1.10's done-notes
      for the gap that second one closed) and leaves every other case green, proving the two checks are
      independently exercised.

- [x] 1.8 Bump `FAILURE_FLOOD_SCHEMA_VERSION` 3 → 4 (`:621`), with a comment following the file's own
      convention (`:39-45`'s v2→v3 comment) naming every field this bump adds:
      `input_provenance_version`, `recorded_answer_key_digest`, `recorded_fixture_digest` (null until
      Sibling 3), and each model step's `recorded_surface_preimage_sha256` (null until Sibling 2). No
      migration code, no read of the old `schema_version` value to special-case a row (R-P11.1).
      Verify: `python3 -m py_compile rig/derive.py`.
      Done: bumped to 4 with a comment naming all four fields (the two this batch populates,
      `input_provenance_version` and `recorded_answer_key_digest`, plus the two named-but-not-yet-wired
      `recorded_fixture_digest` and per-step `recorded_surface_preimage_sha256`), stacked above the
      existing v2→v3 comment rather than replacing it. No migration code; re-derive rewrites every row.

- [x] 1.9 **Rewrite (never delete) `_self_test_build_row_model_mismatch()`'s case 3** (`:1260-1270`) —
      R-P10.2. It currently asserts `model_matches_declared: None → state == "complete"`, labelled
      *"old capture — never falsely voids"*; that pinned the defect (WARNING-14 point 1). Rewritten:
      construct the same fixture with no `input_provenance_version`, assert
      `state == "void", void_reason == "input-provenance-missing"`. Add a **new**, additional case in
      the same function: provenance-**intact** (`input_provenance_version` present),
      `model_matches_declared: None`, assert `state == "void", void_reason == "model-mismatch"`.
      Verify: `rig/derive.py --self-test` — both cases print `PASS`; deleting either one leaves half of
      WARNING-14 unproven, per R-P10.2's own scenario.
      Done: case 3 rewritten in place (never deleted) to assert the pre-scheme void; case 4 added
      asserting the provenance-intact `model-mismatch` void. A FIFTH case was also added here, beyond
      this task's own scope, closing a gap mutation-testing found: R-P5.4 and design.md sec 9 both name
      "both sites" (`permission_mode_matches_declared` AND `model_matches_declared`), but only the model
      site had a proving case. Case 5 proves the permission-mode site the same way. Mutation-proven:
      reverting `:883` alone to `is False` turns only case 4 red; reverting `:859` alone to `is False`
      turns only case 5 red; the real file is byte-identical after each mutation cycle.

- [x] 1.10 Add a new self-test function, `_self_test_build_row_answer_key_provenance()`, registered in
      `run_self_test()`'s roster (`:1420-1428`) alongside the existing seven, built on
      `_self_test_make_ff_run_dir` (`:1216-1235`) extended to carry `input_provenance_version` and
      `recorded_answer_key_digest` in its synthetic `arm.json`. Cases (ADR 0013 — every detector must
      be proven able to FIRE, not merely proven silent on clean input):
      - **a.** all provenance present and agreeing → `state == "complete"` (negative control — a gate
        that always voids passes every later case too).
      - **b.** `recorded_answer_key_digest` deliberately mismatches a real on-disk fixture answer key →
        `void, void_reason == "input-provenance-mismatch"`, `"answer-key-drift"` in `anomaly_classes`
        (R-P10.1's own named scenario).
      - **c.** an unrelated task's answer key changes; this row's own key does not → row unaffected
        (spec's "An unrelated answer key changing does not touch this row" scenario).
      - **d.** `input_provenance_version` absent → `void, void_reason == "input-provenance-missing"`,
        `"pre-scheme-provenance"` in `anomaly_classes` (R-P5.2).
      - **e.** version present, `recorded_answer_key_digest` is `null` → same `void_reason`,
        `"provenance-capture-incomplete"` in `anomaly_classes`, **never** `"pre-scheme-provenance"`
        (R-P5.3 — cases d and e MUST reach different anomaly classes or the two absences are
        conflated).
      - **f.** a malformed answer key (`F0.failures` and `R0` both absent) → no exception;
        `state == "void", void_reason == "input-provenance-mismatch"`, `"answer-key-drift"` in
        `anomaly_classes`; `verdict is None`; `causes_present is None`, never `0` (R-P4.1, task 1.6's
        proof).
      - **g.** a row already `void` for another reason before this gate runs → `void_reason` unchanged,
        never overwritten by `"input-provenance-mismatch"` (R-P3.2).
      - **h.** the three existing shakedown rows, no provenance at all → keep
        `void_reason == "shakedown"`, gain `"pre-scheme-provenance"` (R-P8's proof, using a synthetic
        fixture shaped like the real rows, not the real rows themselves).
      Verify: `rig/derive.py --self-test` — all eight cases print `PASS`.
      Done: all eight cases (a-h) implemented exactly as specified and PASS. Each mutation-proven able
      to fire: the digest-mismatch check (b), the pre-scheme annotation (d, h), the null-digest check
      (e), and the malformed-key check (f) were each deliberately broken in a scratch copy of
      `rig/derive.py` (never the committed file) and confirmed to turn exactly the case(s) that check
      protects red, with every other case staying green and the real file byte-identical afterward
      (`git status`/`sha256sum` checked before and after every mutation cycle). Case c is proven by
      construction (per-root indexing) rather than by editing a real fixture file, per the task's own
      instruction.

- [x] 1.11 Re-derive `rig/results/failure-flood-v1/runs.jsonl` from the raw captures already under
      `rig/runs/failure-flood-v1/` (no new run). Confirm the three rows still read
      `state=void, void_reason=shakedown`, now gain `"pre-scheme-provenance"` in `anomaly_classes`, and
      `input_provenance_version`/`recorded_answer_key_digest`/`recorded_fixture_digest` are `null`.
      Verify: `python3 rig/derive.py --experiment failure-flood-v1`; inspect the three rows by hand;
      confirm no row acquired `state=complete` (R-P1.1).
      Done: re-derived. All three rows: `state=void, void_reason=shakedown` (unchanged),
      `anomaly_classes == ["pre-scheme-provenance"]` exactly, `schema_version == 4`,
      `input_provenance_version`/`recorded_answer_key_digest`/`recorded_fixture_digest` all `null`. N
      stays 0 — no row acquired `state=complete`. `tool-surface-v1` was also re-derived (unavoidable —
      `checker_digest` is stamped on both experiments from `derive.py`'s own file bytes, R-P11.2) and its
      42-row projection (excluding only `checker_digest`) is byte-identical to the pre-change file, with
      `schema_version` unchanged at 3 and `build_row`'s registry entry byte-unchanged — this is 4.1's own
      check, run early because editing `derive.py` forced the re-derive regardless; the full cross-cutting
      pass still belongs to 4.x.

---

## Sibling 2 — Face C (closes R-P6)

Depends on: Sibling 1. Blocks: Sibling 3.

- [x] 2.0 **Face A's digest computation is unproven, and its cross-language pin was never built.**
      Found by independent orchestrator mutation-proof after Sibling 1 was committed (`0637d68`), not
      by the apply phase. **Close this before any further Face-A behaviour is trusted.**

      **What is proven, and what is not.** Seven independent mutations of Sibling 1's provenance gate
      each turn `rig/derive.py --self-test` red, so the *comparison* logic is well proven. But replacing
      `answer_key_set_digest()`'s entire body with `return "constant"` leaves **all 43 cases green**.
      Every self-test derives its expected digest by calling `answer_key_set_digest()` itself
      (`derive.py:1373`, `:1406`, `:1466`, `:1519`, `:1613-1614`), so both sides of every comparison
      move together and the function's own computation is proven zero ways.

      **This is this cycle's own defect pattern, recursed.** The reason R-F5.3 cannot detect fixture
      drift is that it re-reads the same live manifest and agrees with itself. A self-test that computes
      both sides of its comparison with the function under test cannot detect that the function is
      wrong, for exactly the same reason. Noting it here so the parallel is not lost: the fix for the
      instrument and the fix for the instrument's own test are the same idea.

      **The cross-language pin was verified, but not committed — and that is the distinction that
      matters.** Task 1.3's done-note is honest and correct: it records that Python's
      `answer_key_set_digest(v1)` and bash's `answer_key_paths | hash_paths` pipeline both produce
      `571e083d27aaef0a63cee3b26de97b14ac8eccdab02dfbe3535aba83728cb7b6` over the real committed v1
      answer-key set. Nobody skipped the check. **It was done by hand, once, and nothing committed will
      catch the two sides drifting apart afterwards** — which is precisely the recurrence ADR 0013 exists
      to catch, and the exact shape task 7.10 was created to stop: a verification performed ad hoc and
      never turned into a committed test. Task 2.1 already requires a real pin for Face C's pair;
      Sibling 1's pair asked only for "verified by hand", so this is a **planning gap, not an apply
      failure**.

      Convenient consequence: the constant design asked to pin with **already exists** — it is in task
      1.3's done-note above. This task is committing it, not discovering it.

      `design.md`'s risk list named the obligation: *"Two cross-language digest agreements are created
      (answer-key set, surface preimage), each pinned by a shared literal constant. A pin failure is the
      finding, not a thing to 'fix' on the failing side."* The runner records in bash
      (`answer_key_paths()` → `hash_paths()`, `run-pipeline.sh:200-201`); the deriver compares in Python
      (`answer_key_set_digest()`, `derive.py:620-646`). `answer_key_paths()` has no `--self-test` case of
      any kind; the only answer-key cases the runner suite carries today are task 7.10's
      `compute_manifest` ones.

      **Why it is not theoretical.** If the two sides differ by so much as a trailing newline, then on
      the first real countable run *every* row voids with `answer-key-drift` — a correct-looking refusal
      whose stated cause is false. That is the fourth occurrence of the shape this rig keeps producing,
      and the one `design.md` §4 cited when it refused to collapse `mismatch` into `missing`.

      Verify, three parts:
      1. A `derive.py --self-test` case builds a synthetic fixture root, digests it, mutates one
         answer-key file's **bytes**, re-digests, and asserts the two differ — the same shape task 7.10
         already committed for `compute_manifest` and `hash_paths` in `run-pipeline.sh --self-test`.
         Mutation-prove it: `return "constant"` in `answer_key_set_digest()` must now turn the suite red.
      2. A `run-pipeline.sh --self-test` case covers `answer_key_paths()` — that it selects exactly
         `answer-key/` relpaths from one root, excludes every other manifest subdirectory, and is sorted.
      3. **The pin**: one synthetic fixture root, digested by both sides, asserted equal. It may live on
         either side, but it must actually execute both implementations rather than compare each to a
         hardcoded string. Per design's own wording, a later failure of this pin is a finding to report,
         never something to "fix" on whichever side looks wrong.
      Done: `_self_test_answer_key_set_digest()` added to `rig/derive.py`, registered in
      `run_self_test()`'s roster. Case (a) builds a synthetic root, digests it via
      `answer_key_set_digest()`, mutates one file's bytes, re-digests, asserts the two differ —
      mutation-proven: `return "constant"` in `answer_key_set_digest()` turns exactly this case red
      (confirmed in a scratch copy under `rig/`, never the committed file; real file `sha256`-verified
      unchanged afterward). Case (b) is the committed pin: it `sed`-extracts `compute_manifest`,
      `answer_key_paths`, `hash_paths` verbatim from `rig/run-pipeline.sh` (the same convention
      `rig/check.sh`'s `load_compute_manifest()` already uses — never re-implemented), `eval`s them in a
      `bash -c` subprocess, and asserts the bash pipeline's digest equals Python's
      `answer_key_set_digest()` over one synthetic fixture root — genuinely executing both
      implementations, never comparing either to a hardcoded string. A parallel case,
      `answer_key_paths`'s own `rig/run-pipeline.sh --self-test` addition (part 2), asserts it selects
      exactly `answer-key/` relpaths, sorted, excluding every other manifest subdirectory —
      mutation-proven by changing its filter to `^tools/` in a scratch copy, which turns that case red
      with `git status`/`sha256sum` confirming the real file untouched before and after. Part 3's pin
      passes on the real, unmutated files (`571e083d27aaef0a63cee3b26de97b14ac8eccdab02dfbe3535aba83728cb7b6`
      for the synthetic root, matching task 1.3's hand-verified constant's own convention).

- [x] 2.1 Add `preimage_digest()` to `rig/run-pipeline.sh`, reproducing `load_surface()` +
      `surface_digest()`'s exact convention (`rig/derive.py:89-99`): dedupe + sort, `# harness:` header
      and blank lines excluded, `sha256` of the joined, sorted, newline-set. This is the **one
      genuinely new algorithm** this whole change introduces (design §1) and the **second
      cross-language digest agreement**, alongside the answer-key set digest from Sibling 1 — pinned by
      a shared literal constant asserted in both `derive.py --self-test` and
      `rig/run-pipeline.sh --self-test`, the same mechanism already used for `surface_digest` at
      `:424-430`. Whoever hits a pin-mismatch failure must not "fix" the failing side to match — the
      disagreement is the finding.
      Verify: `bash -n rig/run-pipeline.sh`.
      Done: `preimage_digest()` added beside `hash_paths()`. `bash -n` clean. The pinned constant
      (`4a626b46a7841184c5d423277a9c17cb15129f4ba32f92a88948b77735bfdcd3`, over the deduped/sorted set
      `["Bash","Read","Write"]`) is asserted independently in both `rig/run-pipeline.sh --self-test`
      (task 2.3's case a) and a new `_self_test_preimage_digest_pin()` in `rig/derive.py`, which asserts
      `surface_digest(["Bash","Read","Write","Read"])` equals the same constant — the shared-literal
      mechanism this task's own text specifies, distinct from task 2.0's stronger both-implementations
      pin (which that task's own text requires precisely because Face A's pair had never had ANY
      committed pin at all; Face C's pair gets one from its first commit).

- [x] 2.2 Record `recorded_surface_preimage_sha256` at the existing per-step preimage existence check
      (`:857-860`) into `write_step_status`'s own dict (`:790-820`), the same site `surface_sha256`
      (`:810`) is already written from. This is the **one digest that is not arm-level** — a three-step
      arm has three invocations and the preimage file can change between them, so it belongs on each
      step's own `status.json`, never on `arm.json`.
      Verify: `bash -n rig/run-pipeline.sh`.
      Done: computed via `preimage_digest "$SURFACE_FILE"` right after `run_model_step`'s existing
      existence check (never before it — the abort path is unchanged and untouched by this field);
      threaded as a new 13th positional argument through `write_step_status`, written into each model
      step's `status.json` as `recorded_surface_preimage_sha256`. `run_code_step`'s own call site passes
      an empty 13th argument (code steps carry no surface, same convention as the existing 7th
      argument). `bash -n` clean.

- [x] 2.3 Add self-test cases a–c to `rig/run-pipeline.sh --self-test` (`self_test()`, `:353`), using
      the existing `expect`/`expect_ne`/`expect_contains` harness:
      - **a.** dedupe + sort, header/blank lines excluded, against a **pinned constant** (the same
        constant asserted on the `derive.py` side per task 2.1).
      - **b.** a preimage with no tool lines yields an **absent** digest, not an empty string read as a
        value — the same empty-field shape `read_back_init`'s own cases already establish (`:432-443`).
      - **c.** a missing preimage file still reaches `missing-surface-preimage` (`:857-860`); provenance
        never masks that abort.
      Verify: `rig/run-pipeline.sh --self-test` — cases a, b, c print `PASS`. Known gap, not fixed here:
      `rig/check.sh`'s `check_component_self_test()` (`rig/check.sh:160-171`) has no bash arm, so this
      flag is never composed by the repo gate (Decision 3) — run it by hand.
      Done, with one deliberate deviation from this task's literal wording, recorded rather than
      silently made: case (c) cannot invoke `run_model_step` directly — that function is defined at
      `:932`, textually AFTER `self_test()`'s own dispatch site at `:650`, so in this script's
      top-to-bottom execution order it is not yet a defined command when `--self-test` runs (confirmed
      live: calling it produced `run_model_step: command not found`, not a real behavioural failure).
      Case (c) instead asserts `preimage_digest()` itself yields an absent digest (never a crash) on a
      missing file, checked directly; `run_model_step`'s own existence check (`:956-959`, unchanged by
      this batch) is what actually produces `missing-surface-preimage`, and it runs strictly before
      `preimage_digest` is ever reached in the real pipeline. Cases (a)/(b) implemented exactly as
      specified, pinned against the same constant as task 2.1's `derive.py`-side assertion.
      Mutation-proven: reverting `preimage_digest()`'s body to `printf '%s' "constant-mutant"` in a
      scratch copy (`rig/.mutant-run-pipeline.sh`, deleted immediately after) turns all three cases red;
      the real file's `sha256` is unchanged before and after.

- [x] 2.4 **R-P6.3 — the frozen comparand's own drift, distinct from a genuine surface mismatch.**
      Extend task 1.5's provenance gate (still ahead of the per-step read-back loop) with a per-model-step
      check: is `input_provenance_version` present and `recorded_surface_preimage_sha256` `null`? — same
      outcome as the existing null-check (`void_reason="input-provenance-missing"`,
      `"provenance-capture-incomplete"`), reached before the per-step loop so the loop is never entered
      with a missing comparand (design §6). Otherwise, compare `recorded_surface_preimage_sha256`
      against a freshly-recomputed `surface_digest(load_surface(FAILURE_FLOOD_SURFACE_ARM))` (the LIVE
      preimage file, at derive time): if they disagree, add `"surface-preimage-drift"` to task 1.5's
      shared `drifted` set. This is a **different** question from task 2.5's comparison below — it asks
      "did the thing that was frozen at run time still match the fixture later," never "did the model's
      observed tool surface match what was frozen." The two MUST NOT share a reason (R-P6.3's own text).
      Verify: `python3 -m py_compile rig/derive.py`.
      Done: `ff_surface_digest` (the live recompute) is now computed BEFORE the provenance gate, so
      the gate can use it too. The null check (task 1.5's pass 2) is extended to also cover any model
      step's `recorded_surface_preimage_sha256` being absent, reaching `provenance-capture-incomplete`
      exactly as the answer-key null case does. The drift check (pass 3) gained a per-model-step loop:
      any step whose `recorded_surface_preimage_sha256` disagrees with `ff_surface_digest` adds
      `"surface-preimage-drift"` to the shared `drifted` set. `py_compile` clean. Mutation-proven:
      disabling this loop's own comparison in a scratch copy of `rig/derive.py` turns exactly the R-P6.3
      firing case (task 2.6's case) red, every other case stays green, and the real file is
      `sha256`-unchanged afterward.

- [x] 2.5 In `build_row_failure_flood`, **delete** the `is not None` guard at `:855`
      (`if ff_surface_digest is not None and step_surface != ff_surface_digest`) — deleted, not
      weakened (R-P6.2). Replace with an unconditional comparison of `step_surface` (the run's own
      observed value) against the new per-step `recorded_surface_preimage_sha256` (the frozen
      comparand, not the live recompute task 2.4 uses): any disagreement still voids
      `void_reason="surface-mismatch"` — the existing reason, entirely unchanged; R-P6 introduces no new
      reason for **this** comparison.
      Verify: `python3 -m py_compile rig/derive.py`.
      Done: the guard deleted, not weakened, exactly as required; the loop now compares `step_surface`
      unconditionally against `step.get("recorded_surface_preimage_sha256")`. `py_compile` clean.
      Mutation-proven that the check can FIRE at all: replacing the `if` with `if False:` in a scratch
      copy turns exactly task 2.6's fire-proof case red — no committed case previously proved
      `build_row_failure_flood`'s own `surface-mismatch` void could fire (only `build_row`'s, a
      different function, had one), so that case was added this batch specifically to close that gap.
      **A finding recorded rather than hidden**: because task 2.4's gate now runs first and its own
      drift check already requires `recorded_surface_preimage_sha256 == ff_surface_digest` for a row to
      reach this loop at all (`state == "complete"`), reverting THIS line's comparand from `recorded_
      surface_preimage_sha256` back to `ff_surface_digest` (the pre-task-2.5 target) produces **zero**
      row-outcome difference on the full suite — every model step that reaches this loop already has
      `recorded == live` by construction of the gate it just passed. This is not a defect: R-P6.1/R-P6.2
      are about the read-back check's own contract (never silently skip on an unavailable comparand,
      never compare against the live recompute), independently of whether a separate, additional gate
      happens to make the distinction unobservable in this exact codebase. The requirement is satisfied
      to the letter; the mutation-proof above (the `if False:` case) proves the detector still fires,
      which is what ADR 0013 actually asks for.

- [x] 2.6 Add the R-P6.3 firing proof to `derive.py --self-test`: a synthetic run with
      `input_provenance_version` present, `recorded_surface_preimage_sha256` set to a value that
      deliberately disagrees with `surface_digest(load_surface(FAILURE_FLOOD_SURFACE_ARM))` over the
      real committed `rig/surfaces/failure-flood.txt`, and `step_surface` (the observed value) set to
      match the recorded comparand (so task 2.5's own check would pass cleanly). Assert
      `void_reason == "input-provenance-mismatch"`, `"surface-preimage-drift"` in `anomaly_classes`,
      and **never** `"surface-mismatch"` — proving the two checks are independently triggerable and
      never conflated.
      Verify: `rig/derive.py --self-test` — the new case prints `PASS`.
      Done: case (c) of the new `_self_test_build_row_surface_preimage_provenance()` implemented exactly
      as specified (`recorded_surface_preimage_sha256` and observed `surface_sha256` both overridden to
      the same wrong value, so they agree with each other but disagree with the live recompute).
      Asserts `void_reason == "input-provenance-mismatch"`, `"surface-preimage-drift"` present,
      `"surface-mismatch"` absent. PASS.

- [x] 2.7 Add the ordering proof to `derive.py --self-test`: a synthetic run whose
      `recorded_surface_preimage_sha256` is deliberately `null` (provenance incomplete) **and** whose
      observed `step_surface` would, if compared, genuinely disagree with the live preimage. Assert the
      row voids via `void_reason="input-provenance-missing"` and **never** reaches or stamps
      `"surface-mismatch"` — without this case, the "correct refusal, false stated cause" regression
      (design §4, §6) is undetectable.
      Verify: `rig/derive.py --self-test` — the new case prints `PASS`.
      Done: case (d) implemented exactly as specified (`recorded_surface_preimage_sha256` null,
      observed `surface_sha256` deliberately wrong). Asserts `void_reason ==
      "input-provenance-missing"`, `"provenance-capture-incomplete"` present, and `void_reason !=
      "surface-mismatch"`. PASS. Mutation-proven: forcing `missing_surface_preimage = False`
      unconditionally in a scratch copy of `rig/derive.py` (defeating task 2.4's own null check) turns
      exactly this case red — every other case, including cases a-c of the same function, stays green.

- [x] 2.8 Re-derive `rig/results/failure-flood-v1/runs.jsonl` from existing raw captures. Confirm the
      three rows are unaffected beyond `recorded_surface_preimage_sha256` appearing as `null` on their
      steps, and `state`/`void_reason`/`anomaly_classes` unchanged from Sibling 1's re-derive.
      Verify: `python3 rig/derive.py --experiment failure-flood-v1`; diff against Sibling 1's re-derive
      output — the only permitted delta is the new per-step field, `null` on all three rows.
      Done: re-derived. All three rows: `state=void, void_reason=shakedown` (unchanged),
      `anomaly_classes == ["pre-scheme-provenance"]` exactly (unchanged), `schema_version == 4`
      (unchanged). Every step across all three rows: `recorded_surface_preimage_sha256` is `null`
      — the only new delta versus Sibling 1's own re-derive, confirmed by a field-by-field diff excluding
      that one new key. `tool-surface-v1` also re-derived (task 4.1's own check, run early for the same
      unavoidable-`checker_digest` reason Sibling 1's task 1.11 noted): 42 rows, byte-identical excluding
      only `checker_digest`, `schema_version` unchanged at 3. Idempotence confirmed for both experiments
      (derived twice, byte-identical both times).

---

## Sibling 3 — Face B + the R-F5.3 claim boundary (closes R-P7)

Depends on: Sibling 2.

- [ ] 3.1 In `rig/run-pipeline.sh`, after the MANIFEST gate (same site as task 1.3), compute
      `recorded_fixture_digest = sha256(MANIFEST.sha256's bytes)` using the one-liner idiom already at
      `:677` (the `LOCKFILE_SHA256` computation). Thread it into the `arm.json` writer the same way as
      `recorded_answer_key_digest` (task 1.4).
      Verify: `bash -n rig/run-pipeline.sh`.

- [ ] 3.2 **R-P7.1a.** Add a fixture-digest check to task 1.5's shared drift-accumulation pass — joining
      it, not inserted at a particular point relative to task 1.5's answer-key check (R-P2.2a forbids
      that framing entirely). Extend the null-check (task 1.5's pass 2 / task 2.4's per-step extension)
      to also cover `recorded_fixture_digest`. In pass 3, compare `recorded_fixture_digest` against a
      freshly-recomputed `fixture_digest_at(root)`; on disagreement, add `"fixture-drift"` to the same
      `drifted` set the answer-key check (task 1.5) and the surface-preimage check (task 2.4) already
      write into. The eventual `void_reason="input-provenance-mismatch"` fires once, after all three
      checks have run, carrying every face that actually disagreed.
      Verify: `python3 -m py_compile rig/derive.py`.

- [ ] 3.3 **Replaces the withdrawn R-P2.2 precedence task** (R-P2.2a: a precedence rule is only needed
      when the `void_reason` slot must choose between two true findings, and this design never asks it
      to choose). Add the both-drifts-recorded self-test case: construct a run recorded against fixture
      root `v2` whose `answer-key/prereg.json` disagrees on **both** the fixture digest and the
      answer-key digest at once (`answer-key/` sits inside `compute_manifest`'s walked set — spec.md
      Decision 2, R-P2.2). Assert the row voids with `void_reason == "input-provenance-mismatch"` and
      `anomaly_classes` contains **both** `"answer-key-drift"` and `"fixture-drift"` — never only one.
      Run the case with the two checks' relative code order swapped (a throwaway local edit, reverted
      immediately after) and confirm the assertion is unchanged either way — proving R-P2.2a's "order
      MUST NOT be observable" as a fact about the accumulation, not a claim about one particular
      ordering that happened to be tested.
      Verify: `rig/derive.py --self-test` — the new case prints `PASS`, in both check orderings.

- [ ] 3.4 Finalize the full negative control (design §9 case 1, first achievable once all three
      digests exist): a synthetic run with `input_provenance_version` present and all three digests
      (answer-key, fixture, surface-preimage) present and agreeing → `state == "complete"`. A gate that
      always voids would pass every other case in this file too — this is the case that catches that.
      Verify: `rig/derive.py --self-test` — the case prints `PASS`.

- [ ] 3.5 Add the R-F5.3 claim-boundary statement (R-P7.2) to this file's own apply-progress note (or
      wherever this cycle's closing report lives): any reference to the archived `R-F5.3` re-derive
      check MUST state it verifies **deriver** drift only, never **fixture** drift, because a re-derive
      re-reads the same live manifest and necessarily agrees with itself.
      Verify: structural readback — the sentence is present and unambiguous.

- [ ] 3.6 Correct `rig/README.md:55` — `failure-flood-v1`'s `schema_version` is stated as **1**; it has
      been **3** since the CRITICAL-1/-2 bump and this cycle takes it to **4**. Correct the number and
      add the four new fields (`input_provenance_version`, `recorded_answer_key_digest`,
      `recorded_fixture_digest`, `recorded_surface_preimage_sha256`) to the row-shape description in the
      same edit — a named correction, not a silent overwrite (Decision 3 lists the sibling gap this
      does **not** also fix: `rig/check.sh` composing `run-pipeline.sh --self-test`).
      Verify: structural readback of `rig/README.md`; `./check.sh` (frontmatter/structure, root).

- [ ] 3.7 Re-derive `rig/results/failure-flood-v1/runs.jsonl` one final time from existing raw
      captures. Confirm all three rows: `state=void, void_reason=shakedown` (unchanged),
      `anomaly_classes == ["pre-scheme-provenance"]` exactly, `schema_version == 4`,
      `recorded_answer_key_digest`/`recorded_fixture_digest` both `null`, every step's
      `recorded_surface_preimage_sha256` `null`.
      Verify: `python3 rig/derive.py --experiment failure-flood-v1`; inspect the three rows by hand.

---

## Cross-cutting verification (spans all three siblings, run once at the end)

- [ ] 4.1 **`tool-surface-v1` non-regression — the 42-row projection (R-P11.2).** Re-derive
      `rig/results/tool-surface-v1/runs.jsonl` from existing raw captures. Project out only
      `checker_digest` (it changes on any `derive.py` edit, per its own `sha256`-of-file-bytes
      definition at `:82`, stamped on both experiments' rows at `:530`/`:1017` — R-P11.2's named,
      unavoidable exclusion). Every remaining byte across all 42 rows MUST be identical to the
      pre-change values; `schema_version` MUST stay `3`. `build_row` (`:410`) and its registry entry
      (`:1079-1089`) MUST be byte-unchanged in the diff — the mechanical guarantee design §7 states.
      Verify: `python3 rig/derive.py --experiment tool-surface-v1`; diff 42 rows against pre-change,
      excluding only `checker_digest`; zero mismatches.

- [ ] 4.2 **`failure-flood-v1`'s own projection (R-P11.2), distinct from 4.1's.** Re-derive; project out
      `schema_version`, `checker_digest`, `anomaly_classes`, and the four fields this change adds. Every
      remaining byte across all 3 rows MUST be identical to the pre-change values, and each row MUST
      still read `state=void, void_reason=shakedown`. Any other delta is a defect, not an expected diff
      (R-P1.1).
      Verify: diff 3 rows against pre-change under this named projection; zero mismatches.

- [ ] 4.3 **Deriver idempotence.** Run `derive.py` twice in a row over the same raw captures for both
      experiments. `runs.jsonl` MUST be byte-identical between the two runs.
      Verify: `python3 rig/derive.py --experiment tool-surface-v1 && cp ... && python3 rig/derive.py --experiment tool-surface-v1 && diff`;
      same for `failure-flood-v1`.

- [ ] 4.4 **Refusal-to-derive stays untouched (R-P12).** Deliberately break one detector (e.g. corrupt a
      `checker_self_test` case in a scratch copy of a `tool-surface-v1` answer key, never the committed
      fixture) and confirm `derive.py` (no `--experiment` flag needed — `run_self_tests()` runs
      unconditionally in `main()`) still exits 1 at `:1468-1470` with **no rows written at all**,
      regardless of any run's own answer-key digest state. Revert the scratch copy immediately.
      Verify: exit code 1; `runs.jsonl` untouched; `git status` on the real fixture tree empty
      throughout.

- [ ] 4.5 **`rig/check.sh` — 20 checks, ~4s — before committing anything under `rig/`.** Run it after
      every sibling lands, not only once at the end.
      Verify: `./rig/check.sh` exits 0. Known, named gap **not fixed by this cycle** (Decision 3,
      proposal's Non-Goals): `check_component_self_test()` (`rig/check.sh:160-171`) composes only
      `derive.py`/`report.py`/`collect.py`'s `--self-test` flags — `rig/run-pipeline.sh --self-test`
      (tasks 2.3, 2.1) has no bash arm in the gate and must be run by hand every time.

- [ ] 4.6 **Root gates before any commit.** `./check.sh` (frontmatter/six-key schema, this file
      included) and `./hooks/pre-commit` (ADR 0009 redaction — **this is a public repo**; every
      committed byte, including the re-derived `runs.jsonl`, is scanned).
      Verify: both exit 0.

- [ ] 4.7 **`MAP.md`'s `sdd/` row still says "2 cycles" and does not name this one.** Added during
      gatekeeping — neither this phase nor the spec caught it. `MAP.md:52` describes `sdd/` as
      *"2 cycles"* and lists `measurement-rig` and `archive/2026-08-18-failure-flood-triage`. This cycle
      makes it three. `MAP.md` is the one hand-maintained index in this repo — it names itself the single
      exception to the generated-or-absent rule, which `decisions/0016` restates — so nothing updates it
      automatically and a stale row here is exactly the failure `AGENTS.md` warns about.
      When updating the row, carry this cycle's boundary verbatim rather than paraphrasing it: an
      instrument for a **failed** ratio target, never a comparative result, **zero countable runs** — the
      same wording the `failure-flood-triage` entry beside it already uses.
      Verify: `MAP.md`'s `sdd/` row names `run-input-provenance`, its count equals the number of
      directories under `sdd/` excluding `archive/` plus the archived entries it lists, and `./check.sh`
      stays clean.
      Note, deliberately NOT a task: `open-work.sh`'s `section_sdd()` (landed on `main` in `25a8756`)
      already enumerates `sdd/*/` outside `sdd/archive/`, and was confirmed during gatekeeping to list
      `run-input-provenance` with no action needed. The generated index and the hand-written one have
      different obligations; only the hand-written one needs this task.

---

## Review Workload Forecast

| Sibling | File | Est. authored lines | Notes |
|---|---|---:|---|
| 1 (Face A + WARNING-14) | `rig/run-pipeline.sh` | ~45 | digest recording, `input_provenance_version`, self-test pin case |
| 1 | `rig/derive.py` | ~215 | new digest function, drift-accumulation gate, `.get()` fixes, schema bump, 8-case self-test + inverted case 3 |
| **1 subtotal** | | **~260** | |
| 2 (Face C) | `rig/run-pipeline.sh` | ~70 | `preimage_digest()`, per-step wiring, self-test cases a–c |
| 2 | `rig/derive.py` | ~80 | `:855` guard deleted, R-P6.3 drift-into-accumulation check (new since gatekeeping), its firing self-test case, ordering-proof self-test case |
| **2 subtotal** | | **~150** | up from the prior draft's ~125 — R-P6.3 (task 2.4) and its firing proof (task 2.6) are new work items this correction added |
| 3 (Face B) | `rig/run-pipeline.sh` | ~20 | one-liner fixture digest, `arm.json` wiring |
| 3 | `rig/derive.py` | ~75 | fixture-drift joining the shared accumulation, both-drifts-recorded self-test (run under both check orderings), negative control |
| 3 | `rig/README.md` | ~10 | `schema_version` correction, row-shape fields |
| **3 subtotal** | | **~105** | up from ~95 — the both-drifts self-test (task 3.3) replaced a simpler precedence case with a slightly larger one |
| **Total** | | **~515** | 260 + 150 + 105 = 515 |

`rig/results/failure-flood-v1/runs.jsonl` and `rig/results/tool-surface-v1/runs.jsonl` are re-derived
(generated), excluded from the authored count per the work-unit-commits convention, but included in
full-snapshot identity and redaction-gate scanning (task 4.6).

- **800-line budget (`review_budget_lines`): NOT at risk.** ~515 total (up from the prior draft's ~480
  — the R-P6.3 addition moved Sibling 2's subtotal, the both-drifts self-test moved Sibling 3's by a
  smaller amount), ~285 lines of headroom.
- **Per-sibling size also stays under the chained-pr skill's own 400-line single-PR trigger**
  (260 / 150 / 105), so line count alone does not force chaining.
- **Chained PRs recommended: Yes — but for an ordering reason, not a size reason.** R-P9.2 makes the
  Sibling 1 → 2 → 3 sequence itself a requirement (a delivery reaching Sibling 3 first and stopping
  reproduces the exact failure this cycle exists to correct). Three reviewable units, landed in strict
  order, make that sequence auditable in the git log the way three commits inside one PR would not
  (a single PR can still be merged as one unit regardless of internal commit order, and a reviewer
  cannot block "PR opens the Face A commit for review before Face C's exists" the way they can block a
  second PR from opening before the first merges).
- **Decision needed before apply: chain strategy.** This phase recommends chaining but does not select
  stacked-vs-tracker; that is `chain_strategy`, collected by the orchestrator per this session's
  preflight note. Either a 3-commit single PR (if the orchestrator judges strict commit ordering
  sufficient enforcement) or 3 stacked PRs (matching the archived cycle's own PR1→PR7E precedent) are
  defensible; a decision is needed, not a default.
- **The spec/design void_reason conflict is resolved, not a pending decision.** The prior draft of this
  file named it as a second blocking decision before Sibling 1 could be applied; it was resolved
  upstream in `spec.md`/`design.md` (commit `43f5281`) before this correction round, and every task in
  this file now implements the settled vocabulary directly (see "Spec/design conflict — resolved" at
  the top). No reconciliation step remains between this file and apply.
