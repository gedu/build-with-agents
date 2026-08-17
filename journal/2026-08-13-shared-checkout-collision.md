---
id: journal/2026-08-13-shared-checkout-collision
type: journal
targets: [any]
status: draft
verified: 2026-08-13
sources: ["skills/checkout-isolation/SKILL.md", "OPERATIONS.md", "theory/loops/verifier-availability.md", "https://code.claude.com/docs/en/cross-session-messaging"]
---

# 2026-08-13 — two sessions, one checkout, and a gate that stops firing

Provenance for `skills/checkout-isolation`. Not authority (ADR 0007).

## How it was found

Mid-task, `./hooks/pre-commit --all` reported **158 tracked files** where the previous run in the
same session had reported 115. Nothing in this session had added 43 files.

The count was the only symptom. Everything else looked normal: `git status` was clean apart from the
expected edits, the files were where they should be, and the work applied. Chasing the number found
that `HEAD` was a commit this session never made, and that the checkout had been moved to
`sdd/failure-flood-triage-planning` — a branch created by another session — **while this one was
editing files in it**.

Nothing errored. There was no conflict, no lock, no warning. The branch changed underneath and the
work simply continued, on the wrong branch.

`ListAgents` then confirmed it directly rather than by inference: `build-with-agents-aa`,
interactive, `busy`, started two days earlier.

## What was verified, and what it cost to verify

### The hook hazard — the finding worth keeping

A worktree does **not** run its own copy of the redaction gate.

`setup.sh --hooks` installs `.git/hooks/pre-commit -> ../../hooks/pre-commit`. Worktrees share the
common directory, so `../../` climbs out of `<original>/.git/hooks/` into the **original checkout's**
working tree. Resolved live: `git rev-parse --git-path hooks/pre-commit` in the worktree returned the
original checkout's path, and its realpath was the original checkout's `hooks/pre-commit`.

Reproduced in a throwaway repository, both halves:

| Original checkout's branch | Commit in the worktree |
|---|---|
| Has `hooks/pre-commit` | Runs **that** version of the gate. Blocked, exit 1 |
| Has no `hooks/` | Symlink dangles, git **skips the hook silently**. Commit lands, exit 0, no output |

The second row is the more dangerous one and it is `theory/loops/verifier-availability.md` verbatim:
not a weak gate, an absent one reporting nothing. **Another session changing branch in their checkout
can disarm the redaction gate of a public repository for every worktree, with no surface saying so.**

### The first test of this was wrong

The first attempt hid `git worktree add`'s failure behind `2>/dev/null`. The add failed — `main` was
already checked out — so the whole test ran in the wrong directory and still printed plausible
output. It was rerun properly rather than reported.

Worth recording because it is the same failure class as the finding itself: a step that could not run,
producing output that looks like a result. The `2>/dev/null` that hid it is the same shape as the
`|| :` this repo removed from its own gate on 2026-08-10.

### Smaller ones, all verified

- **The stash is repository-wide.** `refs/stash` lives in the common directory, so another session
  sees and can pop yours. This is the technical reason a worktree beats a stash on a shared checkout,
  beyond convenience.
- **`git diff` omits untracked files.** The patch made to preserve this session's work carried three
  modified files and silently dropped the one new file — which was the actual deliverable. Caught by
  enumerating `git status --porcelain` rather than trusting the patch.

## What the conversation established that no file records

- **The trigger is not "uncommitted changes".** It is that a checkout has a second writer, and
  uncommitted changes are only one of its signals. A branch you did not create and commits you did
  not make are the others, and both were present here before any file was touched.
- **Long-running work needs a worktree even on a clean tree.** The hazard is the window, not the
  starting state. An SDD cycle that runs for hours will outlive the conditions it started under.
- **The half-switched path is the practical failure**, not forgetting the worktree entirely. The
  session's working directory, its scratchpad and every absolute path already in play point at the
  original checkout. Writing some files to one tree and some to the other is the easy mistake, and it
  produces no error either.
- **A cross-session message is not a handshake.** The documentation is explicit that delivery is not
  guaranteed — the receiving session's inbound controls may hold or refuse it, and a session that
  bypasses permission prompts holds every incoming message for the human. It informs; it cannot
  coordinate, and it cannot authorise. Messaging a `busy` session is safe: the receiver reads it
  between tool calls.
- **The symptom was a number nobody was watching.** The collision was invisible in `git status` and
  visible only in a file count printed by an unrelated gate. Preflight has to record branch and HEAD
  at session start, because by the time something looks wrong the work is already in the wrong place.
