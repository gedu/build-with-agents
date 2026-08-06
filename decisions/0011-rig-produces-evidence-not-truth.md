---
id: decisions/0011-rig-produces-evidence-not-truth
type: decision
targets: [any]
status: validated
verified: 2026-08-06
sources: ["decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0002-journal-is-raw-material-not-citable.md", "sdd/measurement-rig/design.md", "sdd/measurement-rig/spec.md", "research/README.md"]
---

# 0011 — `rig/` is a new area, and a number it produces is evidence rather than truth

## Context

ADR 0010 committed this repo to producing its own measurements. The design for that harness places it
under a new top-level `rig/`, which means it joins `MAP.md`'s citability table — and that table states,
per area, what a reader is allowed to trust. A new area with no declared citability is the one thing the
table exists to prevent.

The design deferred this question to *"whoever writes the first result"*, and the tasks phase correctly
refused to decide it, flagging it as blocked. Both were right to defer rather than assume. Deciding it
**now** matters for a specific reason: the alternative is deciding whether a number is citable while
holding that number, which is the worst possible moment to be asked.

Ratified by the operator on 2026-08-06.

## Decision

`rig/` is a committed area of this repo, and it contains **three different kinds of thing with three
different citability answers.** Conflating them is the failure this ADR exists to prevent.

| What | Citable as truth? | Why |
|---|---|---|
| The rig's **code** — runner, analyser, checkers, fixtures | **Yes**, like `setup.sh` and `hooks/` | Committed, reviewable, and its behaviour is the contract everything else rests on |
| The rig's **output** — rows in `runs.jsonl`, aggregate tables | **No. Evidence only** | A row is an observation from one machine, one model, one configuration |
| **Raw captures** — per-run `stream.jsonl`, `status.json` | **No, and not committed** | Every `init` event carries an absolute home path. Gitignored by construction |

**The load-bearing rule: a number becomes citable only by being promoted into `theory/` with its scope
and its honesty contract attached.** Cite the promoted claim, never the raw row.

That is deliberately the same shape as the existing rule for `research/` — *"Cite the verdict, never the
raw link"* — and for `journal/` under ADR 0002. This repo already distinguishes material from
authority in two places; the rig is the third, and it gets the same treatment rather than a new one.

### What a promotion must carry

A `theory/` file citing rig output states, in the file: the exact configuration compared, N and the
observed spread, the anomaly count, and the numbered known gaps from the spec's honesty contract. A
figure published without its spread is not a promotion — it is a number with its uncertainty deleted.

### The boundary

`rig/` must not be able to break the repo it lives in. `python3` is a **rig-only** prerequisite: the
portability contract in `hooks/pre-commit` — that it runs on a machine which installed nothing —
explicitly does not extend here. The hook is a gate every contributor runs; the rig is instrumentation
one operator runs.

## Consequences

| Consequence | Detail |
|---|---|
| `MAP.md` gains a `rig/` row | With the three-way split above, not a single verdict |
| Task 9.0 is unblocked | It was blocked on exactly this ruling |
| A result cannot be quoted from `runs.jsonl` | Someone wanting to cite a figure must first write the `theory/` promotion, which forces the scope and the gaps to be stated |
| The honesty contract becomes load-bearing rather than decorative | It is a precondition of citability, not an appendix |
| Raw captures stay local | So a reader cannot audit a specific run from the repo alone. Accepted: the row carries the digests that prove which configuration produced it, and publishing home paths to fix this would be worse |

## Alternatives

| Rejected | Reason |
|---|---|
| A `MAP.md` row and no ADR | Leaves undeclared *under what conditions* a rig number is citable, which is the only part that matters. A row can say "no"; it cannot say "no, until promoted with scope and spread" |
| Defer to the first result, as the design proposed | Decides citability while holding the number. If the result is convenient the bar drops, and nobody involved would notice themselves doing it |
| Make rig output citable directly | Turns one machine's observation into repo truth with no scope attached — precisely the misuse ADR 0010 and `skills/source-verdict` test 3 exist to prevent. We refused a vendor's number for less |
| Commit the raw captures for auditability | Every `init` event carries an absolute home path. ADR 0009 forbids it and the pre-commit gate would correctly block it |
