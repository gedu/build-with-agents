---
id: journal/2026-08-05-planning-across-a-trust-boundary
type: journal
targets: [any]
status: draft
verified: 2026-08-05
sources: ["AGENTS.md", "MAP.md"]
---

# 2026-08-05 — planning across a trust boundary (client forbids external AI from reading code)

Brainstorm. **Provenance, not authority** — this entry contains an idea that was proposed one
way and reshaped into another, and the discarded version is kept here on purpose. Nothing below
is implemented, measured, or validated.

## The situation being solved

A client restricts AI use. The specific restriction, as stated:

> The external AI — the one the company does **not** provide — may not read the code.

Two properties matter, because together they set the whole design:

| Property | Value | Why it matters |
|---|---|---|
| Nature of the restriction | **Compliance / legal**, not technical | Rules out anything that merely *disguises* the code |
| In-perimeter model | Exists, may be premium, **can** read all code | The "good model" is not only on the outside |
| External model | Better reasoning (e.g. Opus/Fable vs Copilot), unmetered by the client | The reason to leave the perimeter at all |

## What was proposed first — the obfuscation pipeline

Three agents:

| Agent | Sees code? | Job |
|---|---|---|
| **Obfuscator** | Yes | Cheap model. Emit a "DOM" of the project: structure copied with file/folder names changed, one file per feature describing what it does, plus input/output, consumers, and a navigable graph/table |
| **Planner** | No | Reason only over the obfuscated graph; produce plans and answers |
| **Deobfuscator / interpreter** | Yes | Map the returned plan back onto the real code |

This version was **dropped**. Three reasons, in order of severity.

### 1. Under compliance, obfuscation is not merely useless — it is harmful

Renaming `UserPaymentService` to `ModuleA7` does not satisfy a legal restriction. The
behaviour, the input/output contracts and the business rules **are** the confidential
material, and they are more sensitive than the identifiers. Names are the least sensitive
part of a codebase.

The closest analogy is pseudonymisation under GDPR: pseudonymised personal data is still
personal data. Obfuscated proprietary code is still proprietary code.

The active harm is *false assurance*. A rename layer produces the feeling of protection while
the actual secret crosses the boundary, which makes people comfortable sending things they
should not send. That is worse than sending nothing, and worse than sending something openly
reviewed.

### 2. The difficulty was inverted

The obfuscator was assigned the cheapest model and the hardest task: summarising what a
feature does in business terms, inferring real I/O, identifying consumers. The planner was
assigned the premium model and the easier task: reasoning over an already-digested graph.

A bad summary produces a well-argued, confident, wrong plan. Expensive garbage.

Also relevant: the mechanical half of the obfuscator's job needs **no model at all**. File
tree, imports, call graph, who-consumes-whom and blast radius are deterministic extractions —
CodeGraph already produces them exactly and for free. The model is only required for the
semantic layer.

### 3. Renaming destroys the signal the planner needs

Domain names carry the semantics. Strip them and the planner reasons worse. Add prose
describing what each renamed thing does and the leak returns, only less efficiently encoded.
There is no free lunch here: either the description says what the thing does (leak) or it does
not (planner useless).

The mapping table is also a new secret. If it leaks, everything unwinds at once.

## The test that replaced the obfuscation layer

> Would you publish this text publicly, with the client's name at the top?

If yes, it may cross. If no, it may not — and no amount of renaming changes that. It is
concrete, auditable, and a human can apply it in seconds.

Asked about the brief as originally imagined, the answer was **no**.

That answer does not kill the idea. It says the brief is **not abstract enough yet**. The test
is a **thermostat, not a traffic light**: raise the altitude until the answer becomes yes, and
whatever survives at that altitude is what may leave.

The uncomfortable consequence, recorded because it is the strongest argument against building
anything: at the altitude where the answer becomes yes, the questions are close to generic —
*"how should I structure a React Native app with offline-first sync and three team
boundaries?"* — and that can already be asked today with no pipeline, no obfuscation, and no
agents. **Most of the desired value may need none of this.**

## The reframe — the flow is mostly inbound

The second stated motivation turned out to be the load-bearing one, and it is not about
secrecy at all. It is about **token economics and division of labour**:

1. Spend expensive thinking — planning, brainstorming, architecture, GitHub configuration —
   **outside**, on a subscription the client does not pay for and does not meter.
2. Arrive with the plan already written.
3. Use the client's in-perimeter model — which *can* see the code — to check the plan against
   reality, make minimal adjustments, then execute: write code and files following the
   client's own skills and conventions.

Read the direction of travel: that workflow is mostly **inbound**. Compliance risk exists only
on the outbound leg, and the outbound leg is exactly the part that can shrink to almost
nothing.

So the artefact is not an obfuscation pipeline. It is **plan-import across a trust boundary**.

## SDD is already the transport format

The plan that crosses inward has a shape this repo already defines: SDD artefacts.

| Side | Phase | Notes |
|---|---|---|
| Outside (no code access) | proposal → spec → design → tasks | Written at generic altitude |
| Boundary | human approval of anything outbound | Persisted and diffable |
| Inside (full code access) | bind → apply → verify | Runs under the client's skills and conventions |

`sdd/` is currently empty (`MAP.md`). This would be its first real use.

The residual outbound channel — for the cases where something about the actual project genuinely
must be said — stays a narrow pipe with a **mandatory human gate**: the redactor *drafts*, a
human *approves* egress, and what crossed is persisted for audit. An agent deciding on its own
what is safe to send is precisely what a compliance function will not sign. A small surface is
also the only kind that gets audited honestly.

## The honest cost

A generic plan can produce wrong tasks. The hard work therefore **moves inward**, to the
generic→concrete **binding** step: it must validate the plan against real code and reject what
does not survive contact, not merely translate vocabulary. That step is the heart of the design
and the place it will hurt.

## Scope boundary

Worth stating before building, so the tool is useful instead of disappointing:

| Works for | Does not work for |
|---|---|
| Architecture, patterns, tradeoffs | Bug fixes |
| Testing strategy | "Why is this failing?" |
| Repository / CI / GitHub configuration | Anything needing exact code |

The right column is not a gap to close later. It is structurally impossible: those questions
require the code the external model may not see.

## What would have to be proven before implementing

Nothing here has been measured. The comparison that would justify the work:

- **Baseline** — the in-perimeter model plans directly, with full code access.
- **Variant** — generic plan produced outside, then bound and executed inside.

Plausible that the variant wins on architecture-level questions, where altitude matters and
stronger reasoning shows. Plausible that it loses everywhere the exact code matters. Until that
is measured, this is design on faith.

## Status

Idea only. Not implemented, not validated, no experiment run. To be revisited later; if it
survives the comparison above it graduates to `theory/orchestration/`, and only then can the
reusable parts become `blocks/`.
