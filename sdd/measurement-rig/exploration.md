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
| Controllable tool surface | **Available** | `--allowedTools` / `--disallowedTools` per invocation, and `--agents <json>` for a declared subagent tool set |

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
