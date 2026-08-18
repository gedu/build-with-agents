#!/bin/sh
#
# check.sh — structural invariants of this repository.
#
# The counterpart to hooks/pre-commit. That gate answers "does this contain something that
# must never be published". This one answers "does this repo still hold the shape its own
# rules describe". Redaction is not checked here; there is one gate for it and duplicating
# it would create a second pattern list to keep honest.
#
# WHAT IT CHECKS
#   1. Frontmatter, on every content `.md`. AGENTS.md documents six mandatory fields and
#      justifies them as a machine query interface — "give me the validated blocks for
#      react-native" is a query over exactly these fields. A typo in one of them makes a
#      file invisible to that query while it still reads correctly to a human, so the
#      schema needs a checker or it is a convention rather than an interface.
#   2. Every directory under `skills/` has an entry in `ASK.md`. `skills/README.md` states
#      the obligation ("a new skill needs its entry in ASK.md in the same commit") and
#      ASK.md states that a skill added without an entry is its only failure mode. Both
#      said so with nothing looking.
#
# WHAT IT DELIBERATELY DOES NOT CHECK
#   * Whether an ASK.md entry is any GOOD. It checks that the skill name appears there, not
#     that the phrasing reaches the skill. That claim is what keeps ASK.md `status: draft`,
#     and no checker can settle it.
#   * `targets` membership. AGENTS.md documents `react`, `react-native` and `any`, and
#     MAP.md lists five more as planned. A closed enum here would reject the first Node
#     block on the day it is written, so this checks the field is a non-empty list.
#   * `sources` resolvability. Entries may be URLs or repo-relative paths; opening either is
#     a different job with a network dependency this file will not take on.
#   * Anything under `rig/fixtures/`. Those files are inputs to the measurement harness and
#     imitate a foreign project on purpose; they are not repository content.
#
# WHICH FILES
#   Tracked files AND untracked files git would not ignore. Tracked-only was the obvious
#   choice and it is wrong: `./hooks/pre-commit --all` scans tracked files, and a file
#   written but not yet staged was invisible to it — recorded in
#   journal/2026-08-13-skills-nobody-could-ask-for.md. Checking a file you just wrote and
#   checking the tree are different operations, and this one does both.
#
# EXIT CODES
#   0  clean
#   1  a violation — the file and the field are named
#   2  the check could not run. NOT a pass. Never conflate with 0.
#
# USAGE
#   ./check.sh              check this repository
#   ./check.sh --self-test  build a throwaway repository and assert one exit code per case
#   ./check.sh --help       this header
#
# SELF-TEST
#   ADR 0013 — a committed executable carries its own test, exposed as a flag on that
#   executable. `--self-test` asserts that a well-formed fixture passes and that each
#   invariant, broken one at a time, is reported. A checker with no test is a claim.
#
# PORTABILITY
#   POSIX `sh`, `grep` and `awk`, not `rg`. Same rule as the hooks: this must run on a
#   machine that has not installed anything, and in CI without a setup step.

set -eu

LC_ALL=C
export LC_ALL

# Paths under these prefixes are not repository content. Keep the list short and justify
# every entry in the header above; it is an exemption from the repo-wide schema rule.
EXCLUDED_PREFIX='rig/fixtures/'

show_help() {
  awk 'NR>1 && /^#/ { sub(/^# ?/, ""); print; next } NR>1 { exit }' "$0"
}

die_cannot_run() {
  printf '\n  STRUCTURE CHECK COULD NOT RUN: %s\n  This is exit 2, not a pass.\n' "$1" >&2
  exit 2
}

VIOLATIONS=0
report() {
  if [ "$VIOLATIONS" -eq 0 ]; then
    printf '\n  STRUCTURE CHECK FAILED — this repo does not match its own rules.\n\n' >&2
  fi
  VIOLATIONS=$((VIOLATIONS + 1))
  printf '    %s\n' "$1" >&2
}

# One awk program over every content file. Written as a single pass so the duplicate-`id`
# check has every file in scope, and so an unreadable file aborts the whole run with awk
# exit 2 rather than being skipped in silence.
FRONTMATTER_AWK='
function violate(field, msg) {
  printf "%s: %s: %s\n", cur, field, msg
}
function scalar(v) {
  sub(/[ \t]+#.*$/, "", v)   # a trailing YAML comment is legal on a plain scalar
  sub(/[ \t]+$/, "", v)
  return v
}
function is_list(v) {
  return (v ~ /^\[.*\]$/)
}
function list_is_empty(v,   inner) {
  inner = v
  sub(/^\[/, "", inner)
  sub(/\]$/, "", inner)
  return (inner ~ /^[ \t]*$/)
}
function finish(   i, n, missing, v, id, mm, dd) {
  if (cur == "") return
  if (!opened) {
    violate("frontmatter", "no frontmatter block: line 1 is not `---`")
    return
  }
  if (!closed) {
    violate("frontmatter", "the frontmatter block is never closed by a second `---`")
    return
  }
  n = split("id type targets status verified sources", missing, " ")
  for (i = 1; i <= n; i++) {
    if (!(missing[i] in val)) violate(missing[i], "required field is missing")
  }

  if ("id" in val) {
    id = scalar(val["id"])
    if (id == "") violate("id", "is empty")
    else {
      if (id in id_owner) violate("id", "duplicate: already used by " id_owner[id])
      else id_owner[id] = cur
    }
  }
  if ("type" in val) {
    v = scalar(val["type"])
    if (v !~ /^(theory|block|template|decision|research|journal|skill|index)$/)
      violate("type", "`" v "` is not one of theory, block, template, decision, research, journal, skill, index")
  }
  if ("status" in val) {
    v = scalar(val["status"])
    if (v !~ /^(draft|validated|rejected)$/)
      violate("status", "`" v "` is not one of draft, validated, rejected")
  }
  if ("targets" in val) {
    v = val["targets"]
    sub(/[ \t]+$/, "", v)
    if (!is_list(v)) violate("targets", "`" v "` is not a list; write it as [any]")
    else if (list_is_empty(v)) violate("targets", "is an empty list; write [any] when the content is target-agnostic")
  }
  if ("verified" in val) {
    v = scalar(val["verified"])
    if (v !~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/)
      violate("verified", "`" v "` is not an ISO date (YYYY-MM-DD)")
    else {
      mm = substr(v, 6, 2) + 0
      dd = substr(v, 9, 2) + 0
      if (mm < 1 || mm > 12 || dd < 1 || dd > 31)
        violate("verified", "`" v "` is not a real calendar date")
    }
  }
  if ("sources" in val) {
    v = val["sources"]
    sub(/[ \t]+$/, "", v)
    if (!is_list(v)) violate("sources", "`" v "` is not a list; write it as [] or [\"path\"]")
    else if (list_is_empty(v) && "status" in val && scalar(val["status"]) == "validated")
      violate("sources", "is empty, and AGENTS.md requires a non-empty sources for status: validated")
  }
}
FNR == 1 {
  finish()
  cur = FILENAME
  delete val
  opened = ($0 == "---")
  closed = 0
  next
}
!closed && /^---[ \t]*$/ { closed = 1; next }
!closed && opened {
  if ($0 ~ /^[ \t]*$/) next
  if ($0 !~ /^[A-Za-z_]+:/) {
    violate("frontmatter", "line " FNR " is not `key: value`")
    next
  }
  k = $0; sub(/:.*$/, "", k)
  v = $0; sub(/^[A-Za-z_]+:[ \t]*/, "", v)
  if (k in val) violate(k, "is declared twice in the frontmatter block")
  val[k] = v
  next
}
END { finish() }
'

check_frontmatter() {
  FILES=""
  COUNT=0
  # -c core.quotePath=false keeps non-ASCII paths raw. A path containing a control
  # character is still quoted, and that is the one shape this newline-delimited list cannot
  # carry, so it escalates instead of being silently mis-parsed.
  LIST="$(git -c core.quotePath=false ls-files --cached --others --exclude-standard -- '*.md')" \
    || die_cannot_run "could not list the repository files"

  OLD_IFS="$IFS"
  IFS='
'
  for f in $LIST; do
    IFS="$OLD_IFS"
    case "$f" in
      '"'*) die_cannot_run "the path $f contains a control character; this checker cannot address it safely" ;;
      "$EXCLUDED_PREFIX"*) continue ;;
    esac
    [ -e "$f" ] || continue          # listed, then removed between the two calls
    # A tool entrypoint is a generated symlink to AGENTS.md (`./setup.sh --claude` and
    # friends). Reading one means reading AGENTS.md a second time under a second name, which
    # surfaces as a duplicate `id` — a violation the operator cannot fix, because the file is
    # not theirs to edit. `.gitignore` hides these, but only after `setup.sh` has written its
    # managed block, and that block is per-checkout and uncommitted: a clone, a fresh worktree
    # or a `git reset --hard` leaves it empty and the entrypoints visible again. Skipping the
    # symlink itself does not depend on that state. AGENTS.md: entrypoints are always symlinks
    # and are never committed, so no content file is lost here.
    [ -L "$f" ] && continue
    [ -r "$f" ] || die_cannot_run "'$f' is unreadable; a file that cannot be read is not a file that passed"
    if [ ! -s "$f" ]; then
      # awk never enters a zero-byte file, so it would be validated by nobody.
      report "$f: frontmatter: the file is empty"
      continue
    fi
    FILES="$FILES$f
"
    COUNT=$((COUNT + 1))
    IFS='
'
  done
  IFS="$OLD_IFS"

  [ "$COUNT" -gt 0 ] || die_cannot_run "no content .md files found; this checker had nothing to check"

  set +e
  FINDINGS="$(printf '%s' "$FILES" | tr '\n' '\0' | xargs -0 awk "$FRONTMATTER_AWK")"
  rc=$?
  set -e
  [ "$rc" -eq 0 ] || die_cannot_run "the frontmatter pass exited $rc; see the error above it"

  if [ -n "$FINDINGS" ]; then
    OLD_IFS="$IFS"
    IFS='
'
    for line in $FINDINGS; do
      IFS="$OLD_IFS"
      report "$line"
      IFS='
'
    done
    IFS="$OLD_IFS"
  fi

  FRONTMATTER_COUNT="$COUNT"
}

check_skills_are_askable() {
  SKILL_COUNT=0
  if [ ! -d skills ]; then
    SKILL_COUNT=-1
    return 0
  fi
  [ -f ASK.md ] || die_cannot_run "skills/ exists but ASK.md does not, so this check has no input to read"
  [ -r ASK.md ] || die_cannot_run "ASK.md is unreadable, so this check has no input to read"
  BT='`'
  for d in skills/*/; do
    [ -d "$d" ] || continue          # the glob stays literal when nothing matches
    name="${d#skills/}"
    name="${name%/}"
    # Matched in backticks because that is how ASK.md names them, and because a bare
    # substring match would let `gap` satisfy the obligation of `project-gap-analysis`.
    set +e
    grep -F -q -- "$BT$name$BT" ASK.md
    grc=$?
    set -e
    [ "$grc" -le 1 ] || die_cannot_run "grep exited $grc while reading ASK.md"
    [ "$grc" -eq 0 ] || report "skills/$name: ASK.md: no entry. skills/README.md requires one in the same commit"
    SKILL_COUNT=$((SKILL_COUNT + 1))
  done
}

self_test() {
  SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
  [ -x "$SELF" ] || die_cannot_run "could not locate this script in order to re-invoke it"

  TMP="$(mktemp -d)" || die_cannot_run "could not create a temporary directory"
  trap 'chmod -R u+rwX "$TMP" 2>/dev/null || :; rm -rf "$TMP"' EXIT

  ( cd "$TMP" && git init -q . ) >/dev/null 2>&1 \
    || die_cannot_run "could not create the temporary repository"

  FAILED=0

  expect() {
    set +e
    ( cd "$TMP" && "$SELF" ) >/dev/null 2>&1
    _got=$?
    set -e
    if [ "$_got" -eq "$1" ]; then
      printf '  ok    %s\n' "$2"
    else
      printf '  FAIL  %s — expected exit %s, got %s\n' "$2" "$1" "$_got" >&2
      FAILED=1
    fi
  }

  # write_fm <path> <id> <type> <targets> <status> <verified> <sources> <body>
  write_fm() {
    mkdir -p "$(dirname "$TMP/$1")"
    {
      printf -- '---\n'
      printf 'id: %s\n' "$2"
      printf 'type: %s\n' "$3"
      printf 'targets: %s\n' "$4"
      printf 'status: %s\n' "$5"
      printf 'verified: %s\n' "$6"
      printf 'sources: %s\n' "$7"
      printf -- '---\n\n# %s\n' "$8"
    } > "$TMP/$1"
  }

  fixture() {
    # Wipe the tree rather than naming what to delete. The enumerated form leaked: `other.md`,
    # written by the duplicate-id case, survived into every later case, and those cases still
    # passed because each one expected a non-zero exit and the leftover duplicate was just one
    # more violation in a run that was already failing. The first case to expect 0 is what
    # exposed it. A fixture that lists what to remove is a fixture that hides state as soon as
    # a case writes a path it does not know about.
    find "$TMP" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} + \
      || die_cannot_run "could not reset the self-test fixture"
    write_fm "ASK.md" "ask/index" "index" "[any]" "draft" "2026-08-17" "[]" "ask"
    printf '\nSay **"do the thing"** reaches `alpha`.\n' >> "$TMP/ASK.md"
    write_fm "skills/README.md" "skills/index" "index" "[any]" "draft" "2026-08-17" "[]" "skills"
    write_fm "skills/alpha/SKILL.md" "skills/alpha" "skill" "[any]" "draft" "2026-08-17" "[]" "alpha"
    write_fm "note.md" "note" "theory" "[react-native]" "validated" "2026-08-17" '["note.md"]' "note"
    # Not repository content: excluded by prefix, and deliberately has no frontmatter.
    mkdir -p "$TMP/rig/fixtures/proj"
    printf '# a fixture file, not repo content\n' > "$TMP/rig/fixtures/proj/contract.md"
  }

  fixture
  expect 0 "a well-formed tree passes, and rig/fixtures/ is out of scope"

  fixture
  # sed is avoided here on purpose: rewriting the file wholesale is unambiguous.
  write_fm "note.md" "note" "theory" "[any]" "validated" "2026-08-17" "[]" "note"
  expect 1 "status: validated with empty sources is reported"

  fixture
  write_fm "note.md" "note" "thoery" "[any]" "draft" "2026-08-17" "[]" "note"
  expect 1 "a type outside the documented enum is reported"

  fixture
  write_fm "note.md" "note" "theory" "[any]" "valdiated" "2026-08-17" "[]" "note"
  expect 1 "a status typo is reported"

  fixture
  write_fm "note.md" "note" "theory" "[any]" "draft" "17-08-2026" "[]" "note"
  expect 1 "a non-ISO verified date is reported"

  fixture
  write_fm "note.md" "note" "theory" "[any]" "draft" "2026-13-40" "[]" "note"
  expect 1 "an impossible calendar date is reported"

  fixture
  write_fm "note.md" "note" "theory" "any" "draft" "2026-08-17" "[]" "note"
  expect 1 "targets that is not a list is reported"

  fixture
  { printf -- '---\n'
    printf 'id: note\ntype: theory\ntargets: [any]\nstatus: draft\n'
    printf -- '---\n\n# note\n'
  } > "$TMP/note.md"
  expect 1 "missing required fields are reported"

  fixture
  printf '# no frontmatter at all\n' > "$TMP/note.md"
  expect 1 "a content file with no frontmatter block is reported"

  fixture
  : > "$TMP/note.md"
  expect 1 "an empty content file is reported rather than skipped by awk"

  fixture
  write_fm "other.md" "note" "theory" "[any]" "draft" "2026-08-17" "[]" "other"
  expect 1 "a duplicate id is reported"

  fixture
  write_fm "skills/beta/SKILL.md" "skills/beta" "skill" "[any]" "draft" "2026-08-17" "[]" "beta"
  expect 1 "a skill directory with no ASK.md entry is reported"

  fixture
  rm -f "$TMP/ASK.md"
  expect 2 "skills/ present and ASK.md missing escalates instead of passing"

  fixture
  chmod 000 "$TMP/note.md"
  expect 2 "an unreadable content file escalates instead of being skipped"
  chmod 644 "$TMP/note.md"

  # Found on this checker's first run against a real merged tree, not imagined: `git reset
  # --hard` reverted .gitignore's per-checkout managed block, the generated CLAUDE.md symlink
  # became visible again, and AGENTS.md was reported as a duplicate id of itself.
  fixture
  ln -s "note.md" "$TMP/ALIAS.md"
  expect 0 "a generated symlink entrypoint is skipped, not read as a second content file"
  rm -f "$TMP/ALIAS.md"

  [ "$FAILED" -eq 0 ] || {
    printf '\n  SELF-TEST FAILED — this checker is not behaving as specified.\n' >&2
    exit 1
  }
  printf '  self-test: all cases passed\n'
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
cd "$ROOT" || die_cannot_run "could not enter the repository root '$ROOT'"

check_frontmatter
check_skills_are_askable

if [ "$VIOLATIONS" -gt 0 ]; then
  printf '\n  %s violation(s). Fix them, per AGENTS.md and skills/README.md.\n' "$VIOLATIONS" >&2
  exit 1
fi

if [ "$SKILL_COUNT" -lt 0 ]; then
  printf '  structure check: clean across %s content files; no skills/ directory here\n' "$FRONTMATTER_COUNT"
else
  printf '  structure check: clean across %s content files and %s skill(s)\n' \
    "$FRONTMATTER_COUNT" "$SKILL_COUNT"
fi
exit 0
