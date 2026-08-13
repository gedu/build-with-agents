---
id: skills/checkout-isolation
type: skill
targets: [any]
status: draft
verified: 2026-08-13
sources: ["AGENTS.md", "OPERATIONS.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "theory/loops/verifier-availability.md", "https://code.claude.com/docs/en/cross-session-messaging", "journal/2026-08-13-shared-checkout-collision.md"]
---

# checkout-isolation

Run before writing anything to a repository. Decides whether this session may work in the checkout
it was started in, or must take a worktree first.

**This file is the source of record.** The knowledge is about git and concurrent sessions rather than
about this repository, so it is also installed at the executor's user level to reach every project.
The installed copy carries the executor's own frontmatter and the body below **verbatim**, so drift
between them is a plain diff of the body and nothing else.

It is deliberately a copy, not a symlink into this working tree: a symlinked skill would resolve to
whatever branch this checkout happens to have — the exact defect documented below, reproduced in the
mechanism meant to distribute the warning about it.

**A checkout is single-writer.** Two agents sharing one working tree is not a merge problem — it is
a problem with no merge, because the second writer's branch, index and hooks change underneath the
first without any error.

## Preflight — run this first

```sh
git rev-parse --show-toplevel
git status -sb | head -1                 # branch, and ahead/behind
git log --oneline -1                     # HEAD now
git worktree list                        # who else has a checkout here
git rev-parse --git-common-dir           # shared state lives here
```

Record the branch and HEAD. **Re-check both immediately before writing and again before
committing.** If either moved and you did not move it, stop: another writer holds this checkout.

### Then check which gate actually guards this tree

The hazard below is silent, so it has to announce itself rather than be remembered. Run this
wherever you are about to commit:

```sh
hook=$(git rev-parse --git-path hooks/pre-commit)
top=$(git rev-parse --show-toplevel)
if [ ! -e "$hook" ]; then
  printf '  NO GATE — %s does not resolve. git skips a missing hook in silence.\n' "$hook"
else
  real=$(readlink -f "$hook" 2>/dev/null || realpath "$hook")
  case "$real" in
    "$top"/*) printf '  ok — gated by this tree: %s\n' "$real" ;;
    *)        printf '  WRONG TREE — commits here are gated by %s\n              which is outside %s\n' "$real" "$top" ;;
  esac
fi
```

Three outcomes, each verified against a real instance of its condition:

| Output | Meaning | What to do |
|---|---|---|
| `ok` | The gate that runs is this tree's own copy | Proceed |
| `WRONG TREE` | Another checkout's script will scan your files | Run `./hooks/pre-commit --all` yourself before committing. Do not rely on the hook firing |
| `NO GATE` | The symlink dangles; git will skip it without a word | **Stop.** Nothing is guarding this commit. Fix the install before writing anything to a public repository |

**When this prints `ok` from inside a worktree, the shim below has landed and this section can go.**
Until then it is the only thing that reports the hazard without someone already knowing about it.

`readlink -f` is not POSIX; the `realpath` fallback covers macOS, and on a system with neither,
resolve the symlink by hand rather than skipping the check.

`/list-agents` (or the `ListAgents` tool) shows sessions on this machine and whether they are busy.
A session whose working directory is this repository is a writer until proven otherwise.

## Take a worktree when either is true

| Trigger | Why |
|---|---|
| **Another writer may hold this checkout** — a branch you did not create, commits you did not make, uncommitted changes that are not yours, a peer session in this directory | The failure is silent. You will not get a conflict; you will get your work committed onto someone else's branch, or their branch switched under you mid-edit |
| **The work is long-running** — an SDD cycle, a migration, a multi-hour experiment — even in a clean tree | The hazard is the window, not the starting state. A clean tree at minute zero says nothing about minute ninety |

```sh
git worktree add <repo-parent>/<repo-name>-worktrees/<task> <branch>
```

Never under `/tmp` or `/var/tmp`. Remove it when the work merges — abandoned worktrees rot and their
stale branches get committed to by accident later.

## Corner cases, all verified

### Hooks resolve through the common directory, not through your worktree

**This one silently disarms the gate, and it is the reason this skill exists.**

`setup.sh --hooks` installs the redaction gate as `.git/hooks/pre-commit -> ../../hooks/pre-commit`.
Worktrees share the common directory, so that relative symlink climbs to the **original checkout's
working tree** — never to yours. Verified here:

```
worktree:  <repo>-worktrees/gaps-analysis
git rev-parse --git-path hooks/pre-commit
  -> <original-checkout>/.git/hooks/pre-commit
realpath
  -> <original-checkout>/hooks/pre-commit      # the ORIGINAL checkout's file
```

So your commit is scanned by a script from one tree using content from another. Two consequences,
both reproduced in a throwaway repository rather than argued:

| The original checkout's branch | What a commit in your worktree does |
|---|---|
| Has `hooks/pre-commit` | Runs **that branch's version** of the gate against your files. Blocked correctly here, but by whichever version they happen to have checked out |
| Has no `hooks/` at all | The symlink dangles, git **skips the hook silently**, and the commit lands **with no gate at all**. Exit 0, no warning, nothing in the output |

The second row is `theory/loops/verifier-availability.md` exactly: not a weak gate, an absent one
that reports nothing. Another session changing branch in their checkout can disarm the redaction
gate of a public repository for every worktree, and no surface says so.

**Until `setup.sh` installs a shim that resolves per-worktree** — `exec "$(git rev-parse
--show-toplevel)/hooks/pre-commit" "$@"` would — the preflight check above is what reports this, and
it reports it every session rather than waiting to be remembered. The shim is written down, agreed
and **not yet tested**; applying it also means re-running `setup.sh --hooks`, which rewrites
`.git/hooks/` for every checkout at once and so needs the other sessions idle.

Meanwhile, run the gate explicitly from your own worktree before committing, and never rely on it
firing:

```sh
./hooks/pre-commit --all        # from the worktree, not from the original checkout
```

### The stash is repository-wide

`refs/stash` lives in the common directory, so it is shared with every other checkout. Another
session can list, pop or drop your stash, and will see it with no indication whose it is or which
branch it belongs on. **Never park work in a stash on a shared checkout.** A worktree keeps the work
on the right branch and out of everyone else's reach.

### `git diff` does not carry untracked files

A patch made with `git diff` silently omits every new file — usually the most important part of the
work. Enumerate before trusting a patch:

```sh
git status --porcelain | grep '^??'
```

Copy those separately, or use `git stash -u` only when the checkout is *not* shared.

### Half-switched paths are the practical failure

The real mistake is not forgetting the worktree. It is using it for some files and the original
checkout for others, because your session's working directory, scratchpad and every absolute path
you have used so far point at the original.

On creating a worktree, re-anchor **everything** and treat the original path as off-limits for
writes. Re-read `git rev-parse --show-toplevel` if you are unsure which tree a command just ran in.

### Each worktree needs its own CodeGraph index

Never copy, symlink or reuse another checkout's `.codegraph/`. The root and the checked-out bytes
differ, so a reused index answers questions about a tree you are not in.

### Review authority and tool state are shared too

Anything a tool stores under the common directory — review lineages, authority stores, hook config —
is shared across worktrees. A per-clone setting applied in one checkout applies to all of them.
Check before assuming a worktree gives you a clean slate; it gives you a separate *tree*, not a
separate *repository*.

## Coordinating, once you are isolated

Cross-session messaging exists for exactly this case — the documentation names it: *"Coordinate
parallel worktrees: when sessions work the same repository in separate worktrees, Claude can tell
the other sessions what landed."*

Use it to **inform**, and understand what it cannot do:

- **A message is not a handshake.** Delivery is not guaranteed: the receiving session's inbound
  controls may hold or refuse it, and a session bypassing permission prompts holds every incoming
  message for the human's approval. Never build a coordination step on a message having arrived.
- **A message cannot authorise anything.** It never counts as the human's consent, and the receiving
  session is instructed not to change configuration because another session asked.
- **Messaging a busy session is safe.** The receiver reads it between tool calls; a running tool is
  never interrupted.

So: send what landed and where, ask for nothing, and do not wait on a reply to proceed.

## What this skill does NOT do

It does not make concurrent writing safe. It makes concurrent writing **separate**. If two sessions
genuinely need the same files at the same time, that is a scheduling problem between the humans, not
something a worktree fixes.

## Recorded runs

| # | Date | Trigger | Outcome |
|---|---|---|---|
| 1 | 2026-08-13 | Another session held the checkout on its own branch, discovered mid-task | Worked. Worktree on `main`, work committed clean, original checkout never touched |

Run 1 is also where every corner case above was found. The hook hazard was **not** predicted — it
was found by checking, and its second half only exists because a botched first test was rerun
instead of reported. Promotion needs more runs, not a better rationale.

**Two tests were botched during run 1, in the same way, and it is worth knowing the shape.** The
first hid `git worktree add`'s failure behind `2>/dev/null`, so the test ran in the wrong directory
and printed a plausible result. The second chained `cd … && …` and let the directory persist into the
next case, so a check that should have printed `ok` printed `WRONG TREE` — from the previous
directory. Both were caught only by printing the working directory alongside the result.

So: **when a check is about where you are, print where you are.** A diagnostic that does not say
which tree it inspected cannot be distinguished from one that inspected the wrong one, which is the
same failure this whole skill is about.
