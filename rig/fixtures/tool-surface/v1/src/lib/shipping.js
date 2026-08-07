// lib/shipping.js — free-shipping threshold.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v1).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v2/
// directory instead (sdd/measurement-rig/design.md, Decision 4).
//
// Correct on purpose: a plausible decoy. It sits next to pricing.js, does
// its own boundary check, and is not the seeded defect.

function computeShippingCost(subtotal, baseRate) {
  if (subtotal >= 50) {
    return 0;
  }
  return baseRate;
}

module.exports = { computeShippingCost };
