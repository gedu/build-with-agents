---
id: sdd/run-input-provenance/verify-report
type: journal
targets: [any]
status: draft
verified: 2026-08-27
sources: ["sdd/run-input-provenance/spec.md", "sdd/run-input-provenance/tasks.md", "sdd/run-input-provenance/apply-progress.md", "sdd/run-input-provenance/design.md"]
---

<!-- The admitted bytes are this file WITHOUT the frontmatter block above.
     gentle-ai sdd-verify-validate rejects YAML frontmatter and requires the
     fenced yaml envelope as the first non-empty content; this repo's check.sh
     requires every content .md to open with `---`. The two are satisfied the
     way the previous cycle satisfied them (see
     sdd/archive/2026-08-18-failure-flood-triage/verify-report.md): validate the
     envelope-only bytes, commit with frontmatter prepended. Admitted bytes
     sha256: d166b725cd00ec252d4c42479fbb8c05927679fb2614729f4c73e1f406aa69d2
     admitted as valid: true / verdict: fail, evidence_revision
     sha256:4bdab3396026050e3d43f7bec1545e27806c66995c550bd58fdcf3193eca10f6

     One redaction was applied to the phase's own admitted bytes before commit,
     and it is recorded rather than silent: the WARNING-5 prose quoted the
     checkout-isolation hook preflight's literal output, which contains an
     absolute home path. This repo is public (ADR 0009) and ./hooks/pre-commit
     correctly refused the file. The path is now `<repo>/hooks/pre-commit` and
     the report was re-admitted, which is why the admitted-bytes sha256 above is
     d166b725... and not the phase's original ea0c33c8... The declared
     evidence_revision is a report field, not a hash of the file, so it is
     unchanged. The gate wins over byte-preservation: a public repo cannot carry
     a home path, and the apply phase correctly stopped rather than either
     editing this file on its own or bypassing the hook. -->

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:4bdab3396026050e3d43f7bec1545e27806c66995c550bd58fdcf3193eca10f6
verdict: fail
blockers: 1
critical_findings: 1
requirements: 12/12
scenarios: 19/21
test_command: python3 rig/derive.py --self-test
test_exit_code: 0
test_output_hash: sha256:7743851881f745e7de27a3c3ebb22e7377f8d9228c83ccf18e96bf66820b4206
build_command: ./rig/check.sh
build_exit_code: 0
build_output_hash: sha256:fe778a1340c0ccf99e2484eae8612dfec32d40292a82a3ec7c2a3f4b8f1fc28e
```

# Verification Report — run-input-provenance

Change: `run-input-provenance`. Branch `sdd/failure-flood-triage-planning`, HEAD `2873e04`,
tree `44976be`. Artifact store: hybrid. Mode: full spec verification (proposal, spec, design,
tasks, apply-progress all present).

Read-only on code. Every mutation proof below ran in a throwaway copy of the working tree under
the session scratchpad; the real checkout was `git status` clean before and after and remains at
`2873e04`.

## Verdict

**FAIL — 1 CRITICAL, 5 WARNING, 5 SUGGESTION.**

The cycle's twelve requirements are all satisfied as written, all 35 tasks are genuinely `[x]`, and
every number the orchestrator supplied reproduced independently. The single blocker is not a
requirement violation: it is the **fourth instance of the both-sides-move-together fault**, in Face
C, found by the same method that found the first three. Faces A and B each had this fault registered
as a new task (2.0, 3.8) and closed before their sibling was accepted. Face C's is still open.
Archiving now would record that the class was closed when one of the three faces' comparand
producers is proven zero ways.

## Independent re-verification of the supplied numbers

Every figure below was re-run in this phase, not accepted from the apply reports or the launch
prompt.

| Claim | Result |
|---|---|
| `python3 rig/derive.py --self-test` | **59/59 PASS**, exit 0 — CONFIRMED |
| `bash rig/run-pipeline.sh --self-test` | **28/28 PASS**, exit 0 — CONFIRMED |
| `./rig/check.sh` | **20/20**, exit 0 — CONFIRMED |
| `./check.sh` | clean, `111 content files and 5 skill(s)` — CONFIRMED |
| `./hooks/pre-commit` | exit 0 — CONFIRMED |
| `failure-flood-v1` three rows | `void` / `shakedown` / `["pre-scheme-provenance"]`, `schema_version` 4 — CONFIRMED |
| `failure-flood-v1` provenance fields all `null` | **REFUTED in one detail** — three row-level fields are present-and-`null`; the fourth (`steps[].recorded_surface_preimage_sha256`) is **absent**, not null. See WARNING-1 |
| `tool-surface-v1` 42 rows, `schema_version` 3, only `checker_digest` differs vs `a2cbd6f` | CONFIRMED — per-key diff over all 42 rows yields exactly `{checker_digest: 42}` |
| `build_row` + registry entry byte-unchanged | CONFIRMED |
| Authored lines 385 + 341 + 323 = 1049 vs 800 budget | CONFIRMED exactly (sibling 3 = 323 excluding `MAP.md`'s 2 lines; 1051 with them) |
| Task count | **CORRECTED** — the artifact carries **35** tasks (1.1–1.11, 2.0–2.8, 3.1–3.8, 4.1–4.7), not 30. All 35 `[x]`, zero unchecked |

Commands and hashes for the strict envelope are in the frontmatter. `bash rig/run-pipeline.sh
--self-test` exit 0, output hash
`sha256:b58aa49a7ff6e8de756125833161d9345054113d6448944ed99c09dc1c1c0112`.

## Requirement compliance — all twelve

| Req | Status | Proof (file:line) |
|---|---|---|
| **R-P2.1** Face A recorded at run time, one root, runner never resolves `task_id` | **Satisfied** | `rig/run-pipeline.sh:748` (`RECORDED_ANSWER_KEY_DIGEST="$(answer_key_paths "$FIXTURE_ROOT" \| hash_paths "$FIXTURE_ROOT")"`); `answer_key_paths()` at `:200-202` filters `compute_manifest`'s output by `^answer-key/` prefix — no `task_id` logic anywhere in the runner. Read back at `rig/derive.py:931`, `:1189` |
| **R-P2.2** one edit records BOTH drifts, no precedence | **Satisfied** | `rig/derive.py:954-981` — one `drifted` set accumulated across all faces, single decision at `:979-981`. Case 58 asserts both classes present |
| **R-P2.2a** withdrawn precedence MUST NOT return; order not observable | **Satisfied** | Verified by reading `rig/derive.py:954-981`: no per-face `void_reason`, no early `break`/`return`, no ordering predicate. `rg 'precedence'` over `rig/` returns nothing. Order-independence is structural, not conventional |
| **R-P3.1** drifted answer key voids, before scoring | **Satisfied** | Detector `rig/derive.py:955-957`; gate closes at `:981`, all scoring is downstream at `:1116-1155` (`verdict`, `integrity_guard_pass`, `causes_claimed`, `causes_correct`) — ordering holds. Case 44 |
| **R-P3.2** downgrade-only | **Satisfied** | Nested inside `elif state == "complete":` at `rig/derive.py:922`. Case 49 (already-void row keeps `no-preregistration`) |
| **R-P4.1** no direct subscripts; malformed key voids, never raises | **Satisfied** | `rig/derive.py:967-969` (`ak.get("F0") or {}`, `"R0" not in ak`), `:1139` (`ak.get("F0", {}).get("failures", [])`), `:1153` (`ak.get("R0", [])`), `:1238` (`len(ak["R0"]) if ak and "R0" in ak else None`). Case 48 |
| **R-P5.1** positive marker recorded | **Satisfied** | Written `rig/run-pipeline.sh:1210` (`"input_provenance_version": 1`); read `rig/derive.py:917`, projected `:1188` |
| **R-P5.2** pre-scheme voids, annotation independent of transition | **Satisfied** | `rig/derive.py:918-921` — `anomaly_classes.add` is outside the `state == "complete"` guard, the transition inside it. Cases 46, 50 |
| **R-P5.3** null digest → `provenance-capture-incomplete`, distinguishable | **Satisfied** | `rig/derive.py:931-943`, covering all three faces including the per-step surface term at `:937-940`. Cases 47, 57 |
| **R-P5.4** not-`True` is not-proven, both sites | **Satisfied** | `rig/derive.py:1005` and `:1034`. Cases 30, 31 |
| **R-P5.5** pre-scheme caught once, not twice | **Satisfied** | The `if/elif` at `rig/derive.py:918`/`:922` is mutually exclusive by construction. Case 29 |
| **R-P6.1** comparand frozen per run | **Satisfied** | `rig/derive.py:1001` compares `step["surface_sha256"]` against `step["recorded_surface_preimage_sha256"]`; recorded at `rig/run-pipeline.sh:971` via `preimage_digest "$SURFACE_FILE"`, threaded at `:915` |
| **R-P6.2** the `is not None` guard MUST NOT persist unchanged | **Satisfied** | Guard deleted; `rig/derive.py:993-1000` records why, and the missing-comparand case is now handled by the null gate at `:937-943` instead of silently skipping. Case 54 is the ordering proof |
| **R-P6.3** frozen-vs-live drift gets its own reason, never `surface-mismatch` | **Satisfied in letter, undermined in substance** | Detector `rig/derive.py:974-978`; case 53 asserts `surface-preimage-drift` and NOT `surface-mismatch`. But the live comparand's producer is unproven — see CRITICAL-1 |
| **R-P7.1** fixture digest recorded at run time | **Satisfied** | `rig/run-pipeline.sh:738` (`RECORDED_FIXTURE_DIGEST`), taken over bytes the recompute-compare gate at `:718-724` has already proven match the live tree. Read back `rig/derive.py:936`, `:1190` |
| **R-P7.1a** disagreement → `input-provenance-mismatch` + `fixture-drift` | **Satisfied** | `rig/derive.py:958-960`. Case 56 asserts `fixture-drift` present and `answer-key-drift` absent |
| **R-P7.2** R-F5.3 claim boundary stated unambiguously | **Satisfied** | `sdd/run-input-provenance/apply-progress.md:472-482` — "verifies deriver drift only, never fixture drift", with the mechanism spelled out. Independently restated at `MAP.md:52`. `rig/README.md`'s correction never cites R-F5.3, so its conditional obligation is not triggered there. `hypotheses/0002:36` cites R-F5.3 but about occupancy monotonicity, and was untouched by this cycle |
| **R-P8.1 / R-P8.2** three rows marked, never promoted | **Satisfied** | Verified against the committed file: 3 rows, `schema_version` 4, `state=void`, `void_reason=shakedown`, `anomaly_classes == ["pre-scheme-provenance"]` exactly. Zero `complete` rows |
| **R-P9.1** 7.15 retired, replaced by three siblings | **Satisfied** | `sdd/run-input-provenance/tasks.md:80` records the retirement and the mapping |
| **R-P9.2** the A → C → B order is itself the contract | **Satisfied** | Verified in `git log`, oldest first: `0637d68` (Face A) → `5cfa456` (Face C) → `2873e04` (Face B). Confirmed by first appearance of each detector's own class string in the diffs: `answer-key-drift` first in `0637d68`, `surface-preimage-drift` first in `5cfa456`, `fixture-drift` first in `2873e04`. No face's detector landed early |
| **R-P10.1** every new/changed detector proven able to fire | **Satisfied** | Cases 44 (R-P3), 48 (R-P4), 29/30/31 (R-P5), 53 (R-P6), 56 (R-P7.1a) all PASS at runtime |
| **R-P10.2** case 3 rewritten not deleted, plus a new case | **Satisfied** | `rig/derive.py:1594-1604` (rewritten case 3, asserts `input-provenance-missing`) and `:1603-1607` (new case 4, asserts `model-mismatch`). A third, unrequired case 5 covers `permission_mode_matches_declared`. Cases 29, 30, 31 |
| **R-P11.1** additive bump, no migrations | **Satisfied with one shortfall** | `FAILURE_FLOOD_SCHEMA_VERSION = 4` at `rig/derive.py:651`; nothing reads the old value. But "rewrites every existing row with ... the new fields" does not hold for Face C's per-step field — WARNING-1 |
| **R-P11.2** two per-experiment projections | **Satisfied** | Re-derived and diffed per key against `a2cbd6f`. `tool-surface-v1`: 42 rows, differing keys exactly `{checker_digest: 42}`, `schema_version` 3 both sides. `failure-flood-v1`: 3 rows, differing keys exactly `{checker_digest, schema_version, anomaly_classes}` — zero disallowed deltas |
| **R-P12.1** refusal stays all-or-nothing | **Satisfied, with a claim boundary** | Block intact at `rig/derive.py:2211-2213`. Proven live: corrupting `checker_self_test.negative_control` in `rig/fixtures/tool-surface/v1/answer-key/t1.json` makes `--experiment tool-surface-v1` exit 1 with the refusal message and both `runs.jsonl` byte-unchanged. But it is **vacuous for `failure-flood-v1`** — WARNING-2 |
| **R-P12.2** one row's mismatch does not refuse everything | **Satisfied** | `build_row_failure_flood` has no refusal path; cases 44/48 prove a per-row void with no exception escaping. The "other rows still derive" half is architecturally guaranteed by `main()`'s per-directory loop but is not exercised by a multi-directory case |
| **R-P1.1** N stays 0 | **Satisfied** | 0 rows `state=complete` in the committed file, verified directly. Nothing in the change can promote a row |

Requirement-level total: **12 / 12 satisfied.** Scenario-level: **19 / 21** with passing covering
evidence; the two partials are both under R-P12 (see WARNING-2).

## CRITICAL-1 — the fourth both-sides-move-together instance: `load_surface()`

**`rig/derive.py:97-100` (`load_surface`) is the producer of Face C's live drift comparand, and its
computation is proven zero ways.** Face C's new drift check at `rig/derive.py:974-978` compares the
runner's recorded value against `ff_surface_digest`, built at `:901` as
`surface_digest(load_surface(FAILURE_FLOOD_SURFACE_ARM))`. Every self-test that supplies a
`recorded_surface_preimage_sha256` default computes it with the identical expression —
`_self_test_make_ff_run_dir` at `rig/derive.py:1519` assigns one `real_surface_digest` to BOTH
`surface_sha256` (`:1524`) and `recorded_surface_preimage_sha256` (`:1525`). All three sides of both
Face C comparisons are therefore the same expression, and a wrong `load_surface` moves all three
together.

The pin does not cover it. `_self_test_preimage_digest_pin()` (`rig/derive.py:1375-1388`) asserts
`surface_digest(["Bash","Read","Write","Read"])` equals the constant that
`rig/run-pipeline.sh --self-test` case a (`:578-581`) also asserts. Both sides feed a *hardcoded
list* on the Python side, so the pin proves the **hash convention** and never the **parse**. Task
2.1's own done-note (`tasks.md:385-392`) already names this as "the shared-literal mechanism ...
distinct from task 2.0's stronger both-implementations pin" — the artifact knew the pin was the
weaker kind, but did not draw the consequence. **No task is mis-checked; the gap is at requirement
level, so it needs a new task, exactly as 2.0 and 3.8 did.**

**Mutation proof, run in a throwaway full copy of the working tree** (baseline reproduced there
first: 59/59, 28/28, 20/20):

| Mutation | `derive --self-test` | `run-pipeline --self-test` | `rig/check.sh` |
|---|---|---|---|
| **M1** — `load_surface` stops excluding `#` header (drop `and not l.startswith("#")`) | **59/59 PASS**, exit 0 | 28/28, exit 0 | **20/20 PASS** |
| **M2** — `load_surface` returns a subset (`[1:]`) | **59/59 PASS**, exit 0 | 28/28, exit 0 | **20/20 PASS** |
| **M3** (control) — `surface_digest` returns a constant | exit 1, pin case red | — | — |

`rig/check.sh` reaching 20/20 under M1/M2 needs one clarification, because a naive run shows it
failing. `check_derive_reproduce` re-derives and compares against the committed `runs.jsonl`, and
`checker_digest` is `sha256` of `derive.py`'s own bytes (`:83`), so that check fails on **any** edit
to `derive.py` — proven with a control that appended nothing but a comment and produced the same
two failures. It therefore carries zero behavioural signal. Following the normal post-edit workflow
that R-P11.1's no-migrations rule requires (regenerate the goldens, then re-run), the mutated tree
reports **20/20 passed, 59/59, 28/28** — every gate green with a broken comparand producer.

**What it costs in production.** Under M1, Python's live comparand and bash's recorded comparand
disagree over the real committed preimage (`6a7da017…` vs `d8693e27…`, both computed directly).
Because the read-back loop at `:1001` now compares bash-against-bash, it stays silent, so the only
symptom is Face C's drift check firing: every model step of every row would void
`input-provenance-mismatch` with `"surface-preimage-drift"`. That reads as *the fixture moved after
the run* when the truth is *the deriver's parser is wrong* — **a correct refusal carrying a false
stated cause, blaming the fixture for a deriver defect.** R-P6.3 exists to keep exactly those two
statements apart, and `exploration.md` §2 records that shape as already having occurred three times
in this rig. `tasks.md:341-344` predicted this class in writing for Face A's cross-language pair and
closed it with task 2.0 part b; Face C's pair was left with the weaker mechanism.

**Blast radius is bounded, and the orchestrator should weigh this before accepting FAIL.** The fault
can only over-void; it cannot promote a row to `complete`, so no false green is reachable. N = 0, so
nothing citable depends on it today, and `STEP_TIMEOUT_S`/`SUITE_TIMEOUT_S` remain placeholders, so
a further cycle stands between here and the first countable run. A reader could reasonably grade
this WARNING. I grade it CRITICAL on consistency: the identical fault in the identical position was
treated as blocking for Face A (task 2.0) and Face B (task 3.8), and applying a weaker standard to
the third face is itself the failure mode this cycle exists to correct.

**Proposed follow-up task 2.9 (Sibling 2 / Face C, under R-P6.1 + R-P6.3 + R-P10.1)** — give Face C
the same real cross-language pin Face A has: `sed`-extract `preimage_digest()` from
`rig/run-pipeline.sh`, run the deriver's own full path (`surface_digest(load_surface(...))`, never a
hardcoded list) over one synthetic preimage file carrying a `# harness:` header, blank lines,
duplicates and indentation, and assert equality.

**The remedy is validated, not asserted.** Written and executed in the scratch copy: it prints
`4a626b46…` on both sides at baseline (PASS — and, usefully, the same constant already pinned), and
goes red under both M1 and M2.

| | baseline | M1 | M2 |
|---|---|---|---|
| proposed Face C pin | PASS | **FAIL** | **FAIL** |

## What else I checked before concluding this was the only remaining instance

The launch prompt named seven candidates. Each was checked rather than assumed.

| Candidate | Independent proof of its computation? |
|---|---|
| `surface_digest` (`derive.py:90`) | **Yes** — pinned literal at `:1383-1385`; control M3 turns it red |
| `preimage_digest` (bash, `run-pipeline.sh:255`) | **Yes** — pinned literal over a real synthetic file, `:578-581`; also covers absent/empty shapes at `:586-599` |
| `answer_key_set_digest` (`derive.py:621`) | **Yes** — task 2.0 case a (self-mutation) + case b (real `sed`-extracted cross-language pin) |
| `fixture_digest_at` (`derive.py:612`) | **Yes** — task 3.8 case a, same-length one-byte mutation with a length assertion at `:2137-2139` |
| `hash_paths` (bash, `:226`) | **Yes** — before/after fire-proofs at `:432-454` (edit changes it, order does not, missing ≠ empty, outside-set does not) plus task 2.0's pin |
| `compute_manifest` (bash, `:162`) | **Yes, and the strongest of them** — pinned in production against the committed `MANIFEST.sha256` at `:718-724`, which hard-refuses the run on mismatch; path selection proven at `:533-561` |
| `checker_digest` (`derive.py:83`) | Out of scope — Face D, declared Non-Goal, excluded by R-F5.3's own scenario |
| `fixture_digest(version)` (tool-surface) | Untouched by this cycle; pinned by the committed 42-row golden |
| `load_surface` (`derive.py:97`) | **NO — CRITICAL-1** |
| `manifest_workspace_paths`, `answer_key_paths` | Yes — exact-literal expectations at `:557-569` |
| `read_back_init` (bash, `:333`) | Produces `surface_sha256` from the CLI's own init event; not a comparand this cycle changed |

## WARNING-1 — Face C's per-step field is absent, not null, on all three committed rows

`steps[].recorded_surface_preimage_sha256` is **not a key** on any of the three committed
`failure-flood-v1` rows. The row-level fields are written explicitly (`rig/derive.py:1188-1190`,
`arm_data.get(...)`), so they land as present-and-`null`; the per-step field has no such write and
relies on `step_out = dict(step)` at `:1052` copying it through, which cannot invent a key a
pre-scheme `arm.json` never had.

R-P11.1 requires that re-deriving "rewrites every existing row with the new schema version **and the
new fields**". Three of four land; the fourth does not. Detection is unaffected — `:938` uses
`s.get(...) is None`, which treats absent and null alike — but the consumer contract is asymmetric
(`row["recorded_fixture_digest"]` yields `None`, `row["steps"][i]["recorded_surface_preimage_sha256"]`
raises `KeyError`). It also makes PR #8's "all four provenance fields `null`" and
`apply-progress.md:174`'s neighbouring claim imprecise; `apply-progress.md:181` is correct because it
says "the three new row-level fields".

Not a blocker: no requirement is violated in substance, `rig/derive.py:654-657` documents the
copy-through decision deliberately, and no consumer reads the field today (`rig/report.py` does not).
Worth one line of correction on archive.

## WARNING-2 — the refusal-to-derive gate is vacuous for `failure-flood-v1`

`run_self_tests()` is fed the **per-experiment** answer-key loader (`rig/derive.py:2210`) and skips
every key without `tool_sets` (`:381-384`). `failure-flood`'s answer keys carry `C`/`F0`/`S0`/`R0`
and define no `checker_self_test`, so for that experiment `run_self_tests()` iterates **zero cases
and returns `True` vacuously.** Proven live: the same corrupted `t1/negative_control` that makes
`--experiment tool-surface-v1` exit 1 with no rows leaves `--experiment failure-flood-v1` at exit 0
with rows written.

Compounding it: the 59-case `--self-test` suite — which contains **every one of this cycle's detector
proofs** — is not composed into the derive path at all. Only `rig/check.sh` composes it
(`check_component_self_test`, `:160-171`), and that helper hardcodes `python3` (`:163`), which is
also the named bash-arm gap. So `python3 rig/derive.py --experiment failure-flood-v1` will derive
rows with all 59 proofs broken.

This is **not a violation of R-P12.1**, which asks only that the existing refusal not be weakened —
it was not, and the skip predates this cycle (task 5.8). But R-P12's scenarios are written in
failure-flood terms, and the precondition "`run_self_tests()` fails" is unsatisfiable there, which is
why R-P12's two scenarios are graded partial. Task 4.4's parenthetical — "no `--experiment` flag
needed — `run_self_tests()` runs unconditionally in `main()`" — is literally true and materially
misleading; the done-note's own evidence is honest and correctly names `tool-surface-v1`.

## WARNING-3 — task 2.5's comparand change is a row-outcome no-op, and that should be a permanent claim boundary

Sibling 2's report recorded task 2.5's comparand choice as a provable no-op at the row-outcome level.
**Confirmed still true after Sibling 3, and confirmed empirically**: reverting `rig/derive.py:1001`
to the pre-change live comparand (`step_surface != ff_surface_digest`) leaves **59/59 green**. It has
to — the Face C accumulation at `:974-978` voids any row whose recorded value differs from
`ff_surface_digest` for any model step, so every row reaching the read-back loop satisfies
`recorded == live` and the two comparands are indistinguishable there. R-P6.1 and R-P6.2 are
satisfied on their own terms.

**It should be recorded as a permanent claim boundary rather than left as an apply-phase note**,
because the no-op is conditional on a guarantee living 25 lines away. Narrowing or removing the
Face C drift accumulation at `:974-978` would silently make `:1001`'s comparand observable, and
there is no test — and by construction can be no test — that would notice. The right home is a
comment at `:993-1001` naming `:974-978` as the invariant's owner. Sibling 3 did not disturb it.

## WARNING-4 — R-P2.2a's order-swap proof was executed but never committed

`2873e04`'s message records that the both-drifts case was proven "under the checks' own code order
and again with that order swapped in a scratch copy". The swapped run is gone with the session. The
property itself is structurally true and I verified it by reading `rig/derive.py:954-981` (one
accumulator, no early exit, no ordering predicate), so R-P2.2a is satisfied — but ADR 0013's own rule
is that a committed executable carries its own test, and this proof does not re-run.

## WARNING-5 — no worktree taken, against `checkout-isolation`

An SDD cycle is long-running work in a checkout that demonstrably has other writers: three foreign
worktrees exist (`gaps-analysis` on `main`, `installer-shape` on `docs/installer-shape`,
`open-work-index` on `feat/gap-record-prowler`) and `stash@{0}` is not this cycle's.

**One mitigation verified rather than assumed.** The `checkout-isolation` hook preflight, run from
this checkout, prints `ok — gated by this tree: <repo>/hooks/pre-commit` (the absolute path this
command actually printed is redacted here per ADR 0009 — this repo is public). The primary checkout's
hook resolves inside its own tree, so all three sibling commits **were** covered by the redaction
gate. Running the same check from each worktree prints `WRONG TREE` for all three, confirming the
shim gap is still open and still accurately described. Had this cycle taken a worktree, its commits
would have been gated by another tree's script.

## SUGGESTIONS

1. **`rig/check.sh` has no bash self-test arm** — `check_component_self_test()` hardcodes `python3`
   (`rig/check.sh:163`), so `rig/run-pipeline.sh --self-test` is never composed and must be run by
   hand. Confirmed; accurately described; correctly deferred by spec Decision 3.
2. **`STEP_TIMEOUT_S=180` / `SUITE_TIMEOUT_S=150` remain placeholders** (`rig/run-pipeline.sh:85-86`),
   and the comment names them as such pending task 5.7's wall-clock measurement. Confirmed. Closing
   this cycle does not found the first countable run.
3. **Three Engram observations cite commits that no longer exist on any branch** — #308, #322 and
   #344 reference `123b622` and `afced18` for Sibling 3. Both are unreachable
   (`git branch -a --contains 123b622` is empty); the live commit is `2873e04`, same parent and same
   message, different tree. Worth correcting on archive so the durable record cites a reachable
   commit.
4. **Task count** — the launch prompt said 30; the artifact carries 35. All `[x]`.
5. **Authored-line count excludes `MAP.md`** — 1049 reconciles exactly on that convention, 1051 with
   it. Immaterial to the authorized `size:exception`, but the convention is worth stating once.

## The N = 0 prose scan

Every file this cycle touched was scanned, plus the delivery surface. Files: `MAP.md`,
`rig/README.md`, `rig/derive.py`, `rig/run-pipeline.sh`,
`sdd/run-input-provenance/apply-progress.md`, `sdd/run-input-provenance/tasks.md`,
`rig/results/failure-flood-v1/runs.jsonl`, `rig/results/tool-surface-v1/runs.jsonl`, and PR #8's
body. Method: a phrase scan for constructions that assert countable results, then a full read of
every occurrence of `countable`, `comparative`, `N =`, `N is`, `state=complete` and `"complete"` in
the prose files.

**Result: no violation. The boundary holds in every artifact.** The two phrase-scan hits in
`tasks.md` (`:15`, `:641`) are the prohibition itself, not a breach.

The four sentences that came closest, each read in full and each clean:

- `sdd/run-input-provenance/tasks.md:341-344` — "on the first real countable run *every* row voids
  with `answer-key-drift`". Conditional and counterfactual (`If the two sides differ by so much as a
  trailing newline, then …`), inside a mutation-proof rationale. Names a future risk, asserts no
  present result. Notably, this is the sentence that predicted CRITICAL-1's class for Face A.
- `apply-progress.md:221` and `:788` — "Whether to fund a real, countable run stays the operator's
  [decision]". Forward-looking and explicitly unfunded.
- `MAP.md:52` — the longest and most exposed passage, and correct: "still an instrument plus a
  **failed** ratio target, never a comparative result: zero countable runs", with the archived
  cycle's boundary carried verbatim rather than paraphrased.
- `rig/README.md:63-74` — the schema correction. Describes only field names and the schema bump; no
  outcome language of any kind. Task 3.6's done-note records that it was re-read specifically against
  this constraint, and that re-read holds.

**PR #8's body is the strongest of the artifacts on this point**, not merely compliant: it opens with
a blockquote (`N = zero countable rows`), splits "What can be claimed" from "What cannot be claimed",
states that no countable run has ever been made, and volunteers that the timeout placeholders mean
closing this cycle is **not** sufficient to found the first one. Its one imprecision is factual, not
boundary-related: "all four provenance fields `null`" (see WARNING-1).

## Design coherence

| Design decision | Code state |
|---|---|
| §1 Face C is per-step, Faces A/B arm-level | Held — `rig/run-pipeline.sh:915` (step) vs `:1211-1212` (arm) |
| §2 set-wide answer-key digest per fixture root | Held — `rig/run-pipeline.sh:748` |
| §4 one `void_reason` pair + per-face drift classes | Held — `rig/derive.py:921`, `:942`, `:980` and the three drift strings |
| §7 `tool-surface-v1`'s registry entry gains no key | Held — `rig/derive.py:1246-1256` byte-unchanged; `answer_key_digest` appears only in the failure-flood entry at `:1270` |
| §9 cross-language pins, a disagreement is the finding | **Partly held** — real pin for Face A, correctly-argued absence for Face B (`rig/derive.py:2107-2121`), but Face C's is a shared literal that never exercises the Python parse (CRITICAL-1) |

## What would have to change for the next grade up

**FAIL → PASS WITH WARNINGS:** close CRITICAL-1 by adding the validated Face C cross-language pin as
task 2.9. One self-test case; the exact form is proven above to pass clean and fail under both
mutations. Nothing else blocks.

**PASS WITH WARNINGS → PASS:** additionally (a) write Face C's per-step field explicitly so all four
provenance fields are present-and-`null` on re-derived rows, and correct the "all four ... null"
wording (WARNING-1); (b) either give `failure-flood`'s answer keys a `checker_self_test` block or
compose `derive.py --self-test` into the derive path, so R-P12.1's gate is not vacuous for the
experiment this cycle is about (WARNING-2); (c) record task 2.5's no-op as a permanent claim boundary
at `rig/derive.py:993-1001`, naming `:974-978` as the invariant's owner (WARNING-3); (d) commit the
order-swap proof (WARNING-4).

WARNING-5 is not closable retroactively; it is a process note for the next cycle, and the hook
preflight above shows the redaction gate did in fact cover these commits.
