---
id: decisions/0014-a-public-guarantee-cannot-be-opt-in
type: decision
targets: [any]
status: draft
verified: 2026-08-17
sources: ["journal/2026-08-17-three-rules-with-no-verifier.md", "AGENTS.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "theory/loops/verifier-availability.md", "skills/README.md", "gaps/0001-rn-expo-wallet-timeboxed.md", "gaps/0002-expensify-app.md"]
---

# 0014 — A guarantee a public repo depends on cannot be opt-in and local

`status: draft` — the decision is made, **both layers are now implemented**, and the operator has not
ratified it. Promotion to `validated` is the operator's act, not this file's, and this amendment does
not attempt it: what changed on 2026-10-14 is *Implementation status*, not the status field.

**Read "Implementation status" before citing this ADR.** Both layers now exist in the tree. What still
does not exist is the part no committed file can ship: a **required** status check. So the finding in
*Context* is narrowed, not closed — a fresh clone gets scanned whether or not anybody installed
anything, and a pull request still merges with the scan red. "No gate" became "a gate that reports and
does not block"; read the three limits under *The limit* before treating either phrase as the other.

## Context

Every guarantee this repository has is local and opt-in.

Git hooks live in `.git/`, which is never cloned, and git deliberately runs nothing on clone. The
installer is `./setup.sh --hooks`, a manual step somebody has to know about, and its output is
gitignored so a worktree does not inherit it either. A collaborator who clones this repo and commits
has **no redaction gate**, and no surface here says so. ADR 0009 gated the class that caused a real
leak; it gated it on exactly one machine.

Three rules had no implementing layer at all — the test `theory/loops/verifier-availability.md`
prescribes is to ask which layer implements a rule, not to read the rule:

| # | Rule | Stated in | Implemented by |
|---|---|---|---|
| A | Redaction covers commit **messages** | `AGENTS.md` — "in prose, in frontmatter, or in a commit message" | Nothing. `hooks/pre-commit` scans staged files |
| B | The frontmatter schema is a machine query interface | `AGENTS.md`, ADR 0004 | Nothing. `status: valdiated` was accepted in silence |
| C | A new skill needs an entry in `ASK.md` in the same commit | `skills/README.md`, `ASK.md` | Nothing. Both files name this as the failure mode |

CI was **never rejected here — it was never raised.** No ADR mentions it, `OPERATIONS.md` has no row
for it, and `.github/` does not exist. The only mentions of CI in tracked content are observations
about other people's projects in `gaps/`, which makes the omission pointed: `gaps/0001` marks a
project down to `absent` for having declared checks that nothing invokes at an obligatory point, and
on a fresh clone this repository scores the same way. The instrument was never turned on its owner.
Provenance in `journal/2026-08-17-three-rules-with-no-verifier.md`.

## Decision

**Every rule this public repository depends on gets a verifier, and at least one copy of that
verifier runs where a collaborator cannot skip it.** Local hooks stay and keep their job of catching
a problem before it exists; they stop being the only layer.

| Layer | Covers | Force |
|---|---|---|
| A server-side job | Redaction over the tree, redaction over the pushed commit messages, structural invariants, and the self-tests of every committed executable | Runs on the server. Nothing to install, nothing to opt into, no way to not have it. **Implemented** as `.github/workflows/verify.yml`, and **running** since 2026-10-14 — see its two remaining limits: it detects after publication, and no check is required |
| `hooks/pre-commit` | Redaction over staged files | Prevents. Requires `./setup.sh --hooks` |
| `hooks/commit-msg` | Redaction over the proposed commit message | Prevents. Requires `./setup.sh --hooks` |
| `./check.sh` | Frontmatter schema, and rule C | Reports. Run by hand or by CI |
| `AGENTS.md` | A private name written as a bare word | Prompt policy. Guides, enforces nothing. Unchanged by this ADR |

Three properties are not negotiable in any of them:

- **Every check distinguishes "could not run" from "passed"**, and exits 2 for the first. A job that
  cannot run its check fails. `gaps/0002` records the counterexample this is written against: a CI
  step gathering its file list with `|| true`, passing having examined nothing.
- **Every committed executable carries its own test** (ADR 0013), and CI runs that test *in the same
  job, before* the check it guards. Split across two jobs, a check could report clean in a green job
  while its own self-test failed in a red one.
- **One rule, one implementation.** `hooks/pre-commit` and `hooks/commit-msg` enforce the same
  redaction rule and therefore source one pattern list, `hooks/redaction-patterns.sh`. Both exit 2 if
  it is missing rather than scanning every line against an empty list.

## Implementation status

Shipped in the same commit as this ADR:

| Layer | State |
|---|---|
| `hooks/commit-msg` | Implemented, self-tested, installed by `./setup.sh --hooks` |
| `hooks/redaction-patterns.sh` | Implemented. Both gates source it; both exit 2 when it is missing |
| `./check.sh` | Implemented, self-tested. Rules B and C now have a verifier |

**The server-side layer: deferred 2026-08-17, committed 2026-10-14.**

What the deferral recorded was accurate and worth re-reading, because the artifact it described turned
out to exist. The file was not lost and not rewritten: it was recovered **byte-identical** (blob
`2fc49e65…` on both sides) from a dangling commit of 2026-08-17 that had never reached a branch and was
still in the object database. The description below matched the object exactly — three jobs, each
pairing its self-test with the check it guards, a range step handling an all-zeros or unreachable
`before` by scanning full history loudly rather than scanning nothing, every event value passed through
the environment so none of it is parsed as shell.

That is a fact about git worth keeping: `git commit` on a branch that is then abandoned leaves the
object reachable only by `git fsck --lost-found`, and "we decided this and never built it" can be
wrong in the direction of *already built*. Before rewriting something a decision file says was written
and verified, search the object database. The search that found it took one command:

```sh
git fsck --lost-found --no-reflogs | awk '/dangling commit/ {print $3}' | \
  while read -r c; do git show --stat --format='%h %ad %s' "$c"; done
```

One job was added on the way in, and it is this ADR's own rule applied rather than a new idea: its
non-negotiable list says every committed executable carries its own test and CI runs it, and **two
executables** post-date the draft — `./setup.sh --self-test` and `./open-work.sh`, which did not exist on
2026-08-17. `./open-work.sh` is *run*, not only self-tested, and accepted only on exit 0: its exit 2
means "could not run", which this ADR forbids reporting as a pass, while its exit 0 proves nothing
about content — open work is not a violation, so the step must never be able to fail a push for
holding any.

*Correction, 2026-10-14.* This paragraph opened "Two jobs were added", which was wrong the day T3 wrote
it: the recovered draft holds three jobs and T3 holds four, so T3 added one job covering two
executables. Measured with `git show <rev>:.github/workflows/verify.yml` over `fcaae282` (3) and
`a5f81c4` (4), counting the job keys under `jobs:`. Two executables, one job — the sentence counted the
executables and named them jobs. Same class as `MAP.md`'s stale task count, one file over: a derived
figure asserted instead of computed.

**The rig's own tests: covered 2026-10-14, by a rule rather than a list.** Two more committed
executables post-date the draft the same way `setup.sh` and `open-work.sh` did — `rig/check.sh` and
`rig/run-pipeline.sh` — and no `rig/*` path appeared in the workflow at all. A fourth job now runs them,
plus the three `rig/*.py` modules' own `--self-test` (mode `100644`, so outside this ADR's word
"executable"; they are covered because ADR 0013 is their warrant and CI ran them nowhere, the only thing
that composes them being inside `rig/check.sh`'s real gate). Two properties of that job are load-bearing
beyond this ADR:

| Property | Why it is stated here |
|---|---|
| Its targets are **discovered from the index**, not listed in the file: committed executables by mode `100755` under `rig/`, plus the tracked `rig/*.py` modules, both excluding `rig/fixtures/` | This ADR's rule rotted once by the repo growing around a hardcoded list. A new rig executable is covered the day it is committed; a commit that discovers zero targets exits 2 rather than passing |
| It runs **`--self-test` dispatches only**, never `rig/check.sh`'s real gate | CI checks out a tree with no gitignored `rig/runs/`. There the real gate fails 5/18 **and truncates both committed `rig/results/*/runs.jsonl` to zero bytes**, then reports green against the wipe. The five self-tests are hermetic by measurement: 1.74 s total, goldens stay at 3 and 42 lines, `git status` empty |

The token-scope objection that deferred it is now moot in one direction and standing in the other. Moot:
the operator selected this work knowing what it was, and the file is committed under ordinary repository
policy. **Amended 2026-10-14, same day, by the push that closed it.** Two sentences below were written
while the workflow had never run; it has run now, on both a `push` and a `pull_request` event, five jobs
green, and a planted frontmatter violation turned exactly one of them red on the server naming the file and
the field while the other four stayed green. So *"committing is not running"* stopped being the live
question — but it was the correct sentence when written, and *"running is not blocking"* replaced it as
the one that costs anything.

Standing, in the narrower form: **running is not blocking.** Verify the state rather than reasoning from
either phrase, and name which number answers which question — three endpoints here return a confident
integer for three different facts:

| Question | Command | This repo, 2026-10-14 |
|---|---|---|
| Has GitHub ever **seen** the file? | `gh api …/actions/workflows \| .total_count` | **1** workflow definition. Was `0` until 2026-10-14 |
| Has it ever **executed**? | `gh api …/actions/runs \| .total_count`, or `gh run list` | **7** runs |
| Is any check **required**? | `gh api …/rulesets` **then** `gh api …/rulesets/<id>`; read `rules` off the **detail** call | no `status_check` rule (detail: `deletion`, `non_fast_forward`, `pull_request`) |

The two ruleset calls are not interchangeable, and the cheap one is a trap of this ADR's own making: the
**list** endpoint returns no `rules` key at all (measured 2026-10-15: its keys are `id`, `name`, `target`,
`enforcement`, `source`, `source_type`, `created_at`, `updated_at`, `_links`, `node_id`). A filter written
over the list therefore iterates over nothing and still answers "no `status_check`" — the same shape as a
commit-range gate reporting clean across 0 messages. An empty `rules` array is *could not run*, never
satisfied. `OPERATIONS.md` carries the corrected two-call recipe.

`.total_count` from the *workflows* endpoint is the count of **definitions**, not of executions. An earlier
draft of this amendment called it "runs this repo has ever had", which would tell a reader checking
"did this ever run" that it ran once when it had run seven times. Same trap as the 404 two paragraphs
below: the API answers, and the answer is about something else. Read *The limit* before treating "a gate" as one word: this layer reports, the local hooks
prevent, and **`gh api …/branches/main/protection` answers 404 for a ruleset**, which is how this ADR's own
shipping PR came to publish "main is not protected" about a ruleset that had been live 58 days.

**What still costs, restated so nobody cites this ADR as if it were closed:**

- The fresh-clone guarantee **exists in the tree and now runs on the server** (amended 2026-10-14). It was
  never about whether a clone installs anything — it was about whether GitHub ever saw the file. That half
  closed; the blocking half below did not.
- Rules A, B and C have verifiers at two layers. Coverage stops being "local and opt-in", which is what
  this ADR was written to end; it does not become *blocking*.
- No status check is required, so a pull request merges with the scan red or never-run. That is
  repository configuration in a web UI and it stays undone; *The limit* below says why this file cannot
  ship it.
- The owner is covered by a checkout's own hooks **only** where they are installed and resolve to that
  tree. `skills/checkout-isolation` exists because that is not automatic — and it is still true today:
  the commit that landed this layer was made in a worktree whose gate reported `WRONG TREE`, and every
  check in it was run by hand. The workflow does not change that, because it runs after the push.

Revisit when a second contributor arrives, or when running the gates by hand stops being reliable.
The decision above does not need remaking; only the scope question does.

## The limit, stated rather than sold

**A push-triggered job detects; it does not prevent.** By the time it runs, the content is on GitHub
and ADR 0009's opening sentence applies: pushing is not reversible in any way that matters. For a
secret, detection after publication means *rotate it*, not *remove it*.

Prevention on a shared branch needs a **required status check on a protected branch**, so that a pull
request cannot merge until these jobs pass. That is repository configuration in a web UI, not a
committed file, so this ADR cannot ship it and does not claim it. Nobody has enabled it.

What the workflow does buy, honestly stated:

| It does | It does not |
|---|---|
| Make a violation visible to everyone, immediately, without anyone installing anything | Stop the push that published it |
| Catch what a collaborator with no hooks committed | Replace the local hooks, which are the preventive layer |
| Prove the gates still work, on every push, on a machine nobody configured | Cover the class no pattern can catch — a private name as a bare word |

The local hooks are therefore not redundant. They are the only layer that prevents, and CI is the
only layer that always runs. Neither substitutes for the other.

## Consequences

| Consequence | Detail |
|---|---|
| A fresh clone would be covered without a setup step | **Realised in the tree, and running on the server since 2026-10-14** (amended the same day it was written). The jobs need nothing installed and run on a collaborator's push whether or not that person read `OPERATIONS.md`. The part a committed file cannot buy is now one third, not two: GitHub has seen the workflow and executes it, and what remains undone is that **no status check is required**, so coverage is a report, not a block |
| A second redaction gate exists, so the pattern list is now shared | `hooks/redaction-patterns.sh` is sourced by both hooks. Editing it means running both self-tests; each asserts a real finding through the list, and each asserts exit 2 when the file is missing |
| The frontmatter schema became an interface with a checker | `./check.sh` names the file and the field. `AGENTS.md`'s "schema = doc" rule now has a third artifact to keep in step: change the fields and `check.sh` changes in the same commit |
| A new skill without an `ASK.md` entry fails the build | The obligation in `skills/README.md` stops depending on somebody remembering — **once the workflow runs**, which is the same condition as above. `./check.sh` reports it locally either way |
| CI must never grow a check that cannot fail | Every step either produces a result or exits non-zero. `continue-on-error`, `|| true` and a silently empty scan range are forbidden here by name |
| A new-branch or force-push event scans more, never less | `github.event.before` is all zeros then, and the range is invalid. The workflow falls back to the full reachable history and logs that it did |
| The repo gained a `.github/` directory it did not have | It holds workflows. `setup.sh --copilot` also generates a gitignored file there; the two do not collide, because `setup.sh` ignores the **narrow path** `/.github/copilot-instructions.md`, not the directory — verified before committing a file that had to stay visible, since a wholesale `/.github/` ignore would have hidden this workflow in silence and reported nothing |

## Alternatives

| Rejected | Reason |
|---|---|
| Document harder — tell collaborators to run `./setup.sh --hooks` | This is prompt policy for humans, and `verifier-availability.md` measures what it is worth: an instruction has a non-zero failure rate and its failure is silent. The repo already documented all three rules, which is how they got three verifiers between them: none |
| Ship the hooks via `core.hooksPath` in a committed config | `core.hooksPath` is set by a command, not by a committed file, so it needs the same manual step it was meant to remove. Still local, still opt-in, still absent from the machine of the person who did not read this |
| Put the checks only in CI and drop the local hooks | Deletes the layer that prevents. A commit message caught locally is rewritten before it exists; caught in CI it is already published |
| One CI job running all four checks in sequence | A failing early step would skip the rest, and the log would report less than it checked. Three jobs give three independent results, and each pairs its self-test with the check it guards |
| Pin `actions/checkout` to `@v4` or `@v7` | A tag is mutable, and this is the step that fetches the code every other step trusts. Pinned to a commit with the version in a comment |
| Extend `hooks/pre-commit` to also scan the commit message | Wrong hook. `pre-commit` runs before the message exists; git provides `commit-msg` for exactly this, and one file per concern is the repo's own rule |
| A `tests/` directory and a runner for the new executables | Refused by ADR 0013 for the same reasons, which have not changed. Each new executable carries a `--self-test` flag |
| Validate frontmatter with a YAML parser | Adds a dependency the hooks' portability rule forbids and CI would then have to install. The six fields are one line each, and `awk` reads them |
