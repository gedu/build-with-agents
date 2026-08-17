```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:d3f892d5cf5eb3197b3a1b85822610e281193d5683dd51123ea880effbbb59ed
verdict: fail
blockers: 4
critical_findings: 4
requirements: 20/31
scenarios: 9/19
test_command: python3 rig/collect.py --self-test
test_exit_code: 0
test_output_hash: sha256:31313c822cb28c171708ee6471ab68f89ddd2bd9879a299927be742530fd8640
build_command: ./hooks/pre-commit --all
build_exit_code: 0
build_output_hash: sha256:044a5249118ba4791f84c44a79a7922c1896ee21a6efbcad9117c310af07a70a
```

# Verification Report — failure-flood-triage

## Artifact metadata

The `gentle-ai sdd-verify-validate` gate requires a fenced `yaml` envelope as the first non-empty
content, which is incompatible with `AGENTS.md`'s `---` front-matter contract. The validator is the
hard gate (admission denied means zero writes), so the envelope wins and the queryable fields are
carried here instead. Recorded as SUGGESTION-5 rather than silently dropped.

| Field | Value |
|---|---|
| `id` | `sdd/failure-flood-triage/verify-report` |
| `type` | `journal` |
| `targets` | `[any]` |
| `status` | `draft` |
| `verified` | 2026-08-17 |
| `sources` | `sdd/failure-flood-triage/{spec,design,tasks,apply-progress}.md`, `decisions/0009`, `0010`, `0011`, `0012`, `0013`, `0014` |
| Verified against | commit `fa49b35`, branch `sdd/failure-flood-triage-planning`, tree clean |

SDD verify phase. Independent requirements/runtime verification, run 2026-08-17 against commit
`fa49b35` on `sdd/failure-flood-triage-planning`, tree clean at start and at finish.

**Method, stated because it is the point.** No `[x]` and no done-note was accepted as evidence.
Every number, exit code, digest and output claimed in `tasks.md` that a command can reproduce was
re-derived here with that command, and what could not be re-derived is listed under "Not verified"
rather than assumed to pass. Two done-note claims did not survive that re-derivation; both are
recorded below with the command that contradicts them.

**No countable run was spent.** The Hard Ordering Gate was exercised by extracting `check_prereg()`
verbatim from `rig/run-pipeline.sh:221-266` and running it in isolation against the real repository
and against scratch repositories — never by invoking the pipeline past preflight.

## Verdict

**FAIL — not ready to archive.**

| Severity | Count |
|---|---|
| CRITICAL | 4 |
| WARNING | 6 |
| SUGGESTION | 4 |

The implementation is of high quality and its self-reporting is unusually honest: the ratio failure,
the stage-1 shortfall, the 5.9 gap and the six real bugs found by live testing are all recorded as
failures rather than reinterpreted. The blockers are not sloppiness — they are **four spec
requirements that no artifact tracks as open**. Three of them (`R-F2.2`, `R-F3.2`, `R-F7.3`) appear
in `spec.md` and then in **no** design section, **no** task and **no** blocked-task note. Archiving
now would file a spec whose MUSTs are silently unimplemented as complete.

## Completeness

| Dimension | Result | Evidence |
|---|---|---|
| Tasks checked | 34 of 35 | `rg -c '^\s*- \[x\]' sdd/failure-flood-triage/tasks.md` → 35, of which one (`tasks.md:581`) is an inline correction marker, not a task |
| Tasks open | 1 — task 5.9 | `rg -n '^\s*- \[ \]'` → `tasks.md:1001` only |
| Open task declared | Yes | `## Blocked tasks` names 5.9 and its downstream consumer 6.4 |
| Spec requirements | 31 (`R-F1.1`–`R-F11.2`) | `rg -c '^\*\*R-F[0-9]+\.[0-9]+\*\*' spec.md` |
| Spec scenarios | 19 | `rg -c '^#### Scenario:' spec.md` |
| Requirements met | 20 |
| Requirements partially met | 5 |
| Requirements unmet | 4 |
| Requirements not verifiable here | 2 |

## Build / gate evidence — every command actually run

| Command | Exit | Output |
|---|---|---|
| `./hooks/pre-commit --all` | **0** | `redaction check: clean across 172 tracked files` |
| `./hooks/pre-commit --self-test` | **0** | 3/3 cases pass |
| `bash -n rig/run-pipeline.sh` | 0 | — |
| `bash -n rig/run.sh` | 0 | — |
| `bash -n hooks/pre-commit` | 0 | — |
| `python3 -m py_compile` × 5 (`report.py`, `derive.py`, `collect.py`, `generate-cases.py`, `axis_table.py`) | 0 each | — |
| `python3 rig/collect.py --self-test` | **0** | **14** `[PASS]` lines |
| `python3 rig/collect.py` (no flag) | **2** | required-arguments message; self-test never reached — flag-gating confirmed (R-F1.3) |
| `python3 rig/fixtures/failure-flood/v2/tools/generate-cases.py --self-test` | **0** | 3/3 pass; totals 720/567/432/384/384/336 = **2,823**; prints no ratio |
| `./rig/run-pipeline.sh s1 monolithic 99` (no `--permission-mode`) | **2** | `--permission-mode is required (R-F7.4)` |
| `python3 rig/derive.py --experiment failure-flood-v1` | 0 | 3 rows, all `state=void (shakedown)`; output **byte-identical** to the committed `runs.jsonl` |
| `python3 rig/derive.py` (default) | 0 | 42 rows; output **byte-identical** to the committed `runs.jsonl` |
| `python3 rig/report.py --experiment failure-flood-v1` | 0 | **4** table headers + the excluded-row list |
| `python3 rig/report.py` (default) | 0 | unchanged |
| `git status --porcelain` after all of the above | — | empty |

There is no test runner and no package manager in this repository (ADR 0013), so "run the suite" is
not a verification surface here and none was invented.

## Independently re-derived numbers

Each of these was recomputed here, not read from a done-note.

| Claim (source) | Re-derived | Agrees |
|---|---|---|
| v1 `MANIFEST.sha256` (task 3.5/4.2) | recomputed over `src,tests,runtime,tools,answer-key,prompts`, 12 files | **exact match** |
| v2 `MANIFEST.sha256` (task 3.5/4.4/5.4b) | same convention, 23 files | **exact match** |
| `case-table.sha256` = `b15b8d16…5becb1` (task 3.4) | regenerated into a scratch dir, 2,823 cases | **exact match** |
| Tool-surface digest `d8693e27…f8daa` (task 5.4) | `sha256(sorted(set(31 tools)))` from the committed preimage | **exact match**, and equals the `surface_sha256` read back on all 4 model steps across **both** arms (R-F6.2) |
| Pre-registration digest `83ef1760…a6724` (task 6.6 Part B) | `check_prereg()` extracted verbatim, run against the **real** repo | **exact match** — see below |
| `s2` totals 499 failing / 2,383 passing / 2,882 tests (task 4.3) | `s2.json` `S0.totals` | **exact match** |
| `s1` totals 4 / 32 / 36 (task 4.2) | `s1.json` `S0.totals` | **exact match** |
| `R0` holds exactly 6 causes for s2, 3 for s1 (R-F9.1) | `len(R0)` | **exact match** |
| 42-row peak-occupancy retro-derive (tasks 1.2–1.4, R-F5.3) | 42/42 rows: peak non-null, `occupancy_aggregate_matches: true`, `occupancy_is_monotone: true`, `schema_version: 3`, `context_window_tokens: 1000000`, `model_turns <= num_turns` on every row | **exact match** |
| `rig/run.sh` untouched (R-F6.4) | `git diff --stat main...HEAD -- rig/run.sh` | **empty** |
| Answer-keys committed before prompts (R-F1.1) | `s1.json`/`s2.json` 2026-08-12; `prompts/s1.txt` 2026-08-13 | **checker-before-prompt holds** |
| ADR 0014 before slice 3a (R-F11.1) | ADR `9eccf8d` 2026-08-11; first fixture commit `1c72fa9` 2026-08-12 | **ordering holds** |

## Hard Ordering Gate — all three layers, judged

**Layer 1 (`--shakedown` unconditional).** Read at `rig/run-pipeline.sh:745-749`. The stamp reads no
`DIRTY`, no `DIRTY_OK` and no prior `ARM_STATE` — it is a bare `if [ "$SHAKEDOWN" -eq 1 ]`. This is
exactly the property `rig/run.sh:463-466` lacks. All three committed rows carry
`state=void, void_reason=shakedown`; `report.py` counts **0 of 3**. **Sound.**

One consequence worth naming, which the file itself names: the read-only-substrate check at
`run-pipeline.sh:762-766` runs **after** the shakedown stamp and overwrites `void` with `failed`. A
shakedown run that caught a real violation therefore loses its `shakedown` marker. It does not leak
countability — `failed` is excluded by `report.py`'s `state=="complete"` filter and by layer 3's own
`state == "complete"` precondition — and the tradeoff is reasoned in a comment. Accepted.

**Layer 2 (pre-registration preflight).** Not accepted from the done-note. `check_prereg()` was
extracted verbatim (`run-pipeline.sh:221-266`) into a scratch script and run five ways:

| Case | Result |
|---|---|
| Real repo, v2 fixture, hypotheses committed and clean | **exit 0**, digest `83ef1760de4e283931d4e5bd8174277d17bccd1be16a0cc08ed4104e9d8a6724` |
| Real repo, v1 fixture (no `prereg.json`) | **exit 2** `missing-prereg-config` |
| Scratch repo, no `hypotheses/` | **exit 2** `zero_matches: hypotheses/0002-*.md` |
| Scratch repo, hypotheses present but untracked | **exit 2** `untracked: hypotheses/0002-…` |
| Scratch repo, hypotheses added and committed | **exit 0**, digest **identical to the real repo's** |

**Task 6.6's proof is sound, and its done-note describes its own limits accurately.** Two specific
judgements:

1. The scratch-repo transition it reported is **corroborated, not merely plausible**: the digest it
   printed post-state (`83ef1760…`) is byte-identical to the one the real repository now produces
   with the hypotheses genuinely committed. An isolated scratch proof that reproduces the real
   artifact's digest is a strong proof, not a weak substitute.
2. Its "What this does NOT prove" paragraph is accurate and complete as far as it goes — it names
   the other preflight checks and the fact that nothing past preflight ran. It is honest about the
   `tracked_but_dirty` intermediate state too, and correct that continuing in the real repo would
   have required a commit and then a real `claude -p` invocation.

Not spending a countable run to prove a guardrail was the right call and the substitute was adequate.

**Layer 3 (`derive.py` backstop).** Read at `rig/derive.py:731-733`:
`state == "complete" and not shakedown_used and not prereg_digest` → `void: no-preregistration`.
Downgrade-only, independent of layer 2. **Sound.** Its own comment correctly states it cannot fire
against a run made through today's runner and exists for a row the deriver cannot trust.

## The ratio target — is the FAILED verdict still recorded as failed?

**Yes, at every load-bearing site.** Searched every tracked file for `83:1`, `433`, `500:1`,
`TARGET FAILED`:

- `spec.md:68` — outcome row reads **`~83:1 — TARGET FAILED`**.
- `spec.md:70-80` — "The ratio target FAILED, and it is recorded as failed rather than replaced…
  The target is not softened, reworded, or retroactively swapped for something the measurement
  satisfies." Amplifying to reach the target is rejected **on measurement** (it would push the
  monolithic arm past a 1M window, converting a cost measurement into an impossibility measurement).
- `tasks.md:617-618` — "Achieved ratio = **499:6 (~83.2:1)**, NOT the spec's ~433–500:1 order of
  magnitude — measured, not reached; no injection or axis value was tuned."
- `s2.json:277` — the same verdict with the full per-module yield spread (3.9% to 43.5%).
- `generate-cases.py --self-test` — refuses to print a ratio at all, by design.

**No downstream reinterpretation was found.** One stale pre-failure claim survives, in code rather
than in a journal — see WARNING-1.

## No countable run exists — confirmed

`rig/results/failure-flood-v1/runs.jsonl` holds exactly 3 rows. Every one:
`state=void`, `void_reason=shakedown`, `verdict=null`, `causes_claimed=null`, `causes_correct=null`.
`report.py` names all three in its excluded list. `python3 rig/derive.py --experiment
failure-flood-v1` re-derives them byte-identically from the raw captures, so the committed file is
not a hand-edit. **No artifact claims or implies a measurement that has not happened**; the
apply-progress closing section states it explicitly.

## Task 5.9 and the precision/recall table — honesty check

`report.py`'s diagnostic table does **not** imply population. But the presentation is weaker than
`tasks.md` task 6.4's done-note describes.

Task 6.4's note states the table "prints `causes_claimed/causes_correct are null on every row (task
5.9 not implemented; R-F3.2 cannot be honestly computed yet)` per (task_id, arm)". Run today, that
string **does not appear**. `diagnostic_precision_recall_table()` iterates `_by_task_arm(complete)`,
and `complete` is empty, so the loop body never executes. The header prints; nothing prints beneath
it. The same is true of the other three tables. The channel is named, which is the R-F4.2 property
the PR6 gatekeeping fix restored — but the *reason* is invisible in the output, and the done-note
describes an output that today's data does not produce. See WARNING-4.

## Requirement trace — all 31

| ID | Status | Evidence / gap |
|---|---|---|
| R-F1.1 | **Met** | `C`/`F0`/`S0`/`R0` all present in `s1.json`/`s2.json`; answer-key commits precede prompt commits (git dates) |
| R-F1.2 | **Met (not independently re-run)** | Isolation results recorded per cause in both answer keys; re-running requires `npm ci` + Jest, not attempted |
| R-F1.3 | **Met** | `collect.py --self-test` → exit 0, 14 PASS incl. (b) discrimination and (d) repetition; no-flag → exit 2 without reaching the self-test |
| R-F1.4 | **Met** | self-test (g.1) same file → same signature; (g.2) different files → different signatures |
| R-F2.1 | **Partial** | `suite_state` recorded independently; the run-axis field is named `state`, not `run_state` (inherited from the tool-surface schema). Functionally satisfied, nominally divergent |
| **R-F2.2** | **UNMET** | `suite_state_cause` exists in **no** executable. `git grep suite_state_cause` matches only `spec.md` and two answer-key `_purpose` strings that defer it ("for later classification"). No `void_reason=suite-state-mismatch` anywhere. `derive.py` never reads `S0`. **No design section, no task, no blocked-task note.** Both R-F2.2 scenarios are unimplemented |
| R-F2.3 | **Met** | `collect.py:296` emits a `__suite__` failure record when `suite_state != ran` |
| R-F3.1 | **Met** | Format quoted verbatim in `prompts/s1.txt` and `prompts/s2.txt` (byte-identical files); frozen before any run |
| **R-F3.2** | **UNMET** | No scoring function exists. No `claimed`/`correct` set computation, no `precision`/`recall`, no `^[\w/.\-]+:\d+$` parser, no `ROOT-CAUSE-REPORT` reader anywhere in `rig/`. `causes_claimed`/`causes_correct` are hardcoded `None` (`derive.py:864-865`). Task 5.9 covers only threading the **file** out of the workspace — the scoring function it feeds is a second, untracked gap. The scenario "A malformed report scores as no claims, not a crash" has nothing to exercise |
| R-F4.1 | **Met** | Pair reported per (task_id, arm); nothing blends them (read + run) |
| R-F4.2 | **Partial** | `green_restore_verdict()` returns the four values and reuses `ro_substrate_violation` as the integrity guard, as the spec's own words require. But `C` is frozen in both answer keys and **read by no executable**; the "Deleting a test is caught" scenario is satisfied only indirectly (all tests live under the read-only `tests/` substrate, so deletion trips the hash guard). "Partial credit fires at least once" cannot be satisfied — zero complete rows |
| R-F4.3 | **Met** | Read `report.py` end to end: four separate functions, `occupancy_table` deliberately called twice rather than once for both, no sum/weight/AND anywhere. Confirmed by running both experiment modes |
| R-F5.1 | **Met** | `peak_occupancy_tokens`, `occupancy_series`, `context_window_tokens: 1000000` on every row; `model_turns <= num_turns` on all 42 tool-surface rows (dedup evidence) |
| R-F5.2 | **Met** | `cumulative_occupancy_tokens` non-null on all three failure-flood rows |
| R-F5.3 | **Met** | 42/42 rows: peak non-null, `occupancy_aggregate_matches: true`, `occupancy_is_monotone: true`; full re-derive byte-identical |
| R-F5.4 | **Met** | Peak and cumulative are two separate tables from one function called twice |
| R-F6.1 | **Met** | `materialize_step()` `cp -R`s only `src/`, `tests/`, `runtime/`; the fixture roots contain no `.git` |
| R-F6.2 | **Met** | One committed preimage for both arms; digest reproduced from the file and matching the read-back on all 4 model steps in both arms |
| R-F6.3 | **Partial / unverified** | Re-collect-after-each-cluster is instructed in the prompt prose only; nothing mechanically enforces or checks it, and no run has exercised it |
| R-F6.4 | **Met** | Sibling runner exists; `rig/run.sh` diff across `main...HEAD` is empty; no `--disallowedTools` in `run_model_step` |
| **R-F7.1** | **Partial → UNMET on two clauses** | Recorded: arm, fixture version, `fixture_digest`, `case_table_digest`, `lockfile_sha256`, `prereg_digest`, `code_commit`, per-step `surface_sha256`. **Missing: any hash of the prompt bytes** — `run-pipeline.sh:15-19` says so itself and defers it to task 5.8, which is `[x]` and did not add it, leaving an orphaned deferral. **Model is recorded but not pinned** — `run-pipeline.sh` passes no `--model`, and the three committed rows already show drift (`claude-opus-5[1m]` on `s1-monolithic-01` vs `claude-sonnet-5` on the other two). See CRITICAL-3 |
| R-F7.2 | **Not implemented / not yet applicable** | No N-escalation logic exists in `run-pipeline.sh` or `report.py`; iteration is an operator-supplied argument. The rule is registered in both hypothesis files but nothing enforces or reports it |
| **R-F7.3** | **UNMET for this experiment** | The failure-flood row and its per-step records carry `occupancy_series`, `peak/cumulative_occupancy_tokens`, `model_turns`, `bash_call_count`. They carry **no** separate `input`, `output`, `cache_read_input` or `cache_creation_input` fields, and **no tool-call names** — only a Bash count. Occupancy is precisely the "single total" the requirement forbids. `tool-surface-v1`'s own rows do carry all four plus a `tool_calls` list, so this is a regression in the new row builder, not a repo-wide limitation. Untracked by any task |
| R-F7.4 | **Met** | Live: invocation without `--permission-mode` → exit 2. `declared_permission_mode` on the row; `permission_mode_matches_declared: true` on all 4 model steps; `derive.py:752` voids on mismatch |
| R-F8.1 | **Met** | Both files exist, are tracked, are committed clean; `check_prereg()` returns exit 0 with a digest, and exit 2 in every failure branch tested |
| R-F8.2 | **Met** | Unconditional stamp verified by reading; all three rows carry it, including one run with `dirty_ok_used: false` on a genuinely clean tree |
| R-F9.1 | **Partial, honestly** | Stage 2 holds exactly 6 causes (`len(R0) == 6`). Stage 1 measured **4** failing cases, not the stated 10 — recorded as a structural property of the donor tests, explicitly "not tuned to reach 10". "Real failures of real logic" was verified empirically at task 3.3 by a scratch mutation (49/392); not re-derivable here without Jest |
| R-F9.2 | **Met** | Achieved ratio measured, recorded, and shipped with the stated comparison to ~500:1; the generator refuses to print a ratio it cannot measure |
| R-F10.1 | **Met** | No field or schema name contains a tool name; `collector: "jest-json@1"` is a value, and `collect.py:90` addresses exactly this |
| R-F11.1 | **Met** | ADR 0014 exists and predates the first fixture commit |
| R-F11.2 | **Met** | Clause B declines ADR 0013's trigger on the record and restates it more sharply |

## Issues

### CRITICAL

**CRITICAL-1 — `R-F2.2` (`suite_state_cause`) is unimplemented and untracked.**
The spec makes it a MUST with two worked scenarios and names it in Key Learning #1 as the mechanism
that "still resolves the run-axis/suite-axis conflict". Nothing implements it: no field, no
`suite-state-mismatch` void reason, and `derive.py` never reads `S0` at all. It appears in **no**
design section, **no** task, and **no** blocked-task note — `git grep suite_state_cause` returns only
`spec.md` and two answer-key `_purpose` strings that explicitly defer it to "later". Consequence: an
environment-caused suite failure would be scored as an injection-caused one, which is the exact
confusion R-F2 exists to prevent. Because it is untracked, archiving would record it as delivered.

**CRITICAL-2 — `R-F3.2` (attribution scoring) is unimplemented, and task 5.9 does not cover all of
it.** Task 5.9 is correctly open and correctly identified as blocking 6.4. But 5.9's scope is
threading `root-cause-report.txt` out of the ephemeral workspace. The scoring function R-F3.2
specifies — deduplicated `claimed` set, `correct = claimed ∩ RC_true`, `precision` reported `n/a`
when `claimed` is empty, `recall`, and the malformed-file-is-not-a-crash behaviour — does not exist
anywhere in `rig/`. R-F3.2 is the **primary outcome channel** (R-F4.1). Closing 5.9 alone would not
produce a number; a second, currently unnamed work unit is required.

**CRITICAL-3 — the model is not pinned, and the committed data already shows it drifting.**
ADR 0010 is "vary the harness, not the model"; R-F7.1 requires the model id "fixed across arms".
`rig/run-pipeline.sh` passes no `--model` to `claude -p` (`run-pipeline.sh:614`), so the model is
inherited from ambient CLI configuration — structurally the identical hazard R-F7.4 was written to
close for `permission_mode`, left open for the one variable ADR 0010 cares most about. This is not
hypothetical: the three committed rows carry **two different models** (`claude-opus-5[1m]` and
`claude-sonnet-5`), including two `s1-monolithic` runs that disagree with each other.
`build_row_failure_flood` has **no** `model-mismatch` void, although `build_row` (tool-surface-v1)
has one at `derive.py:474`. A countable `s2` comparison started today could silently run its two
arms on two different models and produce a result attributed to harness shape.

**CRITICAL-4 — `R-F7.3` regression: per-turn token components are not recorded for this
experiment.** The requirement is explicit that input, output, `cache_read_input` and
`cache_creation_input` are recorded **separately, never a single total**, plus tool-call count *and
names*. The failure-flood row and step records carry only derived occupancy sums plus
`bash_call_count`. `tool-surface-v1` rows carry all four components and a full `tool_calls` list, so
the capability exists and was not carried into the new row builder. Untracked by any task.

### WARNING

**WARNING-1 — ADR 0009 documentation-trap violation, introduced by this cycle.**
`sdd/failure-flood-triage/apply-progress.md:798` contains a literal redaction-search pattern that
instantiates the maintainer's surname and employer name as real values, in a committed file of a
public repository. ADR 0009 and `AGENTS.md` both carry this as a named rule: *"Never paste a real
value in order to describe how to find it. Redaction patterns, search commands and incident
write-ups describe the shape of the forbidden string and never contain an instance of it."* ADR 0009
exempts a bare **first** name only. Introduced by commit `4394833` (PR4); it is the sole occurrence
in the tracked tree. `hooks/pre-commit` cannot catch it — it gates the path class only, and ADR 0009
says so — so the repeated `redaction check: clean` citations in the done-notes are not evidence about
this class. Note that the absolute repository path itself appears in **no** committed file:
`git grep -F '/Users/'` over the tracked tree returns nothing.

**WARNING-2 — a stale pre-failure ratio claim survives in committed code.**
`rig/fixtures/failure-flood/v2/tools/axis_table.py:19-21` still reads: "landing the aggregate in the
~2,600-3,000 / ~433-500:1 target band". This is a docstring, not an append-only journal entry. Read
against generated counts it is true (2,823 generated, 470:1); read against `R-F9.2`'s own definition
of the ratio (`total_failing_cases / 6`) it asserts a band the measurement refuted at 83:1. It
preserves exactly the generated-vs-failing conflation `spec.md:118-127` identified as the original
error. The trailing clause ("achieved counts are reported by generate-cases.py itself, never assumed
here") mitigates but does not correct it.

**WARNING-3 — `derive.py`'s R-A1.4 self-test is empty for `failure-flood-v1` and looks like output.**
`python3 rig/derive.py --experiment failure-flood-v1` prints
`checker self-test (R-A1.4 — each detector must be observed to fire):` followed by **nothing**.
`run_self_tests()` skips every answer key lacking `tool_sets` (`derive.py:380`), which is all of
failure-flood's. The skip is honestly reasoned in the code comment and in task 5.8's done-note, so
this is not a false claim — but the *printed* result is an empty section under a header asserting
that every detector was observed to fire, which is the same silent-empty-section shape as the
green-restore defect PR6 gatekeeping caught. None of failure-flood-v1's own detectors
(`no-preregistration`, `surface-mismatch`, `permission-mode-mismatch`, green-restore,
`ro_substrate_violation`) is proven to fire by any self-test.

**WARNING-4 — task 6.4's done-note describes report output that today's data does not produce.**
It states the diagnostic table prints the `causes_claimed/causes_correct are null on every row (task
5.9 not implemented…)` message "per (task_id, arm)". With zero complete rows the per-key loop
produces no lines at all, so the message is absent from the real output. Verified by running
`python3 rig/report.py --experiment failure-flood-v1`. The claim is not false about the code, but it
is false about the artifact a reader will see, and it was written in the same note that corrected an
earlier false claim about the same four tables.

**WARNING-5 — step/suite timeouts are still labelled placeholders after the measurement that was
supposed to retire them.**
`run-pipeline.sh:82-89`: `STEP_TIMEOUT_S=180`, `SUITE_TIMEOUT_S=150`, commented "Both PLACEHOLDERS
pending task 5.7's real wall-clock measurement (not run by this unit)", citing `rig/run.sh:59-67`'s
"re-derive it, do not nudge it" precedent. Task 5.7 ran and is `[x]`, but the placeholders were not
re-derived. Measured against the real captures: `03-apply` on `s2-pipeline-9054` took **120,207 ms**
— 67% of the 180 s budget — and `01-monolith` on `s1-monolithic-01` took **101,475 ms** on the far
smaller v1 fixture. A countable `s2` monolithic run reading a 0.35 MB flood is the longest step this
design has, and it has never been timed. Non-trivial risk that the first countable run voids on
`timeout`.

**WARNING-6 — the run-axis field is named `state`, not `run_state` (R-F2.1).**
Consistent with the pre-existing tool-surface schema and functionally correct (nothing derives it
from `suite_state`), but the spec names a field that no row carries. Either the spec or the schema
should say the same thing.

### SUGGESTION

**SUGGESTION-1 — a stated total does not equal the sum of its own parts, in the cycle that
registered that exact rule.** Task 4.3's verify line claims `rig/collect.py --self-test` passes
"all 15 cases PASS (a, b, c.1–c.4, d, e, f, g.1, g.2, h.1, h.2, i)". The enumerated list holds 14
items and the command emits **14** `[PASS]` lines (`| grep -c '[PASS]'` → 14). `BACKLOG.md` entry 1
rule (b) is precisely "a stated total must equal the sum of its own stated parts", and names "a
second and third occurrence" as its unblock trigger. This is a candidate second occurrence.

**SUGGESTION-2 — `C` is frozen in both answer keys and read by nothing.** R-F4.2's "Deleting a test
is caught" scenario names a post-run-identifier-set-versus-`C` comparison; the implementation relies
on the read-only-substrate hash guard instead. That works for this fixture because every test lives
under `tests/`. Either implement the `C` comparison or record in the spec that the hash guard
subsumes it for import-free fixtures.

**SUGGESTION-3 — the four failure-flood tables print bare headers with no "none" line.** The
excluded-rows table uses `or ["none"]`; the other four do not. A `(no complete rows)` line would make
the empty state self-explaining, and would carry the 5.9 reason into the output where WARNING-4 shows
it is currently missing.

**SUGGESTION-4 — `apply-progress.md:513` still asserts "~470:1 — inside the operator-confirmed
~433–500:1 band" at its own site.** The correction lands 574 lines later at `apply-progress.md:1087`.
Append-only journalling is the right discipline and `tasks.md:367-375` does carry an in-place
`CORRECTION 2026-08-12`, so this is presentational only — but a one-line forward pointer at the
original site would stop a reader quoting the superseded figure.

**SUGGESTION-5 — the verify-report cannot satisfy both `AGENTS.md` and the native validator.**
`gentle-ai sdd-verify-validate` denies admission unless a fenced `yaml` envelope is the first
non-empty content; `AGENTS.md`'s frontmatter contract says every content file starts with a `---`
block. This file resolves it in the validator's favour and carries the frontmatter fields as a table
under "Artifact metadata". Worth an explicit repo decision so the next verify-report does not
re-litigate it.

## Design coherence

| Design decision | Code state | Note |
|---|---|---|
| Sibling runner, `run.sh` untouched (R-F6.4) | Holds | `git diff main...HEAD -- rig/run.sh` empty |
| Decision 9a — generated rows never committed | Holds | `rig/results` carries no case rows; `cases/` generated to scratch only |
| Decision 9a — `tools/`/`answer-key/`/`prompts/` never materialised | Holds | `manifest_workspace_paths()` filters to `src/tests/runtime` |
| Decision 9b — bounded `clusters/1` view | Holds | `member_test_ids` absent; self-test case (f) proves it |
| Design "File changes" claims v1 gets `tools/generate-cases.py` | **Stale** | Contradicted by R-F9.1 and by disk. Flagged at task 3.5, still unfixed — carried forward, pre-existing |
| Design's four-item ADR-0014 self-test roster | **Internally inconsistent** | Flagged in PR1's own findings; does not change Clause B's decision |

## Not verified — stated rather than assumed

These could not be checked in this environment and are **not** counted as passing:

1. **Every claim requiring a Jest run.** No package manager or `node_modules` is present, and the
   fixture suite needs `npm ci`. This covers: the clean-baseline zero-failure claims (tasks 3.1/3.2),
   the per-injection isolation signatures (4.1/4.3), the 2,882-passing amplified clean run, and the
   R-F9.1 empirical "real failures of real logic" mutation (49/392). Their evidence here is the
   committed answer keys plus done-notes only.
2. **`check_prereg()`'s `more_than_one_match` and `tracked_but_dirty` branches.** Four of six
   branches were exercised directly; these two were not (task 6.6 shows `tracked_but_dirty` firing
   live, which I did not reproduce).
3. **Every live-tamper claim** (MANIFEST accept-before/reject-after, case-table digest tamper,
   `hash_paths` before/after, the five task-5.5 substrate-violation cases). The *current* state was
   re-derived — both manifests and the case-table digest match exactly — but the tamper transitions
   were not re-performed, to avoid dirtying tracked fixture bytes.
4. **Anything that requires a countable run**: R-F7.2's sampling escalation, R-F4.2's "partial credit
   fires at least once" scenario, R-F6.3's re-collect behaviour, and both hypotheses.

## What must happen before archive

| # | Action | Blocks archive |
|---|---|---|
| 1 | Implement `R-F2.2` (`suite_state_cause` + `suite-state-mismatch` void), or amend the spec to withdraw it with a recorded reason | Yes |
| 2 | Register the `R-F3.2` scoring function as a task in its own right, distinct from 5.9 | Yes |
| 3 | Pin `--model` in `run-pipeline.sh` and add a `model-mismatch` void to `build_row_failure_flood` | Yes — a countable run is unsafe without it |
| 4 | Record `R-F7.3`'s four token components and tool-call names per model step, or amend the requirement | Yes |
| 5 | Remove the literal redaction pattern at `apply-progress.md:798` | Yes — public repo, ADR 0009 |
| 6 | Re-derive `STEP_TIMEOUT_S`/`SUITE_TIMEOUT_S` from task 5.7's real wall clocks | No, but do it before the countable run |
| 7 | Correct `axis_table.py:19-21`'s target-band claim | No |
| 8 | Correct task 6.4's and task 4.3's done-notes | No |

**Verdict: FAIL.** Return to `sdd-apply` for items 1–5, or obtain an explicit operator decision to
amend `spec.md` and record the withdrawn requirements. Task 5.9 is correctly open and correctly
declared; it is not the blocker. The blockers are the three requirements nothing tracks and the one
redaction line.

## Key Learnings

1. A per-key loop over an empty collection prints a header with no body and reads identically to a
   channel that had no data — the same shape twice in this cycle, in `report.py` and in `derive.py`.
2. An isolated scratch-repo proof becomes strong evidence when its digest reproduces byte-identically
   against the real repository once the real preconditions land.
3. A requirement that reaches `spec.md` but never reaches design or tasks leaves no `[ ]` anywhere,
   so task-completion counting cannot detect it — only an ID-by-ID trace can.
4. Recording a variable is not pinning it: three shakedown rows on one experiment already carry two
   different model ids because the runner passes no `--model`.
5. A redaction rule is most likely to be broken by the paragraph documenting how the redaction was
   checked, which is why ADR 0009 states that as a rule rather than a caution.
