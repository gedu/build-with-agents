#!/usr/bin/env bash
#
# rig/run-pipeline.sh — multi-step arm driver for the failure-flood-triage
# experiment (spec R-F6.4, design.md secs 2/5/7). Sibling to rig/run.sh
# (R-F6.4: "rig/run.sh MUST NOT be refactored... refactoring risks
# invalidating that verification") — a fresh script, duplicating only what
# it must (dirty-tree guard, manifest recompute-compare, the sha256-
# combining hash convention, the mkdir-is-the-lock idempotence pattern).
#
# THIS UNIT'S SCOPE (tasks.md PR5, tasks 5.1/5.2/5.3/5.4/5.4b/5.5/5.6 ONLY).
# NOT built here, named so a gap is never mistaken for an oversight:
#   - 5.7: the real --shakedown shakedown run. Not performed by this apply.
#   - 5.8: derive.py's --experiment dispatcher. This file writes raw
#     per-run/per-step artifacts only, never a runs.jsonl row. No
#     `prompt_sha256` field is written to status.json either — R-F7.1's
#     "hash of each role's exact prompt bytes" is satisfiable from the
#     already-committed `rig/surfaces/failure-flood.txt` digest convention
#     applied to the prompt file, but wiring that recording is 5.8's own
#     row-builder concern, not this unit's.
#   - 5.4 (DONE): rig/surfaces/failure-flood.txt captured twice
#     from a real, non-nested `claude -p` invocation, compared byte-for-byte,
#     committed. See apply-progress.md's "PR5b" section for both digests.
#   - 5.4b (DONE): prompts/s1.txt and prompts/s2.txt created under
#     both fixtures — the design.md-vs-disk gap task 3.5 first found for
#     v1's tools/ row (tasks.md:482-494) and this file's own prior revision
#     flagged again for prompts/ is now closed. Both files are covered by
#     compute_manifest()'s "prompts" subdirectory (added this unit) and are
#     loaded per task_id, never per role — see run_model_step()'s own
#     comment for why one file must serve every role in both arms.
#   - 5.5 (DONE this unit): the diagnostician-writes-to-src violation now
#     classifies arm state (see the "read-only substrate / diagnostician-
#     writes-to-src" classification block near the bottom of this file).
#     A REAL BUG WAS FOUND AND FIXED, live, before 5.5 could be built at
#     all: `hash_paths()`'s own `python3 - "$1" <<'PY' ... PY` invocation
#     redirects the python3 process's stdin to the heredoc (its own source
#     text), which silently discards whatever the CALLER piped in
#     (`printf '%s\n' "$paths" | hash_paths "$ws"`) — `sys.stdin` inside the
#     running script hits EOF immediately, so every call hashed an EMPTY
#     file list. This exactly explains PR5b's flagged anomaly
#     (`substrate_changed: false` on the s1 monolith step despite the
#     model's own transcript showing three real `Edit` calls under `src/`
#     and `npm test` flipping from 4 failed to 36 passed). Reproduced
#     standalone (`READ_COUNT=0` printed from inside the script) before
#     touching any fixture-facing code, then fixed by moving the piped
#     path list off stdin and into an env var (`HASH_PATHS_INPUT="$(cat)"`
#     prefixed onto the python3 invocation), re-tested standalone
#     (`READ_COUNT=1`, a real byte edit now flips the digest), see
#     apply-progress.md's "PR5c" section for both raw transcripts.
#
# EXIT CODES (house convention, matching rig/run.sh's own comment block):
#   0  the arm reached `complete` or `void` (a designed outcome, never a
#      failure).
#   1  the arm reached `failed` — an assertion fired: `tests/`/`runtime/`
#      (the read-only substrate, plus generated `cases/`, design.md 9a)
#      mutated by any step, or the diagnostician (the `diagnose` role) wrote
#      to `src/` (task 5.5; design.md sec 2: "the violation is detected:
#      the diagnostician's workspace is re-hashed against its materialised
#      file list, and any change to src/ sets arm state failed, not void").
#   2  could not run at all: bad arguments, a missing prerequisite (node,
#      npm below floor, a missing prompt or surface preimage), a dirty tree,
#      a MANIFEST mismatch, a case-table digest mismatch, a failed `npm ci`,
#      a missing/failed pre-registration check, or no --permission-mode.
#
# status.json (per step) and arm.json + the arm-level status.json are
# flushed before every exit path reachable AFTER the run directory is
# claimed (Amendment 1). A pre-flight refusal (before the run directory is
# claimed) writes nothing — same as rig/run.sh's own die_cannot_run.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPERIMENT="failure-flood-v1"
RUNS_ROOT="$REPO_ROOT/rig/runs/$EXPERIMENT"
SURFACES_ROOT="$REPO_ROOT/rig/surfaces"
SURFACE_FILE="$SURFACES_ROOT/failure-flood.txt"

# Node major-version floor: jest@29.7.0's `engines` field is documented as
# "^14.15.0 || ^16.10.0 || >=18.0.0"; 18 satisfies that outright. Not
# measured from an installed node_modules — never committed, ADR 0014 A.
NODE_FLOOR_MAJOR=18

# Per-step timeout, and the suite-collection timeout nested inside a code
# step's collect.py call — R-F9.2/design.md 9b: the suite timeout must be
# separate from, and smaller than, the arm's; collect.py "can only enforce
# the value it is given" (--help). Both PLACEHOLDERS pending task 5.7's real
# wall-clock measurement (not run by this unit) — rig/run.sh:59-67's own
# TIMEOUT_S derivation precedent ("re-derive it, do not nudge it").
STEP_TIMEOUT_S=180
SUITE_TIMEOUT_S=150
if [ "$SUITE_TIMEOUT_S" -ge "$STEP_TIMEOUT_S" ]; then
  printf 'BUG: SUITE_TIMEOUT_S (%s) must be strictly smaller than STEP_TIMEOUT_S (%s) — design.md 9b.\n' \
    "$SUITE_TIMEOUT_S" "$STEP_TIMEOUT_S" >&2
  exit 2
fi

# `claude --help`'s own --permission-mode enum, quoted verbatim: "choices:
# \"acceptEdits\", \"auto\", \"bypassPermissions\", \"manual\", \"dontAsk\", \"plan\"".
PERMISSION_MODE_CHOICES="acceptEdits auto bypassPermissions manual dontAsk plan"

usage() {
  cat <<'USAGE'
Usage: rig/run-pipeline.sh <task_id> <arm> <iteration> --permission-mode <mode> [--shakedown] [--dirty-ok]

  task_id            s1 (failure-flood/v1, stage 1) | s2 (failure-flood/v2, stage 2)
  arm                monolithic | pipeline
  iteration          an iteration slot, e.g. 03, or a void re-run suffix, e.g. 03r1
  --permission-mode  REQUIRED, never inherited (R-F7.4). One of:
                     acceptEdits, auto, bypassPermissions, manual, dontAsk, plan
  --shakedown        stamps void_reason=shakedown UNCONDITIONALLY on the arm-level
                     row (Hard Ordering Gate layer 1) and skips the pre-registration
                     preflight (layer 2). Distinct from --dirty-ok (R-F8.2).
  --dirty-ok         bypass the dirty-tree guard. Does not itself produce a
                     countable row, and does not imply --shakedown.

Guards, launches ONE multi-step arm, and persists its artifacts under
rig/runs/failure-flood-v1/<run_id>/. rig/run.sh is untouched (R-F6.4) — this
is its sibling for the multi-invocation pipeline.
USAGE
}

warn() { printf '  !! %s\n' "$1" >&2; }
die_bad_args() { warn "$1"; usage >&2; exit 2; }
die_cannot_run() { printf '\n  COULD NOT RUN: %s\n  This is exit 2, not a pass.\n' "$1" >&2; exit 2; }
now_ms() { python3 -c 'import time; print(int(time.time() * 1000))'; }

# compute_manifest <fixture-root> — sorted "sha256  relpath" over src/,
# tests/, runtime/, tools/, answer-key/, prompts/. Adapted from
# rig/run.sh:154-171.
# CORRECTED BY LIVE MEASUREMENT: task 3.5's done-note (tasks.md:448-450)
# describes the path set as "…, answer-key/case-table.sha256" (one file) —
# true only at THAT task's own moment, before 4.2/4.4 added
# answer-key/s1.json, s2.json, prereg.json. A first version of this function
# walked only that single file and its live recompute-compare against the
# real committed v2/MANIFEST.sha256 mismatched by exactly those 2 lines.
# Walking the whole answer-key/ directory (like src/tests/runtime/tools)
# matches the actual committed manifests for both v1 and v2 — verified live.
# Skips __pycache__/*.pyc under tools/ (task 3.5's hazard finding).
# SECOND CORRECTION (task 5.4b): "prompts" added to this tuple. Design.md 9a
# groups prompts/ with tools/ and answer-key/ as "never-materialised" but
# manifest-covered — the generator/checker/prompt bytes must all be frozen
# and tamper-detected the same way, even though only prompts/ is excluded
# from manifest_workspace_paths() below (never copied into a step's
# workspace). Omitting it here would leave prompts/s1.txt and
# prompts/s2.txt uncovered by the MANIFEST.sha256 recompute-compare gate —
# exactly the class of hole design.md 9a exists to close for tools/ and
# answer-key/.
compute_manifest() {
  python3 - "$1" <<'PY'
import hashlib, pathlib, sys

root = pathlib.Path(sys.argv[1])
lines = []
for sub in ("src", "tests", "runtime", "tools", "answer-key", "prompts"):
    d = root / sub
    if not d.is_dir():
        continue
    for p in sorted(d.rglob("*")):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        rel = p.relative_to(root).as_posix()
        lines.append((rel, f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}"))
lines.sort(key=lambda t: t[0])
print("\n".join(l for _, l in lines))
PY
}

# manifest_workspace_paths <fixture-root> — relpaths under src/, tests/,
# runtime/ ONLY (never tools/ or answer-key/, "NEVER materialised" per
# design.md 9a), derived from compute_manifest()'s own output — NEVER a
# directory walk (task 5.6; rig/run.sh:147's `find . -type f` would descend
# node_modules once the per-run install symlink exists).
manifest_workspace_paths() {
  compute_manifest "$1" | awk '{print $2}' | grep -E '^(src|tests|runtime)/' | sort
}

# hash_paths <workspace-root> — one sha256 over exactly the explicit relpath
# list piped in on stdin, one per line — never a fresh directory listing.
# Identical combining convention to rig/run.sh:122-141's hash_fixture_files
# and rig/fixtures/failure-flood/v2/tools/generate-cases.py's
# case_table_digest (task 3.4's own done-note, tasks.md:427: "reused, not
# invented, so a future consumer... has one digest-of-a-file-set convention
# to implement, not two").
#
# REAL BUG FOUND AND FIXED (task 5.5): the path list MUST NOT be read via
# `sys.stdin` inside a `python3 - <<'PY'` invocation — the heredoc IS that
# process's stdin (it is how `-` receives the script source itself), so it
# silently overrides whatever the caller piped in and `sys.stdin` inside the
# running script hits EOF immediately, hashing an empty list every time.
# Reproduced standalone before this fix (`READ_COUNT=0` regardless of what
# was piped in) — this is the exact, previously-unexplained cause of PR5b's
# flagged anomaly (`substrate_changed: false` on a step whose own transcript
# shows three real `src/` edits and a suite flipping from 4 failed to 36
# passed). Fixed by taking the path list off stdin entirely, into an env var
# consumed by name (`os.environ["HASH_PATHS_INPUT"]`) — `python3`'s own
# stdin stays bound to the heredoc, and the caller's pipe is read by `cat`
# in the same command, never by the python process. See apply-progress.md's
# "PR5c" section for both the broken and fixed standalone reproductions.
hash_paths() {
  HASH_PATHS_INPUT="$(cat)" python3 - "$1" <<'PY'
import hashlib, os, pathlib, sys

root = pathlib.Path(sys.argv[1])
lines = []
for rel in sorted(l.strip() for l in os.environ["HASH_PATHS_INPUT"].splitlines() if l.strip()):
    p = root / rel
    try:
        content = p.read_bytes()
    except FileNotFoundError:
        content = b"<missing>"
    lines.append(f"{hashlib.sha256(content).hexdigest()}  {rel}")
print(hashlib.sha256("\n".join(lines).encode()).hexdigest())
PY
}

# check_prereg <fixture-root> — Hard Ordering Gate layer 2
# (answer-key/prereg.json's `check` block, task 4.4). Prints prereg_digest
# and exits 0 on pass; prints the EXACT prereg.json-named reason to stderr
# and exits 2 on any violation.
check_prereg() {
  python3 - "$1" "$REPO_ROOT" <<'PY'
import hashlib, json, pathlib, subprocess, sys

fixture_root, repo_root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
prereg_path = fixture_root / "answer-key" / "prereg.json"
if not prereg_path.is_file():
    print(f"missing-prereg-config: no {prereg_path} exists — non-shakedown "
          f"invocations require a pre-registration file to check against "
          f"(Hard Ordering Gate layer 2); this fixture version has none by "
          f"design (prereg.json's own scope block: task_id s1/v1 is "
          f"structurally always invoked with --shakedown)", file=sys.stderr)
    sys.exit(2)

spec = json.loads(prereg_path.read_text())
digest_input = []
for entry in spec["required_hypotheses"]:
    glob = entry["path_glob"]
    matches = sorted(repo_root.glob(glob))
    if len(matches) == 0:
        print(f"zero_matches: {glob}", file=sys.stderr)
        sys.exit(2)
    if len(matches) > 1:
        print(f"more_than_one_match: {glob} -> {[str(m) for m in matches]}", file=sys.stderr)
        sys.exit(2)
    match = matches[0]
    rel = match.relative_to(repo_root).as_posix()
    tracked = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "--error-unmatch", rel],
        capture_output=True,
    ).returncode == 0
    if not tracked:
        print(f"untracked: {rel}", file=sys.stderr)
        sys.exit(2)
    dirty = subprocess.run(
        ["git", "-C", str(repo_root), "status", "--porcelain", "--", rel],
        capture_output=True, text=True,
    ).stdout.strip()
    if dirty:
        print(f"tracked_but_dirty: {rel}", file=sys.stderr)
        sys.exit(2)
    digest_input.append(f"{hashlib.sha256(match.read_bytes()).hexdigest()}  {rel}")

print(hashlib.sha256("\n".join(sorted(digest_input)).encode()).hexdigest())
PY
}

# read_back_init <stream.jsonl> — prints "<surface_sha256> <permission_mode>"
# (empty fields when no init event was emitted). surface_sha256 reuses
# rig/derive.py:87-91's surface_digest() convention exactly:
# sha256(sorted(set(tool_names))), so task 5.8's row builder can compare it
# to rig/surfaces/failure-flood.txt without a second algorithm. This file
# RECORDS the comparison inputs; it does not decide surface-mismatch itself
# — every existing precedent (rig/derive.py:456-464, never rig/run.sh) puts
# that decision in derive.py, so failure-flood-v1 keeps the same split.
read_back_init() {
  python3 - "$1" <<'PY'
import hashlib, json, sys

path = sys.argv[1]
tools, mode = [], ""
try:
    with open(path, "rb") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except Exception:
                continue
            if ev.get("type") == "system" and ev.get("subtype") == "init":
                tools = ev.get("tools", [])
                mode = ev.get("permissionMode", "")
                break
except FileNotFoundError:
    pass
digest = hashlib.sha256("\n".join(sorted(set(tools))).encode()).hexdigest() if tools else ""
print(f"{digest} {mode}")
PY
}

# ---- argument parsing -------------------------------------------------

SHAKEDOWN=0
DIRTY_OK=0
PERMISSION_MODE=""
POSITIONAL=()
while [ $# -gt 0 ]; do
  case "$1" in
    --shakedown) SHAKEDOWN=1; shift ;;
    --dirty-ok) DIRTY_OK=1; shift ;;
    --permission-mode)
      [ $# -ge 2 ] || die_bad_args "--permission-mode requires a value"
      PERMISSION_MODE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --*) die_bad_args "unknown flag '$1'" ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

[ "${#POSITIONAL[@]}" -eq 3 ] || die_bad_args "expected 3 positional arguments (task_id arm iteration), got ${#POSITIONAL[@]}"
TASK_ID="${POSITIONAL[0]}"; ARM="${POSITIONAL[1]}"; ITERATION="${POSITIONAL[2]}"

case "$TASK_ID" in s1|s2) ;; *) die_bad_args "task_id must be s1 or s2 — got '$TASK_ID'" ;; esac
case "$ARM" in monolithic|pipeline) ;; *) die_bad_args "arm must be monolithic or pipeline — got '$ARM'" ;; esac
case "$ITERATION" in [0-9]*) ;; *) die_bad_args "iteration must start with a digit (e.g. 03, or 03r1 for a void re-run) — got '$ITERATION'" ;; esac
case "$ITERATION" in *[!a-zA-Z0-9]*) die_bad_args "iteration must be alphanumeric only — got '$ITERATION'" ;; esac

# R-F7.4: permission_mode is a named argument, never inherited, no default.
[ -n "$PERMISSION_MODE" ] || die_bad_args "--permission-mode is required (R-F7.4) — one of: $PERMISSION_MODE_CHOICES"
case " $PERMISSION_MODE_CHOICES " in
  *" $PERMISSION_MODE "*) ;;
  *) die_bad_args "--permission-mode must be one of: $PERMISSION_MODE_CHOICES — got '$PERMISSION_MODE'" ;;
esac

RUN_ID="${TASK_ID}-${ARM}-${ITERATION}"

case "$TASK_ID" in
  s1) FIXTURE_VERSION="v1" ;;
  s2) FIXTURE_VERSION="v2" ;;
esac
FIXTURE_ROOT="$REPO_ROOT/rig/fixtures/failure-flood/$FIXTURE_VERSION"

case "$ARM" in
  monolithic) STEPS=(01-monolith:model 99-verify:code) ;;
  pipeline)   STEPS=(01-collect:code 02-diagnose:model 03-apply:model 99-verify:code) ;;
esac

# ---- prerequisite checks (exit 2) --------------------------------------

command -v python3 >/dev/null 2>&1 || die_cannot_run "python3 is missing (rig-only prerequisite, decisions/0011)."
command -v timeout >/dev/null 2>&1 || die_cannot_run "'timeout' is missing (GNU coreutils on macOS: brew install coreutils)."
command -v claude >/dev/null 2>&1 || die_cannot_run "'claude' CLI is missing from PATH."
command -v node >/dev/null 2>&1 || die_cannot_run "'node' is missing — fixture toolchain prerequisite (design.md sec 5)."
command -v npm >/dev/null 2>&1 || die_cannot_run "'npm' is missing — fixture toolchain prerequisite (design.md sec 5)."

NODE_VERSION="$(node --version)"
NPM_VERSION="$(npm --version)"
NODE_MAJOR="$(printf '%s' "$NODE_VERSION" | sed -E 's/^v?([0-9]+).*/\1/')"
[ "$NODE_MAJOR" -ge "$NODE_FLOOR_MAJOR" ] || die_cannot_run "node major version $NODE_MAJOR is below the declared floor $NODE_FLOOR_MAJOR ($NODE_VERSION) — design.md sec 5"

DRIVER_VERSION="$(claude --version 2>/dev/null || echo unknown)"
PYTHON_VERSION="$(python3 --version 2>&1)"

# ---- dirty-tree guard ---------------------------------------------------
# Scoped to rig/, same as rig/run.sh:277-289 and for the same reason
# ("enumerating each path by hand would silently miss a future addition").

DIRTY="$(git -C "$REPO_ROOT" status --porcelain -- rig)"
if [ -n "$DIRTY" ] && [ "$DIRTY_OK" -ne 1 ]; then
  die_cannot_run "the tree is dirty under rig/ (staged or unstaged). Re-run with --dirty-ok, or commit/stash first:
$DIRTY"
fi
CODE_COMMIT="$(git -C "$REPO_ROOT" rev-parse HEAD)"
[ "$DIRTY_OK" -eq 1 ] && [ -n "$DIRTY" ] && CODE_COMMIT="${CODE_COMMIT}-dirty"

# ---- MANIFEST recompute-compare -----------------------------------------

MANIFEST_FILE="$FIXTURE_ROOT/MANIFEST.sha256"
[ -f "$MANIFEST_FILE" ] || die_cannot_run "missing $MANIFEST_FILE — freeze the fixture before running."
COMPUTED_MANIFEST="$(compute_manifest "$FIXTURE_ROOT")"
COMMITTED_MANIFEST="$(cat "$MANIFEST_FILE")"
if [ "$COMPUTED_MANIFEST" != "$COMMITTED_MANIFEST" ]; then
  die_cannot_run "MANIFEST.sha256 mismatch under $FIXTURE_ROOT — refusing to run against a tampered or edited fixture."
fi

# ---- Hard Ordering Gate, layer 2 (pre-registration) ---------------------
# tasks.md "Hard Ordering Gate": "Preflight refuses (exit 2)... any
# non-shakedown invocation unless hypotheses/0002-*.md and hypotheses/0003-*.md
# exist, are git-tracked, and are clean". Skipped entirely under --shakedown
# (layer 1 below supersedes it unconditionally regardless).

PREREG_DIGEST=""
if [ "$SHAKEDOWN" -ne 1 ]; then
  PREREG_STDERR="$(mktemp)"
  if ! PREREG_DIGEST="$(check_prereg "$FIXTURE_ROOT" 2>"$PREREG_STDERR")"; then
    REASON="$(cat "$PREREG_STDERR")"
    rm -f "$PREREG_STDERR"
    die_cannot_run "pre-registration guard failed (Hard Ordering Gate layer 2): $REASON"
  fi
  rm -f "$PREREG_STDERR"
fi

# ---- per-run setup: install, case generation, case-table digest --------
# design.md data flow: "per-run root... npm ci... tools/generate-cases.py
# -> cases/ -> digest vs answer-key/case-table.sha256 -> exit 2" — after the
# preflight above, before any run directory is claimed.

PER_RUN_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/rig-ff-run.XXXXXX")"
INSTALL_DIR="$PER_RUN_ROOT/install"
mkdir -p "$INSTALL_DIR"
cp "$FIXTURE_ROOT/runtime/package.json" "$FIXTURE_ROOT/runtime/package-lock.json" "$INSTALL_DIR/"
LOCKFILE_SHA256="$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$FIXTURE_ROOT/runtime/package-lock.json")"
# `npm ci --prefix <dir>` != `cd <dir> && npm ci` — measured live: --prefix
# resolves the root package against the CALLER's cwd while installing into
# <dir>/node_modules, so it failed EUSAGE against <repo>'s own (absent)
# package.json. `cd` first, matching the committed `npm test` convention.
if ! ( cd "$INSTALL_DIR" && npm ci --silent >"$PER_RUN_ROOT/npm-ci.log" 2>&1 ); then
  cat "$PER_RUN_ROOT/npm-ci.log" >&2
  die_cannot_run "npm ci failed under $INSTALL_DIR — package.json/lockfile mismatch is the reproducibility check (design.md sec 5)"
fi

CASE_TABLE_DIGEST=""
CASE_COUNT=0
CASE_NAMES=()
if [ "$FIXTURE_VERSION" = "v2" ]; then
  if ! GEN_OUT="$(python3 "$FIXTURE_ROOT/tools/generate-cases.py" --out-dir "$PER_RUN_ROOT" 2>"$PER_RUN_ROOT/gen.err")"; then
    cat "$PER_RUN_ROOT/gen.err" >&2
    die_cannot_run "tools/generate-cases.py failed under $PER_RUN_ROOT"
  fi
  CASE_TABLE_DIGEST="$(printf '%s\n' "$GEN_OUT" | sed -n 's/^case_table_digest: //p')"
  [ -n "$CASE_TABLE_DIGEST" ] || die_cannot_run "tools/generate-cases.py printed no case_table_digest line — cannot verify the freeze"
  EXPECTED_DIGEST="$(cat "$FIXTURE_ROOT/answer-key/case-table.sha256")"
  if [ "$CASE_TABLE_DIGEST" != "$EXPECTED_DIGEST" ]; then
    die_cannot_run "case-table digest mismatch: generated $CASE_TABLE_DIGEST != committed $EXPECTED_DIGEST ($FIXTURE_ROOT/answer-key/case-table.sha256)"
  fi
  while IFS= read -r name; do CASE_NAMES+=("$name"); done < <(printf '%s\n' "$GEN_OUT" | sed -n 's/^  \([A-Za-z0-9_]*\):.*/\1/p' | sort)
  CASE_COUNT="$(printf '%s\n' "$GEN_OUT" | sed -n 's/^generate-cases\.py: wrote [0-9]* case tables, \([0-9]*\) total cases.*/\1/p')"
fi

# ---- the hashed file list (task 5.6) ------------------------------------
# The manifest's own path set (src/, tests/, runtime/ only — tools/ and
# answer-key/ are never materialised, design.md 9a) plus the generated case
# paths, captured here — before the per-run install's node_modules symlink
# is created in any per-step workspace below. Never a directory walk.

WORKSPACE_PATHS="$(manifest_workspace_paths "$FIXTURE_ROOT")"
for name in "${CASE_NAMES[@]+"${CASE_NAMES[@]}"}"; do
  WORKSPACE_PATHS="$WORKSPACE_PATHS
cases/${name}.json"
done
WORKSPACE_PATHS="$(printf '%s\n' "$WORKSPACE_PATHS" | sed '/^$/d' | sort)"
WORKSPACE_FILE_COUNT="$(printf '%s\n' "$WORKSPACE_PATHS" | wc -l | tr -d ' ')"

# ---- the two zones the re-hash instrument classifies (task 5.5) ---------
# design.md sec 2 / design.md 9a: `src/` is writable (the applier's and
# MONOLITHIC's whole job); `tests/`, `runtime/` and generated `cases/` are
# read-only substrate for every role, in every step. Split from the same
# WORKSPACE_PATHS list above — never a second directory walk — so a change
# can be classified by WHERE it landed, not just THAT something changed.
SRC_PATHS="$(printf '%s\n' "$WORKSPACE_PATHS" | grep -E '^src/' || true)"
RO_PATHS="$(printf '%s\n' "$WORKSPACE_PATHS" | grep -vE '^src/' || true)"

# ---- claim the run directory (mkdir is the lock, rig/run.sh's Decision 6) -

mkdir -p "$RUNS_ROOT"
RUN_DIR="$RUNS_ROOT/$RUN_ID"
if ! mkdir "$RUN_DIR" 2>/dev/null; then
  if [ -f "$RUN_DIR/status.json" ]; then
    PRIOR_STATE="$(python3 -c 'import json,sys
print(json.load(open(sys.argv[1])).get("state","unknown"))' "$RUN_DIR/status.json" 2>/dev/null || echo unknown)"
    case "$PRIOR_STATE" in
      complete|void)
        echo "  run $RUN_ID already $PRIOR_STATE — skipping (idempotent). Use a new iteration suffix (e.g. ${ITERATION}r1) to retry."
        exit 0
        ;;
      *)
        die_cannot_run "run $RUN_ID exists with status.json state '$PRIOR_STATE' (expected complete or void). Inspect $RUN_DIR by hand."
        ;;
    esac
  else
    ORPHAN="${RUN_DIR}.orphan.$(python3 -c 'import time; print(int(time.time()))')"
    mv "$RUN_DIR" "$ORPHAN"
    echo "  moved incomplete run dir aside: ${ORPHAN#"$REPO_ROOT"/}"
    mkdir "$RUN_DIR" || die_cannot_run "could not create $RUN_DIR even after orphaning the previous attempt"
  fi
fi
mkdir -p "$RUN_DIR/steps"

# ---- materialize (task 5.2) ---------------------------------------------
# Fresh workspace per step: src/ + tests/ + runtime/ copied, node_modules
# symlinked to the per-run, machine-local install directory (never the
# committed tree — design.md sec 5's cheat-vector row), cases/ copied in for
# v2. tools/, answer-key/ and prompts/ are never copied into a workspace
# (design.md 9a; prompts are read directly by invoke() below, not shipped
# into the agent's own materialised tree).

materialize_step() {
  local ws
  ws="$(mktemp -d "${TMPDIR:-/tmp}/rig-ff-ws.XXXXXX")"
  cp -R "$FIXTURE_ROOT/src" "$ws/src"
  cp -R "$FIXTURE_ROOT/tests" "$ws/tests"
  cp -R "$FIXTURE_ROOT/runtime" "$ws/runtime"
  rm -f "$ws/runtime/node_modules"
  ln -s "$INSTALL_DIR/node_modules" "$ws/runtime/node_modules"
  if [ "$FIXTURE_VERSION" = "v2" ]; then
    mkdir -p "$ws/cases"
    cp "$PER_RUN_ROOT"/cases/*.json "$ws/cases/" 2>/dev/null || true
  fi
  printf '%s' "$ws"
}

write_step_status() {
  # $1 dir  $2 role  $3 kind  $4 exit_code  $5 wall_ms  $6 substrate_changed
  # $7 surface_sha256  $8 permission_mode_actual  $9 timed_out
  # $10 src_changed  $11 ro_changed (task 5.5 — the two zones the arm-level
  # classification reads; substrate_changed stays the OR of both, unchanged
  # shape, for anything already reading that one field)
  ROLE="$2" KIND="$3" EXIT_CODE="$4" WALL_MS="$5" SUBSTRATE_CHANGED="$6" \
  SURFACE_SHA256="$7" PERMISSION_MODE_ACTUAL="$8" TIMED_OUT="${9:-0}" \
  SRC_CHANGED="${10:-0}" RO_CHANGED="${11:-0}" \
  DECLARED_PERMISSION_MODE="$PERMISSION_MODE" STATUS_FILE="$1/status.json" \
  python3 <<'PY'
import json, os

env = os.environ
actual = env["PERMISSION_MODE_ACTUAL"] or None
data = {
    "role": env["ROLE"],
    "kind": env["KIND"],
    "exit_code": int(env["EXIT_CODE"]),
    "wall_ms": int(env["WALL_MS"]),
    "timed_out": env["TIMED_OUT"] == "1",
    # substrate_changed is the OR of the two zones below — kept for anything
    # already reading this one field. Role-aware classification (task 5.5)
    # reads src_changed/ro_changed, never this combined bit, because src/
    # changing is legitimate for the applier and MONOLITHIC and illegitimate
    # only for the diagnostician.
    "substrate_changed": env["SUBSTRATE_CHANGED"] == "1",
    "src_changed": env["SRC_CHANGED"] == "1",
    "ro_changed": env["RO_CHANGED"] == "1",
    "surface_sha256": env["SURFACE_SHA256"] or None,
    "declared_permission_mode": env["DECLARED_PERMISSION_MODE"],
    "permission_mode_actual": actual,
    "permission_mode_matches_declared": (actual == env["DECLARED_PERMISSION_MODE"]) if actual else None,
}
with open(env["STATUS_FILE"], "w") as f:
    json.dump(data, f, indent=2, sort_keys=True)
    f.write("\n")
PY
}

ABORT_REASON=""
# task 5.5 — set by either step runner below; read by arm-level classification
# after the step loop. Two separate flags because they mean different things:
# RO_SUBSTRATE_VIOLATION fires for ANY role/step that touches tests/runtime/
# cases (illegitimate for everyone); DIAGNOSTICIAN_SRC_VIOLATION fires only
# when the diagnose role touches src/ (legitimate for monolith/apply).
RO_SUBSTRATE_VIOLATION=0
DIAGNOSTICIAN_SRC_VIOLATION=0

run_model_step() {
  local name="$1" dir="$2" ws="$3"
  local role="${name#*-}"
  # ONE prompt file PER task_id, never per role (task 5.4b; tasks.md:794
  # "one `.txt` per `task_id` (`s1`, `s2`)" — exactly two files, not three).
  # This is the same naming convention rig/run.sh:306 already uses
  # (`PROMPT_FILE="$FIXTURE_ROOT/prompts/${TASK_ID}.txt"`), and it is what
  # makes ADR 0010's "harness shape is the only variable" provable at the
  # byte level: MONOLITHIC's one model step and PIPELINE's `diagnose` and
  # `apply` steps all load the identical committed file for a given
  # task_id, so no role or arm can be handed a differently-worded task.
  # What differs between roles is never the prompt text — it is the
  # workspace state each role's invocation is composed with (a bounded
  # clusters view, or a copied-in fix-plan.txt), which is harness shape,
  # the one dimension ADR 0010 permits to vary.
  local prompt_file="$FIXTURE_ROOT/prompts/${TASK_ID}.txt"
  # Checked here, per-invocation, immediately before invoking — not as a
  # global up-front gate, so a PIPELINE arm's earlier code step (01-collect)
  # can still run and persist real artifacts even while a later step's
  # prompt is missing (see this file's own "THIS UNIT'S SCOPE" header).
  if [ ! -f "$prompt_file" ]; then
    ABORT_REASON="missing-prompt:$prompt_file"
    return 0
  fi
  if [ ! -f "$SURFACE_FILE" ]; then
    ABORT_REASON="missing-surface-preimage:$SURFACE_FILE"
    return 0
  fi
  local prompt_text
  prompt_text="$(cat "$prompt_file")"
  if [ "$role" = "apply" ] && [ -f "$RUN_DIR/steps/02-diagnose/handoff/fix-plan.txt" ]; then
    cp "$RUN_DIR/steps/02-diagnose/handoff/fix-plan.txt" "$ws/fix-plan.txt"
  fi

  # task 5.5: pre-hashed separately by zone, never as one combined list — a
  # legitimate src/ write by monolith/apply must not be conflated with the
  # illegitimate one (the diagnostician), and a tests/runtime/cases write is
  # illegitimate for every role.
  local src_pre src_post ro_pre ro_post
  src_pre="$(printf '%s\n' "$SRC_PATHS" | hash_paths "$ws")"
  ro_pre="$(printf '%s\n' "$RO_PATHS" | hash_paths "$ws")"

  local start_ms end_ms exit_code timed_out=0
  start_ms="$(now_ms)"
  set +e
  (
    cd "$ws"
    # --strict-mcp-config in BOTH arms (design.md Amendment 3, restated in
    # rig/run.sh's own header comment). No --disallowedTools: R-F6.4 "Both
    # arms MUST allow Bash and a write tool" — there is no broad/scoped
    # narrowing here, unlike rig/run.sh's own experiment.
    exec timeout "$STEP_TIMEOUT_S" claude -p "$prompt_text" \
      --output-format stream-json --verbose \
      --strict-mcp-config --permission-mode "$PERMISSION_MODE" \
      >>"$dir/stream.jsonl" 2>>"$dir/stderr.log"
  ) &
  local child=$!
  trap 'kill -TERM "$child" 2>/dev/null' TERM INT
  wait "$child"; exit_code=$?
  trap - TERM INT
  set -e
  end_ms="$(now_ms)"
  [ "$exit_code" -eq 124 ] && timed_out=1

  src_post="$(printf '%s\n' "$SRC_PATHS" | hash_paths "$ws")"
  ro_post="$(printf '%s\n' "$RO_PATHS" | hash_paths "$ws")"
  local src_changed=0 ro_changed=0
  [ "$src_pre" != "$src_post" ] && src_changed=1
  [ "$ro_pre" != "$ro_post" ] && ro_changed=1
  local substrate=0; { [ "$src_changed" -eq 1 ] || [ "$ro_changed" -eq 1 ]; } && substrate=1

  # task 5.5 classification: tests/runtime/cases (RO_PATHS) is illegitimate
  # for EVERY role; src/ is illegitimate ONLY for the diagnostician — the
  # applier and MONOLITHIC are supposed to write src/, that is their job.
  [ "$ro_changed" -eq 1 ] && RO_SUBSTRATE_VIOLATION=1
  [ "$role" = "diagnose" ] && [ "$src_changed" -eq 1 ] && DIAGNOSTICIAN_SRC_VIOLATION=1

  local read_back surf perm
  read_back="$(read_back_init "$dir/stream.jsonl")"
  surf="${read_back%% *}"; perm="${read_back#* }"

  # Thread the fix-plan out (design.md sec 2): the diagnostician's only
  # writable place is its workspace root; copy it out and hash it before
  # this workspace is discarded, so the applier's fresh workspace (built by
  # the next materialize_step call) gets a frozen copy, never the live one.
  if [ "$role" = "diagnose" ] && [ -f "$ws/fix-plan.txt" ]; then
    mkdir -p "$dir/handoff"
    cp "$ws/fix-plan.txt" "$dir/handoff/fix-plan.txt"
  fi

  write_step_status "$dir" "$role" model "$exit_code" $((end_ms - start_ms)) "$substrate" "$surf" "$perm" "$timed_out" "$src_changed" "$ro_changed"
  [ "$timed_out" -eq 1 ] && { ABORT_REASON="timeout"; return 0; }
  return 0
}

run_code_step() {
  local name="$1" dir="$2" ws="$3"
  local role="${name#*-}"
  local expected_suites=3
  [ "$FIXTURE_VERSION" = "v2" ] && expected_suites=6

  # task 5.5: same zone split as run_model_step. A code step's role is never
  # "diagnose", so only the RO_PATHS (tests/runtime/cases) zone can flag a
  # violation here — a code step legitimately touches nothing under src/.
  local src_pre src_post ro_pre ro_post
  src_pre="$(printf '%s\n' "$SRC_PATHS" | hash_paths "$ws")"
  ro_pre="$(printf '%s\n' "$RO_PATHS" | hash_paths "$ws")"

  local start_ms end_ms exit_code
  start_ms="$(now_ms)"
  set +e
  FAILURE_FLOOD_CASE_DIR="$ws/cases" timeout "$STEP_TIMEOUT_S" python3 "$REPO_ROOT/rig/collect.py" \
    --cwd "$ws/runtime" \
    --report-file "$dir/report.json" \
    --collection-output "$dir/collection.json" \
    --clusters-output "$dir/clusters.json" \
    --suite-timeout-s "$SUITE_TIMEOUT_S" \
    --expected-suites "$expected_suites" \
    >"$dir/collect.log" 2>&1
  exit_code=$?
  set -e
  end_ms="$(now_ms)"

  src_post="$(printf '%s\n' "$SRC_PATHS" | hash_paths "$ws")"
  ro_post="$(printf '%s\n' "$RO_PATHS" | hash_paths "$ws")"
  local src_changed=0 ro_changed=0
  [ "$src_pre" != "$src_post" ] && src_changed=1
  [ "$ro_pre" != "$ro_post" ] && ro_changed=1
  local substrate=0; { [ "$src_changed" -eq 1 ] || [ "$ro_changed" -eq 1 ]; } && substrate=1
  [ "$ro_changed" -eq 1 ] && RO_SUBSTRATE_VIOLATION=1

  # Tokens are recorded 0, not absent (design.md sec 2: "keeps the 'zero
  # model tokens' claim read back rather than asserted").
  write_step_status "$dir" "$role" code "$exit_code" $((end_ms - start_ms)) "$substrate" "" "" 0 "$src_changed" "$ro_changed"
  # collector-error (design.md Decision 3: run-axis void, never a suite
  # state) is collect.py's own exit 2.
  [ "$exit_code" -eq 2 ] && { ABORT_REASON="collector-error"; return 0; }
  return 0
}

LAST_WORKSPACE=""
for spec in "${STEPS[@]}"; do
  STEP_NAME="${spec%%:*}"
  STEP_KIND="${spec##*:}"
  STEP_DIR="$RUN_DIR/steps/$STEP_NAME"
  mkdir -p "$STEP_DIR"

  if [ "$STEP_NAME" = "99-verify" ]; then
    STEP_WS="$LAST_WORKSPACE"
  else
    STEP_WS="$(materialize_step)"
    LAST_WORKSPACE="$STEP_WS"
  fi

  if [ "$STEP_KIND" = "model" ]; then
    run_model_step "$STEP_NAME" "$STEP_DIR" "$STEP_WS"
  else
    run_code_step "$STEP_NAME" "$STEP_DIR" "$STEP_WS"
  fi

  [ -n "$ABORT_REASON" ] && break
done

# ---- arm-level classification, arm.json, arm status.json ---------------

case "$ABORT_REASON" in
  missing-prompt:*) ARM_EXIT=2; ARM_STATE="void"; ARM_VOID_REASON="missing-prompt" ;;
  missing-surface-preimage:*) ARM_EXIT=2; ARM_STATE="void"; ARM_VOID_REASON="missing-surface-preimage" ;;
  timeout) ARM_EXIT=0; ARM_STATE="void"; ARM_VOID_REASON="timeout" ;;
  collector-error) ARM_EXIT=0; ARM_STATE="void"; ARM_VOID_REASON="collector-error" ;;
  "") ARM_EXIT=0; ARM_STATE="complete"; ARM_VOID_REASON="" ;;
esac
# ARM_EXIT=2's "void" here deliberately blurs the 0/2 partition the header
# comment states (0=complete/void, 2=could not run): Amendment 1 ("status.json
# flushed... before exit 2 where possible") wins over exit-code purity once
# the run directory is already claimed — evidence over a clean partition.
# Recorded as a tension, not hidden; see the apply report.

# Hard Ordering Gate layer 1 (R-F8.2): UNCONDITIONAL. Does not read DIRTY,
# DIRTY_OK, or whatever ARM_STATE the loop above produced — the exact
# property rig/run.sh:463-466 lacks ("[ \"$DIRTY_OK\" -eq 1 ] && [ -n \"$DIRTY\" ]",
# stamped only when the tree is ACTUALLY dirty). This line has no such guard.
if [ "$SHAKEDOWN" -eq 1 ]; then
  ARM_STATE="void"
  ARM_VOID_REASON="shakedown"
fi

# ---- read-only substrate / diagnostician-writes-to-src (task 5.5) -------
# Runs LAST, after every other classification above INCLUDING the
# unconditional shakedown stamp — the task's own wording is "any change to
# src/ [by the diagnostician] sets arm state failed, never void", and
# design.md sec 2 / the exit-code table (this file's header) name both
# violations as the same assertion-fired outcome, exit 1. Placing this check
# after shakedown is what makes "never void" literally true: even a
# --shakedown run that caught a real violation is reported as failed, not
# silently absorbed into void_reason=shakedown. This does not weaken layer 1
# (R-F8.2) as a COUNTABILITY guard — a failed row is exactly as excluded from
# any hypothesis test as a void one; it changes only which of the two named
# outcomes the row is stamped with, which is the visible signal a real
# defect happened.
if [ "$RO_SUBSTRATE_VIOLATION" -eq 1 ] || [ "$DIAGNOSTICIAN_SRC_VIOLATION" -eq 1 ]; then
  ARM_STATE="failed"
  ARM_VOID_REASON=""
  ARM_EXIT=1
fi

STEP_NAMES_CSV="$(printf '%s\n' "${STEPS[@]%%:*}" | paste -sd, -)"
RUN_ID="$RUN_ID" TASK_ID="$TASK_ID" ARM="$ARM" ITERATION="$ITERATION" EXPERIMENT="$EXPERIMENT" \
FIXTURE_VERSION="$FIXTURE_VERSION" STEP_NAMES="$STEP_NAMES_CSV" RUN_DIR="$RUN_DIR" \
NODE_VERSION="$NODE_VERSION" NPM_VERSION="$NPM_VERSION" PYTHON_VERSION="$PYTHON_VERSION" \
DRIVER_VERSION="$DRIVER_VERSION" LOCKFILE_SHA256="$LOCKFILE_SHA256" \
CASE_TABLE_DIGEST="$CASE_TABLE_DIGEST" CASE_COUNT="$CASE_COUNT" PREREG_DIGEST="$PREREG_DIGEST" \
CODE_COMMIT="$CODE_COMMIT" DECLARED_PERMISSION_MODE="$PERMISSION_MODE" \
STATE="$ARM_STATE" VOID_REASON="$ARM_VOID_REASON" ABORT_REASON="$ABORT_REASON" DIRTY_OK_USED="$DIRTY_OK" \
SHAKEDOWN_USED="$SHAKEDOWN" WORKSPACE_FILE_COUNT="$WORKSPACE_FILE_COUNT" \
RO_SUBSTRATE_VIOLATION="$RO_SUBSTRATE_VIOLATION" DIAGNOSTICIAN_SRC_VIOLATION="$DIAGNOSTICIAN_SRC_VIOLATION" \
python3 <<'PY'
import json, os

env = os.environ
steps = []
for name in env["STEP_NAMES"].split(","):
    p = os.path.join(env["RUN_DIR"], "steps", name, "status.json")
    step = json.load(open(p)) if os.path.isfile(p) else {"status": "not-run"}
    step["index"] = name
    steps.append(step)

arm = {
    "run_id": env["RUN_ID"], "experiment": env["EXPERIMENT"], "task_id": env["TASK_ID"],
    "arm": env["ARM"], "iteration": env["ITERATION"], "fixture_version": env["FIXTURE_VERSION"],
    "code_commit": env["CODE_COMMIT"], "node_version": env["NODE_VERSION"],
    "npm_version": env["NPM_VERSION"], "python_version": env["PYTHON_VERSION"],
    "driver_version": env["DRIVER_VERSION"], "lockfile_sha256": env["LOCKFILE_SHA256"],
    "case_table_digest": env["CASE_TABLE_DIGEST"] or None,
    "case_count": int(env["CASE_COUNT"] or 0),
    "prereg_digest": env["PREREG_DIGEST"] or None,
    "declared_permission_mode": env["DECLARED_PERMISSION_MODE"],
    "workspace_file_count": int(env["WORKSPACE_FILE_COUNT"]),
    "dirty_ok_used": env["DIRTY_OK_USED"] == "1",
    "shakedown_used": env["SHAKEDOWN_USED"] == "1",
    "abort_reason": env["ABORT_REASON"] or None,
    # task 5.5's own classification, at the arm level (each step's status.json
    # already carries the same per-step src_changed/ro_changed evidence).
    "ro_substrate_violation": env["RO_SUBSTRATE_VIOLATION"] == "1",
    "diagnostician_src_violation": env["DIAGNOSTICIAN_SRC_VIOLATION"] == "1",
    "state": env["STATE"],
    "void_reason": env["VOID_REASON"] or None,
    "steps": steps,
}
with open(os.path.join(env["RUN_DIR"], "arm.json"), "w") as f:
    json.dump(arm, f, indent=2, sort_keys=True)
    f.write("\n")

if env["STATE"]:
    status = {
        "run_id": env["RUN_ID"], "experiment": env["EXPERIMENT"], "state": env["STATE"],
        "void_reason": env["VOID_REASON"] or None, "code_commit": env["CODE_COMMIT"],
    }
    with open(os.path.join(env["RUN_DIR"], "status.json"), "w") as f:
        json.dump(status, f, indent=2, sort_keys=True)
        f.write("\n")
PY

if [ "$ARM_EXIT" -eq 2 ]; then
  die_cannot_run "arm aborted after the run directory was claimed ($ABORT_REASON); arm.json is written under $RUN_DIR for inspection"
fi

if [ "$ARM_EXIT" -eq 1 ]; then
  printf '\n  ASSERTION FIRED: arm %s -> failed (ro_substrate_violation=%s diagnostician_src_violation=%s). This is exit 1, not exit 2 — the run directory was already claimed and status.json/arm.json are flushed under %s.\n' \
    "$RUN_ID" "$RO_SUBSTRATE_VIOLATION" "$DIAGNOSTICIAN_SRC_VIOLATION" "$RUN_DIR" >&2
fi

printf '  run %s: state=%s%s -> %s\n' "$RUN_ID" "$ARM_STATE" "${ARM_VOID_REASON:+ ($ARM_VOID_REASON)}" "$RUN_DIR"
exit "$ARM_EXIT"
