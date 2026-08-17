---
id: rig/index
type: index
targets: [any]
status: draft
verified: 2026-08-13
sources: ["decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "decisions/0014-a-fixtures-runtime-is-substrate-not-this-repos-runner.md", "sdd/measurement-rig/design.md", "sdd/failure-flood-triage/design.md"]
---

# rig/

An instrument, not a truth. `rig/` holds this repo's own measurement harness: a runner, an
analyser, and the frozen fixtures they run against. See `decisions/0010` for why this repo
measures its own harness instead of trusting a vendor's number, and `decisions/0011` for the
citability split below.

## What is here, and what each part is allowed to say

| What | Citable as truth? | Why |
|---|---|---|
| Code — `run.sh`, `derive.py`, `report.py`, checkers, fixtures | **Yes**, like `setup.sh` and `hooks/` | Committed, reviewable, and its behaviour is the contract everything else rests on |
| Output — rows in `results/*/runs.jsonl`, aggregate tables | **No — evidence only** | One machine, one model, one configuration. A row is an observation, not a conclusion |
| Raw captures — per-run `stream.jsonl`, `status.json` under `runs/` | **No, and not committed** | Every `init` event carries an absolute home path; gitignored by construction |

**A number becomes citable only by being promoted into `theory/` with its scope, its N and
spread, its anomaly count, and the honesty contract attached.** Cite the promotion, never a raw
row from this directory — the same rule this repo already applies to `research/` ("cite the
verdict, never the link") and to `journal/` under ADR 0002.

## Layout

```
rig/
├── run.sh                          # guards, launches, persists ONE run — nothing else
├── run-pipeline.sh                 # sibling runner: multi-step arms (failure-flood-triage)
├── derive.py                       # total, deterministic: run dirs -> one committed row each
├── report.py                       # aggregates rows into per-experiment tables
├── surfaces/                       # committed preimages of the expected visible tool set
├── fixtures/<experiment>/<version>/ # frozen, hash-frozen (MANIFEST.sha256), additively versioned
├── results/<experiment>/runs.jsonl  # committed, append-only, rebuilt by derive.py
└── runs/                            # gitignored — raw per-run captures, machine-local only
```

## The experiment axis is real, and it is dispatched, not forked

Two experiments live here now, not one: `tool-surface-v1` (arms `broad`/`scoped`, `run.sh`) and
`failure-flood-v1` (arms `monolithic`/`pipeline`, the sibling `run-pipeline.sh`). `derive.py` and
`report.py` both take an `--experiment <name>` flag (default `tool-surface-v1`, for backward
compatibility) and dispatch to that experiment's own row-builder and table set — one file each, not a
copy-pasted sibling per experiment (`sdd/failure-flood-triage/design.md` sec 6: "the deriver is total"
carries over unchanged; the dispatcher is what is new).

**The two-schema rule.** Each experiment owns its own row shape — `tool-surface-v1`'s row
(`schema_version` 3, cells `proper`/`improper-success`/`clean-failure`/`failure`) and
`failure-flood-v1`'s row (`schema_version` 1, `green`/`partial`/`no-progress`/`regressed` plus
`peak_occupancy_tokens`/`cumulative_occupancy_tokens`/`causes_claimed`/`causes_correct`) are **not**
unified into one superset schema. A field that exists for one experiment and not the other stays absent
from the other's rows rather than padded with a placeholder — the same "no field tooling does not read"
discipline `AGENTS.md`'s frontmatter contract already applies to documents, applied here to `runs.jsonl`
rows. Adding a third experiment means adding a third row-builder and a third report function, never
widening the first two.

## Does NOT belong here

- A conclusion. That gets promoted to `theory/` once a number exists, per `decisions/0011`.
- An edit to a frozen fixture version. A change is a new `vN+1/` directory; the old one is
  never touched (design.md, Decision 4).

## Prerequisites

`python3` (stdlib only) and a GNU-compatible `timeout` are rig-only prerequisites. The
portability contract in `hooks/pre-commit` — that it runs on a machine which installed
nothing — explicitly does not extend here (`decisions/0011`, the boundary section).

**The fixture-runtime boundary.** `failure-flood-v1`'s fixtures (`fixtures/failure-flood/v1/`,
`v2/`) carry their own `node`/`npm`/Jest runtime, installed on demand per run into a machine-local
`mktemp` directory. `decisions/0014` (ratified for this cycle's PR1) settles that this does **not**
reverse `decisions/0013`'s repo-level "no test runner" rule: the fixture's runtime is substrate the rig
measures, never this repo's own test runner. The boundary is explicit — nothing outside `rig/fixtures/`
gains a `node_modules/` dependency, and no repo-level command starts depending on Jest.
