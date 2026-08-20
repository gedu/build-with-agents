---
id: gaps/index
type: index
targets: [any]
status: draft
verified: 2026-08-20
sources: ["AGENTS.md", "MAP.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0012-a-hypothesis-is-never-citable.md", "skills/project-gap-analysis/SKILL.md"]
---

# gaps/

Gap analyses of existing projects, measured against this repo's validated practices. Goal (c) in
`AGENTS.md`, and the demand signal that decides what `blocks/` holds.

Produced by `skills/project-gap-analysis`. One file per analysis, `NNNN-<slug>.md`.

Three analyses recorded. One demand has reached three occurrences and resolved to an existing draft skill rather than to a new block; a second is at one. Nothing has been built here yet.

## No project is identifiable here

Every file in this directory was written by reading a project that is not this one, and this
repository is public. **No gap record may carry a repository, product, client, team, service or host
name, or any path outside this repo.** A project is described by its class — stack, rough size, what
it is for — and never by its identity.

### The one exception: a public source is named

**This paragraph was missing for eight days and this file said the opposite of what the directory
did.** `skills/project-gap-analysis` grew the exception during its run 2 and `MAP.md` already
described this directory as *"private projects de-identified, public sources named"*, while `0002`
sat here naming a public repository — against the rule stated directly above it. Found by run 3,
which could not write a named record under a README that forbade one. Recorded rather than quietly
fixed, because the shape is the point: a rule updated in one file and not in the file that states it
is a rule that now argues with itself, and the second reader is the one who pays.

A public open-source repository is **named**, exactly as `research/` names its sources.
De-identifying one protects nothing — the class description identifies it to anyone who cares — and
it makes every claim in the record unverifiable to a reader who could otherwise open the repository
and check it.

The limit is narrow, and `skills/project-gap-analysis` carries it in full: public means *the practice
being analysed is already published*. Not that the company is well known, not that someone made the
code available to you, and not that a repository is public while the finding concerns something it
did not publish. When in doubt the default rule above wins, because a wrong call is not correctable
after a push.

`hooks/pre-commit` does not protect this directory. It blocks absolute home paths and known secret
shapes; a private name written as a bare word is exactly the class ADR 0009 records as
unpattern-matchable. A clean gate is not evidence about the thing this directory is most likely to
leak.

The stripping happens **while writing**, not in a later review pass. The skill's procedure separates
a full-detail working report, which stays outside this repo forever, from the record committed here.

## Citability

**Evidence only, and only in aggregate.** Same rule as `rig/` output under ADR 0011, for the same
reason: one observation is not a law.

| Claim | Backed by a gap record? |
|---|---|
| "This project lacked a verifier-availability check" | Yes. That is what the record observed |
| "Projects generally lack verifier-availability checks" | **No.** One record is one project |
| "We should build a block for X" | **No** — see the demand rule below |

A single record never enters a `theory/` file's `sources` as support for a general claim. It may be
cited as one observation, labelled as one.

## The demand rule

**A block is built when the same demand appears in at least two independent gap records** — different
projects, different owners, analysed separately. Until then the demand is recorded and waits.

One analysis plus enthusiasm produces a `blocks/` directory full of things that solved one project's
problem and are described as reusable practice. That is inventing knowledge with extra steps, which
is what `AGENTS.md`'s no-invented-knowledge rule exists to stop.

Waiting is not passivity. A recorded demand with one occurrence is a standing question that the next
analysis can answer, which is the same mechanism `hypotheses/` uses.

## Does NOT belong here

- Advice for the analysed project — that is the working report, and it stays with its owner.
- A practice conclusion drawn from one project — that is a `hypotheses/` entry at best.
- Anything a reader could use to identify the project.

## Frontmatter contract

Repo schema from `AGENTS.md`, with `type: research` — the same choice `hypotheses/` made, so no new
type is introduced:

```yaml
---
id: gaps/NNNN-<slug>
type: research
targets: [react, react-native, any]
status: validated
verified: 2026-08-12
sources: []
---
```

`status: validated` means the analysis was completed and de-identified, not that its demand is
settled. `sources` carries the `theory/` files whose checks were run.
