---
id: decisions/0016-open-work-is-enumerated-from-structure
type: decision
targets: [any]
status: draft
verified: 2026-08-19
sources: ["journal/2026-08-19-what-open-work-actually-looks-like.md", "AGENTS.md", "MAP.md", "OPERATIONS.md", "check.sh", "BACKLOG.md", "decisions/0004-mandatory-frontmatter-as-query-interface.md", "decisions/0012-a-hypothesis-is-never-citable.md", "decisions/0013-a-committed-executable-carries-its-own-test.md"]
---

# 0016 — Open work is enumerated from structure, and the enumerator reports its own coverage

**Not ratified.** Implemented as `open-work.sh` and used, but the operator has not ratified it.
Same posture as `0014`, and for the same reason: an ADR that says "this is how we find open work"
becomes citable the moment it is `validated`, and it should earn that by being used first.

## Context

The standing problem is *"I don't know what is open"* — enumeration, not ranking. `AGENTS.md`
already forbids the obvious answer: *"Stale hand-written indexes are worse than no index"* and
*"tables are generated or absent"*. `MAP.md` closes with the same rule and names itself the single
exception. So the index is generated or it does not exist.

The question is what it reads. A design note written on 2026-08-18 proposed keying it on
`## What is not settled` sections, described as the de facto convention across `skills/`, `sdd/`,
`upstream/` and `journal/`. Counted on 2026-08-19, that heading exists in **two files, both in
`journal/`**. A generator built on it would have printed a two-item index and carried the authority
of being generated while doing it.

That is the failure mode worth naming, because it is *not* the stale-index failure `AGENTS.md`
already covers. A stale hand-written table is visibly hand-written and a reader discounts it. A
generated index is read as complete by construction, so a generator with a thin input is more
dangerous than the table it replaced, not less.

The second proposed input, `status: draft`, was already suspected and turned out to be worse than
suspected: 57 of 103 content files. A signal matching more than half the repository ranks nothing.

Provenance: `journal/2026-08-19-what-open-work-actually-looks-like.md`, which carries both counts
with the commands that produced them.

## Decision

**Open work is enumerated from structure — directory membership and frontmatter fields — never from
a prose convention alone. The enumerator prints its own coverage alongside its findings, and a
source that does not exist prints `absent`, never `0`.**

Implemented as `./open-work.sh`: POSIX `sh`, output to stdout only, exit 0 or exit 2, carrying its
own `--self-test` per ADR 0013.

### Structure first, because structure is already enforced

Five of the six sources are a directory listing or a frontmatter field, and `check.sh` already
verifies the frontmatter schema on every content file. The index therefore inherits a checked input
rather than introducing an unchecked one — the query interface ADR 0004 built the schema for, used
for the query it was built for.

| Source | Kind | Why it means "open" |
|---|---|---|
| `BACKLOG.md` `###` entries | prose, structured | Its own contract: every entry carries a named unblock condition |
| `hypotheses/` | directory | A declared test with no result. Zero citability, ADR 0012 |
| `gaps/` | directory | Demand below the two-occurrence threshold that would build something |
| `decisions/` with `status: draft` | frontmatter | Decided, not ratified |
| `sdd/` outside `sdd/archive/` | directory | A cycle in flight; archiving is what closes it |
| `## What is not settled` | prose | Declared unsettled, wherever someone wrote it |

The prose convention stays — as the *smallest* input rather than the foundation. Enumerating it is
also the cheapest way to make writing more of them worth doing.

### Coverage is part of the output, not a footnote

The generator prints how many files each source matched and how many content files it scanned. This
is the only thing that would have caught the 2026-08-18 error from inside the output: a marker
covering two files reads as a two-file marker instead of as the state of the repository.

`hooks/commit-msg --range` already established the narrower half of this rule — it prints the number
of messages it scanned *including zero*, because an empty range and a clean range are otherwise
indistinguishable. `absent` versus `0` is the same distinction one level up.

### It reports, so it does not judge

Exit 0 when the index was produced, exit 2 when it could not run. **No exit 1.** Open work is not a
violation, and a repository with three open hypotheses is a healthy repository.

## Consequences

| Consequence | Detail |
|---|---|
| `check.sh` is untouched | Its contract stays one question with one meaning per exit code. A `--open-work` flag would have made exit 1 mean either "this repo broke its rules" or "there is work to do", and `OPERATIONS.md` maps commands to moments — these are different moments |
| Nothing is written to disk | Stdout only. No generated file to gitignore, no managed block for `setup.sh` to own, nothing that can be stale. A redirect is the operator's and this script will not refresh it |
| `BACKLOG.md` keeps its job | It holds authored reasoning — why a thing is blocked and what exactly unblocks it. No generator synthesises that. The index prints its titles and unblock conditions and never restates the reasoning: the index points, the source states |
| A new convention will not announce itself | A seventh source appearing later is invisible until someone adds it. The COVERAGE block is the mitigation and it is a weak one — it makes a *thinning* source visible, not a *missing* one |
| Prose quality is unchecked | The index reports that a file declares itself unsettled, never whether the declaration is any good. Same limit `check.sh` accepts on `ASK.md` entries, and no checker settles it |
| The index can be wrong the same way | If a source directory is emptied by mistake, this prints `absent` and keeps going. `absent` is loud on purpose, but it is still a line of output and not a failure |

## Alternatives

| Rejected | Reason |
|---|---|
| A flag on `check.sh` | Two contracts in one executable. Its exit 1 already means "this repo does not match its own rules"; open work is not that, and overloading it makes both answers less readable |
| Key the index on `## What is not settled` | The premise was measured and is false: two files, both `journal/`. It stays as one input of six |
| Key the index on `status: draft` | 57 of 103 content files. Reported as a number under COVERAGE, never as an entry |
| A hand-written roadmap | Forbidden by `AGENTS.md`, and the repo has its own evidence: `skills/context-checkpoint` asked three separate runs to record their results and got zero. A list depending on somebody remembering has already failed here |
| Rank the entries by priority | The stated problem is enumeration. A priority layer is a second thing to keep honest and nobody has asked for it yet; it is added if the index shows it is needed, per the same two-occurrence discipline `gaps/` applies |
| Write the index to a gitignored file | Trades a stale committed table for a stale uncommitted one, and buys a managed-block entry for `setup.sh` to own. Stdout has neither problem |
