---
id: backlog
type: index
targets: [any]
status: draft
verified: 2026-08-13
sources: ["AGENTS.md", "gaps/README.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "sdd/failure-flood-triage/tasks.md"]
---

# BACKLOG.md — candidate practices and deliverables, blocked and waiting

Real demands and candidate practices that are not yet actionable, each with its own named unblock
condition. Nothing here is built ahead of that condition — the same no-invented-knowledge rule
`AGENTS.md` states for `blocks/`, and the same "waiting is not passivity" discipline `gaps/README.md`
already applies to a demand seen only once.

## What belongs here

- A candidate practice observed once, recorded with its exact trigger for building it — never built on
  that first observation alone.
- A downstream deliverable this repo's own work points at but has not yet earned the right to publish,
  with the exact evidence gap that blocks it.

## Does NOT belong here

- A demand already promoted — that becomes a `blocks/`/`templates/` entry, or a `theory/` file.
- A vague "we should eventually…" with no stated unblock condition. Per the same rule `hypotheses/`
  enforces on a test, an entry with no named trigger is not a backlog item, it is a wish.

## Entries

### 1. Claim discipline — candidate practice, blocked on recurrence

**What**: Two rules, applied from task 3.4 onward in `sdd/failure-flood-triage` and both already shown
to work on first use: (a) any appeal to a rule, convention, precedent or prior decision must carry
`path:line` plus the verbatim quote — what cannot be quoted is reframed as "I am choosing X because Y"
rather than dressed as authority; (b) any number a command can produce must come with that command, and
a stated total must equal the sum of its own stated parts.

**Blocked on**: a second and third occurrence, not this first one. Building a claim-verifier after one
instance is infrastructure ahead of content — the failure mode `decisions/0013` implicitly warns against
by keeping a checker minimal and test-first, and the same reason `blocks/`/`templates/` stay empty until
`gaps/` records a second independent demand for the same thing.

**What made the original catchable, recorded because it inverts the intuition**: the axis is not
vague-versus-precise but verifiable-versus-not. A precise invented claim is *safer* than a vague correct
one, because the precise one is checkable in one grep. The artifact failure that surfaced this was
arithmetic, not fabrication — a declared total checked against a real `numstat`, with the parts listed
right beside it. That needs addition, not a fabrication detector.

**Trigger for building a checker**: a second and third occurrence of either rule being violated,
observed independently.

**Source**: `sdd/failure-flood-triage/tasks.md` task 6.8.

### 2. Portable procedure — downstream deliverable, blocked on evidence promotion

**What**: The collector → diagnostician → applier flow (`rig/collect.py`, `rig/run-pipeline.sh`) applied
to a real failing suite outside this repo — the form the incident that originated the failure-flood
experiment actually needs, and which no artifact in this cycle names.

**Blocked on**: the experiment's evidence must first be promoted into `theory/`, carrying its scope and
spread, per `decisions/0011`. A procedure published before the measurement is a recommendation without
magnitude — the fault `theory/agents/tool-surface-design.md` already carries, and which this experiment
exists to stop repeating.

**Not written yet, deliberately**: no block or skill exists for this in `blocks/`/`templates/` (both
still empty — `gaps/` is their demand signal, per `MAP.md`'s own description of that directory).

**Trigger for writing the block or skill**: a `theory/` write on the failure-flood-triage measurement,
with scope and spread attached, exists first.

**Source**: `sdd/failure-flood-triage/tasks.md` task 6.7.
