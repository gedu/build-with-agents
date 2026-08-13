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


FAILURE_FLOOD_EXPERIMENT = "failure-flood-v1"
FAILURE_FLOOD_SCHEMA_VERSION = 1
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

    # Read-back downgrades (never upgrades — same discipline as build_row's
    # own complete-only checks above): the surface/permission-mode
    # comparison is explicitly THIS file's job, never run-pipeline.sh's own
    # (task 5.2's done-note; run-pipeline.sh's read_back_init() comment:
    # "every existing precedent puts that decision in derive.py").
    ff_surface = surfaces.get(FAILURE_FLOOD_SURFACE_ARM) or []
    ff_surface_digest = surface_digest(ff_surface) if ff_surface else None
    if state == "complete":
        for step in steps_meta:
            if step.get("kind") != "model":
                continue
            step_surface = step.get("surface_sha256")
            if ff_surface_digest is not None and step_surface != ff_surface_digest:
                state, void_reason = "void", "surface-mismatch"
                anomaly_classes.add("surface-mismatch")
                break
            if step.get("permission_mode_matches_declared") is False:
                state, void_reason = "void", "permission-mode-mismatch"
                anomaly_classes.add("permission-mode-mismatch")
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
            model_turns_total += occ["model_turns"]
            if occ["peak_occupancy_tokens"] is not None:
                peak_occupancy_tokens = max(peak_occupancy_tokens or 0, occ["peak_occupancy_tokens"])
            cumulative_occupancy_tokens += occ["cumulative_occupancy_tokens"] or 0
            if occ["occupancy_is_monotone"] is not None:
                occupancy_is_monotone = (occupancy_is_monotone is not False) and occ["occupancy_is_monotone"]
            if occ["context_window_tokens"] is not None:
                context_window_tokens = occ["context_window_tokens"]
        steps_out.append(step_out)

    # ---- green-restore (R-F4.2), from the LAST 99-verify step's real
    # collection.json plus the fixture's own F0 — no capture gap here,
    # unlike diagnostic attribution below.
    suite_state = partial_reason = report_bytes = None
    verdict = integrity_guard_pass = None
    verify_path = run_dir / "steps" / "99-verify" / "collection.json"
    ak = answer_keys.get(task_id)
    if state == "complete" and verify_path.is_file() and ak:
        collection = json.loads(verify_path.read_text())
        suite_state = collection.get("suite_state")
        partial_reason = collection.get("partial_reason")
        report_bytes = collection.get("report_bytes")
        if suite_state == "ran":
            verdict, integrity_guard_pass = green_restore_verdict(
                collection.get("failures", []), ak["F0"]["failures"], ro_substrate_violation
            )

    bash_call_count_total = sum(s.get("bash_call_count", 0) for s in steps_out)
    fixture_version = FAILURE_FLOOD_FIXTURE_VERSIONS.get(task_id, "v1")

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
        "suite_state": suite_state,
        "partial_reason": partial_reason,
        "report_bytes": report_bytes,
        "verdict": verdict,
        "integrity_guard_pass": integrity_guard_pass,
        # Diagnostic attribution (R-F3.2) is DEFERRED, not invented: scoring
        # needs the model-written root-cause-report.txt file, and no step in
        # run-pipeline.sh threads that file out of the ephemeral workspace
        # before it is discarded — the same class of gap task 5.4b found and
        # closed for fix-plan.txt (which DOES get an explicit handoff copy,
        # run-pipeline.sh's own comment above run_model_step()). Found live
        # while building this row (the s1 shakedown transcript shows the
        # model reporting causes only in prose, never matching the frozen
        # `<path>:<line>`-only file format R-F3.1 requires), flagged here
        # rather than scored against the wrong artifact. A future task must
        # add a handoff copy analogous to fix-plan.txt's before these three
        # fields can be populated honestly.
        "causes_claimed": None,
        "causes_correct": None,
        "causes_present": len(ak["R0"]) if ak else None,
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
        "apply_ambient_drift_pairing": False,
    },
}


def parse_args(argv):
    """Manual parsing, stdlib only (decisions/0011) — one recognised flag."""
    experiment = "tool-surface-v1"
    i = 0
    while i < len(argv):
        if argv[i] == "--experiment":
            if i + 1 >= len(argv):
                print("--experiment requires a value", file=sys.stderr)
                sys.exit(2)
            experiment = argv[i + 1]
            i += 2
        else:
            print(f"unknown argument: {argv[i]!r}", file=sys.stderr)
            sys.exit(2)
    return experiment


def main():
    experiment = parse_args(sys.argv[1:])
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
