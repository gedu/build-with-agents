---
id: journal/2026-08-05-context-measurement
type: journal
targets: [any]
status: draft
verified: 2026-08-05
sources: ["https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents", "https://huggingface.co/datasets/openai/mrcr", "journal/2026-08-05-first-commit-gate-bypass.md"]
---

# 2026-08-05 — measuring a real context window, and what it corrected

First measurement of a live context window on this project, taken with Claude Code's
`/context` on `claude-opus-5[1m]`. It corrected an estimate of mine and reframed the
saturation audit. Journal, so provenance — not authority.

## The measurement

502.4k of 1M tokens used (50%). Free: 497.6k (49.8%).

| Category | Tokens | % of window |
|---|---|---|
| **Messages** | **461.2k** | **46.1%** |
| System tools | 18.2k | 1.8% |
| Memory files (`CLAUDE.md` 10.3k + `context7.md` 516) | 10.9k | 1.1% |
| System prompt | 5.9k | 0.6% |
| Skills (38 skills, descriptions only) | 2.8k | 0.3% |
| MCP tools loaded (90 tools) | 2.3k | 0.2% |
| Custom agents (18 agents) | 1.3k | 0.1% |

Counted separately, and **not** part of the 502.4k:

| Deferred (declared, not loaded) | Tokens |
|---|---|
| MCP tool schemas | 48.3k |
| System tool schemas | 16.8k |

## Three things it corrected

### 1. My byte-based estimate was 25% low

Earlier the same day, from `CLAUDE.md` being 31k bytes, this journal's author estimated
"~7.5–8k tokens" using a ~4 chars/token rule of thumb. The real figure is **10.3k**, so the
actual ratio is closer to **3.0 chars/token**. The estimate was not in the right ballpark and
should not have been offered as one. Tokens get measured, not approximated — and the
approximation error was in the direction that understates the problem.

### 2. The configuration is not the saturation problem — the conversation is

Everything that is not conversation — root instructions, skills, agents, MCP, system prompt,
system tools — totals **41.4k tokens: 8.2% of the context in use**. Messages alone are
**91.8%**.

This reframes the `CLAUDE.md` audit run earlier today. Its findings are real, but they are
**correctness defects, not budget defects**. The duplicated review-lens rules matter because
the two statements are worded *differently* and a reader must reconcile them — not because
they cost tokens. At 10.3k, the entire root instruction file is about 1/45th of what the
conversation costs. Optimising it for size would be optimising the wrong 2%.

The general form, worth keeping: **audit configuration for coherence, manage conversation for
volume.** They are different problems with different fixes, and the token counts say which is
which.

### 3. Deferred loading is the largest single win, and it is invisible until measured

65.1k tokens of tool schemas (48.3k MCP + 16.8k system) are declared but not loaded. That is
**more than the entire always-on configuration surface**, saved by deferral alone.

Where it concentrates: of the 48.3k deferred MCP schemas, roughly **34.5k is one server** —
Notion, whose largest single tools are `notion-create-comment` (4.1k),
`notion-query-meeting-notes` (3.9k), `notion-update-page` (2.7k) and `notion-search` (2.4k).
A further ~9.2k is 22 `authenticate` / `complete_authentication` pairs for services that may
never be used in a given session. Loaded eagerly, one MCP server would have cost three times
the root instruction file.

This is the same shape as the lazy `sdd-orchestrator-workflow.md` (18k, deliberately kept out
of the always-on thread by `CLAUDE.md:301-307`) — and it is the pattern to write up: the cost
of a capability is not what it costs to *have*, it is what it costs to *load*.

## On clearing context, and why not on a threshold

The open question this measurement was taken to answer: when should a long session be cleared,
and can that be automated?

What the evidence supports:

- Degradation with length is real and named — Anthropic calls it **context rot**, and frames it
  as an **attention budget** drawn down as tokens grow.
- It is not a cliff. Their own phrasing is calibrated: models "remain highly capable at longer
  contexts but may show reduced precision for information retrieval and long-range reasoning."
- **No published threshold applies here.** The measured numbers available (arXiv:2603.08274)
  stop at 200K and cover open-weight models only. This session is at 502k on a model that study
  excluded. Anyone quoting a token number as the moment to clear is extrapolating.

What argues against automating it on a token count, and this is the sharp part: surfacing a
remaining-context countdown *to the model* is a documented anti-pattern. Anthropic's own
migration guidance records "context anxiety" — a model worrying about running out of context,
suggesting a new session or trimming its own work, "most often when the harness surfaces a
remaining-token countdown", with the explicit instruction to avoid showing explicit
context-budget counts. It is documented for Claude Fable 5 specifically; the general form
appears in their prompt-audit guidance as "budget countdowns rendered into context… can cause
premature wrap-up behavior."

So the naive design — watch the token count, warn the agent as it climbs — risks *causing* the
degradation it means to prevent.

The alternative that the evidence does support: **checkpoint on work-unit boundaries, not on
token counts.** This project has now done that twice by hand — the gentle-ai upgrade handoff
and the first-commit bypass entry — and both times the next session resumed without
re-deriving anything. The signal to checkpoint is not a number; it is finishing a unit of work.
The symptoms that mean it is overdue are behavioural: re-deriving settled facts, contradicting
an earlier decision, losing track of what was verified versus assumed.

Captured as `skills/context-checkpoint/`, `status: draft` — the mechanism is written but has
not yet been used enough to claim it works.
