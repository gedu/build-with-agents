---
id: sdd/testing-capabilities
type: journal
targets: [any]
status: draft
verified: 2026-08-06
sources: ["AGENTS.md", "hooks/pre-commit", "journal/2026-08-05-redaction-gate-and-2478-on-224.md"]
---

# Testing Capabilities

Detected at SDD init. This is a knowledge-base repo (Markdown + two Bash scripts), not an
application with a package manager or a test framework. Do not invent a test command for
later SDD phases to run — none exists.

## Testing Capabilities

**Strict TDD Mode**: disabled
**Detected**: 2026-08-06

### Test Runner

- Command: none
- Framework: none. No `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, or `Makefile`
  exists in this repo. `journal/2026-08-05-redaction-gate-and-2478-on-224.md` §7 already
  records "no committed test for `hooks/pre-commit`" as an open, ADR-shaped gap — this is not
  a new finding, it is confirmation of a known one.

### Test Layers

| Layer       | Available | Tool |
| ----------- | --------- | ---- |
| Unit        | ❌        | —    |
| Integration | ❌        | —    |
| E2E         | ❌        | —    |

### Coverage

- Available: ❌
- Command: —

### Quality Tools

| Tool         | Available | Command |
| ------------ | --------- | ------- |
| Linter       | ❌        | — (no `shellcheck` on this machine either) |
| Type checker | ❌        | — (no typed language in this repo) |
| Formatter    | ❌        | — |

## What DOES exist and is real verification

Not a test runner, but a functioning, committed gate — later phases should treat these as the
available checks, and must not be told to "run the tests" when there are none.

| Check | Command | Meaning |
| --- | --- | --- |
| Redaction gate (staged diff) | `./hooks/pre-commit` | Exit 0 clean, 1 finding, 2 could not run (never conflate 2 with 0) |
| Redaction gate (whole tree) | `./hooks/pre-commit --all` | Same exit contract, audits every tracked file |
| Shell syntax check | `bash -n <script>` | Confirms a shell script parses; not a behavior test |

Both `hooks/pre-commit` and `setup.sh` currently pass `bash -n`.

## Implication for later SDD phases

- `sdd-tasks` and `sdd-apply` must not schedule a "run the test suite" step.
- Verification for a change touching `hooks/pre-commit` or `setup.sh` means: `bash -n`, a manual
  exercise of the affected code path, and `./hooks/pre-commit --all` where redaction-relevant.
- Verification for a change touching only `theory/`, `research/`, `decisions/`, or `journal/`
  means: frontmatter contract compliance and citability rules — there is no runtime to exercise.
