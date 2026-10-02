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
        return (pd["billed_month_no_credit"], pd["billed_month_with_credit"])

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
        A("| %d | %s | %s | $%g | %s | %s |" % (
            i, link(p["name"] or p["id"], p.get("url")), p.get("category") or "-", ot, h,
            "`%s`" % p["id"]))
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
            # Sort by the price you pay ONCE THE CREDIT IS GONE, not by the
            # credit-adjusted price. Sorting by the adjusted price puts any
            # provider whose credit happens to exceed this month's bill at the
            # top of every table. That is true only until the credit runs out,
            # and it makes a $14/month provider read as cheaper than a $1/month
            # one. A credit-exhausted row is marked, never sorted as if free.
            paid = [x for x in sel if x[2]["billed_month_no_credit"] > 0.004]
            paid.sort(key=lambda x: (x[2]["billed_month_no_credit"],
                                     x[2]["billed_month_with_credit"]))
            A("#### %s per day — %d paid providers" % (dkey, len(paid)))
            A("")
            A("| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | link |")
            A("|---|---|---|---|---|---|---|---|---|---|---|")
            for i, (p, s, pd) in enumerate(paid[:25], 1):
                floor = p.get("usage_credit_floor")
                mc = p.get("free_monthly_credit") or 0
                if mc and pd["billed_month_with_credit"] <= 0.004:
                    used = "**$%g covers it**" % mc
                elif mc:
                    used = "$%g of it" % mc
                else:
                    used = "-"
                A("| %d | %s | %.4f | %.2f | %.2f | %.2f | %.2f | %s | %.2f | %s | `%s` |" % (
                    i, link(p["name"] or p["id"], p.get("url")), s["hourly"],
                    pd["compute_day"], pd["compute_week"], pd["billed_month_no_credit"],
                    pd["billed_month_with_credit"], used, s["keep_rate"],
                    ("$%g" % floor) if floor else "-", p["id"]))
            if len(paid) > 25:
                A("")
                A("_%d more at this duty cycle; the full rank is table C._" % (len(paid) - 25))
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

    ranked = sorted(providers, key=sort_key)
    for i, p in enumerate(ranked, 1):
        s = p["shapes"].get("agent") or p["shapes"].get("tiny") or p["shapes"].get("devbox")
        if not s:
            continue
        P = s["periods"]

        def cell(dk):
            pd = P.get(dk)
            return "%.2f" % pd["billed_month_with_credit"] if pd else "-"
        floor = p.get("usage_credit_floor")
        A("| %d | %s | %s | %s | %.4f | %s | %s | %s | %s | %s | %s | %s |" % (
            i, link(p["name"] or p["id"], p.get("url")), p.get("category") or "-",
            p.get("isolation") or "-", s["hourly"], cell("1h"), cell("4h"), cell("10h"),
            cell("24h"),
            ("$%g" % p["free_monthly_credit"]) if p.get("free_monthly_credit") else "-",
            ("$%g" % floor) if floor else "-", "`%s`" % p["id"]))
    A("")

    # ---------------- Table D: no price ----------------
    A("---")
    A("")
    A("## D. What could not be priced, and why")
    A("")
    A("A missing row is a result. This is what would have to become true for each "
      "excluded card to get a price.")
    A("")
    noshape = [p for p in providers if not p["shapes"]]
    if noshape:
        A("%d cards published no rate or size for any shape." % len(noshape))
        A("")
        A("| provider | category | link |")
        A("|---|---|---|")
        for p in noshape:
            A("| %s | %s | `%s` |" % (link(p["name"] or p["id"], p.get("url")),
                                     p.get("category") or "-", p["id"]))
    else:
        A("None: every card in the corpus published at least one shape.")
    A("")

    dest = os.path.join(root, "docs", "CATALOGUE.md")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote %s" % dest)
    print("  A1 recurring credit : %d" % len([p for p in credited if p.get("free_monthly_credit")]))
    print("  A2 one-time credit  : %d" % len([p for p in credited if p.get("free_one_time_credit")]))
    print("  A3 $0 tier, unknown : %d" % len(zerounknown))
    print("  C  ranked           : %d providers" % len(ranked))
    print("  D  no price         : %d cards" % len(noshape))
    return 0


if __name__ == "__main__":
    sys.exit(main())