---
id: journal/2026-08-05-redaction-gate-and-2478-on-224
type: journal
targets: [any]
status: draft
verified: 2026-08-05
sources: ["upstream/gentle-ai/0001-correction-acceptance-blocks-receipt.md", "decisions/0008-review-lenses-may-use-subagents.md", "decisions/0009-redaction-is-a-repo-wide-rule.md"]
---

# 2026-08-05 — the redaction gate, and #2478 confirmed on 2.2.4

Two things happened and only one of them was planned. The planned one was ratifying ADR 0009 and
building its enforcement. The unplanned one is that the bounded review of that work reproduced a
filed upstream defect on a version where the report said it could not be tested.

## 1. Bypass record — fourth, and a different cause from the first three

**This commit ships without a `gentle-ai` review receipt.** Recorded because ADR 0008 said bypasses
must stop being routine, and a bypass that is not written down stops carrying information.

What is bypassed is narrow, and the distinction matters: the **`gentle-ai` lifecycle gate** has no
receipt to validate. The repo's own new `hooks/pre-commit` redaction gate **ran and passed** on this
commit — it was not skipped, and `--no-verify` was not used.

The first three bypasses on this date were the Agent-tool conflict, resolved by ADR 0008. **That
conflict did not recur.** The four review lenses ran as sub-agents without obstruction, which is the
first end-to-end evidence that ADR 0008 actually works. This bypass has a different and external
cause.

## 2. What the review did before it got stuck

Lineage `review-bcfce2ce488fc844`. Fresh start, workspace projection, 8 paths, 598 changed lines.
Native classification: tier **high**, on three signals it derived itself — a new file with mode
`100755`, plus `process_boundary` and `shell_source` on `setup.sh`. Four lenses, correction budget
200.

Findings: **2 CRITICAL, 5 WARNING.** Both CRITICALs were in the redaction hook, and both were real —
each was reproduced first-hand before being accepted, on the standing rule that a sub-agent's report
is not evidence.

**CRITICAL 1 — `--all` did not audit the whole tree.** The hook exempted its own file from `--all`
mode so its pattern table would not match itself. The exemption stripped *every* line of the file,
not just the table, so a secret anywhere else in it was unreachable by the audit. Fixed by
**deleting the exemption outright**: two lenses independently verified that no pattern matches its
own source text, so the exemption was never necessary. `--all` now runs clean across 58 tracked files
with nothing exempted.

**CRITICAL 2 — a fail-open in the gate.** `hits="$(… | grep -E -- "$regex" || :)"` collapsed grep's
exit 0, 1 and 2 into success. A broken pattern produced an empty result that the loop read as
"nothing found", and the commit passed. Reproduced directly: a malformed pattern exits 2, and with
`|| :` the captured output is empty. Fixed with an explicit status capture and a documented
three-state exit contract — **0 clean, 1 finding, 2 could not run.**

That second one is worth keeping for a reason beyond the fix. `theory/loops/verifier-availability.md`
argues that the dangerous state is a gate that cannot run but does not say so. **The gate written to
enforce ADR 0009 had exactly that defect on its first day**, and no amount of care in writing it
caught it — an independent lens did. The file argued the principle; the review demonstrated it on the
file's own author.

An independent read-only validator passed both fixes and surfaced one residual: `all_tracked_lines`
still swallows per-file `grep` status, so an unreadable tracked file is silently skipped in `--all`.
Same fail-open shape, narrower blast radius, `--all` only. Recorded as a follow-up because the
contract permits one correction transaction and it was already spent.

## 3. #2478 reproduces on 2.2.4 — the version gap is closed

`upstream/gentle-ai/0001` states the defect was reproduced on 2.2.2 and **not re-tested on 2.2.4**,
because a replay stops earlier at a `recovery_authorization_required` transition, so
`finalize --validation` was unreachable and the defect could be "neither confirmed nor cleared on
that version".

It reproduces on 2.2.4. Observed, in order:

1. `finalize` after four captured lens results → `correction_required`
2. `finalize --correction-lines 60` → plan accepted
3. bounded edit to one path, then `capture-evidence --outcome passed` → **succeeds**, returns a
   `record_digest`, and `status --next-transition` advances to `targeted_validation_required`
4. `finalize --validation <file>` → `Error: compact correction acceptance requires captured
   repository verification evidence`

No permutation of flags advances past step 4. Exactly what the report predicted.

**Why the earlier attempt was inconclusive and this one was not.** The earlier attempt *replayed an
abandoned lineage*, which stops before the correction stage. This was a **fresh** `review start` on a
new target, which walks the whole path and arrives at the defect. That is a reusable rule: **to test a
correction-stage defect, open a new lineage — do not replay an abandoned one.**

Issue #2478 is `open`, labels `bug` / `status:needs-review`, **zero comments**. This 2.2.4
confirmation is the most useful thing a triager could receive, and filing it is a human act — not
done here.

## 4. Why the release candidate is not the way out

Checked against the release notes rather than against memory. `v2.3.0-rc.1` carries three
self-declared defects, **none of them #2478**, and upstream's own note says *"Revert to v2.2.4 while
rc.2 is prepared."* Its first defect breaks the documented negotiated `--contract … --next-transition`
invocation — the exact bootstrap this session depends on. So the candidate would break what works and
still not fix what blocks. `rc.2` does not exist yet.

Staying on 2.2.4 is upstream's own instruction, not a preference.

## 5. Undocumented CLI behaviour, found by probing

None of this is in the orchestrator contract, and each cost time. Candidate material for a fifth
upstream report.

- The reviewer result schema is only discoverable through `gentle-ai review schema reviewer`, which
  nothing in the contract points at. Everything below was found by probing error messages first.
- `capture-result` **rejects** `--cwd` together with `--repository-context`. `capture-evidence`
  **requires** `--cwd`. Two sibling commands disagree about the same flag.
- A finding's `lens` field takes the **short** form (`risk`). Passing `review-risk` fails with
  `finding[0] is not bound to "review-risk"`, a message that names the value it just refused and
  gives no hint that the long form is the problem.
- `id` must match `^R[1-4]-…`; `evidence` is an array of plain strings, not objects; unknown fields
  are refused outright.
- Evidence must be captured against the `correction_target_identity` from the validation request, not
  against the current workspace snapshot identity. Those differ **even when the candidate tree is
  byte-identical**, which makes the mismatch invisible to a `git diff` check.

## 6. Open, deliberately

- **Lineage `review-bcfce2ce488fc844` is left in `correction_required`.** It is the second abandoned
  lineage in this repo. Benign on the same reasoning as the first, but **do not treat it as a blocker
  without re-running the bootstrap** — a fresh target returns `applicability: unrelated`, which is how
  the first one was cleared this session.
- **No committed test for `hooks/pre-commit`.** Raised by a lens as a WARNING and not fixed: a test
  would need a new path, which the frozen candidate does not admit. Where tests live in this repo is
  still ADR-shaped, and this is now the second time that gap has been recorded.
- **The `all_tracked_lines` fail-open** at the line the validator named.
- **Commenting on #2478**, which publishes under a human identity.
