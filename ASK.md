---
id: ask/index
type: index
targets: [any]
status: draft
verified: 2026-09-03
sources: ["skills/checkout-isolation/SKILL.md", "skills/context-checkpoint/SKILL.md", "skills/hypothesis-cycle/SKILL.md", "skills/project-gap-analysis/SKILL.md", "skills/guided-diagnosis/SKILL.md", "skills/source-verdict/SKILL.md", "skills/README.md", "journal/2026-08-13-skills-nobody-could-ask-for.md"]
---

# ASK.md — what you can ask for

Written for the **human**, not the executor. Every other file in this repo is written for an agent to
act on. This one answers the question an agent never asks and never surfaces: *what can I request?*

It exists because a skill's `description` is written to make a **model** select correctly, not to
tell a person what is available. Both were true of `checkout-isolation` for a full day: installed,
working, globally reachable, and unknown to the person who wrote it.

`status: draft` — every entry is verified against the `SKILL.md` it names, but nobody has used this
file yet. It promotes when a request phrased from here actually triggers the right skill.

## First, whether they are loaded at all

Five of the six reach an executor only through the `.claude/skills` symlink `./setup.sh` generates,
so they load **only in a session rooted in this repo**. `checkout-isolation` is the exception: it is
installed at user level and reaches every project.

`setup.sh` output is gitignored and never committed, so a fresh worktree does not inherit it — the
same shape as the hook hazard `checkout-isolation` documents. **Run `./setup.sh --<tool>` once per
checkout.** This worktree did not have it while this file was being written, which is how the
omission was found.

## The six

Say it however you like — selection is semantic, not literal. "work in a worktree", "put this in a
worktree" and "am I safe to write here" all reach the same skill. The wording below is the shape.

**"start in a worktree"** · **"who else is holding this checkout?"** → `checkout-isolation`
Records branch and HEAD, lists the other checkouts, and reports **which pre-commit hook actually
guards the tree you are in** — a worktree does not run its own. Runs before any write whether you
ask or not; ask explicitly when starting long work in a tree that looks clean.
*The only one of the six also installed at user level, so it reaches every project.*

**"checkpoint this before I clear the conversation"** → `context-checkpoint`
Closes the work unit so the conversation can be cleared without losing what it established, and so
the next session resumes instead of re-deriving. `draft`.

**"is that actually true? test it"** → `hypothesis-cycle`
Takes a claim from said-out-loud to a verdict `theory/` can hold: classified by logical form, given
a declared test, and stopped when it costs more than it is worth. `draft`.

**"analyse <project> and tell me what it is missing"** → `project-gap-analysis`
Seven checks against validated `theory/`. Full detail stays in a report **outside** this repo; only
a de-identified record lands in `gaps/`. Two recorded runs. `draft`.

**"here is a link — worth building on?"** → `source-verdict`
A verdict on a post, thread, paper or vendor doc by evidence rather than by author, written as the
five-section entry `research/` requires. `validated` — the only one of the six.

**"I don't know where to start"** · **"walk me through what my project is missing"** → `guided-diagnosis`
An ordered walkthrough for somebody starting cold: establishes where the executor is standing, asks
for the target once, delegates the seven checks to `project-gap-analysis`, and reports every absence
**with the `validated` artifact behind it** — an absence it cannot cite is not reported as a finding.
Says out loud, before being asked, that `blocks/` and `templates/` are empty, so what comes back is
reasoning and at most one `draft` skill. Deliberately **not** called an installer: ADR 0017 lets a
diagnosis ship before its prescription exists, on the condition that the missing half is never
implied to exist. `draft`, never run.

## What this file does not cover

The other skills reachable from this machine — `sdd-*`, `judgment-day`, `branch-pr`,
`work-unit-commits` and the rest — are installed at user level and come from elsewhere. They are
deliberately out of scope here: this file covers what **this repo** produced. Their index is
generated separately by the `skill-registry` skill, which writes a delegator-facing table of every
skill it can find.

## Keeping it honest

This is a hand-maintained list, which the repo otherwise avoids. It is allowed here because the
phrases live in no frontmatter field, so there is no generated source it can contradict — the only
way it goes wrong is a skill added without an entry.

`skills/README.md` carries that obligation, at the point where a skill is created. Adding a sixth
skill means adding its two lines here in the same commit.
