---
id: operations
type: index
targets: [any]
status: validated
verified: 2026-08-13
sources: ["AGENTS.md", "MAP.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0011-rig-produces-evidence-not-truth.md", "theory/agents/capability-load-cost.md"]
---

# OPERATIONS.md — what to run, and when

`MAP.md` answers *where does knowledge live*. This file answers *what can I execute, and at what moment*.

Written for an agent. Read it when you are about to change something, verify something, or measure
something — not on arrival.

## What this file deliberately does not contain

**Flags.** Every command below has `--help`, and that is the authority for its interface. Copying flag
lists here would create a hand-maintained table that duplicates a source of truth and drifts from it
silently — the failure `AGENTS.md` forbids and the one `decisions/0004` records this repo committing.

What `--help` cannot tell you is **when** to run something and **what its output obliges you to do**.
That is the whole content of this file.

It also lives outside `AGENTS.md` on purpose. Per `theory/agents/capability-load-cost.md`, a procedure
only some sessions need belongs behind a read-on-demand pointer rather than in an always-resident file.
`AGENTS.md` carries the pointer; the procedure is here.

## Decision table — start here

| You are about to… | Run | Non-negotiable? |
|---|---|---|
| Work in a fresh clone | `./setup.sh --<tool>` | Yes. Nothing tool-specific is committed |
| Get the redaction gates installed | `./setup.sh --hooks` | Yes. Without it neither gate fires |
| Commit anything | nothing — both hooks fire by themselves | Yes, once installed |
| Check the whole tree, not just a diff | `./hooks/pre-commit --all` | Before any push, and after any bulk edit |
| Check commit messages that are already written | `./hooks/commit-msg --range <A> <B>` | Before pushing from a checkout where the hooks were never installed |
| Check the structural invariants | `./check.sh` | After writing or editing any content `.md`, and after adding a skill |
| Change `hooks/pre-commit` or `hooks/commit-msg` | that file's `--self-test` | Yes. Each gate carries its own test (ADR 0013) |
| Change `hooks/redaction-patterns.sh` | **both** hooks' `--self-test` | Yes. One list, two readers |
| Change `check.sh` | `./check.sh --self-test` | Yes, same reason |
| Change shell | `sh -n <file>`, or `bash -n` for `setup.sh` and `hooks/pre-commit` | Yes. There is still no test *runner*, by decision — ADR 0013 |
| Change Python | `python3 -m py_compile <file>` | Yes, same reason |
| Change `rig/collect.py` | `python3 rig/collect.py --self-test` | Yes. The collector carries its own test, same flag-gated shape as `hooks/pre-commit --self-test` (ADR 0013) |
| Produce a measurement | `./rig/run.sh` → `rig/derive.py` → `rig/report.py` | In that order. See below |
| Commit reviewed work | see *Review lifecycle* | Currently blocked upstream. See below |

## The gates, and what their exits oblige

### `./hooks/pre-commit`

The redaction gate (ADR 0009). Runs automatically on commit once `./setup.sh --hooks` has linked it.

**In a worktree it does not run your copy, and it may not run at all.** `setup.sh --hooks` installs
`.git/hooks/pre-commit -> ../../hooks/pre-commit`, and worktrees share the common directory, so that
symlink resolves to the **original checkout's** working tree. Verified 2026-08-13: a commit made in a
worktree is scanned by whatever version of the script the original checkout has on its current
branch — and if that branch has no `hooks/` at all, the symlink dangles, git skips the hook in
silence, and the commit lands **with no gate**, exit 0, no warning.

So from a worktree, run it explicitly before committing and do not rely on it firing:

```sh
./hooks/pre-commit --all      # from your worktree, not from the original checkout
```

`skills/checkout-isolation` carries the reproduction and the rest of the shared-checkout hazards.

| Exit | Meaning | What you must do |
|---|---|---|
| 0 | Clean | Proceed |
| 1 | A finding | Fix it. Never `--no-verify` past a finding |
| 2 | **Could not run** | **Treat as a failure, not a pass.** Something broke — a bad pattern, a locale problem, an unreadable file. Diagnose before committing |

Exit 2 exists because a check that cannot run is not a check. That distinction is the subject of
`theory/loops/verifier-availability.md`, and this gate shipped with a fail-open on its first day —
see `journal/2026-08-05-redaction-gate-and-2478-on-224.md`.

**What it does not catch**, and you must therefore catch yourself: a private project or client name
written as a bare word. No pattern can tell a public repository name from a client's. A clean run is not
evidence about that class — ask before writing a shared source's name, per `AGENTS.md`.

### `./hooks/commit-msg`

The same redaction rule over the **proposed commit message**, which `pre-commit` never saw —
`AGENTS.md` forbids the same shapes "in prose, in frontmatter, or in a commit message". Installed by
`./setup.sh --hooks` alongside `pre-commit`, and it shares one pattern list with it,
`hooks/redaction-patterns.sh`. Exit codes are `pre-commit`'s, and mean the same things.

A message rejected here has **not** entered history: fix the message and commit again. That is the
whole reason this runs at `commit-msg` rather than after a push.

Two modes, and the second is the one you need in a worktree or a fresh clone:

```sh
./hooks/commit-msg <file>          # what git calls. Never run by hand
./hooks/commit-msg --range <A> <B> # every commit message in A..B. `-` for A means "no lower bound"
```

`--range` refuses an unresolvable revision with exit 2 rather than scanning an empty range, and it
prints the number of messages it actually scanned, including zero. **Read that number**: a range that
turns out to be empty and a range that was clean look identical otherwise.

### `./check.sh`

The structural invariants `hooks/pre-commit` does not cover, and the counterpart to it: that gate
answers *does this contain something that must never be published*, this one answers *does this repo
still hold the shape its own rules describe*. Frontmatter on every content `.md`, and every directory
under `skills/` having an entry in `ASK.md`. Reasoning in ADR 0014, which is `draft` — the decision is
implemented, the operator has not ratified it.

| Exit | Meaning | What you must do |
|---|---|---|
| 0 | Clean | Proceed |
| 1 | A violation | Fix it. The file and the field are named |
| 2 | **Could not run** | **Treat as a failure, not a pass.** An unreadable file, no content files found, or `skills/` present with no `ASK.md` |

It reads tracked files **and** untracked files git would not ignore, which is where it differs from
`./hooks/pre-commit --all`. That gate reads tracked files only, so a file you just wrote and have not
staged is invisible to it — recorded in `journal/2026-08-13-skills-nobody-could-ask-for.md`. Anything
under `rig/fixtures/` is out of scope by design; those files imitate a foreign project.

What it does **not** check: whether an `ASK.md` entry is any good, `targets` membership, and whether a
`sources` entry resolves. `./check.sh --help` carries the full list and the reason for each.

### There is no CI. Every command above is yours to run

ADR 0014 decided this repository needs a server-side copy of these checks and records why it is
deferred. Nothing on a server runs them today, so treat this section as the operating reality rather
than a temporary note:

- **Before any push**, run `./hooks/pre-commit --all` and `./check.sh`. Nothing will do it for you and
  nothing will tell you that you skipped it.
- **`--all` reads tracked files only.** A file you just wrote is invisible to it until you stage it.
  Staging then rerunning is the check; writing then running is not.
- **A clone has no gate at all** until somebody runs `./setup.sh --hooks`, and a worktree does not
  inherit that install. Run `skills/checkout-isolation`'s gate check to see which `pre-commit` — if
  any — actually guards the tree you are in.

`main` is protected by a repository ruleset: pull request required, force-push and deletion blocked,
and **no required status check**, because there is no check for it to require. A pull request
therefore merges on nobody having looked.

Nothing in that file may `continue-on-error`, `|| true`, or skip its way to green. A job that cannot
run its check must fail; that is the rule the whole file exists to hold.

### `bash -n` and `python3 -m py_compile`

This project has **no test runner** (`sdd/testing-capabilities.md`). These two, the `--self-test` flag on
each committed executable (ADR 0013), and running the thing and reading its real output are the entire
verification surface. A claim that something works must be backed by output you actually produced.

Note which shell: `setup.sh` and `hooks/pre-commit` are `bash`; `hooks/commit-msg`, `check.sh` and
`hooks/redaction-patterns.sh` are POSIX `sh`, so `sh -n` is the right check for those three.

## Producing a measurement

Three programs, one direction, no shared state but files. ADR 0010 governs what a measurement may vary;
ADR 0011 governs what its output may claim.

```
./rig/run.sh <task_id> <arm> <iteration>   # ONE run. Guards, launches, persists. Parses nothing
python3 rig/derive.py                      # ALL run dirs -> rows. Total function, rebuilds every time
python3 rig/report.py                      # rows -> four-cell tables
```

**Order matters and the split is the point.** `run.sh` never decides an outcome, so a checker bug costs a
re-derivation rather than 30 re-runs. `derive.py` is *total* — it rebuilds `runs.jsonl` completely on
every invocation, which is why double-counting is structurally impossible rather than defended against.

| Situation | What it means |
|---|---|
| `run.sh` exits 2 | Could not run. A dirty tree, a missing preimage, a failed prerequisite. Nothing was measured |
| A row is `void` | Environmental, not a result. Excluded and replaced. `void_reason` says why |
| A row is `state: complete` | It produced numbers, pass or fail. Both are results |
| `report.py` names excluded slots | Read them. A slot voided in one arm removes its pair from the comparison |

**Before believing any number**, confirm `derive.py` reproduces byte-identically across two runs. That is
the cheapest available proof that the deriver is a function of the run directories and nothing else.

**Before quoting any number**, read ADR 0011: rig output is **evidence, not truth**. A figure becomes
citable only by promotion into `theory/` carrying its scope, its spread and the honesty contract. Never
quote a row.

## Review lifecycle — currently blocked, and this is the state to check first

`gentle-ai` provides the bounded review whose receipt the delivery gates validate. **Do not explore its
commands.** Bootstrap once and execute only the exact transition it returns:

```
gentle-ai review status --cwd . --contract gentle-ai.review-integration/v2 --next-transition
```

The contract is `/v2` as of 2.3.0. It was `/v1` here until the generated rules were regenerated by the
upgrade; `upstream/gentle-ai/0003-*` records that transition and is closed.

**Review is currently DISABLED for this clone**, since 2026-08-10:
`gentle-ai review mode disable --scope clone`. Global is untouched, so other repositories are unaffected.
Re-enable with `gentle-ai review mode enable`. Delivery here runs under ordinary repository policy — the
redaction gate, `bash -n`, the self-test — and reports `disabled/unmanaged`, never a fabricated approval.

**Two blockers, and the earlier one is not #2478.**

1. `capture-result` rejects every reviewer artifact with `reviewer artifact admission incomplete:
   reviewer evidence reports that candidate inspection was unavailable`, so a review cannot even record
   its lens results. Note the message misdiagnoses: the first real cause is a missing top-level `lens`
   field, which `gentle-ai review advisory validate` reports correctly and which the published schema
   marks *optional*. Adding it makes `advisory validate` return `transport_validated: true` while
   `capture-result` still refuses. Do not trust that error string; run `advisory validate` instead.
2. `finalize --validation` refuses evidence that `status` reports as accepted — upstream
   [#2478](https://github.com/Gentleman-Programming/gentle-ai/issues/2478), open, confirmed on 2.2.4.
   **Status on 2.3.0 is unknown**: blocker 1 stops the lifecycle before it can be reached. Full
   reproduction in `journal/2026-08-05-redaction-gate-and-2478-on-224.md`.

Also on record: `gentle-ai review abandon` refuses a pristine lineage when an *unrelated* lineage in the
same store is corrupt, and `review repair --preflight` classifies the store as unrepairable. That is why
the kill switch, not `abandon`, was the exit taken here.

Two facts that cost time before they were written down:

- **A fresh `review start` reaches the defect; replaying an abandoned lineage does not** — it stops
  earlier at `recovery_authorization_required`. To test a correction-stage defect, open a new lineage.
- **An abandoned lineage in `reviewing` is not a blocker.** Re-run the bootstrap: unrelated content
  returns `applicability: unrelated`. A previous session lost two days to reading it as a blocker.

`gga` is a different tool for a different job — AI code review at pre-commit. Its verdict is
probabilistic, which is the wrong layer for redaction. Keep the two hooks separate; `setup.sh` warns and
skips rather than replacing an existing hook.

## Prerequisites, and where they do and do not apply

| Tool | Needed for | Notes |
|---|---|---|
| `bash`, `git` | Everything | — |
| `python3` (stdlib only) | `rig/derive.py`, `rig/report.py` | **Rig-only.** The hooks and `check.sh` deliberately do not depend on it — they must run on a machine that installed nothing, and in CI with no setup step |
| GNU-compatible `timeout` | `rig/run.sh`, `rig/run-pipeline.sh` | **Rig-only.** macOS ships a BSD `timeout` that is not compatible; `brew install coreutils` provides the GNU one. Both runners' preflight `die_cannot_run`s without it |
| `node` (≥18), `npm`, Jest | `rig/fixtures/failure-flood/*`'s own runtime (design.md sec 5) | **Rig-only AND fixture-only.** `node_modules/` is installed on demand by `run-pipeline.sh`'s own `npm ci` step, into a per-run `mktemp` directory outside the repo entirely — never into the fixture tree, so no `.gitignore` change is needed |
| `claude` CLI | `rig/run.sh` | Subscription auth is enough. No API key. `--bare` is not used in v1 |
| `gentle-ai` | Review lifecycle | Installed here: **2.3.0 stable** (auto-updated from 2.2.4 on 2026-08-10; `gga` wrapper still v2.10.1). Review is disabled for this clone — see *Review lifecycle* |

## When something is wrong

- **A gate reports exit 2** — it could not run. That is not a pass and never a reason to proceed.
- **A number surprises you** — check what produced it before believing it. A fixture that reverts the
  code under test and then reports every fix as failed is a real incident in this repo, not a
  hypothetical; see `theory/loops/reading-and-running-find-different-defects.md`.
- **A sub-agent reports success** — verify the artifacts, paths and effects. A report is a claim.
- **A flag behaves unlike its description** — believe the run. Reading `--help` produced three confident
  wrong conclusions in this project's short history, and each was corrected by two cheap probes.
