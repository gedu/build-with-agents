---
id: sdd/failure-flood-triage/tasks
type: journal
targets: [any]
status: draft
verified: 2026-08-11
sources: ["sdd/failure-flood-triage/proposal.md", "sdd/failure-flood-triage/spec.md",
"sdd/failure-flood-triage/design.md", "sdd/measurement-rig/tasks.md",
"decisions/0013-a-committed-executable-carries-its-own-test.md", "skills/hypothesis-cycle/SKILL.md",
"skills/README.md"]
---

# Tasks: failure-flood-triage

No test runner exists in this repo, by decision (ADR 0013). Verification below is `bash -n`,
`python3 -m py_compile`, `./hooks/pre-commit --all`, each executable's own `--self-test`, and manual
adversarial exercises — never "run the repo's test suite." One exception, named explicitly because it
is easy to blur: **`rig/fixtures/failure-flood/*` carries its own Jest suite, and running that suite is
the correct verification surface for fixture content** (PR3/PR4). That suite reports on the fixture,
never on `<repo>`, and no `<repo>`-level command runs it — the boundary PR1's ADR ratifies.

**Word-budget note, flagged rather than silently exceeded** (same precedent as `design.md`'s own flag):
this change is seven work units carrying spec-mandated hardening (integrity guard, pre-registration
gate, threat-matrix adversarial checks, per-task verification) that do not compress under the generic
530-word tasks budget without losing a requirement. Completeness over brevity, stated here.

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | ~2,000–2,300 authored total (up from the proposal's ~1,850: +ADR file, +derive.py `--experiment` dispatcher folded into PR5, +uncertainty on real donor-module byte count in PR3/PR4). Generated case rows are never committed (Decision 9a) and are excluded by construction, not by convention |
| Changed-line ceiling | **700, ratified 2026-08-11 for the whole remaining stack** (was 400, then 500 raised per-PR). Two work units exceeded it before the number was corrected: PR1 at 422 and PR2 at 682. The per-PR estimates below were derived from these task bullets rather than from the `design.md` sections those bullets implement, which is why they read low — the implementations were not inflated. PR2 in particular cannot be split at all: ADR 0013 requires a self-test to ship inside the file it tests, so extracting `collect.py`'s ~150 self-test lines to fit a budget would violate a ratified decision. PR3/PR4 keep their named splits so no single PR becomes unreviewable |
| Chained PRs recommended | **Yes** |
| Suggested split | PR1 → PR2 → PR3 → PR4 → PR5 → PR6 (stacked) |
| Delivery strategy | chained PRs, `size:exception` NOT taken |
| Chain strategy | **stacked-to-main** — PR1 targets `main`; each subsequent PR targets the previous PR's branch |

```text
Decision needed before apply: No — resolved 2026-08-11
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
Changed-line ceiling: 700 (ratified 2026-08-11 for the remaining stack)
```

**Decision needed before apply — both resolved 2026-08-11, so apply is unblocked:** (1) the per-module
axis-table amplification target proposed in PR3.3 (below) is **operator-confirmed**. R-F9.2 still binds:
the achieved ratio must be measured per run and never assumed — confirming a target does not license
assuming the outcome. (2) The named contingency split for PR3/PR4 (below) is **pre-authorized** and
applies without a further decision if their real authored diff exceeds the ratified 700, since real
donor-module source length is unknown until the modules are actually copied in.

### Per-PR line estimate and split point

| PR | Slice(s) | Est. lines | Risk | Named split if it overruns |
|---|---|---|---|---|
| PR1 | item1 (peak-occupancy retro-derive) + item3 (ADR) | ~260 | Low | — |
| PR2 | item2 (collector + normalizer) | ~300 | Low–Medium | — |
| PR3 | item4 (3a: clean fixture + case generator, v1+v2) | ~400–700 | **High** | **3a-i**: v1 stage-1 clean substrate (3 modules, tests, runtime) → **3a-ii**: v2 stage-2 clean substrate (remaining modules, `tools/generate-cases.py`, axis table, `case-table.sha256`) |
| PR4 | item5 (3b: injections + measured answer-key, v1+v2) | ~300–500 | Medium–High | **3b-i**: v1 injections + `F0`/`R0`/`S0` → **3b-ii**: v2 injections + amplified key + cluster-per-injection measurement |
| PR5 | item6 (`run-pipeline.sh` + surface preimage + `derive.py` dispatcher) | ~350–420 | Medium | **5a**: `run-pipeline.sh` + `rig/surfaces/failure-flood.txt` → **5b**: `derive.py --experiment` dispatcher, second row builder, `no-preregistration` void |
| PR6 | item7 (hypotheses + `OPERATIONS.md` + `report.py` tables + portable-procedure backlog entry) | ~270 | Low | — |

## The ADR rides with PR1, not PR2 — decided, with reasoning

Seven work units, six approved PR boundaries (per the proposal's own approved order). The ADR
(spec R-F11, design "fixture/repo boundary ADR") must land before PR3 (3a) and blocks neither PR1 nor
PR2 — so either can host it. **Chosen: PR1.** PR1 is ~150 authored lines against PR2's ~300; adding a
~90–120-line decision record to PR1 leaves ~260, comfortably under budget, whereas the same addition to
PR2 (~390–420) sits at or over the edge for no benefit — the ADR is thematically independent of both
(design: "does not block slices 1 or 2, which touch neither the fixture nor the toolchain"), so the
deciding factor is purely headroom, not cohesion. Landing it in PR1, the first PR in the stack, also
removes any chance of forgetting it before PR3 — the ordering becomes structural (stack order), not a
remembered convention.

## Hard Ordering Gate — no countable run before the hypotheses land (R-F8, design §7)

**Named failure mode this replaces:** `rig/run.sh:463–466` stamps `void_reason=dirty-tree` only when
`[ "$DIRTY_OK" -eq 1 ] && [ -n "$DIRTY" ]` — i.e. only if the tree is *actually* dirty at invocation
time. PR5's shakedown runs after PR5 is committed, on a clean tree, so `--dirty-ok` alone would stamp
nothing and produce a fully countable row — leaking into N, spread, and both hypothesis tests. This is
the exact ADR 0012 violation the gate below exists to prevent, and it is why the guard is mechanical,
not a remembered flag convention.

Three independent layers, per design §7 (none of which anyone can forget or bypass with one flag):

1. `run-pipeline.sh` exposes a **dedicated `--shakedown` flag**, distinct from `--dirty-ok`, that stamps
   `void_reason=shakedown` **unconditionally** on every row it produces, regardless of tree state.
2. Preflight refuses (`exit 2`) to run the shakedown without `--shakedown` explicitly set, and separately
   refuses (`exit 2`) any **non**-shakedown invocation unless `hypotheses/0002-*.md` and
   `hypotheses/0003-*.md` exist, are git-tracked, and are clean (frozen list in `answer-key/prereg.json`,
   inside the MANIFEST).
3. `derive.py` stamps any row with `prereg_digest: null` as `void: no-preregistration` — a second,
   independent layer that does not depend on the runner having enforced (2) correctly.

**Task-list consequence:** PR5's own shakedown verification run (task 5.7 below) MUST invoke
`--shakedown` explicitly, never `--dirty-ok` alone, even though the tree is clean at that point. PR6
(hypotheses + report) MUST land before any stage-2 comparison run is funded; PR5 structurally cannot
produce a countable row before PR6 lands, because `hypotheses/0002-*`/`0003-*` do not exist yet — layer
2 refuses to start, which is "structurally impossible," not "forbidden."

## PR1 — Peak-occupancy retro-derive + fixture/repo boundary ADR

Depends on: nothing. Blocks: PR3 (R-F11 scenario — 3a must not proceed without the ADR).

- [x] 1.1 Modify `rig/derive.py`: walk `assistant` stream events, de-duplicate by `message.id` (keep
      first occurrence in stream order), build the per-turn `occupancy_series`.
      Verify: `python3 -m py_compile rig/derive.py`. **Done** — `parse_stream` now returns a sixth
      value, `turns` (stream-ordered, de-duplicated `(message_id, usage)` pairs); compile passes.
- [x] 1.2 Add fields to `tool-surface-v1` rows: `model_turns`, `occupancy_series`,
      `peak_occupancy_tokens` (max over series), `peak_occupancy_turn`, `cumulative_occupancy_tokens`
      (sum over series + output), `occupancy_aggregate_matches` (cross-check vs `result.usage`),
      `occupancy_is_monotone`, `context_window_tokens`. Bump `tool-surface-v1` `schema_version` 2 → 3.
      Verify: re-derive all 42 existing rows; project out `schema_version`, `checker_digest`, and every
      new key; every remaining byte identical to the pre-change row (the achievable claim per design's
      correction — anything stronger chases `checker_digest`'s self-hash, which changes on any edit).
      **Done** — new `compute_occupancy()` helper; all eight fields added to the row. Projection
      regression run: 42/42 rows byte-identical after excluding `schema_version`, `checker_digest`, and
      the eight new keys. Zero mismatches.
- [x] 1.3 Confirm `occupancy_aggregate_matches: true` on all 42 rows; then, on one **copied** capture
      (never the committed one), mutate one turn's usage and confirm the mismatch anomaly fires.
      Verify: manual before/after diff of the anomaly field on the copy only. **Done** — 42/42 rows
      show `occupancy_aggregate_matches: true`. On a scratch copy of one capture's `stream.jsonl`
      (never `rig/runs/`, which is gitignored and untouched), bumping one turn's
      `cache_read_input_tokens` by 1000 flipped `occupancy_aggregate_matches` from `true` to `false`
      and changed only that turn's `occupancy_series` entry — the mismatch anomaly fires correctly.
- [x] 1.4 Record whether `occupancy_is_monotone` is `true` on all 42 rows or diverges anywhere.
      This is the R-F5's "settle before any new spend" gate — its result is read, not assumed, before
      PR3 begins. Verify: value present and non-null on every row. **Done and reported below** —
      `occupancy_is_monotone` is `true` on all 42/42 rows, non-null everywhere. See the finding note
      below the task list.
- [x] 1.5 Create `decisions/0014-a-fixtures-runtime-is-substrate-not-this-repos-runner.md`. Clause A:
      a rig fixture (`rig/fixtures/failure-flood/*`) may carry its own runtime (Node/npm) and test
      runner (Jest); that runtime is substrate under measurement, never this repo's verification
      surface, which remains `hooks/pre-commit`, `bash -n`, `python3 -m py_compile`, and each committed
      executable's own self-test — unchanged. States the practical test: the fixture's suite reports on
      the fixture, never on this repo, and no repo-level command runs it. Clause B: explicitly declines
      ADR 0013's supersession trigger ("when a third executable needs a test") on the record, though it
      is met (this change commits three: `run-pipeline.sh`, the collector, `tools/generate-cases.py`),
      because the per-executable self-test pattern still holds for all of them; restates the trigger
      more sharply — "when a self-test needs fixtures too large to inline."
      Verify: structural readback against R-F11.1/R-F11.2's required content; `./hooks/pre-commit --all`.

**PR1 apply-time findings, recorded rather than silently absorbed:**

- **`occupancy_is_monotone` is `true` on all 42/42 rows — settled, not sampled.** Every deduplicated
  per-turn occupancy series in the corpus rises (or holds) turn over turn; peak equals the final turn
  everywhere. Per R-F5's own framing, this means peak occupancy is **redundant with cumulative on this
  task class** for `tool-surface-v1` — a real, reportable finding (design.md's own stated risk: "a 'no'
  would mean `hypotheses/0002` and `0003` are closer to one claim than two"). It does not mean the peak
  channel is wrong to build for `failure-flood-v1` — a longer, multi-step pipeline arm with fresh
  per-step sessions and different cache behavior is exactly the case where the two channels could
  diverge, and this task class (`tool-surface-v1`, single-session, growing cache) is not evidence either
  way for that different shape. Reported here so PR6's hypotheses are written against the true, not
  assumed, state of this instrument.
- **The `rig/runs/` vs `rig/results/tool-surface-v1/runs.jsonl` count discrepancy named in this change's
  launch instructions does not reproduce on this machine.** Both are exactly 42, with an exact 1:1
  `run_id` correspondence (verified: `set(dir names) == set(run_id values)`, symmetric difference
  empty). No incomplete or void capture is missing a directory, and no directory is missing a row.
  Recorded as a correction rather than silently building an explanation for a gap that measurement does
  not show.
- **`derive.py`'s projection regression passed with zero mismatches** across all 42 rows, excluding
  `schema_version`, `checker_digest`, and the eight new keys (`model_turns`, `occupancy_series`,
  `peak_occupancy_tokens`, `peak_occupancy_turn`, `cumulative_occupancy_tokens`,
  `occupancy_aggregate_matches`, `occupancy_is_monotone`, `context_window_tokens`).
- **`decisions/0014-*.md`'s Clause B roster follows this task's explicit brief** (four self-test-carrying
  executables: `hooks/pre-commit`, `rig/derive.py`, `rig/run-pipeline.sh`, `rig/collect.py`; the case
  generator named as the future candidate, not counted among the four) **rather than
  `design.md`'s own worked "what the ADR must settle" paragraph**, whose literal four-item list
  (`hooks/pre-commit`, `collect.py`, `run-pipeline.sh`, `tools/generate-cases.py`) drops `rig/derive.py` —
  the one executable ADR 0013 names as its original precedent — while adding the case generator to the
  same list it is later named the *future* candidate for. Neither four-item list reconciles against ADR
  0013's own "two already, a third triggers" framing: 2 pre-existing (`hooks/pre-commit`, `derive.py`) +
  3 new (`run-pipeline.sh`, `collect.py`, `tools/generate-cases.py`) once every PR lands is 5, not 4,
  under either roster. This does not change Clause B's decision (decline the trigger; the
  infrastructure-ahead-of-content reasoning holds whether the count is 4 or 5) — flagged here as a
  design.md internal inconsistency for the record, not resolved by silently picking whichever count
  looks cleanest.

## PR2 — Collector + signature normalizer

Depends on: PR1 (independent content, sequenced by the stack). Blocks: PR3, PR4 (both need the
collector to validate fixture/injection signatures).

- [x] 2.1 Create `rig/collect.py` (`python3`, stdlib only). Invokes the suite itself, pinned
      `--runInBand` + JSON report file. Emits `collection/1` (suite state, totals, `failures`,
      `clusters`, `identifier_set_digest`).
      Verify: `python3 -m py_compile rig/collect.py`. **Done** — exit 0.
- [x] 2.2 Implement the three suite states (`ran` / `did-not-start` / `partial`) decided from evidence
      (report parseable + count check), plus `collector-error` as a **run-axis void**, never a suite
      state (absent/underfloor toolchain, install missing, lockfile mismatch, collector's own crash).
      Verify: synthetic Jest-JSON fragments inlined in the file (no fixtures directory, per ADR 0013)
      exercise all four outcomes. **Done** — self-test cases (c.1)-(c.4) and (e) below exercise
      `ran`/`did-not-start`/`partial`/`partial+suite-timeout`/`collector-error` from inlined synthetic
      fragments; no fixtures directory created. Also implemented, per design.md 9b (explicitly binding
      per this phase's launch instructions, though not spelled out in this task's own line):
      `report_bytes` + a declared ceiling (`--max-report-bytes`, default 64 MiB) that exits 2
      `collector-error: report-too-large` rather than streaming-parsing; a second, bounded `clusters/1`
      artifact (`clusters_view()`) carrying no `member_test_ids`, so it is bounded by cluster count, not
      failure count.
- [x] 2.3 Implement the normalizer: relative `test_id`, signature over the first-failure message
      truncated at the first stack line, fixed-order normalization (ANSI/CRLF/whitespace/path/line:col),
      matcher-shaped-head-only `signature_text`, `sha256(...)[:16]`. Deterministic cluster ordering
      (`count desc, signature asc`).
      Verify: `rig/collect.py --self-test`, cases (a)–(e). **Done, all 9 checks PASS** (the 5 named
      a-e plus 4 sub-checks under (c) for the fourth, at-scale sub-case and the bounded clusters view):
      (a) same cause, differing absolute path/line/col/order **and** differing Expected/Received body
      (the 9c amplification case, not only path/line/order) → same signature — PASS;
      **(b) two genuinely different causes → different signatures — PASS**;
      (c) `ran`/`did-not-start`/`partial`/`partial+suite-timeout` each fire from a synthetic report —
      PASS ×4;
      (d) same input twice → byte-identical output — PASS;
      (e) absent toolchain → `collector-error`, never a suite state — PASS.
- [x] 2.4 Confirm the `--self-test` flag is gated (never runs unconditionally inside a measured arm,
      unlike `derive.py`'s unconditional self-test — a different, correctly-not-reused pattern per
      design's correction #3).
      Verify: `rig/collect.py` with no flag prints/does nothing beyond normal collection; `./hooks/pre-commit --all`.
      **Done** — no-flag invocation with no other arguments exits 2 with a required-arguments message
      (never reaches or prints the self-test); `./hooks/pre-commit --all` exit 0 (see apply-progress for
      the full run against the tracked tree).

## PR3 — Clean fixture + case generator (3a)

Depends on: PR1 (ADR must exist — R-F11 scenario), PR2 (collector validates the clean baseline).

- [x] 3.1 Create `rig/fixtures/failure-flood/v1/{src,tests,runtime}/**` — stage-1 clean substrate
      (donor modules hosting 3 of the 6 root causes), author-authorized real code per the proposal's
      recorded authorization. `package.json` + `package-lock.json` under `runtime/`.
      Verify: **the fixture's own Jest run** (`npm ci && npx jest --runInBand`) reports zero failures —
      a non-zero clean baseline voids the fixture, not the run.
      **Done (PR3a-i)** — three donor modules copied from the operator-authorized donor project (source
      identified only as "the donor project" per redaction instruction), chosen as a subset of the
      six-module set the case-count table (`applyKeypadInput` 15, `parseTokenAmount` 13, `confirmSeed` 12,
      `parseTransfers` 9, `formatTokenAmount` 8, `isValidEthereumAddress` 8 — the six highest-case
      import-free candidates, ~65 base cases total) implies for stage 2: `applyKeypadInput` (15 cases —
      intended root cause: a boundary/off-by-one condition in the decimal-cap or leading-zero check),
      `confirmSeed` (12 cases — intended root cause: an index/position-mapping defect between
      `CONFIRM_POSITIONS` and the picks array), `parseTransfers` (9 cases — intended root cause: a
      direction/fee-association mapping defect, e.g. case-sensitivity or fee-lookup keying). All three
      modules and their test files import nothing from each other or from any third module, so no PR4
      injection into one can shadow a signature in another. `parseTokenAmount` and `formatTokenAmount`
      were deliberately NOT both taken into this stage-1 subset even though both rank in the top six:
      `parseTokenAmount.test.ts` imports `formatTokenAmount` for one round-trip assertion, so an injection
      into `formatTokenAmount` would also fail a `parseTokenAmount` test — a real masking risk for
      whichever of PR3a-ii/PR4 assigns both of those two modules a root cause. Flagged here rather than
      discovered at the 4.1 isolation-validation gate.
      Redaction: every copied line read by hand before staging. One comment in `parseTransfers.ts`
      naming a specific third-party indexer product was genericized to "a token-transfers indexer
      endpoint" (conservative call — not the donor's own project/client/employer name, but not needed for
      the module's behavior either, so removed rather than argued over). No absolute path, project name,
      employer, person name, API key, or real-deployment contract address found in any copied byte;
      confirmed no `react`, `react-native`, `expo-*`, or MMKV import in any copied file (all three source
      modules and their tests are, and remain, import-free).
      Runtime: `runtime/package.json` pins `jest` 29.7.0, `ts-jest` 29.4.12, `typescript` 5.9.2,
      `@types/jest` 29.5.14, `@types/node` 20.19.9 (no `^`/`~` ranges); `runtime/package-lock.json`
      (`lockfileVersion: 3`) generated once via `npm install` in a machine-local scratch directory outside
      `<repo>`, never inside it. `runtime/jest.config.js` resolves `rootDir` and the `ts-jest` transform
      via `__dirname`/`require.resolve` rather than `process.cwd()`, so it works whether invoked from
      `runtime/` (`npm test`) or after `src/`+`tests/`+`runtime/` are later re-materialized elsewhere with
      the same relative layout — no `node_modules` symlink required for this fixture's own Jest run.
      Verified twice: (1) `npm install` + `npm test` in the scratch build directory; (2) the actual
      committed-tree bytes copied to a fresh `mktemp -d` directory outside `<repo>`, `npm ci` (fresh
      install from the committed lockfile), then `npx jest --config jest.config.js --runInBand` — **3
      suites, 36 tests, 0 failures, exit 0** both times. Cleaned up after; no `node_modules/` anywhere
      under `<repo>`, `.gitignore` unchanged.
      **MANIFEST.sha256 deliberately deferred, not silently skipped**: task 3.5 computes one manifest over
      `src/`, `tests/`, `runtime/`, `tools/`, `answer-key/case-table.sha256` **for both v1 and v2** — most
      of that path set (`tools/`, `answer-key/case-table.sha256`, and all of v2) does not exist yet after
      this task alone (3.2–3.4 pending). Freezing a manifest now would either omit paths 3.5 explicitly
      requires (a manifest that is not what 3.5 specifies) or force a second incompatible freeze once
      3.2–3.4 land. No `MANIFEST.sha256` is committed in this PR; task 3.5 remains the single point where
      it is computed, once, over the complete set it was designed to cover.
- [x] 3.2 Create `rig/fixtures/failure-flood/v2/{src,tests,runtime}/**` — stage-2 clean substrate, same
      six root-cause-hosting modules, same clean behavior as v1 where modules overlap.
      Verify: same Jest run, zero failures, on v2.
      **Done (PR3a-ii)** — v2 hosts all six root-cause-hosting modules. The three v1 modules
      (`applyKeypadInput` 15, `confirmSeed` 12, `parseTransfers` 9 — 36 base cases) are present as
      **byte-identical copies** (both `src/*.ts` and `tests/*.test.ts`; sha256 matched per file, not
      merely asserted) rather than re-derived from the donor a second time — this is the checkable
      reading of "same clean behavior as v1 where modules overlap": identical bytes cannot drift from
      v1's behavior, whereas a second hand-copy could silently diverge on a redaction edit or an
      import-path rewrite. v1 itself was not touched (`git diff` on `v1/` is empty before and after this
      task, confirming Design Decision 4 — a fixture change is a new version directory, never an edit to
      an existing one).

      **Correction to this task's own launch brief, verified rather than trusted**: `parseTokenAmount`
      (13 cases), named in the launch brief's case-count table as one of the "six highest-case
      import-free candidates," is disqualified per R-F1.1 — flagged already at PR3a-i, re-verified here
      by direct `import` grep on `parseTokenAmount.test.ts` as it exists in the donor project:
      `import { formatTokenAmount } from './formatTokenAmount'` at line 1, for one round-trip assertion.
      Taking both into the corpus would let an injection into `formatTokenAmount` also fail a
      `parseTokenAmount` test — the masking pair R-F1.1 exists to prevent. `parseTokenAmount` is excluded
      from the six; **the three added modules are `formatTokenAmount` (8 cases), `isValidEthereumAddress`
      (8), `balanceOfCall` (7)** — the three highest-case import-free candidates remaining after
      `parseTokenAmount`'s removal (the fourth candidate, `formatRelativeTime`, also 7 cases, was not
      needed once three were chosen; `balanceOfCall` was preferred over it for defect-class diversity —
      an encoding/hex-decoding defect surface distinct from `applyKeypadInput`'s boundary/off-by-one
      defect, whereas `formatRelativeTime`'s threshold logic would have been a second instance of the
      same defect class).

      **Base-case total is 59, not ~65 — reported, not silently absorbed.** The ~65 figure in this
      task's own launch brief and in PR3a-i's forward-looking arithmetic assumed `parseTokenAmount`'s 13
      cases were part of the eventual six; disqualifying it removes 13 cases, and the best available
      3-of-4 replacement from the remaining import-free candidates (`formatTokenAmount` 8,
      `isValidEthereumAddress` 8, `balanceOfCall` 7, `formatRelativeTime` 7 — max 3-of-4 sum is 23) adds
      back only 23, not 13. Six-module total: 36 (v1's three) + 23 (v2's three new) = **59 base cases**,
      a 6-case (9%) shortfall against the ~65 target. Consequence for task 3.3's per-module amplification
      target, flagged here for that task rather than fixed now (3.3 is out of scope for this batch): at
      the operator-confirmed ~40–46× multiplier, 59 base cases yields ~2,360–2,714 generated cases
      (~393–452:1 against 6 causes), versus the ~2,600–3,000 (~430–500:1) the corrected
      multiplier was set to reach assuming 65 base cases. Closing the gap without changing the module set
      again would need a multiplier of roughly **44–51×** at 59 base cases to land back in the
      ~2,600–3,000 range — task 3.3's own arithmetic, not decided here.

      Independence check, run on the copied set as actually copied (not assumed from the donor audit),
      **both directions**: (1) `rg -n "^import"` over all six `v2/src/*.ts` files — zero import lines;
      no source module depends on another, and none imports a test file. (2) `rg -n "^import"` over all
      six `v2/tests/*.test.ts` files — each imports exactly one thing, its own namesake module via
      `../src/<name>` (`applyKeypadInput`, `confirmSeed`, `parseTransfers`, `formatTokenAmount`,
      `isValidEthereumAddress`, `balanceOfCall`) — no test imports a sibling module. No masking pair
      exists among the six as committed.

      Redaction: all three new files (`formatTokenAmount.ts`, `isValidEthereumAddress.ts`,
      `balanceOfCall.ts`) and their three test files read by hand before staging. No donor project name,
      absolute path, employer, person name, API key, token, hostname, or real-deployment address found.
      `balanceOfCall.ts`'s `BALANCE_OF_SELECTOR` constant is the public ERC-20 `balanceOf(address)`
      selector (a standard, not a private value); `balanceOfCall.test.ts`'s `ADDRESS` constant is a
      synthetic hex string used only to exercise the encode/decode round-trip, not a real deployed
      contract or wallet address. Confirmed (grep, not assumed): zero `react`/`react-native`/`expo-*`/MMKV
      imports and zero donor-project-name/home-directory-path matches across the entire new `v2/` tree.

      Runtime: `v2/runtime/package.json` pins the identical versions as v1 (no `^`/`~`): `jest` 29.7.0,
      `ts-jest` 29.4.12, `typescript` 5.9.2, `@types/jest` 29.5.14, `@types/node` 20.19.9.
      `v2/runtime/package-lock.json` (`lockfileVersion: 3`) generated once via `npm install` in a
      `mktemp` directory outside `<repo>`. `v2/runtime/jest.config.js`/`tsconfig.json` are the same
      `__dirname`/`require.resolve`-based pattern as v1's, unchanged in shape.

      Verified twice, per ADR 0014 Clause A (never inside `<repo>`): (1) scratch build directory,
      `npm install` + `npm test` → 6 suites, 59 tests, 0 failures, exit 0. (2) the actual staged bytes
      copied to a second, fresh `mktemp -d` directory, `npm ci` (fresh install strictly from the
      committed lockfile) → 281 packages, `npx jest --config jest.config.js --runInBand` → 6 suites, 59
      tests, 0 failures, exit 0; re-ran via the committed `npm test` script → same. Both temp dirs removed
      after; no `node_modules/` anywhere under `<repo>`, `.gitignore` unchanged. Clean baseline — the
      fixture is not voided.

      Not built in this task (explicitly deferred to 3.3/3.4/3.5, not started): `tools/generate-cases.py`,
      the axis table, `answer-key/case-table.sha256`, `MANIFEST.sha256`.
- [x] 3.3 Create `tools/generate-cases.py` + its axis table (Decision 9a — commit the generator, not the
      expanded tables). **Per-module sizing (R-F9.2's design/tasks deliverable) — operator-confirmed
      2026-08-11; R-F9.2 still binds, so the achieved ratio MUST be measured, never assumed:**
      target amplification **~44–51×** each module's existing real case count, against a **measured base
      of 59** — not the 65 an earlier draft assumed, which still counted the disqualified
      `parseTokenAmount`. The v2 fixture's own Jest baseline reports exactly 59 tests, so the base is
      measured before the multiplier is chosen. Mirrors spec Decision B's worked examples
      (15 → ~660–765 rows, 12 → ~528–612), for an aggregate stage-2 corpus on the order of ~2,600–3,000
      generated failing cases across the 6 modules (≈433–500 : 1 against 6 causes — a stated comparison
      to the real incident's ~500:1, per R-F9.2, measured never assumed).
      No collector change is needed: its report ceiling is 64 MB against a 5–20 MB expected report.
      Verify: `python3 -m py_compile tools/generate-cases.py`;
      `tools/generate-cases.py --self-test` — byte-identical output across two runs **and** across two
      orderings of its input (no clock, no RNG, sorted keys, `\n` endings).
      **Done** — `rig/fixtures/failure-flood/v2/tools/{generate-cases.py,axis_table.py}` (v2 only; R-F9.1
      excludes stage-1 from amplification, so v1 gets no generator and its diff is confirmed empty).
      **Per-module achieved multiplier is uniformly ~48× (confirmSeed ~47.2×)**, all inside the
      operator-confirmed ~44–51× band: `applyKeypadInput` 15→720, `confirmSeed` 12→567, `parseTransfers`
      9→432, `formatTokenAmount` 8→384, `isValidEthereumAddress` 8→384, `balanceOfCall` 7→336. **Measured
      aggregate: 2,823 generated cases across 6 causes = ~470:1** — inside the target ~433–500:1 band,
      measured by actually running the generator, not computed by hand and assumed (R-F9.2).
      **Design question resolved, not assumed**: design.md 9a says amplification is consumed by "one
      `it.each` per module," but the v2 test files are the donor's own tests, not table-driven. Resolved
      by adding one `it.each` block per module (two for `balanceOfCall`, one per exported function) to the
      six existing `v2/tests/*.test.ts` files plus a shared `tests/_loadCases.ts` helper — legitimate
      inside PR3 per this task's own launch instruction, since v2 is not frozen until 3.5's MANIFEST.
      **Backward-compatibility hazard found and closed**: an unconditional `it.each` would have required a
      case table to exist for the already-verified clean-baseline `npm test` (PR3a-ii: 6 suites/59
      tests/0 failures) to keep passing, silently changing that recorded result. Closed by gating each
      block on `process.env.FAILURE_FLOOD_CASE_DIR`: `loadCases()` returns `[]` when unset, and each block
      is wrapped in `(cases.length > 0 ? describe : describe.skip)` rather than trusting `it.each([])`'s
      own undocumented empty-array behavior. Re-verified in a fresh `mktemp` outside `<repo>` (ADR 0014
      Clause A): no env var → 6 suites, **59 passed + 7 skipped = 66 total, 0 failures** (byte-identical
      base-case outcome to PR3a-ii); env var pointing at freshly generated tables → 6 suites, **2,882
      passed, 0 failures** (59 + 2,823, exactly the measured aggregate above) — proving the Python
      reference implementations agree with the real TypeScript clean logic on every one of 2,823 rows.
      **R-F9.1 ("real failures of real logic") verified empirically, not asserted**: deliberately widened
      `isValidEthereumAddress`'s regex to `{39,41}` in a throwaway scratch copy (never the committed tree)
      — 49 of the 392 base+amplified cases for that module then genuinely failed through the real
      TypeScript function, proving the amplified rows exercise real logic that a real injected bug would
      break, not synthetic assertions.
      **A determinism bug was found and fixed by the self-test itself, not by inspection**: the first
      `parseTransfers` builder derived `transactionHash` from a running loop counter and derived the
      paymaster `feeAmount` from the axis table's own list position — both are iteration-order-dependent,
      so reversing the axis table's lists produced different bytes even after canonical content-sorting.
      Fixed by deriving `tx_hash` from a `sha256` of the case's own field values, and `fee_amount` from a
      freshly-`sorted()` copy of the amounts list rather than the axis table's own order. Recorded as a
      finding because the same order-independence bug class ("uses a positional/loop-counter index instead
      of content") is easy to reintroduce in a future axis, and the fix pattern (derive identifiers from
      content, canonicalize before indexing) generalises.
      Redaction: no new absolute paths, donor names, or values beyond what PR3a-i/ii already cleared —
      `generate-cases.py`/`axis_table.py` contain only synthetic tokens (`w00`..`w23`), the same test-file
      addresses already committed in PR3a-ii, and formula-derived hex/integer values.
      `./hooks/pre-commit --all` → exit 0, "redaction check: clean across 153 tracked files".
      **Not built in this task** (explicitly deferred to 3.4/3.5, not started): `answer-key/case-table.sha256`,
      `MANIFEST.sha256`.
- [ ] 3.4 Commit `answer-key/case-table.sha256` — the expected digest of the generated output —
      **inside** the MANIFEST, so it cannot be edited to match a tampered generation (the ordering that
      carries the whole guarantee).
      Verify: tamper one generated byte at the per-run install site → digest compare → `exit 2`.
      Tamper the committed expected digest instead → MANIFEST mismatch → `exit 2` (both directions,
      because either alone leaves a hole).
- [ ] 3.5 Compute `MANIFEST.sha256` over the manifest's own path set — `src/`, `tests/`, `runtime/`,
      `tools/`, `answer-key/case-table.sha256` (not `prompts/`, `answer-key/` F0/R0/S0, or `prereg.json`
      — those land in PR4) for both v1 and v2. **Never a directory walk** — `run.sh:147`'s
      `find . -type f` would descend `node_modules`; the file list is built from the manifest's own
      path set, captured before the install symlink exists.
      Verify: accept-before (a check proceeds past the guard); unstaged byte tamper after freeze →
      `exit 2`; revert, tree clean.

## PR4 — Injections + measured answer-key (3b)

Depends on: PR3 (clean substrate + generator must exist first).

- [ ] 4.1 Inject the 3 stage-1 root causes into v1's `src/`. For each injection in isolation against the
      clean fixture, run `rig/collect.py` and confirm it produces its expected, frozen signature.
      Verify: an injection producing zero new failures is **rejected from the corpus** before any prompt
      exists (R-F1.2 scenario).
- [ ] 4.2 Freeze v1's `F0` (measured failure set), `S0` (measured suite state + signature), `R0`
      (root-cause label per member of `F0`, from the isolation validation in 4.1 — measured, never the
      declared injection list). Handle the masked-cause scenario: a shadowed cause is absent from the
      scoring key, not present-but-missed.
      Verify: `F0`/`R0`/`S0` committed under `answer-key/`, dated before `prompts/t*.txt` exists.
- [ ] 4.3 Repeat 4.1–4.2 for v2's 6 stage-2 root causes, injected through the same real modules the
      generator amplifies. Measure clusters-per-injection under amplification (design 9c) — a cause
      whose cluster count grows with `case_count` is a normalizer defect, not a key entry, and must be
      fixed in PR2 before this freezes, not absorbed into `R0`.
      Verify: per-injection isolation signature match, same as 4.1, on v2.
- [ ] 4.4 Commit `answer-key/prereg.json` — the frozen list of required hypothesis file paths — inside
      the MANIFEST (Hard Ordering Gate, layer 1).
      Verify: `./hooks/pre-commit --all`; MANIFEST accept-before / reject-tampered-after repeated for
      the full v1+v2 manifest (now covering `answer-key/` and `prompts/`-adjacent paths added since PR3).

## PR5 — `run-pipeline.sh` + surface preimage + `derive.py` dispatcher

Depends on: PR2 (collector), PR4 (answer-key + `prereg.json` must exist for preflight to check against).

- [ ] 5.1 Create `rig/run-pipeline.sh`. Preflight: manifest recompute-compare, `node`/`npm` presence +
      floor, lockfile digest, case-table digest, dirty-tree guard, pre-registration guard (Hard Ordering
      Gate layer 2) — any failure `exit 2`, before any run directory is claimed.
      Verify: `bash -n rig/run-pipeline.sh`.
- [ ] 5.2 Per-step materialize (fresh workspace per step, `node_modules` symlinked to a per-run
      machine-local install directory, never the committed tree), invoke, persist (`status.json`
      flushed before every exit path, including 1 and 2), read back surface + permission mode per
      invocation against the committed preimage.
      Verify (git repository selection): run from a different cwd and from a nested directory; both must
      stamp the same `code_commit`.
- [ ] 5.3 `--shakedown` flag: stamps `void_reason=shakedown` **unconditionally**, regardless of tree
      state (Hard Ordering Gate layer 1). `permission_mode` explicitly declared as a named argument,
      never inherited; recorded on the row; a run with no permission-mode argument refuses to start.
      Verify (commit state): stage a fixture edit → `exit 2`; repeat unstaged.
- [ ] 5.4 Capture `rig/surfaces/failure-flood.txt` (both arms need `Bash` + a write tool,
      `--strict-mcp-config` required) — captured **twice**, compared, then committed.
      Verify (subprocess argument composition): fixture path and prompt containing spaces, quotes, and
      non-ASCII run unchanged; `init.tools` still matches the preimage.
- [ ] 5.5 Detect the diagnostician-writes-to-`src/` violation (re-hash its workspace against its
      materialised file list; any change to `src/` → arm state `failed`, never `void`).
      Verify (agent-executed shell, new threat-matrix row): a deliberate case editing a test file, and
      one editing `package.json`; both must reach `regressed`/`failed`, never `green`.
- [ ] 5.6 Build the hashed file list from the manifest's own path set plus generated case paths,
      captured before the `node_modules` symlink exists.
      Verify (symlink traversal, new row): hashed file count equals manifest + case paths, with
      `node_modules` present.
      Verify (generated bytes entering a measured run, new row — distinct call site from PR3.4): tamper
      generated output mid-run → `exit 2`; tamper the expected digest → manifest mismatch → `exit 2`.
- [ ] 5.7 Run the actual `--shakedown` shakedown on the now-clean, now-committed tree.
      Verify: row stamps `void_reason=shakedown` unconditionally — the Hard Ordering Gate's own proof —
      and is excluded from every count.
- [ ] 5.8 Modify `rig/derive.py`: `--experiment` dispatcher, per-experiment registry (`runs root`,
      `fixture roots`, `run-id grammar`, `arm names`, row builder), `no-preregistration` void (Hard
      Ordering Gate layer 3).
      Verify: **re-run PR1's 42-row projection regression** — it must still pass unchanged after the
      dispatcher lands (design §6's stated reason for touching this file twice rather than duplicating
      it); `python3 -m py_compile rig/derive.py`; `./hooks/pre-commit --all`.

## PR6 — Hypotheses + `OPERATIONS.md` + `report.py` tables

Depends on: PR5 (the runner and its void machinery must exist for the hypotheses to be testable at
all). This is the PR that makes a countable run possible — see the Hard Ordering Gate above.

- [ ] 6.1 Create `hypotheses/0002-pipeline-shape-lowers-peak-occupancy.md` — statistical claim, exact
      support (median PIPELINE peak ≤ 0.5× median MONOLITHIC, non-overlapping ranges) **and** exact
      refute (ranges overlap, or PIPELINE's median ≥ MONOLITHIC's) conditions, per ADR 0012.
      Verify: structural readback — both conditions present, neither vague.
- [ ] 6.2 Create `hypotheses/0003-serial-triage-compounds-cumulative-tokens.md` — support (median
      PIPELINE cumulative ≤ 0.6× MONOLITHIC, non-overlapping) and refute (PIPELINE's median ≥
      MONOLITHIC's — a live possibility, stated as such) conditions.
      Verify: same structural readback.
- [ ] 6.3 Modify `OPERATIONS.md`: add the Node/npm/Jest prerequisites row (rig-only, fixture-only,
      `node_modules/` on demand, no `.gitignore` change needed), the missing GNU-compatible `timeout`
      row the table has been missing all along, and `collect.py --self-test` in the decision table.
      Verify: `./hooks/pre-commit --all`.
- [ ] 6.4 Modify `rig/report.py`: `--experiment` dispatcher, per-experiment arm names, four new
      **uncombined** tables — diagnostic precision/recall pair, green-restore verdict distribution, peak
      occupancy, cumulative occupancy. No composite score anywhere in the file (R-A1.3/R-F4.3).
      Verify: `python3 -m py_compile rig/report.py`; manual read of the file confirms no summed/ANDed
      field.
- [ ] 6.5 Modify `rig/README.md` (experiment axis becomes real; the two-schema rule; the fixture-runtime
      boundary, citing PR1's ADR) and `MAP.md` (experiment count).
      Verify: `./hooks/pre-commit --all` across the full tracked tree.
- [ ] 6.6 Confirm the Hard Ordering Gate closes: with `hypotheses/0002-*` absent (pre-PR6 state,
      re-checked against a throwaway copy), `run-pipeline.sh` must `exit 2` on any non-`--shakedown`
      invocation.
      Verify: this is the structural-impossibility proof named in the design's own verification
      strategy table — re-run once more after 6.1–6.2 land, confirming the same invocation now proceeds.
- [ ] 6.7 Register the **portable procedure** as a named downstream deliverable in `BACKLOG.md`: the
      collector → diagnostician → applier flow applied to a real failing suite outside this repo, which
      is the form the originating incident actually needs and which no artifact in this cycle names.
      Record it as **blocked**, with its unblock condition stated explicitly: the experiment's evidence
      must first be promoted into `theory/` carrying its scope and spread, per ADR 0011. **Do not write
      the block or skill in this cycle** — a procedure published before the measurement is a
      recommendation without magnitude, which is the fault `theory/agents/tool-surface-design.md`
      already carries and which this whole experiment exists to stop repeating. Note `blocks/` and
      `templates/` are currently empty and are its eventual home, per `MAP.md`'s description of `gaps/`
      as the demand signal for `blocks/`. `BACKLOG.md` is currently an empty file, so this task
      establishes its shape and must satisfy `AGENTS.md`'s frontmatter contract (`type: index`).
      Verify: `./hooks/pre-commit --all`; `MAP.md`'s area table still describes `BACKLOG.md` accurately.

## No-implementation, verification-only tasks

1.3, 1.4, 3.1 (Jest run only), 3.2 (Jest run only), 5.7, 6.6.

## Blocked tasks

None yet — the stack has not started. PR3 is blocked on PR1 (ADR) per R-F11's own scenario; PR5 is
blocked on PR4 (`prereg.json`/answer-key must exist for its preflight to check against); PR6 is the
gate that makes any countable run possible at all. No PR in this list may skip ahead of its dependency.
