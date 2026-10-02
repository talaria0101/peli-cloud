# poc

`peli-cloud-query.py` answers ONE question:

    Given a monthly budget and a shape, which providers in the catalogue can
    actually run it, and what stops the ones that cannot?

    python3 poc/peli-cloud-query.py --budget 5 --category agent-sandbox

It is a proof of concept, written 2026-10-02.

- It reads `data/ranking-cheapest-first.json`. It does not re-price. Re-pricing
  here would make the answer depend on this file instead of on the instrument
  that measured it.
- It is not imported by anything, and it must not be. A proof of concept with a
  caller is a dependency.
- It has no error paths beyond a missing catalogue, no retries, and no handling
  for a provider whose card changed shape after the catalogue date.

## What it does not handle

- egress, storage overage, IPv4, seats and 24/7 cost are not priced
- region availability and network allowlists are not re-checked
- free credit is as published, never redeemed
- `--vcpu` / `--ram` filter on the shape each row was already priced at; they do
  not re-price a row at a new shape
