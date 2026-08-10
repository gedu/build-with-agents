---
id: upstream/claude-code/bash-subsumes-glob-and-grep
type: research
targets: [any]
status: draft
verified: 2026-08-10
sources: ["https://code.claude.com/docs/en/tools-reference", "https://code.claude.com/docs/en/cli-reference", "https://github.com/anthropics/claude-code/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml"]
---

# Report 0001 — `--disallowedTools Bash` raises the tool count; `Bash` suppresses `Glob` and `Grep`

**Copy-paste sheet.** Each `## FIELD n` heading matches one field of the upstream Bug Report form,
in form order.

Open with `gh issue create --repo anthropics/claude-code --web`, pick **🐛 Bug Report**.
Use the web form, not `--body-file`. **FIELD 1** (the three preflight checkboxes) and **submitting**
are yours.

---

## TITLE

The template forces a `[BUG] ` prefix; type the rest after it.

```
[BUG] --disallowedTools Bash increases the visible tool count — Bash silently suppresses Glob and Grep
```

---

## FIELD 1 — Preflight Checklist

Yours to tick. All three are required. Note the second one — `This is a single bug report` — is why
this report covers one behaviour only.

---

## FIELD 2 — What's Wrong?

Denying one tool with `--disallowedTools` can **increase** the number of tools Claude can see.

`--disallowedTools Bash` removes `Bash` and, as a side effect, causes `Glob` and `Grep` to appear —
tools that are absent from the surface whenever `Bash` is available. The net change is −1 +2 = **+1**.

Reproduced on 2.1.224, macOS, with `--strict-mcp-config` so no MCP server contributes:

| Invocation | Tools in `system/init` | `Bash` | `Glob` | `Grep` |
|---|---|---|---|---|
| `--strict-mcp-config` (baseline) | **31** | present | absent | absent |
| `--strict-mcp-config --disallowedTools Write` (control) | **30** | present | absent | absent |
| `--strict-mcp-config --disallowedTools Bash` | **32** | absent | **present** | **present** |

The `Write` control is what makes this a defect rather than a misreading: denying `Write` removes
exactly `Write` and nothing else, which is what the flag documents. Denying `Bash` does something
categorically different.

It is not an artifact of `--strict-mcp-config`. With MCP servers connected the same shape holds —
baseline 55 names, `--disallowedTools Bash` 56 names, the difference being −`Bash` +`Glob` +`Grep`.

**Why this is a bug and not a preference.** Three separate things break:

1. **The tools reference documents `Bash`, `Glob` and `Grep` as independent tools** with separate
   entries and distinct purposes. Nothing on that page, or in the CLI reference's
   `--disallowedTools` entry, says one suppresses the others.
2. **`--disallowedTools` is documented as subtractive**: a bare tool name "removes the matching
   tools from Claude's context". It is reasonable to read that as monotonic. It is not.
3. **It silently defeats the flag's purpose.** Someone reaching for `--disallowedTools Bash` is
   almost always trying to reduce what the agent can reach. They get a *larger* surface, including
   two filesystem-search tools they did not ask to add.

I am labelling as inference, not fact, that the suppression is an intentional context-saving
measure — `Bash` can express what `Glob` and `Grep` do, so exposing all three is redundant. If that
is right, the defect is that it is undocumented and unpredictable, not that it happens.

**Duplicate search.** Run against this repository on 2026-08-10 across `allowedTools`,
`disallowedTools`, `strict-mcp-config`, `Glob Grep hidden Bash`, `Bash tool replaces Glob Grep`,
`search tools hidden when Bash available` and `tools differ between identical runs`. Nothing
matches. The nearest neighbours are all about *permission* rules failing to match or failing to
inherit, which is a different mechanism and a different failure direction:

- **#78063** — `disallowedTools` not inherited by subagents. About propagation across an
  Agent-tool boundary; here a single top-level invocation is already wrong.
- **#79005** — inline `--agents 'tools: []'` no longer denies tools in headless `-p`. A deny that
  fails to remove a tool; here a deny *adds* two.
- **#75315 / #67849 / #76509** — path- and pattern-scoped permission rules never matching. Those
  concern rule matching at call time, not the composition of the visible surface at `init`.

---

## FIELD 3 — What Should Happen?

Either of these resolves it; the first is the smaller change.

**Document it.** State in the tools reference and in the `--disallowedTools` entry of the CLI
reference that `Glob` and `Grep` are exposed only when `Bash` is unavailable, so denying `Bash` adds
them. Then `--disallowedTools` at least behaves predictably once read.

**Or make the flag monotonic.** `--disallowedTools X` should never cause a tool other than `X` to
appear. If `Glob`/`Grep` are suppressed for redundancy, that suppression should be decided
independently of what the user denied, or the newly-exposed tools should be suppressible in the
same invocation.

Either way, `--disallowedTools <name>` should never raise the tool count.

---

## FIELD 4 — Error Messages/Logs

Plain text only — this field auto-renders as a shell block, so do not add fences.

```
$ claude --version
2.1.224 (Claude Code)

$ probe() { claude -p 'Reply with only: ok' --output-format stream-json --verbose "$@" \
  | python3 -c "import json,sys; t=next(e['tools'] for e in map(json.loads,sys.stdin) if e.get('subtype')=='init'); print(len(t), 'Bash' in t, 'Glob' in t, 'Grep' in t)"; }

# count  Bash  Glob  Grep
$ probe --strict-mcp-config
31 True False False

$ probe --strict-mcp-config --disallowedTools Write
30 True False False

$ probe --strict-mcp-config --disallowedTools Bash
32 False True True

Denying Write removes exactly one name. Denying Bash removes one and adds two.

Same shape with MCP servers connected (no --strict-mcp-config):

$ probe
55 True False False

$ probe --disallowedTools Bash
56 False True True
```

---

## FIELD 5 — Steps to Reproduce

1. Confirm the version: `claude --version` reports `2.1.224 (Claude Code)`.

2. Print the baseline surface. `--strict-mcp-config` keeps MCP servers out of the count so the
   numbers are reproducible on any machine:

   ```
   claude -p 'Reply with only: ok' --output-format stream-json --verbose --strict-mcp-config \
     | python3 -c "import json,sys; t=next(e['tools'] for e in map(json.loads,sys.stdin) if e.get('subtype')=='init'); print(len(t), sorted(t))"
   ```

   Observe **31** names. `Bash` is in the list; `Glob` and `Grep` are not.

3. Run the control — deny a tool with no known relationship to the others:

   ```
   claude -p 'Reply with only: ok' --output-format stream-json --verbose --strict-mcp-config \
     --disallowedTools Write \
     | python3 -c "import json,sys; t=next(e['tools'] for e in map(json.loads,sys.stdin) if e.get('subtype')=='init'); print(len(t), sorted(t))"
   ```

   Observe **30** names — exactly `Write` removed. This is the documented behaviour.

4. Now deny `Bash`:

   ```
   claude -p 'Reply with only: ok' --output-format stream-json --verbose --strict-mcp-config \
     --disallowedTools Bash \
     | python3 -c "import json,sys; t=next(e['tools'] for e in map(json.loads,sys.stdin) if e.get('subtype')=='init'); print(len(t), sorted(t))"
   ```

   Observe **32** names — one more than the baseline. `Bash` is gone; `Glob` and `Grep` are now
   present.

5. Optional, to confirm it is not an interaction with `--strict-mcp-config`: repeat steps 2 and 4
   without that flag. The counts scale with however many MCP tools are connected, and the
   `−Bash +Glob +Grep` difference is unchanged.

---

## FIELD 6 — Claude Model

Select: **Opus**

The `system/init` surface is emitted before the first model turn, and the behaviour reproduced
identically across every run regardless of model.

---

## FIELD 7 — Is this a regression?

Select: **No, this never worked**

See FIELD 13 — the same behaviour was measured on 2.1.222, so it is not new in 2.1.224.

---

## FIELD 8 — Last Working Version

Leave empty. There is no observed version where `--disallowedTools Bash` behaved monotonically.

---

## FIELD 9 — Claude Code Version

```
2.1.224 (Claude Code)
```

---

## FIELD 10 — Platform

Select: **Anthropic API**

Reproduced on a Claude subscription login rather than a raw API key; `Anthropic API` is the closest
option the dropdown offers.

---

## FIELD 11 — Operating System

Select: **macOS**

---

## FIELD 12 — Terminal/Shell

Select: **Non-interactive/CI environment**

Every command above is a non-interactive `claude -p` invocation with its output piped. The same
32-name surface was also confirmed from an ordinary interactive macOS terminal, so the behaviour is
not specific to non-interactive mode.

---

## FIELD 13 — Additional Information

**Not a regression, and stable across versions.** The same `−Bash +Glob +Grep` shape was measured on
**2.1.222**: baseline 54 names, `--disallowedTools Bash` 55 names. Every absolute count is one lower
there than on 2.1.224 because the `ListAgents` built-in shipped in between. The shape is unchanged.

**Also invariant to how the CLI is launched.** The 32-name surface reproduces byte-identically from
a plain terminal, from a pseudo-terminal, and from inside another Claude Code session both with and
without the `CLAUDECODE`/`CLAUDE_CODE_*` environment variables present. Eight paired probes plus
four single-condition probes, all on 2.1.224.

**How this was found.** Building a measurement harness that holds the model fixed and varies only
the number of tool names resident in context. The harness needs an exact, committed preimage of the
expected visible surface so it can void any run whose actual surface drifts. `--disallowedTools
Bash` was chosen to shrink the surface; the preimage then disagreed with every run, because the
surface had grown instead. The harness caught it, but only because it was checking. Anything relying
on `--disallowedTools` to bound what an agent can reach would not have noticed.

**One unexplained observation, reported without a mechanism.** In 1 of 8 `--strict-mcp-config`
probes the `ListAgents` built-in was absent, giving 31 names where the other 7 gave 32. It was the
first invocation of the sequence, and an earlier session showed the same first-of-sequence pattern.
That is 4 observations across 2 sessions and a correlation, not a cause. It is mentioned here only
so the counts in this report are not read as perfectly stable; it is not part of this report's
claim, and it is not being filed as a bug, because no mechanism has been demonstrated.
