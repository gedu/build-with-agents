#!/usr/bin/env python3
"""rig/collect.py — the Jest-JSON collector and signature normalizer for the
failure-flood-triage experiment (sdd/failure-flood-triage: spec R-F1.3,
R-F2.1-2.3, R-F10.1; design.md Decision 3, sections 4, 9b, 9c).

STDLIB ONLY, python3 (decisions/0011 — already an authorised rig
prerequisite). No Node collector: a Node collector cannot report that Node
itself is broken, and "suite did not start" is a required state (design.md
Decision 3) — so this collector owns the suite invocation and can see the
whole run/suite axis, upstream of the process it launches.

Two independent axes, never conflated (spec R-F2.1):
  run axis    — could the harness even run the collector/suite invocation.
                `collector-error` lives here, as a `void`, and is exit 2 —
                never one of the three suite states below.
  suite axis  — did the injected fixture's own suite execute.
                `ran` / `did-not-start` / `partial` (partial gains
                `partial_reason: suite-timeout` at scale, design.md 9b).

Two artifacts, not one (design.md 9b): the full `collection/1` (schema below)
is written for scoring; a separate, smaller `clusters` view — clusters,
counts, one representative each, no member lists — is what a diagnostician
receives. It is bounded by CLUSTER count, never by failure count, which is
the whole point at ~2,500 failures: the full collection carries thousands of
`member_test_ids`, the clusters view does not.

Clustering is exact-signature grouping in one pass, O(n) — no similarity
metric, no pairwise comparison, no threshold (design.md 9c: at 2,500
failures a similarity clusterer is ~3M comparisons and nondeterministic
under tie-breaking; hash grouping is neither).

The signature is computed over the matcher-shaped HEAD of the first failure
message only, truncated before any stack line and before any Expected:/
Received: body. This is load-bearing, not tidy (design.md 9c): a
table-driven case's expected/received values vary per case *within* one
root cause, and a signature taken over that body would shatter one cause
into hundreds of clusters. `signature_text` lives once per cluster
(`cluster/1`), never once per `failure/1` — at scale that is the difference
between a few KB and megabytes of repeated text.

No schema name carries a tool name (spec R-F10.1) — `collector: "jest-json@1"`
is a recorded VALUE, so a later `tsc` or lint collector is a new plugin, not
a schema change.

`--self-test` is FLAG-GATED (never runs unconditionally), per ADR 0013's
ratified shape — the precedent is `hooks/pre-commit --self-test`
(hooks/pre-commit:149), not `derive.py`'s unconditional self-test inside
`main()` (design.md's own correction #3: both patterns exist in this repo
now, deliberately, because this collector runs K times inside one measured
arm and must not print or pay for a self-test on every invocation, and each
invocation also runs a large suite (design.md 9c)).
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

SCHEMA_COLLECTION = "collection/1"
COLLECTOR_ID = "jest-json@1"
NORMALIZER_VERSION = 1

# Order-of-magnitude stated, not assumed (design.md 9b): ~2,500 failing cases
# at ~1.5-4 KB each puts a real report at order 5-20 MB. json.load handles
# that comfortably; the ceiling below is a stated bound with margin, not a
# streaming parser built ahead of any content that needs one.
DEFAULT_MAX_REPORT_BYTES = 64 * 1024 * 1024


class CollectorError(Exception):
    """Run-axis failure — the collector could not run at all. Always exit 2,
    never a suite state (design.md Decision 3's fourth-outcome-that-is-not-
    a-state)."""

    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}" if detail else reason)


# ---- the normalizer (spec R-F1.3, design.md section "The normalizer") -----

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_STACK_LINE_RE = re.compile(r"^\s*at [^\n]*$", re.MULTILINE)
_EXPECTED_RECEIVED_RE = re.compile(r"^\s*(Expected|Received)\b.*$", re.MULTILINE)
_LINECOL_RE = re.compile(r":\d+:\d+")
_WHITESPACE_RUN_RE = re.compile(r"[ \t]+")


def normalize_signature_text(raw_message: str, workspace_root: str = None) -> str:
    """Total, deterministic function: raw first-failure message -> the
    matcher-shaped head that becomes the cluster signature. Fixed order
    (design.md, algorithm item 3):

    1. strip ANSI colour
    2. normalise CRLF -> LF
    3. cut at the first stack line (`^\\s+at `) — stack frames carry only
       paths and line numbers, nothing else of value
    4. cut at the first Expected:/Received: line — the expected/received
       BODY varies per case within one root cause; the signature must not
    5. rewrite any surviving workspace-absolute path to its relative form
    6. rewrite `:<digits>:<digits>` to `:L:C`
    7. collapse whitespace runs, strip
    """
    if raw_message is None:
        raw_message = ""
    text = _ANSI_RE.sub("", raw_message)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    m = _STACK_LINE_RE.search(text)
    if m:
        text = text[: m.start()]

    m = _EXPECTED_RECEIVED_RE.search(text)
    if m:
        text = text[: m.start()]

    if workspace_root:
        root = workspace_root.rstrip("/")
        text = text.replace(root + "/", "")
        text = text.replace(root, "")

    text = _LINECOL_RE.sub(":L:C", text)
    text = _WHITESPACE_RUN_RE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return text.strip()


def signature_of(signature_text: str) -> str:
    return hashlib.sha256(signature_text.encode("utf-8")).hexdigest()[:16]


def build_test_id(file_path: str, workspace_root: str, ancestor_titles, title: str) -> str:
    """`<relpath>::<ancestor titles joined ' > '>::<title>` — relative kills
    the random `mktemp` workspace path (design.md, algorithm item 1)."""
    try:
        rel = os.path.relpath(file_path, workspace_root)
    except ValueError:
        rel = file_path
    ancestors = " > ".join(ancestor_titles or [])
    return f"{rel}::{ancestors}::{title}"


# ---- suite-state classification (design.md Decision 3's table) ------------

def classify_report(report: dict, expected_suites: int = None):
    """Returns (suite_state, partial_reason, totals) from an already-parsed
    Jest --json report. Never raises CollectorError — an absent/unparseable
    toolchain is caught before this is ever called."""
    totals = {
        "tests": report.get("numTotalTests", 0) or 0,
        "passed": report.get("numPassedTests", 0) or 0,
        "failed": report.get("numFailedTests", 0) or 0,
        "suites_expected": expected_suites if expected_suites is not None else report.get("numTotalTestSuites", 0) or 0,
        "suites_reported": report.get("numTotalTestSuites", 0) or 0,
    }
    if totals["tests"] == 0:
        # Parseable report, zero tests reported, toolchain present, fixture
        # frozen — a measurement, not an error (design.md Decision 3).
        return "did-not-start", None, totals
    if expected_suites is not None and totals["suites_reported"] < expected_suites:
        return "partial", None, totals
    return "ran", None, totals


# ---- failure/cluster construction (design.md section 4) -------------------

def collect_failures(report: dict, workspace_root: str, suite_state: str, partial_reason: str):
    """Every failed assertion in the report, plus (R-F2.3) a synthetic
    `__suite__` failure whenever `suite_state != ran`, so F0/R0 scoring never
    special-cases the suite axis."""
    failures = []
    for suite in report.get("testResults", []) or []:
        file_path = suite.get("name", "") or suite.get("testFilePath", "")
        for assertion in suite.get("assertionResults", []) or []:
            if assertion.get("status") != "failed":
                continue
            test_id = build_test_id(
                file_path, workspace_root, assertion.get("ancestorTitles"), assertion.get("title", "")
            )
            messages = assertion.get("failureMessages") or [""]
            sig_text = normalize_signature_text(messages[0], workspace_root)
            failures.append({"test_id": test_id, "status": "failed", "signature": signature_of(sig_text), "signature_text": sig_text})

    if suite_state != "ran":
        head = report.get("diagnostics_head") or partial_reason or suite_state
        sig_text = normalize_signature_text(head, workspace_root)
        failures.append({"test_id": "__suite__", "status": "failed", "signature": signature_of(sig_text), "signature_text": sig_text})

    failures.sort(key=lambda f: f["test_id"])
    return failures


def build_clusters(failures):
    """Exact-signature grouping, one pass, O(n) (design.md 9c). Total order:
    `(count desc, signature asc)` (design.md, algorithm item 5) — `cluster_id`
    is assigned from that rank, so it is deterministic and stable."""
    by_signature = {}
    for f in failures:
        g = by_signature.setdefault(f["signature"], {"signature_text": f["signature_text"], "member_test_ids": []})
        g["member_test_ids"].append(f["test_id"])

    clusters = []
    for signature, g in by_signature.items():
        members = sorted(g["member_test_ids"])
        clusters.append({
            "signature": signature,
            "signature_text": g["signature_text"],
            "count": len(members),
            "representative_test_id": members[0],
            "member_test_ids": members,
        })
    clusters.sort(key=lambda c: (-c["count"], c["signature"]))
    for i, c in enumerate(clusters, start=1):
        c["cluster_id"] = f"c{i}"
    return clusters


def identifier_set_digest(failures) -> str:
    """sha256 over sorted test_ids — the integrity guard's cheap half
    (design.md section 4): compare against C's digest and a deleted,
    renamed or skipped test is caught in one comparison."""
    ids = sorted(f["test_id"] for f in failures)
    return hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()


def build_collection(report: dict, workspace_root: str, suite_state: str, partial_reason: str, report_bytes: int, totals: dict):
    failures = collect_failures(report, workspace_root, suite_state, partial_reason)
    clusters = build_clusters(failures)
    public_failures = [{"test_id": f["test_id"], "status": f["status"], "signature": f["signature"]} for f in failures]
    public_clusters = [
        {k: c[k] for k in ("cluster_id", "signature", "signature_text", "count", "representative_test_id", "member_test_ids")}
        for c in clusters
    ]
    collection = {
        "schema": SCHEMA_COLLECTION,
        "suite_state": suite_state,
        "collector": COLLECTOR_ID,
        "normalizer_version": NORMALIZER_VERSION,
        "totals": totals,
        "report_bytes": report_bytes,
        "identifier_set_digest": identifier_set_digest(failures),
        "failures": public_failures,
        "clusters": public_clusters,
    }
    if partial_reason:
        collection["partial_reason"] = partial_reason
    if suite_state == "did-not-start":
        collection["diagnostics_head"] = report.get("diagnostics_head")
    return collection


def clusters_view(collection: dict):
    """The bounded artifact a diagnostician receives (design.md 9b): clusters,
    counts, one representative each. Deliberately drops `member_test_ids` —
    that list is what makes the full `collection/1` large at scale, and this
    view's whole reason to exist is to stay small regardless of failure
    count, bounded only by cluster count."""
    return {
        "schema": "clusters/1",
        "suite_state": collection["suite_state"],
        "clusters": [
            {k: c[k] for k in ("cluster_id", "signature", "signature_text", "count", "representative_test_id")}
            for c in collection["clusters"]
        ],
    }


# ---- suite invocation (owns the process; sees toolchain failures too) -----

def check_toolchain():
    """Node/npm absent is `collector-error`, a run-axis void, never a suite
    state (design.md Decision 3) — a Node collector could not report this
    about itself, which is why this collector is python3 (design.md
    Decision 3's option table)."""
    if shutil.which("node") is None or shutil.which("npm") is None:
        raise CollectorError("toolchain-absent", "node and/or npm not found on PATH")


def run_suite(cwd: str, report_file: str, suite_timeout_s: float, jest_args=None):
    """Invokes the suite itself, pinned `--runInBand` + a JSON report file
    (design.md section 3): single-worker execution removes worker count and
    interleaving as nondeterminism sources at the source. Returns
    (timed_out: bool)."""
    check_toolchain()
    args = ["npx", "jest", "--runInBand", "--json", f"--outputFile={report_file}"]
    args += list(jest_args or [])
    try:
        subprocess.run(args, cwd=cwd, timeout=suite_timeout_s, capture_output=True)
        return False
    except subprocess.TimeoutExpired:
        return True
    except (FileNotFoundError, OSError) as exc:
        raise CollectorError("collector-crash", str(exc))


def collect(cwd: str, report_file: str, suite_timeout_s: float, max_report_bytes: int, expected_suites: int = None, jest_args=None):
    """Runs the suite, classifies the outcome, and returns a `collection/1`
    dict. Raises CollectorError (run axis, exit 2) on anything that means
    the collector itself could not run — never on a suite outcome, however
    bad, which is always one of the three states instead (design.md
    Decision 3)."""
    workspace_root = os.path.abspath(cwd)
    timed_out = run_suite(cwd, report_file, suite_timeout_s, jest_args)

    if timed_out:
        # The suite's own timeout is separate from, and smaller than, the
        # arm's (design.md 9b) — without that separation a slow flood and a
        # hung agent are indistinguishable. Enforced by the CALLER passing a
        # suite_timeout_s smaller than its own arm timeout; this function
        # only classifies what it observed.
        report_bytes = os.path.getsize(report_file) if os.path.isfile(report_file) else 0
        totals = {"tests": 0, "passed": 0, "failed": 0, "suites_expected": expected_suites or 0, "suites_reported": 0}
        return build_collection({}, workspace_root, "partial", "suite-timeout", report_bytes, totals)

    if not os.path.isfile(report_file):
        totals = {"tests": 0, "passed": 0, "failed": 0, "suites_expected": expected_suites or 0, "suites_reported": 0}
        return build_collection({"diagnostics_head": "no report file produced"}, workspace_root, "did-not-start", None, 0, totals)

    report_bytes = os.path.getsize(report_file)
    if report_bytes > max_report_bytes:
        raise CollectorError("report-too-large", f"{report_bytes} bytes > ceiling {max_report_bytes}")

    try:
        with open(report_file, "r", encoding="utf-8") as f:
            report = json.load(f)
    except (ValueError, OSError) as exc:
        totals = {"tests": 0, "passed": 0, "failed": 0, "suites_expected": expected_suites or 0, "suites_reported": 0}
        return build_collection({"diagnostics_head": f"unparseable report: {exc}"}, workspace_root, "did-not-start", None, report_bytes, totals)

    suite_state, partial_reason, totals = classify_report(report, expected_suites)
    return build_collection(report, workspace_root, suite_state, partial_reason, report_bytes, totals)


# ---- --self-test (flag-gated; ADR 0013's ratified shape) ------------------
#
# Synthetic Jest-JSON fragments are INLINED here, per ADR 0013's
# no-fixtures-directory rule — no fixtures directory, no sample files on
# disk (design.md section "The normalizer").

_SELF_TEST_REPORT_RAN = {
    "numTotalTests": 4, "numPassedTests": 2, "numFailedTests": 2, "numTotalTestSuites": 1,
    "testResults": [
        {
            "name": "/tmp/rig-workspace.abc123/tests/math.test.js",
            "assertionResults": [
                {"status": "passed", "ancestorTitles": ["math"], "title": "adds"},
                {
                    "status": "failed", "ancestorTitles": ["math"], "title": "divides case 1",
                    "failureMessages": [
                        "expect(received).toBe(expected) // Object.is equality\n\n"
                        "Expected: 5\nReceived: 3\n"
                        "    at Object.<anonymous> (/tmp/rig-workspace.abc123/tests/math.test.js:12:34)"
                    ],
                },
                {
                    "status": "failed", "ancestorTitles": ["math"], "title": "divides case 2",
                    "failureMessages": [
                        # Case (a): same cause, differing absolute path, line/col, and
                        # differing Expected/Received body — MUST normalize identical
                        # to the fragment above. This is the amplification-at-scale
                        # requirement (design.md 9c), not only path/line/order.
                        "expect(received).toBe(expected) // Object.is equality\n\n"
                        "Expected: 9\nReceived: 1\n"
                        "    at Object.<anonymous> (/tmp/rig-workspace.def456/tests/math.test.js:99:7)"
                    ],
                },
                {
                    "status": "failed", "ancestorTitles": ["math"], "title": "parses",
                    "failureMessages": [
                        # Case (b): a genuinely different cause — MUST normalize to a
                        # DIFFERENT signature from the two above. A normalizer that
                        # always returns one constant passes (a) trivially; this is
                        # the direction that catches it (design.md 9c/table row b).
                        "TypeError: Cannot read properties of undefined (reading 'value')\n"
                        "    at Object.<anonymous> (/tmp/rig-workspace.abc123/tests/math.test.js:40:5)"
                    ],
                },
            ],
        }
    ],
}

_SELF_TEST_REPORT_DID_NOT_START = {"numTotalTests": 0, "numPassedTests": 0, "numFailedTests": 0, "numTotalTestSuites": 0, "testResults": []}

_SELF_TEST_REPORT_PARTIAL = {"numTotalTests": 10, "numPassedTests": 8, "numFailedTests": 2, "numTotalTestSuites": 2, "testResults": []}


def _self_test_normalizer_determinism_and_discrimination():
    """Cases (a) and (b) (design.md, self-test table)."""
    ok = True
    suite = _SELF_TEST_REPORT_RAN["testResults"][0]
    root = "/tmp/rig-workspace.abc123"
    div1 = suite["assertionResults"][1]["failureMessages"][0]
    div2 = suite["assertionResults"][2]["failureMessages"][0]
    parse_fail = suite["assertionResults"][3]["failureMessages"][0]

    sig_div1 = signature_of(normalize_signature_text(div1, root))
    sig_div2 = signature_of(normalize_signature_text(div2, root))
    sig_parse = signature_of(normalize_signature_text(parse_fail, root))

    case_a = sig_div1 == sig_div2
    ok = ok and case_a
    print(f"  [{'PASS' if case_a else 'FAIL'}] (a) same cause, differing path/line/col/Expected-Received -> same signature")

    case_b = sig_div1 != sig_parse
    ok = ok and case_b
    print(f"  [{'PASS' if case_b else 'FAIL'}] (b) two genuinely different causes -> different signatures"
          " (the discrimination case a constant-returning normalizer fails)")
    return ok


def _self_test_suite_states():
    """Case (c): each of the three suite states fires from a synthetic report."""
    ok = True
    state, reason, _ = classify_report(_SELF_TEST_REPORT_RAN)
    case_ran = state == "ran"
    ok = ok and case_ran
    print(f"  [{'PASS' if case_ran else 'FAIL'}] (c.1) parseable report, tests_reported > 0 -> 'ran'")

    state, reason, _ = classify_report(_SELF_TEST_REPORT_DID_NOT_START)
    case_dns = state == "did-not-start"
    ok = ok and case_dns
    print(f"  [{'PASS' if case_dns else 'FAIL'}] (c.2) zero tests reported -> 'did-not-start'")

    state, reason, _ = classify_report(_SELF_TEST_REPORT_PARTIAL, expected_suites=5)
    case_partial = state == "partial"
    ok = ok and case_partial
    print(f"  [{'PASS' if case_partial else 'FAIL'}] (c.3) suites_reported < expected -> 'partial'")

    # Disclosed simplification: this exercises build_collection's own
    # plumbing of a timeout outcome into partial/suite-timeout directly,
    # rather than collect()'s live subprocess.run(timeout=...) path — there
    # is no fixture/suite to time out against in this PR (PR3/PR4), and
    # collect()'s timed_out branch above builds exactly this shape.
    collection = build_collection({}, "/tmp/ws", "partial", "suite-timeout", 0, {"tests": 0, "passed": 0, "failed": 0, "suites_expected": 1, "suites_reported": 0})
    case_timeout = collection.get("partial_reason") == "suite-timeout" and collection["suite_state"] == "partial"
    ok = ok and case_timeout
    print(f"  [{'PASS' if case_timeout else 'FAIL'}] (c.4) suite timeout -> 'partial' with partial_reason=suite-timeout")
    return ok


def _self_test_idempotence():
    """Case (d): same input twice -> byte-identical output."""
    root = "/tmp/rig-workspace.abc123"
    totals = {"tests": 4, "passed": 2, "failed": 2, "suites_expected": 1, "suites_reported": 1}
    out1 = json.dumps(build_collection(_SELF_TEST_REPORT_RAN, root, "ran", None, 512, totals), sort_keys=True)
    out2 = json.dumps(build_collection(_SELF_TEST_REPORT_RAN, root, "ran", None, 512, totals), sort_keys=True)
    ok = out1 == out2
    print(f"  [{'PASS' if ok else 'FAIL'}] (d) same input twice -> byte-identical output")
    return ok


def _self_test_absent_toolchain():
    """Case (e): absent toolchain -> collector-error, never a suite state."""
    with mock.patch.object(shutil, "which", return_value=None):
        try:
            check_toolchain()
            fired = False
        except CollectorError as exc:
            fired = exc.reason == "toolchain-absent"
    print(f"  [{'PASS' if fired else 'FAIL'}] (e) absent toolchain -> CollectorError('toolchain-absent'), not a suite state")
    return fired


def _self_test_clusters_view_bounded():
    """clusters_view drops member_test_ids — the field that makes the full
    collection large at scale (design.md 9b)."""
    root = "/tmp/rig-workspace.abc123"
    totals = {"tests": 4, "passed": 2, "failed": 2, "suites_expected": 1, "suites_reported": 1}
    collection = build_collection(_SELF_TEST_REPORT_RAN, root, "ran", None, 512, totals)
    view = clusters_view(collection)
    ok = all("member_test_ids" not in c for c in view["clusters"]) and len(view["clusters"]) == len(collection["clusters"])
    print(f"  [{'PASS' if ok else 'FAIL'}] (f) clusters view carries no member_test_ids, one row per cluster")
    return ok


def run_self_test() -> bool:
    print("collect.py self-test (spec R-F1.3, design.md 'The normalizer'):")
    results = [
        _self_test_normalizer_determinism_and_discrimination(),
        _self_test_suite_states(),
        _self_test_idempotence(),
        _self_test_absent_toolchain(),
        _self_test_clusters_view_bounded(),
    ]
    ok = all(results)
    print("\nself-test: all cases passed" if ok else "\nSELF-TEST FAILED", file=sys.stderr if not ok else sys.stdout)
    return ok


# ---- CLI --------------------------------------------------------------

def build_arg_parser():
    p = argparse.ArgumentParser(description="Jest-JSON collector and signature normalizer (rig/collect.py).")
    p.add_argument("--self-test", action="store_true", help="run the flag-gated self-test and exit; never runs unconditionally")
    p.add_argument("--cwd", default=".", help="workspace root the suite runs in")
    p.add_argument("--report-file", help="path Jest's --outputFile writes to")
    p.add_argument("--collection-output", help="path to write the full collection/1 artifact")
    p.add_argument("--clusters-output", help="path to write the bounded clusters view")
    p.add_argument("--suite-timeout-s", type=float, default=120.0,
                    help="suite invocation timeout; MUST be smaller than the caller's own arm timeout (design.md 9b)")
    p.add_argument("--max-report-bytes", type=int, default=DEFAULT_MAX_REPORT_BYTES)
    p.add_argument("--expected-suites", type=int, default=None)
    p.add_argument("--jest-arg", action="append", default=[], help="extra argv forwarded to jest, repeatable")
    return p


def main(argv=None):
    args = build_arg_parser().parse_args(argv)

    if args.self_test:
        return 0 if run_self_test() else 1

    if not args.report_file or not args.collection_output or not args.clusters_output:
        print("collect.py: --report-file, --collection-output and --clusters-output are required "
              "for a real run (only --self-test may omit them)", file=sys.stderr)
        return 2

    try:
        collection = collect(
            cwd=args.cwd,
            report_file=args.report_file,
            suite_timeout_s=args.suite_timeout_s,
            max_report_bytes=args.max_report_bytes,
            expected_suites=args.expected_suites,
            jest_args=args.jest_arg,
        )
    except CollectorError as exc:
        print(f"collect.py: collector-error: {exc}", file=sys.stderr)
        return 2

    Path(args.collection_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.collection_output).write_text(json.dumps(collection, sort_keys=True) + "\n")
    Path(args.clusters_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.clusters_output).write_text(json.dumps(clusters_view(collection), sort_keys=True) + "\n")

    print(f"collect.py: suite_state={collection['suite_state']}"
          + (f" partial_reason={collection['partial_reason']}" if collection.get("partial_reason") else "")
          + f" failures={len(collection['failures'])} clusters={len(collection['clusters'])}"
          + f" report_bytes={collection['report_bytes']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
