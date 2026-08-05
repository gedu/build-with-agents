---
id: theory/agents/capability-load-cost
type: theory
targets: [any]
status: validated
verified: 2026-08-05
sources: ["https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop", "journal/2026-08-05-context-measurement.md", "research/agent-loop-optimization-bytebytego.md"]
---

# The cost of a capability is what it costs to load, not what it costs to have

**The claim.** An agent's context cost is not a function of how many tools, skills or servers it is
connected to. It is a function of how many of their **definitions are resident in the window**.
Declare a capability by name and it is nearly free; load its schema and you pay for it every turn
of the conversation.

The consequence is counter-intuitive and it is the useful part: **adding capability and adding
context cost are separable decisions.** Most discussions of agent design assume they are the same
thing.

## First-hand evidence

Verified directly in the session that produced this file, on Claude Code with
`claude-opus-5[1m]`:

- Roughly 90 MCP tools and 18 custom agents were connected and callable.
- Their **names** were resident. Their **parameter schemas were not**.
- Calling one required an explicit schema-loading step first — a keyword query returning the full
  JSONSchema, after which the tool was invocable. Before that step the tool could not be called at
  all, because no parameter contract existed in context.

That is the mechanism, observed rather than reported: capability is declared cheaply and its
definition is fetched on demand.

## The measurement

From `journal/2026-08-05-context-measurement.md`. **A single observation**, one model, one session,
one project — recorded with its date because a token figure is not a constant:

| Surface | Tokens | Resident? |
|---|---|---|
| Conversation messages | 461.2k | Yes |
| Everything not conversation (instructions, skills, agents, system prompt, system tools) | **41.4k** | Yes |
| MCP tool schemas | **48.3k** | **No — deferred** |
| System tool schemas | **16.8k** | **No — deferred** |

Two findings from those four rows.

**Deferral saved more than the entire always-on configuration surface costs.** 65.1k deferred
against 41.4k resident. The largest single lever in the whole configuration was the one that is
invisible until measured, because it shows up as an absence.

**One server dominated.** Of 48.3k deferred MCP schemas, roughly 34.5k was a single service, and a
further ~9.2k was 22 paired `authenticate` / `complete_authentication` tools for services that may
go unused in a given session. Loaded eagerly, that one server would have cost **three times the
root instruction file**.

Scope, stated because the number will otherwise be quoted as a law: these figures are one
measurement on one harness. The **mechanism** generalises; the **magnitudes** are an example.

## Independent corroboration

The same technique appears as a shipped production optimisation outside this vendor. Reporting
attributed to named engineers behind Codex and ChatGPT Work describes, among harness-layer
efficiency techniques, **deferred tool discovery using BM25 lexical ranking to load tool schemas
on demand**.

That is second-hand and labelled as such — attributed reporting, not vendor documentation. See
`research/agent-loop-optimization-bytebytego.md` for the verdict and its limits. Its weight here is
narrow but real: two independent harnesses, built by different organisations, converged on
deferring tool schemas. That is evidence the constraint is structural rather than an artifact of
one implementation.

## What follows for design

- **Count what is resident, not what is connected.** "How many MCP servers do you have" is close to
  meaningless as a cost question.
- **A capability with a large schema is a candidate for deferral, not for deletion.** The choice is
  not connect-or-don't.
- **Instruction files are usually the wrong optimisation target.** In the measurement above the
  entire non-conversation surface was 8.2% of the window and conversation was 91.8%. Shrinking a
  10.3k instruction file to save tokens is optimising 2% while ignoring the rest.
- The general form: **audit configuration for coherence, manage conversation for volume.** They are
  different problems and the token counts say which is which. A duplicated rule matters because a
  reader must reconcile two wordings, not because it costs tokens.
- The same shape applies to instructions, not just tools: a large procedure that only some sessions
  need belongs behind a read-on-demand pointer rather than in an always-on file.

## What would sharpen it

Measurements on a second harness, and a resident-vs-deferred comparison of the same tool set on the
same task — which would turn "deferral saves tokens" into a quality claim as well as a cost one.
Neither has been run here.
