#!/usr/bin/env python3
"""91-minimum-bill-penalty.py

QUESTION: what does the minimum billable unit do to a provider that a headline
rate hides?

A published $/hour is not what you pay for a short burst. 42 modes in the corpus
bill a minimum of one hour and 9 bill a minimum of one day. For an agent that
starts and stops a sandbox many times a day, the minimum is the price that
actually applies, and a table of headline rates hides it completely.

This is the correction to revision 3's tables. Vultr publishes $0.0298/hour,
which ranks 20th in the `agent` 10 h/day table. It also publishes a one-hour
minimum, so holding one machine for ten hours in one block costs the same as
holding ten separate machines for one hour each: $29.80 either way, and a
hundred short sessions cost $29.80 each.

The model is deliberately simple and deliberately conservative:

    billed hours per day = ceil(demand / minimum) x minimum

where `demand` is the hours the workload wants. This is the WORST case, because
it assumes every session is shorter than the minimum. A real agent that starts a
sandbox once and holds it for the hour pays once, not n times. The point is not
to predict the bill; it is to show which headline rates cannot survive contact
with a bursty workload, and it does that by sitting on the pessimistic side of
every row.

The result is a second ranking: the same providers, priced as a bursty agent
rather than a long-running one. Where the two rankings disagree, the minimum is
the reason, and the row says so.

Exit codes: 0 ran, 1 no data, 2 could not run.
"""

import json
import math
import os
import sys
import datetime

HOURS_PER_MONTH = 30.0


def NOW():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(root, "data", "period-model.json")
    if not os.path.exists(src):
        print("could not run: %s missing; run experiments/70-period-model.py" % src,
              file=sys.stderr)
        return 2
    with open(src, encoding="utf-8") as fh:
        doc = json.load(fh)

    # TWO profiles, because a single burst number hides the same error in the
    # opposite direction.
    #
    # "many short sessions": 20 starts a day of 15 minutes each = 5 hours of
    # real demand. This is the profile that punishes a long minimum. With a
    # one-hour minimum, 20 x 1 h = 20 h billed against 5 h wanted: 4x.
    #
    # "few long sessions": 5 starts a day of 2 hours each = 10 hours of demand.
    # A one-hour minimum never bites here, because every session already exceeds
    # it. This is the profile that rewards a long minimum by wasting nothing.
    #
    # Both bill the SAME 10 hours of demand in the smooth case, so the comparison
    # is like for like. The first profile is the one an agent that runs a tool
    # call, reads a result and starts again actually lives in.
    PROFILES = {
        "many-short": {"starts": 20, "hours_each": 0.25},
        "few-long":   {"starts": 5,  "hours_each": 2.0},
    }

    rows = []
    for p in doc.get("providers") or []:
        s = (p.get("shapes") or {}).get("agent")
        if not s:
            continue
        hourly = s["hourly"]
        mb = s.get("min_billed_seconds")
        gran = s.get("granularity_s")
        min_h = (mb / 3600.0) if isinstance(mb, (int, float)) and mb > 0 else 0.0
        gran_h = (gran / 3600.0) if isinstance(gran, (int, float)) and gran > 0 else 0.0

        # Smooth case: one machine held for the whole 10 hours of demand,
        # rounded up to the granularity. This is what the period tables assume.
        demand_day = 10.0
        smooth_day = demand_day
        if gran_h > 0:
            smooth_day = math.ceil(demand_day / gran_h) * gran_h

        row = {
            "id": p["id"], "name": p.get("name"), "url": p.get("url"),
            "hourly": hourly,
            "min_billed_seconds": mb, "granularity_s": gran,
            "min_billed_hours": min_h,
            "smooth_day_h": smooth_day,
            "smooth_month": round(hourly * smooth_day * HOURS_PER_MONTH, 2),
            "not_self_serve": s.get("not_self_serve"),
            "profiles": {},
        }

        for pname, prof in PROFILES.items():
            demand = prof["starts"] * prof["hours_each"]
            # Each separate start is billed at least the minimum, rounded up to
            # the granularity. Nothing is shared between starts: a minimum
            # billable unit is per instance, per start.
            per = max(prof["hours_each"], min_h)
            if gran_h > 0:
                per = math.ceil(per / gran_h) * gran_h
            billed_day = per * prof["starts"]
            # Compare like for like against the SAME demand in the smooth case.
            base = demand
            if gran_h > 0:
                base = math.ceil(base / gran_h) * gran_h
            row["profiles"][pname] = {
                "starts": prof["starts"],
                "hours_each": prof["hours_each"],
                "demand_day_h": demand,
                "billed_day_h": billed_day,
                "month": round(hourly * billed_day * HOURS_PER_MONTH, 2),
                "month_smooth_same_demand": round(hourly * base * HOURS_PER_MONTH, 2),
                "penalty_x": round(billed_day / base, 2) if base else None,
            }
        row["burst_month"] = row["profiles"]["many-short"]["month"]
        row["penalty_x"] = row["profiles"]["many-short"]["penalty_x"]
        row["penalty_usd"] = round(
            row["profiles"]["many-short"]["month"]
            - row["profiles"]["many-short"]["month_smooth_same_demand"], 2)
        rows.append(row)

    if not rows:
        print("no providers to model", file=sys.stderr)
        return 1

    print("== conditions ==")
    print("date_utc     : %s" % NOW())
    print("shape        : agent (2 vCPU / 4 GiB)")
    print("demand       : 10 machine-hours a day, every provider")
    print("profiles     : many-short = 20 starts x 0.25 h (5 h demand)")
    print("               few-long   = 5 starts x 2.0 h (10 h demand)")
    print("               both compared against the SAME demand, smoothed")
    print("rounding     : billed hours = ceil(demand / minimum) x minimum")
    print("WARNING      : the burst case is the PESSIMISTIC bound. It assumes every")
    print("               session is shorter than the minimum. A real agent that")
    print("               holds one sandbox for the hour pays once. Read these rows")
    print("               as 'this headline rate cannot survive a bursty workload',")
    print("               not as a predicted bill.")
    print()

    penalised = [r for r in rows if (r["penalty_x"] or 1) > 1.0]
    print("providers priced at the `agent` shape : %d" % len(rows))
    print("providers where the minimum bill bites : %d (many-short profile)"
          % len(penalised))
    for pname in PROFILES:
        bite = [r for r in rows if (r["profiles"][pname]["penalty_x"] or 1) > 1.0]
        print("   %-12s penalty bites on %d providers" % (pname, len(bite)))
    print()

    # The headline table: what a headline rate hides.
    worst = sorted(penalised, key=lambda r: -r["penalty_usd"])[:20]
    for pname in ("many-short", "few-long"):
        bite = sorted([r for r in rows
                       if (r["profiles"][pname]["penalty_x"] or 1) > 1.0],
                      key=lambda r: -r["profiles"][pname]["penalty_x"])[:12]
        if not bite:
            print("== %s: the minimum bill changes nothing ==" % pname)
            print("   Every provider here bills per second or per minute with no")
            print("   minimum above a minute, so a bursty and a smooth agent pay")
            print("   the same. That is a real finding about this market, not an")
            print("   absence of one.")
            print()
            continue
        print("== %s: where the minimum bill changes the answer most ==" % pname)
        print("%-30s %9s %11s %10s %8s %10s" % ("provider", "$/hour", "smooth/mo",
                                               "burst/mo", "penalty", "minimum"))
        print("-" * 88)
        for r in bite:
            mb = r["min_billed_seconds"]
            mbs = ("%g s" % mb) if isinstance(mb, (int, float)) and mb else "-"
            pr = r["profiles"][pname]
            print("%-30s %9.4f %11.2f %10.2f %7.2fx %10s" % (
                (r["name"] or r["id"])[:30], r["hourly"],
                pr["month_smooth_same_demand"], pr["month"], pr["penalty_x"], mbs))
        print()

    # Rank inversion: where the burst case reorders the market.
    smooth_rank = {r["id"]: i for i, r in
                   enumerate(sorted(rows, key=lambda x: x["smooth_month"]), 1)}
    burst_rank = {r["id"]: i for i, r in
                  enumerate(sorted(rows, key=lambda x: x["burst_month"]), 1)}
    moved = [(abs(smooth_rank[r["id"]] - burst_rank[r["id"]]), r)
             for r in rows]
    moved.sort(key=lambda x: -x[0])

    print("== biggest rank changes between a smooth and a bursty agent ==")
    print("%-30s %8s %8s %8s %s" % ("provider", "smooth#", "burst#", "moves", "minimum"))
    print("-" * 78)
    for delta, r in moved[:15]:
        if delta == 0:
            break
        mb = r["min_billed_seconds"]
        mbs = ("%g s min" % mb) if isinstance(mb, (int, float)) and mb else "none"
        direction = "down" if burst_rank[r["id"]] > smooth_rank[r["id"]] else "UP"
        print("%-30s %8d %8d %6d %-4s %s" % (
            (r["name"] or r["id"])[:30], smooth_rank[r["id"]], burst_rank[r["id"]],
            delta, direction, mbs))
    print()

    dest = os.path.join(root, "data", "minimum-bill-penalty.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump({"at": NOW(), "profiles": PROFILES,
                   "demand_hours_per_day": 10.0,
                   "caveat": "each profile is compared against the SAME demand, "
                             "smoothed; these are bounds, not predicted bills",
                   "rows": rows}, fh, indent=1, sort_keys=True)
    print("wrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())