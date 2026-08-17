---
id: gaps/0002-expensify-app
type: research
targets: [react-native]
status: validated
verified: 2026-08-12
sources: ["skills/project-gap-analysis/SKILL.md", "gaps/0001-rn-expo-wallet-timeboxed.md", "https://github.com/Expensify/App", "theory/agents/capability-load-cost.md", "theory/agents/instruction-provenance.md", "theory/agents/tool-surface-design.md", "theory/llm/context-degradation-at-length.md", "theory/loops/reading-and-running-find-different-defects.md", "theory/loops/verifier-availability.md", "theory/orchestration/delegation-and-context-boundaries.md"]
---

# 0002 — Expensify/App

Second run of `skills/project-gap-analysis`. Deliberately chosen as a **different owner** at the
opposite end of the scale from `gaps/0001`.

## Why this one is named

`gaps/README.md` requires records to be de-identified. This record departs from that rule, and the
reason is that following it here would have been worse on both counts.

`Expensify/App` is a **public** open-source repository. De-identifying it would not have protected
anything — "a very large React Native app with 64 CI workflows, four review subagents and 285k
commits since 2020" identifies it to anyone who cares — while making every claim below
**unverifiable**. The rule exists to stop a private project's weaknesses being published; it is not
a reason to make a public project's *published* practice uncheckable.

The general rule stands. The exception is: **a public source may be named, exactly as `research/`
names its sources.** Recorded in the skill.

## Project class

React Native + TypeScript, React Native Onyx for state, iOS/Android/Web. ~11,970 tracked files,
~285,000 commits, continuous since 2020-08, hundreds of contributors with no single dominant author.
Open source, community-contributed, with a HybridApp architecture spanning a second repository.

**Scope of this analysis: the agent-practice surface only** — `.claude/`, root instruction files, CI
workflows, hooks, and the declared review and test configuration. Roughly a hundred files. The
~11,900 application source files were not read, because none of the seven checks asks about them.
Checks 5 and 6 were **sampled, not enumerated**; both say so below.

## Checks

| # | Check | Verdict | vs `0001` |
|---|---|---|---|
| 1 | Resident capability cost | `present` | same |
| 2 | Instruction provenance | `present` | **0001 was `partial`** |
| 3 | Tool surface as prose | `present` | same |
| 4 | Reset practice | `absent` | **same — second occurrence** |
| 5 | Both defect channels | `present` (sampled) | same |
| 6 | Verifier availability | `partial` | **0001 was `absent`** |
| 7 | Delegation boundaries | `present` | 0001 was `n-a` |

### 1 — `present`, and close to exemplary

`.claude/skills/coding-standards/` holds roughly fifty coding rules as **one standalone file per
rule**, reached from a quick-reference table of links in `SKILL.md`. Only the index is resident; a
rule body is read when a rule is actually in question.

That is `theory/agents/capability-load-cost.md`'s claim implemented rather than merely respected:
declared by name it is nearly free, and the bytes are paid only on load. The same shape recurs in
`agent-device-evidence/references/` and `onyx/offline-patterns.md`.

Named honestly: `coding-standards` carries `alwaysApply: true`, so its index **is** resident every
turn. That is the correct half to keep resident — an index of links is the cheap part, and it is what
makes on-demand loading discoverable at all.

### 2 — `present`

Two entry points, and the pointer runs the right way. `AGENTS.md` is three lines and says all
guidelines are consolidated into `CLAUDE.md`, which then carries 362 lines of stack, architecture,
conventions and testing guidance.

**This is the exact pattern `gaps/0001` was missing.** Same two-file structure, same short
tool-neutral file — and here it resolves, because it names the file that holds everything. An
executor entering at the tool-neutral name reaches the full instruction set in one hop.

### 3 — `present`

Subagent descriptions are one line, action-first, and state what the agent produces — "Reviews code
and creates inline comments for specific rule violations." Skill descriptions name domain and
trigger together. Each subagent additionally declares an explicit `tools:` allowlist, which is
check 1's principle applied per agent rather than only per project.

Two cosmetic observations, neither driving the verdict: one agent file opens with a blank line
between `---` and `name:`, which some frontmatter parsers will not accept; and one `tools:` value
carries a trailing space.

### 4 — `absent`

No session-reset, context-management or clearing guidance anywhere in the root instructions,
`.claude/`, or the contributing guides. Neither a behavioural trigger nor a token-count one.

**This is the second independent occurrence.** See *Demand* below — it is the finding of this record.

### 5 — `present`, sampled

Reading channel: `PR_REVIEW_GUIDELINES.md`, `.github/CODEOWNERS`, a pull-request template, a
contributing guide on AI etiquette, and — unusually — **four automated reviewer subagents** that
produce structured review output. The reading channel is not only present, it is partly mechanised.

Execution channel: dedicated `test`, `lint`, `typecheck` and build workflows in CI, a
`playwright-app-testing` skill, and an `agent-device` skill carrying device-automation flows with
committed test macros.

Sampled by configuration, not by enumerating the suite. Depth of either channel is not established
here, only its existence.

### 6 — `partial`

Sixty-four CI workflows, including dedicated `lint.yml`, `typecheck.yml` and `test.yml`. Checks
exist and are invoked automatically. There are no git hooks; enforcement lives in CI and in a
`PostToolUse` settings hook that formats every file an agent edits.

Fail-open shapes are present but **deliberately placed away from checks**: the `continue-on-error`
occurrences sit on deploy and artifact steps — submitting a previous production build, downloading a
dSYM, uploading release assets, building storybook docs, hiding a bot's old comments. A failed
artifact upload not blocking an already-successful deploy is correct.

The verdict is `partial` rather than `present` for one specific instance. In the spell-check
workflow, the step that gathers the file list to check ends `... | grep -v '^\.' > changed-files.txt
|| true`. That swallows *all* of grep's non-zero exits, not only "no matches". If the gathering step
fails outright, `changed-files.txt` is empty and the spell check passes having examined nothing — a
gate reporting success on content it never read.

This is the same defect class, and the same `grep`-three-states shape, that this repository found and
fixed in its own redaction gate. Narrow consequence here, and worth naming precisely so it is not
read as a claim about Expensify's CI discipline generally: 63 of 64 workflows were not audited, only
pattern-scanned.

### 7 — `present`, and close to exemplary

Four subagents, each with an explicit `tools:` allowlist. The one body read in full carries
everything across the boundary in writing: the role, where the rules physically live, a numbered
procedure, an explicit output JSON schema, a fallback for the token-limit failure mode, a `CRITICAL`
constraint bounding what may be commented on, and an explicit list of what the agent must **not** do.

That is `theory/orchestration/delegation-and-context-boundaries.md` satisfied: nothing load-bearing
is left to be inherited from a parent conversation the child never had.

One observation: that procedure's numbering runs 1, 2, 3, 4, 3, 4, 5, 6, 7 — two duplicated indices
in a prompt that instructs the agent to build a checklist from its own numbered steps.

## Unstatable findings

None.

## Demand

| From | Capability wanted | Occurrences |
|---|---|---|
| Check 4 | A behavioural session-reset trigger, never a token threshold | **2** — `0001`, `0002` |
| Check 2 | A bidirectional instruction-provenance pattern | 1 — `0001` only |
| Check 6 | A minimal enforcement gate for a React Native project | 1 — `0001` only |

### Check 4 has reached two independent occurrences

A 48-hour single-developer timebox and a six-year, 285k-commit, multi-hundred-contributor open-source
project — different owners, different scales, analysed separately — **both lack any session-reset
practice.** Neither has a token threshold, which is correct; neither has a behavioural trigger, which
is the gap.

That the two projects agree here while disagreeing on checks 2 and 6 is what makes this worth
something. Checks 2 and 6 track project maturity, exactly as scale would predict. Check 4 does not:
it is absent at both ends.

**What this licenses, and what it does not.** It licenses treating the demand as real rather than
imagined. It does **not** license a claim about React Native projects generally — two observations
are two observations, and `skills/source-verdict`'s scope rule applies to this repo's own findings
as much as to anyone else's.

The answer is not a new block. It is `skills/context-checkpoint`, already in this repo at
`status: draft`, whose promotion criterion is recorded runs. Its demand is now evidenced from two
independent projects; its *execution* still has one recorded run. Those are different questions and
neither substitutes for the other.

### Two demands from 0001 met a worked solution rather than a second occurrence

Checks 2 and 6 came out `present` and `partial` here against `partial` and `absent` in `0001`. That
does not advance either demand — a project that already solved something is not a second project
asking for it.

It supplies something else: **a verified pattern**. Expensify's `AGENTS.md`→`CLAUDE.md` pointer is
precisely what `0001` lacked, working, in production, in a repository anyone can open.

This is a case the skill did not model. A gap record can carry a *solution* as well as a *demand*,
and when the second occurrence eventually arrives, the block should be **extracted from the working
example rather than designed from the complaint**. Recorded in the skill.
