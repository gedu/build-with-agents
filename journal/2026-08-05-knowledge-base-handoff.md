---
id: journal/2026-08-05-knowledge-base-handoff
type: journal
targets: [any]
status: draft
verified: 2026-08-05
sources: ["skills/context-checkpoint/SKILL.md", "MAP.md", "decisions/0008-review-lenses-may-use-subagents.md"]
---

# 2026-08-05 — handoff: the repo's first knowledge base

Checkpoint written by following `skills/context-checkpoint/SKILL.md`. **This is that skill's first
end-to-end run**, which is the evidence it needs for promotion out of `draft` — record whether it
worked on resume.

Written for a reader with none of the conversation.

## 1. Where we stopped — the next action

Write **`theory/agents/tool-surface-design.md`**. It is the last identified doc with evidence already
in hand, and it currently rests on one source only:
`research/claude-certified-architect-exam-guide.md`.

Material available for it, all already adjudicated:

- Tool descriptions are the primary mechanism models use for tool selection; minimal descriptions
  produce unreliable selection among similar tools.
- Too many tools degrades selection reliability ("18 instead of 4-5", offered as illustration, **not**
  a measured threshold).
- Agents holding tools outside their specialization tend to misuse them; scoped per-role access with
  narrow cross-role exceptions is the recommended shape.
- Splitting generic tools into purpose-specific ones with defined I/O contracts; renaming to remove
  functional overlap.
- MCP resources as content catalogs to reduce exploratory tool calls.
- Structured error responses: `errorCategory`, `isRetryable`, and why uniform "Operation failed"
  prevents recovery decisions.

**Required framing**, or the file will overclaim: this must connect to
`theory/agents/capability-load-cost.md`, which already establishes that deferral fixes token cost and
does **not** fix selection reliability, because selection happens over resident tool *names*. Scoping
is the lever for selection; deferral is the lever for cost. Do not merge them.

After that, `theory/` has no remaining identified gap with evidence in hand. Everything else needs an
experiment first — see section 4.

## 2. Versions and identifiers

All verified on 2026-08-05.

| Item | Value |
|---|---|
| Repo | `gedu/build-with-agents`, **PUBLIC** |
| `origin/main` == `main` | `5251614`, 0 ahead / 0 behind, working tree clean |
| Model in use | `claude-opus-5[1m]` |
| `gentle-ai` | 2.2.4 (Homebrew) |
| `gga` wrapper | v2.10.1 |
| Upstream issue #2478 | `OPEN`, labels `bug` + `status:needs-review`, **0 comments** |
| Abandoned review lineage | `review-652ceb5b0ca479c9`, left in state `reviewing` |
| Review bootstrap now returns | `applicability: unrelated`, `receipt: not_applicable`, `action: start` |

Commit sequence this session, oldest first:

```
3cd2d40  scaffold (pre-existing)
bed4dec  fix(decisions): machine-local paths out of ADR sources
255ca50  docs: context measurement, trust-boundary, second bypass record
4fdca55  feat: first verified knowledge + source-verdict skill
f48786b  feat(decisions): ADR 0008 — review lenses may use sub-agents
5251614  feat(theory): first orchestration doc + three-layer enforcement model
```

Sources adjudicated, cite by these identifiers and never by a local path:

- Anthropic, *Claude Certified Architect – Foundations Exam Guide*, v1.0, effective July 2026, exam
  code CCAR-F. **Handling limit: §13/§14 make exam questions, options and scenarios Anthropic's
  confidential property. This repo is public — cite claims, never reproduce the quiz.**
- Gentle AI, *Guía de aprendizaje*, Cap. 1, *Anatomía y funcionamiento de gentle-orchestrator*, PDF,
  21 pp., generated 2026-07-21.
- arXiv:2603.08274 — JV Roig, submitted 2026-03-09.

## 3. Verified versus assumed

The section a summary always drops. An unmarked assumption becomes a fact next session.

### Verified first-hand this session

- Repo visibility, sync state, clean tree, all commit SHAs above.
- A tree-wide search for absolute home paths, the machine username and the private project name →
  **zero matches**. (The search pattern is deliberately not written out here: quoting it would
  reintroduce the very string being redacted, which happened once while writing this file.)
- Tool versions and issue #2478's state, by direct command.
- **arXiv:2603.08274 exists and is stronger than the journal recorded**: 35 open-weight models,
  32K/128K/200K, fabrication 1.19–7% at 32K rising above 10% at 200K, on H200 / MI300X / Gaudi 3.
- Anthropic's context-rot and attention-budget quotes — fetched and quoted verbatim.
- ByteByteGo contains exactly **one** number (~20% worse TTFT on Broadwell). It is a map of
  mechanisms, not a measurement study.
- Both PDFs read in full — 39 pages and 21 pages.
- The deferral mechanism, directly: tools were resident by name only, and a schema had to be loaded
  by explicit lookup before one could be called.
- The Agent-tool directive is **not** in `AGENTS.md`, project or user `settings.json`, `gentle-ai`'s
  generated files, or the `engram` plugin.

### Assumed, inherited, or explicitly not verified — do not promote these

- **The context numbers** (502.4k/1M used, 41.4k resident, 65.1k deferred, 34.5k one MCP server).
  These come from a **previous session's** `/context`, carried as journal provenance. They were
  **not** re-measured. `theory/agents/capability-load-cost.md` labels them as a single observation
  for this reason.
- **The "context anxiety" / countdown anti-pattern claim.** Journal only. **Not** confirmed against
  first-party guidance, and deliberately excluded from
  `theory/llm/context-degradation-at-length.md`. Still open.
- **Whether `/memory` would have located the directive.** Reasoned that it would not, because the
  directive is stage-three (running session) and `/memory` enumerates stage two. **Not tested.**
- **`: >"$tmp"` unguarded at `setup.sh:250`.** Inherited from an earlier journal entry. The line
  numbers were confirmed to exist; the defect itself was **not** re-analysed.
- **`gentle-ai review start` classifying a markdown ADR as `executable_change`.** Observed once.
  Whether it is a defect depends on the classifier's real definition, which was not checked.
- **A possible fifth upstream report** on `external.authorize_recovery` naming a surface no
  orchestrator may derive. Unverified.
- **The bodies of upstream reports 0002–0004.** Only their titles, field counts (10 each) and absence
  of placeholders were checked. Their content was **not** read or validated.

## 4. Open items, explicitly not resolved

**Deliberately left open:**

- **`skills/context-checkpoint` stays `status: draft`.** Its promotion criterion is end-to-end runs,
  not better citations. First-party support arrived this session and was **not** treated as
  sufficient. This handoff is run #1.
- **Upstream reports 0002–0004 remain unfiled.** Filing is a human act — it publishes under
  Eduardo's GitHub identity and cannot be cleanly withdrawn. Also: their titles are plain descriptive
  sentences, unlike 0001's `fix(review): …`, and upstream expects conventional-commit shaped titles.
  Normalising them was deferred, not rejected.
- **No paid-promotion tier** for the author-trust benchmark. Decided this session: the project is
  open source, so the integrity objection is moot.
- **No `theory/` file on delegation efficacy.** Both vendor sources describe delegation and neither
  measures it. Writing one would be invention.

**Unresolved and still costing something:**

- **No repo-wide redaction rule exists.** `AGENTS.md` has none; redaction is written only in
  `upstream/gentle-ai/README.md`, scoped to staged reports, when it is really a property of anything
  pushed to a public repo. That gap is what let the first commit publish a username path. ADR-shaped.
- **The abandoned lineage** `review-652ceb5b0ca479c9` sits in `reviewing`. Benign — verified that
  unrelated content returns `applicability: unrelated` — but **do not read it as a blocker without
  re-running the bootstrap.** A previous session made exactly that mistake.
- **Commit granularity versus workspace-bound receipts.** A receipt binds the whole workspace
  projection, so a reviewed batch maps to one commit. Splitting into work-unit commits needs one
  review cycle per commit. Unresolved; irrelevant while the tree is clean.
- **Experiments named but never run:** delegated versus inline on the same task (quality and tokens);
  resident versus deferred tool sets on the same task; retrieval precision at 500K–1M on a frontier
  model. Every "what would sharpen it" section in `theory/` points at one of these.

## 5. What the conversation established that no file records

- **If the Agent-tool prohibition reappears, do not re-diagnose it.** It is stage-three, unlocatable,
  and *not* a `gentle-ai` defect — no release affects it and there is nothing to file. ADR 0008 is
  the standing authority to override it. Two days were lost to that misattribution once.
- **Eduardo's goal, and its one hard dependency.** Four parts: (1) a single install command wiring
  `gentle-ai` + `engram` + stack-selected skills; (2) an auditor that answers "is this project
  AI-ready, what are the gaps"; (3) contribute upstream while learning; (4) eventually build an MCP
  as a learning exercise. **(2) is blocked on a written definition of "AI-ready", and that
  definition is the `theory/` content.** Writing theory is the auditor's specification, not a detour.
  (1) is mechanical, independent, and buildable any time — `setup.sh` already does part of it.
- **Candidate dimensions for the AI-readiness checklist**, from two adjudicated sources: the six
  "using agents" items plus the walkinglabs topic map — with the correction that harness engineering
  does **not** belong only on the "building agents" path. `theory/agents/capability-load-cost.md` is
  harness knowledge derived entirely from *using* an existing tool.
- **The author-trust rule, corrected and accepted.** "Only trust reputable authors" cannot be the
  test — it shields credentialed nonsense and discards checkable claims for arriving in the wrong
  genre. Reputation is a **prior**; the verdict is whether claims are checkable and whether you
  checked them. Two design constraints if the trust index is ever built: a score must never let a
  claim skip the tests, and the corpus is biased toward *shared* sources, which selects for virality
  — the thing being filtered for.
- **Publishing only high scorers still leaves survivorship bias.** Absence reads as a negative signal
  once the list is known. Fix: publish **what was evaluated**, so absence means "not evaluated".
- **Where this project actually sits.** The graph-engineering roadmap's Phase 4 — validation gates,
  recovery paths, checkpoints, observability — describes work already done here and already painful.
  Its Step 3 (the verifier is everything) is precisely what blocked three commits. Starting that
  roadmap at Phase 1 would be walking backwards, and by its own Step 19 the stated goal needs no
  graph at all.
- **The three-layer enforcement heuristic applies to this project's own instructions.** Prompt policy
  < runtime permission < native code. `CLAUDE.md` is full of `MANDATORY` and "non-skippable hard
  gates"; per the orchestrator guide those are prompt text unless another layer implements an
  equivalent check. The test is not to read the rule but to ask which layer implements it. Emphatic
  wording is weak evidence of enforcement and mild evidence against it.
- **A subagent's report is not evidence.** Verify artifacts, paths and effects before asserting
  success. This is the strongest single line found in any source this session.
