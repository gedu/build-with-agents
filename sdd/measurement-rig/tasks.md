---
id: sdd/measurement-rig/tasks
type: journal
targets: [any]
status: draft
verified: 2026-08-06
sources: ["sdd/measurement-rig/spec.md", "sdd/measurement-rig/design.md", "decisions/0010-measurements-vary-the-harness-not-the-model.md", "sdd/testing-capabilities.md", "AGENTS.md"]
---

# Tasks: measurement-rig

No test runner exists in this repo (`sdd/testing-capabilities.md`). Verification below is
`bash -n`, `./hooks/pre-commit[--all]`, manual adversarial exercises, and derive.py's
byte-identity re-derivation check — never "run the tests."

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | ~1,200+ authored total (run.sh ~200, derive.py ~250, report.py ~150, 3 fixtures ~500, docs/index ~60, answer-keys/prompts ~90); `runs.jsonl` rows are generated goldens, excluded from authored count |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1 → PR2 → PR3 → PR4 → PR5 → PR6 (see below) |
| Delivery strategy | ask-always |
| Chain strategy | pending — team decision needed |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | PR | Focused check | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Scaffolding + tier-1 fixture (checker-before-prompt) + `run.sh` + runner-only shakedown | PR1 | `bash -n rig/run.sh` | Manual: dirty-tree, manifest-tamper, mid-kill exercises via `rig/run.sh --dirty-ok` | Delete `rig/` entirely |
| 2 | `derive.py` + `report.py` + negative-control observation | PR2 | Run `derive.py` twice, diff `runs.jsonl` byte-identical | One real `claude` run via `run.sh` (negative control) | Revert `derive.py`/`report.py`; PR1 stays valid |
| 3 | Tier-1 pilot (10 runs) + derived timeout | PR3 | `./hooks/pre-commit --all` on new rows | 10 live `claude -p` runs (5 BROAD + 5 SCOPED) | Revert timeout constant + tier-1 rows |
| 4 | Tier-2 fixture + cell | PR4 | `bash -n`; MANIFEST before/after | Up to 15 live runs | Revert tier-2 files/rows + refreeze |
| 5 | Tier-3 fixture + cell | PR5 | Same as PR4 | Up to 15 live runs | Revert tier-3 files/rows + refreeze |
| 6 | Aggregation + `theory/` write | PR6 | `python3 rig/report.py` | N/A — pure aggregation, no live run | Revert `theory/agents/tool-surface-design.md` only |

PR2 is at the 400-line edge (derive.py+report.py ≈ 400); split into 2a/2b if the real diff exceeds budget.

## Phase 0: Scaffolding — no code (blocked: none) — DONE 2026-08-06

- [x] 0.1 Register `rig/` in `MAP.md`'s Areas table, citable **No** (instrument/process record). Verified already present (commit `575add3`); no edit needed this batch.
- [x] 0.2 Create `rig/README.md` (`type: index`): rig is an instrument, not truth; results reach `theory/` via a normal write.
- [x] 0.3 Add `/rig/runs/` to `.gitignore` **outside** `setup.sh`'s `BEGIN_MARK`/`END_MARK` managed block — verified via `./setup.sh --claude --dry-run` (managed-block count unchanged; entry not reported as managed).

## Phase 1: Tier-1 fixture, checker before prompt (blocked: Phase 0) — DONE 2026-08-06

- [x] 1.1 Create `rig/fixtures/tool-surface/v1/src/paginate.js` — `pageSlice()` off-by-one boundary defect (line 24) + 3 correct helpers.
- [x] 1.2 Commit `answer-key/t1.json` (seeded line; expected `{Read}`, off-set `{Glob,Grep}`, forbidden = rest) in its **own commit**, before 1.3 — checker-first provable from `git log` order (commit `7441a01` before `506827f`).
- [x] 1.3 In a later commit, create `prompts/t1.txt` (exact tier-1 prompt bytes). **Deviation**: path corrected to `paginate.js` (not `fixtures/v1/tier1/paginate.js` as spec's literal wording had it) — the agent's workspace is a flat copy of `src/`'s contents only (design.md Decision 4), so that literal path would never resolve. See apply report.
- [x] 1.4 Added to `t1.json`: R-A1.7 negative control + off-set case, as `checker_self_test` (consumed by `derive.py` once built, Phase 4).
- [x] 1.5 Computed + committed `MANIFEST.sha256` over tier-1 `src/`, `prompts/`, `answer-key/`.

## Phase 2: Runner `rig/run.sh` (blocked: Phase 1) — DONE 2026-08-06

- [x] 2.1 Resolve repo root from own `BASH_SOURCE`; dirty-tree guard (`git status --porcelain`) → exit 2; MANIFEST recompute-compare → exit 2; `python3`/`timeout`/`claude` presence checks → exit 2.
- [x] 2.2 `--dirty-ok` flag: bypasses dirty-tree guard only, stamps `code_commit: <sha>-dirty` + `void_reason: dirty-tree`.
- [x] 2.3 Materialize `src/` copy only to a machine-local workspace outside `<repo>` (no `answer-key/`, no discoverable repo `AGENTS.md`).
- [x] 2.4 Invoke: fixed `timeout $TIMEOUT_S claude -p … --output-format stream-json --verbose ${DISALLOW:+--disallowedTools …}`, stream redirected to a file, never piped. `rig/surfaces/broad.txt` deliberately not committed this batch (see apply report); `scoped.txt` committed as the invariant `{Glob,Grep,Read}`.
- [x] 2.5 Persist `status.json` after exit (`exit_code`, `timed_out`, `wall_ms`, `timeout_s`, `driver_version`, plus `state`/`void_reason` — a mechanical, non-semantic classification); ≤1 unparseable trailing line tolerated only when `timed_out`.
- [x] 2.6 Re-hash workspace copy post-run (substrate-mutation check), scoped to the fixture's own captured file list after a live-run false-positive was found and fixed (`.atl/` ambient cache — see apply report).
- [x] 2.7 Exit contract: 0 all `complete`/`void`, non-zero any `failed`, 2 could-not-start — `status.json` flushed before every exit path.
- [x] 2.8 Verified `bash -n rig/run.sh`.
- [x] (unassigned in this checklist, required by design Decision 6, implemented here) `mkdir`-is-the-lock idempotence claim + orphan-aside on an absent prior attempt, load-bearing for 3.1.
- [x] (found during shakedown, not a listed task) Fixed: run.sh did not forward TERM/INT to its child process, orphaning a live `claude` call on a targeted `kill <pid>`.

## Phase 3: Runner-only shakedown (blocked: Phase 2) — DONE 2026-08-06, all real live runs

- [x] 3.1 Kill a run mid-flight. SIGTERM: caught, forwarded to the child, run.sh finished gracefully (`state=void, void_reason=missing-result`) — required a runner fix (see 2.x). SIGKILL (uncatchable by any process): confirmed `stream.jsonl` had ≥1 parseable line and the dir was left `absent` (no `status.json`); a follow-up invocation of the same `run_id` correctly moved it aside as `.orphan.<ts>` and re-attempted.
- [x] 3.2 Staged fixture edit → exit 2. Unstaged fixture edit → exit 2. Both confirmed live.
- [x] 3.3 Manifest tamper (unstaged byte, dirty-tree guard bypassed via `--dirty-ok` to isolate the MANIFEST check specifically) → exit 2, confirmed live.
- [x] 3.4 Ran from `/tmp` and from a nested repo dir (`theory/`) → identical `code_commit`, matching `HEAD`, confirmed live both times.
- [x] 3.5 Prompt containing spaces, quotes, backticks, `$(cmd)`, and non-ASCII, invoked from a directory path also containing spaces and quotes → passed through byte-for-byte with no shell injection, confirmed live via the transcript's own `result` text. The `init.tools`-vs-preimage half is deferred with `rig/surfaces/broad.txt` (see apply report) — not exercised this batch.

## Phase 4: Analyser `derive.py` + `report.py` (blocked: Phase 2)

- [ ] 4.1 `rig/derive.py`: parse `stream.jsonl`; read-back verification (surface/model/prompt/code/cwd/ambient-drift → void reasons).
- [ ] 4.2 Outcome checker (regex line-set vs answer key) + practice checker (forbidden-tool scan + earlier-Read/Grep-of-file scan).
- [ ] 4.3 Four-cell classify; total `runs.jsonl` rebuild; `schema_version` stamped; `cwd_is_expected` bool only, never raw `cwd`.
- [ ] 4.4 Verify: run `derive.py` twice over same run dirs → `runs.jsonl` byte-identical.
- [ ] 4.5 `rig/report.py`: per-arm four-cell table, off-set/forbidden distribution, anomaly log (X=3) — no composite score, ever.
- [ ] 4.6 Pairing rule: aggregate only `(task_id, iteration)` completed in **both** arms; name every excluded slot + arm + void reason.
- [ ] 4.7 Confirm wall-clock is per-row diagnostic only, never differenced by `report.py`.
- [ ] 4.8 Verify stdlib-only imports (`json`, `hashlib`, `statistics`, `pathlib`); no `pip`/venv.

## Phase 5: Negative control, observed (blocked: Phase 4)

- [ ] 5.1 Run the negative control: BROAD flags declaring the SCOPED expected digest.
- [ ] 5.2 Observe: MUST void `surface-mismatch`. If not — STOP; no `theory/` write may occur; file as its own blocked follow-up, not a silent pass.

## Phase 6: Tier-1 pilot + derived timeout (blocked: Phase 3 AND Phase 5 both passing)

- [ ] 6.1 Run tier-1 cell: 5 BROAD + 5 SCOPED, `TIMEOUT_S=300` (pilot bound only).
- [ ] 6.2 If any pilot run times out: pilot invalid — raise bound, re-run before continuing.
- [ ] 6.3 Derive `ceil(3 × slowest_successful_pilot_wall_s / 30) × 30`, floor 120s; update `run.sh` constant + WHY comment.
- [ ] 6.4 Compute `T_task = 2 × (files_in_answer_key + 2) + 1`; record.
- [ ] 6.5 Apply N=5→10→15 variance rule to tier-1 spread; report final N + min/max range.
- [ ] 6.6 `./hooks/pre-commit --all` over committed rows.

## Phase 7: Tier-2 fixture + cell (blocked: Phase 6, all shakedown assertions passed)

- [ ] 7.1 Create `src/utils/date.js` (midnight boundary defect) + 3-4 correct distractors.
- [ ] 7.2 Commit `answer-key/t2.json` (+ its own R-A1.7 negative control + off-set case) **before** the prompt commit.
- [ ] 7.3 Commit `prompts/t2.txt` in a later commit.
- [ ] 7.4 Refreeze `MANIFEST.sha256`; verify accept-before / reject-tampered-after.
- [ ] 7.5 Run tier-2 cell (N=5→15 variance rule); report N + range.

## Phase 8: Tier-3 fixture + cell (blocked: Phase 6; independent of Phase 7)

- [ ] 8.1 Create `src/handlers/checkout.js`, `src/lib/pricing.js` (`>` vs `>=` defect), `src/lib/pricing.contract.md`.
- [ ] 8.2 Commit `answer-key/t3.json` (+ negative control + off-set case) **before** the prompt commit.
- [ ] 8.3 Commit `prompts/t3.txt` in a later commit.
- [ ] 8.4 Refreeze `MANIFEST.sha256`; verify before/after as in 7.4.
- [ ] 8.5 Run tier-3 cell (N=5→15 variance rule); report N + range.

## Phase 9: Aggregation + theory write (blocked: Phase 7 AND Phase 8; 9.0 gates 9.4)

- [ ] 9.0 **[BLOCKED — design gap, not decided here]** Design's Open Questions defers whether `rig/`'s `MAP.md` entry needs its own ADR to "whoever writes the first result." Needs an explicit ruling before 9.4, not a tasks-phase decision.
- [ ] 9.1 Run `rig/report.py` over all committed rows: four-cell table, off-set distribution, anomaly log, all 3 tasks.
- [ ] 9.2 Apply X=3 instrument-doubt threshold; investigate before writing `theory/` if tripped.
- [ ] 9.3 Apply the pre-registered falsification table; determine exactly one verdict (Supports/Narrows/Contradicts).
- [ ] 9.4 Modify `theory/agents/tool-surface-design.md`: verdict, four-cell table, off-set distribution, anomaly log, R-A1.6 honesty-contract limitations (6 items). No code.

## No-code tasks

0.1, 0.2, 0.3, 3.1–3.5 (verification only), 4.4, 4.8 (verification), 5.1–5.2 (run + observe), 6.2, 6.5, 6.6, 9.0–9.4.

## Blocked tasks

5.2 (gates all downstream work on the negative control firing), 6.1–6.6 (gated on 3.1–3.5 AND 5.1–5.2), 7.x/8.x (gated on Phase 6 passing in full), 9.x (gated on 7.x AND 8.x), 9.0 (design-level gap — needs an explicit ruling, not authored here), 9.4 (gated on 9.0–9.3).

## Amendment 1 — scope and delivery decided, 2026-08-06

Ratified by the operator after reading the Review Workload Forecast above.

**Scope: tier 2 is deferred. v1 is tier 1 as pilot plus tier 3 as the measurement.**

Tier 1 calibrates the rig and derives the timeout; tier 3 carries the measurement. The reasoning is a
reversal worth recording, because the obvious cut was the wrong one: **tier 1 alone is the version most
likely to return null.** One file and one action gives a run almost no opportunity to wander, so a broad
surface would look identical to a scoped one and the experiment would answer nothing. Tier 3 —
reproduce, locate, verify — is where BROAD has the most decision points and where signal should appear if
the claim in `theory/agents/tool-surface-design.md` holds at all.

Phase 7 (tier 2) is **deferred, not cancelled**. Its tasks stay in this file, unstarted. Phase 8 (tier 3)
is renumbered in effect to run immediately after Phase 6, and Phase 9's blocking condition becomes
Phase 6 AND Phase 8.

Estimated effect on the forecast: roughly 1,200 authored lines down to roughly 800, still above the
400-line budget, which the delivery decision below addresses rather than hides.

**Delivery: sequential commits to `main`. No PRs, no chain.**

This repo has no pull request in its history — every commit went straight to `main`. The 400-line budget
exists to bound review burden, and the review it bounds is the `gentle-ai` bounded review, which cannot
reach a receipt while upstream #2478 stands. A PR chain here would be ceremony bought with real
complexity.

What is kept from the chained plan is the part that carries the value: **the work-unit slicing.** Each
unit lands as its own commit, reviewable on its own, in the order the phases require. What is dropped is
only the branch and PR machinery around them.

**Task 9.0 is unblocked** by `decisions/0011-rig-produces-evidence-not-truth.md`, which rules that `rig/`
code is citable, its output is evidence only, and a figure becomes citable solely by promotion into
`theory/` carrying its scope, its spread and the honesty contract. That makes 9.4 a promotion with
preconditions rather than a write.

## Carried forward into Phase 4/5 — blocker found during the Phase 0-3 apply batch, 2026-08-06

`rig/surfaces/broad.txt` (the committed preimage of the BROAD arm's expected-visible tool set) was
**deliberately not created** in this batch. The `claude` session available to that apply batch was a
nested sub-agent invocation whose own visible tool set (33 names, missing `Glob`/`Grep` entirely, plus
several tools not part of a normal top-level session) does not match this repo's own prior reconnaissance
baseline (54 tools, 25 MCP servers — `sdd/measurement-rig/exploration.md`). Committing a preimage
captured from that sandbox would have been wrong, silently breaking every future void-classification.
`rig/surfaces/broad.txt` must be captured from a real, non-nested `claude` session (`--output-format
stream-json --verbose`, no flags, read the `init.tools` array, sort, commit) on whatever machine actually
runs Phase 5's negative control and Phase 6's pilot. `rig/run.sh` already refuses to run the `scoped` arm
with a clear exit-2 message until that file exists; the `broad` arm needs no change and was fully
exercised in Phase 3's shakedown.
