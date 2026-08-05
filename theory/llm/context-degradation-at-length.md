---
id: theory/llm/context-degradation-at-length
type: theory
targets: [any]
status: validated
verified: 2026-08-05
sources: ["https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents", "https://arxiv.org/abs/2603.08274", "journal/2026-08-05-context-measurement.md", "research/claude-certified-architect-exam-guide.md"]
---

# Context degradation with length is real and measured — and no published threshold tells you when to clear

**The claim.** Model output quality degrades as context grows. This is documented and measured,
not folklore. But it is a gradient, not a cliff, and **no published measurement supports picking a
token number as the moment to reset a session.** Anyone who quotes one is extrapolating.

## What is established

Anthropic's engineering guidance defines the phenomenon and names it **context rot**:

> "as the number of tokens in the context window increases, the model's ability to accurately
> recall information from that context decreases"

and gives the mechanism as a budget being spent:

> "LLMs have an 'attention budget' that they draw on when parsing large volumes of context. Every
> new token introduced depletes this budget by some amount."

Read the calibration in their own description of the effect, because it is doing real work:

> "models remain highly capable at longer contexts but may show reduced precision for information
> retrieval and long-range reasoning compared to their performance on shorter contexts"

**Highly capable** with **reduced precision**, in two named task classes. That is not a collapse,
and it is not uniform across what a model does.

## What is measured, and exactly how far it reaches

arXiv:2603.08274 (JV Roig, submitted 2026-03-09) is the strongest public measurement available at
the time of writing: a 172-billion-token study of hallucination in document Q&A.

| Property | Value |
|---|---|
| Models | 35, **open-weight only** |
| Context lengths tested | 32K, 128K, **200K maximum** |
| Fabrication rate, best models at 32K | 1.19 – 7% |
| Fabrication rate at 200K | **exceeds 10%** |
| Reported dominant factor | Model selection, over temperature or hardware |

Two readings, and both matter.

**The degradation is real and it is large.** Roughly a doubling-to-tenfold increase in fabrication
between 32K and 200K, on the same models. Anyone treating long context as free is contradicted by
direct measurement.

**And the measurement does not reach the case most people are in.** Its ceiling is 200K, on
open-weight models. It measures *fabrication in document-grounded Q&A* — one task class, not
"degradation" in general. A session at 500K on a frontier proprietary model with a 1M window is
**outside this study's scope in three separate dimensions**: length, model class, and task.

This is the scope test from `skills/source-verdict` applied to a genuinely good source. The paper
is not weak. It is being asked a question it did not measure.

## A second, distinct effect: position, not just length

Anthropic's architect guide names the **"lost in the middle"** effect: models process information at
the beginning and end of long inputs reliably, but may omit findings from middle sections
(`research/claude-certified-architect-exam-guide.md`).

This is **not the length claim restated**. Length says: more tokens, less precision. Position says:
*where* in the input something sits changes whether it is used at all. A short input can suffer the
positional effect and a long one can be arranged to mitigate it. The guide's own mitigation is
structural rather than reductive — put key findings at the beginning of aggregated inputs, and give
detailed results explicit section headers.

The same guide states, in an answer rationale, that **larger context windows do not solve attention
quality problems.** That is the sharpest available first-party statement against the assumption that a
1M window makes any of this go away, and it is why the scope limit above matters rather than being a
technicality.

## The consequence for practice

There is no defensible token threshold to automate on. What exists is:

- A documented direction of travel — worse with length, on retrieval and long-range reasoning
  first.
- A measured curve that stops well below where long-context sessions now operate.
- No published number for frontier long-context models.

So the trigger for resetting a session cannot be read off a counter. The signals that are actually
available are **behavioural**: re-deriving a fact already settled, contradicting an earlier
decision in the same session, losing the distinction between what was verified and what was
assumed.

First-party guidance names the same class of signal independently, which is the strongest support this
approach has. It describes degradation in extended sessions as models *"giving inconsistent answers
and referencing 'typical patterns' rather than specific classes discovered earlier"* — a behavioural
symptom, described without reference to any token count. It also states that starting a new session
with a structured summary is more reliable than resuming with stale tool results, and recommends
scratchpad files for persisting key findings across context boundaries.

Two conclusions follow. The behavioural trigger is not a workaround adopted because no threshold was
available — it is what the vendor describes too. And "referencing typical patterns instead of the
specifics discovered earlier" is a **more useful symptom than the three listed above**, because it is
observable from the outside by anyone reading the output, not only by the agent noticing its own
repetition.

That is why `skills/context-checkpoint` triggers on finishing a unit of work rather than on a token
count. It also records a second reason — that surfacing a remaining-context countdown to the model
is itself an anti-pattern — but **that claim is not verified here**; it is carried in
`journal/2026-08-05-context-measurement.md` as unverified provenance and must be checked against
first-party guidance before it is relied on.

## Scope of this file

Vendor-bound where it quotes Anthropic; open-weight-bound and ≤200K where it quotes the study. The
general direction is well supported. **The absence of a usable threshold is the load-bearing
finding**, and it is the part most likely to be misquoted as "context length does not matter."

## What would sharpen it

A measurement at 500K–1M on frontier models, or a local reproduction: run a fixed retrieval task
in this repo at increasing context sizes and record where precision falls. Until one of those
exists, treating any specific number as the clear-the-session point is invention.
