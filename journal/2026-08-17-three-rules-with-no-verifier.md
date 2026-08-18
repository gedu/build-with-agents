---
id: journal/2026-08-17-three-rules-with-no-verifier
type: journal
targets: [any]
status: draft
verified: 2026-08-17
sources: ["AGENTS.md", "OPERATIONS.md", "hooks/pre-commit", "skills/README.md", "ASK.md", "setup.sh", "theory/loops/verifier-availability.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "gaps/0001-rn-expo-wallet-timeboxed.md", "gaps/0002-expensify-app.md"]
---

# 2026-08-17 — three rules with no verifier, and gates nobody has to install

Provenance for `decisions/0014-a-public-guarantee-cannot-be-opt-in.md`. Not authority (ADR 0007).

## The test that was applied

`theory/loops/verifier-availability.md` states it: **the practical test is not to read the rule but
to ask which layer implements it.** Applied to this repo's own rules, one at a time. The result was
worse than a missing check, because the answer for a fresh clone is the same for every rule the repo
does enforce.

## Finding 1 — every gate here is opt-in, and nothing says so

| Fact | Consequence |
|---|---|
| Git hooks live in `.git/`, which is never cloned | A clone arrives with no gate |
| Git deliberately runs nothing on clone | Nothing installs one either |
| `./setup.sh --hooks` is the installer, and it is a manual step | Somebody must know to run it |
| `setup.sh` output is gitignored and never committed | A worktree does not inherit it either — already recorded on 2026-08-13 |

So a collaborator who does not run `./setup.sh --hooks` has **no redaction gate**, and the repo emits
no signal at all about that. This is the `never was a gate` row of `verifier-availability.md` reached
from a new direction: the gate is real, it is tested, and it is absent from the machine that matters.

The rule it fails to enforce is the one with the highest cost. This repo is public, and ADR 0009
opens by saying pushing is not reversible in any way that matters.

## Finding 2 — three rules with no implementing layer

| # | Rule | Stated in | Layer that implemented it |
|---|---|---|---|
| A | Redaction covers commit **messages** | `AGENTS.md` — "in prose, in frontmatter, or in a commit message" | None. `hooks/pre-commit` scans staged **files** |
| B | The frontmatter schema is a machine query interface | `AGENTS.md` frontmatter contract, ADR 0004 | None. `status: valdiated` or an invented `type:` is accepted in silence |
| C | A new skill needs an entry in `ASK.md` in the same commit | `skills/README.md`, restated in `ASK.md` | None. `ASK.md` calls this its only failure mode |

B is the sharpest of the three, because the schema's stated purpose is to be **queried**. A typo does
not degrade a query, it removes the file from the result set while the file still reads correctly to a
human. And ADR 0004's own query tooling was never built, so nothing else was ever going to notice.

C is documented as hand-maintained on the narrow ground that no generated source can contradict it.
That argument is about *drift*, and it is sound. It says nothing about *omission*, which is the
failure both files name.

## Finding 3 — CI was never rejected. It was never considered

Checked before writing anything, because "rejected once" and "never raised" call for different
documents:

| Where a rejection would be | What is there |
|---|---|
| `decisions/` | No ADR mentions CI, GitHub Actions, or a server-side check |
| `OPERATIONS.md` decision table | No row. Every entry is a command the operator runs locally |
| `.github/` | Does not exist. `setup.sh --copilot` would generate one file into it, gitignored |
| Anywhere in tracked content | The only mentions of CI are observations about **other** projects, in `gaps/` |

There is therefore no decision to supersede, and ADR 0014 is a first decision rather than a reversal.

The `gaps/` mentions are worth keeping, because the instrument was pointed outward and never inward:

- `gaps/0001` scores check 6 **`absent`** — four declared checks, no CI configuration and no
  installed git hook, nothing invoking any of them at an obligatory point. Its own words: *"a loop
  with no check step"*.
- `gaps/0002` scores check 6 **`partial`** — enforcement lives in CI, and one workflow gathers its
  file list with `|| true`, so the check passes having examined nothing.

Applied to this repository on a fresh clone, check 6 reads `absent`, and it is the same shape
`gaps/0001` was marked down for. `gaps/0002`'s defect is the one the new workflow is written against:
every job must distinguish *could not run* from *passed*.

## What was verified while building, with the output that proves it

Everything below ran in this worktree. `./setup.sh --hooks` was deliberately **not** run here: in a
worktree that path writes into the shared common directory, which another session depends on.

| Check | Output |
|---|---|
| `./hooks/pre-commit --self-test` | 4 cases ok, `self-test: all cases passed`, exit 0 |
| `./hooks/pre-commit --all` | `clean across 121 tracked files`, exit 0. Repeated in a scratch copy with this change's own six new files staged: `clean across 126 tracked files` |
| `./hooks/commit-msg --self-test` | 8 cases ok, `self-test: all cases passed`, exit 0 |
| `./hooks/commit-msg --range - HEAD` | `clean across 79 commit message(s)`, exit 0 — the whole existing history, so CI does not open red |
| `./check.sh` | `clean across 91 content files and 5 skill(s)`, exit 0 |
| `./check.sh --self-test` | 14 cases ok, `self-test: all cases passed`, exit 0 |
| `bash -n` / `sh -n` on all five shell files | silent, exit 0 |
| `setup.sh --hooks`, twice, in a scratch clone | `link` then `ok` for both hooks, exit 0 both runs |
| A real `git commit` with a home-path shape in the **message** | aborted, exit 1, and the commit is absent from `git log` |
| A real `git commit` with a clean message | landed |
| Twelve simulated CI events against the workflow's range step | 0 / 1 / 2 as specified, including all-zeros `before` |

Four things that only showed up by running it:

- **The pattern list duplicated itself the moment a second gate existed.** Extracting
  `hooks/redaction-patterns.sh` was not tidiness — two copies of a security gate's patterns drift, and
  the weaker copy is the one that fires. Both hooks now fail with exit 2 if that file is missing,
  because an empty pattern list scans every line against nothing and reports clean.
- **`--all` and `check.sh` count different populations on purpose**: 121 tracked files against 89
  content `.md`. `rig/fixtures/` is excluded from the second — those files imitate a foreign project
  and two of them legitimately have no frontmatter.
- **A self-test can pass for the wrong reason.** So `check.sh` was also run against a scratch copy of
  the tree, outside the repo, with six invariants broken by hand: a `status` typo, an invented `type`,
  an emptied `sources` on a `validated` file, a non-ISO `verified`, an unbracketed `targets`, and a
  sixth skill with no `ASK.md` entry. It named all six, each with the file and the field.
- **`git commit -v` puts the staged diff inside the commit message file.** Scanning it would report
  pre-existing context lines as commit-message findings on every verbose commit. The gate cuts off at
  the scissors line, and the self-test asserts it.

## How it ended, the next day

The workflow was **not committed.** Pushing it failed on a token scope: GitHub refuses to let an
OAuth app create or update anything under `.github/workflows/` without `workflow`, because a workflow
file is code GitHub executes on its own runners with access to the repository's secrets. `repo` grants
writing code; `workflow` grants writing code that runs. Different blast radius, separate scope, and
the block is the feature.

The operator asked the question worth recording: **why add this now.** The honest answer is that the
beneficiary does not exist — there is no second contributor — and this repo's own rule against
building for imagined demand applies to its own infrastructure as much as to `blocks/`. The scope
stayed as it was, the local half shipped, and the server-side half is deferred with its reasoning
intact in ADR 0014, which now carries an *Implementation status* section saying plainly that the
fresh-clone guarantee does not exist.

Two things this cost, both recorded rather than smoothed over:

- Every document that had been written to describe a working CI had to be corrected in the same
  breath — `AGENTS.md`, `MAP.md`, `OPERATIONS.md` and the ADR itself. A repo that documents a
  guarantee it does not have is worse than one that documents none, and the window where that was
  true lasted one commit.
- `OPERATIONS.md` gained a section titled *There is no CI* rather than losing the CI section quietly.
  The absence is now the documented operating reality, which is the only form in which a reader
  learns it.

Also learned, and general: **`main` was protected before the thing that would enforce it existed.** A
ruleset now requires a pull request and blocks force-push and deletion, with no required status check,
because a required check that never reports leaves every pull request waiting forever. Protection and
the check it should require have an order, and it is not the intuitive one.

## What is not settled

| Open | Why it is open |
|---|---|
| The workflow was never committed and has never executed | Deferred on the scope question above. Its YAML parses and its range logic was exercised across twelve simulated events; neither is a green run, and it is not in the repository |
| `on: push` detects, it does not prevent | The content is already published when the job starts. Prevention needs a required status check on a protected branch, which is repository configuration and not a committed file. Nobody has enabled it |
| ADR 0014 is unratified | Written as `status: draft`. The operator ratifies |
| `targets` membership is unchecked | `AGENTS.md` documents three values, `MAP.md` lists five more as planned. A closed enum would reject the first Node block on the day it is written |
| Whether an `ASK.md` entry is any good | `check.sh` verifies the skill name is present. That a phrase reaches the right skill is exactly the claim keeping `ASK.md` at `draft`, and no checker settles it |
