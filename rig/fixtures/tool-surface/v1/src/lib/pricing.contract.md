# pricing.contract.md — bulk-discount boundary

Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v1).
Do not edit — a fix here is a different fixture and would invalidate any
runs.jsonl row keyed on fixture_digest. Changes land in a new v2/
directory instead (sdd/measurement-rig/design.md, Decision 4).

## Contract

Orders with a subtotal of **$100 or more** receive a 10% bulk discount.

The boundary is **inclusive**: an order landing exactly on $100.00 is "at
least $100" and must receive the discount. "At least" does not mean
"more than."

`lib/pricing.js` is the implementation of this contract.
