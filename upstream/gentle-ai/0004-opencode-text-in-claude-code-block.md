---
id: upstream/gentle-ai/opencode-text-in-claude-code-block
type: research
targets: [any]
status: validated
verified: 2026-08-05
sources: ["https://github.com/Gentleman-Programming/gentle-ai/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml"]
---

# Report 0004 — OpenCode-specific instructions ship inside a Claude-Code-bound block

**Copy-paste sheet.** Each `## FIELD n` heading matches one field of the upstream Bug Report
form, in form order.

Open with `gh issue create --repo Gentleman-Programming/gentle-ai --web`, pick **Bug Report**.
Use the web form, not `--body-file`. **FIELD 1** (pre-flight checkboxes) and **submitting** are
yours.

---

## TITLE

```
OpenCode-specific instructions are generated into a block that declares itself Claude Code only
```

---

## FIELD 2 — 📝 Bug Description

The `<!-- gentle-ai:sdd-orchestrator -->` block written into `~/.claude/CLAUDE.md` opens by
scoping itself to one runtime:

> Bind this to the Claude Code orchestrator rule only. Do NOT apply it to executor phase agents
> such as `sdd-apply` or `sdd-verify`.

It then gives OpenCode-specific behavioural facts as if they applied:

- *"These results are not persisted by OpenCode's background-agent plugin, so summarize any needed handoff explicitly…"* — a claim about a plugin that is not running, used to justify a behaviour the Claude Code agent should adopt.
- *"OpenCode's managed hook does this automatically."* — stated inline in the reviewer-result capture instructions, so a Claude Code agent may read it as describing its own environment and skip the explicit capture step.

The CodeGraph block adds a third: it forbids placing worktrees under `/tmp/opencode`, a path
specific to another runtime.

The second one is the most consequential: an agent that believes a hook captures results
automatically has a reason not to run `capture-result` itself. In this installation there is no
such hook, so the step would simply not happen.

---

## FIELD 3 — 🔄 Steps to Reproduce

1. Install gentle-ai with Claude Code as the agent and run its sync.
2. Open `~/.claude/CLAUDE.md`.
3. Read the header of the `gentle-ai:sdd-orchestrator` block (line 184 here) — it binds the block
   to Claude Code.
4. Search the same file for `OpenCode` and `/tmp/opencode` (lines 8, 212 and 267 here).

---

## FIELD 4 — ✅ Expected Behavior

Generated instructions describe only the runtime they were generated for. Where a rule exists
*because* of another runtime's behaviour, either state the rule without the cross-runtime
justification, or emit the runtime-specific sentence only into that runtime's file.

---

## FIELD 5 — ❌ Actual Behavior

A block explicitly scoped to Claude Code carries three OpenCode-specific statements, one of which
("OpenCode's managed hook does this automatically") describes automation that does not exist in
the installation being instructed. Users cannot strip them locally — the whole file is inside
`gentle-ai` marker pairs and `sync` overwrites edits.

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

Pick from the live dropdown — closest match is the generated agent-rules/instructions area,
otherwise **CLI (commands, flags)**.

---

## FIELD 10 — 💡 Logs / Error Output

Plain text only — this field auto-renders as a shell block, so do not add fences.

```
$ rg -n -i 'opencode|Claude Code orchestrator' ~/.claude/CLAUDE.md

8:   ... Never place a CodeGraph-dependent worktree under `/tmp`, `/var/tmp`, or `/tmp/opencode` ...
184: Bind this to the Claude Code orchestrator rule only. Do NOT apply it to executor phase agents ...
212: ... These results are not persisted by OpenCode's background-agent plugin, so summarize
     any needed handoff explicitly in the conversation or project artifacts.
267: ... Capture its JSON with `gentle-ai review capture-result ...`; OpenCode's managed hook
     does this automatically.
```

---

## FIELD 11 — Additional Context

Found while auditing the always-on instruction surface. Cheapest of the three reports filed from
this installation to fix, and the one with the clearest behavioural consequence: line 267 gives a
Claude Code agent a stated reason to skip `capture-result`, which is a required step of the
review lifecycle in that runtime.
