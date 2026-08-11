---
id: sdd/failure-flood-triage/apply-progress
type: journal
targets: [any]
status: draft
verified: 2026-08-11
sources: ["sdd/failure-flood-triage/tasks.md", "sdd/failure-flood-triage/spec.md", "sdd/failure-flood-triage/design.md"]
---

# Apply progress: failure-flood-triage

Chained-PR delivery (`stacked-to-main`). This journal is appended per PR batch, never rewritten; each
entry names its own PR and leaves prior entries untouched.

## PR1 — Peak-occupancy retro-derive + fixture/repo boundary ADR — DONE

All five tasks (1.1–1.5) complete. See `sdd/failure-flood-triage/tasks.md`'s PR1 section for the
per-task done-notes and the findings note directly below it.

**Files changed:**
- `rig/derive.py` — modified. `parse_stream` now also returns a stream-ordered, `message.id`-de-duplicated
  `turns` list (kept first occurrence). New `compute_occupancy()` helper computes `model_turns`,
  `occupancy_series`, `peak_occupancy_tokens`, `peak_occupancy_turn`, `cumulative_occupancy_tokens`,
  `occupancy_aggregate_matches`, `occupancy_is_monotone`, `context_window_tokens`. `SCHEMA_VERSION` 2 → 3.
- `rig/results/tool-surface-v1/runs.jsonl` — regenerated (derive.py is a total function; all 42 rows
  rebuilt from the raw captures under gitignored `rig/runs/`).
- `decisions/0014-a-fixtures-runtime-is-substrate-not-this-repos-runner.md` — new. Two clauses per
  R-F11.1/R-F11.2.
- `sdd/failure-flood-triage/tasks.md` — PR1 tasks marked `[x]`, findings note added.

**Verification run, with real results:**
- `python3 -m py_compile rig/derive.py` → exit 0.
- `python3 rig/derive.py` → exit 0, derived 42/42 rows, idempotent re-run (total-function property held).
- Projection regression (task 1.2): before/after `runs.jsonl` compared per row, excluding
  `schema_version`, `checker_digest`, and the eight new keys. **0 mismatches across 42/42 rows.**
- `occupancy_aggregate_matches` (task 1.3): **`true` on 42/42 rows.** Mutation check on a scratch copy
  of one capture's `stream.jsonl` (never `rig/runs/`, gitignored and untouched) — bumping one turn's
  `cache_read_input_tokens` by 1000 flips the field to `false`. Detector proven able to fire (R-A1.4).
- `occupancy_is_monotone` (task 1.4): **`true` on 42/42 rows, non-null everywhere.** See finding below.
- `./hooks/pre-commit --all` → **exit 0**, "redaction check: clean across 122 tracked files" (covers all
  four changed/new files once staged).
- `./hooks/pre-commit --self-test` → **exit 0**, all 3 cases PASS.

**The `occupancy_is_monotone` finding, stated plainly:** all 42/42 existing `tool-surface-v1` rows have a
non-decreasing per-turn occupancy series; peak equals the final turn everywhere in this corpus. This is
the same result both previously-sampled captures showed, now settled across the full set rather than
assumed from a sample. Per R-F5's own framing this means **peak occupancy carries no information beyond
cumulative on this task class** — a real, reportable finding, not an instrument failure. It says nothing
about `failure-flood-v1`'s multi-step pipeline arm, where fresh per-step sessions and different cache
behavior are exactly the shape that could diverge; this result is scoped to `tool-surface-v1` only.

**Corrections to the launch brief, verified against this machine's actual state:**
- The claimed `rig/runs/` (43 dirs) vs `runs.jsonl` (42 rows) discrepancy **does not reproduce here**:
  both are exactly 42, with an exact 1:1 `run_id` ↔ directory-name correspondence, symmetric difference
  empty. Recorded as a correction, not papered over with an invented explanation for a gap that isn't
  there on this machine.
- `decisions/0014-*.md`'s Clause B roster (four self-test-carrying executables: `hooks/pre-commit`,
  `rig/derive.py`, `rig/run-pipeline.sh`, `rig/collect.py`; the case generator named as the *future*
  candidate, not one of the four) follows this task's explicit brief rather than `design.md`'s own
  "what the ADR must settle" paragraph, whose literal four-item list drops `rig/derive.py` (ADR 0013's
  own cited precedent) while folding `tools/generate-cases.py` into the same list it later names as the
  future candidate. Neither four-item list reconciles against ADR 0013's own "two already, a third
  triggers" framing (2 pre-existing + 3 new = 5 once every PR lands). Flagged for the record; does not
  change Clause B's decision either way.

**Line budget:** `git diff --cached --stat` on the four changed files: 286 insertions / 60 deletions
(346 total). Authored lines only (excluding the machine-regenerated `runs.jsonl`): 262 — within the
~260-line estimate and the 400-line PR1 budget.

**Not committed or pushed** — staged only, per instruction; the commit is the orchestrator's.

## PR2 — Collector + signature normalizer — DONE

All four tasks (2.1–2.4) complete. See `sdd/failure-flood-triage/tasks.md`'s PR2 section for the
per-task done-notes.

**Files changed:**
- `rig/collect.py` — new. `python3`, stdlib only (`argparse`, `hashlib`, `json`, `os`, `re`, `shutil`,
  `subprocess`, `sys`, `unittest.mock` for the self-test's toolchain-absent patch). Collector +
  signature normalizer + flag-gated `--self-test` in one file, per Decision 9a's precedent
  (case-generator-style single-file self-test).
- `sdd/failure-flood-triage/tasks.md` — PR2 tasks 2.1–2.4 marked `[x]` with per-task done-notes.

**What `collect.py` implements, beyond the task list's own literal wording** (design.md §9b/§9c bind
this file per the launch brief, even though the task bullets for 2.1/2.2 don't spell every clause out):
- `report_bytes` recorded on the envelope, plus `--max-report-bytes` (default 64 MiB) as a declared
  ceiling — over it, `collect()` raises `CollectorError("report-too-large", ...)`, which `main()` turns
  into exit 2. No streaming parser; `json.load` is used directly, per design.md 9b's explicit rejection
  of "infrastructure ahead of content."
- **Two artifacts, not one.** `build_collection()` produces the full `collection/1` (failures + clusters,
  each cluster carrying `member_test_ids`); `clusters_view()` derives a second, separate `clusters/1`
  dict that drops `member_test_ids` entirely. The CLI writes both, to `--collection-output` and
  `--clusters-output` respectively. The clusters view is bounded by cluster count because it simply
  never carries the per-failure list, not because of any additional truncation logic.
- `suite_timeout_s` handling: `collect()` calls `run_suite()`, which wraps the suite subprocess in
  `subprocess.run(..., timeout=suite_timeout_s)`. A `TimeoutExpired` is classified `partial` with
  `partial_reason: "suite-timeout"` — a **suite-axis** measurement, never `collector-error`. The CLI
  exposes this as `--suite-timeout-s` (default 120.0) with a docstring/help note that the caller (future
  `run-pipeline.sh`, PR5) MUST pass a value smaller than its own arm timeout — `collect.py` itself has no
  visibility into the arm timeout and cannot enforce the "smaller than" half of that rule; it only
  enforces whatever value it's given. **Recorded here as a real limitation for PR5 to close, not
  papered over**: the separation design.md 9b requires is a *contract between two files*, and this PR
  can only build its half.
- `collector-error` (run axis, exit 2) covers: absent `node`/`npm` on PATH (`toolchain-absent`), a crash
  launching the subprocess (`collector-crash`), and `report-too-large`. **Deliberately NOT implemented
  in this PR**: `node`/`npm` version-floor checking and lockfile-digest-mismatch detection, both named
  in design.md's Decision 3 table as `collector-error` causes. Neither has an actual floor value or
  lockfile to check against yet — those arrive with the real fixture/runtime in PR3/PR4 (`package.json`
  + `package-lock.json` under `runtime/`). Building the check now against no real lockfile would be
  guessing at an interface PR3/PR4 might change; flagged rather than stubbed silently.

**The normalizer's exact algorithm, as implemented** (design.md's own algorithm items 1–5, plus one
elaboration the design text leaves implicit): the "matcher-shaped head" (item 4) is computed as
strip-ANSI → CRLF→LF → truncate at the first line matching `^\s*at ` (the first stack frame) → truncate
*that* result again at the first line matching `^\s*(Expected|Received)\b` → rewrite any
workspace-absolute path substring to relative → rewrite `:\d+:\d+` to `:L:C` → collapse whitespace runs
→ strip. The Expected/Received truncation is the one design.md states as a *consequence* ("never the
expected/received body") without giving the exact cut rule; the regex above is this implementation's
concrete choice, and the self-test's case (a) exercises it directly by feeding two failures that differ
in **both** path/line/col **and** Expected/Received values and asserting they still collapse to one
signature — the 9c amplification requirement, not just the path/line/order case the task bullet names.

**Verification run, with real results:**
- `python3 -m py_compile rig/collect.py` → **exit 0**.
- `python3 rig/collect.py --self-test` → **exit 0**, all 9 checks PASS: (a) same-cause/differing
  path+line+col+order+Expected-Received → same signature; (b) two genuinely different causes → different
  signatures (the discrimination case a constant-returning normalizer would fail); (c.1)–(c.4) each of
  `ran`/`did-not-start`/`partial`/`partial+suite-timeout` fires from a synthetic report; (d) same input
  twice → byte-identical `json.dumps(..., sort_keys=True)` output; (e) absent toolchain (patched via
  `unittest.mock.patch.object(shutil, "which", return_value=None)`) → `CollectorError("toolchain-absent")`,
  never a suite state; (f) `clusters_view()` carries no `member_test_ids`, one row per cluster.
- `python3 rig/collect.py` (no flag, no other args) → **exit 2**, printed
  `"--report-file, --collection-output and --clusters-output are required for a real run (only
  --self-test may omit them)"` — confirms the self-test flag is gated: this path never reaches
  `run_self_test()`, so a no-flag invocation inside a measured arm prints/pays nothing beyond the normal
  collection attempt (task 2.4's verify).
- `git add rig/collect.py sdd/failure-flood-triage/tasks.md` then `./hooks/pre-commit --all` → **exit 0**,
  `"redaction check: clean across 124 tracked files"`.
- `./hooks/pre-commit --self-test` → **exit 0**, all 3 cases PASS (unchanged by this PR; re-run for the
  record since `--all` was also re-run).

**Line budget — over, flagged rather than hidden:** `git diff --cached --numstat` on the two changed
files: `rig/collect.py` 552 insertions / 0 deletions; `sdd/failure-flood-triage/tasks.md` 25 insertions /
13 deletions. **Total 590 changed lines against the launch brief's 500-line budget and ~300-line
estimate — 90 lines (18%) over.** The overage traces to implementing the design.md §9b/§9c scale
clauses (report-too-large ceiling, the second `clusters/1` artifact, the `suite-timeout` partial
sub-case) that the task list's own 2.1/2.2 bullets don't spell out in full, on top of the base collector
+ normalizer + 9-case self-test the ~300-line estimate was presumably sized against. Not trimmed after
the fact to force it under budget, since every one of those clauses was named explicitly binding by this
phase's own launch instructions.

**Not committed or pushed** — staged only, per instruction; the commit is the orchestrator's, which
still has the attempt ledger to settle.

## PR3 onward — not started

PR3 (clean fixture + case generator) through PR6 remain exactly as `tasks.md` describes them, all `[ ]`.
PR3 depends on PR1 (satisfied) and PR2 (now satisfied — the collector exists to validate the clean
baseline); PR5 is blocked on PR4; PR6 is the Hard-Ordering-Gate closer. Not touched: `rig/derive.py`,
`rig/run.sh`, any fixture under `rig/fixtures/`.
