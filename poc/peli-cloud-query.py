#!/usr/bin/env python3
"""peli-cloud-query.py — PROOF OF CONCEPT, ONE QUESTION:

    Given a monthly budget and a shape, which providers in the catalogue can
    actually run it, and what stops the ones that cannot?

This is a proof of concept, not a product. It answers one question and stops.
It does not re-price anything, does not retry, does not handle a provider whose
card changes shape, and must never be imported by anything else.

It reads data/ranking-cheapest-first.json, which is produced by
experiments/30-rank-providers.py. It does NOT recompute prices: doing so would
make the answer depend on this file rather than on the instrument that measured
it.

Exit codes: 0 it ran (whether or not anything matched), 1 it ran and the
catalogue is missing or empty, 2 it could not run.

Usage:
    python3 poc/peli-cloud-query.py --budget 5
    python3 poc/peli-cloud-query.py --budget 5 --vcpu 4 --ram 8 --tier self-serve
"""

import argparse
import json
import os
import sys


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--budget", type=float, required=True,
                    help="max all-in dollars per month")
    ap.add_argument("--vcpu", type=int, default=None,
                    help="required vCPU; providers whose smallest usable machine is "
                         "bigger are excluded and listed separately")
    ap.add_argument("--ram", type=float, default=None, help="required GiB")
    ap.add_argument("--tier", choices=["self-serve", "any"], default="self-serve",
                    help="self-serve excludes rows whose cheapest regime is spot, "
                         "negotiated or a term commit")
    ap.add_argument("--category", default=None, help="exact category, e.g. agent-sandbox")
    ap.add_argument("--catalogue", default=None, help="path to the ranking JSON")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cat_path = args.catalogue or os.path.join(root, "data", "ranking-cheapest-first.json")
    if not os.path.exists(cat_path):
        print("could not run: %s missing; run experiments/30-rank-providers.py first"
              % cat_path, file=sys.stderr)
        return 2
    with open(cat_path, encoding="utf-8") as fh:
        doc = json.load(fh)
    ranked = doc.get("ranked") or []
    if not ranked:
        print("ran, but the catalogue has no ranked rows", file=sys.stderr)
        return 1

    print("== conditions ==")
    print("catalogue  : %s" % os.path.relpath(cat_path, root))
    print("catalogue at: %s" % doc.get("ranked_at"))
    print("workload in catalogue: %s" % doc.get("workload_label"))
    print("query      : budget <= $%.2f/mo, %s vCPU, %s GiB, tier=%s, category=%s"
          % (args.budget,
             args.vcpu if args.vcpu else doc["workload"]["vcpu"],
             args.ram if args.ram else doc["workload"]["ram_gib"],
             args.tier, args.category or "any"))
    print()
    print("NOTE the catalogue was priced at ONE workload. --vcpu/--ram here only")
    print("filter on the shape each row was actually priced at; they do not re-price.")
    print()

    fit, too_small, too_dear = [], [], []
    for r in ranked:
        if args.tier == "self-serve" and r.get("tier") == "not-self-serve-only":
            continue
        if args.category and r.get("category") != args.category:
            continue
        shape = r.get("entry_shape") or {}
        if args.vcpu and isinstance(shape, dict) and shape.get("vcpu") is not None:
            if shape["vcpu"] < args.vcpu:
                too_small.append(r)
                continue
        if args.ram and isinstance(shape, dict) and shape.get("ram_gib") is not None:
            if shape["ram_gib"] < args.ram:
                too_small.append(r)
                continue
        if r["all_in_month_usd"] <= args.budget:
            fit.append(r)
        else:
            too_dear.append(r)

    print("== %d provider(s) at or under budget ==" % len(fit))
    print("%-4s %-30s %-14s %8s  %s" % ("rank", "provider", "category", "$/mo", "free"))
    for r in fit[:40]:
        free = []
        if r.get("free_monthly_credit"):
            free.append("$%g/mo" % r["free_monthly_credit"])
        if r.get("free_one_time_credit"):
            free.append("$%g once" % r["free_one_time_credit"])
        print("%-4d %-30s %-14s %8.2f  %s" %
              (r["rank"], (r["name"] or r["id"])[:30], (r["category"] or "-")[:14],
               r["all_in_month_usd"], ", ".join(free)))
    if len(fit) > 40:
        print("  ... and %d more" % (len(fit) - 40))

    print()
    print("== nearest 10 above budget (the ones you would otherwise have picked) ==")
    for r in sorted(too_dear, key=lambda x: x["all_in_month_usd"])[:10]:
        print("%-4d %-30s %8.2f  (%+.2f over)"
              % (r["rank"], (r["name"] or r["id"])[:30], r["all_in_month_usd"],
                 r["all_in_month_usd"] - args.budget))

    if too_small:
        print()
        print("== %d excluded for being smaller than the requested shape ==" % len(too_small))
        for r in too_small[:10]:
            print("%-4d %-30s smallest usable %s" %
                  (r["rank"], (r["name"] or r["id"])[:30],
                   (r.get("entry_shape") or {}).get("vcpu")))

    print()
    print("== what this does not handle ==")
    print("  * egress, storage overage, IPv4, seats and 24/7 cost are not priced here")
    print("  * region availability and network allowlists are not re-checked")
    print("  * a provider whose card changed after the catalogue date is not re-read")
    print("  * free credit is as published, never redeemed")
    return 0


if __name__ == "__main__":
    sys.exit(main())