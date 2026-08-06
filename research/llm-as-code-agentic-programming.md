---
id: research/llm-as-code-agentic-programming
type: research
targets: [any]
status: validated
verified: 2026-08-06
sources: ["https://arxiv.org/abs/2606.15874", "https://arxiv.org/html/2606.15874v2", "theory/loops/verifier-availability.md", "theory/agents/capability-load-cost.md"]
---

# LLM-as-Code: Agentic Programming for Agent Harness (arXiv:2606.15874)

## Claim

That token explosion, control-flow hallucination and unreliable completion in LLM agents are
**architectural consequences of giving a probabilistic system the deterministic work of looping,
branching and sequencing** — not implementation bugs — and therefore that control flow belongs in
the program, with the model invoked only where reasoning or generation is actually required.

Stated by the authors in a form that is unusually direct for a paper: *"A better prompt or a stronger
model cannot guarantee the reliability of the LLM agent."*

## Source

arXiv:2606.15874v2, *LLM-as-Code: Agentic Programming for Agent Harness*. Qi, Fu, Gao, Zhang, Yan,
Wu, Zhao. Submitted 2026-06-23. Corresponding author at City University of Hong Kong.

Accessed 2026-08-06. The PDF body did not extract; the HTML rendering did, and the numbers below were
re-fetched a second time with a verbatim-quote-only request before being written down here, because a
reader's summary of a paper is not the paper.

**Not vendor-affiliated.** Academic authors, evaluating against a public benchmark and a public
leaderboard, with no product being sold. By `skills/source-verdict` test 6 there is no incentive
pointing at a particular result.

## Contrast

**The central claim converges with the strongest thing already written in this repo, from a
completely independent direction.** `theory/loops/verifier-availability.md` carries a three-layer
enforcement model — prompt policy < runtime permission < native code — and concludes that emphatic
instruction wording is weak evidence of enforcement, because *"the practical test is not to read the
rule but to ask which layer implements it."* That was derived from one vendor's guidance plus local
incidents.

This paper reaches the same place empirically and states it more strongly: the deterministic work
should be **in the program**, and no amount of prompting substitutes. Two independent derivations,
one normative and one measured, is materially better evidence than either alone.

**A second convergence, with the cost axis.** The paper argues context grows **O(depth)** rather than
O(steps × average output), because each call's context is its ancestor chain in a DAG with returned
subtrees collapsed to summaries: *"no call ever carries the whole task's history, only its ancestor
chain."* That is `theory/agents/capability-load-cost.md`'s claim — cost is a function of what is
resident, not of what exists — arriving in a third domain, after tools and after delegated artifacts.

**Local reproduction (test 8): not run.** No OSWorld harness exists here and none was built. This is
recorded as a gap in this entry, not as a weakness of the source.

### The numbers, and the seam in them

Verbatim from Table 1, *"GUI automation on OSWorld (Xie et al., 2024) (overall success %)"*, whose
columns are `Method | Max Steps | Overall`:

| Method | Max Steps | Overall |
|---|---|---|
| LLM-as-Code w/ Claude Sonnet 4.6 | 15 | **86.8** |
| Holo3-35B-A3B | 100 | 80.4 |
| OpenAPA w/ Gemini-3.1-pro | 100 | 78.3 |
| Claude Sonnet 4 | 100 | 72.1 |

Per-domain, at 15 steps against baselines at 100: Chrome 93.5 (best baseline 78.3), Multi-Apps 80.0
(65.7), OS 100.0 (95.8).

**The seam, and it is the reason this entry is scoped rather than endorsed.** The paper discloses it
plainly: *"Baseline numbers are from its public leaderboard (accessed 2026-06-02) and run up to 100
steps; Ours wins in 15 steps."*

So a single comparison mixes two provenance tiers from `skills/source-verdict` test 2. The 86.8% is
**measured by the authors**. Every baseline is **cited to a leaderboard** the authors did not re-run.
That is honest reporting and it is still not a head-to-head: the baselines were produced by other
harnesses, on other dates, under conditions nobody controlled for. Disclosure removes the charge of
concealment, not the confound.

Two further scope limits:

- **One model.** The result pairs Agentic Programming with Claude Sonnet 4.6 only. The claim "this
  architecture is better" rests on n=1 model on n=1 benchmark.
- **The authors bound their own claim**, which raises confidence in the rest of it: Agentic
  Programming *"does not subsume fully exploratory tasks"* and is claimed effective *"when a workflow
  has a known structure."*

The step-count gap is the part that survives every objection. 15 versus up to 100 is large enough
that leaderboard noise does not plausibly account for it, and step count is a cleaner quantity than
success rate because it is bounded by construction rather than measured.

## Verdict

**`supported`**, scoped tightly.

- **Supported** for the architectural claim, which is the load-bearing one and which is corroborated
  independently by first-party vendor guidance already adjudicated in this repo.
- **Supported, narrowly**, for the efficiency result: one model, one benchmark, GUI/computer-use
  tasks, with baselines taken from a leaderboard rather than re-run. Cite it as *"86.8% at 15 steps
  versus leaderboard baselines at up to 100 steps on OSWorld"* — never as *"LLM-as-Code beats agent
  frameworks."* The second sentence is wider than the evidence.
- **Not evidence** for anything about non-GUI agents, other models, or exploratory workflows. The
  authors say so themselves.

## Follow-up

Promote into `theory/loops/`. It is the first **measured** support this repo has for the claim that
deterministic control belongs outside the model, and the existing enforcement section in
`theory/loops/verifier-availability.md` currently rests on normative guidance plus local incidents.
Add it there as independent corroboration with its scope attached, rather than starting a new file —
the claim is the same claim.

Also worth a line in `theory/agents/capability-load-cost.md`: the O(depth) context argument is that
file's shape in a third domain, and the file already invites exactly this kind of extension.
