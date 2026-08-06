---
id: research/agent-harness-explainer-cluster
type: research
targets: [any]
status: validated
verified: 2026-08-06
sources: ["https://www.langchain.com/blog/how-to-build-a-custom-agent-harness", "https://dev.to/naimulkarim/what-is-an-ai-agent-harness-370m", "https://www.techademy.com/how-ai-agents-work", "https://www.dhirajdas.dev/blog/how-to-test-ai-agents-harness-guide", "https://blogs.oracle.com/developers/what-is-the-ai-agent-loop-the-core-architecture-behind-autonomous-ai-systems", "theory/orchestration/delegation-and-context-boundaries.md"]
---

# Five agent-loop / harness explainers, adjudicated together

## Claim

Collectively: that an "agent harness" is the software surrounding a model that lets it act, that the
model owns reasoning while the harness owns execution, memory, tools and guardrails, and that every
agent runs a variant of the same perceive → reason → act → reflect loop.

Adjudicated as one entry because **they make the same definitional claim and none of them carries a
falsifiable one.** Four separate `unverifiable` stubs would record less than this does.

## Source

All accessed 2026-08-06.

| Source | What it is | Falsifiable claim? |
|---|---|---|
| LangChain, *How to build a custom agent harness* | Vendor blog. *"The harness is the scaffolding around the model that connects it to the real world"*; `agent = model + harness` | None. No numbers, no citations beyond its own docs |
| Naimul Karim, dev.to, *What is an AI Agent Harness?* | Independent explainer. *"the software infrastructure that surrounds a Large Language Model… and enables it to interact with the outside world"* | None |
| Techademy, *How AI agents work* | Marketing content for a training platform, ending in a mentor-session CTA | None. Its "50 tools", "30 model calls", "10–20 active tools" are illustrative, not measured |
| Dhiraj Das, *How to test AI agents: harness guide* | Independent prescriptive guide on testing agents | None. No study, benchmark or disclosed method |
| Oracle, *What is the AI agent loop* | **Not retrievable** — HTTP 403 on access | Cannot be assessed |

The Oracle link is recorded as **unreachable, not as empty.** Nothing about its content is being
judged here; it returned 403 and was never read. If it matters, it needs to be supplied as text.

## Contrast

**The definitions agree with each other and with local use, which is the one thing worth taking.**
Three independent parties — a framework vendor, an independent developer and a training company —
converge on the same split: the model decides, the harness executes and constrains. That convergence
makes "harness" safe to use as shared vocabulary in this repo rather than a term needing local
definition. Vocabulary is a real deliverable; it is not evidence.

**LangChain's middleware framing is the most concrete thing in the group**: *"Middleware hooks into the
agent loop at each step: before and after model calls, before and after tool calls, at agent startup
and teardown."* That is a description of where deterministic checks can attach, which is the same
question `theory/loops/verifier-availability.md` asks as "which layer implements it". Usable as a map
of insertion points. Still first-party to one framework and uncited.

**One of the five is materially more useful than the other four, and it converges with a local
first-hand finding.** Dhiraj Das's testing guide has no numbers, but it articulates, from outside this
repo, exactly the rule this week produced twice:

> *"never trust the report if the system under test did not actually change correctly"*
>
> *"Testing the story is weak. Testing the state change is the serious version."*
>
> *"Grade the outcome first: did tests pass, did the right file change, did the database row exist,
> did the approval gate trigger?"*

`theory/orchestration/delegation-and-context-boundaries.md` already carries *"a subagent's report is
not evidence — verify artifacts, paths and effects"* from two vendor sources. This is a third,
independent statement of it, from the testing direction rather than the delegation direction.

It also lands on the harder case recorded in
`journal/2026-08-05-redaction-gate-and-2478-on-224.md` §6, where the thing reporting falsely was not a
subagent but **my own test harness** — a fixture repo that reverted the code under test on every reset
and then reported that every fix had failed. Das's rule generalises to that: grade the state, not the
story, including when the story is your own tooling's.

Its grader taxonomy is the reusable part: code-based graders *"cheap and objective: unit tests, static
analysis, regex, schema validation, database queries, tool-call checks"*, model-based graders needing
calibration, human graders as the slow gold standard. That is a three-tier ordering that maps cleanly
onto this repo's prompt-policy / runtime / native-code layers, and it is the same insight — put the
deterministic check first.

**Where the group is weakest.** The perceive → reason → act → reflect framing common to the
explainers is a taxonomy, and by test 1 a taxonomy is not a claim: no observation would contradict it.
It is useful for talking and useless for deciding. None of these sources would change a design
decision in this repo.

## Verdict

**`unverifiable`**, for all five, and for two distinct reasons that should not be blurred.

- **Four contain no falsifiable claim.** They are definitions, taxonomies and prescriptions. Per
  `research/README.md` and the `source-verdict` skill this is the expected verdict for explainers, and
  it is **not** a synonym for false. Their value is vocabulary, a map of harness responsibilities, and
  LangChain's list of loop insertion points.
- **One was never read.** The Oracle post returned 403. It has no verdict because it has no assessed
  content.

Recorded uses, so this entry is not merely dismissive: "harness" is now safe shared vocabulary;
LangChain's middleware hook points are a usable map; Das's grader tiers and his grade-the-state rule
are worth carrying.

## Follow-up

**One promotion, narrow.** Das's grade-the-state-not-the-story rule strengthens the "report is not
evidence" section of `theory/orchestration/delegation-and-context-boundaries.md` as a third
independent articulation, and it extends that section's scope from *a delegate's report* to *any
verification instrument's report, including your own*. That extension is supported by local first-hand
evidence, not by Das — cite him for the principle and this repo's journal for the instance.

Nothing else in this group is promotable. No numbers, no method, no measurement.

If the Oracle piece matters, supply its text and it gets its own entry.
