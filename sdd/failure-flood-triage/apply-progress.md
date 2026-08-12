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

## PR3a-i — Clean fixture, stage-1 substrate (task 3.1 only) — DONE

Task 3.1 only. Tasks 3.2 (v2 substrate), 3.3 (`tools/generate-cases.py`), 3.4 (`case-table.sha256`), and
3.5 (`MANIFEST.sha256`) are explicitly **not** started in this batch — see `tasks.md`'s task 3.1 done-note
for the deferral reasoning. PR3a-ii picks those up.

**Files changed:**
- `rig/fixtures/failure-flood/v1/src/applyKeypadInput.ts` — new. Author-authorized donor code, copied
  byte-for-byte (no redaction needed — clean).
- `rig/fixtures/failure-flood/v1/src/confirmSeed.ts` — new. Same, clean.
- `rig/fixtures/failure-flood/v1/src/parseTransfers.ts` — new. One doc-comment genericized (see below);
  otherwise unchanged donor logic.
- `rig/fixtures/failure-flood/v1/tests/applyKeypadInput.test.ts` — new. Donor test file, import path
  updated from `./applyKeypadInput` to `../src/applyKeypadInput` (tests live in a sibling `tests/`
  directory here, not colocated with `src/` as in the donor project); assertions unchanged.
- `rig/fixtures/failure-flood/v1/tests/confirmSeed.test.ts` — new. Same import-path fix, assertions
  unchanged.
- `rig/fixtures/failure-flood/v1/tests/parseTransfers.test.ts` — new. Same import-path fix, assertions
  unchanged.
- `rig/fixtures/failure-flood/v1/runtime/package.json` — new. Pinned `devDependencies` (no `^`/`~`):
  `jest` 29.7.0, `ts-jest` 29.4.12, `typescript` 5.9.2, `@types/jest` 29.5.14, `@types/node` 20.19.9.
  `"test": "jest --config jest.config.js --runInBand"`.
- `rig/fixtures/failure-flood/v1/runtime/package-lock.json` — new. `lockfileVersion: 3`, generated once
  by `npm install` in a scratch directory outside `<repo>`; the exact bytes committed are what `npm ci`
  reproduces from the pinned `package.json` above.
- `rig/fixtures/failure-flood/v1/runtime/tsconfig.json` — new. `target: ES2020`, `module: commonjs`,
  `strict: true`, `include` covers `../src/**/*.ts` and `../tests/**/*.ts`.
- `rig/fixtures/failure-flood/v1/runtime/jest.config.js` — new. Computes `rootDir` and the `ts-jest`
  transform path from `__dirname`/`require.resolve`, never `process.cwd()`, so the same file keeps
  working if `src/`+`tests/`+`runtime/` are later copied elsewhere with the same relative layout (the
  eventual per-run materialization PR5 builds) without needing a `node_modules` symlink at a workspace
  root for this fixture's own suite to run.
- `sdd/failure-flood-triage/tasks.md` — task 3.1 marked `[x]` with the full done-note (module selection,
  redaction, runtime pinning, verification, MANIFEST deferral reason).

**Module selection, and why** (case-count table from the launch brief: `applyKeypadInput` 15,
`parseTokenAmount` 13, `confirmSeed` 12, `parseTransfers` 9, `formatTokenAmount` 8,
`isValidEthereumAddress` 8, `balanceOfCall` 7, `formatRelativeTime` 7 — all eight confirmed import-free
by direct read of the donor bytes, not taken on the audit's word):

The top six by case count (`applyKeypadInput` … `isValidEthereumAddress`, summing to 65 base cases) are
the set the launch brief's own forward-looking arithmetic is computed against (~65 × 30–35× ≈
1,950–2,275, below the ~2,500–3,000 stage-2 target — a real gap, but one this task's module choice
cannot make worse or better, since stage 1 only injects 3 of the 6 stage-2 modules, never adds a
seventh). Picked **`applyKeypadInput`**, **`confirmSeed`**, **`parseTransfers`** as the 3-of-6 for stage
1 — a subset, not an addition, because task 3.2 requires v2 to host "the same six root-cause-hosting
modules" as v1's 3, meaning v1's 3 must already be members of whatever six PR3a-ii commits to.

Independence check (read, not assumed): all three source modules and all three test files import
nothing but their own module under test — zero cross-module imports among the three, confirmed by
`rg -n "^import"` on each file. An injection into any one cannot fail a test that belongs to either of
the other two.

**Deliberately excluded from this subset: `parseTokenAmount`.** It ranks #2 by case count and would
otherwise be an obvious pick, but `parseTokenAmount.test.ts` imports `formatTokenAmount` for one
round-trip assertion (`formatTokenAmount(parseTokenAmount('42.07', 6), 6)`). Taking both `parseTokenAmount`
and `formatTokenAmount` into the same root-cause set (whether now or in PR3a-ii/PR4, since both remain in
the six-module set regardless) means an injection into `formatTokenAmount` alone would also fail a
`parseTokenAmount` test — a masking pair the "no cause can mask another" requirement exists to prevent.
Flagged here, at 3a-i, specifically so PR4's per-injection isolation validation (task 4.1) does not
discover it as a surprise: whichever future task assigns these two modules their stage-2 root causes
needs either (a) an isolation check that treats the round-trip assertion's failure as informative rather
than a masking violation, or (b) a small edit to that one round-trip test at injection time so it isolates
correctly. Neither is decided here — this is a heads-up for PR3a-ii/PR4, not a fix.

Root-cause intent recorded for PR4 (not built now — PR4 is out of scope for this batch):
- `applyKeypadInput`: a boundary/off-by-one condition in the decimal-cap comparison
  (`current.length - dotIndex - 1 >= maxDecimals`) or the leading-zero replacement branch.
- `confirmSeed`: an index/position-mapping defect between `CONFIRM_POSITIONS` (`[2, 6, 10]`) and the
  `picks` array — e.g. an off-by-one in the position used inside `isConfirmCorrect`'s `every`.
- `parseTransfers`: a direction/fee-association mapping defect — e.g. losing the case-insensitive address
  compare, or keying the fee `Map` on the wrong hash.

**Redaction (manual read of every copied line, per instruction — the gate cannot catch bare project
names):**
- `parseTransfers.ts`'s doc-comment named a specific third-party indexer product by name. Genericized to
  "a token-transfers indexer endpoint." Judgment call, stated as one: this is a third party's public
  product name, not the donor's own project/client/employer/person name that ADR 0009 targets, and the
  proposal's authorization already accepts the product domain becoming visible — but the name added
  nothing the module's behavior needed, so it was the cheaper thing to remove rather than defend.
- No absolute path, project name, employer name, person name, API key, token, hostname, or
  real-deployment contract address found in any of the six copied files (3 source + 3 test). The one
  fixed constant that looks address-shaped (`BALANCE_OF_SELECTOR` — this repo did not end up copying the
  module that defines it, since `balanceOfCall` was not one of the three selected) is a public ERC-20
  method selector, not a private value, and is moot here since that file was not copied.
- `rg -n "react-native|from 'react'|from \"react\"|expo-|MMKV|mmkv"` over the whole new fixture directory
  → no matches, confirming the audit's "RN-free" claim against the actual copied bytes rather than
  trusting it.
- `rg -n -i "<donor-project-name>|<repo-external-home-dir>"` (the two identifying strings this report
  itself must not write) over the new fixture directory → no matches.

**Verification run, with real results:**
- Scratch build (outside `<repo>`): `npm install` in the scratch `runtime/` → 280 packages, generates
  `package-lock.json`. `npm test` → **3 suites, 36 tests, 0 failures, exit 0.**
- Real verification (per ADR 0014 Clause A — never in the committed tree): copied the actual staged
  `src/`, `tests/`, `runtime/` bytes to a fresh `mktemp -d` directory outside `<repo>` (mirroring
  `rig/run.sh`'s existing pattern), `npm ci` there (fresh install strictly from the committed lockfile,
  not the scratch one) → 281 packages, then `npx jest --config jest.config.js --runInBand` from
  `runtime/` → **3 suites, 36 tests, 0 failures, exit 0.** Re-ran via the committed `npm test` script
  itself → same result, exit 0. Temp directory removed afterward; confirmed no `node_modules/` anywhere
  under `<repo>` and `.gitignore` unchanged.
- `git add rig/fixtures/failure-flood/v1` then `./hooks/pre-commit --all` → **exit 0**,
  `"redaction check: clean across 134 tracked files"`. `./hooks/pre-commit` (staged-only, no `--all`) →
  **exit 0**, no output.

**Line budget:** `git diff --cached --numstat` on the ten new files: 4,253 insertions / 0 deletions
across `runtime/jest.config.js` (28), `runtime/package-lock.json` (3,860), `runtime/package.json` (16),
`runtime/tsconfig.json` (14), the 3 source files (33 + 17 + 59 = 109), and the 3 test files
(65 + 70 + 91 = 226). **Authored lines only, per Section E's "generated goldens are excluded from
authored risk count" rule — `package-lock.json` is machine-generated, deterministic `npm install` output,
the same class of artifact that rule names, not hand-authored content: 393 lines, well inside the
700-line ceiling this batch was given.** Raw diff (including the lockfile) is 4,253 lines, ~6× the
ceiling — reported here rather than hidden, exactly because the ceiling's own wording ("ratified for the
remaining stack") did not name a lockfile exception explicitly; this batch is applying Section E's
general rule to a case Section E's own example phrase ("generated goldens") describes closely enough to
apply, but the orchestrator may disagree with that reading. Excluding no other file from the count.

**Not committed or pushed** — staged only, per instruction; the commit is the orchestrator's, which
still has the attempt ledger to settle.

## PR3a-ii onward — not started

Task 3.2 (v2 stage-2 substrate) through 3.5 (`MANIFEST.sha256`), and PR4–PR6 in full, remain exactly as
`tasks.md` describes them, all `[ ]`. PR3a-ii depends on this batch (satisfied for its own scope) and
should also resolve the `parseTokenAmount`/`formatTokenAmount` cross-test-import flag above before or
during PR4's isolation validation. Not touched: `rig/derive.py`, `rig/run.sh`, `rig/collect.py`,
`rig/fixtures/failure-flood/v2/`, `tools/`.
