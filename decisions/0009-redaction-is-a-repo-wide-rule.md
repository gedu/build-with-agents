---
id: decisions/0009-redaction-is-a-repo-wide-rule
type: decision
targets: [any]
status: validated
verified: 2026-08-05
sources: ["journal/2026-08-05-first-commit-gate-bypass.md", "journal/2026-08-05-knowledge-base-handoff.md", "theory/loops/verifier-availability.md"]
---

# 0009 — Redaction is a repo-wide rule, not a staged-report rule

## Context

This repository is **public**. Every committed file is a published artifact the moment it is
pushed, and pushing is not reversible in any way that matters — a rewritten history does not
unpublish what was already fetched, mirrored or indexed.

The repo had a redaction rule. It lived in `upstream/gentle-ai/README.md`, it said to redact
absolute paths containing a username, tokens and hostnames before committing, and it established
`<repo>` as the substitution for the repository root. Two problems with it:

- It was **scoped to staged upstream reports**, one directory out of fifteen.
- It lived in `upstream/`, which `AGENTS.md` marks as **not citable**. So the repo's only redaction
  rule sat in the one place a rule carries no authority.

Meanwhile the actual exposure happened somewhere that rule never covered.

**The incident.** `decisions/0001` and `decisions/0004` were committed with an absolute path under a
home directory — containing the machine username and the name of an unrelated private project — in
the `sources` frontmatter of both files and in the body of the journal entry they pointed at. Pushed
publicly. Repaired forward in `bed4dec`, deliberately not by rewriting history, on the reasoning that
the content was already out.

Three properties of that incident are why a note in a README was not enough.

**A rule already existed and did not hold.** `AGENTS.md` defines `sources` as "URLs or repo-relative
file paths". An absolute machine-local path violates that on its face. The rule was in the root
instruction file, in a table, in the same document as the schema it governs — and it was broken by
the two ratified ADRs that define the repo's contract, including the ADR whose entire subject is
frontmatter as a machine-queryable interface. The failure was not ignorance of the rule.

**Nothing was positioned to catch it.** No review lens flagged it. It surfaced later, during an
unrelated bypass write-up, by a human reading frontmatter. That is the state
`theory/loops/verifier-availability.md` ranks as undetectable: a constraint that was only ever a
sentence, reporting nothing and blocking nothing.

**The redaction work itself leaked.** Three times on 2026-08-05 the same string re-entered the repo
while documenting how to keep it out — twice through the mechanism built to catch it. Writing "search
for `<the literal value>`" reintroduces the literal value. This is not carelessness; it is a
structural property of documenting a forbidden string, and no rule that ignores it will survive
contact with its own documentation.

Ratified by the operator on 2026-08-05, resolving the open item recorded in
`journal/2026-08-05-knowledge-base-handoff.md` §4.

## Decision

**Redaction applies to every committed file in this repository, without exception for directory,
type or status.** The rule moves into `AGENTS.md`, where the repo's non-negotiable rules live and
where it is citable.

### Never committed

| Forbidden | Why |
|---|---|
| Absolute paths under a home directory (`/Users/<name>/…`, `/home/<name>/…`, `C:\Users\<name>\…`) | Carries the machine username, and resolves for exactly one reader |
| Names of private repositories, projects or clients | A private repo is equally unauditable named or unnamed, so naming it is exposure for zero gain. **Public sources may be named — see the classification rule below** |
| Tokens, credentials, API keys, session identifiers | Irreversible on publication |
| Hostnames, machine names, internal URLs a reader cannot resolve | Infrastructure detail, useless to a reader, useful to a scanner |

### Substitutions

| Instead of | Write |
|---|---|
| The repository root | `<repo>` |
| A home directory | `~` or `<home>` |
| Another local project | Describe its role. Do not name it |
| A machine-local file cited as evidence | A repo-relative path, a URL, or a journal entry recording what was observed |

That last row is the one with teeth. A citation that resolves on one machine is not evidence — it is
decorative, and `decisions/` is citable as truth unconditionally, so its backing citations must be
openable by a reader who has only this repo.

### Classification is asked for, not inferred

Added on the operator's correction during ratification, because the rule as first drafted was too
blunt to be correct.

**A path does not say whether what it points at is public.** A directory under a home directory may
be a clone of a public repository, a client's private code, or a local scratch copy — three
different handling requirements behind identical-looking paths. An agent has no way to tell them
apart by inspection, and guessing fails in both directions: naming a private client is exposure,
and redacting a public repository destroys a citation a reader could have opened.

Therefore, for any repository, document or path the operator shares from outside this project, the
agent **asks how to refer to it before writing it anywhere** — doc, ADR, journal, commit message or
`sources` field — and never writes the full path regardless of the answer. Outside-the-project and
confirmed public → the name alone. Outside and private or unconfirmed → its role, described. Inside
the project → a project-relative path. The operative rule and its table live in `AGENTS.md`.

The answer is then **recorded and reused**, so the question is asked once and every later document
agrees with the earlier ones.

Note what this concedes: **redaction and citability genuinely conflict here**, and this ADR does not
resolve the conflict by rule. A public source that cannot be named cannot be checked by a reader,
which is a real cost that the blanket version of this rule was quietly paying. Only the operator has
the information to decide, so the decision is routed to the operator rather than to a default.

### The documentation trap, stated as a rule

**Never paste a real value in order to describe how to find it.** Redaction patterns, search
commands and incident write-ups describe the *shape* of the forbidden string and never contain an
instance of it. A file explaining a redaction is the highest-risk file in the repo for reintroducing
what it redacts, because the author is holding the value in mind and has a reason to type it.

### Scope note on names

A bare first name is not covered. The repository owner's identity is already public through the
remote and the commit trailer, so redacting a first name protects nothing while making prose
unreadable. The rule targets **machine paths, private project names, and secrets** — not authorship.

## Which layer enforces this, stated plainly

By `theory/loops/verifier-availability.md`, the test of a rule is not to read it but to ask which
layer implements it. So, for this one:

| Layer | Covers | Status |
|---|---|---|
| Native check (`hooks/pre-commit`) | Absolute home paths, known secret shapes | **Implemented.** Blocks the commit |
| Runtime permission | — | Not applicable. No tool grant expresses "do not write this string" |
| Prompt policy (`AGENTS.md`) | Private names as bare words, classification of shared sources | **Unavoidably prompt policy.** Guides an agent, enforces nothing |

**The split is not a compromise, it is the correct division.** The path class is structural: a path
is either repo-relative or it is not, and a pattern decides that without knowing anything about the
world. The name class is semantic: no pattern can tell a public repository name from a client's, so
it is a judgment that requires the operator. Trying to mechanise the second half is what led through
denylists, hashes and key pairs before the structural framing collapsed the problem — a hash of a
short project name is brute-forced from public repository listings, and it would still have missed
the possessive form that actually leaked.

So the enforcement claim is precise and bounded: **the class that caused the incident is now
gated.** `hooks/pre-commit` fails the commit on an absolute home path or a known secret shape,
verified end-to-end against a real `git commit` that aborted, and against placeholder forms that
correctly pass so this rule remains documentable.

The class that survived the previous audit — a private name written as a bare word — is **not**
gated and cannot be. It is covered by the ask-before-writing rule above, which is prompt policy with
a non-zero failure rate. A clean run of the check is not evidence about that class, and the hook says
so in its own output rather than leaving the reader to infer it.

## Consequences

| Consequence | Detail |
|---|---|
| One rule, one location | Redaction lives in `AGENTS.md` and is citable. The `upstream/` note becomes a local restatement of a repo-wide rule, not the rule itself |
| Machine paths cannot be evidence | Citations must resolve for a reader with only this repo. Where the evidence is genuinely local, a journal entry recording the observation is the citable artifact |
| Incident write-ups get harder to write | Describing a leak without instantiating it takes more words. Accepted — the alternative is the failure that already happened three times in a day |
| The path class is gated, the name class is not | `hooks/pre-commit`, installed by `./setup.sh --hooks`. The asymmetry is stated above instead of being papered over |
| `gga` is not this hook | `gga install` writes an AI-code-review pre-commit hook. Its verdict is probabilistic, which is the wrong layer for redaction. `setup.sh` warns and skips rather than replacing an existing hook |
| The rule found live violations on first application | See below. The inherited "zero matches" claim was a false negative |

## First application, recorded because it falsified an inherited claim

`journal/2026-08-05-knowledge-base-handoff.md` §3 lists, under *verified first-hand*, a tree-wide
search for home paths, the machine username and the private project name returning **zero matches**.
Applying the rule above as a search over all four forbidden categories — rather than over path shapes
alone — returned **three matches**, all in `decisions/0004`, which named the private project in its
consequences and alternatives tables.

The repair in `bed4dec` had removed the *path* and left the *name*, and the verifying search looked
for the path. So the earlier check was correct about what it searched and wrong about what it
concluded, and the conclusion is what got written down.

Two things worth keeping from that, beyond the fix:

- **`decisions/0004` declined to name the repository in its Context section and then named it three
  times in its own tables**, two sections below. A file can state a redaction intent and violate it
  internally, which means "we decided to redact it" is not evidence that it is redacted.
- **A redaction check must enumerate the forbidden categories, not the last incident.** The previous
  search was shaped by the leak that had already been found. That is the general failure: a check
  written from an incident verifies the incident, and reports clean on the category.

Corrected in the same commit that ratified this ADR.

## Alternatives

| Rejected | Reason |
|---|---|
| Widen the `upstream/` note in place | Leaves the repo's redaction rule in a directory `AGENTS.md` declares non-citable. A rule nobody may cite cannot be applied against a disagreement |
| Rely on the existing `sources` format rule | Already tried by accident. It is narrower than the exposure — it constrains one frontmatter field and says nothing about prose, commit messages or journal bodies — and it was violated by the ADRs that define it |
| Write the pre-commit check first and skip the ADR | The check needs a definition of what to forbid, and that definition is this document. Also leaves the WHY unrecorded, so the next contributor reads a grep pattern with no rationale and weakens it |
| Make the repo private | Discards goal (c) in `AGENTS.md`, and the reason to publish is that the practices are meant to be auditable. Redaction is the cost of that, not an argument against it |
| Rewrite history to remove the published path | Already considered and rejected in `bed4dec`. A rewrite does not unpublish what was fetched, and it breaks every reference for a cosmetic gain |
