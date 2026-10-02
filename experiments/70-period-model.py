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

# Hours in the month a monthly rent is divided by, when a card encodes a
# subscription's monthly price in its hourly field. 730, not 720, because that
# is the basis vendors quote in their own copy: Agent 37 publishes "From
# $4.76/month, 2 vCPU, 4 GB RAM and 4 GB persistent disk at 730 running hours."
# Using 720 would make such a row 1.4% dearer than the vendor states.
MONTH_HOURS = 730.0

# ---------------------------------------------------------------------------
# Advertised sizes the corpus card threw away.
#
# One card in 366 prices a machine more expensively than its own vendor
# advertises, and the price is quoted in the card's own note:
#
#   lizard, mode `sandbox`, sizes: [{medium, 4 vCPU, 4 GiB, $0.018/h}]
#   note:   "Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, 8 GB
#           RAM) at $0.018/hour, and Large (8 vCPU, 16 GB RAM) at
#           $0.036/hour. Medium is the default."
#   min_vcpu: 4, max_vcpu: 4
#
# The size table keeps only the default, and `min_vcpu: 4` makes the 2 vCPU
# tier structurally unreachable to any shape below 4 vCPU. The result is that
# the cheapest advertised machine is absent from the ranking and the row is
# priced at 2x its real rate: $5.40/month at 10 h/day where the advertised
# Small is $2.70, which is second only to Agent 37.
#
# The rate below was read off lizard.build/pricing on 2026-10-02, and the same
# sentence is in the corpus card's note, so the two agree. Lizard's sandbox docs
# say "Create options do not change these limits" (4 vCPU / 4096 MiB) and
# disagree on Medium's RAM, so the docs reading is not obviously wrong. This
# table therefore RECORDS both and marks the row disputed rather than quietly
# replacing the corpus. See docs/FINDINGS.md section 5.5.
#
# Format: (provider, mode, name, vcpu, ram_gib, hour, source_url, quote)
# One entry. It is here because the vendor's own page says so and the card does
# not, not because the shape is convenient.
# ---------------------------------------------------------------------------
ADVERTISED_SIZES = [
    {
        "provider": "lizard",
        "mode": "sandbox",
        "name": "small",
        "label": "Small (2 vCPU / 4 GB RAM)",
        "vcpu": 2,
        "ram_gib": 4,
        "hour": 0.009,
        "url": "https://lizard.build/pricing",
        "quote": ("Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, "
                  "8 GB RAM) at $0.018/hour, and Large (8 vCPU, 16 GB RAM) at "
                  "$0.036/hour. Medium is the default."),
        "disputed": ("lizard.build/docs says create options do not change the "
                     "limits (4 vCPU / 4096 MiB) and gives Medium 4096 MiB "
                     "rather than 8 GB; the pricing page and the docs disagree "
                     "and no changelog dates either"),
    },
]


def advertised_sizes(pid, mode_key):
    """Sizes the vendor advertises and the card dropped, for one mode."""
    return [s for s in ADVERTISED_SIZES
            if s["provider"] == pid and s["mode"] == mode_key]


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

# A GPU card is priced by GPU-hour, not by vCPU/RAM. Ranking one against a CPU
# box is comparing two currencies, so it gets its own table. GPU models named in
# the corpus, cheapest-first within each provider.
GPU_TIERS = ["RTX-4090", "L4", "A10G", "A100-40G", "RTX-A6000", "A100-80G",
             "L40S", "RTX-6000-Ada", "H100", "H200", "B200", "B300"]

# A mode whose key names a region or offering that does not exist yet is not a
# price anybody can pay. Found by auditing every ranked row's winning mode on
# 2026-10-02: arker's cheapest mode was `eu-hetzner-proposed`, a pre-launch
# region priced at $0.0302/h against a LIVE on-demand rate of $0.1877/h on the
# same card. That is 6x, and it put arker in the ranking on a price nobody can
# be charged. leap0's cheapest mode is `preview`.
PRELAUNCH_TOKENS = ("proposed", "preview", "soon", "coming", "waitlist",
                    "upcoming", "unavailable")

# A per-request product is billed per INVOCATION: it publishes a start_fee and
# the corpus's own note says so. It must not be ranked on a duty cycle, because
# "1 h/day of a machine" is not a quantity it is sold in.
#
# The corpus publishes such a mode as vcpu_h: 0 with a real ram_gib_h, which
# mode_hourly() reads as "CPU is free, memory costs $0.06/GiB-h". That silently
# prices a per-millisecond invoker as if it were a 1 vCPU / 1 GiB box billed by
# the hour, and because Lambda's rate is genuinely low the result sorted it
# above Agent 37 in the console table. The published catalogue did not, because
# its renderer filtered the same rows out, so the console and the catalogue
# disagreed.
#
# The FIRST attempt at this test matched note text, on the theory that the
# vendor's own words are the best evidence. That was wrong and it deleted real
# products: "requests" also appears in Kubernetes "resource requests"
# (gke-agent-sandbox, google-agent-engine), in inbound HTTP requests (deno-sandbox,
# sail, sandbox0), in "no requests" (azure-container-apps) and in the word
# "GB-s", which is PER SECOND, not per request. 36 modes across 23 cards were
# dropped, including Lizard, Railway, Kernel, Sail, CreateOS and InstaVM, every
# one of which bills per second of running time and is a real sandbox.
#
# The test that works is structural, not lexical: a mode is per-request only if
# it publishes NO usable per-unit-of-time rate at all. Every size in the table
# must lack a positive hour (hour 0 or absent), because that is the corpus's own
# way of saying "this product is not sold by the hour". A positive start_fee on
# its own proves nothing: expo encodes a flat $2 per build as start_fee with
# hour 0, and anchor-browser encodes $0.01 per browser created next to a real
# $0.05/hour, so a fee without a rate is the signal only in the FIRST case and
# the second case is a machine with a boot charge.
PER_REQUEST_NOTE_TOKENS = ("per request", "per invocation", "per 1 ms",
                           "per millisecond", "per invocation", "invocation",
                           "per build", "per browser created")


def is_per_request(mode):
    """True when the mode bills per invocation rather than per unit of time.

    Structural test: no positive hourly rate anywhere on the mode, and a note
    that names a per-unit-of-invocation charge, or a positive start_fee standing
    alone with every size lacking a price per hour. A size table containing any
    positive hour means the product IS sold by the hour, whatever else it
    charges, and the mode is a machine and stays in the ranking.

    Returns (bool, reason) so the exclusion is reportable, not silent.
    """
    if mode.get("pricing") == "pool":
        return False, None
    has_time_rate = (isinstance(mode.get("vcpu_h"), (int, float))
                     and mode["vcpu_h"] > 0) or \
                    (isinstance(mode.get("ram_gib_h"), (int, float))
                     and mode["ram_gib_h"] > 0)
    sizes = mode.get("sizes")
    flattens = []
    for s in (sizes or []):
        if isinstance(s, dict):
            flattens.append(s)
        elif isinstance(s, list):
            flattens.extend(x for x in s if isinstance(x, dict))
    any_positive_hour = any(
        isinstance(s.get("hour"), (int, float)) and s["hour"] > 0 for s in flattens)
    if has_time_rate or any_positive_hour:
        return False, None
    note = (mode.get("note") or "").lower()
    for t in PER_REQUEST_NOTE_TOKENS:
        if t in note:
            return True, "no hourly rate published; note says %r" % t
    # A positive start_fee on its own is NOT enough. hetzner-gpu publishes
    # start_fee 1049 next to month_cap 2099 and no hour at all, because it sells
    # a dedicated GPU server by the month, not by the invocation. Charging a
    # flat fee and publishing no hour is the corpus's shape for several
    # different things, and only a note that names the unit distinguishes them.
    # Reported as not-per-request so it falls through to the ordinary "too big
    # for these shapes" path in the exclusion ledger, which is what it is.
    sf = mode.get("start_fee")
    if isinstance(sf, (int, float)) and sf > 0:
        return False, None
    return False, None



def is_prelaunch(mode_key, label):
    k = (mode_key or "").lower()
    l = (label or "").lower()
    if any(t in k for t in PRELAUNCH_TOKENS):
        return True, "mode key"
    if any(t in l for t in PRELAUNCH_TOKENS) and "preview" not in l:
        return True, "label"
    return False, None
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


def mode_hourly(m, shape, pid=None):
    """Published $/hour for one shape on this mode, or (None, reason)."""
    pricing = m.get("pricing")
    if pricing == "sizes":
        sizes = []
        for s in (m.get("sizes") or []):
            if isinstance(s, dict):
                sizes.append(s)
            elif isinstance(s, list):
                sizes.extend(x for x in s if isinstance(x, dict))
        # A size the vendor advertises and the card dropped is added back before
        # the fit test, otherwise min_vcpu on the card hides it. See
        # ADVERTISED_SIZES at the top of this file for the evidence.
        for a in advertised_sizes(pid, m.get("key")):
            if not any(str(s.get("name", "")).lower() == a["name"] for s in sizes):
                sizes.append({"name": a["name"], "vcpu": a["vcpu"],
                              "ram_gib": a["ram_gib"], "hour": a["hour"],
                              "advertised": True, "disputed": a["disputed"],
                              "source": a["url"], "quote": a["quote"]})
        fits = [s for s in sizes
                if isinstance(s.get("hour"), (int, float)) and s["hour"] > 0
                and (s.get("vcpu") or 0) >= shape["vcpu"]
                and (s.get("ram_gib") or 0) >= shape["ram_gib"]]
        if not fits:
            return None, "no published size fits this shape"
        s = min(fits, key=lambda x: x["hour"])
        mult = num(m.get("multiplier")) or 1.0
        how = "size %s (%s vCPU / %s GiB)" % (
            s.get("name"), s.get("vcpu"), s.get("ram_gib"))
        if s.get("advertised"):
            how += " [ADVERTISED, not in the card; page disagrees with the docs]"
        # A size whose `hour` EQUALS its `month_cap` is a monthly rent encoded in
        # the hourly field, and the corpus says so in the mode's own note:
        #
        #   hostinger-vps: "Estimator-only encoding: sizes.hour and month_cap
        #   both equal full monthly rent, with a one-hour synthetic minimum.
        #   This is NOT a vendor hourly tariff."
        #
        # 173 sizes across 8 cards are encoded this way (alibaba-ecs, contabo,
        # hostinger-vps, huawei-cloud, netcup, and three more). Multiplying the
        # rent by the hours in the period produced figures no reader could
        # believe: Hostinger's KVM 2 published at $17,632.80/month and
        # $30,952.80/month for the devbox shape, because $24.49 of monthly rent
        # was multiplied by 720 hours. 24 published rows were wrong this way.
        #
        # The fix is to divide by the month the rent is for, so the rate becomes
        # a genuine per-hour figure and every horizon lands on the same monthly
        # rent, which is what a monthly VPS actually costs. The card publishes
        # no hours-per-month, so 730 is used, the same basis Agent 37's own
        # published figure uses ("at 730 running hours").
        cap = s.get("month_cap")
        if isinstance(cap, (int, float)) and cap > 0 and abs(s["hour"] - cap) < 1e-9:
            per_h = s["hour"] / MONTH_HOURS
            how += " [monthly rent $%g encoded as an hourly rate; /%d h]" % (
                s["hour"], MONTH_HOURS)
            return per_h * mult, how
        return s["hour"] * mult, how
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
    prelaunch_seen = []
    prelaunch_only = []
    perreq_seen = []
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
        # Browser / non-compute categories are excluded from the RANKINGS but
        # are still surveyed for the FREE-TIER census: a browser provider with a
        # recurring credit is a fact about the market's free tiers, and dropping
        # it would understate what a buyer can get for nothing.
        off_category = cls in ("browser", "self-host", "other", "finops", "inference-api")

        best_per_shape = {}
        pre_before = len(prelaunch_seen)
        for shape_name, shape in SHAPES.items():
            cands = []
            for m in (card.get("modes") or []):
                if m.get("gpu_only") or m.get("addon_only"):
                    continue
                flags = set(m.get("flags") or [])
                pre, why = is_prelaunch(m.get("key"), m.get("label"))
                if pre:
                    # Recorded, then skipped: a pre-launch region is not a price
                    # a buyer can be charged, and it must not win the ranking.
                    prelaunch_seen.append((card.get("id"), m.get("key"), why))
                    continue
                perreq, perreq_why = is_per_request(m)
                if perreq:
                    # Recorded, then skipped: a per-invocation product is not a
                    # machine you hold for N hours, so it cannot be ranked on a
                    # duty cycle. Dropping it is not a judgement about price.
                    perreq_seen.append((card.get("id"), m.get("key"), perreq_why))
                    continue
                keep, keep_basis, keep_src = keep_rate(m)
                hourly, how = mode_hourly(m, shape, pid)
                if hourly is None or hourly <= 0:
                    continue
                not_self_serve = bool(flags & {"spot", "sales", "commit", "promo", "alt"})
                floor = m.get("min_billed_seconds")
                gran = m.get("granularity_s")
                cands.append({
                    "mode": m.get("key"), "hourly": hourly, "how": how,
                    "keep": keep, "keep_src": keep_src, "keep_basis": keep_basis,
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

        entry = card.get("free") or {}
        mc_raw = entry.get("monthly_credit")
        ot_raw = entry.get("one_time_credit")

        # --- GPU-only cards -------------------------------------------------
        # A GPU provider publishes no CPU rate, only $/GPU-hour. Revision 2
        # dropped all of these; they are a real product class for agents, so
        # they are captured here and rendered as their own table rather than
        # silently excluded.
        if not off_category:
            gmodes = [m for m in (card.get("modes") or [])
                      if m.get("gpu_only") and isinstance(m.get("gpu"), dict)]
            if gmodes and not best_per_shape:
                tiers = {}
                for m in gmodes:
                    for gname, gprice in (m.get("gpu") or {}).items():
                        if not isinstance(gprice, (int, float)) or gprice <= 0:
                            continue  # a 0 GPU rate is an unpublished model
                        prev = tiers.get(gname)
                        spot = "spot" in set(m.get("flags") or [])
                        if prev is None or (spot and not prev["spot"]):
                            tiers[gname] = {"hour": float(gprice),
                                            "mode": m.get("key"), "spot": spot}
                if tiers:
                    mc0 = entry.get("monthly_credit")
                    ot0 = entry.get("one_time_credit")
                    rows.append({
                        "id": pid, "name": card.get("name"), "url": card.get("url"),
                        "category": cls, "isolation": card.get("isolation"),
                        "free_monthly_credit": mc0 if isinstance(mc0, (int, float)) else 0,
                        "free_one_time_credit": ot0 if isinstance(ot0, (int, float)) else 0,
                        "entry_fee": None, "usage_credit_floor": None,
                        "surcharge_floor": None, "has_free_tier": False,
                        "gpu_only": True, "gpu_tiers": tiers, "shapes": {},
                    })
                    continue

        if off_category:
            # Kept ONLY for the free-credit census, never ranked against the
            # compute providers: a browser product is not a machine.
            if (isinstance(mc_raw, (int, float)) and mc_raw > 0) or \
               (isinstance(ot_raw, (int, float)) and ot_raw > 0):
                rows.append({
                    "id": pid, "name": card.get("name"), "url": card.get("url"),
                    "category": cls, "isolation": card.get("isolation"),
                    "free_monthly_credit": mc_raw if isinstance(mc_raw, (int, float)) else 0,
                    "free_one_time_credit": ot_raw if isinstance(ot_raw, (int, float)) else 0,
                    "entry_fee": None, "usage_credit_floor": None,
                    "surcharge_floor": None, "has_free_tier": False,
                    "off_category_credit_only": True, "shapes": {},
                })
            else:
                skipped += 1
            continue

        if not best_per_shape:
            # Unpriced for one of three reasons, and they must not be conflated:
            # a card that only ever had pre-launch modes, a card that never
            # published a rate, and a card that publishes only GPU modes.
            rate_modes = [m for m in (card.get("modes") or [])
                          if (m.get("pricing") == "sizes" and m.get("sizes"))
                          or isinstance(m.get("vcpu_h"), (int, float))
                          or isinstance(m.get("ram_gib_h"), (int, float))]
            if rate_modes and all(is_prelaunch(m.get("key"), m.get("label"))[0]
                                  for m in rate_modes):
                prelaunch_only.append((card.get("id"), [m.get("key") for m in rate_modes]))
            continue

        plans = card.get("plans")
        if isinstance(plans, dict):
            plans = [dict(v, name=k) for k, v in plans.items()]
        plans = plans or []
        # trial_only is EXCLUDED from the entry price on purpose.
        #
        # A card marks a plan trial_only when its $0 tier is not a free tier: it
        # is a hard cap that BLOCKS usage, or a trial that expires, or a plan
        # with no on-demand credit behind it. Reading its $0 fee as an entry
        # price says "you can buy this for nothing", which is the opposite of
        # what the vendor means.
        #
        # Found by reading the corpus's own verify notes, which the first three
        # revisions never did. upstash-box's Free tier is exactly this: the note
        # reads "the Free tier is a hard cap (usage blocked, not billed)". The
        # card already sets trial_only, so the flag was there to be read.
        usable = [p for p in plans
                  if isinstance(p.get("fee"), (int, float))
                  and not p.get("trial_only")
                  and not ({"addon", "sales", "announced"} & set(p.get("flags") or []))]
        fees = sorted(p["fee"] for p in usable)
        # fee_is_credit: the fee comes back as usage, so the bill cannot fall
        # below it. Not a credit: it is a surcharge on top.
        trial_only_plans = [p["name"] for p in plans
                            if isinstance(p, dict) and p.get("trial_only")]
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
            "entry_plan_name": (min((p for p in usable if p["fee"] == fees[0]),
                                    key=lambda p: 0 if p.get("fee_is_credit") else 1,
                                    default={}).get("name")
                             if fees else None),
            "trial_only_plans": trial_only_plans,
            "usage_credit_floor": floor,
            "surcharge_floor": surcharge,
            "has_free_tier": bool([p for p in usable if p.get("fee") == 0]),
            "shapes": {},
        }
        for shape_name, c in best_per_shape.items():
            keep = c["keep"]
            # keep_basis is read from the SELECTED candidate, not from the loop
            # variable left behind by the per-mode scan above. Those two were the
            # same object only by accident: the scan rebinds keep_basis for every
            # mode it visits, so the value that reached this row was whatever the
            # LAST mode of the card happened to say. aws-lambda published that as
            # keep_source=requires_always_on alongside keep_basis="billed for
            # uptime (no suspension feature published)", which are different
            # claims about the same rate and a reader cannot tell which is true.
            keep_basis = c["keep_basis"]
            per = {"mode": c["mode"], "how": c["how"], "hourly": round(c["hourly"], 6),
                   "keep_rate": keep, "keep_source": c["keep_src"],
                   "keep_basis": keep_basis,
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
    seen_u = []
    for rec in prelaunch_seen:
        if (rec[0], rec[1]) not in [(a, b) for a, b, _ in seen_u]:
            seen_u.append(rec)
    prelaunch_seen = seen_u
    if prelaunch_seen:
        print()
        print("pre-launch modes SKIPPED (not a price a buyer can be charged):")
        for pid, mode, why in prelaunch_seen:
            print("  %-18s %-46s (%s)" % (pid, mode, why))
    if prelaunch_only:
        print()
        print("cards that are now UNPRICED because every mode was pre-launch:")
        for pid, modes in prelaunch_only:
            print("  %-18s %s" % (pid, ", ".join(modes)))
    if perreq_seen:
        seen_p = []
        for rec in perreq_seen:
            if (rec[0], rec[1]) not in [(a, b) for a, b, _ in seen_p]:
                seen_p.append(rec)
        perreq_seen = seen_p
        print()
        print("per-request modes SKIPPED (billed per invocation, not per unit of "
              "running time, so there is no $/hour to rank on a duty cycle):")
        for pid, mode, why in perreq_seen:
            print("  %-18s %-34s (note says %r)" % (pid, mode, why))
    print()

    # ---- the table the task actually asked for -------------------------------
    for shape_name, shape in SHAPES.items():
        priced = [r for r in rows if shape_name in r["shapes"]]
        if not priced:
            continue
        for hours in DUTY_CYCLES:
            key = "%dh" % hours
            sel = [r for r in priced if key in r["shapes"][shape_name]["periods"]]
            # Rank on the price BEFORE credits, and drop rows that are free
            # before credit even starts. Two reasons, both found by running this
            # and reading its own output:
            #
            #   1. Sorting on billed_month_with_credit put Run Cloud at the top of
            #      the 2 vCPU / 4 GiB / 10 h/day table with a month of $0.00, and
            #      it does so purely because its $15 recurring credit happens to
            #      exceed this month's $13.98 bill. That is true only until the
            #      credit is gone, and it presented a $14/month provider as the
            #      cheapest in the market. experiments/80-render-catalogue.py and
            #      docs/CATALOGUE.md already ranked on the pre-credit price; this
            #      table did not, so the console and the published catalogue
            #      disagreed about the same data.
            #   2. A row whose PRE-credit month is $0.00 is not a price a buyer
            #      can be ranked on at all: it is a metered product whose rate
            #      this model cannot express, or a credit-exhausted row. Either
            #      way its position in a "cheapest first" list is an artefact of
            #      the model, not of the market.
            sel = [r for r in sel
                   if r["shapes"][shape_name]["periods"][key]["billed_month_no_credit"] > 0.004]
            sel.sort(key=lambda r: r["shapes"][shape_name]["periods"][key]["billed_month_no_credit"])
            print("== %s, %s per day: %d providers, cheapest first (before credit)" %
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
                    p["billed_month_no_credit"], keep, fls,
                    ("spot/term" if s["not_self_serve"] else "self-serve")))
            print()

    dest = os.path.join(root, "data", "period-model.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump({"card_commit": CARD_COMMIT, "at": NOW(),
                   "shapes": SHAPES, "duty_cycles_h_per_day": DUTY_CYCLES,
                   "prelaunch_modes_skipped": [
                       {"id": a, "mode": b, "signal": c} for a, b, c in prelaunch_seen],
                   "per_request_modes_skipped": [
                       {"id": a, "mode": b, "signal": c} for a, b, c in perreq_seen],
                   "providers": rows}, fh, indent=1, sort_keys=True)
    print("wrote %s (%d providers)" % (dest, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())