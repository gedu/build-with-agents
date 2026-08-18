---
id: sdd/archive/2026-08-18-failure-flood-triage/archive-report
type: journal
targets: [any]
status: validated
verified: 2026-08-18
sources: ["sdd/archive/2026-08-18-failure-flood-triage/spec.md", "sdd/archive/2026-08-18-failure-flood-triage/tasks.md", "sdd/archive/2026-08-18-failure-flood-triage/verify-report.md", "sdd/archive/2026-08-18-failure-flood-triage/apply-progress.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0012-a-hypothesis-is-never-citable.md"]
cycle_status: complete_with_warnings
verification_round: 4
verified_commit: a7d2a0b
---

# Archive Report: failure-flood-triage

**Change**: `failure-flood-triage`  
**Archived**: 2026-08-18 to `sdd/archive/2026-08-18-failure-flood-triage/`  
**Status**: Closed with warnings permitted  
**Cycle Result**: PASS WITH WARNINGS — Archive Permitted

## Artifact Traceability (Engram Observation IDs)

All artifacts retrieved for final state authority:

| Artifact | Observation ID | Retrieved |
|----------|---|---|
| proposal.md | #220 | 2026-08-18 |
| spec.md | #222 | 2026-08-18 |
| design.md | #223 | 2026-08-18 |
| tasks.md | #225 | 2026-08-18 |
| verify-report.md | #263 | 2026-08-18 |

## THE ARCHIVE CONDITION

**Boundary sentence, carried verbatim per specification:**

> This cycle delivers an instrument plus a failed target, never a comparative result.

**What this means**: The cycle has delivered:
- A built, self-verified measurement instrument (the `failure-flood-v1` and `failure-flood-v2` rigs plus their derived metrics)
- Ground truth measured and frozen (42 baseline captures, 3 staged runs, all entry points verified)
- A target that **FAILED** at ~83:1 against a ratified 500:1 order of magnitude, and this failure is recorded explicitly as FAILED, not softened

**What cannot be claimed**:
- Any comparative result between harness shapes (both arms are still pending countable runs)
- Countable rows: **N = zero** in every cell of both outcome channels (diagnostic attribution and green-restore)
- Neither hypothesis is settled per ADR 0012 — they remain open

**No countable run has ever been made**. Every row in `rig/results/failure-flood-v1/runs.jsonl` carries `state=void`, and every void reason is documented (shakedown, dirty-tree, or no-preregistration).

## Verification Round 4: PASS WITH WARNINGS

**Final Verdict**: 0 CRITICAL, 14 WARNING, 5 SUGGESTION  
**Verified Commit**: `a7d2a0b`  
**Authority**: Native verification gate ledger recorded `outcome: passed`, `complete: true`

**Verification Gate Exit Codes** (final run, all present):
- `./hooks/pre-commit --all`: **exit 0**
- `./check.sh`: **exit 0**
- `./rig/check.sh`: **exit 0** (20/20 checks passed)

### Post-Verification Work: PR8

PR8 landed **AFTER round 4 verification** and is therefore NOT covered by any verification round. PR8 implements process improvements (commit `836cb23`), not fixes to verified findings.

**What was done in PR8**:
- Built `rig/check.sh` — a fast (~2.2s) rig-scoped pre-flight gate with six checks
- Mutation-tested all six check families in a scratch copy (never the working tree)
- Registered `rig/check.sh` in `OPERATIONS.md`
- **Evidence type**: Mutation testing in scratch environment, not a verification round

**Verification of PR8**:
- All eight committed executables remain byte-identical to the pre-PR8 state
- Manifests regenerated with a different enumerator and sha256 implementation, both match
- Negative control confirmed: comment-only edits still trip the manifest gate
- Mutation testing reproduced CRITICAL-6 (manifest re-freeze failure) in 2.6 seconds

## Key Findings from Verification Report

Per Engram #263 (verify-report.md):

### WARNING-14 — The Three-Sided Gap (Now One Confirmed Defect)

Root cause: **`derive.py` distinguishes "proven wrong" from everything else and never distinguishes "proven right" from "not proven at all".** Every downgrade tests `is False`, so a `None` value passes unchallenged.

**Demonstrated**: A destroyed-capture directory, when promoted to countable shape with its capture untouched:
- Derives as `state=void/surface-mismatch` under the committed 31-tool preimage (correct)
- Derives as `state=complete, verdict=green` under a header-only preimage (incorrect)

**Consequence**: For that shape, the model and permission-mode pins are dead. Detection currently depends on an accidental guard with diagnostically wrong reason. **This blocks the first countable run, not the archive.**

**Related issues** (from the same root cause):
- Task 7.15 (fixture_digest present-derived) — scope gap
- WARNING-10 (model_matches_declared absent) — silent pass
- Stray-directory detection — weak

### Task 7.15 Under-Scoped (Deliberately Open)

Task 7.15 must NOT be closed as written. The present-derived class is at least three fields wide:
1. `MANIFEST.sha256` → `fixture_digest`
2. `answer-key/*.json` → `R0`/`S0` → `causes_correct`/`suite_state_cause`/`verdict` (scoring path — wider than task 7.15)
3. `rig/surfaces/failure-flood.txt` → the `surface-mismatch` void

Second-order consequence: Because the field follows the present, **R-F5.3's byte-identical re-derive cannot detect that a fixture moved under already-recorded rows**. Round 4's re-derive is byte-identical only because manifests were re-frozen first.

### WARNING-13: Validator Scope

`gentle-ai sdd-verify-validate` admits a passing verdict only at full requirement coverage (31/31, 19/19), which is unreachable by construction for this change, so a passing verdict cannot be emitted under that contract. The verifier satisfied `check.sh` and recorded the validator denial as a deliberate, reported deviation. This is expected and does not block archive.

## Task Completion Status

**Deliberately Open Tasks** (not closed by design, per launch prompt):

- **Task 7.10**: `rig/run-pipeline.sh --self-test` — Registered, deliberately deferred
  - Reason: Needs its own bash-harness construction; extracted-function pattern was re-invented ad hoc in three separate batches
  - Related: ADR 0013's trigger ("when a third executable needs a test") is met here, but per-executable self-test pattern still holds
  - Status: Remains `[ ]` in tasks.md by explicit record

- **Task 7.15**: `fixture_digest` present-derived — Registered, deliberately deferred
  - Reason: Under-scoped as written; scope includes at least three fields, not one
  - Consequence: Cannot close until the full scope is re-examined per verification finding
  - Status: Remains `[ ]` in tasks.md by explicit record

**All other implementation tasks** (PR1–PR8): Marked complete (`[x]`)

**Changed Lines** (PR8 batch): 524 authored lines
- `rig/check.sh`: 522 lines (new file)
- `OPERATIONS.md`: 2 modified lines, 1 added

**Total stack (PR1–PR8)**: ~2,050 authored lines over six PRs, within ratified 700-line per-PR ceiling (chained delivery approved)

## ADR Renumbering Note

This cycle's `decisions/0014-a-fixtures-runtime-is-substrate-not-this-repos-runner.md` was renumbered to **`0015`** after `main` independently published its own `0014` (PR7D event). Archive text cites it as `0015`.

## Specification Alignment

**No openspec/ delta specs found** — this repository uses `sdd/` as the sole artifact store in hybrid mode.

## Archive Move Verification

**Mechanical copy contract**: All artifacts moved via `git mv` with byte-identity verified via `diff -r`.

```
Archive move: sdd/failure-flood-triage → sdd/archive/2026-08-18-failure-flood-triage
Verification: diff -r (empty diff = success)
Result: PASS — no differences detected
```

Source directory confirmed gone; destination confirmed intact.

## Blockage Analysis

**CRITICAL issues in verification**: 0 — Archive permitted per native gate.

**WARNING issues that affect final state**:
- WARNING-14 (three-sided gap in `derive.py` logic) — blocks first countable run, not archive
- WARNING-13 (validator scope limitation) — expected by design, does not block archive
- Tasks 7.10, 7.15 deliberately open — recorded in spec and design, closure deferred by explicit decision

## Delivery Summary

**Status**: Archive complete  
**Authorization**: Native review gate returned `reviewGate` absent (no review conducted for this candidate; proceeding under ordinary repository policy)  
**Gate checks**: All three gates pass (exit 0)  
**Verification verdict**: PASS WITH WARNINGS — archive permitted  
**Archive integrity**: Mechanical move verified, byte-identical

## What Ships

This cycle ships:

1. **The `failure-flood-v1` and `failure-flood-v2` measurement instruments** fully constructed, tested, and frozen
2. **A failure-flood dataset** (42 baseline captures, 3 stage runs) — ground truth for the target ratio
3. **Process improvements** (PR8: `rig/check.sh` pre-flight gate) to prevent future manifest mismatches
4. **Deliberate deferrals** recorded in open tasks and specification for future work (hypotheses testing, fixture scope re-examination, bash-harness extraction)

The cycle does NOT ship:
- Countable runs (all rows remain void)
- Comparative harness results (both arms incomplete)
- A passing hypothesis test (both remain open per ADR 0012)

## Key Learnings

1. Verifying an inherited assumption against `derive.py` rather than trusting it reordered the whole delivery — the "verified cost instrument" could not measure the primary metric.

2. A deliberate config-breakage injection is mechanically indistinguishable from an environmental void without a separate guard — WARNING-14's root cause.

3. Slice ordering can silently violate ADR 0012 (pre-registration landing after the runner needed explicit guards).

4. Shell gotcha: backticks inside double-quoted git commit messages are command-substituted — use `git commit -F <file>` instead.

5. Generated case tables at amplified scale become a cheat vector and must join `tests/` and `runtime/` as read-only substrate.

---

**Archived**: 2026-08-18  
**Cycle**: Complete with documented warnings  
**Next**: No additional SDD phases required. Recommendations for follow-up work recorded in open tasks (7.10, 7.15).
