#!/usr/bin/env python3
"""tools/generate-cases.py — the deterministic case-table generator for the
failure-flood-triage stage-2 fixture (sdd/failure-flood-triage: spec Decision
B, R-F9.1-9.2; design.md Decision 9a). python3, stdlib only.

WHAT THIS GENERATES, AND WHY IT IS A GENERATOR AND NOT A COMMITTED TABLE
-------------------------------------------------------------------------
"Table-driven" amplification means the extra failing cases live in DATA
consumed by one `it.each` per module, not in thousands of test files
(design.md 9a). Committing ~3,000 generated rows (~300 KB) would be
unreviewed authored bytes; committing this ~450-line generator plus its axis
table (`axis_table.py`) instead means a reader runs one deterministic program
to see the bytes, and the freeze becomes a digest (task 3.4) rather than a
pile of rows nobody reads.

The six reference implementations below are a DELIBERATE, INDEPENDENT
port of the six real TypeScript modules under ../src/, computing expected
output for the SAME CLEAN LOGIC. This is what keeps the amplified cases real
failures of real logic (R-F9.1): a generated row pairs a real input with the
clean expected output, and the row is then executed against the real,
injected TypeScript module by the `it.each` harness added to ../tests/
(never against this Python reference) — so an injected root cause produces a
genuine, observable test failure, never a synthetic assertion written to
resemble one. Generated tables are derived from CLEAN behaviour only, so
they are byte-identical between the clean and injected fixture (design.md
9a) and reveal nothing about which cause is injected where.

DETERMINISM BY CONSTRUCTION
----------------------------
No clock, no RNG, no iteration over unordered input: every row is built from
the axis table's literal values or from an index-driven formula (`range`,
modular arithmetic), and the final list for each module is SORTED BY ITS OWN
CONTENT (`json.dumps(row, sort_keys=True)`) before being written — never by
whatever order the axis table happened to list its values in. That is what
makes `--self-test`'s reordering case provable rather than assumed: shuffling
the axis table's own lists changes iteration order but not the canonical
sort key, so the emitted bytes do not change.

Output: one JSON array per module, sorted keys, `\\n`-terminated
(`<out-dir>/cases/<module>.json`), written to a per-run, machine-local
directory OUTSIDE <repo> (the same root `npm ci` already installs into,
design.md section 5) — never committed (design.md 9a).

`--self-test` is FLAG-GATED, following `rig/collect.py`'s precedent
(ADR 0013's ratified shape, hooks/pre-commit:149) — never unconditional like
`derive.py`'s. It proves, without writing any file:
  (a) determinism   — two independent builds are byte-identical
  (b) reordering     — reversing every axis-table list still byte-identical
  (c) discrimination — one changed axis value changes the emitted bytes
A generator satisfying only (a)+(b) could return a constant table and still
pass; (c) is the direction that catches that (mirrors rig/collect.py's own
case (b), design.md 9c).
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import axis_table  # noqa: E402  (sibling file, script-relative import)

# ---- reference implementations (mirror ../src/*.ts on CLEAN behaviour) ----

CONFIRM_POSITIONS = (2, 6, 10)
ETH_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
BALANCE_OF_SELECTOR = "0x70a08231"
ADDRESS_PADDING = 64
BASE_HEX_SEED = 0x1234567890ABCDEF1234567890ABCDEF12345678


def apply_keypad_input(current, key, max_decimals):
    if key == "back":
        return current[:-1]
    if key == ".":
        if "." in current:
            return current
        return "0." if current == "" else current + "."
    if current == "" or current == "0":
        return "0" if key == "0" else key
    dot_index = current.find(".")
    if dot_index != -1 and len(current) - dot_index - 1 >= max_decimals:
        return current
    return current + key


def get_seed_words(seed):
    return seed.strip().split()


def is_pick_correct(seed, position, word):
    words = get_seed_words(seed)
    seed_word = words[position] if 0 <= position < len(words) else None
    return seed_word is not None and seed_word == word


def is_confirm_correct(seed, picks):
    for index, position in enumerate(CONFIRM_POSITIONS):
        pick = picks[index] if index < len(picks) else None
        if pick is None or not is_pick_correct(seed, position, pick):
            return False
    return True


def parse_transfers(transfers, account):
    account_lc = account.lower()
    fee_by_hash = {}
    for t in transfers:
        if t["label"] == "paymasterTransaction":
            fee_by_hash[t["transactionHash"]] = t["amount"]
    result = []
    for t in transfers:
        if t["label"] != "transaction":
            continue
        direction = "in" if t["to"].lower() == account_lc else "out"
        peer = t["from"] if direction == "in" else t["to"]
        fee_amount = fee_by_hash.get(t["transactionHash"]) if direction == "out" else None
        result.append({
            "hash": t["transactionHash"], "direction": direction, "peer": peer,
            "amount": t["amount"], "timestamp": t["timestamp"],
            "blockNumber": t["blockNumber"], "feeAmount": fee_amount,
        })
    result.sort(key=lambda tx: -tx["timestamp"])
    return result


def format_token_amount(base_units, decimals):
    if base_units is None or base_units == "":
        return "0.00"
    raw = int(base_units)
    divisor = 10 ** decimals
    whole = raw // divisor
    cents_divisor = 10 ** max(decimals - 2, 0)
    cents = (raw % divisor) // cents_divisor
    return f"{whole}.{str(cents).zfill(2)}"


def is_valid_ethereum_address(address):
    return ETH_ADDRESS_RE.fullmatch(address) is not None


def encode_balance_of(account_address):
    body = account_address.lower()
    if body.startswith("0x"):
        body = body[2:]
    return BALANCE_OF_SELECTOR + body.rjust(ADDRESS_PADDING, "0")


def decode_balance_hex(result_hex):
    if result_hex in ("", "0x"):
        return "0"
    return str(int(result_hex, 16))


def hex_body(i):
    """24+144 deterministic 40-hex-char bodies, no RNG: a fixed seed offset
    by index, wrapped into the hex address space."""
    return format((BASE_HEX_SEED + i) % (16 ** 40), "040x")


# ---- per-module case builders (each reads its own axis dict, real logic) --

def build_apply_keypad_input_cases(axis):
    rows = []
    for current in axis["currents"]:
        for key in axis["keys"]:
            for max_decimals in axis["max_decimals"]:
                rows.append({
                    "current": current, "key": key, "maxDecimals": max_decimals,
                    "expected": apply_keypad_input(current, key, max_decimals),
                })
    return rows


def _seed_for_offset(offset, pool_size=24):
    words = [f"w{(offset + j) % pool_size:02d}" for j in range(12)]
    return " ".join(words)


def build_confirm_seed_cases(axis):
    rows = []
    for offset in axis["seed_offsets"]:
        seed = _seed_for_offset(offset, axis["word_pool_size"])
        words = get_seed_words(seed)
        for pattern in axis["correctness_patterns"]:
            picks = []
            for index, mode in enumerate(pattern):
                position = CONFIRM_POSITIONS[index]
                if mode == "correct":
                    picks.append(words[position])
                elif mode == "wrong":
                    wrong_index = (position + 1) % len(words)
                    picks.append(words[wrong_index])
                else:
                    picks.append(None)
            rows.append({
                "seed": seed, "picks": picks,
                "expected": is_confirm_correct(seed, picks),
            })
    return rows


_ACCOUNT_BASE = "0x998Cb71fC83Df5E21a3927E8861Aa33995522175"
_OTHER = "0xdd1ffde9c04268d555b1f965c510b2d46bc230c3"
_PAYMASTER = "0x8b1f6cb5d062aa2ce8d581942bbb960420d875ba"


def _account_variant(label):
    if label == "lower":
        return _ACCOUNT_BASE.lower()
    if label == "upper":
        return _ACCOUNT_BASE.upper()
    return _ACCOUNT_BASE  # 'mixed'


def build_parse_transfers_cases(axis):
    """`tx_hash` is derived from the case's own field VALUES (sha256 of a
    fixed-order composite key), never from a running loop counter — a
    counter-based id would depend on iteration order and break the
    reordering self-test even after the final row list is content-sorted
    (found by running the self-test, not assumed correct by inspection)."""
    rows = []
    account_lc = _ACCOUNT_BASE.lower()
    for direction in axis["directions"]:
        for case_label in axis["account_cases"]:
            for amount in axis["amounts"]:
                for timestamp in axis["timestamps"]:
                    for paymaster_mode in axis["paymaster_modes"]:
                        account = _account_variant(case_label)
                        key = f"{direction}|{case_label}|{amount}|{timestamp}|{paymaster_mode}"
                        tx_hash = "0xcase" + hashlib.sha256(key.encode()).hexdigest()[:8]
                        block = timestamp // 10 + 100
                        frm, to = (account_lc, _OTHER) if direction == "out" else (_OTHER, account_lc)
                        transfers = [{
                            "transactionHash": tx_hash, "blockNumber": block,
                            "amount": amount, "timestamp": timestamp,
                            "from": frm, "to": to, "label": "transaction",
                        }]
                        if paymaster_mode == "fee":
                            # Selected from a CANONICALLY SORTED copy, not the
                            # axis table's own list order — "next amount" by
                            # positional index would otherwise depend on
                            # iteration order and break the reordering
                            # self-test (same class of bug `tx_hash` had).
                            sorted_amounts = sorted(axis["amounts"])
                            fee_amount = sorted_amounts[(sorted_amounts.index(amount) + 1) % len(sorted_amounts)]
                            transfers.append({
                                "transactionHash": tx_hash, "blockNumber": block,
                                "amount": fee_amount, "timestamp": timestamp,
                                "from": account_lc, "to": _PAYMASTER,
                                "label": "paymasterTransaction",
                            })
                        rows.append({
                            "transfers": transfers, "account": account,
                            "expected": parse_transfers(transfers, account),
                        })
    return rows


def build_format_token_amount_cases(axis):
    base_units_list = list(axis["sentinel_base_units"])
    for i in range(axis["numeric_base_units_count"]):
        base_units_list.append(str((i + 1) * (10 ** (i % 6))))
    rows = []
    for base_units in base_units_list:
        for decimals in axis["decimals"]:
            rows.append({
                "baseUnits": base_units, "decimals": decimals,
                "expected": format_token_amount(base_units, decimals),
            })
    return rows


def _apply_address_mutation(mutation, body):
    valid = f"0x{body}"
    if mutation == "identity":
        return valid
    if mutation == "uppercase_hex":
        return f"0x{body.upper()}"
    if mutation == "mixed_case":
        mixed = "".join(c.upper() if i % 2 == 0 else c for i, c in enumerate(body))
        return f"0x{mixed}"
    if mutation == "no_prefix":
        return body
    if mutation == "too_short":
        return f"0x{body[:-1]}"
    if mutation == "too_long":
        return f"0x{body}a"
    if mutation == "non_hex_char":
        return f"0x{body[:-1]}g"
    if mutation == "empty":
        return ""
    if mutation == "bare_prefix":
        return "0x"
    if mutation == "uppercase_prefix":
        return f"0X{body}"
    if mutation == "leading_space":
        return f" {valid}"
    if mutation == "trailing_space":
        return f"{valid} "
    if mutation == "double_prefix":
        return f"0x0x{body}"
    if mutation == "unicode_digit":
        return f"0x{body[:20]}０{body[21:]}"  # fullwidth '0', not [0-9a-fA-F]
    if mutation == "plus_prefix":
        return f"+{valid}"
    if mutation == "newline_middle":
        return f"0x{body[:20]}\n{body[20:]}"
    raise ValueError(f"unknown mutation: {mutation}")


def build_is_valid_ethereum_address_cases(axis):
    rows = []
    for i in range(axis["hex_body_count"]):
        body = hex_body(i)
        for mutation in axis["mutations"]:
            address = _apply_address_mutation(mutation, body)
            rows.append({"address": address, "expected": is_valid_ethereum_address(address)})
    return rows


def build_balance_of_call_cases(axis):
    rows = []
    for i in range(axis["encode_address_count"]):
        address = f"0x{hex_body(i)}"
        rows.append({
            "function": "encodeBalanceOf", "address": address,
            "expected": encode_balance_of(address),
        })
    for result_hex in axis["decode_sentinels"]:
        rows.append({
            "function": "decodeBalanceHex", "resultHex": result_hex,
            "expected": decode_balance_hex(result_hex),
        })
    for i in range(axis["decode_hex_count"]):
        result_hex = f"0x{(i + 1) * 9999991:064x}"
        rows.append({
            "function": "decodeBalanceHex", "resultHex": result_hex,
            "expected": decode_balance_hex(result_hex),
        })
    return rows


BUILDERS = {
    "applyKeypadInput": build_apply_keypad_input_cases,
    "confirmSeed": build_confirm_seed_cases,
    "parseTransfers": build_parse_transfers_cases,
    "formatTokenAmount": build_format_token_amount_cases,
    "isValidEthereumAddress": build_is_valid_ethereum_address_cases,
    "balanceOfCall": build_balance_of_call_cases,
}


def build_all_cases(table):
    """Total function: axis table -> {module: sorted case list}. Sorted by
    each row's OWN content, never by the axis table's iteration order — the
    property the reordering self-test depends on."""
    result = {}
    for name, builder in BUILDERS.items():
        rows = builder(table[name])
        rows.sort(key=lambda r: json.dumps(r, sort_keys=True))
        for i, row in enumerate(rows):
            row["case_id"] = i
        result[name] = rows
    return result


def serialize(rows):
    return json.dumps(rows, sort_keys=True) + "\n"


def write_cases(table, out_dir):
    cases_dir = Path(out_dir) / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    all_cases = build_all_cases(table)
    paths = {}
    for name, rows in all_cases.items():
        path = cases_dir / f"{name}.json"
        path.write_text(serialize(rows))
        paths[name] = str(path)
    return all_cases, paths


# ---- --self-test (flag-gated; ADR 0013's ratified shape) ------------------

def _deep_reverse_lists(value):
    """Recursively reverses every list found, leaving scalars/tuples/dicts'
    non-list structure alone. Used to prove output is order-independent
    (Decision 9a: 'no iteration over unordered input')."""
    if isinstance(value, list):
        return [_deep_reverse_lists(v) for v in reversed(value)]
    if isinstance(value, dict):
        return {k: _deep_reverse_lists(v) for k, v in value.items()}
    return value


def _mutated_axis_table():
    import copy
    mutated = copy.deepcopy(axis_table.AXIS_TABLE)
    mutated["applyKeypadInput"]["max_decimals"] = mutated["applyKeypadInput"]["max_decimals"] + [5]
    return mutated


def _bytes_for(table):
    return {name: serialize(rows) for name, rows in build_all_cases(table).items()}


def run_self_test():
    print("generate-cases.py self-test (spec R-F9.1-9.2, design.md Decision 9a):")
    original = _bytes_for(axis_table.AXIS_TABLE)
    again = _bytes_for(axis_table.AXIS_TABLE)
    determinism_ok = original == again
    print(f"  [{'PASS' if determinism_ok else 'FAIL'}] (a) two independent builds -> byte-identical output")

    reordered_table = _deep_reverse_lists(axis_table.AXIS_TABLE)
    reordered = _bytes_for(reordered_table)
    reordering_ok = original == reordered
    print(f"  [{'PASS' if reordering_ok else 'FAIL'}] (b) every axis list reversed -> still byte-identical output")

    mutated = _bytes_for(_mutated_axis_table())
    discrimination_ok = original != mutated
    print(f"  [{'PASS' if discrimination_ok else 'FAIL'}] (c) one changed axis value -> DIFFERENT output "
          "(a constant-output generator would fail this)")

    counts = {name: len(rows) for name, rows in build_all_cases(axis_table.AXIS_TABLE).items()}
    total = sum(counts.values())
    n_causes = len(counts)
    print(f"  measured (not assumed, R-F9.2): {counts}, total={total}, "
          f"ratio={total}:{n_causes} (~{total / n_causes:.0f}:1 against {n_causes} causes)")

    return determinism_ok and reordering_ok and discrimination_ok


# ---- CLI --------------------------------------------------------------

def build_arg_parser():
    p = argparse.ArgumentParser(description="Deterministic amplified case-table generator (design.md Decision 9a).")
    p.add_argument("--self-test", action="store_true", help="run the flag-gated self-test and exit; never runs unconditionally")
    p.add_argument("--out-dir", help="per-run, machine-local directory to write cases/ into — never inside <repo>")
    return p


def main(argv=None):
    args = build_arg_parser().parse_args(argv)

    if args.self_test:
        return 0 if run_self_test() else 1

    if not args.out_dir:
        print("generate-cases.py: --out-dir is required for a real run (only --self-test may omit it)", file=sys.stderr)
        return 2

    all_cases, paths = write_cases(axis_table.AXIS_TABLE, args.out_dir)
    total = sum(len(rows) for rows in all_cases.values())
    n_causes = len(all_cases)
    print(f"generate-cases.py: wrote {len(paths)} case tables, {total} total cases "
          f"({total}:{n_causes}, ~{total / n_causes:.0f}:1 against {n_causes} causes)")
    for name in sorted(all_cases):
        base = axis_table.BASE_CASE_COUNTS[name]
        n = len(all_cases[name])
        print(f"  {name}: {n} cases (base {base}, ~{n / base:.1f}x) -> {paths[name]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
