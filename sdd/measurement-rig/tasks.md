---
id: sdd/measurement-rig/tasks
type: journal
targets: [any]
status: draft
verified: 2026-08-07
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

## Phase 4: Analyser `derive.py` + `report.py` (blocked: Phase 2) — DONE 2026-08-07

- [x] 4.1 `rig/derive.py`: parse `stream.jsonl`; read-back verification (surface/model/cwd/ambient-drift →
      void reasons). **Scope note**: prompt and code-commit read-back are recorded on the row
      (`prompt_sha256`, `code_commit`) rather than re-voided by `derive.py`, because `run.sh` already
      guards both pre-launch (manifest compare, dirty-tree check) and design.md's own read-back table
      places those two checks at "exit 2 pre-launch", not as a `derive.py` void path.
- [x] 4.2 Outcome checker (regex line-set vs answer key) + practice checker (forbidden-tool scan +
      earlier-Read/Grep-of-file scan), plus a self-test-specific simplified practice evaluator for the
      `checker_self_test` fragments (documented in-code: those fragments carry no `file_path`, only
      `{name, is_error}`, so file-level matching is relaxed to "a Read/Grep call occurred" — disclosed
      simplification, not invented behaviour).
- [x] 4.3 Four-cell classify; total `runs.jsonl` rebuild; `schema_version` stamped; `cwd_is_expected` bool
      only, never raw `cwd` (verified: no `cwd` key appears anywhere in the emitted row).
- [x] 4.4 Verified: ran `derive.py` twice as two independent processes over the same 5 real run dirs;
      `runs.jsonl` and stdout both byte-identical (`diff` clean both times).
- [x] 4.5 `rig/report.py`: per-arm four-cell table, off-set/forbidden distribution, anomaly log (X=3) — no
      composite score anywhere in the file.
- [x] 4.6 Pairing rule: aggregate only `(task_id, iteration)` completed in **both** arms; every excluded
      slot named with its `run_id`, arm, state and void_reason.
- [x] 4.7 Confirmed: `report.py` prints `wall_ms` per row for diagnosis only; no function differences it
      between arms.
- [x] 4.8 Verified stdlib-only imports: `derive.py` uses `hashlib, json, re, sys, pathlib`; `report.py`
      uses `json, statistics, sys, pathlib`. No `pip`, no venv, no third-party import in either file.

**Bug found and fixed by running, not reasoning** (twice, both real): (1) the practice checker was
comparing full `path:line` reported strings against file-only tool-call targets — silently always failing
the match. Fixed by stripping the line number before comparison. (2) `report.py`'s anomaly log summed
`void_reason` and `anomaly_classes` separately, double-counting the same anomalous run under one class
name (`surface-mismatch` read `4` instead of `2`). Fixed by unioning both into one set per row before
counting. Neither bug was visible from reading the code; both were only visible from real output.

**Real data used, not invented fixtures**: the two gitignored completed runs `t1-broad-90` /
`t1-scoped-90` derive to `clean-failure` / `proper` exactly as predicted (broad's extra `paginate.js:23`
line fails outcome while passing practice; scoped's exact single line passes both). Three additional
leftover shakedown directories (`t1-broad-93/94/95`, pre-dating Amendments 2–3) were also present and
correctly void: `93` as `dirty-tree` (from its own `status.json`, `--dirty-ok` shakedown), `94`/`95` as
`surface-mismatch` — their `init.tools` show the OLD 54-tool/`Bash`-present surface, which no longer
matches the amended 31-tool `broad.txt` preimage. This is the read-back check correctly catching stale
captures, not a bug in either the runner or the deriver.

**`checker_self_test` run and observed to fire (R-A1.4)**, output reproduced:
```
checker self-test (R-A1.4 — each detector must be observed to fire):
  [PASS] t1/negative_control: practice_pass=False (want False), cell_if_outcome_pass='improper-success' (want 'improper-success')
  [PASS] t1/off_set_case: practice_pass=True (want True), offset_calls=1 (want 1), forbidden_calls=0 (want 0)
```

**Budget**: authored diff is `derive.py` 445 + `report.py` 179 = 624 lines, against the tasks-phase
forecast of ~400 (`runs.jsonl`'s 5 generated rows excluded from the authored count per the review-workload
convention). This is over forecast, not "well past" it by this batch's own read of that guard — the file
split is already the design-mandated one (runner/analyser/aggregator boundary), so there is no further
natural internal split, and every excess line traces to a named, verified requirement (ambient-drift
pairing, the checker self-test harness, three void-precedence layers) rather than padding. Reported here
rather than trimmed, matching how the Phase 0–3 batch handled its own overage.

## Phase 5: Negative control, observed (blocked: Phase 4) — DONE 2026-08-07

- [x] 5.1 Run the negative control: BROAD flags declaring the SCOPED expected digest. **Bookkeeping
      correction, not new work**: this was actually run, in both directions, and committed as
      `addf183` ("negative control fires both ways, and stops disabling the experiment") together
      with spec/design Amendment 3 — the checkboxes were simply never ticked at the time. No new
      commit made by this batch for 5.1/5.2 themselves.
- [x] 5.2 Observe: MUST void `surface-mismatch`. **Confirmed from `addf183`**: both directions voided
      `surface-mismatch` as required. The same commit found the second-order problem — the two
      deliberate controls plus two leftover genuine ones tripped the pre-registered X=3
      instrument-doubt threshold — and fixed it with the `0c<n>` control-slot convention (R-A3.1/R-A3.2),
      which is why `report.py`'s anomaly log now separates "controls that fired as designed" from the
      genuine count.

## Phase 6: Tier-1 pilot + derived timeout (blocked: Phase 3 AND Phase 5 both passing) — NOT STARTED,
superseded this batch by a tier-3 pilot instead; see the note below Phase 8.

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

## Phase 8: Tier-3 fixture + cell (blocked: Phase 6; independent of Phase 7) — fixture DONE 2026-08-07,
pilot run and reported, full cell (8.5) BLOCKED on a surface-preimage recapture

- [x] 8.1 Create `src/handlers/checkout.js`, `src/lib/pricing.js` (`>` vs `>=` defect),
      `src/lib/pricing.contract.md`. **Deviation, additive**: also created `src/lib/shipping.js` as a
      fourth file — a plausible decoy (its own correct boundary check, `subtotal >= 50`, sitting next
      to `pricing.js`) — a requirement of this batch's brief (multi-file, decoy, cross-referencing)
      that the literal task text above did not name. `checkout.js` imports both `pricing.js` and
      `shipping.js`, so the decoy is read by every run as part of the natural call chain, never
      artificially bolted on. Committed `bd24be0`.
- [x] 8.2 Commit `answer-key/t3.json` (+ negative control + off-set case) **before** the prompt commit.
      Same commit as 8.1 (`bd24be0`), matching the tier-1 precedent (`7441a01`) of landing fixture
      source and answer key together, still strictly before the prompt.
- [x] 8.3 Commit `prompts/t3.txt` in a later commit. Committed `939ca0b`, together with 8.4. The prompt
      names only `handlers/checkout.js` (entry point) and `lib/pricing.contract.md` (where the
      contract lives) — never `lib/pricing.js` (the defect) or `lib/shipping.js` (the decoy).
- [x] 8.4 Refreeze `MANIFEST.sha256`; verify before/after as in 7.4. Committed `939ca0b`. Verified live:
      accept-before passed (a run proceeded past the manifest check); an unstaged tamper of
      `lib/pricing.js` after refreeze produced exit 2 with the MANIFEST-mismatch message, confirmed
      live, then reverted (`git checkout --`, tree clean again before any pilot run).
- [ ] 8.5 Run tier-3 cell (N=5→15 variance rule); report N + range. **NOT started.** Blocked by the
      pilot's own finding below — the committed surface preimages are stale, so no run against them
      would be countable.

### Tier-3 pilot — 3 pairs, run 2026-08-07, explicit substitute for Phase 6

**Scope deviation, stated rather than hidden.** This batch's brief directed the tier-3 fixture plus a
small pilot directly, ahead of Phase 6's tier-1 pilot and ahead of Phase 5 being formally ticked (5.1/5.2
above are a bookkeeping correction of already-done work, not new work this batch). The reasoning carried
over from Amendment 1: tier 1 is the arm least likely to show anything, so the numbers Phase 6 exists to
produce — real cost/wall-time, a derived timeout, whether the task creates tool-call divergence, whether
the answer format holds — are more informative measured on tier 3 directly. **Phase 6 itself remains
unstarted** and is not being retroactively marked done; this is a substitution of *which* pilot produced
the calibration numbers, not a claim that Phase 6's tasks are satisfied.

Ran `t3-broad-{01,02,03}` and `t3-scoped-{01,02,03}` live, sequentially, `TIMEOUT_S=300` (pilot bound,
unchanged). Also present: one incidental extra `t3-broad-99` — a manifest-guard shakedown check (test
8.4's "accept" half) that was meant to be interrupted after ~1s and instead ran to completion because the
kill signal did not reach the child before it finished; kept as real, unmutated, non-dirty bonus evidence
rather than discarded, and clearly excluded from the "3 pairs" count below.

**Finding, and it is the headline finding of this pilot, not a footnote: all six deliberate pilot runs
voided `surface-mismatch`.** `init.tools` now carries a new built-in, `ListAgents`, absent from both
committed preimages (`rig/surfaces/broad.txt`: 31 → observed 32; `scoped.txt`: 3 → observed 4). The
bonus `t3-broad-99` ran earlier in the same session, before the drift, with the old 31-tool surface, and
is unaffected — narrowing the drift window to inside this one working session. `mcp_server_count` stayed
0 throughout (ruling out an MCP-timing repeat of design.md Amendment 3); this is a new class of drift, a
built-in tool appearing, not the MCP-connection-race class already documented. **The read-back
verification did exactly its job**: it caught the drift and voided the affected rows rather than
silently recording six rows measured against a surface that no longer matches what is committed.
`rig/report.py`'s anomaly log confirms: `surface-mismatch: 8` (2 genuine pre-Amendment leftovers + 6 new),
correctly tripping the pre-registered X=3 instrument-doubt threshold — this is not a clean log, and per
spec no `theory/` write may occur while it reads this way. **`rig/surfaces/broad.txt` and `scoped.txt`
must be recaptured — and reverified stable across repeated captures, per design.md Amendment 3's own
precedent — before Phase 6, 7, or 8.5 can produce a single countable row.** This is a blocking
prerequisite for all of them, not specific to tier 3.

The four numbers this pilot exists to produce, computed from the real transcripts despite the void
(the void concerns countability toward the four-cell classification, not whether the underlying
process timing/cost/content is real):

1. **Real per-run cost and wall time, tier 3, with spread.** BROAD: cost \$0.3103 / \$0.3169 / \$0.3102
   (all three, 4-5 turns); wall 11.6s / 13.6s / 11.7s. SCOPED: cost \$0.2637 / \$0.2206 / \$0.2214; wall
   12.8s / 11.0s / 14.6s. (Bonus `t3-broad-99`: \$0.8771, 20.6s — an outlier, likely a cold-cache session
   start; not folded into the ranges above since it is outside the deliberate 3-pair set.) This replaces
   the tasks-phase floor ("two tier-1 runs") with six real tier-3 observations: tier 3 costs roughly
   30-35% more than tier-1's per-run figures and completes in 11-15 seconds, an order of magnitude under
   the 300s pilot bound.
2. **Derived timeout.** `ceil(3 × slowest_successful_pilot_wall_s / 30) × 30`, floor 120s. Slowest of the
   six deliberate pilot runs is 14.586s (`t3-scoped-03`): `ceil(3×14.586/30)×30 = 60`, floored to **120s**.
   Using the bonus run's 20.608s instead does not change the answer (`ceil(3×20.608/30)×30 = 90`, still
   floored to **120s**). Both computations land on the floor — a real, calibrated number, replacing the
   provisional 300s, though not yet written into `run.sh`'s `TIMEOUT_S` constant (deferred to whichever
   phase actually runs the countable cell, since the surface must be recaptured first regardless and a
   constant change belongs with the run it calibrates).
3. **Tool-call divergence: minimal, and this is a finding about the fixture, stated plainly per this
   batch's own instruction.** Every one of the six pilot runs (both arms) read exactly the same four
   files, in the same order: `handlers/checkout.js` → `lib/pricing.contract.md` and `lib/pricing.js` →
   `lib/shipping.js` (the decoy, read by every run as part of the natural `require()` chain, never
   mis-reported as the defect by any run). Two of six runs (one BROAD, one SCOPED — no arm pattern)
   additionally made one `Glob **/*` call before the first `Read`. Tool-call multisets were therefore
   **identical between arms for 1 of 3 pairs** (pair 03: `Read×4` both arms) and **differed only by that
   one incidental `Glob`** for the other 2 pairs — never a qualitatively different search strategy, never
   a wrong file read, never a missed cross-reference. The fixture forces multi-file navigation and a
   contract-vs-implementation check (satisfying this batch's structural requirements), but the corrected
   navigation path is close to fully determined by the literal `require()` statements in `checkout.js`,
   so BROAD's larger surface had almost no opportunity to express itself through tool selection here —
   the same shape of result tier 1 already showed, for a related reason. **No conclusion about the
   hypothesis is drawn from this** — three pairs is far below what the pre-registered power table
   (`hypotheses/0001`) says can resolve anything, and the void status means these particular six do not
   even reach the four-cell table.
4. **Answer format: held perfectly, all 7 real runs.** Every transcript's final message was exactly
   `lib/pricing.js:12` — the exact answer-key line, exact required format, no extra text, no near-miss
   line number, in both arms and in the bonus run. No formatting or ambiguity failure occurred; the
   fixture's prompt was unambiguous to every run that completed.

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
