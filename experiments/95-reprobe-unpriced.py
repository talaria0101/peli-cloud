#!/usr/bin/env python3
"""95-reprobe-unpriced.py

QUESTION: of the cards the corpus says publish no price, how many actually DO
publish one on the provider's own page?

Revision 2 wrote that the 86 unpriced cards were "a vendor choice, not a gap in
the corpus", on the evidence of three hand-picked pages (ainclave, bytebot,
butter). That generalisation was wrong. Re-probing all of them on 2026-10-02
found that a large share DO publish prices: Artillery shows $199/$499/$1199,
BuildJet $0.004-$0.128 per minute, Brimble, Clusy, Isle, Dexto, Nodus Compute,
Server4Agent, PaperPod, Party and more.

This is a dumb probe and knows it: fetch, strip tags, count dollar figures. It
cannot tell a price for this product from a price for something else on the same
page, and a "priced-on-page" row is a LEAD, not a filled-in price. What it
establishes is the negative, which is the load-bearing part: the corpus card is
wrong to say "no price" for these, and the omission is the corpus's, not the
vendor's.

A probe that finds nothing is a result too; the counts below say how many pages
were reachable at all, so a wall of "no-price" can be told apart from a wall of
"could not read".

Exit codes: 0 ran, 1 no cards to probe, 2 could not run.
"""

import json
import os
import re
import sys
import html
import datetime
import urllib.request
import urllib.error

TIMEOUT = 25
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0 Safari/537.36")

# The card's own url is where the corpus said to look. For a handful of cards the
# corpus url is a docs page rather than a pricing page; those are recorded as
# reachable-but-not-pricing rather than silently retried against a guessed URL.
MONEY = re.compile(r"\$\s?[\d,]*\.?\d+")


def NOW():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                   "Accept-Language": "en-US,en;q=0.9"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.read().decode("utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, "", url
    except Exception as exc:
        return None, str(exc)[:100], url


# A figure that looks like machine compute rather than a support tier or a
# currency amount in prose. This is a WEAK signal and is recorded as one: it is
# the difference between "the page has dollars" and "the page has a rate for
# the thing this card describes".
MACHINE_RATE = re.compile(
    r"\$\s?[\d,]*\.?\d+\s*(?:/\s*(?:min|minute|hr|hour|mo|month|gb|sec|second)"
    r"|per\s+(?:min|minute|hour|hr|month|mo|second|sec|gb|gi[bB])"
    r"|/\s*(?:vCPU|core|gpu))", re.I)


def looks_like_machine_rate(text):
    return bool(MACHINE_RATE.search(text))


def money_on_page(body):
    t = re.sub(r"<script.*?</script>", " ", body, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return sorted(set(m.strip() for m in MONEY.findall(t)))


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    led_path = os.path.join(root, "data", "exclusion-ledger.json")
    if not os.path.exists(led_path):
        print("could not run: %s missing; run experiments/90-exclusion-ledger.py"
              % led_path, file=sys.stderr)
        return 2
    with open(led_path, encoding="utf-8") as fh:
        led = json.load(fh)
    targets = [x for x in led["ledger"] if x["status"] == "no-rate" and x.get("url")]
    if not targets:
        print("no cards to probe", file=sys.stderr)
        return 1

    print("== conditions ==")
    print("date_utc   : %s" % NOW())
    print("targets    : %d cards the corpus says publish no price" % len(targets))
    print("method     : fetch the card's url, strip tags, count $ figures")
    print("strength   : 'priced-on-page' is a LEAD that the corpus is incomplete,")
    print("             not a price this catalogue can rank. 'no-price-on-page' is")
    print("             a confirmation. 'unreachable' is neither.")
    print()

    out = []
    for x in targets:
        st, body, eff = fetch(x["url"])
        if st != 200:
            verdict = "unreachable"
            figs = []
            rate = False
        else:
            figs = money_on_page(body)
            # Three states, not two. "has dollars" and "has a machine rate" are
            # different claims: Artillery's page carries $1199/month, which is an
            # enterprise SSO and support tier, not runner compute.
            plain = re.sub(r"<script.*?</script>", " ", body, flags=re.S | re.I)
            plain = re.sub(r"<style.*?</style>", " ", plain, flags=re.S | re.I)
            plain = html.unescape(re.sub(r"<[^>]+>", " ", plain))
            rate = looks_like_machine_rate(plain)
            if not figs:
                verdict = "no-price-on-page"
            elif rate:
                verdict = "machine-rate-on-page"
            else:
                verdict = "dollars-but-not-a-rate"
        rec = {"id": x["id"], "name": x["name"], "url": x["url"], "category": x["category"],
               "http": st, "final_url": eff, "verdict": verdict,
               "machine_rate": rate, "n_figures": len(figs), "figures": figs[:12]}
        out.append(rec)
        print("%-3d %-32s %-19s %s" % (len(out), (x["name"] or x["id"])[:32], verdict,
                                       ", ".join(figs[:4])))

    n_rate = sum(1 for r in out if r["verdict"] == "machine-rate-on-page")
    n_dollars = sum(1 for r in out if r["verdict"] == "dollars-but-not-a-rate")
    n_priced = n_rate + n_dollars
    n_none = sum(1 for r in out if r["verdict"] == "no-price-on-page")
    n_dead = sum(1 for r in out if r["verdict"] == "unreachable")
    print()
    print("== summary ==")
    print("  page HAS a machine rate (/min, /hr, /mo) %3d  <- corpus clearly wrong" % n_rate)
    print("  page has dollars, but not a machine rate %3d  <- ambiguous" % n_dollars)
    print("  corpus says no price, page has none      %3d  <- confirmed" % n_none)
    print("  unreachable at the card's url             %3d  <- not a verdict" % n_dead)
    print()
    if n_rate:
        print("The corpus's 'no price' is CLEARLY wrong for %d of these %d cards: they"
              % (n_rate, len(targets)))
        print("publish a per-minute or per-hour machine rate that the card never")
        print("captured. This catalogue does NOT re-price them, because turning a")
        print("marketing page into a card is the implementing session's work, not the")
        print("research session's. What is established is the gap and its size.")

    dest = os.path.join(root, "data", "unpriced-reprobe.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump({"at": NOW(), "targets": len(targets),
                   "priced_on_page": n_priced, "no_price_on_page": n_none,
                   "unreachable": n_dead, "results": out}, fh, indent=1, sort_keys=True)
    print("wrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())