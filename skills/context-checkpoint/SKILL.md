---
id: skills/context-checkpoint
type: skill
targets: [any]
status: draft
verified: 2026-08-05
sources: ["journal/2026-08-05-context-measurement.md", "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents", "research/claude-certified-architect-exam-guide.md"]
---

# context-checkpoint

Close a work unit so the conversation can be cleared without losing anything, and so the next
session resumes without re-deriving what this one established.

`status: draft` — **still draft, deliberately.** The design choice below now has first-party support:
Anthropic's architect guide states that starting a new session with a structured summary is more
reliable than resuming with stale tool results, recommends scratchpad files for persisting key
findings across context boundaries, and describes context degradation behaviourally — models
"referencing 'typical patterns' rather than specific classes discovered earlier" — with no token
threshold attached (`research/claude-certified-architect-exam-guide.md`).

That strengthens the *rationale*. It does not satisfy this file's stated promotion criterion, which
is that **the loop has been run end-to-end enough times to know it works.** It has not. External
agreement about a design is not evidence that this particular procedure executes cleanly, and
conflating the two would be the scope error `skills/source-verdict` test 3 exists to catch.

Promote when there are recorded end-to-end runs, not when a better citation arrives. Do not cite as
validated practice.

## When to invoke

**On finishing a unit of work.** Not on a token count. See
`journal/2026-08-05-context-measurement.md` for why the token-threshold design is rejected:
surfacing a remaining-context countdown to the model is a documented cause of premature
wrap-up behaviour, so the obvious automation risks causing the failure it means to prevent.

Behavioural signals that a checkpoint is already overdue:

- Re-deriving a fact the conversation settled earlier
- Contradicting a decision made earlier in the same session
- Losing the distinction between what was *verified* and what was *assumed*
- Reaching for a file that was already read and summarised

Any one of those means clear now, not later — the degradation has already started.

## What this skill does NOT do

**It cannot clear the context and continue in the same turn.** A command runs inside the context
it would destroy; there is no "clear and carry on" in one step. Any design promising that is
confused about where the instruction lives.

The loop is therefore two halves with a human keystroke between them:

| Half | Who runs it | Mechanism |
|---|---|---|
| 1. Persist | this skill | memory write + a handoff file on disk |
| 2. Rehydrate | the harness, automatically | session-start hook reads memory back |

Half 2 already works — a session-start hook that injects prior-session memory is an existing,
observed capability, not something this skill needs to build. The only manual step is the clear
itself, and that is correct: discarding a conversation is not a decision to automate.

## Procedure

### 1. Write the handoff file first

`journal/YYYY-MM-DD-<slug>-handoff.md`, following the frontmatter contract in `AGENTS.md`
(`type: journal`, `status: draft`). It must carry, in this order:

1. **Where we stopped** — the exact next action, phrased so it can be executed without
   reconstruction.
2. **Versions and identifiers** — tool versions, lineages, issue numbers, commit SHAs. These are
   the facts most expensive to re-derive and the first to go stale; record them with dates.
3. **What is verified vs. assumed** — the single most valuable section, and the one a summary
   always drops. An unmarked assumption becomes a fact in the next session.
4. **Open items, explicitly not resolved** — including the ones deliberately left open, and why.
5. **What the conversation established that no file records** — the reasoning that would
   otherwise die with the context.

Write it as if the reader has none of the conversation, because they will not.

### 2. Persist to memory

Save a session summary through whatever persistent-memory surface the runtime provides. Memory
and the handoff file are not redundant: memory survives without the repo, the file survives
without the memory backend, and each is readable when the other is unavailable.

### 3. State the resume point in the reply

Name the handoff file and the next action in the final message, before the clear. The user is
about to lose the conversation; the last thing they read should be what happens next.

### 4. Then the human clears

Not the agent. The agent's job ends at "safe to clear."

## Why a summary is not a checkpoint

Compaction and summarisation preserve *what was said*. A checkpoint preserves *what is true and
what is next*. The difference shows up on resume: a summary hands the next session a narrative it
must re-interpret, while a handoff hands it a state it can act on.

Concretely, the failure a summary produces: it flattens "verified against the tool output" and
"seemed right at the time" into the same confident past tense. The next session inherits the
confidence without the evidence — and that is indistinguishable from a hallucination, except
that it was self-inflicted one session earlier.
