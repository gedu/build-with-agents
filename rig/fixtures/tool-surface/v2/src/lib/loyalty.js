// lib/loyalty.js — loyalty-tier discount.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v2).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v3/
// directory instead (sdd/measurement-rig/design.md, Decision 4).
//
// The rule this function must satisfy is stated once, in
// ./pricing.contract.md — not repeated here.

function computeLoyaltyDiscount(subtotal, lifetimeOrders) {
  if (lifetimeOrders > 5) {
    return round(subtotal * 0.05);
  }
  return 0;
}

function round(amount) {
  return Math.round(amount * 100) / 100;
}

module.exports = { computeLoyaltyDiscount };
