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
| Turn count | **Partial** | No confirmed single field. Proxy: count assistant messages in the stream. Cheap and exact |
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

- **Turn-count field name is unconfirmed.** Resolve empirically: one real run, inspect the actual result
  line, then write the parser. Do not write the parser first.
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
