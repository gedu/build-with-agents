---
id: decisions/0014-a-fixtures-runtime-is-substrate-not-this-repos-runner
type: decision
targets: [any]
status: validated
verified: 2026-08-11
sources: ["decisions/0013-a-committed-executable-carries-its-own-test.md", "decisions/0011-rig-produces-evidence-not-truth.md", "sdd/failure-flood-triage/spec.md", "sdd/failure-flood-triage/design.md"]
---

# 0014 — A rig fixture's runtime is substrate under measurement, not this repo's test runner

## Context

`sdd/failure-flood-triage` needs `rig/fixtures/failure-flood/*`: a fixture carrying real donor-module
code, a committed Node/npm install, and a Jest suite that the agent under measurement invokes as part
of the task. ADR 0013 decided that no repo-level test runner exists here, by design — `hooks/pre-commit`
and `rig/derive.py` each carry a self-test, invoked by a flag, and that is the only tested code in the
repository. A fixture whose own suite is real, invoked, and load-bearing looks at first glance like the
exact thing that decision rejected.

It is not the same question, and this ADR exists to say so on the record before any fixture content is
committed (spec R-F11.1's ordering precondition), because two things arrive in the same change and must
not be answered as one:

1. May a rig fixture carry its own runtime and test runner, without reversing ADR 0013's repo-level "no
   test runner" decision?
2. This same change also commits three executables that carry their own test surface —
   `rig/run-pipeline.sh`, the collector (`rig/collect.py`), and its signature normalizer's `--self-test`
   flag (spec R-F1.3) — which means ADR 0013's own stated supersession trigger, *"when a third executable
   needs a test"*, is textually met, independently of question 1. Sources: `decisions/0013-...md`, spec
   R-F11.2.

## Decision

**Clause A.** A rig fixture (here, `rig/fixtures/failure-flood/*`) MAY carry its own runtime (Node/npm)
and test runner (Jest). That runtime is **substrate under measurement** — content the harness feeds to
an agent and later collects failures from — never this repo's own verification surface. This repo's
verification surface is unchanged: `hooks/pre-commit`, `bash -n`, `python3 -m py_compile`, and each
committed executable's own self-test.

The practical test of the boundary: **the fixture's own suite reports on the fixture, never on this
repo, and no repo-level command runs it.** Nothing under `rig/`, `hooks/`, or any `AGENTS.md`-governed
area invokes `npx jest` against the fixture as a precondition of anything this repo asserts about
itself. The fixture's `package.json`/`package-lock.json` live under `runtime/`, install to a per-run,
machine-local directory (never the committed tree), and `.gitignore` does not change to accommodate
them.

**Clause B.** ADR 0013's own stated supersession trigger — *"when a third executable needs a test"* —
is met by this same change: after it lands, four executables carry a self-test (`hooks/pre-commit`,
`rig/derive.py`, `rig/run-pipeline.sh`, `rig/collect.py`), not the two ADR 0013 was written against.
This ADR explicitly **declines** the trigger on the record. The per-executable self-test pattern still
holds cleanly for all four: each test still ships inside the file it tests, needs nothing but what
already runs that file, and a `tests/` directory built to hold four still-independent tests is
infrastructure ahead of content — the exact failure mode ADR 0013 named, now observed to still apply one
executable later than the number in its own trigger.

The trigger is restated sharper, in place of the count it used: **extraction becomes the right call when
a self-test needs fixtures too large to inline**, not when a specific executable count is reached. The
first plausible future candidate is `tools/generate-cases.py`'s self-test (failure-flood-triage's PR3):
if proving that generator deterministic and discriminating ever needs committed input tables rather than
inline synthetic fragments, that is the trigger firing for real, not a fourth exception to wave through.

## Consequences

| Consequence | Detail |
|---|---|
| The boundary is checkable, not asserted | "No repo-level command runs the fixture's suite" is a grep-able claim over `hooks/`, `rig/*.sh`, `rig/*.py`, and `OPERATIONS.md` — not a promise that has to be taken on faith |
| ADR 0013 is not reopened by count alone | Declining the trigger here means a future fifth or sixth self-test executable does not automatically reopen this question either; only the fixtures-too-large-to-inline condition does |
| The fixture's install is explicitly out of `hooks/pre-commit`'s scope | The redaction gate and every other repo-level check still run over tracked bytes only; a fixture's `node_modules/` is per-run and never tracked |
| A future second fixture inherits the boundary for free | Any later `rig/fixtures/<other>/*` with its own runtime is already covered by Clause A; this ADR does not need re-ratifying per fixture |

## Alternatives

| Rejected | Reason |
|---|---|
| Amend ADR 0013 to say "no test runner, except fixtures" | Reads as a carve-out invented after the fact for one experiment, when the two questions (repo verification surface vs. fixture content) were never actually in conflict — a fixture's suite was never repo verification |
| Treat the third/fourth-executable trigger as fired and extract a runner now | There is still exactly one test per file, invoked the same way, with no shared discovery or convention needed across them; extracting a runner for four independent flag-gated self-tests is the "infrastructure ahead of content" failure ADR 0013 exists to name, not a fix for it |
| Silently let the trigger lapse without recording the decision | ADR 0007: rationale that only exists in a conversation does not exist. A trigger textually met and not acted on needs the same record a trigger acted on would get, or the next reader re-derives the same question from scratch |
| Give the fixture its own ADR number without touching 0013 at all | Loses the one place a reader would look for "does the fixture's Jest suite violate the no-test-runner decision" — the answer belongs next to the decision it is being asked about |
