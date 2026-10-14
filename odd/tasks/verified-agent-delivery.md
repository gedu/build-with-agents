---
id: odd/verified-agent-delivery/tasks
type: journal
targets: [any]
status: draft
verified: 2026-10-14
sources: ["journal/2026-08-17-three-rules-with-no-verifier.md", "theory/loops/verifier-availability.md", "decisions/0014-a-public-guarantee-cannot-be-opt-in.md", "decisions/0016-open-work-is-enumerated-from-structure.md", "decisions/0013-a-committed-executable-carries-its-own-test.md", "sdd/archive/2026-08-27-run-input-provenance/archive-report.md", "hypotheses/0002-pipeline-shape-lowers-peak-occupancy.md", "hypotheses/0003-serial-triage-compounds-cumulative-tokens.md", "skills/checkout-isolation/SKILL.md", "gaps/0002-expensify-app.md"]
---

# Feature: verified agent delivery

Locator: `odd/tasks/verified-agent-delivery.md`

Objective in one line: make "the agent said it is done" replaceable by a generated, machine-checked
list of what the change owed and whether each item was discharged — and give that list a denominator
that runs where a collaborator cannot skip it.

Created 2026-10-14. Worktree `ci/public-gate` from `origin/main` at `57faaf3`.

## Specs

Quoted from the operator's own words. A spec is what acceptance is judged against; none of them are
paraphrased, and nothing below adds a requirement nobody asked for.

**S1 — the goal, verbatim.** *"darle un proyecto a un agente, decirle que haga algo y tener un 99.9%
de confianza que TODO lo que tenia que hacer se hizo, no rompio nada en paralelo, arreglo o actualizo
las dependencias que implicaban por ese cambio, arreglo o mejoro lo que tenia que hacerse debido al
cambio"*

Decomposed into the four guarantees it names, which are the only four this feature addresses:

| # | Guarantee | Phrase it comes from | Owned by |
|---|---|---|---|
| (a) | every required item was done | *"TODO lo que tenia que hacer se hizo"* | existing: the ODD checklist + `receipt-check` shape |
| (b) | nothing else broke | *"no rompio nada en paralelo"* | existing: suites, `rig/check.sh` |
| (c) | dependencies the change implied were updated | *"arreglo o actualizo las dependencias que implicaban por ese cambio"* | **T6 — nothing in any repo enumerates these today** |
| (d) | what the change made necessary was fixed or improved | *"arreglo o mejoro lo que tenia que hacerse debido al cambio"* | **T6 — same gap** |

**S2 — the number is split, decided 2026-10-14.** 99.9% is claimed over *mechanically enumerable
derived obligations* only. Requirements misread and false prose claims go to a second reviewer, not to
a gate. Chosen over a global 99.9% oracle, and over measuring the ceiling first without a target.

**S3 — one build location, decided 2026-10-14.** Everything lands in this repository. The stream
(`agent-harness`, project repos) emits receipts; this repo derives, reports and promotes to `theory/`.
The producer of the work never grades its own work.

**S4 — four pieces selected, decided 2026-10-14, all selected, none deferred.** Graduate the runs that
already exist and close the timeout placeholders (T4, T5); land the server-side layer ADR 0014 decided
and never built (T3); build the obligation ledger (T6); run a gap analysis on a public Callstack RN
repo (T7). **Amended 2026-10-14 by T7's own result:** the clause originally attached to T7 — *"to take
verifier-availability from one occurrence to two"* — was a premise, not a requirement, and it was false
twice over. Check 6's `partial` demand sat at **one** occurrence across `0001`–`0003`, not one each, and
T7 added **zero**, because the target failed the independence test (`gaps/0004`). What S4 asked for was
the analysis; the occurrence was a hoped-for by-product. Recorded here so the selection is quoted
accurately, not upgraded after the fact.

**S5 — the standing instruction about this repo.** *"no lo expandás con más teoría"* and *"fusionalo al
stream, donde cada pieza nueva nace con su gate y su experimento"*. Accepted for the work; **not**
accepted for the grading — see S3. Consequence: no new `theory/` file is written by this feature except
as the promotion of a measured number, per ADR 0011.

**S6 — fixture, not repository, for new mini-projects.** *"Agregás un fixture con los botones, no un
repo nuevo por tema."* Anything new that imitates a project lands under `rig/fixtures/<name>/v<n>/`,
hash-frozen by `MANIFEST.sha256`, additively versioned.

**S7 — the material outside this project.** The operator pointed at a folder of Callstack OSS clones
outside this repository. The words used named a machine-local directory, elided here as `<home>/…/<forks
workspace>`, because ADR 0009 forbids a home-directory path in any committed file *including inside a
quotation*, and `hooks/pre-commit` matches only `(/Users|/home)/…` — a relative fragment passes it. The
material enters **only through `gaps/`**. Naming follows this repo's own rule, not an operator statement:
`gaps/README.md` licenses naming a **public** open-source repository ("public means the practice being
analysed is already published"), and `gaps/0002` is the precedent — `Expensify/App`, named, with its URL
in `sources`. Verified 2026-10-14 against the GitHub API rather than inferred from a folder name:
`callstackincubator/repack-atlas` resolves with `private: false`; a sibling lookup at a guessed org
returned no record and is named nowhere in this feature. Never a path outside this repo, in any file.

**S8 — every gate proves it fires.** A check that cannot fail is not a check. Each gate added or
changed by this feature carries a planted violation in its own `--self-test` that asserts non-zero
exit, and distinguishes "could not run" (exit 2) from "passed" (exit 0). Already the repo's rule
(ADR 0013, ADR 0014's non-negotiable properties); named as a spec here because the two most expensive
local incidents in the operator's own incident log are exactly a check reporting green without testing
what it claims.

## Test seams (confirmed 2026-10-14)

| Seam | What it proves | Prior art |
|---|---|---|
| `./open-work.sh --self-test` exit code per case | a new enumeration source reports what it sees, and reports `absent` when the directory is gone | its own `self_test()` (was `open-work.sh:401`; my T2 edit moved it to 498 — see L11); asserts printed output, not only exit code |
| `./check.sh --self-test` | a planted frontmatter violation is reported, one invariant at a time | `check.sh` self-test, the shape S8 generalises |
| `./hooks/pre-commit --all` / `--self-test` | a planted leak fails the gate; a missing pattern list exits 2 | `hooks/pre-commit:142` builds a throwaway repo and asserts the fail |
| `bash -n` / `python3 -m py_compile` | syntax gate for a file whose behaviour costs a real run to reach | `OPERATIONS.md` decision table |
| `rig/check.sh` | seconds-long: manifests, composed `--self-test`s, byte-identical re-derive | added by the failure-flood cycle for this exact purpose |
| `rig/run-pipeline.sh --self-test` | the pipeline runner's extractable functions, runnable without a model call | its own dispatch, `--self-test) SELF_TEST=1` |
| `python3 rig/report.py --experiment <name>` | the aggregate table a cell's verdict is read from | the table `hypotheses/0001`'s Result section was written from |

No new seam is created by this feature. Every task is exercised through one of the seven above.

## Tasks

Ordered by dependency, not by discovery. Work the frontier: any task whose blockers are done.

- [x] **T1 Write this document, and give the new `odd/` directory its pointer in `MAP.md`**
  - Blocked by: None
  - Seams: `./check.sh` (the file must satisfy the frontmatter schema it inherits)
  - Evidence: **this file cannot carry its own commit hash**, so its hash is recorded by the next
    commit in the Progress table below — the same self-reference `run-input-provenance` exists to make
    visible, met on the first document this feature wrote. Checks: `./check.sh` exit 0,
    `./check.sh --self-test` exit 0, `./hooks/pre-commit --all` exit 0, all run from this worktree
    because the hook does not fire here (see Log L4). `type: journal` chosen deliberately: `check.sh:132`
    holds a closed enum and adding a type means editing `AGENTS.md` and `check.sh` in the same commit —
    a schema change, not a doc task.
  - Not done by T1: `open-work.sh` cannot see `odd/`. That gap is T2, and it is Log L5.

- [x] **T2 Make the generated index of open work see `odd/tasks/` — RED first**
  - Blocked by: T1
  - Seams: `./open-work.sh --self-test`
  - RED observed before any edit: with this document present and no new source, the index printed
    *15 item(s) across 6 source(s)* and zero mentions of `odd/`. Reproduced, not hypothetical.
  - Closure rule decided and stated in the executable's header, as this task required: **open while one
    `- [ ]` remains**; closed when every box is ticked; a document with **no checkbox at all is
    UNDECIDABLE and is still listed**. The reason for the third state is this repo's own rule — "absent
    is not empty", one level down. Absence of evidence of completion is not completion, and a checklist
    nobody wrote is precisely the case to surface rather than to skip.
  - Cases added first (5), then verified by deletion: with the section removed the suite reports **12
    FAIL and exit 1**, so the cases test the behaviour and not each other.
  - Evidence: `./open-work.sh --self-test` 0 restored / 1 mutant; `sh -n` 0; `./check.sh` 0 over 117
    content files; `./hooks/pre-commit --all` 0 over 195 tracked files; the index now prints *16 items
    across 7 source(s)* and names this document with its unchecked-task count (**5**, at this commit —
    see L8, that figure is derived from this document's own checkboxes and rots one tick later).
  - Derived obligations this change created, discharged in the same commit: `MAP.md` (row + how-to-query
    line + correction), `OPERATIONS.md` (source list and the closure rule), `decisions/0016` (amendment:
    its count, its table, its "five of the six" claim, and its predicted-but-unmitigated seventh
    source), and this document. `journal/2026-08-19` also says "six sources" and was **not** edited — a
    dated record is provenance, not a pointer to maintain.

- [x] **T3 Land the server-side layer: one workflow, four jobs, each pairing its self-test with the
  check it guards**
  - Blocked by: T2 (so the workflow can run T2's executable, and so `odd/` is visible to what it reports)
  - Seams: `hooks/pre-commit --self-test`, `hooks/commit-msg --range`, `check.sh --self-test`,
    `open-work.sh --self-test`, plus a planted-violation commit on a throwaway branch proving a job
    goes red (S8)
  - `ADR 0014` states this was *"written and verified locally — three jobs, each pairing its self-test
    with the check it guards, a range step handling an all-zeros or unreachable `before` by scanning
    full history loudly rather than scanning nothing, and every event value passed through the
    environment so none of it is parsed as shell. It is not committed."* It is not in this checkout's
    history: `git ls-tree -r origin/main` has no `.github/`. Recovering it (reflog, a worktree, a
    stash) is the first step; rewriting it is the fallback, and if rewritten, that is recorded rather
    than presented as recovery.
  - Ratifying ADR 0014 to `validated` is **the operator's act, not this task's**. T3 changes
    *Implementation status*, and says the token-scope objection is now moot because the operator
    selected this work knowing it.
  - Push, branch protection and required status checks stay the operator's — ADR 0014 is explicit that
    protection is a web-UI setting no committed file can ship.
  - **Recovered, not rewritten.** Found by searching the object database before writing anything:
    dangling commit `fcaae282` (2026-08-17) holds `.github/workflows/verify.yml`, 134 lines, and the
    working-tree file is **byte-identical** to it — blob `2fc49e6521803d1fb91143b5c5abe84893d7695d` on
    both sides. A `git commit` on a branch that never became a ref leaves the object reachable only by
    `git fsck --lost-found`, so "decided and never built" was wrong in the direction of *already built*.
    The search that found it is recorded in ADR 0014 as one command.
  - **Four jobs, not three.** The task named three because ADR 0014's draft had three. Two committed
    executables post-date that draft — `./setup.sh --self-test` and `./open-work.sh`, which did not exist
    on 2026-08-17 — and ADR 0014's own non-negotiable list already requires CI to run every committed
    executable's own test. The fourth job applies the decision; it adds none. Its one non-self-test step
    runs `./open-work.sh` and accepts **only exit 0**, because exit 2 means *could not run* (forbidden as
    a pass) while exit 0 proves nothing about content — the step must never fail a push for holding open
    work. Verified rather than asserted: an index exiting 2 fails the step with **and** without `bash -e`.
  - Evidence: `actionlint` 1.7.12 exit 0 on the file, **and it fires** — a broken mapping and an unquoted
    variable each exit 1 (SC2086), so exit 0 here is a result and not a silence; `shellcheck` 0.11.0 was
    present, which is the precondition for `actionlint` to have read the inline shell at all.
    Independently verified the dependency pin: tag `v7.0.1` resolves to `3d3c42e5…`, commit message
    "prep v7.0.1 release (#2531)", 2026-07-17 — the pin names a real release, not a mutable tag.
    Command-level mutants for the jobs: `./hooks/pre-commit --all` with a planted home-path in a tracked
    file → **exit 1**; `./check.sh` with a planted `type: thoery` → **exit 1**, naming file and field;
    `commit-msg --range` over a leaky message is asserted by the hook's own suite (`hooks/commit-msg:299`).
    `git check-ignore` exit 1 → the workflow is not ignored, and `setup.sh` ignores the narrow path
    `/.github/copilot-instructions.md`, not the directory, so `--copilot` cannot hide this file.
  - **What is NOT proven, stated as the gap it is.** S8 asked for a planted-violation *push* proving a
    job goes red on the server. Not done: pushing is the operator's decision, so the end-to-end claim
    "this workflow turns red on GitHub" is **unverified**, and command-level mutants are the strongest
    available substitute. The repository's Actions API returns `total_count: 0` as measured today
    (`gh api repos/<owner>/<repo>/actions/workflows`) — the workflow is committed and has never run.
    "Committed" and "running" are written apart in every file this task touched, for that reason.

- [x] **T4 Measure the two timeout placeholders and replace them with measured values**
  - Blocked by: None (parallel with T2, disjoint files: `rig/run-pipeline.sh` only)
  - Seams: `rig/check.sh`, `rig/run-pipeline.sh --self-test`
  - Held `STEP_TIMEOUT_S=180` and `SUITE_TIMEOUT_S=150`, marked *"PLACEHOLDERS pending task 5.7's real
    wall-clock measurement"*. The archive-report called them *"undone configuration with no stated
    trigger"* — there was no blocker, nobody ran the measurement. Now **390 / 120**.
  - The measurement is the fixture suite's wall clock under the pinned runtime, taken N times, not a
    guess with margin. Recorded: 3 amplified samples (1252, 1258, 1719 ms over 2,882 tests / 6 suites),
    1 unamplified (889 ms), plus the four committed model-step walls the script's own rows carry
    (101475, 89539, 88486, 120207 ms). Derivation is `rig/run.sh`'s existing rule, unchanged.
  - Invariant kept and mutant-proved: suite timeout strictly smaller than step timeout, or exit 2.
    `STEP=100 / SUITE=150` exits 2 naming design.md 9b.
  - **One of the two values is not measurement-backed and the file says so**: a *clean*-fixture wall is
    unobtainable from this tree — committed `failure-flood/v2/src/` IS the injected substrate, so the
    clean baseline exists only as the `C` block in `answer-key/s2.json`, never as runnable source. Every
    candidate basis lands under the 120 s floor, so `SUITE_TIMEOUT_S` is set **by the floor**. Re-derive
    if a clean wall is ever committed; do not nudge it.
  - Derived obligations this change created, all discharged in the same commit: the **7** live `path:line`
    citations into `rig/run-pipeline.sh` that existed at `a5f81c4` and which the edit invalidated
    (`hypotheses/0002` ×4, `MAP.md`'s `sdd/` row, this document's seams table and its own T4 body), the
    claim that the values are still placeholders (`MAP.md`), and the hand-stated closed-task count in
    `MAP.md`'s `odd/` row that T4 closing made stale. See L11 — 49 of the drift lines are mine, the rest
    predates this session, and one citation was wrong the day it was written.

- [ ] **T5 Found the first countable run: `failure-flood` stage 2, both arms, N=5 per cell**
  - Blocked by: ~~T4~~ closed 2026-10-14. Both archives named the timeout placeholders as *the* concrete
    prerequisite for a countable run; with T4 done, the only thing left is the operator's decision to
    fund the spend. Nothing in the rig is configured-by-placeholder any more.
  - Seams: `rig/run-pipeline.sh`, `python3 rig/derive.py`, `python3 rig/report.py --experiment failure-flood-v1`
  - This is the only task here that spends real model credit and needs the `claude` CLI. `s2` exists in
    the fixture (`failure-flood/v2`) and `hypotheses/0002`/`0003` are both **registered and open,
    written before any `s2` run existed** — so the verdict is decidable, not a choice made after seeing
    the number.
  - Report per `(task_id, arm)`, never blended, per the R-F5.4/R-F4.1 discipline the reporter already
    enforces. Report the void rows by name.
  - R-F7.2: a cell whose five runs all land in the same green-restore state escalates N. Escalation is
    reported as escalation, not quietly absorbed.

- [ ] **T6 The obligation ledger: enumerate what a change derived, from structure, not from prose**
  - Blocked by: T2 — reuse its enumeration machinery and its header rules; do not write a second
    enumerator
  - Seams: a new committed executable's own `--self-test` (shape fixed by ADR 0013), plus a planted
    violation per obligation class (S8)
  - Attacks (c) and (d) of S1 — the two guarantees nothing in any of the operator's repos enumerates.
    Derived obligation classes to enumerate, each from a fact on disk: lockfile stale against its
    manifest; committed generated artifact older than its source; a doc or spec that cites a changed
    path; a caller of a changed symbol. Each class either resolves or names itself as undecidable —
    `absent` is never `empty` (ADR 0016), and "cannot decide" is never "satisfied".
  - Scope it to one repository and one language first (this repo, shell and Python; or the fixture).
    The `gaps/0002` lesson binds: extract the shape from an example that already works, do not design
    from the complaint. `gaps/0004` is the working prior art, and T7 is what records it: the agent-sync
    check (`scripts/agent-sync.mjs`, drift fails CI with exit 1) and the commit-range/commit-title checks
    that its pull-request runners take. **Corrected 2026-10-14:** this row first cited
    `npm run agent:check` and `npm run check:commits`, which appear **nowhere in the committed record** —
    they came from the working report, which by design does not cross into this repo. A citation that
    resolves only on the author's machine is the off-by-one-at-birth class from L11, one level up: it
    named real things and pointed at nothing a reader can open.

- [x] **T7 `gaps/0004` — gap analysis of a public Callstack RN repo, via `skills/project-gap-analysis`**
  - Blocked by: None (read-only, disjoint surface; it can run any time and feeds T6, not the reverse)
  - Seams: the skill's own checklist, and `./check.sh` on the record it writes
  - **The premise this task was registered on was false, and it was false in two independent ways.** As
    written this task said check 6 was `partial` *"at one occurrence across `0001`/`0002`/`0003`"* and that
    *"a second occurrence is what licenses the first `blocks/` entry"*. Measured from the records: `0001`
    scored check 6 `absent` (demand at 1), `0002` scored it `partial` and states in its own Demand table
    *"1 — `0001` only"* — i.e. it declined to advance it — and `0003` calls it ***"First"* as a `partial`**.
    So the demand sat at **one** occurrence, and T7 was to be the second. What actually happened is the
    finding: the target failed `gaps/README.md`'s independence test, so **T7 adds zero occurrences** and
    check 6 is still at one. The task's hoped-for output was never a requirement of S4; S4 asked for the
    analysis. See S4's amendment.
  - Target chosen for a specific reason: `callstackincubator/repack-atlas` — public, `private: false`
    verified 2026-10-14, named under the `gaps/README.md` exception S7 records — already ships an
    agent-sync drift check and commit-range/commit-title gates. **Its value turned out to be the opposite
    of what was expected.** It is the operator's own repository: 142 commits under two identities that are
    both the operator's, and its own design document lists this operator's tooling — and `0003`'s project
    — as borrowed sources. So it is a **dependent** observation: worked patterns and a transfer test, not
    demand. Five of seven checks came out at or above what the backing docs ask for, which is the
    strongest evidence in this repo that these practices *transfer*, and recording that as a demand would
    have been the error.
  - The two findings that outlive the record: **check 4 `absent` would have been its fourth occurrence and
    is not counted** (fourth appearance, zero occurrences), and **check 6's `partial` here arrived for a
    reason no earlier record had** — `scripts/agent-sync.mjs` parses no flags, so a one-character typo in
    `--check` falls through to *repair* mode. Measured on a drifted tree: correct flag → exit 1; typo →
    recreated the deleted symlink, printed "5 skills in sync", exit 0, and the real check afterwards then
    exited 0. **Zero swallow shapes in `.github/` and `scripts/`**, which is exactly why a pattern scan —
    the method runs 1–3 used, and the right method for defects that leave a mark — would have reported
    `present`. Found only by running the gate in three states.
  - **Our own gate does the same thing, and it is now measured:** `./hooks/commit-msg --range HEAD HEAD`
    prints "clean across 0 commit message(s)" and **exits 0**. A range naming zero commits is
    *could-not-run*; we report a pass. Same class, in this repo, on the gate that audits this task's own
    commits.
  - Naming is licensed by S7 and by the exception `gaps/README.md` records; the redaction gate is run
    by hand from this worktree regardless, because a clean gate is not evidence about the half it
    cannot pattern-match.

- [x] **T8 `rig/run.sh`'s `TIMEOUT_S`: the value was right, the comment's range was wrong at birth**
  - Blocked by: None (found while measuring for T4; not T4's surface — its task text scoped T4 to
    `rig/run-pipeline.sh` only, for disjointness with T2, and one commit must not move two
    independently-derived bounds on two different scripts)
  - Seams: `bash -n rig/run.sh`, `rig/check.sh`. **Weaker than it looks**: `rig/run.sh` has no
    `--self-test`, so nothing asserts this bound — the value is read, never checked. That is T9's subject.
  - **The premise this task was registered on was false, and my own note repeated it for two turns.**
    As first written this task said the file's own rule "yields 180" and its 14.586 s basis was
    "superseded". Both wrong. The rule names its population — `sdd/measurement-rig/tasks.md:242`:
    *"Slowest of the six deliberate pilot runs is 14.586s (`t3-scoped-03`)"*. Those six
    (`t3-broad-{01,02,03}`, `t3-scoped-{01,02,03}`) do max at **14586 ms**, verified from the raw
    captures. So `120 = max(120, ceil(3×14.586/30)×30)` is a **correct** application of the rule to the
    population the rule names. 180 came from applying the same rule to all 42 rows — a different
    population, and the doc never makes that reading.
  - What *is* false is the range in the same comment: *"Observed walls across the pilot were 11-52s"*.
    The pilot is **11.0-14.6 s**. 11-52 s is the whole 42-row table — and at `134dbe8`, the commit that
    wrote the sentence, that table **already held 42 rows, 27 of them `t3v2`** (`git show` verified).
    Off by population at birth: the third instance of the class in one session, after `0002:38`'s
    off-by-one and the `11-52s` range itself.
  - "Nothing has ever timed out" was also weaker than it read — true and checkable (**0** rows carry
    `void_reason=timeout`; all 42 raw captures record `timed_out=false`, `exit_code=0`), but **every one
    of the 42 ran with `timeout_s: 300`**. The 120 bound has never been exercised by a single run.
  - Decision taken with the operator: **leave 120, correct the prose.** `run.sh` drives
    `tool-surface-v1` only (`task_id t1|t2|t3|t3v2`), `hypotheses/0001` is closed, T5's `s2` runs through
    `run-pipeline.sh` — so raising the bound would calibrate for a run nobody has funded. The comment now
    names the trigger instead: a future t3v2-class run re-derives first, where 51.778 s → 3× → **180**,
    and 120 would sit at **2.32x** rather than the 3× `design.md` §5 calls "the point". The slowest wall
    ever recorded is **43%** of the 120 bound.

- [x] **T9 Run the rig executables' own self-tests in CI — ADR 0014's rule, applied to the two it missed**
  - Blocked by: None. Not blocked by T8 (different file, different defect, no shared line).
  - Seams: `actionlint` with `shellcheck` present (the shape T3 established: exit 0 on the file, exit 1 on
    each planted mutant — S8 binds, so a mutant is required, not optional)
  - Measured from `git ls-files -s`, excluding `rig/fixtures/`: **8** committed executables (mode 100755),
    **7** implement a `--self-test` dispatch (`rig/run.sh` does not), and `.github/workflows/verify.yml`
    runs **5** of them — no `rig/*` path appears in the workflow at all. The 2 uncovered: `rig/check.sh
    --self-test`, `rig/run-pipeline.sh --self-test`.
  - Warrant is ADR 0014's non-negotiable list, not a new idea; its Implementation section already applied
    the same rule to `setup.sh` and `open-work.sh` for post-dating the draft. See L12 for the disposition
    that binds here — this must **not** be filed as a restatement of the archived SUGGESTION-1.
  - **Question 1, settled: no — and the modules are covered on a different warrant anyway.** The three
    `.py` files are mode `100644`, so ADR 0014's word "executable" does not reach them (measured: the
    six-file mode listing). They are in the job on ADR 0013 plus a fact about this workflow: CI ran them
    **nowhere**, because the only thing that composes their `--self-test` is `check_component_self_test()`
    inside `rig/check.sh`'s **real gate** — which is the forbidden one. So excluding them on a technicality
    would have shipped a job that looks complete and still never tests the three most-edited rig files.
    Naming the warrant separately matters: this does not quietly widen "executable", which later readers
    rely on for the 8/7/5 counts above.
  - **Question 2, settled: the bash arm cannot fix this, and the spec's framing was wrong.** Not a choice
    between two designs — one of them does not work. `rig/check.sh` dispatches `--self-test) self_test;
    exit $?`, and the three `check_component_self_test` calls sit at 507-509, **below** that exit. Adding a
    bash arm there changes nothing CI can reach, because CI cannot run the real gate. Verified by
    instrumenting `python3` on `PATH` to log every invocation during `rig/check.sh --self-test`: five
    synthetic-fixture heredocs, **zero** `--self-test` calls. Own CI step, therefore — and a *job*, not
    steps appended to `executables`, which is ADR 0014's own stated reason (sequential checks in one job
    let a failing early step skip the rest, so the log reports less than was checked).
  - **The design choice the task did not name, made deliberately: discovery, not a list.** Targets come
    from the index — mode `100755` under `rig/`, plus tracked `rig/*.py`, both excluding `rig/fixtures/`
    (the same exclusion `check.sh` and `open-work.sh` already apply to frozen measurement inputs). The
    defect being fixed *is* a hardcoded list that rotted while the repo grew, so a file written with the
    two names in it reintroduces the failure class at the moment it closes the instance. Zero discovered
    exits 2; discovered-but-none-carries-the-flag exits 2; a path with no `--self-test` is named as
    untested rather than skipped in silence (`absent` is not `covered`).
  - **Evidence (S8: four mutants fired, two guards held).** `actionlint` 1.7.12 exit 0 with `shellcheck`
    0.11.0 present, and it **caught real dead code** in the first draft (`SC2329`, a helper I left
    uncalled) — the linter was demonstrably capable of failing before its silence meant anything, per L10.
    Both inline `run:` blocks then `shellcheck` clean. Step executed in a real clone (`has .git`, no
    `rig/runs/`). Counted honestly rather than rounded up: **four planted mutants, each observed to make
    the step non-zero**, plus **two guards that hold on the happy path** and a baseline control. A first
    draft of this line said "six mutants, each observed to fire", which is false — two of the six did not
    fire, because they are not mutants; they are the positive checks that discovery and `set -u` behave.

    | # | Intervention | Observed | Kind |
    |---|---|---|---|
    | — | none (as-is) | exit 0, **5 self-tests ran** | control |
    | 1 | `classify_manifest` expectation inverted in `rig/check.sh` | **exit 1**, other four still ran | mutant, fired |
    | 2 | new mode-`100755` `rig/newtool.sh` committed | **6 ran**, picked up with no workflow edit | guard: discovery |
    | 3 | same file, own `--self-test` exits 1 | **exit 1** naming it | mutant, fired |
    | 4 | discovery pathspec pointed at nothing | **exit 2**, "refusing to report a pass for having tested nothing" | mutant, fired |
    | 5 | six paths found, none carrying the flag | **exit 2**, "this job ran nothing" | mutant, fired |
    | 6 | `untested` array empty under `set -u` | **exit 0**, no unbound-variable crash | guard: `set -u` |

    Row 1 is the S8 property that matters most here: the failing test did **not** stop the other four, so
    one red instrument cannot hide the state of the rest. Hermeticity re-measured in that clone, not
    inherited from L11's archive: all five self-tests in **1.74 s**, both goldens stay at **3 and 42
    lines**, `git status` empty afterwards. Both rig self-tests **exit 2 naming `python3`** when `PATH`
    lacks it (measured), so a missing interpreter lands as could-not-run, never as a pass — the property
    the workflow header claims. Discovery verified at the CI's real depth in a genuine `--depth 1` clone
    over `file://` (a local clone silently ignores `--depth`, which is what made an earlier run of this
    check worthless): same 3 executables, same 3 modules.
  - **Derived obligations created by this change, all discharged in the same commit:** `MAP.md`'s `.github/`
    row claimed "4 jobs, each pairing its self-test with the check it guards" — both halves went stale, and
    the second is now *deliberately* violated by one row, so the row states the exception rather than a
    count (a count there is exactly the hand-stated figure L11 says to delete, not update);
    `OPERATIONS.md`'s CI job table (new row) and its "Each self-test runs in the same job as the check it
    guards" paragraph (needed the exception named); `rig/README.md`'s live claim that
    `run-pipeline.sh --self-test` "must still be run by hand" — **false as of this commit**, corrected to
    say the composition gap inside the gate is unchanged while CI coverage is new, which is the
    distinction SUGGESTION-1's disposition turns on; `decisions/0014` Implementation status. No `path:line`
    citation into any file this change edits (`hypotheses/0002`'s four cites point into
    `rig/run-pipeline.sh`, which T9 does not touch), verified by grep before editing rather than after.
  - Forbidden by evidence, and respected: `rig/check.sh`'s real gate is **not** in CI. A clean checkout has
    no gitignored `rig/runs/`, and there it fails 5/18 **and truncates both committed goldens to zero
    bytes** (L11). Only `--self-test` dispatches run here; the job's comment says so in the file, because
    the tempting "improvement" is to add the real gate and every signal would then go green.


## Explicitly not in this feature

| Not here | Why |
|---|---|
| A new `theory/` file | S5. A number is citable only by promotion with scope, N and spread (ADR 0011), and no number exists yet beyond the one already promoted into `capability-load-cost.md`. |
| Graduating `tool-surface-v1` again | Its hypothesis is **already closed** — see L3. The `t3v2` rows were graded on 2026-08-10 and produced `hypotheses/0001`'s null plus the ≈224-token-per-entry figure. Nothing left to graduate. |
| Enabling branch protection or required status checks | A repository setting in a web UI. ADR 0014 says plainly no committed file ships it and nobody has enabled it. |
| Ratifying ADR 0014 or ADR 0016 to `validated` | The operator's act, stated in both files. This feature may change their Implementation status, not their status field. |
| A `tests/` directory or a test runner | Refused by ADR 0013, unchanged. Each executable carries its own `--self-test`. |
| Turning the 99.9% into a global oracle | S2. The operator split it deliberately; a requirement misread is not a gate's subject. |
| Pushing, opening PRs, merging | The operator's decision, always. T1–T7 land as work-unit commits on `ci/public-gate`. |

## Checks

Run from this worktree, in this order, after any task. The hook does **not** fire here (L4), so every
gate below is invoked by hand and its exit code is read.

| Check | Command | Expected |
|---|---|---|
| Syntax | `bash -n` / `sh -n` on every touched shell file | 0 |
| Python syntax | `python3 -m py_compile` on every touched `.py` | 0 |
| Self-tests | `./check.sh --self-test`, `./open-work.sh --self-test`, `./hooks/pre-commit --self-test`, `./hooks/commit-msg --self-test` | 0 each |
| Structural | `./check.sh` | 0 |
| Redaction, whole tree | `./hooks/pre-commit --all` | 0. **Scans `git ls-files` only**, so a brand-new file is invisible to it until it is tracked or `git add -N`'d — found the hard way on T7, whose whole subject was one untracked file. Run it once before adding and once after (`git add -N <new files>`), and plant a mutant *in the new file* to prove the gate can fail on content no prior run ever saw |
| Redaction, messages | `./hooks/commit-msg --range - HEAD` | 0. `-` means no lower bound (every reachable commit). **Never `<same> <same>`**: a zero-commit range prints "clean across 0 commit message(s)" and exits 0 — measured, and the vacuous-pass class `gaps/0004` was written about. The count printed must be non-zero or the step scanned nothing |
| Rig integrity | `rig/check.sh` | 0, and `git diff -- rig/` empty after the byte-identical re-derive. **Copy `rig/runs/` in from the primary checkout first** — it is gitignored, so a worktree has none, and with none this gate truncates both committed `rig/results/*/runs.jsonl` to zero lines and then reports green against the wipe (L11) |
| Index honesty | `./open-work.sh` | reads its COVERAGE block; `absent` distinguished from `0` |

## Progress and evidence

| Task | Outcome | Commit | Check observed |
|---|---|---|---|
| T1 | done | `2839cd6` | `./check.sh` 0 over the tree; `./check.sh --self-test` 0; `./hooks/pre-commit --all` 0; `./open-work.sh` printed 6 sources and did **not** list this document — T2's red reproduced before T2 was written |
| T2 | done | `4ad47d7` (recorded by T4 — the self-reference note below resolves for every task but the one writing it) | `./open-work.sh --self-test` 0; **12 FAIL + exit 1** with the new section deleted (deletion-mutant, recount without truncation); `sh -n` 0; `./check.sh` 0; `./hooks/pre-commit --all` 0; index prints 16 items across 7 sources. **One derived obligation this task created went undischarged and was found later:** its own seams-table cite `open-work.sh:401` was moved to 498 by this very commit — the commit that documented why cites break moved one. Repaired at T4, L11. |
| T3 | done, **not yet running** | `a5f81c4` (recorded by T4) | `actionlint` 1.7.12 exit 0, exit 1 on both planted mutants (broken mapping; unquoted var → SC2086) with `shellcheck` 0.11.0 present; recovered file byte-identical to blob `2fc49e65…`; `git check-ignore` exit 1; mutants of the job commands: `pre-commit --all` 1 with a planted path, `check.sh` 1 with a planted `type:`; `gh api …/actions/workflows` → `total_count: 0` |
| T4 | done | `97d45eb` (recorded by T8 — the first task whose hash became knowable at the *next* commit, which is the shape of the self-reference note, not a gap) | `rig/check.sh` **20/20** with `rig/runs/` copied in, both `rig/results/*/runs.jsonl` byte-intact after (`git diff -- rig/results/` empty); `bash -n` 0; invariant mutant `STEP=100/SUITE=150` → exit 2; `./check.sh` 0 over 117 content files; amplified suite measured 3× (1252/1258/1719 ms, 2,882 tests, 499 failed / 2,383 passed — matching `answer-key/s2.json`'s F0 exactly, which is what proves the sandbox replicated the route); `report_bytes` 2,790,891 vs `DEFAULT_MAX_REPORT_BYTES` 64 MiB = 24.0x. **Post-commit proof:** with `hypotheses/0002` clean at `97d45eb`, `rig/check.sh` returned to **20/20, exit 0** and both goldens stayed at 3 and 42 lines — the Hard Ordering Gate's refusal was the dirty-tree precondition, not a regression | `rig/check.sh` **20/20** with `rig/runs/` copied in, both `rig/results/*/runs.jsonl` byte-intact after (`git diff -- rig/results/` empty); `bash -n` 0; invariant mutant `STEP=100/SUITE=150` → exit 2; `./check.sh` 0 over 117 content files; amplified suite measured 3× (1252/1258/1719 ms, 2,882 tests, 499 failed / 2,383 passed — matching `answer-key/s2.json`'s F0 exactly, which is what proves the sandbox replicated the route); `report_bytes` 2,790,891 vs `DEFAULT_MAX_REPORT_BYTES` 64 MiB = 24.0x |
| T8 | done, **value unchanged** | `bcb37eb`. **Recorded late by two, measured rather than reasoned.** Its hash was knowable the moment `bcb37eb` itself landed, so the first commit that could carry it was its child `439abbc` (`git rev-parse 439abbc^` = `bcb37eb`) — chance #1, which named it zero times; `1a1fd8e` is chance #2, also zero mentions; this commit is chance #3. A first draft of this cell said "late by one" — a count written from the feel of the sequence instead of from `git show <rev> | grep -c bcb37eb`, which is the same failure L11 and L14 record, arriving again in a sentence about counts. The self-reference note explains why a cell cannot carry its own hash; it does not excuse skipping the next commit, and `439abbc` had both the hash and the free-text space to write | `bash -n rig/run.sh` 0; all eight numbers in the corrected comment re-verified against committed data (pilot six 10990-14586 ms; all-42 10990-51778 ms; 0 rows `void_reason=timeout`; 42 raw captures `timed_out=false` all under `timeout_s=300`; 51778/120000 = 43%; 120/51.778 = 2.32x; ceil(3×51.778/30)×30 = 180; the table already held 42 rows / 27 `t3v2` at `134dbe8`, checked with `git show`). The fix is prose: **`TIMEOUT_S` stays 120**, which is the rule applied to the population the rule names. `rig/check.sh` 20/20, goldens intact. |
| T9 | done | `439abbc` — knowable only once `1a1fd8e` existed, so this is the first commit that could carry it: on time. **Its evidence figures belong to `bcb37eb`, not to it.** 117 content files, 196 tracked files and 149 messages are values in the tree the battery actually ran against — `439abbc`'s parent — because a task measures the tree *before* its own commit lands, never the commit that records it. The message count is what proves this: `git rev-list --count` gives 149 at `bcb37eb`, 150 at `439abbc`, 151 at `1a1fd8e`, so "149" can only be the parent's tree. A first draft of this cell anchored all three to `439abbc` — a false attribution made by reasoning that "the commit that names them" must be "the commit they were measured in", which is the off-by-one-at-birth class from L11 arriving in my own fresh sentence about staleness. All three are counters over reachable repository state and move with any later commit; read them as value-at-`bcb37eb`, never as standing claims, and they are deliberately not chased forward | `actionlint` 1.7.12 **exit 0** with `shellcheck` 0.11.0 present, and **exit 1 on the first draft** (`SC2329`, dead helper) so the pass is a result not a silence; both inline `run:` blocks `shellcheck` clean; step run in a real clone: baseline **exit 0, 5 ran**, four planted mutants **exit 1/1/2/2**, two guards held (new executable auto-discovered → **6 ran**; empty `untested` under `set -u` → **exit 0**); hermetic in a clone with no `rig/runs/` — **1.74 s**, goldens stay **3 and 42**, `git status` empty; both rig self-tests **exit 2 naming `python3`** on a `PATH` without it; discovery confirmed in a genuine `--depth 1` `file://` clone. Full battery after the edit: `check.sh --self-test` 0, `open-work.sh --self-test` 0, `pre-commit --self-test` 0, `commit-msg --self-test` 0, `./check.sh` 0 (117 content files, 5 skills), `pre-commit --all` 0 (196 tracked files), `commit-msg --range - HEAD` 0 (149 messages), `rig/check.sh` **20/20**, `open-work.sh` 0 |
| T7 | done, **and the premise it was registered on was false** | `1a1fd8e` | Battery of 22 gate invocations, each run unpiped with `$?` read on the next line, **all exit 0**: `bash -n` × 8 committed executables, `py_compile` × 5 tracked modules, `check.sh --self-test`, `open-work.sh --self-test`, `pre-commit --self-test`, `commit-msg --self-test`, `./check.sh` (**118** content files, 5 skills), `pre-commit --all`, `commit-msg --range - HEAD` (**150** messages, measured at `439abbc` — that range scans every reachable commit, so this task's own commit necessarily advances the number it was measured against; per L8 it is value-at-`439abbc`, not a standing claim, and is not chased), `rig/check.sh` **20/20**, `open-work.sh` (17 items / 7 sources, `gaps/: 4`). **Two holes closed rather than reported green:** (1) `pre-commit --all` scanned 196 tracked files and *missed this task's entire subject* — `gaps/0004` was untracked — so it was re-run with the file in scope (**197**, exit 0) and **mutant-proved on that file, on both trees it was edited on** — before and after this unit's edits to it: a planted home path → **exit 1** naming `gaps/0004-repack-atlas.md:329` both times, file restored **byte-identical** each time (`sha256 01e5be81…` pre-edit, `1a409691…` on the committed final text); (2) the `--range <same> <same>` vacuous pass reproduced on our own gate, **exit 0 on 0 messages**. Goldens stayed **3 and 42 lines**, `git status --short -- rig/` empty. Spec-premise re-check from the records: `0002`'s own Demand row reads *"1 — `0001` only"* and `0003`'s reads ***"First"***, so check 6 sat at **one** occurrence and T7 added **zero** — see S4's amendment and L14. |
| T5, T6 | not started | — | — |

## Log

**L1 — the operator's request, verbatim (2026-10-14).**
*"quisiera continuar, nose donde estamos, pero otro agente con el que hablaba sobre SDLC le pase esto y
me dijo: 1. build-with-agents: no lo expandás con más teoría […la tabla de fusión con el stream…]
Los proyectos mini ya los tenés: rig/fixtures/failure-flood y tool-surface, con MANIFEST.sha256 y answer
key. Agregás un fixture con los botones, no un repo nuevo por tema., creo que tenemos mas apps para
evaluar, en la carpeta de <home>/…/<forks workspace> hay mucho material, o nose que crees que necesitamos para
mejorar esto porque estamos viendo de crear algo (nose que) que tiene como objetivo, darle un proyecto a
un agente, decirle que haga algo y tener un 99.9% de confianza que TODO lo que tenia que hacer se hizo,
no rompio nada en paralelo, arreglo o actualizo las dependencias que implicaban por ese cambio, arreglo o
mejoro lo que tenia que hacerse debido al cambio, y aca tenemos muchos datos y evidencias que pueden
ayudar a completar eso"*

**L2 — the decision the request turned into (2026-10-14).** Four pieces selected, all of them; build
location is this repository with the stream as evidence source; the 99.9% is split into mechanically
enumerable obligations, the rest to a second reviewer. Recorded as S2/S3/S4 rather than left in chat.

**L3 — a false claim I made and retracted in the same session, recorded because the mechanism is the
finding.** I told the operator *"las 24 filas matched de t3v2 ya están tomadas y nadie las graduó; tu
primer número real sale de graduar lo que ya tenés"*. False for `tool-surface-v1`: `hypotheses/0001` has
a **Result section dated 2026-08-10** — 12/12 versus 12/12, gap *exactly zero* in both partitions,
**not supported**, closed for that task class — and the ≈224 tokens-per-resident-tool-entry figure was
already promoted into `theory/agents/capability-load-cost.md`. The stale reading came from trusting the
summary prose in `MAP.md`/`rig/README.md`/the archive-report, which say *"zero countable runs"* — true of
`failure-flood-v1` (3 rows, all `void`, `void_reason=shakedown`) and false of `tool-surface-v1` (42 rows,
29 `complete`). **Mechanism: this checkout was 63 commits behind `origin/main`, so every conclusion read
from it was silently aged.** The incident line went to the operator's private incident log, not here.
Consequence for this feature's discipline: read a hypothesis's `## Result`/`## Status` before repeating
any claim about whether it is open.

**L4 — checkout isolation, verified rather than assumed (2026-10-14).** `skills/checkout-isolation` is
required before writing. Five worktrees exist on this clone; the branch this session started on
(`sdd/failure-flood-triage-planning`, `2a817e1`) is an ancestor of `origin/main` — fully merged. New
worktree `ci/public-gate` from `origin/main` at `57faaf3`. The gate-resolution check printed
`WRONG TREE — commits here are gated by <original checkout>/hooks/pre-commit`: the skill's predicted
hazard, reproduced on the first attempt, so **no commit in this feature relies on a hook firing** and
every gate above is run explicitly from this tree.

**L5 — the new directory exposes a hole in the repo's own index, before any feature code exists (2026-10-14).**
`./open-work.sh` is *"the generated index of what is open"*, enumerates six sources, and cannot see
`odd/tasks/`. So the first effect of tracking this work is that the index under-reports this repository's
open work while looking complete — ADR 0016's failure class, and `verifier-availability.md`'s last row: a
gate that never was one. This is T2, and it is the feature's cheapest real lesson: **a tracking mechanism
the index cannot see is not a record.** It is also the argument for T6 in one sentence — an obligation
created by an act nobody enumerates is exactly an unmet obligation that reports nothing.
*Closed by T2 the same day; the class of gap it describes is still open and ADR 0016 now says so.*

**L7 — writing T6's justification for it, before T6 exists (2026-10-14).** Doing T2 produced a stream of
derived obligations, and the way they were found is the evidence T6 needs to be built from measurement
rather than from imagination:

| Obligation | How it was found | Was anything watching? |
|---|---|---|
| `MAP.md` said "six structural sources", twice | Grepped the number before editing | No — I happened to grep |
| `OPERATIONS.md` listed the sources by name | Same grep | No |
| `decisions/0016` counted them and claimed a total | Same grep | No |
| `journal/2026-08-19` says "six sources" too | Same grep | No — and correctly **not** changed: a dated record is provenance |
| My own draft of the 0016 amendment summed to **8 over 7 sources** | Added my numbers up, one step before committing | **No.** Nothing would have caught this. |
| My own draft claimed "six of seven inherit a checked input" | Recounted against `check.sh`, which enforces exactly two things | No |
| A header sentence that said "Source 6" and silently pointed at the new source after insertion | Read it after renumbering | No |

Five of seven were caught by a grep I chose to run and six of seven by a check I chose to perform. That
is not a process, it is a habit, and the one that mattered most — the arithmetic — arrived one step
before a commit by accident. S8's premise is that every gate must prove it fires; the honest statement of
where this repository actually stands is that **the highest-value checks in this commit were all
optional and none of them fired.** T6's scope is therefore narrow and specific: not "verify the agent's
work", but *enumerate the places a changed string or count is repeated, and name them when the change
touches one.* That is a grep over a repo with no build step, and it is decidable.

**L8 — a count in the tracking document that the tracking document itself produces went stale in the
same commit that recorded it (2026-10-14).** T2's evidence line said *6 task(s) still unchecked* —
measured while T2 was open, which is exactly when a writer is looking. Ticking `- [x] T2` made it 5. The
first draft of that line also said *15 items*, the RED figure, next to the GREEN one, which is correct as
history and reads as a contradiction unless the two moments are named.

The rule this earns, stated as a rule so it survives the number: **an evidence line may cite a figure
measured during the work, but a figure this document's own state produces must be written as the rule
plus its value at that commit, never as a standing claim.** It is the same property
`sdd/archive/2026-08-27-run-input-provenance` exists to guarantee — a record must carry what it was
measured against — arriving one level down, where what it was measured against is *itself, earlier*.

**L9 — the thing ADR 0014 said was never built had been built, committed, and left in the object
 database for two months (2026-10-14).** T3's own text instructed: recover first, rewrite only as a
fallback. Recovering took one `git fsck --lost-found` loop over dangling commits, because the workflow
was written, committed on a branch that never became a ref, and then abandoned — the blob outlived every
story about it. Three consequences worth more than this task:

1. **A decision file's "it is not committed" is a claim about one branch, not about the object database.**
   The cost of believing it without checking was not a lost afternoon — it was a *second, worse*
   implementation of a gate, written fresh, next to the verified one, with nothing saying which was which.
   Before rewriting anything a decision file says exists-but-wasn't-shipped, search for it.
2. **Byte-identity is what makes "recovered" a true sentence.** Comparing `git rev-parse <obj>:<path>`
   against `git hash-object <path>` costs one command and is the only thing separating recovery from a
   rewrite described as recovery. Without it, "I recovered it" and "I rewrote it the same way" are
   indistinguishable, and only one of them carries the original's verification history.
3. **The ADR's own rule was the source of the extra job, not a new idea.** ADR 0014 lists as
   non-negotiable that CI runs every committed executable's own test; two executables were written after
   the draft, so the file had silently stopped satisfying the decision it implements. A committed gate
   can rot by the *repo growing around it*, which no self-test of the gate would ever report.

**L10 — a limit found while writing about limits (2026-10-14).** `actionlint` exits 0 on a workflow whose
inline shell it never analysed, because `shellcheck` was not installed to begin with. The tool that
verifies a gate is itself subject to `theory/loops/verifier-availability.md`: an absent analyser produces
a clean exit and reports nothing. So "actionlint passed" was not evidence until the analyser's presence
was checked and two mutants were planted to show exit 1. The rule this leaves, which generalises S8
beyond this repo: **verify the verifier is capable of failing before citing its silence as a pass.**

Two findings that outlive T2 and belong to the repository, not to this task:

1. **ADR 0016 predicted this event and its remedy did not fire.** Its consequences table says a seventh
   source appearing later is invisible until someone adds it, and names the COVERAGE block as the
   mitigation. `odd/tasks/` appeared, COVERAGE printed its usual two counts, nothing noticed. What did
   catch it was the author of the new directory asking a question on the day of creation — a question
   that is written nowhere as a gate. Recorded in ADR 0016's amended row.
2. **The correction carried the defect it was correcting.** My amendment to a non-summing total summed
   to 8 over 7, because I classified `odd/tasks/` as both "a directory listing" and "a directory with
   checkboxes". Fixed by disjoint classes: 3 + 1 + 1 + 2 = 7. The general form, which is the one worth
   keeping: a partition counts each item once, and an item that belongs to two descriptions means the
   descriptions are the bug, not the item.

**L11 — closing T4 spent more effort on what the closing broke than on the measurement (2026-10-14).**

The measurement itself was cheap: 8 seconds in a machine-local sandbox, no model credit, and its totals
reproduced the answer key exactly. Everything hard came after, from the +49-line change that recorded it.

Three of the numbers in the first draft of this entry were wrong, and all three were wrong the same way:
I wrote "my 5-line edit", "6 live cites", and "413 lines of drift" from memory of the edit rather than
from a measurement of it. The true values are +54/−5 (net 49), 7, and 424. A fourth — "the ceiling is
right by 23x" in the code comment — was a ratio I asserted without computing. Same session, same failure,
third time stating a derived number before deriving it; the row below is written about one of them and is
not exempt. What caught all four was running the grep and the blob comparison, which is the only check
that has ever worked on this class.

| Finding | Evidence | Where it went |
|---|---|---|
| A gate in this repo truncates the evidence it grades | Running `rig/check.sh` twice in this worktree cut both committed `rig/results/*/runs.jsonl` to **0 lines** (`failure-flood-v1` 3 rows, `tool-surface-v1` 42). Reproduced independently in a clean `git archive`: **5/18 failed and both goldens 0 lines**. Cause is structural: `rig/runs/` is gitignored, a worktree has none, `derive.py` globs zero run dirs and `open("w")` truncates before writing nothing. Restored by `git checkout -- rig/results/`, then the documented workaround: copy `rig/runs` in. | The Checks table above now names the precondition. My CI does **not** invoke `rig/*`, so no CI exposure — verified, not assumed. |
| I did not search memory before running it | Engram obs 370 (2026-09-03) predicts this exactly, workaround included. It was one `mem_search` away and I ran the gate anyway. Second-order version of the trap: the first run reports 4/18, the second reports fewer, because run one already rewrote what run two compares against. | Recorded here rather than only in the private log, because the fix is in a file. |
| My comment asserted a ratio I had not computed | I wrote "the ceiling is right by 23x". There is no ceiling in `run-pipeline.sh` at all; the real one is `DEFAULT_MAX_REPORT_BYTES = 64 MiB` at `collect.py:133`, and the ratio is **24.0x**. Second time in one session I stated a computed number without computing it — the first was calling the committed `wall_ms=1681` impossible. | Corrected in the comment with the constant's name and value. |
| Citation drift: I owned 49 lines of a 424-line move | **7** live `path:line` cites into this file existed at `a5f81c4`. My change is +54/−5, net **+49**, so it shifted every later line by 49 — not the "5-line edit" I first wrote here, and the number of cites was 7, not 6. `run_model_step()` sat at 563 when `0002` was written, 938 at `a5f81c4`, 987 now: of its 424-line total drift, **375 predate this session** (the provenance cycle grew the file, nobody re-anchored). Measured per-symbol against the blobs at `4eddfe9` and `a5f81c4`, not estimated. | Re-anchored to `:733`/`:734`, `:987`, `:1044`. |
| Two citations anchored to prose, not symbols | `MAP.md` cited `:85`, which at `origin/main` was the *comment* saying PLACEHOLDERS — a correct anchor that my edit deleted along with the prose. This document's seams table cited `:103`, the `usage()` text mentioning `--self-test`. Both resolved honestly when written; neither survives a rewrite of unrelated prose. | `MAP.md`'s claim rewritten with no line cite; the seams row now names the dispatch (`--self-test) SELF_TEST=1`) instead of a number. |
| A citation wrong the day it was written | `0002:38` cites `:346` for PIPELINE's `STEPS` array. At `4eddfe9`, line 346 was **MONOLITHIC's** array; PIPELINE's was 347. Not drift — an off-by-one at birth, 375 lines of drift never touched it. | Fixed, and named as a distinct defect: **a drift checker cannot catch this class.** It is T6 evidence, and it argues the ledger must verify a citation *resolves to what it names*, not merely that it has not moved. |
| A hand-stated derived count rotted inside one commit | `MAP.md`'s `odd/` row said "2 of 7 tasks closed"; T4 closing made it 3. This document predicted exactly that at L8 about its *own* checkbox count. | The count is **deleted** from `MAP.md`, not updated — `AGENTS.md`: tables are generated or absent, and `open-work.sh` prints the number. |
| Two ordinals for one source | `MAP.md` called `odd/tasks/` the *seventh* source and, three rows below, *source 6* — both written by me. `open-work.sh`'s own header already records that inserting a source renumbers the others and leaves a sentence that reads fine. I read that warning and wrote the bug into two rows anyway. | Ordinals replaced with names, in prose and in this document. |
| The Hard Ordering Gate refused my own edit, correctly | With `hypotheses/0002` modified, `rig/check.sh` reports **1/20, exit 1**, naming `preflight:v2 -- COULD NOT RUN: tracked_but_dirty` — not a failure and not a pass, which is exactly the distinction ADR 0014 demands. Proved deterministic: reverting that one file to `HEAD` gives **20/20, exit 0**; restoring the edit returns 1/20. Cause is `answer-key/prereg.json`, whose `check` block requires `must_be_clean: true` on the two globs it freezes — *"uncommitted edits to a hypothesis file are not frozen support/refute conditions (ADR 0012)"*. It also fixes `verified: 2026-08-13` as a field: bumping it to the day before the run is the exact move the gate exists to make expensive. | Accepted as correct, and it dictates the shape of this work unit rather than its order: `must_be_clean` reads the **working tree**, so the rig gate cannot go green again until the pointer fix is *committed* — while it sits uncommitted, `preflight:v2` refuses and `rig/check.sh` stays 1/20. Re-running to 20/20 after the commit is the proof. `verified:` stays 2026-08-13. |
| Four numbers in this entry were asserted, not computed | "my 5-line edit" (really +54/−5, net 49), "6 live cites" (7), "413 lines of drift" (424), and "the ceiling is right by 23x" in the code comment (24.0x). All four were cheap to measure and none was measured before being written. | Corrected from `git show`/blob line numbers and `collect.py:133`. The check that worked was the grep, every time. |

Two judgement calls worth stating, because both could have gone the other way:

1. **`hypotheses/0002`'s `verified:` field was left at 2026-08-13.** Bumping it to today would move the
   pre-registration date, and the edit checked four locators, not the claim. The three structural facts
   the hypothesis rests on were re-read and still hold (`case "$ARM"` is top-level, `run_model_step()`
   issues one fresh invocation, `--resume` appears zero times in the file), but re-dating a
   pre-registration to the day before the run is exactly what pre-registration exists to forbid.
2. **I reverted my own `rig/run.sh` fix — and the defect I reverted it for was half false.** I found it
   while measuring and recorded that the file's own rule "then yields 180". Reverting was right: T4's task
   text scopes it to `rig/run-pipeline.sh` only (disjointness with T2), and one commit must not move two
   independently-derived bounds on two different scripts. But *why* I reverted it was wrong — the rule
   names six pilot runs as its population, they do max at 14.586 s, and 120 is correct. I held a false
   premise through two turns of notes and a committed document because I had checked the **maximum**
   (`51.778 s`, real) without checking **which population the rule was allowed to sample**. Re-verified
   at T8 and corrected there. The general form, which is the one worth keeping: before calling a derived
   constant stale, verify the set the rule is defined over, not just the biggest number in the data.

**L12 — two follow-ups that this feature's own ADR says are already decided (2026-10-14).** While
checking whether my new CI job satisfies ADR 0014, I counted committed executables and which of them CI
runs their own test. First count said "5 of 11" and was wrong twice over: I counted the three rig `.py`
files, which are mode `100644` — not executables — and I matched `basename rig/check.sh` against the
`./check.sh --self-test` line, reporting `rig/check.sh` as covered when **no `rig/*` path appears anywhere
in `.github/workflows/verify.yml`**. Measured from `git ls-files -s`, excluding `rig/fixtures/`:

| | count | which |
|---|---|---|
| Committed executables (mode 100755, outside fixtures) | **8** | `check.sh`, `open-work.sh`, `setup.sh`, `hooks/pre-commit`, `hooks/commit-msg`, `rig/check.sh`, `rig/run-pipeline.sh`, `rig/run.sh` |
| Implement a `--self-test` dispatch | **7** | all but `rig/run.sh` — which has none; the string I first matched is help text, and invoking it exits 2 |
| CI runs their own test | **5** | `check.sh`, `open-work.sh`, `setup.sh`, `hooks/pre-commit`, `hooks/commit-msg` |
| **Not run by CI** | **2** | `rig/check.sh --self-test`, `rig/run-pipeline.sh --self-test` — both exist, both exit 0, both hermetic |

ADR 0014's non-negotiable list already says *every committed executable carries its own test and CI runs
it*, and its Implementation section applies that rule to two executables that post-date the draft. The two
rig executables post-date it the same way. So T9 is not a proposal, it is the ADR's own rule applied.

The reason it was skipped is worth keeping, and my first version of it was wrong. The "Does NOT belong
here" prose of `rig/README.md` — a **live, committed** file — already names the gap: `check_component_self_test()` "still has no bash arm, so
`run-pipeline.sh --self-test` is never composed by the repo gate and must still be run by hand." The
archive's disposition of it (SUGGESTION-1) refuses to re-register it: *"Explicitly out of scope by a spec
decision made during this cycle, not a new discovery… Restating it as a fresh backlog entry would
manufacture a trigger this cycle never decided on."* That judgement was correct, and it binds me: I may
not launder it into a new proposal by rediscovering it.

So T9 is not that suggestion restated. It rests on a different warrant: **ADR 0014's non-negotiable list**
says every committed executable carries its own test and CI runs it, and that ADR's Implementation section
already applied the rule to two executables that post-dated the draft. `rig/check.sh` and
`rig/run-pipeline.sh` post-date it the same way. A decision does not need occurrence-weight the way an
observation does — and the ADR itself already required this of the copy of the rule it ships.

What SUGGESTION-1 leaves genuinely unresolved is quoted in its own disposition: `design.md` left open
*"whether the check.sh bash-arm gap is registered here or its own cycle"* **without naming a trigger for
either**. T9 supplies the thing that was missing — a named trigger — rather than repeating the complaint.

The CI job must encode one distinction: **self-test versus gate**. `rig/check.sh`'s real gate cannot go in
CI, because CI checks out a tree with no gitignored `rig/runs/`, and L11 reproduces what that does — 5/18
failed, both committed goldens truncated to zero bytes, verified in a clean `git archive` rather than
inferred. Each executable's own `--self-test` is safe: `rig/run-pipeline.sh` 0.98 s, `rig/check.sh` 0.29 s,
the three `.py` suites 0.37 s together, all exit 0 in that same clean archive, leaving
`rig/results/*/runs.jsonl` at 3 and 42 lines. Same line ADR 0014 draws between could-not-run and passed,
drawn one level down.

Two things T9 must **ask**, not assume: whether ADR 0014's "every committed executable" covers the three
`100644` rig `.py` files invoked via `python3` (the ADR does not answer it); and whether fixing the gate
means composing the bash arm inside `rig/check.sh`, or adding a CI step, since those leave different
things true. And `rig/run.sh`'s missing `--self-test` is a separate gap from T8's stale number — same file,
two independent defects, one about a value, one about a gate.

**L13 — T9 closed, and the spec's own framing of it was the most expensive thing to check (2026-10-14).**

T9 was written as a choice between two designs. Only one of them works, and the one that does not is the
one the task text leaned toward. `rig/check.sh` dispatches `--self-test) self_test; exit $?`, and the three
`check_component_self_test` calls sit **below** that exit — so adding the missing bash arm would have
changed nothing CI can reach, because CI cannot run the real gate. Reading the dispatch would have told me
this in ten seconds; I nearly built it anyway because the task said "or as its own CI step" and that `or`
made both options look live. **The check that worked was instrumenting `python3` on `PATH` to log its own
invocations**: five synthetic-fixture heredocs during `--self-test`, zero `--self-test` calls. Control flow
read by eye is a hypothesis; a logged invocation is a measurement.

Three findings worth more than the job:

| Finding | Evidence | Consequence |
|---|---|---|
| ADR 0014's "Two jobs were added on the way in" was false the day my own T3 wrote it | recovered draft has **3** jobs, `a5f81c4` has **4** — one job was added, covering **two executables**. Counted the executables, named them jobs | Corrected in the ADR, dated, with the recipe (`git show <rev>:…` over `fcaae282` vs `a5f81c4`). Third instance of the hand-stated-count class, and the first one inside a **decision file** — the artifacts other files cite as authority |
| My first T9 evidence line said "six mutants, each observed to fire" | Four mutants fire. Two of the six are positive guards (discovery picks up a new executable; empty array survives `set -u`) — they do not "fire" because they are not mutants | Recounted into a table with a Kind column. Caught by recounting before committing, the one method that has ever worked on this class (L11) |
| Two sentences I wrote **minutes** earlier were defective | "(previous paragraph)" pointed at the pairing-rule paragraph while the wipe warning it cited was two paragraphs up; "discovered from the index (mode `100755`…)" under-described the set, since the `100644` modules are also run | Both fixed by naming what they resolve to (a heading in the workflow file; the full two-rule set). This is the *citation resolves to what it names* discipline applied to prose cross-references, not just `path:line` — the off-by-one-at-birth class from L11, arriving in my own fresh sentences about other people's staleness |

The design decision the task never named, made deliberately: **discovery over a list.** The defect being
fixed *is* a hardcoded list that rotted while the repo grew (ADR 0014's rule rotted exactly that way once).
A job that names `rig/check.sh` and `rig/run-pipeline.sh` in prose closes this instance and leaves the
failure class loaded for the next executable. So the targets come from the index — `100755` under `rig/`
plus tracked `rig/*.py`, both excluding `rig/fixtures/` — and the mutant that proves it is the one that
matters most: a newly committed `rig/newtool.sh` was picked up with **no edit to the workflow**. Zero
discovered exits 2, because a scan that examined nothing is `could not run` (`gaps/0002`'s counterexample).

Two things that did **not** change, named so nobody reads this as more than it is: the composition gap
inside `rig/check.sh` is untouched — `run-pipeline.sh --self-test` is still not composed by this repo's own
rig gate, and `rig/README.md` now says the gap is open while CI coverage is new, which is exactly the
distinction SUGGESTION-1's disposition turns on. And `rig/run.sh` still has no `--self-test` at all: the
job names it as untested rather than counting it as covered. Whether to give it one is a separate decision
with its own trigger, not a footnote to this one.

**L6 — two defects in this document's own first draft, found by re-reading it against the rules it cites,
not by any gate (2026-10-14).**

| Defect | What was wrong | What fixed it |
|---|---|---|
| An operator decision that never happened | S7 stated the operator had classified the external repositories as public and nameable. Asked today the operator selected four pieces, a build location and a split target — and said nothing about naming. Attributing to the human a permission they did not grant is the exact failure this repo's citation discipline exists to stop. | S7 now rests on `gaps/README.md`'s own rule plus an API lookup reported in that spec, including the sibling that failed to resolve and is therefore unnamed. |
| A machine-local path inside a quotation | The operator's verbatim request contained a relative path under a home directory. `hooks/pre-commit` matches `(/Users\|/home)/[A-Za-z0-9._-]` and **cannot match a relative fragment**, so the gate returned 0 while the file carried the class ADR 0009 keeps as human judgment. | Elided visibly as `<home>/…/<forks workspace>`, inside the quote, marked rather than smoothed over. Every other word of the request stays verbatim — S1's whole purpose is that acceptance is judged against what was actually said. |

The order of discovery is the finding: **`./hooks/pre-commit` exited 0 on this file before either defect
was found.** "A clean gate is not evidence about that half" is a sentence `AGENTS.md` and `gaps/README.md`
both already carry, met from the inside, on the file written to obey it. It is also S8 in miniature — the
gate fired, and what it proved was narrower than a green exit reads as.

**L14 — T7 closed, and the correction I was told to write needed correcting too (2026-10-14).**

T7's own premise was false, in two independent ways, and both were in the committed task text. Check 6
was registered as `partial` "at one occurrence across `0001`/`0002`/`0003`" with "a second occurrence …
what licenses the first `blocks/` entry". The records say otherwise, in their own words: `0001` scored
check 6 `absent`; `0002` scored it `partial` and its Demand row reads **"1 — `0001` only"**, declining to
advance it; `0003`'s row reads **"First"** as a `partial`. So the demand was at **one** occurrence and T7
was to be the second — and T7 added **zero**, because the target failed `gaps/README.md`'s independence
test (142 commits under two identities that are both the operator's; its own design document names this
operator's tooling, and `0003`'s project, as borrowed sources). S4 is amended rather than quietly
re-read: what S4 asked for was the analysis, the occurrence was a hoped-for by-product.

Three of the corrections I was handed for `gaps/README.md` were themselves false, and each was cheap to
check. Sweeping every commit in this branch's ancestry — 79 commits carrying the count sentence, stated
count vs records on disk at that same commit:

| Claim I was given | Measured | Consequence |
|---|---|---|
| "no number is hand-stated in this file" is false because line 85 says "three outcomes" | True that it is false, wrong about why: the same **paragraph** hand-states the demand accounting, and that one is irreducible — `open-work.sh` counts files, not owners, so "two *independent* occurrences" cannot be derived | Rewritten to name which numbers are hand-stated and why they must stay. The replacement enumerates them instead of counting them: a count of the counts is this failure one level down |
| "a hand-stated count here rotted twice already" — and `df8af55`'s "Three analyses recorded" was **correct** | **Zero** rotted, but the arithmetic was wrong twice. Exactly **1** of 79 commits disagreed with its own tree: `df8af55`, which stated three beside **two** files — `0003` first appears in its *child* `6115b79`. Wrong **at birth**, not by drift, and that one is in this branch. (`b55f86a` and `79f5532` also mismatch; both are outside this ancestry — a stash and a parallel branch.) | The rot story is gone; the birth defect and the *sibling* file's real rot replace it, with the sweep stated so a reader can re-run it |
| "`rottud`" was a misspelling in the text | **Never existed before this document.** `git log --all -S 'rottud'` → **0 commits**; the working tree had 0 files. The only two occurrences anywhere now are this Log entry and its callback below, which name the word in order to record that it was never written — a self-referential hit, so re-running that grep returns 1 file and must be read as this file only | Recorded because the sentence was deleted anyway, and a false reason for a correct deletion is still a false reason |

The real rot was `ASK.md`'s "Two recorded runs": true on 2026-08-13 the day it was written, stale from
the third record on 2026-08-20 until today — **55 days across 22 published commits** (`6115b79..57faaf3`,
both fixed commits), during which `ASK.md` was edited **zero** times, so no human ever re-read the line while
it lied. It is also the first case in this feature where the second copy of a number was never even
*looked at*, which is a different failure from the drift L11 records. `ASK.md`'s `verified:` → 2026-10-14
because its entry's prose was rewritten and re-checked. `MAP.md`'s stays `2026-08-13`: precedent inside
this feature — `4ad47d7`, `97d45eb` and `439abbc` each edited that row and none bumped it — and this unit
replaces a hand-count in that cell with a pointer to the generator, which removes a claim rather than
re-verifying one.

**Two of the eleven gates scanned less than they read, and both were closed before the battery was
called green.** `./hooks/pre-commit --all` builds its list from `git ls-files`, so the first run
("clean across 196 tracked files") had **never seen this task's entire subject** — `gaps/0004` was
untracked. Per S8 an exit 0 on content it did not read is not a pass: re-ran with the file in scope
(**197**, exit 0), then planted a home path *in the new file* → **exit 1** naming
`gaps/0004-repack-atlas.md:329`, restored **byte-identical** each time (`sha256 01e5be81…` before that
edit, `1a409691…` on the final text — the sha the evidence line first quoted was the pre-edit file's, so
the mutant was re-run rather than the number left to rot). Separately, `./hooks/commit-msg --range HEAD HEAD` prints "clean across 0 commit message(s)" and
**exits 0** — our own gate committing the exact class `gaps/0004` was written about, now measured on our
own tree instead of asserted. Both are now in the Checks table with what makes each non-vacuous.

**The derived obligations this closing created, and where each went.** `decisions/0017` cited "three
projects, **three owners**" as the strongest demand in the repo; under the rule T7 just wrote into
`gaps/README.md`, ownership was established for **none** of the three and `0001`'s target is
*unestablished*. The count survives (`0002` and `0003` are independent on recorded evidence —
organisation-owned, `0003` created 2016-08-24 a decade before the operator's tooling existed, code search
**0** hits vs **30**/**329** controls), so the ADR's decision is unchanged; it carries a dated amendment
with `verified:` left at `2026-08-27` per the `0016` precedent, because bumping it would claim the
original sentence still holds. `gaps/0004:251` said "the three prior occurrences stand on their own" —
true at `0004`'s own writing, contradicted by the rule this unit adds; now two-established plus one
unestablished. And **T6's task text cited `npm run agent:check` and `npm run check:commits`, which appear
nowhere in any committed file** — they came from the working report, which by design never crosses into
this repo. A citation that resolves only on the author's machine is L11's off-by-one-at-birth class one
level up: it named real things and pointed at nothing a reader can open.

**The rule this run earns, which is about the correction rather than the finding:** a correction arrives
as a bundle — the true fact, the false claim it replaces, and a history justifying it — and the third
part is the part nobody re-derives, because it looks like background. Here the background was the false
part twice (`df8af55` was not correct; `rottud` never existed) while the deletion it justified was
correct anyway. **Verify a correction's history with the same command you would use to verify its
conclusion** — here one loop over `git rev-list` comparing a stated count against `git ls-tree` at the
same commit, which costs seconds and is the only thing that has ever worked on this class (L11, again).
My own first draft of that replacement text then hand-stated "28 commits" for a rot window of **22
published** ones, counting six unpushed commits of my own into a published-history claim. Caught by
computing it before committing, which remains the only method that works.

**L15 — the commit that recorded T7 created the staleness it was recording, and its own fix was wrong
twice (2026-10-14).**

`1a1fd8e` landed and, in landing, made three things false: the T8/T9/T7 cells still read "this commit's
hash is the next one's to record", and it advanced `commit-msg --range - HEAD` from **150 to 151** — the
count its own T7 evidence line hand-states. A commit that changes what it just reported is not a defect
in the report; it is L8 arriving one commit earlier than L8 expected.

The fix contained two false claims of my own, each killed by one command:

| Claim I wrote | Measured | Why the reasoning was wrong |
|---|---|---|
| Anchored T9's 117 / 196 / **149** to `439abbc` — "the commit that names them" | 149 exists at **one** commit: `bcb37eb`. `git rev-list --count` gives 149 / 150 / 151 at `bcb37eb` / `439abbc` / `1a1fd8e` | **A task measures the tree before its own commit lands, never the commit that records it.** T9's battery ran against `439abbc`'s parent. Off-by-one at birth again, in a sentence whose subject was off-by-one-at-birth |
| T8's hash was "late by one" | **Late by two.** Its hash was knowable the moment `bcb37eb` landed; chance #1 was its child `439abbc` (`git rev-parse 439abbc^`), chance #2 was `1a1fd8e`, and `grep -c bcb37eb` returns **0** for both. This commit is chance #3 | Counted from the feel of the sequence. The check is `git show <rev>:… \| grep -c`, which I had already used three times today |

**And the correction I committed earlier this session had a moving ref in it.** Two lines asserted "55
days across 22 published commits (`6115b79..origin/main`)". `origin/main` is not a fact about history, it
is a pointer that grows the moment anything is pushed to it — so the sentence reporting a rot was itself
built to rot, and the number it defends would silently stop matching. Both are pinned to `57faaf3`, a
fixed commit, and the count re-verified after the pin: `git rev-list --count 6115b79..57faaf3` → **22**.
`AGENTS.md`'s rule is that a citation must resolve for a reader holding only this repo; a ref whose value
depends on when you fetch it does not resolve at all.

The rule this earns, which generalises past this file: **anchor a derived count to fixed objects — commit
hashes, never refs — and anchor it to the tree it was measured in.** "HEAD", "main", "origin/main" and
"this commit" are all the same hazard wearing different clothes: they name a different thing depending on
when they are read, which is exactly what makes a number unfalsifiable rather than merely old. The
message-count case adds the second half: when the measurement and the record are separated by a commit,
the number belongs to the parent, and writing the child's hash next to it is a false attribution even
though the child is where the sentence lives.
