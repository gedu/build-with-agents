---
id: upstream/gentle-ai/generated-rules-pin-contract-v1
type: research
targets: [any]
status: rejected
verified: 2026-08-10
sources: ["https://github.com/Gentleman-Programming/gentle-ai/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml", "https://github.com/Gentleman-Programming/gentle-ai/releases/tag/v2.3.0-rc.1", "journal/2026-08-10-upstream-audit-handoff.md"]
---

# Report 0003 — generated agent rules hardcode `review-integration/v1`, which 2.3.0 changes

## DO NOT FILE — resolved on 2.3.0 stable, 2026-08-10

**The predicted failure did not occur, because `sync` did what FIELD 4 asked for.** This report
predicted that an installation carrying `/v1` in its generated rules would, after upgrading to
2.3.0, be following instructions naming a superseded contract with no sanctioned way to discover
the current one. FIELD 4 listed three acceptable fixes; the second was *"`sync` regenerates the
pinned version to match the installed release."* That is what happened.

Verified first-hand on 2.3.0 stable, on the same installation this report was written from:

```
rg -c 'review-integration/v1' <home>/.claude/CLAUDE.md   ->  0
rg -c 'review-integration/v2' <home>/.claude/CLAUDE.md   ->  4
```

Same four sites, opposite version. The `review capabilities --contract .../v1` instruction quoted
in FIELD 10 is also gone from the generated block. There is nothing left to file: the observation
about 2.2.4 was accurate, and the defect it predicted was fixed before it could bite.

**The earlier claim that this report was "confirmed on stable" was wrong.** It was recorded in
`journal/2026-08-10-upstream-audit-handoff.md` and inherited from there. The generated file's
mtime is 23 minutes *earlier* than the commit asserting the opposite, so the claim was already
false when it was written down. A finding verified at discovery time is not verified at write
time; on a file the tool regenerates, those are different facts.

**What is NOT covered by this closure.** A separate and still-open defect was found while checking
this one: `gentle-ai review capabilities` with no arguments answers `contract:
gentle-ai.review-integration/v1`, while `--contract gentle-ai.review-integration/v2 --agent
claude-code` fails deterministically with `operation_failed`, `required_inputs: []`,
`retry_safe: true` and `next_action: retry` that never succeeds. That is a different mechanism in
a different area, and it does not belong in this report. Do not resurrect this file by pasting it
in — stage it as its own report.

Everything below is preserved as the original record. It is no longer filable.

---

**Copy-paste sheet.** Each `## FIELD n` heading matches one field of the upstream Bug Report
form, in form order.

Open with `gh issue create --repo Gentleman-Programming/gentle-ai --web`, pick **Bug Report**.
Use the web form, not `--body-file`. **FIELD 1** (pre-flight checkboxes) and **submitting** are
yours.

---

## TITLE

```
Generated CLAUDE.md hardcodes --contract gentle-ai.review-integration/v1 with no version-agnostic guidance
```

---

## FIELD 2 — 📝 Bug Description

The `<!-- gentle-ai:sdd-orchestrator -->` block that `sync` writes into `~/.claude/CLAUDE.md`
instructs the orchestrator to bootstrap the review lifecycle with a literal contract version:

> bootstrap exactly once with `gentle-ai review status --cwd <repo> --contract gentle-ai.review-integration/v1 --next-transition`

That version string is hardcoded into the shipped agent rules, and the same paragraph forbids
discovering alternatives: *"never explore commands"* and *"never … call `gentle-ai ... --help`
during lifecycle routing."*

On 2.2.4 the `/v1` call works — and notably returns a payload whose own schema field reads
`gentle-ai.review-integration.status/v2`, so the contract identifier and the response schema
version are already out of step within a single release.

The v2.3.0-rc.1 release notes then document the negotiated call using `/v2`:

> `gentle-ai review status --cwd <repo> --contract gentle-ai.review-integration/v2 --next-transition`

So an installation whose generated rules say `/v1` will, after upgrading to 2.3.0, be following
instructions that name a contract version the release notes have moved past — and the same rules
forbid it from discovering the correct form. Because the file is entirely inside `gentle-ai`
marker pairs, users cannot correct it locally; `sync` overwrites the edit.

Secondary, lower confidence and a judgment call rather than a defect: that instruction is a
single ~1,100-character paragraph mixing lifecycle routing policy with operational flag detail
(staging semantics, per-gate flags, refuter rules) that only applies once a review is already
running. Splitting routing from operation would make the version pin easier to notice and easier
to maintain — but the version pin above is the actionable part.

---

## FIELD 3 — 🔄 Steps to Reproduce

1. On gentle-ai 2.2.4, run its sync so `~/.claude/CLAUDE.md` is generated.
2. Find the "Lifecycle receipt rule" inside the `gentle-ai:sdd-orchestrator` block (in this
   installation, line 233).
3. Observe the hardcoded `--contract gentle-ai.review-integration/v1`.
4. Run that exact command against a repository and read the returned `schema` field — it reports
   `gentle-ai.review-integration.status/v2`.
5. Compare against the v2.3.0-rc.1 release notes, which document the negotiated form with
   `--contract gentle-ai.review-integration/v2`.

---

## FIELD 4 — ✅ Expected Behavior

Either the generated rules do not pin a contract version — deriving it from the installed binary
— or `sync` regenerates the pinned version to match the installed release, or the rules carry
explicit guidance for what to do when the pinned contract is rejected. Any of the three keeps a
version bump from stranding the shipped instructions.

---

## FIELD 5 — ❌ Actual Behavior

The version is a literal in generated text, the same paragraph prohibits discovery, and the
release that changes it is already published as a prerelease. The failure mode is silent: the
orchestrator follows its rules, names an outdated contract, and has no sanctioned way to find
the current one.

---

## FIELD 6 — Gentle AI Version

```
gga v2.10.1 (gentle-ai 2.2.4, Homebrew)
```

Compared against the published v2.3.0-rc.1 release notes; that prerelease is **not** installed
here (its own notes recommend staying on 2.2.4).

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
$ rg -n 'review-integration' ~/.claude/CLAUDE.md
233: ... bootstrap exactly once with `gentle-ai review status --cwd <repo>
     --contract gentle-ai.review-integration/v1 --next-transition` ...
233: ... query exactly once `gentle-ai review capabilities
     --contract gentle-ai.review-integration/v1` ...

$ gentle-ai review status --cwd <repo> --contract gentle-ai.review-integration/v1 --next-transition
{
  "schema": "gentle-ai.review-integration.status/v2",
  "contract": "gentle-ai.review-integration/v1",
  ...
}
```

---

## FIELD 11 — Additional Context

Filed from the same installation as report 0001 (upstream #2478). Not blocking anything today —
the `/v1` form still works on 2.2.4. Filed now because it becomes a live defect the moment
2.3.0 ships, and because the "never explore commands" instruction in the same paragraph removes
the escape hatch an agent would otherwise use.
