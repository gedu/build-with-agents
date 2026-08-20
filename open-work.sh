#!/bin/sh
#
# open-work.sh - a generated index of what is open in this repository.
#
# The third of three root executables, and the only one that is not a gate. `hooks/pre-commit`
# answers "does this contain something that must never be published". `check.sh` answers "does
# this repo still hold the shape its own rules describe". This one answers "what is open", and
# it answers it by enumerating, never by ranking.
#
# WHY THIS IS NOT A FLAG ON check.sh
#   `check.sh` carries its answer in its exit code, where 1 means a violation. Open work is not
#   a violation - a repository with three open hypotheses is a healthy repository. A flag that
#   made `check.sh` exit 1 because work is open would be wrong, and one that exited 0 while
#   printing a report would put two contracts in one executable. `OPERATIONS.md` also maps
#   commands to moments, and these are different moments: `check.sh` runs after editing a
#   content file, this runs when a session starts. ADR 0016 carries the reasoning.
#
# WHAT IT READS - structure first, prose last
#   Five of the six sources are a directory listing or a frontmatter field, and `check.sh`
#   already verifies that schema on every content file. So this inherits a checked input
#   instead of introducing an unchecked one.
#
#     1. BACKLOG.md `###` entries       blocked work, each with its own named unblock condition
#     2. hypotheses/                    open claims with a declared test (ADR 0012: zero citability)
#     3. gaps/                          demand records below the two-occurrence threshold
#     4. decisions/ with status: draft  a decision made and not ratified
#     5. sdd/ outside sdd/archive/      a cycle still in flight
#     6. `## What is not settled`       declared-unsettled prose, wherever someone wrote it
#
#   Source 6 was proposed as the foundation of this index. Counted, it exists in two files,
#   both under `journal/`. It stays as the smallest input rather than the basis, because a
#   generated index built on a two-file marker would have read as complete while being nearly
#   empty - a worse failure than the stale hand-written table AGENTS.md already forbids.
#
# WHAT IT DELIBERATELY DOES NOT READ
#   * `status: draft` as an entry source. It covers well over half the content files here, most
#     of them simply unpromoted content. A signal matching half the repository ranks nothing.
#     It is printed under COVERAGE as a number, never as an entry.
#   * The body of anything it lists. The index points; the source states. Restating a blocked
#     entry's reasoning would create a second copy to keep honest, which is the drift AGENTS.md
#     forbids and the reason this file exists rather than a hand-written roadmap.
#   * Priority. The problem is "I do not know what is open", not "I do not know what order to
#     do it in". A ranking layer is added if this index shows it is needed, not before.
#
# ABSENT IS NOT EMPTY
#   A source that does not exist prints `absent`, never `0`. `hooks/commit-msg --range` already
#   carries the narrow form of this rule - it prints how many messages it scanned including
#   zero, because an empty range and a clean range are otherwise indistinguishable. A deleted
#   directory and a directory with nothing open are the same distinction one level up, and one
#   of them is good news while the other is a broken index.
#
# OUTPUT GOES TO STDOUT AND NOWHERE ELSE
#   Nothing is written to disk, so there is no generated file to gitignore, no managed block for
#   `setup.sh` to own, and no artifact that can be stale. Redirect it if you want a copy; that
#   copy is yours and this script will not refresh it.
#
#   It also prints no filesystem path outside the repository - not the checkout root, not a
#   temporary directory. This output is meant to be pasted into a session or an issue, and
#   ADR 0009 applies to anything that leaves the machine.
#
# EXIT CODES
#   0  the index was produced. Open work is not an error
#   2  could not run. NOT a pass, and never conflated with 0
#   There is deliberately no exit 1. This reports; it does not judge.
#
# USAGE
#   ./open-work.sh              print the index
#   ./open-work.sh --self-test  build a throwaway repository and assert the output
#   ./open-work.sh --help       this header
#
# SELF-TEST
#   ADR 0013 - a committed executable carries its own test, exposed as a flag on that
#   executable. A checker may assert exit codes alone, because for a checker the exit code IS
#   the output. For a generator it is not: a script that exits 0 and prints nothing would sail
#   through such a test. So every case here asserts what was printed, not only what was
#   returned.
#
# PORTABILITY
#   POSIX `sh`, `grep -E` and `awk`, never `rg`. Same rule as the hooks and `check.sh`: this
#   must run on a machine that has not installed anything, and in CI with no setup step.

set -eu

LC_ALL=C
export LC_ALL

# Same exemption `check.sh` takes, for the same reason: these imitate a foreign project and are
# inputs to the measurement harness, not repository content.
EXCLUDED_PREFIX='rig/fixtures/'

TOTAL=0
SOURCES=0

show_help() {
  awk 'NR>1 && /^#/ { sub(/^# ?/, ""); print; next } NR>1 { exit }' "$0"
}

die_cannot_run() {
  printf '\n  OPEN-WORK INDEX COULD NOT RUN: %s\n  This is exit 2, not an empty index.\n' "$1" >&2
  exit 2
}

head_row() {
  # <title> <source label> <state>
  SOURCES=$((SOURCES + 1))
  printf '\n  %-52s %s: %s\n' "$1" "$2" "$3"
}

item()    { printf '      %s\n' "$1"; }
detail()  { printf '        %s\n' "$1"; }

# Read one frontmatter scalar. Prints nothing when the file has no frontmatter block, which is
# a shape `check.sh` reports; this file is not a second checker and stays quiet about it.
fm_field() {
  awk -v want="$2" '
    NR == 1 && $0 != "---" { exit }
    NR > 1 && /^---[ \t]*$/ { exit }
    NR > 1 {
      k = $0; sub(/:.*$/, "", k)
      if (k == want) {
        v = $0
        sub(/^[A-Za-z_]+:[ \t]*/, "", v)
        sub(/[ \t]+#.*$/, "", v)
        sub(/[ \t]+$/, "", v)
        print v
        exit
      }
    }
  ' "$1"
}

# Every content .md, by the same rule `check.sh` uses: tracked AND untracked-not-ignored, minus
# the fixture prefix, minus generated symlink entrypoints. A file written and not yet staged is
# open work too, so tracked-only would be the wrong list here for the same reason it was there.
collect_content() {
  CONTENT=''
  CONTENT_COUNT=0
  # Sorted, because `--cached` and `--others` are emitted in two runs and a file's staging
  # state would otherwise reorder the index. A generated artifact that renders differently
  # from one moment to the next cannot be diffed, and this repo already holds that rule for
  # `rig/derive.py`: reproducing byte-identically is the cheapest proof of a function.
  LIST="$(git -c core.quotePath=false ls-files --cached --others --exclude-standard -- '*.md' | sort)" \
    || die_cannot_run "could not list the repository files"

  OLD_IFS="$IFS"
  IFS='
'
  for f in $LIST; do
    IFS="$OLD_IFS"
    case "$f" in
      '"'*) die_cannot_run "the path $f contains a control character; this index cannot address it safely" ;;
      "$EXCLUDED_PREFIX"*) IFS='
'; continue ;;
    esac
    if [ ! -e "$f" ]; then IFS='
'; continue; fi
    if [ -L "$f" ]; then IFS='
'; continue; fi
    [ -r "$f" ] || die_cannot_run "'$f' is unreadable; an index that skipped it would under-report"
    CONTENT="$CONTENT$f
"
    CONTENT_COUNT=$((CONTENT_COUNT + 1))
    IFS='
'
  done
  IFS="$OLD_IFS"

  [ "$CONTENT_COUNT" -gt 0 ] || die_cannot_run "no content .md files found; this index had nothing to read"
}

# --- source 1: BACKLOG.md ----------------------------------------------------------------
BACKLOG_AWK='
function emit() {
  if (t == "") return
  if (length(b) > 92) b = substr(b, 1, 92) "..."
  printf "%s\t%s\n", t, b
}
/^### / {
  emit()
  t = $0
  sub(/^###[ \t]+/, "", t)
  sub(/^[0-9]+\.[ \t]*/, "", t)
  b = ""
  next
}
/^\*\*Blocked on\*\*/ {
  if (t != "" && b == "") {
    b = $0
    sub(/^\*\*Blocked on\*\*:?[ \t]*/, "", b)
  }
  next
}
END { emit() }
'

section_backlog() {
  if [ ! -e BACKLOG.md ]; then
    head_row "BLOCKED, WITH A NAMED UNBLOCK CONDITION" "BACKLOG.md" "absent"
    detail "the file this repo records blocked work in does not exist here"
    return 0
  fi
  [ -r BACKLOG.md ] || die_cannot_run "BACKLOG.md exists but is unreadable, so this index would under-report"

  ROWS="$(awk "$BACKLOG_AWK" BACKLOG.md)" || die_cannot_run "the BACKLOG.md pass failed"
  n=0
  if [ -n "$ROWS" ]; then
    n="$(printf '%s\n' "$ROWS" | wc -l | tr -d ' ')"
  fi
  head_row "BLOCKED, WITH A NAMED UNBLOCK CONDITION" "BACKLOG.md" "$n"
  [ "$n" -eq 0 ] && return 0

  OLD_IFS="$IFS"
  IFS='
'
  for line in $ROWS; do
    IFS="$OLD_IFS"
    title="${line%%	*}"
    blocked="${line#*	}"
    item "$title"
    if [ -n "$blocked" ] && [ "$blocked" != "$title" ]; then
      detail "unblock: $blocked"
    else
      detail "unblock: NOT STATED - BACKLOG.md requires one; an entry without it is a wish"
    fi
    IFS='
'
  done
  IFS="$OLD_IFS"
  TOTAL=$((TOTAL + n))
}

# --- sources 2 and 3: a directory of numbered records ------------------------------------
section_dir() {
  # <dir> <title> <note>
  d="$1"
  if [ ! -d "$d" ]; then
    head_row "$2" "$d/" "absent"
    return 0
  fi
  [ -r "$d" ] || die_cannot_run "$d/ exists but is unreadable, so this index would under-report"

  found=''
  n=0
  for f in "$d"/*.md; do
    [ -f "$f" ] || continue
    case "$f" in "$d"/README.md) continue ;; esac
    base="${f##*/}"
    found="$found${base%.md}
"
    n=$((n + 1))
  done
  head_row "$2" "$d/" "$n"
  [ -n "$3" ] && detail "$3"
  if [ "$n" -gt 0 ]; then
    OLD_IFS="$IFS"
    IFS='
'
    for e in $found; do
      IFS="$OLD_IFS"
      item "$e"
      IFS='
'
    done
    IFS="$OLD_IFS"
    TOTAL=$((TOTAL + n))
  fi
}

# --- source 4: an ADR decided but not ratified -------------------------------------------
section_unratified() {
  if [ ! -d decisions ]; then
    head_row "DECIDED, NOT RATIFIED" "decisions/" "absent"
    return 0
  fi
  found=''
  n=0
  for f in decisions/*.md; do
    [ -f "$f" ] || continue
    case "$f" in decisions/README.md) continue ;; esac
    [ -r "$f" ] || die_cannot_run "'$f' is unreadable, so this index would under-report"
    st="$(fm_field "$f" status)"
    [ "$st" = "draft" ] || continue
    base="${f##*/}"
    found="$found${base%.md}
"
    n=$((n + 1))
  done
  head_row "DECIDED, NOT RATIFIED" "decisions/" "$n"
  detail "status: draft on an ADR means the reasoning stands and the operator has not ratified it"
  if [ "$n" -gt 0 ]; then
    OLD_IFS="$IFS"
    IFS='
'
    for e in $found; do
      IFS="$OLD_IFS"
      item "$e"
      IFS='
'
    done
    IFS="$OLD_IFS"
    TOTAL=$((TOTAL + n))
  fi
}

# --- source 5: an SDD cycle that has not been archived -----------------------------------
section_sdd() {
  if [ ! -d sdd ]; then
    head_row "SDD CYCLES IN FLIGHT" "sdd/" "absent"
    return 0
  fi
  found=''
  n=0
  for d in sdd/*/; do
    [ -d "$d" ] || continue
    case "$d" in sdd/archive/) continue ;; esac
    name="${d#sdd/}"
    found="$found${name%/}
"
    n=$((n + 1))
  done
  head_row "SDD CYCLES IN FLIGHT" "sdd/" "$n"
  detail "archiving is what closes a cycle; anything outside sdd/archive/ is still open"
  if [ "$n" -gt 0 ]; then
    OLD_IFS="$IFS"
    IFS='
'
    for e in $found; do
      IFS="$OLD_IFS"
      item "$e"
      IFS='
'
    done
    IFS="$OLD_IFS"
    TOTAL=$((TOTAL + n))
  fi
}

# --- source 6: the prose convention ------------------------------------------------------
section_not_settled() {
  found=''
  n=0
  OLD_IFS="$IFS"
  IFS='
'
  for f in $CONTENT; do
    IFS="$OLD_IFS"
    set +e
    grep -E -q '^#{2,}[ \t]+What is not settled' -- "$f"
    grc=$?
    set -e
    [ "$grc" -le 1 ] || die_cannot_run "grep exited $grc while reading '$f'"
    if [ "$grc" -eq 0 ]; then
      found="$found$f
"
      n=$((n + 1))
    fi
    IFS='
'
  done
  IFS="$OLD_IFS"

  head_row "DECLARED UNSETTLED, IN PROSE" '`## What is not settled`' "$n files"
  detail "reported, never judged: that a file declares itself unsettled is the claim"
  if [ "$n" -gt 0 ]; then
    OLD_IFS="$IFS"
    IFS='
'
    for e in $found; do
      IFS="$OLD_IFS"
      item "$e"
      IFS='
'
    done
    IFS="$OLD_IFS"
    TOTAL=$((TOTAL + n))
  fi
}

# --- coverage ----------------------------------------------------------------------------
section_coverage() {
  drafts=0
  OLD_IFS="$IFS"
  IFS='
'
  for f in $CONTENT; do
    IFS="$OLD_IFS"
    st="$(fm_field "$f" status)"
    [ "$st" = "draft" ] && drafts=$((drafts + 1))
    IFS='
'
  done
  IFS="$OLD_IFS"

  printf '\n  COVERAGE - what this index can and cannot see\n'
  detail "$CONTENT_COUNT content .md scanned: tracked and untracked-not-ignored, minus ${EXCLUDED_PREFIX} and generated symlinks"
  detail "status: draft covers $drafts of them, so it is NOT an entry source here (ADR 0016)"
  detail "'absent' above means the source is missing, which is not the same as empty"
  detail "a convention nobody has written yet is invisible to this: the counts are the only warning"
}

# --- self-test ---------------------------------------------------------------------------
self_test() {
  SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
  [ -x "$SELF" ] || die_cannot_run "could not locate this script in order to re-invoke it"

  TMP="$(mktemp -d)" || die_cannot_run "could not create a temporary directory"
  trap 'chmod -R u+rwX "$TMP" 2>/dev/null || :; rm -rf "$TMP"' EXIT

  ( cd "$TMP" && git init -q . ) >/dev/null 2>&1 \
    || die_cannot_run "could not create the temporary repository"

  FAILED=0
  CASE=''
  OUT=''
  RC=0

  run_index() {
    set +e
    OUT="$( cd "$TMP" && "$SELF" 2>&1 )"
    RC=$?
    set -e
  }

  ok()   { printf '  ok    %s\n' "$1"; }
  bad()  { printf '  FAIL  %s - %s\n' "$CASE" "$1" >&2; FAILED=1; }

  assert_rc() {
    if [ "$RC" -eq "$1" ]; then ok "$CASE: exit $1"; else bad "expected exit $1, got $RC"; fi
  }
  assert_out() {
    if printf '%s\n' "$OUT" | grep -F -q -- "$1"; then
      ok "$CASE: prints '$1'"
    else
      bad "expected the output to contain '$1'"
    fi
  }
  assert_not_out() {
    if printf '%s\n' "$OUT" | grep -F -q -- "$1"; then
      bad "the output must not contain '$1'"
    else
      ok "$CASE: does not print '$1'"
    fi
  }
  # Same assertion, for a needle that must not be echoed either. The absolute-path case is
  # the reason it exists: printing the needle to prove the needle is absent puts the string
  # back on the terminal this script's header promises to keep it off.
  assert_absent_quiet() {
    if printf '%s\n' "$OUT" | grep -F -q -- "$1"; then
      bad "the output must not contain $2"
    else
      ok "$CASE: does not print $2"
    fi
  }

  # write_fm <path> <id> <type> <status> <body>
  write_fm() {
    mkdir -p "$(dirname "$TMP/$1")"
    {
      printf -- '---\n'
      printf 'id: %s\n' "$2"
      printf 'type: %s\n' "$3"
      printf 'targets: [any]\n'
      printf 'status: %s\n' "$4"
      printf 'verified: 2026-08-19\n'
      printf 'sources: []\n'
      printf -- '---\n\n# %s\n' "$5"
    } > "$TMP/$1"
  }

  # Wipe rather than enumerate what to remove: `check.sh`'s self-test recorded that an
  # enumerated reset leaks a file the next case does not know about, and the leak stays
  # invisible while every case expects the same result.
  fixture() {
    find "$TMP" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} + \
      || die_cannot_run "could not reset the self-test fixture"

    write_fm "BACKLOG.md" "backlog" "index" "draft" "backlog"
    {
      printf '\n## Entries\n\n'
      printf '### 1. Alpha practice - blocked on recurrence\n\n'
      printf '**Blocked on**: a second independent occurrence.\n\n'
      printf '### 2. Beta deliverable - blocked on promotion\n\n'
      printf '**Blocked on**: the evidence reaching theory/ first.\n'
    } >> "$TMP/BACKLOG.md"

    write_fm "hypotheses/README.md" "hypotheses/index" "index" "draft" "hypotheses"
    write_fm "hypotheses/0001-a-claim.md" "hypotheses/0001-a-claim" "research" "draft" "a claim"

    write_fm "gaps/README.md" "gaps/index" "index" "draft" "gaps"
    write_fm "gaps/0001-a-project.md" "gaps/0001-a-project" "research" "validated" "a project"

    write_fm "decisions/0001-ratified.md" "decisions/0001-ratified" "decision" "validated" "ratified"
    write_fm "decisions/0002-unratified.md" "decisions/0002-unratified" "decision" "draft" "unratified"

    write_fm "sdd/README.md" "sdd/index" "index" "draft" "sdd"
    write_fm "sdd/in-flight/spec.md" "sdd/in-flight/spec" "index" "draft" "spec"
    write_fm "sdd/archive/2026-01-01-done/spec.md" "sdd/archive/done/spec" "index" "draft" "done"

    write_fm "journal/2026-08-19-a-note.md" "journal/a-note" "journal" "draft" "a note"
    printf '\n## What is not settled\n\nSomething.\n' >> "$TMP/journal/2026-08-19-a-note.md"

    # Not repository content: excluded by prefix, and carries a marker that must be ignored.
    mkdir -p "$TMP/rig/fixtures/proj"
    printf '## What is not settled\n\nfixture noise\n' > "$TMP/rig/fixtures/proj/notes.md"
  }

  CASE="a well-formed tree"
  fixture; run_index
  assert_rc 0
  assert_out "BACKLOG.md: 2"
  assert_out "Alpha practice - blocked on recurrence"
  assert_out "unblock: a second independent occurrence."
  assert_out "hypotheses/: 1"
  assert_out "gaps/: 1"
  assert_out "decisions/: 1"
  assert_out "0002-unratified"
  assert_out "sdd/: 1"
  assert_out "in-flight"
  assert_out "1 files"
  assert_out "journal/2026-08-19-a-note.md"
  assert_out "COVERAGE"

  CASE="README.md is not a record"
  assert_not_out "hypotheses/README"

  CASE="an archived cycle is closed, not open"
  assert_not_out "2026-01-01-done"

  CASE="a ratified ADR is not open work"
  assert_not_out "0001-ratified"

  CASE="rig/fixtures/ is out of scope even when it carries the marker"
  assert_not_out "rig/fixtures/proj/notes.md"

  CASE="no absolute path leaks into output"
  assert_absent_quiet "$TMP" "the checkout's absolute path"

  CASE="a missing source prints absent, not zero"
  fixture; rm -f "$TMP/BACKLOG.md"; rm -rf "$TMP/gaps"; run_index
  assert_rc 0
  assert_out "BACKLOG.md: absent"
  assert_out "gaps/: absent"
  assert_not_out "BACKLOG.md: 0"

  CASE="an empty source prints zero, not absent"
  fixture; rm -f "$TMP/hypotheses/0001-a-claim.md"; run_index
  assert_rc 0
  assert_out "hypotheses/: 0"
  assert_not_out "hypotheses/: absent"

  CASE="a backlog entry with no unblock condition is named as such"
  fixture
  write_fm "BACKLOG.md" "backlog" "index" "draft" "backlog"
  printf '\n### 1. A wish with no trigger\n\nnothing here.\n' >> "$TMP/BACKLOG.md"
  run_index
  assert_rc 0
  assert_out "unblock: NOT STATED"

  CASE="an existing but unreadable declared source escalates"
  fixture; chmod 000 "$TMP/BACKLOG.md"; run_index
  assert_rc 2
  assert_out "This is exit 2"
  chmod 644 "$TMP/BACKLOG.md"

  CASE="an unreadable content file escalates rather than being skipped"
  fixture; chmod 000 "$TMP/journal/2026-08-19-a-note.md"; run_index
  assert_rc 2
  chmod 644 "$TMP/journal/2026-08-19-a-note.md"

  CASE="a tree with no content files escalates instead of printing an empty index"
  fixture
  find "$TMP" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
  run_index
  assert_rc 2

  CASE="outside a git repository it cannot run"
  NOGIT="$(mktemp -d)" || die_cannot_run "could not create a second temporary directory"
  set +e
  ( cd "$NOGIT" && "$SELF" ) >/dev/null 2>&1
  RC=$?
  set -e
  rm -rf "$NOGIT"
  OUT=''
  assert_rc 2

  [ "$FAILED" -eq 0 ] || {
    printf '\n  SELF-TEST FAILED - this generator is not behaving as specified.\n' >&2
    exit 1
  }
  printf '\n  self-test: all cases passed\n'
  exit 0
}

case "${1:-}" in
  "")           : ;;
  --help)       show_help; exit 0 ;;
  --self-test)  self_test ;;
  *)            die_cannot_run "unknown argument '$1'. Use no argument, --self-test, or --help." ;;
esac

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" \
  || die_cannot_run "this is not a git repository, so there is nothing to enumerate"
cd "$ROOT" || die_cannot_run "could not enter the repository root"

collect_content

set +e
REV="$(git rev-parse --short HEAD 2>/dev/null)"
set -e
[ -n "$REV" ] || REV='no commit yet'

BODY="$(
  section_backlog
  section_dir hypotheses "OPEN CLAIMS, ZERO CITABILITY (ADR 0012)" \
    "a declared test with no result. Nothing here may be cited, not even as evidence"
  section_dir gaps "DEMAND RECORDS, BELOW THE BUILD THRESHOLD" \
    "two independent records for the same demand are what build a block; see gaps/README.md"
  section_unratified
  section_sdd
  section_not_settled
  printf '__TOTAL__%s\n' "$TOTAL"
  printf '__SOURCES__%s\n' "$SOURCES"
)" || die_cannot_run "an index section failed; nothing above it is trustworthy"

TOTAL="$(printf '%s\n' "$BODY" | awk -F'__TOTAL__' '/^__TOTAL__/ { print $2 }')"
SOURCES="$(printf '%s\n' "$BODY" | awk -F'__SOURCES__' '/^__SOURCES__/ { print $2 }')"

printf '\n  OPEN WORK - %s item(s) across %s source(s), at %s\n' "$TOTAL" "$SOURCES" "$REV"
printf '  Generated by ./open-work.sh. Nothing here is hand-maintained; re-run to refresh.\n'
printf '%s\n' "$BODY" | grep -v -E '^__(TOTAL|SOURCES)__'
section_coverage
printf '\n'
exit 0
