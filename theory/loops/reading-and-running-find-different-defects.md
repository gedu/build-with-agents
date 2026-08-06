---
id: theory/loops/reading-and-running-find-different-defects
type: theory
targets: [any]
status: validated
verified: 2026-08-06
sources: ["journal/2026-08-05-redaction-gate-and-2478-on-224.md", "decisions/0009-redaction-is-a-repo-wide-rule.md", "research/claude-certified-architect-exam-guide.md", "research/agent-harness-explainer-cluster.md", "theory/loops/verifier-availability.md"]
---

# Independent review buys independence of reasoning, not independence of assumptions

**The claim.** Reading code and executing it against hostile input find **different classes of
defect**, and neither class is a subset of the other. Reading finds where the implementation departs
from the author's intent. Execution finds where the author's **model of the environment** departs
from the environment.

The consequence is the useful part, and it is counter-intuitive: **adding more independent readers
does not reach the second class.** Independent review is independent of the author's *reasoning*. It
is not independent of the author's *assumptions about how the surrounding tools behave*, because a
reader who has not run the code inherits those assumptions by default. Four reviewers who all believe
`git diff` prints `+++ b/path` will all miss the case where it prints `+++ "b/path"`.

## The evidence

One change, first-hand, in this repo on 2026-08-05: a new deterministic redaction gate — 598 changed
lines including a new executable shell script — reviewed by four independent adversarial lenses
(`review-risk`, `review-resilience`, `review-readability`, `review-reliability`) running as separate
agents with fresh context and read-only tools, then subjected to an adversarial input pass afterwards.
Full record in `journal/2026-08-05-redaction-gate-and-2478-on-224.md`.

Six real defects. They partition cleanly.

### What reading found, and execution had not

| Defect | Why reading found it |
|---|---|
| `grep`'s exit 2 collapsed with exit 1 by `\|\| :` — a fail-open in a gate | The exit-code contract is visible in the source. The author's reasoning about it was simply wrong |
| `--all` mode exempted its own whole file, not just its pattern table | The exemption's stated purpose and its actual breadth disagree, on one line |

Both are defects of **intent versus implementation**, and both survived a careful author. The tests
written alongside the code passed — because they were happy-path tests, chosen by the person holding
the wrong belief. Execution did not find these. Reading did.

This is `research/claude-certified-architect-exam-guide.md`'s claim behaving as advertised: a reviewer
without the generation context questions decisions the generating session will not, because it has
already been persuaded by its own reasoning.

### What execution found, and four independent readers had not

| Defect | Why reading could not find it |
|---|---|
| Filename with a space → git appends a TAB to the `+++` header | Requires knowing git's header formatting for that case |
| Filename with non-ASCII → git **quotes** the whole path, so the parser silently attributed findings to the **previous file** | Requires knowing git quotes paths at all |
| Binary file in audit mode → `grep` prints "Binary file X matches" instead of content | Requires knowing grep's binary behaviour |
| Binary file staged → `git diff` emits only "Binary files differ", no added lines | Requires knowing git's binary diff behaviour |

Every one of the four has the same shape: **the defect is not in what the code says, it is in what
something the code calls actually emits.** The source reads correctly against a plausible mental model
of `git` and `grep`. The model is wrong in four places, and nothing in the file reveals that.

Note who found them: the **same author** who wrote the defects, ten minutes later, by running the code
against inputs nobody had chosen for it. Independence contributed nothing. Execution contributed
everything.

### Two defects that even the corner-case design missed

Sharper still, and the reason this file does not simply say "write tests":

- Forcing a text diff for binaries looked like the fix and changed nothing, because **awk truncates a
  record at the first NUL byte**, so the added line arrived as an empty string and scanned clean.
- Fixing that surfaced the next layer: `tr`, then `awk`, aborting outright on a blob's invalid
  multibyte input under a UTF-8 locale.

Neither was predicted by the person designing the corner cases. They were **produced by running the
fix**. So the boundary is not reading-versus-testing; it is reading-versus-**execution**, and each
execution can reveal a layer the previous one hid.

## Why the classes are disjoint, stated as a mechanism

| | Verifies | Blind to |
|---|---|---|
| Reading (human or independent lens) | Implementation against **stated intent** | Every assumption the reader shares with the author about external behaviour |
| Executing against hostile input | Implementation against **actual environment** | Intent — a program can be confidently, correctly wrong about what it should do |

A reviewer's leverage comes from not sharing the author's reasoning. Nothing about that gives them a
better model of what `git diff` prints. Environmental knowledge is not a property of independence; it
is a property of having looked, and looking means running.

The converse holds and is why execution does not dominate either: a test suite written by the author
encodes the author's intent, so it cannot detect that the intent was wrong. The two fail-open defects
above passed every test in existence at the time.

## Consequences for design

- **Run both, and do not treat either as covering the other.** A clean review is not evidence about
  environmental behaviour; a green suite is not evidence about intent.
- **Adversarial input is a distinct step with a distinct owner's question**: not "is this correct?"
  but "what does the thing I am calling actually do at its edges?" Enumerate the *external* surfaces
  the code depends on and abuse each one.
- **Do not scale reviewers to reach environmental defects.** More readers is the wrong lever; it is
  the lever that looks like it should work.
- **Prefer code-based, deterministic checks first**, then judgment-shaped ones — the ordering in
  `research/agent-harness-explainer-cluster.md` and the layer ordering in
  `theory/loops/verifier-availability.md`. An assumption about `grep` is checkable by running `grep`,
  which is cheaper and stronger than any amount of reasoning about `grep`.
- **The instrument is in scope.** In the same episode the test harness itself reported every fix as
  failed while silently running the old code. Before believing a result, confirm what produced it was
  the thing under test — see the report-is-not-evidence section in
  `theory/orchestration/delegation-and-context-boundaries.md`.

## Scope

**One change, one repository, one day, six defects.** This is a documented case with a clean internal
structure, not a measurement: no sample, no control, no second trial. The partition is what the case
demonstrates; the *proportions* prove nothing — that four defects fell on one side and two on the
other is an artifact of this change, which happened to be a shell script whose entire job is calling
external tools. Code with little environmental surface would partition differently.

The reviewers were **LLM sub-agents with read-only tools** and fresh context. Whether human reviewers
partition the same way is untested here and plausibly differs — a human who has debugged `git` output
before carries environmental knowledge a fresh reader does not.

This file makes **no efficacy claim about review in general.** It claims the two activities have
different reach, evidenced once, with the mechanism stated so the claim can be attacked.

## What would sharpen it

The same change reviewed by readers who are told to *run* the code, versus readers restricted to
reading, on a change with substantial external surface — to test whether the partition is about the
activity or about the tooling the reviewer is given. The lenses here had `Read`, `Grep` and `Glob` and
no execution tool at all, which means this case cannot distinguish "reading does not find these" from
"these reviewers could not run anything." That is a real confound and it is the first thing to fix.
