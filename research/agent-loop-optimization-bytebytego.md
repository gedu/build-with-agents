---
id: research/agent-loop-optimization-bytebytego
type: research
targets: [any]
status: validated
verified: 2026-08-05
sources: ["https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop"]
---

# How ChatGPT optimizes its agent loop — ByteByteGo

## Claim

An agent loop is made fast by optimisations spread across three layers — harness, API and
inference — including deferred tool discovery, incremental request bodies, stable prompt prefixes
for cache hits, delta tokenization, speculative decoding, and cache-aware request routing.

## Source

`https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop` — accessed 2026-08-05.

Attribution: reporting based on conversations with named engineers who shipped efficiency work
behind Codex and ChatGPT Work. **Not vendor documentation.** Second-hand and attributed, which by
`skills/source-verdict` test 7 is usable when labelled, and is not evidence about the vendor in the
way a first-party engineering doc would be.

## Contrast

**Reproduced locally, and this is the load-bearing part of the verdict.** The article's
harness-layer claim about *deferred tool discovery — loading tool schemas on demand via BM25
lexical ranking* — matches a mechanism observed first-hand in this repo's own session on
2026-08-05: ~90 MCP tools resident by name only, schemas absent, and an explicit keyword-ranked
lookup required before any of them could be called.

Independently measured here: 65.1k tokens of tool schemas declared but not loaded, against 41.4k
tokens of total resident configuration
(`journal/2026-08-05-context-measurement.md`). Two harnesses built by different organisations
converged on the same technique.

**Where the article is weaker than it reads.** Almost all of it describes *mechanisms*, not
*measured improvements*. Exactly one quantitative figure appears — roughly 20% worse time-to-first-
token on older Broadwell CPUs. Every other claim would need the vendor's own numbers to verify, and
those are not given. By test 2, most of this is architecture description, not evidence.

Nothing in it was refuted. The inference-layer claims (speculative decoding, prefill/decode fleet
separation, cache-aware routing) are consistent with published practice but were **not** checked
here and are not relied on.

## Verdict

**`partially supported`.**

- **Supported**, and independently corroborated by local first-hand observation: deferred tool
  schema loading as a harness-level context optimisation.
- **Unverified but plausible and unrefuted**: the API- and inference-layer mechanisms. Specific,
  attributed, and untestable from outside.
- **Not supported as quantitative evidence**: the article contains one number. It is a map of
  techniques, not a measurement study.

Scope: claims are about OpenAI's production systems. They do not generalise to other harnesses
except where independently reproduced — which here, for exactly one claim, they were.

## Follow-up

Promoted to `theory/agents/capability-load-cost.md`, where it serves as the independent
corroboration for a claim whose primary evidence is local measurement. Deliberately **not** cited
there for anything at the API or inference layer.
