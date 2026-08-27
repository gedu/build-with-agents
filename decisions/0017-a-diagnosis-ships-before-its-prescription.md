---
id: decisions/0017-a-diagnosis-ships-before-its-prescription
type: decision
targets: [any]
status: draft
verified: 2026-08-27
sources: ["journal/2026-08-26-the-installer-already-exists-split-in-two.md", "MAP.md", "gaps/README.md", "gaps/0001-rn-expo-wallet-timeboxed.md", "gaps/0002-expensify-app.md", "gaps/0003-prowler.md", "skills/project-gap-analysis/SKILL.md", "decisions/0003-blocks-and-templates-are-separate.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0011-rig-produces-evidence-not-truth.md", "theory/agents/capability-load-cost.md", "theory/agents/instruction-provenance.md", "theory/agents/tool-surface-design.md", "theory/llm/context-degradation-at-length.md", "theory/loops/reading-and-running-find-different-defects.md", "theory/loops/verifier-availability.md", "theory/orchestration/delegation-and-context-boundaries.md"]
---

# 0017 — A diagnosis ships before its prescription

`status: draft`. Ratification is the operator's act, and this has not been used yet — the same
standard `0016` is held to.

## Context

The question arrived as a request: could someone who does not know where to start get "the basics" of
agent practice, guided, and have it be tested rather than copied. The obvious build is a surface that
hands over a starter kit, and `gaps/README.md` names that exact thing as the failure it exists to
stop — "inventing knowledge with extra steps".

That made the request look blocked on `blocks/`. It is not, and the premise was wrong. A frontmatter
query over this repo returns **19 `validated` artifacts**, and the seven checks in
`skills/project-gap-analysis` map one-to-one onto the seven `validated` files in `theory/`. The
diagnostic layer is fully backed. What is empty is the *prescriptive* layer — `blocks/` and
`templates/`, which ADR 0003 already keeps separate from each other and which `MAP.md` describes as
executable artifacts with a contract.

So the forces are not diagnosis-versus-nothing. They are diagnosis-versus-prescription, and only one
of the two has earned anything.

The constraint that made it urgent is what waiting would cost. Reset practice is `absent` in all
three gap records — three projects, three owners, spanning a timeboxed solo build and two mature
public repositories. That is the most evidence any demand in this repo has accumulated, and it
resolved to promoting an existing draft skill rather than to a new block, which `gaps/README.md`
records as the outcome the demand rule is *supposed* to produce when the answer already exists.
Waiting for the prescriptive layer therefore waits on an output the mechanism does not reliably
produce.

Decided by the operator on 2026-08-27, on the question the journal entry above left open.

## Decision

**A surface may deliver a diagnosis to a human while `blocks/` and `templates/` are empty, provided
every absence it reports names the `validated` artifact that backs it, and provided it never presents
a missing prescription as though one existed.**

## Consequences

| Consequence | Detail |
|---|---|
| The seven checks reach people now | Their entire backing is already `validated`, so nothing is invented by delivering them |
| Every reported absence carries its source | An absence with no `validated` artifact behind it is not a finding and is not reported. This is the whole guard |
| The inventory is stated, not implied | A surface that reports gaps must say what it can and cannot hand back. Today that is zero validated blocks and one `draft` skill, and saying so is not a weakness to hide |
| `draft` does not block delivery | `skills/project-gap-analysis` is `draft` and ships anyway. `draft` withholds citability, never use — the same reading ADR 0016 is held to |
| Running it feeds the thing it lacks | Each run is a candidate gap record, and gap records are the demand signal `blocks/` waits on. The surface produces the evidence for its own missing half |
| The working report never crosses | Unchanged from `skills/project-gap-analysis`: full detail stays with the project's owner, and only a de-identified record may enter this repo (ADR 0009) |
| It forbids the prescriptive shortcut | No block, template or fix may be handed over because a diagnosis found a gap. The demand rule still governs `blocks/`, unamended by this ADR |

## Alternatives

| Rejected | Reason |
|---|---|
| Wait until `blocks/` holds something | Rejected on evidence, not impatience. The strongest demand this repo has ever recorded reached three independent occurrences and produced a skill promotion, not a block. Waiting for the prescriptive layer waits on an output the demand rule does not reliably produce |
| Ship a starter kit of "basic" blocks | `gaps/README.md` names it directly: one analysis plus enthusiasm produces a directory of things that solved one project's problem, described as reusable practice |
| Let anyone write gap records straight into this repo, to scale the demand signal | Hands the unmatchable half of ADR 0009 — a private name written as a bare word — to people who never read the rule, writing into a public repository. `hooks/pre-commit` cannot catch that class, and says so |
| Point the surface at new or scaffolded projects instead of existing ones | Rejected on evidence. All seven checks read an existing agent-practice surface; on an empty repository every check is trivially `absent`. Run 3 chose a mature project for exactly this reason: a project that lacks everything tells you little, because every check fails for the same reason |
| Report absences without naming their backing, to keep the output short | That is the failure `theory/loops/verifier-availability.md` describes, turned outward: a verdict a reader cannot trace is indistinguishable from one nobody checked |
