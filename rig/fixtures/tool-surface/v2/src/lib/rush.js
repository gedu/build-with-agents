// lib/rush.js — rush-order fee.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v2).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v3/
// directory instead (sdd/measurement-rig/design.md, Decision 4).
//
// The rule this function must satisfy is stated once, in
// ./pricing.contract.md — not repeated here.

const RUSH_FEE = 12;

function computeRushFee(subtotal) {
  if (subtotal > 150) {
    return 0;
  }
  return RUSH_FEE;
}

module.exports = { computeRushFee };
