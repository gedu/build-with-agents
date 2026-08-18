"""rig/fixtures/failure-flood/v2/tools/axis_table.py — the axis table for
tools/generate-cases.py (sdd/failure-flood-triage spec Decision B, R-F9.1-9.2;
design.md Decision 9a). PURE DATA: no control flow beyond simple list
comprehensions and no I/O, so nothing here can vary run to run.

Never materialised into any agent workspace (design.md's materialised /
never-materialised manifest split) — this file describes the amplification
structure and must not be visible to a measured arm, exactly like
`answer-key/` is never inside cwd.

Every list below is read by generate-cases.py in the order given, but the
generator's own `--self-test` proves the emitted case tables are identical
regardless of that order: output is sorted by content before it is written,
never by this file's list order (Decision 9a: "no iteration over unordered
input").

Six modules, one axis dict each, matching the measured base-case counts
frozen in spec.md Decision B (59 total: 15+12+9+8+8+7). Target multiplier is
~48x per module (within the operator-confirmed ~44-51x range), landing the
aggregate in the ~2,600-3,000 / ~433-500:1 target band — achieved counts are
reported by generate-cases.py itself, never assumed here (R-F9.2).
"""

# --- applyKeypadInput (15 real cases) --------------------------------------
APPLY_KEYPAD_INPUT = {
    "currents": ["", "0", "5", "9", "12", "120", "0.", "12.", "12.5", "1.123456"],
    "keys": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "back"],
    "max_decimals": [0, 1, 2, 3, 4, 6],
}  # 10 * 12 * 6 = 720

# --- confirmSeed (12 real cases) --------------------------------------------
CONFIRM_SEED = {
    "word_pool_size": 24,             # synthetic tokens "w00".."w23"
    "seed_offsets": list(range(21)),  # 21 distinct 12-word rotations of the pool
    "correctness_patterns": [
        (a, b, c)
        for a in ("correct", "wrong", "null")
        for b in ("correct", "wrong", "null")
        for c in ("correct", "wrong", "null")
    ],  # 3^3 = 27, one entry per CONFIRM_POSITIONS slot
}  # 21 * 27 = 567

# --- parseTransfers (9 real cases) ------------------------------------------
PARSE_TRANSFERS = {
    "directions": ["in", "out"],
    "account_cases": ["lower", "upper", "mixed"],
    "amounts": ["10.0", "0.5", "1.482513", "999.999999", "0.000001", "12345.6"],
    "timestamps": [1000, 1500, 2000, 2500, 3000, 3500],
    "paymaster_modes": ["none", "fee"],
}  # 2 * 3 * 6 * 6 * 2 = 432

# --- formatTokenAmount (8 real cases) ---------------------------------------
FORMAT_TOKEN_AMOUNT = {
    "sentinel_base_units": [None, "", "0"],
    "numeric_base_units_count": 21,  # + 3 sentinels above = 24
    "decimals": [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 24, 30],
}  # 24 * 16 = 384

# --- isValidEthereumAddress (8 real cases) ----------------------------------
IS_VALID_ETHEREUM_ADDRESS = {
    "hex_body_count": 24,
    "mutations": [
        "identity", "uppercase_hex", "mixed_case", "no_prefix", "too_short",
        "too_long", "non_hex_char", "empty", "bare_prefix", "uppercase_prefix",
        "leading_space", "trailing_space", "double_prefix", "unicode_digit",
        "plus_prefix", "newline_middle",
    ],
}  # 24 * 16 = 384

# --- balanceOfCall (7 real cases) -------------------------------------------
BALANCE_OF_CALL = {
    "encode_address_count": 144,
    "decode_sentinels": ["", "0x", "0x" + "0" * 64],
    "decode_hex_count": 189,  # + 3 sentinels above = 192
}  # 144 + 192 = 336

AXIS_TABLE = {
    "applyKeypadInput": APPLY_KEYPAD_INPUT,
    "confirmSeed": CONFIRM_SEED,
    "parseTransfers": PARSE_TRANSFERS,
    "formatTokenAmount": FORMAT_TOKEN_AMOUNT,
    "isValidEthereumAddress": IS_VALID_ETHEREUM_ADDRESS,
    "balanceOfCall": BALANCE_OF_CALL,
}

# Measured base-case counts (spec.md Decision B), used only for the reported
# ratio — never for generation itself, which reads the axis lists above.
BASE_CASE_COUNTS = {
    "applyKeypadInput": 15,
    "confirmSeed": 12,
    "parseTransfers": 9,
    "formatTokenAmount": 8,
    "isValidEthereumAddress": 8,
    "balanceOfCall": 7,
}
