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

## PR2 onward — not started

PR2 (collector + normalizer) through PR6 remain exactly as `tasks.md` describes them, all `[ ]`. PR3 is
blocked on PR1 (now satisfied — the ADR exists); PR5 is blocked on PR4; PR6 is the Hard-Ordering-Gate
closer. No PR beyond PR1 has been touched.
