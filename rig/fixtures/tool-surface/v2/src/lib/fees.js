// lib/fees.js — small-order handling fee.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v2).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v3/
// directory instead (sdd/measurement-rig/design.md, Decision 4).
//
// Correct on purpose: a plausible decoy. It is not one of this fixture's
// seeded defects.

const HANDLING_FEE = 5;

function computeHandlingFee(subtotal) {
  if (subtotal < 20) {
    return HANDLING_FEE;
  }
  return 0;
}

module.exports = { computeHandlingFee };
