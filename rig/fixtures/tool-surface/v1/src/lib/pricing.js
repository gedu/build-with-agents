// lib/pricing.js — bulk-discount computation.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v1).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v2/
// directory instead (sdd/measurement-rig/design.md, Decision 4).
//
// The boundary this function must satisfy is stated once, in
// ./pricing.contract.md — not repeated here.

function computeDiscount(subtotal) {
  if (subtotal > 100) {
    return Math.round(subtotal * 0.10 * 100) / 100;
  }
  return 0;
}

module.exports = { computeDiscount };
