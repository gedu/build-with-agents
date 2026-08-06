#!/usr/bin/env bash
#
# rig/run.sh — guards, launches, and persists ONE measurement-rig run.
#
# This script never parses the transcript for task outcome, never
# aggregates rows, and never decides a verdict on the fixture task — that
# is rig/derive.py's job, deliberately kept separate so a checker bug never
# requires re-spending a live run (sdd/measurement-rig/design.md, Decision
# 1). The one thing this script DOES read back from the transcript is
# purely mechanical: whether the last line looks like a `result` event, so
# it can tell `complete` apart from `void` for its own idempotence lock
# (Decision 6) — never whether the reported answer was right.
#
# Safety contract, matching setup.sh's: this script never launches against
# a fixture that does not match its own frozen MANIFEST, never launches
# against an unclean tree unless told to with --dirty-ok (which can never
# produce a countable row), and always writes status.json — including on
# a non-zero exit — before it exits, so a failure investigation always has
# evidence to read rather than a mystery.
#
# EXIT CODES (mirrors hooks/pre-commit's 0/1/2 house convention, and spec
# Amendment 1 R-A1.1's three-run-state contract):
#   0  the run reached `complete` or `void` (state field in status.json).
#      An environmental anomaly is a DESIGNED outcome, not a failure, and
#      must never be conflated with one — see design.md's Amendment 1.
#   1  the run reached `failed` — the harness's own assertion fired. Right
#      now the only thing this script can assert without parsing the
#      transcript is that the read-only workspace copy was mutated; that is
#      the only thing that can produce this exit code.
#   2  could not run at all: bad arguments, a missing prerequisite, a dirty
#      tree, a MANIFEST mismatch, or (scoped arm only) a missing surface
#      preimage. NOT a pass. Never conflated with 0.
#
# `status.json` is written before every exit path, including exit 2 where
# possible and exit 1 always — see gentle-ai issue #1883 (spec Amendment 1
# R-A1.1): a harness that reports failure and still exits 0, or that exits
# non-zero and takes its evidence with it, turns a diagnosable failure into
# a mystery either way.
#
# NEVER --allowedTools (no visibility effect — verified in exploration.md).
# NEVER --strict-mcp-config (drops mcp_servers 25 -> 0, a second variable).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPERIMENT="tool-surface-v1"
FIXTURE_ROOT="$REPO_ROOT/rig/fixtures/tool-surface/v1"
RUNS_ROOT="$REPO_ROOT/rig/runs/$EXPERIMENT"
SURFACES_ROOT="$REPO_ROOT/rig/surfaces"

# Pilot bound only (design.md Decision 5). Its job is to be replaced once
# the tier-1 pilot (Phase 6, not yet run) derives the real bound from
# 3x the slowest successful pilot run, floor 120s.
TIMEOUT_S=300

usage() {
  cat <<'USAGE'
Usage: rig/run.sh <task_id> <arm> <iteration> [--dirty-ok]

  task_id     t1 | t2 | t3
  arm         broad | scoped
  iteration   an iteration slot, e.g. 03, or a void re-run suffix, e.g. 03r1
              (design.md Decision 6: run_id = <task_id>-<arm>-<iteration>)
  --dirty-ok  bypass the dirty-tree guard. Shakedown only: the resulting
              row is stamped void_reason=dirty-tree and can never be counted.

Guards, launches ONE claude invocation, and persists its artifacts under
rig/runs/<experiment>/<run_id>/. Never parses the transcript for task
outcome, never aggregates — see rig/derive.py for that.
USAGE
}

warn() { printf '  !! %s\n' "$1" >&2; }

die_bad_args() {
  warn "$1"
  usage >&2
  exit 2
}

die_cannot_run() {
  printf '\n  COULD NOT RUN: %s\n  This is exit 2, not a pass.\n' "$1" >&2
  exit 2
}

# now_ms — millisecond epoch via python3, not `date +%N`: BSD date (the
# macOS default) has no sub-second format specifier at all, and python3 is
# already a hard prerequisite below, so reusing it avoids a second new
# dependency (e.g. GNU coreutils' gdate) for one timestamp.
now_ms() { python3 -c 'import time; print(int(time.time() * 1000))'; }

# hash_fixture_files <dir> — one sha256 over exactly the files that were
# materialized from the fixture's src/ (a manifest computed once, right
# after materialization, and reused for the post-run re-hash) — never
# "whatever is in <dir> now".
#
# EXECUTED, not reasoned: this shakedown found that `claude` itself writes
# an ambient `.atl/skill-registry*` cache into its own cwd on every
# invocation, regardless of which tools the agent used — this repo's own
# .gitignore already names `.atl/` as "local agent state, not the
# tool-neutral sources". Neither arm has a WRITE tool, so the agent cannot
# create that file itself, and hashing "the whole directory" produced a
# false substrate_mutated=true on every single run, including one where
# the fixture file was verified byte-identical by hand. The question this
# check must answer is "did the agent's read-only substrate change", not
# "did any file appear in the directory" — those are different questions,
# and only the first one is a finding.
hash_fixture_files() {
  # $1 = workspace root; the explicit path list comes in on stdin, one
  # relative path per line — NEVER a fresh directory listing, so a file
  # that appears later (ambient tooling) cannot enter the comparison, and
  # a file that disappears is still caught (hashed as "<missing>").
  python3 - "$1" <<'PY'
import hashlib, pathlib, sys

root = pathlib.Path(sys.argv[1])
lines = []
for rel in sorted(l.strip() for l in sys.stdin if l.strip()):
    p = root / rel
    try:
        content = p.read_bytes()
    except FileNotFoundError:
        content = b"<missing>"
    lines.append(f"{hashlib.sha256(content).hexdigest()}  {rel}")
print(hashlib.sha256("\n".join(lines).encode()).hexdigest())
PY
}

# list_fixture_files <dir> — the relative-path manifest captured once,
# right after materialization, and reused unchanged for both the pre- and
# post-run hash so the comparison's scope cannot silently drift.
list_fixture_files() {
  ( cd "$1" && find . -type f | sed 's#^\./##' | sort )
}

# compute_manifest <fixture-root> — sorted "sha256  relpath" over
# src/, prompts/, answer-key/. Matches the format MANIFEST.sha256 was
# generated with (rig/fixtures/tool-surface/v1/MANIFEST.sha256), so the
# comparison in verify_manifest() is byte-for-byte.
compute_manifest() {
  python3 - "$1" <<'PY'
import hashlib, pathlib, sys

root = pathlib.Path(sys.argv[1])
lines = []
for sub in ("src", "prompts", "answer-key"):
    d = root / sub
    if not d.is_dir():
        continue
    for p in sorted(d.rglob("*")):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            lines.append((rel, f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}"))
lines.sort(key=lambda t: t[0])
print("\n".join(l for _, l in lines))
PY
}

# classify_stream <stream.jsonl> <timed_out 0|1> — prints one of:
#   complete
#   void:<reason>
# plus, on stderr, "truncated_tail" if the tolerance rule fired.
# This is a MECHANICAL check only (is the last line valid JSON with
# type=="result"), never a semantic read of tool calls or the reported
# answer — that boundary is what keeps this in run.sh's scope rather than
# derive.py's (design.md Decision 1).
classify_stream() {
  python3 - "$1" "$2" <<'PY'
import json, sys

path, timed_out = sys.argv[1], sys.argv[2] == "1"
try:
    with open(path, "rb") as f:
        raw = f.read()
except FileNotFoundError:
    print("void:missing-result")
    sys.exit(0)

lines = [l for l in raw.split(b"\n") if l.strip()]
if not lines:
    print("void:missing-result")
    sys.exit(0)


def is_result(line):
    try:
        return json.loads(line).get("type") == "result"
    except Exception:
        return None  # unparseable, distinct from "parseable but not a result"


last = is_result(lines[-1])
if last is None and timed_out and len(lines) >= 2:
    # Exactly one unparseable trailing line is tolerated ONLY on a
    # timed_out run (design.md Decision 2) — an expected artifact of the
    # kill, not a corrupt stream. Fall back to the line before it.
    print("truncated_tail", file=sys.stderr)
    last = is_result(lines[-2])

if last is True:
    print("complete")
elif timed_out:
    print("void:timeout")
else:
    print("void:missing-result")
PY
}

# ---- argument parsing -------------------------------------------------

DIRTY_OK=0
POSITIONAL=()
for arg in "$@"; do
  case "$arg" in
    --dirty-ok) DIRTY_OK=1 ;;
    -h|--help) usage; exit 0 ;;
    --*) die_bad_args "unknown flag '$arg'" ;;
    *) POSITIONAL+=("$arg") ;;
  esac
done

[ "${#POSITIONAL[@]}" -eq 3 ] || die_bad_args "expected 3 positional arguments (task_id arm iteration), got ${#POSITIONAL[@]}"

TASK_ID="${POSITIONAL[0]}"
ARM="${POSITIONAL[1]}"
ITERATION="${POSITIONAL[2]}"

case "$TASK_ID" in t1|t2|t3) ;; *) die_bad_args "task_id must be t1, t2 or t3 — got '$TASK_ID'" ;; esac
case "$ARM" in broad|scoped) ;; *) die_bad_args "arm must be broad or scoped — got '$ARM'" ;; esac
case "$ITERATION" in
  [0-9]*) ;;
  *) die_bad_args "iteration must start with a digit (e.g. 03, or 03r1 for a void re-run) — got '$ITERATION'" ;;
esac
# Reject anything that is not a safe path component (this becomes part of a
# directory name below; see the "subprocess argument composition" row in
# design.md's threat matrix).
case "$ITERATION" in
  *[!a-zA-Z0-9]*) die_bad_args "iteration must be alphanumeric only — got '$ITERATION'" ;;
esac

RUN_ID="${TASK_ID}-${ARM}-${ITERATION}"

# ---- prerequisite checks (exit 2: could not run) ----------------------

command -v python3 >/dev/null 2>&1 || die_cannot_run "python3 is missing. It is a rig-only prerequisite (decisions/0011); the hooks/pre-commit portability contract does not extend here."
command -v timeout >/dev/null 2>&1 || die_cannot_run "'timeout' is missing. On macOS this is GNU coreutils' timeout (brew install coreutils), not a stock BSD command — a rig-only prerequisite, same class as python3."
command -v claude >/dev/null 2>&1 || die_cannot_run "'claude' CLI is missing from PATH."

DRIVER_VERSION="$(claude --version 2>/dev/null || echo unknown)"
PYTHON_VERSION="$(python3 --version 2>&1)"

# ---- dirty-tree guard ---------------------------------------------------
#
# Scoped to the whole rig/ tree rather than enumerating the fixture,
# checker, prompt and driver paths individually: every one of those already
# lives under rig/, and enumerating each path by hand would silently miss a
# future addition (e.g. rig/derive.py) unless this list is remembered to be
# updated in lockstep. rig/runs/ is gitignored and therefore invisible to
# `git status` regardless, so it cannot cause a false-dirty result.
DIRTY="$(git -C "$REPO_ROOT" status --porcelain -- rig)"
if [ -n "$DIRTY" ] && [ "$DIRTY_OK" -ne 1 ]; then
  die_cannot_run "the tree is dirty under rig/ (staged or unstaged). Re-run with --dirty-ok for a shakedown-only run (never countable), or commit/stash first:
$DIRTY"
fi

CODE_COMMIT="$(git -C "$REPO_ROOT" rev-parse HEAD)"
if [ "$DIRTY_OK" -eq 1 ] && [ -n "$DIRTY" ]; then
  CODE_COMMIT="${CODE_COMMIT}-dirty"
fi

# ---- MANIFEST recompute-compare ----------------------------------------

MANIFEST_FILE="$FIXTURE_ROOT/MANIFEST.sha256"
[ -f "$MANIFEST_FILE" ] || die_cannot_run "missing $MANIFEST_FILE — freeze the fixture before running (rig/README.md)."
COMPUTED_MANIFEST="$(compute_manifest "$FIXTURE_ROOT")"
COMMITTED_MANIFEST="$(cat "$MANIFEST_FILE")"
if [ "$COMPUTED_MANIFEST" != "$COMMITTED_MANIFEST" ]; then
  die_cannot_run "MANIFEST.sha256 mismatch — the fixture on disk does not match what was frozen. Refusing to run against a tampered or edited fixture (design.md Decision 4). A change belongs in a new v2/ directory, not an edit to v1/."
fi

PROMPT_FILE="$FIXTURE_ROOT/prompts/${TASK_ID}.txt"
[ -f "$PROMPT_FILE" ] || die_cannot_run "missing $PROMPT_FILE"

# ---- scoped-arm disallow list -------------------------------------------
#
# DISALLOW is computed as (broad surface) minus (scoped surface), both read
# from committed preimages — never a string built ad hoc in this script
# (design.md's threat matrix: "the disallowed list is a committed file, not
# a constructed string"). rig/surfaces/broad.txt does not exist yet: it
# must be captured from a real, non-nested `claude` session on the machine
# that runs the actual experiment (see rig/README.md and this batch's
# apply report) — a value guessed here would be exactly the kind of
# invented knowledge AGENTS.md forbids, and a wrong one would silently
# break every future void-classification.
# Bash is disallowed in BOTH arms, and that is not a preference (design.md
# Amendment 2). Bash SUBSUMES Glob and Grep: while it is available the surface
# presents Bash alone and hides them; removing it exposes both. Leaving Bash in
# the broad arm would therefore mean the arms differ in CAPABILITY — broad could
# shell out, scoped could not — instead of only in breadth, which is a second
# variable and the one thing ADR 0010 constraint 2 forbids.
#
# It is also correct on its own terms: these tasks only REPORT defects, so no arm
# needs to execute anything, and a shell in one arm could substitute for the very
# search tools the practice check exists to observe.
BASELINE_DISALLOW="Bash"

DISALLOW="$BASELINE_DISALLOW"
if [ "$ARM" = scoped ]; then
  BROAD_SURFACE="$SURFACES_ROOT/broad.txt"
  SCOPED_SURFACE="$SURFACES_ROOT/scoped.txt"
  [ -f "$BROAD_SURFACE" ] || die_cannot_run "missing $BROAD_SURFACE. The scoped arm's list is Bash plus (broad surface minus scoped surface); broad.txt must be captured with --strict-mcp-config --disallowedTools Bash. See rig/README.md."
  [ -f "$SCOPED_SURFACE" ] || die_cannot_run "missing $SCOPED_SURFACE"
  # broad.txt was itself captured with Bash already disallowed, so Bash is NOT a
  # member of it and `comm` can never emit it. Prepending BASELINE_DISALLOW is
  # therefore load-bearing, not belt-and-braces: without it the scoped arm would
  # keep Bash, which would hide Glob and Grep and invert the comparison.
  EXTRA="$(comm -23 <(sort -u "$BROAD_SURFACE") <(sort -u "$SCOPED_SURFACE") | paste -sd, -)"
  [ -n "$EXTRA" ] || die_cannot_run "computed --disallowedTools list is empty; broad.txt and scoped.txt are identical, or broad.txt is stale"
  DISALLOW="$BASELINE_DISALLOW,$EXTRA"
fi

# ---- materialize the workspace ------------------------------------------
#
# Outside <repo>, machine-local, a copy of src/'s CONTENTS only — never
# answer-key/, never discoverable via a repo AGENTS.md/CLAUDE.md walked up
# from cwd (design.md Decision 4). Flattened (not nested under a src/
# subdirectory) so a reported relative path is just e.g. "paginate.js".
WORKSPACE_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/rig-workspace.XXXXXX")"
cp -R "$FIXTURE_ROOT/src/." "$WORKSPACE_ROOT/"
FIXTURE_FILE_LIST="$(list_fixture_files "$WORKSPACE_ROOT")"
PRE_HASH="$(printf '%s\n' "$FIXTURE_FILE_LIST" | hash_fixture_files "$WORKSPACE_ROOT")"

# ---- claim the run directory (Decision 6: mkdir is the lock) ------------

mkdir -p "$RUNS_ROOT"
RUN_DIR="$RUNS_ROOT/$RUN_ID"
if ! mkdir "$RUN_DIR" 2>/dev/null; then
  if [ -f "$RUN_DIR/status.json" ]; then
    PRIOR_STATE="$(python3 -c 'import json,sys
d=json.load(open(sys.argv[1]))
print(d.get("state","unknown"))' "$RUN_DIR/status.json" 2>/dev/null || echo unknown)"
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

cp "$PROMPT_FILE" "$RUN_DIR/prompt.txt"
PROMPT_TEXT="$(cat "$PROMPT_FILE")"

# ---- invoke --------------------------------------------------------------
#
# Redirected straight to a file, never piped into a parser (design.md
# Decision 2): a parser crash in the pipe would destroy the transcript.
#
# Backgrounded, with an explicit trap, rather than run in the foreground
# inside a plain subshell. EXECUTED, not reasoned: an earlier version of
# this script ran the invocation in the foreground, and killing run.sh's
# own PID (as opposed to Ctrl-C, which signals the whole terminal process
# group) left `timeout`/`claude` running as an orphan — still billing,
# still writing to stream.jsonl, with nothing left tracking it. Forwarding
# the signal to the child explicitly is what makes the mid-flight-kill
# shakedown (Phase 3, 3.1) actually test what it claims to.
START_MS="$(now_ms)"
set +e
(
  cd "$WORKSPACE_ROOT"
  # --strict-mcp-config is REQUIRED in both arms, and it reverses an earlier
  # prohibition in this file's own design (Amendment 3). Without it the visible
  # surface is NOT REPRODUCIBLE: two identical invocations seconds apart returned
  # 55 and 82 tools, because a remote MCP server recorded as "pending" finished
  # connecting between them and contributed 27 names. Runs in the same arm would
  # differ by 27 tools, the read-back would correctly void an unpredictable share
  # of them as surface-mismatch, and the experiment would never accumulate its N.
  #
  # It was forbidden before because it moves MCP server count from 25 to 0 and is
  # therefore a second variable. True of one arm. Applied to BOTH arms it is a
  # constant — the same correction Amendment 2 made for Bash.
  exec timeout "$TIMEOUT_S" claude -p "$PROMPT_TEXT" \
    --output-format stream-json --verbose \
    --strict-mcp-config \
    ${DISALLOW:+--disallowedTools "$DISALLOW"} \
    >>"$RUN_DIR/stream.jsonl" 2>>"$RUN_DIR/stderr.log"
) &
CHILD_PID=$!
trap 'kill -TERM "$CHILD_PID" 2>/dev/null' TERM INT
wait "$CHILD_PID"
EXIT_CODE=$?
trap - TERM INT
set -e
END_MS="$(now_ms)"
WALL_MS=$((END_MS - START_MS))
TIMED_OUT=0
[ "$EXIT_CODE" -eq 124 ] && TIMED_OUT=1

# ---- substrate-mutation check --------------------------------------------
#
# Neither arm has a write tool, so a change to one of the ORIGINAL fixture
# files is a finding, not a tolerance (design.md Decision 4). Scoped to the
# exact file list captured at materialization time (see hash_fixture_files'
# own comment for why: ambient tooling writes into the workspace cwd
# regardless of the agent's own tool use, and that is not this check's
# concern).
POST_HASH="$(printf '%s\n' "$FIXTURE_FILE_LIST" | hash_fixture_files "$WORKSPACE_ROOT")"
SUBSTRATE_MUTATED=0
[ "$PRE_HASH" != "$POST_HASH" ] && SUBSTRATE_MUTATED=1

# ---- classify and persist status.json ------------------------------------
#
# classify_stream is mechanical (does the stream end in a `result` event),
# never semantic. Full read-back verification (surface/model/prompt/
# cwd/ambient-drift -> void reasons) is rig/derive.py's job, not built in
# this batch (design.md Decision 7).
STREAM_STATE_RAW="$(classify_stream "$RUN_DIR/stream.jsonl" "$TIMED_OUT" 2>"$RUN_DIR/.classify_stderr" || true)"
TRUNCATED_TAIL=0
grep -q truncated_tail "$RUN_DIR/.classify_stderr" 2>/dev/null && TRUNCATED_TAIL=1
rm -f "$RUN_DIR/.classify_stderr"

STATE="${STREAM_STATE_RAW%%:*}"
VOID_REASON=""
case "$STREAM_STATE_RAW" in
  void:*) VOID_REASON="${STREAM_STATE_RAW#void:}" ;;
esac

# A dirty-tree run can never be counted, regardless of what the stream
# looks like (design.md Decision 3).
if [ "$DIRTY_OK" -eq 1 ] && [ -n "$DIRTY" ]; then
  STATE="void"
  VOID_REASON="dirty-tree"
fi

# Assertion firing overrides everything else, including a dirty-ok run:
# a mutated read-only substrate is a genuine finding, not a discard.
if [ "$SUBSTRATE_MUTATED" -eq 1 ]; then
  STATE="failed"
  VOID_REASON=""
fi

STATUS_FILE="$RUN_DIR/status.json"
# Every value crosses the bash/python boundary as an environment variable,
# never spliced into the heredoc as text: a hand-built conditional (empty
# string vs `null`, quoting a value that might itself contain a quote) is
# exactly the kind of fragile string surgery this script's own threat
# matrix warns against for the claude invocation, and status.json deserves
# the same discipline.
RUN_ID="$RUN_ID" EXPERIMENT="$EXPERIMENT" TASK_ID="$TASK_ID" ARM="$ARM" \
ITERATION="$ITERATION" STATE="$STATE" VOID_REASON="$VOID_REASON" \
EXIT_CODE="$EXIT_CODE" TIMED_OUT="$TIMED_OUT" TRUNCATED_TAIL="$TRUNCATED_TAIL" \
SUBSTRATE_MUTATED="$SUBSTRATE_MUTATED" WALL_MS="$WALL_MS" TIMEOUT_S="$TIMEOUT_S" \
CODE_COMMIT="$CODE_COMMIT" DIRTY_OK_USED="$DIRTY_OK" DRIVER_VERSION="$DRIVER_VERSION" \
PYTHON_VERSION="$PYTHON_VERSION" STATUS_FILE="$STATUS_FILE" \
python3 <<'PY'
import json, os

env = os.environ
data = {
    "run_id": env["RUN_ID"],
    "experiment": env["EXPERIMENT"],
    "task_id": env["TASK_ID"],
    "arm": env["ARM"],
    "iteration": env["ITERATION"],
    "state": env["STATE"],
    "void_reason": env["VOID_REASON"] or None,
    "exit_code": int(env["EXIT_CODE"]),
    "timed_out": env["TIMED_OUT"] == "1",
    "truncated_tail": env["TRUNCATED_TAIL"] == "1",
    "substrate_mutated": env["SUBSTRATE_MUTATED"] == "1",
    "wall_ms": int(env["WALL_MS"]),
    "timeout_s": int(env["TIMEOUT_S"]),
    "code_commit": env["CODE_COMMIT"],
    "dirty_ok_used": env["DIRTY_OK_USED"] == "1",
    "driver_version": env["DRIVER_VERSION"],
    "python_version": env["PYTHON_VERSION"],
}
with open(env["STATUS_FILE"], "w") as f:
    json.dump(data, f, indent=2, sort_keys=True)
    f.write("\n")
PY

FINAL_EXIT=0
[ "$STATE" = failed ] && FINAL_EXIT=1

printf '  run %s: state=%s%s exit_code=%s wall_ms=%s -> %s\n' \
  "$RUN_ID" "$STATE" "${VOID_REASON:+ ($VOID_REASON)}" "$EXIT_CODE" "$WALL_MS" "$RUN_DIR"

exit "$FINAL_EXIT"
