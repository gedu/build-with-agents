---
id: journal/2026-08-05-second-gate-bypass-agent-conflict
type: journal
targets: [any]
status: draft
verified: 2026-08-05
sources: ["journal/2026-08-05-first-commit-gate-bypass.md", "AGENTS.md", "decisions/0001-agents-md-as-single-source-of-truth.md"]
---

# 2026-08-05 — second gate bypass, and it is not the same cause as the first

The second commit also lands **without a review receipt**. Recording it because a bypass that
happens twice stops being an incident and starts being a pattern, and because the cause is
**different from the first one** — which matters, since only one of the two is upstream's fault.

## The two bypasses are unrelated

| | First bypass | This one |
|---|---|---|
| Cause | `gentle-ai`'s own lifecycle could not reach a receipt | Local configuration forbids the sub-agent a lens needs |
| Whose defect | Upstream — filed as [#2478](https://github.com/Gentleman-Programming/gentle-ai/issues/2478) | Ours. Nothing to file |
| Fixed by a release? | Possibly | **No.** No version of `gentle-ai` changes this |

Conflating them would produce a wrong expectation — that upgrading fixes it. It does not.

## What actually happened

A fresh bounded review **started cleanly**, which corrects the first bypass entry:

```
lineage_id       review-652ceb5b0ca479c9      state: reviewing
risk_level       medium                       changed_files 12, changed_lines 830
selected_lenses  ["review-reliability"]       correction_budget 200
```

The first entry recorded the lineage as stuck in `correction_required` / `scope_changed`,
needing a maintainer recovery authorization an orchestrator may not construct. That was true of
the **old target**. Against new content the bootstrap returns `applicability: unrelated`,
`receipt: not_applicable`, `action: start`. There was a clean path the whole time.

Worth naming the process failure, not just the fact: this session relayed "the gate is blocked"
from a journal entry without re-running the bootstrap. `AGENTS.md` already forbids exactly that
— `journal/` is provenance, never authority. The rule was written, and then not applied to the
repo's own journal. A stale journal claim is a witness statement, and witness statements go
stale.

## Why the lens could not run

`review-reliability` runs as a sub-agent. The active session configuration states: *do not call
the Agent tool unless the user requested it.* Searched for the origin — `AGENTS.md`, project and
user `settings.json`, `gentle-ai`'s generated files, the `engram` plugin. Not found in any of
them. It is a Claude Code session-level directive whose emitting file was not located.

So the conflict is: the review contract requires delegation, and the session forbids it. An
agent may not resolve that by overriding the operator's explicit prohibition.

**Consequence, stated plainly:** with this session configuration, a bounded review can be
*started* but never *finished*. Every commit is therefore a bypass. That is not a bug in any
tool; it is a configuration that cannot satisfy its own gate.

## Decision

Committed without a receipt, with the operator's explicit instruction to proceed rather than
keep stalling on lifecycle mechanics. The content is documentation, journal entries, one draft
skill and a schema fix — no executable behaviour changes.

Note for the next session, because this is what confused this one: lineage
`review-652ceb5b0ca479c9` is left in state `reviewing` against a target that this commit's
journal entry already invalidated. It is **benign** — verified today that unrelated content
returns `applicability: unrelated`, so it will not block a future review. Do not read it as a
blocker without re-running the bootstrap first.

## Open items

- **The real decision, unresolved:** either review lenses are allowed to use sub-agents, or the
  review gate is formally not in use here. The current middle position produces a bypass per
  commit and an audit trail of excuses. ADR-shaped; not decided in this session.
- **No repo-wide redaction rule exists.** `AGENTS.md` has none. Redaction is written only in
  `upstream/gentle-ai/README.md`, scoped to staged reports, when it is really a property of
  anything pushed to a public repository. That gap is what let the first commit publish an
  absolute path containing a username. Also ADR-shaped.
- `gentle-ai review start` classified `decisions/0001-…md` as `risk_reasons: [{code:
  executable_change}]`. A markdown ADR is not executable. **Unverified** — check the classifier's
  real definition before treating it as a defect worth filing.
- Carried forward, unchanged: `: >"$tmp"` unguarded at `setup.sh:250`; `setup.sh` has no
  committed test harness; the possible fifth upstream report on `external.authorize_recovery`.
