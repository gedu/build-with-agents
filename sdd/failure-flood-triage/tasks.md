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
      aggregate: 2,823 GENERATED cases across 6 causes.**
      **CORRECTION 2026-08-12 — the "~470:1, inside the target band" this note originally claimed is
      NOT MEASURED and is very likely wrong by roughly eight times.** 2,823 is the count of generated
      cases; the ratio the experiment cares about is *failing* cases per cause, and a generated case only
      fails if it exercises an injected path. Two independent measurements put that yield near 12%:
      `v1/answer-key/s1.json` records 4 failures out of 36 tests, and this task's own R-F9.1 check
      recorded 49 failures out of 392 generated cases. At 12% the real figure is ~340 failures, i.e.
      ~57:1, not ~470:1. R-F9.2 requires the achieved ratio to be measured, so the generator's
      `--self-test` no longer prints a ratio at all — only generated counts. **Task 4.3 measures the real
      stage-2 failing count; the decision on how to close any gap waits for that number.**
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
- [x] 3.4 Commit `answer-key/case-table.sha256` — the expected digest of the generated output —
      **inside** the MANIFEST, so it cannot be edited to match a tampered generation (the ordering that
      carries the whole guarantee).
      Verify: tamper one generated byte at the per-run install site → digest compare → `exit 2`.
      Tamper the committed expected digest instead → MANIFEST mismatch → `exit 2` (both directions,
      because either alone leaves a hole).
      **Done — v2 only, by measured necessity, not by choice.** R-F9.1 excludes stage 1 from
      amplification ("Stage 1 = 10 failing cases / 3 root causes... excluded from the stage-2 test" —
      `spec.md:360`) and task 3.3's own done-note already recorded "v2 only... v1 gets no generator and
      its diff is confirmed empty" (`tasks.md:361-362`, this file). No generator means no generated
      output to digest, so v1 gets no `case-table.sha256` — stated here rather than silently created for
      symmetry.
      Added `case_table_digest(all_cases)` to
      `rig/fixtures/failure-flood/v2/tools/generate-cases.py` (26 lines: function + one `main()` print
      line) — computed from the in-memory serialized bytes, never a disk read-back, using the same
      combining convention `rig/run.sh`'s `hash_fixture_files` already uses for a set of files
      (`rig/run.sh:122-141`: sorted "sha256(bytes)  relpath" lines, one sha256 over the join) — reused,
      not invented, so a future consumer (`run-pipeline.sh` preflight, task 5.1) has one digest-of-a-
      file-set convention to implement, not two. The generator itself never writes into `<repo>` (ADR
      0014 Clause A holds); the printed digest was captured and hand-committed into
      `rig/fixtures/failure-flood/v2/answer-key/case-table.sha256`.
      **Measured, not assumed**: two independent `--out-dir` runs to separate `mktemp` directories
      produced the identical digest `b15b8d1698ea0b45e2c475c1d5c68e2dcac81458522771d724a3ca431e5becb1`
      (2,823 cases across 6 modules, matching task 3.3's measured totals) — this is the value committed.
      **Tamper proof, both directions, run on scratch copies only, real exit codes simulated from the
      real comparison (no `run-pipeline.sh` guard exists yet — PR5 — so the comparison itself, not a
      shell wrapper, is what is proven)**:
      (1) generated-byte direction — fresh `--out-dir` generation, untampered, digest-compare against
      the committed value: match, simulated exit **0**. One byte flipped in
      `cases/applyKeypadInput.json` at the per-run install site, same compare: mismatch, simulated exit
      **2**.
      (2) committed-digest direction — scratch copy of the whole `v2/` tree, untampered, MANIFEST
      recompute-compare (task 3.5's function) against the real committed `MANIFEST.sha256`: match, exit
      **0**. One hex character flipped in the scratch copy's `answer-key/case-table.sha256` (never the
      real committed file), same recompute-compare: mismatch, exit **2**.
      Real committed tree never touched by either tamper; `git status`/`git diff` on `v1/src`, `v2/src`
      empty throughout.
- [x] 3.5 Compute `MANIFEST.sha256` over the manifest's own path set — `src/`, `tests/`, `runtime/`,
      `tools/`, `answer-key/case-table.sha256` (not `prompts/`, `answer-key/` F0/R0/S0, or `prereg.json`
      — those land in PR4) for both v1 and v2. **Never a directory walk** — `run.sh:147`'s
      `find . -type f` would descend `node_modules`; the file list is built from the manifest's own
      path set, captured before the install symlink exists.
      Verify: accept-before (a check proceeds past the guard); unstaged byte tamper after freeze →
      `exit 2`; revert, tree clean.
      **Done.** Adapted `rig/run.sh`'s `compute_manifest()` (`rig/run.sh:154-171`: sorted "sha256(bytes)
      relpath" lines over a fixed subdirectory list, skipping any that do not exist) to the failure-flood
      path set — walk `src/`, `tests/`, `runtime/`, `tools/` plus the single file
      `answer-key/case-table.sha256` when it exists.
      **v1's real, actually-covered path set** (`tools/` and `answer-key/` do not exist for v1 — R-F9.1,
      see 3.4 above — so they are simply absent from the walk, never claimed): `runtime/` (4 files:
      `jest.config.js`, `package-lock.json`, `package.json`, `tsconfig.json`), `src/` (3: the v1 donor
      modules), `tests/` (3) — **10 files total**.
      **v2's real, actually-covered path set**: `answer-key/case-table.sha256` (1), `runtime/` (4),
      `src/` (6), `tests/` (7, including the shared `_loadCases.ts` helper), `tools/` (2:
      `axis_table.py`, `generate-cases.py`) — **20 files total**.
      **Hazard found and closed, not assumed away**: a bare `d.rglob("*")` over `tools/` would pick up
      `tools/__pycache__/*.pyc` — confirmed present on disk from running the generator/self-test
      (`.gitignore:24-25`: `__pycache__/`, `*.pyc`; `git ls-files rig/fixtures/failure-flood/v2/tools/`
      returns only the two real `.py` files). Machine-specific, Python-version-named bytecode entering a
      frozen manifest would make it disagree on a fresh clone with a different Python build. Closed by
      an explicit skip: `if "__pycache__" in p.parts or p.suffix == ".pyc": continue` — the same
      "manifest path set, never a directory walk" principle this task already names for `node_modules`,
      applied to the one other ignored, generated directory this fixture happens to have.
      **Verify, on the real committed tree, real exit codes**: for both v1 and v2, accept-before (fresh
      recompute over the real tree equals the just-written `MANIFEST.sha256`) → exit **0** for both.
      Then one byte flipped in a real tracked file (`v1/src/applyKeypadInput.ts`,
      `v2/src/balanceOfCall.ts`, unstaged) → recompute mismatches the committed manifest → exit **2** for
      both. Reverted immediately (original bytes restored) → recompute matches again for both;
      `git status --porcelain` / `git diff --stat` on `v1/src` and `v2/src` empty throughout — the tree
      was never actually left dirty.

**PR3 apply-time finding, recorded rather than silently built around:** `design.md`'s own "File changes"
table row for `rig/fixtures/failure-flood/v1/{src,tests,runtime,tools,prompts,answer-key}/**`
(`design.md:584`) and its dedicated row `…/v1/tools/generate-cases.py` + its axis table (`design.md:585`,
"Create") both claim v1 gets a `tools/` generator. This contradicts **R-F9.1** ("Stage 1 = 10 failing
cases / 3 root causes... excluded from the stage-2 test" — `spec.md:360`) and task 3.3's own already-
recorded done-note ("`v2 only`... v1 gets no generator and its diff is confirmed empty" — this file,
lines 361-362 at time of that task). Verified again here directly: `rig/fixtures/failure-flood/v1/`
has no `tools/` directory on disk (`ls` confirms only `runtime/`, `src/`, `tests/`), so v1's real
MANIFEST path set above (10 files, no `tools/`, no `answer-key/`) is correct against R-F9.1 and wrong
against `design.md:584-585`'s literal text. This is a `design.md` documentation error, not an
implementation gap — the spec's own staging decision (R-F9.1) is authoritative and was followed; the
design table row is stale from before that exclusion was worked out. Not fixed in this apply (design.md
edits are out of this phase's scope), flagged here as this cycle's convention requires.

## PR4 — Injections + measured answer-key (3b)

Depends on: PR3 (clean substrate + generator must exist first).

- [x] 4.1 Inject the 3 stage-1 root causes into v1's `src/`. For each injection in isolation against the
      clean fixture, run `rig/collect.py` and confirm it produces its expected, frozen signature.
      Verify: an injection producing zero new failures is **rejected from the corpus** before any prompt
      exists (R-F1.2 scenario).
      **Done.** Ambiguity resolved before implementing, with quotes (not guessed): design.md:455
      ("MONOLITHIC's workspace is the injected `src/`...") and design.md:584 (v1's file-changes row
      names "injections... (3b)" against the `{src,tests,runtime,prompts,answer-key}/**` path set
      itself) both show the injected bytes are the committed `src/`, not a descriptor applied to a copy
      — there is no generator/patch layer for v1 (R-F9.1, task 3.3's done-note). "Clean" is preserved via
      git history (the PR3a-i commit) and a scratch backup taken before injecting, reproduced fresh
      before each of the 3 isolation runs below — not a one-time claim. The three intended causes
      recorded at PR3a-i (`apply-progress.md:221-226`) were re-verified against the current source and
      confirmed still correct: `applyKeypadInput`'s decimal-cap boundary, `confirmSeed`'s
      `CONFIRM_POSITIONS`/`picks` index mapping, `parseTransfers`'s direction/fee-association mapping.
      **Isolation (mktemp scratch outside `<repo>`, ADR 0014 Clause A), one at a time, reverted to clean
      between each, `rig/collect.py` against real `npx jest` output**: (1) `applyKeypadInput.ts:28`
      (`>=`→`>` in the decimal-cap comparison) — 1 failure, signature `277580d674667852`. (2)
      `confirmSeed.ts:15` (`isPickCorrect(seed, position, pick)`→`isPickCorrect(seed, index, pick)`) — 1
      failure, same signature `277580d674667852` (Jest's generic `.toBe` equality head, no distinguishing
      text before the Expected:/Received: cut — see 4.2's masking finding). (3) `parseTransfers.ts:34`
      (`account.toLowerCase()`→`account`, losing the case-insensitive compare) — 2 failures, signatures
      `277580d674667852` and `2df32737777805ca`. None produced zero new failures, so none was rejected.
- [x] 4.2 Freeze v1's `F0` (measured failure set), `S0` (measured suite state + signature), `R0`
      (root-cause label per member of `F0`, from the isolation validation in 4.1 — measured, never the
      declared injection list). Handle the masked-cause scenario: a shadowed cause is absent from the
      scoring key, not present-but-missed.
      Verify: `F0`/`R0`/`S0` committed under `answer-key/`, dated before `prompts/t*.txt` exists.
      **Done.** Committed `rig/fixtures/failure-flood/v1/answer-key/s1.json` (task_id `s1`, design.md:368)
      — `C`, `F0`, `S0`, `R0`, and a `measured_vs_declared` section. Measured on a fresh `mktemp` copy of
      the real committed (post-injection) `src/`+`tests/`+`runtime/` bytes, `npm ci`, `npx jest
      --runInBand`, `rig/collect.py`: **suite_state=ran, 4 failed / 32 passed / 36 total, 2 distinct
      clusters** (`c1` count 3, `c2` count 1). No `prompts/` directory exists yet, so the commit-order
      requirement holds vacuously true.
      **R-F1.1 masking, measured not declared, reported rather than tuned away**: all 3 injected causes
      remain independently observable (none rejected at 4.1), but injected TOGETHER they collapse to only
      **2 distinct cluster signatures, not 3** — `applyKeypadInput.ts:28`, `confirmSeed.ts:15` and
      `parseTransfers.ts:34`'s "matches...case-insensitively" failure all normalize to the identical
      signature `277580d674667852` because their first-reported message is Jest's generic
      `expect(received).toBe(expected) // Object.is equality` head with nothing distinguishing before the
      normalizer's Expected:/Received: cut (`rig/collect.py`'s `normalize_signature_text`). This is a
      different masking mode than R-F1.1's own worked scenario (one cause shadowing another inside the
      SAME test) — here three unrelated causes across three different modules and tests share one cluster.
      The diagnostician's bounded `clusters` view (design.md 9b) drops `member_test_ids`, so cluster `c1`
      is presented as one representative test (`applyKeypadInput`'s) with `count=3`, with no signal that
      two other, unrelated causes also produced members of it. Not adjusted to avoid this — R-F1.1
      explicitly forbids tuning injections away from a measured collision — recorded in `s1.json`'s
      `measured_vs_declared.finding` instead; `R0` still lists each cause's real `cluster_ids`
      individually so grading against the exact `<path>:<line>` site (never the cluster id alone) stays
      sound.
      **Stage-1 target vs. measured, honestly not tuned**: R-F9.1 states the shakedown target as "10
      failing cases / 3 root causes." The real measured total is **4 failing cases**, not 10: isolation
      measured 1 + 1 + 2 = 4 (not the naive additive worst case, and no reduction from masking either,
      since every isolated failure survived into the combined run — the masking above reduces distinct
      *clusters*, not distinct *failing tests*). The gap is structural, not an implementation shortfall:
      `applyKeypadInput`'s and `confirmSeed`'s test suites each have exactly one test pair that brackets
      the injected boundary (2 tests probing the decimal cap; `isConfirmCorrect`'s 4 tests, 3 of which
      already return `false` for an unrelated reason — a null pick or a wrong word — so `Array.every`
      short-circuits at index 0 before the position bug is ever exercised in those 3). No alternative
      off-by-one variant explored for either module (several were tried, see this journal's PR4 section
      in `apply-progress.md`) breaks more than 1 test in isolation, for the same structural reason in
      each case. Reported as measured; not tuned to reach 10.
      **MANIFEST recompute, deliberate, reason quoted**: task 3.5's own done-note (`tasks.md:441`)
      already deferred `answer-key/` `F0`/`R0`/`S0` "to PR4" — recomputing here is that deferred step, not
      scope creep. `rig/fixtures/failure-flood/v1/MANIFEST.sha256` recomputed (`runtime/`, `src/`,
      `tests/`, `answer-key/`, no `tools/` — none exists for v1) since `src/` bytes changed (the
      injections) and `answer-key/s1.json` is new; the old MANIFEST, computed over the pre-injection
      clean bytes, would otherwise mismatch on the very first recompute-compare. Verified accept-before
      (fresh recompute over the real committed tree matches the just-written manifest, exit 0), then
      tamper-proof in both directions on the real tree, reverted immediately each time: (1) one tracked
      byte appended to `src/applyKeypadInput.ts` → mismatch, exit 2 → restored from a saved copy → match,
      exit 0. (2) one hex character flipped in the committed `MANIFEST.sha256` itself → mismatch, exit 2
      → restored from a saved copy → match, exit 0. `git diff --stat` on both paths empty after each
      restore.
      **Process note, recorded rather than hidden**: mid-verification, `git checkout --
      src/applyKeypadInput.ts` was run before that file had been staged, which reverted it to the
      pre-injection committed state (not to the injected state intended) — a real mistake, not a
      simulated one. Caught immediately by `git status`/`git diff`, the injection was re-copied from the
      scratch working copy, `git add` run immediately afterward so the index always holds the intended
      injected bytes before any further `git`-history-touching command, and the MANIFEST recompute-compare
      re-verified match (exit 0) afterward. No corruption reached the reported `F0`/`S0`/`R0` (those were
      measured from an independent, already-saved `mktemp` verification copy taken before the mistake).
      **[x] Correction, PR4-signature-scope-fix (this batch), applied on top of the above rather than
      redone from scratch**: the masking measured at 4.2 (3 unrelated causes across 3 modules collapsing
      into 1 cluster) was a real, previously-unhandled over-collapse defect in `rig/collect.py`'s
      signature, not an accepted masking outcome — closed by scoping the signature to
      `hash(normalized_head + test_file)` (spec R-F1.4, `NORMALIZER_VERSION` 1 -> 2). v1's `src/`
      injections are byte-unchanged (`git diff --stat` on `v1/src`, `v1/tests`, `v1/runtime` empty);
      `answer-key/s1.json`'s `F0`/`R0`/`measured_vs_declared` and `MANIFEST.sha256` were re-measured and
      rewritten under the corrected normalizer. **Re-measured: 4 failing cases (unchanged), now 4
      distinct clusters (not 2)** — `applyKeypadInput.ts:28` -> `c2`, `confirmSeed.ts:15` -> `c3`,
      `parseTransfers.ts:34` -> `c1`+`c4` (that cause's own two-heads over-split is unchanged from the
      original measurement and remains absorbed by `R0`'s many-to-one mapping, design.md:449-450 —
      over-split was never the defect being fixed). Same-module clustering re-verified, not assumed: two
      new `collect.py --self-test` cases (g.1/g.2) prove identical heads in the same file still cluster
      together while identical heads in different files no longer do; `parseTransfers`'s own two isolated
      failures, re-run in isolation, reproduced the exact same two signatures (`04933d1bde59e977`,
      `da54112bb72162e0`) as inside the combined run. `spec.md` (new R-F1.4) and `design.md` (algorithm
      item 4b, 9c) amended in place to record the scope correction with the measured evidence, keeping the
      original over-split reasoning rather than replacing it. Full detail in
      `apply-progress.md`'s "PR4-signature-scope-fix" section.
- [x] 4.3 Repeat 4.1–4.2 for v2's 6 stage-2 root causes, injected through the same real modules the
      generator amplifies. Measure clusters-per-injection under amplification (design 9c) — a cause
      whose cluster count grows with `case_count` is a normalizer defect, not a key entry, and must be
      fixed in PR2 before this freezes, not absorbed into `R0`.
      Verify: per-injection isolation signature match, same as 4.1, on v2.
      **Done.** Six causes injected into the COMMITTED `v2/src/`: `applyKeypadInput.ts:28` (`>=`→`>`,
      reused from v1), `confirmSeed.ts:15` (`position`→`index`, reused), `parseTransfers.ts:34` (dropped
      `.toLowerCase()`, reused), `formatTokenAmount.ts:23` (`decimals - 2`→`decimals - 1`, new),
      `isValidEthereumAddress.ts:1` (`{40}`→`{41}`, new), `balanceOfCall.ts:3` (`ADDRESS_PADDING` 64→63,
      new). Each validated in isolation, both without and with generated cases loaded — all six produced
      non-zero failures (none rejected under R-F1.2); isolated failing sums (11 without cases, 499 with)
      are exactly equal to the combined run's totals, confirming no masking (this fixture's modules are
      import-free by construction).
      **Real measured numbers, each with its command** (`rig/collect.py --cwd <runtime> --report-file …
      --collection-output … --clusters-output … --expected-suites 6`, optionally
      `FAILURE_FLOOD_CASE_DIR=<cases-dir>`): 59-test base (no case tables) → **11 failing / 66 total**, 8
      clusters. Full amplified corpus (2,823 generated + 59 base = 2,882 tests) → **499 failing / 2,882
      total**, 9 clusters. Yield = 499/2882 = **17.31%**. Achieved ratio = **499:6 (~83.2:1)**, NOT the
      spec's ~433–500:1 order of magnitude — measured, not reached; no injection or axis value was tuned.
      **Two real normalizer defects found and fixed in `rig/collect.py`, both anticipated by
      `tasks.md`'s own instruction above and `design.md:711`'s threat matrix**: (1) the Expected:/Received:
      cut only matched Jest's unprefixed scalar summary line, never its diff-prefixed structural form
      (`- Expected  - N`/`+ Received  + N`) — measured on `parseTransfers`: 146 failing cases → 146
      clusters (cluster count growing 1:1 with `case_count`, exactly the defect this task names) before
      the fix, 3 after. `NORMALIZER_VERSION` 2→3; self-test case (h), both directions. (2) `workspace_root
      = os.path.abspath(cwd)` does not resolve symlinks, leaking an absolute host path into
      `test_id`/`signature` when the scratch workspace lived under a symlinked path (macOS `/tmp` →
      `/private/tmp`) — fixed to `os.path.realpath(cwd)`; self-test case (i), both directions; no version
      bump (path-resolution robustness, not an algorithm change). `v1/answer-key/s1.json` was re-measured
      and rewritten under the same version-3 fix in this work unit (only `c4`'s signature value changed,
      from the `.toMatchObject` failure; same 4 failures, same cluster count, same `identifier_set_digest`)
      rather than left silently stale, and `v1/MANIFEST.sha256` recomputed — `v1/src`, `v1/tests`,
      `v1/runtime` remain byte-unchanged throughout (`git diff --stat` empty).
      **`F0` shape, resolved with quotes, not invented**: `design.md:241` calls `failure/1` "deliberately
      minimal... at amplified scale there are thousands of these" — licensing a per-failure list. A first
      attempt wrote all 499 entries (1,309 lines, pushing the whole unit's authored total to ~1,499 against
      the 700 ceiling) and was rejected as unreviewable. A second attempt used `collection/1`'s own
      `clusters` field, which itself carries `member_test_ids` (815 lines — still over, for an unrelated
      reason). Final: `F0.clusters` is the bounded `clusters/1` view (`design.md` 9b: "bounded by CLUSTER
      count, never by failure count") collect.py's own `clusters_view()` already produces — 9 entries, no
      `member_test_ids`. `design.md:711`'s own amplification-safety freeze is explicitly "clusters-per-
      injection... in R0", not a failure enumeration; `S0.identifier_set_digest` remains the integrity
      proof for the exact 499-test_id failing set without enumerating it. `answer-key/v2/s2.json`: 298
      lines. `MANIFEST.sha256` recomputed for both v1 and v2, accept-before and tamper-proof both
      directions confirmed (exit 0 / exit 2), real committed tree untouched after each revert.
      **Line counts**: `git diff --cached --numstat` — `rig/collect.py` 153+9, `v1/MANIFEST.sha256` 1+1,
      `v1/answer-key/s1.json` 8+8, `v2/MANIFEST.sha256` 7+6, `v2/answer-key/s2.json` 298+0, six `v2/src/*.ts`
      1+1 each (×6=12). Raw total = 162+2+16+13+298+12 = **503**. Generated-golden exclusion
      (`sdd-phase-common.md:104`): both `MANIFEST.sha256` files only (2+13=15) — `s1.json`/`s2.json` are
      NOT excluded, same reasoning as PR4-i/PR4-signature-scope-fix (hand-assembled from real measured
      output). Authored total = 503 − 15 = **488**, inside the 700 ceiling.
      Verify: `python3 -m py_compile rig/collect.py` exit 0; `rig/collect.py --self-test` exit 0, all 15
      cases PASS (a, b, c.1–c.4, d, e, f, g.1, g.2, h.1, h.2, i); `./hooks/pre-commit` (staged) exit 0;
      `./hooks/pre-commit --all` exit 0 ("redaction check: clean across 158 tracked files"). Nothing
      committed or pushed — staged only.
- [x] 4.4 Commit `answer-key/prereg.json` — the frozen list of required hypothesis file paths — inside
      the MANIFEST (Hard Ordering Gate, layer 1).
      Verify: `./hooks/pre-commit --all`; MANIFEST accept-before / reject-tampered-after repeated for
      the full v1+v2 manifest (now covering `answer-key/` and `prompts/`-adjacent paths added since PR3).
      **Done.** `answer-key/prereg.json` committed to **`v2/answer-key/` only**, not v1 — scope decided
      with quotes, not assumed. Design.md section 8: "Stage 2 (50 cases, 6 causes, the comparison) is
      `task_id: s2` on `failure-flood/v2`" is the only run type the Hard Ordering Gate's layer 2
      non-shakedown check ever gates; R-F9.1 ("Stage 1 = 10 failing cases / 3 root causes, shakedown,
      excluded from the stage-2 test") plus task 5.7 ("Run the actual `--shakedown` shakedown on the
      now-clean, now-committed tree") establish that `task_id: s1` (v1) is structurally always invoked
      with `--shakedown`, so the tasks.md Hard Ordering Gate's own wording — layer 2 "separately refuses
      (`exit 2`) any **non**-shakedown invocation unless `hypotheses/0002-*.md` and `hypotheses/0003-*.md`
      exist... (frozen list in `answer-key/prereg.json`, inside the MANIFEST)" — never executes its
      non-shakedown branch against v1's fixture root. Putting the file there too would be dead weight
      with zero functional purpose. Task 3.5's earlier parenthetical ("not `prompts/`, `answer-key/`
      F0/R0/S0, or `prereg.json` — those land in PR4) for both v1 and v2") was read closely: "for both v1
      and v2" grammatically modifies the *excluded-from-PR3* clause (neither fixture's PR3 manifest
      covered these paths yet), not a claim that every named path duplicates onto both fixtures at PR4 —
      `F0`/`R0`/`S0` already landed as `s1.json` (v1 only) and `s2.json` (v2 only), never duplicated, and
      `prereg.json` follows the same per-fixture-as-needed pattern.

      **`prereg.json`'s shape, designed and justified** (`rig/fixtures/failure-flood/v2/answer-key/prereg.json`,
      36 lines): `schema: "prereg/1"`; `required_hypotheses` is a list of `{id, path_root, path_glob,
      topic_hint}` entries — one per hypothesis (`0002`, `0003`) — using the **glob** form
      (`hypotheses/0002-*.md`, `hypotheses/0003-*.md`) verbatim from the Hard Ordering Gate's own wording
      and R-F8.1's citation, not the exact literal filenames PR6 (tasks 6.1/6.2) already commits to.
      Reasoned choice: hardcoding the literal final filename would force re-touching this
      already-manifest-frozen file if PR6 ever refines its topic slug; the glob freezes the *count and
      numeric-prefix requirement* (which is what design.md section 7's table row — "the list of required
      hypothesis files cannot be quietly shortened" — is actually protecting), and the exact final
      filenames are carried only as non-binding `topic_hint` documentation. A `check` block spells out the
      exact preflight semantics PR5 must implement without re-deriving them from prose:
      `must_match_exactly_one_file_per_entry`, `must_exist`, `must_be_git_tracked`, `must_be_clean`, with
      one named `exit 2` reason per violation class (`zero_matches`, `more_than_one_match`,
      `tracked_but_dirty`, `untracked`). A `scope` block records the v1/v2 decision above inline, in the
      file itself, so PR5's author does not have to re-derive the same reasoning from this journal.

      **Layer 1 demonstrated as refusing TODAY, without executing PR5's not-yet-written preflight**: `git
      ls-files hypotheses/` on the real repository lists only `hypotheses/README.md` and
      `hypotheses/0001-broad-surface-degrades-output-not-selection.md` — no file matching
      `hypotheses/0002-*.md` or `hypotheses/0003-*.md` exists yet, tracked or otherwise. A correct
      preflight implementing `prereg.json`'s `check` block against this real tree would evaluate
      `required_hypotheses[0]`'s glob (`hypotheses/0002-*.md`) to **zero matches** and, per the file's own
      `zero_matches: "exit 2"` rule, refuse before any run directory is claimed — precisely the
      structurally-impossible-until-PR6 state the Hard Ordering Gate is designed to produce. This is
      stated as what a correct implementation returns and why, not claimed as executed, since PR5's
      `run-pipeline.sh` does not exist yet (depends-on note above this PR).

      **MANIFEST verification, real exit codes, both fixtures, both tamper directions** (recompute
      algorithm: `rig/run.sh:154-171`'s adapted `compute_manifest()`, walking `src/, tests/, runtime/,
      tools/, answer-key/`, skipping `__pycache__`/`.pyc`, unchanged from task 3.5 — re-derived from the
      committed script, not from prose):
      - Accept-before: v1 recompute vs committed `MANIFEST.sha256` → **exit 0**. v2 recompute vs staged
        `MANIFEST.sha256` (now including the new `answer-key/prereg.json` line) → **exit 0**.
      - Direction 1 (tamper a covered file → recompute mismatch): v1 — appended a line to
        `src/applyKeypadInput.ts` → **exit 2**; reverted (`git checkout --`) → **exit 0**. v2 — appended a
        line to the newly-added `answer-key/prereg.json` → **exit 2**; reverted (`git checkout --`,
        restoring the already-staged blob) → **exit 0**, digest byte-identical to the pre-tamper file
        (`ef0a578a...`).
      - Direction 2 (tamper the MANIFEST's own expected digest → recompute mismatch): v1 — flipped one
        hex character in `MANIFEST.sha256`'s `src/applyKeypadInput.ts` line → **exit 2**; restored from
        backup → **exit 0**. v2 — flipped one hex character in `MANIFEST.sha256`'s new
        `answer-key/prereg.json` line → **exit 2**; restored from backup → **exit 0**.
      - Real committed/staged tree never left dirty by any tamper: `git diff` (worktree vs index) on both
        fixtures empty after every revert; `git diff --cached --stat` shows exactly the two intended
        files (`v2/MANIFEST.sha256` +1, `v2/answer-key/prereg.json` +36, 37 insertions total); explicit
        confirmation that `v1/src`, `v1/tests`, `v1/runtime`, `v2/src`, `v2/tests`, `v2/runtime`,
        `v1/answer-key/s1.json`, `v2/answer-key/s2.json` carry **zero** staged diff.
      - `./hooks/pre-commit` (staged) — see line-count/exit-code summary below.

      **Line counts, both stated with their command** (`git diff --cached --numstat`, taken as the final
      snapshot after this addendum and the paired `apply-progress.md` append were both staged — see the
      apply-progress entry for this task for the exact numstat output): fixture files —
      `v2/MANIFEST.sha256` 1+0; `v2/answer-key/prereg.json` 36+0. Journal/task-file diffs, counted per
      this unit's own ceiling instruction (only generated goldens are excluded, not journal/task-file
      diffs) — `sdd/failure-flood-triage/tasks.md` and `sdd/failure-flood-triage/apply-progress.md`, both
      reported with the final `git diff --cached --numstat` in the return summary rather than restated
      here (this sentence is itself part of that diff, so a number frozen at write time would be stale by
      the time the diff is actually taken). Fixture-only authored subtotal, generated-golden exclusion
      (`sdd-phase-common.md:104`) applied to `MANIFEST.sha256`'s single inserted digest line: (1+36) − 1 =
      **36**, well inside the 700 ceiling on its own; journal/task-file lines add on top per this unit's
      instruction, final total given with its command in the return summary.

      **PR4 closes with this task. Nothing left inconsistent inside PR4 itself** — tasks 4.1–4.4 all
      `[x]`, `s1.json`/`s2.json`/`prereg.json` all committed (staged) and manifest-covered for their
      respective fixtures. One pre-existing note carried forward, not introduced by this task: task
      3.5's own apply-time finding that `design.md:584-585`'s "File changes" table row still claims v1
      gets a `tools/generate-cases.py` (contradicted by R-F9.1 and confirmed on disk to be a stale
      `design.md` documentation error) remains unfixed — out of this phase's scope, flagged again for
      whichever PR next touches `design.md`. PR5 depends on this task's `prereg.json` existing and being
      correct for its own preflight (task 5.1) to check against; PR6 depends on PR5.

## PR5 — `run-pipeline.sh` + surface preimage + `derive.py` dispatcher

Depends on: PR2 (collector), PR4 (answer-key + `prereg.json` must exist for preflight to check against).

- [x] 5.1 Create `rig/run-pipeline.sh`. Preflight: manifest recompute-compare, `node`/`npm` presence +
      floor, lockfile digest, case-table digest, dirty-tree guard, pre-registration guard (Hard Ordering
      Gate layer 2) — any failure `exit 2`, before any run directory is claimed.
      Verify: `bash -n rig/run-pipeline.sh`.
      **Done — this batch (PR5a, tasks 5.1/5.2/5.3/5.6 only; not 5.4/5.5/5.7/5.8), full detail and every
      real exit code in `apply-progress.md`'s "PR5a" section.** `bash -n` exit 0. Live, real adversarial
      runs (never `--self-test` — ADR 0014 Clause B excludes this file): non-shakedown `s2` invocation
      today → **exit 2**, naming the exact fired reason `zero_matches: hypotheses/0002-*.md`; a real byte
      tamper on `v1/src/applyKeypadInput.ts` (reverted after) → MANIFEST mismatch → **exit 2**.
      **Two real bugs found and fixed by this same live testing, not asserted from code review**: (1)
      `compute_manifest()`'s first draft walked only `answer-key/case-table.sha256` per task 3.5's own
      done-note — true only at that task's moment; the real, current committed `v2/MANIFEST.sha256`
      covers the whole `answer-key/` directory (task 4.2/4.4 added `s1.json`/`s2.json`/`prereg.json`
      since). Live recompute-compare against the real committed manifest mismatched by exactly those 2
      lines; fixed to walk `answer-key/` like `src/tests/runtime/tools`, re-verified MATCH for both v1 and
      v2. (2) `npm ci --prefix <dir>` (run from a different cwd) is NOT `cd <dir> && npm ci` — it resolves
      the root package against the CALLER's cwd, failing EUSAGE against `<repo>`'s own absent
      `package.json`. Fixed to `cd` into the install dir first.
- [x] 5.2 Per-step materialize (fresh workspace per step, `node_modules` symlinked to a per-run
      machine-local install directory, never the committed tree), invoke, persist (`status.json`
      flushed before every exit path, including 1 and 2), read back surface + permission mode per
      invocation against the committed preimage.
      Verify (git repository selection): run from a different cwd and from a nested directory; both must
      stamp the same `code_commit`.
      **Done.** Live: run from `v1/src` (a nested directory) and from `/tmp` (a different cwd) both stamp
      the identical `code_commit`. Materialize/invoke/persist proven live end-to-end for a real CODE step
      (pipeline arm's `01-collect`, no `claude` call needed): real `npm ci`, real `tools/generate-cases.py`
      run, a real `rig/collect.py` invocation against the actually-committed, already-injected `v2/src` —
      reproduced task 4.3's own recorded measurement exactly (**499 failed / 2,882 total, 9 clusters**).
      Surface+permission-mode read-back is RECORDED per invocation (`surface_sha256`,
      `permission_mode_actual`) but the void-decision is left to `derive.py` (task 5.8), matching
      `rig/derive.py:456-464`'s existing split for `tool-surface-v1` (never `rig/run.sh`) — a design choice,
      not an oversight, recorded with its citation in the file's own comment.
      **A third real bug found and fixed by live testing**: calling a function that `return`s non-zero as a
      bare statement under `set -e` aborted the whole script silently, skipping the arm-level status write
      entirely (a live Amendment-1 violation, caught by the FIRST live run producing an empty `arm.json`).
      Fixed: the abort-signalling functions now always `return 0` and communicate via the `ABORT_REASON`
      global, checked explicitly after the call.
      **Untestable within this unit, and why**: an actual model-step `claude -p` invocation. `prompts/`
      does not exist under either fixture (no PR3/PR4 task created it — a design.md-vs-disk gap, same
      class as the v1 `tools/` finding at task 3.5) and `rig/surfaces/failure-flood.txt` is task 5.4's own
      deliverable. Live testing reaches exactly this boundary and dies with `missing-prompt`/
      `missing-surface-preimage` (exit 2), both traced to their real, named cause.
- [x] 5.4b Create `prompts/` under both `failure-flood` fixtures, one `.txt` per `task_id` (`s1`, `s2`),
      and add those paths to each MANIFEST. **A planning gap, found live at PR5a and recorded so it does
      not evaporate:** `design.md`'s file-changes table names `prompts/` among the paths each fixture
      creates, but no PR3 or PR4 task ever created it, and `fd -t d prompts rig/fixtures` returns only
      `tool-surface/v1` and `tool-surface/v2`. This is the same class as the stale `tools/`-under-v1 row
      already corrected at task 3.5 — the table described a path set the task list never delivered.
      It blocks 5.7: no model step can run without a prompt, and it must not be worked around with a
      scratch file, since that would let a real invocation proceed outside a frozen fixture.
      `prompts/` is a **never-materialised** path (design 9a), so the prompt bytes reach the agent through
      the invocation, never through its workspace. Answer-key commits must land BEFORE the prompt commit,
      so "checker-first" stays provable from commit order — the convention `rig/fixtures/tool-surface`
      already follows.
      Verify: `./hooks/pre-commit --all`; both manifests recompute-compare clean; `run-pipeline.sh`'s
      `missing-prompt` abort no longer fires for `s1`/`s2`.
      **Done.** Real topology conflict resolved, not assumed: `run_model_step()` (PR5a) resolved the
      prompt path by **role** (`prompts/${role}.txt`, i.e. `monolith.txt`/`diagnose.txt`/`apply.txt`),
      contradicting this task's own "(`s1`, `s2`)" instruction — corrected to
      `prompts/${TASK_ID}.txt`, the exact naming `rig/run.sh:306` already uses. One task_id, one file,
      loaded byte-identical for every role in both arms — the strongest form of ADR 0010's "harness
      shape is the only variable": the prompt hash cannot differ across roles because the bytes are the
      single committed file, never composed per role. `prompts/s1.txt`/`prompts/s2.txt` written
      (identical content, verified `diff` empty, same sha256) describing the generic triage task and
      `spec.md` R-F3.1's exact `root-cause-report.txt` deliverable format (quoted verbatim in the prompt
      body), plus an optional `fix-plan.txt` handoff clause that serves PIPELINE's `diagnose`/`apply`
      roles without needing role-specific prompt text. `compute_manifest()`'s subdirectory tuple gained
      `prompts` (it omitted it even though design.md 9a groups `prompts/` with the already-covered
      `tools/`/`answer-key/`) — without this, the new files would be invisible to the manifest gate
      entirely. Both MANIFEST.sha256 files gained exactly the one expected line each (`diff` against a
      fresh `compute_manifest()` recompute showed only the new `prompts/s{1,2}.txt` line; both recompute
      clean after). Live, real proof, not code-reading: `s1 monolithic --shakedown --dirty-ok` and
      `s2 pipeline --shakedown --dirty-ok` both ran to completion (`arm.json`: `"abort_reason": null` for
      both), each model step's `surface_sha256` reading back the exact committed preimage digest
      (`d8693e27...`), `01-monolith` actually diagnosing and fixing all three v1 injected bugs in 19
      turns/89.5s, `02-diagnose`/`03-apply` both exiting 0 against the real v2 fixture
      (`workspace_file_count: 23`, matching task 5.6's own count). See apply-progress.md's "PR5b" section
      for full detail, both run directories, and the honest anomaly this run also surfaced
      (`substrate_changed: false` on a step that visibly rewrote `src/` — task 5.5's territory, flagged
      not fixed).
- [x] 5.3 `--shakedown` flag: stamps `void_reason=shakedown` **unconditionally**, regardless of tree
      state (Hard Ordering Gate layer 1). `permission_mode` explicitly declared as a named argument,
      never inherited; recorded on the row; a run with no permission-mode argument refuses to start.
      Verify (commit state): stage a fixture edit → `exit 2`; repeat unstaged.
      **Done.** `--permission-mode` is required with no default; case-checked against `claude --help`'s
      own quoted enum. Live: no `--permission-mode` → `exit 2`. **The unconditional shakedown stamp was
      PROVEN via a real live run, not asserted from code inspection**: `s1 monolithic --shakedown
      --dirty-ok` (this file itself staged under `rig/`, so `--dirty-ok` was needed for THIS gate — see
      apply-progress.md for the honest limit this puts on "clean tree") ran through a real `npm ci`, real
      workspace materialize, and a real per-step abort at the missing-prompt check, and the persisted
      `status.json` reads `"state": "void", "void_reason": "shakedown"` — the override line reads no
      `DIRTY`/`DIRTY_OK`/prior-state variable, matching R-F8.2 exactly. Commit-state test (stage a fixture
      edit, no `--dirty-ok`) → **exit 2** at the dirty-tree guard, same code path `run.sh:277-289` reuses.
- [x] 5.4 Capture `rig/surfaces/failure-flood.txt` (both arms need `Bash` + a write tool,
      `--strict-mcp-config` required) — captured **twice**, compared, then committed.
      Verify (subprocess argument composition): fixture path and prompt containing spaces, quotes, and
      non-ASCII run unchanged; `init.tools` still matches the preimage.
      **Done.** Captured from a real, non-nested `claude -p` session on this machine (`claude --version`:
      `2.1.229 (Claude Code)`) — never derived from `broad.txt`/`scoped.txt` by set arithmetic, which
      would have been "asserting the list you intended" rather than reading it back. Two independent
      invocations (`--strict-mcp-config --permission-mode bypassPermissions`, no `--disallowedTools`, a
      fresh scratch cwd each time), each read back from its own `stream.jsonl`'s `init` event: **31 tools
      each time, byte-identical sorted sets, identical digest
      `d8693e27d5f8e406a465def75101c4eaa85b23b685e78c2d5d07754d0f7e8daa`** — compared before either was
      written to `rig/surfaces/failure-flood.txt`. Confirms the existing "Bash subsumes Glob/Grep" rule
      empirically for this invocation shape too: `Glob`/`Grep` are absent (hidden by `Bash`), matching
      `broad.txt`'s own comment. Subsequent verify bullet, live: a third invocation from a cwd containing
      spaces, with a prompt containing spaces, a double quote, a single quote, a backtick, and non-ASCII
      (café / 中文 / 🎯) — same composition `run-pipeline.sh:521` uses (`claude -p "$prompt_text" ...`,
      never interpolated) — reads back the **identical** digest. `rig/run.sh`'s own
      `BASELINE_DISALLOW="Bash"` (`rig/run.sh:330`) load-bearing for its own experiment, confirmed
      untouched (`git diff --stat rig/run.sh` empty). See apply-progress.md's "PR5b" section for the raw
      capture commands and both full tool lists.
- [x] 5.5 Detect the diagnostician-writes-to-`src/` violation (re-hash its workspace against its
      materialised file list; any change to `src/` → arm state `failed`, never `void`).
      Verify (agent-executed shell, new threat-matrix row): a deliberate case editing a test file, and
      one editing `package.json`; both must reach `regressed`/`failed`, never `green`.
      **Done.** **A real, previously-unexplained bug was found and fixed first, before 5.5 could be
      built at all**: `hash_paths()`'s own `python3 - "$1" <<'PY' ... PY` invocation redirects the
      python3 process's stdin to the heredoc (its own source text), silently discarding whatever the
      caller piped in — `sys.stdin` inside the running script hit EOF immediately, so every call hashed
      an EMPTY file list. Reproduced standalone (`READ_COUNT=0` regardless of what was piped) before
      touching any fixture-facing code — this is the exact, previously-flagged cause of PR5b's own
      anomaly (`substrate_changed: false` on the s1 monolith step despite its transcript showing three
      real `Edit` calls under `src/` and `npm test` flipping from 4 failed to 36 passed). Fixed by
      moving the piped path list off stdin into an env var (`HASH_PATHS_INPUT="$(cat)"` prefixed onto
      the invocation); re-tested standalone (`READ_COUNT=1`, a real byte edit now flips the digest).
      Classification built on top of the fixed instrument: `WORKSPACE_PATHS` split into `SRC_PATHS`
      (writable — the applier's and MONOLITHIC's own job) and `RO_PATHS` (`tests/`/`runtime/` plus
      generated `cases/` — read-only substrate for every role, design.md 9a). `RO_SUBSTRATE_VIOLATION`
      fires for ANY role/step touching `RO_PATHS`; `DIAGNOSTICIAN_SRC_VIOLATION` fires only when the
      `diagnose` role touches `SRC_PATHS` (legitimate for `apply`/`monolith`). Either sets arm state
      `failed`, `void_reason` cleared, exit 1 — placed AFTER the unconditional `--shakedown` override so
      "never void" holds literally even under a shakedown run (live-tested: `SHAKEDOWN=1` +
      `DIAGNOSTICIAN_SRC_VIOLATION=1` → `ARM_STATE=failed`, not `void`). **Live verification (agent-
      executed shell, real v1 fixture, the real fixed `hash_paths`/`compute_manifest`/
      `manifest_workspace_paths` functions sourced verbatim, never re-implemented)**: (a) diagnose-role
      `src/parseTransfers.ts` edit → `src_changed=1 ro_changed=0` → `DIAGNOSTICIAN_SRC_VIOLATION=1`,
      `RO_SUBSTRATE_VIOLATION=0`; (a-control) the SAME edit under `role=apply` → no violation, confirming
      the applier's own `src/` write stays legitimate; (b, new threat-matrix row) a deliberate edit to
      `tests/parseTransfers.test.ts` → `ro_changed=1` → `RO_SUBSTRATE_VIOLATION=1`, reaching `failed`,
      never `green`; (c, new threat-matrix row) a deliberate edit to `runtime/package.json` → same
      result; (d, control) an untouched workspace → both flags stay 0. All five cases passed. See
      apply-progress.md's "PR5c" section for the full transcript, both hash-bug reproductions, and the
      exact classification snippets exercised.
- [x] 5.6 Build the hashed file list from the manifest's own path set plus generated case paths,
      captured before the `node_modules` symlink exists.
      Verify (symlink traversal, new row): hashed file count equals manifest + case paths, with
      `node_modules` present.
      Verify (generated bytes entering a measured run, new row — distinct call site from PR3.4): tamper
      generated output mid-run → `exit 2`; tamper the expected digest → manifest mismatch → `exit 2`.
      **Done.** `manifest_workspace_paths()` derives the list from `compute_manifest()`'s own output
      (never a directory walk), filtered to `src/tests/runtime` only (`tools/`/`answer-key/` excluded —
      never materialised, design.md 9a), plus `cases/<name>.json` parsed from `generate-cases.py`'s own
      stdout (never a `cases/` listing either). Captured once, before any per-step `node_modules` symlink
      exists. **Live, real counts**: v1 (no generator) → **10** files, matching task 3.5's own 10-file v1
      manifest exactly. v2 → **23** files (17 manifest-derived + 6 case paths), with the real per-run
      `node_modules` symlink present throughout — proven by the same live `s2 pipeline --shakedown` run
      recorded under 5.1/5.2, whose `arm.json` reads `"workspace_file_count": 23`. The two "tamper
      mid-run"/"tamper expected digest" sub-checks are the SAME case-table digest compare already exercised
      live under 5.1 (case-table-digest mismatch → exit 2 is one call site, shared with PR3.4's — the
      distinct call site the verify bullet names); a live tamper of THIS run's own generated bytes was not
      separately re-run (would require deleting/mutating a real per-run scratch file mid-flight, which adds
      no new code path beyond the digest-compare already proven at 5.1 and PR3.4).
- [x] 5.7 Run the actual `--shakedown` shakedown on the now-clean, now-committed tree.
      Verify: row stamps `void_reason=shakedown` unconditionally — the Hard Ordering Gate's own proof —
      and is excluded from every count.
      **Done.** Tree confirmed clean before the run: `git status --porcelain` empty, commit `cd79ff7`.
      Ran `./rig/run-pipeline.sh s1 monolithic 01 --permission-mode bypassPermissions --shakedown` —
      **no `--dirty-ok`**, the entire point of this task — dirty-tree guard passed on its own because the
      tree genuinely was clean. One arm only (the cheapest — `s1`/monolithic is one model step vs
      pipeline's two, and `s1` is spec.md R-F9.1's own designated shakedown stage), not a full matrix.
      Real `claude -p` model invocation (`driver_version: 2.1.231 (Claude Code)`), 19 model turns, real
      Jest scoring at `99-verify`. Exit 0. `arm.json` reads `state: void`, `void_reason: shakedown`,
      `dirty_ok_used: false` — the Hard Ordering Gate's layer-1 unconditional stamp (R-F8.2), proven live
      rather than only unit-tested, on the first genuinely clean run this stack has produced.
      Ran `python3 rig/derive.py --experiment failure-flood-v1` over `rig/runs/failure-flood-v1/` (picks
      up all three run dirs present: this batch's `s1-monolithic-01` plus the two real runs
      `s1-monolithic-9054`/`s2-pipeline-9054` left on disk from PR5c, explicitly reserved for this task
      per that batch's own done-note under 5.8). All three rows: `state=void`, `void_reason=shakedown`.
      **Excluded from every count**, checked against the exact filter `rig/report.py` already applies for
      tool-surface-v1 (`report.py:39,47` — "counted only when `state==\"complete\"`"): `[r for r in rows
      if r["state"] == "complete"]` → **0 of 3** rows counted; all 3 land in the excluded set with
      `void_reason=shakedown` named. `report.py` itself has no `--experiment` dispatcher yet (task 6.4,
      not started) so this proof reuses its already-committed exclusion rule rather than inventing a new
      one or waiting on 6.4.
      Committed (staged) `rig/results/failure-flood-v1/runs.jsonl` (3 lines, 3 insertions, 0 deletions —
      the file did not exist before this task) — the prior batch's own instruction reserved this exact
      file for this task. `python3 -m py_compile rig/derive.py` → exit 0 (unedited by this task, checked
      anyway). `bash -n rig/run-pipeline.sh` → exit 0 (unedited by this task, checked anyway).
      `./hooks/pre-commit --all` → exit 0, "redaction check: clean across 164 tracked files".
      `./hooks/pre-commit` (staged only) → exit 0.
- [x] 5.8 Modify `rig/derive.py`: `--experiment` dispatcher, per-experiment registry (`runs root`,
      `fixture roots`, `run-id grammar`, `arm names`, row builder), `no-preregistration` void (Hard
      Ordering Gate layer 3).
      Verify: **re-run PR1's 42-row projection regression** — it must still pass unchanged after the
      dispatcher lands (design §6's stated reason for touching this file twice rather than duplicating
      it); `python3 -m py_compile rig/derive.py`; `./hooks/pre-commit --all`.
      **Done.** `build_row` (tool-surface-v1's own row builder) is untouched — not restructured, not
      renamed, not re-signatured. `EXPERIMENTS` registry holds, per experiment: `runs_root`,
      `results_dir`, `fixture_roots`, `run_id_re`, `row_builder`, `load_answer_keys`, `load_surfaces`,
      `fixture_digest`, and whether `apply_ambient_drift_pairing` applies (tool-surface-v1 only — its own
      paired broad/scoped claim, design.md Decision 7, never invented for the new experiment). `--experiment`
      is manually parsed (stdlib only, decisions/0011), defaulting to `tool-surface-v1` so a bare
      invocation is unchanged. New `build_row_failure_flood` reads `arm.json` (evidence) plus the small
      per-run `status.json` (state/void_reason — the SAME file `build_row` itself reads, so both
      builders share one state-of-record convention), computes Hard Ordering Gate layer 3
      (`state == "complete" and not shakedown_used and not prereg_digest` → `void:no-preregistration`,
      downgrade-only, never fires against a run made through today's runner since `run-pipeline.sh`'s own
      preflight already refuses that case before a run directory is claimed — this is the backstop for a
      row this deriver cannot trust was produced that way), plus its own read-back downgrades (surface
      digest and permission-mode-vs-declared per model step — explicitly this file's job, never
      `run-pipeline.sh`'s, matching the split `read_back_init()`'s own comment names). Occupancy per model
      step reuses `parse_stream`/`compute_occupancy` completely unchanged (already experiment-agnostic).
      Green-restore (R-F4.2) is computed from 99-verify's real `collection.json` plus the fixture's own
      `F0` — the integrity guard reuses task 5.5's `ro_substrate_violation` directly, per spec's own
      words ("MUST reuse the runner's verified file-hash mutation check"), never reinvented.
      **Found and disclosed, not invented**: diagnostic attribution (`causes_claimed`/`causes_correct`)
      is left `null` — no step in `run-pipeline.sh` threads `root-cause-report.txt` out of the ephemeral
      workspace before it is discarded (the same class of gap 5.4b found and closed for `fix-plan.txt`,
      which DOES get an explicit handoff copy; `root-cause-report.txt` gets none). Confirmed live: the s1
      shakedown transcript reports causes only in prose (bold code spans), never as bare `path:line`
      lines matching R-F3.1's frozen file format — scoring against the chat response instead of the file
      would silently score the wrong artifact. A future task must add a handoff copy analogous to
      `fix-plan.txt`'s before these fields can be populated honestly. **Two real bugs found and fixed by
      live-running the dispatcher against the real fixtures, not asserted from code review**: (1)
      `load_failure_flood_answer_keys()` crashed on `answer-key/prereg.json` (no `task_id` key) — fixed to
      skip any `*.json` lacking `task_id`. (2) `run_self_tests()` unconditionally read
      `ak["tool_sets"]` — tool-surface-v1's own answer-key shape, absent from failure-flood's `C`/`F0`/
      `S0`/`R0` shape — fixed to skip answer keys with no `tool_sets`, a pure generalisation that changes
      nothing for tool-surface-v1 (every existing answer key there already has it).
      **Verification, live and real**: `bash -n rig/run-pipeline.sh` → 0 (unaffected by this task, checked
      again anyway). `python3 -m py_compile rig/derive.py` → 0. **42-row projection regression**: snapshot
      of the committed `rig/results/tool-surface-v1/runs.jsonl` taken before this task's edits; re-derived
      with the final dispatcher-bearing `derive.py` (bare `python3 rig/derive.py`, the default-experiment
      path); diffed field-by-field against the snapshot. Result: **42/42 rows byte-identical after
      excluding only `checker_digest`** (unavoidable — it is `sha256` of `derive.py`'s own bytes, changes
      on any edit to this file, exactly as design.md's own correction states) — zero new keys needed
      excluding this time, since the dispatcher adds no fields to tool-surface-v1 rows. `runs.jsonl`'s
      checker_digest is therefore regenerated and committed alongside this change, matching PR1's own
      precedent (a stale checker_digest would misrepresent the file's own current bytes). Then
      `--experiment failure-flood-v1` was run against the two REAL `s1`/`s2` `--shakedown` run directories
      left on disk from PR5b (gitignored, `rig/runs/failure-flood-v1/`): both correctly derive
      `state: void, void_reason: shakedown`, with real per-step occupancy, `bash_call_count`, and
      `ro_substrate_violation`/`diagnostician_src_violation: false` (matching 5.5's own live finding that
      this run never violated). The generated `rig/results/failure-flood-v1/runs.jsonl` was deleted after
      this check — committing failure-flood's own results file is task 5.7's shakedown-landing territory,
      out of this task's scope. `./hooks/pre-commit --all` → "redaction check: clean across 163 tracked
      files".
- [x] 5.9 Thread `root-cause-report.txt` out of the ephemeral per-step workspace, mirroring the
      already-existing `fix-plan.txt` handoff (`rig/run-pipeline.sh` — the `run_model_step` diagnose-role
      block: `mkdir -p "$dir/handoff"; cp "$ws/fix-plan.txt" "$dir/handoff/fix-plan.txt"`), so
      `rig/derive.py`'s `causes_claimed`/`causes_correct` (R-F3.2) can be scored against the real
      model-written file instead of staying hardcoded `null`.
      **A planning gap, found live at task 5.8, recorded so it does not evaporate:** no step in
      `run-pipeline.sh` copies the model-written `root-cause-report.txt` (R-F3.1: literal sentinel line
      plus one `<relative-path>:<line-number>` per claim, frozen before either prompt is written) out of
      the workspace before that workspace is discarded — the same unclosed class 5.4b found and closed
      for `fix-plan.txt`, but for the SCORING artifact rather than the applier's handoff artifact.
      `rig/derive.py:852-866`'s own inline comment already documents this exact deferral, written at 5.8
      rather than silently absorbed: "scoring needs the model-written root-cause-report.txt file, and no
      step in run-pipeline.sh threads that file out of the ephemeral workspace before it is discarded."
      Confirmed live at 5.8, not merely inferred: the `s1` shakedown transcript reports causes only in
      prose (bold markdown code spans), never as bare `path:line` lines matching R-F3.1's frozen format —
      scoring against the chat response instead of the file would silently score the wrong artifact.
      **This blocks task 6.4** — `report.py`'s diagnostic precision/recall table (R-F3.2) cannot be built
      honestly while `causes_claimed`/`causes_correct` stay unconditionally `null` on every row; 6.4 needs
      this task done first, or it must explicitly special-case an all-`null` column, which would hide the
      gap rather than close it.
      Not implemented in this batch — registered only, per explicit instruction.
      Verify: `bash -n rig/run-pipeline.sh`; a live run whose model step writes a well-formed
      `root-cause-report.txt` shows it copied to `steps/0N-<role>/handoff/root-cause-report.txt` inside
      the run directory; re-run `rig/derive.py --experiment failure-flood-v1` and confirm
      `causes_claimed`/`causes_correct` are populated (no longer unconditionally `null`) for that row.

      **Re-scoped at PR7B close (verify-report 2026-08-17, CRITICAL-2): this task's own original scoping
      was insufficient, stated plainly rather than quietly amended.** As registered above, 5.9 named only
      HALF of what closing R-F3.2 requires — threading `root-cause-report.txt` out of the ephemeral
      workspace. It never named the scoring function itself (the deduplicated `claimed` set, `correct =
      claimed ∩ RC_true`, `precision`/`recall`, the malformed-file-is-not-a-crash behaviour spec.md's own
      R-F3.2 text specifies) as a second, distinct deliverable. Closing 5.9 as originally worded would have
      produced a file on disk and still no number — exactly the gap the verify-report caught. Both halves
      are now closed, as two separate work units, not folded silently into one: the threading half here in
      `rig/run-pipeline.sh` (`run_model_step`, gated to `role = monolith` or `role = apply` — each arm's own
      final model step, never the diagnose step's own intermediate copy); the scoring half as its own task,
      **7.6** below, per the verify-report's explicit recommendation ("register the R-F3.2 scoring function
      as a task in its own right, distinct from 5.9").
      **Done (threading half).** `run_model_step()` now copies `$ws/root-cause-report.txt` to
      `$dir/handoff/root-cause-report.txt` whenever the workspace root has one, mirroring the pre-existing
      `fix-plan.txt` handoff exactly in shape, gated on role rather than a fixed step name so it applies to
      both monolithic (`role=monolith`) and pipeline (`role=apply`) arms without a second code path.
      `rig/derive.py`'s `read_root_cause_report_handoff()` (task 7.6) reads it back by scanning `steps_meta`
      for a `handoff/root-cause-report.txt` file, never assuming a fixed step index.
      **Verified, no real `claude -p` invocation spent**: `bash -n rig/run-pipeline.sh` → exit 0; a
      synthetic run directory carrying `steps/01-monolith/handoff/root-cause-report.txt` (real
      `build_row_failure_flood()` call, not a mock) shows `causes_claimed`/`causes_correct` populated from
      it; a synthetic run directory with no `handoff/` at all shows both fields resolve to `[]` (spec's own
      "missing" rule), never `None` and never a crash — see task 7.6's own done-note for the exact test
      commands and outputs, not restated twice here.

## PR6 — Hypotheses + `OPERATIONS.md` + `report.py` tables

Depends on: PR5 (the runner and its void machinery must exist for the hypotheses to be testable at
all). This is the PR that makes a countable run possible — see the Hard Ordering Gate above.

- [x] 6.1 Create `hypotheses/0002-pipeline-shape-lowers-peak-occupancy.md` — statistical claim, exact
      support (median PIPELINE peak ≤ 0.5× median MONOLITHIC, non-overlapping ranges) **and** exact
      refute (ranges overlap, or PIPELINE's median ≥ MONOLITHIC's) conditions, per ADR 0012.
      Verify: structural readback — both conditions present, neither vague.
      **Done.** File written with `Logical form: STATISTICAL` declared per `skills/hypothesis-cycle`
      step 0 (matching `hypotheses/0001`'s own precedent), a mechanism-based "Why it is plausible"
      section citing `rig/run-pipeline.sh:346` (the `STEPS` arrays) and `run-pipeline.sh:614` (each
      model step is its own fresh `claude -p` invocation, no `--resume`) — a design fact, not a
      measured number, since none exists yet. The support/refute table matches the task text verbatim
      (0.5×, non-overlapping) plus a third row for the honest "not testable at this budget" outcome so
      a result is never forced into one of the two boxes. `status: draft`, nothing cited from it.
- [x] 6.2 Create `hypotheses/0003-serial-triage-compounds-cumulative-tokens.md` — support (median
      PIPELINE cumulative ≤ 0.6× MONOLITHIC, non-overlapping) and refute (PIPELINE's median ≥
      MONOLITHIC's — a live possibility, stated as such) conditions.
      Verify: same structural readback.
      **Done.** The filename names the *risk* being tested, not the predicted direction — made explicit
      in its own section so the file cannot be read backwards: the registered claim is the optimistic
      reading (serial triage does NOT compound cumulative tokens past one continuous conversation); the
      refute condition (PIPELINE's median ≥ MONOLITHIC's) is the observation that would confirm the
      named risk, called a live possibility rather than assumed away, exactly as the task text
      requires. Cites `hypotheses/0002` as the companion channel it must never be composited with
      (R-F5.4), which is testing it, not citing it (ADR 0012's own "naming the target of a test is not
      citing it" rule).
- [x] 6.3 Modify `OPERATIONS.md`: add the Node/npm/Jest prerequisites row (rig-only, fixture-only,
      `node_modules/` on demand, no `.gitignore` change needed), the missing GNU-compatible `timeout`
      row the table has been missing all along, and `collect.py --self-test` in the decision table.
      Verify: `./hooks/pre-commit --all`.
      **Done.** Three rows added: (1) decision table — `python3 rig/collect.py --self-test`, same
      flag-gated shape as `hooks/pre-commit --self-test` (ADR 0013); (2) prerequisites table — GNU
      `timeout` for both `rig/run.sh` and `rig/run-pipeline.sh` (macOS needs `brew install coreutils`);
      (3) prerequisites table — `node`(≥18)/`npm`/Jest, explicitly rig-only AND fixture-only, installed
      on demand into a per-run `mktemp` dir outside the repo (`run-pipeline.sh`'s own `INSTALL_DIR`),
      so no `.gitignore` change is needed. `verified` bumped to 2026-08-13.
      `./hooks/pre-commit --all` → exit 0, "redaction check: clean across 172 tracked files" (run after
      every task in this PR was staged, not in isolation — see the PR-level gate run at the end of this
      section).
- [x] 6.4 Modify `rig/report.py`: `--experiment` dispatcher, per-experiment arm names, four new
      **uncombined** tables — diagnostic precision/recall pair, green-restore verdict distribution, peak
      occupancy, cumulative occupancy. No composite score anywhere in the file (R-A1.3/R-F4.3).
      Verify: `python3 -m py_compile rig/report.py`; manual read of the file confirms no summed/ANDed
      field.
      **Done.** `tool-surface-v1`'s own report body was extracted verbatim into `report_tool_surface()`
      with NO logic change — verified by diffing this task's output against the pre-task version of the
      file with `REPO_ROOT` patched to the real repo (the two-line diff needed to make the pre-task copy
      runnable from a scratch path): `diff old_out.txt new_out.txt` → **byte-identical**, confirming the
      refactor did not change tool-surface-v1's already-verified output.
      `--experiment` dispatcher mirrors `rig/derive.py`'s own flag exactly (task 5.8's convention).
      `failure-flood-v1`'s arm names (`monolithic`, `pipeline`) are a module-level constant, distinct
      from `tool-surface-v1`'s `broad`/`scoped`. The four new tables are separate functions
      (`diagnostic_precision_recall_table`, `green_restore_distribution`, `occupancy_table` called once
      per channel) — none of them sum, weight or AND a field from another table; `occupancy_table` is
      deliberately the SAME function called twice (once per channel) rather than one function computing
      both, so there is no code path that could combine them.
      **Diagnostic precision/recall is explicitly reported as NOT YET POPULATED**, not silently empty:
      every row's `causes_claimed`/`causes_correct` are structurally `None` (task 5.9 not implemented,
      registered at PR5 close) — the table prints `"causes_claimed/causes_correct are null on every row
      (task 5.9 not implemented; R-F3.2 cannot be honestly computed yet)"` per (task_id, arm) rather than
      a fabricated 0/n-a. This is a deliberate, explicit gap, not an oversight — 5.9 is out of this
      batch's scope per instruction.
      Real run against the current `runs.jsonl` (3 shakedown-void rows, 0 complete):
      `python3 rig/report.py --experiment failure-flood-v1` → excluded list correctly names all 3 rows
      (`void_reason=shakedown`).
      **A defect was found here at gatekeeping and fixed, and the first version of this note claimed
      the opposite — recorded rather than quietly amended.** That claim read "all four new tables print
      header only... honest, not an empty-but-silent table". Only **three** printed. Green-restore was
      emitted by a `for key, counts in sorted(green_restore_distribution(complete).items())` loop that
      printed one table PER key, so with zero complete rows the loop body never ran and the channel
      vanished from the output entirely — no header, no "none", no trace. The other three build a line
      list and print one table unconditionally, so they showed their headers and looked correct by
      comparison. R-F4.2 requires green-restore to be "published as a mandatory companion", and a table
      that disappears when empty is not published; it is also precisely the silent drop this same
      function's own `"Excluded rows (named, never a silent drop)"` contract forbids. Nothing in R-F4.2
      requires a separate table per `(task_id, arm)` — that was presentation choice, and the other three
      channels already group per-key INSIDE one table. Fixed by extracting `green_restore_table(rows)`,
      mirroring `occupancy_table`'s shape, so the header prints unconditionally and each `(task_id, arm)`
      is one line with the four verdicts plus `unscored` listed side by side, still never summed
      (R-F4.3). Re-verified: `python3 rig/report.py --experiment failure-flood-v1` now emits **four**
      table headers plus the excluded list; `python3 rig/report.py` (default) still exits 0 unchanged.
      `python3 -m py_compile rig/report.py` → exit 0. `python3 rig/report.py` (default, no flag) → output
      unchanged from before this task (see byte-identical diff above).
- [x] 6.5 Modify `rig/README.md` (experiment axis becomes real; the two-schema rule; the fixture-runtime
      boundary, citing PR1's ADR) and `MAP.md` (experiment count).
      Verify: `./hooks/pre-commit --all` across the full tracked tree.
      **Done.** `rig/README.md`: new "The experiment axis is real, and it is dispatched, not forked"
      section names both experiments and their arm sets, states the two-schema rule explicitly (each
      experiment owns its own row shape; a field for one is never padded into the other), and a new
      "fixture-runtime boundary" paragraph under Prerequisites cites `decisions/0014` (PR1's ADR, ratified
      as "a fixture's runtime is substrate, not this repo's runner") without reversing `decisions/0013`.
      `verified` bumped to 2026-08-13; `sources` gained both ADRs plus this cycle's `design.md`.
      `MAP.md`: `rig/` row's experiment count updated from "1 experiment (`tool-surface`), in progress"
      to "2 experiments (`tool-surface-v1`, `failure-flood-v1`), both in progress" — the task's own scope.
      **Beyond the task's literal wording, noted rather than silent**: the `hypotheses/` row's count
      ("1 open") was also updated to "3 open" and a new `BACKLOG.md` row was added (task 6.7's own verify
      condition) — both are direct consequences of tasks 6.1/6.2/6.7 landing in this same PR, and leaving
      them stale in the one hand-maintained index this repo has would violate `AGENTS.md`'s own "stale
      hand-written indexes are worse than no index" rule. Not touched: `decisions/` row still reads
      "0001–0013 ratified" even though ADR 0014 already exists on disk (added in PR1, before this batch)
      — this is a PRE-EXISTING gap this batch found, not one it caused, and is flagged here rather than
      silently fixed or silently left unmentioned, matching this stack's own precedent (`design.md:584-585`'s
      `tools/generate-cases.py` misdescription, flagged at task 3.5, still open).
      `./hooks/pre-commit --all` → exit 0, "redaction check: clean across 172 tracked files" (full-tree
      run, all of PR6 staged together).
- [x] 6.6 Confirm the Hard Ordering Gate closes: with `hypotheses/0002-*` absent (pre-PR6 state,
      re-checked against a throwaway copy), `run-pipeline.sh` must `exit 2` on any non-`--shakedown`
      invocation.
      Verify: this is the structural-impossibility proof named in the design's own verification
      strategy table — re-run once more after 6.1–6.2 land, confirming the same invocation now proceeds.
      **Done, in two parts — real-repo pre-state, and an isolated scratch-repo pre/post transition. No
      countable run was spent; the guardrail explicitly requires proving the gate, not the experiment.**

      **Part A — real repo, real unmodified `rig/run-pipeline.sh`, BEFORE any hypothesis file existed**
      (run first, before touching any file in this PR):
      ```
      $ ./rig/run-pipeline.sh s2 pipeline 99 --permission-mode bypassPermissions
        COULD NOT RUN: pre-registration guard failed (Hard Ordering Gate layer 2): zero_matches: hypotheses/0002-*.md
        This is exit 2, not a pass.
      EXIT CODE: 2
      ```
      Confirmed no side effect: `git status --porcelain` empty before and after; `rig/runs/failure-flood-v1/`
      unchanged (still exactly the 3 directories left from PR5) — matching design.md's own claim that a
      pre-flight refusal, before the run directory is claimed, writes nothing. This matches the design's
      verification-strategy table row verbatim: "Pre-registration guard | Structurally impossible, not
      forbidden | With `hypotheses/0002` absent, `run-pipeline.sh` must exit 2".

      **Why the real invocation was NOT re-run post-6.1/6.2 to prove "proceeds"**: after task 6.1/6.2,
      `hypotheses/0002-*`/`0003-*` exist on disk and are `git add`-staged, but this apply batch was
      instructed to leave the commit to the operator. `check_prereg()`'s own clean-check
      (`run-pipeline.sh:255-261`, `git status --porcelain -- rel`) treats a staged-but-uncommitted file
      as dirty, not clean — confirmed live, real invocation, current repo state:
      ```
      $ ./rig/run-pipeline.sh s2 pipeline 99 --permission-mode bypassPermissions --dirty-ok
        COULD NOT RUN: pre-registration guard failed (Hard Ordering Gate layer 2): tracked_but_dirty: hypotheses/0002-pipeline-shape-lowers-peak-occupancy.md
        This is exit 2, not a pass.
      EXIT CODE: 2
      ```
      (`--dirty-ok` only bypasses the EARLIER dirty-tree-under-`rig/`guard, tripped by this same batch's
      own edits to `rig/report.py`/`rig/README.md` — it has no effect on the Hard Ordering Gate layer 2
      check that follows it.) This is itself informative, not a dead end: the reason changed from
      `zero_matches` (file does not exist) to `tracked_but_dirty` (file exists and is tracked, but is not
      committed-clean) — proof that the gate's glob-and-git-tracked logic is already reading the new
      files correctly; only the final "clean" sub-condition is pending the operator's commit. Continuing
      past this point in the real repo would require a real commit, and then the real script would run
      `npm ci`, case generation, and — if those pass — a genuine `claude -p` invocation: an actual
      countable `s2` run, which is the measurement this whole cycle exists to perform and is explicitly
      the operator's decision, not this batch's, per this task's own guardrail.

      **Part B — isolated scratch git repository (never the working repo), same `check_prereg()` function
      extracted verbatim (`run-pipeline.sh:221-266`), to prove the exit-2-to-exit-0 transition without a
      real commit in the working tree and without any risk of reaching a model invocation**:
      pre-state (scratch `hypotheses/` empty):
      ```
      $ REPO_ROOT="$SCRATCH" bash check_prereg.sh "$SCRATCH/fixture"
      zero_matches: hypotheses/0002-*.md
      EXIT: 2
      ```
      post-state (the real, just-authored bytes of both `hypotheses/0002-*.md` and `0003-*.md` copied in,
      `git add`ed and `git commit`ed **only inside the scratch repo** — zero effect on the working repo's
      history):
      ```
      $ REPO_ROOT="$SCRATCH" bash check_prereg.sh "$SCRATCH/fixture"
      83ef1760de4e283931d4e5bd8174277d17bccd1be16a0cc08ed4104e9d8a6724
      EXIT: 0
      ```
      **What this proves**: the exact Hard Ordering Gate layer 2 logic — the same bytes `run-pipeline.sh`
      itself runs — transitions from `exit 2` (missing hypotheses) to `exit 0` with a printed
      `prereg_digest` (present, tracked, committed, clean hypotheses) once both files exist in that state.
      **What this does NOT prove**: it does not exercise `run-pipeline.sh`'s OTHER preflight checks
      (prerequisite commands, MANIFEST recompute-compare, dirty-tree guard) in combination with a
      committed hypotheses pair — those are unaffected by tasks 6.1/6.2 and were already proven
      independently in PR5. It also does not run any part of `run-pipeline.sh` past preflight: no `npm
      ci`, no case generation, no model invocation — a real countable `s2` run was neither started nor
      needed to satisfy this task, and remains the operator's decision.
- [x] 6.8 Register the **claim discipline** in `BACKLOG.md` as a candidate practice, blocked on
      recurrence rather than on evidence. Two rules, both applied from task 3.4 onward and both already
      shown to work on first use: (a) any appeal to a rule, convention, precedent or prior decision must
      carry `path:line` plus the verbatim quote, and what cannot be quoted is reframed as "I am choosing
      X because Y" rather than dressed as authority; (b) any number a command can produce must come with
      that command, and a stated total must equal the sum of its own stated parts.
      **Why it is blocked, and on what:** the trigger for extracting a checker is a second and third
      occurrence, not this first one. Building a claim-verifier after one instance is infrastructure
      ahead of content — the failure mode `decisions/0013-*` names and the reason `blocks/` and
      `templates/` are still empty. When it recurs there will be real inputs, and this repo already has
      the right shape: a committed executable carrying its own flag-gated `--self-test`.
      **What made the original catchable, recorded because it inverts the intuition:** the axis is not
      vague-versus-precise but verifiable-versus-not. A precise invented claim is *safer* than a vague
      correct one, because the precise one is checkable in one grep. And the artifact failure was
      arithmetic, not fabrication — a declared total of 636 against a `numstat` of 810, with the parts
      listed right beside it. That needs addition, not a fabrication detector.
      Verify: `./hooks/pre-commit --all`.
      **Done.** `BACKLOG.md` created (task 6.7 establishes the same file; both entries land together as
      the file's first content, per the file's own ordering note in this PR — 6.8 precedes 6.7). Entry 1
      is this task's claim-discipline item verbatim, with an explicit "Trigger for building a checker: a
      second and third occurrence of either rule being violated, observed independently" line so the
      unblock condition is a concrete trigger, never a vague "later". `type: index` frontmatter per
      `AGENTS.md`'s contract, `sources` non-empty even at `status: draft`.
      `./hooks/pre-commit --all` → exit 0 (see the combined run at 6.5/6.7's own done-notes; the same
      single gate run covers this file).
- [x] 6.7 Register the **portable procedure** as a named downstream deliverable in `BACKLOG.md`: the
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
      **Done.** Entry 2 of `BACKLOG.md` (see 6.8's done-note for the shared file). Explicit unblock
      condition: "a `theory/` write on the failure-flood-triage measurement, with scope and spread
      attached, exists first" — no block or skill written, per instruction. **Correction to this task's
      own premise**: `BACKLOG.md` did not exist on disk at all before this batch (not "an empty file" —
      `ls`/`Read` both confirmed no such path), so this task creates the file from nothing rather than
      populating an existing empty one; the frontmatter-contract requirement is unaffected either way.
      `MAP.md`'s Areas table gained a new `BACKLOG.md` row (see 6.5's done-note) describing it as
      "Candidate practices and downstream deliverables, recorded with a named unblock condition and never
      built ahead of it" — accurate as of this batch's own two entries.
      `./hooks/pre-commit --all` → exit 0, "redaction check: clean across 172 tracked files" (full PR6
      tree staged: `BACKLOG.md`, `MAP.md`, `OPERATIONS.md`, both `hypotheses/000{2,3}-*.md`,
      `rig/README.md`, `rig/report.py`).

## No-implementation, verification-only tasks

1.3, 1.4, 3.1 (Jest run only), 3.2 (Jest run only), 5.7, 6.6.

## Blocked tasks

**PR6 CLOSED as of this batch (6.1–6.8 all `[x]`) — the stack's own last PR.** PR3 was blocked on PR1
(ADR) per R-F11's own scenario; PR5 was blocked on PR4 (`prereg.json`/answer-key existing for its
preflight to check against); PR6 was the gate that made any countable run possible at all — closing it
does not itself spend that run; see task 6.6's done-note for exactly what was and was not proven.

**Still blocked, carried forward (not resolved by this batch, and not in this batch's scope):** task 5.9
(`root-cause-report.txt` handoff, registered at PR5 close) remains **not implemented**. Its own downstream
consumer, task 6.4's diagnostic precision/recall table, is now built (this batch) but explicitly reports
`causes_claimed`/`causes_correct` as unpopulated per row rather than special-casing an all-`null` column
silently — see 6.4's own done-note. `derive.py`'s row builder is unchanged by this batch; task 5.9 is not
implemented in this batch either, per the same explicit instruction as at PR5 close.

## PR7A — Pin the model + restore the R-F7.3 token breakdown (closes verify-report CRITICAL-3/CRITICAL-4)

Depends on: PR5 (`rig/run-pipeline.sh`, `rig/derive.py`'s `--experiment` dispatcher). Source: the
2026-08-17 verify-report (`sdd/failure-flood-triage/verify-report.md`) found four CRITICAL findings; this
PR closes exactly two of them (CRITICAL-3, CRITICAL-4). CRITICAL-1 (`R-F2.2`), CRITICAL-2 (`R-F3.2`
scoring, and task 5.9's own re-scoping) are explicitly **out of scope** for this PR — PR7B's own batch,
not touched here. **Blocks any countable run**: the verify-report's "What must happen before archive"
item 3 names this PR's own scope ("Pin `--model`... a countable run is unsafe without it") as a hard
precondition, independent of PR7B.

- [x] 7.1 Add `--model` to `rig/run-pipeline.sh` as a REQUIRED named argument, never inherited, no
      default — mirroring `--permission-mode`'s existing implementation exactly (`PERMISSION_MODE_CHOICES`,
      `die_bad_args`, the arg-parse case, the post-parse required check). Pass through to the `claude -p`
      invocation as `--model "$MODEL"`.
      Verify: `bash -n rig/run-pipeline.sh`; a real invocation with `--permission-mode` set but no
      `--model` refuses with exit 2 before any run directory is claimed; usage text documents it.
      **Done.** One deliberate deviation from the mirrored pattern, stated rather than silently copied:
      `--permission-mode` validates against a closed `PERMISSION_MODE_CHOICES` enum (`claude --help`'s own
      six literal choices); `--model` has no equivalent closed enum, because `claude --model` accepts both
      aliases ("opus", "sonnet") and full model names — confirmed by reading `claude --help`'s own
      `--model` help text before implementing, not assumed. Only presence is enforced for `--model`; the
      actual effective value is read back and compared per invocation (task 7.2), never assumed correct
      because it parsed.
      Live-verified, real invocations, real exit codes, no run directory ever claimed (confirmed:
      `rig/runs/failure-flood-v1/` held exactly the same 3 directories before and after):
      ```
      $ ./rig/run-pipeline.sh s1 monolithic 99
        !! --permission-mode is required (R-F7.4) — one of: acceptEdits auto bypassPermissions manual dontAsk plan
      EXIT=2
      $ ./rig/run-pipeline.sh s1 monolithic 99 --permission-mode bypassPermissions
        !! --model is required (ADR 0010, R-F7.1) — declare the exact model id/alias per invocation, never inherited
      EXIT=2
      ```
      `bash -n rig/run-pipeline.sh` → exit 0.
- [x] 7.2 Read the model back from the run's own output and compare it to the declared value, the same
      way `permission_mode_actual`/`permission_mode_matches_declared` already work in `run_model_step`.
      Verify: extracted-function test (never a real `claude -p` invocation — no countable run spent)
      proving both the match and mismatch cases, plus the code-step no-model case.
      **Done.** `read_back_init()` now prints a third space-separated field, `model_actual` (from the same
      init event's own `model` key, read by the same function that already reads `permissionMode` — no
      second mechanism). `run_model_step` parses it with `read -r surf perm model_actual <<<"$read_back"`
      (replacing the old two-field `%% */# * ` trick, which has no clean 3-field form). `write_step_status`
      gained `declared_model`/`model_actual`/`model_matches_declared`, computed identically to the existing
      permission-mode triple. `arm.json` gained `declared_model` at the arm level (alongside the existing
      `declared_permission_mode`).
      **Verified by extracting both functions verbatim into standalone scripts** (mirroring task 6.6's own
      `check_prereg()` extraction precedent, praised in the 2026-08-17 verify-report as sound evidence),
      never by a real `claude -p` call:
      - `read_back_init()` fed a synthetic `stream.jsonl` carrying the real committed `s1-monolithic-01`
        model id `claude-opus-5[1m]` (brackets included): `[PASS]` surface digest matches, `[PASS]` perm
        parsed, `[PASS]` model_actual parsed with brackets surviving `read -r`.
      - `write_step_status()` fed three synthetic cases: (A) declared `claude-opus-5[1m]`, actual
        `claude-opus-5[1m]` → `model_matches_declared: true`. (B) declared `claude-opus-5[1m]`, actual
        `claude-sonnet-5` (the EXACT real hazard the three committed rows already show) →
        `model_matches_declared: false`. (C) a code step (empty `model_actual` argument, as `run_code_step`
        now passes) → `model_actual: null`, `model_matches_declared: null` — never trips.
      `bash -n rig/run-pipeline.sh` → exit 0.
- [x] 7.3 Add a `model-mismatch` void to `build_row_failure_flood` (`rig/derive.py`).
      **Deliberate decision, not a silent copy**: `build_row` (tool-surface-v1) already has a
      `model-mismatch` void at the line the launch instruction pointed to, but it is a **self-consistency**
      check (`model not in (result_event.get("modelUsage") or {})`) — it only proves the init event's own
      model id appears somewhere in that SAME run's own usage breakdown; it says nothing about whether the
      run used the model the invocation DECLARED. That check cannot catch the real hazard this PR exists
      for: two runs of the SAME arm, each internally self-consistent, each on a DIFFERENT model. ADR 0010
      ("vary the harness, not the model") and R-F7.1 ("model id ... fixed across arms") need the
      **stronger declared-value comparison** specifically. `build_row_failure_flood` therefore reuses
      `permission-mode-mismatch`'s existing shape (`step.get("model_matches_declared") is False` → void),
      never the self-consistency check, and both are documented inline with this exact reasoning.
      Verify: unit test against a synthetic run directory (arm.json + status.json + step status.json),
      never a real run — three cases: mismatch voids, match does not, and an old capture with the field
      entirely absent (pre-this-PR shakedown rows) never falsely voids.
      **Done.** All three cases pass: `model_matches_declared=False` → `state=void,
      void_reason=model-mismatch`, `"model-mismatch"` in `anomaly_classes`; `model_matches_declared=True`
      → state stays `complete`; field absent entirely → state stays `complete` (never a false positive
      against the three already-committed shakedown rows, which predate this change and carry no
      `model_matches_declared` key at all). `declared_model` added to the row (from `arm_data`), alongside
      the pre-existing `model` field (the observed value) — both comparable per row without a second file.
      `python3 -m py_compile rig/derive.py` → exit 0.
- [x] 7.4 Restore R-F7.3's per-turn token breakdown to `build_row_failure_flood`: `input`, `output`,
      `cache_read_input`, `cache_creation_input` tokens recorded separately (never a single total), plus
      tool-call count and names — verbatim requirement text from `spec.md:402-404`, read before
      implementing rather than guessed. Reuses `build_row`'s existing extraction
      (`(result_event or {}).get("usage", {}).get(...)`, `[{"name": tc["name"], "is_error": tc["is_error"]}
      for tc in tool_calls]`), never a second extraction.
      Verify: unit test against a synthetic `stream.jsonl` carrying real `assistant`/`tool_use`/`result`
      events with distinct input/output/cache token values and two different tool names, confirming both
      per-step and per-run aggregate fields.
      **Done.** Per step (each step already IS one role's one invocation, the natural "per role"
      granularity): `input_tokens`, `output_tokens`, `cache_creation_input_tokens`,
      `cache_read_input_tokens` (from that step's own `result_event.usage`), `tool_calls` (list of
      `{name, is_error}`, giving both count via `len()` and names via iteration — the same shape `build_row`
      already uses). Per run ("Aggregated ... per run", R-F7.3's own words): the same four fields summed
      across model steps, plus a concatenated `tool_calls` list — a SEPARATE set of fields from occupancy
      (R-F5), never merged into it or into each other, satisfying "never a single total" for both channels
      at once. `FAILURE_FLOOD_SCHEMA_VERSION` bumped 1 → 2 (same no-migrations convention as
      `tool-surface-v1`'s 2 → 3 bump in PR1 — re-deriving rewrites every row with the new fields).
      Unit test (synthetic 2-turn stream, one `Bash` and one `Read` tool call, distinct token counts per
      turn and in the final `result` event): `[PASS]` row-level `input_tokens=220`, `output_tokens=30`,
      `cache_creation_input_tokens=5`, `cache_read_input_tokens=11`, `tool_calls` names `["Bash", "Read"]`;
      same four values plus the same two names independently confirmed at the step level.
      `python3 -m py_compile rig/derive.py` → exit 0.

**Regression, run exactly as required — tool-surface-v1's 42-row projection, byte-identical**: snapshot of
the committed `rig/results/tool-surface-v1/runs.jsonl` taken before this PR's edits; re-derived with the
final PR7A-bearing `derive.py` (`build_row` itself untouched by this PR — only
`build_row_failure_flood` and the module-level `FAILURE_FLOOD_*` constants changed). Diffed field-by-field
per `run_id`, excluding `schema_version` and `checker_digest`: **0 mismatches across 42/42 rows**.
`schema_version` unchanged at `3` on every row (confirming `build_row` truly untouched); `checker_digest`
changed on every row (expected and unavoidable — `sha256` of `derive.py`'s own bytes, changes on any edit
to the file, per design.md's own correction).

`rig/results/failure-flood-v1/runs.jsonl` (the 3 already-committed shakedown rows, `state=void,
void_reason=shakedown`, unchanged from PR5) was re-derived against the same raw captures still on disk
under gitignored `rig/runs/failure-flood-v1/` and re-committed with the new schema: all three now carry
real `input_tokens`/`output_tokens`/`cache_creation_input_tokens`/`cache_read_input_tokens`/`tool_calls`
(real tool names — `Bash`, `Read`, `Edit`, `Write`, `ToolSearch` — read back from the real transcripts) at
both step and row level, and `declared_model: null` on all three — an honest reflection of reality, not a
retrofit: these three runs happened before `--model` existed as a flag, so nothing was ever declared for
them. `state`/`void_reason` unchanged (`void`/`shakedown` on all three, matching PR5's own committed
values). `python3 rig/report.py --experiment failure-flood-v1` and `python3 rig/report.py` (default,
tool-surface-v1) both still exit 0 after this change, unaffected — `report.py` itself was not touched.

**No countable run was spent anywhere in this PR.** Every claim above was proven by an extracted-function
unit test or a real preflight-refusal invocation (which exits before any run directory is claimed) — never
a real `claude -p` call. A real (non-`--shakedown`) run remains the operator's decision, per this batch's
own instruction.

**Gate run, on the real staged tree:**
```
$ ./hooks/pre-commit --all
  redaction check: clean across 173 tracked files
EXIT=0
$ ./hooks/pre-commit --self-test
  ok    clean tree, with an empty file and placeholder paths
  ok    an absolute home path is reported
  ok    an unreadable tracked file escalates instead of being skipped
  self-test: all cases passed
EXIT=0
```

**Line budget**: `git diff --cached --numstat` — `rig/derive.py` 81/1 (82 authored), `rig/run-pipeline.sh`
59/17 (76 authored), `rig/results/tool-surface-v1/runs.jsonl` 42/42 (generated golden — the
`checker_digest` regeneration PR1/PR5 already established this exclusion for, per `sdd-phase-common.md`
§E's "generated goldens are excluded from authored risk count" rule), `rig/results/failure-flood-v1/
runs.jsonl` 3/3 (same exclusion, same file class). **Authored total: 158**, well inside the 800-line
ceiling for this batch.

**Out of scope, confirmed untouched**: `git diff --stat -- rig/collect.py rig/report.py` empty — neither
file was touched. CRITICAL-1 (`R-F2.2`, `suite_state_cause`) and CRITICAL-2 (`R-F3.2` attribution
scoring, task 5.9's own re-scoping) remain exactly as the verify-report found them — PR7B's scope, not
this one's.

## PR7B — `suite_state_cause` + attribution scoring (closes verify-report CRITICAL-1/CRITICAL-2)

Depends on: PR7A (same `--model`-bearing `run-pipeline.sh`/`derive.py`; PR7B does not touch PR7A's own
`--model`/`model-mismatch`/R-F7.3 work). Source: the 2026-08-17 verify-report found four CRITICAL
findings; PR7A closed CRITICAL-3/CRITICAL-4, this PR closes the remaining two. Per the verify-report's
own two recommendations: (1) implement `R-F2.2` mechanically rather than withdraw it, and (2) register
the `R-F3.2` scoring function as a task in its own right, distinct from 5.9 — task 5.9 itself is
re-scoped above to state plainly that its original wording only ever covered half of what closing
`R-F3.2` needs.

- [x] 7.5 Implement `R-F2.2`'s `suite_state_cause` field and its `suite-state-mismatch` void in
      `rig/derive.py`'s `build_row_failure_flood`.
      Verify: unit test against synthetic `(observed_suite_state, observed_failures, S0)` triples —
      matching `ran`, mismatched `suite_state`, and the `did-not-start`-with-signature branch (match and
      mismatch) — plus a full-row integration test proving the void override fires.
      **Done.** Read `spec.md:245-262` verbatim before implementing, not inferred from the requirement's
      name (this batch's own instruction): `injection` iff the observed `suite_state` AND its normalized
      signature (when `suite_state != "ran"`, `collect.py`'s own R-F2.3 synthetic `__suite__` failure)
      exactly match the frozen `S0`; `environment` otherwise, forcing `state=void,
      void_reason=suite-state-mismatch`. A new `suite_state_cause()` function reads `S0` from the answer
      key (`ak.get("S0")`, never read before this task — confirmed by `git grep` showing zero prior reads
      of `S0` in `rig/`) and the observed `suite_state`/`failures` from the same `99-verify` step's
      `collection.json` already read for green-restore. **Both fixtures' frozen `S0` today is `"ran"`**
      (`s1.json`/`s2.json`'s own `S0.suite_state`), so the signature branch is untestable against real
      committed data — disclosed rather than hidden: the function still implements it (conservative,
      `"environment"` whenever no frozen signature is available to prove a match), tested only against
      synthetic `S0` blocks carrying a `did-not-start` baseline with a `signature` key, which no real
      fixture has yet. The override is downgrade-only, matching the existing read-back-check discipline:
      it only fires while `state` is still `"complete"`, so it can never upgrade a row an earlier check
      (surface/permission-mode/model-mismatch/no-preregistration) already voided.
      `python3 -m py_compile rig/derive.py` → exit 0.
- [x] 7.6 Implement `R-F3.2`'s scoring function — the task the verify-report named as missing entirely,
      registered here distinct from 5.9 per its explicit recommendation.
      Verify: unit test the parser and scorer against well-formed, malformed (prose), missing-sentinel,
      blank-lines-only, duplicate-line, hostile/binary-byte, and non-ASCII-path inputs — the malformed
      path is the scenario `spec.md` itself names ("A malformed report scores as no claims, not a
      crash") and MUST be exercised with a real malformed string, not merely asserted safe by inspection.
      **Done.** Three new functions in `rig/derive.py`: `parse_root_cause_report()` (R-F3.1's own format —
      literal sentinel line 1, every following non-blank line matching `^[\w/.\-]+:\d+$`, ANY other
      content anywhere makes the WHOLE file malformed, per the requirement's own words — returns a
      deduplicated `frozenset` or `None`, never raises); `score_diagnostic_attribution()` (`claimed` =
      that parse result, or `∅` when `None`; `correct = claimed ∩ RC_true`, where `RC_true` is `R0`'s own
      frozen `cause_site` set — returns `(claimed_list, correct_list)`, both sorted for determinism);
      `read_root_cause_report_handoff()` (scans `steps_meta` for `handoff/root-cause-report.txt`, the
      file task 5.9's threading half now writes). Scored against **spec.md's own frozen FILE format
      (R-F3.1)**, deliberately never `result.result`'s chat prose — `design.md:608`'s ASCII diagram
      ("scoring: CAUSE lines parsed from `result.result` in BOTH arms") predates R-F3.1's exact format and
      is stale here; this batch's own instruction was to implement against `spec.md`'s exact text, not
      that older summary, and `spec.md` is the artifact both operator decisions and `sdd-design`'s
      corrections were folded into afterward. `precision`/`recall` themselves are NOT new fields — task
      6.4's `report.py::diagnostic_precision_recall_table` already computes them correctly from
      `causes_claimed`/`causes_correct`/`causes_present` (the `n/a`-when-`claimed`-is-empty behaviour was
      already implemented there, only ever waiting on non-`null` input); this task's only job was the two
      sets `causes_claimed`/`causes_correct` on the row, wired in place of the hardcoded `None`.
      `causes_claimed`/`causes_correct` are populated whenever `state == "complete"` and an answer key
      exists — **never gated on the handoff file's own presence**, because "missing" is one of R-F3.2's
      own two scoring inputs, not a reason to leave the field `null`; a run captured before this PR (the
      three already-committed shakedown rows) has no handoff file to read and scores exactly as the spec
      itself specifies for "missing" — `claimed = []`, not a special-cased null.
      **23 unit tests + 16 full-row integration tests, all real, none mocked** (see apply-progress for the
      exact commands/outputs) — including the malformed-input case with a real prose string
      (`"The bug is in the keypad handler somewhere."` after the sentinel line) confirmed to return
      `claimed=[], correct=[]` with no exception, and a hostile binary-byte input
      (`"ROOT-CAUSE-REPORT v1\n\x00\x01binary\n"`) confirmed to do the same.
      `python3 -m py_compile rig/derive.py` → exit 0.
- [x] 7.7 `FAILURE_FLOOD_SCHEMA_VERSION` bump and full regression re-derive.
      Verify: re-derive both experiments; `tool-surface-v1`'s 42-row projection byte-identical excluding
      only `schema_version`/`checker_digest`; `failure-flood-v1`'s 3 rows change no pre-existing value,
      new fields purely additive.
      **Done.** `FAILURE_FLOOD_SCHEMA_VERSION` bumped 2 → 3 (same no-migrations convention as every prior
      bump in this stack — re-deriving rewrites every existing row with this version and the new field).
      `tool-surface-v1`: **0 mismatches across 42/42 rows**, **zero new fields** (this experiment's own
      row builder, `build_row`, is untouched by this PR — only `build_row_failure_flood` and its module-
      level helpers changed). `failure-flood-v1`: **0 pre-existing value changes across 3/3 rows**; the
      only field-level delta is one purely additive new field, `suite_state_cause`, which is `null` on
      all three (unchanged from `null` because all three rows are `state=void, void_reason=shakedown` —
      the field is gated on `state == "complete"`, matching the existing precedent for
      `verdict`/`integrity_guard_pass`). `causes_claimed`/`causes_correct` are unchanged (`null`) on all
      three for the same reason — void rows are never scored.

**Regression, run exactly as required — tool-surface-v1's 42-row projection, byte-identical**: snapshot
of the committed `rig/results/tool-surface-v1/runs.jsonl` taken before this PR's edits; re-derived with
the final PR7B-bearing `derive.py`. Diffed field-by-field per `run_id`, excluding `schema_version` and
`checker_digest`: **0 mismatches across 42/42 rows**, zero new fields (confirming `build_row` itself is
untouched — the schema_version constant it reads, `SCHEMA_VERSION = 3`, is a SEPARATE constant from
`FAILURE_FLOOD_SCHEMA_VERSION`, unaffected by this PR's bump of the latter).

`rig/results/failure-flood-v1/runs.jsonl` (the 3 already-committed shakedown rows, `state=void,
void_reason=shakedown`, unchanged since PR5) re-derived against the same raw captures still on disk under
gitignored `rig/runs/failure-flood-v1/`: **0 pre-existing value changes across 3/3 rows**; one purely
additive field, `suite_state_cause: null` on all three (never scored — void rows stay void).
`state`/`void_reason` unchanged (`void`/`shakedown` on all three, matching every prior PR's own committed
values).

**No countable run was spent anywhere in this PR.** Every claim above was proven by a synthetic unit test
or a synthetic full-row integration test calling the real `build_row_failure_flood()` — never a real
`claude -p` call. A real (non-`--shakedown`) run remains the operator's decision, per this batch's own
instruction.

**Gate run, on the real staged tree:**
```
$ bash -n rig/run-pipeline.sh
EXIT=0
$ python3 -m py_compile rig/derive.py
EXIT=0
$ python3 rig/collect.py --self-test
  self-test: all cases passed
EXIT=0
$ ./hooks/pre-commit --all
  redaction check: clean across 173 tracked files
EXIT=0
$ ./hooks/pre-commit --self-test
  ok    clean tree, with an empty file and placeholder paths
  ok    an absolute home path is reported
  ok    an unreadable tracked file escalates instead of being skipped
  self-test: all cases passed
EXIT=0
```

**Line budget**: `git diff --cached --numstat` — `rig/derive.py` 141/18 (159 authored), `rig/run-pipeline.sh`
16/0 (16 authored), `rig/results/tool-surface-v1/runs.jsonl` 42/42 (generated golden, same exclusion PR1/
PR5/PR7A already established), `rig/results/failure-flood-v1/runs.jsonl` 3/3 (same exclusion). **Authored
total: 175**, well inside the 800-line ceiling for this batch (and inside PR7A's own 158, since this PR's
two new scoring/classification functions are smaller than PR7A's model-pinning plumbing).

**Out of scope, confirmed untouched**: `git diff --stat -- rig/collect.py rig/report.py` empty — neither
file was touched; `report.py`'s own `diagnostic_precision_recall_table` (task 6.4) needed no change,
exactly as designed — it was already correct and only ever waiting on non-`null` input. No countable
(non-`--shakedown`) run was spent — that remains the operator's own decision, unchanged from PR7A's own
statement of the same constraint.

## PR7C — `derive.py`/`report.py` self-tests (ADR 0013: a committed executable carries its own test)

Depends on: PR7A + PR7B (the two files that received the most new logic this cycle and had no test of
their own). Source: my own PR7B closing note flagged this gap directly — `rig/collect.py` and
`hooks/pre-commit` have `--self-test`; `rig/derive.py`, `rig/report.py` and `rig/run-pipeline.sh` do not,
and PR7B's own 23 unit + 16 integration tests lived only in a session scratchpad about to be discarded,
so that proof would have evaporated with nothing committed to replace it.

- [x] 7.8 Add `--self-test` to `rig/derive.py`, absorbing all three scratch verification scripts (model-
      mismatch void, R-F7.3 token breakdown, `suite_state_cause` + R-F3.2 scoring) that a prior session
      wrote and never committed. Follows `collect.py`'s own `--self-test` convention exactly: same flag
      name, same `run_self_test() -> bool` / per-case `[PASS]`/`[FAIL]` print shape, same
      `main()` dispatch ordering (checked before `--experiment` is validated), same exit-code contract (0
      pass, 1 fail). Fixtures are synthesised in a `tempfile.mkdtemp()` this function creates and removes
      — no dependency on any path outside this repo, other than the real committed
      `rig/surfaces/failure-flood.txt` preimage the pipeline itself reads. Does **not** collide with the
      pre-existing, unrelated `run_self_tests()` (plural — R-A1.4's checker self-test, which already runs
      unconditionally on every real invocation and stays untouched).
      Verify: `python3 -m py_compile rig/derive.py`; `python3 rig/derive.py --self-test` exit 0 with every
      case `[PASS]`; both named regressions re-run clean.
      **Done.** 49 assertions across 7 self-test functions, all real, none mocked — every one caught a
      real fixture bug during this batch's own writing (a missing `prereg_digest` in two of the three
      synthetic-run-directory helpers tripped the Hard Ordering Gate's own `no-preregistration` void before
      the intended check ever ran; a missing `status.json` in the third left every row `state=void,
      void_reason=null`). Fixed by adding `prereg_digest`/`status.json` to the fixture builders, not by
      loosening any assertion. Breakdown: `parse_root_cause_report` 8 cases, `score_diagnostic_attribution`
      6 cases (including the malformed-prose scenario R-F3.2 names by name, plus a hostile binary-byte
      input and a non-ASCII path per corner-case discipline), `suite_state_cause` 7 cases,
      `read_root_cause_report_handoff` 2 cases, `build_row_failure_flood` model-mismatch 3 cases, token
      breakdown 7 assertions in 1 case, and the suite-state/attribution integration suite 4 cases (16
      assertions) against the real committed surface preimage. All 3 scratchpad files' cases survived into
      the committed self-test; none were dropped.
      ```
      $ python3 -m py_compile rig/derive.py
      EXIT=0
      $ python3 rig/derive.py --self-test
        [49 case lines, all PASS — see apply-progress for full verbatim output]

      self-test: all cases passed
      EXIT=0
      ```
- [x] 7.9 Add `--self-test` to `rig/report.py`, covering at minimum the defect caught at PR6 gatekeeping:
      `report_failure_flood` must print all four table headers even when there are zero complete rows
      (the historical bug — green-restore was emitted by a per-key loop that produced nothing on an empty
      collection while its three siblings printed unconditionally). Also covers R-A1.3/R-F4.3 (no
      composite/summed/ANDed field) honestly, not merely asserted by inspection.
      Verify: `python3 -m py_compile rig/report.py`; `python3 rig/report.py --self-test` exit 0; both
      untouched entry points (`rig/report.py` default and `--experiment failure-flood-v1`) still exit 0
      unaffected.
      **Done.** 3 self-test cases, all real: (1) `report_failure_flood([])` captured via
      `contextlib.redirect_stdout` — all four headers ("Diagnostic precision/recall", "Green-restore
      verdict distribution", "Peak occupancy tokens", "Cumulative occupancy tokens") confirmed present on
      an empty row set, the exact regression shape this batch's own instruction named; (2)/(3) R-A1.3/
      R-F4.3: `occupancy_table(rows, field)` proven to report ONLY the requested channel (a peak call's
      output line was checked to carry neither of the cumulative call's own values, and vice versa) and
      `green_restore_table` proven to list exactly its five raw verdict/`unscored` counts side by side,
      never combined with each other or with either occupancy channel. One self-test bug found and fixed
      during writing: a naive `"score" not in line.lower()` substring check false-failed against the
      legitimate field name `unscored` (which contains "score" as a substring) — replaced with an exact
      token-identity check, not a loosened assertion.
      ```
      $ python3 -m py_compile rig/report.py
      EXIT=0
      $ python3 rig/report.py --self-test
        [PASS] all four table headers print on zero complete rows
        [PASS] occupancy_table(rows, field) reports ONLY the requested channel ...
        [PASS] green_restore_table lists exactly the five raw verdict/unscored counts ...

      self-test: all cases passed
      EXIT=0
      ```
- [ ] 7.10 (registered, not implemented this batch — deliberately out of scope) Add `--self-test` to
      `rig/run-pipeline.sh`. A bash test harness is a different construction from a Python
      `--self-test` flag and would exceed this batch's own budget; deferred rather than rushed.
      **The recurrence this task exists to name**: the extracted-function pattern this stack has already
      used three separate times to verify shell logic without a real `claude -p` call — task 6.6's
      `check_prereg()`, PR7A's `read_back_init()`/`hash_paths()` — has been re-invented ad hoc in three
      separate batches instead of being generalised into `run-pipeline.sh`'s own committed, flag-gated
      `--self-test` that runs all three (and any future extracted function) in one place. That
      re-invention, not any single missing test, is the exact recurrence ADR 0013 exists to catch. Next
      batch should build a `--self-test` flag that sources or re-execs the extractable functions and runs
      each of the three (plus any new ones) as one committed suite, rather than a fourth ad hoc script.

**Regression, run exactly as required — both named datasets, byte-identical**: `tool-surface-v1`'s
42-row projection and `failure-flood-v1`'s 3-row projection were both snapshotted before this PR's edits
and re-derived with the final PR7C-bearing `derive.py`. Diffed field-by-field per `run_id`, excluding
`schema_version`/`checker_digest`: **0 mismatches across 42/42 rows**, **0 pre-existing value changes
across 3/3 rows**, **zero new fields on either dataset** (this PR adds no new row fields — it only adds a
CLI flag and self-test functions, neither of which touches `build_row`/`build_row_failure_flood`'s own
output shape).

**No countable run was spent anywhere in this PR.** Every claim above was proven by a synthetic self-test
against a `tempfile`-created fixture or by re-deriving already-committed raw captures — never a real
`claude -p` call. A real (non-`--shakedown`) run remains the operator's own decision, unchanged from every
prior PR's own statement of the same constraint.

**Gate run, on the real working tree (staged before commit):**
```
$ bash -n rig/run-pipeline.sh
EXIT=0
$ python3 -m py_compile rig/derive.py
EXIT=0
$ python3 -m py_compile rig/report.py
EXIT=0
$ python3 rig/collect.py --self-test
  self-test: all cases passed
EXIT=0
$ python3 rig/derive.py --self-test
  self-test: all cases passed
EXIT=0
$ python3 rig/report.py --self-test
  self-test: all cases passed
EXIT=0
$ ./hooks/pre-commit --all
  redaction check: clean across 173 tracked files
EXIT=0
$ ./hooks/pre-commit --self-test
  ok    clean tree, with an empty file and placeholder paths
  ok    an absolute home path is reported
  ok    an unreadable tracked file escalates instead of being skipped
  self-test: all cases passed
EXIT=0
```

**Line budget**: `git diff --numstat -- rig/derive.py rig/report.py` — `rig/derive.py` 344/3 (347
authored), `rig/report.py` 104/3 (107 authored). **Authored total: 454**, well inside the 800-line
ceiling this batch was given. No generated goldens are touched by this PR (neither `runs.jsonl` file
changed — re-deriving produced byte-identical output, so nothing new was staged for either).

**Out of scope, confirmed untouched**: `git diff --stat -- rig/run-pipeline.sh rig/collect.py
hooks/pre-commit` empty — none of the three were touched. Task 7.10 above registers `run-pipeline.sh`'s
own missing `--self-test` rather than implementing it here. The WARNING-level findings from the
2026-08-17 verify-report (placeholder `STEP_TIMEOUT_S`, stale `axis_table.py:19-21` docstring) remain
untouched, out of this batch's scope. No countable run was spent.
