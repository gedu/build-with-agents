---
id: upstream/gentle-ai/duplicated-review-lens-rules
type: research
targets: [any]
status: validated
verified: 2026-08-05
sources: ["https://github.com/Gentleman-Programming/gentle-ai/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml", "journal/2026-08-05-context-measurement.md"]
---

# Report 0002 — review-lens selection is generated twice with divergent wording

**Copy-paste sheet.** Each `## FIELD n` heading matches one field of the upstream Bug Report
form, in form order. Copy between one heading and the next, paste, move on.

Open with `gh issue create --repo Gentleman-Programming/gentle-ai --web`, pick **Bug Report**.
Use the web form, not `--body-file` — the form is what applies the default `bug` and
`status:needs-review` labels.

Two things only you can do: **FIELD 1** (pre-flight checkboxes) is an attestation by whoever
submits — tick it yourself. And **submitting**, which publishes under your GitHub identity.

---

## TITLE

```
Generated CLAUDE.md states review-lens selection twice with divergent tier wording
```

---

## FIELD 2 — 📝 Bug Description

`gentle-ai sync` writes review-lens selection rules into `~/.claude/CLAUDE.md` twice, in two
different managed blocks, using two different wordings of the same tier thresholds.

The `<!-- gentle-ai:sdd-orchestrator -->` block contains a "Review Lens Selection" section. The
`<!-- gentle-ai:trigger-rules -->` block contains the same decision procedure again. The
identical 4-row risk table appears in both — once as a Markdown table, once inlined as prose.

Exact duplication would only waste tokens. These two differ in wording, which is worse: an agent
reading the file has to decide whether they express one rule or two, and there is no way to tell
from the file.

The High-risk line-count threshold is the clearest case:

- sdd-orchestrator block: `>400 changed lines outside pure human documentation`
- trigger-rules block: `more than 400 authored changed lines in code, configuration, prompts, agent rules, workflows, runtime instruction docs, mixed content, or active content`

Those may be intended as the same rule, but "changed lines outside pure human documentation" and
"authored changed lines in [enumerated list]" are not the same predicate. A diff of 500 changed
lines in generated goldens classifies differently depending on which sentence the agent applies.

---

## FIELD 3 — 🔄 Steps to Reproduce

1. Install gentle-ai and run its sync so `~/.claude/CLAUDE.md` is generated.
2. Open `~/.claude/CLAUDE.md`.
3. Find the `## Review Lens Selection` section inside the `gentle-ai:sdd-orchestrator` managed
   block (in this installation, lines 239–255).
4. Find the `## Agent Trigger Rules` section inside the `gentle-ai:trigger-rules` managed block
   (lines 310–326).
5. Compare the tier definitions and the risk table between the two.

---

## FIELD 4 — ✅ Expected Behavior

One authoritative statement of lens selection in the generated file, with the other block
referencing it rather than restating it. If both blocks must be self-contained for independent
installation, the two statements should be byte-identical for the shared rules so no
reconciliation is possible.

---

## FIELD 5 — ❌ Actual Behavior

The rule is stated twice with different predicates for the same tier boundary. Both statements
are presented as authoritative decision procedures — one says "this is a decision procedure, not
advice", the other says "apply it as a decision procedure, not advice" — so neither reads as the
subordinate copy.

Because the whole file sits inside `gentle-ai` marker pairs, a user cannot fix this locally: the
next sync overwrites the edit. The fix has to be upstream.

---

## FIELD 6 — Gentle AI Version

```
gga v2.10.1 (gentle-ai 2.2.4, Homebrew)
```

---

## FIELD 7 — Operating System

Select: **macOS**

---

## FIELD 8 — AI Agent / Client

Select: **Claude Code**

---

## FIELD 9 — 📋 Affected Area

Pick from the live dropdown — closest match is the generated agent-rules/instructions area. If
no such option exists, **CLI (commands, flags)** is the fallback, since `sync` is what writes
the file.

---

## FIELD 10 — 💡 Logs / Error Output

Plain text only — this field auto-renders as a shell block, so do not add fences.

```
$ rg -n 'Review Lens Selection|Agent Trigger Rules|400' ~/.claude/CLAUDE.md

239:#### Review Lens Selection
245:3. **Hot path** ... or >400 changed lines outside pure human documentation ...
246:4. **Large pure human documentation** (>400 authored lines with no code, ...
311:## Agent Trigger Rules
317:... or more than 400 authored changed lines in code, configuration, prompts,
    agent rules, workflows, runtime instruction docs, mixed content, or active content) ...
```

---

## FIELD 11 — Additional Context

Found while auditing the always-on instruction surface for token cost. Worth noting for
prioritisation: measured with Claude Code's `/context`, the whole generated `CLAUDE.md` is 10.3k
tokens — about 2% of a 502k-token session. **So this is not a cost problem.** The cost of the
duplication is the reconciliation an agent has to perform between two differently-worded
authoritative rules, which is a correctness risk rather than a budget one.
