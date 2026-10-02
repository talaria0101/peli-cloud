#!/usr/bin/env python3
"""30-rank-providers.py

QUESTION: sorted cheapest-first, which providers does a paying buyer actually
face, and at what all-in cost for one specific, stated workload?

The workload is stated in WORKLOAD below and is the same for every provider.
Nothing is ranked on its own convenience: a hyperscaler is ranked because you can
buy its smallest machine and use it, not because it is a sandbox. Every row
carries the compromises that stand between the price and the workload, because a
price without them is the "recommendation with its failure mode removed" the
methodology warns about.

This ranks on peli-cloud's own model. It does not call battleships'
site/engine.js, which is the thing being measured; the engine is run separately
in experiments/40-crosscheck-engine.py so the two disagree in public.

Exit codes: 0 ranked, 1 nothing ranked, 2 could not run.
"""

import json
import os
import sys
import datetime
import subprocess

HOURS_PER_MONTH = 730.0

# The workload. Every number here is a choice, and changing it changes the
# ranking; they are printed with every run so a reader never has to guess.
WORKLOAD = {
    "vcpu": 2, "ram_gib": 4, "disk_gib": 20,
    "session_min": 10, "sessions_month": 300,
    "concurrency": 2, "always_on": 0,
    "monthly_credit": 0,
}
WORKLOAD_LABEL = "2 vCPU / 4 GiB / 20 GiB, 300 x 10-min sessions a month, nothing always-on"

# A plan is not a usable entry when it cannot deliver the requested shape.
# "unverified" is a real state, not a synonym for yes.
MIN_PLAN_VCPU = 2
MIN_PLAN_RAM = 4


def NOW():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_describe(path):
    try:
        return subprocess.run(["git", "-C", path, "rev-parse", "--short=12", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def known(x):
    """A published positive price. None, NaN, a string and a non-positive
    number all read as 'not published'.

    Why positive-only: observed 2026-10-02 against the corpus at f6a71ab09fef.
    research/cards/aws-ec2.json mode `gpu-l4` carries `"hour": 0` on its
    cheapest size (g6.xlarge, L4 GPU instances that AWS no longer publishes a
    price for). A truthiness test reads that 0 as a real price and ranks a
    4 vCPU GPU box at $0.00/month, which is how 45 providers ended up tied at
    the top of the first run of this script. Non-positive is not a price.
    """
    if x is None:
        return False
    if isinstance(x, str):
        return False
    if isinstance(x, float) and x != x:
        return False
    try:
        return float(x) > 0
    except (TypeError, ValueError):
        return False


def all_in_month(provider, mode, shape_wanted=True, allow_not_self_serve=False):
    """Cheapest all-in monthly dollars for this provider's best entry mode.

    Modes are filtered by the extractor's three-way classification. A
    'not-self-serve' mode (spot, negotiated, term commit, promo) is only
    considered when allow_not_self_serve is set, and when it wins, the row says
    so. Excluding them by default is the difference between "the cheapest
    sandbox" and "the cheapest sandbox nobody has to negotiate for".
    """
    compromises = []
    w = WORKLOAD
    best = None

    for m in mode.get("modes", []):
        cls = m.get("mode_class")
        if cls == "no":
            continue
        if cls == "not-self-serve" and not allow_not_self_serve:
            continue
        flags = set(m.get("flags") or [])
        if "stock" in flags:
            compromises.append("stock-limited, not guaranteed available")

        plan_fee = m.get("min_commit") or 0.0
        hour = None
        shape = m.get("smallest_shape")
        if m.get("pricing") == "sizes":
            sizes = m.get("sizes") or []
            # Cheapest published size that satisfies the requested shape. A size
            # smaller than asked is a compromise, not a match, and says so.
            fits = [s for s in sizes
                    if (not shape_wanted or (known(s.get("vcpu")) and known(s.get("ram_gib"))
                        and s["vcpu"] >= w["vcpu"] and s["ram_gib"] >= w["ram_gib"]))]
            pool = fits or sizes
            if not pool:
                continue
            s = min(pool, key=lambda x: x["hour"])
            hour = s["hour"]
            shape = {"name": s.get("name"), "vcpu": s.get("vcpu"), "ram_gib": s.get("ram_gib")}
            if shape_wanted and not fits and known(s.get("vcpu")):
                compromises.append("smallest usable size is %s vCPU / %s GiB"
                                   % (s["vcpu"], s["ram_gib"]))
            hours = w["session_min"] / 60.0 * w["sessions_month"]
            cap = s.get("month_cap")
            usage = hour * hours
            if known(cap):
                usage = min(usage, cap)
            compute = usage
        elif known(m.get("vcpu_h")) or known(m.get("ram_gib_h")):
            shape = (w["vcpu"], w["ram_gib"]) if shape_wanted else (1, 1)
            cpu_basis = m.get("cpu_basis", "alloc")
            ram_basis = m.get("ram_basis", "alloc")
            vh = m.get("vcpu_h") or 0.0
            rh = m.get("ram_gib_h") or 0.0
            cpu = shape[0] * vh * (w.get("cpu_util", 1.0) if cpu_basis == "busy" else 1.0)
            ram = shape[1] * rh * (w.get("ram_util", 1.0) if ram_basis == "busy" else 1.0)
            hours = w["session_min"] / 60.0 * w["sessions_month"]
            compute = (cpu + ram) * hours
        else:
            continue

        if not known(hour) and not (known(m.get("vcpu_h")) or known(m.get("ram_gib_h"))):
            continue

        cand = {"total": compute + plan_fee, "compute": compute, "plan_fee": plan_fee,
                "mode": m.get("mode"), "pricing": m.get("pricing"),
                "hour": hour, "vcpu_h": m.get("vcpu_h"),
                "ram_gib_h": m.get("ram_gib_h"), "shape": shape,
                "mode_class": cls, "gpu_only": bool(m.get("gpu_only")),
                "plan": m.get("plan_required")}
        if best is None or cand["total"] < best["total"]:
            best = cand

    if best is None:
        return None, "no published rate or size", compromises
    return best, None, compromises


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(root, "data", "provider-universe.json")
    if not os.path.exists(src):
        print("could not run: %s missing; run experiments/20-extract-provider-universe.py" % src,
              file=sys.stderr)
        return 2
    with open(src, encoding="utf-8") as fh:
        universe = json.load(fh)

    rows, unrankable = [], []
    for p in universe["providers"]:
        if p.get("error"):
            unrankable.append((p["id"], "card parse error: %s" % p["error"]))
            continue
        if p.get("category_class") in ("self-host", "other", "finops", "inference-api"):
            unrankable.append((p["id"], "not a compute provider (%s)" % p.get("category_class")))
            continue
        entry = p.get("entry_month_usd")
        if entry is None:
            unrankable.append((p["id"], "no priced self-serve plan"))
            continue
        # Tier 1: self-serve only. Tier 2: spot / negotiated / term commit allowed.
        best, reason, comp = all_in_month(p, p, allow_not_self_serve=False)
        best2, reason2, comp2 = all_in_month(p, p, allow_not_self_serve=True)
        if best is None and best2 is None:
            unrankable.append((p["id"], reason or reason2))
            continue
        if best is None:
            best, comp = best2, comp2
            tier = "not-self-serve-only"
        else:
            tier = "self-serve" if (best2 is None or best["total"] <= best2["total"]) else "self-serve-wins"
        row = {
            "id": p["id"], "name": p.get("name"), "url": p.get("url"),
            "category": p.get("category_class"), "isolation": p.get("isolation"),
            "entry_month_usd": entry,
            "tier": tier,
            "has_genuine_free_tier": p.get("has_genuine_free_tier"),
            "free_monthly_credit": p.get("free_monthly_credit"),
            "free_one_time_credit": p.get("free_one_time_credit"),
            "has_sales_plan": p.get("has_sales_plan"),
            "min_commit_month_usd": p.get("min_commit_month_usd"),
            "all_in_month_usd": round(best["total"], 2),
            "compute_month_usd": round(best["compute"], 2),
            "platform_fee_month_usd": round(best["plan_fee"], 2),
            "priced_by": best["mode"], "pricing_kind": best["pricing"],
            "hour": best["hour"], "vcpu_h": best["vcpu_h"], "ram_gib_h": best["ram_gib_h"],
            "entry_shape": best["shape"], "entry_plan": best["plan"],
            "card_sha256_12": p.get("card_sha256_12"),
        }
        if best2 is not None and best2["total"] > best["total"]:
            row["cheaper_with_negotiation_usd"] = round(best2["total"], 2)
            row["cheaper_with_negotiation_mode"] = best2["mode"]
            comp = list(comp) + ["cheaper only with spot / negotiated / term pricing: $%.2f" % best2["total"]]
        row["compromises"] = sorted(set(comp))
        rows.append(row)

    rows.sort(key=lambda r: (r["all_in_month_usd"], r["id"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i

    print("== conditions ==")
    print("date_utc    : %s" % NOW())
    print("universe    : %d cards at commit %s" % (universe["card_count"], universe["card_commit"]))
    print("workload    : %s" % WORKLOAD_LABEL)
    print("model       : platform fee + (cheapest published size x session hours),")
    print("              or (per-vCPU + per-GiB rates x shape x session hours).")
    print("              Always-on, egress, storage and IPv4 are NOT included;")
    print("              they are priced by the provider's own card, not here.")
    print("tiers       : self-serve = a new account can buy it at that price with no")
    print("              negotiation. not-self-serve-only = the cheapest published")
    print("              regime is spot, negotiated, or a multi-month term commit.")
    print("              Both appear; the second never outranks the first silently.")
    print()

    if not rows:
        print("nothing ranked")
        return 1

    print("== ranked %d of %d cards (%d unrankable) ==" %
          (len(rows), universe["card_count"], len(unrankable)))
    print()
    hdr = "%-4s %-30s %-13s %9s %9s %-13s %-14s %s" % (
        "rank", "provider", "category", "entry$/mo", "all-in$/mo", "isolation", "tier", "priced by")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print("%-4d %-30s %-13s %9s %9.2f %-13s %-14s %s" % (
            r["rank"], (r["name"] or r["id"])[:30], (r["category"] or "-")[:13],
            ("%.2f" % r["entry_month_usd"]) if r["entry_month_usd"] else "-",
            r["all_in_month_usd"], (r["isolation"] or "-")[:13], r["tier"], r["priced_by"]))
    print()
    print("== unrankable (%d) ==" % len(unrankable))
    for pid, why in sorted(unrankable):
        print("  %-28s %s" % (pid, why))
    print()

    out = {"workload": WORKLOAD, "workload_label": WORKLOAD_LABEL,
           "ranking_commit": git_describe(os.path.join(root, "references", "battleships")),
           "upstream_card_commit": universe["card_commit"],
           "ranked_at": NOW(),
           "ranked": rows, "unrankable": [{"id": a, "reason": b} for a, b in unrankable]}
    dest = os.path.join(root, "data", "ranking-cheapest-first.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("wrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())