---
id: journal/2026-08-26-the-installer-already-exists-split-in-two
type: journal
targets: [any]
status: draft
verified: 2026-08-26
sources: ["MAP.md", "AGENTS.md", "ASK.md", "BACKLOG.md", "gaps/README.md", "gaps/0001-rn-expo-wallet-timeboxed.md", "gaps/0002-expensify-app.md", "gaps/0003-prowler.md", "skills/context-checkpoint/SKILL.md", "skills/project-gap-analysis/SKILL.md", "skills/checkout-isolation/SKILL.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0014-a-public-guarantee-cannot-be-opt-in.md", "https://claude.com/docs/claude-tag/users/memory"]
---

# 2026-08-26 — the installer already exists, split in two

Provenance only (ADR 0007). No ADR is proposed here yet; the question that would justify one is
named at the end.

## Where it started

A public thread described an org running issue triage, status collection, cross-tool questions and
agent-to-agent handoffs through Claude in Slack, and recommended every org roll it out. The request
that followed was not "install that". It was: **could someone who does not know where to start get
the basics of this, guided, and have it be tested rather than copied.**

Three findings, in the order they were forced.

## Finding 1 — the automation asked about does not exist here at all

Not a gap in ambition, a gap in layer. The thread's setup is a surface over accumulated context.
This repo has the context and none of the surface, and nothing here runs unattended:

| Layer | State |
|---|---|
| `.github/` | Directory does not exist. ADR 0014 decided a workflow and records why it is deferred |
| `check.sh`, `hooks/pre-commit` | `MAP.md:85` — "Both are local and must be run by hand — nothing runs them for you (ADR 0014)" |
| Per-checkout install | `setup.sh` output is gitignored, so a fresh worktree inherits no gate |

So "that level of automation" has a step zero nobody had named: something must run without being
asked. Until then every layer above it is a surface over an unenforced base.

## Finding 2 — what was asked for already has a name, and is empty on purpose

The request maps exactly onto `blocks/` and `templates/` as `MAP.md` already declares them:
minimal reusable artifacts with a contract, plus copy-ready compositions. Five README files,
zero content.

The reason is `gaps/README.md`'s demand rule: a block is built when the same demand appears in **at
least two independent gap records** — different projects, different owners, analysed separately.
And the failure it exists to stop is precisely the thing a starter kit is (`gaps/README.md:75`):

> One analysis plus enthusiasm produces a `blocks/` directory full of things that solved one
> project's problem and are described as reusable practice. That is inventing knowledge with extra
> steps.

A guided installer that hands someone ten "basic" blocks would satisfy the request as phrased and
violate the rule that makes the answer worth anything. The request is right; the obvious
implementation of it is the documented anti-pattern.

## Finding 3 — exactly one demand has earned it, and it does not resolve to a block

Checked rather than assumed. Across the three gap records, one check is `absent` in every one:

| Check | `0001` single dev, declared 48h scope | `0002` public repo, ~285k commits | `0003` public repo |
|---|---|---|---|
| 4 — Reset practice | `absent` | `absent` | `absent` |

Three projects, three owners, analysed separately, spanning a timeboxed solo build to
mature public repositories. The demand rule needs two; this has three. And
`gaps/README.md:17` already records where it landed: "One demand has reached three
occurrences and **resolved to an existing draft skill rather than to a new block**; a second
is at one." That skill is `skills/context-checkpoint`.

No other check is `absent` anywhere. So the honest inventory available to any installer
today is: **zero validated blocks, one draft skill** — and the one demand with the strongest
evidence in this repo still does not produce a block.

That last point is the one worth keeping. Three independent occurrences is the most evidence
any demand here has ever accumulated, and it resolved to promoting something that already
existed. An installer built to hand out blocks would have nothing to hand out even at
maximum evidence.

## The proposal that was wrong, and what refuted it

Proposed in conversation: promote `skills/context-checkpoint` from `draft` to `validated`, on the
grounds that it is the only demand with earned evidence.

Refuted by the skill's own stated criterion, which is not about evidence of demand but evidence of
execution (`skills/context-checkpoint/SKILL.md:23`):

> the loop has been run end-to-end **enough times to know it works.**

Its own Recorded runs table: run 1 and run 2 outcomes **never recorded**, run 3 worked. One
recorded run. The file states the consequence itself — "Promote when there are recorded end-to-end
runs, not when a better citation arrives."

The generalisable error, worth keeping because it is not obvious: **a promotion is not a task.** It
cannot be produced by a session deciding to do it, because its input accrues across sessions that
each record one honest outcome. Treating it as a work item is the same category error the file
already warns about one paragraph earlier — external agreement strengthened the rationale and did
not touch the criterion. Demand evidence and execution evidence are different axes, and satisfying
the first says nothing about the second.

## The shape that does not invent knowledge

Diagnosis before prescription. The installer does not open with an inventory; it opens with the
seven checks of `skills/project-gap-analysis` run against the asker's own project, reports what is
absent with the `theory/` file backing each check, and hands over only what has earned `validated`.

That the honest answer is currently almost empty is the feature. It grows one earned block at a
time, each with two independent records behind it.

Stated plainly, because it reframes the work: **the installer already exists, split in two.**
`skills/project-gap-analysis` is the half that diagnoses and works. `blocks/` is the half that
prescribes and is empty. What is missing is not a new artifact but the join, plus a surface a human
can talk to.

## The boundary an agent cannot cross

Everything scriptable is delegable: reading state, writing configs, `setup.sh`, hooks, a CI
workflow, `gh` for repository state, then `check.sh` to verify. OAuth is not. Installing a Slack
app, authorising connectors and changing org settings require a human in a browser holding admin
rights, and that is true of any vendor.

So the artifact is a **guided** installer: it does the scriptable work, stops at each human gate
with the exact instruction, and verifies the gate was passed before continuing. Not a lower ambition
— the same shape `skills/context-checkpoint` already documents for the clear itself, where the
agent's job ends at "safe to proceed" and the keystroke is the human's.

## One note on where the knowledge would live

The vendor documentation for channel memory says, in its own words, that long playbooks belong in a
repository the agent can read rather than in memory, because memory is a curated note whose long
entries crowd out everything else. That is this repo. Channel memory would hold a pointer to
`MAP.md` and the instruction to respect `status`, not the knowledge.

Two hazards, both this repo's own rules applied to that surface:

- Memory generated in **public** channels is shared workspace-wide. Under ADR 0009 that is an
  unguarded publication surface, and the class it would leak — a private project name written as a
  bare word — is the half `hooks/pre-commit` explicitly cannot pattern-match.
- A channel answer flattens `status`. `hypotheses/` has zero citability (ADR 0012) and `gaps/`
  records are evidence only in aggregate; neither distinction survives being read aloud in a
  channel by default.

## Session hazard, recorded because it fired

While this conversation ran, another session committed `cf42a54` to
`sdd/failure-flood-triage-planning` in the shared checkout — HEAD moved without this session moving
it, the trigger `skills/checkout-isolation` names. A worktree was taken before any write.

Its gate check printed `WRONG TREE` from inside the new worktree: commits there are scanned by the
original checkout's `hooks/pre-commit`, so the redaction gate was run by hand. Second independent
occurrence of the hazard that skill documents, and the pending per-worktree shim is still not
installed.

## Correction, recorded because it is the same failure twice

Finding 3 was first written as **two** records and two occurrences, and committed that way. It
was computed against a local `main` that was more than twenty commits behind `origin/main` and
missing `gaps/0003-prowler.md` entirely. The conclusion survived and got stronger; the count
was wrong, and nothing in the tree said so.

The same shape as the botched tests recorded in `skills/checkout-isolation` — a check that does
not state which tree it inspected cannot be told apart from one that inspected the wrong tree.
There it was a working directory. Here it was a branch twenty commits stale, in a worktree cut
from it, with every gate reporting clean. `check.sh` and the redaction gate both passed on the
stale tree, because neither is a freshness check and neither claims to be.

So the discipline extends: **when a finding counts things, state the revision it counted at.**
Verified at `origin/main` `7ba686f`.

## What would justify an ADR

Not "build an installer" — that is a deliverable, and `BACKLOG.md` requires a named unblock
condition rather than a wish. The question underneath it is the one worth deciding:

**does a diagnosis-first surface get to speak to a human before `blocks/` holds anything, or does
an installer with an empty inventory misrepresent the repo by existing?**
