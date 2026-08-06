---
id: skills/source-verdict
type: skill
targets: [any]
status: validated
verified: 2026-08-06
sources: ["research/README.md", "AGENTS.md", "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents", "https://arxiv.org/abs/2603.08274", "research/agent-loop-oracle.md", "research/agent-loop-termination-kinney.md"]
---

# source-verdict

Decide whether a received source — post, blog, thread, paper, PDF, course, vendor doc — carries
knowledge you can build on, and close it with a verdict that `research/` can hold.

Produces the five-section entry `research/README.md` requires: Claim, Source, Contrast, Verdict,
Follow-up.

## The rule this skill exists to prevent

**Do not adjudicate by author.** "Only trust reputable authors" is an authority heuristic, and it
is exactly what lets a credentialed person publish an unfounded claim unchallenged. It also fails
in the other direction: it discards a checkable claim because of the genre it arrived in.

Reputation is a **prior** — it tells you how hard to look. It is never the verdict.

The verdict comes from one question: **are the claims checkable, and did you check them?**

## Score claims, not documents

A single piece routinely carries a sound claim and a false one. Extract each claim separately and
give each its own verdict, then summarise the document. A document-level verdict destroys exactly
the information you needed.

The corollary matters: **a piece that sells hard can still contain a true claim, and a sober piece
can be wrong.** Tone is not evidence.

## The eight tests

Run them in this order. The first three decide most cases.

### 1. Falsifiability

Could the claim turn out false? If no observation would contradict it, it is not a claim — it is a
position, and positions cannot be supported or refuted.

- Not a claim: *"graphs are the outermost edge of AI engineering."*
- A claim: *"fabrication exceeds 10% at 200K tokens across 35 open-weight models."*

### 2. Number provenance

Is there a number, and where did it come from? Three tiers, and the gap between them is large:

| Tier | What it means |
|---|---|
| Measured by the author, method disclosed | Strongest. You can attack the method |
| Cited to a named source | Checkable. Go check it — the citation is often weaker than the claim it is used for |
| No number, or a number with no method | Decoration. Not evidence |

#### Repetition is not provenance

**Before counting agreement between sources, resolve their attributions to an origin. If they resolve
to the same one, N is 1.**

A figure with no disclosed method does not improve by appearing in more places. Two documents quoting
one unsourced number is *one unsourced number appearing twice* — and it reads exactly like independent
confirmation, which is what makes this worth a rule rather than a remark.

The distinction that keeps this from becoming blanket suspicion of any repeated figure:

| Shared root | Verdict on the repetition |
|---|---|
| A named, reachable source — a paper, a public benchmark, a dated dataset | **Legitimate.** Both cite something that can be attacked. Go attack it |
| An undisclosed internal measurement, a vendor's "internal data", an unattributed anecdote | **Adds nothing.** Count it once, and once is not enough |

The test is whether the shared root is **reachable**, not whether it is shared.

Worked example, from this repo: two agent-loop articles — an independent practitioner synthesis and a
vendor engineering post, three months apart, no other overlap — both report ~4x/15x token multipliers
and a 90.2% multi-agent result, both attributed to the same vendor's internal data, neither with a
method. Read alone, either looks like a source. Read together, they look like consensus. They are one
unsourced figure. See `research/agent-loop-termination-kinney.md` and `research/agent-loop-oracle.md`.

The same two pieces also agree on layered loop-termination guidance without citing each other, and
**that** agreement does carry weight, because it is convergence on design reasoning rather than a relayed
number. Same pair of sources, opposite conclusions about what their overlap proves. Ask which kind of
overlap you have before you count it.

Corollary for a corpus rather than a pair: a set assembled from what circulates is **selected for
circulation**, so the most-repeated figure in it is the one to distrust first, not the one to trust.

### 3. Scope

What population does the evidence cover, and is the claim wider than the evidence? **This is the
most common failure in otherwise honest work**, and the hardest to notice because nothing looks
wrong.

Worked example: arXiv:2603.08274 measures 35 **open-weight** models at 32K/128K/200K. It is real
evidence. A claim about frontier proprietary models at 1M context is **outside its scope**, and
citing it there is misuse of a good source.

### 4. Self-contradiction

Does the piece contradict itself? Cheap to check and decisive when it hits. A document that
argues both sides of its own thesis has told you its thesis is not load-bearing.

### 5. Urgency

Does the value of acting depend on acting *now*? Real knowledge does not expire in weeks.
"The window is closing", "before the crowd catches up", "years ahead" are sales mechanisms.

Important: urgency is evidence about the **author's incentive**, not about the claim's truth. It
lowers your prior and tells you to check harder. It does not refute anything by itself.

### 6. Incentive

What does the author get if you believe this — a course, a cohort, consulting, subscriptions,
followers? Not disqualifying; everyone has incentives. It tells you *which* claim to attack first:
the one the sale depends on.

### 7. First-party

For a claim about how a specific tool or model behaves, who is speaking?

| Source | Weight |
|---|---|
| The vendor's own engineering documentation | Strongest for that vendor's behavior |
| A third party quoting named engineers at the vendor | Attributed second-hand. Usable, labelled |
| A third party with no attribution | Not evidence about the vendor |

Vendor-bound behavior stays labelled as vendor-bound. It is not a general law.

### 8. Local reproduction

**The strongest test, and the one almost nobody runs.** Can you reproduce any part of the claim in
your own environment?

A source that survives local reproduction outranks any credential. A source that fails it is
refuted no matter who wrote it. When a claim is reproducible and you did not reproduce it, say so
in the Contrast section — that is a gap in your work, not in the source.

## Verdict

Map to the enum `research/README.md` defines. The reason is mandatory; a bare verdict is not
reviewable.

| Verdict | Use when |
|---|---|
| `supported` | Checkable claims, checked, and they held. Scope stated |
| `partially supported` | Some claims held, others failed. **Say which** |
| `refuted` | A load-bearing claim failed a test you ran |
| `unverifiable` | No falsifiable claim, or the evidence is not reachable. **Not a synonym for false** |

`unverifiable` is the verdict for most curricula, opinion pieces and taxonomies. They can still be
useful — as maps, vocabulary or checklists. Record that use, and record that it is not evidence.

## What survives into theory/

A verdict is not knowledge yet. Promote to `theory/` only when:

- The claim passed falsifiability, number provenance and scope, and
- `sources` can be filled with material a reader can open, and
- the claim is stated no wider than the evidence supports.

If a claim is only true for one vendor, one version or one measurement, the `theory/` file says so
in the body. A theory file that hides its scope is worse than no file — it will be cited later as
a general law.

## Do not delete refuted sources

Per `research/README.md`, a `refuted` source stays in the repo as `status: rejected`. Deleting it
loses the refutation and invites re-importing the same bad claim in six months, usually from a
different author who read the same original.
