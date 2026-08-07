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

STDLIB ONLY (decisions/0011): json, statistics, pathlib.
"""

import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT = "tool-surface-v1"
RUNS_PATH = REPO_ROOT / "rig/results" / EXPERIMENT / "runs.jsonl"
INSTRUMENT_DOUBT_THRESHOLD = 3  # X = 3, spec's instrument-doubt rule


def load_rows():
    if not RUNS_PATH.is_file():
        return []
    return [json.loads(l) for l in RUNS_PATH.read_text().splitlines() if l.strip()]


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


def main():
    rows = load_rows()
    if not rows:
        print(f"no rows found at {RUNS_PATH.relative_to(REPO_ROOT)} — run rig/derive.py first.")
        return 0

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


if __name__ == "__main__":
    sys.exit(main())
