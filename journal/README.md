---
id: journal/index
type: index
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---

# journal/

Dated conversations, brainstorms and thinking-out-loud. **Raw material.**

One entry: `2026-08-04-repo-skeleton-design.md`, the design conversation behind ADRs 0001–0007.

## Citability — authority vs provenance

| Use | Allowed | Detail |
|---|---|---|
| As **authority** | **Never** | Nothing here may justify a decision on the grounds that a journal entry says so. A brainstorm contains options that sounded good and were then discarded. |
| As **provenance** | **Yes** | Valid evidence of *where* a decision came from. Belongs in the `sources` of the doc that supersedes it. |

Citing a law versus citing a witness. See ADR 0007.

To make a journal insight usable as truth: promote it to `theory/` with sources, or to
`decisions/` as an ADR. Until then it does not exist as authority.

## Naming

`YYYY-MM-DD-slug.md`. Multiple entries per day are fine; keep the slug distinct.

## Belongs here / does NOT

- Yes: transcript-like notes, open questions, half-formed ideas, dead ends, the path that
  led to a decision so the ADR can point at it.
- No: anything another file is meant to rely on; secrets, credentials, or
  client-confidential material.

## Frontmatter contract

```yaml
---
id: journal/YYYY-MM-DD-<slug>
type: journal
targets: [react, react-native, any]
status: draft
verified: 2026-08-04
sources: []
---
```

Journal entries stay `status: draft` permanently. `draft` here means "raw", not "in
progress" — promotion happens by writing a different file elsewhere, not by flipping this
field.
