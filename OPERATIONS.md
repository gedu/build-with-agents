---
id: operations
type: index
targets: [any]
status: validated
verified: 2026-08-07
sources: ["AGENTS.md", "MAP.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0011-rig-produces-evidence-not-truth.md", "theory/agents/capability-load-cost.md"]
---

# OPERATIONS.md — what to run, and when

`MAP.md` answers *where does knowledge live*. This file answers *what can I execute, and at what moment*.

Written for an agent. Read it when you are about to change something, verify something, or measure
something — not on arrival.

## What this file deliberately does not contain

**Flags.** Every command below has `--help`, and that is the authority for its interface. Copying flag
lists here would create a hand-maintained table that duplicates a source of truth and drifts from it
silently — the failure `AGENTS.md` forbids and the one `decisions/0004` records this repo committing.

What `--help` cannot tell you is **when** to run something and **what its output obliges you to do**.
That is the whole content of this file.

It also lives outside `AGENTS.md` on purpose. Per `theory/agents/capability-load-cost.md`, a procedure
only some sessions need belongs behind a read-on-demand pointer rather than in an always-resident file.
`AGENTS.md` carries the pointer; the procedure is here.

## Decision table — start here

| You are about to… | Run | Non-negotiable? |
|---|---|---|
| Work in a fresh clone | `./setup.sh --<tool>` | Yes. Nothing tool-specific is committed |
| Get the redaction gate installed | `./setup.sh --hooks` | Yes. Without it the gate does not fire |
| Commit anything | nothing — the hook fires by itself | Yes, once installed |
| Check the whole tree, not just a diff | `./hooks/pre-commit --all` | Before any push, and after any bulk edit |
| Change shell | `bash -n <file>` | Yes. There is no test runner here |
| Change Python | `python3 -m py_compile <file>` | Yes, same reason |
| Produce a measurement | `./rig/run.sh` → `rig/derive.py` → `rig/report.py` | In that order. See below |
| Commit reviewed work | see *Review lifecycle* | Currently blocked upstream. See below |

## The gates, and what their exits oblige

### `./hooks/pre-commit`

The redaction gate (ADR 0009). Runs automatically on commit once `./setup.sh --hooks` has linked it.

| Exit | Meaning | What you must do |
|---|---|---|
| 0 | Clean | Proceed |
| 1 | A finding | Fix it. Never `--no-verify` past a finding |
| 2 | **Could not run** | **Treat as a failure, not a pass.** Something broke — a bad pattern, a locale problem, an unreadable file. Diagnose before committing |

Exit 2 exists because a check that cannot run is not a check. That distinction is the subject of
`theory/loops/verifier-availability.md`, and this gate shipped with a fail-open on its first day —
see `journal/2026-08-05-redaction-gate-and-2478-on-224.md`.

**What it does not catch**, and you must therefore catch yourself: a private project or client name
written as a bare word. No pattern can tell a public repository name from a client's. A clean run is not
evidence about that class — ask before writing a shared source's name, per `AGENTS.md`.

### `bash -n` and `python3 -m py_compile`

This project has **no test runner** (`sdd/testing-capabilities.md`). These two plus running the thing and
reading its real output are the entire verification surface. A claim that something works must be backed
by output you actually produced.

## Producing a measurement

Three programs, one direction, no shared state but files. ADR 0010 governs what a measurement may vary;
ADR 0011 governs what its output may claim.

```
./rig/run.sh <task_id> <arm> <iteration>   # ONE run. Guards, launches, persists. Parses nothing
python3 rig/derive.py                      # ALL run dirs -> rows. Total function, rebuilds every time
python3 rig/report.py                      # rows -> four-cell tables
```

**Order matters and the split is the point.** `run.sh` never decides an outcome, so a checker bug costs a
re-derivation rather than 30 re-runs. `derive.py` is *total* — it rebuilds `runs.jsonl` completely on
every invocation, which is why double-counting is structurally impossible rather than defended against.

| Situation | What it means |
|---|---|
| `run.sh` exits 2 | Could not run. A dirty tree, a missing preimage, a failed prerequisite. Nothing was measured |
| A row is `void` | Environmental, not a result. Excluded and replaced. `void_reason` says why |
| A row is `state: complete` | It produced numbers, pass or fail. Both are results |
| `report.py` names excluded slots | Read them. A slot voided in one arm removes its pair from the comparison |

**Before believing any number**, confirm `derive.py` reproduces byte-identically across two runs. That is
the cheapest available proof that the deriver is a function of the run directories and nothing else.

**Before quoting any number**, read ADR 0011: rig output is **evidence, not truth**. A figure becomes
citable only by promotion into `theory/` carrying its scope, its spread and the honesty contract. Never
quote a row.

## Review lifecycle — currently blocked, and this is the state to check first

`gentle-ai` provides the bounded review whose receipt the delivery gates validate. **Do not explore its
commands.** Bootstrap once and execute only the exact transition it returns:

```
gentle-ai review status --cwd . --contract gentle-ai.review-integration/v1 --next-transition
```

**Known blocker.** `finalize --validation` refuses evidence that `status` reports as accepted — upstream
[#2478](https://github.com/Gentleman-Programming/gentle-ai/issues/2478), open, and confirmed by this repo
to reproduce on 2.2.4. No receipt is producible, so commits currently ship as documented bypasses. Full
reproduction in `journal/2026-08-05-redaction-gate-and-2478-on-224.md`.

Two facts that cost time before they were written down:

- **A fresh `review start` reaches the defect; replaying an abandoned lineage does not** — it stops
  earlier at `recovery_authorization_required`. To test a correction-stage defect, open a new lineage.
- **An abandoned lineage in `reviewing` is not a blocker.** Re-run the bootstrap: unrelated content
  returns `applicability: unrelated`. A previous session lost two days to reading it as a blocker.

`gga` is a different tool for a different job — AI code review at pre-commit. Its verdict is
probabilistic, which is the wrong layer for redaction. Keep the two hooks separate; `setup.sh` warns and
skips rather than replacing an existing hook.

## Prerequisites, and where they do and do not apply

| Tool | Needed for | Notes |
|---|---|---|
| `bash`, `git` | Everything | — |
| `python3` (stdlib only) | `rig/derive.py`, `rig/report.py` | **Rig-only.** `hooks/pre-commit` deliberately does not depend on it — it must run on a machine that installed nothing |
| `claude` CLI | `rig/run.sh` | Subscription auth is enough. No API key. `--bare` is not used in v1 |
| `gentle-ai` | Review lifecycle | Stay on 2.2.4 — upstream's own note says to revert to it while rc.2 is prepared |

## When something is wrong

- **A gate reports exit 2** — it could not run. That is not a pass and never a reason to proceed.
- **A number surprises you** — check what produced it before believing it. A fixture that reverts the
  code under test and then reports every fix as failed is a real incident in this repo, not a
  hypothetical; see `theory/loops/reading-and-running-find-different-defects.md`.
- **A sub-agent reports success** — verify the artifacts, paths and effects. A report is a claim.
- **A flag behaves unlike its description** — believe the run. Reading `--help` produced three confident
  wrong conclusions in this project's short history, and each was corrected by two cheap probes.
