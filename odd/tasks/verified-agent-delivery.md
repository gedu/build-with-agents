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
repo to take verifier-availability from one occurrence to two (T7).

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
| `./open-work.sh --self-test` exit code per case | a new enumeration source reports what it sees, and reports `absent` when the directory is gone | `open-work.sh:401` self-test; asserts printed output, not only exit code |
| `./check.sh --self-test` | a planted frontmatter violation is reported, one invariant at a time | `check.sh` self-test, the shape S8 generalises |
| `./hooks/pre-commit --all` / `--self-test` | a planted leak fails the gate; a missing pattern list exits 2 | `hooks/pre-commit:142` builds a throwaway repo and asserts the fail |
| `bash -n` / `python3 -m py_compile` | syntax gate for a file whose behaviour costs a real run to reach | `OPERATIONS.md` decision table |
| `rig/check.sh` | seconds-long: manifests, composed `--self-test`s, byte-identical re-derive | added by the failure-flood cycle for this exact purpose |
| `rig/run-pipeline.sh --self-test` | the pipeline runner's extractable functions, runnable without a model call | `rig/run-pipeline.sh:103` |
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

- [ ] **T3 Land the server-side layer: one workflow, three jobs, each pairing its self-test with the
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

- [ ] **T4 Measure the two timeout placeholders and replace them with measured values**
  - Blocked by: None (parallel with T2, disjoint files: `rig/run-pipeline.sh` only)
  - Seams: `rig/check.sh`, `rig/run-pipeline.sh --self-test`
  - `rig/run-pipeline.sh:88-89` hold `STEP_TIMEOUT_S=180` and `SUITE_TIMEOUT_S=150`, marked
    *"PLACEHOLDERS pending task 5.7's real wall-clock measurement"*. The archive-report calls them
    *"undone configuration with no stated trigger"* — there is no blocker, nobody ran the measurement.
  - The measurement is the fixture suite's wall clock under the pinned runtime, taken N times, not a
    guess with margin. Record how many samples, and keep the invariant the script already enforces:
    suite timeout strictly smaller than step timeout, or exit 2.

- [ ] **T5 Found the first countable run: `failure-flood` stage 2, both arms, N=5 per cell**
  - Blocked by: T4
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
    from the complaint. `repack-atlas`'s `npm run agent:check` and `npm run check:commits` are the
    working prior art, and T7 is what records them as such.

- [ ] **T7 `gaps/0004` — gap analysis of a public Callstack RN repo, via `skills/project-gap-analysis`**
  - Blocked by: None (read-only, disjoint surface; it can run any time and feeds T6, not the reverse)
  - Seams: the skill's own checklist, and `./check.sh` on the record it writes
  - Target chosen for a specific reason: `callstackincubator/repack-atlas` — public, `private: false`
    verified 2026-10-14, named under the `gaps/README.md` exception S7 records — already ships
    `npm run agent:check` and `npm run check:commits`. Check 6 (verifier availability) is `partial` at one occurrence across
    `0001`/`0002`/`0003`; a second occurrence is what licenses the first `blocks/` entry, and
    `gaps/0002` states the rule for how it is built — from the working example, extracted, not invented.
  - Naming is licensed by S7 and by the exception `gaps/README.md` records; the redaction gate is run
    by hand from this worktree regardless, because a clean gate is not evidence about the half it
    cannot pattern-match.

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
| Redaction, whole tree | `./hooks/pre-commit --all` | 0 |
| Redaction, messages | `./hooks/commit-msg --range - HEAD` | 0 |
| Rig integrity | `rig/check.sh` | 0, and `git diff -- rig/` empty after the byte-identical re-derive |
| Index honesty | `./open-work.sh` | reads its COVERAGE block; `absent` distinguished from `0` |

## Progress and evidence

| Task | Outcome | Commit | Check observed |
|---|---|---|---|
| T1 | done | `2839cd6` | `./check.sh` 0 over the tree; `./check.sh --self-test` 0; `./hooks/pre-commit --all` 0; `./open-work.sh` printed 6 sources and did **not** list this document — T2's red reproduced before T2 was written |
| T2 | done | this commit's hash is the next one's to record, per T1's self-reference note | `./open-work.sh --self-test` 0; **12 FAIL + exit 1** with the new section deleted (deletion-mutant, recount without truncation); `sh -n` 0; `./check.sh` 0; `./hooks/pre-commit --all` 0; index prints 16 items across 7 sources |
| T3–T7 | not started | — | — |

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
