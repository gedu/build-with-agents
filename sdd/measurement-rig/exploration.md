---
id: sdd/measurement-rig/exploration
type: journal
targets: [any]
status: draft
verified: 2026-08-06
sources: ["decisions/0010-measurements-vary-the-harness-not-the-model.md", "theory/agents/tool-surface-design.md", "sdd/testing-capabilities.md"]
---

# measurement-rig — exploration: can a single agent run be instrumented?

SDD exploration phase for the change `measurement-rig`. Investigation only. No proposal, no design.

The design was settled in `decisions/0010-measurements-vary-the-harness-not-the-model.md`. The open
question this phase exists to answer is narrower and decides whether any of it is buildable: **can one
agent run be instrumented programmatically?**

Four signals are required. Without the second one there is no first experiment at all, because
`theory/agents/tool-surface-design.md`'s untested claim is about *selection reliability*, and that is
counted from the tool-call list.

## Result: all four signals are obtainable

| Signal | Status | Evidence |
|---|---|---|
| Tokens, with cache split | **Available** | `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` as separate fields |
| Tool-call transcript | **Available** | `tool_use` blocks carrying `name` and verbatim `input`, paired to `tool_result` by `tool_use_id` |
| Wall clock | **Available** | Per-event timestamps |
| Turn count | **Available** — `num_turns` | Confirmed by a real run. See the correction below; this row said "partial" before one command settled it |
| Controllable tool surface | **Available — via `--disallowedTools`, not `--allowedTools`** | Floor is 3 tools (`Glob`, `Grep`, `Read`). `--allowedTools` has no visibility effect at all. See the reconnaissance section |

### Verified first-hand, not taken from the exploration's report

The sub-agent's findings were re-checked directly, because a sub-agent's report is not evidence:

- **Session transcripts exist on disk** as JSONL under `~/.claude/projects/<sanitized-cwd>/<session-id>.jsonl`,
  and carry the four usage fields separately. Confirmed by reading a real file and extracting the field
  names.
- **`tool_use` blocks and `tool_use_id` pairing are present** in that same file — 20 tool-use blocks in
  the one sampled.
- **The CLI flags are real**: `--agents`, `--allowedTools`, `--disallowedTools`, `--bare`, and
  `--output-format` accepting `text | json | stream-json`. Confirmed from `claude --help`.

### A correction to the exploration's recommendation, found by reading the full flag text

> **Both subsections below were themselves superseded by an actual run — see *Correction, from one run
> that cost two seconds*.** They are kept because the sequence is the point: reading the flag text fixed
> one error and introduced another, and only executing settled it. Do not act on the two subsections
> immediately following without reading that correction first.

The exploration proposed `--bare` alongside `--agents`, and a truncated reading of `--bare` suggested
those conflict. They do not — the opposite is true. `--bare`'s full description ends:

> Explicitly provide context via: `--system-prompt[-file]`, `--append-system-prompt[-file]`,
> `--add-dir` (CLAUDE.md dirs), `--mcp-config`, `--settings`, `--agents`, `--plugin-dir`.

`--bare` skips **auto-discovery** — hooks, LSP, plugin sync, auto-memory, `CLAUDE.md` discovery,
background prefetches, keychain reads — and requires every input to be passed explicitly. That is
precisely constraint 2 of ADR 0010: one variable per run, with everything held fixed recorded. Under
`--bare` the harness is **declared** rather than inherited from whatever the machine happens to have
configured, which is the difference between a reproducible run and a run that silently depends on this
laptop.

So `--bare` is not merely compatible with the rig. It is close to a requirement for it.

### A cost prerequisite the exploration did not surface

`--bare` states: *"Anthropic auth is strictly `ANTHROPIC_API_KEY` or `apiKeyHelper` via `--settings`
(OAuth and keychain are never read)."*

The rig therefore runs on **API spend, not subscription**. Combined with ADR 0010's constraint 3 —
N runs per cell — cost scales as N × tasks × 2 harnesses and is real money. This is a v1 scoping input,
not a blocker.

## Correction, from one run that cost two seconds

Everything above about `--bare` was reasoned from `claude --help`. **One actual invocation corrected two
claims and closed one open question.** It is recorded here rather than silently folded in, because the
shape of the mistake is the point.

The command, run with **no `ANTHROPIC_API_KEY` set at all**:

```
claude -p "Reply with only the two characters: ok" --output-format json
```

**Correction 1 — the subscription works, and `--bare` is not near-required.** The run succeeded on
ordinary session auth. Headless mode does not need an API key; only `--bare` does, because only `--bare`
refuses OAuth and keychain. The earlier framing of `--bare` as close to a requirement for the rig was
wrong, and it was wrong in the direction of adding a cost and a prerequisite that do not exist.

**Correction 2 — turn count is not partial.** The result carries `"num_turns":1` directly. It also
carries `total_cost_usd`, which is better than deriving cost from token counts, and an `iterations`
array giving a per-message breakdown.

**What the same run revealed, and it is the useful part.** For a prompt that asked the model to emit two
characters, the usage was:

```
"cache_creation_input_tokens": 26001, "cache_read_input_tokens": 15758,
"input_tokens": 2, "output_tokens": 4, "total_cost_usd": 0.2679…
```

Twenty-six thousand tokens of cache creation to do nothing. That is the ambient context — `CLAUDE.md`
auto-discovery, hooks, plugin sync, auto-memory — and it is exactly the "inherited from this machine"
problem with a number attached.

So what `--bare` actually buys is now measurable, and it is **not correctness**: it is not paying for
context the task does not need, and portability of the resulting numbers to another machine.

**Why that does not invalidate a subscription-based v1.** The ambient overhead is a **constant, not a
variable**. If it is identical in arm A and arm B, the *difference* between them remains attributable to
the tool surface, which is the only quantity the first experiment claims to measure. On a subscription
the reported `total_cost_usd` is notional rather than billed, so the overhead costs plan tokens, not
money.

**Revised recommendation for v1: subscription, without `--bare`.** Nothing needs to be provisioned.
Reserve `--bare` plus an API key for when the numbers must be reproducible off this machine — a real
goal, and not the first one.

Also observed and worth keeping: `stop_reason: "end_turn"` as the termination signal, `service_tier`,
`modelUsage` keyed by exact model id, and the cache-creation split by TTL
(`ephemeral_1h_input_tokens` versus `ephemeral_5m_input_tokens`).

**And one thing this did NOT settle.** `claude --help` shows no `--max-turns` flag in this version, so
there is no obvious per-invocation loop bound. ADR 0010 wants runs bounded; where that bound comes from
is now an open spec question rather than an assumed flag.

This correction is the clearest instance so far of
`theory/loops/reading-and-running-find-different-defects.md`: reading the flag text produced a confident
wrong conclusion about auth and a "partial" verdict on a field that exists, and a single execution fixed
both while surfacing a cost fact no amount of reading would have produced.

## Reconnaissance: the schema, and the finding that constrains the first experiment

One run with a forced tool call, then four one-line variations. Nine `stream-json` events per run. Total
cost of the whole reconnaissance under two dollars.

### The event schema, confirmed

| Event | Carries |
|---|---|
| `system` / `hook_started`, `hook_response` | Ambient hooks firing — observable, so it can be recorded rather than assumed |
| `system` / `init` | **`tools` (the exact array)**, `mcp_servers` with per-server status, `model`, `permissionMode`, `cwd` |
| `assistant` | `message.content[]` with `text` and `tool_use` blocks; `tool_use` gives `id`, `name`, `input`; plus `timestamp`, `request_id`, `parent_tool_use_id` |
| `user` | `tool_use_result`, and a `tool_result` content block paired by `tool_use_id` with `is_error` |
| `rate_limit_event` | `status`, `rateLimitType`, `overageStatus`, `isUsingOverage`, `resetsAt` |
| `result` / `success` | `num_turns`, `stop_reason`, `total_cost_usd`, full `usage`, `modelUsage` by model id, **`permission_denials`** |

Two of those were not anticipated and both are useful. **`init.tools` means the tool surface does not
have to be asserted — it can be read back from the run itself**, which is what constraint 2 of ADR 0010
wants a hash of. And `permission_denials` plus `is_error` on a tool result give a second, independent
angle on wrong-tool counting beyond comparing names against an allowed set.

Calibration: one tool call produced `num_turns: 2`, so turns run about one more than tool calls.

### The finding: `--allowedTools` does not scope the visible surface

Four runs, same trivial prompt, one flag changed at a time:

| Configuration | Visible tools | MCP servers | Cost |
|---|---|---|---|
| Baseline, no flags | 54 | 25 | $0.2208 |
| `--allowedTools "Read"` | **54** | 25 | **$0.2208** |
| `--strict-mcp-config` | **30** | 0 | $0.1967 |
| Both | 30 | 0 | $0.1967 |

`--allowedTools` changed nothing — identical tool count and identical cost to the cent. It is a
**permission** filter, not a visibility control. The model still sees every name.

**That breaks the first experiment as designed.** `theory/agents/tool-surface-design.md`'s claim is that
selection happens over resident *names*, so an arm that keeps all 54 names resident and merely forbids
calling them does not reduce selection complexity at all. It would have measured nothing, and it would
have looked like it worked.

`--strict-mcp-config` does work: 54 → 30 tools, 25 → 0 servers. **But the remaining 30 are built-in and
no flag tested removes them.** The scoped arm therefore has a floor of 30, so the intended contrast of
roughly 5 versus 90 is not reachable this way.

### The mechanism, found by continuing to probe: `--disallowedTools`

Three more runs settled it, and the answer is an asymmetry between two flags that read like a pair:

| Flag | Effect on the visible surface |
|---|---|
| `--allowedTools` | **None.** 54 → 54. A permission allowlist only |
| `--disallowedTools` | **Removes names from visibility.** Every tool named disappears from `init.tools` |
| `--agents <json>` | **None** on a `-p` main-agent run. 30 → 30. It declares agents available to invoke, not the caller's own surface |
| `--strict-mcp-config` | Drops all MCP tools **and disconnects the servers**. 54 → 30, servers 25 → 0 |

Naming eleven tools took the surface from 30 to 21. Naming the full built-in set took it to **three:
`Glob`, `Grep`, `Read`.**

### `--disallowedTools` accepts MCP tool names, which removes a confound

Added after the proposal phase flagged it, and it matters more than it looks. The route above reached 3
tools using `--strict-mcp-config` **plus** `--disallowedTools` — but `--strict-mcp-config` also takes the
MCP server count from 25 to 0. That is a **second variable**, and an experiment with two variables cannot
attribute its result to either.

Tested directly by naming two MCP tools and nothing else:

| | Result |
|---|---|
| Visible tools | 54 → **52** — exactly the two named disappeared |
| `mcp_servers` | **25, unchanged.** Servers stay connected |
| An MCP tool *not* named | Still visible |

So the scoped arm can reach 3 tools through **one mechanism only**, with every MCP server still
connected. `--strict-mcp-config` is not needed and should not be used, because it changes connection
state as well as surface.

That is the difference between a single-variable comparison and a confounded one. Both arms pay identical
MCP connection overhead; **only the tool names differ**, which is exactly the quantity
`theory/agents/tool-surface-design.md` claims selection happens over.

**So the first experiment is executable at full contrast after all: 54 versus 3, a factor of 18.** That
is the shape ADR 0010 wanted, and it happens to sit at the same order as the *"18 instead of 4-5"*
illustration in `research/claude-certified-architect-exam-guide.md` that
`theory/agents/tool-surface-design.md` is built on. The design was never wrong — the flag was.

### The cost axis, and why it makes the experiment cleaner than expected

| Surface | Cost of a trivial run |
|---|---|
| 54 tools, 25 MCP servers | $0.2208 |
| 30 tools, 0 MCP servers | $0.1967 |
| 3 tools | $0.2012 |

Going from 54 names to 3 changed cost by about **$0.02, roughly 9%**, and the ambient context in every
one of those runs was ~26k tokens. So **the names are nearly free and the ambient context dominates** —
which is `theory/agents/capability-load-cost.md`'s claim showing up in a third harness.

That is not a footnote, it is what makes the experiment clean: **because 51 extra tool names cost almost
nothing, any difference between the two arms in wrong-tool calls or task success cannot be attributed to
cost.** The confound that would have muddied the result is small enough to set aside, which isolates
exactly the quantity the experiment exists to measure — selection reliability.

Recorded as **observations, not measurements**: single runs, no repeats, no variance, and two runs
sharing a configuration returned byte-identical costs, so caching is doing work these deltas do not
separate out. ADR 0010's constraint 3 exists for precisely this reason.

Also observed: `permissionMode` came back as `bypassPermissions` without anyone asking for it, inherited
from ambient settings. Another instance of the configuration this machine supplies silently, and now
recorded per run because `init` reports it.

## Negative result, recorded because it kills an option cheaply

**`gentle-ai` / `gga` carry no usable telemetry.** Local review-context files under the tool's own state
directory follow schema `gentle-ai.review-repository-context/v1` and hold lineage, target and repository
identity hashes only. No token, cost, usage or tool-call field in anything sampled. That is unsurprising:
it is a content-hash review-lineage system, a different domain. Sampled rather than exhaustive.

## The design fork this phase surfaced and did not resolve

Two instrumentation paths exist and they measure different things. This belongs to `sdd-propose`.

| Path | Measures | Cost |
|---|---|---|
| Claude Code headless CLI (`claude --bare -p --output-format stream-json`) | The **actual product harness** — the same surface the existing `theory/agents/` observations were made on | Carries the product's own behaviour, which is the point and also a confound |
| The Anthropic API / SDK directly | A **harness we construct**, with total control of the tool surface and no product behaviour in the way | Measures our rig, not the tool anyone uses |

The CLI path is recommended for v1 on the grounds that this repo's existing claims are about that
harness, so measurements should be comparable to them. `--output-format json` is **insufficient** — it
returns only the final aggregate. `stream-json` is required, because wrong-tool-call counting needs the
per-call transcript.

## Open, and explicitly not resolved here

- ~~Turn-count field name is unconfirmed.~~ **Closed** — it is `num_turns`. Closed by doing exactly what
  this item said to do: one real run before writing any parser.
- **No per-invocation loop bound is available.** `claude --help` exposes no `--max-turns` in this version.
  ADR 0010 requires bounded runs, so where the bound comes from is an open spec question — a wall-clock
  timeout around the process, a cost ceiling checked after the fact, or something else.
- **"Wrong-tool call" still has no per-task definition.** Pre-existing gap, recorded in ADR 0010 and
  unchanged by this phase. It is a `sdd-spec` input.
- **No driver-script language is established in this repo.** Only Bash exists today. A `sdd-design`
  decision.
- **Using the internal transcript format as the primary source would be a maintenance trap.** It is
  undocumented and can change without notice. Use `stream-json` as the contract and the on-disk
  transcript only as a cross-check.

## A note on the exploration's own scope claim

The sub-agent reported that the `claude-api` and `claude-code-guide` skills "do not exist on this
machine" and substituted live documentation fetches. Half right, and the distinction matters: they are
not resolvable as files under the agent skills directory, which is why a sub-agent could not load them —
but `claude-api` **is** available to the main session as a skill. Its conclusions stand, because the API
field names were independently confirmed against a real on-disk transcript rather than resting on the
fetch alone. Recorded so a later phase needing authoritative API facts loads the skill instead of
fetching docs.
