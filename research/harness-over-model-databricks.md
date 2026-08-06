---
id: research/harness-over-model-databricks
type: research
targets: [any]
status: validated
verified: 2026-08-06
sources: ["https://www.databricks.com/blog/ai-harness", "theory/agents/capability-load-cost.md"]
---

# The harness, not the model, decides agent outcomes (Databricks)

## Claim

That the harness dominates agent quality: *"The same model can place significantly higher or lower
[on benchmarks] depending entirely on how the harness is built"*, and *"Most operational agent
failures come from the harness, not the model itself."*

Offered with one supporting figure: pairing GPT-5.5 with an *OfficeQA Pro Agent Harness* scored
**52.63%**, up from **36.10%** with GPT-5.4.

## Source

`https://www.databricks.com/blog/ai-harness`, accessed 2026-08-06. Vendor engineering blog. Databricks
sells the agent platform the post positions, so by `skills/source-verdict` test 6 the claim the sale
depends on is *"harness quality is where the wins are"* — which is exactly the claim being made.

## Contrast

**The direction of the claim is consistent with everything measured locally.** This repo's own
first-hand work has repeatedly found harness-level structure dominating model-level choices:
`theory/agents/capability-load-cost.md` measured deferral saving more context than the entire
always-on configuration surface, and the redaction gate built this week failed and was fixed four
times without any model changing. So *"the harness matters a lot"* is not in dispute here.

**The number, however, does not carry.** By test 2 it sits at the weakest usable tier and arguably
below it:

- **Method: not disclosed.** No description of the evaluation protocol, prompt set, retry policy or
  scoring.
- **Population: not specified.** *OfficeQA Pro* is named but not defined, sized or published in the
  post; nothing states how many tasks or trials the two figures rest on.
- **Two variables move at once.** 36.10% is GPT-5.4 and 52.63% is GPT-5.5 **with** a different
  harness. Model and harness both changed between the two figures, so the comparison cannot isolate
  the harness — which is the only thing the number is offered to prove. The post's own framing
  ("cutting errors nearly in half") is computed from these two mixed-variable figures.

That last point is decisive and it is a scope error in the source, not an ambiguity in my reading: a
claim of the form *"the harness explains this delta"* requires holding the model fixed. Nothing here
does.

**`"Most operational agent failures come from the harness"`** is the more interesting assertion and it
has no evidence attached at all — no incident population, no classification scheme, no counts. It is
plausible, this repo's own week is anecdotally consistent with it, and it remains unfalsifiable as
stated because "most" has no denominator.

**Local reproduction: not applicable.** OfficeQA Pro is not publicly reachable from the post, so there
is nothing to reproduce even in principle. That is a property of the source.

## Verdict

**`partially supported`.**

- **Supported as vocabulary and as a framing**: the harness is a first-class engineering surface, and
  its building blocks are worth enumerating. The post's list of harness responsibilities is a usable
  checklist.
- **Not supported as evidence for the headline number.** 52.63% vs 36.10% changes the model and the
  harness simultaneously, discloses no method, and names a benchmark that is not published. It must
  not be cited in `theory/` as quantifying a harness effect, because it does not isolate one.
- **Unfalsifiable** for *"most operational agent failures come from the harness"*, absent any
  denominator.

## Follow-up

**No promotion to `theory/`.** The directional claim is already better supported locally by
first-hand measurement, and adding a vendor figure that cannot isolate its own variable would weaken
the file that took it, not strengthen it.

Kept because the failure is instructive: this is a well-written post whose single number cannot
support its single claim, and noticing that took reading the two figures side by side rather than
reading the prose around them. That is `skills/source-verdict` test 3 catching a case where nothing
looks wrong.
