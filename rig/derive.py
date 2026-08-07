#!/usr/bin/env python3
"""rig/derive.py — a TOTAL, deterministic function from run directories to
rig/results/<experiment>/runs.jsonl.

"Total" is load-bearing (sdd/measurement-rig/design.md, Decision 6): this
script never appends and never remembers what it wrote last time. It reads
every run directory under rig/runs/<experiment>/ from scratch and rebuilds
the whole file, sorted by run_id. That is what makes double-counting
structurally impossible instead of merely defended against — there is no
"already written" state to get out of sync with reality.

It never decides task outcome by trusting what run.sh or the invocation
*intended*. Every claim is read back from the transcript itself
(design.md, Decision 7): the visible tool surface is compared against the
committed preimage in rig/surfaces/<arm>.txt, never against a flag string —
a flag string always matches itself, which is exactly how an ineffective
--disallowedTools value would go unnoticed.

STDLIB ONLY: json, hashlib, statistics (unused here, kept for report.py's
sake is a separate file), pathlib, re. No pip, no venv (decisions/0011).

Constraint this script accepts rather than works around: raw run captures
live under the gitignored rig/runs/ and are retained locally by whoever ran
them (decisions/0011's boundary section). Running this on a machine that
does not have all the raw captures a committed runs.jsonl was built from
will rebuild a SMALLER file. That is the total-function contract working
as designed, not a bug — but it means derive.py must be run on the machine
holding the raw evidence, never blindly on a fresh clone.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = 1
REPO_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT = "tool-surface-v1"
FIXTURE_ROOT = REPO_ROOT / "rig/fixtures/tool-surface/v1"
SURFACES_ROOT = REPO_ROOT / "rig/surfaces"
RUNS_ROOT = REPO_ROOT / "rig/runs" / EXPERIMENT
RESULTS_DIR = REPO_ROOT / "rig/results" / EXPERIMENT
RUN_ID_RE = re.compile(r"^(t[123])-(broad|scoped)-([0-9][A-Za-z0-9]*)$")
# mktemp -d "$TMPDIR/rig-workspace.XXXXXX" (run.sh) — exactly 6 template
# chars. This is a SHAPE check, not an exact-path check: run.sh does not
# persist the workspace path it generated, so derive.py cannot compare
# against the real one after the fact. Checking the shape is the honest
# substitute — disclosed here rather than silently treated as equivalent.
WORKSPACE_NAME_RE = re.compile(r"^rig-workspace\.[A-Za-z0-9]{6}$")
CHECKER_DIGEST = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def surface_digest(names) -> str:
    """Same function applied to a committed preimage AND to an observed
    init.tools list — the only way the comparison catches a flag that
    looked right but did nothing (design.md Decision 7)."""
    return sha256_hex("\n".join(sorted(set(names))).encode())


def load_surface(arm: str):
    return sorted(l.strip() for l in (SURFACES_ROOT / f"{arm}.txt").read_text().splitlines() if l.strip())


def load_answer_keys():
    keys = {}
    ak_dir = FIXTURE_ROOT / "answer-key"
    if ak_dir.is_dir():
        for f in sorted(ak_dir.glob("*.json")):
            data = json.loads(f.read_text())
            keys[data["task_id"]] = data
    return keys


def fixture_digest() -> str:
    manifest = FIXTURE_ROOT / "MANIFEST.sha256"
    return sha256_hex(manifest.read_bytes()) if manifest.is_file() else None


# ---- transcript parsing (best-effort; never trusts what was intended) ----

def parse_stream(path: Path, truncated_tail_expected: bool):
    """Returns (init_event, tool_calls, hook_names, result_event, anomalies).

    tool_calls: [{"name": str, "target": str|None, "is_error": bool}, ...]
    target is resolved in memory for matching only — never written to a row
    (design.md's cwd rule extends to any other path-shaped tool input).
    """
    init_event, result_event = None, None
    hook_names = set()
    tool_calls = []
    anomalies = []
    if not path.is_file():
        return None, [], set(), None, ["missing-result"]

    lines = [l for l in path.read_bytes().split(b"\n") if l.strip()]
    parsed = []
    for i, raw in enumerate(lines):
        try:
            parsed.append(json.loads(raw))
        except Exception:
            is_last = i == len(lines) - 1
            if is_last and truncated_tail_expected:
                continue  # tolerated exactly once, on a timed-out run only
            anomalies.append("unparseable-stream")

    by_tool_use_id = {}
    for ev in parsed:
        t = ev.get("type")
        if t == "system" and ev.get("subtype") == "init":
            init_event = ev
        elif t == "system" and ev.get("subtype") == "hook_started":
            hook_names.add(ev.get("hook_name"))
        elif t == "result":
            result_event = ev
        elif t == "rate_limit_event":
            info = ev.get("rate_limit_info", {})
            if info.get("status") != "allowed" or info.get("overageStatus") not in ("allowed", None):
                anomalies.append("rate-limit")
        elif t == "assistant":
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    by_tool_use_id[block["id"]] = block
        elif t == "user":
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") == "tool_result" and block.get("tool_use_id") in by_tool_use_id:
                    tu = by_tool_use_id.pop(block["tool_use_id"])
                    tool_calls.append({
                        "name": tu.get("name"),
                        "target": resolve_target(tu, block, init_event),
                        "is_error": bool(block.get("is_error", False)),
                    })
    # Any tool_use never paired with a tool_result (e.g. transcript cut by a
    # kill) still counts toward forbidden/off-set accounting — the call was
    # made, whether or not its result survived.
    for tu in by_tool_use_id.values():
        tool_calls.append({"name": tu.get("name"), "target": None, "is_error": False})
    return init_event, tool_calls, hook_names, result_event, anomalies


def resolve_target(tool_use, tool_result_block, init_event):
    """Best-effort file this tool call targeted, relative to the run's cwd.
    Only Read and Grep are given evidentiary weight by the practice check
    (spec R-A1's practice-check rule) — Glob's result is still useful for
    forbidden/off-set accounting but is never asked to prove a Read/Grep
    happened."""
    name = tool_use.get("name")
    cwd = (init_event or {}).get("cwd")
    if name == "Read":
        fp = tool_use.get("input", {}).get("file_path")
        if fp and cwd and fp.startswith(cwd):
            return str(Path(fp).relative_to(cwd).as_posix())
        return fp
    if name == "Grep":
        p = tool_use.get("input", {}).get("path")
        if p and not any(c in p for c in "*?[]"):
            return p
        result = tool_result_block.get("content")
        # The CLI has been observed to also carry a richer structured
        # result outside message.content; not exercised by any real Grep
        # call captured so far (t1 never needed one) — documented gap, not
        # invented behaviour.
        if isinstance(result, list) and result:
            return result[0] if isinstance(result[0], str) else None
    return None


# ---- the two checkers (outcome, practice) ---------------------------------

DEFECT_LINE_RE = re.compile(r"^[\w/.\-]+:\d+$")


def check_outcome(final_text: str, answer_key: list) -> bool:
    if final_text is None:
        return False
    reported = [l for l in final_text.splitlines() if DEFECT_LINE_RE.match(l)]
    expected = {f"{d['path']}:{d['line']}" for d in answer_key}
    return set(reported) == expected and len(reported) == len(expected)


def check_practice(tool_calls, reported_paths, expected, off_set):
    universe = set(expected) | set(off_set)
    offset_calls = sum(1 for tc in tool_calls if tc["name"] in off_set)
    forbidden_calls = sum(1 for tc in tool_calls if tc["name"] not in universe)
    matched = {tc["target"] for tc in tool_calls if tc["name"] in ("Read", "Grep") and tc["target"]}
    practice_pass = forbidden_calls == 0 and all(p in matched for p in reported_paths)
    return offset_calls, forbidden_calls, practice_pass


def check_practice_self_test(synthetic_tool_uses, reported_paths, expected, off_set):
    """The checker_self_test fragments carry only {name, is_error} — no
    file_path/target, because they exist to prove the forbidden/off-set
    scan and the "no Read/Grep at all" case fire, not to re-prove file-level
    resolution (that is exercised by every real Read in production rows).
    Simplification is intentional and disclosed, not invented: a Read/Grep
    call anywhere in the fragment is treated as evidence for every reported
    path, since these fixtures always have exactly one file in play."""
    universe = set(expected) | set(off_set)
    offset_calls = sum(1 for tu in synthetic_tool_uses if tu["name"] in off_set)
    forbidden_calls = sum(1 for tu in synthetic_tool_uses if tu["name"] not in universe)
    saw_read_or_grep = any(tu["name"] in ("Read", "Grep") for tu in synthetic_tool_uses)
    practice_pass = forbidden_calls == 0 and (not reported_paths or saw_read_or_grep)
    return offset_calls, forbidden_calls, practice_pass


def classify(outcome_pass: bool, practice_pass: bool) -> str:
    if outcome_pass and practice_pass:
        return "proper"
    if outcome_pass and not practice_pass:
        return "improper-success"
    if not outcome_pass and practice_pass:
        return "clean-failure"
    return "failure"


# ---- R-A1.4: every detector must be proven able to fire -------------------

def run_self_tests(answer_keys) -> bool:
    ok = True
    print("checker self-test (R-A1.4 — each detector must be observed to fire):")
    for task_id, ak in sorted(answer_keys.items()):
        cases = ak.get("checker_self_test", {})
        expected, off_set = ak["tool_sets"]["expected"], ak["tool_sets"]["off_set"]
        for case_name, case in cases.items():
            if case_name.startswith("_"):
                continue
            synth = case["synthetic_tool_uses"]
            reported = case["reported_defect_lines"]
            offset_calls, forbidden_calls, practice_pass = check_practice_self_test(synth, reported, expected, off_set)
            checks = []
            if "expected_practice_pass" in case:
                checks.append(("practice_pass", practice_pass, case["expected_practice_pass"]))
            if "expected_offset_calls" in case:
                checks.append(("offset_calls", offset_calls, case["expected_offset_calls"]))
            if "expected_forbidden_calls" in case:
                checks.append(("forbidden_calls", forbidden_calls, case["expected_forbidden_calls"]))
            if "expected_cell_if_outcome_pass" in case:
                checks.append(("cell_if_outcome_pass", classify(True, practice_pass), case["expected_cell_if_outcome_pass"]))
            case_ok = all(actual == want for _, actual, want in checks)
            ok = ok and case_ok
            status = "PASS" if case_ok else "FAIL"
            print(f"  [{status}] {task_id}/{case_name}: " + ", ".join(f"{k}={a!r} (want {w!r})" for k, a, w in checks))
    return ok


# ---- one run directory -> one row -----------------------------------------

def build_row(run_dir: Path, surfaces, digests, answer_keys):
    m = RUN_ID_RE.match(run_dir.name)
    if not m:
        return None
    task_id, arm, iteration = m.groups()

    status_path = run_dir / "status.json"
    if not status_path.is_file():
        # run.sh always writes status.json before every exit path it
        # controls; a directory with none is one it never finished
        # claiming (Decision 6 orphans these on the NEXT invocation, not
        # here). Recorded as void rather than silently dropped.
        status = {"state": "void", "void_reason": "missing-status", "exit_code": None,
                   "timed_out": False, "truncated_tail": False, "wall_ms": None,
                   "timeout_s": None, "code_commit": None, "driver_version": None,
                   "python_version": None}
    else:
        status = json.loads(status_path.read_text())

    prompt_path = run_dir / "prompt.txt"
    prompt_sha256 = sha256_hex(prompt_path.read_bytes()) if prompt_path.is_file() else None

    init_event, tool_calls, hook_names, result_event, stream_anomalies = parse_stream(
        run_dir / "stream.jsonl", status.get("truncated_tail", False)
    )

    state = status["state"]
    void_reason = status.get("void_reason")
    anomaly_classes = set(stream_anomalies)

    tool_surface_sha256 = model = permission_mode = cwd_is_expected = None
    mcp_server_count = tool_count = num_turns = None

    if init_event:
        tools = init_event.get("tools", [])
        tool_surface_sha256 = surface_digest(tools)
        tool_count = len(tools)
        model = init_event.get("model")
        permission_mode = init_event.get("permissionMode")
        mcp_server_count = len(init_event.get("mcp_servers", []))
        cwd = init_event.get("cwd", "")
        cwd_is_expected = bool(WORKSPACE_NAME_RE.match(Path(cwd).name)) if cwd else False

    # derive.py's own read-back verification only applies to a run run.sh
    # itself believed complete — it can only ever DOWNGRADE complete to
    # void, never upgrade a void/failed run.sh already gave up on
    # (design.md Decision 7 layers on top of, and never overrides
    # downward, run.sh's mechanical result-event check).
    if state == "complete":
        if not init_event or not result_event:
            state, void_reason = "void", "missing-result"
        elif tool_surface_sha256 != surface_digest(surfaces[arm]):
            state, void_reason = "void", "surface-mismatch"
            anomaly_classes.add("surface-mismatch")
        elif model not in (result_event.get("modelUsage") or {}):
            state, void_reason = "void", "model-mismatch"
            anomaly_classes.add("model-mismatch")
        elif not cwd_is_expected:
            state, void_reason = "void", "cwd-mismatch"
            anomaly_classes.add("cwd-mismatch")
        elif result_event.get("stop_reason") != "end_turn":
            state, void_reason = "void", "non-end-turn"
            anomaly_classes.add("non-end-turn")
        elif anomaly_classes:
            # A run that parsed clean up to here but tripped a stream-level
            # anomaly (unparseable line, a real rate-limit hit) still voids
            # — spec's void list names both explicitly.
            state, void_reason = "void", sorted(anomaly_classes)[0]

    outcome_pass = practice_pass = classification = over_ceiling = None
    offset_calls = forbidden_calls = None
    ak = answer_keys.get(task_id)
    if state == "complete" and ak:
        final_text = result_event.get("result")
        outcome_pass = check_outcome(final_text, ak["answer_key"])
        reported_lines = [l for l in (final_text or "").splitlines() if DEFECT_LINE_RE.match(l)]
        # rsplit on the LAST ':' — a defect line is "<path>:<line-number>"
        # and the practice check needs the path alone to compare against a
        # tool call's target (which never carries a line number).
        reported_paths = [l.rsplit(":", 1)[0] for l in reported_lines]
        offset_calls, forbidden_calls, practice_pass = check_practice(
            tool_calls, reported_paths, ak["tool_sets"]["expected"], ak["tool_sets"]["off_set"]
        )
        classification = classify(outcome_pass, practice_pass)
        t_task = 2 * (len(ak["answer_key"]) + 2) + 1
        over_ceiling = (result_event.get("num_turns") or 0) > t_task

    if result_event:
        num_turns = result_event.get("num_turns")

    row = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_dir.name,
        "experiment": EXPERIMENT,
        "task_id": task_id,
        "arm": arm,
        "iteration": iteration,
        "model": model,
        "harness_version": status.get("driver_version"),
        "python": status.get("python_version"),
        "prompt_sha256": prompt_sha256,
        "tool_surface_sha256": tool_surface_sha256,
        "tool_count": tool_count,
        "fixture_version": "v1",
        "fixture_digest": digests["fixture"],
        "checker_digest": digests["checker"],
        "code_commit": status.get("code_commit"),
        "cwd_is_expected": cwd_is_expected,
        "permission_mode": permission_mode,
        "mcp_server_count": mcp_server_count,
        "state": state,
        "void_reason": void_reason,
        "truncated_tail": bool(status.get("truncated_tail")),
        "num_turns": num_turns,
        "over_ceiling": over_ceiling,
        "wall_ms": status.get("wall_ms"),
        "total_cost_usd": (result_event or {}).get("total_cost_usd"),
        "input_tokens": (result_event or {}).get("usage", {}).get("input_tokens"),
        "output_tokens": (result_event or {}).get("usage", {}).get("output_tokens"),
        "cache_creation_input_tokens": (result_event or {}).get("usage", {}).get("cache_creation_input_tokens"),
        "cache_read_input_tokens": (result_event or {}).get("usage", {}).get("cache_read_input_tokens"),
        "stop_reason": (result_event or {}).get("stop_reason"),
        "permission_denials": (result_event or {}).get("permission_denials", []),
        "tool_calls": [{"name": tc["name"], "is_error": tc["is_error"]} for tc in tool_calls],
        "offset_calls": offset_calls,
        "forbidden_calls": forbidden_calls,
        "outcome_pass": outcome_pass,
        "practice_pass": practice_pass,
        "classification": classification,
        "anomaly_classes": sorted(anomaly_classes),
    }
    return row, permission_mode, mcp_server_count, sorted(hook_names)


def apply_ambient_drift_pairing(built):
    """Design.md Decision 7's ambient-drift row is a PAIRED claim
    (permissionMode / mcp_servers / hook_started must match ACROSS the
    arms of one cell), unlike every other read-back check which is a
    property of one run alone. Done as a second pass over everything
    build_row already computed, so derive.py stays one total function
    rather than needing a live counterpart at parse time."""
    by_slot = {}
    for row, pmode, mcp_count, hooks in built:
        by_slot.setdefault((row["task_id"], row["iteration"]), []).append((row, pmode, mcp_count, hooks))
    for slot_rows in by_slot.values():
        if len(slot_rows) != 2:
            continue
        (r1, p1, m1, h1), (r2, p2, m2, h2) = slot_rows
        if r1["state"] != "complete" or r2["state"] != "complete":
            continue
        if (p1, m1, h1) != (p2, m2, h2):
            for r in (r1, r2):
                r["state"] = "void"
                r["void_reason"] = "ambient-drift"
                r["outcome_pass"] = r["practice_pass"] = r["classification"] = None
                r["over_ceiling"] = None


def main():
    answer_keys = load_answer_keys()
    if not run_self_tests(answer_keys):
        print("\nSelf-test FAILED — a detector cannot be proven to fire. Refusing to derive rows.", file=sys.stderr)
        return 1

    surfaces = {"broad": load_surface("broad"), "scoped": load_surface("scoped")}
    digests = {"fixture": fixture_digest(), "checker": CHECKER_DIGEST}

    run_dirs = sorted(p for p in RUNS_ROOT.glob("*") if p.is_dir()) if RUNS_ROOT.is_dir() else []
    built = []
    for run_dir in run_dirs:
        result = build_row(run_dir, surfaces, digests, answer_keys)
        if result:
            built.append(result)

    apply_ambient_drift_pairing(built)

    rows = sorted((b[0] for b in built), key=lambda r: r["run_id"])
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "runs.jsonl"
    with out_path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True))
            f.write("\n")

    print(f"\nderived {len(rows)} row(s) from {len(run_dirs)} run dir(s) -> {out_path.relative_to(REPO_ROOT)}")
    for row in rows:
        print(f"  {row['run_id']}: state={row['state']}"
              + (f" ({row['void_reason']})" if row["void_reason"] else "")
              + (f" classification={row['classification']}" if row["classification"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
