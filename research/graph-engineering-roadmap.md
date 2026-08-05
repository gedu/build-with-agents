---
id: research/graph-engineering-roadmap
type: research
targets: [any]
status: validated
verified: 2026-08-05
sources: ["Untitled social post, 'Phase 1–5 / Steps 1–20' graph engineering roadmap, pasted in full 2026-08-05. No canonical URL supplied; author not identified."]
---

# The 20-step "graph engineering" roadmap

## Claim

Two distinct claims travel together in this piece, and they must be scored separately because one
is technical and one is commercial.

1. **Technical**: agentic work is built from loops (action → result → check → repeat); a graph is
   many loops wired together via nodes, edges and state; five patterns cover most real systems
   (router, orchestrator-worker, parallel fan-out/fan-in, evaluator-optimizer, human-in-the-loop
   gate); reliability comes from validation gates, recovery paths, checkpoints and observability;
   and the senior skill is knowing when *not* to build a graph.
2. **Commercial**: "graph engineering" is a two-week-old term; learning it now puts you "years
   ahead"; the opportunity window is closing as the crowd catches up; six to eight weeks of
   practice yields a skill "almost nobody could do a month ago".

## Source

Social-post format, pasted in full. **No URL, no author, no citations, no numbers anywhere in the
piece.** By test 2 (number provenance) the entire document is at the bottom tier: there is nothing
to check.

## Contrast

**On the technical claims — largely sound, and unoriginal in a good way.** Three are strong enough
to keep:

- *"A loop with a weak verifier produces confident garbage fast."* This is the load-bearing idea in
  the whole piece, and it is correct.
- *Not every node should be an LLM; most should be plain functions.* Correct and under-stated
  elsewhere.
- *Knowing when not to build a graph is the real graduation.* Correct.

The five patterns are standard orchestration shapes, and Phase 4 (gates, recovery paths, state
persistence, tracing) is ordinary reliability engineering. None of it is wrong. None of it is new.

**On the commercial claims — refuted, by the document itself.** It opens with "the term is two
weeks old" and an urgency argument built on that novelty, then later states the underlying skill has
been *"valuable for years under other names."* Both cannot hold: if the skill is old, being early to
the **label** buys nothing, which is the opposite of the piece's own thesis. That is a
self-contradiction on the load-bearing sales claim (test 4).

Independently: node/edge/state orchestration is not two weeks old. Graph-orchestration frameworks
predate this post by years, and the shape — a directed graph of tasks with conditional routing and
shared state — is decades old in dataflow and workflow scheduling.

The "years ahead", "window closing" and "almost nobody could do this a month ago" claims are
unfalsifiable (test 1) and are the classic urgency pattern (test 5). Test 6 identifies what the
urgency is for: the piece is shaped to sell a learning path.

**Locally relevant, and the reason this entry is worth keeping.** Its Phase 4 — validation gates,
recovery paths, checkpoints, observability — describes work already done and already painful in this
repo: the `gentle-ai` review gate as validation gate, two documented bypasses as the missing
recovery path, `skills/context-checkpoint` as state persistence, and the journal entries as tracing.
Its Phase 1 Step 3 (the verifier is everything) is precisely the defect that blocked both commits
on 2026-08-05: the verifier could not run.

So the roadmap's own framing places this repo mid-Phase-4, not at Step 1 — and by its own Step 19,
this project's stated goal (an install command and a project auditor) does not need a graph at all.

## Verdict

**`partially supported`.**

- **Supported**: the loop-before-graph ordering, the primacy of the verifier, mixed LLM/deterministic
  nodes, the five patterns, and the restraint principle. All standard, all correct, none original.
- **Refuted**: novelty, urgency, and the closing-window framing — contradicted by the document's own
  later text and by the actual age of the practice.
- **Not evidence for anything**: zero numbers, zero citations, unattributed.

Usable as a **curriculum checklist**. Not citable as evidence for any claim about how agentic
systems behave.

## Follow-up

No `theory/` promotion. It contains no measurement, so nothing in it can satisfy the
`theory/` sources requirement on its own — the sound claims need independent evidence before they
can be written as knowledge here.

Kept as the worked example in `skills/source-verdict` of a document whose technical spine and
commercial packaging deserve opposite verdicts. Retained rather than deleted per
`research/README.md`, so the refutation survives the next time the same claim arrives from a
different author.
