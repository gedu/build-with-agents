---
id: theory/orchestration/delegation-and-context-boundaries
type: theory
targets: [any]
status: validated
verified: 2026-08-06
sources: ["research/gentle-orchestrator-anatomy-guide.md", "research/claude-certified-architect-exam-guide.md", "research/agent-harness-explainer-cluster.md", "journal/2026-08-05-redaction-gate-and-2478-on-224.md", "theory/agents/capability-load-cost.md"]
---

# A delegation is a context boundary, and everything the child needs must cross it explicitly

**The claim.** Delegating work to a subagent does not extend the parent's context into a helper. It
**creates a new one**, empty of the parent's conversation. That property is the reason delegation
works and the reason it fails: it protects the child from accumulated noise, and it silently drops
every constraint the parent never wrote down.

The practical rule that follows: **a delegation is only as good as its mission statement**, because
the mission is the entire universe the child will ever see.

## The property, confirmed independently twice

Two harnesses built by different organisations state the same thing.

- Gentle AI's orchestrator guide: subagents begin with fresh context and no memory of the main
  thread — *"un subagente no hereda mágicamente toda la conversación. Si una restricción solo vive en
  el hilo del padre y no se envía ni está disponible en un artefacto referenciado, el hijo puede no
  conocerla."* It lists "each phase remembers the whole conversation" as a common misconception.
- Anthropic's architect guide: subagent context must be provided explicitly in the prompt; subagents
  do not automatically inherit parent context or share memory between invocations.

Independent agreement across two implementations is what makes this structural rather than a quirk of
one product. Treat it as a property of delegated execution, not a configuration detail.

**The failure mode is specific and quiet.** A constraint stated once in conversation — "don't touch
the auth module", "the client forbids X" — is invisible to every child spawned afterwards. Nothing
errors. The child does competent work that violates a rule it was never told.

## What must cross the boundary

Synthesising both sources, a delegation carries: the concrete objective and expected result; scope and
relevant paths; **user constraints**; references to required artifacts rather than copies of them;
only the recovered prior context that is indispensable; the artifact-store modality; exact paths of
applicable skill files; the expected verification commands or evidence; and an instruction not to
re-delegate when the role is bounded execution.

Two of those deserve emphasis because they are the ones most often skipped.

**References, not copies.** Artifacts are passed by path or key. Gentle AI's guide is explicit that
an artifact "no necesita copiarse completo al prompt del agente padre", and that this separation is
what keeps the parent thread from growing. This is `theory/agents/capability-load-cost.md` applied to
a third domain: the cost of a dependency is what it costs to *load*, not what it costs to *reference*.
Tools, instructions and now artifacts follow the same shape.

**Skills do not travel automatically.** Listed as a misconception in the same guide: the orchestrator
must resolve the skill registry and include exact paths in the child's prompt. A skill the parent
"has" is not a skill the child has.

## The report is not the evidence

The sharpest claim in either source, and the one that makes this an orchestration problem rather than
a prompting problem:

> A subagent's result **does not prove the work happened**. It is a report. The orchestrator must
> check artifacts, paths and appropriate evidence before asserting success.

A coordinator that accepts a delegate's success report has not verified anything — it has acquired a
second unverified claim and moved it up one level. And the aggregation makes it worse: a parent
summarising five green reports produces one confident summary carrying five unexamined assertions,
with the uncertainty of each now invisible.

This is `theory/loops/verifier-availability.md` seen from the other side. There, the verifier was
unavailable and the gate reported "not run". Here, the verifier is *skipped* because a report is
mistaken for a check — and it reports success. Same missing verifier, louder failure.

### The rule is not about subagents — it is about instruments, including your own

Both sources above frame this as a property of *delegation*, and framing it that way leaves a gap that
was found the hard way here.

An independent statement of the same rule, from the testing direction rather than the delegation
direction, is broader and better: *"never trust the report if the system under test did not actually
change correctly"*, and *"Testing the story is weak. Testing the state change is the serious
version"* (`research/agent-harness-explainer-cluster.md`). Note what that formulation does **not**
mention: who or what produced the report. It is a rule about reports, not about subagents.

**The local instance, and it is why the widening is not pedantry.** Recorded in
`journal/2026-08-05-redaction-gate-and-2478-on-224.md` §6: a corner-case pass on a newly built gate
reported that every fix had failed. The fixes were correct. The **test harness** was reverting the code
under test on every reset — the artifact under test had been committed inside the fixture repository —
so the suite was exercising the old version while its output described the new one. A verified-false
conclusion was one step from being published, and nothing in it involved a subagent.

So the correct scope is: **anything that reports on work you did not directly observe is a claim, not
evidence.** A delegate's summary, a test suite's output, a linter's exit code, a CI badge, and your own
one-off script are the same category. The delegation case is the most discussed, not the most dangerous
— your own tooling is trusted more precisely because you wrote it.

The operational form, which is cheap: **before believing a report, confirm what produced it was the
thing you meant to test.** In the case above, one `rg` against the fixture copy would have shown it
lacked the fix. That check took seconds and was not run, because the suite was the thing being trusted.

**The grader ordering that follows**, from the same source: code-based checks first — *"unit tests,
static analysis, regex, schema validation, database queries, tool-call checks"* — then model-based
graders, which *"need calibration"*, then humans as the slow gold standard. That is the three-layer
enforcement ordering in `theory/loops/verifier-availability.md` restated for verification: put the
deterministic, inspectable check first, and reserve judgment-shaped checks for what genuinely requires
judgment.

Scope: the source carries **no measurement** — no study, no benchmark, no method. It is prescriptive
guidance, and its verdict is `unverifiable` for that reason. It is cited here for the principle and its
sharper framing. The instance that gives the principle teeth is local and first-hand.

## When not to delegate, and how much

Delegation is not free, and both sources bound it rather than encourage it.

The governing principle in Gentle AI's guide is that an action should be delegated when it would
**inflate the main context unnecessarily** — not to distribute work for appearance. Its stated limits:
use the smallest useful subagent flow; prefer a single writer to avoid conflicts; parallelise only
independent investigations or reviews; **do not turn children into new orchestrators**; record each
launch so the same task is not duplicated; and verify effects before reporting success.

Anthropic's guide adds the complementary failure at the decomposition step: **too-narrow
decomposition by the coordinator produces incomplete coverage** — subagents each execute their
assignment correctly while the union of assignments misses whole areas of the topic. Every individual
report is green and the aggregate is wrong.

Note the shape of that one. It cannot be caught by verifying any single delegate, because no delegate
failed. It is only visible by asking what was never assigned — which means **coverage is a property
of the parent's plan, and only the parent can check it.**

## Consequences for design

- **Write the mission as if the child knows nothing**, because it knows nothing.
- **Constraints belong in artifacts or in the mission, never only in conversation.** A rule that
  lives in the parent thread does not exist for the child.
- **Pass dependencies by reference**; let the child load them from the store.
- **Verify effects, not reports.** Check the artifacts, paths and evidence a delegate claims to have
  produced.
- **Audit the decomposition for coverage** separately from auditing each result, because narrow
  decomposition produces no failures to find.
- **Do not let children delegate.** Depth converts one context boundary into a chain of them, and
  each hop loses whatever was not explicitly forwarded.

## Scope

Two harnesses (OpenCode via gentle-ai, and Claude's Agent SDK), both vendor-documented, **no
measurements in either**. Neither source offers evidence that delegation improves outcomes — only
descriptions of how it behaves and normative rules for using it. So this file is a **contract
description, not an efficacy claim**, and it must not be cited as evidence that delegating is better
than not delegating.

The configuration mechanisms behind these claims (`permission.task`, overlay definitions, `allowedTools`
including `Task`) are harness-specific and deliberately excluded — see
`research/gentle-orchestrator-anatomy-guide.md` for why mixing them is a documented defect class.

## What would sharpen it

The measurement neither source provides: the same task executed delegated versus inline, comparing
result quality and total tokens. That is the experiment this repo has repeatedly named as missing —
the delegation rules currently in use are prompt policy backed by reasoning, not by data. Until it is
run, "delegate at four files" is a convention, not a finding.
