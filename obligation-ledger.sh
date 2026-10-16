#!/bin/sh
#
# obligation-ledger.sh - what did this change make somebody else's sentence wrong about?
#
# WHAT QUESTION THIS ANSWERS
#   S1 guarantees (c) and (d): "arreglo o actualizo las dependencias que implicaban por ese cambio"
#   and "arreglo o mejoro lo que tenia que hacerse debido al cambio". Both describe obligations an
#   ACT creates: a line moves, a count changes, a claim about a tool ages. Before this file,
#   nothing enumerated them. The feature Log's own table (L7) records that five of the seven
#   obligations a single commit created were found by a grep someone CHOSE to run, and none by a
#   check that fired. This file turns that habit into the classes below.
#
# WHY THIS IS NOT A GATE
#   Exit codes are open-work.sh's, deliberately: 0 means the ledger was produced, 2 means it could
#   not run, and there is no exit 1 outside --self-test. An open obligation is not a violation - a
#   repository with stale citations is a repository that kept working - and a report that exits 1
#   whenever it finds anything trains people to walk past it. This reports; a human judges which
#   findings to discharge. What CI may do (and WU3 does) is run it where nobody can skip it.
#
# THE ONE RULE EVERY CLASS FOLLOWS
#   A zero must be earned. Every class prints the denominator it scanned, a class with no
#   population prints ABSENT (never an empty pass), and --range over zero commits is exit 2 - the
#   exact vacuous pass ./hooks/commit-msg --range HEAD HEAD still commits and gaps/0004 was
#   written about. UNDECIDABLE is its own verdict: a cite the ledger cannot judge is printed as
#   such, never folded into the pass column (absent is not empty, one level down; a
#   cannot-decide is never a satisfied).
#
# THE CORPUS, AND WHY IT IS NOT RE-DERIVED
#   Content files come from ./open-work.sh --list-content, the seam that flag exists for. A ledger
#   that enumerated content itself would be the second copy of a rule this repository has already
#   been burned by twice (two hooks, two pattern lists; two counters, one stale). Source files
#   (.sh, .py outside rig/fixtures/) are added from the git index - they are the targets citations
#   resolve into and the definitions the symbol inventory is built from, and they are not .md, so
#   --list-content cannot carry them. The absence of the seam is could-not-run, never a degraded
#   private enumeration: the self-test plants a repository with no open-work.sh and asserts exit 2.
#
#   journal/ and sdd/archive/ are PROVENANCE scope: their findings are counted and named, never
#   listed as obligations. A dated record is provenance, not a pointer to maintain - the rule T2
#   already applied to journal/2026-08-19 ("six sources", left standing on purpose). sdd/ outside
#   archive is live: a cycle in flight owes its citations.
#
# THE CLASSES
#   C1 citation resolves to what it names. For every path:line cite, the cited lines must contain
#      at least one symbol the citing line itself names, where a symbol means a name DEFINED in a
#      committed source file (shell function, python def/class, or top-level assignment) of six or
#      more characters or containing an underscore. Zero such anchors is UNDECIDABLE, not FAIL:
#      this rule fires on both real defects this feature found by hand (a DIRTY_OK cite pointing
#      156 lines from its guard; a TIMEOUT_S cite pointing at a comment) with precision 2/2 on a
#      prototype, and folding an unanchorable cite into the FAIL column is how a check starts
#      crying wolf and gets disabled. A length-and-shape floor was measured necessary: a bare
#      "pass" token resolved against a test-helper named pass() in another file - a coincidence
#      that would have manufactured a false FAIL.
#      A cite whose line carries the house age-marker (was ...) is HISTORICAL: provenance kept on
#      purpose, checked before the anchor test because an age-marker needs no anchors to mean it.
#   C1a a cite past the file's end is FAIL by line count alone - no anchors needed, and it beats
#      the age-marker: a line beyond the last line was never true at any time. This is what
#      catches a cite that was never true: measured, two evidence lines in this feature's own spec
#      name line 329 of a 327-line file, in the commit that wrote them.
#   C2 hand-stated counts against generators. Only inside type: index files, and only for nouns a
#      generator actually prints (content files, item(s), source(s), skill(s), demand records).
#      A count of something nothing counts is not this class - it is prose (L14: the irreducible
#      "two independent occurrences" stays prose on purpose).
#   C3 a hash quoted in live prose that IS a git object and resolves from no ref. Reported, never
#      condemned: that hash is the evidence the object existed - the recovered dangling commit
#      this whole feature rests on (L9) - and deleting the citation destroys recovery provenance.
#      A hex token that is no git object at all is a digest prefix, and digests are not this class
#      (measured on the live tree: 5 of the 8 tokens a naive rule flagged were sha256 prefixes).
#   C4 a claim asserting a VALUE for a tool's response field must name the endpoint whose
#      semantics it asserts, within the line or its two neighbours. The guard is assertion shape
#      (a digit glued to the field token through nothing but markup and spacing) plus an endpoint
#      window: measured naive, most of the bare mentions were prose ABOUT the defect, not
#      assertions of a value, and a guard that flags its own documentation is a wolf-cry.
#      The field token must be RESPONSE-SHAPED - `total_count`, or a dotted token carrying an
#      underscore - because a first draft accepted any dotted token, which made every file cite
#      an assertion (`spec.md:419` became "the field .md asserts 419") and turned 4 real claims
#      into 29 reports. That is the class this file exists to close, rebuilt inside itself: a
#      rule whose shape is too wide cries wolf once and gets walked past forever (rule (d)).
#   C5 a derived count in an index file must be pinned to fixed objects. A revision range ending
#      in main / origin/main / HEAD beside a number is a sentence built to rot - L15, met twice in
#      one day here, and gaps/README.md's own correction is the fixed-objects exemplar.
#   D1 lockfile older than the manifest it locks. Population is discovered from the index. ABSENT
#      in this repository today (the only lockfiles are inside the frozen fixtures) - and the
#      ABSENT line must not read like a pass, because a JS consumer running this same file WOULD
#      have population.
#   D2 a committed generated artifact older (by last commit) than a committed file that WRITES
#      it. The writers are DISCOVERED - a tracked source naming both the artifact directory and
#      the derived-table filename, and carrying a write primitive - never listed, because a
#      hardcoded pair-list is the failure class T9 just closed. This file never RUNS the writer:
#      it compares commit times and says what to re-derive. (Running the writer here would be
#      wrong twice: the rig's real gate cannot run in a tree without the gitignored capture
#      directory, and a report that mutates what it reports is L11's truncation incident.)
#   D3 (--range) citations INTO paths the range changed, judged per cite with C1's verdicts, plus
#      a CHECK naming every index file that mentions a changed path - the L7 table mechanised.
#   D4 (--range) who calls what the range touched, at the two levels this repo can decide: files
#      invoked by name from another source or workflow, and functions called from a file that does
#      not define them - either in the call shape `name(` (python, command substitutions) or as a
#      line-initial bare shell invocation `name args`. The line-initial form is what shell files
#      actually use; a first draft matched only `name(` and would have reported zero shell call
#      edges in a repository that is mostly shell. Cross-file PROSE mentions of a symbol are still
#      not this class: 117 of 282 names would "cross-reference" that way, which is noise, not a
#      call graph.
#
# WHAT THIS CANNOT SEE (printed as a COVERAGE block with every run)
#   * Prose counts and claims with no path:line form - "all five currently resolve", "late by
#     one". L17's class needs a second reader, not this ledger; the UNDECIDABLE count is the
#     honest ceiling of what a machine can judge here.
#   * A citation wrapping across two comment lines - matched by nothing that reads one line. One
#     such cite exists in live scope (measured); named as a limit, not a defect (rule (g)).
#   * Meaning. A cite whose anchor token appears in the target by coincidence resolves here and
#     may still be false in the sense that matters. C1 is a floor, not a ceiling.
#   * A moved symbol whose name never changes and whose cite shares no token with its definition
#     line (the `moved it to 498` family): UNDECIDABLE by construction. Anchor cites to symbol
#     names or to section headers, never to bare numbers (L15).
#
# EXIT CODES
#   0  the ledger was produced. Findings live in the report, not in the exit code.
#   2  could not run: not a repository, the --list-content seam absent or refusing, --range naming
#      zero commits or an unresolvable revision, or an unreadable argument. NEVER conflated with 0.
#
# USAGE
#   ./obligation-ledger.sh                audit the tree as it stands (C1-C5, D1, D2)
#   ./obligation-ledger.sh --range A B    add the derived classes D3, D4 for what A..B changed
#   ./obligation-ledger.sh --self-test    throwaway repositories, one planted violation per class
#   ./obligation-ledger.sh --help         this header
#   (--range with '-' as an endpoint is refused, loudly: an unbounded scan is what the no-argument
#   mode above already is, and dressing it up as a review range would be decoration.)
#
# PORTABILITY
#   POSIX sh, awk, grep -E. No python3 - OPERATIONS.md marks it Rig-only, and this is a root
#   executable, which must run on a machine that has installed nothing. No rg, same reason.
#   BSD and GNU both: no interval expressions in awk (macOS awk ignores them silently - measured),
#   no bash-only ${var//} substitution, no backtick inside a double-quoted string.
#   Prints repository-relative paths only: ADR 0009 applies to anything this prints.

set -eu

LC_ALL=C
export LC_ALL

BT="$(printf '\140')"     # one backtick, built rather than written: a literal one inside
BTAB="$(printf '\t')"     # double quotes would start a command substitution at parse time.

die_cannot_run() {
  printf '\n  OBLIGATION LEDGER COULD NOT RUN: %s\n  This is exit 2, not an empty ledger. A ledger that read nothing cannot report a pass.\n' "$1" >&2
  exit 2
}

show_help() {
  awk 'NR>1 && /^#/ { sub(/^# ?/, ""); print; next } NR>1 { exit }' "$0"
}

# SELF-TEST (ADR 0013, S8)
# Built from throwaway repositories under mktemp, never from this repository: a self-test that
# asserted THIS tree's counts would rot the moment anything here was committed (L8), and one that
# planted violations in the real tree would be the redaction gate's own nightmare. Every case
# asserts what was PRINTED, not only the exit code - for a report, the lines are the product.
# One planted violation per class (S8), plus the guards that prove the scoping is real: a
# C2 phrase outside index scope and a C4 claim WITH an endpoint must both stay silent, because a
# check that flags correct text is a check that gets walked past (rule (d)).
self_test() {
  SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
  [ -x "$SELF" ] || { printf 'self-test: cannot locate this script to re-invoke it\n' >&2; exit 2; }
  ST="$(mktemp -d)" || { printf 'self-test: cannot create a temporary directory\n' >&2; exit 2; }
  trap 'rm -rf "$ST"' EXIT

  FAILED=0; CASE=''; OUT=''; RC=0
  OF="$ST/out"

  ok()  { printf '  ok    %s\n' "$1"; }
  bad() {
    printf '  FAIL  %s - %s\n' "$CASE" "$1" >&2
    # A failing assertion must show what it actually saw. Without this, one broken fixture reads
    # as thirty-six broken classes, and the first thing anyone reaches for is editing the
    # assertions - which is how a suite starts agreeing with a broken implementation. Bounded to
    # the head, because the point is the first unexpected line, not the whole report.
    printf '        (exit %s; first lines were:\n' "$RC" >&2
    printf '%s\n' "$OUT" | sed -n '1,6p' | sed 's/^/        | /' >&2
    printf '        )\n' >&2
    FAILED=1
  }
  assert_rc() {
    if [ "$RC" -eq "$1" ]; then ok "$CASE: exit $1"; else bad "expected exit $1, got $RC"; fi
  }
  assert_out() {
    if printf '%s\n' "$OUT" | grep -qF -- "$1"; then ok "$CASE: prints '$1'"
    else bad "expected the output to contain '$1'"; fi
  }
  assert_absent() {
    if printf '%s\n' "$OUT" | grep -qF -- "$1"; then bad "the output must not contain '$1'"
    else ok "$CASE: does not print '$1'"; fi
  }
  assert_count() {
    c="$(printf '%s\n' "$OUT" | grep -cF -- "$1" || true)"
    if [ "${c:-0}" -eq "$2" ]; then ok "$CASE: '$1' appears $2 time(s)"
    else bad "expected '$1' exactly $2 time(s), got ${c:-0}"; fi
  }
  # Anchored regex count. The verdict vector is asserted as an ANCHORED line, because a substring
  # test on 'HISTORICAL 1' also matches 'HISTORICAL 10' - an off-by-nine is exactly what a
  # counting check must not miss. Pipes are [|] so ERE reads them literally on BSD and GNU alike.
  assert_re() {
    c="$(printf '%s\n' "$OUT" | grep -cE -- "$1" || true)"
    if [ "${c:-0}" -eq "$2" ]; then ok "$CASE: /$1/ matches $2 line(s)"
    else bad "expected /$1/ to match exactly $2 line(s), got ${c:-0}"; fi
  }

  run_in() {
    d="$1"; shift
    set +e
    ( cd "$d" && "$SELF" "$@" ) > "$OF" 2>&1
    RC=$?
    set -e
    OUT="$(cat "$OF")"
  }

  new_repo() {
    R="$ST/$1"; rm -rf "$R"; mkdir -p "$R"
    ( cd "$R" && git init -q . \
        && git config user.email selftest@example.invalid \
        && git config user.name selftest ) >/dev/null 2>&1 \
      || { printf 'self-test: could not create a temporary repository\n' >&2; exit 2; }
  }

  cmt() {  # cmt <dir> <epoch> <message> - '@<epoch> +0000' is the form git parses as an exact
           # timestamp; a bare integer goes through approxidate and silently means something else.
    ( cd "$1" && export GIT_AUTHOR_DATE="@$2 +0000" GIT_COMMITTER_DATE="@$2 +0000" \
        && git add -A >/dev/null 2>&1 && git commit -qm "$3" >/dev/null 2>&1 )
  }

  fm() {  # fm <id> <type>
    printf -- '---\nid: %s\ntype: %s\ntargets: [any]\nstatus: validated\nverified: 2026-08-04\nsources: []\n---\n' "$1" "$2"
  }

  seam() {  # the --list-content contract this ledger consumes; a real seam, not a mock of a helper
    # Written with a QUOTED heredoc, not printf with nested quotes. The first draft assembled the
    # line through the '"'"' idiom and got it one character wrong, so the generated open-work.sh
    # carried an unterminated quote and died at parse time - which the suite reported as 36 failed
    # classes when exactly one line was broken. Nested quoting is the bug class this repository
    # exists to close; building a fixture out of it was avoidable the first time.
    cat > "$1/open-work.sh" <<'SEAM_EOF'
#!/bin/sh
L="$(git ls-files --cached --others --exclude-standard -- '*.md' | sort)"
[ -n "$L" ] || { printf 'no content files\n' >&2; exit 2; }
printf '%s\n' "$L"
SEAM_EOF
    chmod +x "$1/open-work.sh"
  }

  # ---------------------------------------------------------------- the main scenario repo
  new_repo r1
  seam "$ST/r1"
  mkdir -p "$ST/r1/sub" "$ST/r1/sub2" "$ST/r1/package" "$ST/r1/rig/results/exp" "$ST/r1/journal"
  printf '%s\n' '#!/bin/sh' '# a tool' '# banner' '# comment' 'MY_LONG_CONST=1' 'helper_fn() { :; }' \
    > "$ST/r1/tool.sh"
  printf '%s\n' 'sub caller' 'helper_fn 1' > "$ST/r1/sub/caller.sh"
  # A deliberately SHORT defined name. It exists so the anchor length-floor is load-bearing:
  # without the floor this name becomes an anchor, and the mutant that drops the floor then turns
  # one UNDECIDABLE into one FAIL. A rule nothing can violate is a rule nothing tests.
  printf '%s\n' '#!/bin/sh' 'ab=1' > "$ST/r1/shortsym.sh"
  printf '%s\n' 'dup one' > "$ST/r1/sub/dup.md"
  printf '%s\n' 'dup two' > "$ST/r1/sub2/dup.md"
  printf '%s\n' '{"run_id":"old"}' > "$ST/r1/rig/results/exp/runs.jsonl"
  printf '%s\n' '{"lock":1}' > "$ST/r1/package/package-lock.json"
  cmt "$ST/r1" 1700000000 'base: seam, sources, artifact, lockfile'

  HB="$( cd "$ST/r1" && printf 'orphan object\n' | git hash-object -w --stdin )"
  HBS="$(printf '%s' "$HB" | cut -c1-7)"; HBM="$(printf '%s' "$HB" | cut -c1-10)"
  # Hex-shaped, present in the tree, and guaranteed to be NO git object. The first draft took the
  # first 16 characters of HB plus padding - which is a PREFIX of HB, and git resolves prefixes,
  # so the "digest" was reachable as an abbreviation of a real object: the decoy asserted the
  # opposite of what it claimed. The complement map differs at character one, so it cannot be a
  # prefix of the object it is built from, by construction rather than by luck.
  FAKEHEX="$(printf '%s' "$HB" | cut -c1-16 | tr '0123456789abcdef' 'fedcba9876543210')"

  {
    printf '%s\n' 'Guard: see `tool.sh:5` for MY_LONG_CONST'
    printf '%s\n' 'Stale: see `tool.sh:1` for MY_LONG_CONST'
    printf '%s\n' 'Vague: see `tool.sh:3`'
    printf 'Aged: was %s%s%s for MY_LONG_CONST\n' "$BT" 'tool.sh:1' "$BT"
    printf '%s\n' 'Absent: see `missing.js:12`'
    printf '%s\n' 'Twice: see `dup.md:1`'
    printf '%s\n' 'Gone: see `tool.sh:999`'
    printf '%s\n' 'Short: see `tool.sh:1` about ab'
  } > "$ST/r1/doc_a.md"
  {
    fm idx index
    printf '%s\n' 'Index lists 17 content files today.'
    printf '%s\n' 'It rotted across 22 published commits (`6115b79..origin/main`).'
    printf '%s\n' 'The seam file is tool.sh and it matters.'
  } > "$ST/r1/index_a.md"
  {
    fm th theory
    printf '%s\n' 'Measured 17 content files in one experiment.'
  } > "$ST/r1/theory_a.md"
  {
    fm hash index
    # THREE spellings of one object at TWO different lengths, and that is the load-bearing part.
    # The first draft planted only a 7-char prefix and the 40-char sha. That pair dedupes under
    # BOTH rules - by resolved id and by raw token - because the SEEN list stores the resolved id,
    # so the mutant that dedupes by raw token survives it (measured: SURVIVED, diff verified). A
    # second prefix of a DIFFERENT length is the only input that separates the two rules: the
    # token rule sees two distinct tokens and reports one object twice. A fixture cannot assert a
    # rule its own input cannot violate (same lesson as the `ab` anchor-length decoy).
    printf 'Three spellings, one object: %s, %s and %s.\n' "$HBS" "$HBM" "$HB"
    # A hex token that is NOT a git object: a digest prefix. The class must skip it, so it needs
    # to exist in the fixture - without one, the guard that separates digests from objects has
    # no population and a mutant deleting it survives (measured, in exactly this sweep).
    printf '%s\n' "Digest prefix ${FAKEHEX} is a sha256 prefix, not a commit."
  } > "$ST/r1/hash_a.md"
  {
    fm api index
    printf '%s\n' 'The tool returned `total_count` = **7** that day.'
  } > "$ST/r1/api_a.md"
  {
    fm api2 index
    printf '%s\n' 'gh api repos/x/y/actions/runs | .total_count = **7** runs.'
  } > "$ST/r1/api_b.md"
  {
    fm jr journal
    printf '%s\n' 'At the time it cited `tool.sh:999`.'
  } > "$ST/r1/journal/2026-01-01-record.md"
  printf '%s\n' '{"manifest":1}' > "$ST/r1/package/package.json"
  printf '%s\n' '# writer' 'from pathlib import Path' 'Path("rig/results/exp/runs.jsonl").write_text("x")' \
    > "$ST/r1/rig/gen.py"
  printf '%s\n' '#!/bin/sh' '# a tool' '# banner' '# comment' 'MY_LONG_CONST=1' 'helper_fn() { :; }' '# changed later' \
    > "$ST/r1/tool.sh"
  cmt "$ST/r1" 1700000600 'docs, index, api claims, newer writer and manifest'

  # Guard repo for the ABSENT branch: seam + one md, no lockfiles, no artifacts, no cited paths.
  new_repo r3
  seam "$ST/r3"
  printf '%s\n' 'plain file' > "$ST/r3/plain.md"
  cmt "$ST/r3" 1700000000 'seam and one md only'

  CASE='tree mode runs and reports its denominators'
  run_in "$ST/r1"
  assert_rc 0
  assert_out 'OBLIGATION LEDGER - tree audit'
  assert_out 'cites in live scope:'

  # THE VERDICT VECTOR AS A GOLDEN, one planted cite per verdict, asserted as COUNTS not as
  # messages. This exists because a mutant sweep deleted VERDICT='HISTORICAL' and the suite stayed
  # green: the VDETAIL string still said HISTORICAL (only the assignment was gone), so the
  # message assertion passed while the cite silently moved to another bucket. A test that greps
  # for a label cannot see a miscount of that label - which is the one thing a counter must not
  # be blind to. These figures were READ from a run (asserted at 99 first, corrected from the
  # reported got), never computed from the fixture by hand: hand-derived goldens are L11's class.
  CASE='the verdict vector is a golden: one planted cite per bucket, plus one that only the anchor floor keeps undecided'
  # UNDECIDABLE is 2, not 1: the planted `Short:` cite names only the 2-character defined name
  # `ab`, which the anchor length-floor rejects. Delete the floor and that cite moves to FAIL -
  # which is what makes the floor load-bearing instead of decorative (measured: it was the exact
  # mutant that survived the first sweep). Values READ from a run, never computed by hand.
  assert_re 'cites in live scope: RESOLVE 1 [|] FAIL 1 [|] FAIL-range 1 [|] UNDECIDABLE 2 [|] UNRESOLVED 1 [|] AMBIGUOUS 1 [|] HISTORICAL 1$' 1

  CASE='C2/C4/C5/C1a report exactly the planted finding each, no more (scope over-reach is a defect)'
  assert_count 'REPORT a generator prints this number' 1
  assert_count 'asserts a value for the field' 1
  assert_count 'REPORT pin this to a fixed commit' 1
  assert_count 'could never have been true' 1

  CASE='C1: a cite naming its defined symbol on the cited line resolves'
  assert_absent 'doc_a.md:1 cites tool.sh:5'

  CASE='C1: a planted stale cite is a FAIL naming the symbol it missed (S8)'
  assert_out 'doc_a.md:2 cites tool.sh:1 - the cited lines name none of: MY_LONG_CONST'

  CASE='C1: a cite with no defined symbol is UNDECIDABLE, never folded into the pass column'
  assert_out 'doc_a.md:3 -> tool.sh:3 - the citing line names no defined symbol'

  CASE='C1: the house age-marker (was ...) reads as HISTORICAL, not as a defect'
  assert_out 'doc_a.md:4 cites tool.sh:1 - the line marks the cite as its own age'

  CASE='C1: a cite to no tracked path is UNRESOLVED and carries its range'
  assert_out 'doc_a.md:5 names missing.js:12, which resolves to no tracked path'

  CASE='C1: a basename several paths carry is AMBIGUOUS'
  assert_out 'doc_a.md:6 names dup.md:1 and 2 tracked paths carry that basename'

  CASE='C1a: a planted cite past the end of the file could never have been true (S8)'
  assert_out 'FAIL       doc_a.md:7 cites tool.sh:999 - tool.sh has 7 lines; this cite could never have been true'

  CASE='provenance scope: dated records are counted and aggregated, never listed as obligations'
  assert_out 'provenance FAILs by file'
  if printf '%s\n' "$OUT" | sed -n '/provenance FAILs by file/,$p' | grep -qF 'journal/2026-01-01-record.md'; then
    ok "provenance aggregation names journal/2026-01-01-record.md"
  else
    bad "the dated record must appear under the provenance aggregation"
  fi
  live_fail_lines="$(printf '%s\n' "$OUT" | sed -n '/cites in live scope:/,/provenance FAILs by file/p' \
    | grep -cE '^  (FAIL|UNRESOLVED|UNDECIDABLE|AMBIGUOUS|HISTORICAL)' || true)"
  if [ "${live_fail_lines:-0}" -ge 4 ] && ! printf '%s\n' "$OUT" \
      | sed -n '/cites in live scope:/,/provenance FAILs by file/p' | grep -qF 'journal/2026-01-01-record.md'; then
    ok "live-scope details list planted findings and no dated record"
  else
    bad "live details must carry the planted findings without the dated record"
  fi

  CASE='C2: a planted hand-stated generator count in an index file is reported (S8)'
  assert_out 'REPORT a generator prints this number'
  assert_out 'index_a.md:9:'
  assert_out '17 content files'

  CASE='C2 guard: the same phrase in a non-index file is NOT reported (the guard repo never appears)'
  assert_absent 'theory_a.md'

  CASE='C3: an unreachable git object quoted in live prose is REPORTed (S8), prefix and full sha as ONE object'
  assert_out "REPORT   $HBS (blob,"
  assert_count "REPORT   $HBS" 1
  assert_absent "REPORT   $HB "

  CASE='C3 guard: a hex token that is no git object is a digest prefix, not an unreachable commit'
  # The needle carries the trailing period on purpose: the class HEADING also says "resolves from
  # no ref", and counting that phrase measured the heading, not the finding (got 2, expected 1).
  assert_count 'resolves from no ref.' 1
  assert_absent "$FAKEHEX "

  CASE='C4: a field claim with a value and no endpoint is REPORTed (S8)'
  assert_out 'api_a.md:9 asserts a value for the field total_count and names no endpoint'

  CASE='C4 guard: the identical claim WITH an endpoint stays silent'
  assert_absent 'api_b.md:2 asserts a value'

  CASE='C5: a planted range ending in a moving ref beside a number is reported (S8)'
  assert_out 'REPORT pin this to a fixed commit'
  assert_out 'index_a.md:10:'

  CASE='D1: a planted lockfile older than its manifest is STALE (S8)'
  assert_out 'STALE    package/package-lock.json predates the last commit touching package/package.json'

  CASE='D1 guard: a tree with no lockfile prints ABSENT, not an empty pass'
  run_in "$ST/r3"
  assert_rc 0
  assert_out 'D1 - a lockfile must not be older than the manifest it locks'
  assert_out 'ABSENT: this repository tracks no lockfile'

  CASE='D2: a planted artifact older than its discovered writer is STALE (S8)'
  run_in "$ST/r1"
  assert_out 'STALE    rig/results/exp/runs.jsonl predates the last commit touching rig/gen.py'
  assert_out 'discovered 1 writer(s) from the index'

  CASE='--range: zero commits is exit 2, never the vacuous clean the hook still prints'
  run_in "$ST/r1" --range HEAD HEAD
  assert_rc 2
  assert_out 'names 0 commits'

  CASE='--range: an unresolvable revision is exit 2, not an empty scan'
  run_in "$ST/r1" --range HEAD nope-not-a-rev
  assert_rc 2
  assert_out 'does not resolve'

  CASE='--range: D3 judges every cite into a changed path, D4 names the real caller (S8)'
  run_in "$ST/r1" --range 'HEAD~1' HEAD
  assert_rc 0
  assert_out 'D3 - citations INTO the HEAD~1..HEAD range'
  assert_out 'ok       doc_a.md:1 cites tool.sh:5 and resolves after the change'
  assert_out 'mentions tool.sh'
  assert_out 'helper_fn (defined in tool.sh) is called from: sub/caller.sh'

  CASE='the seam is mandatory: no open-work.sh is could-not-run, never a private enumeration'
  new_repo r2
  printf '%s\n' 'just a file' > "$ST/r2/x.md"
  cmt "$ST/r2" 1700000000 'no seam'
  run_in "$ST/r2"
  assert_rc 2
  assert_out 'open-work.sh is absent or not executable'

  CASE='empty input is never a pass: a seam that finds no content exits 2'
  new_repo r3empty
  seam "$ST/r3empty"
  printf '%s\n' '#!/bin/sh' '# source but not content' > "$ST/r3empty/only.sh"
  cmt "$ST/r3empty" 1700000000 'seam with no content'
  run_in "$ST/r3empty"
  assert_rc 2
  assert_out '--list-content exited 2'

  CASE='not a repository is exit 2'
  R4="$ST/r4"; mkdir -p "$R4"
  run_in "$R4"
  assert_rc 2
  assert_out 'not a git repository'

  CASE='unknown arguments are refused with exit 2'
  run_in "$ST/r1" --made-up
  assert_rc 2
  assert_out 'unknown argument'

  CASE='--help prints the header and exits 0'
  run_in "$ST/r1" --help
  assert_rc 0
  assert_out 'obligation-ledger.sh - what did this change make somebody else'

  CASE='running from a subdirectory prints repository-relative paths only'
  run_in "$ST/r1/sub"
  assert_rc 0
  assert_out 'doc_a.md'
  assert_absent "$ST"

  CASE='the ledger is a function of the tree: two runs are byte-identical'
  ( cd "$ST/r1" && "$SELF" ) > "$ST/run-a" 2>&1 || true
  ( cd "$ST/r1" && "$SELF" ) > "$ST/run-b" 2>&1 || true
  if cmp -s "$ST/run-a" "$ST/run-b"; then ok 'two runs byte-identical'; else bad 'output moved between runs; a report that cannot be diffed cannot gate anything'; fi

  [ "$FAILED" -eq 0 ] || {
    printf '\n  SELF-TEST FAILED - this ledger is not behaving as specified.\n' >&2
    exit 1
  }
  printf '\n  self-test: all cases passed\n'
  exit 0
}

MODE='tree'
RANGE_FROM=''
RANGE_TO=''

case "${1:-}" in
  '')          : ;;
  --range)
    [ "$#" -eq 3 ] || die_cannot_run "--range needs exactly two revisions: --range <from> <to>. An unbounded scan is what the no-argument mode is for."
    RANGE_FROM="$2"
    RANGE_TO="$3"
    MODE='range'
    ;;
  --self-test) self_test ;;
  --help)      show_help; exit 0 ;;
  *)           die_cannot_run "unknown argument '$1'. Use no argument, --range A B, --self-test, or --help." ;;
esac

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" \
  || die_cannot_run "this is not a git repository, so there is nothing to audit"
cd "$ROOT" || die_cannot_run "could not enter the repository root"

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
SELF="$SELF_DIR/$(basename "$0")"
SELF_NAME="$(basename "$0")"

TMPD="$(mktemp -d)" || die_cannot_run "could not create a temporary directory"
trap 'rm -rf "$TMPD"' EXIT

# The seam. Refusing to fall back to a private enumerator is the whole point of the flag, so the
# absence of the seam is could-not-run, not a degraded mode.
LIST_TOOL="$ROOT/open-work.sh"
[ -x "$LIST_TOOL" ] \
  || die_cannot_run "./open-work.sh is absent or not executable; this ledger consumes its --list-content seam, and a ledger that re-derived the content rule would be the second enumerator this repository already forbids"

CONTENT="$TMPD/content"
SRCS="$TMPD/srcs"
CORPUS="$TMPD/corpus"
INV="$TMPD/inventory"
IDX="$TMPD/indexfiles"
CITES="$TMPD/cites"

set +e
"$LIST_TOOL" --list-content > "$CONTENT" 2> "$TMPD/listerr"
LIST_RC=$?
set -e
[ "$LIST_RC" -eq 0 ] || die_cannot_run "./open-work.sh --list-content exited $LIST_RC: $(head -n 1 "$TMPD/listerr" 2>/dev/null)"

git ls-files -- '*.sh' '*.py' | grep -v '^rig/fixtures/' > "$SRCS" || true
sort -u "$CONTENT" "$SRCS" > "$CORPUS"

# The symbol inventory: names DEFINED in committed sources. Two rules were measured before
# trusting this set: it must contain the constants the two known defects anchor on (DIRTY_OK,
# TIMEOUT_S - both top-level assignments, so assignments are in), and it must not be a keyword
# list (a bare python pass line defines nothing - the extractor below cannot emit it).
SYMS_AWK='
{
  if (match($0, /^[A-Za-z_][A-Za-z0-9_]*[ \t]*\(\)[ \t]*\{/)) { s = substr($0, 1, RLENGTH); sub(/[ \t]*\(.*/, "", s); print s }
  if (match($0, /[A-Za-z_][A-Za-z0-9_]*[ \t]*\(\)[ \t]*\{/)) { s = substr($0, RSTART, RLENGTH); sub(/[ \t]*\(.*/, "", s); print s }
  if (match($0, /(^|[ \t])(def|class)[ \t]+[A-Za-z_][A-Za-z0-9_]*/)) { s = substr($0, RSTART, RLENGTH); sub(/.*(def|class)[ \t]+/, "", s); print s }
  if (match($0, /^[A-Za-z_][A-Za-z0-9_]*=/)) { s = substr($0, 1, RLENGTH); sub(/=$/, "", s); print s }
}
'
if [ -s "$SRCS" ]; then
  tr '\n' '\0' < "$SRCS" | xargs -0 awk "$SYMS_AWK" 2>/dev/null | sort -u > "$INV" || true
else
  : > "$INV"
fi
[ -f "$INV" ] || : > "$INV"

CITE_RE='[A-Za-z0-9_./-]+\.(sh|py|mjs|js|json|yml|yaml|md):[0-9]+(-[0-9]+)?'

: > "$CITES"
while IFS= read -r f; do
  case "$f" in
    journal/*|sdd/archive/*) scope=prov ;;
    *)                     scope=obl ;;
  esac
  grep -noE "$CITE_RE" "$f" 2>/dev/null | while IFS=: read -r ln cite; do
    printf '%s\t%s\t%s\t%s\n' "$scope" "$f" "$ln" "$cite"
  done >> "$CITES" || true
done < "$CORPUS"

: > "$IDX"
while IFS= read -r f; do
  t="$(awk 'NR <= 12 && /^type:/ { sub(/^type:[ \t]*/, ""); print; exit }' "$f" 2>/dev/null)"
  [ "$t" = index ] && printf '%s\n' "$f" >> "$IDX"
done < "$CONTENT"

rev() {
  set +e
  r="$(git rev-parse --short HEAD 2>/dev/null)"
  set -e
  [ -n "$r" ] || r='no commit yet'
  printf '%s' "$r"
}

file_lines() { awk 'END { print NR }' "$1" 2>/dev/null; }

sec()  { printf '\n  %s\n' "$1"; }
note() { printf '    %s\n' "$1"; }

is_provenance() {
  case "$1" in journal/*|sdd/archive/*) return 0 ;; esac
  return 1
}

# verdict <citing-file> <citing-line-no> <cite-string>
# Sets VERDICT to RESOLVE | FAIL | FAILRANGE | UNDECIDABLE | UNRESOLVED | AMBIGUOUS | HISTORICAL
# and VDETAIL to the printed detail (empty on RESOLVE). Increments nothing: callers own counting,
# so D3 can reuse the same judgement without double-booking C1's denominators.
verdict() {
  cf="$1"; cln="$2"; cite="$3"
  tgt="${cite%%:*}"
  rng="${cite#*:}"
  lo="${rng%%-*}"
  hi="$(printf '%s' "$rng" | awk -F- '{ print ($2 == "" ? $1 : $2) }')"
  stem="$(basename "$tgt")"; stem="${stem%.*}"

  path=''
  if [ -f "$tgt" ]; then
    path="$tgt"
  else
    cand="$(git ls-files -- "*${tgt}" 2>/dev/null | grep -v '^rig/fixtures/' | sed '/^$/d')"
    n="$(printf '%s\n' "$cand" | grep -c . || true)"
    if [ "${n:-0}" -eq 1 ]; then
      path="$(printf '%s\n' "$cand" | head -n 1)"
    elif [ "${n:-0}" -gt 1 ]; then
      VERDICT='AMBIGUOUS'
      VDETAIL="AMBIGUOUS  $cf:$cln names $cite and $n tracked paths carry that basename; the cite does not say which one it saw"
      return 0
    else
      VERDICT='UNRESOLVED'
      VDETAIL="UNRESOLVED $cf:$cln names $tgt:$rng, which resolves to no tracked path. Fixture interiors and generated entrypoints land here; a planned file is not yet a defect and not yet a resolution either."
      return 0
    fi
  fi

  lines="$(file_lines "$path")"
  if [ "$hi" -gt "$lines" ]; then
    VERDICT='FAILRANGE'
    VDETAIL="FAIL       $cf:$cln cites $tgt:$rng - $path has $lines lines; this cite could never have been true, at any commit"
    return 0
  fi

  cl="$(awk -v L="$cln" 'NR == L' "$cf")"
  case "$cl" in
    *"was ${BT}${cite}${BT}"*)
      VERDICT='HISTORICAL'
      VDETAIL="HISTORICAL $cf:$cln cites $tgt:$rng - the line marks the cite as its own age, so it is provenance kept on purpose, not a pointer to repair"
      return 0 ;;
  esac

  anchors="$(printf '%s\n' "$cl" \
    | grep -oE '[A-Za-z_][A-Za-z0-9_]*' \
    | awk 'length($0) >= 6 || index($0, "_") > 0' \
    | grep -v -x -F -e "$stem" \
    | sort -u \
    | grep -Fxf "$INV" || true)"
  if [ -z "$anchors" ]; then
    VERDICT='UNDECIDABLE'
    VDETAIL="UNDECIDABLE $cf:$cln -> $tgt:$rng - the citing line names no defined symbol, so nothing here can judge it. This is the ceiling of a machine check, not a pass."
    return 0
  fi

  blob="$(awk -v a="$lo" -v b="$hi" 'NR >= a && NR <= b' "$path" 2>/dev/null)"
  hit=0
  OLD_IFS="$IFS"; IFS='
'
  for a in $anchors; do
    case "$blob" in
      *"$a"*) hit=1; break ;;
    esac
  done
  IFS="$OLD_IFS"
  if [ "$hit" -eq 1 ]; then
    VERDICT='RESOLVE'
    VDETAIL=''
    return 0
  fi

  VERDICT='FAIL'
  VDETAIL="FAIL       $cf:$cln cites $tgt:$rng - the cited lines name none of: $(printf '%s' "$anchors" | tr '\n' ' ')"
  return 0
}

class_c1() {
  n_tot=0; n_res=0; n_fail=0; n_range=0; n_und=0; n_unr=0; n_amb=0; n_hist=0
  p_tot=0; p_fail=0
  PF_COUNTS="$TMPD/provcounts"; : > "$PF_COUNTS"
  DETAILS=''
  PDETAILS=''
  while IFS="$BTAB" read -r scope cf cln cite; do
    [ -n "$cf" ] || continue
    verdict "$cf" "$cln" "$cite"
    if [ "$scope" = prov ]; then
      p_tot=$((p_tot + 1))
      case "$VERDICT" in
        FAIL|FAILRANGE)
          p_fail=$((p_fail + 1))
          printf '%s\n' "$cf" >> "$PF_COUNTS" ;;
      esac
      continue
    fi
    n_tot=$((n_tot + 1))
    case "$VERDICT" in
      RESOLVE)     n_res=$((n_res + 1)) ;;
      FAIL)        n_fail=$((n_fail + 1));   DETAILS="$DETAILS
$VDETAIL" ;;
      FAILRANGE)   n_range=$((n_range + 1)); DETAILS="$DETAILS
$VDETAIL" ;;
      UNDECIDABLE) n_und=$((n_und + 1));     DETAILS="$DETAILS
$VDETAIL" ;;
      UNRESOLVED)  n_unr=$((n_unr + 1));     DETAILS="$DETAILS
$VDETAIL" ;;
      AMBIGUOUS)   n_amb=$((n_amb + 1));     DETAILS="$DETAILS
$VDETAIL" ;;
      HISTORICAL)  n_hist=$((n_hist + 1));   DETAILS="$DETAILS
$VDETAIL" ;;
    esac
  done < "$CITES"

  sec 'C1 / C1a - every citation resolves to what it names'
  printf '  scanned %s cites in live scope: RESOLVE %s | FAIL %s | FAIL-range %s | UNDECIDABLE %s | UNRESOLVED %s | AMBIGUOUS %s | HISTORICAL %s\n' \
    "$n_tot" "$n_res" "$n_fail" "$n_range" "$n_und" "$n_unr" "$n_amb" "$n_hist"
  printf '  provenance scope (journal/, sdd/archive/ - dated records: named, never obligations): %s cites, %s of them do not resolve\n' "$p_tot" "$p_fail"
  [ -n "$DETAILS" ] && printf '%s\n' "$DETAILS"  | sed '/^$/d' | sed 's/^/  /'
  if [ "$p_fail" -gt 0 ]; then
    printf '  provenance FAILs by file (dated records - repair one only if you are re-opening that cycle):\n'
    sort "$PF_COUNTS" | uniq -c | sort -rn | sed 's/^/    /'
  fi
  return 0
}

class_c2() {
  HITS="$TMPD/c2hits"; : > "$HITS"
  while IFS= read -r f; do
    grep -noE '[^A-Za-z0-9*][0-9]+(\*\*)? (content files?|item\(s\)|items?|source\(s\)|sources?|skill\(s\)|skills?|demand records?)' "$f" 2>/dev/null \
      | sed "s|^|$f:|" >> "$HITS" || true
  done < "$IDX"
  nidx="$(grep -c . "$IDX" || true)"
  nhit="$(grep -c . "$HITS" || true)"
  sec 'C2 - no hand-stated count of something a generator prints (type: index files only)'
  printf '  scanned %s index files; %s hand-stated generator count(s)\n' "${nidx:-0}" "${nhit:-0}"
  if [ "${nhit:-0}" -gt 0 ]; then
    # awk, not sed. The first draft prefixed these lines with
    #   sed 's/^/  REPORT ... (printed by ./check.sh) .../'
    # and the '/' inside ./check.sh closed the substitution early: sed died, the pipeline still
    # exited 0, and a class that HAD found something printed NOTHING and read as clean. That is
    # the vacuous pass this repository's whole S8 rule exists to catch, arriving here through a
    # delimiter. A prefix step must not be able to fail silently.
    awk '{ print "  REPORT a generator prints this number - name it (printed by ./check.sh) or delete it: " $0 }' "$HITS"
  fi
  return 0
}

class_c3() {
  REACH="$TMPD/reachable"
  {
    git rev-list --objects --all 2>/dev/null
    git rev-list --objects HEAD 2>/dev/null
  } | cut -c1-40 | sort -u > "$REACH" || true
  [ -f "$REACH" ] || : > "$REACH"
  HASHES="$TMPD/hashes"; : > "$HASHES"
  tr '\n' '\0' < "$CONTENT" | xargs -0 grep -ohE '\b[0-9a-f]{7,40}\b' 2>/dev/null \
    | sort | uniq -c | awk '{ print $2 " " $1 }' > "$HASHES" || true
  [ -f "$HASHES" ] || : > "$HASHES"
  ntok="$(awk '{ s += $2 } END { print s + 0 }' "$HASHES")"
  nrep=0
  REPORTS=''
  # One line per OBJECT, not per token. Two reasons, both measured here: a short prefix and the
  # full sha it abbreviates are the same object (git rev-parse collapses them), and the naive
  # first draft of this dedupe used `case "$SEEN" in *"\n$full\n"*)` - which NEVER matched,
  # because in POSIX sh a \n inside a pattern is a literal backslash and n, not a newline. The
  # duplicate survived until a real run printed 2fc49e65 beside its own full sha. Hence a file
  # and grep -qxF: the membership test is only as portable as its delimiter.
  SEENF="$TMPD/seen"; : > "$SEENF"
  while read -r h n; do
    [ -n "$h" ] || continue
    set +e
    typ="$(git cat-file -t "$h" 2>/dev/null)"
    full="$(git rev-parse "$h" 2>/dev/null)"
    set -e
    [ -n "$typ" ] || continue
    grep -q "^${h}" "$REACH" && continue
    grep -qxF "$full" "$SEENF" && continue
    printf '%s\n' "$full" >> "$SEENF"
    set +e
    files="$(xargs grep -lE "\b${h}\b" < "$CONTENT" 2>/dev/null | grep -v -E '^(journal|sdd/archive)/' | tr '\n' ' ')"
    set -e
    [ -n "$files" ] || continue      # unreachable hashes inside dated records are provenance, not live claims
    nrep=$((nrep + 1))
    REPORTS="$REPORTS
REPORT   $h ($typ, $n live mention(s) in: $files) resolves from no ref. Reported, not condemned: an unreachable object is recovery evidence, and deleting the citation destroys the record that the object existed."
  done < "$HASHES"
  sec 'C3 - a quoted hash that IS a git object and resolves from no ref is reported, never auto-condemned'
  printf '  scanned %s hex tokens in live prose; %s distinct live objects unreachable from any ref (prefixes of the same object are counted once; tokens that are no git object are digest prefixes - not this class; unreachable hashes inside dated records are provenance)\n' "$ntok" "$nrep"
  [ -n "$REPORTS" ] && printf '%s\n' "$REPORTS" | sed '/^$/d' | sed 's/^/  /'
  return 0
}

class_c4() {
  OUT="$TMPD/c4"; : > "$OUT"
  # The assertion-shape scan. Two rules this scan owes to a bug its first draft shipped with,
  # found by running the file with `time` BEFORE writing its self-test: the draft tested the
  # after-token with match(), which CLOBBERS RSTART/RLENGTH - on a no-match those become 0/-1,
  # substr(line, -1) is the whole line, and the scan never advanced. An infinite loop in the
  # class that audits citation staleness, off by one through a return value, born in the commit
  # that exists to catch off-by-one-at-birth. Hence: `~` for the test (it never touches RSTART),
  # and a hard progress guard so no future edit can spin without matching.
  C4_AWK='
    { b[NR] = $0 }
    END {
      for (i = 1; i <= NR; i++) {
        line = b[i]; tok = ""
        asserted = 0
        while (length(line) > 0 && match(line, /(total_count|[.][a-z][a-z0-9]*(_[a-z0-9]+)+)/)) {
          tok = substr(line, RSTART, RLENGTH)
          adv = RSTART + RLENGTH
          after = substr(line, adv, 31)
          if (after ~ /^[*`= :|]*[0-9]/) { asserted = 1; break }
          if (adv <= 1) break
          line = substr(line, adv)
        }
        if (!asserted) continue
        ep = 0
        lo = (i > 2 ? i - 2 : 1)
        hi = (i + 2 < NR ? i + 2 : NR)
        for (j = lo; j <= hi; j++)
          if (b[j] ~ /gh api|repos\/|actions\/runs|actions\/workflows|rulesets|run list|jq |endpoint/) { ep = 1; break }
        if (!ep)
          printf "REPORT   %s:%d asserts a value for the field %s and names no endpoint in the line or its two neighbours - the same field name from a different endpoint is indistinguishable by inspection (L18)\n", F, i, tok
      }
    }
  '
  while IFS= read -r f; do
    is_provenance "$f" && continue
    grep -q 'total_count\|[.][a-z][a-z0-9]*_' "$f" 2>/dev/null || continue
    awk -v F="$f" "$C4_AWK" "$f" >> "$OUT" 2>/dev/null || true
  done < "$CONTENT"
  n="$(grep -c . "$OUT" || true)"
  scanned="$( ( xargs grep -ohE 'total_count|[.][a-z][a-z0-9]*(_[a-z0-9]+)+' < "$CONTENT" 2>/dev/null || true ) | wc -l | tr -d ' ')"
  sec 'C4 - a claim asserting a tool-output value must name the field AND the endpoint'
  printf '  %s response-shaped field tokens scanned; %s assert a value with no endpoint nearby\n' "${scanned:-0}" "${n:-0}"
  [ "${n:-0}" -gt 0 ] && sed 's/^/  /' "$OUT"
  return 0
}

class_c5() {
  OUT="$TMPD/c5"; : > "$OUT"
  while IFS= read -r f; do
    grep -nE '[^ ]\.\.(origin/)?(main|master|HEAD)([^A-Za-z0-9._/-]|$)' "$f" 2>/dev/null \
      | grep -E '[0-9]' | sed "s|^|$f:|" >> "$OUT" || true
  done < "$IDX"
  n="$(grep -c . "$OUT" || true)"
  nidx="$(grep -c . "$IDX" || true)"
  sec 'C5 - a derived count in an index file is pinned to fixed objects, never to a moving ref'
  printf '  scanned %s index files; %s ranges end in main/origin/main/HEAD beside a number\n' "${nidx:-0}" "${n:-0}"
  [ "${n:-0}" -gt 0 ] && sed 's/^/  REPORT pin this to a fixed commit - the number stops matching the moment anything is pushed (L15): /' "$OUT" | sed 's/^/  /'
  return 0
}

class_d1() {
  LOCKS="$TMPD/locks"
  git ls-files | grep -E '(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|bun\.lock|bun\.lockb|composer\.lock|Gemfile\.lock|poetry\.lock|Cargo\.lock|go\.sum|Package\.resolved|Podfile\.lock|uv\.lock)$' \
    | grep -v '^rig/fixtures/' > "$LOCKS" || true
  [ -f "$LOCKS" ] || : > "$LOCKS"
  n="$(grep -c . "$LOCKS" || true)"
  sec 'D1 - a lockfile must not be older than the manifest it locks'
  if [ "${n:-0}" -eq 0 ]; then
    printf '  ABSENT: this repository tracks no lockfile outside rig/fixtures/. The class has no population here and says ABSENT rather than report an empty pass - a JS consumer running this same file WOULD have population, and the two states must not print the same line.\n'
    return 0
  fi
  printf '  scanned %s lockfile(s) outside fixtures\n' "$n"
  while IFS= read -r lock; do
    dirn="$(dirname "$lock")"
    case "$lock" in
      *package-lock.json|*yarn.lock|*pnpm-lock.yaml|*bun.lock|*bun.lockb) manifest="$dirn/package.json" ;;
      *composer.lock)   manifest="$dirn/composer.json" ;;
      *Gemfile.lock)    manifest="$dirn/Gemfile" ;;
      *poetry.lock|*uv.lock) manifest="$dirn/pyproject.toml" ;;
      *Cargo.lock)      manifest="$dirn/Cargo.toml" ;;
      *go.sum)          manifest="$dirn/go.mod" ;;
      *Podfile.lock)    manifest="$dirn/Podfile" ;;
      *)                manifest='' ;;
    esac
    [ -n "$manifest" ] || continue
    if ! git ls-files --error-unmatch "$manifest" >/dev/null 2>&1; then
      note "STALE    $lock names $manifest, which is not tracked - a lock with no tracked manifest cannot be re-derived by anyone else"
      continue
    fi
    set +e
    t_lock="$(git log -1 --format=%ct -- "$lock")"
    t_man="$(git log -1 --format=%ct -- "$manifest")"
    set -e
    if [ "${t_man:-0}" -gt "${t_lock:-0}" ]; then
      note "STALE    $lock predates the last commit touching $manifest - re-lock before anyone installs from it"
    fi
  done < "$LOCKS"
  return 0
}

class_d2() {
  WR="$TMPD/writers"; : > "$WR"
  while IFS= read -r p; do
    [ "$p" = "$SELF_NAME" ] && continue   # this file names the literals it greps for; it writes nothing
    grep -q 'rig/results' "$p" 2>/dev/null || continue
    grep -q 'runs[.]jsonl' "$p" 2>/dev/null || continue
    grep -qE 'write_bytes|write_text|open\([^)]*"w"' "$p" 2>/dev/null || continue
    printf '%s\n' "$p" >> "$WR"
  done < "$SRCS"
  ART="$TMPD/artifacts"
  git ls-files -- 'rig/results/' > "$ART" || true
  [ -f "$ART" ] || : > "$ART"
  na="$(grep -c . "$ART" || true)"
  nw="$(grep -c . "$WR" || true)"
  sec 'D2 - a committed generated artifact must not be older than a committed file that writes it'
  printf '  discovered %s writer(s) from the index (names the artifact directory AND the derived-table file AND carries a write primitive; never a hardcoded list - T9), %s committed artifact(s)\n' "${nw:-0}" "${na:-0}"
  if [ "${na:-0}" -eq 0 ]; then
    printf '  ABSENT: no committed generated artifact under rig/results/.\n'
    return 0
  fi
  while IFS= read -r a; do
    set +e
    t_art="$(git log -1 --format=%ct -- "$a")"
    set -e
    while IFS= read -r w; do
      [ -n "$w" ] || continue
      set +e
      t_w="$(git log -1 --format=%ct -- "$w")"
      set -e
      if [ "${t_w:-0}" -gt "${t_art:-0}" ]; then
        note "STALE    $a predates the last commit touching $w - re-derive before quoting it. This file never RUNS the writer: the real gate cannot run in a tree without the gitignored capture directory (L11), and a report that mutates what it reports is the truncation incident."
      fi
    done < "$WR"
  done < "$ART"
  return 0
}

class_d34() {
  set +e
  n="$(git rev-list --count "${RANGE_FROM}..${RANGE_TO}" 2>&1)"
  set -e
  case "$n" in
    ''|*[!0-9]*) die_cannot_run "--range ${RANGE_FROM}..${RANGE_TO} does not resolve: $n" ;;
  esac
  [ "$n" -gt 0 ] || die_cannot_run "--range ${RANGE_FROM}..${RANGE_TO} names 0 commits. A range that scanned nothing is could-not-run, not clean - the vacuous pass gaps/0004 was written about, reproduced on ./hooks/commit-msg --range HEAD HEAD"

  CHANGED="$TMPD/changed"
  git diff --name-only "${RANGE_FROM}" "${RANGE_TO}" 2>/dev/null | grep -v '^rig/fixtures/' > "$CHANGED" || true
  [ -f "$CHANGED" ] || : > "$CHANGED"
  nc="$(grep -c . "$CHANGED" || true)"

  sec "D3 - citations INTO the ${RANGE_FROM}..${RANGE_TO} range ($n commit(s), ${nc:-0} path(s) changed)"
  if [ "${nc:-0}" -eq 0 ]; then
    printf '  0 content paths changed; D3 has no population for this range and says so\n'
    printf '\n  D4 - who calls what the range touched\n  0 content paths changed; nothing to look up\n'
    return 0
  fi

  while IFS= read -r p; do
    base="$(basename "$p")"
    hits=0
    while IFS="$BTAB" read -r scope cf cln cite; do
      [ -n "$cf" ] || continue
      tgt="${cite%%:*}"
      [ "$tgt" = "$p" ] || [ "$tgt" = "$base" ] || continue
      hits=$((hits + 1))
      verdict "$cf" "$cln" "$cite"
      case "$VERDICT" in
        RESOLVE)    note "ok       $cf:$cln cites $cite and resolves after the change" ;;
        HISTORICAL) note "historical $cf:$cln cites $cite - marked as age, kept on purpose" ;;
        *)          note "OBLIG    $VDETAIL" ;;
      esac
    done < "$CITES"
    [ "$hits" -eq 0 ] && note "no cite names $p - read the two lines below before calling that clean"
    while IFS= read -r ix; do
      set +e
      m="$(grep -cF "$base" "$ix" 2>/dev/null)"
      set -e
      [ "${m:-0}" -gt 0 ] && note "CHECK    $ix mentions $base $m time(s); sentences there may carry counts or claims this range moved (L7's grep-that-was-a-choice, mechanised)"
    done < "$IDX"

    case "$p" in
      *.sh|*.py|*/workflows/*|hooks/*)
        callers="$(git ls-files -- '*.sh' '*.py' '.github/*' 'hooks/*' | grep -v '^rig/fixtures/' | grep -v "^${p}\$" | xargs grep -lF "$base" 2>/dev/null | sed '/^$/d' || true)"
        [ -n "$callers" ] && note "CHECK    invoked or named by: $(printf '%s' "$callers" | tr '\n' ' ')"
        ;;
    esac
  done < "$CHANGED"

  sec 'D4 - functions defined in the changed sources and called from files that do not define them'
  any=0
  while IFS= read -r p; do
    case "$p" in *.sh|*.py) : ;; *) continue ;; esac
    [ -f "$p" ] || continue
    defs="$(awk "$SYMS_AWK" "$p" | sort -u)"
    while IFS= read -r s; do
      [ -n "$s" ] || continue
      grep -qxF "$s" "$INV" || continue
      cl="$(git ls-files -- '*.sh' '*.py' | grep -v '^rig/fixtures/' | grep -v "^${p}\$" | xargs grep -lE "(^|[^A-Za-z0-9_])${s} *\(|^[ \t]*${s}([ \t]|\$)" 2>/dev/null | sed '/^$/d' || true)"
      [ -n "$cl" ] || continue
      any=1
      note "CHECK    $s (defined in $p) is called from: $(printf '%s' "$cl" | tr '\n' ' ')"
    done <<DEFS
$defs
DEFS
  done < "$CHANGED"
  [ "$any" -eq 0 ] && printf '  none found across the changed sources\n'
  return 0
}

printf '\n  OBLIGATION LEDGER - %s audit at %s\n' "$MODE" "$(rev)"
printf '  Reports; does not judge (exit 0 with findings, exit 2 when it could not run). Read the denominators: a class that scanned 0 things proves nothing.\n'

CONTENT_N="$(grep -c . "$CONTENT" || true)"
SRCS_N="$(grep -c . "$SRCS" || true)"
INV_N="$(grep -c . "$INV" || true)"
IDX_N="$(grep -c . "$IDX" || true)"
printf '  corpus: %s content files from the --list-content seam + %s committed sources (rig/fixtures/ excluded by the shared rule)\n' "${CONTENT_N:-0}" "${SRCS_N:-0}"
printf '  symbol inventory: %s defined names; index-scope files: %s\n' "${INV_N:-0}" "${IDX_N:-0}"

class_c1
class_c2
class_c3
class_c4
class_c5
class_d1
class_d2
if [ "$MODE" = range ]; then class_d34; fi

sec 'COVERAGE - what this ledger cannot see'
printf '  * prose counts and claims with no path:line form (L17, L8): a second reader is the only verifier; the UNDECIDABLE count above is the machine-judged ceiling.\n'
printf '  * a citation wrapping across two comment lines: single-line scanning under-reports this class by design (rule (g)); measured 1 in live scope.\n'
printf '  * a symbol name and its cite on DIFFERENT lines of one comment block (the derive.py:1476 shape, and the moved-it-to-498 family): UNDECIDABLE by construction, not a pass. Anchor cites to symbol names or section headers, never to bare numbers (L15).\n'
printf '  * meaning: an anchor token can be in the cited lines by coincidence. C1 is a floor, not a ceiling.\n'
printf '\n  Generated by ./obligation-ledger.sh. Nothing here is hand-maintained; re-run to refresh.\n\n'
exit 0
