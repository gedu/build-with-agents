#!/usr/bin/env bash
#
# setup.sh — generate tool-specific entrypoints for this tool-neutral repo.
#
# AGENTS.md and skills/ are the committed sources of truth. Every entrypoint this
# script creates is a symlink, is gitignored, and is never committed.
#
# Safety contract: this script never overwrites a pre-existing regular file or
# directory, and never retargets a symlink that points somewhere unexpected. It
# skips and warns instead. Running it twice is a no-op.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BEGIN_MARK="# >>> generated AI tool assets (managed by setup.sh) >>>"
END_MARK="# <<< generated AI tool assets (managed by setup.sh) <<<"
BLOCK_NOTE="# Do not edit inside this block by hand; \`./setup.sh\` owns it."

DRY_RUN=0
TOOLS=""
WARNINGS=0
IGNORE_ENTRIES=""
INSTALL_HOOKS=0

usage() {
  cat <<'USAGE'
Usage: ./setup.sh [--claude] [--gemini] [--codex] [--copilot] [--hooks] [--all] [--dry-run] [--help]

Generates the tool-specific entrypoints that this repo deliberately does not commit.
With no tool flag, this help is printed and nothing on disk is touched.

Flags:
  --claude    CLAUDE.md -> AGENTS.md (root and every nested AGENTS.md), .claude/skills -> ../skills
  --gemini    GEMINI.md -> AGENTS.md (root and every nested AGENTS.md), .gemini/skills -> ../skills
  --codex     .codex/skills -> ../skills  (Codex reads AGENTS.md natively; no alias needed)
  --copilot   .github/copilot-instructions.md -> ../AGENTS.md  (repo root only)
  --hooks     .git/hooks/pre-commit -> ../../hooks/pre-commit  (redaction gate, ADR 0009)
              .git/hooks/commit-msg -> ../../hooks/commit-msg  (same gate, commit message)
  --all       every tool above, plus --hooks
  --dry-run   report the actions without touching the filesystem
  --self-test run this script's own tests (ADR 0013) and exit; writes only to a temp dir
  --help      this message

Notes:
  * Nested AGENTS.md files get a sibling alias per tool, so scoped instructions port
    to every executor. Copilot is root-only because it resolves a single
    .github/copilot-instructions.md and ignores nested copies.
  * Generated paths are written to .gitignore inside a managed block as exact,
    repo-root-anchored paths, so a committed file that merely shares a basename is
    never untracked. Re-running does not duplicate entries.
  * Existing real files, unexpected symlinks, and non-directory or symlinked parent
    paths are skipped with a loud warning, never overwritten or written through.
USAGE
}

say()  { printf '  %s\n' "$1"; }
warn() { printf '  !! WARNING: %s\n' "$1" >&2; WARNINGS=$((WARNINGS + 1)); }

add_tool() {
  case " $TOOLS " in
    *" $1 "*) : ;;
    *) TOOLS="$TOOLS $1" ;;
  esac
}

# Gitignore entries are whitespace-separated. Every generated path in this repo is
# space-free by construction; keep it that way.
add_ignore() {
  case " $IGNORE_ENTRIES " in
    *" $1 "*) : ;;
    *) IGNORE_ENTRIES="$IGNORE_ENTRIES $1" ;;
  esac
}

# link <target-relative-to-link-dir> <absolute-link-path>
# Returns nonzero when it skips, so callers keep going with the next action.
link() {
  local target="$1"
  local link_path="$2"
  local shown="${link_path#"$REPO_ROOT"/}"
  local parent
  local parent_shown
  local current

  parent="$(dirname "$link_path")"
  parent_shown="${parent#"$REPO_ROOT"/}"

  # Validate the parent directory before inspecting or creating the leaf.
  # A symlinked parent would place the link outside this repo, where the
  # relative target no longer resolves; and `mkdir -p` fails hard under
  # `set -e` when a path component is a regular file or a dangling symlink
  # (its tolerance covers pre-existing directories only).
  if [ -L "$parent" ]; then
    warn "skipping $shown: parent path '$parent_shown' is a symlink. Refusing to write through it — the link would land outside this repo and '$target' would not resolve."
    return 1
  fi
  if [ -e "$parent" ] && [ ! -d "$parent" ]; then
    warn "skipping $shown: parent path '$parent_shown' exists and is not a directory. Refusing to replace it."
    return 1
  fi

  if [ -L "$link_path" ]; then
    current="$(readlink "$link_path")"
    if [ "$current" = "$target" ]; then
      say "ok    $shown -> $target"
      return 0
    fi
    warn "skipping $shown: symlink points to '$current', expected '$target'. Remove it by hand if that is stale."
    return 1
  fi

  if [ -e "$link_path" ]; then
    warn "skipping $shown: a real file or directory already exists there. Refusing to overwrite it."
    return 1
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    say "dry   would link $shown -> $target"
    return 0
  fi

  if [ ! -d "$parent" ]; then
    mkdir -p "$parent" || {
      warn "skipping $shown: could not create parent directory '$parent_shown'."
      return 1
    }
  fi
  # Guarded like the mkdir -p above: under `set -e` a bare failure here would abort
  # the whole run mid-loop, leaving some entrypoints created, the rest missing, and
  # sync_gitignore never reached. Skip and warn instead, per the safety contract.
  ln -sfn "$target" "$link_path" || {
    warn "skipping $shown: could not create the symlink at '$link_path'."
    return 1
  }
  say "link  $shown -> $target"
}

# alias_every_agents_file <alias-basename>
# Creates the sibling alias next to every AGENTS.md in the repo, .git excluded, and
# registers each alias as an anchored gitignore path. Registration happens even when
# the link itself is skipped, so the managed block describes the whole intended set.
alias_every_agents_file() {
  local alias_name="$1"
  local agents_file dir rel
  while IFS= read -r agents_file; do
    [ -n "$agents_file" ] || continue
    dir="$(dirname "$agents_file")"
    rel="${dir#"$REPO_ROOT"}"
    add_ignore "$rel/$alias_name"
    link "AGENTS.md" "$dir/$alias_name" || :
  done <<EOF
$(find "$REPO_ROOT" -type f -name AGENTS.md -not -path "$REPO_ROOT/.git/*")
EOF
}

tool_claude() {
  say "[claude]"
  add_ignore "/.claude/skills"
  alias_every_agents_file "CLAUDE.md"
  link "../skills" "$REPO_ROOT/.claude/skills" || :
}

tool_gemini() {
  say "[gemini]"
  add_ignore "/.gemini/skills"
  alias_every_agents_file "GEMINI.md"
  link "../skills" "$REPO_ROOT/.gemini/skills" || :
}

tool_codex() {
  say "[codex]"
  add_ignore "/.codex/skills"
  link "../skills" "$REPO_ROOT/.codex/skills" || :
  say "note  Codex reads AGENTS.md directly; no instruction alias is generated."
}

tool_copilot() {
  say "[copilot]"
  add_ignore "/.github/copilot-instructions.md"
  link "../AGENTS.md" "$REPO_ROOT/.github/copilot-instructions.md" || :
  say "note  Copilot resolves only the repo-root instructions file; nested AGENTS.md are not aliased."
}

# The redaction gate from decisions/0009. Not a "tool" entrypoint: it is a git hook,
# so it is linked into .git/hooks/ and is deliberately NOT registered in .gitignore —
# nothing under .git/ is trackable, and an entry there would be noise in the managed
# block.
#
# Two hooks, one rule: pre-commit scans the staged files, commit-msg scans the proposed
# message. AGENTS.md forbids the same shapes in both, and until commit-msg existed the
# message half was documented and unenforced (ADR 0014). They share one pattern list in
# hooks/redaction-patterns.sh, which is sourced rather than linked — it is data, not a
# hook, and git has no hook slot for it.
#
# link() carries the safety contract that matters here: `gga install` writes a real
# .git/hooks/pre-commit for AI code review, and if one already exists this warns and
# skips rather than silently replacing someone's review hook. Chain them by hand if
# both are wanted — they check different things at different layers.
install_hooks() {
  say "[hooks]"
  link "../../hooks/pre-commit" "$REPO_ROOT/.git/hooks/pre-commit" || :
  link "../../hooks/commit-msg" "$REPO_ROOT/.git/hooks/commit-msg" || :
  say "note  redaction gates only. Run ./hooks/pre-commit --all to audit the whole tree,"
  say "      and ./check.sh for the structural invariants it does not cover."
}

list_contains() {
  local needle="$1"
  shift
  local item
  for item in "$@"; do
    [ "$item" = "$needle" ] && return 0
  done
  return 1
}

sync_gitignore() {
  local gi="$REPO_ROOT/.gitignore"
  local before=() inside=() after=() final=()
  local state="before" line
  local desired=()
  local entry

  for entry in $IGNORE_ENTRIES; do
    desired+=("$entry")
  done

  if [ "${#desired[@]}" -eq 0 ]; then
    return 0
  fi

  if [ -f "$gi" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
      case "$state" in
        before)
          if [ "$line" = "$BEGIN_MARK" ]; then state="inside"; else before+=("$line"); fi
          ;;
        inside)
          if [ "$line" = "$END_MARK" ]; then state="after"; else inside+=("$line"); fi
          ;;
        after)
          after+=("$line")
          ;;
      esac
    done < "$gi"
  fi

  if [ "$state" = "inside" ]; then
    warn ".gitignore has an unterminated managed block; rewriting it with a closing marker."
  fi

  # Keep entries already inside the block so a partial run (one tool) does not drop
  # another tool's entries, then add whatever is missing. Order is stable, so re-runs
  # produce byte-identical output.
  # Comments, blanks, and any entry not starting with '/' are dropped. Every path this
  # script emits is repo-root-anchored; an unanchored line is therefore legacy output
  # from an older version, where a bare `CLAUDE.md` matched at any depth and would
  # silently untrack a legitimately committed file of that name.
  local existing
  if [ "${#inside[@]}" -gt 0 ]; then
    for existing in "${inside[@]}"; do
      case "$existing" in
        /*) final+=("$existing") ;;
        *) : ;;
      esac
    done
  fi
  local want
  for want in "${desired[@]}"; do
    if [ "${#final[@]}" -eq 0 ] || ! list_contains "$want" "${final[@]}"; then
      final+=("$want")
    fi
  done

  local tmp="$gi.setup.tmp.$$"
  : >"$tmp"
  if [ "${#before[@]}" -gt 0 ]; then
    printf '%s\n' "${before[@]}" >>"$tmp"
    if [ -n "${before[$((${#before[@]} - 1))]}" ]; then
      printf '\n' >>"$tmp"
    fi
  fi
  printf '%s\n%s\n' "$BEGIN_MARK" "$BLOCK_NOTE" >>"$tmp"
  printf '%s\n' "${final[@]}" >>"$tmp"
  printf '%s\n' "$END_MARK" >>"$tmp"
  if [ "${#after[@]}" -gt 0 ]; then
    printf '%s\n' "${after[@]}" >>"$tmp"
  fi

  if [ -f "$gi" ] && cmp -s "$tmp" "$gi"; then
    rm -f "$tmp"
    say "ok    .gitignore managed block already up to date"
    return 0
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    rm -f "$tmp"
    say "dry   would update the .gitignore managed block (${#final[@]} entries)"
    return 0
  fi

  # This runs after every entrypoint already exists on disk. A bare failure here would
  # abort with generated files present but absent from the managed block, so a later
  # `git add -A` would commit exactly what this repo refuses to commit. Warn loudly and
  # remove the temp file rather than leaving it behind.
  mv "$tmp" "$gi" || {
    rm -f "$tmp"
    warn "could not write '$gi': the managed block was NOT updated. Generated entrypoints may exist on disk without being gitignored — do not commit until this is fixed."
    return 1
  }
  say "write .gitignore managed block (${#final[@]} entries)"
}

# --- self-test ---------------------------------------------------------------
#
# ADR 0013: a committed executable carries its own test, exposed as a flag on that
# executable. Run `./setup.sh --self-test` after editing this file. It is not run
# automatically — that expectation lives in OPERATIONS.md.
#
# What it covers is the safety contract in the header, and only the failures that
# are SILENT. A run that prints "Done." while it has overwritten a committed file,
# retargeted someone else's symlink, or written an unanchored .gitignore entry that
# untracks a real file, is the failure worth a test. Output wording is not.
#
# Every case builds a throwaway repo under `mktemp -d` holding a copy of this
# script, so nothing here reads or writes the repository it ships in.

ST_FAILS=0
ST_TMPDIRS=""
ST_DIR=""
ST_RC=0

st_pass() { printf '  PASS  %s\n' "$1"; }
st_fail() { printf '  FAIL  %s\n' "$1" >&2; ST_FAILS=$((ST_FAILS + 1)); }

st_cleanup() {
  local d
  for d in $ST_TMPDIRS; do
    [ -n "$d" ] && [ -d "$d" ] && rm -rf "$d"
  done
}

# st_sandbox — fresh throwaway repo with a copy of this script. Sets ST_DIR.
# Deliberately not a command substitution: that runs in a subshell, and the
# temp-directory list it appended to would be discarded, leaking every sandbox.
st_sandbox() {
  ST_DIR="$(mktemp -d)"
  ST_TMPDIRS="$ST_TMPDIRS $ST_DIR"
  mkdir -p "$ST_DIR/skills/example" "$ST_DIR/hooks"
  printf 'root instructions\n' >"$ST_DIR/AGENTS.md"
  printf 'placeholder\n' >"$ST_DIR/skills/example/SKILL.md"
  printf '#!/bin/sh\nexit 0\n' >"$ST_DIR/hooks/pre-commit"
  printf '#!/bin/sh\nexit 0\n' >"$ST_DIR/hooks/commit-msg"
  chmod +x "$ST_DIR/hooks/pre-commit" "$ST_DIR/hooks/commit-msg"
  cp "$REPO_ROOT/setup.sh" "$ST_DIR/setup.sh"
  chmod +x "$ST_DIR/setup.sh"
  git -C "$ST_DIR" init -q >/dev/null 2>&1 || :
}

# st_run <sandbox> <args...> — runs the sandboxed copy. Records its status in
# ST_RC and always returns 0, so `set -e` does not abort the suite on a run that
# is *expected* to exit nonzero.
st_run() {
  local d="$1"
  shift
  ST_RC=0
  ( cd "$d" && ./setup.sh "$@" ) >/dev/null 2>&1 || ST_RC=$?
  return 0
}

# The header promises a pre-existing regular file is never overwritten. This is the
# case that costs a committed file if it ever regresses.
st_case_keeps_real_file() {
  st_sandbox
  local d="$ST_DIR"
  printf 'hand written, committed\n' >"$d/CLAUDE.md"
  st_run "$d" --claude
  if [ -L "$d/CLAUDE.md" ]; then
    st_fail "a pre-existing regular CLAUDE.md was replaced by a symlink"
  elif [ "$(cat "$d/CLAUDE.md")" != "hand written, committed" ]; then
    st_fail "a pre-existing regular CLAUDE.md was modified"
  elif [ "$ST_RC" -eq 0 ]; then
    st_fail "skipping a real file exited 0; a warning must exit nonzero"
  else
    st_pass "keeps a pre-existing regular file, and exits nonzero"
  fi
}

# `gga install` writes a real .git/hooks/pre-commit, and other tools alias the same
# basenames. Retargeting someone else's link is the silent half of that collision.
st_case_keeps_foreign_symlink() {
  st_sandbox
  local d="$ST_DIR"
  ln -s SOMETHING_ELSE.md "$d/CLAUDE.md"
  st_run "$d" --claude
  if [ "$(readlink "$d/CLAUDE.md")" != "SOMETHING_ELSE.md" ]; then
    st_fail "a symlink pointing somewhere unexpected was retargeted instead of skipped"
  elif [ "$ST_RC" -eq 0 ]; then
    st_fail "skipping an unexpected symlink exited 0"
  else
    st_pass "keeps a symlink that points somewhere unexpected"
  fi
}

# The one that untracks a real file. An unanchored `CLAUDE.md` matches at any depth,
# so a legitimately committed file of that name disappears from git with no error.
st_case_drops_unanchored_ignore() {
  st_sandbox
  local d="$ST_DIR"
  {
    printf '%s\n' "$BEGIN_MARK"
    printf '%s\n' "$BLOCK_NOTE"
    printf 'CLAUDE.md\n'
    printf '%s\n' "$END_MARK"
  } >"$d/.gitignore"
  st_run "$d" --claude
  if grep -qx 'CLAUDE.md' "$d/.gitignore"; then
    st_fail "an unanchored legacy entry survived; it untracks a committed file of that name at any depth"
  elif ! grep -qx '/CLAUDE.md' "$d/.gitignore"; then
    st_fail "the anchored entry /CLAUDE.md was not written"
  else
    st_pass "drops unanchored legacy entries, writes repo-root-anchored paths"
  fi
}

# The header promises running twice is a no-op. Byte-identical, not merely valid:
# duplicating entries is the drift this managed block exists to prevent.
st_case_idempotent() {
  st_sandbox
  local d="$ST_DIR"
  st_run "$d" --claude
  cp "$d/.gitignore" "$d/gitignore.first.$$"
  st_run "$d" --claude
  if [ "$ST_RC" -ne 0 ]; then
    st_fail "a second identical run exited $ST_RC; re-running must be a no-op"
  elif ! cmp -s "$d/gitignore.first.$$" "$d/.gitignore"; then
    st_fail "a second run changed .gitignore; entries are duplicating"
  else
    st_pass "re-running is a no-op and .gitignore stays byte-identical"
  fi
}

# A dry run that writes is worse than no dry run: it is inspected precisely by
# someone who has decided not to commit yet.
st_case_dry_run_writes_nothing() {
  st_sandbox
  local d="$ST_DIR"
  st_run "$d" --claude --dry-run
  if [ -e "$d/CLAUDE.md" ] || [ -L "$d/CLAUDE.md" ]; then
    st_fail "--dry-run created CLAUDE.md"
  elif [ -e "$d/.claude" ]; then
    st_fail "--dry-run created the .claude parent directory"
  elif [ -e "$d/.gitignore" ]; then
    st_fail "--dry-run wrote .gitignore"
  elif [ "$ST_RC" -ne 0 ]; then
    st_fail "--dry-run on a clean tree exited $ST_RC"
  else
    st_pass "--dry-run touches nothing on disk"
  fi
}

# Hooks contribute no gitignore entries. Rewriting the block on a --hooks-only run
# would churn a committed file for a run that had nothing to sync.
st_case_hooks_only_leaves_ignore_alone() {
  st_sandbox
  local d="$ST_DIR"
  printf 'notes\n' >"$d/.gitignore"
  st_run "$d" --hooks
  if [ ! -L "$d/.git/hooks/pre-commit" ]; then
    st_fail "--hooks did not install the pre-commit gate"
  elif [ ! -L "$d/.git/hooks/commit-msg" ]; then
    st_fail "--hooks did not install the commit-msg gate"
  elif [ "$(cat "$d/.gitignore")" != "notes" ]; then
    st_fail "--hooks rewrote .gitignore; a hooks-only run has nothing to sync"
  elif [ "$ST_RC" -ne 0 ]; then
    st_fail "--hooks on a clean tree exited $ST_RC"
  else
    st_pass "--hooks installs both gates and leaves .gitignore untouched"
  fi
}

self_test() {
  printf 'setup.sh --self-test (ADR 0013)\n\n'
  trap st_cleanup EXIT
  st_case_keeps_real_file
  st_case_keeps_foreign_symlink
  st_case_drops_unanchored_ignore
  st_case_idempotent
  st_case_dry_run_writes_nothing
  st_case_hooks_only_leaves_ignore_alone
  if [ "$ST_FAILS" -eq 0 ]; then
    printf '\n  self-test: 6 case(s) passed\n'
    return 0
  fi
  printf '\n  self-test: %s of 6 case(s) FAILED\n' "$ST_FAILS" >&2
  return 1
}

main() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --claude)  add_tool claude ;;
      --gemini)  add_tool gemini ;;
      --codex)   add_tool codex ;;
      --copilot) add_tool copilot ;;
      --hooks)   INSTALL_HOOKS=1 ;;
      --all)     add_tool claude; add_tool gemini; add_tool codex; add_tool copilot; INSTALL_HOOKS=1 ;;
      --dry-run) DRY_RUN=1 ;;
      --self-test) self_test; exit $? ;;
      -h|--help) usage; exit 0 ;;
      *)
        printf 'setup.sh: unknown option: %s\n\n' "$1" >&2
        usage >&2
        exit 2
        ;;
    esac
    shift
  done

  if [ -z "$TOOLS" ] && [ "$INSTALL_HOOKS" -eq 0 ]; then
    usage
    exit 0
  fi

  [ "$DRY_RUN" -eq 1 ] && say "dry-run: nothing will be written"
  say "repo: $REPO_ROOT"

  local tool
  for tool in $TOOLS; do
    "tool_$tool"
  done

  [ "$INSTALL_HOOKS" -eq 1 ] && install_hooks

  # Hooks contribute no gitignore entries, so a --hooks-only run has nothing to sync
  # and must not rewrite the managed block.
  if [ -z "$TOOLS" ]; then
    if [ "$WARNINGS" -gt 0 ]; then
      printf '\nDone with %s warning(s). Nothing was overwritten.\n' "$WARNINGS" >&2
      exit 1
    fi
    printf '\nDone. Run this again any time; it is idempotent.\n'
    return 0
  fi

  say "[gitignore]"
  # `|| :` keeps the warn-and-continue contract: sync_gitignore already warned and
  # incremented WARNINGS, so the run must still reach the summary below and exit 1
  # rather than dying here under `set -e`.
  sync_gitignore || :

  if [ "$WARNINGS" -gt 0 ]; then
    printf '\nDone with %s warning(s). Nothing was overwritten.\n' "$WARNINGS" >&2
    exit 1
  fi
  printf '\nDone. Run this again any time; it is idempotent.\n'
}

main "$@"
