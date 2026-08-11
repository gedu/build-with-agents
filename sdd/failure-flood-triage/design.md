---
id: sdd/failure-flood-triage/design
type: journal
targets: [any]
status: draft
verified: 2026-08-11
sources: ["sdd/failure-flood-triage/proposal.md", "sdd/failure-flood-triage/exploration.md", "sdd/measurement-rig/design.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "rig/run.sh", "rig/derive.py", "rig/report.py", "rig/README.md", "rig/fixtures/tool-surface/v1/answer-key/t1.json", "rig/results/tool-surface-v1/runs.jsonl", "OPERATIONS.md", "hooks/pre-commit", ".gitignore", "skills/hypothesis-cycle/SKILL.md", "skills/source-verdict/SKILL.md"]
---

# failure-flood-triage — design: a second experiment that does not disturb the first

SDD design phase for `failure-flood-triage`. Architecture and decisions only. No task breakdown, no
implementation.

Bounded by the proposal's settled decisions (sibling runner, model held fixed, two unsummed outcome
channels, author-authorized fixture code, five-slice order) and by ADR 0013's verification surface:
`hooks/pre-commit`, `bash -n`, `python3 -m py_compile`, and each executable's own self-test.

**Three claims in the inputs did not survive contact with the code.** They are corrected in the
decisions where they bite and collected at the end, because two of them change what slice 1 must
build and one changes how slice 4 can be verified.

## Technical approach

Two experiments, one directory tree, **one instrument seam moved and nothing else**.

`rig/run.sh` is untouched. A sibling `rig/run-pipeline.sh` owns the multi-invocation arm. `derive.py`
and `report.py` gain an `--experiment` dispatcher and a second row builder; the `tool-surface-v1`
code path is byte-verified unchanged over its 42 existing rows. A new `rig/collect.py` is the
plain-code collector and signature normalizer, and it is the only new program a measured arm invokes —
the case-table generator (Decision 9a) runs in preflight, outside every arm and outside every context.

The property that makes the multi-step arm fit a schema built for single invocations is arithmetic,
not engineering:

> **Peak is a max and cumulative is a sum. Both compose over steps.** `peak(arm) = max(peak(step))`,
> `cumulative(arm) = Σ cumulative(step)`. So per-step records are sufficient, and no cross-step
> reconstruction pass is needed anywhere.

## 1. Peak occupancy comes from a de-duplicated per-turn series, and the series is committed

Measured directly from two of the 42 local captures (raw captures are gitignored per ADR 0011, so
these figures are stated for whoever holds them, and every one is reproducible from the committed row
they are compared against):

| Capture | `assistant` events | distinct `message.id` | per-turn `cache_read` | committed row's `cache_read_input_tokens` |
|---|---|---|---|---|
| `t3v2-broad-13` | 14 | **4** | 16602 → 39942 → 40854 → 43736 | **141134** = the exact sum |
| `t3-broad-03` | 6 | **3** | 16602 → 39833 → 40735 | **97170** = the exact sum |

Three consequences, and the first two are corrections.

**One model turn emits several `assistant` events, each echoing the same `message.usage`.** In
`t3v2-broad-13`, lines 4/5/6 carry byte-identical usage and one shared `message.id`. A per-event sum
would over-count by ~3.5×. `derive.py` already walks these events (`elif t == "assistant":`, line
173) for `tool_use` blocks and discards their usage (the row is built from `result_event` only, lines
441–447). The new walk **de-duplicates by `message.id`**, keeping first occurrence in stream order.
Max is duplicate-safe, so peak alone would not need this; the series and every sum do, and deriving
everything from one de-duplicated series is what stops the two channels from being computed by two
different rules.

**Cumulative occupancy is already on the committed row, so slice 1 is only about peak.** The `result`
event's `usage` is an *aggregate over turns*, not the final turn: 141134 is the sum, verified twice.
The row's `input_tokens + cache_read_input_tokens + cache_creation_input_tokens` (7 + 141134 + 27894
= 169035 for `t3v2-broad-13`) **is** the cumulative channel today. The proposal's risk 1 is correct
about peak and over-broad about cumulative.

Slice 1 adds cumulative anyway, computed independently from the series — **because the redundancy is
the detector**. Two paths to one number, and disagreement is `occupancy-aggregate-mismatch`, which is
the R-A1.4 proof this channel can fire, obtainable with no run and no model call.

**There is a `contextWindow` field, and it is a constant, not a reading.** `result.modelUsage[model]`
carries `contextWindow: 1000000` and `maxOutputTokens: 64000` — the window's *size*. `result.usage`
also carries an `iterations` array, but it holds exactly **one** entry (the final message), not a
per-turn history. So the proposal's honesty contract holds as written — occupancy remains a measured
proxy — but for a sharper reason than "the CLI exposes no field": it exposes the denominator and not
the numerator. Record `context_window_tokens` on the row so the proxy can later be expressed as a
fraction without re-parsing.

**Why `input + cache_read + cache_creation` is the right proxy**: those three fields partition the
turn's prompt, so their sum is the prompt size regardless of cache state — which matters here because
a pipeline's later steps are fresh sessions with different cache behaviour. Output tokens are excluded
from occupancy and counted once, as next turn's input, so nothing is double-counted.

### The schema bump, and what "pre-existing rows unchanged" can actually mean

| Option | Tradeoff | Decision |
|---|---|---|
| Store only `peak_occupancy_tokens` | Smallest row. But raw captures are not committed, so a committed peak with no committed series is a number **no reader of this repo can check** — the exact failure ADR 0011's citability split exists to prevent | Rejected |
| Store the full per-turn series | Rows grow by 3–14 integers | **Chosen.** Integers only: redaction-safe by construction, and the peak becomes auditable from the repo alone |
| Bump the shared schema for both experiments | Forces `tool-surface` rows to carry null pipeline fields, i.e. the generalisation the proposal deferred | Rejected |
| **`schema_version` is per-experiment** | Two numbers to keep straight | **Chosen.** `tool-surface-v1` goes 2 → 3; `failure-flood-*` starts at its own 1 |

New fields on `tool-surface-v1` rows: `model_turns` (distinct `message.id` count — deliberately not
conflated with `num_turns`, which was 10 against 4 turns), `occupancy_series` (per-turn integers),
`peak_occupancy_tokens`, `peak_occupancy_turn`, `cumulative_occupancy_tokens`,
`occupancy_aggregate_matches`, `occupancy_is_monotone`, `context_window_tokens`.

`occupancy_is_monotone` is not decoration. In both sampled captures the series rises monotonically, so
peak was simply the last turn — which would make peak and cumulative far less independent than the
proposal's "different failure modes" framing assumes. Over 42 rows this boolean answers that for free,
before any new spend, and it is exactly `skills/hypothesis-cycle` Step 1 check 4 applied to
`hypotheses/0002`.

**The byte-stability check must exclude two fields, or it fails for the wrong reason.** `derive.py`
sets `CHECKER_DIGEST = sha256(own bytes)` (line 78) and stamps it on every row, so editing `derive.py`
*necessarily* changes `checker_digest` on all 42 rows. The verifiable claim is therefore:

> Re-derive; for every row, project out the new keys, `schema_version`, and `checker_digest`. Every
> remaining byte is identical across all 42 rows.

Anything stronger is not achievable and would send slice 1 chasing a phantom.

## 2. One `run_id` per arm-run, with per-step sub-records

| Option | Tradeoff | Decision |
|---|---|---|
| One `run_id` per model invocation | `report.py` pairs by `(task_id, iteration)`; the hypotheses compare *arms*. Whole-arm peak would need a join `derive.py`'s total-function shape does not have | Rejected |
| One `run_id` per arm-run, steps as sub-records | The row grows a nested array | **Chosen.** Compositionality (above) makes it sufficient |
| A second runner per role | Three drivers, three exit contracts, one experiment | Rejected |

`run_id = <task_id>-<arm>-<iteration>` is unchanged, so the existing grammar is reusable per
experiment. Arms are `monolithic` and `pipeline`. On-disk layout:

```
rig/runs/failure-flood-v1/<run_id>/
├── status.json                       # arm-level sentinel: state, void_reason, exit_code, wall_ms
├── arm.json                          # ordered step manifest, prereg digest, toolchain versions
└── steps/
    ├── 01-collect/    result.json  status.json          # plain code. tokens recorded as 0, not absent
    ├── 02-diagnose/   prompt.txt  stream.jsonl  status.json  handoff/fix-plan.txt
    ├── 03-apply/      prompt.txt  stream.jsonl  status.json
    └── 99-verify/     result.json  status.json          # scoring collection. NOT part of arm cost
```

MONOLITHIC is one model step (`01-monolith`) plus `99-verify`. The collector is a PIPELINE component;
the **scoring** collection at `99-verify` runs in both arms, is performed by the harness, and is
excluded from every cost and occupancy figure. Recording a collector step with explicit `tokens: 0`
rather than omitting it keeps the "zero model tokens" claim read back rather than asserted, and stops
a sum from silently skipping a step.

**Threading the fix-plan, and the cheat it has to close.** The diagnostician's only writable place is
its workspace, so it writes `fix-plan.txt` at the workspace root. The harness then copies it out to
`steps/02-diagnose/handoff/`, hashes it as `handoff_sha256`, and **materialises a fresh workspace for
the applier** from the frozen fixture plus that one file. Fresh, not inherited: otherwise incidental
diagnostician edits would silently change what the applier was shown, which is the one variable under
test.

**No repository is materialised for any role, in either arm** — settled by the spec, and wider than the
original hardening item, which named only the diagnostician and thereby left the applier as a side
door. So `git apply` does not exist and every application is a direct file write. The applier's contract
is therefore `fix-plan/1`'s `target_paths` plus a write tool, with no patch format anywhere in the
pipeline.

That creates a real hazard the proposal does not name. The settled rule is that the tool surface is
**identical across arms and roles**, so the diagnostician *can* edit source — and if it does,
PIPELINE has collapsed into MONOLITHIC while still reporting two cheap steps. The surface stays
identical (narrowing it would be the second variable the proposal correctly forbids); instead the
violation is **detected**: the diagnostician's workspace is re-hashed against its materialised file
list, and any change to `src/` sets arm state `failed`, not `void`. This reuses `run.sh`'s verified
mutation instrument in the one role where a write tool is present but writing is illegitimate.

**The permission mode must be declared, not inherited — and today it is inherited.** All 42 committed
rows record `permission_mode: "bypassPermissions"`, and `run.sh` passes no permission flag anywhere.
The mode came from the ambient environment. That was harmless for an experiment where no arm had a
write tool; here, whether `Bash` and the write tool actually *execute* depends on it, so an inherited
value makes the arms non-reproducible from a plain terminal and turns a shell prompt into a measured
"failure". `run-pipeline.sh` therefore sets the permission mode explicitly, records it, and voids
`permission-mode-mismatch` when the read-back `init.permissionMode` differs from the declared value —
the same preimage-not-flag-string discipline as the surface check.

**The new surface preimage.** `run.sh`'s `BASELINE_DISALLOW="Bash"` (line 330) does not move; it is
load-bearing for its own experiment, where `Bash` subsumes `Glob`/`Grep`. `run-pipeline.sh` carries
its own baseline, both arms need `Bash` and a write tool, and one preimage is captured under
`rig/surfaces/failure-flood.txt` with `--strict-mcp-config` (required in both arms, Amendment 3) and
committed. It is captured **twice and compared** before being committed — the discipline that found
Amendment 3. `init.tools` is read back **per invocation**, so a three-step arm produces three surface
digests and any disagreement voids the whole arm `surface-mismatch`.

## 3. The collector is `python3`, invokes the suite itself, and separates the run axis from the suite axis

| Option | Tradeoff | Decision |
|---|---|---|
| Node collector | Parses Jest JSON natively. But **a Node collector cannot report that Node is broken**, and "suite did not start" is a required state | Rejected |
| `python3`, stdlib only | Parses JSON produced by a subprocess it launched | **Chosen.** Already an authorised rig prerequisite (ADR 0011); the failure it must report is upstream of it |
| Parse a report file someone else produced | The collector could not distinguish "no report" from "not run" | Rejected. It owns the invocation |

Invocation is pinned to `--runInBand` and a JSON report file. Single-worker execution removes worker
count and interleaving as nondeterminism sources **at the source**, which is cheaper and more honest
than normalising them away afterwards.

### Three suite states, decided from evidence, plus a fourth outcome that is not a state

| Outcome | Decided by | Axis |
|---|---|---|
| `ran` | report parseable and `tests_reported > 0` | suite — **counted** |
| `did-not-start` | no parseable report, or zero tests reported, **with the toolchain present and the fixture frozen** | suite — **counted**. This is a measurement, and the config injection exists to produce it |
| `partial` | report parseable but reported suite count < the frozen expected count, or the runner died mid-report | suite — **counted** |
| `collector-error` | `node`/`npm` absent or below floor, install missing, lockfile digest mismatch, collector's own crash | **run axis — `void`, never a suite state** |

That table is hardening item 3 made mechanical. The distinction is decidable, not a judgment call: a
non-start with a present toolchain and a matching manifest is the fixture behaving as frozen; a
non-start with an absent toolchain is the environment, and the run never happened.

### The normalizer, and the direction of its self-test that nobody writes

Named nondeterminism sources: the `mktemp` workspace path, worker scheduling, suite and test ordering,
durations, ANSI colour, stack-frame line/column numbers, and per-case expected/received values.

Algorithm, total and ordered:

1. `test_id = <test file path relative to workspace root> :: <ancestor titles joined " > "> :: <title>`. Relative kills the random path.
2. Signature input = the first failure message, **truncated at the first stack line** (`^\s+at `). Stack frames carry paths and line numbers and nothing else of value.
3. Normalise in fixed order: strip ANSI, normalise CRLF, collapse whitespace runs, rewrite any surviving workspace-absolute path to its relative form, rewrite `:<digits>:<digits>` to `:L:C`.
4. `signature_text` = the **matcher-shaped head** only (error class plus matcher), never the expected/received body — those vary per case *within* one cause, and a signature that varies per case is not a cluster key. `signature = sha256(signature_text)[:16]`, with `signature_text` kept in plain text on the record so the clustering is auditable.
5. Total order: records by `test_id`; clusters by `(count desc, signature asc)`. `cluster_id` is assigned from that rank, so it is deterministic and stable.

`rig/collect.py --self-test` is flag-gated (ADR 0013's ratified shape — the flag lives on
`hooks/pre-commit`, line 149, and `OPERATIONS.md`'s decision table) rather than unconditional, because
the collector runs K times inside a measured arm and must not print or pay on every invocation. Cases,
and **case (b) is the one that gets skipped**:

| # | Case | Why |
|---|---|---|
| a | Two failures differing only in absolute path, line/column and order → **same** signature | Determinism |
| b | Two failures with genuinely different causes → **different** signatures | **A normalizer returning a constant passes (a) perfectly.** Without this direction the whole cluster channel can be silently dead |
| c | Each of the three suite states fires from a synthetic report | R-A1.4 |
| d | Same input twice → byte-identical output | Idempotence, the property `derive.py` already holds |
| e | Absent toolchain → `collector-error`, not a suite state | The axis separation above |

Synthetic Jest-JSON fragments are inlined in the file, per ADR 0013's no-fixtures-directory rule.

## 4. Domain-neutral schemas — and the exact-match device that makes the primary channel gradeable

No schema *name* contains a tool name; the tool appears only as a recorded **value** (`collector:
"jest-json@1"`), so a later `tsc` or lint collector is a new plugin, not a schema change.

```json
// failure/1  — deliberately minimal. At amplified scale there are thousands of these,
//              so signature_text lives once per cluster and never once per failure.
{"test_id": "<relpath>::<suite path>::<title>", "status": "failed", "signature": "<16-hex>"}

// cluster/1   (signature/1 is the {signature, signature_text, count} projection)
{"cluster_id": "c1", "signature": "<16-hex>", "signature_text": "<normalized head>",
 "count": 12, "representative_test_id": "<test_id>", "member_test_ids": ["<test_id>", "..."]}

// collection/1  — the envelope, and the integrity guard's cheap half
{"schema": "collection/1", "suite_state": "ran|did-not-start|partial",
 "collector": "jest-json@1", "normalizer_version": 1,
 "totals": {"tests": 138, "passed": 88, "failed": 50,
            "suites_expected": 18, "suites_reported": 18},
 "identifier_set_digest": "<sha256 over sorted test_ids>",
 "failures": ["<failure/1>"], "clusters": ["<cluster/1>"],
 "diagnostics_head": "<normalized startup error, only when did-not-start>"}

// fix-plan/1
{"schema": "fix-plan/1",
 "causes": [{"cause_id": "r1", "cause_site": "<relpath>:<line>",
             "cause_label": "<free text — recorded, never graded>",
             "cluster_ids": ["c1", "c4"], "target_paths": ["<relpath>"]}]}
// No patch field, by decision: no repository is materialised for any role in either arm,
// so `git apply` does not exist and target_paths is the applier's whole addressing mechanism.
```

`identifier_set_digest` is what makes the integrity guard cheap: compare it to `C`'s digest and a
deleted, renamed or skipped test is caught in one comparison.

**The root-cause report format is frozen in the spec, and it reuses the `<path>:<line>` exact-match
device.** Both arms emit, in their final assistant text, lines of the frozen form:

```
CAUSE <path>:<line> <cluster_id>[,<cluster_id>…]
```

`<path>:<line>` is the cause *site*, graded by set comparison against `R0` exactly as the prior
experiment graded defect lines — the same deterministic device, already verified in `derive.py`'s
`DEFECT_LINE_RE` path, which is why this design's own closed-vocabulary proposal is superseded rather
than argued for.

| Option | Consequence | Decision |
|---|---|---|
| Free-text root causes | Scoring needs a judgment call about whether two phrasings mean one cause. ADR 0010 constraint 1 forbids exactly this | Rejected |
| A closed label vocabulary with distractors (this design's earlier choice) | Gradeable, but introduces a vocabulary whose size sets a chance baseline that then has to be disclosed and defended | **Superseded.** The site device needs no vocabulary, so it needs no baseline disclosure |
| **`<path>:<line>` cause sites plus cluster ids** | The site space is every source line, so shotgunning is possible | **Chosen** (spec-frozen). Precision bounds shotgunning, exactly as in the prior experiment. A free-text label may accompany a line; it is **recorded and never graded** |

`R0` is a **many-to-one cluster → cause-site mapping**, measured in slice 3b rather than asserted: one
injection may legitimately produce several signatures, and the key records how many.

Precision and recall are computed identically in both arms from these lines, and published as a pair —
never an F-score (`R-A1.3`). `causes_present` counts distinct sites in `R0`; `clusters_present` counts
the signatures they map to. The two are reported side by side so a cause that fragmented under
amplification is visible rather than silently penalised.

## 5. The fixture's runtime is lockfile-pinned, installed per run, and never enters a hash by a directory walk

| Concern | Mechanism |
|---|---|
| Install | `npm ci`, never `npm install`. `ci` installs exactly the lockfile and fails when `package.json` and the lock disagree — that failure *is* the reproducibility check |
| Pinning | `package.json` + `package-lock.json` committed under a fixture `runtime/` path, inside the MANIFEST. `lockfile_sha256` on the row |
| Version drift | `node --version` / `npm --version` recorded on the row; a declared major floor enforced in preflight. Recorded, not frozen — freezing a machine's Node version would brick the fixture on every upgrade |
| Missing toolchain | Preflight `exit 2` before any run directory is claimed. No row, no partial arm. Mid-arm loss is `void: collector-error`, per Decision 3 |
| The cheat vector | `runtime/`, `tests/` **and the generated case tables** are read-only substrate; only `src/` is writable. Editing `package.json`, a test, or a case row to reach green is `regressed`. The case tables matter most here: at amplified scale they hold every expectation, so an unguarded table is the cheapest possible cheat |
| `.gitignore` | No change. Blanket `node_modules/` at line 19 already covers it; `/rig/runs/` at line 40 is the precedent for a rig-local uncommitted directory, both outside `setup.sh`'s managed block |

**`node_modules` lives outside the repo and is reached by a symlink into a per-run install directory.**
Copying thousands of files per step is not affordable; symlinking into the *committed* fixture tree
would let the agent's shell write through it and leak across runs. A per-run, machine-local install
directory has neither problem, and it is thrown away with the workspace.

**One concrete correction for whoever implements it.** `run.sh`'s file-list instrument is the right one
to reuse, but not as written: `list_fixture_files()` (line 147) is `find . -type f`, which would
descend into `node_modules` and make every hash both enormous and dependent on the install. The list
must be built from the **manifest's own path set**, captured before the symlink exists.

## 6. Two experiments, one deriver, dispatched — and the slice order is what makes that safe

| Option | Tradeoff | Decision |
|---|---|---|
| Duplicate `derive.py` | Zero risk to the verified path, but two files that must both stay *total*, drifting independently | Rejected |
| A second file importing shared helpers | Cleanest isolation; creates an import dependency between two programs that must both be total functions | Second best. Recorded, not chosen |
| **`--experiment` dispatcher, per-experiment registry, two row builders** | Touches a verified file | **Chosen** |

The deciding argument is the slice order, not taste: **slice 1 already edits `derive.py`** for the
occupancy fields, and its verification is the 42-row projection check. By the time slice 4 needs the
dispatcher, that check exists and re-runs. Adding the dispatcher behind an already-established
regression check is cheaper than maintaining a second total function. `build_row` for `tool-surface`
is not restructured; the registry holds `(runs root, fixture roots, run-id grammar, arm names, row
builder)`.

`report.py` takes the same dispatcher, per-experiment arm names, and four new tables that are never
combined: diagnostic precision/recall pairs, the green-restore verdict distribution, peak occupancy,
and cumulative occupancy. Dollar cost keeps its existing separate table and is not the lead.

## 7. Pre-registration is a preflight guard, not a convention — and the convention it replaces is already broken

The proposal's guard is that slice 4's shakedown runs under `--dirty-ok`, which stamps
`void_reason=dirty-tree`. **Read against the code, that does not hold.** `run.sh` lines 463–466:

```bash
if [ "$DIRTY_OK" -eq 1 ] && [ -n "$DIRTY" ]; then
  STATE="void"
  VOID_REASON="dirty-tree"
fi
```

The void stamp is conditional on the tree *actually being dirty*. `--dirty-ok` on a clean tree stamps
nothing and produces a fully countable row — and slice 4's shakedown runs after slice 4 is committed,
i.e. on a clean tree. The proposal's mechanism would have permitted exactly the countable-run-before-
pre-registration it was written to prevent. Three layers replace it, none of which anyone can forget:

| Layer | Where | Effect |
|---|---|---|
| The required list is frozen in the fixture | `answer-key/prereg.json`, inside the MANIFEST | The list of required hypothesis files cannot be quietly shortened without an exit-2 manifest mismatch |
| Preflight, same class as the manifest check | `run-pipeline.sh` | Every listed path must exist, be git-tracked and be clean. Otherwise **exit 2**. Records `prereg_digest` |
| The row cannot be counted without it | `derive.py` | A row with `prereg_digest: null` is `void: no-preregistration`; `report.py` already excludes voids and names them |

Before slice 5 the hypothesis files do not exist, so layer 2 refuses to launch at all — structurally
impossible, not forbidden. Slice 4's shakedown therefore needs its own exit, and it is a dedicated
`--shakedown` flag whose **only** meaning is "this run is uncountable": it skips the prereg preflight
and stamps `void_reason=shakedown` **unconditionally**, with no dependence on tree state. That is the
hole above, closed by construction rather than by remembering a flag.

`run.sh` keeps its conditional stamp. Its experiment is closed, changing it is out of scope, and it is
recorded here as a latent follow-up rather than silently fixed.

## 8. Stage 1 and stage 2 are two fixture versions, which makes the pre-registered exclusion structural

Stage 1 (10 cases, 3 causes, shakedown) is `task_id: s1` on `failure-flood/v1`. Stage 2 (50 cases, 6
causes, the comparison) is `task_id: s2` on `failure-flood/v2`, injected into the same clean substrate
and frozen separately. This is the existing precedent exactly — `t3` on `v1`, `t3v2` on `v2`, "the
version a task_id names is fixed at the moment that task_id is introduced".

The payoff is that the proposal's pre-registered exclusion stops being a promise. `report.py` pairs by
`(task_id, iteration)`, so stage-1 rows **cannot** enter a stage-2 table: different `task_id`,
different `fixture_digest`, and the aggregator already refuses to merge across a `fixture_digest`
difference. Re-deriving the 0.6 cumulative constant from stage 1 is then provably not post-hoc metric
selection.

## 9. Amplification: the flood is table-driven, and the freeze becomes a digest

Resolved by the operator: stage 2 is **table-driven parameterization of the real donor modules** — same
six root causes, same real logic, hundreds to thousands of failing cases. Raising stage 2 only to the
donor ceiling was rejected, and the deciding evidence is a number this design put on the row:
`context_window_tokens` is **1,000,000**, so ~138 cases may not stress the MONOLITHIC arm at all. A
null there is the same failure mode that left `measurement-rig` PARTIAL, which is the outcome the whole
change exists to avoid.

Four consequences, each decided rather than absorbed.

### 9a. Committed bytes versus generated bytes — the crux

First, what "table-driven" does to the byte count: the amplification lives in **data tables consumed by
one `it.each` per module**, not in thousands of test files. So the real choice is not "thousands of
files or a generator" — it is **one large committed table or one small committed generator**.

| Option | Tradeoff | Decision |
|---|---|---|
| Commit the expanded tables | `MANIFEST.sha256` covers them and immutability is literal. But ~3,000 rows × ~100 B ≈ 300 KB of authored additions that no reviewer will read, landing in the slice already sitting **at** the 400-line budget | Rejected |
| Generate at install with no committed expectation | The manifest cannot cover bytes that do not exist, so the fixture's immutability guarantee weakens silently — precisely the named hazard | Rejected |
| **Commit the generator, its axis table, and the expected output digest** | A reader must run one deterministic program to see the bytes | **Chosen. The freeze becomes a digest, and a digest inside the MANIFEST is exactly as strong as the bytes it stands for** |

Mechanism:

- `tools/generate-cases.py` and its axis table are committed and **manifest-covered**, so the recipe cannot change without an exit-2 mismatch.
- `answer-key/case-table.sha256` holds the expected digest of the generated output. It is **inside the manifest**, so it cannot be edited to match a tampered generation — that ordering is what carries the whole guarantee.
- Generation runs into the per-run machine-local root outside `<repo>` (where `npm ci` already installs), then the digest is compared. Mismatch is **exit 2**, the same class as a manifest mismatch. `.gitignore` needs no change, for the same reason the install needed none.
- Determinism is by construction, not by hope: no clock, no RNG, no iteration over unordered input, output written with sorted keys and `\n` endings. Its `--self-test` asserts byte-identical output across two runs **and** across two orderings of its input.

Two rules this forces into the open, each generalising something already true:

| Rule | Why |
|---|---|
| Manifest paths split into **materialised** (`src/`, `tests/`, `runtime/`, generated cases) and **never-materialised** (`prompts/`, `answer-key/`, `tools/`) | The generator describes the injection structure and must not be visible to the agent. This is the existing "`answer-key/` is never inside cwd" rule, stated once as a general split instead of one special case |
| The hash file set comes from the manifest path set plus the generated case paths — **never a directory walk** | Already required by `run.sh:147`'s `find . -type f` descending `node_modules`; the generated tables make it doubly required |

The generated tables are derived from **clean** behaviour, so they are byte-identical between the clean
fixture and the injected one. That is what keeps `C` and `F0` comparable, and it means an agent reading
a case table learns the suite's expectations — which it could already do by reading the tests — and
nothing whatsoever about the injections.

### 9b. Collector scale

Magnitude, stated rather than assumed: ~2,500 failing cases at a message-plus-stack of roughly 1.5–4 KB
puts the Jest JSON report at **order 5–20 MB**. `json.load` handles that in well under a second at
roughly 10× peak RSS, so **streaming is not needed**, and building a chunked parser for it would be
infrastructure ahead of content. What is needed instead:

- `report_bytes` on the row, plus a **declared ceiling** above which the collector exits 2 `collector-error: report-too-large` rather than thrashing silently. A guessed streaming parser is replaced by a stated bound and an honest refusal.
- **Two artifacts, not one.** The full `collection/1` is written to the run directory for scoring; a **bounded clusters view** — clusters, counts, one representative each — is what the diagnostician receives. It is bounded by cluster count, not failure count, and that bound *is* the pipeline's mechanism, so it must be its own artifact rather than a slice of a large one.
- The three suite states survive unchanged and gain one at-scale sub-case: `partial` with `partial_reason: suite-timeout`. That needs its own bound — **the suite's timeout is separate from, and smaller than, the arm's** — derived from a measured clean-fixture wall (×3, floor stated, the rig's existing derivation rule) and recorded as `suite_timeout_s`. Without the separation, a slow flood and a hung agent are indistinguishable. A suite timeout on the **clean** baseline voids the fixture at the 3a gate; during an arm it is `partial`, a measurement.
- `--runInBand` holds. A few thousand pure-function cases run in seconds single-threaded, and single-worker is what removes scheduling nondeterminism at the source rather than normalising it away.

### 9c. Normalizer cost and determinism at scale

Clustering is **exact-signature grouping in one pass — O(n), no pairwise comparison, no similarity
metric, no threshold.** At 2,500 failures a similarity clusterer would be ~3M comparisons *and*
nondeterministic under tie-breaking; hash grouping is neither, and it stays a total function.
Normalising 2,500 heads of ~200 characters is milliseconds, so "zero model tokens" survives the
scale-up literally rather than approximately.

Flag-gated `--self-test` is confirmed, and amplification strengthens the reason: the collector is
invoked K times per arm and each invocation now also **runs a large suite**, so a self-test on every
invocation would add real wall time inside a measured arm.

**Amplification is also what makes the head-only signature rule load-bearing rather than tidy.**
Table-driven cases differ in their expected and received values, so a signature taken over the message
*body* would shatter one root cause into hundreds of clusters and destroy the cluster counts the
diagnostician is shown. Taking only the matcher-shaped head is what keeps a cause's cluster count
small — and where a cause genuinely produces several heads (a throw carrying a parameter value), slice
3b **measures** that count and `R0` records the many-to-one mapping. The key absorbs it; the algorithm
does not change.

### 9d. What MONOLITHIC receives, and the pre-digestion that would destroy the comparison

MONOLITHIC's workspace is the injected `src/`, the tests, the runtime, the generated case tables, a
`node_modules` symlink, `Bash`, and a write tool. **It runs the suite itself and encounters the real
output.** The harness performs no collection before or during that arm; the only collector invocation
is `99-verify`, after the arm has terminated, and its output never enters the arm's context. Nothing
truncates, caps, summarises or pre-digests the flood for that arm — **doing so would silently convert
MONOLITHIC into PIPELINE and delete the experiment.**

The corollary must not be suppressed: the arm **has a shell**, so a monolithic agent may invent its own
triage — `--onlyFailures`, a pipe through `head`, a `grep`. That is a legitimate and interesting outcome
of the harness shape under test, and it has to be observable rather than prevented. `bash_call_count` is
recorded per step; the command strings stay in the gitignored capture, per ADR 0011's path rule. If
self-triage happens often, the result is about *one agent with a shell* versus *a fixed pipeline*, and
the report must say so rather than reading it as pipeline superiority.

If the raw flood exceeds the window, that is the measurement: a high peak on a `complete` row, or
`void: timeout` if the agent never terminates. There is deliberately **no** special "flood too large"
state, because inventing one would let the harness decide the quantity being measured.

## The fixture/repo boundary ADR — approved, and what it must settle

**Approved by the operator: the narrow ADR is written before slice 3a.** The argument that carried it is
recorded below, followed by the scope the ADR has to cover so slice 3a is not blocked on an undecided
boundary.

The strongest argument is textual rather than a matter of taste. ADR 0013 names its own supersession
trigger — *"when a third executable needs a test"* — and this change adds two executables that carry a
self-test: `collect.py` (collector plus normalizer in one file) and, since Decision 9a,
`tools/generate-cases.py`. That takes the repo from two such executables to four. **The
trigger fires whether or not the fixture question is asked**, so ADR 0013 is revisited in this change
either way. Doing that deliberately costs one file; doing it by accident costs the decision.

Second, the fixture/repo boundary is not a fact a table can carry. `OPERATIONS.md`'s prerequisites
table answers *what you need installed*. The claim here is a boundary — *a rig fixture's suite is
substrate under measurement, never this repo's verification surface* — and this repo has direct
evidence about what happens to boundaries that live only in prose: ADR 0013 exists because the same
gap was recorded five separate times in the journal without a decision. A fixture shipping Jest will
read as ADR 0013 being quietly reversed, and a prerequisites row will not stop that reading in six
months.

Third, timing. The ADR's content is fully decidable now; nothing slice 3a discovers changes it.
Writing it while holding a half-built fixture means writing it under pressure to justify what already
exists, which is the ADR-0012 fault in a different register.

Recommended shape: **one ADR, two clauses.** Clause A states the boundary and restates the repo's
verification surface (`hooks/pre-commit`, `bash -n`, `python3 -m py_compile`, per-executable
self-tests) as unchanged. Clause B **declines ADR 0013's supersession trigger on the record**, with the
reason — four executables carry self-tests once this change lands, up from the two ADR 0013 was written
against, and a `tests/` runner built to hold them is still infrastructure ahead of content — and
restates the trigger more sharply. Declining a trigger explicitly is worth more than letting it lapse.

Rejected alternative: amend ADR 0013 in place. This repo's decisions are additive records, and "a
fixture may carry a runner" is a different claim from "an executable carries its own test". Folding
them together muddies both.

**What the ADR must settle, in one paragraph, so slice 3a is unblocked.** Clause A ratifies that a rig
fixture may carry its own runtime (Node and npm) and its own test runner (Jest), that this runtime is
**substrate under measurement and never this repo's verification surface**, and that the repo's
verification surface therefore remains exactly what ADR 0013 and `OPERATIONS.md` already name:
`hooks/pre-commit`, `bash -n`, `python3 -m py_compile`, and each committed executable's own self-test —
unchanged by anything in this experiment. Clause A also states the boundary's practical test, so it
survives being read by a stranger: a fixture's suite reports on the *fixture*, never on this repo, and
no repo-level command runs it. Clause B addresses ADR 0013 directly rather than leaving its trigger to
lapse: the trigger *"when a third executable needs a test"* is **met and explicitly declined on the
record**, because the per-executable self-test pattern still holds for all four (`hooks/pre-commit`,
`rig/derive.py` — ADR 0013's own cited precedent, which an earlier draft of this paragraph dropped —
`rig/collect.py`, and `tools/generate-cases.py`) and a `tests/` runner built to hold four self-tests is
still infrastructure ahead of content. `run-pipeline.sh` carries no self-test in this plan and is
excluded from the roster. Clause B then restates the trigger more sharply, in
the form the next real case will take: **when a self-test needs fixtures too large to inline.** The case
generator's self-test is the first plausible candidate for that, which is exactly why declining now is a
decision rather than a deferral. The ADR is written before slice 3a; it does not block slices 1 or 2,
which touch neither the fixture nor the toolchain. The `OPERATIONS.md` prerequisites edit remains
separate and still covers both the Node/npm/Jest row and the GNU `timeout` row the table has been
missing all along.

## Data flow

```
rig/fixtures/failure-flood/v1  (committed: src/ tests/ runtime/ tools/ prompts/ answer-key/,
                                MANIFEST.sha256 over all six)
        │  manifest + git-clean + node/npm floor + lockfile digest + PREREG preflight  ──► exit 2
        ▼
per-run root (machine-local, outside <repo>)
        │  npm ci ──► node_modules
        │  tools/generate-cases.py ──► cases/  ──► digest vs answer-key/case-table.sha256 ──► exit 2
        │
        ├─► workspace(step) = src/ + tests/ + runtime/ + cases/ + node_modules symlink [fresh per step]
        ▼                     (tools/, prompts/, answer-key/ are NEVER materialised)
rig/run-pipeline.sh
   PIPELINE                                      MONOLITHIC
   01 collect ── collect.py                          01 monolith ── claude -p (Bash + write)
        ├─► collection/1  (full, scoring only)            │  runs the suite ITSELF, raw output,
        └─► clusters view (bounded by cluster count)      │  nothing pre-digested, no cap, no
        │   → the ONLY thing the diagnostician sees       │  harness collection during the arm
   02 diagnose ── claude -p ──► fix-plan.txt              │
        │  copied out, hashed, workspace re-hashed        │
        │  (src/ changed here ⇒ arm state failed)         │
   03 apply    ── claude -p, direct file writes           │
        │  (no .git materialised ⇒ no git apply)          │
        │  + re-collect K times                           │
        ▼                                                 ▼
   both arms' final text carries the frozen  CAUSE <path>:<line> <cluster_ids>  lines
        ▼
   99 verify   ── collect.py  (harness-run, AFTER the arm, excluded from arm cost and context)
        ▼
   status.json + arm.json + steps/**   ──►  rig/runs/failure-flood-v1/<run_id>/
        ▼
rig/derive.py --experiment failure-flood-v1
   de-dup by message.id ─► per-turn series ─► peak = max, cumulative = Σ, cross-checked vs result.usage
   read-back per invocation: surface · model · permission mode · cwd
   scoring: CAUSE lines parsed from result.result in BOTH arms ─► precision/recall vs R0
            four-value verdict · integrity guard vs C
        ▼
rig/results/failure-flood-v1/runs.jsonl  (committed; integers and digests only)
        ▼
rig/report.py ──► 4 uncombined tables + cost table + anomaly log (X = 3)
        ▼
hypotheses/0002, 0003 ──► theory/  (one write, only if a number survives)
```

## File changes

| File | Action | Description |
|---|---|---|
| `rig/derive.py` | Modify | Slice 1: occupancy fields, `message.id` de-dup, aggregate cross-check, schema 3. Slice 4: `--experiment` dispatcher, second row builder, `no-preregistration` void |
| `rig/report.py` | Modify | `--experiment` dispatcher, per-experiment arms, four new uncombined tables |
| `rig/collect.py` | Create | Collector + signature normalizer + `--self-test`. `python3`, stdlib only |
| `rig/run-pipeline.sh` | Create | Multi-step arm driver: preflight (manifest, toolchain, lockfile, prereg), per-step materialise/invoke/persist, per-invocation read-back, `--shakedown` |
| `rig/surfaces/failure-flood.txt` | Create | The new preimage. Captured twice, compared, then committed |
| `rig/fixtures/failure-flood/v1/{src,tests,runtime,tools,prompts,answer-key}/**` | Create | Clean substrate (3a), injections + measured `F0`/`R0`/`S0` (3b), `prereg.json`, `MANIFEST.sha256` over all six paths |
| `…/v1/tools/generate-cases.py` + its axis table | Create | Decision 9a. Deterministic case-table generator, manifest-covered, never materialised, carries `--self-test` |
| `…/v1/answer-key/case-table.sha256` | Create | The expected digest of the generated tables. Inside the manifest, which is what makes the digest a freeze rather than a note |
| `rig/fixtures/failure-flood/v2/**` | Create | Stage 2, amplified. Same clean substrate and same six causes, different axis table, frozen separately |
| `rig/results/failure-flood-v1/runs.jsonl` | Create | Committed rows for the new experiment |
| `hypotheses/0002-*.md`, `hypotheses/0003-*.md` | Create | Slice 5. Their existence is a launch precondition, enforced in preflight |
| `rig/README.md` | Modify | The experiment axis becomes real; the two-schema rule; the fixture-runtime boundary |
| `OPERATIONS.md` | Modify | Node + npm rows (rig-only, fixture-only), the missing GNU `timeout` row, `collect.py --self-test` in the decision table |
| `MAP.md` | Modify | Experiment count |
| `decisions/00NN-*.md` | Create — **approved** | The two-clause ADR above. Lands before slice 3a; does not block slices 1 or 2 |
| `rig/run.sh` | **Unchanged** | Its cost instrument is verified. Its conditional `--dirty-ok` stamp is recorded as a follow-up, not fixed here |
| `.gitignore` | **Unchanged** | Blanket `node_modules/` covers the install, and the generated case tables are written outside `<repo>` — chosen partly so this file stays untouched |

## Interfaces and contracts

`run-pipeline.sh` exit codes follow the house convention exactly:

```
0  the arm reached `complete` or `void`  (void is a designed outcome, never a failure)
1  the arm reached `failed` — an assertion fired: read-only substrate mutated,
   test/runtime bytes changed, or the diagnostician wrote to src/
2  could not run: dirty tree, manifest mismatch, missing/underfloor node|npm,
   lockfile digest mismatch, CASE-TABLE digest mismatch, report-too-large,
   missing pre-registration, bad argument. NOT a pass.
```

`status.json` is flushed on every exit path including 1 and 2, before exiting — Amendment 1's
ordering rule, for the same reason.

One `failure-flood` row, load-bearing fields only:

```json
{"schema_version": 1, "run_id": "s2-pipeline-03", "experiment": "failure-flood-v1",
 "task_id": "s2", "arm": "pipeline", "iteration": "3",
 "model": "<id>", "harness_version": "<cli>", "python": "<x.y.z>",
 "node_version": "<x.y.z>", "npm_version": "<x.y.z>", "lockfile_sha256": "<hex>",
 "case_table_digest": "<hex>", "case_count": 3000, "report_bytes": 0,
 "suite_timeout_s": 0, "partial_reason": null, "bash_call_count": 0,
 "fixture_version": "v2", "fixture_digest": "<hex>", "checker_digest": "<hex>",
 "prereg_digest": "<hex>", "code_commit": "<sha>", "declared_permission_mode": "<mode>",
 "state": "complete", "void_reason": null,
 "peak_occupancy_tokens": 0, "cumulative_occupancy_tokens": 0,
 "occupancy_is_monotone": true, "occupancy_aggregate_matches": true,
 "context_window_tokens": 0, "total_cost_usd": 0.0,
 "suite_state": "ran", "verdict": "partial",
 "integrity_guard_pass": true, "identifier_set_matches_clean": true,
 "causes_claimed": 0, "causes_correct": 0, "causes_present": 0, "clusters_present": 0,
 "steps": [{"index": 1, "role": "collect", "kind": "code",
            "peak_occupancy_tokens": 0, "cumulative_occupancy_tokens": 0, "model_turns": 0},
           {"index": 2, "role": "diagnose", "kind": "model",
            "prompt_sha256": "<hex>", "tool_surface_sha256": "<hex>",
            "handoff_sha256": "<hex>", "model_turns": 4,
            "occupancy_series": [0, 0, 0, 0],
            "peak_occupancy_tokens": 0, "cumulative_occupancy_tokens": 0}],
 "anomaly_classes": []}
```

Precision and recall are **not** stored — the three counts are, and the pair is computed in
`report.py`. Storing a ratio invites a later caller to blend two ratios; storing counts does not.

## Verification strategy

No test runner, by decision (ADR 0013). The surface is what exists, plus each executable's self-test.

| Layer | What | How |
|---|---|---|
| Syntax | `rig/run-pipeline.sh` | `bash -n` |
| Syntax | `rig/collect.py`, `derive.py`, `report.py` | `python3 -m py_compile` |
| Redaction | Every committed file, including the new `runs.jsonl` | `./hooks/pre-commit --all`. The integers-and-digests-only row shape keeps this passing by construction |
| Normalizer | Determinism **and discrimination** | `rig/collect.py --self-test`, cases (a)–(e). (b) is the one that keeps the cluster channel alive |
| Occupancy detector | Can it fire, on data already paid for? | Slice 1: 42 rows re-derive with the projection check; `occupancy_aggregate_matches` true on all 42; mutate one turn's usage in a copied capture and require the mismatch anomaly |
| Deriver idempotence | The existing property | Derive twice; `runs.jsonl` byte-identical |
| Integrity guard | Can it fire? | A deliberate case that deletes one test, and one that edits a test file's bytes; both must reach `regressed` / `failed`, never `green` |
| Suite-state separation | Three states, plus the void | Synthetic reports for `ran`/`did-not-start`/`partial`; an absent-toolchain run must exit 2, not report a state |
| Case generator | Determinism and freeze honesty | `tools/generate-cases.py --self-test`: byte-identical output across two runs and across two input orderings. Then tamper one generated byte and require **exit 2** on the digest compare — the same both-directions proof the MANIFEST guard already got |
| Collector at scale | The stated magnitude is real | Run against the amplified fixture once and record `report_bytes`, `case_count` and wall; assert the declared ceiling is above the observed size with margin, and that `--runInBand` stays inside `suite_timeout_s` |
| Signature stability under amplification | One cause does not shatter into hundreds of clusters | Slice 3b measures clusters-per-injection on the amplified fixture and freezes it in `R0`. A cause whose cluster count grows with `case_count` is a normalizer defect, not a key entry |
| No pre-digestion in MONOLITHIC | The comparison exists | Assert the arm's step list contains exactly one model step and no collector step before `99-verify`; assert `99-verify` output appears in no prompt bytes |
| Surface and mode | Per invocation | Read-back vs the committed preimage and the declared mode; a deliberate mismatch control must void |
| Pre-registration guard | Structurally impossible, not forbidden | With `hypotheses/0002` absent, `run-pipeline.sh` must exit 2 — and `--shakedown` must stamp `void_reason=shakedown` on a **clean** tree |

## Threat matrix

Applicable: the design invokes subprocesses (`claude`, `npm`, the suite under `timeout`), copies trees,
creates symlinks, and reads `git` state. Verification for applicable rows is `bash -n` plus a manual
adversarial exercise; there is no runner in which to write a RED test, and inventing one is out of
scope (ADR 0013).

| Boundary | Applicability | Design response | Planned check |
|---|---|---|---|
| Documentation-like paths | **N/A** — nothing classifies a file as executable from its path | — | — |
| Git repository selection | **Applicable** — dirty-tree guard, `code_commit`, and the prereg tracked/clean check all depend on which repo answered | Resolve the root once from `BASH_SOURCE` (the `setup.sh` idiom); pass explicit paths to `git`; never `git -C` with a caller-supplied value | Run from a different cwd and from a nested directory; both must stamp the same `code_commit` |
| Commit state | **Applicable** — a staged fixture edit would be measured while `code_commit` named the unedited tree | `git status --porcelain` over `rig/`, which reports staged and unstaged; exit 2 on any output | Stage a fixture edit, require exit 2; repeat unstaged |
| Push state | **N/A** — the rig never pushes | — | — |
| PR commands | **N/A** — no `gh`, no PR composition | — | — |
| Subprocess argument composition | **Applicable** — prompts, disallow lists and workspace paths reach three subprocesses | Prompt passed as one quoted argument read from a file, never interpolated; the disallow list is a committed preimage, never a constructed string; `timeout` wraps every child; `npm ci` given an explicit prefix, never an inherited cwd | Fixture path and prompt containing spaces, quotes and non-ASCII must run unchanged, with `init.tools` still matching the preimage |
| Agent-executed shell (new row) | **Applicable** — both arms hold `Bash` and a write tool, which no prior arm had | Workspace is outside `<repo>`, materialised per step, and thrown away; `node_modules` is a symlink to a per-run machine-local directory so a write through it cannot touch committed bytes or leak across runs; `src/` writable, `tests/`+`runtime/` read-only and re-hashed | A deliberate case that edits a test file and one that edits `package.json`; both must reach `regressed`/`failed` |
| Symlink traversal (new row) | **Applicable** — the hash instrument must not descend the symlink | File list built from the manifest's path set plus the generated case paths, captured **before** the symlink exists; never `find . -type f` | Assert the hashed file count equals manifest + case paths, with `node_modules` present |
| Generated bytes entering a measured run (new row) | **Applicable** — thousands of case rows are produced at run time and materialised into a workspace the agent can read | The generator and its axis table are manifest-covered; the expected output digest is **inside the manifest**; generation happens outside `<repo>` and is compared before the workspace is built; a mismatch is exit 2 before any run directory is claimed | Tamper the generated output → exit 2. Tamper the expected digest → manifest mismatch → exit 2. Both directions, because either alone leaves a hole |

## Migration and rollout

No data migration. Slice 1 is a `schema_version` bump on an existing experiment, which under a total
deriver is a rebuild, not a migration; rollback is reverting one commit and re-deriving. The new
experiment's rows are a new file, so nothing existing is disturbed at any point. Nothing in `theory/`
is touched until a number exists, so rollback before that point is deleting the new fixture
directories, `run-pipeline.sh` and `collect.py`. Fixtures are additively versioned, so no rollback ever
mutates a frozen version.

## Corrections to the inputs, collected

| # | Input claim | What the code says | Effect |
|---|---|---|---|
| 1 | Peak occupancy is not derivable from `runs.jsonl`; both runway channels need retro-derivation | Correct for peak. **Cumulative is already on the row**: `result.usage` is an aggregate over turns (141134 = 16602+39942+40854+43736, verified on a second capture) | Slice 1 shrinks to peak plus a series; cumulative becomes a cross-check, which is stronger than a new field |
| 2 | Slice 4's shakedown is "structurally uncountable" under `--dirty-ok` | `run.sh` stamps `void_reason=dirty-tree` **only when the tree is actually dirty** (lines 463–466). After slice 4 commits, the tree is clean and the row is countable | Decision 7: a prereg preflight plus a `--shakedown` flag that stamps unconditionally |
| 3 | The `--self-test` flag pattern is "already load-bearing in `rig/derive.py`" | `derive.py`'s self-test is **unconditional** in `main()`, not flag-gated. The flag lives on `hooks/pre-commit` (line 149), per ADR 0013 | Both patterns exist; the collector takes the flag (it runs inside a measured arm), the deriver keeps the unconditional gate |
| 4 | "The CLI exposes no context-window-used field" | It exposes `contextWindow: 1000000` and `maxOutputTokens`, plus a one-entry `iterations` array — the denominator, not the numerator | Honesty contract stands, with a sharper reason. `context_window_tokens` recorded |
| 5 | Pre-existing rows must re-derive **byte-stable** across the bump | `checker_digest` is `sha256` of `derive.py`'s own bytes (line 78), so editing the file necessarily changes it on all 42 rows | The check is a projection excluding new keys, `schema_version` and `checker_digest`. Anything stronger is unachievable |

## Open questions

- [x] **Governance.** ~~Write the narrow two-clause ADR before slice 3a?~~ **Approved.** Scope stated above.
- [x] **Does the applier get a repository?** ~~Open.~~ **Settled by the spec: no repository for ANY role, in either arm.** The original hardening item named only the diagnostician, which left the applier as a side door. Consequence designed for: `git apply` is unavailable and application is by direct file write, so `fix-plan/1`'s `target_paths` is the applier's whole addressing mechanism and needs no patch field. Two precisions worth stating, because "no git" is not self-enforcing: the guarantee is **no reachable history**, and it holds because the workspace is a `mktemp` directory outside `<repo>` where `git rev-parse` finds nothing to walk up to; and since both arms hold `Bash`, an agent *can* run `git init`, which is harmless — there is no prior commit to diff — and invisible to the substrate hash, because that hash is taken over the manifest path set and not a directory walk. That is the same lesson `run.sh` already learned from `claude` writing an ambient `.atl/skill-registry` into its cwd.
- [x] **Is 50 cases from 6 causes the right flood ratio?** ~~Open.~~ **Resolved by amplification** (Decision 9): table-driven parameterization of the same six causes, hundreds to thousands of cases. Decision 8 keeps the escape cheap — a different ratio is a new fixture version, never an edit.
- [ ] **The cause-site space and its chance baseline.** The closed vocabulary is superseded, but its question survives in a new form: `<path>:<line>` sites are drawn from every source line, so the report should state the site-space size alongside the precision/recall pair, exactly as vocabulary size would have been stated. Frozen in slice 3b, before the prompts are authored.
- [ ] **Does MONOLITHIC self-triage through its shell?** If it routinely reduces the flood itself (`--onlyFailures`, a pipe through `head`), the experiment measures *one agent with a shell* versus *a fixed pipeline*, which is a different and still-interesting claim. `bash_call_count` per step is the cheap signal; the stage-1 shakedown should be read for it before stage 2 is funded.
- [ ] **Does peak diverge from cumulative at all?** Both sampled captures were monotone, making peak the final turn. `occupancy_is_monotone` over 42 rows answers this in slice 1, and a "no" would mean `hypotheses/0002` and `0003` are closer to one claim than two.
- [ ] **This document exceeds the generic 800-word design budget.** Deliberate: the orchestrator asked for a sibling to `sdd/measurement-rig/design.md`, and the repo's own precedent for a measurement design is a decision record of this size. Flagged rather than silently ignored.
