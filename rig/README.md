---
id: rig/index
type: index
targets: [any]
status: draft
verified: 2026-08-06
sources: ["decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0011-rig-produces-evidence-not-truth.md", "sdd/measurement-rig/design.md"]
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
├── derive.py                       # total, deterministic: run dirs -> one committed row each
├── report.py                       # aggregates rows into the four-cell tables
├── surfaces/                       # committed preimages of the expected visible tool set
├── fixtures/<experiment>/<version>/ # frozen, hash-frozen (MANIFEST.sha256), additively versioned
├── results/<experiment>/runs.jsonl  # committed, append-only, rebuilt by derive.py
└── runs/                            # gitignored — raw per-run captures, machine-local only
```

## Does NOT belong here

- A conclusion. That gets promoted to `theory/` once a number exists, per `decisions/0011`.
- An edit to a frozen fixture version. A change is a new `vN+1/` directory; the old one is
  never touched (design.md, Decision 4).

## Prerequisites

`python3` (stdlib only) and a GNU-compatible `timeout` are rig-only prerequisites. The
portability contract in `hooks/pre-commit` — that it runs on a machine which installed
nothing — explicitly does not extend here (`decisions/0011`, the boundary section).
