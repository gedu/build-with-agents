---
id: theory/agents/capability-load-cost
type: theory
targets: [any]
status: validated
verified: 2026-08-10
sources: ["https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop", "journal/2026-08-05-context-measurement.md", "research/agent-loop-optimization-bytebytego.md", "research/claude-certified-architect-exam-guide.md", "research/llm-as-code-agentic-programming.md", "rig/results/tool-surface-v1/runs.jsonl", "sdd/measurement-rig/spec.md"]
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

### The same shape in a third domain: context as a function of structure

An academic result argues that an agent's context need not grow with the number of steps taken. If
control flow lives in the program, each model call's context is its **ancestor chain** in a call DAG
with returned subtrees collapsed to summaries — so length is a function of **call depth**, not of
accumulation: *"no call ever carries the whole task's history, only its ancestor chain"*
(`research/llm-as-code-agentic-programming.md`, arXiv:2606.15874).

That is this file's claim again, in a domain it did not anticipate. The pattern now holds three times:

| Domain | Cost is a function of | Not of |
|---|---|---|
| Tools | Schemas **loaded** | Tools connected |
| Artifacts across a delegation boundary | Artifacts **copied into a prompt** | Artifacts referenced |
| Conversation in an agent loop | Ancestor-chain **depth** | Steps executed |

Each was reached independently, and none of the three sources states the general form. The general
form is: **context cost is set by what a given call must carry, and what a call must carry is a design
choice, not a consequence of scale.** Every instance above is someone discovering that separately.

Scope: the third row is one paper's architectural argument, measured on GUI automation with one model
against leaderboard baselines — see the verdict for the seam in that comparison. The *mechanism* is
what generalises here, exactly as with the two rows above it.

## The limit of this claim — deferral does not fix everything it appears to fix

Anthropic's architect guide states that giving an agent access to too many tools — *"18 instead of
4-5"* — degrades **tool selection reliability** by increasing decision complexity, and that agents
holding tools outside their specialization tend to misuse them
(`research/claude-certified-architect-exam-guide.md`). First-party, though offered as illustration
rather than as a measured threshold.

Combining that with the mechanism above produces a distinction **neither source states on its own**,
and it is the most important qualification on this file:

| Problem | Fixed by deferral? |
|---|---|
| Schema tokens resident in the window | **Yes** — that is exactly what deferral removes |
| Decision complexity when selecting a tool | **No** — the *names* stay resident and still enter the choice |

Deferral was silently credited with solving both. It solves one. A harness can hold 90 deferred tools
at almost no token cost and still present the model with a 90-way selection problem, because
selection happens over the names.

The two therefore need different remedies: deferral for cost, and **scoping** — giving an agent only
the tools its role requires — for selection reliability. The guide's own recommendation is scoped tool
access per role with narrow cross-role exceptions, which is a different lever from deferral entirely.

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

## Measured here: what one resident tool entry costs

The file above rests on one `/context` reading and on the deferral mechanism observed directly. Neither
gave a **per-tool** number. This repo's measurement rig now has one.

**Design.** Same task, same model, same CLI version, same prompt bytes, twelve paired runs. One variable:
the visible tool surface, **32 names versus 3**, set with `--disallowedTools` and read back from each
run's own `init` event rather than asserted from the flags.

**Result.**

| Quantity | Value |
|---|---|
| Comparable pairs | 12 |
| Extra visible tools in the broad arm | 29 |
| Extra `cache_creation_input_tokens`, median | **6,489** (min 4,964, max 6,585) |
| **Per resident tool entry** | **≈ 224 tokens** |
| Cost delta, median | $0.088 per run |
| Pairs where broad cost more | **12 of 12** |

Two independent tests on that: a sign test at 12 of 12 gives p = 0.000244, and Mann-Whitney on the
nine same-order pairs gives an exact one-sided p = 0.000021.

**A confound of ours, found and ruled out.** Every pair initially ran the broad arm first, so a
within-pair cache-warming effect would have produced exactly the flat delta observed and been
indistinguishable from a structural one. Three pairs run in the reverse order settle it: scoped-first
gives a median cache delta of 6,511 against broad-first's 6,467, and every pair in both orders is
positive. The difference does not depend on who goes first.

**What this refines.** The earlier measurement showed deferral removing 65.1k of schema from the window.
This shows what remains **after** deferral: a tool that is merely *listed* still costs about 224 tokens
per run, because a name arrives with a description. So "declare a capability by name and it is nearly
free" is true relative to loading a schema and **false in absolute terms** — 90 deferred tools would
carry roughly 20k tokens of resident entries by this figure, which is not nothing and is not what the
sentence implies.

### Scope, and it is narrow

One machine, one model (`claude-opus-5[1m]`), one CLI version (2.1.224), one synthetic task, subscription
auth where the reported cost is notional rather than billed. Ambient context of roughly 26k tokens is
present and identical in both arms, so it cancels in the delta and inflates neither number.

Two anomaly classes occurred and both have diagnosed causes rather than open ones: four runs voided on
CLI version drift, and six on `ListAgents` being intermittently absent under 2.1.224 — structurally a
broad-arm-only fault, since the scoped arm disallows that tool either way. Two broad runs were excluded
by that mechanism; their exclusion rests on a surface check unrelated to cost.

**224 tokens per entry is this harness's number, not a law.** It is a function of how long the tool
descriptions happen to be, and a harness with terser or richer descriptions would land elsewhere. The
*mechanism* — a resident entry costs its name plus its description, every turn — is what generalises.

## What would sharpen it

Measurements on a second harness, and a resident-vs-deferred comparison of the same tool set on the
same task. Neither has been run here.

Note what the section above already settled: the quality dimension this file originally asked for
arrived from first-party guidance, and it **did not** confirm the convenient answer. It showed that
deferral and selection reliability are separate problems. Asking for the sharpening produced a
narrower claim, not a broader one — which is the outcome to expect when the question is asked
honestly.
