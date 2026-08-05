---
id: decisions/0004-mandatory-frontmatter-as-query-interface
type: decision
targets: [any]
status: validated
verified: 2026-08-05
sources: ["journal/2026-08-04-repo-skeleton-design.md"]
---

# 0004 — Mandatory frontmatter on every content file, as a query interface

## Context

The point is not tidiness. It is that an AI can answer *"give me validated blocks for
react-native"* in one query instead of reading the whole repo. A repo with good folders but
no metadata still forces blind grep.

Two failures observed in a private repository outside this one shape the rules below — the same
repository ADR 0001 cites, and for the same reason not named here: its hand-maintained skill
tables went stale, and its own `skill-creator` template
omitted the very fields its generator depends on (`metadata.scope`, `metadata.auto_invoke`),
so skills written from that template were silently skipped.

## Decision

Every content file carries mandatory frontmatter: `id`, `type`, `targets`, `status`,
`verified`, `sources`.

## Consequences

| Consequence | Detail |
|---|---|
| Frontmatter is the query interface | Fields exist to serve queries, not decoration. Do not add fields tooling does not read. |
| **Every table in this repo is either generated or does not exist** | Never hand-maintain a table duplicating data that lives in frontmatter. Prowler's hand-maintained skill tables went stale. |
| **A schema and its documentation are one artifact** | Documented fields and the fields tooling reads change together, in the same commit. Prowler's `skill-creator` template omitted fields its generator required, and the resulting skills were silently skipped. |
| Every file pays a small tax | Six fields, including README index files. |

## Alternatives

| Rejected | Reason |
|---|---|
| Good folder structure, no metadata | Still forces blind grep; no query can answer "validated blocks for react-native". |
| A hand-maintained index table instead of frontmatter | Prowler proves it goes stale. |
