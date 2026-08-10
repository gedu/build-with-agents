// lib/shipping.js — free-shipping threshold.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v2).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v3/
// directory instead (sdd/measurement-rig/design.md, Decision 4).
//
// Correct on purpose: a plain decoy. It is not one of this fixture's
// seeded defects.

function computeShippingCost(subtotal, baseRate) {
  if (subtotal >= 75) {
    return 0;
  }
  return baseRate;
}

module.exports = { computeShippingCost };
