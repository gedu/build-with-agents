---
id: sdd/archive/2026-08-27-run-input-provenance/archive-report
type: journal
targets: [any]
status: validated
verified: 2026-08-27
sources: ["sdd/archive/2026-08-27-run-input-provenance/proposal.md", "sdd/archive/2026-08-27-run-input-provenance/spec.md", "sdd/archive/2026-08-27-run-input-provenance/design.md", "sdd/archive/2026-08-27-run-input-provenance/tasks.md", "sdd/archive/2026-08-27-run-input-provenance/apply-progress.md", "sdd/archive/2026-08-27-run-input-provenance/verify-report.md", "BACKLOG.md", "MAP.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "decisions/0011-rig-produces-evidence-not-truth.md", "decisions/0012-a-hypothesis-is-never-citable.md", "decisions/0013-a-committed-executable-carries-its-own-test.md"]
cycle_status: complete_with_warnings
verification_round: 2
verified_commit: cdd50d4
---

# Archive Report: run-input-provenance

**Change**: `run-input-provenance`
**Archived**: 2026-08-27 to `sdd/archive/2026-08-27-run-input-provenance/`
**Status**: Closed with warnings permitted
**Cycle Result**: PASS WITH WARNINGS — 0 CRITICAL, 6 WARNING, 9 SUGGESTION

## THE ARCHIVE CONDITION — read this before anything else in this report

**Boundary sentence, carried forward from `MAP.md:52` and PR #8's own body:**

> Still an instrument plus a **failed** ratio target, never a comparative result: zero countable runs.

This cycle delivered **detection**, never a comparative result. `N = 0` in every cell of
`rig/results/failure-flood-v1/runs.jsonl`; all three rows remain `state=void`, and this archive move
touches none of them. What it built: a run now records a digest of every input it was scored against
— the answer key (Face A), the fixture (Face B), and the surface preimage (Face C) — at the moment it
is scored against it, so a row can no longer claim agreement with an input it never actually compared.
This closes the prior archived cycle's own R-F5.3 gap (a re-derive only ever proved deriver drift,
never fixture drift).

**What cannot be claimed from this archive:**
- Any comparative result between harness shapes, or between "before" and "after" this change on a
  real workload
- A countable run of any kind — the void rows this cycle touched stay void, by construction
- That the instrument is ready to found the first countable run: **`STEP_TIMEOUT_S=180` and
  `SUITE_TIMEOUT_S=150` remain placeholders at `rig/run-pipeline.sh:85-86`**. Closing this cycle does
  **not** found the first countable run — that is separate, unstarted work.

The repository's own `N = 0` prose scan (second verify pass, over `MAP.md`, `rig/README.md`,
`rig/derive.py`, `rig/run-pipeline.sh`, `apply-progress.md`, `tasks.md`, both `runs.jsonl`, and PR #8's
body) found **no violation of this boundary anywhere** — the closest four sentences are all
conditional, counterfactual, or explicitly forward-looking and unfunded. This archive report
continues that discipline: nothing below asserts a comparative or countable result.

## Artifact Traceability (Engram Observation IDs)

All artifacts retrieved for final-state authority, per the Final-State Authority hierarchy in the
`sdd-archive` skill (launch-prompt facts and the most recent `sdd-verify` pass outrank earlier
snapshots):

| Artifact | Observation ID(s) | Retrieved |
|----------|---|---|
| proposal.md | #299 (also #300, the gatekeeper pass record) | 2026-08-27 |
| spec.md | #302 (corrective round 1; also #303, #306) | 2026-08-27 |
| design.md | #304 (also #305, #306) | 2026-08-27 |
| tasks.md | #308 (CYCLE COMPLETE, amended; also #341, #344, #345 — see the durable-record correction below) | 2026-08-27 |
| apply-progress.md | #322 | 2026-08-27 |
| verify-report.md | #356 (first pass) and **#360 (second pass, authoritative for final state)** | 2026-08-27 |

The verify-report **file itself** (`sdd/archive/2026-08-27-run-input-provenance/verify-report.md`) was
read in full rather than relied on by preview, per its status as the authority on what this cycle did
and did not establish. Its own second-pass verdict (`PASS WITH WARNINGS — 0 CRITICAL, 6 WARNING, 9
SUGGESTION`, requirements 12/12, scenarios 21/21, 36 tasks all `[x]`) is what this archive report
carries forward as final state, superseding its own first pass (`FAIL — 1 CRITICAL`), which the
verify-report itself retains rather than erases.

## Verdict and Gate Summary (second pass, authoritative)

| Gate | Result |
|---|---|
| `python3 rig/derive.py --self-test` | 60/60, exit 0 |
| `bash rig/run-pipeline.sh --self-test` | 28/28, exit 0 |
| `./rig/check.sh` | 20/20, exit 0 |
| `./check.sh` (repo-wide, post-move) | clean, 112 content files, 5 skill(s) — see verbatim output below |
| `./hooks/pre-commit --all` (post-move) | exit 0 — see verbatim output below |
| Requirements | 12/12 satisfied |
| Scenarios | 21/21 with passing runtime evidence |
| Tasks | 36/36 `[x]`, zero unchecked |
| Authored lines vs 800-line review budget | 1147 (1149 counting `MAP.md`), 2.23x the ~515 forecast — `size:exception` authorized 2026-08-26 rather than re-slicing, because R-P9.2 makes the sibling order (Face A → C → B) part of the contract |
| Implementation commits, oldest first | `0637d68` (Face A + WARNING-14) → `5cfa456` (Face C + task 2.0) → `2873e04` (Face B + cross-cutting + task 3.8) → `4217d4a` (task 2.9, closing CRITICAL-1) |

## Task Completion Gate

`sdd/archive/2026-08-27-run-input-provenance/tasks.md` was inspected before this move: all tasks
1.1–1.11 (Sibling 1), 2.0–2.9 (Sibling 2), 3.1–3.8 and cross-cutting 4.1–4.7 (Sibling 3) are `[x]`.
36 tasks total, zero unchecked. No stale-checkbox reconciliation was needed or performed.

## Native Review Receipt Gate

Checked directly: `gentle-ai review mode status --cwd <repo>` reports receipt-driven development
**off** (decided by `clone_local`; global is `on` but the clone-local override wins). No review was
started for this candidate. Per the skill's Native Review Receipt Gate, `reviewGate` is structurally
**absent** in this case (kill switch off) — there is no `disabled/unmanaged` value to check for, and
archive proceeds under ordinary repository policy. This matches the prior archived cycle's own
authorization record.

## Mechanical Copy Contract — evidence

Seven artifacts moved with `git mv`, verified against a pre-move `cp -R` snapshot with `diff -r`:

```
git mv sdd/run-input-provenance sdd/archive/2026-08-27-run-input-provenance
```

(`git mv` on the directory moved all seven files in one operation — `apply-progress.md`, `design.md`,
`exploration.md`, `proposal.md`, `spec.md`, `tasks.md`, `verify-report.md` — recorded by git as seven
renames.)

**`diff -r` readback (pre-move snapshot vs. archived destination): empty, exit 0.** This archive
report is additive and was written after the readback, so it is correctly excluded from the
comparison.

Source directory `sdd/run-input-provenance/` confirmed gone after the move; destination confirmed to
hold all seven files, byte-identical.

## Findings carried forward — all 15, each with its home and why

`verify-report.md`'s second pass named **6 WARNING and 9 SUGGESTION** findings. Seven of them were
already given a named, requirement-bound remedy by the verify-report itself (its own "What would have
to change for the last grade up" table, tasks **F-1** through **F-7**) — that table is reproduced
below unchanged, because it is already the shape this repo uses for a closed cycle's open follow-ups
(the precedent archive, `sdd/archive/2026-08-18-failure-flood-triage/archive-report.md`, recorded its
own open items — tasks 7.10 and 7.15 — the same way, directly in the archive report; task 7.15 is in
fact what became **this** cycle's proposal, so this is a working precedent, not an assumption).

**Home chosen: the archive report, not `BACKLOG.md`, for every F-numbered item.** `BACKLOG.md`'s own
admission rule is strict: an entry needs a *named unblock condition* — something not yet actionable,
waiting on a stated trigger (a second occurrence, an evidence promotion, and so on). Every F-item below
already has a concrete, described remedy and no external trigger to wait for; the only reason it is not
done is that this cycle's scope stopped at closing CRITICAL-1. Forcing a ready-to-execute code change
into `BACKLOG.md` would violate its own "an entry with no named trigger is not a backlog item, it is a
wish" rule in the other direction — these are not wishes, they are scoped-out work, and this repo's own
precedent already shows where scoped-out work belongs: the archive report, to be picked up as a future
SDD proposal when someone chooses to.

| Task | Source finding(s) | Requirement | Change |
|---|---|---|---|
| **F-1** | WARNING-1 | R-P11.1 | Write Face C's per-step field explicitly so all four provenance fields are present-and-`null` on re-derived rows, and correct the "all four … null" wording in PR #8 and `apply-progress.md:174` |
| **F-2** | WARNING-2 | R-P12.1 | Either give `failure-flood`'s answer keys a `checker_self_test` block or compose `derive.py --self-test` into the derive path, so the refusal gate is not vacuous for the experiment this cycle is actually about; also correct task 4.4's parenthetical |
| **F-3** | WARNING-3 | R-P6.1 / R-P6.2 | Add one clause at `rig/derive.py:993-1000` naming `:974-978` as the owner of the invariant that makes `:1001`'s comparand unobservable |
| **F-4** | WARNING-4 | R-P2.2a / R-P10.1 | Commit the order-swap proof as a self-test case so it re-runs, satisfying ADR 0013 |
| **F-5** | SUGGESTION-6 | R-P10.1 | Give `load_surface()` an additive `root=SURFACES_ROOT` default so no self-test writes into `rig/surfaces/`; failing that, convert task 2.9's bare `assert` into a reported `[FAIL]` case and `.gitignore` the fixed arm name |
| **F-6** | SUGGESTION-3, SUGGESTION-7 | — (durable-record hygiene, not an R-P requirement) | Correction sweep on the durable record — see "Durable-record correction sweep" below, performed as part of this archive, not deferred |
| **F-7** | WARNING-6, SUGGESTION-9 | R-P12.1 / R-P12.2 / R-P10.1 | Commit the two R-P12 scenario proofs executed during the second verify pass (a multi-directory derive case and a cleanly-failing-detector refusal case) so they re-run from the repository; fold in SUGGESTION-9's two-line `.get()` fix in `run_self_tests()` while there |

None of F-1 through F-7 blocks archive. None promotes any row past `void`, and none touches `rig/`
(verified below — this archive move made zero code changes).

### The remaining eight findings, each judged individually

| # | Finding | Home | Why |
|---|---|---|---|
| **WARNING-5** | No worktree taken, against `checkout-isolation`, across all four implementation commits plus the two verify passes | **This archive report only** (Process Note, below) — explicitly not `BACKLOG.md` | It is not a candidate practice awaiting a trigger: `checkout-isolation` already exists as a validated-in-practice skill (`skills/checkout-isolation/SKILL.md`, referenced throughout this cycle). The finding is that the skill was not followed, not that a new practice needs building. `verify-report.md` itself says it is "not closable retroactively; it is a process note for the next cycle" — there is nothing to schedule, only something to remember, and a process reminder with no code or artifact remedy has no home in `BACKLOG.md`'s "candidate practice / downstream deliverable" scope |
| **SUGGESTION-1** | `rig/check.sh` has no bash self-test arm | **Already recorded** — `spec.md` Decision 3 and `design.md` §9 (both archived, unchanged) | Explicitly out of scope by a spec decision made *during* this cycle, not a new discovery. `design.md` itself left open "whether the check.sh bash-arm gap is registered here or its own cycle" without naming a trigger for either — so per `BACKLOG.md`'s own rule, it is not yet admissible there. Restating it as a fresh backlog entry would manufacture a trigger this cycle never decided on. It stays exactly where the cycle's own artifacts already put it |
| **SUGGESTION-2** | `STEP_TIMEOUT_S` / `SUITE_TIMEOUT_S` remain placeholders | **This report's own boundary section, above** — not `BACKLOG.md` | This is the single fact this archive is most obligated to state plainly (per the launch prompt's non-negotiable constraints), and it already leads this report. It is not "blocked on" anything external — it is simply undone configuration with no stated trigger, so it does not fit `BACKLOG.md`'s blocked-on-a-condition shape either. It is future SDD-proposal scope, named here so nobody mistakes this archive for founding the first countable run |
| **SUGGESTION-3** | Durable records (#308, #322, #344) cite unreachable commits `123b622` / `afced18` | **F-6**, performed this archive — see below | Administrative correction to the durable record, not a code requirement |
| **SUGGESTION-4** | Task count corrected 30 → 35 → 36 | **This report** (already stated correctly above as 36) | Purely informational; already resolved by carrying the correct final number. No action item, no `BACKLOG.md` entry — there is nothing left to do |
| **SUGGESTION-5** | Authored-line count convention (1147 excluding `MAP.md`, 1149 including it) | **This report** (stated once, above) | Informational convention, not an action. No `BACKLOG.md` entry |
| **SUGGESTION-7** | An absolute home path in Engram observation #322 | **Already resolved before this archive phase began** | Re-checked directly (`mem_get_observation(322)`, full text): the current revision (6) already carries its own note — "This observation itself was redacted on 2026-08-27 (verify finding S-7)" — and quotes only the safe `checkout-isolation` hook-preflight claim, no path. Nothing left to do here; recorded so this archive does not claim credit for a fix that predates it |
| **SUGGESTION-8** | "Cross-language" overstates what task 2.0's and task 2.9's pins span (both sides execute in CPython over two independently written source texts) | **This report only — no admissible home beyond it, stated plainly rather than invented** | It has no named unblock trigger; it is a "worth one clause in the docstring" improvement, which is exactly the shape `BACKLOG.md`'s own rule excludes ("an entry with no named trigger is not a backlog item, it is a wish"). It is too minor to warrant its own F-numbered follow-up task. Recorded here as the complete extent of its home: a future `rig/derive.py` docstring edit near `_self_test_load_surface_preimage_pin()` and `_self_test_preimage_digest_pin()`, whenever someone is already touching that code |
| **SUGGESTION-9** | A malformed `checker_self_test` block crashes `run_self_tests()` with a `TypeError` traceback instead of a reported `[FAIL]` | **Folded into F-7**, per the verify-report's own instruction | Same unguarded-subscript shape R-P4.1 exists to forbid, one layer over; cheap to fix alongside F-7's other `run_self_tests()` work |

**Count check**: 6 WARNING (1–6) + 9 SUGGESTION (1–9) = 15 findings. F-1..F-4 carry WARNING-1..4; F-5
carries SUGGESTION-6; F-6 carries SUGGESTION-3 and SUGGESTION-7 (SUGGESTION-7 already resolved); F-7
carries WARNING-6 and SUGGESTION-9. WARNING-5, SUGGESTION-1, SUGGESTION-2, SUGGESTION-4, SUGGESTION-5,
and SUGGESTION-8 are judged individually above. 6 + 9 = 15 accounted for, zero dropped silently.

## Durable-record correction sweep (F-6, performed as part of this archive)

`verify-report.md`'s SUGGESTION-3 and F-6 both frame this as an "on archive" action, and F-6 carries no
R-P requirement — it is record hygiene, not code, so it belongs to this phase rather than a future one.

Checked directly against the live repository:

- **SUGGESTION-7** (absolute home path in #322): **already resolved**, predates this archive phase —
  see the table above.
- **SUGGESTION-3** (stale commit citations): `git branch -a --contains 123b622` and `git branch -a
  --contains afced18` both return empty — neither commit is reachable from any ref. `2873e04` and
  `4217d4a` are both reachable (`git log --oneline -1 <sha>` resolves each). Engram observation **#322**
  was independently confirmed already corrected (its current revision cites `4217d4a` throughout, no
  `123b622`/`afced18` anywhere). Observations **#308** and **#344** still cite `123b622` (and, for
  #308, `afced18` as the commit it replaced) as if either were final.

This phase has no `mem_update` tool available — only `mem_search`, `mem_get_observation`, and
`mem_save` (which creates a new observation or upserts a topic's *latest* observation wholesale, rather
than patching text in place). Editing #308's or #344's substantive content in place, just to fix a
citation, risks losing information under the guise of a citation fix — the opposite of this cycle's own
record-not-erase discipline. Instead, one new, narrowly-scoped correction was saved:
`sdd/run-input-provenance/durable-record-correction` (see below), naming exactly which commits are
unreachable and which are the real ones, without touching #308 or #344's own text. This is the same
shape as every other correction this cycle made (`MAP.md`, `rig/README.md`): named, not silent, and
additive rather than an overwrite.

## MAP.md correction

`MAP.md:52` described this change as "applied (not yet verified)" — true when that line was written,
false now that the second verify pass and this archive have both landed. Corrected in this archive's
commit, as a named correction rather than a silent overwrite (the same convention this cycle used four
times: `rig/README.md`'s schema correction, `spec.md`'s R-P5/R-P11.2 corrections, `tasks.md`'s two
correction rounds, and `MAP.md`'s own prior edit during this cycle). The row now names the archive
path, the second-pass verdict, and states the `STEP_TIMEOUT_S`/`SUITE_TIMEOUT_S` boundary inline; a
short **Correction** paragraph was added directly below the Areas table explaining what changed and
why, matching `rig/README.md`'s own "Correction (…): …" convention exactly. `sdd/` row count (3 cycles)
is unchanged by archiving — 1 open (`measurement-rig`) plus 2 now-archived.

## Gate outputs (verbatim, run after the move)

**`./check.sh`:**
```
structure check: clean across 112 content files and 5 skill(s)
```
Exit 0.

**`./hooks/pre-commit --all`:** exit 0 (run before staging the archive commit; see Delivery below).

**`git diff HEAD -- rig/`:** empty. Zero bytes of output, confirming this archive phase made no code
change under `rig/`.

## Verify-report admitted-bytes reproducibility (post-move)

`verify-report.md`'s own HTML comment documents the extraction rule for its admitted bytes: strip the
frontmatter and the comment, and everything from the ` ```yaml ` fence to EOF is the admitted content.
Reproduced directly against the **moved** file
(`sdd/archive/2026-08-27-run-input-provenance/verify-report.md`):

```
$ tail -n +46 verify-report.md | shasum -a 256
c7e4f4ba5421ab21c4d77dd3489441816920d3bed6083b50cb32720f5ff3398b  -

$ gentle-ai sdd-verify-validate --input - --requirements 12 --scenarios 21 < <(tail -n +46 verify-report.md)
{
  "valid": true,
  "verdict": "pass_with_warnings",
  "evidence_revision": "sha256:2a78414391fdb3cdd98cf817d9d6365e71c50e6e86a56fd682ea9d2f44ece1d8"
}
```

The sha256 matches the file's own documented second-pass value exactly, and `gentle-ai
sdd-verify-validate` re-admits it with the identical verdict. The move did not alter the admitted
bytes, as the empty `diff -r` already guaranteed structurally; this is the independent confirmation
using the rule the file itself documents, not a restatement of the diff.

## What Ships

1. **A run's own record of what it was scored against** — `recorded_answer_key_digest` (Face A),
   `recorded_fixture_digest` (Face B), `recorded_surface_preimage_sha256` (Face C, per-step), and a
   positive `input_provenance_version` marker distinguishing "pre-scheme" from "captured under scheme
   but incomplete". A comparison whose comparand can no longer silently drift out from under it.
2. **Every comparand producer this cycle touched, independently proven able to fire** — including
   `load_surface()`, closed last by task 2.9 after the first verify pass caught it as the fourth
   instance of the same both-sides-move-together fault the prior cycle first found (R-F5.3), then Face
   A (task 2.0), then Face B (task 3.8), then Face C (task 2.9) — four independent second-look
   discoveries, never a phase re-running its own proof table.
3. **The transferable lesson, restated once more here because it is this cycle's real yield**: a
   comparison whose two sides are both derived from the function under test proves the comparison and
   proves the computation zero ways. Found four times, independently, by choosing mutation targets a
   prior phase had not tried.
4. **Two-sided cross-implementation pins for Faces A and C** — bash's `preimage_digest()` is itself a
   `python3` heredoc, so "cross-language" overstates what these pins span (SUGGESTION-8): both sides
   execute in CPython over two independently written source texts, and that is the real and sufficient
   guarantee — the texts cannot drift apart unnoticed. Face B deliberately carries no such pin, and
   that is correct: both sides run one `sha256`-of-bytes idiom over the same file, with no independent
   reimplementation to drift.

This cycle does **not** ship:
- Any countable run (`N = 0`, unchanged by this cycle and by this archive)
- Any comparative harness result
- A settled hypothesis (all three in `hypotheses/` remain open per ADR 0012, untouched by this cycle)
- Working timeout values — `STEP_TIMEOUT_S`/`SUITE_TIMEOUT_S` are still placeholders

## Delivery Summary

**Status**: Archive complete
**Authorization**: Native review gate `reviewGate` structurally absent (receipt-driven development is
off, decided by `clone_local`) — archive proceeds under ordinary repository policy
**Gate checks**: `./check.sh` clean (112 content files, 5 skills), `./hooks/pre-commit --all` exit 0,
`git diff HEAD -- rig/` empty
**Verification verdict**: PASS WITH WARNINGS — 0 CRITICAL, 6 WARNING, 9 SUGGESTION — archive permitted
**Archive integrity**: Mechanical `git mv`, `diff -r` empty (verbatim above)
**Delivery**: PR #8 (open, pushed) — this archive commit lands inside that PR, per this repository's
convention (the prior cycle's archive commit was likewise carried by its own PR, #4)

---

**Archived**: 2026-08-27
**Cycle**: Complete with documented warnings
**Next**: No additional SDD phases required for `run-input-provenance`. Seven named follow-ups
(F-1..F-7) recorded above for a future cycle to pick up at will; none blocks this archive. The
concrete prerequisite for founding the first countable run — real `STEP_TIMEOUT_S`/`SUITE_TIMEOUT_S`
values — is separate, unstarted work, named here so it is not mistaken for closed.
