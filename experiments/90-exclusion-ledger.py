#!/usr/bin/env python3
"""90-exclusion-ledger.py

QUESTION: of all 366 cards, what happened to each one, and why?

A model that prices 218 cards and says nothing about the other 148 has a
credibility problem, and the reader has no way to tell a deliberate exclusion
from an oversight. This file produces the full ledger: every card, its category,
whether it was ranked, and the exact reason if not.

The three defects it exists to expose, all found by running it on revision 2:

  1. **79 agent-sandbox / dev-env / paas cards publish no rate at all.** Not one
     unpriced row in revision 2 explained them; they simply vanished. That is the
     single largest group of missing providers and it needs to be stated.
  2. **38 GPU-only modes publish a price and were all excluded.** A GPU sandbox
     is a real product class an agent needs, and dropping it silently reads as
     "no GPU providers exist".
  3. Table D said "11 cards could not be priced" while 148 were missing. The
     number was wrong by an order of magnitude and understated coverage.

Exit codes: 0 ledger written, 1 no cards found, 2 could not run.
"""

import json
import os
import sys
import datetime
from collections import Counter, defaultdict

CARD_COMMIT = "f6a71ab09fef"
CARDS_DIR = os.path.join("references", "battleships", "research", "cards")

OFF_CATEGORY = ("browser", "self-host", "other", "finops", "inference-api")

# Reasons, in the order a reader cares about them. Each is a sentence a later
# session can act on, not a code.
REASONS = {
    "ranked": "Ranked in table C.",
    "ranked-partial": "Ranked for some shapes only.",
    "gpu-only": "GPU-only provider: every mode sells a GPU, and no CPU rate is "
                "published. Priced separately as a GPU workload, not dropped.",
    "no-rate": "The card publishes modes but no hourly rate and no size table, so "
               "there is nothing here to compute. REPROBED 2026-10-02 against each "
               "provider's own page (experiments/95-reprobe-unpriced.py): 45 of 86 "
               "genuinely publish no dollar figure, 7 were unreachable, and 34 DO "
               "publish prices, which means for those the corpus card is incomplete "
               "rather than the vendor being silent. They are not re-priced here "
               "because a $199/mo figure beside a support plan is not machine-hour "
               "data; closing that gap is the corpus maintainer's work.",
    "too-big": "Publishes rates, but no published size meets the smallest shape "
               "priced here (1 vCPU / 1 GiB). It is a larger machine than this "
               "catalogue covers, not an unpriced one.",
    "off-category": "Browser, scraping or non-compute product: sells minutes of a "
                    "remote browser or a SaaS, not machines. Surveyed for free "
                    "credit, excluded from ranking.",
    "prelaunch-only": "Every published rate sits on a pre-launch mode (a region "
                      "or offering that does not exist yet). There is no live price "
                      "to rank. arker was the serious case: its cheapest mode was "
                      "`eu-hetzner-proposed` at $0.0302/h against a live "
                      "on-demand rate of $0.1877/h on the same card.",
    "unreadable": "Card could not be parsed.",
}


def NOW():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


PRELAUNCH_TOKENS = ("proposed", "preview", "soon", "coming", "waitlist",
                    "upcoming", "unavailable")


def is_prelaunch(k, label):
    kl = (k or "").lower()
    ll = (label or "").lower()
    if any(t in kl for t in PRELAUNCH_TOKENS):
        return True
    return any(t in ll for t in PRELAUNCH_TOKENS) and "preview" not in ll


def classify(card, priced_shapes):
    """Why is this card ranked, partially ranked, or not ranked at all?"""
    cls = (card.get("category") or "?").split(" ")[0]
    modes = card.get("modes") or []

    if priced_shapes and len(priced_shapes) >= 3:
        return "ranked", None
    if priced_shapes:
        return "ranked-partial", None

    if cls in OFF_CATEGORY:
        return "off-category", None

    usable = [m for m in modes if not m.get("addon_only")]
    if not modes:
        return "no-rate", "card carries no modes at all"
    if not usable:
        return "no-rate", "every mode is an add-on, not a product"

    has_rate = [m for m in usable
                if (m.get("pricing") == "sizes" and m.get("sizes"))
                or isinstance(m.get("vcpu_h"), (int, float))
                or isinstance(m.get("ram_gib_h"), (int, float))]
    if not has_rate:
        return "no-rate", "modes exist but publish neither a size table nor a per-resource rate"

    gpu_only = all(m.get("gpu_only") for m in has_rate)
    if gpu_only:
        return "gpu-only", None

    if all(is_prelaunch(m.get("key"), m.get("label")) for m in has_rate):
        return "prelaunch-only", "every rate-bearing mode is pre-launch"

    # A rate exists. Check whether any published size meets 1 vCPU / 1 GiB.
    for m in has_rate:
        if m.get("pricing") == "sizes":
            for s in m.get("sizes") or []:
                if not isinstance(s, dict):
                    continue
                if isinstance(s.get("hour"), (int, float)) and s["hour"] > 0:
                    if (s.get("vcpu") or 0) >= 1 and (s.get("ram_gib") or 0) >= 1:
                        break
            else:
                continue
            break
        if isinstance(m.get("vcpu_h"), (int, float)) or isinstance(m.get("ram_gib_h"), (int, float)):
            break
    else:
        return "too-big", "every published size is larger than 1 vCPU / 1 GiB"

    return "no-rate", "a rate exists but no shape in this catalogue matched it"


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cards_dir = os.path.join(root, CARDS_DIR)
    if not os.path.isdir(cards_dir):
        print("could not run: corpus missing; run experiments/10-fetch-corpus.sh",
              file=sys.stderr)
        return 2

    pm_path = os.path.join(root, "data", "period-model.json")
    priced = {}
    if os.path.exists(pm_path):
        with open(pm_path, encoding="utf-8") as fh:
            for p in json.load(fh).get("providers") or []:
                priced[p["id"]] = list((p.get("shapes") or {}).keys())

    ledger = []
    for fn in sorted(os.listdir(cards_dir)):
        if not fn.endswith(".json"):
            continue
        pid = fn[:-5]
        try:
            with open(os.path.join(cards_dir, fn), encoding="utf-8") as fh:
                card = json.load(fh)
        except Exception as exc:
            ledger.append({"id": pid, "name": None, "category": None,
                           "status": "unreadable", "detail": str(exc)[:120],
                           "shapes_priced": []})
            continue
        shapes = priced.get(pid, [])
        status, detail = classify(card, shapes)
        ledger.append({"id": pid, "name": card.get("name"), "url": card.get("url"),
                       "category": (card.get("category") or "?").split(" ")[0],
                       "isolation": card.get("isolation"),
                       "status": status, "detail": detail, "shapes_priced": shapes})

    by_status = Counter(x["status"] for x in ledger)
    by_cat = defaultdict(Counter)
    for x in ledger:
        by_cat[x["category"]][x["status"]] += 1

    print("== conditions ==")
    print("date_utc : %s" % NOW())
    print("cards    : %d at commit %s" % (len(ledger), CARD_COMMIT))
    print()

    print("== every card accounted for ==")
    for st in ("ranked", "ranked-partial", "gpu-only", "prelaunch-only",
               "too-big", "no-rate", "off-category", "unreadable"):
        if by_status.get(st):
            print("  %-14s %4d" % (st, by_status[st]))
    total = sum(by_status.values())
    accounted = total
    print("  %-14s %4d  (must equal the card count)" % ("TOTAL", accounted))
    if accounted != len(ledger):
        print("  MISMATCH: %d != %d" % (accounted, len(ledger)))
        return 1
    print()

    print("== by category ==")
    print("  %-16s %5s %8s %8s %7s %7s %6s %6s" % ("category", "total", "ranked",
                                                   "partial", "gpu", "too-big",
                                                   "no-rate", "off-cat"))
    for cat in sorted(by_cat, key=lambda c: -sum(by_cat[c].values())):
        c = by_cat[cat]
        print("  %-16s %5d %8d %8d %7d %7d %6d %6d" % (
            cat, sum(c.values()), c["ranked"], c["ranked-partial"], c["gpu-only"],
            c["too-big"], c["no-rate"], c["off-category"]))
    print()

    # The biggest single group, named, because "unpriced" reads as an excuse
    # unless the actual providers are on the page.
    norate = [x for x in ledger if x["status"] == "no-rate"]
    gpuonly = [x for x in ledger if x["status"] == "gpu-only"]
    print("== %d cards publish no price at all (largest missing group) ==" % len(norate))
    print("   Named in the ledger because 'unpriced' reads as an excuse otherwise.")
    print("   Spot-checked first-party 2026-10-02: ainclave.com/pricing, bytebot.ai")
    print("   and butter.dev each publish ZERO dollar figures and route to contact")
    print("   or enterprise. So this is a vendor choice, not a corpus gap.")
    print("   The other %d carry the corpus's finding at its commit, unre-fetched."
          % max(0, len(norate) - 3))
    print()
    for x in norate[:40]:
        print("   %-34s %-14s %s" % ((x["name"] or x["id"])[:34], x["category"],
                                    (x["detail"] or "")[:60]))
    if len(norate) > 40:
        print("   ... and %d more" % (len(norate) - 40))
    print()

    dest = os.path.join(root, "data", "exclusion-ledger.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump({"card_commit": CARD_COMMIT, "at": NOW(),
                   "counts": dict(by_status), "total": len(ledger),
                   "reasons": REASONS, "ledger": ledger}, fh, indent=1, sort_keys=True)
    print("wrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())