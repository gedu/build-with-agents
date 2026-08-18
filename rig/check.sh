#!/usr/bin/env bash
#
# rig/check.sh — the rig's own fast pre-flight gate.
#
# WHY THIS EXISTS
#   Verify rounds in this cycle were repeatedly blocked by the previous round's own remedy:
#   twice, a committed change silently broke `rig/run-pipeline.sh` and nobody noticed until a
#   full verification round read the output by hand. The worst case (CRITICAL-6): an ADR
#   renumber edited *comment lines* inside manifest-covered fixture files, `MANIFEST.sha256`
#   was never re-frozen, and the runner started exiting 2 at preflight on BOTH fixtures — a
#   defect a two-second `diff` would have caught. This script is that `diff`, plus five more
#   checks the same failure class could hide behind.
#
# WHAT IT CHECKS
#   1. MANIFEST.sha256 recompute-compare for both fixtures (v1, v2) — reuses
#      compute_manifest() extracted verbatim from rig/run-pipeline.sh, never re-implemented.
#   2. Composes the three existing `--self-test` flags: rig/derive.py, rig/report.py,
#      rig/collect.py. Their own cases are not duplicated here.
#   3. Confirms rig/run-pipeline.sh's own preflight reaches PAST the manifest gate on both
#      fixtures, without ever invoking `claude -p` and without claiming a new run directory.
#      v1 has no answer-key/prereg.json by design (task_id s1 is always --shakedown), so a
#      non-shakedown s1 invocation is EXPECTED to exit 2 at the pre-registration gate — that
#      is the proof the manifest gate was already passed, not a failure. v2 DOES have a
#      prereg.json that currently passes, so this check collides its probe with the already-
#      committed void run s2-pipeline-9054, which exits 0 via the idempotent-skip path before
#      ever reaching model invocation. If that run is ever removed, this check refuses rather
#      than risk claiming a fresh run directory.
#   4. rig/derive.py re-derives byte-identically for both experiments (tool-surface-v1,
#      failure-flood-v1) — the committed rig/results/<experiment>/runs.jsonl must not change.
#   5. Stray or partial run directories under rig/runs/failure-flood-v1/. derive.py enumerates
#      every directory matching its run-id pattern, so an extra or malformed one silently
#      becomes an extra row. Two shapes are detected: a partial (no arm.json at all), and a
#      complete-looking-but-corrupted one (a model step reporting exit_code 0 with every
#      read-back field null and no stream.jsonl on disk — the exact shape produced live by a
#      backgrounded probe whose `kill` failed).
#   6. `bash -n` over the rig's own shell scripts and `python3 -m py_compile` over the rig's
#      own Python files (including the fixture's committed generator/helper scripts).
#
# WHY IT LIVES HERE AND NOT IN THE ROOT check.sh OR hooks/pre-commit
#   OPERATIONS.md is explicit: the hooks and the root check.sh deliberately do not depend on
#   python3, because they must run on a machine that installed nothing and in CI with no setup
#   step. This gate needs python3 (to reuse compute_manifest() and to drive derive.py/
#   report.py/collect.py), so it is rig-scoped and standalone, exactly like `python3` itself is
#   already a rig-only prerequisite (decisions/0011). Do not fold this into the root check.sh
#   or hooks/pre-commit, and do not make either of those depend on python3 to absorb it.
#
# EXIT CODES (same contract as every other gate in this repo)
#   0  clean — every check passed
#   1  a check found a real violation. Fix it. Never `--no-verify` past it
#   2  COULD NOT RUN — a prerequisite is missing, or a check's own machinery broke.
#      Never a pass. Never conflated with 0
#
# USAGE
#   rig/check.sh              run every check against the real repository
#   rig/check.sh --self-test  test this gate's OWN helper logic against synthetic fixtures
#   rig/check.sh --help       this header
#
# SELF-TEST (ADR 0013)
#   Kept proportionate, per this unit's own scope: it exercises this gate's OWN classifier
#   functions (manifest compare, the preflight-output classifiers, the stray-run-directory
#   shape detector) against synthetic input in a throwaway temp directory. It does not
#   re-invoke rig/run-pipeline.sh, rig/derive.py, rig/report.py or rig/collect.py — those
#   already carry their own `--self-test` (composed, not duplicated, by check 2 above), and
#   re-testing the whole rig here would be the ADR 0013 gap this file is scoped to close, not
#   the whole rig again.
#
# PORTABILITY
#   bash + python3 (stdlib only, decisions/0011) — the same shell and interpreter every other
#   rig-scoped executable already uses (rig/run.sh, rig/run-pipeline.sh, rig/*.py). Never GNU-
#   only flags beyond what run-pipeline.sh itself already requires (GNU `timeout`).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_PIPELINE="$REPO_ROOT/rig/run-pipeline.sh"
FF_V1="$REPO_ROOT/rig/fixtures/failure-flood/v1"
FF_V2="$REPO_ROOT/rig/fixtures/failure-flood/v2"
FF_RUNS="$REPO_ROOT/rig/runs/failure-flood-v1"

show_help() {
  awk 'NR>1 && /^#/ { sub(/^# ?/, ""); print; next } NR>1 { exit }' "$0"
}

die_cannot_run() {
  printf '\n  RIG CHECK COULD NOT RUN: %s\n  This is exit 2, not a pass.\n' "$1" >&2
  exit 2
}

command -v bash >/dev/null 2>&1 || die_cannot_run "bash is missing"
command -v python3 >/dev/null 2>&1 || die_cannot_run "python3 is missing (rig-only prerequisite, decisions/0011)"
command -v git >/dev/null 2>&1 || die_cannot_run "git is missing"
[ -f "$RUN_PIPELINE" ] || die_cannot_run "$RUN_PIPELINE does not exist"

CHECKS_RUN=0
CHECKS_FAILED=0

pass() {
  CHECKS_RUN=$((CHECKS_RUN + 1))
  printf '  [PASS] %s\n' "$1"
}

fail() {
  CHECKS_RUN=$((CHECKS_RUN + 1))
  CHECKS_FAILED=$((CHECKS_FAILED + 1))
  printf '  [FAIL] %s -- %s\n' "$1" "$2" >&2
}

sha256_file() {
  # $1 path. Prints "<empty>" for a missing file rather than erroring, so a
  # before/after comparison across derive.py's own mkdir -p + write is safe.
  if [ ! -f "$1" ]; then
    printf '<absent>'
    return 0
  fi
  python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"
}

# ---- reuse compute_manifest() from rig/run-pipeline.sh — extracted, never
# re-implemented (R-F... / this unit's own instruction). sed pulls the exact
# function body by name, so a future edit to the function is picked up
# automatically; only a rename or removal requires touching this file.
load_compute_manifest() {
  local body
  body="$(sed -n '/^compute_manifest() {/,/^}/p' "$RUN_PIPELINE")"
  [ -n "$body" ] || die_cannot_run "could not extract compute_manifest() from $RUN_PIPELINE by name — has it moved or been renamed?"
  eval "$body"
  [ "$(type -t compute_manifest)" = "function" ] || die_cannot_run "compute_manifest() did not load after extraction"
}
load_compute_manifest

# ============================================================================
# check 1 — MANIFEST.sha256 recompute-compare, both fixtures
# ============================================================================

classify_manifest() {
  # args: computed committed. Echoes PASS or FAIL.
  if [ "$1" = "$2" ]; then echo PASS; else echo FAIL; fi
}

check_manifest() {
  local root="$1" label="$2" mf computed committed
  mf="$root/MANIFEST.sha256"
  if [ ! -f "$mf" ]; then
    fail "manifest:$label" "missing $mf"
    return
  fi
  computed="$(compute_manifest "$root")"
  committed="$(cat "$mf")"
  if [ "$(classify_manifest "$computed" "$committed")" = "PASS" ]; then
    pass "manifest:$label recompute-compare clean ($mf)"
  else
    fail "manifest:$label" "MANIFEST.sha256 mismatch under $root -- recomputed digest differs from the committed one (this is exactly CRITICAL-6's shape: a fixture file changed and the manifest was never re-frozen)"
  fi
}

# ============================================================================
# check 2 — compose the three existing --self-test flags
# ============================================================================

check_component_self_test() {
  local script="$1" out rc
  set +e
  out="$(python3 "$REPO_ROOT/rig/$script" --self-test 2>&1)"
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then
    pass "self-test:$script (exit 0)"
  else
    fail "self-test:$script" "exited $rc -- $(printf '%s' "$out" | tail -3 | tr '\n' ' ')"
  fi
}

# ============================================================================
# check 3 — runner preflight reaches past the manifest gate on both
# fixtures, without spending a run and without ever invoking `claude -p`
# ============================================================================

classify_preflight_v1() {
  # args: rc out before after. Echoes PASS or FAIL.
  local rc="$1" out="$2" before="$3" after="$4"
  if [ "$rc" -eq 2 ] \
    && printf '%s' "$out" | grep -q 'missing-prereg-config' \
    && ! printf '%s' "$out" | grep -q 'MANIFEST.sha256 mismatch' \
    && [ "$before" = "$after" ]; then
    echo PASS
  else
    echo FAIL
  fi
}

classify_preflight_v2() {
  # args: rc out before after. Echoes PASS or FAIL.
  local rc="$1" out="$2" before="$3" after="$4"
  if [ "$rc" -eq 0 ] \
    && printf '%s' "$out" | grep -q 'already void.*skipping (idempotent)' \
    && ! printf '%s' "$out" | grep -q 'MANIFEST.sha256 mismatch' \
    && [ "$before" = "$after" ]; then
    echo PASS
  else
    echo FAIL
  fi
}

ff_runs_count() {
  [ -d "$FF_RUNS" ] || { echo 0; return; }
  find "$FF_RUNS" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' '
}

check_preflight_v1() {
  local before after out rc
  before="$(ff_runs_count)"
  set +e
  # Never --shakedown: the whole point is to observe the non-shakedown
  # preflight order (manifest, then the pre-registration gate). Iteration is
  # a sentinel that cannot collide with a real run id; v1 dies at the
  # pre-registration gate before ever attempting to claim a run directory,
  # so no directory is created regardless of which iteration is used.
  # --dirty-ok is required here, not optional: this gate is meant to run
  # while rig/ files are being edited (that is the whole point of a fast
  # local pre-flight check), and rig/check.sh's own presence under rig/ as
  # an uncommitted file trips run-pipeline.sh's unrelated dirty-tree guard
  # otherwise -- a false negative on THIS check, not a real preflight-order
  # regression. --dirty-ok bypasses only that guard (R-F8.2); it never
  # implies --shakedown and produces no countable row on its own.
  out="$("$RUN_PIPELINE" s1 monolithic 00checkgate --permission-mode dontAsk --model check-gate-probe --dirty-ok 2>&1)"
  rc=$?
  set -e
  after="$(ff_runs_count)"
  if [ "$(classify_preflight_v1 "$rc" "$out" "$before" "$after")" = "PASS" ]; then
    pass "preflight:v1 reaches the pre-registration gate past the manifest gate (exit 2 by design, v1 has no prereg.json); no run directory created"
  else
    fail "preflight:v1" "expected exit 2 at the pre-registration gate with no new run directory; got exit $rc, run-dir count $before -> $after -- $(printf '%s' "$out" | tail -3 | tr '\n' ' ')"
  fi
}

check_preflight_v2() {
  if [ ! -f "$FF_RUNS/s2-pipeline-9054/status.json" ]; then
    fail "preflight:v2" "the committed idempotent collision target s2-pipeline-9054 is gone; refusing to probe with a fresh iteration because that would risk claiming a new run directory and reaching a real invocation"
    return
  fi
  local before after out rc
  before="$(ff_runs_count)"
  set +e
  # v2 DOES have a prereg.json that currently passes, so this deliberately
  # collides with the already-committed void run: run-pipeline.sh's own
  # idempotent-skip path (mkdir fails, prior state is void/complete) exits 0
  # BEFORE materialize_step/run_model_step ever runs -- no claude invocation,
  # no new run directory, even though npm ci + case generation (real, cheap,
  # cache-warm preflight setup) do run first. --dirty-ok for the same reason
  # as check_preflight_v1 above.
  out="$("$RUN_PIPELINE" s2 pipeline 9054 --permission-mode dontAsk --model check-gate-probe --dirty-ok 2>&1)"
  rc=$?
  set -e
  after="$(ff_runs_count)"
  if [ "$(classify_preflight_v2 "$rc" "$out" "$before" "$after")" = "PASS" ]; then
    pass "preflight:v2 reaches past the manifest gate and the pre-registration gate; idempotent skip on the existing void run, no run spent, claude never invoked"
  else
    fail "preflight:v2" "expected exit 0 idempotent skip on s2-pipeline-9054 with no new run directory; got exit $rc, run-dir count $before -> $after -- $(printf '%s' "$out" | tail -3 | tr '\n' ' ')"
  fi
}

# ============================================================================
# check 4 — derive.py re-derives byte-identically for both experiments
# ============================================================================

check_derive_reproducible() {
  local exp="$1" results_file before after out rc
  results_file="$REPO_ROOT/rig/results/$exp/runs.jsonl"
  before="$(sha256_file "$results_file")"
  set +e
  out="$(python3 "$REPO_ROOT/rig/derive.py" --experiment "$exp" 2>&1)"
  rc=$?
  set -e
  if [ "$rc" -ne 0 ]; then
    fail "derive-reproduce:$exp" "derive.py --experiment $exp exited $rc -- $(printf '%s' "$out" | tail -5 | tr '\n' ' ')"
    return
  fi
  after="$(sha256_file "$results_file")"
  if [ "$before" = "$after" ]; then
    pass "derive-reproduce:$exp re-derives byte-identically ($results_file unchanged)"
  else
    fail "derive-reproduce:$exp" "$results_file changed after re-derivation (before=$before after=$after) -- derive.py is not a pure function of the run directories"
  fi
}

# ============================================================================
# check 5 — stray or partial run directories under rig/runs/failure-flood-v1/
# ============================================================================

FF_RUN_ID_PATTERN='^s[12]-(monolithic|pipeline)-[0-9][A-Za-z0-9]*$'

classify_run_dir() {
  # $1 = run directory path. Echoes "OK", "PARTIAL" (no arm.json), or
  # "CORRUPTED:<step>" (a model step with exit_code 0, every read-back field
  # null, and no stream.jsonl on disk). Mirrors derive.py's own
  # build_row_failure_flood() read order (arm.json, then per-step evidence)
  # without importing it, since this classifier answers a structural question
  # ("is this directory a genuine run?"), not derive.py's scoring question.
  local dir="$1"
  if [ ! -f "$dir/arm.json" ]; then
    echo PARTIAL
    return
  fi
  python3 - "$dir" <<'PY'
import json, os, sys

run_dir = sys.argv[1]
with open(os.path.join(run_dir, "arm.json")) as f:
    data = json.load(f)
for step in data.get("steps", []):
    if step.get("kind") != "model":
        continue
    stream_path = os.path.join(run_dir, "steps", str(step.get("index", "")), "stream.jsonl")
    if (
        step.get("exit_code") == 0
        and step.get("permission_mode_actual") is None
        and step.get("surface_sha256") is None
        and not os.path.isfile(stream_path)
    ):
        print(f"CORRUPTED:{step.get('index', '?')}")
        break
else:
    print("OK")
PY
}

check_stray_run_dirs() {
  if [ ! -d "$FF_RUNS" ]; then
    fail "stray-run-dirs" "$FF_RUNS does not exist"
    return
  fi
  local d name verdict any=0
  for d in "$FF_RUNS"/*/; do
    [ -d "$d" ] || continue
    name="$(basename "$d")"
    [[ "$name" =~ $FF_RUN_ID_PATTERN ]] || continue
    any=1
    verdict="$(classify_run_dir "${d%/}")"
    case "$verdict" in
      OK)
        pass "stray-run-dir:$name genuinely complete (arm.json present, every model step's read-back evidence is consistent)"
        ;;
      PARTIAL)
        fail "stray-run-dir:$name" "partial run directory -- no arm.json; derive.py would still enumerate it as a row and default it to void"
        ;;
      CORRUPTED:*)
        fail "stray-run-dir:$name" "complete-looking but corrupted -- step ${verdict#CORRUPTED:} reports exit_code 0 with every read-back field null and no stream.jsonl on disk"
        ;;
      *)
        fail "stray-run-dir:$name" "classifier produced an unrecognised verdict: $verdict"
        ;;
    esac
  done
  [ "$any" -eq 1 ] || fail "stray-run-dirs" "no run-id-shaped directory found under $FF_RUNS -- expected at least the 3 committed rows"
}

# ============================================================================
# check 6 — bash -n and python3 -m py_compile over the rig's own files
# ============================================================================

check_syntax() {
  local f out rc
  for f in "$REPO_ROOT/rig/run.sh" "$REPO_ROOT/rig/run-pipeline.sh" "$REPO_ROOT/rig/check.sh"; do
    set +e
    out="$(bash -n "$f" 2>&1)"
    rc=$?
    set -e
    if [ "$rc" -eq 0 ]; then
      pass "syntax:bash -n $(basename "$f")"
    else
      fail "syntax:bash -n $(basename "$f")" "$out"
    fi
  done
  for f in "$REPO_ROOT/rig/collect.py" "$REPO_ROOT/rig/derive.py" "$REPO_ROOT/rig/report.py" \
    "$REPO_ROOT/rig/fixtures/failure-flood/v2/tools/generate-cases.py" \
    "$REPO_ROOT/rig/fixtures/failure-flood/v2/tools/axis_table.py"; do
    [ -f "$f" ] || continue
    set +e
    out="$(python3 -m py_compile "$f" 2>&1)"
    rc=$?
    set -e
    if [ "$rc" -eq 0 ]; then
      pass "syntax:py_compile $(basename "$f")"
    else
      fail "syntax:py_compile $(basename "$f")" "$out"
    fi
  done
}

# ============================================================================
# self-test (ADR 0013) — this gate's own classifiers, synthetic input only
# ============================================================================

self_test() {
  local tmp failed=0
  tmp="$(mktemp -d)" || die_cannot_run "could not create a temporary directory"
  # NOT `trap ... EXIT`: that fires when the whole script exits, by which
  # point this function's `local tmp` is out of scope again and `set -u`
  # turns the reference into "tmp: unbound variable", clobbering an
  # otherwise-passing self-test's own exit code. Clean up explicitly on
  # every return path instead.

  expect() {
    # $1 expected  $2 got  $3 label
    if [ "$1" = "$2" ]; then
      printf '  [PASS] %s\n' "$3"
    else
      printf '  [FAIL] %s -- expected %s, got %s\n' "$3" "$1" "$2" >&2
      failed=1
    fi
  }

  # -- classify_manifest -------------------------------------------------
  expect PASS "$(classify_manifest 'a b' 'a b')" "classify_manifest: identical digests pass"
  expect FAIL "$(classify_manifest 'a b' 'a c')" "classify_manifest: differing digests fail"

  # -- compute_manifest() itself, via a synthetic fixture (also proves the
  # extraction from rig/run-pipeline.sh actually loaded a working function)
  mkdir -p "$tmp/fixture/src"
  printf 'original\n' >"$tmp/fixture/src/a.ts"
  local m1 m2
  m1="$(compute_manifest "$tmp/fixture")"
  printf 'original\n' >"$tmp/fixture/MANIFEST.sha256.tmp" # unrelated file, not under a covered subdir
  m2="$(compute_manifest "$tmp/fixture")"
  expect "$m1" "$m2" "compute_manifest: an uncovered top-level file does not change the digest"
  printf 'changed\n' >"$tmp/fixture/src/a.ts"
  local m3
  m3="$(compute_manifest "$tmp/fixture")"
  if [ "$m1" != "$m3" ]; then
    printf '  [PASS] %s\n' "compute_manifest: editing a covered file changes the digest (CRITICAL-6's own shape)"
  else
    printf '  [FAIL] %s\n' "compute_manifest: editing a covered file did NOT change the digest" >&2
    failed=1
  fi
  rm -rf "$tmp/fixture"

  # -- classify_preflight_v1 ----------------------------------------------
  expect PASS "$(classify_preflight_v1 2 'missing-prereg-config: no prereg.json' 3 3)" \
    "classify_preflight_v1: exit 2 + expected message + stable dir count passes"
  expect FAIL "$(classify_preflight_v1 2 'MANIFEST.sha256 mismatch' 3 3)" \
    "classify_preflight_v1: a manifest-mismatch message fails even at exit 2"
  expect FAIL "$(classify_preflight_v1 0 'missing-prereg-config' 3 3)" \
    "classify_preflight_v1: exit 0 fails regardless of message"
  expect FAIL "$(classify_preflight_v1 2 'missing-prereg-config' 3 4)" \
    "classify_preflight_v1: a new run directory (count changed) fails"

  # -- classify_preflight_v2 ----------------------------------------------
  expect PASS "$(classify_preflight_v2 0 'run s2-pipeline-9054 already void -- skipping (idempotent)' 3 3)" \
    "classify_preflight_v2: exit 0 + idempotent-skip message + stable dir count passes"
  expect FAIL "$(classify_preflight_v2 0 'MANIFEST.sha256 mismatch' 3 3)" \
    "classify_preflight_v2: a manifest-mismatch message fails even at exit 0"
  expect FAIL "$(classify_preflight_v2 2 'run s2-pipeline-9054 already void -- skipping (idempotent)' 3 3)" \
    "classify_preflight_v2: a non-zero exit fails regardless of message"
  expect FAIL "$(classify_preflight_v2 0 'run s2-pipeline-9054 already void -- skipping (idempotent)' 3 4)" \
    "classify_preflight_v2: a new run directory (count changed) fails"

  # -- classify_run_dir -----------------------------------------------------
  mkdir -p "$tmp/runs/s1-monolithic-01/steps/01-monolith"
  cat >"$tmp/runs/s1-monolithic-01/arm.json" <<'JSON'
{"steps": [{"index": "01-monolith", "kind": "model", "exit_code": 0,
            "permission_mode_actual": "bypassPermissions",
            "surface_sha256": "deadbeef"}]}
JSON
  printf '{}\n' >"$tmp/runs/s1-monolithic-01/steps/01-monolith/stream.jsonl"
  expect OK "$(classify_run_dir "$tmp/runs/s1-monolithic-01")" \
    "classify_run_dir: a genuinely complete directory is OK"

  mkdir -p "$tmp/runs/s1-monolithic-02"
  expect PARTIAL "$(classify_run_dir "$tmp/runs/s1-monolithic-02")" \
    "classify_run_dir: a directory with no arm.json is PARTIAL"

  mkdir -p "$tmp/runs/s2-pipeline-03/steps/03-apply"
  cat >"$tmp/runs/s2-pipeline-03/arm.json" <<'JSON'
{"steps": [{"index": "03-apply", "kind": "model", "exit_code": 0,
            "permission_mode_actual": null, "surface_sha256": null}]}
JSON
  # deliberately no stream.jsonl -- the reproduced live shape
  expect "CORRUPTED:03-apply" "$(classify_run_dir "$tmp/runs/s2-pipeline-03")" \
    "classify_run_dir: exit_code 0 + null read-back + no stream.jsonl is CORRUPTED"

  rm -rf "$tmp"

  if [ "$failed" -eq 0 ]; then
    printf '\n  self-test: all cases passed\n'
    return 0
  fi
  printf '\n  SELF-TEST FAILED -- rig/check.sh is not behaving as specified.\n' >&2
  return 1
}

# ============================================================================
# entry point
# ============================================================================

case "${1:-}" in
  "") : ;;
  --help) show_help; exit 0 ;;
  --self-test)
    self_test
    exit $?
    ;;
  *) die_cannot_run "unknown argument '$1'. Use no argument, --self-test, or --help." ;;
esac

check_manifest "$FF_V1" v1
check_manifest "$FF_V2" v2
check_component_self_test derive.py
check_component_self_test report.py
check_component_self_test collect.py
check_preflight_v1
check_preflight_v2
check_derive_reproducible tool-surface-v1
check_derive_reproducible failure-flood-v1
check_stray_run_dirs
check_syntax

if [ "$CHECKS_FAILED" -gt 0 ]; then
  printf '\n  rig/check.sh: %s/%s check(s) failed.\n' "$CHECKS_FAILED" "$CHECKS_RUN" >&2
  exit 1
fi
printf '\n  rig/check.sh: %s/%s check(s) passed.\n' "$CHECKS_RUN" "$CHECKS_RUN"
exit 0
