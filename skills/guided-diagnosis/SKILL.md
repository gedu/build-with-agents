---
id: skills/guided-diagnosis
type: skill
targets: [any]
status: draft
verified: 2026-09-03
sources: ["decisions/0017-a-diagnosis-ships-before-its-prescription.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "skills/project-gap-analysis/SKILL.md", "skills/checkout-isolation/SKILL.md", "skills/context-checkpoint/SKILL.md", "gaps/README.md", "ASK.md", "OPERATIONS.md", "MAP.md", "theory/agents/capability-load-cost.md", "theory/agents/instruction-provenance.md", "theory/agents/tool-surface-design.md", "theory/llm/context-degradation-at-length.md", "theory/loops/reading-and-running-find-different-defects.md", "theory/loops/verifier-availability.md", "theory/orchestration/delegation-and-context-boundaries.md"]
---

# guided-diagnosis

Walk somebody who does not know where to start through what their project is missing, in order, and
hand back only what this repo has earned the right to give.

`status: draft` — **never run.** Its promotion criterion is in **Recorded runs** below, and it is
recorded runs, not a better rationale.

## Why this is not called an installer

That was the request, and the name is refused on purpose. ADR 0017 permits delivering a diagnosis
while `blocks/` and `templates/` are empty, on one condition: **a missing prescription is never
presented as though one existed.** A skill called `installer` makes exactly that promise in the one
place a reader cannot avoid reading it.

What it does install is real but small: the entrypoints and gates in `OPERATIONS.md`, which exist
and are tested. What it cannot install is a fix for a practice gap, because `blocks/` holds nothing.
Both facts are stated to the person in step 6 rather than left for them to discover.

## The order

### 0. Record the previous run's outcome

Before anything else, add a row to **Recorded runs** for the run this session is continuing, and say
whether it worked — naming which step carried the weight or which one was missing when it was needed.
If this session is not continuing a run, say so and move on.

This step is first because it is the one that gets skipped. `skills/context-checkpoint` spent three
runs asking a future session to record its result and got two blanks, because the request lived in a
file each cycle superseded. The answer belongs in this file, which nothing supersedes.

### 1. Establish where the executor is standing

Not where the target project is — where **you** are. This skill writes a gap record into a public
repository, so its own footing is load-bearing.

- Run `skills/checkout-isolation` first. It reports the branch, the other checkouts, and **which
  `pre-commit` actually guards this tree** — a worktree does not run its own.
- Confirm `./setup.sh --<tool>` has been run in this checkout. Its output is gitignored, so a fresh
  clone or worktree inherits nothing. `./setup.sh --dry-run` reports without writing.
- If the gate prints `WRONG TREE` or `NO GATE`, run `./hooks/pre-commit --all` by hand before any
  commit and do not rely on the hook firing.

State the result out loud. A step about where you are that does not say where you are cannot be told
apart from one that looked in the wrong place.

### 2. Ask for the target, once

One question, then stop: **what project, and who owns it.** Enough to know the stack, the rough size,
what it is for, and whether it is public or private — nothing else. Head counts, org structure and
roadmap are not practice gaps and are not asked for.

Record the answer so step 0 of the next run does not ask again.

### 3. Diagnose — delegate, do not reimplement

Invoke `skills/project-gap-analysis`. **Do not restate its seven checks here.** It owns them, it owns
the verdict vocabulary, and it owns the two-artifact split that keeps a private project out of a
public repo. Duplicating any of that creates two copies to keep in step, with nothing enforcing it.

That skill is `draft` and still changing — three runs, two gaps found in itself each time, the rate
not falling. Expect to find a gap in it, and record that gap in *its* file, not this one.

### 4. Report each absence with its backing

Every absence reported names the `validated` artifact behind it. This is the condition ADR 0017
attaches to being allowed to speak at all.

An absence with no `validated` artifact behind it **is not a finding** and is not reported. Say that
the check could not be decided, and why. `theory/loops/verifier-availability.md` is the reason: a
verdict a reader cannot trace is indistinguishable from one nobody checked.

### 5. Hand back only what earned it

| What the diagnosis found | What may be handed over |
|---|---|
| Any absence | The `validated` `theory/` file that explains why it matters. Always available |
| An absence a skill already answers | That skill, labelled with its real `status`. A `draft` skill is handed over *as* `draft` |
| Anything else | The name of the absence, and nothing executable |

Never hand over a block or template because a diagnosis found a gap. The demand rule in
`gaps/README.md` governs `blocks/`, and this skill does not amend it.

### 6. Say what is not available

Out loud, unprompted, before they ask: **`blocks/` and `templates/` are empty.** Today this hands
back reasoning and at most one `draft` skill. That is the honest inventory, and stating it is the
difference between a diagnosis and a sales pitch.

### 7. Record

The full-detail working report stays with the project's owner, outside this repo, forever. Only the
de-identified gap record enters `gaps/`, written from the report and never the reverse — subtractive,
per `skills/project-gap-analysis`, because a record written directly never had the detail to lose.

Then add this run's row to **Recorded runs** in this file.

## What this skill never does

- **Never invents a block** to have something to hand over. That is `gaps/README.md`'s named
  anti-pattern: inventing knowledge with extra steps.
- **Never lets the working report cross** into this repository, whatever permission was granted.
  Permission to name is not a reason to name.
- **Never claims a setup step it did not verify.** OAuth — a Slack app, connector authorisation, org
  settings — needs a human in a browser with admin rights. Stop, give the exact instruction, and
  confirm it happened before continuing.
- **Never re-asks what step 0 already recorded.**

## Recorded runs

The criterion is *recorded* runs, and a run recorded only as a success is a habit rather than a
criterion. An honest "step 4 had nothing to cite, and here is where" is worth more than a promotion.

| # | Date | Target class | Gap record | Did the skill work |
|---|---|---|---|---|
| — | — | — | — | **None yet.** |

Promote when there are recorded end-to-end runs — not when ADR 0017 is ratified, and not when
`project-gap-analysis` is promoted. Those change the rationale and the dependency; neither is
evidence that this procedure executes cleanly.
