---
id: research/index
type: index
targets: [any]
status: draft
verified: 2026-08-05
sources: []
---

# research/

Incoming material — links, papers, threads, vendor docs — contrasted against evidence and
closed with a **verdict**. A link with no verdict is an open tab, not research.

Entries are not enumerated here; the directory carries the truth and `MAP.md` carries the count.

## Required shape

| Section | Content |
|---------|---------|
| Claim | What the source asserts, in one sentence |
| Source | URL or file path, plus date accessed |
| Contrast | What other sources or local experiments say |
| Verdict | `supported` / `partially supported` / `refuted` / `unverifiable`, with the reason |
| Follow-up | The `theory/` or `decisions/` file this should become, if any |

## Citability

Cite the **verdict**, never the raw link. A source that ends up `refuted` stays in the
repo as `status: rejected`; deleting it loses the refutation and invites re-importing the
same bad claim later.

## Does NOT belong here

- Unread link dumps; personal notes and brainstorms (`journal/`).
- Conclusions promoted to truth. Once a verdict is settled, write the `theory/` file.

## Frontmatter contract

```yaml
---
id: research/<slug>
type: research
targets: [react, react-native, any]
status: draft
verified: 2026-08-05
sources: []
---
```

`sources` must contain the material under review — it is the point of the file.
