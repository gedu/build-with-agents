// lib/pricing.js — bulk-discount computation.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v2).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v3/
// directory instead (sdd/measurement-rig/design.md, Decision 4).
//
// The rules this function must satisfy are stated once, in
// ./pricing.contract.md — not repeated here.

function computeBulkDiscount(subtotal) {
  if (subtotal > 250) {
    return round(subtotal * 0.15);
  }
  if (subtotal > 100) {
    return round(subtotal * 0.10);
  }
  return 0;
}

function round(amount) {
  return Math.round(amount * 100) / 100;
}

module.exports = { computeBulkDiscount };
