---
id: research/two-paths-using-vs-building-agents
type: research
targets: [any]
status: validated
verified: 2026-08-05
sources: ["Untitled social post, 'usar agentes vs crear agentes' two-path learning split, pasted in full 2026-08-05. No canonical URL supplied; author not identified."]
---

# The "using agents vs building agents" two-path split

## Claim

Learning about agents is best organised by first choosing between two paths, because they require
different knowledge:

- **Using agents** (Claude Code, Codex and similar): context engineering, task decomposition,
  persistent instructions via `CLAUDE.md`/`AGENTS.md`, skills + subagents + MCP, feedback loops,
  validation systems.
- **Building agents**: agent loops and orchestration, harness engineering, tool design, context /
  state / memory, guardrails and sandboxing, evals and tracing.

## Source

Social-post format, pasted in full 2026-08-05. No URL, no author, no citations, no numbers.

## Contrast

**A taxonomy, not an empirical claim** (test 1). "These two paths require different knowledge" has
no observation that would falsify it, so it cannot be supported or refuted as evidence. It is scored
here on usefulness instead, which is the only thing it offers.

**Its first path was checked against local evidence and matched completely.** All six items on the
"using agents" list correspond to machinery already running in this environment: the 2026-08-05
`/context` measurement (context engineering), SDD phases (task decomposition), `AGENTS.md` plus
seven ratified ADRs (persistent instructions), 38 skills / 18 agents / ~90 MCP tools (skills,
subagents, MCP), the SDD cycle (feedback loops), and the `gentle-ai` review lifecycle (validation
systems).

Six of six. That is the useful output of this source: it functions as a **diagnostic** that
correctly located this project's position, and it did so more accurately than the graph-engineering
roadmap in `research/graph-engineering-roadmap.md`, which implied a Step-1 starting point for a
project already operating in that roadmap's Phase 4.

**Where it is thin.** The two paths are less separable than stated. Harness engineering appears only
on the "building" path, yet deferred tool loading, instruction precedence and context budgeting —
all harness concerns — are exactly what a heavy *user* of Claude Code manages daily; see
`theory/agents/capability-load-cost.md`, which is harness knowledge derived entirely from using an
existing tool. The post concedes the paths are "connected" but places harness engineering wholly on
one side, which is where the taxonomy leaks.

No urgency framing, no sale, no novelty claim. Notably absent, and worth recording as a contrast
with the graph-engineering post, whose technical content was comparable in quality but wrapped in
manufactured scarcity.

## Verdict

**`unverifiable`** — no falsifiable claim — **and useful**, which are independent properties.

- Useful as an **orientation tool**: it resolved a real "where do I start" question and its first
  path matched local reality six-for-six.
- Not citable as evidence for any claim about agents.
- One substantive weakness recorded: placing harness engineering exclusively on the building path is
  contradicted by local evidence.

Unattributed, but with nothing empirical asserted there is nothing that author reputation would
change here.

## Follow-up

No `theory/` promotion.

Used as an orientation input: the "using agents" list is a reasonable candidate set of dimensions
for the project AI-readiness checklist, alongside the walkinglabs topic map
(`research/harness-engineering-course-walkinglabs.md`), with the harness-engineering placement
corrected.
