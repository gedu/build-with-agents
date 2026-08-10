---
id: journal/2026-08-10-upstream-audit-handoff
type: journal
targets: [any]
status: draft
verified: 2026-08-10
sources: ["skills/context-checkpoint/SKILL.md", "upstream/claude-code/README.md", "upstream/claude-code/0001-bash-subsumes-glob-and-grep.md", "sdd/measurement-rig/tasks.md", "https://code.claude.com/docs/en/cli-reference", "https://code.claude.com/docs/en/tools-reference", "https://code.claude.com/docs/en/headless"]
---

# 2026-08-10 — handoff: the upstream report audit, and what it cost

Third end-to-end run of `skills/context-checkpoint`. Record whether it worked on resume — that is
its promotion criterion.

Supersedes `journal/2026-08-10-measurement-rig-handoff.md`, whose §1 next action is now **done and
was partly wrong**. Read this file, not that one, for current state.

Written for a reader with none of the conversation.

## 1. Where we stopped — the next action

**Re-test upstream #2478 on `gentle-ai` 2.3.0.** The machine auto-updated from 2.2.4 mid-session.
The issue is still `OPEN`, 0 comments, untouched since 2026-08-04, and the v2.3.0 release notes never
mention it. The only way to know whether it is fixed is to re-run the repro, and the repro needs a
**fresh lineage** — replay does not trigger it.

Nothing blocks it. It costs a real bounded review, which is why it was not started without asking.

Two smaller items, both unblocked, if that one is not wanted:

- **`hooks/pre-commit:133` fail-open.** `grep -a -nH '' -- "$f" 2>/dev/null || :` swallows per-file
  status, so an unreadable tracked file is silently skipped in `--all`. Found by a validator, never
  fixed. This is the redaction gate of a **public** repo — highest value of the small items.
- **`rig/run.sh:62` still `TIMEOUT_S=300`**, where the derived value is 120s. Trivial.

## 2. Versions and identifiers, all verified 2026-08-10

| Item | Value |
|---|---|
| Repo | `gedu/build-with-agents`, **PUBLIC**, issues enabled, blank issues enabled |
| `origin/main` == `main` | `228e473`, clean tree, everything pushed |
| Claude Code CLI | **2.1.224** |
| Model | `claude-opus-5[1m]` |
| `gentle-ai` | **2.3.0 stable** — was 2.2.4; it auto-updated. `gga` wrapper still v2.10.1 |
| `review-integration/v1` | live, protocol **1.5** |
| `review-integration/v2` | live, protocol **2.2** — on the same binary |
| Upstream #2478 | `OPEN`, 0 comments, unchanged since 2026-08-04, **status on 2.3.0 unknown** |
| Our tracking issue | `gedu/build-with-agents` **#1**, open |
| Upstream `v2.4.0-rc.3` | exists (2026-08-09); latest stable remains `v2.3.0` |

## 3. Verified versus assumed

The section a summary always drops.

### Verified first-hand this session

- **Four of the five staged CLI findings are documented behaviour**, each verified by quoting the
  live docs, not inferred:
  - `--allowedTools` not changing the visible surface — the CLI reference names `--tools` as the
    flag that restricts availability.
  - `--disallowedTools` removing names — "removes the matching tools from Claude's context".
  - The MCP-timing dependence — a remote server with a cached tool list "shows `pending` in
    `system/init`, and connects on its first tool call".
  - `ListAgents` intermittency was never filable: 4 observations, no mechanism.
- **`Bash` suppresses `Glob`/`Grep` is genuinely undocumented**, and the tools reference presents all
  three as independent. On 2.1.224 with `--strict-mcp-config`: baseline **31** (Bash present, no
  Glob/Grep); `--disallowedTools Write` → **30**, exactly one removed; `--disallowedTools Bash` →
  **32**, −Bash +Glob +Grep. The `Write` control is what makes it a defect rather than a misreading.
- Same shape without `--strict-mcp-config` (55 → 56) and on 2.1.222 (54 → 55), so **not a regression**.
- **The nesting question is closed on all four channels.** Environment inheritance (4 nested vs 4
  scrubbed, alternating order), the controlling terminal (pty via `script`), and process ancestry
  (a plain terminal, operator-run) are each not a channel. The committed preimage reproduces
  byte-identically from all of them.
- **The 33-vs-54 gap was a category error on our side.** A sub-agent's own tool set is a different
  object from a `claude -p` `init.tools` array. The numbers were never comparable.
- Duplicate search against ~14.8k open `anthropics/claude-code` issues, ~12 queries, no match.
- `review-integration/v1` **and** `/v2` both answer on 2.3.0, while the generated
  `~/.claude/CLAUDE.md` hardcodes `/v1` in 4 places and mentions `/v2` zero times.
- Redaction gate clean across 110 tracked files.

### Assumed, inherited, or explicitly not verified — do not promote these

- **Whether #2478 is fixed on 2.3.0.** Unknown. Not tested. The release notes' silence is not evidence
  either way.
- **That the `Bash` suppression is an intentional context-saving measure.** Labelled as inference
  inside the report itself, and it must stay labelled. The filed claim is "undocumented and
  non-monotonic", never "wrong to do".
- **The cause of the `ListAgents` intermittency.** Now 4 observations across 2 sessions, all
  first-of-sequence. That is a correlation. No mechanism. Do not write one into anything.
- **The other four `gentle-ai` reports (0001–0004) are all written against 2.2.4.** The machine is on
  2.3.0. Every version field needs re-verification before any of them is filed.
- **`hooks/pre-commit` still has no committed test.** Recorded four times now as ADR-shaped: where do
  tests live in this repo.

## 4. Open, deliberately

- **Report 0003 is now stronger, not resolved.** It was drafted as a *prediction* against the
  v2.3.0-rc.1 notes; it is now an *observation* on stable — the installation is pinned to `/v1` on a
  binary shipping both, while the same generated rules forbid discovery. Upgrade its status before
  filing.
- **Filing remains a human act.** Tracking issue #1 exists so 0001 does not get lost; nothing has
  been published to any repository we do not own.
- **No performance/efficiency review lens exists.** Flagged twice now, deferred by the operator.

## 5. What the conversation established that no file records

- **"Undocumented" is a claim about documentation, and a probe can never establish it.** Four
  findings survived weeks of probe-verification and died in twenty minutes of reading the docs. This
  repo already carried the mirror lesson — "reading produced confident wrong conclusions, cheap
  probes corrected them" — and applying only that half is exactly what got us here. Both halves are
  now written into `upstream/claude-code/README.md` as an entry rule for that directory.
- **The upstream form's shape decided the report's scope, not our judgement.**
  `anthropics/claude-code` requires a preflight attestation that a report covers exactly one bug. A
  five-finding report was never filable there, whatever we thought of it. **Read the target's
  template before deciding what a report contains.**
- **A control is what separates a defect from a misreading.** `--disallowedTools Write` removing
  exactly one name is the single most load-bearing line in report 0001. Without it the report is one
  observation and an opinion; with it, the behaviour is isolated.
- **The destination was wrong in the previous handoff and nearly stayed wrong.** It said
  `upstream/gentle-ai/0005-*` for findings about the Claude Code CLI. `upstream/README.md`'s own
  layout rule — one directory per tool — settled it without needing a decision. When a plan and a
  standing rule disagree, check the rule before executing the plan.
- **Two flags this repo never knew existed**, both found during the audit, both relevant to `rig/`:
  `--tools` (the documented way to restrict the built-in set, which is what the rig does by hand with
  `--disallowedTools`) and `--bare` ("the recommended mode for scripted and SDK calls", skips all
  auto-discovery, needs `ANTHROPIC_API_KEY` rather than a subscription login). Neither invalidates a
  committed result — the achieved surface was verified against a preimage on every run — but both
  belong in any future revision.
- **`sdd/measurement-rig/tasks.md` had drifted to 17 phantom open items** while the experiment had
  already promoted its first result. Reconciled to 9 done / 7 cancelled / 1 open. A task file that
  nobody reconciles becomes a source of false blockers.
