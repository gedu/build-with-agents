// lib/tax.js — regional sales-tax exemption.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v2).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v3/
// directory instead (sdd/measurement-rig/design.md, Decision 4).
//
// Correct on purpose: a plain decoy. It is not one of this fixture's
// seeded defects.

const EXEMPT_REGIONS = ['OR', 'MT', 'NH', 'DE', 'AK'];
const TAX_RATE = 0.08;

function computeTax(subtotal, regionCode) {
  if (EXEMPT_REGIONS.includes(regionCode)) {
    return 0;
  }
  return round(subtotal * TAX_RATE);
}

function round(amount) {
  return Math.round(amount * 100) / 100;
}

module.exports = { computeTax };
