---
id: journal/2026-08-19-what-open-work-actually-looks-like
type: journal
targets: [any]
status: draft
verified: 2026-08-19
sources: []
---

# 2026-08-19 — What open work in this repo actually looks like, once counted

Provenance for `decisions/0016`. Journal, so: never authority, valid as the record of where
that ADR came from (ADR 0007).

## Where this started

A handoff note asked for a **generated index of open work** — the operator's problem stated as
*"I don't know what is open"*, not *"I don't know what order to do it in"*. So: enumerate, do not
rank. It named the inputs it expected the index to read, and the first one was
`## What is not settled` sections, described as the de facto convention, *"present in `skills/`,
`sdd/`, `upstream/`, `journal/`, and elsewhere"*.

## The premise was wrong, and counting is what showed it

```sh
rg -l '^##+ .*not settled' --glob '!rig/fixtures/**'
```

Two files. Both in `journal/`. None in `skills/`, `sdd/` or `upstream/`.

A generator keyed on that heading would have produced a two-line index and looked authoritative
doing it. That is worse than the stale hand-written index `AGENTS.md` warns about, because
"generated" reads as "complete" — the reader has no reason to doubt it, and nothing in the output
would have said the marker only ever covered two files.

The handoff was written five days earlier by a session that had just been working in those two
journal entries. It generalised from what was in front of it. That is not carelessness; it is what
an unmeasured claim looks like from the inside, and it is the exact failure `BACKLOG.md` entry 1
(claim discipline) already describes: *any number a command can produce must come with that
command*. The handoff's claim was producible in one `rg` and was not produced.

## What the second stated input turned out to be worth

The handoff also warned that `status: draft` alone is not a useful signal — "48 files carry it".
That warning was right in kind and stale in number:

```sh
# 103 content .md files (tracked + untracked, minus rig/fixtures/, minus generated symlinks)
draft 57   validated 45   rejected 1
```

57 of 103. Better than half the repository. A signal that matches more than half of everything
ranks nothing, and most of those files are unpromoted content rather than open work — 14 in `sdd/`,
14 in `journal/`. Kept out of the index as an entry source. Reported as a number instead.

## What is actually open, counted rather than assumed

Six sources survived. Each already exists as a convention somewhere other than in the generator:

| Source | What it holds | Count today |
|---|---|---|
| `BACKLOG.md` `###` entries | Blocked work, each with a named unblock condition | 2 |
| `hypotheses/` | Open claims with a declared test. Zero citability (ADR 0012) | 3 |
| `gaps/` | Demand records below the two-occurrence threshold | 2 |
| `decisions/` with `status: draft` | A decision made and not ratified | 1 (`0014`) |
| `sdd/` outside `sdd/archive/` | A cycle still in flight | 1 (`measurement-rig`) |
| `## What is not settled` | Declared-unsettled prose, wherever it is | 2 files |

Five of the six are **structural** — a directory listing or a frontmatter field, both already
enforced by `check.sh`. Only the sixth is a prose convention, and it is now the smallest input
rather than the foundation.

## The three design questions, and what settled each

### Extend `check.sh`, or a sibling?

Sibling. `check.sh`'s header states its question — *"does this repo still hold the shape its own
rules describe"* — and its exit codes carry the answer, where `1` means a violation. **Open work is
not a violation.** A repo with three open hypotheses is a healthy repo. A flag that made `check.sh`
exit 1 because work is open would be wrong; one that exited 0 while printing a report would put two
contracts in one executable. `OPERATIONS.md` maps commands to moments, and these are different
moments: `check.sh` runs after editing a content file, the index is read when a session starts.

### Which side of the not-committed line does the output fall on?

Neither. It goes to **stdout and nowhere else**. Nothing on disk means nothing to gitignore, no
managed block for `setup.sh` to own, and no file that can be stale — the strongest available form of
"generated or absent". A redirect is the operator's business and this script will not refresh it.

### Does it replace `BACKLOG.md`?

No, and this was the one real risk of the task. `BACKLOG.md` holds *authored reasoning* — why a
thing is blocked, what exactly would unblock it, and in entry 1's case an inverted intuition worth
more than the entry itself. No generator synthesises that. `MAP.md` already lists it as an Area and
as citable. So the index **reads** it and prints each entry's title and unblock condition, and never
restates the reasoning. The index points; the source states.

## One thing found by building it

`hooks/commit-msg --range` already carries a lesson this generator needed: it prints how many
messages it scanned, *including zero*, because an empty range and a clean range look identical
otherwise. Same shape here. A source that does not exist prints `absent`, never `0` — otherwise
"the directory was deleted" and "nothing is open there" render the same, and the second is good news
while the first is a broken index.

## What is not settled

| Open | Why it is open |
|---|---|
| Whether the six sources are the right six | They are what exists today, counted. A seventh convention appearing later will not announce itself; the COVERAGE block is what makes that visible, and nobody has yet had to use it for that |
| Whether anyone reads it at session start | The same claim `ASK.md` carries and cannot settle. Using it is what promotes it |
| `## What is not settled` as a convention | It is now enumerated, which is a reason to write more of them. Whether that actually happens is untested, and the index does not require it |
| The prose sources are unchecked for quality | The index reports that a file declares itself unsettled. Whether the declaration is any good is the `ASK.md` problem again, and no checker settles it |
