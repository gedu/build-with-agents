---
id: sdd/failure-flood-triage/verify-report
type: journal
targets: [any]
status: draft
verified: 2026-08-18
sources: ["sdd/failure-flood-triage/spec.md", "sdd/failure-flood-triage/tasks.md", "sdd/failure-flood-triage/apply-progress.md", "sdd/failure-flood-triage/design.md"]
---

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:b6bf1d11b633cf765701e18748ae82483c705d17f0321ac77ec4b35a02d0d0a6
verdict: fail
blockers: 1
critical_findings: 1
requirements: 24/31
scenarios: 12/19
test_command: python3 rig/derive.py --self-test
test_exit_code: 0
test_output_hash: sha256:ec410c539bf625bd78adb5cdfd7097629b1d97d32a16679b456c4a3f7eb34741
build_command: ./hooks/pre-commit --all
build_exit_code: 0
build_output_hash: sha256:fa1cb7af2c3423d538542fc5d5c74470bebc7a41d6749e16e09ea099a25c2ad1
```

# Verification Report — failure-flood-triage

## Round 2 — 2026-08-18. This section SUPERSEDES the 2026-08-17 verdict below

The 2026-08-17 report is retained verbatim under "Superseded — round 1". Its findings and their
resolutions are the record; nothing in it is deleted. Where round 2 contradicts round 1, round 2
wins and says so explicitly.

| Field | Value |
|---|---|
| `id` | `sdd/failure-flood-triage/verify-report` |
| `type` | `journal` |
| `targets` | `[any]` |
| `status` | `draft` |
| `verified` | 2026-08-18 |
| `sources` | `sdd/failure-flood-triage/{spec,design,tasks,apply-progress}.md`, `decisions/0009`–`0013`, `0015` |
| Verified against | commit `3172930`, branch `sdd/failure-flood-triage-planning`, tree clean at start and finish |
| Batches under review | `713a3ec` (PR7A), `9aa7c65` (PR7B), `3172930` (PR7C), `ca43bde` (ADR 0009 fix) |

**Method.** No `[x]`, no done-note and no commit message was accepted as evidence of closure. Each of
round 1's four CRITICALs was re-derived from source plus execution. Where round 1 relied on reading,
round 2 additionally ran an adversarial probe. No countable run was spent: every claim below comes
from a `--self-test`, a mutation of a copy in a scratch tree, a re-derive of already-committed
captures, an argument-gate rejection that exits before any invocation, or git inspection.

### Round 2 verdict

**FAIL — one blocker, but it is not any of round 1's.**

| Severity | Count | Change from round 1 |
|---|---|---|
| CRITICAL | **1** (new) | round 1's 4 are **all closed** |
| WARNING | **11** | 5 of 6 carried forward, 1 closed, 6 new |
| SUGGESTION | **5** | 4 carried forward unchanged, 1 restated |

All four round-1 blockers are genuinely closed, and the closures survive adversarial probing rather
than merely matching their done-notes. The single new blocker was not introduced by this change and
is not an implementation defect: **`main` created a second ADR numbered 0014 six days after this
branch created its own.** Nothing tracks it, and archiving would file `R-F11.1` as delivered against
an identifier that resolves to two different documents.

---

## Round 1's four CRITICALs, re-derived one by one

### CRITICAL-1 — `R-F2.2` (`suite_state_cause`): **CLOSED**

| Check | Evidence |
|---|---|
| Function exists | `rig/derive.py:762-790` `suite_state_cause(observed_suite_state, observed_failures, s0)` |
| Wired into the row builder | `rig/derive.py:975` — called inside the `state == "complete"` block |
| `environment` forces void | `rig/derive.py:976-978` → `state="void"`, `void_reason="suite-state-mismatch"`, anomaly class added |
| Field published on the row | `rig/derive.py:1053` `"suite_state_cause"` |
| Downgrade-only | The block runs only while `state` is still `complete`; it can never upgrade a row an earlier check voided |
| Self-test coverage | 7 direct cases + 4 integration cases |

**The control was proven to fire, not assumed.** `suite_state_cause` was mutated in a scratch copy to
`return "injection"` unconditionally:

```
--- MUTATION [M1_suite_state_cause_always_injection] EXIT=1  PASS=31 FAIL=6
  [FAIL] suite_state_cause: did-not-start vs frozen ran -> environment
  [FAIL] suite_state_cause: no S0 -> None
  [FAIL] suite_state_cause: no observed suite_state -> None
  [FAIL] suite_state_cause: did-not-start, different signature -> environment
  [FAIL] suite_state_cause: did-not-start, no signature present -> environment (conservative)
  [FAIL] build_row_failure_flood case2 (environment -> void): state forced to void=False, ...
```

**On the synthetic-only disclosure: the disclosure is accurate, and sufficient as far as it goes —
but it understates the gap by one step.**

Accurate: both fixtures' frozen `S0.suite_state` is `"ran"`, so `suite_state_cause` collapses to a
plain equality check for every row derivable today, and the docstring says exactly that, names the
signature branch as future-fixture-only, and states the conservative default.

Understated: **neither frozen `S0` contains a `signature` key at all.** Their key sets are exactly
`['_purpose', 'identifier_set_digest', 'suite_state', 'totals']`. So R-F2.2's "*and its normalized
signature exactly match the frozen `S0`*" half has no frozen counterpart in committed data — it is
not merely unexercised, it is unexercisable, and would remain so even if a future run produced
`did-not-start`. Recorded as WARNING-7, not as a blocker: the code's conservative default
(`environment` when no frozen signature is available) means the absence downgrades rather than
fabricates a match, which is the correct failure direction.

### CRITICAL-2 — `R-F3.2` (attribution scoring): **CLOSED**

| Spec clause (`spec.md:284-287`) | Implementation | Verified by |
|---|---|---|
| `claimed` = deduplicated set of valid lines | `parse_root_cause_report` `derive.py:700-720` — returns a `frozenset` | self-test case "duplicate lines deduplicated" |
| empty if malformed | returns `None` → `frozenset()` at `:739-740` | cases: malformed prose, missing sentinel, one bad line, empty string |
| empty if missing | `read_root_cause_report_handoff` returns `None` | case "no handoff file -> causes_claimed == []" |
| `correct = claimed ∩ RC_true` | `derive.py:741` | case "correct = intersection" |
| `RC_true` = frozen file:line set from `R0` | `derive.py:996` `{d["cause_site"] for d in ak["R0"]}` | `s1.json` len(R0)=3, `s2.json` len(R0)=6 |
| `precision` reported `n/a` when `claimed` empty, never silently 0 | `report.py:263-272` | read + `report.py --self-test` |
| `recall` = correct over `RC_true` | `report.py:266` divides by `causes_present`; `derive.py:1071` defines `causes_present = len(ak["R0"])` | arithmetic identity confirmed |
| Both arms scored by the identical function | one function, no arm branch | read end to end |

**It reads the frozen file, never chat prose — confirmed at both ends of the handoff.**
`read_root_cause_report_handoff` (`derive.py:745-759`) scans `steps_meta` for
`steps/<step>/handoff/root-cause-report.txt`. That file is produced by `run-pipeline.sh:705-708`,
which copies the workspace file and is gated to `role = monolith` or `role = apply` — each arm's own
final model step, deliberately never the diagnose step's stale intermediate. There is no
`result.result` read anywhere in the scoring path.

**Malformed and missing score as no claims without crashing** — proven, not asserted. Self-test
covers malformed prose, `None`, hostile binary bytes, and a non-ASCII path; all return
`claimed = []` and raise nothing. Mutation control:

```
--- MUTATION [M3_parse_root_cause_always_none] EXIT=1  PASS=30 FAIL=7
```

**`design.md`'s stale diagram is STILL uncorrected, and there are two stale lines, not one.**

- `design.md:608` — "scoring: CAUSE lines parsed from `result.result` in BOTH arms" — describes the
  chat-prose channel R-F3.1 replaced.
- `design.md:599` — "both arms' final text carries the frozen `CAUSE <path>:<line> <cluster_ids>`
  lines" — a different, older format entirely, superseded by `ROOT-CAUSE-REPORT v1` plus bare
  `path:line`.

`derive.py:728-730` names the staleness in its own docstring and implements to `spec.md` correctly,
so no code is wrong. But the design artifact was never amended, and round 1 flagged only the first of
the two lines. Recorded as WARNING-8.

### CRITICAL-3 — the model pin: **CLOSED**

**Required, no default, and the rejection is real.** `run-pipeline.sh:365`. Five invocation shapes run
live, each exiting before any `claude` invocation:

| Invocation | Exit | Message |
|---|---|---|
| `--permission-mode bypassPermissions` (no `--model`) | **2** | `--model is required (ADR 0010, R-F7.1) — declare the exact model id/alias per invocation, never inherited` |
| `--model claude-sonnet-5` (no `--permission-mode`) | **2** | `--permission-mode is required (R-F7.4) — one of: …` |
| neither flag | **2** | `--permission-mode is required (R-F7.4) — …` |
| `--model` with no value | **2** | `--model requires a value` |
| `--model ""` | **2** | `--model is required (ADR 0010, R-F7.1) — …` |

`rig/runs/` was digested before and after all five: identical, `53ae6547…e56af`.
`git status --porcelain` empty throughout.

**The declared value reaches `claude -p`.** `run-pipeline.sh:651-653` is the only `claude -p`
invocation in the file (the other three `claude` mentions are a usage-text reference, a `command -v`
presence check, and `claude --version`), and it carries `--model "$MODEL"` where `$MODEL` is the
parsed argument.

**The read-back compares correctly.** `read_back_init` (`:287-313`) parses `model` from the same
`system/init` event, by the same function, in the same pass as `permissionMode` and the tool surface.
`write_step_status` (`:581-583`) records `declared_model`, `model_actual`, and
`model_matches_declared`.

**The void uses the declared-value comparison, not self-consistency.** `derive.py:883-886`, on
`model_matches_declared is False`. Deliberately stronger than `build_row`'s tool-surface check, which
cannot distinguish two internally consistent runs on different models — the exact shape the three
committed rows already exhibit.

**Adversarial probe against the LIVE committed surface preimage** (the self-test isolates the model
check with an empty surface; this probe does not):

| Probe | Result |
|---|---|
| Real mismatch, surface correct | `state=void`, `void_reason=model-mismatch` |
| CONTROL — matching model, surface correct | `state=complete`, `void_reason=None` (the void is not always-on) |
| `declared_model: null` with `model_matches_declared: False` | `state=void`, `void_reason=model-mismatch` |
| No `init` event at all (so `model_actual` is null) | `state=void`, `void_reason=surface-mismatch` — the earlier surface check closes this hole |
| `model_matches_declared` key **absent entirely**, surface correct | `state=complete`, `void_reason=None` — **passes silently** |

Mutation control on the void itself:

```
--- MUTATION [M2_model_mismatch_void_disabled] EXIT=1  PASS=36 FAIL=1
  [FAIL] build_row_failure_flood: model_matches_declared=False -> state=void, void_reason=model-mismatch
```

**The three pre-existing `declared_model: null` rows are handled honestly and do not pass as
"matching".** Their per-step `status.json` files carry no model keys at all (they predate the flag),
and all three rows are `state=void, void_reason=shakedown`. The model check sits inside
`if state == "complete"`, so it is never reached for them; they are excluded from every count by
state, and the row records `declared_model: null` — an honest "not declared", never a fabricated
match. Confirmed by reading all 11 committed `status.json` files and all 3 rows.

The last probe row is the one residual: a **complete** row whose step status lacks the comparison
field passes with no void. Today's runner cannot produce that shape (`write_step_status` writes all
three model fields unconditionally) and no committed row has it, so this is not a blocker — but there
is no downgrade backstop equivalent to the `no-preregistration` layer-3 check that exists for exactly
this class of untrustworthy row. Recorded as WARNING-10.

### CRITICAL-4 — `R-F7.3` token breakdown: **CLOSED for the clause round 1 named; one literal spec clause remains unmet**

Round 1's finding was that the failure-flood row and step records carried "no separate `input`,
`output`, `cache_read_input` or `cache_creation_input` fields, and no tool-call names — only a Bash
count". That is closed:

| Level | Fields | Site |
|---|---|---|
| Per model step | `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `tool_calls` (name + `is_error`) | `derive.py:924-929` |
| Per run | the same four, summed separately, plus a concatenated `tool_calls` | `derive.py:946-954`, row `:1047-1051` |

Never folded into occupancy: occupancy remains a separate R-F5 channel, and the four components are a
parallel field set. Verified on committed data (row 1: `input_tokens=36`, `output_tokens=4452`,
`cache_creation_input_tokens=38985`, `cache_read_input_tokens=914069`, 18 named tool calls). Two
mutation controls fire:

```
--- MUTATION [M4_row_input_tokens_zeroed]  EXIT=1 PASS=36 FAIL=1  [FAIL] ... row input_tokens
--- MUTATION [M5_tool_calls_dropped]       EXIT=1 PASS=36 FAIL=1  [FAIL] ... row tool_calls names
```

**Residual, stated because the requirement's own words are narrower than what landed.** R-F7.3 reads
"*Per role, **per turn***". What landed is per-role (one step is one role's one invocation) and
per-run. Per-turn remains only `occupancy_series` — one derived total per turn, which is precisely the
"single total" shape the requirement forbids. The data is present in the raw captures (the s1 monolith
step's transcript carries 31 assistant events, each with `input_tokens`, `output_tokens`,
`cache_read_input_tokens`, `cache_creation_input_tokens`), so this is an extraction that was not done,
not information that was lost. Recorded as WARNING-9.

---

## The new blocker

### CRITICAL-5 (NEW) — two different ADRs are both numbered 0014

| Lineage | File | First commit |
|---|---|---|
| This branch | `decisions/0014-a-fixtures-runtime-is-substrate-not-this-repos-runner.md` | `7a5c066`, 2026-08-11 |
| `main` | `decisions/0014-a-public-guarantee-cannot-be-opt-in.md` | `a46794a`, 2026-08-17 |

```
$ diff <(git ls-tree -r --name-only HEAD -- decisions/) <(git ls-tree -r --name-only main -- decisions/)
< decisions/0014-a-fixtures-runtime-is-substrate-not-this-repos-runner.md
> decisions/0014-a-public-guarantee-cannot-be-opt-in.md
```

This branch created `0014` first and it is this change's own `R-F11.1` deliverable ("a narrow ADR
approved before slice 3a"). `main` took the same number six days later. The branch's `0014` is cited
by 9 tracked files including `spec.md`, `rig/run-pipeline.sh`, `rig/README.md` and both fixture
runtimes; `main`'s is cited by `MAP.md` in three places. `MAP.md` itself already disagrees:

| Lineage | `MAP.md` line |
|---|---|
| branch | `0001`–`0014` ratified |
| `main` | `0001`–`0013` ratified; `0014` **draft**, implemented but not ratified |

**Why this blocks archive rather than merge alone.** `decisions/` is citable as truth unconditionally
in this repository (ADR 0009's own words), so a duplicated identifier breaks the citation namespace in
both directions: every existing "ADR 0014" reference becomes ambiguous the moment the two histories
meet. Archiving files `R-F11.1` as met against that identifier, and **no artifact tracks the
collision** — the same failure shape as round 1's CRITICAL-1/-2, where a real gap left no `[ ]`
anywhere for task counting to find.

This is not an implementation defect and the remedy is an operator decision (renumber one lineage and
update its citations), which is outside this phase's authority.

**Resolution (PR7D, 2026-08-18).** The operator decided: `main`'s `0014-a-public-guarantee-cannot-be-
opt-in.md` keeps `0014` — it was already pushed to the public remote (`a46794a`, 2026-08-17) before this
collision was found, and a public identifier is load-bearing for outside citers in a way an unpushed one
is not, chronology of ratification aside. This branch's `0014-a-fixtures-runtime-is-substrate-not-this-
repos-runner.md` was renamed to `decisions/0015-a-fixtures-runtime-is-substrate-not-this-repos-runner.md`
in this same batch, with a renumbering note added to the ADR's own frontmatter and body, and every
citation to it in `spec.md`, `tasks.md`, `MAP.md`, `rig/README.md`, `rig/run-pipeline.sh`,
`rig/fixtures/failure-flood/{v1,v2}/runtime/package.json`, and
`rig/fixtures/failure-flood/v2/tools/generate-cases.py` updated to `0015`. This finding above, and the
collision it documents, are left standing exactly as round 2 found them; this note records the remedy
without rewriting the finding. Closes action item 1 of "What must happen before archive" below.

**Related, and part of the same drift.** `main`'s `a46794a` also rewrote `hooks/pre-commit` (+99
lines) and added `hooks/redaction-patterns.sh`, `hooks/commit-msg` and `check.sh`. Every
`redaction check: clean` citation in this stack — including this report's own `build_command` — was
produced by the **branch's older** `hooks/pre-commit`, not `main`'s. The substantive ADR 0009 result
below was obtained by an independent scan and does not depend on which checker ran, but the cited gate
output does.

### Correction to the orchestrator's own pre-flight claim

The launch brief stated the branch is "0 commits behind `main`". Re-derived:

```
$ git rev-list --count HEAD..main
3
$ git log --oneline HEAD..main
1801fd2 fix(check): skip generated symlinks, and isolate the self-test fixture
a46794a feat(hooks): give three unverified rules a verifier
e0b5b0b docs(agents): point the executor at ASK.md
```

Three commits, one of which is the ADR-0014 collision above. Everything else in the brief was
confirmed; this one item was not.

---

## Orchestrator claims re-derived rather than accepted

| Claim | Verdict | Evidence |
|---|---|---|
| Both required-argument gates reject at exit 2, `rig/runs/` unchanged | **CONFIRMED** | 5 rejection shapes, all exit 2; `rig/runs/` digest identical before/after; tree clean |
| `tool-surface-v1`: 42 to 42 rows, zero fields added, zero mismatches on pre-existing fields | **CONFIRMED** | Field-set diff vs `fa49b35`: added none, removed none; the only changed field name across all 42 rows is `checker_digest` |
| `failure-flood-v1`: only `suite_state_cause` plus PR7A's six fields added; no pre-existing value changed; additive inside each `steps` entry | **CONFIRMED** | 7 row fields added (`declared_model`, `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `tool_calls`, `suite_state_cause`); inside `steps`: 5 keys added, 0 removed, **0 pre-existing key value changes**, 0 top-level changes. `schema_version` 1 to 3 |
| `derive.py --self-test` exit 0, `report.py --self-test` exit 0 | **CONFIRMED** | plus `bash -n` x3, `py_compile` x3, `collect.py --self-test` (14 PASS), `pre-commit --all` and `--self-test`, all exit 0 |
| `report.py --self-test` fires under mutation | **CONFIRMED INDEPENDENTLY** | forced `occupancy_table` to a fixed channel, exit 1, channel-isolation case `[FAIL]` |
| `derive.py --self-test` mutation test (not previously done) | **DONE — control fires** | see below |
| "0 commits behind `main`" | **REFUTED** | 3 commits behind |

### `derive.py --self-test` is a real control

Five independent defects injected into a copy in a scratch tree (the real file was never modified;
`git status --porcelain` empty throughout). Baseline in the same scratch tree: exit 0, 37 `[PASS]`,
0 `[FAIL]`.

| Mutation | Exit | PASS/FAIL | Failing case |
|---|---|---|---|
| `suite_state_cause` always returns `injection` | **1** | 31/6 | the 5 classification cases plus integration case 2 |
| model-mismatch void disabled | **1** | 36/1 | `model_matches_declared=False -> void` |
| `parse_root_cause_report` always returns `None` | **1** | 30/7 | 3 parse plus 3 scoring cases |
| row `input_tokens` forced to `0` | **1** | 36/1 | `token breakdown: row input_tokens` |
| row `tool_calls` forced to empty | **1** | 36/1 | `token breakdown: row tool_calls names` |

Every mutation produced exit 1 and the *specific* expected failing case, not a blanket failure. The
self-test cannot pass a broken deriver.

**One note on the reported count, which is NOT a rule-(b) violation.** `apply-progress.md` renders the
result as "49/49 `[PASS]`". The command emits **37** `[PASS]` lines carrying **49** assertions (26
single-assertion cases plus 7 token-breakdown assertions plus 4 integration cases carrying
5+5+3+3=16). The stated total does equal the sum of its own stated parts; only the `[PASS]` label is
attached to the wrong number. Distinguished here explicitly from SUGGESTION-1, which is a genuine sum
mismatch.

---

## Task 5.9's re-scoping — honest, and both halves are closed

**Honest.** `tasks.md:1027-1038` states it in the first sentence: *"this task's own original scoping
was insufficient, stated plainly rather than quietly amended"*, then *"5.9 named only HALF of what
closing R-F3.2 requires"*, then *"Closing 5.9 as originally worded would have produced a file on disk
and still no number — exactly the gap the verify-report caught."* The original registration text is
left intact above the correction rather than edited, and the second half is registered as its own task
7.6 per round 1's explicit recommendation. That is the discipline round 1 asked for.

**Both halves closed:**

| Half | Where | Verified by |
|---|---|---|
| Threading `root-cause-report.txt` out of the ephemeral workspace | `run-pipeline.sh:705-708`, role-gated to `monolith`/`apply` | reading plus `bash -n` exit 0 |
| The scoring function | `derive.py:700-742`, wired at `:994-998` | 14 self-test cases plus mutation M3 |

**Residual on the first half.** The threading is a bash `cp`; no test exercises it, because no run
since PR7B has produced a `root-cause-report.txt` and `bash -n` proves only syntax. The read side is
tested (`read_root_cause_report_handoff`, 2 tempfile cases) but the write side is verified by reading
alone. This is exactly the hole registered-but-unimplemented task 7.10 (`run-pipeline.sh --self-test`)
would close. Recorded as WARNING-12.

---

## ADR 0009 — independently scanned, and CLEAN

Scan over all **173 tracked files**, reporting counts only, with no forbidden value written into this
report at any point.

| Category | Tracked files containing it |
|---|---|
| Home-directory absolute path (the repository root) | **0** |
| Employer / organisation name | **0** |
| Maintainer surname | **0** |
| Full email address | **0** |
| Dash-mangled home path (the session scratch directory name) | **0** |
| Session scratch root prefix, private-tmp scratch prefix | **0** |
| Bare **first** name | 3 — all in 2026-08-05 scaffold/journal commits, **explicitly exempt** by ADR 0009's own scope note |

**WARNING-1 is CLOSED.** `ca43bde` removed the instantiated identity terms from `apply-progress.md`;
the file now contains zero occurrences of the employer or surname tokens. No scratchpad path leaked
from PR7C's work.

Four tracked files match the bare home-path **prefix**. All four are shape descriptions, not
instances: two rule tables using `<name>` placeholders (`AGENTS.md:63`, `decisions/0009:66`), one
search-command pattern carrying the prefix only (`apply-progress.md:386`), and round 1's own pattern
citation (`verify-report.md:292`). None carries an account name. Two files match the Windows home
shape, both as placeholders in the same two rule tables.

**Correction to round 1.** `verify-report.md:292` asserts that a tree-wide search for the home-path
prefix "returns nothing". That is false, and was already false when written — the two rule tables
predate it. The accurate claim, which round 2 substitutes, is: **no tracked file carries an
instantiated home-directory path**; the prefix appears only inside placeholder forms, which ADR 0009
requires to remain documentable.

Also confirmed: `/rig/runs/` is gitignored deliberately and for an ADR 0009 reason stated in
`.gitignore` itself — every `init` event carries an absolute home path. Round 1's phrasing
"re-derives byte-identically from the raw captures" is therefore a working-tree-local proof by design,
not a repo-reproducible one. That is the correct tradeoff, and it is recorded rather than treated as a
gap.

---

## Non-regression across PR1–PR6

Every previously-verified artifact re-derived at `3172930`, not read from a note.

| Item | Result |
|---|---|
| `tool-surface-v1` re-derive | byte-identical to the committed `runs.jsonl` |
| `failure-flood-v1` re-derive | byte-identical to the committed `runs.jsonl` |
| v1 `MANIFEST.sha256` | 12 files, **0 bad** |
| v2 `MANIFEST.sha256` | 23 files, **0 bad** |
| Case-table digest, regenerated into a scratch dir | `b15b8d16…5becb1` — **exact match** to the frozen `case-table.sha256` |
| Tool-surface preimage digest from the committed file | `d8693e27…f8daa`, 31 tools — and equals `surface_sha256` on every model step of every row |
| `check_prereg()` (Hard Ordering Gate layer 2) | **byte-identical** to `fa49b35`: 46 lines, sha256 `82d3cb8e…5274`. Round 1's five-branch verification carries forward unchanged |
| Hard Ordering Gate layer 1 | `run-pipeline.sh:802` still a bare `if [ "$SHAKEDOWN" -eq 1 ]` — unconditional, reads no dirty flag and no prior state |
| Hard Ordering Gate layer 3 | `derive.py:839` unchanged |
| `s1`/`s2` totals | `(4, 32, 36)` and `(499, 2383, 2882)` — **exact match** |
| `R0` cause counts | 3 and 6 — **exact match** |
| 42-row occupancy invariants (R-F5.3) | 42/42 on all six properties: peak non-null, aggregate matches, monotone, `context_window_tokens == 1000000`, `model_turns <= num_turns`, `schema_version == 3` |
| `rig/run.sh` untouched (R-F6.4) | `git diff --stat main...HEAD -- rig/run.sh` empty |
| `rig/collect.py`, `hooks/pre-commit` untouched by PR7A/B/C | `git diff --stat fa49b35..HEAD` empty for both |
| Tree state | clean at start, after every command, and at finish |

**Nothing has regressed.**

---

## Gate evidence — every command actually run in round 2

| Command | Exit | Output |
|---|---|---|
| `bash -n` on `run-pipeline.sh`, `run.sh`, `hooks/pre-commit` | 0 each | — |
| `python3 -m py_compile` x3 (`derive.py`, `report.py`, `collect.py`) | 0 each | — |
| `python3 rig/collect.py --self-test` | **0** | 14 `[PASS]` |
| `python3 rig/derive.py --self-test` | **0** | 37 `[PASS]`, 0 `[FAIL]`, 49 assertions |
| `python3 rig/report.py --self-test` | **0** | 3 `[PASS]` |
| `./hooks/pre-commit --all` | **0** | `redaction check: clean across 173 tracked files` |
| `./hooks/pre-commit --self-test` | **0** | all cases pass |
| `python3 rig/derive.py --experiment failure-flood-v1` | 0 | 3 rows, all `state=void (shakedown)`, byte-identical output |
| `python3 rig/derive.py` (default) | 0 | 42 rows, byte-identical output |
| `python3 rig/report.py --experiment failure-flood-v1` | 0 | excluded-row list plus 4 bare table headers |
| `rig/run-pipeline.sh` x5 argument-gate shapes | **2** each | see CRITICAL-3 |
| `generate-cases.py --out <scratch>` | 0 | `case_table_digest: b15b8d16…5becb1` |
| 5 x mutated `derive.py --self-test` (scratch copy) | **1** each | see mutation table |
| 1 x mutated `report.py --self-test` (scratch copy) | **1** | channel-isolation case `[FAIL]` |
| `git status --porcelain` after all of the above | — | empty |

No test runner and no package manager exist in this repository (ADR 0013). "Run the suite" is not a
verification surface here and none was invented.

---

## Requirement trace — deltas from round 1 only

Requirements not listed here are unchanged from round 1's table below.

| ID | Round 1 | Round 2 | Note |
|---|---|---|---|
| **R-F2.2** | UNMET | **Met** | Mechanism complete and mutation-proven. Signature half unexercisable against committed fixtures (WARNING-7) |
| **R-F3.2** | UNMET | **Met** | Frozen-file scoring, not chat prose. Malformed/missing proven non-crashing |
| **R-F7.1** | Partial, UNMET on two clauses | **Partial** | Model clause **now met** (pinned, read back, voided). Prompt-byte-hash clause **still unmet** — `prompt_sha256` exists in `build_row` (`derive.py:430`) but no failure-flood row carries any prompt key; `run-pipeline.sh:15-18`'s deferral to task 5.8 remains orphaned |
| **R-F7.3** | UNMET | **Partial** | Four components plus tool-call names now recorded per role and per run. Literal "per turn" clause still unmet (WARNING-9) |
| R-F4.1 | Met | Met | Now genuinely reachable — the pair it names finally has a producer |

Totals: **24 of 31 met** (was 20), 4 partial, 1 not-yet-applicable, 2 not verifiable here.
Scenarios: **12 of 19** demonstrably covered (was 9) — the three newly covered are R-F3.2's
malformed-report scenario and both R-F2.2 scenarios, each by a passing, mutation-proven self-test
case. The remaining 7 need a countable run or a Jest run.

---

## Issues

### CRITICAL

**CRITICAL-5 — two different ADRs numbered `0014`.** Full detail above. Blocks archive; remedy is an
operator decision, not a code change.

### WARNING

Carried forward from round 1, re-verified as still open:

**WARNING-2 — stale pre-failure ratio claim in committed code.** `axis_table.py:19-21` still reads
"landing the aggregate in the ~2,600-3,000 / ~433-500:1 target band". Verbatim unchanged.

**WARNING-3 — `derive.py`'s R-A1.4 self-test section is empty for `failure-flood-v1`.** Re-run today:
`checker self-test (R-A1.4 — each detector must be observed to fire):` followed by nothing. Now *more*
pointed than in round 1: the experiment has since gained two new detectors (`suite-state-mismatch`,
`model-mismatch`), and neither appears under a header asserting every detector was observed to fire.
They *are* covered by `--self-test`, which is the better mechanism — so the fix is to make the empty
section say so, not to add cases.

**WARNING-4 — task 6.4's done-note describes report output today's data does not produce.** Re-run:
the four tables print bare headers with no body; the described per-(task_id, arm) message is absent.

**WARNING-5 — step/suite timeouts still labelled placeholders.** `run-pipeline.sh:85-89`:
`STEP_TIMEOUT_S=180`, `SUITE_TIMEOUT_S=150`, still commented "Both PLACEHOLDERS pending task 5.7's
real wall-clock measurement". Task 5.7 ran; they were not re-derived. `03-apply` on `s2-pipeline-9054`
took 120,207 ms against a 180 s budget.

**WARNING-6 — the run-axis field is `state`, not `run_state` (R-F2.1).** Confirmed on the committed
rows: `run_state` absent, `state` and `suite_state` present.

**WARNING-1 — CLOSED** by `ca43bde`. See the ADR 0009 section.

New in round 2:

**WARNING-7 — the frozen `S0` carries no `signature`, and two `_purpose` strings say it does.** Both
answer keys' `S0` key sets are `['_purpose', 'identifier_set_digest', 'suite_state', 'totals']`, yet
both `_purpose` strings open with "frozen suite state + its normalized signature". R-F2.2's signature
clause therefore has no frozen counterpart in committed data. The code fails in the safe direction;
the fixture's self-description does not match the fixture.

**WARNING-8 — `design.md`'s ASCII diagram is stale in two places, not one.** `:608` names
`result.result` as the scoring source; `:599` names an older `CAUSE <path>:<line> <cluster_ids>`
format. Both are superseded by R-F3.1/R-F3.2 as implemented. The code is right; the design artifact
was never amended.

**WARNING-9 — R-F7.3's literal "per turn" clause is unmet.** Components are per-role and per-run;
per-turn remains a single derived occupancy total, the shape the requirement forbids. The per-turn
components exist in the raw captures, so this is an extraction not done rather than data lost.

**WARNING-10 — a complete row with `model_matches_declared` absent passes silently.** Not producible
by today's runner and not present in any committed row, but there is no downgrade backstop for it,
unlike the `no-preregistration` layer-3 check that exists for exactly this class.

**WARNING-11 — `report.py` still tells the reader task 5.9 is not implemented.** `report.py:244-247`
(docstring) and `:252-256` (printed message) both state that `causes_claimed`/`causes_correct` stay
`None` "until task 5.9 threads `root-cause-report.txt`" and that "R-F3.2 cannot be honestly computed
yet". Task 5.9 and the scoring function are both closed, so this is a false statement in
output-producing code — the same class as WARNING-2. Relatedly, `tasks.md:1290-1295`'s
`## Blocked tasks` section still says 5.9 "remains **not implemented**"; it is superseded only by later
per-task notes, never by that section itself.

**WARNING-12 — the threading half of task 5.9 is verified by reading only.** The bash `cp` at
`run-pipeline.sh:705-708` is covered by `bash -n` (syntax) and by reading; no test exercises it,
because no run since PR7B has produced a `root-cause-report.txt`. Registered-but-unimplemented task
7.10 (`run-pipeline.sh --self-test`) is exactly the mechanism that would close it.

### SUGGESTION

**SUGGESTION-1 — still open.** `tasks.md:651-652` claims `collect.py --self-test` passes "all **15**
cases (a, b, c.1–c.4, d, e, f, g.1, g.2, h.1, h.2, i)". The enumeration holds 14 items and the command
emits **14** `[PASS]` lines. Re-derived today. `BACKLOG.md` entry 1 rule (b) names "a second and third
occurrence" as its unblock trigger; this remains the candidate second occurrence, and round 2
deliberately did **not** count the "49/49 `[PASS]`" rendering as a third — see the note above.

**SUGGESTION-2 — still open.** `C` is frozen in both answer keys and read by no executable.

**SUGGESTION-3 — still open.** The four failure-flood tables print bare headers with no
`(no complete rows)` line, unlike the excluded-rows table's `or ["none"]`.

**SUGGESTION-4 — still open.** `apply-progress.md:513` still asserts "~470:1 — inside the
operator-confirmed ~433–500:1 band" at its own site, corrected 574 lines later.

**SUGGESTION-5 — still open, and this report resolves it the same way.** The fenced `yaml` envelope
required by `gentle-ai sdd-verify-validate` is incompatible with `AGENTS.md`'s front-matter contract;
the validator wins and the frontmatter fields are carried as a table.

---

## Not verified at all — stated rather than assumed

1. **Everything requiring a Jest run.** No package manager and no `node_modules`. Covers the clean
   baselines (3.1/3.2), per-injection isolation signatures (4.1/4.3), the 2,882-passing amplified
   clean run, and R-F9.1's empirical mutation (49/392).
2. **`check_prereg()`'s `more_than_one_match` and `tracked_but_dirty` branches** — not re-run in round
   2. Mitigated, not ignored: the function is byte-identical to the revision round 1 verified across
   five branches, so that verification transfers.
3. **Live-tamper transitions.** Current state re-derived (both manifests, the case-table digest, the
   surface digest all match exactly); the tamper transitions were not re-performed, to avoid dirtying
   tracked fixture bytes.
4. **Anything requiring a countable run**: R-F7.2's sampling escalation, R-F4.2's "partial credit
   fires at least once", R-F6.3's re-collect behaviour, both hypotheses, the model pin end-to-end
   through a real `claude -p`, and the task-5.9 `cp` executing for real.
5. **`main`'s newer `hooks/pre-commit`** against this branch's tree. The branch's checker was used; the
   substantive ADR 0009 result above came from an independent scan that does not depend on it.

---

## What must happen before archive

| # | Action | Blocks archive |
|---|---|---|
| 1 | Resolve the ADR `0014` collision — renumber one lineage and update its citations. Operator decision | **Yes** |
| 2 | Correct `report.py:244-256` so it stops reporting task 5.9 as unimplemented | No — but it is a false statement shipped in code |
| 3 | Correct `design.md:599` and `:608` to R-F3.1's actual format and source | No |
| 4 | Either freeze a `signature` in both `S0` blocks or correct the two `_purpose` strings | No |
| 5 | Re-derive `STEP_TIMEOUT_S`/`SUITE_TIMEOUT_S` from task 5.7's real wall clocks | No — but do it before the countable run |
| 6 | Record R-F7.3's four components per turn, or amend the clause | No |
| 7 | Add a downgrade backstop for a complete row with no declared-model comparison | No |
| 8 | Correct `axis_table.py:19-21`, `tasks.md:651-652`, `tasks.md:1290-1295`, task 6.4's note | No |
| 9 | Implement task 7.10 so the task-5.9 `cp` and the argument gates get a committed test | No |

**Verdict: FAIL — one blocker.** Round 1's four CRITICALs are closed and their closures survived
adversarial re-derivation, including mutation testing of the control that certifies them. The
remaining blocker is an identifier collision created outside this change, and its remedy is an operator
decision rather than more implementation.

## Round 2 Key Learnings

1. A self-test that has never been mutated is an untested test; five injected defects proved this
   repository's deriver self-test fails specifically rather than passing unconditionally.
2. A void that only fires on an explicit `False` silently accepts a missing field, so the absent-key
   case needs its own probe rather than inheritance from the mismatch case.
3. Two branches can independently claim the same ADR number, and no task-completion count or
   requirement trace inside one branch can detect it.
4. A requirement can be closed at the granularity it was reported against and still miss a narrower
   clause in its own sentence, which is why the spec text and not the finding text is the checklist.
5. A fixture's `_purpose` prose can advertise a frozen field that the fixture does not contain, and
   only a key-set dump rather than a value read will surface it.

---
---

# Superseded — round 1, 2026-08-17

**This report is superseded by round 2 above.** It is retained in full because its findings and their
resolutions are the record. Round 2 contradicts it in two places, both stated above: the home-path
prefix claim at its line 292, and the four CRITICALs it lists, all now closed. Its own `yaml` envelope
is retained below as prose rather than as a fenced block, so that the round-2 envelope remains the
first non-empty content of this file.

> Round-1 envelope, retained verbatim as an indented block (a second fenced `yaml`
> envelope would compete with round 2's for first-non-empty position):

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
| `sources` | `sdd/failure-flood-triage/{spec,design,tasks,apply-progress}.md`, `decisions/0009`, `0010`, `0011`, `0012`, `0013`, `0015` |
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
| ADR 0015 before slice 3a (R-F11.1) | ADR `9eccf8d` 2026-08-11; first fixture commit `1c72fa9` 2026-08-12 | **ordering holds** |

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
| R-F11.1 | **Met** | ADR 0015 (filed as `0014` at the time) exists and predates the first fixture commit |
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
| Design's four-item ADR-0015 self-test roster | **Internally inconsistent** | Flagged in PR1's own findings; does not change Clause B's decision |

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
