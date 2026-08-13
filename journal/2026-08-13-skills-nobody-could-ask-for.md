---
id: journal/2026-08-13-skills-nobody-could-ask-for
type: journal
targets: [any]
status: draft
verified: 2026-08-13
sources: ["ASK.md", "skills/README.md", "skills/project-gap-analysis/SKILL.md", "skills/checkout-isolation/SKILL.md", "AGENTS.md", "MAP.md"]
---

# 2026-08-13 — five skills, and no way for their owner to ask for one

Provenance for `ASK.md`. Not authority (ADR 0007).

## How it was found

The question was whether `skills/checkout-isolation` could be carried into other projects. It already
could — it has been installed at user level since this morning and reaches every project on the
machine. The person who wrote it did not know that.

That is the finding. The mechanism worked; the human could not see it.

A skill's `description` is written so a **model** selects correctly. Nothing reads it to a person, and
nothing in this repo answered *what can I ask for*. Every file here is addressed to an executor.

## The proposal that was rejected, and why

The first answer offered was an eighth check in `skills/project-gap-analysis` ("does this project
have our skills?") plus a new `skill-transfer` skill to adapt and install them. Three reasons it was
wrong, in order of severity:

1. **It breaks the target skill's own invariant.** `project-gap-analysis` states that every check
   cites a `theory/` source and that a check without one is "an opinion with a checkbox". There is no
   validated doc behind *do you have our skills*, because it is a recommendation rather than a
   projected claim. The check would have been the first invented one.
2. **The demand rule had not fired.** One occurrence. The skill's own rule is two independent gap
   records before anything gets built.
3. **The answer partly existed.** The `skill-registry` skill already scans every skill directory on
   the machine and generates an index. Building a second mechanism is the "two half-finished answers
   to the same question" that `project-gap-analysis` warns about — found only by looking, which is
   the step the skill asks for and the one enthusiasm skips.

What survived was the complaint, not the design. `skill-registry`'s output is labelled **delegator
use only**: a table of trigger prose and absolute paths, written for an agent selecting a skill. It
cannot answer a human's question because it was never addressing one.

## What the repo's own rules decided

The shape of `ASK.md` was not chosen. Four rules already in the repo settled it:

| Constraint | Source | Consequence |
|---|---|---|
| No loose `.md` under `skills/` except its README | `skills/README.md` | The file goes at the root |
| Every table is generated or does not exist; `MAP.md` is the one hand-maintained index and holds pointers, never data | `MAP.md` | Not a table, and not a section of `MAP.md` — request phrases are data |
| All artifacts in English | `AGENTS.md` | English, though its only reader speaks Spanish |
| Do not add fields tooling does not read | `AGENTS.md` | No `ask:` frontmatter field, because no tooling reads frontmatter today |

The last one killed the tidier design. Putting the phrase in frontmatter and generating the list is
the version that cannot go stale, but it requires a generator, and this repo has **no
frontmatter-reading tooling at all** — verified, zero hits. A generator for five rows is the same
overbuild the proposal above was rejected for.

So the list is hand-maintained, which the repo otherwise refuses. It is admissible on a narrow
ground: the phrases exist in no frontmatter field, so there is no generated source for them to
contradict. The only failure is a skill added without an entry, and that obligation now sits in
`skills/README.md`, where a skill is created — not in `ASK.md`, which the person adding a skill has
no reason to open.

## Two things verified while writing it

- **`./hooks/pre-commit --all` scans tracked files only.** `ASK.md` was invisible to the gate until
  it was staged: 119 files, then 120. Writing a file and running the gate proves nothing about that
  file. Same family as the `git diff` omission recorded on 2026-08-13, but in the gate itself, and
  it means *audit the tree* and *audit what I just wrote* are different operations.
- **A worktree does not inherit `setup.sh` output.** This worktree had no `.claude/`, so four of the
  five skills could not load in it at all. The output is gitignored and never committed, so it is
  per-checkout by design. `ASK.md` promised "say this, get that" without that precondition until the
  omission was caught — by the owner asking whether the wordings had to be exact.

`--hooks` was deliberately not run here. In a worktree that path resolves into the **shared** common
directory, so it writes state another session depends on, and it would not fix the `WRONG TREE`
result anyway: the relative symlink always climbs to the original checkout's working tree. The gate
was run by hand instead, which is what `checkout-isolation` prescribes for that outcome.

## What is not settled

`ASK.md` is `draft`. Its claim is not that the five skills exist — that is checkable — but that a
request phrased from it reaches the right skill. Nobody has tried yet. The other ~22 user-level
skills on this machine are deliberately out of scope; scope was set to what this repo produced.
