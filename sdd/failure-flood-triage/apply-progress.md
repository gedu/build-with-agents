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
