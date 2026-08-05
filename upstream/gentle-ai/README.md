---
id: upstream/gentle-ai/index
type: index
targets: [any]
status: validated
verified: 2026-08-05
sources: ["https://github.com/Gentleman-Programming/gentle-ai/blob/main/CONTRIBUTING.md", "https://github.com/Gentleman-Programming/gentle-ai/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml"]
---

# upstream/gentle-ai/

Staged reports and experiments against [`gentle-ai`](https://github.com/Gentleman-Programming/gentle-ai).
This file is the reporting protocol: what upstream requires, what an agent may do without
asking, and what only a human can do.

## Staged reports

| Report | Subject | Filed |
|--------|---------|-------|
| `0001-correction-acceptance-blocks-receipt.md` | Bounded review in `correction_required` can never reach a receipt; `status` and `finalize` disagree about captured evidence | [#2478](https://github.com/Gentleman-Programming/gentle-ai/issues/2478) — open, `status:needs-review` |

## What upstream requires

Taken from `CONTRIBUTING.md` and `.github/ISSUE_TEMPLATE/bug_report.yml`. Verify against the
sources before relying on it — upstream can change these rules without telling us.

**Issue-first is mandatory.** "No PR without an issue. No exceptions." A PR without a linked,
approved issue is rejected automatically. An issue must be filed through the Bug Report or
Feature Request template, and a maintainer applies the `status:approved` label when it is ready
to be worked. That label is the gate: nothing else authorizes a PR.

The Bug Report template applies `bug` and `status:needs-review` by default and requires:

| Field | Required | Notes |
|-------|----------|-------|
| `preflight` | yes | Two checkboxes: searched for duplicates, understood the PR rejection policy |
| `description` | yes | What the bug is |
| `steps` | yes | Numbered reproduction |
| `expected` | yes | Documented or contracted behavior |
| `actual` | yes | Verbatim observed behavior |
| `version` | yes | The field says to run `gga version`, which reports the **wrapper** version (`v2.10.1`), not the `gentle-ai` binary version (`2.2.2`). Give both so a triager does not have to guess which one a defect belongs to. |
| `os` | yes | Dropdown: macOS, Linux variants, Windows, WSL |
| `agent` | yes | Dropdown: Claude Code, OpenCode, Gemini CLI, Cursor, Windsurf, Other |
| `area` | yes | Dropdown: CLI, TUI, Installation, Agent Detection, System Detection, Catalog, Documentation, Other |
| `logs` | no | Auto-rendered as a shell block — plain text only, no markdown, no fences |
| `context` | no | Anything else |

There is **no `shell` field** in this template, despite what some contribution guides for sibling
repos describe. Put the shell in `context` if it matters. Titles are conventional-commit shaped
(`fix(<scope>): …`); there is no numeric prefix convention, GitHub assigns the number.

If a PR follows: conventional commit titles matching
`^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([a-z0-9\._-]+\))?!?: .+`,
branch names matching `^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert)\/[a-z0-9._-]+$`,
**400 changed lines or fewer**, a `Closes #N` link, one `type:*` label, work-unit commits that
keep code, tests and docs together, and passing `go test ./...` plus the Docker-based e2e suite
in `e2e/`.

## Report shape

A staged report is written **field-per-field against the upstream form**, not as prose that later
has to be sliced up. Each section is headed `## FIELD n — <exact form label>`, in the order the
form presents them, plus a `## TITLE` section. Filing is then mechanical: copy between headings,
paste, submit. Nothing is rewritten, summarised or re-ordered under time pressure.

The reason for the discipline: mapping a narrative report onto eleven form fields at filing time
is where detail gets dropped and where a hand-edited body loses the template's default labels.
Doing it once, at writing time, makes the mapping reviewable and reusable.

Requirements for a report to count as ready:

- Every required field has content. No `TODO`, no placeholder.
- The dropdown sections state the option to select verbatim, not a description of it.
- The `logs` section is plain text with no markdown, because the form fences it automatically.
- A duplicate search has been run and its result is written into the `description` section as an
  explicit "distinct from #N because …" list. Neighbouring issues are named, and the difference is
  the observed failure mode, not a claim of novelty.
- Inference is labelled as inference.
- Secondary defects found on the way are kept separate from the primary defect, with a note on
  whether they should be folded into an existing issue instead.

Redact before committing: absolute paths containing a username, tokens, and hostnames. Use
`<repo>` for the repository root. This is not cosmetic — a staged report is a public artifact
the moment it is pushed.

## Division of labour

The split is not about capability. It is about who is accountable for an irreversible,
outward-facing act, and who upstream will hold to it.

### Done automatically, no approval needed

- Reproduce the defect and reduce it to deterministic steps.
- Cross-check every claim against real output. No inferred behavior stated as fact; inference
  is labelled as inference.
- Verify the version, environment, and whether a documented contract is actually violated.
- Write the staged report and keep it inside the required shape.
- Redact private paths and secrets.
- Map the report onto the upstream template fields.
- Read `CONTRIBUTING.md` and the issue templates at the time of writing rather than trusting a
  cached memory of them.
- Search upstream for duplicate issues and report what was found.
- Draft the exact issue title and body, ready to submit.
- After an issue exists: check its state and labels on request.
- If `status:approved` is granted and a fix is wanted: write the patch, tests and docs, keep the
  diff at or below 400 lines, run `go test ./...`, and prepare conventionally-named commits and
  branch.

### Requires you, explicitly

- **Filing the issue.** It publishes to a repository you do not own, under your GitHub identity,
  and it cannot be cleanly withdrawn. It is asked for once, per report, and never assumed. The
  recommended route is `gh issue create --repo Gentleman-Programming/gentle-ai --web`, because
  the web form applies the template's required fields and its default `bug` and
  `status:needs-review` labels. Filing through `gh issue create --body-file` bypasses the
  template, so those defaults are not applied and a maintainer has to fix it by hand.
- **Ticking the pre-flight checkboxes.** They are an attestation. Whoever files the issue makes
  it, not the agent that drafted it.
- **Waiting for `status:approved`.** Only a maintainer can apply it. No amount of local work
  substitutes for it, and starting a PR before it exists wastes the work.
- **Applying labels.** Requires triage permission on the repository. Without it, labels are a
  request in the issue body, not an action.
- **Pushing a branch and opening a PR** to a repository you do not own: fork first, and the
  push is yours to authorize.
- **Running the Docker e2e suite**, if Docker is not already running locally.
- **Deciding whether to fix it at all.** A good report is a complete contribution. Filing it and
  stopping there is a legitimate outcome.

## Current state of report 0001

Ready to file. Drafted, verified, redacted, and rewritten field-per-field against the live
template. Duplicate search run against upstream on 2026-08-04.

Title:

```
fix(review): finalize --validation refuses evidence that status reports as accepted (2.2.2)
```

The duplicate search found five neighbours, all distinguished in the report's `description`
section: **#1925** (correction dead-ends, but on a frozen-target mismatch after amend), **#2132**
(`status` is the failing side, not `finalize`), **#1996** (verification *fails* there; here it
passes), **#2248** (same class as our secondary defect 1, not the primary defect), and **#1802**
(closed; *over*-approves by ignoring the captured verdict, where this defect *never* approves
because acceptance cannot see the evidence at all). None is this defect. Upstream has roughly 250
open issues with heavy overlap in the review lifecycle, so expect a maintainer to reach for the
dup button — the "distinct from" list exists to answer that before it is asked.

**On GitHub's similar-issue warning.** The web form surfaces embedding-similar issues while you
type. It matches on wording, not on defect identity, and every review-lifecycle report shares the
vocabulary (`finalize`, `verification evidence`, `canonical`, `receipt`), so a hit there is not
evidence of duplication. Treat it as a prompt to check, not a verdict. Two things make a real
duplicate: the same failing operation at the same lifecycle stage, and the same failure direction.
A closed issue can never absorb a live defect — closing a valid report as a duplicate of a
`wontfix` loses it. When the neighbour is genuinely adjacent, name it in `description` with the
concrete difference and file anyway.

Next action is yours, and it is the only step left:

```
gh issue create --repo Gentleman-Programming/gentle-ai --web
```

Pick **Bug Report**, then copy each `## FIELD n` block from the report into the matching field.
Tick the two pre-flight boxes — that attestation is the submitter's, not the drafter's. After
submitting, record the issue number in the Staged reports table above.
