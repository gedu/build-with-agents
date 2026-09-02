---
id: sdd/run-input-provenance/verify-report
type: journal
targets: [any]
status: draft
verified: 2026-08-27
sources: ["sdd/run-input-provenance/spec.md", "sdd/run-input-provenance/tasks.md", "sdd/run-input-provenance/apply-progress.md", "sdd/run-input-provenance/design.md"]
---

<!-- The admitted bytes are this file WITHOUT the frontmatter block above and
     WITHOUT this comment: they begin at the ```yaml fence and run to EOF.
     gentle-ai sdd-verify-validate rejects YAML frontmatter and requires the
     fenced yaml envelope as the first non-empty content; this repo's check.sh
     requires every content .md to open with `---`. The two are satisfied the
     way the previous cycle satisfied them (see
     sdd/archive/2026-08-18-failure-flood-triage/verify-report.md): validate the
     envelope-only bytes, commit with frontmatter prepended.

     SECOND PASS (re-grade after task 2.9, `4217d4a`). Admitted bytes
     sha256: c7e4f4ba5421ab21c4d77dd3489441816920d3bed6083b50cb32720f5ff3398b
     admitted as valid: true / verdict: pass_with_warnings, evidence_revision
     sha256:2a78414391fdb3cdd98cf817d9d6365e71c50e6e86a56fd682ea9d2f44ece1d8
     (= sha256 of the ASCII commit sha cdd50d4c88b170b00a1cf9356fea94f4754fbe99,
     the same convention the first pass used for 2873e04). Reproduce with:
     strip the frontmatter and this comment, lstrip newlines, then
     `gentle-ai sdd-verify-validate --input - --requirements 12 --scenarios 21`.

     FIRST PASS, superseded but recorded rather than erased. Verdict fail,
     1 CRITICAL, admitted bytes sha256
     d166b725cd00ec252d4c42479fbb8c05927679fb2614729f4c73e1f406aa69d2,
     evidence_revision
     sha256:4bdab3396026050e3d43f7bec1545e27806c66995c550bd58fdcf3193eca10f6
     (bound to 2873e04). One redaction was applied to that pass's own admitted
     bytes before commit, and it is recorded rather than silent: the WARNING-5
     prose quoted the checkout-isolation hook preflight's literal output, which
     contains an absolute home path. This repo is public (ADR 0009) and
     ./hooks/pre-commit correctly refused the file. The path became
     `<repo>/hooks/pre-commit` and the report was re-admitted, which is why the
     first pass's admitted-bytes sha256 is d166b725... and not the phase's
     original ea0c33c8... The gate wins over byte-preservation: a public repo
     cannot carry a home path, and the apply phase correctly stopped rather than
     either editing the report on its own authority or bypassing the hook. The
     second pass re-checked that redaction and found it meaning-preserving, and
     scanned the whole report for any other private identifier: zero hits. -->

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:2a78414391fdb3cdd98cf817d9d6365e71c50e6e86a56fd682ea9d2f44ece1d8
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 12/12
scenarios: 21/21
test_command: python3 rig/derive.py --self-test
test_exit_code: 0
test_output_hash: sha256:eb1149d6a752ffd97565fa9aa85c646d6d2a724dffcfd741d9fc19fbc274918c
build_command: ./rig/check.sh
build_exit_code: 0
build_output_hash: sha256:fe778a1340c0ccf99e2484eae8612dfec32d40292a82a3ec7c2a3f4b8f1fc28e
```

# Verification Report — run-input-provenance

Change: `run-input-provenance`. Branch `sdd/failure-flood-triage-planning`, HEAD `cdd50d4`,
tree `4021c12`. Artifact store: hybrid. Mode: full spec verification (proposal, spec, design,
tasks, apply-progress all present).

Read-only on code. Every mutation proof below ran in a throwaway copy of the working tree exported
with `git archive` under the session scratchpad; the real checkout was `git status` clean before and
after, `rig/derive.py` is sha256 byte-identical (`0ce09c06…`), no stray file remains under
`rig/surfaces/`, and the committed rows' `checker_digest` still equals the live `derive.py` digest.

## Verdict

**PASS WITH WARNINGS — 0 CRITICAL, 6 WARNING, 9 SUGGESTION.**

**This cycle is archivable.** All twelve requirements are satisfied, all 36 tasks are genuinely
`[x]`, and the single blocker from the first pass is closed by task 2.9 with real mutation
sensitivity, proven independently below rather than accepted from the apply report.

## Re-grade — second pass over `4217d4a` and `cdd50d4`

This report supersedes its own first pass (verdict `fail`, 1 CRITICAL, admitted bytes `d166b725…`,
`evidence_revision` bound to `2873e04`). The first pass is not erased: its evidence table, its
requirement-by-requirement proof and its N = 0 prose scan all stand unchanged below, and the
CRITICAL section is rewritten as a closure record rather than deleted, per this cycle's own
record-not-erase discipline.

Scope of the second pass, deliberately narrow: confirm CRITICAL-1's closure, re-check the five
WARNING and five SUGGESTION findings, verify task 2.9's own 98 lines as new and previously
unverified code, and re-grade. The twelve requirement findings were not re-derived except where
task 2.9 bears on them (R-P6.3, R-P10.1 and design §9 — all three improve).

| Gate | First pass | Second pass |
|---|---|---|
| `python3 rig/derive.py --self-test` | 59/59, exit 0 | **60/60, exit 0** |
| `bash rig/run-pipeline.sh --self-test` | 28/28, exit 0 | 28/28, exit 0 (output hash unchanged, `b58aa49a…`) |
| `./rig/check.sh` | 20/20, exit 0 | 20/20, exit 0 (output hash unchanged, `fe778a13…`) |
| `./check.sh` | clean, 111 content files | clean, **112 content files** and 5 skill(s) |
| `./hooks/pre-commit` | exit 0 | exit 0; `--all` also exit 0 |
| Tasks | 35, all `[x]` | **36**, all `[x]`, zero unchecked |
| Authored lines vs 800 budget | 1049 | **1147** (1149 counting `MAP.md`) |
| Scenarios with passing runtime evidence | 19/21 | **21/21** — the two R-P12 partials were executed this pass, see below |

## CRITICAL-1 — CLOSED by task 2.9 (`4217d4a`)

**Closed. The evidence is a differential mutation proof across the two commits, not a reading of the
new test.**

The first pass held that `load_surface()` — the parse behind Face C's live drift comparand
`surface_digest(load_surface(FAILURE_FLOOD_SURFACE_ARM))` at `rig/derive.py:901` — was proven zero
ways, because `_self_test_make_ff_run_dir` computes that one expression and assigns it to *both*
sides of every Face C comparison (`rig/derive.py:1616`), and because
`_self_test_preimage_digest_pin()` asserts `surface_digest()` over a hand-built Python list and never
calls `load_surface()` at all.

Task 2.9 adds `_self_test_load_surface_preimage_pin()` (`rig/derive.py:1391-1488`, +98/-0,
registered at `:2261`). It runs the deriver's own composed path over a synthetic preimage file
carrying a `# harness:` header, blank lines, a duplicate name, and both an indented and a
trailing-whitespace name, and compares it against `preimage_digest()` `sed`-extracted from
`rig/run-pipeline.sh` — the same extraction mechanism task 2.0 part 2 built for Face A.

**Differential proof, both trees exported with `git archive` and run side by side.** Three mutations
of `load_surface()` — drop the `not l.startswith("#")` header filter; append `[1:]` to the sorted
return; remove the value-side `.strip()`:

| Mutation | at `2873e04` (before task 2.9) | at `cdd50d4` (after) |
|---|---|---|
| drop `#` header filter | **59/59 PASS, exit 0 — silent** | **59/60, exit 1** — only the new case red |
| `[1:]` on the sorted return | **59/59 PASS, exit 0 — silent** | **59/60, exit 1** — only the new case red |
| drop value-side `.strip()` | **59/59 PASS, exit 0 — silent** | **59/60, exit 1** — only the new case red |

Each mutation is applied and reverted programmatically with a post-revert byte-equality assertion, so
the three runs are independent. The before/after asymmetry is the closure: the fault the first pass
described was real and undetectable, and is now detected by exactly one case, with no collateral
reds.

**The pin is symmetric, which the apply report did not claim and nobody had checked.** Mutating the
*bash* side instead — dropping the header filter, then the `.strip()`, inside `preimage_digest()`'s
body in `rig/run-pipeline.sh` — turns the new derive case red **and** turns `run-pipeline --self-test`
26/28 (its own pinned-constant case a, plus the empty-set case b). So the pair is anchored at both
ends by frozen literals while the composed parse is pinned two-sidedly: a change to one parse is
caught by the new case, and a change to *both* parses in the same direction is still caught by bash
case a's literal. **The both-sides-move-together class is closed for this pair, not merely relocated.**

**Severity nuance, confirmed independently and recorded so no later reader misreads task 2.9 as a
bugfix.** There was never a live defect. Over the real committed `rig/surfaces/failure-flood.txt`
(31 tool names), Python's `surface_digest(load_surface("failure-flood"))` and bash's
`preimage_digest()` both print
`d8693e27d5f8e406a465def75101c4eaa85b23b685e78c2d5d07754d0f7e8daa`. The gap closed is an unguarded
cross-implementation pair, not a disagreement.

Two consequences for the first pass's own findings, both upgraded:

- **R-P6.3** was graded "Satisfied in letter, undermined in substance". It is now **Satisfied**: the
  live comparand's producer has an independent proof.
- **Design §9** ("cross-language pins, a disagreement is the finding") was graded "Partly held" on
  Face C's account. It is now **Held** for all three faces.

## Task 2.9's own 98 lines — verified as new code

| Check | Result |
|---|---|
| New case present and passing at baseline | Yes — 60/60, exit 0, case named at self-test line 28 |
| Mutation-sensitive on the Python side | Yes — 3/3 mutations red, exactly one case each |
| Mutation-sensitive on the bash side | Yes — 2/2 mutations red on both suites |
| Production code touched | **No** — the `4217d4a` diff to `rig/derive.py` is +98/-0, entirely inside the new self-test function plus one roster line |
| Leaves the tree clean | Yes — `finally: unlink(missing_ok=True)`; `rig/surfaces/` holds exactly `broad.txt`, `failure-flood.txt`, `scoped.txt` after every run |
| Goldens consistent | Yes — 3 `failure-flood-v1` rows and 42 `tool-surface-v1` rows differ from `2873e04` only in `checker_digest`, and that value equals the live `derive.py` sha256 |
| Guard before writing | Yes — `assert not surface_path.exists()` refuses to clobber (fails safe; see SUGGESTION-6 for its failure *shape*) |

## The two R-P12 scenarios the first pass left partial — executed this pass

The first pass recorded 19/21 scenarios and left R-P12's two partial rather than executing them. A
passing verdict cannot rest on incomplete scenario evidence, so this pass executed both rather than
re-labelling them. **Both now hold at runtime.** Every run below was made in a full throwaway copy of
the tree (`rig/runs/` is gitignored, so a `git archive` export carries no run directories and a
filesystem copy was required); the real checkout was clean before and after, and its three `void`
rows are untouched — **N is still 0 in this repository.**

**Scenario: "An unproven deriver still refuses everything, unrelated to any single row's provenance."**
Flipping one `expected_practice_pass` in `rig/fixtures/tool-surface/v1/answer-key/t1.json`'s
`checker_self_test.negative_control` makes `run_self_tests()` report `[FAIL] t1/negative_control`. The
derive then exits **1** with the exact specified message on stderr — `Self-test FAILED — a detector
cannot be proven to fire. Refusing to derive rows.` — and **both** `runs.jsonl` files are
byte-unchanged, so no rows were written for any run. All three THEN clauses hold. The scenario names
no experiment, so this satisfies it as written; that it cannot be satisfied *through the
failure-flood experiment* is WARNING-2, unchanged.

**Scenario: "A single row's provenance mismatch derives everything else normally."** Built with the
deriver's own fixture builder in the throwaway copy: one run directory whose
`recorded_answer_key_digest` is deliberately wrong plus three whose digests match, added alongside
the three existing shakedown directories, then one single `python3 rig/derive.py --experiment
failure-flood-v1` pass over all seven:

```
derived 7 row(s) from 7 run dir(s)
  s1-monolithic-01:      state=void (shakedown)          <- pre-existing, unaffected
  s1-monolithic-9054:    state=void (shakedown)          <- pre-existing, unaffected
  s1-monolithic-91bad:   state=void (input-provenance-mismatch)   anomaly_classes=['answer-key-drift']
  s1-monolithic-91ok1:   state=complete
  s1-monolithic-91ok2:   state=complete
  s1-monolithic-91ok3:   state=complete
  s2-pipeline-9054:      state=void (shakedown)          <- pre-existing, unaffected
```

Exit 0. The mismatched row voids with exactly the specified `void_reason` and `anomaly_classes`, the
three matching rows derive to `complete` on their own inputs, and no other row is disturbed. This is
the composed multi-directory form the GIVEN specifies, which the committed suite does not exercise —
its cases each call `build_row_failure_flood` on one directory at a time, so per-row independence was
proven per row but never through `main()`'s loop. It is proven now.

**Both proofs are runtime evidence from this verification pass, and neither re-runs from the
repository.** That is recorded as WARNING-6, not glossed: it is the same shape as WARNING-4.

## The two previously unexamined items

### 1. Writing a synthetic file into `rig/surfaces/`, the real production directory

**Judgment: acceptable as shipped, and the apply phase's priority was correct — but the failure shape
is wrong, and that is worth one follow-up task (SUGGESTION-6).**

The hazard was checked rather than reasoned about, on all four surfaces named:

| Hazard | Finding |
|---|---|
| Interaction with `compute_manifest()`'s walked set | **None.** `compute_manifest()` walks a *fixture root* over `src`, `tests`, `runtime`, `tools`, `answer-key`, `prompts` (`rig/run-pipeline.sh:162-182`). `rig/surfaces/` is not a fixture root and is not in that list, so a stray file can never enter `MANIFEST.sha256` or the recompute-compare gate |
| Interaction with `rig/check.sh` / `./check.sh` | **None.** Nothing in either gate reads `rig/surfaces/`; `./check.sh` counts content `.md` files, and a stray `.txt` is not one. Verified live: 20/20 and clean at 112 content files with a stray file present |
| Collision with a real arm name | **Not reachable.** Every `load_surface()` call site passes a hardcoded literal — `broad`, `scoped`, `failure-flood` (`rig/derive.py:1253`, `:1264`) — and nothing anywhere in the repo globs, `iterdir`s or `find`s that directory. The arm name is `__self_test_load_surface_preimage_pin`, and the pre-write assert refuses to overwrite |
| Crash mid-test leaving a stray arm file | **Reachable only under SIGKILL or power loss.** `finally` covers normal return, exceptions, `KeyboardInterrupt` and `SystemExit`. Verified: the derive path is unaffected by a stray file (`--experiment failure-flood-v1` exits 0), and deleting it restores the suite to green |

What is genuinely wrong is the *shape* of the residual failure, reproduced directly: with a stray
file present, `--self-test` does not report a `[FAIL]` case — the bare `assert` propagates out of
`run_self_test()` and the run dies with an `AssertionError` traceback. A suite whose job is to name
which case failed instead prints a stack trace, and the state is untracked, so `git add -A` could
commit it. Both are cheap to fix (SUGGESTION-6).

### 2. The new pin's expected value coinciding with task 2.1's pin (`4a626b46…`)

**Judgment: benign, and materially less confusing than the framing suggests, because the new pin
contains no constant at all.**

Verified by reading the code and recomputing: `_self_test_load_surface_preimage_pin()` asserts
`python_digest == bash_digest` and pins **no literal**. The coincidence is real — the synthetic file's
set reduces to `{Bash, Read, Write}`, whose digest is exactly the `4a626b46…` that task 2.1 pins —
but it is a *computed* value that appears nowhere as a constant, so there is no second literal for a
reader to confuse with the first. Nothing needs distinguishing.

The apply phase was right to verify the coincidence rather than assume it, and right to call it a
coincidence: the two cases pin different things over the same value. Task 2.1 pins the hash
*convention* over a hand-built list; task 2.9 pins the *parse* through `load_surface()`. The mutation
table above is the proof they are not redundant — all three `load_surface()` mutations leave task
2.1's case green.

One optional hardening, and one label correction, are recorded as SUGGESTION-7 and SUGGESTION-8.

## The redaction applied to the first pass

**The redaction preserved WARNING-5's meaning exactly, and no other private identifier remains
anywhere in this report.**

WARNING-5's load-bearing claim is that the `checkout-isolation` hook preflight prints `ok` from the
primary checkout — meaning the resolved hook path lies *inside this tree* — so the sibling commits
were covered by the redaction gate. Replacing the absolute prefix with `<repo>` removes the home path
while leaving that claim fully stated and fully checkable: `<repo>/hooks/pre-commit` is inside the
tree by construction, which is precisely what `ok` asserts. Nothing was weakened, and the redaction
is disclosed rather than silent.

Re-verified independently this pass, with paths reduced to basenames before printing:

```
tree=<repo>                          -> ok, gated by this tree: <repo>/hooks/pre-commit
tree=<repo>-worktrees/gaps-analysis  -> WRONG TREE
tree=<repo>-worktrees/installer-shape -> WRONG TREE
tree=<repo>-worktrees/open-work-index -> WRONG TREE
```

Scanned this whole report for every class of private identifier the gate guards: user-home and
system-temporary absolute path prefixes, home-relative and environment-variable path forms,
usernames, e-mail addresses, hostnames, and private repository or remote names. **Zero hits.** `./hooks/pre-commit --all` exits 0 on the tree containing it. The one place an
absolute home path still survives is outside this repository and outside the gate's reach — see
SUGGESTION-7.

## Re-check of the first pass's WARNING findings

All five re-checked against `cdd50d4`. **None resolved, none worsened, none re-graded.** Task 2.9 is
test-only and touches nothing any of them depends on.

| # | Finding | Status | Evidence this pass |
|---|---|---|---|
| **WARNING-1** | `steps[].recorded_surface_preimage_sha256` is absent, not null, on all three committed rows | **Still valid** | Re-read the committed `runs.jsonl`: the three row-level fields are present on 3/3 rows; the per-step field is present on **0/2, 0/2 and 0/4** steps. Unchanged by task 2.9's re-derive |
| **WARNING-2** | The refusal-to-derive gate is vacuous for `failure-flood-v1` | **Still valid** | The `if "tool_sets" not in ak: continue` skip is intact at `rig/derive.py:383`. The self-test suite is still not composed into the derive path — it is now a **60**-case suite that `python3 rig/derive.py --experiment failure-flood-v1` still does not run. Grading held at WARNING, not raised: R-P12.1 asks only that the existing refusal not be weakened, and the refusal *is* covered by a passing runtime test for `tool-surface-v1`. Raising it now on no new evidence would be the inconsistency this cycle exists to correct |
| **WARNING-3** | Task 2.5's comparand change is a row-outcome no-op that should be a permanent claim boundary | **Still valid, empirically re-proven** | Reverting `rig/derive.py:1001` to the pre-change live comparand leaves **60/60 green, exit 0** — the no-op survives task 2.9, and still no test would notice. The comment at `:993-1000` explains the *deletion* and calls the drift comparand "above", but does not record that the no-op is *conditional* on the `:974-978` accumulation continuing to exist. Partially mitigated, not closed |
| **WARNING-4** | R-P2.2a's order-swap proof was executed but never committed | **Still valid** | `tasks.md:664` and `:675` describe the swap as "a throwaway local edit, reverted"; `:982` records that it "needed a real, executed order-swap proof (a scratch-copy `--self-test` run…)". Nothing in `rig/derive.py` re-runs it. The property itself remains structurally true |
| **WARNING-6** | *(new)* The two R-P12 scenario proofs do not re-run from the repository | **New this pass** | Both were executed here (section above) and both hold, but neither exists as a committed case: the composed multi-directory derive was assembled in a throwaway copy, and the all-or-nothing refusal was proven by hand-corrupting an answer key. ADR 0013's rule is that a committed executable carries its own test. Same shape as WARNING-4, and the same remedy — see F-4 and F-7 |
| **WARNING-5** | No worktree taken, against `checkout-isolation` | **Still valid, and now covers a fourth commit** | Three foreign worktrees and a foreign `stash@{0}` still present; task 2.9 and the report commit were both made in the shared primary checkout. Re-verified above: the primary checkout's gate resolves inside its own tree, so all four commits *were* gated. Not retroactively closable — a process note for the next cycle |

## SUGGESTIONS

1. **`rig/check.sh` has no bash self-test arm** — `check_component_self_test()` hardcodes `python3`
   (`rig/check.sh:163`), so `rig/run-pipeline.sh --self-test` is never composed and must be run by
   hand. Still true; correctly deferred by spec Decision 3.
2. **`STEP_TIMEOUT_S=180` / `SUITE_TIMEOUT_S=150` remain placeholders**
   (`rig/run-pipeline.sh:85-86`). Still true. Closing this cycle does not found the first countable
   run.
3. **Durable records cite commits that no longer exist, and one now cites a stale HEAD** — Engram
   observations #308, #322 and #344 reference `123b622` and `afced18` for Sibling 3; both are still
   unreachable this pass (`git branch -a --contains` empty), while `2873e04`, `5cfa456` and
   `4217d4a` are all reachable. Additionally, this report's own first pass declared HEAD `2873e04`,
   which is no longer HEAD. Worth one correction sweep on archive so every durable citation resolves.
4. **Task count** — the first launch prompt said 30; the first pass corrected it to 35; the artifact
   now carries **36** (1.1–1.11, 2.0–2.9, 3.1–3.8, 4.1–4.7). All `[x]`, zero unchecked.
5. **Authored-line count excludes `MAP.md`** — 1147 reconciles exactly on that convention
   (385 + 341 + 323 + 98), 1149 with it. Immaterial to the authorized `size:exception`, but the
   convention is worth stating once.
6. **NEW — task 2.9's self-test writes into the production `rig/surfaces/` directory, and its
   residual failure is a traceback rather than a reported case.** The choice was correct on its own
   terms: `load_surface()` takes no root parameter, and the apply phase rightly refused to weaken
   production code to make a test reachable. But there is an *additive* alternative that removes the
   production write entirely without weakening anything — `def load_surface(arm, root=SURFACES_ROOT)`,
   leaving every production call site unchanged. Failing that, two one-line fixes: convert the bare
   `assert` into a reported `[FAIL]` case so an interrupted run names itself instead of printing a
   stack trace, and add the fixed arm name to `.gitignore` so a stray file can never be committed.
   Reproduced this pass: with a stray file present, `--self-test` dies with an `AssertionError`
   traceback, and the derive path is unaffected.
7. **NEW — an absolute home path survives in the durable record outside the gate's reach.** Engram
   observation #322's `Learned/BLOCKER` text quotes the very path that `./hooks/pre-commit` refused,
   in full. ADR 0009's redaction obligation is repo-wide, but Engram is not a repository file, so no
   gate scans it. Worth scrubbing that observation on archive; it is the same class of hole the
   pre-commit hook exists to close, one storage layer over.
8. **NEW — "cross-language" overstates what the pin spans, and a future reader should know.** Bash's
   `preimage_digest()` is itself a `python3` heredoc (`rig/run-pipeline.sh:255-268`), so both sides of
   task 2.0's and task 2.9's pins execute in CPython over two independently written source texts. The
   pin's real and sufficient value is that the two *texts* cannot drift apart unnoticed — proven five
   ways above, in both directions. What it does not span is a shared CPython assumption, `str.splitlines()`'s
   treatment of `\x0b`, `\x0c` and `U+2028` being the concrete example: a change there moves both
   sides together. Low impact, since the convention is separately anchored by two frozen literals.
   Worth one clause in the docstring so "cross-language" is not read as more isolation than it buys.

9. **NEW — a malformed `checker_self_test` block crashes the derive instead of failing it.** Found
   while executing R-P12's first scenario: an answer key whose `checker_self_test` case is a string
   rather than an object raises `TypeError: string indices must be integers` at `rig/derive.py:390`
   (`case["synthetic_tool_uses"]`), producing a traceback rather than the refusal message. The
   *outcome* is still safe and still satisfies R-P12.1 in substance — exit 1, no rows written — so
   this is not a requirement violation, and it is pre-existing and untouched by this cycle. But it is
   the same unguarded-subscript shape R-P4.1 exists to forbid one layer over, in a block read from an
   answer key, and R-P4's own `.get()` discipline would close it in two lines.

## First pass — evidence retained unchanged

Everything below is the first pass's own work at `2873e04`, retained rather than re-derived, because
task 2.9 bears on none of it except the three rows already upgraded above. The commands and hashes
in the envelope are this pass's; the first pass's were
`sha256:7743851881f745e7de27a3c3ebb22e7377f8d9228c83ccf18e96bf66820b4206` (test, 59 cases) and the
same `fe778a13…` build hash, which is unchanged and therefore reproducible across both passes.

### Independent re-verification of the supplied numbers

| Claim | Result |
|---|---|
| `python3 rig/derive.py --self-test` | **60/60 PASS**, exit 0 — CONFIRMED (59/59 at `2873e04`) |
| `bash rig/run-pipeline.sh --self-test` | **28/28 PASS**, exit 0 — CONFIRMED |
| `./rig/check.sh` | **20/20**, exit 0 — CONFIRMED |
| `./check.sh` | clean, `112 content files and 5 skill(s)` — CONFIRMED |
| `./hooks/pre-commit` | exit 0 — CONFIRMED |
| `failure-flood-v1` three rows | `void` / `shakedown` / `["pre-scheme-provenance"]`, `schema_version` 4 — CONFIRMED |
| `failure-flood-v1` provenance fields all `null` | **REFUTED in one detail** — three row-level fields are present-and-`null`; the fourth (`steps[].recorded_surface_preimage_sha256`) is **absent**, not null. See WARNING-1 |
| `tool-surface-v1` 42 rows, `schema_version` 3, only `checker_digest` differs | CONFIRMED — per-key diff over all 42 rows yields exactly `{checker_digest: 42}` |
| `build_row` + registry entry byte-unchanged | CONFIRMED |
| Authored lines vs 800 budget | CONFIRMED — 1049 at `2873e04`, **1147** after task 2.9's +98 |
| Task count | **CORRECTED** — **36** tasks, all `[x]`, zero unchecked |

### Requirement compliance — all twelve

| Req | Status | Proof (file:line) |
|---|---|---|
| **R-P2.1** Face A recorded at run time, one root, runner never resolves `task_id` | **Satisfied** | `rig/run-pipeline.sh:748`; `answer_key_paths()` at `:200-202` filters `compute_manifest`'s output by `^answer-key/` prefix — no `task_id` logic anywhere in the runner. Read back at `rig/derive.py:931`, `:1189` |
| **R-P2.2** one edit records BOTH drifts, no precedence | **Satisfied** | `rig/derive.py:954-981` — one `drifted` set accumulated across all faces, single decision at `:979-981`. Case 58 asserts both classes present |
| **R-P2.2a** withdrawn precedence MUST NOT return; order not observable | **Satisfied** | No per-face `void_reason`, no early `break`/`return`, no ordering predicate. `rg 'precedence'` over `rig/` returns nothing. Order-independence is structural, not conventional. See WARNING-4 on the proof's durability |
| **R-P3.1** drifted answer key voids, before scoring | **Satisfied** | Detector `rig/derive.py:955-957`; gate closes at `:981`, all scoring downstream at `:1116-1155`. Case 44 |
| **R-P3.2** downgrade-only | **Satisfied** | Nested inside `elif state == "complete":` at `rig/derive.py:922`. Case 49 |
| **R-P4.1** no direct subscripts; malformed key voids, never raises | **Satisfied** | `rig/derive.py:967-969`, `:1139`, `:1153`, `:1238`. Case 48 |
| **R-P5.1** positive marker recorded | **Satisfied** | Written `rig/run-pipeline.sh:1210`; read `rig/derive.py:917`, projected `:1188` |
| **R-P5.2** pre-scheme voids, annotation independent of transition | **Satisfied** | `rig/derive.py:918-921` — `anomaly_classes.add` is outside the `state == "complete"` guard. Cases 46, 50 |
| **R-P5.3** null digest → `provenance-capture-incomplete`, distinguishable | **Satisfied** | `rig/derive.py:931-943`, covering all three faces including the per-step surface term at `:937-940`. Cases 47, 57 |
| **R-P5.4** not-`True` is not-proven, both sites | **Satisfied** | `rig/derive.py:1005` and `:1034`. Cases 30, 31 |
| **R-P5.5** pre-scheme caught once, not twice | **Satisfied** | The `if/elif` at `rig/derive.py:918`/`:922` is mutually exclusive by construction. Case 29 |
| **R-P6.1** comparand frozen per run | **Satisfied** | `rig/derive.py:1001` compares `step["surface_sha256"]` against `step["recorded_surface_preimage_sha256"]`; recorded at `rig/run-pipeline.sh:971`, threaded at `:915`. See WARNING-3 |
| **R-P6.2** the `is not None` guard MUST NOT persist unchanged | **Satisfied** | Guard deleted; `rig/derive.py:993-1000` records why. Case 54 is the ordering proof |
| **R-P6.3** frozen-vs-live drift gets its own reason, never `surface-mismatch` | **Satisfied** *(upgraded — first pass read "in letter, undermined in substance")* | Detector `rig/derive.py:974-978`; case 53 asserts `surface-preimage-drift` and NOT `surface-mismatch`. The live comparand's producer now has its own proof — task 2.9, closure recorded above |
| **R-P7.1** fixture digest recorded at run time | **Satisfied** | `rig/run-pipeline.sh:738`, over bytes the recompute-compare gate at `:718-724` has already proven match the live tree. Read back `rig/derive.py:936`, `:1190` |
| **R-P7.1a** disagreement → `input-provenance-mismatch` + `fixture-drift` | **Satisfied** | `rig/derive.py:958-960`. Case 56 asserts `fixture-drift` present and `answer-key-drift` absent |
| **R-P7.2** R-F5.3 claim boundary stated unambiguously | **Satisfied** | `sdd/run-input-provenance/apply-progress.md:472-482`, restated at `MAP.md:52`. `rig/README.md`'s correction never cites R-F5.3, so its conditional obligation is not triggered there |
| **R-P8.1 / R-P8.2** three rows marked, never promoted | **Satisfied** | Verified against the committed file: 3 rows, `schema_version` 4, `state=void`, `void_reason=shakedown`, `anomaly_classes == ["pre-scheme-provenance"]`. Zero `complete` rows |
| **R-P9.1** 7.15 retired, replaced by three siblings | **Satisfied** | `sdd/run-input-provenance/tasks.md:80` records the retirement and the mapping |
| **R-P9.2** the A → C → B order is itself the contract | **Satisfied** | `git log` oldest first: `0637d68` (Face A) → `5cfa456` (Face C) → `2873e04` (Face B), confirmed by first appearance of each detector's own class string. No face's detector landed early |
| **R-P10.1** every new/changed detector proven able to fire | **Satisfied** *(strengthened)* | Cases 44, 48, 29/30/31, 53, 56 all PASS at runtime, and task 2.9 extends the same standard from detectors to the *comparand producers* they depend on — all three faces now have one |
| **R-P10.2** case 3 rewritten not deleted, plus a new case | **Satisfied** | `rig/derive.py:1594-1604` and `:1603-1607`, plus an unrequired case 5. Cases 29, 30, 31 |
| **R-P11.1** additive bump, no migrations | **Satisfied with one shortfall** | `FAILURE_FLOOD_SCHEMA_VERSION = 4`; nothing reads the old value. But "rewrites every existing row with … the new fields" does not hold for Face C's per-step field — WARNING-1 |
| **R-P11.2** two per-experiment projections | **Satisfied** | Re-derived and diffed per key. `tool-surface-v1`: 42 rows, differing keys exactly `{checker_digest: 42}`. `failure-flood-v1`: 3 rows, differing keys exactly `{checker_digest, schema_version, anomaly_classes}` — zero disallowed deltas |
| **R-P12.1** refusal stays all-or-nothing | **Satisfied, with a claim boundary** | Block intact; proven live this pass — a cleanly failing detector yields exit 1, the exact refusal message, and both `runs.jsonl` byte-unchanged. Vacuous for `failure-flood-v1` — WARNING-2 |
| **R-P12.2** one row's mismatch does not refuse everything | **Satisfied** | `build_row_failure_flood` has no refusal path; cases 44/48 prove a per-row void with no exception escaping. The "other rows still derive" half is no longer only architectural — proven live this pass over seven directories in one derive (section above). Not exercised by any *committed* case — WARNING-6 |
| **R-P1.1** N stays 0 | **Satisfied** | 0 rows `state=complete` in the committed file. Nothing in the change can promote a row |

Requirement-level total: **12 / 12 satisfied.** Scenario-level: **21 / 21** with passing covering
runtime evidence — the two formerly-partial R-P12 scenarios were executed in this pass (section
above); see WARNING-6 on the durability of those two proofs.

### Comparand producers — the full sweep, re-stated with task 2.9 folded in

| Candidate | Independent proof of its computation? |
|---|---|
| `surface_digest` (`derive.py:90`) | **Yes** — pinned literal at `:1383-1385`; a constant-return control turns it red |
| `preimage_digest` (bash, `run-pipeline.sh:255`) | **Yes** — pinned literal over a real synthetic file, `:578-581`; also covers absent/empty shapes at `:586-599` |
| `answer_key_set_digest` (`derive.py:621`) | **Yes** — task 2.0 case a (self-mutation) + case b (real `sed`-extracted pin) |
| `fixture_digest_at` (`derive.py:612`) | **Yes** — task 3.8 case a, same-length one-byte mutation with a length assertion at `:2137-2139` |
| `hash_paths` (bash, `:226`) | **Yes** — before/after fire-proofs at `:432-454` plus task 2.0's pin |
| `compute_manifest` (bash, `:162`) | **Yes, and the strongest** — pinned in production against the committed `MANIFEST.sha256` at `:718-724`, which hard-refuses the run on mismatch; path selection proven at `:533-561` |
| `load_surface` (`derive.py:97`) | **Yes — closed by task 2.9**, mutation-proven five ways this pass (was the first pass's CRITICAL-1) |
| `checker_digest` (`derive.py:83`) | Out of scope — Face D, declared Non-Goal, excluded by R-F5.3's own scenario |
| `fixture_digest(version)` (tool-surface) | Untouched by this cycle; pinned by the committed 42-row golden |
| `manifest_workspace_paths`, `answer_key_paths` | Yes — exact-literal expectations at `:557-569` |
| `read_back_init` (bash, `:333`) | Produces `surface_sha256` from the CLI's own init event; not a comparand this cycle changed |

**Every comparand producer this cycle touched now has an independent proof.** That was the open item
at the end of the first pass and it is the reason the verdict moves.

### WARNING-1 — Face C's per-step field is absent, not null, on all three committed rows

`steps[].recorded_surface_preimage_sha256` is **not a key** on any of the three committed
`failure-flood-v1` rows. The row-level fields are written explicitly (`rig/derive.py:1188-1190`), so
they land as present-and-`null`; the per-step field has no such write and relies on
`step_out = dict(step)` at `:1052` copying it through, which cannot invent a key a pre-scheme
`arm.json` never had.

R-P11.1 requires that re-deriving "rewrites every existing row with the new schema version **and the
new fields**". Three of four land; the fourth does not. Detection is unaffected — `:938` uses
`s.get(...) is None`, treating absent and null alike — but the consumer contract is asymmetric
(`row["recorded_fixture_digest"]` yields `None`,
`row["steps"][i]["recorded_surface_preimage_sha256"]` raises `KeyError`). It also makes PR #8's "all
four provenance fields `null`" and `apply-progress.md:174`'s neighbouring claim imprecise;
`apply-progress.md:181` is correct because it says "the three new row-level fields".

Not a blocker: no requirement is violated in substance, `rig/derive.py:654-657` documents the
copy-through decision deliberately, and no consumer reads the field today (`rig/report.py` does not).
Worth one line of correction on archive.

### WARNING-2 — the refusal-to-derive gate is vacuous for `failure-flood-v1`

`run_self_tests()` is fed the **per-experiment** answer-key loader (`rig/derive.py:2210`) and skips
every key without `tool_sets` (`:381-384`). `failure-flood`'s answer keys carry `C`/`F0`/`S0`/`R0`
and define no `checker_self_test`, so for that experiment `run_self_tests()` iterates **zero cases
and returns `True` vacuously.** Proven live: the same corrupted `t1/negative_control` that makes
`--experiment tool-surface-v1` exit 1 with no rows leaves `--experiment failure-flood-v1` at exit 0
with rows written.

Compounding it: the self-test suite — which contains **every one of this cycle's detector proofs, now
including task 2.9's** — is not composed into the derive path at all. Only `rig/check.sh` composes it
(`check_component_self_test`, `:160-171`), and that helper hardcodes `python3` (`:163`), which is also
the named bash-arm gap. So `python3 rig/derive.py --experiment failure-flood-v1` will derive rows
with all 60 proofs broken.

This is **not a violation of R-P12.1**, which asks only that the existing refusal not be weakened —
it was not, and the skip predates this cycle (task 5.8). R-P12's two scenarios name no
experiment and are satisfied through `tool-surface-v1` (proven live above), but the precondition
"`run_self_tests()` fails" remains unsatisfiable for the experiment this cycle is actually about, and
that is the substance of this warning. Task 4.4's parenthetical — "no `--experiment` flag
needed — `run_self_tests()` runs unconditionally in `main()`" — is literally true and materially
misleading; the done-note's own evidence is honest and correctly names `tool-surface-v1`.

### WARNING-3 — task 2.5's comparand change is a row-outcome no-op, and that should be a permanent claim boundary

Sibling 2's report recorded task 2.5's comparand choice as a provable no-op at the row-outcome level.
**Confirmed still true after Sibling 3 and after task 2.9, and confirmed empirically twice**:
reverting `rig/derive.py:1001` to the pre-change live comparand (`step_surface != ff_surface_digest`)
leaves **60/60 green**. It has to — the Face C accumulation at `:974-978` voids any row whose
recorded value differs from `ff_surface_digest` for any model step, so every row reaching the
read-back loop satisfies `recorded == live` and the two comparands are indistinguishable there.
R-P6.1 and R-P6.2 are satisfied on their own terms.

**It should be recorded as a permanent claim boundary rather than left as an apply-phase note**,
because the no-op is conditional on a guarantee living 25 lines away. Narrowing or removing the Face
C drift accumulation at `:974-978` would silently make `:1001`'s comparand observable, and there is
no test — and by construction can be no test — that would notice. The comment now at `:993-1000`
explains the deletion and refers to the drift comparand "above", which is close but not the same
claim: it does not say that the no-op *depends* on `:974-978` surviving. The right home is one added
clause there naming `:974-978` as the invariant's owner.

### WARNING-4 — R-P2.2a's order-swap proof was executed but never committed

`2873e04`'s message records that the both-drifts case was proven "under the checks' own code order
and again with that order swapped in a scratch copy". The swapped run is gone with the session. The
property itself is structurally true and was verified by reading `rig/derive.py:954-981` (one
accumulator, no early exit, no ordering predicate), so R-P2.2a is satisfied — but ADR 0013's own rule
is that a committed executable carries its own test, and this proof does not re-run.

### WARNING-5 — no worktree taken, against `checkout-isolation`

An SDD cycle is long-running work in a checkout that demonstrably has other writers: three foreign
worktrees exist (`gaps-analysis` on `main`, `installer-shape` on `docs/installer-shape`,
`open-work-index` on `feat/gap-record-prowler`) and `stash@{0}` is not this cycle's.

**One mitigation verified rather than assumed.** The `checkout-isolation` hook preflight, run from
this checkout, prints `ok — gated by this tree: <repo>/hooks/pre-commit` (the absolute path this
command actually printed is redacted here per ADR 0009 — this repo is public). The primary checkout's
hook resolves inside its own tree, so all four of this cycle's commits **were** covered by the
redaction gate. Running the same check from each worktree prints `WRONG TREE` for all three,
confirming the shim gap is still open and still accurately described. Had this cycle taken a
worktree, its commits would have been gated by another tree's script.

### The N = 0 prose scan

Every file this cycle touched was scanned, plus the delivery surface. Files: `MAP.md`,
`rig/README.md`, `rig/derive.py`, `rig/run-pipeline.sh`,
`sdd/run-input-provenance/apply-progress.md`, `sdd/run-input-provenance/tasks.md`,
`rig/results/failure-flood-v1/runs.jsonl`, `rig/results/tool-surface-v1/runs.jsonl`, and PR #8's
body. Method: a phrase scan for constructions that assert countable results, then a full read of
every occurrence of `countable`, `comparative`, `N =`, `N is`, `state=complete` and `"complete"` in
the prose files.

**Result: no violation. The boundary holds in every artifact.** The two phrase-scan hits in
`tasks.md` (`:15`, `:641`) are the prohibition itself, not a breach. Task 2.9's own additions —
its docstring, its `tasks.md` done-note and its `apply-progress.md` section — introduce no outcome
language: they are about a parse and a digest, and the "no live defect" paragraph is a statement
about two hashes agreeing, not about any run.

The four sentences that came closest, each read in full and each clean:

- `sdd/run-input-provenance/tasks.md:341-344` — "on the first real countable run *every* row voids
  with `answer-key-drift`". Conditional and counterfactual, inside a mutation-proof rationale. Names
  a future risk, asserts no present result. Notably, this is the sentence that predicted CRITICAL-1's
  class for Face A.
- `apply-progress.md:221` and `:788` — "Whether to fund a real, countable run stays the operator's
  [decision]". Forward-looking and explicitly unfunded.
- `MAP.md:52` — the longest and most exposed passage, and correct: "still an instrument plus a
  **failed** ratio target, never a comparative result: zero countable runs", with the archived
  cycle's boundary carried verbatim rather than paraphrased.
- `rig/README.md:63-74` — the schema correction. Describes only field names and the schema bump; no
  outcome language of any kind.

**PR #8's body is the strongest of the artifacts on this point**, not merely compliant: it opens with
a blockquote (`N = zero countable rows`), splits "What can be claimed" from "What cannot be claimed",
states that no countable run has ever been made, and volunteers that the timeout placeholders mean
closing this cycle is **not** sufficient to found the first one. Its one imprecision is factual, not
boundary-related: "all four provenance fields `null`" (see WARNING-1).

### Design coherence

| Design decision | Code state |
|---|---|
| §1 Face C is per-step, Faces A/B arm-level | Held — `rig/run-pipeline.sh:915` (step) vs `:1211-1212` (arm) |
| §2 set-wide answer-key digest per fixture root | Held — `rig/run-pipeline.sh:748` |
| §4 one `void_reason` pair + per-face drift classes | Held — `rig/derive.py:921`, `:942`, `:980` and the three drift strings |
| §7 `tool-surface-v1`'s registry entry gains no key | Held — `rig/derive.py:1246-1256` byte-unchanged; `answer_key_digest` appears only in the failure-flood entry at `:1270` |
| §9 cross-language pins, a disagreement is the finding | **Held** *(upgraded — first pass read "partly held")* — real pin for Face A (task 2.0), correctly-argued absence for Face B (`rig/derive.py:2107-2121`), and now a real two-sided pin for Face C (task 2.9). See SUGGESTION-8 on what "cross-language" does and does not span |

## What would have to change for the last grade up

**PASS WITH WARNINGS → PASS.** None of these blocks archive; each is a named follow-up task with its
requirement.

| Task | Requirement | Change |
|---|---|---|
| **F-1** | R-P11.1 | Write Face C's per-step field explicitly so all four provenance fields are present-and-`null` on re-derived rows, and correct the "all four … null" wording in PR #8 and `apply-progress.md:174` (WARNING-1) |
| **F-2** | R-P12.1 | Either give `failure-flood`'s answer keys a `checker_self_test` block or compose `derive.py --self-test` into the derive path, so the gate is not vacuous for the experiment this cycle is about; also correct task 4.4's parenthetical (WARNING-2) |
| **F-3** | R-P6.1 / R-P6.2 | Add one clause at `rig/derive.py:993-1000` naming `:974-978` as the owner of the invariant that makes `:1001`'s comparand unobservable (WARNING-3) |
| **F-4** | R-P2.2a / R-P10.1 | Commit the order-swap proof as a self-test case so it re-runs (WARNING-4) |
| **F-5** | R-P10.1 | Give `load_surface()` an additive `root=SURFACES_ROOT` default so no self-test writes into `rig/surfaces/`; failing that, convert task 2.9's bare `assert` into a reported `[FAIL]` case and `.gitignore` the fixed arm name (SUGGESTION-6) |
| **F-7** | R-P12.1 / R-P12.2 / R-P10.1 | Commit the two R-P12 scenario proofs executed in this pass so they re-run: a multi-directory derive case (one mismatched plus several matching run dirs in one pass) and a refusal case driven by a cleanly failing detector. Fold in SUGGESTION-9's two-line `.get()` fix while in `run_self_tests()` (WARNING-6) |
| **F-6** | — | Correction sweep on the durable record: scrub the absolute home path from Engram #322, and repoint #308/#322/#344's unreachable `123b622`/`afced18` citations at `2873e04`/`4217d4a` (SUGGESTION-3, SUGGESTION-7) |

WARNING-5 is not closable retroactively; it is a process note for the next cycle, and the hook
preflight above shows the redaction gate did in fact cover all four of this cycle's commits.
