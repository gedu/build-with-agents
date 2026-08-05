---
id: theory/agents/tool-surface-design
type: theory
targets: [any]
status: validated
verified: 2026-08-05
sources: ["research/claude-certified-architect-exam-guide.md", "theory/agents/capability-load-cost.md"]
---

# A tool surface is a prompt, so its reliability is edited in the names and descriptions

**The claim.** When a model chooses a tool, it is reading. The material it reads is the **resident**
part of the tool surface — names and descriptions — and choosing well is a comprehension problem over
that text. Schemas, which hold most of the bytes, do not participate in the choice.

The consequence is where this file earns its place: **every lever that improves selection reliability
is an editing act on resident text** — how tools are named, how responsibilities are split between
them, and which ones a given role can see at all. None of those levers is deferral, and deferral is
not a substitute for any of them.

This file is the other half of `theory/agents/capability-load-cost.md`. That one establishes the cost
axis and ends by naming scoping as the reliability lever without developing it. This one develops it,
and keeps the two axes apart on purpose.

## What is actually resident at the moment of choice

Observed first-hand in the session that produced this file, on Claude Code with `claude-opus-5[1m]`,
and recorded in more detail in `theory/agents/capability-load-cost.md`: roughly 90 MCP tools were
connected and callable, their **names** resident, their **parameter schemas absent** until an explicit
lookup loaded one.

Read that observation again for what it says about *selection* rather than about cost. At the instant
the model decides which tool to call, it has not seen the parameter contract of any candidate. It has
seen a list of names and whatever description text accompanies them. So the decision is made on the
cheapest part of the surface, and the expensive part arrives only after the decision is already made.

That ordering is the whole reason the levers separate. **The surface that costs the most is not the
surface the model chooses from.** Optimising bytes and optimising choices act on different text.

## The three levers, and what each one acts on

All three are first-party recommendations from Anthropic's architect guide, adjudicated in
`research/claude-certified-architect-exam-guide.md`. Normative guidance, no measurements — see Scope.

**1. Descriptions are the mechanism, not documentation.** The guide states that tool descriptions are
the primary mechanism a model uses to select tools, and that minimal descriptions produce unreliable
selection among similar tools. Note the qualifier: *among similar tools*. A thin description is
harmless when a tool is the only plausible candidate and decisive when it is one of three. So
description quality is not a per-tool property — it is a property of each tool **relative to its
nearest neighbours on the surface**.

**2. Split and rename until responsibilities stop overlapping.** The guide's recommendation for
unreliable selection is to split generic tools into purpose-specific ones with defined input/output
contracts, and to rename tools to remove functional overlap. Both moves change nothing about what the
agent can do; they change only what the model reads. A tool that could plausibly answer two different
requests is not an ambiguous capability — it is an ambiguous **name**, and renaming is a real fix
rather than cosmetics.

**3. Scope by role, with narrow exceptions.** The guide states that agents holding tools outside their
specialization tend to misuse them, and recommends scoped per-role tool access with narrow cross-role
exceptions. This is the only lever that works by **removing candidates from the surface** instead of
clarifying them, which is why it is the one deferral cannot imitate: deferral removes schemas from the
window while leaving every name in the choice.

## Why the levers are not interchangeable

The distinction `capability-load-cost.md` draws between cost and selection, extended across all four
failure modes a tool surface actually has:

| Failure | What it looks like | Lever that acts on it |
|---|---|---|
| Schema bytes crowd the window | Context consumed before work begins | **Deferral** |
| Two tools could both plausibly serve the request | Wrong-but-reasonable calls; retries | **Descriptions**, then **splitting / renaming** |
| Many candidates raise decision complexity | Degraded selection as the surface grows | **Scoping** — fewer candidates, not clearer ones |
| A tool outside the role's specialization gets used | Competent-looking misuse | **Scoping** — the tool should not be visible |

Two rows are worth stating plainly because they are where the reasoning usually goes wrong.

**Deferral appears in exactly one row.** It is a byte-level mechanism and it has no effect on the other
three, because the text it removes is not the text the model reads to choose.

**Rows two and three are different problems that both present as "wrong tool called".** Ambiguity is
fixed by writing; count is fixed by removing. Applying the wrong one is silently ineffective — polishing
descriptions on a 90-tool surface makes each candidate clearer while leaving 90 candidates, and pruning
to five near-identical tools leaves five things a model still cannot tell apart.

## The tension neither source states

**This section is local reasoning, not a sourced claim.** It is what the two recommendations do when
put in the same room, and it is labelled so it does not get cited as first-party.

Lever 2 says split generic tools into purpose-specific ones. Lever 3 says fewer tools select more
reliably. **Splitting raises the count.** Taken together the guide recommends both increasing the
number of tools and keeping it low, and it does not say where the two meet.

The resolution the failure table suggests: splitting and counting act on different failures, so the
trade is real but not symmetric. Splitting one overloaded tool into three unambiguous ones is a good
trade when the three are unambiguous *relative to each other* — the ambiguity is removed and the added
count is confined to a surface the role already needed. It is a bad trade when the split produces
neighbours that need their descriptions read carefully to be told apart, because that converts a
naming problem into a comprehension problem without solving anything.

Which means the operative question is not "how many tools" but **"how many tools could plausibly answer
this request"**. That is the number the failure table says degrades reliability, and no source here
measures it. Treat this paragraph as a hypothesis with a stated shape, available to be tested.

## Consequences for design

- **Write descriptions against the nearest neighbour, not against the tool.** The useful sentence is
  the one that says why *this* tool and not the adjacent one.
- **Treat functional overlap as a naming defect** with a known fix. Rename, or split with explicit
  input/output contracts.
- **Scope by role first.** It is the only lever that reduces candidate count, and candidate count is a
  failure mode no amount of description quality reaches.
- **Do not spend the deferral saving on selection.** A surface can hold many deferred tools at almost no
  token cost and still present the model with an unmanageable choice. The cost audit and the reliability
  audit are separate passes over the same configuration.
- **Audit a surface by asking, per likely request, how many tools could plausibly serve it.** A total
  count answers the cost question, and the cost question is already answered by measuring residency.

## Scope

Every sourced claim here is **normative first-party guidance with no disclosed method** — no
measurements, no sample sizes. The one quantitative hint in the source, tool count *"18 instead of
4-5"*, is offered as illustration and **must not be cited as a measured threshold**; it names a
direction, not a boundary.

The residency observation is first-hand but is **one harness, one model, one session**. The mechanism
is what generalises.

Nothing here is evidence that a scoped surface outperforms a broad one. It is a documented
recommendation plus a mechanism that explains why the recommendation is shaped that way — the same
standing as `theory/orchestration/delegation-and-context-boundaries.md`, and subject to the same
prohibition on being cited as efficacy.

## Deliberately excluded

Two items were listed as available material in
`journal/2026-08-05-knowledge-base-handoff.md` §1 and are **not used here**: MCP resources as content
catalogs to reduce exploratory tool calls, and structured error responses (`errorCategory`,
`isRetryable`) as the enabler of recovery decisions.

Neither appears in `research/claude-certified-architect-exam-guide.md`, which is the adjudicated
verdict written from a full read of the source; that file's own follow-up assigns this file three
claims and assigns structured error propagation to `theory/orchestration/`, where it was never written.
So both currently rest on journal prose alone, and by ADR 0007 a journal is provenance and never
authority. The source PDF is not in this repo and they could not be re-checked.

They are plausible and probably true. They are not verified, and this file is `validated`. Recovering
them needs a re-read of the source, after which structured errors belong in `theory/orchestration/`
rather than here — it is a claim about what crosses a boundary, not about how a tool is chosen.

## What would sharpen it

The measurement no source provides: **the same task against the same capabilities, exposed as a broad
surface versus a role-scoped one**, comparing wrong-tool calls and retries. That isolates the scoping
lever from the deferral lever, which is currently the untested seam between this file and
`theory/agents/capability-load-cost.md`.

A second, cheaper experiment tests the tension above directly: one overloaded generic tool versus the
same capability split three ways, measuring whether selection improves or the added neighbours degrade
it. Neither has been run here.
