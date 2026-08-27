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
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCHEMA_VERSION = 3  # v3: added model_turns, occupancy_series, peak_occupancy_tokens,
# peak_occupancy_turn, cumulative_occupancy_tokens, occupancy_aggregate_matches,
# occupancy_is_monotone, context_window_tokens (failure-flood-triage spec
# R-F5.1-5.4, design.md Decision 1). Same no-migrations rule as v2 (design.md
# Decision 8): re-deriving rewrites every existing row with this version and
# the eight new fields; nothing here reads the old value of schema_version to
# special-case anything.
REPO_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT = "tool-surface-v1"
# Fixture location is additively versioned per task_id (design.md Decision 4:
# a fixture change is a new vN/ directory, never an edit to an existing one).
# t3v2 is tier 3's discriminating rebuild; t1/t2/t3 stay on v1 — the version a
# task_id names is fixed at the moment that task_id is introduced.
FIXTURE_VERSIONS = {"t1": "v1", "t2": "v1", "t3": "v1", "t3v2": "v2"}
FIXTURE_ROOTS = {
    v: REPO_ROOT / "rig/fixtures/tool-surface" / v
    for v in sorted(set(FIXTURE_VERSIONS.values()))
}
SURFACES_ROOT = REPO_ROOT / "rig/surfaces"
RUNS_ROOT = REPO_ROOT / "rig/runs" / EXPERIMENT
RESULTS_DIR = REPO_ROOT / "rig/results" / EXPERIMENT
RUN_ID_RE = re.compile(r"^(t[123]|t3v2)-(broad|scoped)-([0-9][A-Za-z0-9]*)$")

# A control slot: iteration `0c<n>`. Still a digit-initial iteration, so the run_id
# grammar is unchanged.
#
# Controls exist to make a detector FIRE (spec R-A1.4), so their anomalies are
# deliberate. Counting them toward the X=3 instrument-doubt threshold means running
# your own controls disables your experiment — observed, not theorised: two
# deliberate surface-mismatch controls plus two genuine ones reached 4 and tripped
# the threshold that blocks any theory/ write.
#
# So a control's anomalies are reported in their own bucket and never in the
# instrument-doubt count. The inversion that matters: a control which does NOT void
# is itself the alarm, because a detector that cannot fire makes every passing run
# meaningless.
CONTROL_ITERATION_RE = re.compile(r"^0c[0-9]+$")
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
    """Tool names only. `# harness: <version>` header is metadata, not a tool."""
    lines = (SURFACES_ROOT / f"{arm}.txt").read_text().splitlines()
    return sorted(l.strip() for l in lines if l.strip() and not l.startswith("#"))


def surface_harness(arm: str):
    """The CLI version this preimage was captured under, or None.

    The visible tool surface is NOT stable across CLI versions — observed:
    2.1.224 shipped `ListAgents` and every run against a 31-tool preimage voided
    surface-mismatch. That reason is diagnostically wrong: the runs were fine and
    the preimage was stale, which is a different problem with a different fix.
    """
    for l in (SURFACES_ROOT / f"{arm}.txt").read_text().splitlines():
        if l.startswith("# harness:"):
            return l.split(":", 1)[1].strip()
    return None


def load_answer_keys():
    """Reads every fixture version's own answer-key/ dir. Task ids are
    disjoint across versions (t1/t2/t3 in v1, t3v2 in v2), so merging into
    one dict keyed by task_id is safe — this is not the aggregation that
    design.md's fixture_digest-mismatch guard forbids, because no two
    versions ever share a task_id."""
    keys = {}
    for root in FIXTURE_ROOTS.values():
        ak_dir = root / "answer-key"
        if ak_dir.is_dir():
            for f in sorted(ak_dir.glob("*.json")):
                data = json.loads(f.read_text())
                keys[data["task_id"]] = data
    return keys


def fixture_digest(version: str) -> str:
    manifest = FIXTURE_ROOTS[version] / "MANIFEST.sha256"
    return sha256_hex(manifest.read_bytes()) if manifest.is_file() else None


# ---- transcript parsing (best-effort; never trusts what was intended) ----

def parse_stream(path: Path, truncated_tail_expected: bool):
    """Returns (init_event, tool_calls, hook_names, result_event, anomalies, turns).

    tool_calls: [{"name": str, "target": str|None, "is_error": bool}, ...]
    target is resolved in memory for matching only — never written to a row
    (design.md's cwd rule extends to any other path-shaped tool input).

    turns: [(message_id, usage_dict), ...], stream order, de-duplicated by
    `message.id` keeping the FIRST occurrence (spec R-F5.1, design.md
    Decision 1). One model turn emits several `assistant` events that echo
    the same `message.usage` byte-for-byte — verified on sampled captures
    (14 events / 4 turns in one, 6 events / 3 turns in another) — so summing
    per event rather than per de-duplicated turn over-counts occupancy
    roughly 3.5x.
    """
    init_event, result_event = None, None
    hook_names = set()
    tool_calls = []
    anomalies = []
    turns = []
    if not path.is_file():
        return None, [], set(), None, ["missing-result"], []

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
    seen_message_ids = set()
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
            msg = ev.get("message", {})
            mid = msg.get("id")
            if mid is not None and mid not in seen_message_ids:
                seen_message_ids.add(mid)
                turns.append((mid, msg.get("usage") or {}))
            for block in msg.get("content", []):
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
    return init_event, tool_calls, hook_names, result_event, anomalies, turns


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


# ---- runway channels: peak and cumulative occupancy (spec R-F5.1-5.4) -----

def compute_occupancy(turns, result_event, model):
    """Peak/cumulative occupancy from the de-duplicated per-turn `assistant`
    usage `parse_stream` already built (design.md Decision 1).

    Why `input + cache_read + cache_creation` is the occupancy proxy: those
    three fields partition one turn's prompt, so their sum is the prompt
    size regardless of cache state. Output tokens are excluded from
    occupancy and counted once, as the next turn's input — nothing is
    double-counted (design.md line 80-83).

    `occupancy_aggregate_matches` is the R-A1.4 proof this channel can fire
    with no new run: `occupancy_series` is summed here from the
    de-duplicated per-turn walk, and independently compared against
    `result_event["usage"]`, which the CLI already aggregates over every
    turn (verified arithmetically: 141134 = 16602+39942+40854+43736 on one
    capture, 97170 = 16602+39833+40735 on another). Two paths to one number;
    disagreement is the anomaly.

    `cumulative_occupancy_tokens` is the sum over de-duplicated turns of the
    same occupancy quantity, **plus** output tokens (spec R-F5.2) — output
    tokens are taken from `result_event["usage"]` directly (already an
    aggregate over every turn) rather than re-summed per turn, because the
    CLI streams several partial `assistant` events per turn and only the
    LAST one carries that turn's final output_tokens count; de-duplicating
    by keeping the FIRST occurrence (correct for occupancy, whose per-turn
    value is stable across duplicates) would under-count output_tokens.
    """
    series = []
    for _mid, usage in turns:
        occ = ((usage.get("input_tokens") or 0)
               + (usage.get("cache_read_input_tokens") or 0)
               + (usage.get("cache_creation_input_tokens") or 0))
        series.append(occ)

    model_turns = len(turns)
    peak_occupancy_tokens = max(series) if series else None
    # 1-indexed, first occurrence on a tie — matches the human-facing "turn N".
    peak_occupancy_turn = series.index(peak_occupancy_tokens) + 1 if series else None
    occupancy_is_monotone = all(series[i] <= series[i + 1] for i in range(len(series) - 1)) if series else None

    cumulative_occupancy_tokens = occupancy_aggregate_matches = None
    if result_event is not None:
        result_usage = result_event.get("usage") or {}
        result_input_side = ((result_usage.get("input_tokens") or 0)
                              + (result_usage.get("cache_read_input_tokens") or 0)
                              + (result_usage.get("cache_creation_input_tokens") or 0))
        occupancy_aggregate_matches = sum(series) == result_input_side
        cumulative_occupancy_tokens = sum(series) + (result_usage.get("output_tokens") or 0)

    context_window_tokens = None
    if result_event is not None and model is not None:
        model_usage = (result_event.get("modelUsage") or {}).get(model) or {}
        context_window_tokens = model_usage.get("contextWindow")

    return {
        "model_turns": model_turns,
        "occupancy_series": series,
        "peak_occupancy_tokens": peak_occupancy_tokens,
        "peak_occupancy_turn": peak_occupancy_turn,
        "cumulative_occupancy_tokens": cumulative_occupancy_tokens,
        "occupancy_aggregate_matches": occupancy_aggregate_matches,
        "occupancy_is_monotone": occupancy_is_monotone,
        "context_window_tokens": context_window_tokens,
    }


# ---- the two checkers (outcome, practice) ---------------------------------

DEFECT_LINE_RE = re.compile(r"^[\w/.\-]+:\d+$")


def check_outcome(final_text: str, answer_key: list):
    """Returns (outcome_pass, defects_found, defects_missed, defects_extra).

    outcome_pass keeps its original all-or-nothing meaning (exact line set,
    no missing line, no extra line, no duplicate). The three counts are a
    SEPARATE recall/precision signal, spelled out per spec R-A1.3: never
    summed or weighted into a score here or by any caller — a task with
    several seeded defects needs found/missed/extra to be distinguishable
    from a single pass/fail bit, which is exactly what a fixture with only
    one defect could never expose."""
    if final_text is None:
        return False, None, None, None
    reported = [l for l in final_text.splitlines() if DEFECT_LINE_RE.match(l)]
    reported_set = set(reported)
    expected_set = {f"{d['path']}:{d['line']}" for d in answer_key}
    outcome_pass = reported_set == expected_set and len(reported) == len(expected_set)
    defects_found = len(expected_set & reported_set)
    defects_missed = len(expected_set - reported_set)
    defects_extra = len(reported_set - expected_set)
    return outcome_pass, defects_found, defects_missed, defects_extra


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
        # tool_sets (expected/off_set) is tool-surface-v1's own answer-key
        # shape; failure-flood's answer keys (task 5.8) carry C/F0/S0/R0
        # instead and define no checker_self_test at all — skip rather than
        # crash. This is a pure generalisation: every existing tool-surface
        # answer key already has tool_sets, so this branch never changes
        # behaviour for that experiment.
        if "tool_sets" not in ak:
            continue
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

    init_event, tool_calls, hook_names, result_event, stream_anomalies, turns = parse_stream(
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

    # Occupancy is a property of the de-duplicated turn walk and the result
    # event alone — computed unconditionally, ahead of the state/void checks
    # below, since none of them depend on it and it never downgrades state.
    occupancy = compute_occupancy(turns, result_event, model)

    # derive.py's own read-back verification only applies to a run run.sh
    # itself believed complete — it can only ever DOWNGRADE complete to
    # void, never upgrade a void/failed run.sh already gave up on
    # (design.md Decision 7 layers on top of, and never overrides
    # downward, run.sh's mechanical result-event check).
    if state == "complete":
        if not init_event or not result_event:
            state, void_reason = "void", "missing-result"
        elif (sh := surface_harness(arm)) is not None and status.get("driver_version") and sh != status["driver_version"]:
            # The preimage predates this CLI. Distinct from surface-mismatch: the
            # run is not at fault and re-running will not help — the preimage needs
            # recapturing under this version.
            state, void_reason = "void", "surface-preimage-stale"
            anomaly_classes.add("surface-preimage-stale")
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
    defects_found = defects_missed = defects_extra = None
    ak = answer_keys.get(task_id)
    if state == "complete" and ak:
        final_text = result_event.get("result")
        outcome_pass, defects_found, defects_missed, defects_extra = check_outcome(final_text, ak["answer_key"])
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

    fixture_version = FIXTURE_VERSIONS.get(task_id, "v1")

    row = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_dir.name,
        "experiment": EXPERIMENT,
        "task_id": task_id,
        "arm": arm,
        "iteration": iteration,
        "is_control": bool(CONTROL_ITERATION_RE.match(iteration)),
        "model": model,
        "harness_version": status.get("driver_version"),
        "python": status.get("python_version"),
        "prompt_sha256": prompt_sha256,
        "tool_surface_sha256": tool_surface_sha256,
        "tool_count": tool_count,
        "fixture_version": fixture_version,
        "fixture_digest": digests["fixture"].get(fixture_version),
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
        # Runway channels (spec R-F5.1-5.4, design.md Decision 1): peak from a
        # de-duplicated per-turn walk, cumulative independently cross-checked
        # against the aggregate the CLI already reports on result_event.usage.
        "model_turns": occupancy["model_turns"],
        "occupancy_series": occupancy["occupancy_series"],
        "peak_occupancy_tokens": occupancy["peak_occupancy_tokens"],
        "peak_occupancy_turn": occupancy["peak_occupancy_turn"],
        "cumulative_occupancy_tokens": occupancy["cumulative_occupancy_tokens"],
        "occupancy_aggregate_matches": occupancy["occupancy_aggregate_matches"],
        "occupancy_is_monotone": occupancy["occupancy_is_monotone"],
        "context_window_tokens": occupancy["context_window_tokens"],
        "stop_reason": (result_event or {}).get("stop_reason"),
        "permission_denials": (result_event or {}).get("permission_denials", []),
        "tool_calls": [{"name": tc["name"], "is_error": tc["is_error"]} for tc in tool_calls],
        "offset_calls": offset_calls,
        "forbidden_calls": forbidden_calls,
        "outcome_pass": outcome_pass,
        # Recall/precision as three separate counts (spec R-A1.3: never
        # summed or weighted into one score, here or by any caller). A task
        # with several seeded defects needs these to be distinguishable from
        # the single outcome_pass bit above.
        "defects_found": defects_found,
        "defects_missed": defects_missed,
        "defects_extra": defects_extra,
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
                r["defects_found"] = r["defects_missed"] = r["defects_extra"] = None


# ---- task 5.8: --experiment dispatcher, per-experiment registry ----------
# design.md sec 6: "the deciding argument is the slice order, not taste:
# slice 1 already edits derive.py for the occupancy fields, and its
# verification is the 42-row projection check. By the time slice 4 needs the
# dispatcher, that check exists and re-runs." `build_row` (tool-surface-v1's
# own row builder) is UNTOUCHED by this section — not restructured, not
# renamed, not re-signatured — so the projection regression has nothing new
# to explain if it fails.

def fixture_digest_at(root: Path):
    """Same convention as fixture_digest() above, generalised to an
    arbitrary root — fixture_digest() itself stays untouched (it is
    tool-surface-v1's own hardcoded FIXTURE_ROOTS lookup) so nothing that
    already calls it can observe a behaviour change."""
    manifest = root / "MANIFEST.sha256"
    return sha256_hex(manifest.read_bytes()) if manifest.is_file() else None


def answer_key_set_digest(root: Path):
    """Face A's digest (run-input-provenance spec R-P2, design.md secs 1/2):
    set-wide over the answer-key/ relpaths of ONE fixture root, never the
    merged load_failure_flood_answer_keys() dict — a run only ever ran
    against one root, and this must be comparable to what a runner (which
    also only ever sees one root) can compute. Mirrors fixture_digest_at()'s
    shape: an arbitrary root, None when there is nothing under it to digest.

    This is a genuine cross-language pair with rig/run-pipeline.sh's
    existing hash_paths(): sorted "sha256(content)  relpath" lines, joined
    by a single newline, then hashed. Reproduced here rather than invented,
    so the two sides can only ever disagree by drifting apart, never by
    starting from two different conventions. The relpath filter/exclusion
    (skip __pycache__/*.pyc) mirrors compute_manifest()'s own walk, which is
    what the runner side filters by prefix to build its own input list."""
    ak_dir = root / "answer-key"
    if not ak_dir.is_dir():
        return None
    rels = []
    for p in ak_dir.rglob("*"):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        rels.append(p.relative_to(root).as_posix())
    lines = [f"{sha256_hex((root / rel).read_bytes())}  {rel}" for rel in sorted(rels)]
    return sha256_hex("\n".join(lines).encode())


FAILURE_FLOOD_EXPERIMENT = "failure-flood-v1"
FAILURE_FLOOD_SCHEMA_VERSION = 4  # v4 (run-input-provenance): adds
# input_provenance_version (row), recorded_answer_key_digest (row, Sibling 1
# — Face A + WARNING-14, R-P2/R-P3/R-P4/R-P5), recorded_fixture_digest (row,
# Sibling 3 — Face B, R-P7), and each model step's
# recorded_surface_preimage_sha256 (per-step, Sibling 2 — Face C, R-P6; no
# deriver code needed for that one, steps are copied through by
# `step_out = dict(step)` below) — a run's own record of what it was scored
# against, read back and compared rather than recomputed live. Correction:
# the two prior siblings' own done-notes here said the other two fields
# stayed "null until" a not-yet-landed sibling; both are now wired, so this
# comment names the sibling that actually populated each field rather than
# leaving a stale forward reference. Same no-migrations rule as every prior
# bump (Decision 8, restated at v2->v3 below): re-deriving rewrites every
# existing row with this version and these fields; nothing here reads the
# old schema_version value to special-case a row's treatment (R-P11.1).
# v3: PR7B closes verify-report CRITICAL-1/-2.
# Added declared_model (row) + model_matches_declared (per step, read back
# from run-pipeline.sh's own write_step_status, mirroring
# permission_mode_matches_declared) and the model-mismatch void it can now
# trigger; and input_tokens/output_tokens/cache_creation_input_tokens/
# cache_read_input_tokens/tool_calls, per step AND per run (R-F7.3) — those
# landed at v2 (PR7A). v3 adds suite_state_cause (R-F2.2) and its
# suite-state-mismatch void, and populates causes_claimed/causes_correct
# (R-F3.2) from a real handoff file instead of a hardcoded None. Same
# no-migrations rule as tool-surface-v1's v2->v3 bump (design.md Decision 8):
# re-deriving rewrites every existing row with this version and these fields.
FAILURE_FLOOD_RUN_ID_RE = re.compile(r"^(s[12])-(monolithic|pipeline)-([0-9][A-Za-z0-9]*)$")
FAILURE_FLOOD_FIXTURE_VERSIONS = {"s1": "v1", "s2": "v2"}
FAILURE_FLOOD_FIXTURE_ROOTS = {
    v: REPO_ROOT / "rig/fixtures/failure-flood" / v
    for v in sorted(set(FAILURE_FLOOD_FIXTURE_VERSIONS.values()))
}
FAILURE_FLOOD_RUNS_ROOT = REPO_ROOT / "rig/runs" / FAILURE_FLOOD_EXPERIMENT
FAILURE_FLOOD_RESULTS_DIR = REPO_ROOT / "rig/results" / FAILURE_FLOOD_EXPERIMENT
# ONE preimage for BOTH arms and every role (R-F6.2: "identical across both
# arms and every role"; task 5.4) — unlike tool-surface-v1's per-arm broad/
# scoped preimages, there is exactly one file, rig/surfaces/failure-flood.txt.
FAILURE_FLOOD_SURFACE_ARM = "failure-flood"


def load_failure_flood_answer_keys():
    """Same shape and same disjoint-task_id safety argument as
    load_answer_keys() above (s1 lives only in v1, s2 only in v2), pointed
    at FAILURE_FLOOD_FIXTURE_ROOTS instead. These answer-key files carry no
    `checker_self_test` key — run_self_tests() already tolerates that
    (`.get("checker_self_test", {})` iterates zero cases), so nothing here
    needs a parallel self-test runner."""
    keys = {}
    for root in FAILURE_FLOOD_FIXTURE_ROOTS.values():
        ak_dir = root / "answer-key"
        if ak_dir.is_dir():
            for f in sorted(ak_dir.glob("*.json")):
                data = json.loads(f.read_text())
                # answer-key/ also carries prereg.json (Hard Ordering Gate
                # layer 2's own config, task 4.4) — a real fixture file, not
                # a task answer-key, and it has no task_id field. Skip it
                # rather than assume a filename; the next non-answer-key
                # *.json this directory gains should not need a new
                # exclusion here.
                if "task_id" not in data:
                    continue
                keys[data["task_id"]] = data
    return keys


def green_restore_verdict(observed_failures, f0_failures, ro_substrate_violation):
    """R-F4.2: four values, never composited. The integrity guard MUST reuse
    the runner's verified file-hash mutation check (spec's own words) —
    that check is task 5.5's ro_substrate_violation, read back here rather
    than reinvented as a second mechanism. observed_failures/f0_failures are
    `collection/1`-shaped lists of {"test_id": ...} (99-verify's own
    collection.json and the fixture's own F0 block share this schema).

    Ordering matters: a regression (integrity guard fired, or a failure
    appeared that was not in F0 — which, since C has zero failures by
    construction, R-F1.3, must have been passing in C) is checked BEFORE
    anything is called green or partial, per R-F4.2's own listed priority.
    """
    if ro_substrate_violation:
        return "regressed", False
    observed_ids = {f["test_id"] for f in observed_failures}
    f0_ids = {f["test_id"] for f in f0_failures}
    if observed_ids - f0_ids:
        return "regressed", True
    if not observed_ids:
        return "green", True
    if observed_ids < f0_ids:
        return "partial", True
    return "no-progress", True


_ROOT_CAUSE_LINE_RE = re.compile(r"^[\w/.\-]+:\d+$")


def parse_root_cause_report(text):
    """R-F3.1: line 1 MUST be the literal sentinel `ROOT-CAUSE-REPORT v1`;
    every following non-blank line MUST match `^[\\w/.\\-]+:\\d+$`, naming one
    claimed `path:line`; any other content anywhere makes the WHOLE file
    malformed (spec's own words, not inferred). Returns a frozenset of
    deduplicated claimed lines, or None when the text is missing entirely or
    fails either check — never raises, matching R-F3.2's own scenario ("A
    malformed report scores as no claims, not a crash")."""
    if text is None:
        return None
    lines = text.splitlines()
    if not lines or lines[0] != "ROOT-CAUSE-REPORT v1":
        return None
    claimed = set()
    for line in lines[1:]:
        if line.strip() == "":
            continue
        if not _ROOT_CAUSE_LINE_RE.match(line):
            return None
        claimed.add(line)
    return frozenset(claimed)


def score_diagnostic_attribution(report_text, rc_true):
    """R-F3.2 (CRITICAL-2, verify-report 2026-08-17): `claimed` = deduplicated
    set of valid lines (empty if malformed/missing, never a crash); `correct`
    = `claimed & rc_true`, where `rc_true` is `R0`'s own frozen `cause_site`
    set. Scored against spec.md's own frozen FILE format (R-F3.1) — never
    `result.result`'s chat prose, which is what design.md's now-stale ASCII
    diagram sketched before R-F3.1's exact format existed (implemented to
    spec.md's exact text, per this batch's own instruction, not to that
    older summary). `precision`/`recall` themselves are computed downstream,
    per (task_id, arm), by `report.py`'s own
    `diagnostic_precision_recall_table` (task 6.4) from these two lists plus
    the pre-existing `causes_present` field — `n/a`-when-`claimed`-is-empty
    is already implemented at that layer; this function's only job is the
    two sets. Returns (claimed_list, correct_list), both sorted for
    determinism."""
    claimed = parse_root_cause_report(report_text)
    if claimed is None:
        claimed = frozenset()
    correct = claimed & rc_true
    return sorted(claimed), sorted(correct)


def read_root_cause_report_handoff(run_dir, steps_meta):
    """Task 5.9 (re-scoped this batch): the handoff copy `run-pipeline.sh`
    now writes at each arm's own final model step (monolith's only step, or
    pipeline's apply step), mirroring the pre-existing `fix-plan.txt`
    handoff convention. Returns the raw text, or None when no step captured
    one — an old run captured before this threading existed, or a role this
    fixture's shared prompt file never reaches for this arm."""
    for step in steps_meta:
        step_name = step.get("index")
        if not step_name:
            continue
        candidate = run_dir / "steps" / step_name / "handoff" / "root-cause-report.txt"
        if candidate.is_file():
            return candidate.read_text()
    return None


def suite_state_cause(observed_suite_state, observed_failures, s0):
    """R-F2.2 (CRITICAL-1, verify-report 2026-08-17): `injection` iff the
    observed `suite_state` AND its normalized signature (when `suite_state
    != "ran"`, collect.py's own R-F2.3 synthetic `__suite__` failure)
    exactly match the frozen `S0` recorded during isolation validation
    before any prompt; `environment` otherwise. Both fixtures' frozen `S0`
    today is `"ran"` (measured before any injection could break suite
    startup — see `s1.json`/`s2.json`'s own `S0` blocks), so this collapses
    to a plain `suite_state` equality check for every row derivable today;
    the signature branch exists for a future fixture whose frozen baseline
    is itself `did-not-start`/`partial`, and stays conservative
    (`"environment"`) whenever no frozen signature is available to prove a
    match — the same "downgrade, never invent a match" discipline the
    read-back checks above already follow. Returns None when there is
    nothing to classify (no observed suite_state, or no frozen S0)."""
    if s0 is None or observed_suite_state is None:
        return None
    if observed_suite_state != s0.get("suite_state"):
        return "environment"
    if observed_suite_state == "ran":
        return "injection"
    frozen_signature = s0.get("signature")
    observed_signature = next(
        (f.get("signature") for f in observed_failures if f.get("test_id") == "__suite__"),
        None,
    )
    if frozen_signature is not None and observed_signature == frozen_signature:
        return "injection"
    return "environment"


def build_row_failure_flood(run_dir: Path, surfaces, digests, answer_keys):
    m = FAILURE_FLOOD_RUN_ID_RE.match(run_dir.name)
    if not m:
        return None
    task_id, arm, iteration = m.groups()

    arm_path = run_dir / "arm.json"
    if arm_path.is_file():
        arm_data = json.loads(arm_path.read_text())
    else:
        # run-pipeline.sh's own Amendment 1 flushes arm.json before every
        # exit path reachable after the run directory is claimed; a
        # directory with none never got that far.
        arm_data = {}

    # State/void_reason are read from the small per-run status.json, the
    # SAME convention build_row (tool-surface-v1) already uses (`status_path
    # = run_dir / "status.json"`) — never from arm.json's own copy of the
    # same two fields, which is authoritative for everything ELSE
    # (evidence/steps) but is a run-pipeline.sh addition this file predates
    # for older run directories captured before task 5.5 landed. Falling
    # back to arm.json's own state/void_reason keeps this row builder
    # working against a run directory produced by either revision.
    status_path = run_dir / "status.json"
    if status_path.is_file():
        run_status = json.loads(status_path.read_text())
        state = run_status.get("state", arm_data.get("state", "void"))
        void_reason = run_status.get("void_reason", arm_data.get("void_reason"))
    else:
        state = arm_data.get("state", "void")
        void_reason = arm_data.get("void_reason")
    shakedown_used = bool(arm_data.get("shakedown_used"))
    prereg_digest = arm_data.get("prereg_digest")
    ro_substrate_violation = bool(arm_data.get("ro_substrate_violation"))
    diagnostician_src_violation = bool(arm_data.get("diagnostician_src_violation"))
    steps_meta = arm_data.get("steps", [])
    anomaly_classes = set()
    fixture_version = FAILURE_FLOOD_FIXTURE_VERSIONS.get(task_id, "v1")
    # Read once, used both by the provenance gate below (R-P4.1's malformed-
    # key detection) and by the scoring sections further down — one variable,
    # never re-fetched, so the two places can't observe a different snapshot
    # of it.
    ak = answer_keys.get(task_id)

    # Hard Ordering Gate layer 3 (design.md sec 7, task 5.8's own scope):
    # a row cannot be counted without a pre-registration digest unless it
    # is a declared shakedown. run-pipeline.sh's own preflight (layer 2)
    # already refuses to launch a non-shakedown run with no prereg file
    # before any run directory is even claimed, so this backstop never
    # fires against a run made through today's runner — it exists for a
    # row this deriver cannot trust was produced that way (report.py
    # already excludes voids and names them, per the same design section).
    if state == "complete" and not shakedown_used and not prereg_digest:
        state, void_reason = "void", "no-preregistration"
        anomaly_classes.add("no-preregistration")

    # ff_surface_digest: the LIVE preimage recompute, read via the same
    # `surfaces` parameter every existing precedent uses (never a second,
    # direct rig/surfaces/ read here) — Face C's own drift comparand below
    # (task 2.4), computed once, ahead of the gate, because that gate now
    # needs it too. No longer the per-step READ-BACK comparand (task 2.5
    # retires that use — see the loop below).
    ff_surface = surfaces.get(FAILURE_FLOOD_SURFACE_ARM) or []
    ff_surface_digest = surface_digest(ff_surface) if ff_surface else None

    # ---- Face A + C + WARNING-14: input-provenance annotation + gate -----
    # (run-input-provenance spec R-P2/R-P3/R-P4/R-P5/R-P6.3, design.md
    # secs 4-6).
    #
    # The ANNOTATION that this capture predates the scheme is independent of
    # the STATE TRANSITION (R-P5.2's own explicit carve-out, proven by the
    # three existing shakedown rows, R-P8): a row already void for another
    # reason still gains "pre-scheme-provenance" when it carries no
    # input_provenance_version at all, without its void_reason changing.
    # Every OTHER provenance check below (digest-null, digest-mismatch,
    # malformed key) stays ordinary downgrade-only: it neither annotates nor
    # transitions a row an earlier check already voided (R-P3.2) — it is
    # nested inside `if state == "complete":`, unlike the marker-absence
    # annotation above it.
    input_provenance_version = arm_data.get("input_provenance_version")
    if input_provenance_version is None:
        anomaly_classes.add("pre-scheme-provenance")
        if state == "complete":
            state, void_reason = "void", "input-provenance-missing"
    elif state == "complete":
        # Pass 2 (R-P5.3): the scheme is present, but a promised digest was
        # recorded null — a destroyed or truncated capture, never conflated
        # with pre-scheme (mutually exclusive with the branch above by
        # construction — R-P5.5's "caught once" scenario). Face C's own
        # promised value is PER MODEL STEP (design.md sec 1 — a three-step
        # arm has three invocations and the preimage file can change between
        # them), unlike Face A's arm-level recorded_answer_key_digest, so it
        # joins this same null check per model step (task 2.4).
        recorded_answer_key_digest = arm_data.get("recorded_answer_key_digest")
        # Face B's own promised value (task 3.1, R-P7.1): arm-level, same
        # null-check as Face A's — a run that never recorded its fixture
        # digest at all cannot say what it was scored against any more than
        # one that never recorded its answer-key digest can.
        recorded_fixture_digest = arm_data.get("recorded_fixture_digest")
        missing_surface_preimage = any(
            s.get("kind") == "model" and s.get("recorded_surface_preimage_sha256") is None
            for s in steps_meta
        )
        if recorded_answer_key_digest is None or recorded_fixture_digest is None or missing_surface_preimage:
            state, void_reason = "void", "input-provenance-missing"
            anomaly_classes.add("provenance-capture-incomplete")
        else:
            # Pass 3 (R-P2.2a): accumulate every drifted face BEFORE
            # deciding, rather than branching on the first mismatch found —
            # this is what makes "check order MUST NOT be observable in the
            # outcome" true by construction, not a convention. Face B's own
            # check (task 3.2, R-P7.1a) JOINS this set rather than being
            # inserted at a particular point relative to the answer-key
            # check — R-P2.2a forbids that framing entirely, which is why
            # this accumulation shape, not an insertion point, is what
            # "joins" means here.
            drifted = set()
            live_answer_key_digest = digests.get("answer_key", {}).get(fixture_version)
            if recorded_answer_key_digest != live_answer_key_digest:
                drifted.add("answer-key-drift")
            live_fixture_digest = digests.get("fixture", {}).get(fixture_version)
            if recorded_fixture_digest != live_fixture_digest:
                drifted.add("fixture-drift")
            if ak is not None:
                # R-P4.1: a malformed key IS an instance of "this row's
                # inputs do not match a scoreable answer key," never a
                # separate class needing its own reason — per the
                # requirement's own text it joins the same `drifted` set a
                # digest mismatch does.
                f0 = ak.get("F0") or {}
                if "failures" not in f0 or "R0" not in ak:
                    drifted.add("answer-key-drift")
            # R-P6.3: "did the thing that was frozen at run time still match
            # the fixture later" — a DIFFERENT question from the read-back
            # loop's own "did the model's observed surface match what was
            # frozen" below (task 2.5). The two MUST NOT share a reason.
            for s in steps_meta:
                if s.get("kind") != "model":
                    continue
                if s.get("recorded_surface_preimage_sha256") != ff_surface_digest:
                    drifted.add("surface-preimage-drift")
            if drifted:
                state, void_reason = "void", "input-provenance-mismatch"
                anomaly_classes |= drifted

    # Read-back downgrades (never upgrades — same discipline as build_row's
    # own complete-only checks above): the surface/permission-mode
    # comparison is explicitly THIS file's job, never run-pipeline.sh's own
    # (task 5.2's done-note; run-pipeline.sh's read_back_init() comment:
    # "every existing precedent puts that decision in derive.py").
    if state == "complete":
        for step in steps_meta:
            if step.get("kind") != "model":
                continue
            step_surface = step.get("surface_sha256")
            # R-P6.2/R-P6.1: the `is not None` guard is DELETED, not
            # weakened — its job (deciding whether this comparison can be
            # trusted at all) moved to the gate above, which never reaches
            # this loop with a missing comparand (R-P5.3's own null check).
            # The comparand is now the run's OWN frozen recording (the
            # OBSERVED step_surface's counterpart), never the live recompute
            # ff_surface_digest — that value is Face C's DRIFT comparand
            # above, a different question (R-P6.3's own text).
            if step_surface != step.get("recorded_surface_preimage_sha256"):
                state, void_reason = "void", "surface-mismatch"
                anomaly_classes.add("surface-mismatch")
                break
            if step.get("permission_mode_matches_declared") is not True:
                # R-P5.4: not-True is not-proven, not "is False" — a `None`
                # read back from a SCHEME-AWARE capture (the only kind that
                # can still be `state == "complete"` here; a pre-scheme row
                # was already voided by the gate above, R-P5.5) has not
                # shown the mode matched either.
                state, void_reason = "void", "permission-mode-mismatch"
                anomaly_classes.add("permission-mode-mismatch")
                break
            # model-mismatch (CRITICAL-3, verify-report 2026-08-17): the
            # STRONGER declared-value comparison, deliberately NOT the
            # self-consistency check build_row (tool-surface-v1) uses at
            # `model not in (result_event.get("modelUsage") or {})` — that
            # check only proves the init event's own model id appears
            # somewhere in the SAME run's usage breakdown; it says nothing
            # about whether the run actually used the model the invocation
            # DECLARED. ADR 0010 ("measurements vary the harness, not the
            # model") and R-F7.1 ("model id ... fixed across arms") both need
            # the declared-value comparison specifically, because the failure
            # this guards against is exactly what the three committed
            # shakedown rows already show: two runs of the SAME arm
            # (s1-monolithic-01, s1-monolithic-9054) disagreeing on model
            # (claude-opus-5[1m] vs claude-sonnet-5) with nothing to catch it.
            # A self-consistency check cannot catch that — both runs are
            # internally consistent, each with a DIFFERENT model. Reusing
            # run-pipeline.sh's own read-back (model_matches_declared,
            # written by write_step_status the same way
            # permission_mode_matches_declared already is) rather than
            # inventing a second comparison mechanism here.
            if step.get("model_matches_declared") is not True:
                # R-P5.4 (same rule as permission_mode_matches_declared
                # above): not-True is not-proven.
                state, void_reason = "void", "model-mismatch"
                anomaly_classes.add("model-mismatch")
                break

    # ---- per-step evidence: occupancy (reusing parse_stream/compute_occupancy
    # unchanged — both are already experiment-agnostic) and bash_call_count.
    steps_out = []
    model_turns_total = 0
    peak_occupancy_tokens = None
    cumulative_occupancy_tokens = 0
    occupancy_is_monotone = None
    context_window_tokens = None
    model = None
    for step in steps_meta:
        step_name = step.get("index")
        step_out = dict(step)
        if step.get("kind") == "model" and step_name:
            stream_path = run_dir / "steps" / step_name / "stream.jsonl"
            init_event, tool_calls, _hooks, result_event, stream_anomalies, turns = parse_stream(
                stream_path, bool(step.get("timed_out"))
            )
            anomaly_classes.update(stream_anomalies)
            if init_event and model is None:
                model = init_event.get("model")
            occ = compute_occupancy(turns, result_event, init_event.get("model") if init_event else None)
            step_out["model_turns"] = occ["model_turns"]
            step_out["occupancy_series"] = occ["occupancy_series"]
            step_out["peak_occupancy_tokens"] = occ["peak_occupancy_tokens"]
            step_out["cumulative_occupancy_tokens"] = occ["cumulative_occupancy_tokens"]
            step_out["bash_call_count"] = sum(1 for tc in tool_calls if tc["name"] == "Bash")
            # R-F7.3 (CRITICAL-4, verify-report 2026-08-17): "input, output,
            # cache_read_input, and cache_creation_input tokens recorded
            # separately (never a single total), plus tool-call count and
            # names." Occupancy above is a DIFFERENT channel (R-F5, a derived
            # proxy for context load) and does not satisfy this — it never
            # did, that is the regression this restores. Reusing build_row's
            # (tool-surface-v1's) own extraction verbatim, applied per step
            # here instead of once per row, since one step here is one
            # role's one invocation — the same granularity build_row's single
            # row already has for its single role.
            step_usage = (result_event or {}).get("usage", {})
            step_out["input_tokens"] = step_usage.get("input_tokens")
            step_out["output_tokens"] = step_usage.get("output_tokens")
            step_out["cache_creation_input_tokens"] = step_usage.get("cache_creation_input_tokens")
            step_out["cache_read_input_tokens"] = step_usage.get("cache_read_input_tokens")
            step_out["tool_calls"] = [{"name": tc["name"], "is_error": tc["is_error"]} for tc in tool_calls]
            model_turns_total += occ["model_turns"]
            if occ["peak_occupancy_tokens"] is not None:
                peak_occupancy_tokens = max(peak_occupancy_tokens or 0, occ["peak_occupancy_tokens"])
            cumulative_occupancy_tokens += occ["cumulative_occupancy_tokens"] or 0
            if occ["occupancy_is_monotone"] is not None:
                occupancy_is_monotone = (occupancy_is_monotone is not False) and occ["occupancy_is_monotone"]
            if occ["context_window_tokens"] is not None:
                context_window_tokens = occ["context_window_tokens"]
        steps_out.append(step_out)

    # R-F7.3's "Aggregated per role and per run" half — the per-step fields
    # just added ARE the per-role breakdown (each step is one role's one
    # invocation); these are the per-run totals, summed the same way
    # bash_call_count_total already is below. Never summed INTO occupancy or
    # any other single figure — a separate, parallel set of fields, per the
    # requirement's own "never a single total."
    input_tokens_total = sum((s.get("input_tokens") or 0) for s in steps_out if s.get("kind") == "model")
    output_tokens_total = sum((s.get("output_tokens") or 0) for s in steps_out if s.get("kind") == "model")
    cache_creation_input_tokens_total = sum(
        (s.get("cache_creation_input_tokens") or 0) for s in steps_out if s.get("kind") == "model"
    )
    cache_read_input_tokens_total = sum(
        (s.get("cache_read_input_tokens") or 0) for s in steps_out if s.get("kind") == "model"
    )
    tool_calls_total = [tc for s in steps_out if s.get("kind") == "model" for tc in (s.get("tool_calls") or [])]

    # ---- green-restore (R-F4.2), from the LAST 99-verify step's real
    # collection.json plus the fixture's own F0 — no capture gap here,
    # unlike diagnostic attribution below.
    suite_state = partial_reason = report_bytes = None
    verdict = integrity_guard_pass = None
    suite_state_cause_value = None
    verify_path = run_dir / "steps" / "99-verify" / "collection.json"
    if state == "complete" and verify_path.is_file() and ak:
        collection = json.loads(verify_path.read_text())
        suite_state = collection.get("suite_state")
        partial_reason = collection.get("partial_reason")
        report_bytes = collection.get("report_bytes")
        observed_failures = collection.get("failures", [])
        # R-F2.2 (CRITICAL-1): run-axis/suite-axis independence's third
        # field. An "environment" cause forces void — same downgrade-only
        # discipline as the read-back checks above (this block only runs
        # while state is still "complete", so it never upgrades a row an
        # earlier check already voided).
        suite_state_cause_value = suite_state_cause(suite_state, observed_failures, ak.get("S0"))
        if suite_state_cause_value == "environment":
            state, void_reason = "void", "suite-state-mismatch"
            anomaly_classes.add("suite-state-mismatch")
        elif suite_state == "ran":
            # R-P4.1: .get()-based, never a direct subscript — a malformed
            # key (no F0.failures) must not raise mid-derive. In practice
            # this branch is unreachable for a row the provenance gate above
            # already voided over that same malformed key (R-P4.1's own
            # "answer-key-drift" case), but the total-function guarantee
            # holds independently of that gate's own reach.
            verdict, integrity_guard_pass = green_restore_verdict(
                observed_failures, ak.get("F0", {}).get("failures", []), ro_substrate_violation
            )

    bash_call_count_total = sum(s.get("bash_call_count", 0) for s in steps_out)

    # Diagnostic attribution (R-F3.2, CRITICAL-2): scored whenever the row
    # is (still) complete and an answer key exists — never gated on the
    # handoff file's own presence, because "missing" is one of R-F3.2's own
    # two scoring inputs ("claimed = ... empty if malformed/missing"), not a
    # reason to leave the field null. A row this deriver cannot score at all
    # (void, or no answer key) keeps both fields None, the same precedent as
    # verdict/integrity_guard_pass above.
    causes_claimed = causes_correct = None
    if state == "complete" and ak:
        rc_true = {d["cause_site"] for d in ak.get("R0", [])}
        report_text = read_root_cause_report_handoff(run_dir, steps_meta)
        causes_claimed, causes_correct = score_diagnostic_attribution(report_text, rc_true)

    row = {
        "schema_version": FAILURE_FLOOD_SCHEMA_VERSION,
        "run_id": run_dir.name,
        "experiment": FAILURE_FLOOD_EXPERIMENT,
        "task_id": task_id,
        "arm": arm,
        "iteration": iteration,
        "model": model,
        "harness_version": arm_data.get("driver_version"),
        "python": arm_data.get("python_version"),
        "node_version": arm_data.get("node_version"),
        "npm_version": arm_data.get("npm_version"),
        "lockfile_sha256": arm_data.get("lockfile_sha256"),
        "case_table_digest": arm_data.get("case_table_digest"),
        "case_count": arm_data.get("case_count"),
        "fixture_version": fixture_version,
        "fixture_digest": digests["fixture"].get(fixture_version),
        "checker_digest": digests["checker"],
        "prereg_digest": prereg_digest,
        "code_commit": arm_data.get("code_commit"),
        "declared_permission_mode": arm_data.get("declared_permission_mode"),
        # ADR 0010 / R-F7.1 (CRITICAL-3): the pinned, per-invocation model
        # declaration, read straight from arm.json — never a repo constant.
        # "model" above stays the observed value from the first model step's
        # init event (unchanged meaning); this is what was DECLARED, so the
        # two are comparable per row without a second file.
        "declared_model": arm_data.get("declared_model"),
        # Faces A and B's own records, read back — never recomputed here
        # (R-P2, R-P5, R-P7). All three fields are already compared against
        # their live values by the provenance gate above (never re-derived a
        # second time for display).
        "input_provenance_version": arm_data.get("input_provenance_version"),
        "recorded_answer_key_digest": arm_data.get("recorded_answer_key_digest"),
        "recorded_fixture_digest": arm_data.get("recorded_fixture_digest"),
        "workspace_file_count": arm_data.get("workspace_file_count"),
        "state": state,
        "void_reason": void_reason,
        # task 5.5's own classification, carried through raw (never
        # recomputed here — run-pipeline.sh already re-hashed the real
        # workspace; this file only reads that verdict back).
        "ro_substrate_violation": ro_substrate_violation,
        "diagnostician_src_violation": diagnostician_src_violation,
        "model_turns": model_turns_total,
        "peak_occupancy_tokens": peak_occupancy_tokens,
        "cumulative_occupancy_tokens": cumulative_occupancy_tokens,
        "occupancy_is_monotone": occupancy_is_monotone,
        "context_window_tokens": context_window_tokens,
        "bash_call_count": bash_call_count_total,
        # R-F7.3 (CRITICAL-4): the four components, separate, never
        # collapsed into occupancy or into each other — "per run" aggregate;
        # each step in "steps" below carries the same four fields at "per
        # role" granularity, plus its own tool_calls (names + count via
        # len()). tool_calls here is the per-run concatenation, same shape
        # build_row (tool-surface-v1) already uses for its own single-role row.
        "input_tokens": input_tokens_total,
        "output_tokens": output_tokens_total,
        "cache_creation_input_tokens": cache_creation_input_tokens_total,
        "cache_read_input_tokens": cache_read_input_tokens_total,
        "tool_calls": tool_calls_total,
        "suite_state": suite_state,
        "suite_state_cause": suite_state_cause_value,
        "partial_reason": partial_reason,
        "report_bytes": report_bytes,
        "verdict": verdict,
        "integrity_guard_pass": integrity_guard_pass,
        # Diagnostic attribution (R-F3.2, CRITICAL-2): populated by
        # score_diagnostic_attribution() above from the real handoff file
        # when one exists, never invented. Task 5.9's own gap (no step
        # threaded root-cause-report.txt out of the ephemeral workspace) is
        # closed alongside this — run_model_step() now copies it out the
        # same way fix-plan.txt already was. A run captured before this PR
        # (the three committed shakedown rows) has no handoff file to read,
        # so it scores exactly as R-F3.2 itself specifies for "missing" —
        # claimed = empty set, not a special-cased null; this is the literal
        # spec text applied honestly to data this deriver can see, not a
        # retrofit.
        "causes_claimed": causes_claimed,
        "causes_correct": causes_correct,
        # R-P4.1: absence is not a count. `len(ak.get("R0", []))` would
        # publish 0, a claim that this task has zero causes; None means "no
        # scoreable R0 to count," never conflated with a real zero.
        "causes_present": len(ak["R0"]) if ak and "R0" in ak else None,
        "steps": steps_out,
        "anomaly_classes": sorted(anomaly_classes),
    }
    return row, None, None, []


EXPERIMENTS = {
    "tool-surface-v1": {
        "runs_root": RUNS_ROOT,
        "results_dir": RESULTS_DIR,
        "fixture_roots": FIXTURE_ROOTS,
        "run_id_re": RUN_ID_RE,
        "row_builder": build_row,
        "load_answer_keys": load_answer_keys,
        "load_surfaces": lambda: {"broad": load_surface("broad"), "scoped": load_surface("scoped")},
        "fixture_digest": lambda version, root: fixture_digest(version),
        "apply_ambient_drift_pairing": True,
    },
    FAILURE_FLOOD_EXPERIMENT: {
        "runs_root": FAILURE_FLOOD_RUNS_ROOT,
        "results_dir": FAILURE_FLOOD_RESULTS_DIR,
        "fixture_roots": FAILURE_FLOOD_FIXTURE_ROOTS,
        "run_id_re": FAILURE_FLOOD_RUN_ID_RE,
        "row_builder": build_row_failure_flood,
        "load_answer_keys": load_failure_flood_answer_keys,
        "load_surfaces": lambda: {FAILURE_FLOOD_SURFACE_ARM: load_surface(FAILURE_FLOOD_SURFACE_ARM)},
        "fixture_digest": lambda version, root: fixture_digest_at(root),
        # tool-surface-v1's own registry entry above gains NO key here —
        # digests["answer_key"] is built in main() only when an experiment
        # declares this key (design.md sec 7's mechanical non-regression
        # guarantee), never unconditionally.
        "answer_key_digest": lambda version, root: answer_key_set_digest(root),
        "apply_ambient_drift_pairing": False,
    },
}


# ---- --self-test (flag-gated; ADR 0013's ratified shape, mirroring
# collect.py's own --self-test exactly: same flag, same output prefix, same
# PASS/FAIL-per-case shape, same exit-code contract) -------------------------
#
# ADR 0013: a committed executable carries its own test. This absorbs three
# prior batches' own verification scripts (model-mismatch void, R-F7.3 token
# breakdown, suite_state_cause + R-F3.2 scoring) that each proved real
# behaviour and would otherwise have evaporated with the session that wrote
# them. Every fixture below is synthesised in a temp dir this function
# creates and removes — no dependency on rig/runs/ or any path outside this
# repo, other than the committed rig/surfaces/failure-flood.txt preimage the
# real pipeline also reads.

def _self_test_answer_key_set_digest():
    """run-input-provenance task 2.0 — a gatekeeping finding raised after
    Sibling 1 was committed: answer_key_set_digest()'s own computation was
    proven ZERO ways. Every existing self-test derives its expected digest
    by calling answer_key_set_digest() itself (this file's own
    _self_test_make_ff_run_dir, _self_test_build_row_model_mismatch, etc.),
    so both sides of every comparison move together and a `return
    "constant"` body left all 43 of Sibling 1's cases green. Two cases close
    that, neither one calling the function under test to build its own
    expected value:

    a. the digest MUST move when the digested bytes move — proven against
    itself, on a synthetic root this case builds and mutates, never against
    another self-test's own fixture. This mutation is append-shaped (adds
    `, "mutated": true` to the JSON, changing the byte length along with the
    content) rather than same-length — left that way deliberately, NOT an
    accidental inconsistency with task 3.8's own case, which was strengthened
    to a same-length, one-byte mutation after the orchestrator found the
    append shape lets a length-hashing (never content-reading) implementation
    pass undetected. That finding applies here too in principle, but this
    case is backstopped by case (b) below: a length-hashing Python side would
    disagree with the bash side over real digested bytes and turn the PIN
    red regardless of what this case alone could catch. Face B's own
    `_self_test_fixture_digest_at()` has no such backstop — no pin exists for
    it (see that function's own docstring for why) — which is why ITS case
    needed the stronger, same-length form and this one did not.

    b. the cross-language pin task 1.3's done-note verified BY HAND, never
    committed: python's answer_key_set_digest() and bash's
    answer_key_paths()|hash_paths() pipeline, EXTRACTED from
    rig/run-pipeline.sh (never re-implemented — the same sed convention
    rig/check.sh's load_compute_manifest() already uses), executed over the
    SAME synthetic root and asserted equal. A later disagreement here is the
    finding to report, never something to "fix" on whichever side looks
    wrong (design.md sec 9)."""
    tmproot = Path(tempfile.mkdtemp())
    try:
        fixture_root = tmproot / "fixture"
        ak_dir = fixture_root / "answer-key"
        ak_dir.mkdir(parents=True)
        (ak_dir / "s1.json").write_text('{"task_id": "s1", "F0": {"failures": []}, "R0": []}')
        (ak_dir / "prereg.json").write_text('{"required_hypotheses": []}')

        digest_before = answer_key_set_digest(fixture_root)
        (ak_dir / "s1.json").write_text(
            '{"task_id": "s1", "F0": {"failures": []}, "R0": [], "mutated": true}'
        )
        digest_after = answer_key_set_digest(fixture_root)
        case_fires = digest_before is not None and digest_before != digest_after

        run_pipeline = REPO_ROOT / "rig" / "run-pipeline.sh"
        bash_script = "set -euo pipefail\n"
        case_pin = False
        try:
            for fn in ("compute_manifest", "answer_key_paths", "hash_paths"):
                extracted = subprocess.run(
                    ["sed", "-n", f"/^{fn}() {{/,/^}}/p", str(run_pipeline)],
                    capture_output=True, text=True, check=True,
                ).stdout
                if not extracted.strip():
                    raise RuntimeError(f"could not extract {fn}() from {run_pipeline} by name")
                bash_script += extracted + "\n"
            bash_script += 'answer_key_paths "$1" | hash_paths "$1"\n'
            bash_digest = subprocess.run(
                ["bash", "-c", bash_script, "answer_key_pin", str(fixture_root)],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
            python_digest = answer_key_set_digest(fixture_root)
            case_pin = python_digest is not None and python_digest == bash_digest
        except (subprocess.CalledProcessError, OSError, RuntimeError) as exc:
            print(f"  [FAIL] answer_key_set_digest cross-language pin could not run: {exc}", file=sys.stderr)
    finally:
        shutil.rmtree(tmproot)
    cases = [
        ("a. mutating a digested file's bytes changes the digest — proven"
         " against itself, not a second self-test's own fixture", case_fires),
        ("b. cross-language pin: python answer_key_set_digest() and bash's"
         " answer_key_paths()|hash_paths() (extracted from run-pipeline.sh)"
         " agree over the same synthetic root", case_pin),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] answer_key_set_digest {name}")
    return ok


def _self_test_preimage_digest_pin():
    """run-input-provenance task 2.1 — the cross-language pin for Face C's
    own new algorithm (preimage_digest(), rig/run-pipeline.sh), the same
    shared-literal-constant mechanism already used for surface_digest at
    rig/run-pipeline.sh:424-430 (design.md sec 9), asserted independently
    here against derive.py's own surface_digest(). A pin failure is the
    finding to report, never a thing to "fix" on whichever side looks
    wrong."""
    pinned = "4a626b46a7841184c5d423277a9c17cb15129f4ba32f92a88948b77735bfdcd3"
    got = surface_digest(["Bash", "Read", "Write", "Read"])
    ok = got == pinned
    print(f"  [{'PASS' if ok else 'FAIL'}] surface_digest: dedupe + sort matches the pinned constant"
          " shared with rig/run-pipeline.sh --self-test's preimage_digest case a")
    return ok


def _self_test_load_surface_preimage_pin():
    """run-input-provenance task 2.9 — task 2.0's and task 3.8's own finding
    recursed into Face C a third time this cycle, raised by sdd-verify and
    independently confirmed by the orchestrator's own mutations after
    Sibling 2 was committed (`5cfa456`): `load_surface()`'s own parse was
    proven ZERO ways. Every self-test that supplies a
    `recorded_surface_preimage_sha256` default (`_self_test_make_ff_run_dir`,
    :1519, and everything built on it) computes ONE
    `surface_digest(load_surface(FAILURE_FLOOD_SURFACE_ARM))` expression and
    assigns it to BOTH sides of every Face C comparison, so both sides move
    together and a wrong `load_surface()` is invisible to them. The pin
    directly above, `_self_test_preimage_digest_pin()`, does not cover it
    either: it asserts `surface_digest()` over a hand-built Python list, so
    it pins the hash CONVENTION and never calls `load_surface()` at all —
    the parse is exactly what it leaves unexercised. Task 2.1's own
    done-note already named this pin as the weaker, shared-literal kind,
    distinct from task 2.0's stronger both-implementations pin; this task
    is closing that gap for Face C the way task 2.0 closed it for Face A.

    This case runs the deriver's OWN full path —
    `surface_digest(load_surface(arm))`, never a hardcoded list — over one
    synthetic preimage file carrying everything the parse must handle: a
    `# harness:` header line (must be excluded), blank lines (must be
    excluded), a duplicate tool name (must be deduped), and both an
    indented and a trailing-whitespace tool name (must be stripped, and
    must still dedupe against each other and against the unindented form
    once stripped). Asserted against the SAME kind of cross-language pin
    task 2.0 part 2 already built for Face A: `preimage_digest()`
    `sed`-extracted from `rig/run-pipeline.sh` (never re-implemented — the
    same convention `rig/check.sh`'s `load_compute_manifest()` and task
    2.0's own pin already use), executed over the identical file. A later
    disagreement here is the finding to report, never something to "fix"
    on whichever side looks wrong (design.md sec 9).

    No production code changed to make this reachable. `load_surface()`
    takes no root parameter — it is hardcoded to
    `SURFACES_ROOT / f"{arm}.txt"` — so the only way in without weakening
    it is to write the synthetic file at that exact path shape, under an
    arm name no real surface file uses, and delete it in `finally`
    regardless of outcome. `SURFACES_ROOT` already resolves inside `rig/`
    (`REPO_ROOT` is derived from `__file__`), so this satisfies the same
    "scratch copies live inside rig/, deleted on every path" discipline
    task 2.0's and task 3.8's own cross-checked-copy mutation proofs used,
    without a second temp root: `SURFACES_ROOT` already is one.

    **No live defect — recorded so a later reader does not misread this
    case as a bugfix.** Independently verified: today,
    `surface_digest(load_surface("failure-flood"))` on the Python side and
    `preimage_digest()` (extracted from `rig/run-pipeline.sh`) on the bash
    side already agree over the real committed
    `rig/surfaces/failure-flood.txt` — both print
    `d8693e27d5f8e406a465def75101c4eaa85b23b685e78c2d5d07754d0f7e8daa`. The
    gap this case closes is that nothing committed would have caught the
    two sides drifting apart, not that they currently disagree."""
    arm = "__self_test_load_surface_preimage_pin"
    surface_path = SURFACES_ROOT / f"{arm}.txt"
    assert not surface_path.exists(), (
        f"refusing to overwrite an existing file at {surface_path}"
    )
    try:
        surface_path.write_text(
            "# harness: v1\n\nBash\n\n  Read\nWrite\nRead   \n"
        )

        python_digest = surface_digest(load_surface(arm))

        run_pipeline = REPO_ROOT / "rig" / "run-pipeline.sh"
        case_pin = False
        try:
            extracted = subprocess.run(
                ["sed", "-n", "/^preimage_digest() {/,/^}/p", str(run_pipeline)],
                capture_output=True, text=True, check=True,
            ).stdout
            if not extracted.strip():
                raise RuntimeError(f"could not extract preimage_digest() from {run_pipeline} by name")
            bash_script = "set -euo pipefail\n" + extracted + '\npreimage_digest "$1"\n'
            bash_digest = subprocess.run(
                ["bash", "-c", bash_script, "load_surface_preimage_pin", str(surface_path)],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
            case_pin = python_digest is not None and python_digest == bash_digest
        except (subprocess.CalledProcessError, OSError, RuntimeError) as exc:
            print(f"  [FAIL] load_surface/preimage_digest cross-language pin could not run: {exc}", file=sys.stderr)
    finally:
        surface_path.unlink(missing_ok=True)
    cases = [
        ("cross-language pin: python surface_digest(load_surface()) and bash's"
         " preimage_digest() (extracted from run-pipeline.sh) agree over the"
         " SAME synthetic file exercising header/blank/duplicate/indented"
         " tool lines — never a hardcoded list on either side", case_pin),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] load_surface preimage {name}")
    return ok


def _self_test_parse_root_cause_report():
    well_formed = "ROOT-CAUSE-REPORT v1\nsrc/a.ts:1\nsrc/b.ts:2\n"
    cases = [
        ("well-formed -> 2 claims", parse_root_cause_report(well_formed) == frozenset({"src/a.ts:1", "src/b.ts:2"})),
        ("malformed prose -> None", parse_root_cause_report("ROOT-CAUSE-REPORT v1\nThe bug is in the keypad handler somewhere.\n") is None),
        ("missing sentinel -> None", parse_root_cause_report("src/a.ts:1\nsrc/b.ts:2\n") is None),
        ("missing file (None) -> None", parse_root_cause_report(None) is None),
        ("blank lines skipped, still valid", parse_root_cause_report("ROOT-CAUSE-REPORT v1\n\nsrc/a.ts:1\n\n") == frozenset({"src/a.ts:1"})),
        ("duplicate lines deduplicated", parse_root_cause_report("ROOT-CAUSE-REPORT v1\nsrc/a.ts:1\nsrc/a.ts:1\n") == frozenset({"src/a.ts:1"})),
        ("one bad line -> whole file malformed", parse_root_cause_report("ROOT-CAUSE-REPORT v1\nsrc/a.ts:1\nnot a path line at all\n") is None),
        ("empty string -> None", parse_root_cause_report("") is None),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] parse_root_cause_report: {name}")
    return ok


def _self_test_score_diagnostic_attribution():
    well_formed = "ROOT-CAUSE-REPORT v1\nsrc/a.ts:1\nsrc/b.ts:2\n"
    rc_true = {"src/a.ts:1", "src/c.ts:9"}
    claimed, correct = score_diagnostic_attribution(well_formed, rc_true)
    claimed_m, correct_m = score_diagnostic_attribution("ROOT-CAUSE-REPORT v1\nThe bug is in the keypad handler somewhere.\n", rc_true)
    claimed_none, correct_none = score_diagnostic_attribution(None, rc_true)
    # Hostile/non-ASCII input, per hypothesis-cycle corner-case discipline —
    # a real binary-byte string and a real accented path, never conceivable-
    # only inputs.
    claimed_h, correct_h = score_diagnostic_attribution("ROOT-CAUSE-REPORT v1\n\x00\x01binary\n", rc_true)
    claimed_u, correct_u = score_diagnostic_attribution("ROOT-CAUSE-REPORT v1\nsrc/café.ts:3\n", rc_true)
    cases = [
        ("well-formed: claimed sorted list", claimed == ["src/a.ts:1", "src/b.ts:2"]),
        ("well-formed: correct = intersection", correct == ["src/a.ts:1"]),
        ("malformed (R-F3.2's own named scenario): claimed empty, no crash", claimed_m == [] and correct_m == []),
        ("missing (None text): claimed empty, no crash", claimed_none == [] and correct_none == []),
        ("hostile/binary bytes-as-text: no crash, claimed empty", claimed_h == [] and correct_h == []),
        ("non-ASCII path: \\w matches unicode word chars in Python re, no crash", claimed_u == ["src/café.ts:3"]),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] score_diagnostic_attribution: {name}")
    return ok


def _self_test_suite_state_cause():
    s0_dns = {"suite_state": "did-not-start", "signature": "X"}
    cases = [
        ("ran==ran -> injection", suite_state_cause("ran", [], {"suite_state": "ran"}) == "injection"),
        ("did-not-start vs frozen ran -> environment",
         suite_state_cause("did-not-start", [{"test_id": "__suite__", "signature": "X"}], {"suite_state": "ran"}) == "environment"),
        ("no S0 -> None", suite_state_cause("ran", [], None) is None),
        ("no observed suite_state -> None", suite_state_cause(None, [], {"suite_state": "ran"}) is None),
        ("did-not-start, matching signature -> injection",
         suite_state_cause("did-not-start", [{"test_id": "__suite__", "signature": "X"}], s0_dns) == "injection"),
        ("did-not-start, different signature -> environment",
         suite_state_cause("did-not-start", [{"test_id": "__suite__", "signature": "Y"}], s0_dns) == "environment"),
        ("did-not-start, no signature present -> environment (conservative)",
         suite_state_cause("did-not-start", [], s0_dns) == "environment"),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] suite_state_cause: {name}")
    return ok


def _self_test_read_root_cause_report_handoff():
    well_formed = "ROOT-CAUSE-REPORT v1\nsrc/a.ts:1\nsrc/b.ts:2\n"
    tmpdir = Path(tempfile.mkdtemp())
    try:
        run_dir = tmpdir / "s1-monolithic-01"
        (run_dir / "steps" / "01-monolith" / "handoff").mkdir(parents=True)
        (run_dir / "steps" / "01-monolith" / "handoff" / "root-cause-report.txt").write_text(well_formed)
        found = read_root_cause_report_handoff(run_dir, [{"index": "01-monolith", "kind": "model"}, {"index": "99-verify", "kind": "code"}])

        run_dir2 = tmpdir / "s1-monolithic-02"
        (run_dir2 / "steps" / "01-monolith").mkdir(parents=True)
        missing = read_root_cause_report_handoff(run_dir2, [{"index": "01-monolith", "kind": "model"}])
    finally:
        shutil.rmtree(tmpdir)
    cases = [
        ("handoff file found and read", found == well_formed),
        ("no handoff file -> None", missing is None),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] read_root_cause_report_handoff: {name}")
    return ok


def _self_test_write_stream(path, model, events=None):
    """Minimal synthetic stream.jsonl: one init event plus caller-supplied
    events (default: a bare result event). Mirrors the real transcript shape
    parse_stream() reads — never a second parsing mechanism."""
    init_ev = {"type": "system", "subtype": "init", "model": model, "cwd": str(path.parent), "tools": []}
    lines = [init_ev] + (events if events is not None else [{"type": "result", "usage": {
        "input_tokens": 10, "output_tokens": 5, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
    }}])
    path.write_text("\n".join(json.dumps(ev) for ev in lines) + "\n")


def _self_test_make_ff_run_dir(root, run_id, step_overrides, write_stream=True, arm_overrides=None):
    """One synthetic s1-monolithic-<N> run directory: arm.json + status.json
    + one model step, matching run-pipeline.sh's own real Amendment-1 shape
    closely enough for build_row_failure_flood to read it as a real run.

    `arm_overrides` carries the provenance-related arm.json fields
    (input_provenance_version, recorded_answer_key_digest,
    recorded_fixture_digest) — arm-level, not per-step, per design.md sec 1.
    Defaults to a provenance-INTACT capture whose recorded digests agree
    with the REAL committed v1 fixture (via answer_key_set_digest() and
    fixture_digest_at() themselves, never a hardcoded string that might
    coincidentally never collide with anything), so every existing caller of
    this fixture builder now carries provenance and none of them accidentally
    drift the new gate — design.md sec 9's own stated intent ("it forces
    every existing detector fixture to carry provenance and proves the new
    gate composes with the old ones rather than sitting beside them"). A
    caller building an s2/v2 run (task 3.3) MUST override both digests to
    the v2 root's own real values, or v2 values, since this default is
    always v1's.

    The one step's OWN default is likewise Face-C-intact (Sibling 2): both
    the OBSERVED `surface_sha256` and the frozen `recorded_surface_preimage_
    sha256` default to the REAL committed rig/surfaces/failure-flood.txt
    digest, so they agree with each other by construction. A caller that
    passes `surfaces={FAILURE_FLOOD_SURFACE_ARM: []}` to isolate itself from
    Face C entirely must also pass the SAME real surface names in — see
    _self_test_build_row_model_mismatch/_self_test_build_row_token_breakdown
    below — so the gate's own live recompute (ff_surface_digest) agrees with
    this default too."""
    real_surface_digest = surface_digest(load_surface(FAILURE_FLOOD_SURFACE_ARM))
    run_dir = root / run_id
    (run_dir / "steps" / "01-monolith").mkdir(parents=True, exist_ok=True)
    step = {
        "index": "01-monolith", "kind": "model", "permission_mode_matches_declared": True,
        "surface_sha256": real_surface_digest,
        "recorded_surface_preimage_sha256": real_surface_digest,
        **step_overrides,
    }
    if write_stream:
        _self_test_write_stream(run_dir / "steps" / "01-monolith" / "stream.jsonl", step_overrides.get("model_actual"))
    (run_dir / "status.json").write_text(json.dumps({"state": "complete", "void_reason": None}))
    arm = {
        # prereg_digest is required or the Hard Ordering Gate layer-3 check
        # (build_row_failure_flood's own "no-preregistration" void) fires
        # before anything this fixture exists to test even runs.
        "declared_model": step_overrides.get("declared_model"), "prereg_digest": "deadbeef", "steps": [step],
        "input_provenance_version": 1,
        "recorded_answer_key_digest": answer_key_set_digest(FAILURE_FLOOD_FIXTURE_ROOTS["v1"]),
        "recorded_fixture_digest": fixture_digest_at(FAILURE_FLOOD_FIXTURE_ROOTS["v1"]),
        **(arm_overrides or {}),
    }
    (run_dir / "arm.json").write_text(json.dumps(arm))
    return run_dir


def _self_test_build_row_model_mismatch():
    """Absorbed from a prior batch's own scratch script (PR7A's model-pin
    verification): cases proving the DECLARED-value comparison (never
    build_row's own self-consistency check, which cannot catch two
    internally-consistent runs of the same arm on different models).

    Case 3 (R-P10.2): REWRITTEN, never deleted. It used to assert
    `model_matches_declared: None -> state == "complete"`, labelled "old
    capture — never falsely voids" — that pinned WARNING-14's own defect as
    intended behaviour rather than naming it as a bug. Deleting it would
    erase the evidence that "absence is consent" was ever asserted; rewriting
    it records the inversion R-P5 makes: the SAME fixture, now with no
    `input_provenance_version`, must void as pre-scheme (R-P5.2). Case 4 is
    NEW and proves the other half: the same `None` read-back, from a
    provenance-INTACT capture, voids as `model-mismatch` (R-P5.4) — together
    they are the WARNING-14 proof; keeping only one leaves the other half
    unproven (R-P10.2's own scenario).

    Case 5 is NEW and closes a gap mutation-testing found during this
    batch's own apply: R-P5.4 names BOTH `:859`
    (`permission_mode_matches_declared`) and `:883`
    (`model_matches_declared`) — design.md sec 9's case 8 says "both sites" —
    but only the model site had a committed case proving it fires. Reverting
    the permission-mode line alone from `is not True` back to `is False`
    left every other case in this file green; only this case catches it."""
    # The REAL committed surface, matching _self_test_make_ff_run_dir's own
    # Face-C-intact step default (Sibling 2) — an empty surface would now
    # disagree with that default and trip surface-mismatch, which is not
    # what this function's own cases are about; isolating this check from
    # Face C is achieved by AGREEING, not by omitting.
    surfaces = {FAILURE_FLOOD_SURFACE_ARM: load_surface(FAILURE_FLOOD_SURFACE_ARM)}
    digests = {"fixture": {"v1": fixture_digest_at(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])}, "checker": "x",
               "answer_key": {"v1": answer_key_set_digest(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])}}
    tmproot = Path(tempfile.mkdtemp())
    try:
        d1 = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99mismatch",
                                          {"declared_model": "claude-opus-5[1m]", "model_actual": "claude-sonnet-5",
                                           "model_matches_declared": False})
        row1, *_ = build_row_failure_flood(d1, surfaces, digests, {})
        case1 = (row1["state"] == "void" and row1["void_reason"] == "model-mismatch"
                 and "model-mismatch" in row1["anomaly_classes"] and row1["declared_model"] == "claude-opus-5[1m]")

        d2 = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99match",
                                          {"declared_model": "claude-opus-5[1m]", "model_actual": "claude-opus-5[1m]",
                                           "model_matches_declared": True})
        row2, *_ = build_row_failure_flood(d2, surfaces, digests, {})
        case2 = row2["state"] == "complete" and row2["void_reason"] is None

        d3 = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99old",
                                          {"declared_model": "claude-opus-5[1m]", "model_actual": None,
                                           "model_matches_declared": None},
                                          arm_overrides={"input_provenance_version": None})
        row3, *_ = build_row_failure_flood(d3, surfaces, digests, {})
        case3 = (row3["state"] == "void" and row3["void_reason"] == "input-provenance-missing"
                 and "pre-scheme-provenance" in row3["anomaly_classes"])

        d4 = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99nullintact",
                                          {"declared_model": "claude-opus-5[1m]", "model_actual": None,
                                           "model_matches_declared": None})
        row4, *_ = build_row_failure_flood(d4, surfaces, digests, {})
        case4 = row4["state"] == "void" and row4["void_reason"] == "model-mismatch"

        d5 = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99permnull",
                                          {"declared_model": "claude-opus-5[1m]", "model_actual": "claude-opus-5[1m]",
                                           "model_matches_declared": True,
                                           "permission_mode_matches_declared": None})
        row5, *_ = build_row_failure_flood(d5, surfaces, digests, {})
        case5 = row5["state"] == "void" and row5["void_reason"] == "permission-mode-mismatch"
    finally:
        shutil.rmtree(tmproot)
    cases = [
        ("model_matches_declared=False -> state=void, void_reason=model-mismatch", case1),
        ("model_matches_declared=True -> state stays complete", case2),
        ("model_matches_declared=None, no input_provenance_version -> void: input-provenance-missing"
         " (rewritten from the old 'never falsely voids' assertion, R-P10.2)", case3),
        ("model_matches_declared=None, provenance INTACT -> void: model-mismatch"
         " (R-P5.4 — WARNING-14's other half)", case4),
        ("permission_mode_matches_declared=None, provenance INTACT -> void: permission-mode-mismatch"
         " (R-P5.4's OTHER site — design.md sec 9's 'both sites', gap found by mutation-testing)", case5),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] build_row_failure_flood: {name}")
    return ok


def _self_test_build_row_token_breakdown():
    """Absorbed from a prior batch's own scratch script (PR7A's R-F7.3
    restoration): per-step and per-run input/output/cache_read/
    cache_creation tokens, plus tool_calls names+count — never a single
    total, per and R-F7.3's own words."""
    # Real committed surface — see _self_test_build_row_model_mismatch's own
    # comment for why (Sibling 2's Face-C-intact default agrees with this).
    surfaces = {FAILURE_FLOOD_SURFACE_ARM: load_surface(FAILURE_FLOOD_SURFACE_ARM)}
    digests = {"fixture": {"v1": fixture_digest_at(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])}, "checker": "x",
               "answer_key": {"v1": answer_key_set_digest(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])}}
    tmproot = Path(tempfile.mkdtemp())
    try:
        events = [
            {"type": "assistant", "message": {"id": "m1", "usage": {
                "input_tokens": 100, "output_tokens": 10, "cache_read_input_tokens": 5, "cache_creation_input_tokens": 2},
                "content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {}}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]}},
            {"type": "assistant", "message": {"id": "m2", "usage": {
                "input_tokens": 120, "output_tokens": 20, "cache_read_input_tokens": 6, "cache_creation_input_tokens": 3},
                "content": [{"type": "tool_use", "id": "t2", "name": "Read", "input": {"file_path": "/x/a"}}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t2", "content": "ok"}]}},
            {"type": "result", "usage": {
                "input_tokens": 220, "output_tokens": 30, "cache_read_input_tokens": 11, "cache_creation_input_tokens": 5}},
        ]
        d = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99tok",
                                         {"declared_model": "claude-opus-5[1m]", "model_actual": "claude-opus-5[1m]",
                                          "model_matches_declared": True}, write_stream=False)
        _self_test_write_stream(d / "steps" / "01-monolith" / "stream.jsonl", "claude-opus-5[1m]", events)
        row, *_ = build_row_failure_flood(d, surfaces, digests, {})
        names = sorted(tc["name"] for tc in row["tool_calls"])
        step_out = row["steps"][0]
        step_names = sorted(tc["name"] for tc in step_out["tool_calls"])
        cases = [
            ("row input_tokens", row["input_tokens"] == 220),
            ("row output_tokens", row["output_tokens"] == 30),
            ("row cache_creation_input_tokens", row["cache_creation_input_tokens"] == 5),
            ("row cache_read_input_tokens", row["cache_read_input_tokens"] == 11),
            ("row tool_calls names", names == ["Bash", "Read"]),
            ("step input/output/cache tokens match row (one model step)",
             step_out["input_tokens"] == 220 and step_out["output_tokens"] == 30
             and step_out["cache_creation_input_tokens"] == 5 and step_out["cache_read_input_tokens"] == 11),
            ("step tool_calls names", step_names == ["Bash", "Read"]),
        ]
    finally:
        shutil.rmtree(tmproot)
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] build_row_failure_flood token breakdown: {name}")
    return ok


def _self_test_build_row_suite_state_and_attribution():
    """Absorbed from a prior batch's own scratch script (PR7B's
    suite_state_cause + R-F3.2 scoring closure): four full-row cases against
    the REAL committed rig/surfaces/failure-flood.txt preimage — injection
    (green, scored), environment (forced void), malformed handoff (claimed
    empty, not voided), and no handoff file at all (claimed empty, not
    voided) — the 16 assertions the verify-report's own malformed-input
    scenario named."""
    surface_names = load_surface(FAILURE_FLOOD_SURFACE_ARM)
    surface_dig = surface_digest(surface_names)
    surfaces = {FAILURE_FLOOD_SURFACE_ARM: surface_names}
    live_answer_key_digest = answer_key_set_digest(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])
    live_fixture_digest = fixture_digest_at(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])
    digests = {"fixture": {"v1": live_fixture_digest, "v2": None}, "checker": CHECKER_DIGEST,
               "answer_key": {"v1": live_answer_key_digest}}
    answer_keys = {"s1": {
        "task_id": "s1", "S0": {"suite_state": "ran"}, "F0": {"failures": []},
        "R0": [{"cause_site": "src/a.ts:1"}, {"cause_site": "src/c.ts:9"}],
    }}

    def make(run_id, handoff_text, collection, tmproot):
        run_dir = tmproot / run_id
        if handoff_text is not None:
            (run_dir / "steps" / "01-monolith" / "handoff").mkdir(parents=True)
            (run_dir / "steps" / "01-monolith" / "handoff" / "root-cause-report.txt").write_text(handoff_text)
        else:
            (run_dir / "steps" / "01-monolith").mkdir(parents=True)
        _self_test_write_stream(run_dir / "steps" / "01-monolith" / "stream.jsonl", "claude-sonnet-5")
        (run_dir / "steps" / "99-verify").mkdir(parents=True)
        (run_dir / "steps" / "99-verify" / "collection.json").write_text(json.dumps(collection))
        (run_dir / "status.json").write_text(json.dumps({"state": "complete", "void_reason": None}))
        (run_dir / "arm.json").write_text(json.dumps({
            "prereg_digest": "deadbeef",
            "input_provenance_version": 1,
            "recorded_answer_key_digest": live_answer_key_digest,
            "recorded_fixture_digest": live_fixture_digest,
            "steps": [
                {"index": "01-monolith", "kind": "model", "surface_sha256": surface_dig,
                 "recorded_surface_preimage_sha256": surface_dig,
                 "permission_mode_matches_declared": True, "model_matches_declared": True},
                {"index": "99-verify", "kind": "code"},
            ]}))
        return run_dir

    tmproot = Path(tempfile.mkdtemp())
    ok = True
    try:
        d1 = make("s1-monolithic-01", "ROOT-CAUSE-REPORT v1\nsrc/a.ts:1\nsrc/b.ts:2\n",
                   {"suite_state": "ran", "partial_reason": None, "report_bytes": 100, "failures": []}, tmproot)
        row1, *_ = build_row_failure_flood(d1, surfaces, digests, answer_keys)
        case1 = [
            ("state stays complete", row1["state"] == "complete"),
            ("suite_state_cause == injection", row1["suite_state_cause"] == "injection"),
            ("verdict == green (no failures)", row1["verdict"] == "green"),
            ("causes_claimed populated from handoff", row1["causes_claimed"] == ["src/a.ts:1", "src/b.ts:2"]),
            ("causes_correct == intersection with R0", row1["causes_correct"] == ["src/a.ts:1"]),
        ]

        d2 = make("s1-monolithic-02", "ROOT-CAUSE-REPORT v1\nsrc/a.ts:1\n",
                   {"suite_state": "did-not-start", "partial_reason": "missing node_modules", "report_bytes": 10,
                    "failures": [{"test_id": "__suite__", "status": "failed", "signature": "sig-env"}]}, tmproot)
        row2, *_ = build_row_failure_flood(d2, surfaces, digests, answer_keys)
        case2 = [
            ("state forced to void", row2["state"] == "void"),
            ("void_reason == suite-state-mismatch", row2["void_reason"] == "suite-state-mismatch"),
            ("suite_state_cause == environment", row2["suite_state_cause"] == "environment"),
            ("'suite-state-mismatch' in anomaly_classes", "suite-state-mismatch" in row2["anomaly_classes"]),
            ("causes_claimed/correct stay None (void row, not scored)",
             row2["causes_claimed"] is None and row2["causes_correct"] is None),
        ]

        d3 = make("s1-monolithic-03", "The root cause is in the keypad handler, roughly.\n",
                   {"suite_state": "ran", "partial_reason": None, "report_bytes": 50, "failures": []}, tmproot)
        row3, *_ = build_row_failure_flood(d3, surfaces, digests, answer_keys)
        case3 = [
            ("state stays complete (malformed report is not voided by R-F2.2)", row3["state"] == "complete"),
            ("causes_claimed == [] (malformed, not a crash)", row3["causes_claimed"] == []),
            ("causes_correct == []", row3["causes_correct"] == []),
        ]

        d4 = make("s1-monolithic-04", None,
                   {"suite_state": "ran", "partial_reason": None, "report_bytes": 50, "failures": []}, tmproot)
        row4, *_ = build_row_failure_flood(d4, surfaces, digests, answer_keys)
        case4 = [
            ("no handoff file -> causes_claimed == [] per spec's 'missing' rule", row4["causes_claimed"] == []),
            ("causes_correct == []", row4["causes_correct"] == []),
            ("state still complete (missing report never voids per R-F2.2/R-F3.2)", row4["state"] == "complete"),
        ]

        for case_name, checks in (("case1 (injection, well-formed)", case1), ("case2 (environment -> void)", case2),
                                   ("case3 (malformed handoff)", case3), ("case4 (no handoff file)", case4)):
            case_ok = all(c for _, c in checks)
            ok = ok and case_ok
            print(f"  [{'PASS' if case_ok else 'FAIL'}] build_row_failure_flood {case_name}: "
                  + ", ".join(f"{n}={c}" for n, c in checks))
    finally:
        shutil.rmtree(tmproot)
    return ok


def _self_test_build_row_answer_key_provenance():
    """Face A's own detector-fires proof (R-P10.1) plus the WARNING-14
    absence-distinction proof (R-P5), built on the same
    _self_test_make_ff_run_dir fixture every other build_row_failure_flood
    self-test uses — now carrying provenance by default (design.md sec 9),
    so this case list is what proves the new gate composes with every
    existing detector rather than sitting beside them. Uses the REAL
    committed surface (Sibling 2's own composition requirement — see
    _self_test_build_row_model_mismatch's comment), never an empty one:
    this function is about Face A, not Face C, and stays isolated from it by
    agreeing rather than by omitting."""
    surfaces = {FAILURE_FLOOD_SURFACE_ARM: load_surface(FAILURE_FLOOD_SURFACE_ARM)}
    live_v1 = answer_key_set_digest(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])
    live_v2 = answer_key_set_digest(FAILURE_FLOOD_FIXTURE_ROOTS["v2"])
    live_fixture_v1 = fixture_digest_at(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])
    digests = {"fixture": {"v1": live_fixture_v1}, "checker": "x", "answer_key": {"v1": live_v1, "v2": live_v2}}
    intact_step = {"declared_model": "claude-opus-5[1m]", "model_actual": "claude-opus-5[1m]",
                    "model_matches_declared": True}
    tmproot = Path(tempfile.mkdtemp())
    try:
        # a. negative control — every digest present and agreeing. A gate
        # that always voids would pass every later case here too.
        d_a = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99pa", intact_step)
        row_a, *_ = build_row_failure_flood(d_a, surfaces, digests, {})
        case_a = row_a["state"] == "complete" and row_a["void_reason"] is None

        # b. recorded digest deliberately disagrees with the REAL on-disk v1
        # answer key (R-P10.1's own named scenario, R-P3's own scenario).
        d_b = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99pb", intact_step,
                                           arm_overrides={"recorded_answer_key_digest": "deadbeef" * 8})
        row_b, *_ = build_row_failure_flood(d_b, surfaces, digests, {})
        case_b = (row_b["state"] == "void" and row_b["void_reason"] == "input-provenance-mismatch"
                   and "answer-key-drift" in row_b["anomaly_classes"])

        # c. an unrelated task's answer key (a DIFFERENT fixture root's own
        # digest, v2) is deliberately wrong in `digests`; this s1/v1 row's
        # own recorded digest still agrees with the real v1 value, so it
        # must be unaffected — spec's own "an unrelated answer key changing
        # does not touch this row" scenario, proven by the per-root indexing
        # itself rather than by editing a real fixture file.
        digests_wrong_v2 = {"fixture": {"v1": live_fixture_v1}, "checker": "x",
                             "answer_key": {"v1": live_v1, "v2": "wrongwrong" * 6}}
        d_c = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99pc", intact_step)
        row_c, *_ = build_row_failure_flood(d_c, surfaces, digests_wrong_v2, {})
        case_c = row_c["state"] == "complete" and row_c["void_reason"] is None

        # d. no input_provenance_version at all -> pre-scheme (R-P5.2).
        d_d = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99pd", intact_step,
                                           arm_overrides={"input_provenance_version": None})
        row_d, *_ = build_row_failure_flood(d_d, surfaces, digests, {})
        case_d = (row_d["state"] == "void" and row_d["void_reason"] == "input-provenance-missing"
                   and "pre-scheme-provenance" in row_d["anomaly_classes"])

        # e. version present, recorded_answer_key_digest null -> incomplete
        # capture (R-P5.3) — MUST reach a different anomaly_classes member
        # than case d, or the two absences are conflated after all.
        d_e = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99pe", intact_step,
                                           arm_overrides={"recorded_answer_key_digest": None})
        row_e, *_ = build_row_failure_flood(d_e, surfaces, digests, {})
        case_e = (row_e["state"] == "void" and row_e["void_reason"] == "input-provenance-missing"
                   and "provenance-capture-incomplete" in row_e["anomaly_classes"]
                   and "pre-scheme-provenance" not in row_e["anomaly_classes"])

        # f. a malformed answer key (F0.failures and R0 both absent) — no
        # exception; voids via the SAME reason as a digest mismatch (R-P4.1),
        # verdict/causes_present stay None — never a crash, never a 0.
        d_f = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99pf", intact_step)
        row_f, *_ = build_row_failure_flood(d_f, surfaces, digests, {"s1": {"task_id": "s1"}})
        case_f = (row_f["state"] == "void" and row_f["void_reason"] == "input-provenance-mismatch"
                   and "answer-key-drift" in row_f["anomaly_classes"]
                   and row_f["verdict"] is None and row_f["causes_present"] is None)

        # g. a row already void for another reason (Hard Ordering Gate layer
        # 3, no-preregistration) before this gate runs -> void_reason
        # unchanged, never overwritten (R-P3.2), even though the digest we
        # also mismatch here would have voided it too if it had been reached.
        d_g = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99pg", intact_step,
                                           arm_overrides={"prereg_digest": None,
                                                            "recorded_answer_key_digest": "deadbeef" * 8})
        row_g, *_ = build_row_failure_flood(d_g, surfaces, digests, {})
        case_g = row_g["state"] == "void" and row_g["void_reason"] == "no-preregistration"

        # h. the three committed shakedown rows' own shape: void for an
        # unrelated reason, no provenance at all — must gain
        # pre-scheme-provenance without losing "shakedown" (R-P8), proven
        # against a SYNTHETIC fixture shaped like the real rows, never the
        # real committed ones.
        run_dir_h = tmproot / "s1-monolithic-99ph"
        (run_dir_h / "steps" / "01-monolith").mkdir(parents=True)
        (run_dir_h / "status.json").write_text(json.dumps({"state": "void", "void_reason": "shakedown"}))
        (run_dir_h / "arm.json").write_text(json.dumps({
            "state": "void", "void_reason": "shakedown", "shakedown_used": True, "steps": [],
        }))
        row_h, *_ = build_row_failure_flood(run_dir_h, surfaces, digests, {})
        case_h = (row_h["state"] == "void" and row_h["void_reason"] == "shakedown"
                   and "pre-scheme-provenance" in row_h["anomaly_classes"])
    finally:
        shutil.rmtree(tmproot)
    cases = [
        ("a. all provenance present and agreeing -> complete (negative control)", case_a),
        ("b. recorded answer-key digest disagrees with the real v1 key"
         " -> void: input-provenance-mismatch, answer-key-drift", case_b),
        ("c. an unrelated (v2) answer key digest being wrong does not touch this s1/v1 row", case_c),
        ("d. no input_provenance_version -> void: input-provenance-missing, pre-scheme-provenance", case_d),
        ("e. version present, digest null -> void: input-provenance-missing, provenance-capture-incomplete"
         " (never pre-scheme-provenance)", case_e),
        ("f. malformed answer key (no F0.failures, no R0) -> no crash; void: input-provenance-mismatch,"
         " answer-key-drift; verdict/causes_present stay None", case_f),
        ("g. already-void row (no-preregistration) keeps its own void_reason, never overwritten", case_g),
        ("h. a synthetic shakedown-shaped row keeps void_reason=shakedown, gains pre-scheme-provenance", case_h),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] build_row_failure_flood answer-key provenance {name}")
    return ok


def _self_test_build_row_surface_preimage_provenance():
    """Face C's own detector-fires proofs (run-input-provenance tasks 2.4,
    2.6, 2.7 — R-P6.3), built on the same _self_test_make_ff_run_dir fixture,
    which now defaults to a Face-C-intact step (both surface_sha256 and
    recorded_surface_preimage_sha256 equal to the real committed preimage
    digest). Case b is this batch's own addition beyond the tasks' literal
    text: no committed case previously proved build_row_failure_flood's
    surface-mismatch void can fire at all (ADR 0013) — only build_row's,
    tool-surface-v1's own row builder, a DIFFERENT function."""
    surfaces = {FAILURE_FLOOD_SURFACE_ARM: load_surface(FAILURE_FLOOD_SURFACE_ARM)}
    digests = {"fixture": {"v1": fixture_digest_at(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])}, "checker": "x",
               "answer_key": {"v1": answer_key_set_digest(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])}}
    intact_step = {"declared_model": "claude-opus-5[1m]", "model_actual": "claude-opus-5[1m]",
                    "model_matches_declared": True}
    tmproot = Path(tempfile.mkdtemp())
    try:
        # a. negative control — everything present and agreeing (design.md
        # sec 9's own "the one that gets skipped").
        d_a = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99sa", intact_step)
        row_a, *_ = build_row_failure_flood(d_a, surfaces, digests, {})
        case_a = row_a["state"] == "complete" and row_a["void_reason"] is None

        # b. the OBSERVED surface disagrees with the run's own FROZEN
        # comparand (never the live recompute, task 2.5's own fix) -> the
        # existing, unchanged surface-mismatch reason.
        d_b = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99sb",
                                           {**intact_step, "surface_sha256": "deadbeef" * 8})
        row_b, *_ = build_row_failure_flood(d_b, surfaces, digests, {})
        case_b = (row_b["state"] == "void" and row_b["void_reason"] == "surface-mismatch"
                   and "surface-mismatch" in row_b["anomaly_classes"])

        # c. R-P6.3 — the FROZEN comparand itself disagrees with a fresh live
        # recompute, while the observed value matches the (wrong) frozen
        # comparand cleanly, so task 2.5's own check would pass. Must reach
        # surface-preimage-drift, never surface-mismatch — the two questions
        # R-P6.3's own text keeps apart.
        d_c = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99sc",
                                           {**intact_step, "surface_sha256": "deadbeef" * 8,
                                            "recorded_surface_preimage_sha256": "deadbeef" * 8})
        row_c, *_ = build_row_failure_flood(d_c, surfaces, digests, {})
        case_c = (row_c["state"] == "void" and row_c["void_reason"] == "input-provenance-mismatch"
                   and "surface-preimage-drift" in row_c["anomaly_classes"]
                   and "surface-mismatch" not in row_c["anomaly_classes"])

        # d. the ordering proof — recorded_surface_preimage_sha256 is null
        # (provenance incomplete) AND the observed value would, if compared,
        # genuinely disagree with the live preimage. MUST void as
        # input-provenance-missing and MUST NOT reach or stamp
        # surface-mismatch — without this case the "correct refusal, false
        # stated cause" regression (design.md secs 4/6) is undetectable.
        d_d = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99sd",
                                           {**intact_step, "surface_sha256": "deadbeef" * 8,
                                            "recorded_surface_preimage_sha256": None})
        row_d, *_ = build_row_failure_flood(d_d, surfaces, digests, {})
        case_d = (row_d["state"] == "void" and row_d["void_reason"] == "input-provenance-missing"
                   and "provenance-capture-incomplete" in row_d["anomaly_classes"]
                   and row_d["void_reason"] != "surface-mismatch")
    finally:
        shutil.rmtree(tmproot)
    cases = [
        ("a. all provenance present and agreeing -> complete (negative control)", case_a),
        ("b. observed surface disagrees with the frozen comparand -> void: surface-mismatch"
         " (task 2.5's own fire-proof — never committed before this batch)", case_b),
        ("c. frozen comparand disagrees with a live recompute, observed matches the (wrong)"
         " comparand -> void: input-provenance-mismatch, surface-preimage-drift, never"
         " surface-mismatch (R-P6.3)", case_c),
        ("d. recorded preimage null, observed would disagree with live if compared -> void:"
         " input-provenance-missing, never surface-mismatch (the ordering proof)", case_d),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] build_row_failure_flood surface-preimage provenance {name}")
    return ok


def _self_test_build_row_fixture_provenance():
    """Face B's own detector-fires proofs (run-input-provenance tasks
    3.2/3.3/3.4, R-P7.1a) plus the full negative control (design.md sec 9
    case 1, "first achievable once all three digests exist" — this batch is
    what makes it achievable). Built on the same _self_test_make_ff_run_dir
    fixture every other build_row_failure_flood self-test uses, which now
    defaults to a Face-B-intact arm (both recorded_fixture_digest and the
    digests dict's own "fixture" entry equal to the REAL committed v1
    MANIFEST.sha256 digest)."""
    surfaces = {FAILURE_FLOOD_SURFACE_ARM: load_surface(FAILURE_FLOOD_SURFACE_ARM)}
    live_fixture_v1 = fixture_digest_at(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])
    live_fixture_v2 = fixture_digest_at(FAILURE_FLOOD_FIXTURE_ROOTS["v2"])
    live_answer_key_v1 = answer_key_set_digest(FAILURE_FLOOD_FIXTURE_ROOTS["v1"])
    live_answer_key_v2 = answer_key_set_digest(FAILURE_FLOOD_FIXTURE_ROOTS["v2"])
    digests = {"fixture": {"v1": live_fixture_v1, "v2": live_fixture_v2},
               "answer_key": {"v1": live_answer_key_v1, "v2": live_answer_key_v2}, "checker": "x"}
    intact_step = {"declared_model": "claude-opus-5[1m]", "model_actual": "claude-opus-5[1m]",
                    "model_matches_declared": True}
    tmproot = Path(tempfile.mkdtemp())
    try:
        # a. task 3.4 — the FULL negative control (design.md sec 9 case 1):
        # input_provenance_version present, all THREE digests (answer-key,
        # fixture, surface-preimage) present and agreeing -> complete. A
        # gate that always voids would pass every other case in this file
        # too; this is the one case that actually catches it.
        d_a = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99fa", intact_step)
        row_a, *_ = build_row_failure_flood(d_a, surfaces, digests, {})
        case_a = row_a["state"] == "complete" and row_a["void_reason"] is None

        # b. Face B's own fire-proof, alone: recorded_fixture_digest
        # deliberately disagrees with the real on-disk v1 MANIFEST.sha256,
        # while Face A and Face C stay intact -> void: input-provenance-
        # mismatch, "fixture-drift" present, "answer-key-drift" ABSENT
        # (proving the two faces are independently triggerable, never
        # conflated, R-P7.1a's own text).
        d_b = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99fb", intact_step,
                                           arm_overrides={"recorded_fixture_digest": "deadbeef" * 8})
        row_b, *_ = build_row_failure_flood(d_b, surfaces, digests, {})
        case_b = (row_b["state"] == "void" and row_b["void_reason"] == "input-provenance-mismatch"
                   and "fixture-drift" in row_b["anomaly_classes"]
                   and "answer-key-drift" not in row_b["anomaly_classes"])

        # c. task 3.2's own null-check extension: version present,
        # recorded_fixture_digest null -> the SAME "input-provenance-missing"
        # / "provenance-capture-incomplete" outcome as a null answer-key or
        # surface-preimage digest already reaches — never "fixture-drift"
        # (an absent value is not a disagreeing one) and never
        # "pre-scheme-provenance" (the scheme marker IS present here).
        d_c = _self_test_make_ff_run_dir(tmproot, "s1-monolithic-99fc", intact_step,
                                           arm_overrides={"recorded_fixture_digest": None})
        row_c, *_ = build_row_failure_flood(d_c, surfaces, digests, {})
        case_c = (row_c["state"] == "void" and row_c["void_reason"] == "input-provenance-missing"
                   and "provenance-capture-incomplete" in row_c["anomaly_classes"]
                   and "fixture-drift" not in row_c["anomaly_classes"]
                   and "pre-scheme-provenance" not in row_c["anomaly_classes"])

        # d. task 3.3 — the both-drifts-recorded case (replaces the withdrawn
        # R-P2.2 precedence task, R-P2.2a): a run recorded against fixture
        # root v2 whose recorded answer-key digest AND recorded fixture
        # digest BOTH disagree with the live v2 values at once — the same
        # shape a single edit to answer-key/prereg.json produces in the real
        # fixture (answer-key/ sits inside compute_manifest()'s own walked
        # set, spec.md Decision 2/R-P2.2). MUST record BOTH drift classes,
        # never a precedence choice between them.
        d_d = _self_test_make_ff_run_dir(tmproot, "s2-monolithic-99fd", intact_step,
                                           arm_overrides={"recorded_answer_key_digest": "deadbeef" * 8,
                                                            "recorded_fixture_digest": "deadbeef" * 8})
        row_d, *_ = build_row_failure_flood(d_d, surfaces, digests, {})
        case_d = (row_d["state"] == "void" and row_d["void_reason"] == "input-provenance-mismatch"
                   and "answer-key-drift" in row_d["anomaly_classes"]
                   and "fixture-drift" in row_d["anomaly_classes"])
    finally:
        shutil.rmtree(tmproot)
    cases = [
        ("a. all three digests present and agreeing -> complete (task 3.4's own negative control)", case_a),
        ("b. recorded fixture digest disagrees with the real v1 MANIFEST.sha256 -> void:"
         " input-provenance-mismatch, fixture-drift, never answer-key-drift", case_b),
        ("c. version present, recorded fixture digest null -> void: input-provenance-missing,"
         " provenance-capture-incomplete (never fixture-drift, never pre-scheme-provenance)", case_c),
        ("d. one v2 run whose answer-key AND fixture digests both drift at once -> void:"
         " input-provenance-mismatch, BOTH answer-key-drift and fixture-drift present"
         " (task 3.3, R-P2.2/R-P2.2a)", case_d),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] build_row_failure_flood fixture provenance {name}")
    return ok


def _self_test_fixture_digest_at():
    """run-input-provenance task 3.8 — a gatekeeping finding raised after
    Sibling 3 was committed, task 2.0's own finding recursed into Face B:
    fixture_digest_at()'s own computation was proven ZERO ways.
    `_self_test_build_row_fixture_provenance()` (task 3.2/3.3/3.4) and every
    other self-test that carries a `recorded_fixture_digest` default derives
    its expected value by calling `fixture_digest_at()` itself (:1526, :1564,
    :1627, :1682, :1784, :1897, :1972-73), so both sides of every comparison
    move together and a `return "constant"` body left all 58 cases green.
    One case closes that, never calling the function under test to build its
    own expected value:

    a. the digest MUST move when the digested bytes move — proven against
    itself, on a synthetic root this case builds and mutates, never against
    another self-test's own fixture. Mirrors task 2.0 part 1's pattern in
    shape (same idea as `_self_test_answer_key_set_digest()`'s own case a,
    applied to `fixture_digest_at()` instead of `answer_key_set_digest()`),
    but NOT verbatim in the mutation's own shape — see the paragraph below,
    a correction the orchestrator's own independent mutation-proof forced
    after this case's first version was already committed (task 3.8's own
    amendment, closing a second, deeper finding of the same class task 3.8
    itself exists to close).

    **The mutation is same-length, one byte changed — deliberately, not an
    append.** The first version of this case mutated by *appending* a line
    (`"...src/a.ts\n"` -> `"...src/a.ts\nmutated  src/b.ts\n"`), which changes
    the byte length along with the content. That shape is satisfiable by any
    wrong implementation that merely varies with length — the orchestrator's
    own follow-up mutation-proof, `sha256_hex(str(len(manifest.read_bytes()))
    .encode())` (hash the byte COUNT, never the bytes), still produced
    `digest_before != digest_after` under an append and stayed green. This
    matters more here than it did for task 2.0's own identically-shaped
    append case: Face A's case is backstopped by a real cross-language pin
    (task 2.0 part 2), and a length-hashing Python side would disagree with
    the bash side and turn THAT case red regardless of this one's own
    weakness. Face B has no pin — correctly, per the paragraph below — which
    makes this single case the ONLY proof `fixture_digest_at()`'s computation
    has. A sole proof must not be satisfiable by an implementation that never
    reads the content, so the mutation here changes one byte at a fixed
    length (`"deadbeef  src/a.ts\n"` -> `"deadbeee  src/a.ts\n"`) instead of
    appending a line. This one change strictly dominates the append form: it
    still catches a constant body and a path-hashing body, and it additionally
    catches a length-hashing body, which the append form could not.

    No cross-language pin is added here, unlike task 2.0 part 2 (Face A) and
    task 2.1 (Face C) — and none is needed. `rig/run-pipeline.sh`'s own
    `RECORDED_FIXTURE_DIGEST` (task 3.1, `:738`) computes the identical
    `hashlib.sha256(open(path, "rb").read()).hexdigest()` idiom over the same
    file bytes as `fixture_digest_at()` does here — the same idiom
    `LOCKFILE_SHA256` already uses, chosen at task 3.1 specifically so no
    independent reimplementation exists on either side to drift apart (see
    task 3.1's own done-note in tasks.md). A pin asserts two independent
    algorithms agree; there is only one algorithm here, expressed twice in
    two languages with no room for either side to diverge in shape (no
    sort order, no line-joining convention, nothing to disagree about except
    the literal bytes both sides already read from the same file). Adding a
    pin here would prove nothing beyond what case (a) already proves, and a
    later reader finding "no pin" next to Face A's and Face C's pins should
    read this paragraph rather than add one."""
    tmproot = Path(tempfile.mkdtemp())
    try:
        fixture_root = tmproot / "fixture"
        fixture_root.mkdir(parents=True)
        (fixture_root / "MANIFEST.sha256").write_text("deadbeef  src/a.ts\n")

        digest_before = fixture_digest_at(fixture_root)
        # Same-length, one byte changed (never an append — see the docstring
        # above): "deadbeef" -> "deadbeee", identical byte count. A
        # length-varying mutation here would be satisfiable by an
        # implementation that hashes the byte COUNT rather than the bytes
        # themselves; this form is not.
        (fixture_root / "MANIFEST.sha256").write_text("deadbeee  src/a.ts\n")
        digest_after = fixture_digest_at(fixture_root)
        case_fires = digest_before is not None and digest_before != digest_after
        assert len("deadbeef  src/a.ts\n") == len("deadbeee  src/a.ts\n"), \
            "the mutation MUST be same-length — a length change would let a" \
            " length-hashing implementation pass this case undetected"
    finally:
        shutil.rmtree(tmproot)
    cases = [
        ("a. mutating MANIFEST.sha256's bytes (same length, one byte"
         " changed — never an append) changes the digest, proven against"
         " itself, not a second self-test's own fixture", case_fires),
    ]
    ok = all(c for _, c in cases)
    for name, cond in cases:
        print(f"  [{'PASS' if cond else 'FAIL'}] fixture_digest_at {name}")
    return ok


def run_self_test() -> bool:
    print("derive.py self-test (ADR 0013 — R-F2.2/R-F3.2/R-F7.1/R-F7.3, restoring three prior"
          " batches' own scratch verification; run-input-provenance Sibling 1 — Face A +"
          " WARNING-14, R-P2/R-P3/R-P4/R-P5):")
    results = [
        _self_test_parse_root_cause_report(),
        _self_test_score_diagnostic_attribution(),
        _self_test_suite_state_cause(),
        _self_test_read_root_cause_report_handoff(),
        _self_test_answer_key_set_digest(),
        _self_test_preimage_digest_pin(),
        _self_test_load_surface_preimage_pin(),
        _self_test_build_row_model_mismatch(),
        _self_test_build_row_token_breakdown(),
        _self_test_build_row_suite_state_and_attribution(),
        _self_test_build_row_answer_key_provenance(),
        _self_test_build_row_surface_preimage_provenance(),
        _self_test_build_row_fixture_provenance(),
        _self_test_fixture_digest_at(),
    ]
    ok = all(results)
    print("\nself-test: all cases passed" if ok else "\nSELF-TEST FAILED", file=sys.stderr if not ok else sys.stdout)
    return ok


def parse_args(argv):
    """Manual parsing, stdlib only (decisions/0011) — two recognised flags.
    --self-test is flag-gated (ADR 0013, mirroring collect.py's own
    convention) and never runs unconditionally; it is checked by main()
    before --experiment is validated, the same order collect.py uses."""
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

    answer_keys = reg["load_answer_keys"]()
    if not run_self_tests(answer_keys):
        print("\nSelf-test FAILED — a detector cannot be proven to fire. Refusing to derive rows.", file=sys.stderr)
        return 1

    surfaces = reg["load_surfaces"]()
    digests = {
        "fixture": {v: reg["fixture_digest"](v, root) for v, root in reg["fixture_roots"].items()},
        "checker": CHECKER_DIGEST,
    }
    if reg.get("answer_key_digest"):
        digests["answer_key"] = {v: reg["answer_key_digest"](v, root) for v, root in reg["fixture_roots"].items()}

    runs_root = reg["runs_root"]
    run_dirs = sorted(p for p in runs_root.glob("*") if p.is_dir()) if runs_root.is_dir() else []
    built = []
    for run_dir in run_dirs:
        result = reg["row_builder"](run_dir, surfaces, digests, answer_keys)
        if result:
            built.append(result)

    # tool-surface-v1 ONLY (design.md Decision 7's own paired claim, unique to
    # that experiment's broad/scoped cell shape) — untouched, unrenamed, same
    # call as before the dispatcher existed.
    if reg["apply_ambient_drift_pairing"]:
        apply_ambient_drift_pairing(built)

    rows = sorted((b[0] for b in built), key=lambda r: r["run_id"])
    results_dir = reg["results_dir"]
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / "runs.jsonl"
    with out_path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True))
            f.write("\n")

    print(f"\nderived {len(rows)} row(s) from {len(run_dirs)} run dir(s) -> {out_path.relative_to(REPO_ROOT)}")
    for row in rows:
        print(f"  {row['run_id']}: state={row['state']}"
              + (f" ({row['void_reason']})" if row["void_reason"] else "")
              + (f" classification={row['classification']}" if row.get("classification") else "")
              + (f" verdict={row['verdict']}" if row.get("verdict") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
