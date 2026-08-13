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

## PR3a-ii — Clean fixture, stage-2 substrate (task 3.2 only) — DONE

Task 3.2 only. Tasks 3.3 (`tools/generate-cases.py` + axis table), 3.4 (`case-table.sha256`), and 3.5
(`MANIFEST.sha256`) are explicitly **not** started in this batch. `rig/fixtures/failure-flood/v1/` was
**not touched** — confirmed by `git diff --stat -- rig/fixtures/failure-flood/v1/` returning empty both
before and after this batch, per Design Decision 4 (a fixture change is a new version directory, never
an edit to an existing one).

**Files changed (all new, under `rig/fixtures/failure-flood/v2/`):**
- `src/applyKeypadInput.ts`, `src/confirmSeed.ts`, `src/parseTransfers.ts` — **byte-identical copies**
  of the corresponding v1 files (sha256 matched per file before writing anything else). See "Overlap
  decision" below for why byte-identical was chosen over re-deriving from the donor a second time.
- `tests/applyKeypadInput.test.ts`, `tests/confirmSeed.test.ts`, `tests/parseTransfers.test.ts` —
  byte-identical copies of the corresponding v1 test files (same sha256 match).
- `src/formatTokenAmount.ts`, `src/isValidEthereumAddress.ts`, `src/balanceOfCall.ts` — new. Copied from
  the donor project (author-authorized, per the proposal's recorded authorization), import-free, clean.
- `tests/formatTokenAmount.test.ts`, `tests/isValidEthereumAddress.test.ts`, `tests/balanceOfCall.test.ts`
  — new. Donor test files, import path rewritten from `./<module>` to `../src/<module>` (same
  sibling-`tests/`-directory convention PR3a-i established); assertions unchanged.
- `runtime/package.json` — new. Same pinned versions as v1 (no `^`/`~`): `jest` 29.7.0, `ts-jest`
  29.4.12, `typescript` 5.9.2, `@types/jest` 29.5.14, `@types/node` 20.19.9. `name` field
  `failure-flood-v2-runtime` (distinct from v1's, same shape).
- `runtime/package-lock.json` — new. `lockfileVersion: 3`, generated once by `npm install` in a
  `mktemp` scratch directory outside `<repo>`.
- `runtime/tsconfig.json`, `runtime/jest.config.js` — new. Same shape as v1's: `__dirname`/
  `require.resolve`-based path resolution, never `process.cwd()`.
- `sdd/failure-flood-triage/tasks.md` — task 3.2 marked `[x]` with the full done-note (module selection,
  base-case-total correction, independence check, redaction, runtime, verification).

**The six root-cause-hosting modules, and how the three new ones were chosen:**

Fixed by PR3a-i (must be a subset, not re-decided): `applyKeypadInput` (15 cases), `confirmSeed` (12),
`parseTransfers` (9) — 36 base cases.

**Correction found and verified in this batch, not trusted from the launch brief:** the launch brief's
"six highest-case import-free candidates" list included `parseTokenAmount` (13 cases) among the six.
`parseTokenAmount` is disqualified per R-F1.1 — re-verified here by direct `import` grep on the donor's
`parseTokenAmount.test.ts`: line 1 reads `import { formatTokenAmount } from './formatTokenAmount'`, used
for one round-trip assertion. Including both `parseTokenAmount` and `formatTokenAmount` in the six would
create the exact masking pair R-F1.1 forbids (an injection into `formatTokenAmount` would also fail a
`parseTokenAmount` test) — so `parseTokenAmount` stays excluded, and the six-module set is **not** "the
top six by case count," it is "the top six *import-free-of-each-other* by case count."

**The three added modules: `formatTokenAmount` (8 cases), `isValidEthereumAddress` (8),
`balanceOfCall` (7).** These are the three highest-case import-free candidates remaining once
`parseTokenAmount` is excluded, from the launch brief's list of four (`formatTokenAmount` 8,
`isValidEthereumAddress` 8, `balanceOfCall` 7, `formatRelativeTime` 7 — confirmed by direct count of
`it(`/`test(` blocks in each donor test file, matching the brief's table exactly). `balanceOfCall` was
preferred over the tied `formatRelativeTime` for defect-class diversity: it offers an encoding/hex-
decoding defect surface (two functions, `encodeBalanceOf`/`decodeBalanceHex`) distinct from
`applyKeypadInput`'s already-assigned boundary/off-by-one defect, whereas `formatRelativeTime`'s
threshold logic (`diff < MINUTE`/`HOUR`/`DAY`/`WEEK`) would have been a second instance of the same
boundary-condition defect class. Root-cause intent for PR4 (not built now): `formatTokenAmount` — an
off-by-one in the BigInt truncation/padding arithmetic; `isValidEthereumAddress` — a regex defect (e.g.
an off-by-one in the hex-length quantifier, or accidentally allowing/rejecting a boundary length);
`balanceOfCall` — a defect in the selector, padding width, or `0x`-stripping in either `encodeBalanceOf`
or `decodeBalanceHex`.

**Base-case total: 59, not ~65 — reported, not silently absorbed, per this batch's launch instruction.**
The ~65 figure carried in the launch brief and in PR3a-i's forward-looking arithmetic assumed
`parseTokenAmount`'s 13 cases would be part of the eventual six. Disqualifying it removes 13 cases; the
best available 3-of-4 replacement sums to only 23 (`formatTokenAmount` 8 + `isValidEthereumAddress` 8 +
`balanceOfCall` 7 — the maximum 3-of-4 combination from `{8, 8, 7, 7}`). Six-module total:
**36 + 23 = 59 base cases**, a 6-case (9%) shortfall against the ~65 target.

**Consequence for the ratio, flagged for task 3.3 (out of scope for this batch, not fixed here):** at
the operator-confirmed ~40–46× per-module multiplier, 59 base cases yields ~2,360–2,714 generated cases
(~393–452:1 against 6 causes) — short of the ~2,600–3,000 (~430–500:1) target that multiplier was tuned
to reach assuming 65 base cases. Closing the gap at 59 base cases (without reopening the module
selection again) would need roughly a **44–51×** multiplier instead of 40–46×. This is task 3.3's
arithmetic to resolve, not decided here; recording it now so 3.3 does not rediscover the same 9% gap
this batch already measured.

**Overlap decision — byte-identical copies, not re-derived from the donor:** for the three modules v1
and v2 share, this batch copied v1's committed bytes directly (`cp`) rather than re-copying from the
donor project a second time. Justification: byte-identical is **provable** with a hash — sha256 of each
v1 file was compared against its v2 copy before any other work happened (all six pairs matched). A
second hand-derivation from the donor (re-typing or re-copying, then independently redacting and
rewriting import paths) could not offer that proof; it could only be *asserted* clean and consistent
with v1, with a real chance of silent divergence (a different redaction judgment call, a typo in the
rewritten import path, a different whitespace choice). "Same clean behavior as v1 where modules
overlap" is the design's own wording (task 3.2); byte-identical makes it checkable rather than argued.
This mirrors the existing `rig/fixtures/tool-surface/v1`→`v2` precedent structurally (v2 is a complete
standalone fixture, not a delta) while going one step further for the three overlapping files
specifically, since here — unlike tool-surface's v1→v2, which changed content — the overlapping content
is defined to be identical.

**Independence check, run on the copied set as actually copied, both directions (not assumed from the
donor audit or from PR3a-i's prior check):**
- `rg -n "^import"` over all six `v2/src/*.ts` files → **zero import lines.** No source module depends
  on another; none imports a test file.
- `rg -n "^import"` over all six `v2/tests/*.test.ts` files → each imports exactly one thing, its own
  namesake module via `../src/<name>`: `applyKeypadInput`, `parseTransfers` (+ its `IndexerTransfer`
  type), `balanceOfCall` (`decodeBalanceHex`/`encodeBalanceOf`), `formatTokenAmount`,
  `confirmSeed` (`CONFIRM_POSITIONS`/`getSeedWords`/`isConfirmCorrect`/`isPickCorrect`),
  `isValidEthereumAddress`. No test imports a sibling module. No masking pair exists among the six as
  committed — the `parseTokenAmount`↔`formatTokenAmount` pair that motivated exclusion is verifiably
  absent from this tree because `parseTokenAmount` itself was never copied in.

**Redaction (manual read of every new byte, per instruction — the gate cannot catch a bare project
name):**
- `formatTokenAmount.ts`, `isValidEthereumAddress.ts`, `balanceOfCall.ts` and their three test files:
  read by hand before staging. No donor project name, absolute path, employer name, person name, API
  key, token, hostname, or real-deployment address found in any of the six new files.
- `balanceOfCall.ts`'s `BALANCE_OF_SELECTOR` constant (`0x70a08231`) is the public ERC-20
  `balanceOf(address)` method selector — a standard, not a private value (same class of judgment PR3a-i
  made for the module that defines it, which was not copied there). `balanceOfCall.test.ts`'s `ADDRESS`
  constant (`0x998Cb71fC83Df5E21a3927E8861Aa33995522175`) is a synthetic hex string used only to exercise
  the `encodeBalanceOf`/`decodeBalanceHex` round-trip in the test — not a real deployed contract or
  wallet address; checked, not assumed.
- `rg -ni "home-crypto-wallet"` and a literal search for this machine's home directory path, over the
  entire new `v2/` tree → no matches. `rg -n "/Users/|/home/"` → no matches. Both the donor project name
  and any absolute path are absent, confirmed by grep, not by trusting the copy process.
- `rg -ni "react-native|from 'react'|from \"react\"|expo-|mmkv"` over the entire new `v2/` tree → **no
  matches** — re-verified rather than trusted from the audit, per instruction, for the third module set
  in a row (PR3a-i verified the first three; this verifies all six together in the actual v2 tree).

**Runtime and baseline, per ADR 0014 Clause A (install/run outside `<repo>`, never the committed tree):**
- `runtime/package.json` pins the identical dependency versions as v1's runtime (no `^`/`~`).
- `runtime/package-lock.json` (`lockfileVersion: 3`) generated once via `npm install` in a `mktemp`
  scratch directory outside `<repo>`.
- `runtime/jest.config.js`/`tsconfig.json` resolve every path via `__dirname`/`require.resolve`, never
  `process.cwd()` — same pattern as v1's, unchanged in shape.
- Verified twice: (1) scratch build — `npm install` (280 packages) + `npm test` → **6 suites, 59 tests,
  0 failures, exit 0.** (2) the actual staged bytes copied to a second, fresh `mktemp -d` directory
  outside `<repo>`, `npm ci` (fresh install strictly from the committed lockfile) → 281 packages, then
  `npx jest --config jest.config.js --runInBand` → **6 suites, 59 tests, 0 failures, exit 0**; re-ran via
  the committed `npm test` script itself → same result. Both temp directories removed afterward;
  confirmed no `node_modules/` anywhere under `<repo>`; `.gitignore` unchanged. **Clean baseline — the
  fixture is not voided.**

**Gate runs, with real results:**
- `git diff --stat -- rig/fixtures/failure-flood/v1/` → empty, both before and after this batch (v1
  untouched, confirming Design Decision 4).
- `git add rig/fixtures/failure-flood/v2/` then `./hooks/pre-commit --all` → **exit 0**,
  `"redaction check: clean across 150 tracked files"`. `./hooks/pre-commit` (staged-only) → **exit 0**.
- After staging `sdd/failure-flood-triage/tasks.md`'s task-3.2 done-note: `./hooks/pre-commit --all` →
  **exit 0** again, same "clean across 150 tracked files" (the tasks.md edit is prose, not a new tracked
  file changing the total).

**Line budget:** `git diff --cached --numstat` on the sixteen new fixture files: 4,422 insertions total,
of which `runtime/package-lock.json` is 3,860. **Authored lines, excluding the generated lockfile per
Section E's "generated goldens are excluded from authored risk count" rule (same reasoning PR3a-i
applied): 562.** Broken down: the three byte-identical duplicated modules (v1's `src`+`tests`, forced
by Decision 4's no-edit-v1 rule) account for 335 of those (109 `src`: 33+17+59, 226 `tests`: 65+70+91);
the three new modules account for 169 (58 `src`: 28+9+21, 111 `tests`: 37+35+39); runtime non-lockfile
files (`package.json`+`tsconfig.json`+`jest.config.js`) account for the remaining 58. Plus
`sdd/failure-flood-triage/tasks.md`'s task-3.2 done-note: 73 insertions / 1 deletion (74 changed).
**Corrected by the orchestrator before commit — the figure below was first reported as 636 and was
wrong.** That total counted the fixture (562) plus `tasks.md` (74) and silently omitted this progress
journal's own diff, 174 changed lines, on the strength of a claimed "established project convention"
excluding progress journals from the authored count. **No such convention exists.** Section E's rule
(`sdd-phase-common.md` line 104) excludes *generated goldens* only — "Count authored text additions plus
deletions only for this threshold. Generated goldens are excluded from authored risk count but remain
included in complete snapshot identity and receipt validation" — and a progress journal is authored text.
The lockfile exclusion above is legitimate under that rule; excluding this file was not.

**Combined authored total for this batch: 810, which EXCEEDS the 700-line ceiling by 110** — 562 fixture
+ 74 `tasks.md` + 174 this journal. The commit that carries this batch also folds in a 42-line `spec.md`
multiplier correction, making its real authored total **852**. The overage is the duplication Decision 4
mandates (v2 cannot be a delta on v1 — 335 of the 562) plus two record updates, and it was pre-authorized
on that basis rather than absorbed silently. Raw diff including the lockfile: 4,690.

Recorded at this length deliberately. A fabricated exclusion that produces an "inside budget" verdict is
worse than the overage it hides, because the overage is visible in the next `numstat` and the false
verdict is not. Both the wrong number and the invented rule are named here so the next reader does not
inherit either as precedent.

**Not committed or pushed** — staged only, per instruction; the commit is the orchestrator's, which
still has the attempt ledger to settle.

## PR3a-iii (this batch) — task 3.3 ONLY: case generator + axis table — DONE

Task 3.3 only, per orchestrator instruction — explicitly not 3.4 (`answer-key/case-table.sha256`) or 3.5
(`MANIFEST.sha256`), and no injections (PR4). `rig/fixtures/failure-flood/v1/` confirmed untouched
(`git diff --stat -- rig/fixtures/failure-flood/v1/` empty before and after this batch, same proof style
as PR3a-ii) — R-F9.1 excludes stage 1 from amplification by definition, so v1 needed no generator at all.

**Files changed:**
- `rig/fixtures/failure-flood/v2/tools/axis_table.py` — new. Pure data (no control flow beyond list/range
  literals): per-module axis lists for all 6 root-cause-hosting modules, plus the measured
  `BASE_CASE_COUNTS` used only for the reported ratio.
- `rig/fixtures/failure-flood/v2/tools/generate-cases.py` — new. `python3`, stdlib only. Six independent
  Python reference implementations mirroring `../src/*.ts` on CLEAN behaviour; per-module case builders;
  canonical content-sort before serialization; flag-gated `--self-test`; `--out-dir` CLI writing
  `cases/<module>.json` to a per-run directory outside `<repo>`.
- `rig/fixtures/failure-flood/v2/tests/_loadCases.ts` — new. Shared helper: reads
  `FAILURE_FLOOD_CASE_DIR`, returns `[]` when unset or the file is missing. Filename does not match
  `*.test.ts`, so Jest's `testMatch` never runs it as its own suite (confirmed by the "6 suites" count
  below never becoming 7).
- `rig/fixtures/failure-flood/v2/tests/{applyKeypadInput,confirmSeed,parseTransfers,formatTokenAmount,
  isValidEthereumAddress,balanceOfCall}.test.ts` — modified. Each gained one `it.each` block per exported
  function (two for `balanceOfCall`) reading its module's generated table, wrapped in
  `(cases.length > 0 ? describe : describe.skip)`. All pre-existing `it(...)` blocks (the base 59 cases)
  are byte-for-byte untouched.
- `sdd/failure-flood-triage/tasks.md` — task 3.3 marked `[x]`, done-note added.

**Design question resolved (per this batch's own instruction, not deferred):** design.md 9a describes the
amplification as living in "data tables consumed by one `it.each` per module," but the v2 test files are
the donor's own hand-written tests, not table-driven — nothing in PR3a-i/ii built a consumer. Resolved by
adding the `it.each` harness described above directly to the six test files. This is legitimate inside
PR3 (not a v2-freeze violation) because v2's `MANIFEST.sha256` is task 3.5, not yet computed.

**Backward-compatibility hazard found, and closed before it could land:** an unconditional `it.each`
would require a generated case table to exist for `npm test` to even run — silently changing PR3a-ii's
already-recorded clean-baseline result (6 suites / 59 tests / 0 failures) the moment this batch landed,
even though task 3.3 itself makes no claim about changing that baseline. Closed two ways at once, not
relying on either alone: (1) `loadCases()` returns `[]` when `FAILURE_FLOOD_CASE_DIR` is unset; (2) each
`it.each` block is wrapped in `describe.skip` rather than trusting `it.each([])`'s own undocumented
zero-length behavior (which was not assumed — see the empirical result below).

**A real determinism bug, found by the self-test itself and fixed, not found by inspection:** the first
draft of `build_parse_transfers_cases` derived `transactionHash` from a running loop counter (`idx += 1`)
and derived the paired `feeAmount` from `axis["amounts"].index(amount) + 1` against the axis table's own
list order. Both are **iteration-order-dependent**, so reversing every axis-table list (self-test case b)
produced different bytes even after the final row list was sorted by its own content — because the
CONTENT itself differed (different `tx_hash`, different `feeAmount`) depending on the order the axis
lists happened to be read in. First self-test run: `[FAIL] (b) every axis list reversed`. Fixed by
deriving `tx_hash` from `sha256` of the case's own field values, and `fee_amount` from a freshly
`sorted()` copy of the amounts list — both now depend only on content, never on iteration order.
Re-run: `[PASS]` on all three self-test cases. Recorded because this bug class (an identifier or lookup
built from a positional/loop index instead of content) is easy to reintroduce in a future axis and is not
caught by determinism alone — only the reordering case catches it, which is exactly why R-F9.2's own
worked example (design.md's collector self-test, case b) insists on a discrimination-shaped direction, not
only a repetition-shaped one.

**Verification run, with real results:**
- `python3 -m py_compile rig/fixtures/failure-flood/v2/tools/generate-cases.py
  rig/fixtures/failure-flood/v2/tools/axis_table.py` → **exit 0**.
- `tools/generate-cases.py --self-test` → **exit 0**, all three cases PASS:
  (a) two independent in-process builds byte-identical; (b) every axis-table list reversed, still
  byte-identical (after the fix above); (c) one changed axis value (`max_decimals` +`[5]`) produces
  DIFFERENT output — the discrimination case, never trimmed to fit budget, per instruction.
- **Real, not just in-process, determinism**: ran `--out-dir` twice into two separate `mktemp -d`
  directories (outside `<repo>`) → `diff -rq` on both `cases/` trees: **identical**, zero differences.
- **Measured per-module counts (R-F9.2, never assumed)**: `applyKeypadInput` 15→**720** (48.0×),
  `confirmSeed` 12→**567** (47.2×), `parseTransfers` 9→**432** (48.0×), `formatTokenAmount` 8→**384**
  (48.0×), `isValidEthereumAddress` 8→**384** (48.0×), `balanceOfCall` 7→**336** (48.0×).
  **Aggregate: 2,823 generated cases / 6 causes = ~470:1** — inside the operator-confirmed ~433–500:1
  band, and inside the ~44–51× per-module multiplier band (47.2×–48.0× achieved, not the edges).
- **Full v2 Jest suite, real `npm ci` + `npx jest --runInBand`, in a fresh `mktemp -d` outside `<repo>`
  (ADR 0014 Clause A), run twice — once per env-var state:**
  - `FAILURE_FLOOD_CASE_DIR` unset: **6 suites, 59 passed + 7 skipped = 66 total, 0 failures** — the 7
    skipped entries are exactly the 7 `describe.skip` wrappers (6 modules + `balanceOfCall`'s second
    function); the 59 passed are byte-identical in count to PR3a-ii's own recorded clean baseline.
  - `FAILURE_FLOOD_CASE_DIR` pointing at a freshly generated `cases/` directory: **6 suites, 2,882
    passed, 0 failures** — exactly 59 + 2,823, proving every one of the 2,823 Python-computed expected
    values agrees with the real TypeScript module's real clean output.
- **R-F9.1 ("amplified cases MUST remain real failures of real logic") verified empirically, not
  asserted**: in a throwaway scratch copy (never the committed tree, never `rig/runs/`), widened
  `isValidEthereumAddress`'s regex from `{40}$` to `{39,41}$` — a real, meaningful defect — and re-ran
  that module's suite with the case table attached: **49 of 392 base+amplified cases genuinely failed**
  through the real TypeScript function, not zero and not all 392, which is exactly the signature of a
  real logic defect interacting with real varied inputs rather than a synthetic assertion.
- `./hooks/pre-commit --all` → **exit 0**, "redaction check: clean across 153 tracked files" (covers the
  three new/modified file groups above plus `tasks.md`'s done-note).
- Redaction, checked by hand: `axis_table.py`/`generate-cases.py` contain only synthetic tokens
  (`w00`..`w23`), the same test-file addresses PR3a-ii already committed and cleared, and formula-derived
  hex/integer values — no new donor name, absolute path, employer, person name, key, token, or hostname.

**Line budget, both authored components counted — no self-referential-diff exclusion (that PR2-era
convention was already corrected in this journal's own PR3a-ii section above, not re-invented here):**

| Component | Additions | Deletions | Total |
|---|---|---|---|
| Generator + axis table + test harness (`rig/fixtures/failure-flood/v2/tools/**`, `tests/_loadCases.ts`, 6 modified test files) | 685 | 0 | 685 |
| `tasks.md` task-3.3 done-note | 43 | 1 | 44 |
| **Subtotal, excluding this journal's own diff** | **728** | **1** | **729** |

**This journal's own diff is counted too, per explicit instruction for this batch — it is authored text,
not a generated golden, and `sdd-phase-common.md` §E excludes only generated goldens.** This section
(from `## PR3a-iii` to this table, plus the closing lines below) is itself part of the diff being
reported; its own insertion count cannot be known until the file is written, so it is measured after
writing and reported as a separate, final line rather than folded silently into the subtotal above.

**Ceiling is 700 for this work unit. The core code (685) alone is already within budget in isolation, but
the combined authored total — code plus the two journal/task-list updates required to record it —
exceeds 700.** The exact combined total, measured by `git diff --cached --numstat` after this file is
saved, is reported in the return envelope rather than estimated here, per instruction not to trim tests,
comments, or the discrimination case to make a number fit.

**Not committed or pushed** — staged only, per instruction; the commit remains the orchestrator's.

## PR3a-iv onward — not started

Tasks 3.4 (`answer-key/case-table.sha256`, inside the MANIFEST) and 3.5 (`MANIFEST.sha256` over
`src/`, `tests/`, `runtime/`, `tools/`, `answer-key/case-table.sha256`, for both v1 and v2), and PR4–PR6
in full, remain exactly as `tasks.md` describes them, all `[ ]`. 3.4 can now proceed against the real,
measured `cases/` bytes this batch produced (2,823 rows across 6 files); 3.5 still needs 3.4 first. Not
touched: `rig/derive.py`, `rig/run.sh`, `rig/collect.py`, `rig/fixtures/failure-flood/v1/`.

## PR3 (tasks 3.4–3.5) — DONE, closing PR3

Both remaining PR3 tasks completed. See `tasks.md`'s task 3.4/3.5 done-notes for the full per-task
record (digest value, path sets, both tamper proofs, the `__pycache__` hazard); this entry summarizes
files, exit codes, and line counts.

**Files changed:**
- `rig/fixtures/failure-flood/v2/tools/generate-cases.py` — modified. Added `case_table_digest(all_cases)`
  (computed from in-memory serialized bytes, same combining convention as `rig/run.sh`'s
  `hash_fixture_files`, `rig/run.sh:122-141`) and one `main()` print line. 26 insertions, 0 deletions.
  Generator still never writes into `<repo>` (ADR 0014 Clause A unchanged).
- `rig/fixtures/failure-flood/v2/answer-key/case-table.sha256` — new. One line, the hex digest
  `b15b8d1698ea0b45e2c475c1d5c68e2dcac81458522771d724a3ca431e5becb1`, captured from the generator's
  printed output and hand-committed (the generator itself never writes it).
- `rig/fixtures/failure-flood/v1/MANIFEST.sha256` — new. 10 lines: `runtime/` (4), `src/` (3),
  `tests/` (3). No `tools/`, no `answer-key/` — v1 has neither (R-F9.1).
- `rig/fixtures/failure-flood/v2/MANIFEST.sha256` — new. 20 lines: `answer-key/case-table.sha256` (1),
  `runtime/` (4), `src/` (6), `tests/` (7), `tools/` (2).
- `sdd/failure-flood-triage/tasks.md` — tasks 3.4/3.5 marked `[x]` with done-notes; one PR3 apply-time
  finding recorded (`design.md:584-585` claims v1 gets a generator, contradicting R-F9.1 and task 3.3's
  own already-recorded finding — not fixed here, flagged for the record).

**Manifest algorithm** (adapted from `rig/run.sh:154-171`'s `compute_manifest()`, which walks a fixed
subdirectory list — `src`, `prompts`, `answer-key` for `tool-surface` — skipping any that do not exist,
and joins sorted "sha256(bytes)  relpath" lines): walk `src/`, `tests/`, `runtime/`, `tools/` plus the
single file `answer-key/case-table.sha256` when present, explicitly skipping any path containing
`__pycache__` or ending `.pyc` (a hazard found on disk: `tools/__pycache__/*.pyc` exists from running
the generator, is `.gitignore`-excluded at `.gitignore:24-25`, and would otherwise enter a "directory
walk" the task explicitly forbids). Not committed as a standalone script this batch — PR5's
`run-pipeline.sh` (task 5.1) will need its own preflight recompute-compare and should reuse this exact
algorithm, recorded here and in `tasks.md` so it does not need re-deriving.

**Verification run, with real exit codes:**
- `python3 -m py_compile rig/fixtures/failure-flood/v2/tools/generate-cases.py` → exit 0.
- `python3 .../generate-cases.py --self-test` → exit 0, all 3 cases PASS (determinism, reordering,
  discrimination — unaffected by the digest addition).
- Two independent `--out-dir` generations (separate `mktemp` dirs) → identical digest
  `b15b8d1698ea0b45e2c475c1d5c68e2dcac81458522771d724a3ca431e5becb1`.
- **Tamper proof, direction 1 (generated bytes at the per-run install site)**: accept-before (fresh
  generation vs. committed digest) → exit **0**. One byte flipped in `cases/applyKeypadInput.json` →
  exit **2**. Run twice on two separate scratch `mktemp` dirs; real committed tree untouched.
- **Tamper proof, direction 2 (the committed expected digest itself)**: accept-before (scratch copy of
  `v2/`, MANIFEST recompute-compare vs. the real committed `MANIFEST.sha256`) → exit **0**. One hex
  character flipped in the scratch copy's `answer-key/case-table.sha256` → exit **2**. Scratch copy
  only; real committed file never touched.
- **`MANIFEST.sha256` accept-before / unstaged-tamper / revert, on the real committed tree**: for both
  v1 and v2 — accept-before → exit **0** for both. One byte flipped, unstaged, in a real tracked file
  (`v1/src/applyKeypadInput.ts`, `v2/src/balanceOfCall.ts`) → exit **2** for both. Reverted → exit 0
  again for both; `git status --porcelain` / `git diff --stat` on `v1/src`, `v2/src` empty throughout.
- `./hooks/pre-commit` → exit **0**. `./hooks/pre-commit --all` → exit **0**, "redaction check: clean
  across 156 tracked files". `./hooks/pre-commit --self-test` → exit **0**, all cases PASS.

**Line counts, each with the command that produced it:**

`git diff --cached --numstat` (after staging all five changed files):

```
10  0   rig/fixtures/failure-flood/v1/MANIFEST.sha256
20  0   rig/fixtures/failure-flood/v2/MANIFEST.sha256
1   0   rig/fixtures/failure-flood/v2/answer-key/case-table.sha256
26  0   rig/fixtures/failure-flood/v2/tools/generate-cases.py
73  2   sdd/failure-flood-triage/tasks.md
```

Raw total (all files, additions + deletions): 10+20+1+26+73+2 = **132**.

Generated-golden lines (the three `.sha256` digest files — computed output, not hand-authored; excluded
from the §E authored-risk count per `sdd-phase-common.md:104`, quoted: "Generated goldens are excluded
from authored risk count but remain included in complete snapshot identity and receipt validation"):
`MANIFEST.sha256` v1 (10) + `MANIFEST.sha256` v2 (20) + `case-table.sha256` (1) = **31**.

Authored total (raw minus goldens, i.e. `generate-cases.py` + `tasks.md`): 132 − 31 = **101**
(= 26 + 73 + 2, `generate-cases.py`'s 26 insertions plus `tasks.md`'s 73 insertions + 2 deletions).

Both figures (132 raw, 101 authored) are well inside the 700 ceiling — no split needed, no trimming was
required to fit.

**Not committed or pushed** — staged only, per instruction; the commit remains the orchestrator's.

**PR3 is now closed: tasks 3.1–3.5 all `[x]`.** PR4 (injections + measured answer-key, tasks 4.1–4.4)
is next; it depends on PR3's now-complete clean substrate + generator + manifest.

## PR4 (tasks 4.1–4.2 only, the pre-authorized 3b-i slice) — DONE

Tasks 4.1 and 4.2 only. **Not started**: task 4.3 (v2's 6 stage-2 injections) and task 4.4
(`answer-key/prereg.json`) — out of this slice's scope, `rig/fixtures/failure-flood/v2/**` confirmed
untouched (`git diff --stat -- rig/fixtures/failure-flood/v2` empty throughout).

### Design ambiguity, resolved before implementing — with quotes

Task 4.1's literal text ("Inject the 3 stage-1 root causes into v1's `src/`") appears to collide with
the already-frozen `MANIFEST.sha256` (task 3.5) and R-F1.3's "clean fixture MUST be proven zero-failure
before each injection." Resolved by reading, not guessing:

- `design.md:455`: **"MONOLITHIC's workspace is the injected `src/`, the tests, the runtime, the
  generated case tables, a `node_modules` symlink, `Bash`, and a write tool."** — the workspace an agent
  receives literally IS the injected `src/`; there is no descriptor-plus-materialised-copy layer.
- `design.md:584`: the file-changes row for `rig/fixtures/failure-flood/v1/{src,tests,runtime,prompts,
  answer-key}/**` names its own action as covering "injections + measured `F0`/`R0`/`S0` (3b)" — i.e.
  the injection IS a change to that path set, `src/` included, not a separate never-materialised layer.
- `design.md:413`'s never-materialised rule (`prompts/`, `answer-key/`, `tools/`) is stated as "the
  generator describes the injection structure and must not be visible to the agent" — this is about
  `answer-key/` (ground truth: `F0`/`R0`/`S0`) and, for v2, the generator/axis-table that would reveal
  amplification structure. It does **not** apply to `src/` itself, which the agent must see (diagnosing
  the bug IS the experiment). v1 has no generator at all (`R-F9.1`, task 3.3's done-note), so this rule
  reduces here to exactly the pre-existing "`answer-key/` is never inside cwd" case.
- `design.md` section 8 (line 368-369): **"Stage 1 ... is `task_id: s1` on `failure-flood/v1`. Stage 2
  ... injected into the same clean substrate and frozen separately."** — each fixture version is
  injected once and frozen; the "never edit an existing fixture version" rule the launch brief attributed
  to a "Decision 4" does not exist under that name — the closest textual match is the Open Questions line
  ("a different ratio is a new fixture version, never an edit" — about ratio changes creating v3, not
  about the 3a→3b progression within one version's own authoring). Flagged as a real inaccuracy in the
  launch brief, not silently worked around.

**Consequence for "clean, reproducible, not a one-time claim":** the committed `src/` becomes the
injected (buggy) state as its final artifact for this version; "clean" is preserved via git history (the
PR3a-i commit) plus a scratch backup taken before injecting, and was reproduced fresh **three times** —
once per injection, isolated, reverted after each — exactly what R-F1.3 requires structurally, not merely
asserted once.

### Task 4.1 — injections, each validated in isolation

**The three intended causes recorded at PR3a-i (`apply-progress.md:221-226` above) were re-verified
against the current source and confirmed still correct** — no cross-module imports found (already
verified at 3a-i), each module's boundary/index/direction logic unchanged since then:

1. `src/applyKeypadInput.ts:28` — boundary/off-by-one in the decimal-cap comparison:
   `current.length - dotIndex - 1 >= maxDecimals` → `... > maxDecimals` (relaxes the cap by one digit).
2. `src/confirmSeed.ts:15` — index/position-mapping defect in `isConfirmCorrect`:
   `isPickCorrect(seed, position, pick)` → `isPickCorrect(seed, index, pick)` (uses the loop's own index
   instead of `CONFIRM_POSITIONS`' actual position value; `CONFIRM_POSITIONS` itself is untouched).
3. `src/parseTransfers.ts:34` — direction/fee-association mapping defect: `account.toLowerCase()` →
   `account` (drops the case-insensitive compare that both `direction` and, downstream, `feeAmount`
   depend on).

**Isolation validation, one at a time, on a `mktemp` scratch copy outside `<repo>` (ADR 0014 Clause A),
reverted to a saved clean backup between each, real `npx jest --runInBand` + `rig/collect.py`:**

- Clean baseline (`C`): `npm ci` → 281 packages; `npx jest --runInBand` → 3 suites, **36 passed, 0
  failed**, exit 0. `rig/collect.py` → `suite_state=ran`, `failures=0`, `identifier_set_digest`
  = `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (sha256 of the empty string, as
  expected for zero failures).
- Injection 1 alone: **1 failure** — `applyKeypadInput.test.ts::...::ignores digits past the decimal
  cap`, signature `277580d674667852`. Reverted; re-ran clean → 36/36 again.
- Injection 2 alone: **1 failure** — `confirmSeed.test.ts::isConfirmCorrect::returns true when all picks
  match CONFIRM_POSITIONS`, signature `277580d674667852` (same signature as injection 1 — flagged
  immediately, not glossed over; explained under task 4.2 below). Reverted; re-ran clean → 36/36 again.
- Injection 3 alone: **2 failures** — `...maps an incoming transfer (to === account)` (signature
  `2df32737777805ca`) and `...matches the account address case-insensitively` (signature
  `277580d674667852`).

None of the three produced zero new failures, so **none was rejected** (R-F1.2 scenario does not fire
here — reported honestly rather than manufactured).

### Task 4.2 — `F0`/`S0`/`R0` frozen, measured

All 3 injections applied together, verified **twice independently**: once on the working scratch copy,
once more on a **fresh, separate `mktemp` copy of the real staged repo bytes** (`npm ci` there too) —
both gave byte-identical `collection/1` output (same `identifier_set_digest`
`64747c8b2eadfa8f3ca8d3780790aca84f842e3f989b8376333e9f9a569a1f4b`).

**Measured**: `suite_state=ran`, **4 failed / 32 passed / 36 total**, **2 distinct clusters** (`c1`
count 3, signature `277580d674667852`; `c2` count 1, signature `2df32737777805ca`). Committed to
`rig/fixtures/failure-flood/v1/answer-key/s1.json` (task_id `s1`, per `design.md:368`) — `C`, `F0`, `S0`,
`R0`, and a `measured_vs_declared` section recording this section's findings inside the frozen artifact
itself, not only in this journal. No `prompts/` directory exists yet, so the "committed before
`prompts/t*.txt` exists" ordering holds vacuously.

**R0** (per cause site, measured cluster_ids and the isolated test that proved it):

| cause_site | cluster_ids | isolated failing test |
|---|---|---|
| `src/applyKeypadInput.ts:28` | `c1` | "ignores digits past the decimal cap" |
| `src/confirmSeed.ts:15` | `c1` | "returns true when all picks match CONFIRM_POSITIONS" |
| `src/parseTransfers.ts:34` | `c1`, `c2` | "matches...case-insensitively" (`c1`), "maps an incoming transfer" (`c2`) |

**Masking, measured not declared (R-F1.1) — the headline finding of this slice.** All 3 causes stay
individually observable (none rejected at 4.1), but combined they collapse to **2 distinct cluster
signatures, not 3**: `applyKeypadInput`'s, `confirmSeed`'s, and one of `parseTransfers`'s failures all
normalize to the identical signature `277580d674667852` — Jest's generic
`expect(received).toBe(expected) // Object.is equality` head, with nothing distinguishing before
`rig/collect.py`'s `normalize_signature_text` cuts at the first `Expected:`/`Received:` line. This is a
**different** masking mode than R-F1.1's own worked scenario (one cause shadowing another inside the
*same* test): here, three unrelated causes in three different modules and three different tests share
one cluster. The diagnostician's bounded `clusters` view (design.md 9b) deliberately drops
`member_test_ids`, so cluster `c1` is presented as one representative test (`applyKeypadInput`'s) with
`count=3` — nothing in that bounded view signals that two other, unrelated causes also landed in it.
**Not adjusted to avoid this** — R-F1.1 explicitly forbids tuning injections away from a measured
collision — recorded instead, both here and inside `s1.json`'s own `measured_vs_declared.finding`. `R0`
still records each cause's real `cluster_ids` individually (table above), so grading against the exact
`<path>:<line>` site (never the cluster id alone, per design.md section 4's device) stays sound even
though the cluster signature itself cannot discriminate the three.

**Stage-1 target vs. measured, reported honestly rather than tuned.** R-F9.1: *"Stage 1 = 10 failing
cases / 3 root causes, shakedown."* **Measured: 4 failing cases, not 10.** This is not the masking above
reducing the count — every one of the 4 isolated failures survived into the combined run unchanged; the
gap is that isolation itself only ever produced 1 + 1 + 2 = 4, never more, for a structural reason
specific to each module's own test suite, not an implementation shortfall:
- `applyKeypadInput.test.ts` has exactly 2 tests that bracket the decimal-cap boundary ("ignores digits
  past the cap" and "appends the last allowed digit"); any single off-by-one on that comparison flips
  exactly one of the two, never both (they are complementary boundary tests by construction) — tried both
  `>=`→`>` and the equivalent `- 1`-dropping variant, same result each time.
- `confirmSeed.test.ts`'s `isConfirmCorrect` describe block has 4 tests, but 3 of them already return
  `false` for a reason unrelated to position mapping (a wrong word or a `null` pick at index 0), so
  `Array.prototype.every`'s short-circuit exits before the injected position bug is ever reached in those
  3 — only the "all correct" test can observe it, regardless of which index/position variant is chosen
  (tried an index-substitution and a `position ± 1` shift; both isolate to exactly 1 failure for the same
  short-circuit reason).
No alternative reading of either "e.g." example in the recorded intent was selected to inflate this count,
and none was rejected in favor of a weaker one either — `parseTransfers`'s case-insensitivity reading was
kept over "keying the fee `Map` on the wrong hash" specifically because it is the *richer* of the two
named examples (2 failures vs. a verified 1), not because 4 needed padding toward 10.

**MANIFEST recompute, deliberate, reason quoted.** Task 3.5's own done-note (`tasks.md:441`, this journal
above) already deferred `answer-key/` `F0`/`R0`/`S0` "to PR4" — recomputing now is that deferred step.
`rig/fixtures/failure-flood/v1/MANIFEST.sha256` recomputed over `runtime/`, `src/`, `tests/`,
`answer-key/` (still no `tools/` — none exists for v1): `src/` bytes changed (the 3 injections) and
`answer-key/s1.json` is new, so the pre-injection MANIFEST would mismatch on the very first
recompute-compare otherwise.

**Verification, real exit codes, on the real committed/staged tree:**
- Accept-before (fresh recompute vs. the just-written `MANIFEST.sha256`) → exit **0**.
- Tamper direction 1: one tracked byte appended to `src/applyKeypadInput.ts` → mismatch, exit **2** →
  restored from a saved copy → recompute matches again, exit **0**.
- Tamper direction 2: one hex character flipped in the committed `MANIFEST.sha256` itself → mismatch,
  exit **2** → restored from a saved copy → match again, exit **0**. `git diff --stat` on both paths
  empty after each restore.
- `rig/collect.py --self-test` → exit **0**, all 9 self-test cases PASS (unaffected by this slice; run
  as a precondition check before trusting the collector's own output above).
- `./hooks/pre-commit --all` → exit **0**, `"redaction check: clean across 157 tracked files"`.
  `./hooks/pre-commit` (staged only) → exit **0**. `./hooks/pre-commit --self-test` → exit **0**, all 3
  cases PASS.
- Manual redaction grep (`rg -n -i "eduardo|graciano|callstack|/Users/"` and the donor-identifier check)
  over the new/changed files → no matches.

**Process note, recorded rather than hidden.** Mid-verification, `git checkout --
src/applyKeypadInput.ts` was run before that one file had been `git add`-ed, which reverted it to the
pre-injection *committed* state instead of the intended injected state — a real mistake, not a simulated
one. Caught immediately by `git status`/`git diff` (the file showed no staged change when it should
have), the injection was re-copied from the still-intact scratch working copy, `git add` run immediately
afterward on the whole `v1/` fixture so the index always holds the intended bytes before any further
`git`-history-touching command, and the MANIFEST recompute-compare re-verified match (exit 0) afterward.
No corruption reached the reported `F0`/`S0`/`R0` above: those were measured from an independent,
already-saved `mktemp` verification copy of the repo's staged bytes taken *before* this mistake occurred,
and re-confirmed identical to the working-scratch measurement after the recovery.

**Line counts, each with the command that produced it:**

`git diff --cached --numstat` (fixture files only, before the journal/tasks edit):

```
4    3    rig/fixtures/failure-flood/v1/MANIFEST.sha256
127  0    rig/fixtures/failure-flood/v1/answer-key/s1.json
1    1    rig/fixtures/failure-flood/v1/src/applyKeypadInput.ts
1    1    rig/fixtures/failure-flood/v1/src/confirmSeed.ts
1    1    rig/fixtures/failure-flood/v1/src/parseTransfers.ts
```

Fixture raw total: 4+3+127+0+1+1+1+1+1+1 = **140**. All of it is authored/measured content — `s1.json`
is a hand-assembled ground-truth artifact from real collector output, not machine-generated boilerplate,
and the `MANIFEST.sha256`/`src/*.ts` lines are one-line hash entries and single-line logic edits — no
generated-golden exclusion applies here (unlike PR3a-iii/PR3's `case-table.sha256`/lockfile cases).
The journal (`apply-progress.md`, this section) and `tasks.md`'s 4.1/4.2 done-notes add further insertions
on top of the 140 above; both are counted in full as authored text per the same rule this cycle has
applied throughout — the exact combined number is stated by the orchestrator's own `git diff --cached
--numstat` at staging time, since this section is still being written as that command would run. 140 is
the fixture-only floor, already well inside the 700-line ceiling with substantial headroom for the
journal/tasks text.

**Not committed or pushed** — staged only, per instruction; the commit remains the orchestrator's.

**PR4's 3b-i slice (tasks 4.1–4.2) is now closed.** Task 4.3 (v2's 6 stage-2 injections) and task 4.4
(`answer-key/prereg.json`) remain `[ ]`, explicitly out of this slice's authorization.

## PR4-signature-scope-fix — corrective work unit (this batch) — DONE

Corrective, not one of the enumerated 4.1–4.4 tasks: PR4-i's own measurement (`answer-key/s1.json`, task
4.2, above) found the signature normalizer collapsing 3 unrelated causes in 3 different modules into one
cluster, because Jest's generic `.toBe()` equality head carries nothing before the Expected:/Received:
cut and the signature was `hash(head)` alone. This closes that defect, re-measures v1's ground truth
under the corrected normalizer, and amends the artifacts that stated the old rule. Task 4.2 stays marked
`[x]` (its own work — 3 injections, isolation validation, the masking-measured-not-tuned discipline — was
correct); this section is layered on top, with an addendum in `tasks.md` under 4.2 rather than a new
checkbox, since the corrective work unit was not itself one of the seven approved work units.

### What was over-split vs. what was over-collapsed — kept distinct, not conflated

Two failure modes are visible in one fixture, and only one needed a fix:

- **Over-split** (one cause, several signatures) — `parseTransfers.ts:34` already showed this
  (`toBe`-head failure vs. `toMatchObject`-head failure, 2 signatures for 1 cause). **Not touched.**
  `design.md:449-450` (pre-fix line numbers) already states: *"where a cause genuinely produces several
  heads (a throw carrying a parameter value), slice 3b **measures** that count and `R0` records the
  many-to-one mapping. The key absorbs it; the algorithm does not change."* `design.md:286`: *"`R0` is a
  **many-to-one cluster → cause-site mapping**, measured in slice 3b rather than asserted."* Both quotes
  verified against the file before any edit. No algorithm change was made for this mode.
- **Over-collapse** (several causes, one signature) — 3 unrelated causes (`applyKeypadInput.ts:28`,
  `confirmSeed.ts:15`, `parseTransfers.ts:34`'s case-insensitivity failure) sharing cluster
  `277580d674667852` under `normalizer_version: 1`. **This is what was fixed.** Nothing in the spec or
  design defended against it — R-F1.1's own masking scenario is about one cause shadowing another
  *inside the same test*, not three unrelated causes in three different tests.

### The fix (`rig/collect.py`)

1. **Signature is now `hash(normalized_head + test_file)`**, not `hash(normalized_head)` alone.
   `signature_of(signature_text, test_file)` takes both arguments — there is no longer a call site that
   can omit the file. `relative_test_file()` extracted as a shared helper so the signature's file scope
   and `test_id`'s own file component can never drift into two different relative-path conventions.
   `␞` (Symbol for Record Separator, never a printable/whitespace byte) joins the two inputs before
   hashing, so no normalized head text could ever collide with a path to fake a match.
2. **`NORMALIZER_VERSION` bumped 1 -> 2**, with an inline comment stating why: a `collection/1` stamped
   `1` (e.g. the pre-fix `answer-key/s1.json`) MUST NOT be silently compared against one stamped `2` — the
   cluster key itself changed.
3. **The clusters view carries `distinct_test_files` per cluster** — a sorted, deduplicated list of the
   test files among that cluster's members, derived from existing `test_id` data (no new field on
   `failure/1`). It does **not** carry `member_test_ids`: `_self_test_clusters_view_bounded` (case f,
   updated) asserts both — `distinct_test_files` present, `member_test_ids` absent — so the view stays
   bounded by cluster count (a cluster's distinct-file set is at most the fixture's own module count),
   never by failure count.
4. **Same-module clustering re-verified, not assumed to survive.** Two new self-test cases (g.1/g.2, the
   same both-directions discipline task 3.3's own done-note names for the generator's order-dependence
   bug — "either alone leaves a hole"): (g.1) an identical head in the SAME test file still produces the
   SAME signature; (g.2) an identical head in DIFFERENT test files now produces DIFFERENT signatures.
   `python3 rig/collect.py --self-test` → **exit 0, all 11 cases PASS** (the original a–f plus new g.1/g.2,
   `c` itself covering 4 sub-cases):

   ```
   [PASS] (a) same cause, differing path/line/col/Expected-Received -> same signature
   [PASS] (b) two genuinely different causes -> different signatures ...
   [PASS] (c.1)/(c.2)/(c.3)/(c.4) the three suite states + suite-timeout sub-case
   [PASS] (d) same input twice -> byte-identical output
   [PASS] (e) absent toolchain -> CollectorError('toolchain-absent'), not a suite state
   [PASS] (f) clusters view carries distinct_test_files but no member_test_ids, one row per cluster
   [PASS] (g.1) identical head, SAME test file -> SAME signature
   [PASS] (g.2) identical head, DIFFERENT test files -> DIFFERENT signatures
   self-test: all cases passed
   ```
5. **Scope limit, stated in the code, not only here.** `rig/collect.py`'s module docstring and
   `signature_of`'s own docstring now say explicitly: this fix is measured-safe against introducing a new
   over-split failure only because this fixture's six host modules are import-free by construction (the
   independence check already run at PR3a-i/ii — no `src/*.ts` or `tests/*.test.ts` file in `v1` or `v2`
   imports another module or another test). A future fixture whose modules import each other could let
   one real cause legitimately span two test files, which this rule would then over-split; `R0`'s
   many-to-one mapping (unchanged) is what would absorb that, not a reason to loosen this fix.

### Re-measurement — v1's ground truth, per ADR 0014 Clause A (mktemp outside `<repo>`)

Committed `src/`/`tests`/`runtime` bytes (unchanged by this fix) copied to a fresh `mktemp` scratch
directory outside `<repo>`; `npm ci`; `npx jest --config jest.config.js --runInBand --json
--outputFile=report.json`:

```
Test Suites: 3 failed, 3 total
Tests:       4 failed, 32 passed, 36 total
```

Identical totals to the pre-fix measurement (expected — no `src/` byte changed). `rig/collect.py` against
that real report:

```
collect.py: suite_state=ran failures=4 clusters=4 report_bytes=28261
```

**Measured exactly as run, not tuned toward any count**: **4 failing cases (unchanged) across 4 distinct
clusters (was 2)** — one cluster per failure in this fixture, not per cause:

| cluster_id | signature | test file | representative test |
|---|---|---|---|
| c1 | `04933d1bde59e977` | `parseTransfers.test.ts` | "matches the account address case-insensitively" |
| c2 | `607220f5cf3e52b9` | `applyKeypadInput.test.ts` | "ignores digits past the decimal cap" |
| c3 | `65a9e5f9e5eef040` | `confirmSeed.test.ts` | "returns true when all picks match CONFIRM_POSITIONS" |
| c4 | `da54112bb72162e0` | `parseTransfers.test.ts` | "maps an incoming transfer (to === account)" |

Ran a second, independent collector pass over the same report file: byte-identical `collection/1`
(`diff` empty, exit 0) — idempotence held on the real measurement, not only in the self-test.

**Isolation re-verified per cause**, on a clean-reverted copy of the same three files (each injection
applied alone, others reverted to their pre-injection text), `npm ci` + real `npx jest` + `rig/collect.py`
per isolation:

| cause_site | isolated failures | isolated signature(s) | matches combined run? |
|---|---|---|---|
| `applyKeypadInput.ts:28` | 1 | `607220f5cf3e52b9` | yes, byte-identical |
| `confirmSeed.ts:15` | 1 | `65a9e5f9e5eef040` | yes, byte-identical |
| `parseTransfers.ts:34` | 2 | `04933d1bde59e977`, `da54112bb72162e0` | yes, byte-identical, both |

None produced zero new failures (R-F1.2 does not fire). Clean baseline re-confirmed zero-failure before
each isolation (`3 suites, 36 passed, 0 failed`).

`rig/fixtures/failure-flood/v1/answer-key/s1.json` rewritten: `normalizer_version: 2`; `F0`'s 4 failures
keep their `test_id`s and gain their new signatures; `F0.clusters` now lists 4 clusters (c1–c4) each with
`distinct_test_files`; `R0` unchanged in shape (`applyKeypadInput.ts:28` -> `["c2"]`, `confirmSeed.ts:15`
-> `["c3"]`, `parseTransfers.ts:34` -> `["c1", "c4"]` — the over-split mapping, still absorbed, still
recorded per-cause); `measured_vs_declared` rewritten: `clusters_present_in_F0` 2 -> 4,
`total_failing_cases_measured` unchanged at 4 (still short of R-F9.1's stated 10 — that gap is
unchanged and explicitly not this unit's to close, see below), plus a new `superseded_note` explaining
why this is a replacement, not a revision, of the version-1 measurement. `C` and `S0` are unchanged
(`identifier_set_digest`, `suite_state`, `totals` do not depend on the signature).

**Stage 1's 4-vs-10 gap, left exactly as it was found.** R-F9.1 states the stage-1 target as 10 failing
cases / 3 root causes; the measured total is 4, unchanged by this fix (structural — each module's own
test suite limits observable isolated failures, recorded at PR4-i above). This corrective unit's scope
was the signature rule, not the injection count; the gap is recorded here again rather than silently
closed or silently left unremarked.

### `MANIFEST.sha256` recompute

Recomputed over `runtime/`, `src/`, `tests/`, `answer-key/` for v1 (same algorithm as PR3.5/PR4-i:
sorted `sha256(bytes)  relpath` lines, skipping `__pycache__`/`.pyc`, no directory walk). `git diff --
rig/fixtures/failure-flood/v1/MANIFEST.sha256` shows exactly **one** line changed —
`answer-key/s1.json`'s hash — confirming `src/`, `tests/`, `runtime/` are byte-identical to before this
unit (`git diff --stat` on those three paths: empty).

### Artifacts amended to state the corrected rule, not only the fix

- `sdd/failure-flood-triage/spec.md` — new **R-F1.4**, added after R-F1.3's scenarios: signature MUST
  fold in the test file; two scenarios (distinct modules must not collapse; one module must still
  cluster); an explicit scope-limit paragraph.
- `sdd/failure-flood-triage/design.md` — algorithm item 4b (new, keeps item 4's original text unedited);
  a full correction paragraph inside section 9c, placed directly after the ORIGINAL over-split reasoning
  (kept verbatim, not deleted) rather than replacing it — both ends of the finding stay visible, per
  instruction; the self-test case table gains row `g`; the `cluster/1`/`collection/1` JSON schema
  examples updated (`distinct_test_files` added, `normalizer_version` example bumped to 2 with a note).
- `sdd/failure-flood-triage/tasks.md` — an addendum under task 4.2's existing done-note (task stays
  `[x]`, the addendum itself checked off) rather than a new task number, since this corrective unit was
  authorized as a fix to already-approved work, not as an eighth work unit.

### Verification, real exit codes

- `python3 -m py_compile rig/collect.py` → exit **0**.
- `python3 rig/collect.py --self-test` → exit **0**, all 11 cases PASS (listed above).
- `./hooks/pre-commit --all` → exit **0**, `"redaction check: clean across 157 tracked files"`.
- `./hooks/pre-commit` (staged only) → exit **0**.
- `./hooks/pre-commit --self-test` → exit **0**, all 3 cases PASS.
- `git diff --cached --stat -- rig/fixtures/failure-flood/v2` → empty, exit 0 (nothing staged for v2).
- `git diff --stat -- rig/fixtures/failure-flood/v2` → empty, exit 0 (nothing unstaged for v2 either).

### Line counts, each with the command that produced it

`git diff --cached --numstat` (all six files staged this unit):

```
144  19   rig/collect.py
1    1    rig/fixtures/failure-flood/v1/MANIFEST.sha256
50   19   rig/fixtures/failure-flood/v1/answer-key/s1.json
47   4    sdd/failure-flood-triage/design.md
35   0    sdd/failure-flood-triage/spec.md
19   0    sdd/failure-flood-triage/tasks.md
```

Raw total (additions + deletions, every file): 144+19+1+1+50+19+47+4+35+0+19+0 = **339**.

Generated-golden exclusion (`sdd-phase-common.md:104`, quoted: "Generated goldens are excluded from
authored risk count but remain included in complete snapshot identity and receipt validation"):
`MANIFEST.sha256`'s 2 lines (1+1) are the same computed-hash-file class already excluded in PR3/PR4-i.
`answer-key/s1.json` is NOT excluded — same reasoning PR4-i already recorded for it: it is a
hand-assembled ground-truth artifact built from real measured collector output, not machine-generated
boilerplate.

Authored total = raw − MANIFEST exclusion = 339 − 2 = **337** (= 144+19 [collect.py] + 50+19 [s1.json] +
47+4 [design.md] + 35+0 [spec.md] + 19+0 [tasks.md] = 163+69+51+35+19 = 337). Both 339 (raw) and 337
(authored) are well inside the 700-line ceiling; no split was needed.

### apply-progress-journal's own addendum this batch

This section itself adds further insertions on top of the 339/337 above, per the same convention this
cycle has applied throughout (the journal is counted, but is not fixture/rule content) — the combined
number is whatever the orchestrator's own `git diff --cached --numstat` reports at staging time, since
this section is still being written as that command would run.

**Not committed or pushed** — staged only, per instruction; the commit remains the orchestrator's.

**This corrective work unit is now closed.** Task 4.3 (v2's 6 stage-2 injections, under the now-corrected
normalizer) and task 4.4 (`answer-key/prereg.json`) remain `[ ]`, unaffected by and not attempted in this
unit.

## PR4-task-4.3 — v2's six injections and the measured stage-2 ground truth — DONE

**What.** Injected six root causes into the COMMITTED `rig/fixtures/failure-flood/v2/src/`: three reused
from v1 at the same sites (`applyKeypadInput.ts:28`, `confirmSeed.ts:15`, `parseTransfers.ts:34`), three
designed now (`formatTokenAmount.ts:23`, `isValidEthereumAddress.ts:1`, `balanceOfCall.ts:3`). Each
validated in isolation (R-F1.2/R-F1.3) both without and with generated cases loaded. Measured `F0`/`S0`/`R0`
under `normalizer_version: 3` with generated cases loaded, wrote `rig/fixtures/failure-flood/v2/answer-key/s2.json`,
recomputed `v2/MANIFEST.sha256`. Two real normalizer defects were found by this measurement and fixed in
`rig/collect.py`, which required re-measuring and rewriting the already-committed `v1/answer-key/s1.json`
and recomputing `v1/MANIFEST.sha256` in the same work unit rather than leaving it stale.

**Why.** Task 4.3's own instruction, plus R-F1.1/R-F1.2/R-F1.3/R-F9.2: ground truth must be measured
against the real committed, injected fixture, never assumed from the declared injection list or a
pre-registered target ratio.

**The six causes and sites, each with its isolation result** (`rig/collect.py --cwd <runtime> --report-file
… --collection-output … --clusters-output … --expected-suites 6`, `FAILURE_FLOOD_CASE_DIR=<cases-dir>` for
the with-cases condition):

| # | Site | Cause | No-cases failures | With-cases failures | With-cases clusters |
|---|------|-------|---:|---:|---:|
| 1 | `src/applyKeypadInput.ts:28` | `>=` relaxed to `>` in the decimal-cap comparison (reused from v1) | 1 | 41 | 1 |
| 2 | `src/confirmSeed.ts:15` | `isPickCorrect(seed, position, pick)` → `isPickCorrect(seed, index, pick)` (reused) | 1 | 22 | 1 |
| 3 | `src/parseTransfers.ts:34` | dropped `.toLowerCase()` on `account` (reused) | 2 | 146 | 3 |
| 4 | `src/formatTokenAmount.ts:23` | `Math.max(decimals - 2, 0)` → `Math.max(decimals - 1, 0)` (new) | 2 | 45 | 1 |
| 5 | `src/isValidEthereumAddress.ts:1` | `{40}` → `{41}` in the address-length regex (new) | 3 | 99 | 1 |
| 6 | `src/balanceOfCall.ts:3` | `ADDRESS_PADDING = 64` → `63` (new) | 2 | 146 | 2 |
| **sum** | | | **11** | **499** | **9 (combined)** |

None produced zero new failures (R-F1.2: none rejected). Isolated sums (11, 499) are **exactly** equal to
the combined-run totals in both conditions, and every isolated cluster's signature and count are
byte-identical to its counterpart inside the combined run — re-verified, not assumed. This fixture's six
modules are import-free by construction (task 3.2's own independence check, unchanged), so no cross-module
masking was structurally possible. `parseTransfers.ts:34`'s cluster_ids `[c2, c7, c8]` is a within-module
over-split for one cause (three heads: the amplified `.toEqual`, and the two base tests' `.toBe`/
`.toMatchObject`), absorbed by `R0`'s many-to-one mapping per `design.md:449-450` — unchanged in kind from
v1's own over-split, just three heads instead of two.

**The two failing counts, the derived yield, and the achieved ratio — measured, not reached.**
59-test base (no generated case tables, `FAILURE_FLOOD_CASE_DIR` unset): **11 failing / 66 total tests**
(59 real + 7 skipped `describe.skip` blocks), 8 clusters. Full amplified corpus (2,823 generated cases +
59 base = 2,882 tests, `FAILURE_FLOOD_CASE_DIR` set to a fresh `tools/generate-cases.py --out-dir` output —
digest `b15b8d1698ea0b45e2c475c1d5c68e2dcac81458522771d724a3ca431e5becb1`, matching the committed
`answer-key/case-table.sha256`): **499 failing / 2,882 total tests**, 9 clusters. Yield = 499 / 2882 =
**17.3144%**. Achieved ratio = **499:6 (~83.17:1 per cause)** — NOT spec.md Decision B / task 3.3's
~433–500:1 order of magnitude, and also not the ~57:1 the corrective-unit's own correction-note estimated.
Per-module yield spread is real and reported, not smoothed: `applyKeypadInput` 41/720 (5.7%), `confirmSeed`
22/567 (3.9%), `parseTransfers` 146/432 (33.8%), `formatTokenAmount` 45/384 (11.7%),
`isValidEthereumAddress` 99/384 (25.8%), `balanceOfCall` 146/336 (43.5%) — `balanceOfCall`'s
`ADDRESS_PADDING` off-by-one breaks essentially every `encodeBalanceOf` call regardless of input, while
`applyKeypadInput`/`confirmSeed`'s boundary defects only break narrow input slices for the same structural
reason task 4.2 already recorded for v1 (most cases don't reach the exact boundary the injected comparison
moved). No injection or axis-table value was adjusted toward either estimate (R-F9.2, R-F1.1).

**Two real normalizer defects found by this measurement and fixed in `rig/collect.py`, both anticipated
by `tasks.md:602`'s own instruction and `design.md:711`'s threat matrix — quoted, not paraphrased.**
`tasks.md:602`: "a cause whose cluster count grows with `case_count` is a normalizer defect, not a key
entry, and must be fixed in PR2 before this freezes, not absorbed into `R0`." `design.md:711`: "Slice 3b
measures clusters-per-injection on the amplified fixture and freezes it in `R0`. A cause whose cluster
count grows with `case_count` is a normalizer defect, not a key entry."

1. **The Expected:/Received: cut only matched Jest's unprefixed scalar summary line** (`Expected: 5`),
   never its diff-prefixed structural form (`- Expected  - N` / `+ Received  + N`, used by
   `.toEqual()`/`.toMatchObject()`). Measured on `parseTransfers` isolated with cases loaded: **146 failing
   cases → 146 distinct clusters** (cluster count growing 1:1 with `case_count`) before the fix, **3**
   after. Fixed by widening `_EXPECTED_RECEIVED_RE` to `r"^\s*[-+]?\s*(Expected|Received)\b.*$"`.
   `NORMALIZER_VERSION` 2 → 3. Self-test case (h), both directions (h.1: differing diff-prefixed bodies,
   same matcher header → same signature; h.2: genuinely different matcher header → different signature).
2. **`workspace_root = os.path.abspath(cwd)` does not resolve symlinks**, so a scratch workspace under a
   symlinked path (macOS's `/tmp` → `/private/tmp`) leaked an absolute host path into
   `test_id`/`distinct_test_files`/`signature` — measured live: `distinct_test_files` read
   `../../../../private/tmp/<host-scratch-path>/tests/balanceOfCall.test.ts` instead of
   `../tests/balanceOfCall.test.ts`. This is a real violation of R-F1.3's own "deterministic across runs
   (paths, ...)" requirement and of `build_test_id`'s own docstring promise ("relative kills the random
   mktemp workspace path"). Fixed: `workspace_root = os.path.realpath(cwd)`. No `NORMALIZER_VERSION` bump
   (path-resolution robustness, not an algorithm change — does not invalidate any prior byte-value
   comparison taken on a non-symlinked path). Self-test case (i), both directions, using a real
   `tempfile`/`os.symlink` scenario (a synthetic string fixture cannot exercise symlink resolution): the
   fix produces the clean relative path, and the old `abspath` behaviour is shown to differ, not merely
   assumed to.

**v1's `answer-key/s1.json` re-measured and rewritten under the version-3 fix in this same work unit**,
rather than left silently stale — `NORMALIZER_VERSION` 2 declared in a committed answer key that no
longer matches what `rig/collect.py` produces would itself be the "measured, not assumed" violation this
whole task exists to prevent. Re-measured on the real committed (unchanged) `v1/src`+`tests`+`runtime`:
same 4 failures, same `identifier_set_digest` (`64747c8b2eadfa8f3ca8d3780790aca84f842e3f989b8376333e9f9a569a1f4b`),
same cluster count (4) and same cluster-id assignment (c1–c4 unchanged — the new c4 signature still sorts
last ascending). Only `c4`'s signature VALUE changed (`da54112bb72162e0` → `7f2043443e4b144b`, the
`.toMatchObject` failure) and its `signature_text` shrank from the full multi-line diff dump to the bare
matcher head `"Error: expect(received).toMatchObject(expected)"` — which is, cross-checked, byte-identical
to v2's own `c8` (same cause, same site, same file, same fix). The version-1→2 supersession note
(PR4-signature-scope-fix) was kept verbatim below the new version-2→3 note, not overwritten — drift is the
useful part of the record. `v1/MANIFEST.sha256` recomputed (only the `answer-key/s1.json` line changed);
accept-before and tamper-proof both directions confirmed (exit 0 / exit 2, reverted immediately);
`v1/src`, `v1/tests`, `v1/runtime` confirmed byte-unchanged throughout (`git diff --stat` empty, both
staged and unstaged).

**The `F0` shape question, resolved with quotes — two rejected attempts recorded, not hidden.**
`design.md:241` calls `failure/1` "deliberately minimal. At amplified scale there are thousands of these,
so signature_text lives once per cluster and never once per failure" — licensing (even anticipating) a
per-failure list. **Attempt 1**: wrote all 499 per-failure `{test_id, status, signature}` records
literally, one compact line each — 1,309 lines for `s2.json` alone, pushing the whole work unit's authored
total to ~1,499 against the 700-line ceiling. Rejected as unreviewable. **Attempt 2**: switched to
`collection/1`'s own `clusters` field instead — but that field (`collect.py`'s `public_clusters`
projection) itself carries `member_test_ids` per cluster, and two of the nine clusters here have 145 and
144 members: still 815 lines, over budget for a reason that had nothing to do with `case_count`. It was
the wrong artifact, not a smaller version of the right one. **Final**: `design.md` 9b already names a
SEPARATE, already-bounded artifact for exactly this — `clusters_view()`'s `clusters/1` schema: "a bounded
clusters view... clusters, counts, one representative each... bounded by CLUSTER count, never by failure
count." `F0.clusters` in `s2.json` is that view (9 entries, no `member_test_ids`) — the same artifact the
diagnostician itself receives, and the same one PR4-signature-scope-fix already used for the bounded view.
`design.md:711`'s own amplification-safety freeze is explicitly "clusters-per-injection... in `R0`", not a
failure enumeration, and scoring itself is cluster-level (design.md section 4: "`causes_present` counts
distinct sites in `R0`; `clusters_present` counts the signatures they map to"). `S0.identifier_set_digest`
remains the integrity proof for the exact 499-test_id failing SET without `F0` needing to enumerate it.
Final `s2.json`: **298 lines**.

**Line counts, both stated with their command.** `git diff --cached --numstat`: `rig/collect.py` 153+9,
`v1/MANIFEST.sha256` 1+1, `v1/answer-key/s1.json` 8+8, `v2/MANIFEST.sha256` 7+6,
`v2/answer-key/s2.json` 298+0, six `v2/src/*.ts` files 1+1 each (×6 = 12). Raw total =
162+2+16+13+298+12 = **503**. Generated-golden exclusion (`sdd-phase-common.md:104`, same class as every
prior PR in this stack): both `MANIFEST.sha256` files only, 2+13 = **15** — `s1.json`/`s2.json` are NOT
excluded (hand-assembled from real measured output, not machine boilerplate, same reasoning PR4-i and
PR4-signature-scope-fix already recorded). Authored total = 503 − 15 = **488**, inside the 700 ceiling.

**Verification, real exit codes.** `python3 -m py_compile rig/collect.py` exit 0. `rig/collect.py
--self-test` exit 0, all 15 cases PASS (a, b, c.1–c.4, d, e, f, g.1, g.2, h.1, h.2, i). `./hooks/pre-commit`
(staged) exit 0. `./hooks/pre-commit --all` exit 0 ("redaction check: clean across 158 tracked files").
`./hooks/pre-commit --self-test` exit 0 (unaffected, re-run for completeness). MANIFEST accept-before and
tamper-proof both directions, both v1 and v2: exit 0 / exit 2 / exit 0 (reverted), each verified against
the real committed tree, `git diff --stat` empty on `v1/src`/`v1/tests`/`v1/runtime` and on
`v2/src`/`v2/tests`/`v2/runtime` (`v2/src` shown via `git diff --cached --stat`, since the six injections
are staged, not left unstaged) throughout. Redaction: no absolute host path, donor name, employer, or
person name in any committed byte — the two scratch-path mentions inside `s2.json`'s own prose describe
the general macOS `/tmp`→`/private/tmp` symlink behavior generically or use an explicit `<host-scratch-path>`
placeholder, confirmed by `rg` for the actual scratch directory name (no match).

**Redaction/ADR 0014 process.** All measurement ran in `mktemp` scratch directories outside `<repo>` (ADR
0014 Clause A); no `node_modules` anywhere under `<repo>` (confirmed after cleanup). `rig/fixtures/failure-flood/v1/**`
was NOT edited beyond the two files this work unit's coordinator explicitly authorized
(`answer-key/s1.json`, `MANIFEST.sha256`) — `v1/src`, `v1/tests`, `v1/runtime` remain byte-unchanged,
proven above. Per PR4-i's own lesson (a `git checkout --` mistake that reverted an injection before
staging), every injection edit to committed `v2/src/` bytes was `git add`-ed immediately, before any
further git command.

**Not committed or pushed** — staged only, per instruction.

**Task 4.4 (`answer-key/prereg.json`) remains `[ ]`, out of this work unit's scope** — the coordinator's
brief was explicit that this batch is task 4.3 only.

## Task 4.4 — `answer-key/prereg.json` (Hard Ordering Gate, layer 1) — this batch, closes PR4

`sdd-apply` completed task 4.4 for `failure-flood-triage`: committed (staged)
`rig/fixtures/failure-flood/v2/answer-key/prereg.json`, recomputed `v2/MANIFEST.sha256` to cover it, and
marked task 4.4 `[x]` in `tasks.md` with a full addendum (scope decision, file shape, tamper verification,
line counts). Nothing committed or pushed. This closes PR4 (tasks 4.1–4.4 all `[x]`).

**Scope decision — v2 only, not v1, resolved with quotes:** design.md section 8 — "Stage 2 (50 cases, 6
causes, the comparison) is `task_id: s2` on `failure-flood/v2`" — is the only run type the Hard Ordering
Gate's layer 2 non-shakedown check ever gates. R-F9.1 ("Stage 1 = 10 failing cases / 3 root causes,
shakedown, excluded from the stage-2 test") plus task 5.7 ("Run the actual `--shakedown` shakedown on the
now-clean, now-committed tree") establish `task_id: s1` (v1) as structurally always invoked with
`--shakedown`. The Hard Ordering Gate's own wording (tasks.md) makes the non-applicability explicit:
layer 2 "separately refuses (`exit 2`) any **non**-shakedown invocation unless `hypotheses/0002-*.md` and
`hypotheses/0003-*.md` exist... (frozen list in `answer-key/prereg.json`, inside the MANIFEST)" — the
non-shakedown branch never executes against v1's fixture root, so placing the file there too would be
dead weight with zero functional purpose. Task 3.5's earlier parenthetical listing `prereg.json` alongside
`answer-key/` F0/R0/S0 as landing "in PR4... for both v1 and v2" was read closely: that clause modifies
what is *excluded from PR3's manifest* for both fixtures (i.e., neither fixture's PR3 manifest covered
these paths), not a claim every named path duplicates onto both fixtures at PR4 — `F0`/`R0`/`S0` already
landed as `s1.json` (v1 only) and `s2.json` (v2 only), never duplicated, and `prereg.json` follows the
same per-fixture-as-needed pattern.

**`prereg.json`'s shape, designed and justified** (36 lines, `rig/fixtures/failure-flood/v2/answer-key/`):
`schema: "prereg/1"`; a `scope` block recording the v1/v2 decision above inline (so a later reader/PR5
author does not re-derive it from this journal); `required_hypotheses` — one `{id, path_root, path_glob,
topic_hint}` entry per hypothesis (`0002`, `0003`) — using the **glob** form (`hypotheses/0002-*.md`,
`hypotheses/0003-*.md`) copied verbatim from the Hard Ordering Gate's own wording and R-F8.1's citation,
deliberately NOT the exact literal filenames PR6 (tasks 6.1/6.2) already commits to (`topic_hint` carries
those as non-binding documentation only). Reasoning: hardcoding the literal final filename would force
re-touching this already-manifest-frozen file if PR6 ever refines its topic slug; the glob freezes the
*count and numeric-prefix requirement*, which is what design.md section 7's table row ("the list of
required hypothesis files cannot be quietly shortened") actually protects. A `check` block spells out the
exact preflight semantics PR5 must implement without re-deriving them from prose: `must_exist`,
`must_match_exactly_one_file_per_entry`, `must_be_git_tracked`, `must_be_clean`, each with its own named
`exit 2` reason (`zero_matches`, `more_than_one_match`, `tracked_but_dirty`, `untracked`).

**Layer 1 demonstrated as refusing TODAY, without executing PR5's not-yet-written preflight**: `git
ls-files hypotheses/` on the real repository lists only `hypotheses/README.md` and
`hypotheses/0001-broad-surface-degrades-output-not-selection.md` — no file matching `hypotheses/0002-*.md`
or `hypotheses/0003-*.md` exists yet, tracked or otherwise. A correct preflight implementing `prereg.json`'s
`check` block against this real tree would evaluate `required_hypotheses[0]`'s glob to **zero matches**
and, per the file's own `zero_matches: "exit 2"` rule, refuse before any run directory is claimed — the
structurally-impossible-until-PR6 state the Hard Ordering Gate exists to produce. Stated as what a correct
implementation returns and why, never claimed as executed — `run-pipeline.sh` (PR5) does not exist yet.

**MANIFEST verification, real exit codes, both fixtures, both tamper directions**, using the unchanged
recompute algorithm task 3.5 established (`rig/run.sh:154-171`'s adapted `compute_manifest()`, walking
`src/, tests/, runtime/, tools/, answer-key/`, skipping `__pycache__`/`.pyc`):
- **Accept-before**: v1 recompute vs committed `MANIFEST.sha256` → **exit 0**. v2 recompute vs staged
  `MANIFEST.sha256` (now including the new `answer-key/prereg.json` line) → **exit 0**.
- **Direction 1 — tamper a covered file, recompute mismatch**: v1 — appended a line to
  `src/applyKeypadInput.ts` → **exit 2**; reverted (`git checkout --`) → **exit 0**. v2 — appended a line
  to `answer-key/prereg.json` → **exit 2**; reverted (`git checkout --`, restoring the staged blob) →
  **exit 0**, digest confirmed byte-identical to the pre-tamper file (`ef0a578a...`).
- **Direction 2 — tamper the MANIFEST's own expected digest**: v1 — flipped one hex character in
  `MANIFEST.sha256`'s `src/applyKeypadInput.ts` line → **exit 2**; restored from backup → **exit 0**. v2 —
  flipped one hex character in `MANIFEST.sha256`'s new `answer-key/prereg.json` line → **exit 2**;
  restored from backup → **exit 0**.
- Real tree never left dirty: `git diff` (worktree vs index) empty on both fixtures after every revert;
  `git diff --cached --stat` shows exactly `v2/MANIFEST.sha256` (+1) and `v2/answer-key/prereg.json`
  (+36); explicit confirmation `v1/src`, `v1/tests`, `v1/runtime`, `v2/src`, `v2/tests`, `v2/runtime`,
  `v1/answer-key/s1.json`, `v2/answer-key/s2.json` carry **zero** staged diff.

**`./hooks/pre-commit` (staged) and `./hooks/pre-commit --all`**: real exit codes recorded in the return
summary below (both run after this section was written and staged).

**Line counts, both stated with their command.** Fixture-only subtotal (`git diff --cached --numstat`,
stable — these two files are not further edited after this point): `v2/MANIFEST.sha256` 1+0;
`v2/answer-key/prereg.json` 36+0. Generated-golden exclusion (`sdd-phase-common.md:104`): `MANIFEST.sha256`'s
single inserted digest line — `-1`. Fixture-authored subtotal = (1+36) − 1 = **36**. Journal/task-file
diffs (`sdd/failure-flood-triage/tasks.md`, `sdd/failure-flood-triage/apply-progress.md` itself), counted
per this unit's own instruction that only generated goldens are excluded — reported with the exact final
`git diff --cached --numstat` command and output in the return summary to the orchestrator, since this
sentence is itself inside that diff and any number frozen here would be stale by the time the command is
actually run.

**Not committed or pushed** — staged only, per instruction.

**PR4 closes with this task. Nothing left inconsistent inside PR4 by it** — tasks 4.1–4.4 all `[x]`,
`s1.json`/`s2.json`/`prereg.json` all committed (staged) and manifest-covered for their respective
fixtures. One pre-existing note carried forward, not introduced here: task 3.5's own apply-time finding
that `design.md:584-585`'s "File changes" table row still claims v1 gets a `tools/generate-cases.py`
(contradicted by R-F9.1, confirmed stale on disk) remains unfixed — out of this phase's scope, flagged
again for whichever PR next touches `design.md`. **PR5 depends on this task's `answer-key/prereg.json`
existing and being correct** for its own preflight (task 5.1) to check against; PR6 depends on PR5.

## PR5a — `run-pipeline.sh` core (tasks 5.1, 5.2, 5.3, 5.6 ONLY)

Depends on: PR2, PR4. Scope carved explicitly narrower than PR5's own line in tasks.md: NOT 5.4 (surface
preimage capture), NOT 5.5 (diagnostician-writes-to-`src/` violation classification), NOT 5.7 (the real
`--shakedown` shakedown run), NOT 5.8 (`derive.py`'s `--experiment` dispatcher). Created
`rig/run-pipeline.sh` (693 authored lines). `rig/run.sh` is **untouched**: `git status --porcelain --
rig/run.sh` and `git diff --stat -- rig/run.sh` both empty, before and after this batch.

**Two real bugs found by live adversarial testing, not by code review — both fixed, both re-verified
live:**

1. **`compute_manifest()`'s first draft walked only the single file `answer-key/case-table.sha256`**,
   matching task 3.5's own done-note (`tasks.md:448-450`: "…, answer-key/case-table.sha256") — true only
   at that task's own moment in time, before tasks 4.2/4.4 added `answer-key/s1.json`, `s2.json` and
   `prereg.json`. A live recompute-compare of that first draft against the REAL committed
   `v2/MANIFEST.sha256` mismatched by exactly 2 lines (`answer-key/prereg.json`, `answer-key/s2.json`) —
   caught before staging, not asserted as passing. Fixed to walk the whole `answer-key/` directory (same
   as `src/tests/runtime/tools`); re-verified **MATCH** for both v1 and v2 with a standalone Python
   reimplementation of the corrected algorithm run directly against both real committed fixture trees.
2. **`npm ci --prefix <dir>` (invoked from a different cwd) is NOT `cd <dir> && npm ci`.** Live: `npm ci
   --prefix <install-dir>` run from `<repo>` root failed `EUSAGE` — `--prefix` resolves the *root package*
   against the CALLER's cwd while installing into `<install-dir>/node_modules`, so it validated `<repo>`'s
   own (nonexistent) `package.json` against the fixture's lockfile and reported "Missing: install@1.0.0
   from lock file" (`install` being the install directory's own basename, not a real dependency). Manual
   `cd <install-dir> && npm ci --silent` (no `--prefix`) succeeded, exit 0, confirming the diagnosis.
   Fixed: `( cd "$INSTALL_DIR" && npm ci --silent ... )`.
3. **A third bug, found by the very first live run of the `--shakedown` path**: calling a function that
   `return`s non-zero as a bare statement under `set -e` aborts the WHOLE SCRIPT immediately — the first
   live run of the missing-prompt abort path produced an EMPTY `arm.json` and no `status.json` at all,
   silently violating Amendment 1 ("flushed before every exit path, including 1 and 2"), with no error
   message printed. Root cause: `run_model_step ...` called as a bare statement, returning `2` on a
   missing prompt/surface file, which `set -e` treated as script-ending. Fixed: these functions now always
   `return 0` and signal via the `ABORT_REASON` global, checked explicitly by the caller after each call.

**Adversarial exercises actually run, real exit codes, redacted paths (`<repo>` for the real absolute
path, which DID appear in raw terminal output during testing — never in any committed file; confirmed by
`./hooks/pre-commit` below):**

1. **Non-shakedown invocation today, zero hypothesis matches.** `<repo>/rig/run-pipeline.sh s2 pipeline 99
   --permission-mode acceptEdits --dirty-ok` (`--dirty-ok` needed only because `rig/run-pipeline.sh` itself
   is newly staged under `rig/`, tripping the dirty-tree guard first on an un-flagged attempt — confirmed
   by running once without `--dirty-ok` and observing that exact guard fire, exit 2, before retrying).
   Result: **exit 2**, message: `pre-registration guard failed (Hard Ordering Gate layer 2): zero_matches:
   hypotheses/0002-*.md` — the exact `prereg.json`-named reason (`check.zero_matches`,
   `v2/answer-key/prereg.json:30`), matching `git ls-files hypotheses/` showing no `0002-*`/`0003-*` file
   exists yet.
2. **`--shakedown` unconditional void stamp — proven by a real live run, not asserted from code
   inspection.** `<repo>/rig/run-pipeline.sh s1 monolithic 99 --permission-mode acceptEdits --dirty-ok
   --shakedown`. This is NOT a literally clean tree (this file's own staged addition trips the dirty-tree
   guard, hence `--dirty-ok`) — an honest limit on this specific proof, named rather than hidden. The run
   proceeded through a real `npm ci`, a real per-step workspace materialize, and a real abort at the
   missing-`prompts/monolith.txt` check (exit 2, arm aborted post-claim) — and the persisted
   `rig/runs/failure-flood-v1/s1-monolithic-99/status.json` (gitignored, inspected then deleted) read
   `{"state": "void", "void_reason": "shakedown", ...}`. The override code
   (`if [ "$SHAKEDOWN" -eq 1 ]; then ARM_STATE="void"; ARM_VOID_REASON="shakedown"; fi`) reads no `DIRTY`,
   `DIRTY_OK`, or prior `ARM_STATE` value — the exact property `rig/run.sh:463-466`'s
   `[ "$DIRTY_OK" -eq 1 ] && [ -n "$DIRTY" ]` lacks, quoted and read directly from `run.sh` before writing
   this override, not re-derived from tasks.md's prose.
3. **Tampered fixture file → manifest recompute-compare → exit 2, both directions verified.** One byte
   appended to the real tracked `v1/src/applyKeypadInput.ts` (unstaged) → `<repo>/rig/run-pipeline.sh s1
   monolithic 03 --permission-mode acceptEdits --dirty-ok` → **exit 2**, message: `MANIFEST.sha256
   mismatch under <repo>/rig/fixtures/failure-flood/v1`. Reverted (`git checkout --`) →
   `git status --porcelain` on that path empty again, confirmed.
4. **Git-repository-selection verify bullet (task 5.2's own, literally): run from a different cwd and a
   nested directory, both must stamp the same `code_commit`.** Ran once from
   `rig/fixtures/failure-flood/v1/src` (nested) and once from `/tmp` (different cwd); both persisted
   `status.json`s recorded the identical `code_commit` value. `REPO_ROOT`'s
   `BASH_SOURCE`-relative resolution (never a caller-supplied path to `git -C`) is what makes this hold.
5. **A real, unplanned bonus proof of 5.2/5.6 together**: the pipeline arm's `01-collect` step (a CODE
   step — no `claude` call, so nothing here touches PR5's out-of-scope shakedown or a live model
   invocation) actually ran to completion against the real, already-injected, committed `v2/src` with
   freshly generated case tables. Its `collection.json` reports `suite_state: ran`, `totals: {"tests":
   2882, "passed": 2383, "failed": 499}`, `9` clusters — an EXACT reproduction of task 4.3's own
   independently recorded measurement ("499 failing / 2,882 total... 9 clusters"), a strong live
   cross-check that materialize (src/tests/runtime/cases/node_modules-symlink), the per-run install, and
   the `collect.py` invocation wiring are all correct end-to-end, not merely syntax-checked. The same run's
   `arm.json` recorded `case_table_digest: b15b8d1698ea0b45e2c475c1d5c68e2dcac81458522771d724a3ca431e5becb1`
   — byte-identical to the value already committed at task 3.4 — and `workspace_file_count: 23`.

**Untestable within this unit, named precisely (never claimed as run):** any real `claude -p` model-step
invocation (01-monolith, 02-diagnose, 03-apply). Two real, independent blockers, both discovered by trying
to run past them, not assumed: (a) `rig/surfaces/failure-flood.txt` does not exist — task 5.4's own
deliverable, out of this unit's scope by instruction. (b) `prompts/` does not exist under EITHER fixture on
disk at all — **a newly found gap**: no task in PR3 (3.1–3.5) or PR4 (4.1–4.4) ever created it, despite
`design.md`'s own "File changes" table naming `…/v1/{src,tests,runtime,prompts,answer-key}/**` as created,
and despite neither fixture's real, measured MANIFEST path set (task 3.5: "v1... 10 files total"; task
3.5/4.4: v2's real set) ever including a `prompts/` entry. This is the SAME CLASS of `design.md`-vs-disk
discrepancy task 3.5 already found and recorded for v1's stale `tools/` row (`tasks.md:482–494`) —
flagged here, not fixed, since authoring fixture prompt content is not this file's job. Deliberately not
worked around with scratch/placeholder prompt or surface files that would let a real `claude -p` call
proceed: task 5.7 (the real shakedown run) is explicitly out of this unit's scope, and a live model
invocation — even against throwaway content — is the kind of thing that boundary exists to reserve.
Consequently, task 5.5's own violation-detection logic (which needs a real diagnostician turn to write to
`src/`) and the full three-step/four-step arm lifecycle end-to-end are also untested beyond the CODE-step
portion proven in point 5 above — both correctly deferred to their own tasks, not silently declared done.

**Redaction.** `./hooks/pre-commit` (staged): exit 0. `./hooks/pre-commit --all`: exit 0, "redaction
check: clean across 160 tracked files". No absolute host path appears in the committed file itself
(`REPO_ROOT` is resolved dynamically via `BASH_SOURCE`, never hardcoded) — confirmed by the redaction gate
passing, not merely asserted. Absolute paths DID appear in raw terminal output during my own live testing
(this journal entry redacts every one of them to `<repo>`); none were pasted into any committed file.

**Fixture content untouched.** `git status --porcelain -- rig/fixtures` and `git diff --stat -- rig/fixtures`
both empty throughout this batch — no fixture byte was ever left tampered after a revert.

**Line counts, ceiling — OVER, reported rather than trimmed, per this batch's own instruction ("stop and
report rather than trimming a guard to fit").** `git diff --cached --numstat`:
`rig/run-pipeline.sh` 693+0; `sdd/failure-flood-triage/tasks.md` 59+4;
this `apply-progress.md` append (final count taken with the diff itself, see the return summary for the
exact number — this sentence is inside the diff being measured, same caveat PR4.4 already named for the
same reason). Script-only raw = 693. Script + tasks.md raw = 693+59+4 = **756**, already over the 700
ceiling before this journal entry's own lines are added — no generated-goldens exclusion applies (this
file is 100% hand-authored bash + inline Python, no generated content). **Nothing was cut to force a fit**:
every one of the three layers in the Hard Ordering Gate, both fixture-tamper directions, the full
materialize/invoke/persist machinery for both arms, and every load-bearing citation comment shipped as
originally designed; ~37 lines of pure comment verbosity (no logic, no guard, no citation) were trimmed
from an initial 730-line draft before this overage was accepted and reported rather than cut further.
**Root cause of the overage, stated plainly:** the Hard Ordering Gate's three layers, two arms' differing
step topologies (2-step monolithic vs 4-step pipeline), and per-step JSON persistence for both roles
together require real machinery that does not compress under a budget calibrated against single-purpose
scripts like `collect.py`'s own collector-only surface.

**PR5a apply-time finding, recorded rather than silently absorbed**: `prereg.json`'s own `scope` block
(`v2/answer-key/prereg.json`) states task_id `s1`/v1 "is structurally always invoked with `--shakedown`",
which this batch's own preflight ordering makes literally true in a second, independent way — a
non-shakedown `s1` invocation hits `check_prereg()`'s `missing-prereg-config` exit-2 branch (no
`answer-key/prereg.json` exists for v1 at all) before ever reaching a hypothesis-glob check, so v1 refuses
non-shakedown invocations by construction, not merely by the `prereg.json` file's own documentation.

**PR5a does not close PR5.** Tasks 5.4, 5.5, 5.7, 5.8 remain `[ ]`, each blocked on a real, named
dependency (5.4 on nothing but its own capture work; 5.5 on nothing but its own classification logic; 5.7
on 5.4 landing first per the Hard Ordering Gate's own structural-impossibility design; 5.8 on `derive.py`
work not started here). PR6 remains blocked on PR5 closing in full.

## PR5b — tasks 5.4 and 5.4b ONLY (not 5.5, not 5.7, not 5.8)

**Scope discipline.** This batch touched exactly six paths:
`rig/fixtures/failure-flood/{v1,v2}/MANIFEST.sha256` (modified, +1 line each), `rig/run-pipeline.sh`
(modified), `rig/fixtures/failure-flood/{v1,v2}/prompts/{s1,s2}.txt` (created), and
`rig/surfaces/failure-flood.txt` (created). `rig/run.sh`, every fixture's `src/`, `tests/`, `runtime/`,
`s1.json`/`s2.json`/`prereg.json` are untouched — `git diff --stat rig/run.sh` and
`git diff --stat -- rig/fixtures/*/{src,tests,runtime,answer-key}` both empty, `git diff` on
`s1.json`/`s2.json`/`prereg.json` individually also empty. Two other sessions' uncommitted files
(`MAP.md`, `gaps/README.md`, `skills/project-gap-analysis/SKILL.md`, `gaps/0002-*.md`) were left alone —
staged by exact path (`git add <path> <path> ...`), never `git add -A`/`git add .`.

### Task 5.4 — the surface preimage, captured twice and compared

**Constraint honoured, not moved.** `rig/run.sh:330`: `BASELINE_DISALLOW="Bash"` — quoted verbatim,
confirmed unchanged by the empty `rig/run.sh` diff above. That baseline stays local to `run.sh`'s own
scoped-vs-broad comparison; `run-pipeline.sh` carries its own, separate preimage exactly as design.md's
"The new surface preimage" paragraph requires.

**Why a real invocation, not a derivation from `broad.txt`/`scoped.txt`.** `broad.txt` was captured with
`Bash` disallowed; failure-flood's both arms need `Bash` present. Computing "`broad.txt` ∪ {Bash}" would
have been arithmetic on a related file, not a read-back — exactly the "asserting the list you intended"
`run.sh:172`'s own design.md citation and this task's instructions both warn against. `rig/run.sh:315`'s
own comment is explicit that a guessed value here "would silently break every future void-classification"
— so a real subprocess was launched instead.

**Two real, independent captures, compared before either byte reached the repo.** `claude --version` on
this machine: `2.1.229 (Claude Code)`. Capture command (twice, each from a fresh scratch cwd outside
`<repo>`, never a nested nested-fixture path):
```
claude -p "Reply with exactly the single word OK and take no other action. Do not read, write, list, or execute anything." \
  --output-format stream-json --verbose --strict-mcp-config --permission-mode bypassPermissions
```
Both exited 0. Each `stream.jsonl`'s `system`/`init` event's `tools` list, read back exactly the way
`read_back_init()` (`run-pipeline.sh`) and `surface_digest()` (`rig/derive.py:87-91`) already do —
`sha256("\n".join(sorted(set(tools))))` — produced:
- capture 1: 31 tools, digest `d8693e27d5f8e406a465def75101c4eaa85b23b685e78c2d5d07754d0f7e8daa`
- capture 2: 31 tools, digest `d8693e27d5f8e406a465def75101c4eaa85b23b685e78c2d5d07754d0f7e8daa`

Identical sorted sets, identical digest, compared with a Python set-equality check before either was
written anywhere — **not** "captured once and assumed stable". The 31 tools: `Bash`, `CronCreate`,
`CronDelete`, `CronList`, `DesignSync`, `Edit`, `EnterWorktree`, `ExitWorktree`, `ListAgents`, `Monitor`,
`NotebookEdit`, `PushNotification`, `Read`, `RemoteTrigger`, `ReportFindings`, `ScheduleWakeup`,
`SendMessage`, `ShareOnboardingGuide`, `Skill`, `Task`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskOutput`,
`TaskStop`, `TaskUpdate`, `ToolSearch`, `WebFetch`, `WebSearch`, `Workflow`, `Write`. Notably absent:
`Glob`, `Grep` — confirming `run.sh:321-323`'s "Bash subsumes Glob and Grep... while it is available the
surface presents Bash alone and hides them" empirically for this invocation shape too, not just
`run.sh`'s own scoped/broad pair. Committed to `rig/surfaces/failure-flood.txt` in the exact
`broad.txt`/`scoped.txt` format (`# harness: <version> (Claude Code)` header, one tool name per line,
`load_surface()`'s comment-stripping convention).

**Verify bullet, live: subprocess argument composition.** A third real invocation, cwd
`.../scratchpad/adversarial capture 3` (a path containing spaces), prompt text containing spaces, a
double quote, a single quote, a backtick, and non-ASCII (café / 中文 / 🎯), run through the identical
composition `run-pipeline.sh:521` uses for real steps (`claude -p "$PROMPT_TEXT" --strict-mcp-config
--permission-mode bypassPermissions ...`, prompt as one quoted argument, never interpolated into a larger
string) — exit 0, `stderr.log` empty, and the read-back digest was again exactly
`d8693e27d5f8e406a465def75101c4eaa85b23b685e78c2d5d07754d0f7e8daa`. Composition survives adversarial
content; `init.tools` matches the committed preimage regardless.

### Task 5.4b — the missing `prompts/`, and the topology question resolved with quotes

**The literal instruction that decides the naming scheme.** `tasks.md:794` (this task's own text): "one
`.txt` per `task_id` (`s1`, `s2`)" — exactly two files, not three, not one per role.

**The real conflict this task named, found on disk, not assumed.** PR5a's own `run_model_step()`
resolved the prompt path as `local prompt_file="$FIXTURE_ROOT/prompts/${role}.txt"` — `role` being
`monolith`, `diagnose`, or `apply` (derived from the step name), which would need **three** files per
fixture, directly contradicting the two-file instruction above. Corrected to
`local prompt_file="$FIXTURE_ROOT/prompts/${TASK_ID}.txt"` — the exact naming `rig/run.sh:306` already
uses (`PROMPT_FILE="$FIXTURE_ROOT/prompts/${TASK_ID}.txt"`), so `run-pipeline.sh` now follows the same
convention as its sibling rather than inventing a second one.

**Why one file can serve MONOLITHIC's one step and PIPELINE's two model steps, per ADR 0010.** The
constraint is that the same task must be posed to both arms; one committed file, loaded byte-identical
for `monolith`, `diagnose`, and `apply` alike, is a *stronger* guarantee of that than three separately
authored (even if intentionally similar) files could ever prove — the prompt hash cannot silently drift
per role because there is only one set of bytes to hash. What legitimately differs between roles is
never prompt text — it is workspace state (a diagnostician's fresh workspace has no prior `fix-plan.txt`;
an applier's does, copied in by `run-pipeline.sh` itself before invocation) — and workspace composition
is harness shape, the one dimension ADR 0010 permits to vary. The prompt text itself is written to be
agnostic to which role reads it: it states the overall task (investigate failing tests, find root
causes, fix them), an *optional* branch for a role that produces a plan without applying it
(`fix-plan.txt`) and an *optional* branch for a role that finds one already present — both branches are
simply inert for `monolith`, which never encounters either file. Content, not asserted from design intent
alone but checked against `spec.md`'s own hard obligation: `R-F3.1` — "Both arms MUST write a file
`root-cause-report.txt` to the run workspace root before completion, in this exact format... Line 1 is
the literal sentinel [`ROOT-CAUSE-REPORT v1`]. Every following non-blank line MUST match
`^[\w/.\-]+:\d+$`" — quoted into the prompt body verbatim rather than paraphrased, so the deliverable
format the prompt asks for and the format the (future, task 5.8) scorer will parse are provably the same
text.

**A design.md staleness flagged, not silently followed.** `design.md`'s own "Data flow" section (and its
"Decision 4 revised" paragraph) describes the frozen format as `CAUSE <path>:<line> <cluster_ids>` lines
inside the final assistant message, parsed from `result.result` — but `spec.md` (`rg -n "CAUSE"
sdd/failure-flood-triage/spec.md` → zero matches) contains no such format anywhere; `R-F3.1` is the only
current, normative deliverable-format requirement, and it names a **file** (`root-cause-report.txt`), not
a final-message line format. Since `spec.md` was accepted gate-clean and amended in place after
`design.md`'s own revision (per the spec artifact's own Engram note), `spec.md` is treated here as
authoritative and `design.md`'s "Data flow" diagram is flagged as stale — same class of finding as the
`tools/`-under-v1 and `prompts/`-never-created gaps already caught twice in this PR. Not fixed here
(`design.md` is out of this unit's scope); recorded so it does not evaporate, for whichever PR next
touches `design.md`.

**Redaction, ADR 0009.** No donor/client/employer/person name anywhere in `s1.txt`/`s2.txt` — checked by
inspection (the prompt speaks only of "this project's automated test suite") and by
`./hooks/pre-commit --all`'s redaction gate passing over the newly-added files. No specific root-cause
count is disclosed to the agent (the prompt says "root causes", plural, open-ended) — avoiding exactly
the closed-vocabulary ground-truth leak `design.md`'s "Decision 4 revised" already warned against.

**`prompts/` stays never-materialised — confirmed by reading the code, not asserted.**
`materialize_step()` (`run-pipeline.sh`) copies only `src/`, `tests/`, `runtime/` into a step's workspace;
`manifest_workspace_paths()` filters `compute_manifest()`'s own output to `^(src|tests|runtime)/`,
explicitly excluding `prompts/` (and `tools/`, `answer-key/`) from ever being hashed as workspace content
or copied anywhere the agent's tools can see it. `run_model_step()` reads `prompt_file`'s bytes into a
shell variable and passes them as `claude -p`'s own argument — the file's path is never inside the
workspace directory tree at all. Unchanged by this batch; confirmed, not altered.

**Manifest coverage gap found and closed.** `compute_manifest()`'s subdirectory tuple was
`("src", "tests", "runtime", "tools", "answer-key")` — it never included `prompts`, even though
design.md 9a groups `prompts/` with the already-covered `tools/`/`answer-key/` as "never-materialised"
but manifest-covered. Left as-is, the new `prompts/s{1,2}.txt` files would have been invisible to the
MANIFEST.sha256 recompute-compare gate entirely — a tamper to either prompt file would go undetected.
Added `"prompts"` to the tuple. Verified two ways: (1) extracted the exact function body from the edited
file and ran it standalone against both fixture roots — `diff` against each committed `MANIFEST.sha256`
showed exactly one new line each (`prompts/s1.txt` / `prompts/s2.txt`, correct digest, correct sort
position between `answer-key/` and `runtime/`), nothing else changed; (2) after appending those lines,
re-ran the same extracted function and diffed again — **clean, both fixtures**.

**`prompts/s1.txt` and `prompts/s2.txt`.** Identical content by design (see the topology section above —
nothing in `spec.md`/`design.md` requires stage-1 and stage-2 wording to differ, and identical wording
avoids introducing an uncontrolled third variable between stages); `diff` between the two files: empty.
Both sha256 `f6d2d9abf4d0dfa4eda049a32fea2826ea164d1a52a6adad810a0c9c54474c99`.

**Answer-key-before-prompt ordering, confirmed already satisfied, not re-ordered.** `v1/answer-key/s1.json`
and `v2/answer-key/{s2.json,prereg.json,case-table.sha256}` were committed in PR4 (tasks 4.1-4.4), long
before this PR5b commit exists. `git log --diff-filter=A -- rig/fixtures/failure-flood/v1/answer-key/s1.json`
and the `v2/answer-key/*` equivalents all predate this working tree's HEAD by multiple commits (PR4's own
commits); this batch's prompt files are staged, not yet committed, and will land in a commit strictly
after those. "Checker-first" stays provable from commit order without any action needed here.

**Live proof the two aborts no longer fire — real exit codes, not code-reading.**
```
$ bash rig/run-pipeline.sh s1 monolithic 9054 --permission-mode bypassPermissions --shakedown --dirty-ok
  run s1-monolithic-9054: state=void (shakedown) -> .../rig/runs/failure-flood-v1/s1-monolithic-9054
EXIT=0
```
`arm.json`: `"abort_reason": null`, `"workspace_file_count": 10` (matches task 3.5's own v1 count).
Step `01-monolith`: `"exit_code": 0`, `"kind": "model"`, `"surface_sha256":
"d8693e27d5f8e406a465def75101c4eaa85b23b685e78c2d5d07754d0f7e8daa"` (matches the committed preimage
exactly), `"wall_ms": 89539` — an 89.5-second REAL invocation, not an instant abort (an early
`missing-prompt`/`missing-surface-preimage` return happens before `write_step_status` is ever called, so
no step-level `status.json` would exist at all if either had fired). The model's own final message: "Fixed
all three bugs and all 36 tests now pass" — it genuinely found and fixed all three of v1's injected root
causes (`parseTransfers.ts:34`, `confirmSeed.ts:15`, `applyKeypadInput.ts:28`) in 19 turns.
```
$ bash rig/run-pipeline.sh s2 pipeline 9054 --permission-mode bypassPermissions --shakedown --dirty-ok
  run s2-pipeline-9054: state=void (shakedown) -> .../rig/runs/failure-flood-v1/s2-pipeline-9054
EXIT=0
```
`arm.json`: `"abort_reason": null`, `"workspace_file_count": 23` (matches task 5.6's own v2 count).
Steps `02-diagnose` and `03-apply`: both `"exit_code": 0`, `"kind": "model"`, both reading back the same
`d8693e27...` surface digest — proving the SAME `prompts/s2.txt` file served both PIPELINE model roles
without incident, exactly as task 5.4b's own topology decision above requires.

**Regression check, explicit, per this batch's own instruction — a non-shakedown invocation must still
exit 2.**
```
$ bash rig/run-pipeline.sh s2 pipeline 9055 --permission-mode bypassPermissions --dirty-ok
  COULD NOT RUN: pre-registration guard failed (Hard Ordering Gate layer 2): zero_matches: hypotheses/0002-*.md
  This is exit 2, not a pass.
EXIT=2
```
Unchanged from PR4/PR5a's own recorded behaviour — this batch never touched `check_prereg()` or the
`hypotheses/` directory. No countable run is any closer to proceeding than before this PR5b landed.

**An anomaly this same live testing surfaced, flagged not fixed — task 5.5's territory.** `01-monolith`'s
step `status.json` records `"substrate_changed": false` even though the model's own final message
describes editing three files under `src/`. `substrate_changed` is computed by `hash_paths()` over
`WORKSPACE_PATHS` (the manifest's `src`/`tests`/`runtime` paths) taken before and after the invocation;
either that pre/post capture has a real defect, or the observed edits landed somewhere `hash_paths()`
does not cover. Not investigated further — task 5.5 owns "Detect the diagnostician-writes-to-`src/`
violation (re-hash its workspace against its materialised file list...)" and this batch's own instruction
was explicitly tasks 5.4/5.4b only, not 5.5.

**Verification, all real exit codes.**
- `bash -n rig/run-pipeline.sh` → exit 0.
- Both `MANIFEST.sha256` recompute-compare clean (shown above, both directions).
- `./hooks/pre-commit` (staged only) → exit 0.
- `./hooks/pre-commit --all` → exit 0, "redaction check: clean across 163 tracked files".
- `git diff --stat rig/run.sh` → empty. `git diff --stat` on each fixture's `src/`/`tests/`/`runtime/`/
  `answer-key/`/`tools/` → empty. `git diff` on `s1.json`/`s2.json`/`prereg.json` individually → empty.
- Non-shakedown regression check → exit 2 at the pre-registration gate (shown above), unchanged.

**Line counts, ceiling.** `git diff --cached --shortstat` (the six touched files):
**6 files changed, 91 insertions(+), 16 deletions(-)** = 107 raw. Journal/task-file diffs (this
`apply-progress.md` append plus the `tasks.md` 5.4/5.4b done-notes) are counted in the return summary
alongside this file's own final line count, for the same "measuring the diff from inside itself" reason
PR5a's own entry already named. Well under the 700-line ceiling either way.

**Scope not expanded beyond 5.4/5.4b.** No `derive.py` change (task 5.8's `prompt_sha256`/row-builder
territory — `R-F7.1`'s "hash of each role's exact prompt bytes" is satisfiable from the same
`surface_digest()`-style convention applied to the prompt file, but wiring it into `status.json` is 5.8's
own concern, not touched here). No `clusters.json`-into-diagnose-workspace wiring (not named by any task
in this batch; the diagnose role's live run above therefore had the same full `src/`/`tests/`/`runtime/`
copy MONOLITHIC gets, not the bounded clusters view design.md describes — a pre-existing gap, not
introduced or expanded here, flagged for whichever task owns that wiring). Tasks 5.5, 5.7, 5.8 remain
`[ ]`, each blocked exactly as PR5a's own entry already described.
