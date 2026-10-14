---
id: gaps/0004-repack-atlas
type: research
targets: [any]
status: validated
verified: 2026-10-14
sources: ["skills/project-gap-analysis/SKILL.md", "gaps/0001-rn-expo-wallet-timeboxed.md", "gaps/0002-expensify-app.md", "gaps/0003-prowler.md", "https://github.com/callstackincubator/repack-atlas", "theory/agents/capability-load-cost.md", "theory/agents/instruction-provenance.md", "theory/agents/tool-surface-design.md", "theory/llm/context-degradation-at-length.md", "theory/loops/reading-and-running-find-different-defects.md", "theory/loops/verifier-availability.md", "theory/orchestration/delegation-and-context-boundaries.md", "decisions/0014-a-public-guarantee-cannot-be-opt-in.md"]
---

# 0004 — callstackincubator/repack-atlas

**This record adds zero occurrences to any demand.** It is the first analysed project that failed
`gaps/README.md`'s independence test, and that test is what the demand rule rests on. Everything else
here — five of seven checks at or above what the backing `theory/` doc asks for — is a worked pattern,
not a demand signal. Read *Independence* before using any number in this file.

## Why this one is named

`callstackincubator/repack-atlas` resolves `private: false`, `fork: false`, `archived: false`, MIT,
default branch `main` — re-checked against the GitHub API on 2026-10-14 rather than inherited from an
earlier lookup in `odd/tasks/verified-agent-delivery.md`. Named under the exception `gaps/README.md`
records, on the same basis as `0002` names `Expensify/App` and `0003` names Prowler: public means the
practice being analysed is already published.

Naming matters more here than in the earlier records, not less. The load-bearing finding below is a
*published self-declaration*; a reader who cannot open the repository cannot check it, and an
uncheckable claim about someone else's work is worth nothing.

## Independence

Sampled from a fresh HTTPS clone: HEAD at 2026-10-06, 142 commits, first commit 2026-09-29, 359 tracked
files, three workflows, 45 unit test files, one e2e spec, 21 `odd/tasks/` documents.

| Test in `gaps/README.md` | Result |
|---|---|
| Different project | **Yes** — a different repository, first commit a month before this record |
| Analysed separately | **Yes** — fresh clone from the public remote, nothing read from any local checkout |
| Different owner | **No** |

142 commits under two commit identities, both the operator's — one of them is what `gh api user`
resolves to for the account that wrote this repository. No third identity appears in any commit.

For contrast, the independence test **passes** on `0003`: that project is organisation-owned, created
2016-08-24 — a decade before this operator's tooling was created (2026-02-27) — and a code search for
that tooling's organisation inside it returns zero hits. Different owner, no contact, no dependency.
That contrast is why this run's result is worth recording: the test discriminates, so failing it here is
a measurement and not a blanket refusal to count anything.

That alone might be coincidence between two people who share an employer. It is not coincidence, and
the project says so itself. Its own design document has a section listing what it borrowed:

> From [gentle-ai](https://github.com/Gentleman-Programming/gentle-ai): ✅ skills index table in
> `AGENTS.md` with triggers+paths; ✅ `AI_POLICY.md` (human owns the submission; disclose material AI
> help; **no `Co-Authored-By` AI trailers**); ✅ 400-line PR review budget with a maintainer
> `size:exception` escape hatch

with the borrowed files itemised as `AGENTS.md`, `skills/`, `AI_POLICY.md`, `CONTRIBUTING.md`,
`pr-size-policy.yml`, and `AI_POLICY.md` opening by stating it adapts gentle-ai's policy under MIT.

**So the agent practice being graded here descends from this operator's own published tooling, by its
own account.** Counting its gaps as observations would be circular in the worst available direction:
our own tooling reflected back at us as an independent second project asking for a block. That is
manufacturing weight, which is the reasoning `decisions/0012` refuses for pre-registration. The same
logic applies when the pre-registered thing is our own influence.

Consequence, stated as the rule it earns: **the skill's independence test has to include ownership,
and ownership has to be measured before verdicts are written.** See *What this run found in the skill*.

## Project class

TypeScript CLI + studio tooling for Module Federation in React Native. 359 tracked files, 142 commits
whose first and last are seven days apart (2026-09-29 to 2026-10-06), one human author. Three CI workflows, Playwright e2e, an ink-based TUI, a doctor
subsystem, vendored upstream code under a provenance ledger. Agent practice is first-class: a canonical
skills directory, generated adapter links, generated instruction tables, a 21-document `odd/` planning
tree. Not a mobile app; the tooling layer underneath several.

## Checks

### 1. Resident capability cost — `present`, with a measured figure

`theory/agents/capability-load-cost.md`

Resident surface measured, not estimated: `AGENTS.md` 11,164 B, `CLAUDE.md` 86 B, `AI_POLICY.md` 2,709 B
— **13,959 B total**, of which 18 generated table rows (5 + 13, counted inside the marker pairs; a
whole-file `^| ` grep returns 22 and is the wrong measure, because it counts headers and separators).
`CLAUDE.md` is one sentence delegating to
`AGENTS.md` and calling it the only instructions file, so no second body loads.

Five skills; only their names and triggers are resident. Frontmatter description bytes measured:
445 + 395 + 380 + 359 + 348 = **1,927 B across five**. Bodies (3,105–5,975 B each) are fetched on
demand. No MCP configuration, no tool or agent definition files, no prompt files anywhere.

The check's actual subject is a cost that grows by contribution, and that one has a gate:
`scripts/agent-sync.mjs` sets a 1,024-character description cap, fails `--check` over it with a message
naming the file and the limit, and `--check` runs in CI. A resident-cost budget that is enforced rather
than advised — the thing `capability-load-cost.md` asks for and this repo does not itself have.

One honest cost, and it is deliberate: the repo states that agents do not reliably load skills from
descriptions alone, so it also generates an explicit auto-invoke table. That is a second 13 resident
rows bought on purpose to fix a reliability problem the theory doc predicts.

### 2. Instruction provenance — `present`

`theory/agents/instruction-provenance.md`

The runner script's own header names the canonical source, names the two derived artifacts, and gives
both the repair command and the check command. The instruction file marks the generated regions with
begin/end markers, says do-not-edit between them, and names the regenerator inside the file. The skill
that governs skills restates the rule and points at frontmatter as the thing to edit instead.

Machine-enforced, which is what separates this from folklore: CI runs the sync check and drift exits 1.
Observed firing — with one generated adapter link removed, the check exits 1 and names the missing
link and the repair command.

Exactly one `AGENTS.md` in the tree and one 86-byte pointer. No precedence statement exists for the
repository itself; with one canonical file and one pointer there is nothing to rank, so this is
correctly not a gap. (A grep for "precedence" does hit the design document — that passage is `--port`
flag precedence, unrelated.)

### 3. Tool surface as prose — `present`, one rule with no verifier

`theory/agents/tool-surface-design.md`

Every description opens with scope and then a `Trigger:` clause naming concrete paths and symbols, so
sibling selection is decided by which files you are touching rather than by tone. Measured 348–445 B
against a CI-enforced 1,024 B budget — bytes spent where they participate in the choice, which is the
whole claim of the backing doc.

Two soft spots, both verified rather than inferred:

- The `Trigger:` wording is documented as required, and the script **never enforces it**: no failure
  path mentions it. The flag is only *consumed*, via a regex that lifts the trigger into a table
  column. A stated rule with no verifier — this repository's own test for whether a rule exists.
- One pair genuinely overlaps: the setup skill's trigger claims "running the fixture test suite" while
  the doctor skill owns "a finding that has no fixture yet". Adjacent and resolvable; the only pair
  needing a second read.

### 4. Reset practice — `absent`

`theory/llm/context-degradation-at-length.md`

Nothing in the instruction file, the AI policy, the contributing guide, the design document, or any
skill states when to start a fresh session or compact. No behavioural trigger, and no token threshold
— the absence is not the "token number" error, it is the empty case.

The most interesting artifact: one planning document says *"long-session backstop applies."* That rule
is defined nowhere in the repository — that sentence is its only occurrence in any committed file. A
rule invoked and never written down: the agent obeying it has no way to know it fired, and neither does
the reader. Closest relative in this repo is a documented convention nobody implemented.

Two other candidates for "practice" are records, not triggers: one task notes a session ended at
`/clear`, and several carry budget-gate codes emitted by an external harness after the fact.

### 5. Both defect channels — `present`, review depth unestablished

`theory/loops/reading-and-running-find-different-defects.md`

Review channel: PR template with issue link, pasted-output checks and an AI-disclosure line; an
issue-first contribution gate requiring an approved issue; a hard 400-line diff budget with a
maintainer-labelled escape hatch; and an AI policy whose duty is explainability — a reviewer may ask
you to defend any line, and being unable to is a stated rejection reason rather than a punishment.

Execution against hostile input, and it is real: a dedicated fixture makes every user-controlled
manifest string an injection probe — script tags, `onerror` image handlers, `onload` SVG — placed in
app names, expose names and paths, shared package names. An e2e test renders it and asserts the page
shows the probes as literal text, opens no dialog, injects nothing, with a dialog collector watching. A
unit test fails the build if the render path so much as contains `innerHTML`, `outerHTML`,
`insertAdjacentHTML` or `document.write`. Malformed-config and deliberately-corrupt-fixture cases
round it out. No fuzzing, property-testing or mutation tooling.

Depth not establishable from the repository: no `CODEOWNERS`, and the branch-protection endpoint
returns 404 — not protected. "One reviewer per PR by design" exists as prose in the design document.
Third recurrence of 0003's third case: the channel is present, its depth is neither a missing channel
nor a demonstrated one.

### 6. Verifier availability — `partial`, found by running rather than scanning

`theory/loops/verifier-availability.md`

**The cleanest gate surface in this series.** Zero swallowed statuses across the workflows *and* the
scripts — scanned for `continue-on-error`, `|| true`, `|| :`, empty catch, `set +e`. Against 0002's
sixty-four workflows and 0003's 24 continue-on-error plus 43 `|| true`, this repo has none of the
shape at all. Every declared check is invoked at a point nobody skips: push-to-`main` and pull-request
runners take lint, typecheck, build, test, the agent-sync check and the vendored-provenance check;
pull-request runners take commit title, commit range, diff budget and linked-issue.

It distinguishes could-not-run from passed with its own exit 2, measured rather than read: bad flag →
2 with usage; unreachable revision range → 2 naming `git log` failure. And the empty-set case, the one
`gaps/0002`'s counterexample is about, **fails rather than passing**: with the skills directory removed,
the sync check reports "no skills found" and exits 1. (Run in a copy of the clone, not the sampled
tree.)

`partial`, not `present`, for two vacuous passes — and neither is visible to a pattern scan:

| # | Shape | Observed |
|---|---|---|
| (a) | The sync check parses no arguments: it looks for its one flag and, on any other spelling, falls through to **repair** mode | On a drifted tree: correct flag → exit 1, fires. One-character typo in the flag → **recreated the link the drift had removed**, printed "5 skills in sync", exit 0; a subsequent real check then exited 0. A mistyped flag in the CI step does not skip the check — it destroys the evidence and reports green |
| (b) | The 400-line budget job with its two SHA inputs empty | `git diff --numstat` with empty endpoints exits **0 with empty output** (measured), so the sum is 0, the job prints "Within the 400-line review budget" and exits 0. A budget check that passes having diffed nothing |

(a) is the sharper of the two and it is a class none of the earlier records could have found by
grep: there is no swallowed status, no `|| true`, no discarded stderr — nothing to match. It was found
by running the gate with a planted defect and again with a broken invocation, which is
`reading-and-running-find-different-defects.md`'s claim demonstrated on the highest-yield check.
The correct shape already exists two files over: the commit-message checker parses its arguments
defensively and exits 2 on anything unrecognised. Same directory, same author — one of the two gates
knows that an argument it cannot parse means it did not run, and the other one does not.

(b) is the same shape `0002` recorded — an empty gather yielding a green — arriving in a workflow with
no `|| true` anywhere in it, which is why the scan method alone would have called this `present`.

| Verdict ledger | |
|---|---|
| swallow shapes in `.github/` + `scripts/` | **0** |
| vacuous passes demonstrated by execution | **2** |
| gates that exit 2 on could-not-run | measured on two of them |
| local prevention layer | none — no hooks directory, no configured hooks path, nothing shipped |

Prevention here is CI-only and the branch is unprotected, so it **detects and does not prevent** —
`decisions/0014`'s own conclusion, reached independently by a project that never read it.

### 7. Delegation boundaries — `present`, one axis short of 0003

`theory/orchestration/delegation-and-context-boundaries.md`

Delegation is recorded per task with a trigger that is a fact rather than a mood — "writer trigger: 6+
non-trivial files", "mapping trigger: 4+ files". Each delegated unit ships its own constraint block
quoting the parent rule by number, hard constraints restated for the writer (machine paths untouched,
terminal-only surface, a ring-buffer cap), and explicit prohibitions ("No push / PR / repo creation /
publish"). The boundary demonstrably binds: one task records a delegated writer stalling mid-unit with
the parent finishing inline, another records dispatched writers being **refused by a preflight gate**.

Missing axis: no permission, network, time or rate limit attaches to any delegated context — scope is
prose scope. No subagent definition files, no prompt files, and no workflow invokes a model, so there
is no machine-checkable envelope anywhere. `0003` supplies the worked pattern this lacks: bounded
delegation on five explicit axes.

## Unstatable findings

**Zero.** Every claim above is checkable by cloning the named public repository, and the record's two
load-bearing findings are published statements in its own design document. No path outside this repo, no
commit identity, no machine identifier appears in this file.

## Demand

**No occurrence is added to any demand, including check 4's.** Per the Independence section: `gaps/README.md`
requires different projects *and different owners*, and this is the operator's own repository with its
agent layer self-declared as adapted from this operator's published tooling.

| Check | Verdict | Counts toward a demand? |
|---|---|---|
| 4 — reset practice | `absent` | **No.** Would have been the fourth occurrence; it is not independent, so it neither adds nor subtracts. Of the three prior occurrences, **two stand on established ownership** (`0002`, `0003`) and `0001`'s owner is **unestablished** — see `gaps/README.md` and the amendment in `decisions/0017`. The demand clears the two-record bar either way, so this run's zero still changes nothing |
| 6 — verifier availability | `partial` | **No**, same reason. Also worth noting it is `partial` for a *different* reason than 0002/0003, so it would not have pooled cleanly even if it counted |
| 1, 2, 3, 5, 7 | `present` | Not a demand at all — see below |

The two shapes that are genuinely demand-shaped are ones this repository **shares**, so neither is a
block to build:

- **Empty-input vacuous pass.** Our own commit-message gate does the same thing as the one criticised in
  (b) above: `./hooks/commit-msg --range <same> <same>` prints "clean across 0 commit message(s)" and
  exits 0. Measured on this tree. A range that names zero commits is *could not run*, and we report a
  pass.
- **Flag parsing that defaults to doing-the-thing.** Our rig executables read their own flags
  positionally; T9's own CI job had to defend against discovery returning nothing precisely because a
  scan that examined nothing must not report green.

Both land on `decisions/0014`'s non-negotiable list, which this repo wrote and is still discharging.
Recording them as demands from someone else would be laundering our own TODO into a `blocks/` entry.

## What this record supplies rather than asks for

Five of seven checks came out at or above what the backing doc asks for, and this project wrote none of
them itself. Its own source list names the two it took, and **the second one is another record in this
very directory**:

> From [prowler](https://github.com/prowler-cloud/prowler): ✅ `AGENTS.md` as the single source +
> explicit **Auto-invoke** table; ✅ skill metadata driving a sync script; ✅ per-tool symlinks

listed alongside `skills/setup.sh`, `skills/skill-sync` and prowler's PR #9751 as the rationale for the
sync check — plus the gentle-ai list quoted under *Independence*. So the practice graded here is lifted
from two published sources, one of them ours and one of them `0003`'s project.

*A first draft of this paragraph said "unlike 0003 — whose maturity was earned — this one borrowed it".*
Both halves were wrong. `0003` borrowed nothing from this repository (below), but nothing in `0003`
records how **its** practice arose either, so "earned" was an unverified claim about another project
that no one has evidence for — and the comparison was pointless, because this project cites `0003`'s
project as its own upstream. Removed rather than softened.

What survives is the useful part: practices were copied from published documents, adapted, and they
hold up under the same seven checks that graded their sources. That is a **transfer test** — the
strongest evidence in this file, and evidence about the practices rather than about any block.

1. **A CI-enforced budget on the one resident cost that grows by contribution.** Description length
   capped, checked, named in the failure message. This repo has no such cap on its own skill
   descriptions, and check 1's whole argument is that this specific cost compounds.
2. **A gate whose empty-set case fails.** Removing the input directory makes the check exit 1 with a
   reason. This is `gaps/0002`'s counterexample solved in the opposite direction, in a repo small enough
   to read in one sitting — a better extraction target than any of the three larger projects.
3. **Generated regions that name their regenerator inside the markers**, plus a check that fails CI on
   drift and prints the repair command. Provenance you can violate and get told about, which is the form
   `instruction-provenance.md` wants and `0001` lacked.
4. **A per-file vendored-provenance ledger with an exit-1 checker.** Every vendored file needs a
   section, an upstream commit, and a copyright header. Same family as this repo's fixture
   `MANIFEST.sha256` gate, pointed at a different substrate.
5. **Delegation records that survive contact**: refusals and stalls written into the task file, not just
   successes. 0003's five-axis envelope is still the better pattern; this is the honesty half.

## What this run found in the skill

Two gaps, both real, both fixed in `skills/project-gap-analysis/SKILL.md` in this same commit.

1. **Nothing in the procedure establishes ownership.** The demand rule needs different owners; the skill
   never asks, and this is the first analysed project where the answer changes the record's entire
   purpose. Had I not run commit-identity queries on my own initiative, this record would have licensed
   a `blocks/` entry from a dependent observation — the exact failure the demand rule exists to stop,
   arriving through a rule that was never operationalised as a step.
2. **Check 6 is written as a read, and this run's verdict required running.** 0002 and 0003 pattern-scanned
   for swallowed statuses, which is the right method for the defects they found. It cannot find the
   defect here: a flag typo that silently switches a checker into repair mode has no swallowed status,
   no `|| true`, no discarded stderr — there is nothing to match. The check now asks three states per
   gate: run it clean, run it with a planted defect, run it with empty or unrecognised input. That is
   `reading-and-running-find-different-defects.md` applied to the skill's own highest-yield check.

One correction recorded for provenance: the explore pass reported the trigger text as duplicated into
both resident tables and its description total as an estimate. Neither survives measurement — the
auto-invoke table's left column is a separately authored field with different wording, and the byte
total is 1,927 measured. Cited here because a record that silently repairs its own inputs is the class
this repository's whole citation discipline is against.
