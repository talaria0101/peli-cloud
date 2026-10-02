#!/usr/bin/env python3
"""20-extract-provider-universe.py

QUESTION: for every provider card in the battleships corpus, what is the cheapest
monthly price a paying customer can actually reach, measured only from primary
card fields (plan fees, resource rates, published sizes) with no reliance on the
upstream engine's own total?

This is deliberately NOT site/engine.js. That file is the thing under test, and
an extractor that calls it reports the subject's own opinion of itself
(methodology section 4.5: measure from outside the thing you are measuring).
Where this file and the engine disagree, that disagreement is the finding.

Inputs pinned: references/battleships at the commit named in CARD_COMMIT, fetched
by experiments/10-fetch-corpus.sh.

Exit codes: 0 cards extracted, 1 extraction produced nothing, 2 could not run.
"""

import json
import os
import sys
import hashlib
import datetime
from collections import Counter

CARD_COMMIT = "f6a71ab09fefa68e355ef47c52315e099f99c921"
CARDS_SUBDIR = "research/cards"
HOURS_PER_MONTH = 730.0  # upstream engine constant; stated here so it is visible


def NOW():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def known(x):
    """A published number: not None, not NaN, not a string. Zero counts.

    Zero is deliberately allowed here, because it is the CORRECT value for a
    plan fee (a free tier) and for a $0 credit. A $0/hour SIZE is a different
    animal and is filtered by rate_known() below.
    """
    if x is None:
        return False
    if isinstance(x, str):
        return False
    if isinstance(x, float) and x != x:
        return False
    return True


def rate_known(x):
    """A published hourly RATE, which must be strictly positive.

    Why this is separate from known(): research/cards/aws-ec2.json mode
    `gpu-l4` lists `g6.xlarge` at `"hour": 0` because AWS no longer publishes a
    price for it. Left in the extracted size list it is worse than useless: the
    ranker picks the cheapest size that fits, selects the $0 row, then drops the
    whole card for being free, when the card in fact has a real $0.50 size beside
    it. Found by the guard-mutation review on 2026-10-02 with a planted
    [$0, $0.50] card. A $0 plan fee must NOT be filtered by this: a free plan
    is real and is how most of this corpus charges.
    """
    return known(x) and isinstance(x, (int, float)) and float(x) > 0


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def shape_resource_rate(m):
    """Cheapest published per-resource hourly rate for one mode.

    Returns (vcpu_h, ram_gib_h, basis) where each element may be None. For
    'sizes' pricing there is no per-resource rate; the caller uses size tables.
    """
    v = m.get("vcpu_h")
    r = m.get("ram_gib_h")
    return (v if known(v) else None,
            r if known(r) else None,
            m.get("cpu_basis") or m.get("ram_basis") or "alloc")


def flatten_sizes(sizes):
    """Return (flat_list, nested_rows). A size element is normally an object,
    but several cards nest a list inside `sizes` (scaleway dedicated-compute
    nests the MEMORY3 row; coasty wraps its single rate in a one-element list).
    A size whose vCPU/RAM are null sells a rate without a machine shape; it is
    kept but marked, because the engine prices it and a shape-less rate is still
    a rate.
    """
    flat, nested = [], 0
    for s in (sizes or []):
        if isinstance(s, dict):
            flat.append(s)
        elif isinstance(s, list):
            nested += 1
            flat.extend(x for x in s if isinstance(x, dict))
    return flat, nested


def usable_sizes(sizes):
    """Sizes with a published POSITIVE hourly rate, cheapest-first order kept.

    A $0 rate is not a free size; it is an unpriced placeholder (aws-ec2's
    gpu-l4 g6.xlarge is the live example). It is excluded here so it can never
    be picked as the cheapest option, and its count is reported separately.
    """
    flat, nested = flatten_sizes(sizes)
    ok = [s for s in flat if rate_known(s.get("hour"))]
    return ok, nested


def cheapest_size_h(m):
    """Lowest published hourly price among a mode's size table, with its shape.

    Prefers sizes that publish a machine shape; a shape-less size is the
    fallback. See flatten_sizes for the nested-row irregularity.
    """
    ok, nested = usable_sizes(m.get("sizes"))
    if not ok:
        return {"nested_rows": nested} if nested else None
    shaped = [s for s in ok if known(s.get("vcpu")) and known(s.get("ram_gib"))]
    s = min(shaped or ok, key=lambda x: x["hour"])
    return {"name": s.get("name"), "vcpu": s.get("vcpu"), "ram_gib": s.get("ram_gib"),
            "hour": s["hour"], "disk_gib": s.get("disk_gib"),
            "nested_rows": nested,
            "shaped": bool(shaped),
            "month_cap": s.get("month_cap") if known(s.get("month_cap")) else None}


MODE_CLASSES = {}


def classify_mode(card_class, m):
    """Is this mode a legitimate answer to "run a sandbox, or a VM, or anything
    that runs my code" on a card with a published rate?

    Two states are kept apart on purpose, because collapsing them is what makes a
    catalogue wrong:

      'no'             the mode cannot carry a Linux sandbox workload at all. A
                       browser-session product (Browserbase, Browserless) sells
                       minutes of a remote browser, not machines. Ranking one
                       beside a VM provider compares two different purchases,
                       and this catalogue is of providers.
      'not-self-serve' the mode could carry the workload, but only through spot
                       pricing, a negotiated contract or a multi-month term. It
                       stays in the catalogue, flagged. It does not become the
                       headline price.
      'yes'            published rate, self-serve, reachable by a new account.

    The upstream engine reaches the same split independently: priceSoft names
    these "browser-session product, not a general sandbox", "adjacent product,
    not a like-for-like sandbox" and "interruptible (spot)".
    references/battleships/site/engine.js at commit f6a71ab09fef.
    """
    if m.get("addon_only") or m.get("gpu_only") or m.get("trial_only"):
        return "no"
    if card_class == "browser":
        return "no"
    if m.get("internet") in ("allowlist", "none"):
        return "no"
    flags = set(m.get("flags") or [])
    if flags & {"spot", "sales", "commit", "promo", "alt"}:
        return "not-self-serve"
    return "yes"


def plans_of(card):
    """Plans as a list, from either a list or a name-keyed object.

    Observed 2026-10-02 against the corpus at f6a71ab09fef: 365 of 366 cards
    carry `plans` as a JSON array; research/cards/scaleway.json carries it as an
    object keyed by plan name. An extractor that assumes one shape loses a whole
    provider silently, which is how a card's prices disappear from a table
    without anything looking wrong. Both shapes are read.
    """
    p = card.get("plans")
    if isinstance(p, list):
        return p
    if isinstance(p, dict):
        out = []
        for name, pl in p.items():
            if isinstance(pl, dict):
                pl = dict(pl)
                pl.setdefault("name", name)
                out.append(pl)
        return out
    return []


def extract_card(path):
    with open(path, encoding="utf-8") as fh:
        card = json.load(fh)
    cid = card.get("id") or os.path.basename(path)[:-5]
    modes = card.get("modes") or []
    plans = plans_of(card)
    free = card.get("free") or {}

    rows = []
    for m in modes:
        mkey = m.get("key")
        pricing = m.get("pricing")
        row = {"mode": mkey, "pricing": pricing,
               "flags": m.get("flags") or [],
               "plan_required": None, "min_commit": None,
               "buyable_month_usd": None, "entry_month_usd": None,
               "mode_class": classify_mode(card.get("category"), m),
               "vcpu_h": None, "ram_gib_h": None,
               "smallest_shape": None, "cheapest_hour": None}

        # Which plans gate this mode? Upstream tags plans with mode_keys.
        gated = [p for p in plans
                 if isinstance(p.get("mode_keys"), list) and mkey in p["mode_keys"]]
        if gated:
            cheapest_gate = min(gated, key=lambda p: p.get("fee") if known(p.get("fee")) else 0)
            row["plan_required"] = cheapest_gate.get("name")
            row["min_commit"] = cheapest_gate.get("fee") if known(cheapest_gate.get("fee")) else None

        # Do NOT let addon/gated-only plans masquerade as an entry price.
        is_addon = any("addon" in (p.get("flags") or [])
                       for p in gated) if gated else False
        row["addon_only"] = is_addon

        size = cheapest_size_h(m)
        if size and size.get("nested_rows"):
            row["nested_size_rows"] = size["nested_rows"]
        # A size table holds every size. Keep all of them, so the ranker can pick
        # the cheapest one that actually satisfies a requested shape instead of
        # the cheapest one that happens to be the smallest. Shape-less sizes are
        # kept too, marked, because a rate without a shape is still a rate.
        if pricing == "sizes":
            # Filter to POSITIVE prices here, not just at pick time. If a $0 row
            # is left in the list, the ranker's "cheapest size that fits" picks
            # it and the whole card is dropped for being free, when the card in
            # fact has a real $0.50 size next to the $0 placeholder. This was
            # a real defect: a planted card with sizes [$0, $0.50] priced as
            # None instead of $0.50. See experiments/README.md.
            ok, _nested = usable_sizes(m.get("sizes"))
            row["sizes"] = [{"name": s.get("name"), "vcpu": s.get("vcpu"),
                             "ram_gib": s.get("ram_gib"), "hour": s.get("hour"),
                             "disk_gib": s.get("disk_gib"),
                             "month_cap": s.get("month_cap"),
                             "shaped": known(s.get("vcpu")) and known(s.get("ram_gib"))}
                            for s in ok]
            row["n_zero_priced_sizes"] = sum(
                1 for s in (flatten_sizes(m.get("sizes"))[0])
                if s.get("hour") == 0)
            if _nested:
                row["nested_size_rows"] = _nested
        if pricing == "sizes" and size and rate_known(size.get("hour")):
            row["cheapest_hour"] = size["hour"]
            row["smallest_shape"] = {"name": size["name"], "vcpu": size["vcpu"],
                                     "ram_gib": size["ram_gib"]}
            # A month billed on usage alone (no cap, no floor).
            if size["month_cap"] is not None:
                row["min_commit"] = row["min_commit"] or size["month_cap"]
                row["plan_required"] = row["plan_required"] or "usage cap"
            else:
                row["buyable_month_usd"] = 0.0
        elif pricing in ("resource", "instance", "pool", "browser", None) or known(m.get("vcpu_h")):
            v, r, _ = shape_resource_rate(m)
            row["vcpu_h"], row["ram_gib_h"] = v, r
            if known(v) or known(r):
                row["buyable_month_usd"] = 0.0
        if row["min_commit"] is not None and row["buyable_month_usd"] is not None:
            row["buyable_month_usd"] += row["min_commit"]

        free_credit = free.get("one_time_credit") if known(free.get("one_time_credit")) else 0
        free_month = free.get("monthly_credit") if known(free.get("monthly_credit")) else 0
        row["free_one_time_credit"] = free_credit
        row["free_monthly_credit"] = free_month

        if row["buyable_month_usd"] is None and (row["vcpu_h"] is None and row["cheapest_hour"] is None):
            row["unpriceable"] = "no published rate or size in this mode"
        rows.append(row)

    ent = [p for p in plans if "commit" in (p.get("flags") or [])]
    sales = [p for p in plans if "sales" in (p.get("flags") or [])]
    # $0 does not distinguish "a genuine free tier" from "no price is published".
    # A card whose $0 plans are all placeholders, beta, early-access or
    # application-gated has no free tier and is recorded as unpriced.
    def _free_tier(plans_):
        return [p for p in plans_
                if known(p.get("fee")) and p["fee"] == 0
                and not ({"addon", "sales"} & set(p.get("flags") or []))]
    # An entry plan may be beta / early-access / application-gated: it is still
    # a real, published price a new account can buy. Only sales/addon/announced
    # are excluded, since those are not self-serve at all. obs = kedge and
    # microsandbox, both beta-flagged plans with published rates, which the
    # first cut wrongly dropped from the universe.
    def _entry_ok(p):
        return not ({"addon", "sales", "announced"} & set(p.get("flags") or []))
    entry_plans = [p["fee"] for p in plans if _entry_ok(p) and known(p.get("fee"))]
    entry = min(entry_plans) if entry_plans else None
    real_plans = [p for p in plans if _entry_ok(p)]

    return {
        "id": cid,
        "name": card.get("name"),
        "url": card.get("url"),
        "category": card.get("category"),
        "category_class": (card.get("category") or "").split(" ")[0] or None,
        "isolation": card.get("isolation"),
        "is_browser_product": card.get("category") == "browser",
        "card_sha256_12": digest(path),
        "n_plans": len(plans),
        "n_modes": len(modes),
        "entry_month_usd": entry,
        "has_genuine_free_tier": bool(_free_tier(plans)),
        "n_free_tier_plans": len(_free_tier(plans)),
        "entry_plan_is_beta": any("beta" in (p.get("flags") or []) for p in real_plans
                                  if known(p.get("fee")) and p["fee"] == entry),
        "min_commit_month_usd": min([p["fee"] for p in ent if known(p.get("fee"))], default=None),
        "has_sales_plan": bool(sales),
        "free_monthly_credit": free.get("monthly_credit") if known(free.get("monthly_credit")) else 0,
        "free_one_time_credit": free.get("one_time_credit") if known(free.get("one_time_credit")) else 0,
        "modes": rows,
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cards_dir = os.path.join(root, "references", "battleships", CARDS_SUBDIR)
    if not os.path.isdir(cards_dir):
        print("could not run: %s missing; run experiments/10-fetch-corpus.sh" % cards_dir,
              file=sys.stderr)
        return 2

    paths = sorted(os.path.join(cards_dir, f) for f in os.listdir(cards_dir) if f.endswith(".json"))
    out = []
    for p in paths:
        try:
            out.append(extract_card(p))
        except Exception as exc:  # a malformed card must not silently vanish
            print("WARN: %s: %s" % (p, exc), file=sys.stderr)
            out.append({"id": os.path.basename(p)[:-5], "error": str(exc), "modes": []})

    print("== conditions ==")
    print("date_utc      : %s" % NOW())
    print("cards_dir     : %s" % cards_dir)
    print("card_commit   : %s" % CARD_COMMIT)
    print("cards         : %d" % len(out))
    print("pricing_model : usage-based; a card with no plan fee is $0/mo entry")
    print()

    if not out:
        print("extraction produced nothing")
        return 1

    cats = Counter(c.get("category_class") for c in out)
    print("== categories ==")
    for k, v in cats.most_common():
        print("  %-16s %d" % (k, v))
    print()

    priced = [c for c in out if c.get("entry_month_usd") is not None]
    print("== entry price distribution (cheapest non-addon plan fee, USD/mo) ==")
    buckets = Counter()
    for c in priced:
        f = c["entry_month_usd"]
        b = ("$0" if f == 0 else "<=$10" if f <= 10 else "<=$25" if f <= 25 else
             "<=$50" if f <= 50 else "<=$100" if f <= 100 else "<=$500" if f <= 500 else ">$500")
        buckets[b] += 1
    order = ["$0", "<=$10", "<=$25", "<=$50", "<=$100", "<=$500", ">$500"]
    for b in order:
        if buckets[b]:
            print("  %-8s %d" % (b, buckets[b]))
    print()
    print("cards with no priced plan at all: %d" % (len(out) - len(priced)))
    print()

    dest = os.path.join(root, "data", "provider-universe.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump({"card_commit": CARD_COMMIT,
                   "card_count": len(out),
                   "extracted": NOW(),
                   "providers": out}, fh, indent=1, sort_keys=True)
    print("wrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())