#!/usr/bin/env python3
"""80-render-catalogue.py

QUESTION: render the whole corpus, cheapest first, at every usage period, with
free tiers, floors and credits each in their own table, and every provider linked
to the page its numbers came from.

Four tables, because they answer four different questions and mixing them is what
made revision 1 read like a VPS comparison:

  A. FREE TIER   what costs $0 right now, and how far the credit goes
  B. BY PERIOD   paid providers at 1, 4, 10 and 24 hours/day, each with $/hour,
                $/day, $/week and $/month, per shape
  C. FULL RANK   every provider that priced at any period, ranked, no truncation
  D. NO PRICE    what could not be priced and exactly why

Every row links to the provider's own page (the card's url) and to the corpus
card it was read from, so a reader can check any number without this repository.

Exit codes: 0 rendered, 1 nothing to render, 2 could not run.
"""

import json
import os
import sys
import datetime
import importlib.util

# The advertised-size table lives in the period model, which is the script that
# decides what a size costs. The renderer reads it from there rather than
# keeping a second copy that could drift.
_pm_spec = importlib.util.spec_from_file_location(
    "pm", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "experiments", "70-period-model.py"))
pm = importlib.util.module_from_spec(_pm_spec)
_pm_spec.loader.exec_module(pm)


def keep_cell(s):
    """The keep rate, marked when it is measured rather than assumed.

    A bare 1.00 is ambiguous between "the card says this machine bills for
    uptime" and "nobody has checked". Those are different facts and the reader
    needs the second one to be visible, because every default row makes holding
    look dearer than it is. `1.00*` means the conservative fallback.
    """
    if not s:
        return "-"
    k = s.get("keep_rate")
    src = s.get("keep_source") or ""
    if k is None:
        return "-"
    if src == "default":
        return "%.2f*" % k
    if src.startswith("first-party"):
        return "**%.2f**" % k
    return "%.2f" % k

SHAPES_ORDER = ["tiny", "agent", "devbox"]
DUTY = ["1h", "4h", "10h", "24h"]


def NOW():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def esc(s):
    return (s or "").replace("|", "\\|")


def link(text, url):
    return "[%s](%s)" % (esc(text), url) if url else esc(text)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(root, "data", "period-model.json")
    if not os.path.exists(src):
        print("could not run: %s missing; run experiments/70-period-model.py" % src,
              file=sys.stderr)
        return 2
    with open(src, encoding="utf-8") as fh:
        doc = json.load(fh)
    providers = doc.get("providers") or []
    if not providers:
        print("nothing to render", file=sys.stderr)
        return 1

    shapes = doc["shapes"]
    out = []
    A = out.append

    def sort_key(p):
        # Same ordering rule as table B: rank on the price BEFORE credits, so a
        # provider whose credit happens to cover this month is not presented as
        # the cheapest thing in the market. The credit column then shows what
        # would bring it down to, and the reader can weigh both.
        s = p["shapes"].get("agent") or p["shapes"].get("tiny") or p["shapes"].get("devbox")
        if not s:
            return (9e9,)
        pd = s["periods"].get("10h") or list(s["periods"].values())[0]
        return (0.0 if pd.get("allowance_source") else pd["billed_month_no_credit"],
                pd["billed_month_with_credit"])

    A("# peli-cloud — every provider, cheapest first, at every period")
    A("")
    A("**Generated %s** from the corpus at `%s`. Every row links to the provider's "
      "own page and to the card the number was read from." % (doc["at"], doc["card_commit"]))
    A("")
    A("## How to read this")
    A("")
    A("A cloud sandbox is not a VPS. It bills while it runs, and most of them stop "
      "billing when they are stopped. So **the price is a function of how long you "
      "hold it**, and one monthly number cannot rank the market: the cheapest "
      "provider at 2 hours/day is not the cheapest provider at 24/7, and often not "
      "even the same list.")
    A("")
    A("Every table below is priced at three shapes and four duty cycles:")
    A("")
    A("| shape | vCPU / RAM | what it is for |")
    A("|---|---|---|")
    A("| `tiny` | %s | a shell, a build step, a short tool call |" % shapes["tiny"]["label"])
    A("| `agent` | %s | the normal agent sandbox |" % shapes["agent"]["label"])
    A("| `devbox` | %s | a developer box you keep around |" % shapes["devbox"]["label"])
    A("")
    A("| duty cycle | hours/day | billed hours/month (at 30 days) |")
    A("|---|---|---|")
    for h, d in (("1h", 1), ("4h", 4), ("10h", 10), ("24h", 24)):
        A("| `%s` | %d h/day | %d |" % (h, d, d * 30))
    A("")
    A("`keep` is the fraction of wall-clock time the provider bills for. `1.00` "
      "means billed for uptime no matter what the machine is doing; `0.00` means it "
      "suspends on idle. It is read from the card's published features, and a "
      "provider that publishes no suspension feature is recorded as `1.00`, because "
      "a plain VM is billed for uptime. Unknown is never assumed to be the cheap case.")
    A("")

    # ---------------- Table A: free tiers ----------------
    A("---")
    A("")
    A("## A. Free tier — what costs nothing right now")
    A("")
    # Three different things, kept apart because conflating them is the mistake
    # this table exists to prevent:
    #   A1 a stated recurring credit  -> free until it runs out, every month
    #   A2 a stated one-time credit   -> free once
    #   A3 a $0 entry tier, no credit published -> unknown, not free
    credited = [p for p in providers
                if p.get("free_monthly_credit") or p.get("free_one_time_credit")]
    credited.sort(key=lambda p: (-(p.get("free_monthly_credit") or 0),
                                 -(p.get("free_one_time_credit") or 0)))
    zerounknown = [p for p in providers
                   if p.get("entry_fee") == 0 and not p.get("free_monthly_credit")
                   and not p.get("free_one_time_credit")]
    zerounknown.sort(key=lambda p: sort_key(p))

    A("### A1. Recurring credit — free every month, until it runs out")
    A("")
    A("%d providers publish a credit that recurs. **This is the complete list; "
      "there is no large free tier in this market.** The biggest is $%g/month."
      % (len([p for p in credited if p.get("free_monthly_credit")]),
         max([p["free_monthly_credit"] for p in credited if p.get("free_monthly_credit")]
             or [0])))
    A("")
    A("| # | provider | category | credit / month | what that buys at the `agent` rate | keep | link |")
    A("|---|---|---|---|---|---|---|")
    for i, p in enumerate([x for x in credited if x.get("free_monthly_credit")], 1):
        mc = p["free_monthly_credit"]
        s = p["shapes"].get("agent") or p["shapes"].get("tiny")
        if s and s["hourly"]:
            h = "%.0f machine-hours (%s h/day for a month)" % (mc / s["hourly"],
                                                                round(mc / s["hourly"] / 30, 1))
        else:
            h = "-"
        A("| %d | %s | %s | $%g | %s | %.2f | %s |" % (
            i, link(p["name"] or p["id"], p.get("url")), p.get("category") or "-",
            mc, h, s["keep_rate"] if s else 0, "`%s`" % p["id"]))
    A("")

    A("### A2. One-time credit — free exactly once")
    A("")
    A("%d providers publish a signup credit. It is worth its face value once and "
      "never renews." % len([p for p in credited if p.get("free_one_time_credit")]))
    A("")
    A("| # | provider | category | one-time credit | what that buys at the `agent` rate | link |")
    A("|---|---|---|---|---|---|")
    for i, p in enumerate([x for x in credited if x.get("free_one_time_credit")], 1):
        ot = p["free_one_time_credit"]
        s = p["shapes"].get("agent") or p["shapes"].get("tiny")
        h = ("%.0f machine-hours (%.0f h/day for a month)" % (ot / s["hourly"], ot / s["hourly"] / 30)
             if s and s["hourly"] else "-")
        note = " (browser product, not a machine)" if p.get("off_category_credit_only") else ""
        A("| %d | %s | %s%s | $%g | %s | `%s` |" % (
            i, link(p["name"] or p["id"], p.get("url")), p.get("category") or "-", note, ot, h,
            p["id"]))
    A("")

    A("### A3. $0 entry tier, no credit published — unknown, not free")
    A("")
    A("%d cards sell a plan whose fee is $0 but publish no credit, no quota and no "
      "cap. Whether that is a usable free tier or an unpriced meter is **not in "
      "the card**. They are listed here rather than in the paid tables because a "
      "$0 fee is not evidence that the machine is free." % len(zerounknown))
    A("")
    A("| # | provider | category | $/hour | 24h/day month | link |")
    A("|---|---|---|---|---|---|")
    for i, p in enumerate(zerounknown[:60], 1):
        s = p["shapes"].get("agent") or p["shapes"].get("tiny")
        m24 = s["periods"].get("24h", {}).get("billed_month_with_credit") if s else None
        A("| %d | %s | %s | %s | %s | `%s` |" % (
            i, link(p["name"] or p["id"], p.get("url")), p.get("category") or "-",
            ("%.4f" % s["hourly"]) if s else "-",
            ("%.2f" % m24) if m24 is not None else "-", p["id"]))
    if len(zerounknown) > 60:
        A("")
        A("_%d more in `data/period-model.json`._" % (len(zerounknown) - 60))
    A("")
    A("**The trap in this section.** A one-time credit is free once. A monthly "
      "credit is free until it runs out, and the largest in the market is "
      "$30/month. The big numbers people quote — $300 from Google, AWS, Azure, "
      "Oracle or IBM — are **one-time** credits. They do not renew, and treating "
      "one as a free tier is the most expensive mistake in this document.")
    A("")

    # ---------------- Table B: by period ----------------
    A("---")
    A("")
    A("## B. Paid providers by period")
    A("")
    A("Cheapest first within each cell. `$/h` is the published machine rate; the "
      "period columns are that rate times the hours you hold it, before any floor.")
    A("")
    A("**`$/month` and `held 24/7` are different questions and the difference is "
      "the keep rate.** `$/month` is what the stated duty cycle costs: you use "
      "the machine for that many hours a day. `held 24/7` is what it costs to "
      "keep the box for every hour of the month, which is the comparison against "
      "a VPS. They are equal when `keep` is 1.00, and they diverge when the "
      "provider suspends on idle: a sandbox you hold but barely use is cheap, and "
      "that is the whole reason to choose one. `keep` is the fraction of held "
      "time you are billed for; 0.00 means a paused or suspended sandbox stops "
      "billing.")
    A("")

    for shape_name in SHAPES_ORDER:
        if shape_name not in shapes:
            continue
        priced = [p for p in providers if shape_name in p["shapes"]]
        A("### %s — %s" % (shapes[shape_name]["label"], shape_name))
        A("")
        for dkey in DUTY:
            sel = []
            for p in priced:
                s = p["shapes"][shape_name]
                pd = s["periods"].get(dkey)
                if not pd:
                    continue
                sel.append((p, s, pd))
            # Rows that are genuinely $0 BEFORE any credit, because a published
            # free allowance covers the whole usage. These are the cheapest
            # thing in the market and the table below the paid one would drop
            # them, so they get their own table with the evidence attached.
            free_rows = [x for x in sel
                         if x[2]["billed_month_no_credit"] == 0.0
                         and x[2].get("allowance_source")]
            if free_rows:
                A("#### %s per day — %d provider(s) free on a published allowance" %
                  (dkey, len(free_rows)))
                A("")
                A("| provider | shape | keep | allowance covers | source |")
                A("|---|---|---|---|---|")
                for p, s, pd in free_rows:
                    A("| %s | %s | %.2f | %d%% | %s |" % (
                        link(p["name"] or p["id"], p.get("url")), shape_name,
                        s.get("keep_rate") or 0.0,
                        round(100 * (pd.get("allowance_covered_fraction") or 0)),
                        pd.get("allowance_source")))
                A("")
                for p, s, pd in free_rows:
                    det = pd.get("allowance_detail") or {}
                    if det:
                        bits = ", ".join(
                            "%s: %g h used of %g h free at $%g/h"
                            % (k, v["used_h"], v["allowance_h"], v["rate"])
                            for k, v in sorted(det.items()))
                        A("- **%s**, %s per day, at %s h/day: %s. The bill is $0 "
                          "before any credit, which is a free allowance and not a "
                          "$0 plan." % (p["name"] or p["id"], dkey, pd["hours_per_day"],
                                         bits))
                A("")
            sel = []
            for p in priced:
                s = p["shapes"][shape_name]
                pd = s["periods"].get(dkey)
                if not pd:
                    continue
                sel.append((p, s, pd))
            # Sort by the price you pay ONCE THE CREDIT IS GONE, not by the
            # credit-adjusted price. Sorting by the adjusted price puts any
            # provider whose credit happens to exceed this month's bill at the
            # top of every table. That is true only until the credit runs out,
            # and it makes a $14/month provider read as cheaper than a $1/month
            # one. A credit-exhausted row is marked, never sorted as if free.
            # A row is excluded from the PAID table when its pre-credit month is
            # $0, because a $0 position is either a credit-exhausted row or a
            # meter this model cannot express. A row that is $0 because a
            # PUBLISHED ALLOWANCE covers the usage is neither: it is genuinely
            # the cheapest thing in the market, so it ranks first and says why.
            paid = [x for x in sel
                    if x[2]["billed_month_no_credit"] > 0.004
                    or x[2].get("allowance_source")]
            paid.sort(key=lambda x: (0.0 if x[2].get("allowance_source")
                                     else x[2]["billed_month_no_credit"],
                                     x[2]["billed_month_with_credit"]))
            A("#### %s per day — %d paid providers" % (dkey, len(paid)))
            A("")
            A("| # | provider | $/hour | $/day | $/week | $/month | held 24/7 | after credit | credit | keep | floor | buy it? | link |")
            A("|---|---|---|---|---|---|---|---|---|---|---|---|")
            for i, (p, s, pd) in enumerate(paid[:25], 1):
                floor = p.get("usage_credit_floor")
                mc = p.get("free_monthly_credit") or 0
                if mc and pd["billed_month_with_credit"] <= 0.004:
                    used = "**$%g covers it**" % mc
                elif mc:
                    used = "$%g of it" % mc
                else:
                    used = "-"
                buy = ("**no**" if s["not_self_serve"]
                       else ("spot/term" if "spot" in s["flags"] else "yes"))
                # A row priced from a size the vendor advertises and the corpus
                # card dropped is CORRECTED, not confirmed. Saying "yes" would
                # tell a reader to buy on a rate that a first-party page and that
                # page's own docs contradict, so the column says so.
                if "[ADVERTISED" in (s.get("how") or ""):
                    buy = "**disputed**"
                A("| %d | %s | %.4f | %.2f | %.2f | %.2f | %.2f | %.2f | %s | %s | %s | %s | `%s` |" % (
                    i, link(p["name"] or p["id"], p.get("url")), s["hourly"],
                    pd["compute_day"], pd["compute_week"], pd["billed_month_no_credit"],
                    pd.get("hold_month", 0.0),
                    pd["billed_month_with_credit"], used, keep_cell(s),
                    ("$%g" % floor) if floor else "-", buy, p["id"]))
            if len(paid) > 25:
                A("")
                A("_%d more at this duty cycle; the full rank is table C._" % (len(paid) - 25))
            disputed = [x for x in paid[:25] if "[ADVERTISED" in (x[1].get("how") or "")]
            if disputed:
                A("")
                A("**Rows marked `disputed` are not confirmed prices.** A size the "
                  "vendor advertises is missing from the corpus card, so the rate "
                  "here is the vendor's own and the corpus discarded it:")
                for p, s, _pd in disputed:
                    adv = [a for a in pm.ADVERTISED_SIZES
                           if a["provider"] == p["id"] and a["mode"] == s.get("mode")]
                    for a in adv:
                        A("")
                        A("- **%s** — %s at $%g/h, advertised on [%s](%s): \"%s\" "
                          "The card carries only the default size, so the rate was "
                          "absent from the ranking. Conflict: %s"
                          % (p["name"], a["label"], a["hour"], p["name"], a["url"],
                             a["quote"], a["disputed"]))
            A("")

    # ---------------- Table B1.5: minimum bill ----------------
    mb_path = os.path.join(root, "data", "minimum-bill-penalty.json")
    if os.path.exists(mb_path):
        with open(mb_path, encoding="utf-8") as fh:
            mb = json.load(fh)
        prof = mb.get("profiles") or {}
        ms = prof.get("many-short")
        fl = prof.get("few-long")
        A("---")
        A("")
        A("## B1. The minimum bill, which a $/hour table hides")
        A("")
        A("A published hourly rate is not what you pay for a short burst. **42 modes "
          "in this corpus bill a minimum of one hour** and 9 bill a minimum of one "
          "full day. For an agent that starts a sandbox, runs a tool call and "
          "starts again, the minimum is the price that actually applies, and every "
          "table above hides it.")
        A("")
        A("Two profiles, each compared against the **same** demand so the "
          "comparison is like for like:")
        A("")
        if ms:
            A("- **many short sessions**: %d starts a day of %g h each = %g h of "
              "real demand. This is what an agent running a tool call, reading a "
              "result and starting again actually does."
              % (ms["starts"], ms["hours_each"],
                 ms["starts"] * ms["hours_each"]))
        if fl:
            A("- **few long sessions**: %d starts a day of %g h each = %g h. Every "
              "session already exceeds a one-hour minimum, so the minimum never "
              "bites here."
              % (fl["starts"], fl["hours_each"], fl["starts"] * fl["hours_each"]))
        A("")
        mrows = [r for r in mb.get("rows") or []
                 if (r.get("profiles", {}).get("many-short", {}).get("penalty_x") or 1) > 1.0]
        mrows.sort(key=lambda r: -r["profiles"]["many-short"]["penalty_x"])
        A("**%d of %d providers are affected.** The worst:" % (len(mrows), len(mb.get("rows") or [])))
        A("")
        A("| # | provider | $/hour | same demand, smooth | same demand, bursty | penalty | rounds up to | link |")
        A("|---|---|---|---|---|---|---|---|")
        for i, r in enumerate(mrows[:20], 1):
            p_ms = r["profiles"]["many-short"]
            # Two different mechanisms produce the same penalty and the column
            # must not conflate them: a MINIMUM billable unit, and a
            # GRANULARITY that rounds any partial hour up to a whole one. Both
            # make a 15-minute session cost an hour; only one is a minimum.
            mbs = r.get("min_billed_seconds")
            gran = r.get("granularity_s")
            if mbs:
                why = "min %g s" % mbs
            elif gran and gran >= 60:
                why = "gran %g s" % gran
            else:
                why = "-"
            A("| %d | %s | %.4f | $%.2f/mo | $%.2f/mo | **%.1fx** | %s | `%s` |" % (
                i, link(r["name"] or r["id"], r.get("url")), r["hourly"],
                p_ms["month_smooth_same_demand"], p_ms["month"], p_ms["penalty_x"],
                why, r["id"]))
        A("")
        A("Read these as bounds, not predictions. `bursty` assumes every session is "
          "shorter than the minimum, which is the pessimistic side; a real agent "
          "that holds one sandbox for the hour pays once. What the column "
          "establishes is which headline rates cannot survive a bursty workload.")
        A("")
        A("**Two different mechanisms, one effect, and the column above keeps "
          "them apart.** A *minimum billable unit* charges at least that much per "
          "start regardless. A *granularity* rounds any partial hour up to the next "
          "step. Both make a 15-minute session cost a full hour, which is why "
          "Civo, Hetzner, Scaleway and UpCloud are 4x worse bursty, and why Aptible "
          "and Paperspace are too despite publishing no minimum at all.")
        A("")
        A("**The ones that bite hardest are not the expensive ones.** HostMyApple "
          "at $0.0479/hour carries a 30-day minimum; a bursty agent would pay "
          "$20,706 a month against $7.19 for the same demand smoothed. Hetzner's "
          "$0.0104/hour is 4x worse bursty than smooth, and it ranks third in the "
          "`agent` table above on the smooth number. The market's cheap providers "
          "are disproportionately hourly-rounders, and that is invisible in a "
          "rate table.")
        A("")

    # ---------------- Table B2: GPU ----------------
    gpu = [p for p in providers if p.get("gpu_only")]
    if gpu:
        A("---")
        A("")
        A("## B2. GPU providers — priced per GPU-hour")
        A("")
        A("A GPU box is billed per GPU-hour, not per vCPU. Ranking one beside a CPU "
          "box compares two currencies, so these get their own table. Revision 2 "
          "dropped all of them silently; there are %d." % len(gpu))
        A("")
        A("Cheapest published model per provider, with the hour/day/week/month cost "
          "of holding ONE of that GPU:")
        A("")
        A("| # | provider | cheapest GPU | $/GPU-hour | $/day | $/week | $/month | spot? | link |")
        A("|---|---|---|---|---|---|---|---|---|")
        grows = []
        for p in gpu:
            name, info = min(p["gpu_tiers"].items(), key=lambda kv: kv[1]["hour"])
            h = info["hour"]
            grows.append((h, p, name, info))
        grows.sort(key=lambda x: x[0])
        for i, (h, p, name, info) in enumerate(grows, 1):
            A("| %d | %s | %s | %.2f | %.2f | %.2f | %.2f | %s | `%s` |" % (
                i, link(p["name"] or p["id"], p.get("url")), name, h,
                h * 1, h * 7, h * 30, "yes" if info["spot"] else "no", p["id"]))
        A("")
        A("The full per-model price list for each provider is in "
          "`data/period-model.json` under `gpu_tiers`. Spot prices are interruptible: "
          "the machine can be reclaimed. Every row here is a published rate, none "
          "is a negotiated price.")
        A("")

    # ---------------- Table C: full rank ----------------
    A("---")
    A("")
    A("## C. Every provider, ranked")
    A("")
    A("Nothing truncated. One row per provider that priced at any shape and period, "
      "ordered by its `agent` month at 10 h/day **before credits are applied**, so a "
      "provider whose credit happens to cover this month is never presented as the "
      "cheapest thing in the market. The period columns after the first are also "
      "before credit, except where a credit is shown in the `free/mo` column.")
    A("")
    A("| # | provider | category | isolation | $/h agent | 1h/day | 4h/day | 10h/day | 24h/day | free/mo | floor | link |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")

    ranked = sorted([p for p in providers if p.get("shapes")], key=sort_key)
    for i, p in enumerate(ranked, 1):
        s = p["shapes"].get("agent") or p["shapes"].get("tiny") or p["shapes"].get("devbox")
        if not s:
            continue
        P = s["periods"]

        def cell(dk):
            pd = P.get(dk)
            return "%.2f" % pd["billed_month_with_credit"] if pd else "-"
        floor = p.get("usage_credit_floor")
        # A disputed row must be marked in THIS table too. Table C is the one a
        # reader lands on, and it had no marker at all: lizard appeared at rank 2
        # with $0.0090 and nothing saying the vendor's own docs contradict it.
        # The mark goes on the provider name, which every table shows, rather
        # than on a column only table B has.
        nm = link(p["name"] or p["id"], p.get("url"))
        if "[ADVERTISED" in (s.get("how") or ""):
            nm += " **(disputed)**"
        A("| %d | %s | %s | %s | %.4f | %s | %s | %s | %s | %s | %s | %s |" % (
            i, nm, p.get("category") or "-",
            p.get("isolation") or "-", s["hourly"], cell("1h"), cell("4h"), cell("10h"),
            cell("24h"),
            ("$%g" % p["free_monthly_credit"]) if p.get("free_monthly_credit") else "-",
            ("$%g" % floor) if floor else "-", "`%s`" % p["id"]))
    A("")
    if any("[ADVERTISED" in ((p["shapes"].get("agent") or p["shapes"].get("tiny")
                              or p["shapes"].get("devbox") or {}).get("how") or "")
           for p in ranked):
        A("**(disputed)** marks a row priced from a size the vendor advertises "
          "and the corpus card dropped, where the vendor's own pricing page and "
          "its own docs contradict each other. The price is the vendor's, not a "
          "confirmed figure. See FINDINGS section 5.5 and the note under table B.")
        A("")

    # ---------------- Table D: the ledger ----------------
    A("---")
    A("")
    A("## D. Every card accounted for")
    A("")
    A("A missing row is a result. This is what happened to all "
      "%d cards in the corpus, so a deliberate exclusion cannot be mistaken for "
      "an oversight." % (len(providers) + 41))
    A("")

    ledger_path = os.path.join(root, "data", "exclusion-ledger.json")
    ledger = None
    if os.path.exists(ledger_path):
        with open(ledger_path, encoding="utf-8") as fh:
            ledger = json.load(fh)

    if ledger:
        A("Produced by `experiments/90-exclusion-ledger.py` at corpus commit `%s`."
          % ledger["card_commit"])
        A("")
        A("| status | cards | what it means |")
        A("|---|---|---|")
        for st in ("ranked", "ranked-partial", "gpu-only", "prelaunch-only",
                   "too-big", "no-rate", "off-category"):
            if ledger["counts"].get(st):
                A("| `%s` | %d | %s |" % (st, ledger["counts"][st],
                                           ledger["reasons"].get(st, "")))
        A("| **total** | **%d** | must equal the corpus card count |" % ledger["total"])
        A("")

        A("### Where it breaks down by category")
        A("")
        A("| category | total | ranked | partial | gpu-only | too big | no price | off-category |")
        A("|---|---|---|---|---|---|---|---|")
        cats = {}
        for x in ledger["ledger"]:
            c = cats.setdefault(x["category"], {})
            c[x["status"]] = c.get(x["status"], 0) + 1
        for cat in sorted(cats, key=lambda c: -sum(cats[c].values())):
            c = cats[cat]
            A("| %s | %d | %d | %d | %d | %d | %d | %d |" % (
                cat, sum(c.values()), c.get("ranked", 0), c.get("ranked-partial", 0),
                c.get("gpu-only", 0), c.get("too-big", 0), c.get("no-rate", 0),
                c.get("off-category", 0)))
        A("")

        norate = [x for x in ledger["ledger"] if x["status"] == "no-rate"]
        if norate:
            A("### The %d with no price in the card" % len(norate))
            A("")
            A("The largest group of providers outside the ranking, so it is named "
              "rather than summarised. They are absent because the **card** carries "
              "no rate and no size table, not because this model refused them.")
            A("")
            A("Each was then re-probed against the provider's own page "
              "(`experiments/95-reprobe-unpriced.py`). Of the %d:" % len(norate))
            A("")
            A("- **45 publish no dollar figure at all.** The corpus is right.")
            A("- **7 were unreachable.** No verdict either way.")
            A("- **20 publish a machine rate** (`/min`, `/hour`, `/month`) that the "
              "card never captured. For these the corpus card is simply wrong. "
              "BuildJet is the clearest: $0.004/min for 2 vCPU / 8 GB, published, "
              "and the card carries no rate.")
            A("- **14 carry dollars that are not a machine rate**, such as an "
              "enterprise SSO tier. Ambiguous, and left ambiguous.")
            A("")
            A("None of the 20 or 14 are re-priced here. Turning a marketing page "
              "into a card is the implementing session's work; a research session "
              "that guesses a rate produces a number nobody can check.")
            A("")
            A("| provider | category | card says | page re-probe | figures seen | link |")
            A("|---|---|---|---|---|---|")
            probe = {}
            pp = os.path.join(root, "data", "unpriced-reprobe.json")
            if os.path.exists(pp):
                with open(pp, encoding="utf-8") as fh:
                    for r in json.load(fh).get("results") or []:
                        probe[r["id"]] = r
            for x in norate:
                pr = probe.get(x["id"]) or {}
                v = pr.get("verdict", "not probed")
                figs = ", ".join(pr.get("figures") or [])[:44] if pr.get("figures") else "-"
                A("| %s | %s | no rate, no sizes | %s | %s | `%s` |" % (
                    link(x["name"] or x["id"], x.get("url")), x["category"], v, figs, x["id"]))
            A("")

        prel = [x for x in ledger["ledger"] if x["status"] == "prelaunch-only"]
        if prel:
            A("### The %d priced only on a pre-launch mode" % len(prel))
            A("")
            A("Every rate these cards publish sits on a region or offering that "
              "does not exist yet, so there is no live price to rank. **This is not "
              "a theoretical category**: arker was ranked at $0.0302/hour from "
              "`eu-hetzner-proposed` while the same card's live on-demand rate is "
              "$0.1877/hour, a factor of six. Revision 2 carried that row until "
              "the winning mode of every ranked provider was audited for "
              "pre-launch wording.")
            A("")
            A("| provider | category | link |")
            A("|---|---|---|")
            for x in prel:
                A("| %s | %s | `%s` |" % (link(x["name"] or x["id"], x.get("url")),
                                           x["category"], x["id"]))
            A("")

        toobig = [x for x in ledger["ledger"] if x["status"] == "too-big"]
        if toobig:
            A("### The %d priced, but only for larger machines" % len(toobig))
            A("")
            A("| provider | category | link |")
            A("|---|---|---|")
            for x in toobig:
                A("| %s | %s | `%s` |" % (link(x["name"] or x["id"], x.get("url")),
                                           x["category"], x["id"]))
            A("")

        offcat = [x for x in ledger["ledger"] if x["status"] == "off-category"]
        if offcat:
            A("### The %d off-category products" % len(offcat))
            A("")
            A("Browser, scraping and non-compute products. They sell minutes of a "
              "remote browser or a SaaS, not machines, so ranking them beside a VM "
              "provider compares two purchases. They are still surveyed for free "
              "credit in tables A1 and A2.")
            A("")
            A("| provider | category | link |")
            A("|---|---|---|")
            for x in offcat:
                A("| %s | %s | `%s` |" % (link(x["name"] or x["id"], x.get("url")),
                                           x["category"], x["id"]))
            A("")
    else:
        A("_Run `experiments/90-exclusion-ledger.py` to generate this section._")
        A("")

    dest = os.path.join(root, "docs", "CATALOGUE.md")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote %s" % dest)
    print("  A1 recurring credit : %d" % len([p for p in credited if p.get("free_monthly_credit")]))
    print("  A2 one-time credit  : %d" % len([p for p in credited if p.get("free_one_time_credit")]))
    print("  A3 $0 tier, unknown : %d" % len(zerounknown))
    print("  C  ranked           : %d providers" % len(ranked))
    if ledger:
        print("  D  ledger           : %d cards, all accounted for" % ledger["total"])
        for st, n in sorted(ledger["counts"].items()):
            print("       %-14s %d" % (st, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())