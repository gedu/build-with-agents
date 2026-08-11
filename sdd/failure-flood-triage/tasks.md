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
| 400-line budget risk | **High for PR3 and PR4** (donor-module source size not yet known); Low–Medium elsewhere — see per-PR table below |
| Chained PRs recommended | **Yes** |
| Suggested split | PR1 → PR2 → PR3 → PR4 → PR5 → PR6 (stacked) |
| Delivery strategy | chained PRs, `size:exception` NOT taken |
| Chain strategy | **stacked-to-main** — PR1 targets `main`; each subsequent PR targets the previous PR's branch |

```text
Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High
```

**Decision needed before apply — both resolved 2026-08-11, so apply is unblocked:** (1) the per-module
axis-table amplification target proposed in PR3.3 (below) is **operator-confirmed**. R-F9.2 still binds:
the achieved ratio must be measured per run and never assumed — confirming a target does not license
assuming the outcome. (2) The named contingency split for PR3/PR4 (below) is **pre-authorized** and
applies without a further decision if their real authored diff exceeds 400, since real donor-module
source length is unknown until the modules are actually copied in.

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

- [ ] 1.1 Modify `rig/derive.py`: walk `assistant` stream events, de-duplicate by `message.id` (keep
      first occurrence in stream order), build the per-turn `occupancy_series`.
      Verify: `python3 -m py_compile rig/derive.py`.
- [ ] 1.2 Add fields to `tool-surface-v1` rows: `model_turns`, `occupancy_series`,
      `peak_occupancy_tokens` (max over series), `peak_occupancy_turn`, `cumulative_occupancy_tokens`
      (sum over series + output), `occupancy_aggregate_matches` (cross-check vs `result.usage`),
      `occupancy_is_monotone`, `context_window_tokens`. Bump `tool-surface-v1` `schema_version` 2 → 3.
      Verify: re-derive all 42 existing rows; project out `schema_version`, `checker_digest`, and every
      new key; every remaining byte identical to the pre-change row (the achievable claim per design's
      correction — anything stronger chases `checker_digest`'s self-hash, which changes on any edit).
- [ ] 1.3 Confirm `occupancy_aggregate_matches: true` on all 42 rows; then, on one **copied** capture
      (never the committed one), mutate one turn's usage and confirm the mismatch anomaly fires.
      Verify: manual before/after diff of the anomaly field on the copy only.
- [ ] 1.4 Record whether `occupancy_is_monotone` is `true` on all 42 rows or diverges anywhere.
      This is the R-F5's "settle before any new spend" gate — its result is read, not assumed, before
      PR3 begins. Verify: value present and non-null on every row.
- [ ] 1.5 Create `decisions/0014-a-fixtures-runtime-is-substrate-not-this-repos-runner.md`. Clause A:
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

## PR2 — Collector + signature normalizer

Depends on: PR1 (independent content, sequenced by the stack). Blocks: PR3, PR4 (both need the
collector to validate fixture/injection signatures).

- [ ] 2.1 Create `rig/collect.py` (`python3`, stdlib only). Invokes the suite itself, pinned
      `--runInBand` + JSON report file. Emits `collection/1` (suite state, totals, `failures`,
      `clusters`, `identifier_set_digest`).
      Verify: `python3 -m py_compile rig/collect.py`.
- [ ] 2.2 Implement the three suite states (`ran` / `did-not-start` / `partial`) decided from evidence
      (report parseable + count check), plus `collector-error` as a **run-axis void**, never a suite
      state (absent/underfloor toolchain, install missing, lockfile mismatch, collector's own crash).
      Verify: synthetic Jest-JSON fragments inlined in the file (no fixtures directory, per ADR 0013)
      exercise all four outcomes.
- [ ] 2.3 Implement the normalizer: relative `test_id`, signature over the first-failure message
      truncated at the first stack line, fixed-order normalization (ANSI/CRLF/whitespace/path/line:col),
      matcher-shaped-head-only `signature_text`, `sha256(...)[:16]`. Deterministic cluster ordering
      (`count desc, signature asc`).
      Verify: `rig/collect.py --self-test`, cases (a)–(e):
      (a) same cause, differing path/line/order → same signature;
      **(b) two genuinely different causes → different signatures — the discrimination case a
      constant-returning normalizer would fail, and the one everyone forgets to write**;
      (c) each of the three suite states fires from a synthetic report;
      (d) same input twice → byte-identical output;
      (e) absent toolchain → `collector-error`, never a suite state.
- [ ] 2.4 Confirm the `--self-test` flag is gated (never runs unconditionally inside a measured arm,
      unlike `derive.py`'s unconditional self-test — a different, correctly-not-reused pattern per
      design's correction #3).
      Verify: `rig/collect.py` with no flag prints/does nothing beyond normal collection; `./hooks/pre-commit --all`.

## PR3 — Clean fixture + case generator (3a)

Depends on: PR1 (ADR must exist — R-F11 scenario), PR2 (collector validates the clean baseline).

- [ ] 3.1 Create `rig/fixtures/failure-flood/v1/{src,tests,runtime}/**` — stage-1 clean substrate
      (donor modules hosting 3 of the 6 root causes), author-authorized real code per the proposal's
      recorded authorization. `package.json` + `package-lock.json` under `runtime/`.
      Verify: **the fixture's own Jest run** (`npm ci && npx jest --runInBand`) reports zero failures —
      a non-zero clean baseline voids the fixture, not the run.
- [ ] 3.2 Create `rig/fixtures/failure-flood/v2/{src,tests,runtime}/**` — stage-2 clean substrate, same
      six root-cause-hosting modules, same clean behavior as v1 where modules overlap.
      Verify: same Jest run, zero failures, on v2.
- [ ] 3.3 Create `tools/generate-cases.py` + its axis table (Decision 9a — commit the generator, not the
      expanded tables). **Per-module sizing (R-F9.2's design/tasks deliverable) — operator-confirmed
      2026-08-11; R-F9.2 still binds, so the achieved ratio MUST be measured, never assumed:**
      target amplification ~30–35× each module's existing real case count,
      mirroring spec Decision B's two worked examples (15 → ~500 rows, 13 → ~400 rows), for an aggregate
      stage-2 corpus on the order of ~2,500–3,000 generated failing cases across the 6 modules
      (≈415–500 : 1 against 6 causes — a stated comparison to the real incident's ~500:1, per R-F9.2,
      not an assumption).
      Verify: `python3 -m py_compile tools/generate-cases.py`;
      `tools/generate-cases.py --self-test` — byte-identical output across two runs **and** across two
      orderings of its input (no clock, no RNG, sorted keys, `\n` endings).
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
