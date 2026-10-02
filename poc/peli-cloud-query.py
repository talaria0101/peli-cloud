#!/usr/bin/env python3
"""peli-cloud-query.py — PROOF OF CONCEPT, ONE QUESTION:

    At a given duty cycle and shape, what does each provider cost per hour,
    per day, per week and per month, and which is cheapest?

This is a proof of concept, not a product. It reads
data/period-model.json, which experiments/70-period-model.py produces. It does
NOT recompute prices: doing so would make the answer depend on this file rather
than on the instrument that measured it.

Exit codes: 0 it ran, 1 it ran and the catalogue is empty, 2 could not run.

Usage:
    python3 poc/peli-cloud-query.py --hours 10
    python3 poc/peli-cloud-query.py --hours 4 --shape agent --limit 15
"""

import argparse
import json
import os
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=10,
                    help="hours per day you hold the machine (default 10)")
    ap.add_argument("--shape", default="agent", choices=["tiny", "agent", "devbox"])
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--budget", type=float, default=None,
                    help="only show providers whose month is at or under this")
    ap.add_argument("--category", default=None, help="exact category filter")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "data", "period-model.json")
    if not os.path.exists(path):
        print("could not run: %s missing; run experiments/70-period-model.py" % path,
              file=sys.stderr)
        return 2
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if not doc.get("providers"):
        print("ran, but the period model is empty", file=sys.stderr)
        return 1

    shape_label = doc["shapes"][args.shape]["label"]
    # Snap to the duty cycles actually priced, and say so rather than guessing.
    cycles = doc.get("duty_cycles_h_per_day") or [1, 4, 10, 24]
    nearest = min(cycles, key=lambda c: abs(c - args.hours))
    dkey = "%dh" % nearest

    rows = []
    for p in doc["providers"]:
        s = p.get("shapes", {}).get(args.shape)
        if not s or dkey not in s["periods"]:
            continue
        if args.category and p.get("category") != args.category:
            continue
        pd = s["periods"][dkey]
        if args.budget is not None and pd["billed_month_no_credit"] > args.budget:
            continue
        if pd["billed_month_no_credit"] <= 0.004:
            continue
        rows.append((p, s, pd))
    rows.sort(key=lambda r: r[2]["billed_month_no_credit"])

    print("== conditions ==")
    print("catalogue   : %s at %s" % (os.path.relpath(path, root), doc.get("at")))
    print("shape       : %s" % shape_label)
    print("duty cycle  : %d h/day (%d machine-hours a month at 30 days)"
          % (nearest, nearest * 30))
    if nearest != args.hours:
        print("             (you asked for %g h/day; the model prices %d, used that)"
              % (args.hours, nearest))
    print("ordering    : by month BEFORE credits, so a credit cannot buy the top row")
    print()

    print("== %d providers, cheapest first ==" % len(rows))
    print("%-4s %-32s %8s %8s %9s %9s %8s %s" %
          ("#", "provider", "$/hour", "$/day", "$/week", "$/month", "keep", "category"))
    for i, (p, s, pd) in enumerate(rows[:args.limit], 1):
        print("%-4d %-32s %8.4f %8.2f %9.2f %9.2f %8.2f %s" % (
            i, (p["name"] or p["id"])[:32], s["hourly"], pd["compute_day"],
            pd["compute_week"], pd["billed_month_no_credit"], s["keep_rate"],
            p.get("category") or "-"))

    credited = [(p, pd) for p, s, pd in rows
                if p.get("free_monthly_credit") and pd["billed_month_with_credit"] > 0.004]
    if credited:
        print()
        print("== credits that would reduce these ==")
        for p, pd in sorted(credited, key=lambda r: r[1]["billed_month_with_credit"])[:8]:
            print("%-32s $%.2f -> $%.2f  ($%g/mo credit)"
                  % ((p["name"] or p["id"])[:32], pd["billed_month_no_credit"],
                     pd["billed_month_with_credit"], p["free_monthly_credit"]))

    print()
    print("== what this does not handle ==")
    print("  * egress, storage overage, IPv4 and seats are not in these figures")
    print("  * a plan floor IS included where the card says the fee is a usage credit")
    print("  * free credit is as published, never redeemed")
    print("  * 'keep' is read from published features; 1.00 means billed for uptime")
    return 0


if __name__ == "__main__":
    sys.exit(main())