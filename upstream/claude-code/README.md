---
id: upstream/claude-code/index
type: index
targets: [any]
status: draft
verified: 2026-08-10
sources: ["https://github.com/anthropics/claude-code/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml", "https://code.claude.com/docs/en/cli-reference", "https://code.claude.com/docs/en/tools-reference", "https://code.claude.com/docs/en/headless"]
---

# upstream/claude-code/

Staged reports against [`anthropics/claude-code`](https://github.com/anthropics/claude-code).
Created per `upstream/README.md`'s layout rule — one directory per tool, created when the first
experiment for it exists.

**This is a different upstream from `gentle-ai/`, with a different template and different rules.**
Numbering restarts at `0001` inside this directory. The report below is the fifth staged report in
the repository overall; the handoff journal called it `upstream/gentle-ai/0005-*`, which was a slip.
These are Claude Code CLI behaviours and do not belong in the `gentle-ai` tracker.

## Staged reports

| Report | Subject | Filed |
|--------|---------|-------|
| `0001-bash-subsumes-glob-and-grep.md` | `--disallowedTools Bash` **raises** the visible tool count: `Bash` suppresses `Glob` and `Grep`, undocumented | not filed yet |

## What upstream requires

Taken from `.github/ISSUE_TEMPLATE/bug_report.yml`. Verify against the source before relying on it.

The Bug Report template applies the `bug` label, forces a `[BUG] ` title prefix, and requires:

| Field | Required | Notes |
|-------|----------|-------|
| `preflight` | yes | **Three** checkboxes, all required — see the hard constraint below |
| `actual` — What's Wrong? | yes | |
| `expected` — What Should Happen? | yes | |
| `error_output` | no | `render: shell` — plain text only, no fences |
| `reproduction` — Steps to Reproduce | yes | Template asks explicitly for a minimal example |
| `model` | no | Dropdown: Sonnet (default), Opus, Not sure / Multiple models, Other |
| `regression` | **yes** | Dropdown: worked before / never worked / don't know |
| `working_version` | no | Only if a regression |
| `version` | yes | Output of `claude --version` |
| `platform` | yes | Dropdown: Anthropic API, AWS Bedrock, Google Vertex AI, Other |
| `os` | yes | Dropdown: macOS, Windows, Ubuntu/Debian Linux, Other Linux, Other |
| `terminal` | yes | Dropdown, 13 options including **Non-interactive/CI environment** |
| `additional` | no | |

### The hard constraint: one bug per report

The preflight carries this as a **required** attestation:

> `This is a single bug report (please file separate reports for different bugs)`

A report bundling several behaviours cannot be filed here honestly. Each distinct behaviour needs
its own issue, or it needs to be dropped.

## What "undocumented" costs to claim

The lesson this directory exists to carry, learned expensively on 2026-08-10.

Five CLI behaviours were staged for report, each verified by direct probe, each of which had
silently invalidated a design in this repo. **Four did not survive contact with the
documentation**, and no probe could ever have told us that — a probe establishes what the harness
does, never what the docs already say:

| Behaviour | Verdict |
|---|---|
| `--allowedTools` does not change the visible surface | **Documented.** The CLI reference says it lists "Tools that execute without prompting for permission… To restrict which tools are available, use `--tools` instead" |
| `--disallowedTools` removes names from visibility | **Documented.** A bare tool name "removes the matching tools from Claude's context" |
| `Bash` suppresses `Glob` and `Grep` | **Undocumented.** The tools reference presents all three as independent. Filed as `0001` |
| The surface depends on MCP connection timing | **Documented.** A remote server with a cached tool list "shows `pending` in `system/init`, and connects on its first tool call" |
| `ListAgents` intermittently absent | **Not filable.** Four observations, no mechanism. An observation without a mechanism is not a bug report |

**`undocumented` is a claim about documentation and must be verified against documentation.**
Before staging any report here, read the relevant docs page and quote it. If the behaviour is
described there, the finding is a reading failure on our side, and the honest outcome is to record
that and file nothing.

Two flags surfaced during that audit that this repo had never used, both relevant to `rig/`:

- **`--tools`** — "Specify the list of available tools from the built-in set." The documented way to
  restrict the surface. `rig/run.sh` instead computes `--disallowedTools` as (broad minus scoped).
- **`--bare`** — skips auto-discovery of hooks, skills, plugins, MCP servers, auto memory and
  `CLAUDE.md`; documented as "the recommended mode for scripted and SDK calls" and as giving "the
  same result on every machine". Note it never reads OAuth credentials, so it needs
  `ANTHROPIC_API_KEY` rather than a subscription login.

Neither invalidates the rig's committed results — the achieved surface was verified against a
committed preimage on every run — but both belong in any future revision of it.

## Division of labour

Same split as `gentle-ai/README.md`, and for the same reason. Reproducing, verifying, redacting,
duplicate-searching and drafting are automatic. **Filing is yours**: it publishes under your GitHub
identity to a repository you do not own and cannot be cleanly withdrawn. So is ticking the
preflight boxes — they are an attestation by whoever submits, not by whoever drafted.

Redact before committing and again before filing. The rule is repo-wide and lives in `AGENTS.md`;
ADR 0009 carries the reasoning.
