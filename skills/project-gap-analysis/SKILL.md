---
id: skills/project-gap-analysis
type: skill
targets: [any]
status: draft
verified: 2026-08-20
sources: ["AGENTS.md", "MAP.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0011-rig-produces-evidence-not-truth.md", "gaps/README.md", "theory/agents/capability-load-cost.md", "theory/agents/instruction-provenance.md", "theory/agents/tool-surface-design.md", "theory/llm/context-degradation-at-length.md", "theory/loops/reading-and-running-find-different-defects.md", "theory/loops/verifier-availability.md", "theory/orchestration/delegation-and-context-boundaries.md"]
---

# project-gap-analysis

Analyse an existing project against this repo's validated practices and record what it is missing —
without ever bringing that project's identity into a public repository.

This is goal (c) in `AGENTS.md`. Its output is also the demand signal for goal (b): `blocks/` gets
built from gaps that recurred, never from gaps that were imagined.

`status: draft` — not yet run end to end. See **Recorded runs**.

## The rule this skill exists to prevent

**A gap analysis reads a private project and writes into a public one.** That is the whole risk, and
it is structural rather than accidental: the analysis is *useful* precisely because it is specific,
and specificity is what leaks.

`hooks/pre-commit` cannot save you here. It blocks absolute home paths and known secret shapes. A
private repository name, a client's name, an internal service name — written as a bare word — is the
class the gate explicitly **cannot** pattern-match (ADR 0009). A clean commit is not evidence about
this half.

So identity is stripped **at the moment of writing, not at the moment of committing.** There is no
review pass that catches it later, because by then it reads like ordinary prose.

### Two artifacts, and only one of them is committed

| Artifact | Where | Contains | Committed |
|---|---|---|---|
| Working report | the analysed project, or a scratch directory outside this repo | Everything. Real paths, real names, real line numbers — it is for the person who owns the project | **Never** |
| Gap record | `gaps/NNNN-<slug>.md` in this repo | The findings with every identifier removed | Yes |

Write the working report first and the gap record from it. Never the reverse: de-identifying is
subtractive, and a record written directly is a record that never had the detail to lose.

### What may cross into the gap record

| Never | Write instead |
|---|---|
| Repository, product, client or team name | The project **class**: stack, rough size, what it is for |
| Any path outside this repo | The role of the file: "the root agent instructions", "the CI workflow" |
| Internal service, host or endpoint names | The class of dependency |
| Verbatim code, config or prompts from the project | The *shape* of what was found, in your own words |
| Head counts, org structure, roadmap | Nothing. None of it is a practice gap |

If a finding cannot be stated without one of those, it does not go in the record. Say that
explicitly in the working report and stop — an unstatable finding is a real outcome, not a failure.

### Permission to name is not a reason to name

The owner may volunteer that the project can be named. That settles one question — whether you would
be exceeding what you were allowed — and leaves the other one untouched.

The gap record is committed to a **public** repository. A named record lets anyone correlate a list
of weaknesses with a findable project. For anything holding value, credentials or user data, that is
a published attack surface, and the owner granting permission does not make it less published.

So: **name freely in the working report, de-identify the record anyway.** Nothing is lost — the
owner already has the full-detail version. If they still want the record named after hearing the
reason, that is their call to make explicitly, not a default to fall into.

### The one exception: a public source may be named

A public open-source repository is named, exactly as `research/` names its sources. De-identifying
one is worse on both counts: the class description identifies it to anyone who cares, and every
claim in the record becomes **unverifiable** to a reader who could otherwise open the repository and
check it.

The limit is narrow. Public means *the practice being analysed is already published* — not that the
company is well known, not that a contributor made the code available to you, and not that a
repository is public while the finding concerns something it did not publish. When in doubt the
default rule wins, because a wrong call here is not correctable after a push.

A named record is also a public statement about someone else's work. State findings from evidence,
name what was sampled rather than audited, and record what the project does well with the same care
as what it lacks — the record is worthless as demand signal if it only looks for absences.

## The checks

Each check is a validated `theory/` claim turned into something observable in someone else's
project. **Every check cites its source; none is invented.** That is `AGENTS.md`'s no-invented-
knowledge rule applied to a checklist — a check with no backing doc is an opinion with a checkbox.

Run all seven. Answer each `present` / `partial` / `absent` / `n-a`, with the observation that
decided it.

### 1. Resident capability cost — `theory/agents/capability-load-cost.md`

Cost is what is **loaded**, not what is connected. Look at how many tool, MCP and skill definitions
sit in the window every turn versus being named and fetched on demand.

Look at: agent/MCP configuration, how many servers are always-on, whether tool schemas are deferred.
`absent` looks like every server connected eagerly because it might be useful.

### 2. Instruction provenance — `theory/agents/instruction-provenance.md`

For any given rule the agent follows, can you name the file it physically came from? Precedence
documented without provenance is the failure mode: the agent knows which rule wins and has no way
to change, report or verify the losing one.

Look at: instruction layers, nested instruction files, and especially **generated blocks that a
tool overwrites** — a rule you cannot edit locally is a rule you cannot reconcile.

### 3. Tool surface as prose — `theory/agents/tool-surface-design.md`

The model chooses by reading names and descriptions; schemas hold most of the bytes and do not
participate in the choice. Are custom tools and skills named and described for a reader?

Look at: custom tool/skill names and descriptions. `absent` looks like terse names with elaborate
schemas — bytes spent where they cannot help selection.

### 4. Reset practice — `theory/llm/context-degradation-at-length.md`

Degradation with length is real and measured; **no published measurement supports a token number as
the moment to reset.** So the failure here is bidirectional: no reset practice at all, *or* one
triggered by a token count.

Look at: how sessions end. A behavioural trigger (re-deriving a settled fact, contradicting an
earlier decision, losing the verified/assumed distinction) is `present`. A number is `partial` and
must be recorded as the specific error it is.

### 5. Both defect channels — `theory/loops/reading-and-running-find-different-defects.md`

Reading finds where the implementation departs from intent. Execution against hostile input finds
where the author's model of the environment departs from the environment. Neither class contains
the other.

Look at: whether review and adversarial execution both exist. Having only one is `partial`, and
name which one — that tells you which defect class is currently invisible.

A third case, found on run 1 and easy to get wrong: **both channels exist, but the depth of one
cannot be established from the repository alone.** Review is the usual one — pull requests prove a
shape, not that anyone read the diff. Record `present` and name the unestablished part. Do not
resolve it by assumption in either direction: an unverifiable channel is not a missing channel, and
it is not a working one either.

### 6. Verifier availability — `theory/loops/verifier-availability.md`

**The highest-yield check.** A verifier that cannot run is not a weak gate, it is an absent gate
reporting "not run". Does every gate distinguish *could not run* from *passed*?

Look at: gates, hooks and CI steps that swallow a non-zero status — `|| true`, `|| :`,
`2>/dev/null` on the thing being checked, a loop whose per-item status never reaches its caller.

Worked example, from this repo rather than a hypothetical: `hooks/pre-commit` collapsed grep's three
exit states with `|| :`, so an unreadable tracked file was skipped in silence while the run printed
"clean across N tracked files" and exited 0. A redaction gate reporting a pass on content it never
read. Found by review, fixed in `5703c92`, and now held by `hooks/pre-commit --self-test` (ADR 0013).
This check exists because the failure happened here first.

### 7. Delegation boundaries — `theory/orchestration/delegation-and-context-boundaries.md`

A delegation creates a new, empty context. It protects the child from noise and silently drops every
constraint the parent never wrote down.

Look at: subagent, task or job definitions. Do they carry their constraints explicitly, or assume
what the parent knows? `absent` looks like a prompt that would be ambiguous to someone who had not
been in the conversation.

### Before you run them: reconcile the list

`theory/` grows. Enumerate the files with `status: validated` under `theory/` and compare against the
seven above. If a validated doc has no check here, **stop and say so in the record** rather than
silently analysing against a stale list. Add the check to this file in the same session, or record
why it does not project onto a target project.

## Procedure

1. **Confirm scope with the owner.** Which project, and are you permitted to read it. Do not
   analyse a repository you were not pointed at.
2. **Ask how the project may be referred to.** Before writing a single line. A path does not tell
   you whether something is public. This is the one question that must precede the work.
3. **Reconcile the checklist** against `theory/`, per above.
4. **Run the seven checks**, recording the observation that decided each verdict.
5. **Write the working report**, in full detail, outside this repo.
6. **Write the gap record** in `gaps/`, de-identifying as you write.
7. **Record the run** in the table below.

## Output shape — the gap record

`gaps/NNNN-<slug>.md`, `type: research`, `status: validated` once the analysis is complete
(the analysis was done; the *demand* is what stays provisional). Body:

- **Project class** — stack, rough size, what it is for. No name.
- **Checks** — the seven, each `present` / `partial` / `absent` / `n-a`, each with its
  de-identified observation and its `theory/` citation.
- **Unstatable findings** — a count, and why. Never the content.
- **Demand** — for each `absent` or `partial`, what block would have closed it. Phrased as a
  capability, not as a file name you have already decided on.

`targets` follows the **findings**, not the project. Use `[any]` unless a finding genuinely depends
on the stack — none of the seven checks reads application source, so that is the usual case even when
the project is emphatically a React one. The stack belongs in *Project class*, where it describes what
was analysed, rather than in a field a query will read as "this finding applies to React".

## What a gap record may and may not cause

**One record never justifies building a block.** A single project's gaps are evidence about that
project, exactly as `rig/` output is evidence and not truth (ADR 0011).

A block is built when **the same demand appears in at least two independent gap records** — different
projects, different owners, analysed separately. Until then the demand is recorded and waits.

The reason is the failure this repo is built to avoid: one analysis plus enthusiasm produces a
`blocks/` directory full of things that solved one project's problem and are described as practice.
That is inventing knowledge with extra steps.

### A record may carry a solution instead of a demand

When a check comes out **better** in one project than another, that advances no demand — a project
that already solved something is not a second project asking for it. It supplies something more
useful: a **worked pattern**, in production, that a reader can go and open.

Record it as such. When the second occurrence does arrive, the block is **extracted from the working
example rather than designed from the complaint**, which is the difference between a block that has
been run and a block that has been imagined.

### Two occurrences licenses the demand, not a general claim

Reaching two occurrences means the demand is real rather than imagined. It does **not** license a
statement about projects of that kind generally. `skills/source-verdict`'s scope test — the claim may
never be wider than the evidence — applies to this repo's own findings exactly as it applies to
someone else's blog post.

Also check where the answer already lives. A demand that resolves to an existing draft artifact is
not a request for a new one, and building the new one anyway is how a repository ends up with two
half-finished answers to the same question.

## Recorded runs

Built in from the start, because `skills/context-checkpoint` spent three runs asking a future
session to record its results and got zero — the request lived in a file each cycle superseded. The
answer lives here, in the file nothing supersedes.

| # | Date | Project class | Record | Did the skill work |
|---|---|---|---|---|
| 1 | 2026-08-11 | React Native + Expo mobile wallet, timeboxed, agent-built | `gaps/0001-rn-expo-wallet-timeboxed.md` | **Yes, with two gaps in the skill itself** — see below |
| 2 | 2026-08-12 | Large open-source React Native app, 6 years, hundreds of contributors | `gaps/0002-expensify-app.md` | **Yes, with two more gaps** — and the demand rule fired for the first time |
| 3 | 2026-08-20 | Open-source cloud security platform, 10 years, Python monorepo with a React UI | `gaps/0003-prowler.md` | **Yes, with two more gaps** — and the first project analysed whose agent practice was already mature |

Run 1 produced a complete record with all seven checks decided and no unstatable findings. Two
things the skill did not cover, both found by running it and both now fixed above:

- **Check 5's verdicts were underspecified.** The skill said "having only one channel is `partial`".
  The case that actually occurred is different: both channels exist, but the *depth* of one — whether
  pull requests were genuinely reviewed — is not establishable from a repository alone. That is
  neither `present` nor `partial` as written. Resolved by recording it as `present` with the
  unestablished part named, and the check now says so.
- **Owner authorisation and de-identification are separate decisions.** The owner volunteered that
  the project could be named. The record was still written de-identified, because the rule protects
  against publishing an identifiable weakness map, not only against exceeding permission — and this
  project was a wallet. The skill had no guidance for "permission granted, de-identify anyway".

Run 2 was chosen for **owner independence and scale contrast** rather than convenience: a different
owner, hundreds of contributors, six years, ~11,970 files against ~200. Two more gaps in the skill,
both now fixed above:

- **No exception for a public source.** The de-identification rule was written for private projects
  and read as absolute. Applied literally to a well-known open-source repository it would have
  protected nothing — the class description identifies it anyway — while making every claim
  uncheckable. Now stated as an exception with its limit.
- **A record can carry a solution, not only a demand.** Two checks came out better here than in
  run 1, which advances no demand but supplies a working pattern for one. The skill only modelled
  records as sources of demand.

**The demand rule fired for the first time.** Check 4 reached two independent occurrences, and it
resolved to an existing draft skill rather than to a new block — which is the outcome the rule is
supposed to produce when the answer already exists.

Run 3 was chosen for a property the first two could not supply: a project whose agent practice is
**already mature**. A project that lacks everything tells you little, because every check fails for
the same reason. Two more gaps, both now fixed above:

- **Run 2's own fix was applied in one file and not the other.** Run 2 added the public-source
  exception here, and `gaps/README.md` went on stating the opposite rule in bold — while `0002` sat
  in that directory naming a public repository. Nobody noticed for eight days, because nothing reads
  both files at once. Run 3 could not write a named record under a README forbidding one, which is
  the only reason it surfaced. **A rule changed in a skill must be changed in the file that states it
  as a rule, in the same commit.** The contradiction is now recorded in `gaps/README.md` rather than
  silently repaired: the shape is more instructive than the fix.
- **The output shape said nothing about `targets`.** Runs 1 and 2 both analysed React Native
  projects and used the project's stack, so the question never came up. Run 3's findings are entirely
  stack-independent, and copying the precedent would have claimed a dependency that is not there.
  Now stated in *Output shape* below.

**A `present` verdict is a finding, not a blank.** Three of run 3's seven came out at or above what
the backing `theory/` doc asks for, and one of those is a pattern this repo could not have designed
from its own material. A skill that only records absences would have thrown all three away and
reported a project with two problems.

Promotion to `status: validated` needs recorded runs, not a better rationale. Three runs, every one of
which changed the skill, is evidence that it executes and evidence that it is not settled. The rate is
not falling: run 3 found as many gaps as run 1. Record failures
with the same care as successes: a skill that only records its wins has a habit, not a criterion.
