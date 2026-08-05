---
id: journal/2026-08-05-gentle-ai-upgrade-handoff
type: journal
targets: [any]
status: draft
verified: 2026-08-05
sources: ["upstream/gentle-ai/0001-correction-acceptance-blocks-receipt.md", "journal/2026-08-04-repo-skeleton-design.md"]
---

# 2026-08-05 — state before upgrading gentle-ai

Paused deliberately: a new `gentle-ai` release may fix the RDD/review-lifecycle defects that
blocked the first commit. Everything below is the state at the pause, so work resumes without
re-deriving it. Journal, so provenance — not authority.

## Versions at the pause

| Component | Version |
|-----------|---------|
| `gentle-ai` | 2.2.2 (Homebrew) |
| `gga` wrapper | v2.10.1 |

These two are separate and drift apart. The upstream Bug Report form asks for "Gentle AI
Version" and the field tells you to run `gga version`, which reports the **wrapper**. A review
defect belongs to the `gentle-ai` binary version. Report both.

## Repository state

Nothing committed. `main` sits on the remote's `d3511bb` "Initial commit" (LICENSE only),
14 untracked top-level paths, index clean, `origin` →
`github.com/gedu/build-with-agents`.

Work applied to the working tree but **not committed**:

| Change | Why |
|--------|-----|
| `AGENTS.md` frontmatter added; `type: index` definition widened | Blocking review finding R2-001 — the file mandating "no exceptions" was the only file without frontmatter |
| `MAP.md` promoted `draft` → `validated` with real sources | Blocking review finding R2-002 — claimed citability while `draft` with empty sources |
| `setup.sh` — `ln -sfn` guarded, `mv` guarded + temp cleanup, `sync_gitignore \|\| :` at the call site | Two resilience findings; 316 → 333 lines |
| `upstream/gentle-ai/` created — report 0001 + reporting protocol | Stage the defect that blocked delivery |
| `upstream/README.md`, `MAP.md` index rows | Keep the one hand-maintained index honest |

## Where the review lifecycle stopped

Lineage `review-f0f10534f4457aa3`, tier `high`, correction budget 200. Four 4R lenses ran and
were admitted; six findings; the two blocking ones fixed inside a 15-line correction; a scoped
validator passed both `original_criteria` and `correction_regression`; evidence captured with
`outcome: passed`.

Then `finalize --validation` refused with `compact correction acceptance requires captured
repository verification evidence` — for evidence that `status` reports as accepted and that
`capture-evidence` keeps re-accepting. Six flag permutations, same refusal. No receipt exists,
so every lifecycle gate fails closed. Full detail in
`upstream/gentle-ai/0001-correction-acceptance-blocks-receipt.md`.

The `setup.sh` fix moved the candidate afterwards, so that lineage is spent regardless: those
findings were never in the correction's eligible scope. A fresh `review start` over the new
content is required either way.

## Open item found while writing this

`upstream/gentle-ai/0001-…md` carries `status: ready-to-file`. `AGENTS.md` defines the enum as
`draft | validated | rejected`, so that value is outside it — the same class of defect as
R2-001 and R2-002: a file contradicting the repo's own schema.

`AGENTS.md` also states that schema and doc are one artifact, so changing what `status` accepts
means changing `AGENTS.md` in the same commit. Two coherent resolutions, unresolved on purpose
because it is a schema decision:

1. Add `ready-to-file` to the enum in `AGENTS.md` and document what it means — a staged artifact
   that is verified but whose truth is external and still pending.
2. Use `status: draft` and track filing readiness in the report body and the `upstream/gentle-ai/`
   index table, which already has a `Filed` column.

Left as-is; not silently "fixed" either way.

## Open follow-ups, not blockers

- `setup.sh` has no committed test harness. The differential mocks that proved the `ln`/`mv`
  fixes lived in scratchpad and were deleted. Where tests live in this repo is an ADR-shaped
  decision.
- `decisions/0001` lines 7 and 17, and `decisions/0004` lines 7 and 18, put an absolute
  machine-local path in `sources`, which `AGENTS.md` defines as URLs or repo-relative paths.
- `: >"$tmp"` in `sync_gitignore` is still unguarded, and with `sync_gitignore || :` now at the
  call site `set -e` no longer covers it. Same pattern as the two fixed calls; no lens flagged it.
- ~~Report 0001 is ready to file but **not filed**.~~ Corrected 2026-08-05: it was filed the
  same evening this entry was drafted, as
  [#2478](https://github.com/Gentleman-Programming/gentle-ai/issues/2478). Filing is a human
  act — see the division of labour in `upstream/gentle-ai/README.md`.

## Plan agreed for after the upgrade

Re-verify the defect against the new version first, because the answer changes what happens next.

1. Check both versions; confirm the release notes actually touch review/RDD.
2. Replay the lifecycle on the current content: `review status --next-transition`, then the
   emitted `review start`, four lenses, capture, finalize.
3. **If the defect is fixed:** carry the review through to a real receipt and commit *through*
   the gate. Report 0001 gets updated with the fixed-in version and becomes either a
   confirmation note or a closed-before-filing record.
4. **If it still reproduces:** file report 0001 with the version bumped, then commit with the
   gate bypassed on purpose, documented in a journal entry.
5. Either way: initial commit of the scaffold plus the `setup.sh` fixes, then push to
   `origin/main`.

The two `setup.sh` fixes and the two blocking-finding fixes stand on their own. They were
verified empirically against throwaway mocks and by an independent validator, not by the
tool that is broken.
