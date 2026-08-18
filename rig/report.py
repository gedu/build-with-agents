#!/usr/bin/env python3
"""rig/report.py — aggregates rig/results/<experiment>/runs.jsonl into the
four-cell tables. Never produces a composite score (spec R-A1.3): the four
cells, the off-set/forbidden distribution and the token/cost figures are
printed as separate tables, and nothing here sums them into one number.

Pairing rule (design.md Amendment 1): a (task_id, iteration) slot counts
toward every table below only when BOTH arms reached state=="complete" for
that slot. Every excluded slot is named, with its arm and void_reason —
never a silent drop (spec R-A1.2).

Wall clock is read out per row for diagnosis only. It is never differenced
between arms anywhere in this file (spec R-A1.5) — there is deliberately no
function here that subtracts one arm's wall_ms from the other's.

Task 6.4 (`--experiment` dispatcher): a second experiment,
`failure-flood-v1` (arms `monolithic`/`pipeline`), reuses this file rather
than forking a sibling — same discipline as `rig/derive.py`'s own
`--experiment` registry (task 5.8). Its four tables (diagnostic
precision/recall, green-restore verdict distribution, peak occupancy,
cumulative occupancy — spec R-F3.2/R-F4.1-4.3/R-F5.1-5.4) stay just as
UNCOMBINED as tool-surface-v1's own tables: no field here is ever summed,
weighted or ANDed with another (R-A1.3/R-F4.3).

STDLIB ONLY (decisions/0011): json, statistics, pathlib.
"""

import contextlib
import io
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT = "tool-surface-v1"
RUNS_PATH = REPO_ROOT / "rig/results" / EXPERIMENT / "runs.jsonl"
INSTRUMENT_DOUBT_THRESHOLD = 3  # X = 3, spec's instrument-doubt rule

FAILURE_FLOOD_EXPERIMENT = "failure-flood-v1"
FAILURE_FLOOD_RUNS_PATH = REPO_ROOT / "rig/results" / FAILURE_FLOOD_EXPERIMENT / "runs.jsonl"
FAILURE_FLOOD_ARMS = ("monolithic", "pipeline")  # per-experiment arm names (task 6.4)


def load_rows(runs_path=RUNS_PATH):
    if not runs_path.is_file():
        return []
    return [json.loads(l) for l in runs_path.read_text().splitlines() if l.strip()]


def pair_slots(rows):
    """Returns (paired_rows, excluded) where paired_rows is every row that
    belongs to a (task_id, iteration) slot where BOTH arms are
    state=="complete", and excluded lists every row that is not, each
    tagged with why."""
    by_slot = {}
    for r in rows:
        by_slot.setdefault((r["task_id"], r["iteration"]), []).append(r)

    paired, excluded = [], []
    for slot, slot_rows in by_slot.items():
        arms_complete = {r["arm"] for r in slot_rows if r["state"] == "complete"}
        if arms_complete == {"broad", "scoped"} and len(slot_rows) == 2:
            paired.extend(slot_rows)
            continue
        for r in slot_rows:
            reason = "state!=complete" if r["state"] != "complete" else "no-counterpart-in-other-arm"
            excluded.append({
                "task_id": r["task_id"], "iteration": r["iteration"], "arm": r["arm"],
                "run_id": r["run_id"], "state": r["state"], "void_reason": r["void_reason"],
                "reason": reason,
            })
    return paired, excluded


def four_cell_table(paired_rows):
    """{(task_id, arm): {cell: count}}, cells always published even at 0 —
    improper-success must never be silently merged into pass or fail."""
    cells = ("proper", "improper-success", "clean-failure", "failure")
    table = {}
    for r in paired_rows:
        key = (r["task_id"], r["arm"])
        table.setdefault(key, {c: 0 for c in cells})
        table[key][r["classification"]] += 1
    return table


def offset_forbidden_distribution(paired_rows):
    """Per (task_id, arm): the off-set and forbidden call counts, reported
    as N plus min/max range — never a mean alone (spec's sample-size rule
    applies the same way to this distribution)."""
    dist = {}
    for r in paired_rows:
        key = (r["task_id"], r["arm"])
        dist.setdefault(key, {"offset_calls": [], "forbidden_calls": []})
        dist[key]["offset_calls"].append(r["offset_calls"])
        dist[key]["forbidden_calls"].append(r["forbidden_calls"])
    return dist


def cost_token_figures(paired_rows):
    """Per (task_id, arm), separately — never combined with the four-cell
    counts or with each other into one figure (spec R-A1.3)."""
    figures = {}
    for r in paired_rows:
        key = (r["task_id"], r["arm"])
        figures.setdefault(key, {"total_cost_usd": [], "output_tokens": []})
        figures[key]["total_cost_usd"].append(r["total_cost_usd"])
        figures[key]["output_tokens"].append(r["output_tokens"])
    return figures


def anomaly_log(rows):
    """Every void_reason and every state=="failed" row, across ALL rows —
    not just the paired subset, since an anomaly that only ever hits one
    arm is exactly what this log exists to surface.

    Counted as a SET per row, not a sum of overlapping fields: void_reason
    is very often also a member of that same row's anomaly_classes (derive.py
    populates both from the same detection), and summing both would count
    one anomalous run twice under the same class name."""
    counts, control_counts = {}, {}
    for r in rows:
        classes = set(r.get("anomaly_classes", []))
        if r["state"] == "void" and r["void_reason"]:
            classes.add(r["void_reason"])
        if r["state"] == "failed":
            classes.add("failed")
        if r.get("is_control"):
            # A control that voided did its job. Its anomaly is deliberate and is
            # kept out of the instrument-doubt count — otherwise running controls
            # trips the threshold that blocks the theory/ write.
            #
            # A control that did NOT void is the real alarm: the detector it exists
            # to exercise is dead, and every run that passed that check is worthless.
            # That one counts, and counts loudly.
            if r["state"] == "void":
                for cls in classes:
                    control_counts[cls] = control_counts.get(cls, 0) + 1
            else:
                counts["control-did-not-fire"] = counts.get("control-did-not-fire", 0) + 1
            continue
        for cls in classes:
            counts[cls] = counts.get(cls, 0) + 1
    return counts, control_counts


def print_table(title, rows):
    print(f"\n{title}")
    for row in rows:
        print("  " + row)


def report_tool_surface(rows):
    """tool-surface-v1's own report body, UNCHANGED from before task 6.4 —
    the `--experiment` dispatcher wraps it rather than restructuring it, so
    its already-verified output has nothing new to explain if a regression
    ever shows up here."""
    paired, excluded = pair_slots(rows)

    print_table("Excluded slots (named, never a silent drop):", [
        f"{e['run_id']} ({e['task_id']}/{e['arm']}) state={e['state']}"
        + (f" void_reason={e['void_reason']}" if e["void_reason"] else "")
        + f" — {e['reason']}"
        for e in excluded
    ] or ["none"])

    cells = four_cell_table(paired)
    for (task_id, arm), counts in sorted(cells.items()):
        print_table(f"Four-cell table — {task_id}/{arm} (N={sum(counts.values())}):", [
            f"{cell}: {n}" for cell, n in counts.items()
        ])

    dist = offset_forbidden_distribution(paired)
    for (task_id, arm), d in sorted(dist.items()):
        oc, fc = d["offset_calls"], d["forbidden_calls"]
        print_table(f"Off-set / forbidden distribution — {task_id}/{arm}:", [
            f"offset_calls: N={len(oc)} min={min(oc)} max={max(oc)}",
            f"forbidden_calls: N={len(fc)} min={min(fc)} max={max(fc)}",
        ])

    figures = cost_token_figures(paired)
    for (task_id, arm), f in sorted(figures.items()):
        costs = f["total_cost_usd"]
        toks = f["output_tokens"]
        print_table(f"Cost / token figures — {task_id}/{arm} (reported separately, never combined):", [
            f"total_cost_usd: N={len(costs)} min={min(costs):.4f} max={max(costs):.4f} median={statistics.median(costs):.4f}",
            f"output_tokens: N={len(toks)} min={min(toks)} max={max(toks)}",
        ])

    print("\nWall clock (diagnostic per row only — never differenced between arms):")
    for r in paired:
        print(f"  {r['run_id']}: wall_ms={r['wall_ms']}")

    print("\nDefect recall/precision — three counts per run, reported separately and never")
    print("summed into a score (spec R-A1.3). Meaningful for multi-defect tasks (a single-")
    print("defect task degenerates to found in {0,1}, missed in {0,1}, extra in {0,...}):")
    for r in paired:
        if r.get("defects_found") is not None:
            print(f"  {r['run_id']}: defects_found={r['defects_found']} "
                  f"defects_missed={r['defects_missed']} defects_extra={r['defects_extra']}")

    anomalies, control_anomalies = anomaly_log(rows)
    print_table("Anomaly log (spontaneous — counts toward instrument doubt):",
                [f"{k}: {v}" for k, v in sorted(anomalies.items())] or ["none"])
    print_table("Controls that fired as designed (deliberate — never counted):",
                [f"{k}: {v}" for k, v in sorted(control_anomalies.items())] or ["none"])
    tripped = {k: v for k, v in anomalies.items() if v >= INSTRUMENT_DOUBT_THRESHOLD}
    if tripped:
        print(f"\n  !! INSTRUMENT-DOUBT THRESHOLD TRIPPED (X={INSTRUMENT_DOUBT_THRESHOLD}): {tripped}")
        print("     Per spec: investigate before any theory/ write. A refuting result with a")
        print("     clean anomaly log must not be attributed to the instrument — but this one isn't clean.")

    return 0


# ---- task 6.4: failure-flood-v1's own tables ------------------------------
# Per-experiment arm names (design.md sec 6/8): monolithic/pipeline, never
# tool-surface-v1's broad/scoped. No pairing rule here — unlike Amendment 1,
# failure-flood-v1's hypotheses (0002, 0003) compare each arm's own
# distribution (median, range) independently, never a matched-slot pair —
# so the only exclusion rule is "state==complete", the same filter task 5.7
# proved live against this experiment's own runs.jsonl.

def failure_flood_complete_rows(rows):
    """(complete, excluded) — every non-"complete" row (void or failed) is
    named, never a silent drop, matching R-A1.2's discipline applied here."""
    complete, excluded = [], []
    for r in rows:
        (complete if r["state"] == "complete" else excluded).append(r)
    return complete, excluded


def _by_task_arm(rows):
    table = {}
    for r in rows:
        table.setdefault((r["task_id"], r["arm"]), []).append(r)
    return table


def diagnostic_precision_recall_table(rows):
    """R-F3.2/R-F4.1: precision/recall pair, per (task_id, arm), reported as
    a pair and never blended into one figure. `causes_claimed`/
    `causes_correct` stay structurally `None` (never an empty list) on
    every row until task 5.9 threads `root-cause-report.txt` out of the
    ephemeral workspace (sdd/failure-flood-triage/tasks.md task 5.9) — this
    table says so explicitly rather than reporting a fabricated 0/n-a."""
    lines = []
    for key, rs in sorted(_by_task_arm(rows).items()):
        scored = [r for r in rs if r.get("causes_claimed") is not None]
        if not scored:
            lines.append(
                f"{key[0]}/{key[1]}: N={len(rs)} scored=0 — causes_claimed/"
                "causes_correct are null on every row (task 5.9 not "
                "implemented; R-F3.2 cannot be honestly computed yet)"
            )
            continue
        precisions, recalls = [], []
        for r in scored:
            claimed = set(r["causes_claimed"])
            correct = set(r.get("causes_correct") or [])
            present = r.get("causes_present")
            if claimed:
                precisions.append(len(correct) / len(claimed))
            if present:
                recalls.append(len(correct) / present)
        lines.append(
            f"{key[0]}/{key[1]}: N={len(rs)} scored={len(scored)} "
            f"precision(n/a excluded)=N={len(precisions)} "
            f"{('min=%.3f max=%.3f median=%.3f' % (min(precisions), max(precisions), statistics.median(precisions))) if precisions else 'n/a'} "
            f"recall=N={len(recalls)} "
            f"{('min=%.3f max=%.3f median=%.3f' % (min(recalls), max(recalls), statistics.median(recalls))) if recalls else 'n/a'}"
        )
    return lines


def green_restore_distribution(rows):
    """R-F4.2: four values, plus `unscored` for a complete row whose suite
    never `ran` or whose answer-key was missing — never folded into one of
    the four real verdicts, and never combined with any other channel here
    (R-F4.3)."""
    verdicts = ("green", "partial", "no-progress", "regressed")
    table = {}
    for r in rows:
        key = (r["task_id"], r["arm"])
        table.setdefault(key, {v: 0 for v in verdicts})
        table[key].setdefault("unscored", 0)
        v = r.get("verdict")
        table[key][v if v in verdicts else "unscored"] += 1
    return table


def green_restore_table(rows):
    """One line per (task_id, arm), so the header prints even with zero
    complete rows. R-F4.2 requires this channel to be published as a
    mandatory companion; a per-key loop that emits nothing when the run set
    is empty does not publish it at all, and a table that vanishes is the
    silent drop this file's own excluded-rows contract forbids. Same shape as
    `occupancy_table` — the four verdicts plus `unscored` stay listed side by
    side, never summed (R-F4.3)."""
    lines = []
    for key, counts in sorted(green_restore_distribution(rows).items()):
        lines.append(
            f"{key[0]}/{key[1]}: N={sum(counts.values())} "
            + " ".join(f"{v}={n}" for v, n in counts.items())
        )
    return lines


def occupancy_table(rows, field):
    """Per (task_id, arm): N/min/max/median of `field`
    (`peak_occupancy_tokens` or `cumulative_occupancy_tokens`), skipping
    rows where it is `None`. Reported alone — R-F5.4 forbids combining peak
    and cumulative into one figure, and this function is called once per
    channel rather than once for both."""
    lines = []
    for key, rs in sorted(_by_task_arm(rows).items()):
        vals = [r[field] for r in rs if r.get(field) is not None]
        if not vals:
            lines.append(f"{key[0]}/{key[1]}: N=0 (no complete row has {field})")
            continue
        lines.append(
            f"{key[0]}/{key[1]}: N={len(vals)} min={min(vals)} max={max(vals)} "
            f"median={statistics.median(vals):.1f}"
        )
    return lines


def report_failure_flood(rows):
    complete, excluded = failure_flood_complete_rows(rows)

    print_table("Excluded rows (named, never a silent drop):", [
        f"{e['run_id']} ({e['task_id']}/{e['arm']}) state={e['state']}"
        + (f" void_reason={e['void_reason']}" if e.get("void_reason") else "")
        for e in excluded
    ] or ["none"])

    print_table(
        "Diagnostic precision/recall — R-F3.2/R-F4.1, per (task_id, arm), "
        "the primary outcome channel, never blended into one figure:",
        diagnostic_precision_recall_table(complete),
    )

    print_table(
        "Green-restore verdict distribution — R-F4.2, per (task_id, arm), "
        "never combined with diagnostic attribution or either occupancy "
        "channel:",
        green_restore_table(complete),
    )

    print_table(
        "Peak occupancy tokens — R-F5.1, per (task_id, arm), reported alone "
        "(R-F5.4 — never combined with cumulative occupancy):",
        occupancy_table(complete, "peak_occupancy_tokens"),
    )

    print_table(
        "Cumulative occupancy tokens — R-F5.2, per (task_id, arm), reported "
        "alone (R-F5.4 — never combined with peak occupancy):",
        occupancy_table(complete, "cumulative_occupancy_tokens"),
    )

    return 0


EXPERIMENTS = {
    "tool-surface-v1": {"runs_path": RUNS_PATH, "report_fn": report_tool_surface},
    FAILURE_FLOOD_EXPERIMENT: {"runs_path": FAILURE_FLOOD_RUNS_PATH, "report_fn": report_failure_flood},
}


# ---- --self-test (flag-gated; ADR 0013's ratified shape, mirroring
# collect.py's own --self-test and derive.py's --self-test: same flag, same
# PASS/FAIL-per-case shape, same exit-code contract) --------------------------
#
# ADR 0013: a committed executable carries its own test. report.py received
# real new logic this cycle (task 6.4's --experiment dispatcher and its two
# failure-flood-v1 tables) with none of its own. No fixtures directory, no
# filesystem I/O at all — every row here is an inline synthetic dict, since
# report.py's own inputs are already just JSON rows, not run directories.

_SELF_TEST_HEADERS_FAILURE_FLOOD = (
    "Diagnostic precision/recall",
    "Green-restore verdict distribution",
    "Peak occupancy tokens",
    "Cumulative occupancy tokens",
)


def _self_test_four_headers_on_empty_rows():
    """The PR6 gatekeeping defect this batch's own instruction names: green-
    restore was emitted by a per-key loop that produced nothing on an empty
    collection while its three sibling tables printed unconditionally — a
    header that silently vanishes on zero rows is exactly the "silent drop"
    R-A1.2 forbids elsewhere in this file. Counting headers on an EMPTY row
    set is the regression test that would have caught it before it shipped."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        report_failure_flood([])
    out = buf.getvalue()
    missing = [h for h in _SELF_TEST_HEADERS_FAILURE_FLOOD if h not in out]
    ok = not missing
    print(f"  [{'PASS' if ok else 'FAIL'}] all four table headers print on zero complete rows"
          + ("" if ok else f" (missing: {missing})"))
    return ok


def _self_test_no_composite_field():
    """R-A1.3/R-F4.3: nothing in this file ever sums, weights or ANDs a
    channel with another. Checked in two directions, since either alone
    leaves a hole: (a) occupancy_table takes exactly one `field` argument, so
    a call asking for peak_occupancy_tokens must never leak a
    cumulative_occupancy_tokens value into its own line, and vice versa; (b)
    green_restore_table's four verdict counts plus `unscored` are printed
    side by side (space-joined counts), never folded into a single derived
    'score' token."""
    ok = True
    rows = [
        {"task_id": "s1", "arm": "monolithic", "verdict": "green",
         "peak_occupancy_tokens": 111, "cumulative_occupancy_tokens": 555},
        {"task_id": "s1", "arm": "monolithic", "verdict": "regressed",
         "peak_occupancy_tokens": 222, "cumulative_occupancy_tokens": 999},
    ]
    peak_line = occupancy_table(rows, "peak_occupancy_tokens")[0]
    cumulative_line = occupancy_table(rows, "cumulative_occupancy_tokens")[0]
    case_a = ("111" in peak_line and "222" in peak_line
              and "555" not in peak_line and "999" not in peak_line
              and "555" in cumulative_line and "999" in cumulative_line
              and "111" not in cumulative_line and "222" not in cumulative_line)
    ok = ok and case_a
    print(f"  [{'PASS' if case_a else 'FAIL'}] occupancy_table(rows, field) reports ONLY the requested"
          " channel — a peak call never carries a cumulative value or vice versa")

    gr_line = green_restore_table(rows)[0]
    # Exactly the five known verdict/unscored tokens, each a raw per-verdict
    # count (never combined with a sibling verdict or with either occupancy
    # channel — "unscored" is R-F4.2's own fifth bucket name, not a derived
    # figure, so this checks token identity rather than a naive substring
    # match against "score").
    verdict_tokens = {tok.split("=")[0] for tok in gr_line.split() if "=" in tok and not tok.startswith("N=")}
    case_b = (verdict_tokens == {"green", "partial", "no-progress", "regressed", "unscored"}
              and "green=1" in gr_line and "regressed=1" in gr_line
              and "peak_occupancy_tokens" not in gr_line and "cumulative_occupancy_tokens" not in gr_line)
    ok = ok and case_b
    print(f"  [{'PASS' if case_b else 'FAIL'}] green_restore_table lists exactly the five raw verdict/"
          "unscored counts side by side, never combined with each other or with either occupancy channel")
    return ok


def run_self_test() -> bool:
    print("report.py self-test (ADR 0013 — the PR6 empty-table regression, plus R-A1.3/R-F4.3's"
          " no-composite-field rule):")
    results = [
        _self_test_four_headers_on_empty_rows(),
        _self_test_no_composite_field(),
    ]
    ok = all(results)
    print("\nself-test: all cases passed" if ok else "\nSELF-TEST FAILED", file=sys.stderr if not ok else sys.stdout)
    return ok


# ---- CLI --------------------------------------------------------------

def parse_args(argv):
    """Manual parsing, stdlib only (decisions/0011) — mirrors derive.py's
    own `--experiment` flag exactly (task 5.8's convention, reused here).
    --self-test is flag-gated (ADR 0013) and never runs unconditionally."""
    experiment = "tool-surface-v1"
    self_test = False
    i = 0
    while i < len(argv):
        if argv[i] == "--experiment":
            if i + 1 >= len(argv):
                print("--experiment requires a value", file=sys.stderr)
                sys.exit(2)
            experiment = argv[i + 1]
            i += 2
        elif argv[i] == "--self-test":
            self_test = True
            i += 1
        else:
            print(f"unknown argument: {argv[i]!r}", file=sys.stderr)
            sys.exit(2)
    return experiment, self_test


def main():
    experiment, self_test = parse_args(sys.argv[1:])
    if self_test:
        return 0 if run_self_test() else 1
    if experiment not in EXPERIMENTS:
        print(f"unknown --experiment {experiment!r}; known: {sorted(EXPERIMENTS)}", file=sys.stderr)
        return 2
    reg = EXPERIMENTS[experiment]

    rows = load_rows(reg["runs_path"])
    if not rows:
        print(f"no rows found at {reg['runs_path'].relative_to(REPO_ROOT)} — "
              f"run rig/derive.py --experiment {experiment} first.")
        return 0

    return reg["report_fn"](rows)


if __name__ == "__main__":
    sys.exit(main())
