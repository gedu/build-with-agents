---
id: hypotheses/index
type: index
targets: [any]
status: draft
verified: 2026-08-07
sources: ["decisions/0012-a-hypothesis-is-never-citable.md", "skills/source-verdict/SKILL.md"]
---

# hypotheses/

Falsifiable claims with a declared test and no result yet. Written **before** the experiment that could
settle them, which is the only moment at which writing one is worth anything.

Entries are not enumerated here; the directory carries the truth and `MAP.md` carries the count.

## Citability: zero

Not "evidence only" like `research/` and `rig/`. **Zero.** Nothing may cite a hypothesis — not a
`theory/` file's `sources`, not an ADR's justification, not a commit message arguing a design.

ADR 0012 carries the reasoning. The short version: if a hypothesis carried any weight, writing one
would be a way to manufacture weight without running the test, and pre-registration would become a
laundering channel instead of a constraint.

**Naming one as the target of a test is not citing it.** A spec may say "record this because
`hypotheses/0001` needs it"; that uses the hypothesis as an *object of study*, not as a *warrant* for a
claim. Without this distinction the rule would forbid writing the very experiment that settles the
hypothesis. The line is simple: **you may point at it to say what you are testing. You may never point
at it to say why something is true.**

## Required shape

| Section | Content |
|---|---|
| Claim | One falsifiable sentence. If no observation could contradict it, it does not belong here |
| Why it is plausible | What prompted it — an observation, a source, a run. Not an argument that it is true |
| The test | The **exact** observation that would support it, and the exact one that would refute it. Written before the run |
| What it would change | Which `theory/` file gains, narrows or loses a claim if this resolves either way |
| Status | `open`, or `resolved → <artifact>`, or `refuted` |

**The test section is mandatory.** Without it this is an opinion, and by `skills/source-verdict` test 1
a position can be neither supported nor refuted.

## Resolution is a new artifact, never a status flip

A supported hypothesis is **not** promoted in place. Write the `theory/` file on the evidence, with its
scope and its spread, and record here where it resolved. The theory file cites the **measurement** —
never this file, and never the fact that the outcome was predicted.

A refuted hypothesis stays, with `status: rejected`. The refutation is the value; deleting it invites
re-importing the same idea in six months from someone who reached it independently.

## Does NOT belong here

- A claim you have already tested. That is `theory/` if it held, `rejected` if it did not.
- A question. A hypothesis is a statement that could be wrong; a question cannot be wrong.
- A plan, a preference, or a design intention. Those are `decisions/`.
- An idea with no stated test. Write the test or do not write the file.

## Frontmatter contract

```yaml
---
id: hypotheses/<NNNN>-<slug>
type: research
targets: [any]
status: draft        # never `validated` — see ADR 0012
verified: 2026-08-07
sources: []          # provenance of the idea: the run, journal entry or verdict that prompted it
---
```

`type: research` because a hypothesis is unadjudicated material, and `AGENTS.md`'s type enum has no
value of its own for it. `status` is `draft` while open and `rejected` once refuted — **never
`validated`**, because a validated hypothesis is a `theory/` file and this one is a pointer to it.
