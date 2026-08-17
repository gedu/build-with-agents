#!/bin/sh
#
# hooks/redaction-patterns.sh — the one redaction pattern list, sourced by every gate.
#
# This file is DATA, not a gate. It is sourced, never executed:
#
#   . "<hooks-dir>/redaction-patterns.sh"
#   redaction_patterns | while IFS= read -r entry; do ...; done
#
# WHY IT EXISTS
#   `hooks/pre-commit` scans staged files, `hooks/commit-msg` scans the proposed commit
#   message. Both enforce the same rule (AGENTS.md, ADR 0009) and must therefore forbid
#   exactly the same shapes. Two copies of a security gate's pattern list is a defect and
#   not a style question: the copies drift, the weaker one is the one that fires, and
#   nothing reports the divergence. One list, two readers.
#
# FORMAT
#   One entry per line: <label>|<extended regex>
#   Blank lines and lines starting with `#` are ignored by every reader.
#   The label is what a human sees when the gate fires, so write it as the category, not
#   as the regex. The regex is `grep -E`, POSIX — see PORTABILITY below.
#
# THIS FILE DESCRIBES SHAPES AND CONTAINS NO INSTANCE OF ONE
#   AGENTS.md: "Never paste a real value in order to describe how to find it." Every
#   pattern below requires a real path segment or a real token body, so no pattern matches
#   its own source text and the documented angle-bracketed placeholders never match. That
#   is a property of the patterns, not an exemption: this file is scanned like any other
#   tracked file by `./hooks/pre-commit --all`. Adding a pattern that matches this file is
#   how you find out — it will correctly block its own commit.
#
# WHAT THIS LIST DELIBERATELY DOES NOT COVER
#   * a private project or client name written as a bare word. No pattern separates a
#     public repository name from a client's; that stays a judgment call and lives in
#     AGENTS.md as an ask-before-writing rule. A clean run is not evidence about it.
#   * hostnames. Every URL contains one, so a generic pattern is all false positives.
#
# PORTABILITY
#   POSIX `grep -E`, not `rg`, and no backreferences, lookarounds, `\d` or `{,n}`. A
#   committed hook must run on a machine that has not installed anything, so this list
#   must stay inside the grammar every `grep -E` implements.
#
# TESTING
#   This file has no flag of its own to run: it is data with no control flow, and ADR 0013
#   attaches a test to an executable. It is covered from both sides instead —
#   `./hooks/pre-commit --self-test` and `./hooks/commit-msg --self-test` each assert a
#   real finding through this list, and each asserts exit 2 when this file is missing.
#   Run both after editing it.

# Home-path patterns require at least one character from a real path-segment class after
# the separator. That is exactly what exempts `<home>/…` and `<repo>/…` from matching.
redaction_patterns() {
  cat <<'PATTERNS'
absolute home path (POSIX)|(/Users|/home)/[A-Za-z0-9._-]
absolute home path (Windows)|[A-Za-z]:\\Users\\[A-Za-z0-9._-]
GitHub token|(ghp_|gho_|ghs_|github_pat_)[A-Za-z0-9_]{16,}
Slack token|xox[baprs]-[A-Za-z0-9-]{10,}
OpenAI-style key|sk-[A-Za-z0-9_-]{20,}
AWS access key id|AKIA[0-9A-Z]{16}
PEM private key|-----BEGIN [A-Z ]*PRIVATE KEY-----
PATTERNS
}
