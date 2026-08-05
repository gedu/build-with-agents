---
id: upstream/gentle-ai/correction-acceptance-blocks-receipt
type: research
targets: [any]
status: validated
verified: 2026-08-05
sources: ["https://github.com/Gentleman-Programming/gentle-ai/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml", "https://github.com/Gentleman-Programming/gentle-ai/issues/2478"]
---

# Report 0001 — correction acceptance rejects evidence that status reports as accepted

**Filed upstream as [#2478](https://github.com/Gentleman-Programming/gentle-ai/issues/2478)**
on 2026-08-04 — `open`, labels `bug` / `status:needs-review`, no maintainer response yet.

Reproduced on `gentle-ai` **2.2.2**. **Not re-tested on 2.2.4**: the replay stops earlier, at a
`recovery_authorization_required` collect transition, so `finalize --validation` is unreachable
and the defect can be neither confirmed nor cleared on that version. Do not read the version in
the title as still-reproducing. 2.2.4 does ship `fix(review): expose accepted correction
findings`, but that fixes
[#2050](https://github.com/Gentleman-Programming/gentle-ai/issues/2050) — a different
transition. See `journal/2026-08-05-first-commit-gate-bypass.md` for the full replay output.

The copy-paste sheet below is kept as the filed record.

**This file is a copy-paste sheet, not prose.** Every `## FIELD n` heading below matches one
field of the upstream Bug Report form, in the order the form presents them. Copy everything
between one `## FIELD` heading and the next, paste it into that field, move on. Nothing needs
to be rewritten, summarised or re-ordered at filing time.

Open the form with:

```
gh issue create --repo Gentleman-Programming/gentle-ai --web
```

Then pick **Bug Report**. Use the web form, not `--body-file`: the form is what applies the
template's default `bug` and `status:needs-review` labels. Filing bypasses that and a maintainer
has to fix the labels by hand.

Two things only you can do, and they are deliberately not pre-filled:

- **FIELD 1 (pre-flight checkboxes)** is an attestation by whoever submits. Tick it yourself.
- **Submitting.** This publishes under your GitHub identity to a repo you do not own.

The template layout, verified against `bug_report.yml` on 2026-08-04:

| # | Form field | Type | Required | Source below |
|---|-----------|------|----------|--------------|
| — | Title | input | yes | `## TITLE` |
| 1 | Pre-flight Checklist | 2 checkboxes | yes | tick manually |
| 2 | 📝 Bug Description | textarea | yes | `## FIELD 2` |
| 3 | 🔄 Steps to Reproduce | textarea | yes | `## FIELD 3` |
| 4 | ✅ Expected Behavior | textarea | yes | `## FIELD 4` |
| 5 | ❌ Actual Behavior | textarea | yes | `## FIELD 5` |
| 6 | Gentle AI Version | input | yes | `## FIELD 6` |
| 7 | Operating System | dropdown | yes | `## FIELD 7` |
| 8 | AI Agent / Client | dropdown | yes | `## FIELD 8` |
| 9 | 📋 Affected Area | dropdown | yes | `## FIELD 9` |
| 10 | 💡 Logs / Error Output | textarea, `render: shell` | no | `## FIELD 10` |
| 11 | Additional Context | textarea | no | `## FIELD 11` |

There is **no Shell field** in this template — do not go looking for one. FIELD 10 renders as a
shell block automatically, so it must be plain text: no markdown, no fences of its own.

---

## TITLE

Conventional-commit shape, scope `review`. There is no numeric prefix convention — GitHub
assigns the issue number.

```
fix(review): finalize --validation refuses evidence that status reports as accepted (2.2.2)
```

---

## FIELD 2 — 📝 Bug Description

A bounded review that enters `correction_required` can never reach a receipt. `review status
--next-transition` advances past the evidence stage and asks for targeted validation, but
`review finalize --validation` refuses with a missing-evidence error for evidence that is
present, canonical, and bound to the current authority revision. The two operations disagree
about the same artifact, and there is no third command to break the tie.

Impact: every lifecycle gate fails closed for that candidate. `validate --gate pre-commit` has
no receipt to validate, so the change cannot be delivered through the gate even though the
review completed and its findings were fixed and independently validated.

**This is distinct from the closest open issues.** I searched before filing:

- **#1925** — `in-budget compact correction dead-ends after the edit is applied`. There
  `finalize` refuses because the live snapshot no longer matches the frozen target after the fix
  is amended in. Here the snapshot *does* match (`candidate_tree` equals live `git write-tree`),
  `capture-evidence` succeeds and stays idempotent, and the refusal happens one stage later, at
  `--validation`, with a different message.
- **#2132** — `review status fails before authority evaluation after bounded correction`. There
  `status` is the failing side. Here `status` succeeds and prescribes
  `targeted_validation_required`; `finalize` is the side that refuses.
- **#2248** — `advertised capture-evidence transition omits required parameters`. Same *class* as
  secondary defect 1 in Additional Context below, and possibly the same root — but unrelated to
  the primary defect. Fold secondary defect 1 into #2248 if they share a cause.
- **#1996** — `provide a terminal exit after failed correction verification`. There the
  verification *fails*. Here it passes and is accepted by the capture side; only acceptance
  rejects it, so there is nothing to exit from.
- **#1802** — `derive final outcome from canonical verification evidence` (**closed**, no upstream
  PR planned). GitHub's similar-issue hint surfaces this one, and the two are worth reading
  together, but they are not the same defect and the failure direction is opposite. #1802 is at
  the `validating` / `CompleteVerification` stage, on schema
  `gentle-ai.canonical-verification-evidence/v1`, and *over*-approves: finalize ignores the
  captured verdict and honours the caller's `--failed` flag, so a canonical `fail` can reach
  `approved`. This defect is at correction acceptance, on
  `gentle-ai.review-verification-evidence/v2`, and *never* approves: the captured evidence says
  `passed`, cross-checks on every field, is idempotently re-accepted by `capture-evidence`, and
  acceptance still reports it absent, so no receipt exists at all.

  A shared root is plausible — both are finalize failing to resolve persisted evidence records,
  surfacing as "ignores the verdict" in one case and "reports it missing" in the other. **That is
  inference, not verified against the source.** Flagging it because it may be the useful fix, not
  because it makes these one issue: #1802 is closed and explicitly not being taken upstream, so it
  cannot carry this defect.

---

## FIELD 3 — 🔄 Steps to Reproduce

Deterministic on any repository whose candidate produces at least one blocking finding, so the
review is forced into `correction_required`.

1. In a repository with staged or untracked changes that include an executable shell script
   (this promotes the candidate to `high` tier and selects the four 4R lenses), bootstrap the
   lifecycle and execute the emitted `review.start` command verbatim:

   ```
   gentle-ai review status --cwd <repo> \
     --contract gentle-ai.review-integration/v1 --next-transition
   ```

2. Run each selected lens and capture its result:

   ```
   gentle-ai review capture-result --cwd <repo> --lineage <id> --target <target> \
     --lens <lens> --order <n> --input <result.json>
   ```

   Each result must carry `subject_hash`, `inspection.status: completed`, `inspection.paths`
   covering the complete frozen path manifest, `findings` and `evidence`. At least one finding
   must be `CRITICAL` or `BLOCKER` with `evidence_class: deterministic` and
   `causal_disposition: introduced`, so the review is forced into correction.

3. Finalize with every manifest. The lineage moves to `correction_required`:

   ```
   gentle-ai review finalize --cwd <repo> --lineage <id> \
     --result-artifact '<manifest 0>' … --result-artifact '<manifest n>'
   ```

4. Forecast the correction, then apply a bounded fix to the blocking findings only:

   ```
   gentle-ai review finalize --cwd <repo> --lineage <id> --correction-lines 20
   ```

5. Capture repository verification evidence for the correction target reported by `status`:

   ```
   gentle-ai review capture-evidence --cwd <repo> --lineage=<id> \
     --expected-revision=<rev> --target=<correction target> \
     --outcome=passed --input <evidence.txt>
   ```

   This succeeds, and `status --next-transition` advances to `targeted_validation_required`.

6. Submit the targeted validation artifact for exactly the `request_hash` and
   `correction_target_identity` that `status` reported:

   ```
   gentle-ai review finalize --cwd <repo> --lineage <id> --validation <validation.json>
   ```

   **Observed:** `Error: compact correction acceptance requires captured repository verification
   evidence`. No permutation of flags advances past this point, and no receipt is ever produced.

---

## FIELD 4 — ✅ Expected Behavior

After a correction is applied and repository verification evidence is captured, submitting the
targeted validation artifact should either produce the terminal receipt or return a specific,
actionable refusal about the validation artifact itself.

Concretely, one of these should hold:

1. `review finalize --lineage <id> --validation <file>` consumes the captured evidence already
   persisted for the current correction target and publishes the receipt; or
2. the refusal names what is actually missing or mismatched, so the caller can supply it; or
3. `review status --next-transition` does not advance to `targeted_validation_required` while
   `finalize` still considers the evidence stage unsatisfied.

The contract states that FINALIZE "creates or discovers the terminal receipt" after a bounded
correction whose evidence and targeted validation were supplied. Nothing documents a state in
which both operations are simultaneously correct and mutually exclusive.

---

## FIELD 5 — ❌ Actual Behavior

`review status --next-transition` reports the evidence stage satisfied and requests the targeted
validation input:

```json
{
  "next_transition": {
    "kind": "collect",
    "reason_code": "targeted_validation_required",
    "collect": { "inputs": [ {
      "name": "targeted_validation",
      "schema": "gentle-ai.review-targeted-validation-request/v1",
      "validation_request": {
        "request_hash": "sha256:0d3fdd3f9223bf3782eb6cd49313cda81f15ec1d67414f958ee145e86469b6db",
        "fix_finding_ids": ["R2-001", "R2-002"],
        "correction_target_identity": "sha256:59b7f581b8219c1523628f7c928201a537f043c21efbfb60b49590401e131e80",
        "correction_paths": ["AGENTS.md", "MAP.md"]
      }
    } ] }
  }
}
```

Submitting a schema-valid validation artifact for exactly that `request_hash` and
`correction_target_identity` fails:

```
$ gentle-ai review finalize --cwd <repo> --lineage review-f0f10534f4457aa3 \
    --validation validation.json
Error: compact correction acceptance requires captured repository verification evidence
```

The evidence it reports as missing is present in the transaction store, owner-only, and
consistent with the live repository:

```
$ ls -l <repo>/.git/gentle-ai/review-transactions/v2/review-f0f10534f4457aa3/final-evidence/59b7f581…/
-rw-------  record.json
-rw-------  verification.txt

$ jq '{schema,outcome,authority_revision,target_identity,candidate_tree,ledger_ids}' record.json
{
  "schema": "gentle-ai.review-verification-evidence/v2",
  "outcome": "passed",
  "authority_revision": "sha256:1e865ca86f6f1da6faaceeef9ab40380dd64ec0d4c2d53d67fafe824b8fa4d20",
  "target_identity": "sha256:59b7f581b8219c1523628f7c928201a537f043c21efbfb60b49590401e131e80",
  "candidate_tree": "ef2402b83d912fa991241dc6fe59cc5a10ffeaf6",
  "ledger_ids": ["R2-001", "R2-002"]
}
```

Every field cross-checks:

| Check | Result |
|-------|--------|
| `authority_revision` vs current store revision | identical (`sha256:1e865ca8…`) |
| `target_identity` vs `correction_target_identity` from `status` | identical (`sha256:59b7f581…`) |
| `candidate_tree` vs live `git write-tree` | identical (`ef2402b8…`) |
| `ledger_ids` vs `fix_finding_ids` from `status` | identical (`R2-001`, `R2-002`) |
| file mode | `0600` on both artifacts, same as the accepted reviewer results |
| re-running `capture-evidence` | exits 0, so the capture path still accepts it |

Because `capture-evidence` is idempotent and keeps succeeding, the artifact is demonstrably valid
to the capture side. Only the acceptance side rejects it.

**Every flag combination attempted.** All six return the identical error:

```
--validation <file>
--correction-lines 20 --validation <file>
--correction-lines 20 --validation <file> --evidence <raw evidence file>
--validation <file> --evidence <capture-evidence manifest json>
--validation <file> --evidence <store record.json>
<re-run capture-evidence, then> --validation <file>
```

Re-passing the reviewer results at this stage is correctly refused with a different, clear error,
which confirms the lineage is past the reviewing state:

```
$ gentle-ai review finalize --lineage review-f0f10534f4457aa3 \
    --result-artifact '…' --correction-lines 20 --validation validation.json
Error: reviewer results are accepted only while the authority is reviewing
```

**There is no alternative route for this input.** No `capture-validation` subcommand exists, so
`finalize --validation` is the only one. The available subcommands are: `capabilities, start,
finalize, validate, status, repair, invalidate, abandon, recover, retry-final-verification,
reclaim, inspect-authority, reconcile-authority, reconcile-authority-batch, dispose-result,
reopen-results, quarantine-legacy, quarantine-legacy-fix-scope, repair-legacy-alias, schema,
bind-sdd`.

`review abandon --incomplete-inspection` is also unavailable: the CLI's own rule refuses to
abandon a lineage that captured every selected lens, which this one did. So the lineage cannot be
completed and cannot be discarded.

---

## FIELD 6 — Gentle AI Version

```
gga v2.10.1 (gentle-ai 2.2.2, Homebrew)
```

The template asks for `gga version`, which reports `v2.10.1`. The defect is in the `gentle-ai`
binary it installs, which reports `2.2.2` — both are given so neither has to be guessed.

---

## FIELD 7 — Operating System

Select: **macOS**

---

## FIELD 8 — AI Agent / Client

Select: **Claude Code**

---

## FIELD 9 — 📋 Affected Area

Select: **CLI (commands, flags)**

---

## FIELD 10 — 💡 Logs / Error Output

Plain text only — this field auto-renders as a shell block, so do not add fences or markdown.

```
$ gentle-ai review status --cwd <repo> --contract gentle-ai.review-integration/v1 --next-transition
… "reason_code": "targeted_validation_required"
… "request_hash": "sha256:0d3fdd3f9223bf3782eb6cd49313cda81f15ec1d67414f958ee145e86469b6db"
… "correction_target_identity": "sha256:59b7f581b8219c1523628f7c928201a537f043c21efbfb60b49590401e131e80"
… "fix_finding_ids": ["R2-001","R2-002"]

$ gentle-ai review finalize --cwd <repo> --lineage review-f0f10534f4457aa3 --validation validation.json
Error: compact correction acceptance requires captured repository verification evidence

$ gentle-ai review finalize --cwd <repo> --lineage review-f0f10534f4457aa3 --correction-lines 20 --validation validation.json
Error: compact correction acceptance requires captured repository verification evidence

$ gentle-ai review finalize --cwd <repo> --lineage review-f0f10534f4457aa3 --validation validation.json --evidence evidence.txt
Error: compact correction acceptance requires captured repository verification evidence

$ gentle-ai review capture-evidence --cwd <repo> --lineage=review-f0f10534f4457aa3 --expected-revision=sha256:1e865ca8… --target=sha256:59b7f581… --outcome=passed --input evidence.txt
(exit 0 — capture side still accepts the same artifact)

$ gentle-ai review finalize --cwd <repo> --lineage review-f0f10534f4457aa3 --validation validation.json
Error: compact correction acceptance requires captured repository verification evidence

$ gentle-ai review finalize --lineage review-f0f10534f4457aa3 --expected-revision sha256:ccc7887c… --correction-lines 20
Error: flag provided but not defined: -expected-revision

$ gentle-ai review finalize --lineage review-f0f10534f4457aa3 --target sha256:f0f10534… --correction-lines 20
Error: flag provided but not defined: -target
```

---

## FIELD 11 — Additional Context

### Environment detail

| Item | Value |
|------|-------|
| gentle-ai | 2.2.2 (Homebrew, `Cellar/gentle-ai/2.2.2`) |
| gga | v2.10.1 |
| OS | macOS (Darwin 24.6.0, arm64) |
| Shell | zsh |
| git | repository with an unborn-then-anchored `main`, base commit containing one file |
| Projection | `workspace`, 29 intended-untracked paths, tier `high`, correction budget 200 |
| Lineage | `review-f0f10534f4457aa3` |
| Frozen target | `sha256:f0f10534f4457aa396a4d96a04423bb131cd80884736cd2fc12bb68f8a9be39a` |
| Correction target | `sha256:59b7f581b8219c1523628f7c928201a537f043c21efbfb60b49590401e131e80` |

### Notes for whoever picks this up

- The disagreement is between the evidence lookup used by `status` transition planning and the
  one used by correction acceptance in `finalize`. Both were given the same lineage and the same
  live repository state.
- The evidence is stored under `final-evidence/<correction_target_identity>/`, keyed by the
  correction target. If acceptance instead resolves the key from the original frozen target, or
  recomputes the correction target at acceptance time and gets a different value, that would
  explain the mismatch — **this is inference, not verified against the source.**
- `gentle-ai review finalize` with no `--lineage` compares the live snapshot against the original
  frozen target and reports a mismatch. That is expected after a correction and is not a symptom
  of this bug; noted so it is not chased.

### Secondary defects observed in the same run

Smaller, and they may deserve separate issues. Recorded here because they were found on the path
to the primary defect, not because they belong to it.

**1. `status --next-transition` emits arguments that `finalize` does not define.**

The `correction_lines` collect input advertises `expected-revision` and `target` arguments:

```json
{ "name": "correction_lines", "arguments": [
  { "name": "lineage", "value": "review-…" },
  { "name": "expected-revision", "value": "sha256:ccc7887c…" },
  { "name": "target", "value": "sha256:f0f10534…" } ] }
```

Passing either is rejected — see the last two commands in Logs — and the rejection writes a
defect report to `.git/gentle-ai/defect-reports/`. Only `--lineage` and `--correction-lines` are
accepted, so a caller following the emitted arguments literally fails on the first attempt.

This may be the same root as **#2248** (`advertised capture-evidence transition omits required
parameters`), which reports the equivalent problem on a different transition. Close this as part
of #2248 if so.

**2. Reviewer-result shape is under-documented where it matters most.**

The rejection for a result missing the bound subject is:

```
Error: reviewer artifact admission incomplete: reviewer result omitted the provider-owned
artifact subject: … re-run the lens and invoke gentle-ai review capture-result again on the
same lineage with a result that echoes the binding's top-level subject_hash and a completed
inspection envelope
```

The message is accurate and the schema is discoverable via `gentle-ai review schema reviewer`,
which is good. What is missing is that `subject_hash` must be threaded into the **lens binding**
in the first place. A binding carrying only `lineage`, `target`, `lens` and `order` — which is
what several published orchestrator instruction sets describe — cannot produce an admissible
result, because the lens never receives the `subject_hash` it is required to echo. Surfacing the
required binding fields in the `review start` output next to `artifact_subjects`, or naming them
in this error, would remove a guaranteed first-attempt failure.

In the message's favour: it states that the rejected admission did not consume the lens slot,
which made recovery safe and obvious.
