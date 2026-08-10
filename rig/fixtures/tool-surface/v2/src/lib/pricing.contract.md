# pricing.contract.md — checkout pricing rules

Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v2).
Do not edit — a fix here is a different fixture and would invalidate any
runs.jsonl row keyed on fixture_digest. Changes land in a new v3/
directory instead (sdd/measurement-rig/design.md, Decision 4).

## Rules

1. Orders with a subtotal of $100 or more receive a 10% bulk discount.
2. Orders with a subtotal over $250 receive a 15% bulk discount instead of
   the 10% tier.
3. Orders with a subtotal of $75 or more receive free shipping.
4. A rush-order fee of $12 applies unless the subtotal is $150 or more.
5. Loyalty members with 5 or more lifetime orders receive an extra 5%
   discount, applied in addition to the bulk discount.
6. Orders with a subtotal under $20 pay a $5 handling fee.
7. Orders from a region on the exempt list pay no sales tax.

`lib/pricing.js`, `lib/shipping.js`, `lib/rush.js`, `lib/loyalty.js`,
`lib/fees.js` and `lib/tax.js` implement these rules.
