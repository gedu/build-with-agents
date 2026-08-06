---
id: sdd/measurement-rig/design
type: journal
targets: [any]
status: draft
verified: 2026-08-06
sources: ["sdd/measurement-rig/proposal.md", "sdd/measurement-rig/exploration.md", "decisions/0010-measurements-vary-the-harness-not-the-model.md", "theory/loops/reading-and-running-find-different-defects.md", "AGENTS.md", "sdd/testing-capabilities.md", "hooks/pre-commit", "setup.sh"]
---

# measurement-rig — design: the instrument, and how it proves what it ran

SDD design phase for `measurement-rig`. Architecture and decisions only. No task breakdown.

Bounded by ADR 0010's five constraints and by the proposal's pre-registered falsification table.

## Technical approach

Three programs, one directional pipeline, no shared state beyond files on disk.

**`rig/run.sh`** guards, launches and persists one run — nothing else. It never parses, never
aggregates, never decides a verdict. **`rig/derive.py`** is a *total, deterministic* function from run
directories to one committed JSON row each. **`rig/report.py`** aggregates rows into the four-cell
tables. The split is what buys idempotence (Decision 6) and re-analysis after a checker bug without
re-spending 30 runs.

The invocation is fixed for both arms except one flag:

```
timeout "$TIMEOUT_S" claude -p "$(cat "$PROMPT")" \
  --output-format stream-json --verbose ${DISALLOW:+--disallowedTools "$DISALLOW"} \
  >>"$RUN/stream.jsonl" 2>>"$RUN/stderr.log"
```

`--allowedTools` never appears. `--strict-mcp-config` never appears — it moves MCP server count as
well as surface, which is a second variable.

## Architecture decisions

### 1. Driver language: Bash for the run layer, stdlib `python3` for the analysis layer

| Option | Cost | Decision |
|---|---|---|
| Bash only | The stream is nine nested event types; counting `tool_use` names and computing spread in `awk` is an unmaintainable parser, and this repo has no `shellcheck` to hold it up | Rejected |
| Bash + `jq` | Still a new dependency, and `jq` cannot express the four-cell classification without becoming a program in a language nobody here reads | Rejected |
| `python3` only | The run layer wants `timeout`, redirection and `git` — shell's native idiom; writing it in Python adds `subprocess` plumbing for no gain, and abandons the conventions `setup.sh` and `hooks/pre-commit` already establish | Rejected |
| **Split: Bash runner, `python3` analyser** | Introduces a second language to a repo that had one | **Chosen** |

What the choice costs, stated rather than dodged: **`python3` becomes an undeclared runtime
prerequisite.** The portability contract in `hooks/pre-commit` ("must run on a machine that has not
installed anything") explicitly does **not** extend to the rig, and that boundary is the mitigation:
the hook is a committed gate every contributor runs, the rig is machine-local instrumentation one
operator runs. Bounded by three rules — stdlib only (`json`, `hashlib`, `statistics`, `pathlib`); no
`pip`, no venv, no manifest, no pinning; and `python3 --version` recorded in every row so a later
reader knows what parsed the stream. Absence of `python3` is exit 2 (could not run), never a skip.

### 2. Incremental persistence, and the complete/partial boundary

The stream is redirected **straight to a file**, not piped into a parser. Rationale: a parser in the
pipe means a parser crash destroys the transcript, and a pipeline adds two failure modes (exit status,
buffering) to the one thing that must not fail. The file is the record; parsing is a separate pass over
a file that already exists.

`run.sh` writes `status.json` *after* the process exits, carrying `exit_code`, `timed_out`
(`rc == 124`), `wall_ms`, `timeout_s`, `driver_version`. That file is the completeness sentinel:

| On disk | State | Treatment |
|---|---|---|
| `status.json` + last parseable line is `result` | `complete` | Counted |
| `status.json`, `timed_out: true`, no `result` | `partial` | Void `timeout`; partial stream still read for anomaly attribution, never for the metric |
| `status.json`, `rc == 0`, no `result` line | `partial` | Void `missing-result` |
| No `status.json` | `absent` | Directory moved aside as `<run_id>.orphan.<ts>`, never deleted; counted in the anomaly log |

Truncation rule, so a killed write is not confused with a corrupt stream: **exactly one** unparseable
trailing line is tolerated on a `timed_out` run and recorded as `truncated_tail: true`. An unparseable
line anywhere else is anomaly class `unparseable-stream`.

**One assumption here must be executed, not reasoned.** Whether the CLI line-flushes to a *file*
(rather than buffering until exit) is not established by anything read so far, and
`theory/loops/reading-and-running-find-different-defects.md` is explicit that assumptions about what an
external tool emits are found by running it. Shakedown assertion #1 kills a run mid-flight and requires
`stream.jsonl` to hold at least one parseable line. Pre-registered fallback if it buffers: pipe through
`tee` with `pipefail` off, keeping the file as the sole record.

> **Executed 2026-08-06 — it flushes progressively. The fallback is not needed.** A two-tool-call run was
> backgrounded with `stream-json` redirected to a file, and the file was sized while the process was still
> alive:
>
> | Elapsed | Bytes | Lines | Process alive |
> |---|---|---|---|
> | 4 s | 21,965 | 2 | yes |
> | 8 s | 28,248 | 3 | yes |
> | 12 s | 55,596 | 9 | yes |
> | 16 s | 57,663 | 11 | no |
>
> The record grows during the run, so a killed run leaves a usable partial transcript and the
> redirect-not-pipe decision holds as written. **Shakedown assertion #1 is retained anyway**: this proves
> the behaviour once, on one version, and the assertion is what keeps it proven when the CLI changes. A
> verification that ran once is not a verification that keeps running — which is the same distinction the
> theory file draws between a check that exists and a check that fires.

### 3. Storage: append-only committed JSONL, rebuilt by derivation

| Option | Tradeoff | Decision |
|---|---|---|
| SQLite as the committed store (perf-vibe's literal choice) | A binary blob in a public Markdown repo is undiffable, unreviewable, and opaque to the only committed gate this repo has. Thirty rows do not need a query planner | Rejected |
| Committed raw `stream-json` captures | Every `init` event carries an absolute `cwd`; the redaction gate would correctly block the commit, and should | Rejected |
| **`rig/results/<experiment>/runs.jsonl`, one object per run, `schema_version` on every row** | No ad-hoc querying without importing it somewhere | **Chosen** |

perf-vibe's *discipline* is what carries over, item by item: `schema_version` on every row; repeated
iterations with spread; a commit stamp per row; and the **dirty-tree guard** — `run.sh` refuses to
launch (exit 2) unless `git status --porcelain` is empty for the fixture, checker, prompt and driver
paths, and stamps `code_commit: <sha>`. `--dirty-ok` exists for shakedown only and stamps
`code_commit: <sha>-dirty` plus `void_reason: dirty-tree`, so such a row can never be counted.

Every fixed input is on the row, which is ADR 0010 constraint 2: `model`, `harness_version`, `task_id`,
`arm`, `prompt_sha256`, `tool_surface_sha256`, `fixture_version`, `fixture_digest`, `checker_digest`,
`code_commit`.

**`cwd` handling, before anything is committed.** The recorded `init.cwd` is an absolute path under a
home directory and is therefore never copied into a row. `derive.py` compares it in memory to the
intended workspace path and emits `cwd_is_expected: true|false` only. No hash of it either — a digest
of a home path is a redaction hazard with zero analytic value, while the boolean carries the only fact
the experiment needs. Raw captures live under `rig/runs/`, gitignored, retained locally as evidence.

### 4. Fixtures: committed, hash-frozen, additively versioned

Location `rig/fixtures/tool-surface/v1/` — committed, so its contents are published. That is
acceptable because the fixture is invented code with seeded defects and names nothing private; it is
also *required*, because AGENTS.md holds that a citation must resolve for a reader who has only this
repo, and a result whose substrate is machine-local is uncheckable.

| Concern | Mechanism |
|---|---|
| Freezing | `MANIFEST.sha256` — sorted `sha256␣path` over `src/`, `prompts/`, `answer-key/`. Recomputed and compared **before every run**; mismatch is exit 2, not a warning |
| Identity on the row | `fixture_digest` = sha256 of `MANIFEST.sha256` itself |
| A change never mutating results | Additive versioning: a change is `v2/`; `v1/` is never edited. Aggregation **refuses** to merge rows sharing a `fixture_version` but differing in `fixture_digest` — that combination means a frozen version was edited, and it is an error, not a merge |
| The answer key leaking to the agent | The workspace the agent runs in is a copy of `src/` **only**, materialized outside `<repo>` under a machine-local `<workspace-root>`. `answer-key/` is never inside cwd, and no repo `AGENTS.md`/`CLAUDE.md` is discovered by walking up from cwd, so this repo's own instructions cannot contaminate the task |
| The agent mutating the substrate | The workspace copy is re-hashed **after** the run. Neither arm has a write tool, so any change is a finding, not a tolerance |

Materializing outside `<repo>` changes the ambient context relative to the reconnaissance runs. That is
fine and deliberate: ambient is a constant across arms, both arms use the identical construction, and
`init` is recorded per run so drift is detected rather than assumed.

### 5. The run bound: an external timeout that must not truncate, plus ceilings that flag rather than void

There is no `--max-turns`, so the bound is `timeout(1)` around the process.

| Number | Where it comes from |
|---|---|
| Pilot timeout `300 s` | The proposal's provisional value, used **only** for the tier-1 pilot. Its job is to be replaced |
| Derived timeout | `ceil(3 × slowest_successful_pilot_wall_s / 30) × 30`, floor `120 s`. The `3×` is the point: a truncating bound biases the metric toward whichever arm is faster, and BROAD is the arm plausibly taking more turns — killing slow BROAD runs would manufacture the result the experiment wants. Three times the slowest thing ever observed is the smallest multiple that survives a run doing three times the work |
| Pilot invalidation | If **any** pilot run hits the timeout, the bound is not calibrated. Raise it and re-run the pilot; a pilot containing a truncation cannot calibrate a non-truncating bound |
| Turn ceiling `T_task = 2 × (files_in_answer_key + 2) + 1` | Calibrated from the exploration: one tool call produced `num_turns: 2`, so turns ≈ tool calls + 1. Two calls per file (`Grep` then `Read`), two files of slack |
| Per-run cost flag `$2.50` | `10 × $0.25`, the observed trivial-run cost, where 10 is the turn-ceiling order and per-turn cache reads dominate |
| Experiment budget `$75.00` | `30 × $2.50`. Notional on a subscription; it is a stop-launching threshold, not a bill |

**A deliberate correction to the proposal's open item.** The proposal proposed voiding on `num_turns`
and `total_cost_usd` ceilings. Design rejects that: a run that emitted a `result` event terminated on
its own, so its turn count *is the measurement* — the arm that flails is the finding, and voiding it
deletes the signal. Completed runs above ceiling are recorded `over_ceiling: true` and reported. Only a
run that did not terminate is void. The cost ceiling likewise governs the **experiment** (stop
launching), never an individual completed run.

### 6. Idempotence and resumability

- `run_id = <task>-<arm>-<iteration>` — deterministic, e.g. `t1-broad-03`. No timestamps in identity.
- The claim is `mkdir` (not `mkdir -p`) on the run directory: it **fails if the directory exists**,
  which is the lock. No lockfile, no PID file.
- Existing directory → inspect `status.json`: `complete` → skip; void → skip; absent → orphan it aside
  and re-attempt.
- A re-run after a void takes suffix `r1` in the **same iteration slot** (`t1-broad-03r1`), so voids are
  additive and auditable while the arithmetic stays N = 5. `report.py` counts at most one non-void row
  per `(task, arm, iteration)`; void rows appear only in the anomaly log.
- **The runner never writes `runs.jsonl`.** Derivation is a total rebuild from all run directories,
  sorted by `run_id`, so re-deriving is byte-identical and double-counting is structurally impossible
  rather than defended against.
- No automatic retry. A void is a human decision, because a silent retry hides an anomaly class from
  the X = 3 threshold — which is the one number the proposal pre-registered to keep the instrument
  honest.

### 7. Proving the rig measured what it claims — the loop-theory constraint applied inward

`theory/loops/reading-and-running-find-different-defects.md` records a harness that silently reverted
the code under test and reported every fix as failed. The defence is that **no claim about the
configuration is taken from what the driver passed; every one is read back from the run.**

| Claim | Read-back proof | Failure |
|---|---|---|
| The visible surface was the intended one | `init.tools`, sorted → `tool_surface_sha256`, compared against a digest of the committed preimage `rig/surfaces/<arm>.txt` | void `surface-mismatch` |
| The model was the intended one | `init.model` and the `result.modelUsage` key | void `model-mismatch` |
| The prompt bytes were the intended ones | `prompt_sha256` of the exact bytes passed; the prompt file's hash is in `MANIFEST.sha256` | exit 2 pre-launch |
| The code under test was the committed code | manifest verified pre-run and post-run; `git status` clean; `code_commit` stamped | exit 2 pre-launch |
| The run happened in the intended tree | `init.cwd` vs the materialized workspace | void `cwd-mismatch` |
| Ambient config did not drift | `init.permissionMode`, `mcp_servers` count and per-server status, `hook_started` names; a differing pair within a cell voids the pair | void `ambient-drift` |

The load-bearing detail: **the surface digest is compared to an independently committed preimage, not
to the flag string the driver built.** A flag string always matches itself — that is precisely how the
`--allowedTools` trap would have passed. Comparing read-back `init.tools` against a file written
separately is the only comparison that catches an ineffective flag. Committing the preimage also makes
the hash resolvable for a reader who has only this repo, instead of a bare digest nobody can check.

And the verifier is itself verified, once per experiment: a pre-registered **negative control** run
passes the BROAD flag set while declaring the SCOPED expected digest, and the rig **must** void it
`surface-mismatch`. If it does not, the verification path is broken and no result may be written to
`theory/`. One run, and it is the only thing standing between this rig and the incident that theory
file records.

### 8. What is left crude, deliberately

| Seam left crude | Why that is correct now |
|---|---|
| Three hardcoded task branches, no task registry | The second experiment (delegated-vs-inline) will define the interface from two data points instead of one guess |
| Checkers as three functions behind a dict in one file, no checker interface or discovery | Same reason; a plugin seam invented now is an interface designed from zero examples |
| Constants at the top of `run.sh` with a WHY comment each, no config file | The convention `hooks/pre-commit` already establishes. A config file makes the numbers changeable without changing the reasoning beside them |
| Text file storage, no migrations | Derivation is total, so a `schema_version` bump is a rebuild, not a migration |
| Strictly sequential runs, no parallelism | `rate_limit_event` is an anomaly class; concurrency destroys its attribution. 31 runs of ~1 minute is under an hour |
| min/max/median in stdlib, no significance testing | ADR 0010 asks for spread, not a p-value the sample cannot support |
| No retry, no resume-in-flight, no daemon | See Decision 6 |

The framing that makes this a decision rather than laziness: ADR 0010 scoped v1 to one question
answered end to end, and this repo's documented failure mode is naming experiments and not running
them. A further consideration decides it — **the rig is a verifier that will be cited**, so it inherits
the loop file's demand for review, and the cheapest way to keep it reviewable is to keep it small
enough to read in one sitting.

## Data flow

```
rig/fixtures/tool-surface/v1  (committed, MANIFEST.sha256)
        │  verify manifest + git-clean + python3 present  ──► exit 2
        ▼
materialize src/ copy  ──►  <workspace-root>  (outside <repo>, machine-local)
        │
        ▼
rig/run.sh ── timeout N claude -p … --output-format stream-json --verbose [--disallowedTools …]
        │                                   │
        │                                   └──► rig/runs/<exp>/<run_id>/stream.jsonl  (append)
        ├──► prompt.txt   (exact bytes passed)
        └──► status.json  (exit_code, timed_out, wall_ms)   ← completeness sentinel
        ▼
re-hash workspace copy  ──► substrate-mutation check
        ▼
rig/derive.py  (total, deterministic, re-runnable; strips cwd)
        │  parse → read-back verification → outcome + practice checkers → four-cell classify
        ▼
rig/results/<exp>/runs.jsonl   (committed, redacted, schema_version)
        ▼
rig/report.py ──► four-cell table per arm · off-set distribution · anomaly log (X = 3 check)
        ▼
theory/agents/tool-surface-design.md    ← one write
```

## File changes

| File | Action | Description |
|---|---|---|
| `rig/README.md` | Create | `type: index`. States the rig is an instrument, not truth; its results reach `theory/` through a normal validated write |
| `rig/run.sh` | Create | Preflight guards, materialize, invoke, persist, `status.json`. Exit contract below |
| `rig/derive.py` | Create | Stream parse, read-back verification, both checkers, four-cell classification, `runs.jsonl` rebuild |
| `rig/report.py` | Create | Per-arm four-cell table, off-set distribution, anomaly log |
| `rig/surfaces/broad.txt`, `rig/surfaces/scoped.txt` | Create | Expected tool-name preimages — the independent side of the surface comparison |
| `rig/fixtures/tool-surface/v1/src/**` | Create | Frozen synthetic substrate with seeded defects |
| `rig/fixtures/tool-surface/v1/prompts/t{1,2,3}.txt` | Create | Exact prompt bytes, hashed into the manifest |
| `rig/fixtures/tool-surface/v1/answer-key/t{1,2,3}.json` | Create | Seeded defect set + expected/off-set/forbidden tool sets. Committed **before** the prompts, so checker-first is provable from commit order |
| `rig/fixtures/tool-surface/v1/MANIFEST.sha256` | Create | The freeze |
| `rig/results/tool-surface-v1/runs.jsonl` | Create | Committed rows |
| `.gitignore` | Modify | `/rig/runs/` — added **outside** `setup.sh`'s managed block, which that script owns and rewrites |
| `MAP.md` | Modify | Register the new top-level `rig/`, with citability `No` (instrument and process record) alongside `sdd/` and `upstream/` |
| `theory/agents/tool-surface-design.md` | Modify | Later, once a number exists: measurement, narrowing, or `rejected` marking |

## Interfaces and contracts

`run.sh` exit codes, following the documented convention in `hooks/pre-commit`:

```
0  run completed and passed every read-back verification
1  run completed but is voided — an anomaly, recorded with void_reason
2  could not run: dirty tree, manifest mismatch, missing python3, bad argument.
   NOT a pass. Never conflate with 0.
```

One `runs.jsonl` row, abbreviated to the load-bearing fields:

```json
{"schema_version": 1, "run_id": "t1-broad-03", "experiment": "tool-surface-v1",
 "task_id": "t1", "arm": "broad", "iteration": 3,
 "model": "<model-id>", "harness_version": "<claude-cli-version>", "python": "<x.y.z>",
 "prompt_sha256": "<hex>", "tool_surface_sha256": "<hex>", "tool_count": 54,
 "fixture_version": "v1", "fixture_digest": "<hex>", "checker_digest": "<hex>",
 "code_commit": "<sha>", "cwd_is_expected": true, "permission_mode": "<mode>",
 "mcp_server_count": 25, "state": "complete", "truncated_tail": false,
 "num_turns": 9, "over_ceiling": false, "wall_ms": 41230, "total_cost_usd": 0.61,
 "input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0,
 "cache_read_input_tokens": 0, "stop_reason": "end_turn", "permission_denials": [],
 "tool_calls": [{"name": "Grep", "is_error": false}],
 "offset_calls": 0, "forbidden_calls": 0,
 "outcome_pass": true, "practice_pass": false, "classification": "improper-success",
 "void_reason": null, "anomaly_classes": []}
```

## Verification strategy

`sdd/testing-capabilities.md`: this repo has **no test runner**, and none is scheduled. Verification is
what exists, plus the rig's own shakedown assertions.

| Layer | What | How |
|---|---|---|
| Syntax | `rig/run.sh` | `bash -n` |
| Redaction | Every committed rig file, including `runs.jsonl` | `./hooks/pre-commit --all` — the row shape above exists partly to keep this passing by construction |
| Analyser determinism | `derive.py` | Run twice over the same run directories; `runs.jsonl` must be byte-identical |
| Persistence under kill | `run.sh` | Shakedown #1: kill mid-flight, require ≥ 1 parseable line and an `absent`-state classification |
| Verifier honesty | Read-back path | Shakedown #2: the negative-control run must void `surface-mismatch` |
| Freeze honesty | Manifest guard | Shakedown #3: touch a byte in a fixture copy, require exit 2 |

## Threat matrix

The design invokes subprocesses (`claude` under `timeout`), copies trees, and reads `git` state, so the
matrix applies. Verification for applicable rows is a manual adversarial exercise plus `bash -n` — the
repo has no runner in which to write a RED test, and inventing one is out of scope per ADR 0010.

| Boundary | Applicability | Design response | Planned check |
|---|---|---|---|
| Documentation-like paths | **N/A** — the rig classifies no file as executable and executes nothing from the fixture. The fixture is read-only substrate | — | — |
| Git repository selection | **Applicable** — the dirty-tree guard and `code_commit` depend on which repository answered | `run.sh` resolves the repo root once from its own `BASH_SOURCE` (the `setup.sh` idiom) and passes explicit paths to `git`; never inherits an ambient cwd, never uses `git -C` with a caller-supplied value | Exercise from a different cwd and from a nested directory; both must stamp the same `code_commit` |
| Commit state | **Applicable** — a staged-but-uncommitted fixture edit would be measured while `code_commit` named the unedited tree | Guard is `git status --porcelain` over the fixture, checker, prompt and driver paths, which reports staged **and** unstaged changes; exit 2 on any output | Stage a fixture edit and require exit 2; repeat unstaged |
| Push state | **N/A** — the rig never pushes | — | — |
| PR commands | **N/A** — the rig never composes a `gh` or PR command | — | — |
| Subprocess argument composition (added row) | **Applicable** — the disallowed-tool list and the prompt reach a subprocess | Prompt passed as a single quoted argument read from a file, never interpolated or eval'd; the disallowed list is a committed file, not a constructed string; `timeout` wraps the child so a hung process cannot outlive the run | Fixture path and prompt containing spaces, quotes and non-ASCII must run unchanged; verify `init.tools` still matches the preimage |

## Migration and rollout

No migration — nothing exists yet. Rollout is the proposal's staged delivery, unchanged: the **tier-1
cell (10 runs) plus the negative control** completes end to end first as the shakedown, and tiers 2 and
3 launch only after all three shakedown assertions pass. Nothing in `theory/` is touched until a number
exists, so rollback before that point is deleting `rig/`.

## Open questions

- [ ] Does the CLI line-flush `stream-json` to a redirected file? Decision 2 carries a pre-registered
      fallback either way, but the answer must come from shakedown #1 and not from reading.
- [ ] The derived timeout is unknown until the tier-1 pilot runs. `300 s` is the pilot's bound only.
- [ ] `files_in_answer_key` per task is fixed by the spec phase, which fixes each `T_task`.
- [ ] Does a new top-level `rig/` warrant an ADR, given it joins the `MAP.md` citability table? The
      proposal's affected-areas table already flags `decisions/` as possibly-new; deferring the answer
      to whoever writes the first result, because the citability question only bites once a number exists.

## Amendment 1 — runner and aggregator changes from `gentle-ai/bench`, 2026-08-06

Two design changes required by spec amendment R-A1.1 and R-A1.2. Everything else in that amendment is a
spec-level requirement this design already satisfies.

### Runner exit contract, and the ordering that makes it useful

| Situation | Runner exit |
|---|---|
| All requested runs reached `completed` or `void` | 0 |
| Any run reached `failed` — fixture unprovable, digest mismatch, assertion fired | **non-zero** |
| The runner itself could not start — dirty tree, missing manifest, bad arguments | 2, per the existing house contract |

**The ordering is the load-bearing half**: `status.json` and every partial capture are flushed **before**
the non-zero exit. A harness that exits non-zero and takes its evidence with it turns a diagnosable
failure into a mystery. This is the same reason `hooks/pre-commit` reports exit 2 with its findings
printed rather than aborting silently.

`void` deliberately does not affect the exit. It is a designed outcome, and making it non-zero would
train whoever runs this to ignore the exit code — which is precisely how `gentle-ai` issue #1883 became
possible.

### Aggregator: pair by iteration slot, refuse to sum unequal arms

The aggregator already refuses to merge rows sharing a `fixture_version` with differing `fixture_digest`.
Two rules are added:

- **Pair by `(task_id, iteration)`.** A slot contributes to the comparison only when **both** arms reached
  `completed` for that slot. This is a change from summing each arm independently.
- **Name every excluded slot in the output**, with its arm and void reason. Never a silent drop, and never
  a count without the list.

Rationale specific to this experiment: voids are not expected to distribute evenly between a 54-tool arm
and a 3-tool arm — the broad arm has more ways to run long. Summing arms independently would let that
asymmetry masquerade as the effect being measured.

### Two things confirmed rather than changed

- **Wall clock stays a bound and never enters the comparison** (R-A1.5). The row may carry elapsed time
  for diagnosis; the aggregator must not difference it.
- **The rig's own boundary** already matches the `gentle-ai/bench` discipline of a separate module that
  cannot break the product it measures: `python3` is stated as a rig-only prerequisite, and the
  `hooks/pre-commit` portability contract explicitly does not extend here. No change needed — recorded so
  a later reader does not re-open it.

## Amendment 2 — `Bash` subsumes `Glob` and `Grep`, which was a second variable

Found while verifying the Phase 0–3 apply batch, by probing rather than reading. It would have
invalidated the experiment, and it invalidates Amendment 1's arm arithmetic.

### The observation

Two probes, identical except for one flag:

| Invocation | Visible tools | `Bash` | `Glob` | `Grep` |
|---|---|---|---|---|
| no flags | **54** | present | absent | absent |
| `--disallowedTools Bash` | **55** | absent | **present** | **present** |

Disallowing one tool made the surface **larger**. `Bash` subsumes `Glob` and `Grep`: while it is
available the surface presents `Bash` alone, and removing it exposes the two search tools as separate
entries. Net −1 +2 = +1.

### Three consequences, and the second is the one that matters

**1. Surface size is not monotonic in `--disallowedTools`.** Any code computing the disallow list as
*(broad surface) − (scoped surface)* is wrong, because `Glob` and `Grep` are not members of the broad
surface and cannot be subtracted from it. The design's Decision on the scoped-arm disallow list said
exactly that, and it must change.

**2. The two arms differed in capability, not only in breadth.** BROAD held `Bash` and not
`Glob`/`Grep`; SCOPED held `Glob`/`Grep` and not `Bash`. So BROAD could shell out and SCOPED could not
— **a second variable**, of precisely the kind ADR 0010 constraint 2 forbids and the kind this repo
refused a vendor's number over. A result from those two arms could not have been attributed to surface
breadth, and nothing in the transcript would have said so.

**3. It explains the apply batch's unreconcilable 33-tool observation**, and vindicates its refusal to
invent `rig/surfaces/broad.txt` from a surface it could not reconcile with the recon baseline. Declining
to write down a number it did not trust is what kept this findable.

### The correction

**Disallow `Bash` in both arms.** Then:

| Arm | Definition | Visible |
|---|---|---|
| BROAD | `--disallowedTools Bash` | 55, including `Glob`, `Grep`, `Read` |
| SCOPED | disallow everything except `Glob`, `Grep`, `Read` | 3 |

SCOPED becomes a **true subset** of BROAD. The same three capabilities are reachable in both arms, and
the only thing that differs is how many other names sit alongside them — which is the single quantity
`theory/agents/tool-surface-design.md` claims selection happens over.

`Bash` being absent from both arms is also correct on its own terms: the tasks are defect-*reporting*,
no arm needs to execute anything, and leaving a shell in one arm would let it substitute for the search
tools the practice check is built to observe.

### What this changes downstream

- `rig/surfaces/broad.txt` is captured with `--disallowedTools Bash`, not from a bare invocation.
- The disallow list for SCOPED is computed against **that** preimage, so the subtraction is well-defined.
- The read-back assertion still compares `init.tools` to a committed preimage, unchanged — and this
  finding is the strongest argument yet for why it compares against a preimage rather than against the
  flags the driver passed. The flags were consistent throughout; the surface was not what they implied.

### The method note

Both the exploration and Amendment 1 reasoned about surface size from flag semantics, and both were
wrong in the same direction: they assumed disallowing tools can only shrink the surface. One two-probe
comparison, costing under a dollar, found a confound that four reasoning passes had not. That is the
fourth instance in three days of `theory/loops/reading-and-running-find-different-defects.md` behaving
as written, and the second where the wrong reading would have silently invalidated an experiment rather
than producing a visible error.
