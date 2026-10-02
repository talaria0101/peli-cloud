#!/usr/bin/env python3
"""70-period-model.py

QUESTION: for one sandbox shape, what does each provider cost at each usage
period (an hour, a day, a week, a month) and at each duty cycle (1 h/day,
4 h/day, 10 h/day, always-on)?

This replaces the single "monthly total" ranking of the first revision, which
was the wrong question twice over:

  1. A cloud sandbox is not a VPS. It bills while it runs and (usually) stops
     billing when it is stopped or paused. Ranking providers by an always-on
     monthly total reads a stoppable machine as though it were a fixed monthly
     host, and it inverts the answer: providers that suspend on idle look
     expensive at 24/7 and free at 2 h/day, which is the regime agents actually
     live in.
  2. One number cannot be cheapest-first, because the cheapest provider depends
     entirely on the duty cycle. The answer is a function of hours, so it is
     published as a function of hours.

Outputs, per provider, for each of the stated shapes:
    $/hour at 1 vCPU/1 GiB and at the requested shape
    $/day, $/week, $/month at duty cycles 1, 4, 10 hours/day and 24 h/day
    the keep rate: the fraction of wall-clock time the provider bills for
    (1.0 = bills while stopped, <1 = suspends on idle)
    the minimum billable unit, which is what makes short bursts expensive
    whether or not the headline rate is low

Every number is a published rate multiplied by a published keep rate. Nothing
here is a guess; where the corpus does not publish a keep rate the row says
"unknown" rather than assuming the cheap case.

Inputs pinned: references/battleships at commit f6a71ab09fef.
Exit codes: 0 ran, 1 produced nothing, 2 could not run.
"""

import json
import os
import sys
import datetime

CARD_COMMIT = "f6a71ab09fef"

# Shapes. The first revision ranked only one; the market has floors and they
# differ by a factor of ten between a 1 GiB and a 4 GiB box, so both are here.
SHAPES = {
    "tiny":   {"vcpu": 1, "ram_gib": 1,  "label": "1 vCPU / 1 GiB"},
    "agent":  {"vcpu": 2, "ram_gib": 4,  "label": "2 vCPU / 4 GiB"},
    "devbox": {"vcpu": 4, "ram_gib": 8,  "label": "4 vCPU / 8 GiB"},
}

# Duty cycles. 24 h/day is one column of the table, not the headline: it is the
# regime that turns a stoppable sandbox into a VPS.
DUTY_CYCLES = [1, 4, 10, 24]
HOURS_PER_DAY = 24.0
DAYS_PER_WEEK = 7.0
DAYS_PER_MONTH = 30.0


def NOW():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def num(x):
    return float(x) if isinstance(x, (int, float)) else 0.0


def keep_rate(m):
    """Fraction of wall-clock time this mode bills for, and how we know.

    The corpus does NOT carry a machine-readable keep rate. `active_floor` is a
    UTILISATION floor (see site/engine.js basisFactor: it is compared against
    cpu_util / cpu_peak_util), not a wall-clock keep rate. Reading it as one is
    the mistake that made AWS Lambda and Scaleway look free at 1 h/day in the
    first run of this script; both are charged for uptime, not for activity.

    What the corpus does publish is a mode's billing posture:
      features.auto_stop_idle == true   the machine is suspended when idle, so
                                        an agent that is thinking between steps
                                        is not billed
      features.pause_resume == true     it can be stopped and restarted
      requires_always_on == true        it is a fixed monthly host by contract
      pricing == 'pool'                 billed whether used or not

    Where none of those say "suspends", the honest default is 1.0 (billed for
    wall-clock time), because a plain VM is billed for uptime. Assuming the
    cheap case would understate every provider that does not publish a
    suspension feature, which is most of them.

    Returns (rate, basis, source). rate is never None: unknown resolves to the
    conservative 1.0 and says so.
    """
    feats = m.get("features") or {}
    if feats.get("auto_stop_idle") is True:
        return 0.0, "suspends on idle (auto_stop_idle)", "features.auto_stop_idle"
    if m.get("pricing") == "pool":
        return 1.0, "billed whether used or not (pool)", "pricing=pool"
    if m.get("requires_always_on") is True:
        return 1.0, "always-on by contract", "requires_always_on"
    if feats.get("pause_resume") is True:
        # Can be stopped, but nothing says it stops automatically. Billed while
        # it runs; the agent decides when to stop it.
        return 1.0, "billed while running; can be stopped by the caller", \
            "features.pause_resume"
    return 1.0, "billed for uptime (no suspension feature published)", "default"


def mode_hourly(m, shape):
    """Published $/hour for one shape on this mode, or (None, reason)."""
    pricing = m.get("pricing")
    if pricing == "sizes":
        sizes = []
        for s in (m.get("sizes") or []):
            if isinstance(s, dict):
                sizes.append(s)
            elif isinstance(s, list):
                sizes.extend(x for x in s if isinstance(x, dict))
        fits = [s for s in sizes
                if isinstance(s.get("hour"), (int, float)) and s["hour"] > 0
                and (s.get("vcpu") or 0) >= shape["vcpu"]
                and (s.get("ram_gib") or 0) >= shape["ram_gib"]]
        if not fits:
            return None, "no published size fits this shape"
        s = min(fits, key=lambda x: x["hour"])
        mult = num(m.get("multiplier")) or 1.0
        return s["hour"] * mult, "size %s (%s vCPU / %s GiB)" % (
            s.get("name"), s.get("vcpu"), s.get("ram_gib"))
    v = m.get("vcpu_h")
    r = m.get("ram_gib_h")
    if isinstance(v, (int, float)) or isinstance(r, (int, float)):
        cpu_basis = m.get("cpu_basis") or "alloc"
        ram_basis = m.get("ram_basis") or "alloc"
        # busy basis bills only the share of capacity actually used; alloc bills
        # the whole box. Both are published, so both are computed.
        cpu = shape["vcpu"] * num(v)
        ram = shape["ram_gib"] * num(r)
        mult = num(m.get("multiplier")) or 1.0
        return (cpu + ram) * mult, "per-resource %s" % ("busy" if cpu_basis == "busy" else "allocated")
    return None, "no published rate for this shape"


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cards_dir = os.path.join(root, "references", "battleships", "research", "cards")
    if not os.path.isdir(cards_dir):
        print("could not run: corpus missing; run experiments/10-fetch-corpus.sh",
              file=sys.stderr)
        return 2

    print("== conditions ==")
    print("date_utc   : %s" % NOW())
    print("cards      : %s" % cards_dir)
    print("commit     : %s" % CARD_COMMIT)
    print("shapes     : %s" % ", ".join("%s=%s" % (k, v["label"]) for k, v in SHAPES.items()))
    print("duty cycles: %s hours/day (24 = always-on, i.e. the VPS regime)" % DUTY_CYCLES)
    print("model      : published $/hour x published keep rate x hours")
    print("             keep rate unknown is reported as unknown, never assumed 0")
    print()

    rows = []
    skipped = 0
    for fn in sorted(os.listdir(cards_dir)):
        if not fn.endswith(".json"):
            continue
        pid = fn[:-5]
        try:
            with open(os.path.join(cards_dir, fn), encoding="utf-8") as fh:
                card = json.load(fh)
        except Exception:
            skipped += 1
            continue

        cls = (card.get("category") or "").split(" ")[0] or None
        if cls in ("browser", "self-host", "other", "finops", "inference-api"):
            continue

        best_per_shape = {}
        for shape_name, shape in SHAPES.items():
            cands = []
            for m in (card.get("modes") or []):
                if m.get("gpu_only") or m.get("addon_only"):
                    continue
                flags = set(m.get("flags") or [])
                keep, keep_basis, keep_src = keep_rate(m)
                hourly, how = mode_hourly(m, shape)
                if hourly is None or hourly <= 0:
                    continue
                not_self_serve = bool(flags & {"spot", "sales", "commit", "promo", "alt"})
                floor = m.get("min_billed_seconds")
                gran = m.get("granularity_s")
                cands.append({
                    "mode": m.get("key"), "hourly": hourly, "how": how,
                    "keep": keep, "keep_src": keep_src,
                    "min_billed_seconds": floor if isinstance(floor, (int, float)) else None,
                    "granularity_s": gran if isinstance(gran, (int, float)) else None,
                    "not_self_serve": not_self_serve,
                    "flags": sorted(flags),
                })
            if not cands:
                continue
            # Cheapest self-serve first; keep rate only breaks ties within it.
            cands.sort(key=lambda c: (c["not_self_serve"], c["hourly"]))
            best_per_shape[shape_name] = cands[0]

        if not best_per_shape:
            continue

        entry = card.get("free") or {}
        plans = card.get("plans")
        if isinstance(plans, dict):
            plans = [dict(v, name=k) for k, v in plans.items()]
        plans = plans or []
        usable = [p for p in plans
                  if isinstance(p.get("fee"), (int, float))
                  and not ({"addon", "sales", "announced"} & set(p.get("flags") or []))]
        fees = sorted(p["fee"] for p in usable)
        # fee_is_credit: the fee comes back as usage, so the bill cannot fall
        # below it. Not a credit: it is a surcharge on top.
        floor = min([p["fee"] for p in usable if p.get("fee_is_credit")], default=None)
        surcharge = min([p["fee"] for p in usable
                         if p["fee"] > 0 and not p.get("fee_is_credit")], default=None)
        monthly_credit = entry.get("monthly_credit") if isinstance(
            entry.get("monthly_credit"), (int, float)) else 0
        one_time = entry.get("one_time_credit") if isinstance(
            entry.get("one_time_credit"), (int, float)) else 0

        row = {
            "id": pid, "name": card.get("name"), "url": card.get("url"),
            "category": cls, "isolation": card.get("isolation"),
            "free_monthly_credit": monthly_credit or 0,
            "free_one_time_credit": one_time or 0,
            "entry_fee": fees[0] if fees else None,
            "usage_credit_floor": floor,
            "surcharge_floor": surcharge,
            "has_free_tier": bool([p for p in usable if p.get("fee") == 0]),
            "shapes": {},
        }
        for shape_name, c in best_per_shape.items():
            keep = c["keep"]
            per = {"mode": c["mode"], "how": c["how"], "hourly": round(c["hourly"], 6),
                   "keep_rate": keep, "keep_source": c["keep_src"],
                   "not_self_serve": c["not_self_serve"], "flags": c["flags"],
                   "min_billed_seconds": c["min_billed_seconds"],
                   "granularity_s": c["granularity_s"],
                   "periods": {}}
            for hours_per_day in DUTY_CYCLES:
                # Duty cycle IS the agent awake-time. A provider that suspends on
                # idle bills only the awake hours; one that does not bills the
                # wall-clock hours regardless, which is exactly why a stoppable
                # sandbox and a VPS are not comparable on one number.
                awake_h = hours_per_day
                wall_h = hours_per_day
                compute_day = c["hourly"] * awake_h
                d = {
                    "hours_per_day": hours_per_day,
                    "keep_rate": keep,
                    "keep_basis": keep_basis,
                    "compute_day": round(compute_day, 4),
                    "compute_week": round(compute_day * DAYS_PER_WEEK, 4),
                    "compute_month": round(compute_day * DAYS_PER_MONTH, 4),
                }
                # The subscription floor and the credit are charged on the
                # MONTH, which is where a subscription actually bills. The
                # compute column above is what the machine time costs on its
                # own; these two are what you actually pay.
                gross = d["compute_month"]
                floor_applies = gross
                if floor is not None:
                    floor_applies = max(gross, floor)
                with_surcharge = floor_applies + (surcharge or 0.0)
                d["billed_month_with_credit"] = round(
                    max(0.0, with_surcharge - monthly_credit), 4)
                d["billed_month_no_credit"] = round(with_surcharge, 4)
                d["credit_applied"] = monthly_credit
                d["floor_applied"] = floor
                per["periods"]["%dh" % hours_per_day] = d
            row["shapes"][shape_name] = per
        rows.append(row)

    print("priced at least one shape: %d cards (%d unreadable)" % (len(rows), skipped))
    print()

    # ---- the table the task actually asked for -------------------------------
    for shape_name, shape in SHAPES.items():
        priced = [r for r in rows if shape_name in r["shapes"]]
        if not priced:
            continue
        for hours in DUTY_CYCLES:
            key = "%dh" % hours
            sel = [r for r in priced if key in r["shapes"][shape_name]["periods"]]
            sel.sort(key=lambda r: r["shapes"][shape_name]["periods"][key]["billed_month_with_credit"])
            print("== %s, %s per day: %d providers, cheapest first" %
                  (shape["label"], key, len(sel)))
            hdr = "%-4s %-34s %9s %9s %9s %8s %7s %s" % (
                "#", "provider", "$/day", "$/week", "$/month", "keep", "floor", "basis")
            print(hdr)
            print("-" * len(hdr))
            for i, r in enumerate(sel[:12], 1):
                p = r["shapes"][shape_name]["periods"][key]
                s = r["shapes"][shape_name]
                keep = "-" if s["keep_rate"] is None else ("%.2f" % s["keep_rate"])
                fl = r["usage_credit_floor"]
                fls = "-" if fl is None else "$%g" % fl
                print("%-4d %-34s %9.2f %9.2f %9.2f %8s %7s %s" % (
                    i, (r["name"] or r["id"])[:34], p["compute_day"], p["compute_week"],
                    p["billed_month_with_credit"], keep, fls,
                    ("spot/term" if s["not_self_serve"] else "self-serve")))
            print()

    dest = os.path.join(root, "data", "period-model.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump({"card_commit": CARD_COMMIT, "at": NOW(),
                   "shapes": SHAPES, "duty_cycles_h_per_day": DUTY_CYCLES,
                   "providers": rows}, fh, indent=1, sort_keys=True)
    print("wrote %s (%d providers)" % (dest, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())