---
id: research/claude-certified-architect-exam-guide
type: research
targets: [any]
status: validated
verified: 2026-08-05
sources: ["Anthropic, Claude Certification Program — \"Claude Certified Architect – Foundations Exam Guide\", Version 1.0, effective July 2026, exam code CCAR-F, document control v1.0 July 2026. Distributed preparation PDF; read in full 2026-08-05."]
---

# Claude Certified Architect – Foundations, Exam Guide (Anthropic)

## Claim

Anthropic's authoritative statement of what a competent Claude solution architect must know,
across five weighted domains: Agentic Architecture & Orchestration (27%), Claude Code
Configuration & Workflows (20%), Prompt Engineering & Structured Output (20%), Tool Design & MCP
Integration (18%), Context Management & Reliability (15%). Weights are stated as derived from a job
task analysis, and the passing standard from a formal standard-setting study.

Within those domains it asserts specific, checkable behavioural claims about how agents and models
fail. Those claims — not the credential — are what this entry adjudicates.

## Source

Anthropic, Claude Certification Program. Exam Guide v1.0, effective July 2026, exam code CCAR-F.
Read in full (39 pages) on 2026-08-05.

**First-party** for claims about Claude, Claude Code, the Agent SDK and MCP. By
`skills/source-verdict` test 7 this is the strongest available weight for vendor behavior — it is
the vendor's own normative statement of correct practice, written to certify practitioners against
it.

**Handling constraint, recorded because it binds future use.** §13 prohibits reproducing exam
content in any form and §14 defines exam questions, answer options and scenarios as Anthropic's
confidential property. This repository is public. Therefore: the guide's **technical claims** are
cited and used; its **sample questions, answer options and scenario texts are not reproduced**, here
or in any promoted `theory/` file. This is a redistribution limit, not a doubt about the source.

## Contrast

Checked against local first-hand evidence and against the other sources already adjudicated here.
Four claims are load-bearing for work already written in this repo.

**1. Independent review beats self-review — confirms `decisions/0008` on its own reasoning.**
The guide states that a model "retains reasoning context from generation, making it less likely to
question its own decisions in the same session", and that independent review instances "without
prior reasoning context" are more effective at catching subtle issues than self-review instructions
or extended thinking. It repeats the point for CI: the session that generated code is less effective
at reviewing its own changes than an independent instance.

ADR 0008 reached this from first principles and had no external source. It now has a first-party
one. **This is corroboration of an argument, not the origin of it** — the ADR was ratified before
this source was read.

**2. Tool count degrades selection reliability — supplies the quality claim
`theory/agents/capability-load-cost.md` explicitly lacked.**
The guide states that giving an agent too many tools — "18 instead of 4-5" — degrades tool selection
reliability by increasing decision complexity, and that agents with tools outside their
specialization tend to misuse them.

That file's "what would sharpen it" section asked for exactly this: a quality claim to sit alongside
the token-cost claim. It is now available and first-party.

It also produces a **new distinction neither source states alone**, and this is the most useful
output of reading them together: deferral removes tool *schemas* from context, but the tool *names*
remain resident and still enter the selection decision. So deferral solves the token cost and does
**not** solve selection reliability. Two independent problems that a single mechanism was silently
credited with fixing.

**3. Named behavioural symptoms of context degradation — confirms the design choice in
`skills/context-checkpoint` and `theory/llm/context-degradation-at-length.md`.**
The guide describes degradation in extended sessions as models "giving inconsistent answers and
referencing 'typical patterns' rather than specific classes discovered earlier"; names the
"lost in the middle" effect (reliable at the beginning and end of long inputs, may omit middle
sections); states that starting a new session with a structured summary is more reliable than
resuming with stale tool results; and, in an answer rationale, that larger context windows do not
solve attention quality problems.

Every one of those supports triggering on **behaviour** rather than on a token count, which is what
both local files argued. The "lost in the middle" claim is a *positional* effect, distinct from and
complementary to the length effect measured by arXiv:2603.08274 — it is not the same finding
restated.

**4. Deterministic enforcement vs prompt guidance — sharpens
`theory/loops/verifier-availability.md`.**
The guide distinguishes programmatic enforcement (hooks, prerequisite gates) from prompt-based
guidance, and states that where deterministic compliance is required, prompt instructions alone
have a non-zero failure rate.

It also lists loop-termination anti-patterns: parsing natural language to decide termination,
checking assistant text for completion, and **"setting arbitrary iteration caps as the primary
stopping mechanism"**. That last one required a correction to the local file, which had praised a
bounded correction budget without distinguishing a backstop from a primary signal. Corrected there.

**5. One claim corrected a local overclaim.** The guide documents a `/memory` command "to verify
which memory files are loaded and diagnose inconsistent behavior across sessions".
`theory/agents/instruction-provenance.md` had asserted that enumerability of active instructions was
an absent property. It is present **for memory files**. The claim was narrowed before publication —
see that file's scope section.

**Where the guide is not evidence.** It is normative, not empirical: it states what a competent
architect should believe, with no measurements, no sample sizes and no methodology behind the
behavioural claims. Domain weights and the cut score cite a job task analysis and a standard-setting
study, but neither study is included or referenced in a checkable form. By test 2 (number
provenance) almost every behavioural claim sits at the "cited to a named source" tier at best —
the named source being Anthropic itself. The one quantitative hint, "18 instead of 4-5" tools, is
given as an illustrative example, not a measured threshold.

So it is authoritative about **intent and recommended practice**, and it is not a substitute for
measurement. Where it agrees with a local measurement, the local measurement stays the primary
evidence.

## Verdict

**`supported`**, with scope stated.

- **Supported and first-party** for claims about how Claude, Claude Code, the Agent SDK and MCP
  behave and should be configured. Strongest available weight for that population.
- **Not quantitative evidence.** Normative guidance without disclosed method. Do not cite it for a
  number.
- **Scope**: Anthropic's products at guide v1.0, July 2026. Vendor-bound by construction. The
  credential is time-limited to 12 months by Anthropic's own reasoning that the technology moves —
  which is itself a reason to date every citation from it.

## Follow-up

Promoted into, and corrected, work already written:

| Target | Action |
|---|---|
| `decisions/0008-review-lenses-may-use-subagents.md` | Added as first-party corroboration of the context-isolation argument |
| `theory/agents/capability-load-cost.md` | Added the tool-selection-reliability claim and the new deferral-vs-selection distinction |
| `theory/llm/context-degradation-at-length.md` | Added "lost in the middle", the named behavioural symptoms, and the larger-windows claim |
| `theory/loops/verifier-availability.md` | Added deterministic-vs-probabilistic enforcement; corrected the bounded-budget section to distinguish backstop from primary signal |
| `theory/agents/instruction-provenance.md` | **Corrected** an overclaim about enumerability |
| `skills/context-checkpoint/SKILL.md` | First-party support for checkpoint-over-resume; basis for promotion out of `draft` |

Not yet written, evidence now in hand: `theory/agents/tool-surface-design.md` (descriptions as the
selection mechanism, splitting vs consolidating, scoped tool access) and the first
`theory/orchestration/` file (coordinator-subagent hub-and-spoke, explicit context passing,
structured error propagation, decomposition breadth as a coverage risk).
