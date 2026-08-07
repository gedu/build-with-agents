// handlers/checkout.js — checkout total computation.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v1).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v2/
// directory instead (sdd/measurement-rig/design.md, Decision 4).

const { computeDiscount } = require('../lib/pricing');
const { computeShippingCost } = require('../lib/shipping');

function computeTotal(subtotal, baseShippingRate) {
  const discount = computeDiscount(subtotal);
  const shipping = computeShippingCost(subtotal, baseShippingRate);
  return subtotal - discount + shipping;
}

module.exports = { computeTotal };
