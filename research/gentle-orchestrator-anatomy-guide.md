---
id: research/gentle-orchestrator-anatomy-guide
type: research
targets: [any]
status: validated
verified: 2026-08-05
sources: ["Gentle AI, \"Guía de aprendizaje de Gentle AI\" — Capítulo 1, \"Anatomía y funcionamiento de gentle-orchestrator: configuración, herramientas, permisos, delegación y flujo completo del agente primario de OpenCode\", edición PDF, 21 pp., generated 2026-07-21. Read in full 2026-08-05."]
---

# Anatomía y funcionamiento de gentle-orchestrator (Gentle AI, Capítulo 1)

## Claim

`gentle-orchestrator` is not a binary, a model, or an executor — it is an **agent definition**
composed of OpenCode configuration, installed instructions, a model resolved at runtime, and
transient session context. Its behavior emerges from pieces that must not be conflated, and the
rules governing it are enforced at **three different layers with three different strengths**.

## Source

Gentle AI learning guide, Chapter 1, PDF edition, 21 pages, generated 2026-07-21.

**First-party** for claims about `gentle-ai`, `gentle-orchestrator` and its OpenCode overlay — the
strongest available weight for that population under `skills/source-verdict` test 7.

Notable on its own terms: the document repeatedly **bounds its own claims**. It warns that the
overlay's `"never does work inline"` description should be read as coordinating identity rather than
as proof that write capabilities were removed; it states that prompt words like `MANDATORY` and
`hard gate` remain prompt instructions unless another layer implements an equivalent check; and it
closes with a ten-item misconception list correcting over-readings of itself. A source that marks
where its own authority stops is behaving well by this repo's standards, and that raises the prior
rather than the verdict.

## Contrast

Four findings are load-bearing for work already in this repo. Two of them corrected it.

**1. Review lenses are explicitly allowlisted upstream — this reframes ADR 0008.**

The document lists the complete `permission.task` allowlist and states it includes the Judgment Day
and review agents: `jd-judge-a`, `jd-judge-b`, `jd-fix-agent`, `review-risk`, `review-readability`,
`review-reliability`, `review-resilience`, `review-refuter`.

`decisions/0008-review-lenses-may-use-subagents.md` was ratified as a local resolution to a local
conflict. It was more than that: **the upstream design had already permitted exactly this**, through
a default-deny allowlist with the lenses named as explicit exceptions. The ADR did not grant a new
capability, it removed an obstruction that was never upstream's.

This also sharpens the misattribution recorded in `theory/agents/instruction-provenance.md`. The
conflict was not "gentle-ai's contract versus a session directive with the merits unclear" —
gentle-ai was unambiguous, in configuration, about lenses being permitted delegation targets. Only
one side of that conflict had ever stated its position in a locatable file.

**2. A three-layer enforcement model — extends `theory/loops/verifier-availability.md` and supplies
the state that file was missing.**

The document separates three questions that are routinely collapsed:

| Layer | Question it answers | Practical force |
|---|---|---|
| Tools | Does this operation exist for this agent? | Exposes a capability |
| Permissions | Does the configuration accept this use? | The runtime applies the restriction |
| Prompt policy | When and how should the model use it? | Guides behavior only |

And it states the boundary explicitly: a rule written in the orchestrator prompt does **not**
automatically carry the force of an OpenCode denial, nor is it equivalent to a validation executed
by Go code. Summarised in the document's own terms: the prompt decides what should be requested,
OpenCode decides whether the agent has the tool or delegation configured, and the Go CLI executes
the native operation and validates its internal invariants.

This is a **three-tier refinement of the two-tier distinction** in
`research/claude-certified-architect-exam-guide.md` (programmatic enforcement versus prompt
guidance). It is more precise, and it produces a consequence neither source states: `verifier-
availability.md` distinguished a gate that **fails** from a gate that **did not run**. There is a
third and worse state — **a gate that was never a gate**, because it was only ever prompt text
asserting `MANDATORY`. That one reports nothing and blocks nothing, and it is invisible precisely
because it is loudly worded.

**3. Subagents receive new context — second independent confirmation.**

The document states that subagents begin with fresh context and no memory of the main thread, and
draws the operational consequence: *"Un subagente no hereda mágicamente toda la conversación. Si una
restricción solo vive en el hilo del padre y no se envía ni está disponible en un artefacto
referenciado, el hijo puede no conocerla."* It lists this among common misconceptions ("cada fase
recuerda la conversación completa" — incorrect).

Anthropic's architect guide asserts the same property for the Agent SDK. **Two harnesses built by
different organisations, same property, stated independently.** That converts it from a vendor
detail into a structural feature of delegated execution — which is what makes it theory rather than
configuration trivia.

**4. A subagent's report is not evidence — and this is the sharpest single line in the document.**

Listed as a misconception: *"Un resultado del subagente prueba que el trabajo ocurrió"* — incorrect.
*"Es un reporte. El orquestador debe comprobar artefactos, rutas y evidencia apropiada antes de
afirmar éxito."*

That is a verifier claim, and it closes a loop this repo opened from the other end. A coordinator
that trusts a delegate's success report has no verifier at all — it has a second unverified claim.

**A three-stage provenance chain, which explains a local search failure structurally.**

The document separates versioned **source asset** → installed **effective configuration** → running
**session**, and warns that modifying a repository asset does not demonstrate that an existing
installation has been regenerated, nor does a value in the effective `opencode.json` appear
literally in the source template.

`theory/agents/instruction-provenance.md` recorded a failed search for a directive's origin. That
search covered files — assets and configuration. The directive lived in the **third stage**. The
failure was not carelessness about where to look; it is that only two of the three stages are files
at all.

**Where this source does not reach.** It is **OpenCode-bound**. Its mechanisms — `opencode.json`,
`permission.task`, `__replace__`, the multi-agent overlay, `mode: primary` versus
`mode: subagent` — describe one harness. This repo's own work happens in Claude Code, and
`upstream/gentle-ai/0004-opencode-text-in-claude-code-block.md` documents precisely the confusion of
mixing the two. The **principles** (three enforcement layers, fresh context per delegation, report ≠
evidence, artifacts by reference) transfer. The **configuration specifics do not**, and citing them
as if they applied to Claude Code would repeat the defect report 0004 exists to flag.

Also: it is descriptive and normative, with **no measurements anywhere**. No number appears in 21
pages. By test 2 it sits at the "cited to a named source" tier, the named source being the project's
own configuration — verifiable by reading that configuration, which is better than most, but it is
not evidence about outcomes. It tells you what the system *does*, never how well delegation *works*.

## Verdict

**`supported`**, with scope.

- **Supported and first-party** for the architecture, enforcement layers, delegation contract and
  agent-selection rules of `gentle-orchestrator`.
- **Well-calibrated**, unusually so: it marks its own limits and corrects predictable over-readings.
  That is the behavior `skills/source-verdict` is designed to reward.
- **Not evidence about efficacy.** Zero measurements. It cannot support any claim that delegation
  improves outcomes.
- **Scope**: OpenCode harness, gentle-ai assets as of 2026-07-21. Principles generalise; mechanisms
  do not.

## Follow-up

| Target | Action |
|---|---|
| `theory/orchestration/delegation-and-context-boundaries.md` | **Written** — the first `theory/orchestration/` file, with this as primary source |
| `theory/loops/verifier-availability.md` | Added the third state: a gate that was never a gate |
| `theory/agents/instruction-provenance.md` | Added the three-stage asset → config → session chain as the structural reason the search failed |
| `decisions/0008-review-lenses-may-use-subagents.md` | Added the upstream allowlist finding — the ADR removed an obstruction rather than granting a capability |

Remaining and unwritten: `theory/agents/tool-surface-design.md`, still resting on the Anthropic
guide alone.
