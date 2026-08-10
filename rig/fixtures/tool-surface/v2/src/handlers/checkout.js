// handlers/checkout.js — checkout total computation, entry point.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v2).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v3/
// directory instead (sdd/measurement-rig/design.md, Decision 4).

const { computeBulkDiscount } = require('../lib/pricing');
const { computeShippingCost } = require('../lib/shipping');
const { computeRushFee } = require('../lib/rush');
const { computeLoyaltyDiscount } = require('../lib/loyalty');
const { computeHandlingFee } = require('../lib/fees');
const { computeTax } = require('../lib/tax');

function computeTotal(order) {
  const { subtotal, baseShippingRate, lifetimeOrders, isRush, regionCode } = order;
  const bulkDiscount = computeBulkDiscount(subtotal);
  const loyaltyDiscount = computeLoyaltyDiscount(subtotal, lifetimeOrders);
  const shipping = computeShippingCost(subtotal, baseShippingRate);
  const rushFee = isRush ? computeRushFee(subtotal) : 0;
  const handlingFee = computeHandlingFee(subtotal);
  const tax = computeTax(subtotal, regionCode);
  return subtotal - bulkDiscount - loyaltyDiscount + shipping + rushFee + handlingFee + tax;
}

module.exports = { computeTotal };
