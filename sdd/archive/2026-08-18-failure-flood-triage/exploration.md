---
id: sdd/failure-flood-triage/exploration
type: journal
targets: [any]
status: draft
verified: 2026-08-11
sources: ["decisions/0010-measurements-vary-the-harness-not-the-model.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0012-a-hypothesis-is-never-citable.md", "rig/README.md", "rig/run.sh", "rig/derive.py", "rig/report.py", "sdd/measurement-rig/verify.md", "sdd/measurement-rig/design.md", "sdd/measurement-rig/tasks.md", "hypotheses/README.md", "hypotheses/0001-broad-surface-degrades-output-not-selection.md", "OPERATIONS.md", "AGENTS.md", "MAP.md", ".gitignore", "skills/hypothesis-cycle/SKILL.md", "skills/source-verdict/SKILL.md", "skills/context-checkpoint/SKILL.md"]
---

# failure-flood-triage — exploration

SDD exploration phase for the change `failure-flood-triage`: a second `rig/` experiment
(`rig/fixtures/failure-flood/v1`) comparing a three-role harness (collector → diagnostician →
applier) against a single monolithic agent, on the same broken-test fixture, model held fixed per
ADR 0010. Investigation only. No proposal, no design, no code.

## 1. `rig/` conventions, in precise detail

`rig/README.md` describes the layout: `run.sh` (guards, launches, persists ONE run), `derive.py`
(total, deterministic function from run directories to `runs.jsonl`), `report.py` (aggregates rows
into four-cell tables), `surfaces/` (committed preimages of the expected tool set),
`fixtures/<experiment>/<version>/` (frozen, hash-frozen, additively versioned),
`results/<experiment>/runs.jsonl` (committed, append-only, rebuilt by `derive.py`), and `runs/`
(gitignored — raw per-run captures, machine-local only).

**`MANIFEST.sha256`** is a `sha256sum`-style file: one line per file, `<sha256>  <relpath>`, over
exactly `src/`, `prompts/`, `answer-key/`, sorted by path. It is generated and checked by the same
function, `compute_manifest()`, embedded in `rig/run.sh` (lines ~150–171): the script recomputes it
from the fixture on disk and diffs it byte-for-byte against the committed file before every run,
refusing to run (exit 2) on any mismatch — "Refusing to run against a tampered or edited fixture...
A change belongs in a new v(N+1)/ directory, not an edit to v1/." There is no separate freeze
script; "refreezing" in `sdd/measurement-rig/tasks.md` (task 8.4) is a manual re-derive-and-commit,
verified live before and after.

**`prompts/`** holds one `.txt` file per `task_id`, its exact bytes hashed into the row as
`prompt_sha256`. Answer-key commits land strictly before the corresponding prompt commit, so
"checker-first" is provable from commit order (`sdd/measurement-rig/design.md`, file table).

**`results/` is committed**; raw captures under `rig/runs/` are gitignored via a standalone
`/rig/runs/` entry in `.gitignore`, kept deliberately outside `setup.sh`'s managed block. The reason,
per ADR 0011: every `init` event in a raw transcript carries an absolute home path.

**End-to-end execution**, per `OPERATIONS.md`'s decision table, in order:

```
./rig/run.sh <task_id> <arm> <iteration>   # ONE run. Guards, launches, persists. Parses nothing.
python3 rig/derive.py                      # ALL run dirs -> rows. Total function, rebuilds every time.
python3 rig/report.py                      # rows -> four-cell tables.
```

`rig/run.sh` checks a clean tree under `rig/`, the MANIFEST match, and the prompt file's existence;
materializes `src/` into a `mktemp` workspace outside the repo; runs exactly **one** `claude -p
<prompt>` invocation (`--strict-mcp-config`, a computed `--disallowedTools` list, `Bash` always
disallowed in both arms); writes `stream.jsonl`/`status.json`; and exits 0 (state `complete` or
`void`), 1 (state `failed` — the read-only substrate was mutated), or 2 (could not run at all).
`rig/derive.py` then rebuilds `rig/results/<experiment>/runs.jsonl` completely from every run
directory under `rig/runs/<experiment>/`, sorted by `run_id` — "total" is load-bearing: there is no
"already written" state to desync, so double-counting is structurally impossible. `rig/report.py`
reads that file and prints the four-cell table, the off-set/forbidden distribution, and cost/token
figures as separate tables, never a composite score.

**v1 → v2 versioning** means a fixture *change* is a brand-new version directory; the old one is
never edited. `t1`/`t2`/`t3` stay pinned to `v1/` permanently; `t3v2` (tier 3's discriminating
rebuild) lives under `v2/`. "The version a task_id names is fixed at the moment that task_id is
introduced" (`rig/derive.py` comment).

**What a new experiment directory must provide to fit this harness, precisely stated — and where
the fit breaks down.** `rig/run.sh`, `rig/derive.py`, and `rig/report.py` are **not generic across
experiments as currently written.** All three hardcode `EXPERIMENT = "tool-surface-v1"` (`rig/run.sh`
line 52; `rig/derive.py` line 43; `rig/report.py` line 25), and `rig/run.sh`/`rig/derive.py` further
hardcode a closed `task_id` enum (`t1|t2|t3|t3v2`) mapped to fixture roots under
`rig/fixtures/tool-surface/<version>/`. `MAP.md` still records "1 experiment (`tool-surface`), in
progress." **A second experiment cannot be added by dropping a `fixtures/failure-flood/v1/`
directory alone** — the runner, deriver, and reporter need to be parameterized (or duplicated) to
accept a second experiment name and fixture root. Neither `rig/README.md` nor ADR 0010/0011
describes how a second experiment is meant to coexist with the first; this is undocumented scope,
not a documented extension point.

**A second, deeper mismatch: the run shape itself.** `rig/run.sh` performs exactly **one** `claude
-p` invocation per `run_id`, producing one `stream.jsonl` and one `status.json`. The proposed
three-role harness — a plain-code collector (zero model tokens) that clusters Jest failures, a
diagnostician agent that sees only clusters and representative files and emits a fix-plan file, and
an applier agent that executes the plan mechanically — needs **multiple chained model invocations
per "harness" arm**, with an intermediate artifact (the fix-plan) threaded from the diagnostician's
output into the applier's input. The current one-invocation-per-`run_id` model has no built-in
notion of a multi-step pipeline. Fitting this experiment into the rig is real harness engineering,
not a fixture drop-in.

## 2. Governing ADRs

**ADR 0010** — measurements vary the harness, model held fixed — states five non-negotiable
constraints (quoted in substance, each is "a way this fails silently"):

1. "Every task carries a deterministic pass/fail, and the checker is written before the prompt."
   Not "did it write good code" — file exists with this content, command exits 0, JSON matches a
   schema. "If the verifier cannot be written first, the task does not enter the suite." Code
   planning is explicitly excluded from v1 for exactly this reason: "There is no deterministic
   grader for a plan."
2. "One variable per run, with everything held fixed recorded" — model id, harness version, task
   id, a hash of the exact prompt bytes, a hash of the tool surface.
3. "N runs per cell, reporting spread and not only a mean." One run per cell measures sampling
   noise, not a finding.
4. "One category first, three difficulty tiers, three tasks." A taxonomy is not a claim; five
   categories times three tiers guarantees either a fuzzy grader or an unfinished suite.
5. A named list of what is recorded per run: input/output/**cached** tokens separately (cached and
   uncached differ roughly an order of magnitude in price), turns/loop iterations, wall clock, tool
   calls (count, which tools, and wrong-tool calls), and the deterministic verdict.

**ADR 0011** — `rig/` produces evidence, not truth — a three-way citability split: rig **code**
(runner, analyser, checkers, fixtures) is citable, like `setup.sh`/`hooks/`; rig **output** (rows in
`runs.jsonl`, aggregate tables) is evidence only, never truth on its own; **raw captures** are
neither citable nor committed. "A number becomes citable only by being promoted into `theory/` with
its scope and its honesty contract attached." The boundary section names `python3` and a
GNU-compatible `timeout` as **rig-only** prerequisites explicitly exempt from `hooks/pre-commit`'s
"runs on a machine that installed nothing" portability contract — no other toolchain is named or
pre-authorized this way anywhere in the repo.

**ADR 0012** — a hypothesis is never citable — carries zero citability, not "evidence only." Its
own stated trigger is directly relevant here: the first real run pair of the measurement rig showed
both arms calling identical tools while their answers differed in precision, and writing that
alternative down only *after* seeing tier-3 data would have let the choice of which channel to
report be made with the data already visible — "the exact fault this repo refused a vendor's number
over." A falsification condition is mandatory content; resolution is always a **new artifact**,
never a status flip on the hypothesis file itself.

## 3. The prior cycle's instrument (`sdd/measurement-rig/verify.md`) — verdict: PARTIAL

**Verified: the cost channel.** One figure was promoted to `theory/agents/capability-load-cost.md`:
"≈224 tokens per resident tool entry," from 12 pairs at 32 versus 3 tools, median 6,489 extra
cache-creation tokens for 29 extra names, "Positive 12 of 12, sign test p=0.000244, Mann-Whitney on
the 9 same-order pairs p=0.000021." Also verified live: the MANIFEST guard fired correctly in both
directions on the v2 fixture (accept before freeze, exit 2 on a post-freeze byte tamper); the
three-state exit contract is implemented and exercised; `derive.py` is idempotent (two runs
byte-identical, 15 pre-existing rows re-derive unchanged across a schema bump); the X=3
instrument-doubt threshold "did its job" — it tripped, was investigated rather than waved through,
and was cleared by a deliberate-versus-spontaneous split.

**Not verified: the quality/defect-detection channel**, and this is why the verdict is PARTIAL, not
clean. "R-A1.4 — 'Every detector must be proven able to fire' — is unsatisfied for the quality
detector." Across both fixture generations, every completed run classified `proper`: 12 of 12, in
both arms, zero defects missed, zero invented. The `v2` fixture was purpose-built to fix this —
three real defects instead of one, two near-misses, no bolding, no steering sentence — "and it still
did not discriminate." Consequence: task 9.3 recorded exactly one verdict, "not supported" for
defect-reporting tasks, deliberately not "rejected" — a null on one task class does not refute the
general claim (`hypotheses/0001` stays open).

**What would move this to a clean verdict**, quoted directly because it defines this experiment's
opportunity: "One fixture generation in which a completed run can fail cleanly — a task class with
no single right answer, where recall and precision can genuinely diverge between arms. Until then
the rig is a verified cost instrument and an unverified quality instrument, and it should be
described that way everywhere it is cited." A broken-tests-with-multiple-root-causes fixture, where
"restored to green" admits partial credit, is exactly the shape verify.md asked for — this is a
point in favor of the proposed experiment, not a risk against it.

## 4. Hypothesis obligation

`hypotheses/` has exactly one open entry, `0001-broad-surface-degrades-output-not-selection.md`
(closed "not supported" on defect-reporting task classes on 2026-08-10, remains open for task
classes with no single right answer — which is the class this experiment's fixture belongs to).
Neither ADR 0012 nor `hypotheses/README.md` names a mechanical gate that blocks a rig run absent a
registered hypothesis. But the repo's own established, evidenced practice — `hypotheses/0001` was
registered *before* the tier-3 runs that could settle it, specifically because a tier-1 run had
already revealed an alternative explanatory channel and ADR 0012 was ratified the same day to
prevent choosing which channel to report after the data was visible — makes registering a
falsifiable hypothesis before executing this experiment the correct reading of repo practice, not
merely a nicety. Skipping it would repeat the exact failure ADR 0012 exists to prevent.

The required shape (`hypotheses/README.md`): Claim (one falsifiable sentence) / Why it is plausible
/ The test (the exact support **and** the exact refute observation, written before the run) / What
it would change / Status (`open`, `resolved → <artifact>`, or `refuted`). Frontmatter: `type:
research`, `status: draft` (never `validated`).

Because the task's own framing already treats **peak context occupancy** and **cumulative tokens**
as distinct failure modes, and treats **context occupancy/runway** as primary with **dollar cost**
explicitly secondary, this experiment likely needs at least two separately falsifiable claims
rather than one composite claim — mirroring the R-A1.3 convention already enforced in `rig/report.py`
("never summed or weighted into one score... here or by any caller").

## 5. What to run

`AGENTS.md`'s frontmatter `type` enum is `index | theory | block | template | decision | research |
journal | skill` — confirmed no `config` value; this file uses `type: journal` per
`hypotheses/README.md`'s own precedent for process narrative that is neither a validated finding nor
a decision.

ADR 0009's redaction rule, as codified in `AGENTS.md`'s "Redaction" section: no committed file may
contain a home-directory path, a private project or client name, a token, or a hostname, in prose,
frontmatter, or a commit message — "Every committed file is published the moment it is pushed, and
pushing is not reversible in any way that matters." A private project name written as a bare word
is explicitly called out as the one thing `hooks/pre-commit` **cannot** pattern-match: "a clean check
is not evidence about that half."

`hooks/pre-commit`'s exit-code contract, per `OPERATIONS.md`: `0` clean, proceed; `1` a finding, fix
it, never `--no-verify`; `2` could not run — "treat as a failure, not a pass," something broke (a
bad pattern, a locale problem, an unreadable file), diagnose before committing.

## 6. Fixture feasibility — donor audit

Eighteen pure-TypeScript test files were audited from an external project the operator authorized
extracting a portion of. Per `AGENTS.md`'s shared-material rule it is referred to here only as
**"the donor project"** — no name, no path.

| Module | Test cases | Transitive imports | Verdict |
|---|---|---|---|
| `validateAccountName` | 6 | none | RN-FREE |
| `confirmSeed` | 12 | none | RN-FREE |
| `importSeed` | 8 | `@scure/bip39` (+ its English wordlist) | RN-FREE — real npm dependency, pure-JS crypto, not RN |
| `convertToFiat` | 4 | none | RN-FREE |
| `formatFiat` | 4 | local `Currency` type alias | RN-FREE |
| `addRecent` | 6 | none | RN-FREE |
| `applyKeypadInput` | 15 | none | RN-FREE |
| `balanceOfCall` | 7 | none (`BigInt` only) | RN-FREE |
| `formatRelativeTime` | 7 | none | RN-FREE |
| `formatTokenAmount` | 8 | none (`BigInt` only) | RN-FREE |
| `greetingForHour` | 5 | none | RN-FREE |
| `groupTransactionsByDay` | 6 | type-only import of `Transaction` from `parseTransfers` | RN-FREE |
| `isValidEthereumAddress` | 8 | none | RN-FREE |
| `parseScannedAddress` | 10 | `isValidEthereumAddress` | RN-FREE |
| `parseTokenAmount` | 13 | none | RN-FREE |
| `parseTransfers` | 9 | none | RN-FREE |
| `truncateAddress` | 4 | none | RN-FREE |
| `validateSendAmount` | 6 | none | RN-FREE |

No audited module imports `react-native`, `MMKV`, or any `expo-*` package. **Total: 138 RN-free test
cases** across the 18 modules (130 if `importSeed`'s 8 cases are excluded on the grounds that its one
external dependency needs an actual install rather than a stub). This clears the 50-failing-case
stage-2 target by roughly 2.6×–2.76× under either reading, with substantial headroom for whichever
subset actually gets selected for injected failures.

## 7. The Node/Jest tension

`.gitignore` already carries a blanket `node_modules/` entry — not fixture-scoped — placed outside
`setup.sh`'s managed block, the same treatment already given to `/rig/runs/`. An installed-on-demand,
gitignored `node_modules/` under `rig/fixtures/failure-flood/v1/` would need **no `.gitignore`
change** and is consistent with the one precedent this repo already has for a rig-local, uncommitted,
machine-dependent directory.

However: **nothing in `AGENTS.md`, `OPERATIONS.md`, or the ADRs authorizes a Node/npm/Jest toolchain
as a rig prerequisite.** `OPERATIONS.md`'s prerequisites table and ADR 0011's boundary section name
only `python3` (stdlib only), a GNU-compatible `timeout`, the `claude` CLI, and `gentle-ai`. Existing
`rig/` fixtures (`tool-surface/v1`, `v2`) are bare `.js` files with no install step at all. Introducing
Jest plus an installed `node_modules` is not explicitly forbidden anywhere, but it is also not
explicitly authorized — it would be a genuinely new class of rig-local dependency, and for
consistency with this repo's "schema = doc" discipline it should be added to `OPERATIONS.md`'s
prerequisites table (and arguably named in an ADR) rather than introduced silently.

## Risks and open conflicts

- **Harness-fit risk (high).** `rig/run.sh`, `rig/derive.py`, and `rig/report.py` hardcode
  `EXPERIMENT="tool-surface-v1"` and a closed task-id enum tied to `rig/fixtures/tool-surface/`.
  Adding `rig/fixtures/failure-flood/v1/` alone does not make the harness runnable against it; all
  three scripts need to be parameterized (or duplicated) — scope beyond anything ADR 0010, ADR
  0011, or `rig/README.md` currently describes.
- **Pipeline-shape risk (high).** The collector → diagnostician → applier design needs multiple
  chained model invocations per arm with an intermediate fix-plan artifact threaded between them.
  The rig's current one-`claude -p`-invocation-per-`run_id` model does not support that shape without
  new orchestration.
- **Toolchain-authorization gap (medium).** Node/npm/Jest is not named anywhere as a rig
  prerequisite. Not forbidden, but undocumented; needs an `OPERATIONS.md` update at minimum before
  it is used routinely.
- **Pre-registration obligation (medium).** Per ADR 0012's own stated trigger and `hypotheses/0001`'s
  precedent, at least one — likely two, given the primary metric's own stated peak-vs-cumulative
  split — falsifiable hypotheses should be registered in `hypotheses/` before this experiment runs,
  to avoid the exact post-hoc metric-selection fault the repo has already caught itself making once.
- **Nothing found rules the plan out outright.** The donor audit clears the stage-2 case-count target
  with wide margin, and the prior cycle's own PARTIAL verdict explicitly asks for the kind of
  no-single-right-answer task class this experiment's fixture would provide. The two high risks are
  scoping/design problems for `sdd-propose`/`sdd-design` to resolve, not hard blockers to the change
  as a whole.
