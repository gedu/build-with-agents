---
id: decisions/0014-a-public-guarantee-cannot-be-opt-in
type: decision
targets: [any]
status: draft
verified: 2026-08-17
sources: ["journal/2026-08-17-three-rules-with-no-verifier.md", "AGENTS.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "theory/loops/verifier-availability.md", "skills/README.md", "gaps/0001-rn-expo-wallet-timeboxed.md", "gaps/0002-expensify-app.md"]
---

# 0014 — A guarantee a public repo depends on cannot be opt-in and local

`status: draft` — the decision is made, **half of it is implemented**, and the operator has not
ratified it. Promotion to `validated` is the operator's act, not this file's.

**Read "Implementation status" before citing this ADR.** The local layer shipped. The server-side
layer, which is the half that answers the problem stated below, has not. Until it does, the finding
in *Context* is still true of this repository: a fresh clone has no gate.

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
| A server-side job | Redaction over the tree, redaction over the pushed commit messages, structural invariants | Runs on the server. Nothing to install, nothing to opt into, no way to not have it. **Not implemented — see Implementation status** |
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

**Deferred: the server-side layer.** It was written and verified locally — three jobs, each pairing
its self-test with the check it guards, a range step handling an all-zeros or unreachable `before` by
scanning full history loudly rather than scanning nothing, and every event value passed through the
environment so none of it is parsed as shell. It is not committed.

The reason is not technical. Pushing a workflow file requires a token scope that permits writing code
GitHub itself executes on its runners, and the operator declined to widen the token for a guarantee
whose beneficiary — a second contributor — does not exist yet. That is a defensible call: this ADR's
own rule against building for imagined demand applies to the ADR.

**What that costs, stated plainly so nobody cites this ADR as if it were closed:**

- The fresh-clone guarantee **does not exist**. A collaborator who clones and does not run
  `./setup.sh --hooks` still has no gate, exactly as *Context* describes.
- Rules A, B and C now have verifiers, but every one of them is local and opt-in — the same class of
  coverage this ADR was written to end.
- The owner is covered only in a checkout where the hooks were installed **and** resolve to this tree.
  `skills/checkout-isolation` exists because that is not automatic: this ADR was written in a worktree
  whose gate reported `WRONG TREE`, and every check in it was run by hand.

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
| A fresh clone would be covered without a setup step | **Not realised.** This is what the deferred server-side layer buys: jobs needing nothing installed, running on a collaborator's push whether or not that person read `OPERATIONS.md`. Until it lands, a fresh clone has no gate |
| A second redaction gate exists, so the pattern list is now shared | `hooks/redaction-patterns.sh` is sourced by both hooks. Editing it means running both self-tests; each asserts a real finding through the list, and each asserts exit 2 when the file is missing |
| The frontmatter schema became an interface with a checker | `./check.sh` names the file and the field. `AGENTS.md`'s "schema = doc" rule now has a third artifact to keep in step: change the fields and `check.sh` changes in the same commit |
| A new skill without an `ASK.md` entry fails the build | The obligation in `skills/README.md` stops depending on somebody remembering |
| CI must never grow a check that cannot fail | Every step either produces a result or exits non-zero. `continue-on-error`, `|| true` and a silently empty scan range are forbidden here by name |
| A new-branch or force-push event scans more, never less | `github.event.before` is all zeros then, and the range is invalid. The workflow falls back to the full reachable history and logs that it did |
| The repo gained a `.github/` directory it did not have | It holds workflows. `setup.sh --copilot` also generates a gitignored file there; the two do not collide |

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
