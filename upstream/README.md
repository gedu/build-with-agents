---
id: upstream/index
type: index
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---

# upstream/

Space to exercise `gentle-ai`, `engram` and `gga`, and to stage bug reports before they are
filed upstream. Experiments, not truth.

`gentle-ai/` — 1 staged report, none filed yet. See `gentle-ai/README.md` for the reporting
protocol and the manual/automatic split.

## Layout

`upstream/<tool>/` per tool, e.g. `upstream/gentle-ai/`, `upstream/engram/`, `upstream/gga/`.
Create a tool directory when the first experiment for it exists, not before.

## Required shape for a staged report

| Section | Content |
|---------|---------|
| Tool + version | Exact version or commit exercised |
| Expected | What the documented behavior says should happen |
| Actual | What happened, verbatim output |
| Reproduction | Minimal, deterministic steps |
| Environment | OS, shell, runtime versions |
| Filed | Upstream issue URL, or `not filed yet` |

## Does NOT belong here

- Fixes for those tools — file them upstream, do not fork behavior here.
- Credentials, tokens, or private paths in pasted output. Redact before committing.

## Frontmatter contract

```yaml
---
id: upstream/<tool>/<slug>
type: research
targets: [any]
status: draft
verified: 2026-08-04
sources: []
---
```

`type: research` because a bug report is a claim plus evidence. `sources` holds the upstream
issue URL once filed.
