---
id: decisions/0012-a-hypothesis-is-never-citable
type: decision
targets: [any]
status: validated
verified: 2026-08-07
sources: ["decisions/0002-journal-is-raw-material-not-citable.md", "decisions/0007-journal-is-provenance-not-authority.md", "decisions/0011-rig-produces-evidence-not-truth.md", "skills/source-verdict/SKILL.md", "sdd/measurement-rig/spec.md"]
---

# 0012 — A hypothesis is never citable, and that is what makes pre-registration work

## Context

This repo generates hypotheses faster than it can test them, and until now they had nowhere to live.
`theory/` holds validated claims, `research/` holds adjudicated sources, `journal/` holds provenance. A
falsifiable statement with a declared test and no result yet is none of those, so they ended up
scattered inside "what would sharpen it" sections — real, useful, and impossible to enumerate.

The immediate trigger is concrete. The first real run pair of the measurement rig showed both arms
calling **identical tools** while their answers differed in precision. That raises an alternative to the
claim under test: perhaps a broad surface does not degrade *tool selection* at all, but degrades *output
quality* generally. If that alternative is written down only after tier 3 runs, the choice of which
channel to report becomes a choice made with the data already visible — the exact fault this repo
refused a vendor's number over.

Ratified by the operator on 2026-08-07.

## Decision

**A hypothesis carries zero citability. Not "evidence only" like `research/` and `rig/` — zero.**
Nothing may cite it: not a `theory/` file's `sources`, not an ADR's justification, not a commit message
arguing a design.

Two reasons, and the second is the one specific to hypotheses.

### It is textually indistinguishable from a finding

*"A broad tool surface degrades output quality through context dilution"* reads exactly like a line from
`theory/`. The only thing separating them is a status field, and status fields are not read by someone
quoting a sentence.

This is ADR 0002's rationale — *"a rejected idea would eventually be quoted as a settled decision"* —
with more force, because a hypothesis is **written to look like a finding**. Precision and falsifiability
are what make it useful; they are also what make it quotable by accident.

### If it were citable, pre-registration would stop working

This is the load-bearing reason and it does not apply to `journal/` or `research/`.

The entire value of writing a hypothesis **before** the experiment is that it **constrains what may be
claimed afterwards**. If the written statement itself carried any weight, writing it would become a way
to **manufacture** weight: credit for the claim without running the test. And the failure scales —
write ten hypotheses, run one, and nine remain in the repo reading like knowledge.

So the citability of a hypothesis must be **exactly zero**. Any other value turns pre-registration into
a laundering channel, which is worse than not pre-registering at all, because it produces the appearance
of rigour.

## Consequences

| Consequence | Detail |
|---|---|
| `status` is never `validated` | It is `draft` while open, or `rejected` once refuted. There is no third state |
| Resolution is a **new artifact**, not a status change | A supported hypothesis does not get promoted in place. A `theory/` file is written on the evidence, and the hypothesis records where it resolved |
| The `theory/` file cites the **measurement**, never the prediction | It must stand on its own evidence rather than inherit credibility from having been guessed correctly |
| A falsification condition is **mandatory content** | Without one it is an opinion, and `skills/source-verdict` test 1 says a position can be neither supported nor refuted. A hypothesis with no stated test does not belong in the area |
| A refuted hypothesis is **kept**, never deleted | Same rule as a `refuted` source. The refutation is the value, and deleting it invites re-importing the idea in six months |
| A correct hypothesis earns **no retroactive credit** in the citation graph | Uncomfortable and deliberate. "We predicted this" is precisely how a prediction becomes evidence for itself |

## Alternatives

| Rejected | Reason |
|---|---|
| Keep hypotheses in `theory/` as `status: draft` | Puts an untested claim in the one directory `AGENTS.md` marks citable when validated, one field away from being read as truth. The field is not what a reader quotes |
| Keep them in `journal/` | Journal is dated provenance of what was discussed. A hypothesis is a standing commitment with a test attached, and it must be enumerable and resolvable — neither of which a dated brainstorm supports |
| Make them citable "as evidence", like `research/` verdicts | A `research/` verdict is citable because **someone did the adjudication**. A hypothesis is defined by adjudication *not having happened*. There is nothing to cite |
| Leave them distributed in "what would sharpen it" sections | The status quo. They are real and useful there and cannot be listed, compared, or noticed when one is answered by an unrelated run |
