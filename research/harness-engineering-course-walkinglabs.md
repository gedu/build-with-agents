---
id: research/harness-engineering-course-walkinglabs
type: research
targets: [any]
status: validated
verified: 2026-08-05
sources: ["https://walkinglabs.github.io/learn-harness-engineering/es/"]
---

# Learn Harness Engineering — walkinglabs

## Claim

Programming agents are made reliable by designing the **system around** the model rather than by
seeking a smarter model: a "closed-loop work system". Delivered as 14 lecture modules plus guided
projects and a template library, covering explicit rules and boundaries, context maintenance across
long multi-session tasks, preventing premature declarations of success, full-pipeline verification,
self-reflection, and observable runtime debugging.

## Source

`https://walkinglabs.github.io/learn-harness-engineering/es/` — accessed 2026-08-05.

GitHub Pages course site. Author and affiliation not established from the overview page. Explicitly
aimed at users of existing tools (Claude Code, Codex), **not** at building agent frameworks. No
prerequisites or duration stated.

## Contrast

**No falsifiable claim is made.** This is a curriculum, and a curriculum's assertion is "these are
the right things to learn" — a pedagogical position, not an empirical claim (test 1). There is
nothing here to support or refute. The absence of stated prerequisites and duration also means its
implicit efficacy claim cannot be evaluated.

**Its topic selection, however, can be checked against local evidence — and it holds up well.** Each
module maps onto machinery this repo already runs:

| Course topic | Local implementation |
|---|---|
| Constraining behavior with explicit rules | `AGENTS.md` + ADRs 0001–0007 |
| Context across long multi-session tasks | engram + `skills/context-checkpoint` |
| Preventing premature "victory" | the `gentle-ai` review gate |
| Full-pipeline verification | the bounded review lifecycle |
| Observable runtime debugging | `journal/` entries as run records |

Six-of-six coverage against independently-built local machinery is meaningful about the
curriculum's **scope selection** — it is not inventing topics — while saying nothing about its
teaching quality, which was not evaluated.

Its central thesis, *design the closed loop rather than chase a smarter model*, is consistent with
the direction of `theory/agents/capability-load-cost.md`, though the course is not the evidence for
that file.

## Verdict

**`unverifiable`** — and per `skills/source-verdict`, that is **not a synonym for false**.

There is no measurable claim to adjudicate. Its practical use is as a **curriculum map and gap-
finder**: a checklist of harness concerns against which an existing setup can be audited. Recorded
as useful for that, and explicitly **not** citable as evidence for any claim about agent behavior.

Author credibility unestablished, which under the reputation-is-a-prior rule matters less here than
it would for an empirical claim — there are no numbers to trust or distrust.

## Follow-up

No `theory/` promotion; a curriculum cannot satisfy the sources requirement for a knowledge claim.

Candidate input to the **project AI-readiness checklist** — its six topic areas are a reasonable
first cut at the dimensions such an audit should cover, to be confirmed against local evidence
rather than adopted on the course's authority.
