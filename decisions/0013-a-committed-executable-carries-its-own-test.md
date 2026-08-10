---
id: decisions/0013-a-committed-executable-carries-its-own-test
type: decision
targets: [any]
status: validated
verified: 2026-08-10
sources: ["decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0011-rig-produces-evidence-not-truth.md", "hooks/pre-commit", "rig/derive.py", "sdd/measurement-rig/tasks.md", "journal/2026-08-10-upstream-audit-handoff.md"]
---

# 0013 — A committed executable carries its own test, invoked by its own flag

## Context

This repo commits two executables that enforce things: `hooks/pre-commit`, the ADR 0009 redaction
gate, and `rig/run.sh` with `rig/derive.py`, the measurement instrument. Only one of them has ever
been tested, and it was never decided that it should be — `derive.py` grew a checker self-test
because a phase needed one.

`hooks/pre-commit` has no test at all. That gap has been recorded five separate times across the
journal without ever being resolved, which is the signature of a missing decision rather than a
missing task: nobody was refusing to write the test, there was simply nowhere agreed for it to go.

The trigger is concrete. On 2026-08-10 the hook was changed to close a fail-open (`5703c92`): in
`--all` mode an unreadable tracked file was silently skipped while the run reported "clean across N
tracked files" and exited 0. The fix was verified by hand, with the committed version as a control.
That verification was real and it is now gone — it lived in a terminal, not in the repository.
Nothing would catch a future edit that reintroduces `|| :`.

Ratified by the operator on 2026-08-10, who delegated the choice between the two candidate layouts
to this recommendation.

## Decision

**A committed executable carries its own test, exposed as a flag on that executable.** For the
redaction gate that is `hooks/pre-commit --self-test`. No `tests/` directory and no runner are
created until there are enough tests that extracting one is answering a real problem rather than
anticipating it.

Three reasons, and the second is the one specific to this repo.

### The precedent already exists and already works

`rig/derive.py` carries a checker self-test that fires `PASS` for `t1`, `t3` and `t3v2`, and it was
load-bearing during the schema-2 bump: it is part of what proved the change non-breaking. The
pattern is not hypothetical here, it is the only tested code in the repository.

### The gate's own portability rule forbids the alternative

`hooks/pre-commit` states it in its header: *"POSIX `grep -E`, not `rg`. A committed hook must run
on a machine that has not installed anything."* A test living outside the script needs something to
run it, and that something is a dependency the file has explicitly refused. A self-test inherits the
constraint instead of fighting it — whatever can run the hook can run its test.

### Building a framework for one test is the mistake this repo keeps naming

`blocks/` and `templates/` are empty, and `MAP.md` is hand-maintained because ADR 0004's query
tooling was never built. This repo's standing failure mode is infrastructure ahead of content, not
behind it. A `tests/` directory with a runner, a convention and a discovery rule, built to hold one
test, is that failure mode with a green checkmark on it.

## Consequences

| Consequence | Detail |
|---|---|
| The test cannot be orphaned | It ships in the file it tests. There is no path where the executable is copied, vendored or edited and its test is left behind |
| The test must construct forbidden strings at runtime | A self-test for the redaction gate cannot contain a literal home path, or the gate correctly blocks its own commit. Build the string from fragments that do not match alone. This is a real constraint and it is also a second, free test of the pattern set |
| A totally broken script cannot report its own failure | Accepted. `bash -n` covers syntax, and a hook broken badly enough to not run fails loudly on the next commit rather than silently passing. The failure mode a self-test must catch is the *silent* one — a gate that runs, reports clean, and checked nothing |
| The self-test is not run automatically | Deliberate. Running it inside the commit path would put temporary-directory creation and `chmod` into every commit. It is invoked when the executable changes, and that expectation lives in `OPERATIONS.md` |
| Extraction stays open | When a third executable needs a test, or when a test needs fixtures too large to inline, extracting a runner becomes a real problem with real inputs. This ADR is superseded then, not worked around |

## Alternatives

| Rejected | Reason |
|---|---|
| A `tests/` directory with a runner | New infrastructure, a new convention and a new dependency, created to hold exactly one test. It also reintroduces the drift this repo has already suffered elsewhere: two files that must be kept in step, with nothing enforcing it |
| Keep verifying by hand, as `5703c92` did | It works exactly once. The evidence lives in a terminal and dies with it, which is how the same gap got recorded five times without ever being closed |
| A test framework (bats, shunit2) | Directly contradicts the hook's portability rule. A gate that cannot run on a fresh machine is not a gate |
| Run the self-test automatically inside the commit path | Puts `mktemp`, `git init` and `chmod` on every commit, so the gate becomes slower and more failure-prone in exchange for testing something that only changes when someone edits it |
