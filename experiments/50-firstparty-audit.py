#!/usr/bin/env python3
"""50-firstparty-audit.py

QUESTION: for the providers a reader would actually act on, does the corpus card
still match the vendor's own published page today?

WHAT WOULD FALSIFY THE APPROACH: the vendors render prices client-side, so a
plain fetch returns a shell with no numbers in it. If most of the sample looks
like that, this probe measures nothing, and that is reported rather than quietly
turned into a corpus echo.

This probe is deliberately dumb: fetch, strip tags, find money. It cannot tell a
real price from a marketing sentence. A row that MATCHES the corpus is a weak
signal, because both may be reading the same vendor page or neither may have
changed. A row that DISAGREES is a strong signal and is reported loudly.

Inputs pinned: the sample list in SAMPLE below, each with the corpus card id it
is checked against. Nothing here is inferred; every price printed is a literal
string found in the fetched HTML.

Exit codes: 0 the probe ran (agreement rate is whatever it is)
            1 could not run (no corpus, or no network stack)
"""

import json
import os
import re
import sys
import html
import datetime
import urllib.request
import urllib.error

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0 Safari/537.36")
TIMEOUT = 30

# The sample: the named providers, plus a spread of the cheapest self-serve
# rows, plus a spread of large providers. Each entry is (card id, why chosen).
SAMPLE = [
    ("scaleway",        "named by the operator (stardust); stock-limited cheapest"),
    ("lizard",          "named by the operator"),
    ("freestyle",       "named by the operator"),
    ("boat",            "named by the operator ($20 subscription edge case)"),
    ("e2b",             "cheapest published per-resource agent sandbox"),
    ("daytona",         "same per-resource rate as e2b, different product"),
    ("modal",           "well-known sandbox, larger per-resource rate"),
    ("fly-machines",    "paas with a sandbox mode"),
    ("vercel-sandbox",  "paas with a sandbox mode"),
    ("morph-cloud",     "agent sandbox"),
    ("blaxel",          "agent sandbox"),
    ("runloop",         "dev-env"),
    ("northflank",      "paas"),
    ("cua",             "windows/macos sandbox"),
    ("aws-ec2",         "hyperscaler reference"),
    ("azure-vm",        "hyperscaler"),
    ("oracle",          "hyperscaler, cheap burstable"),
    ("hetzner-cloud",   "hyperscaler, cheap"),
    ("contabo",         "hyperscaler, cheap"),
]


def NOW():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.status, r.read().decode("utf-8", "replace"), r.geturl()


def strip(h):
    t = re.sub(r"<script.*?</script>", " ", h, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), t)
    t = html.unescape(t)
    return re.sub(r"[ \t\r\f\v]+", " ", t)


MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?(?:\s?/\s?(?:mo|month|hr|hour|h|GB|GiB|GB\s?-\s?mo|per\s+\w+))?", re.I)


def money(t):
    out = []
    for m in MONEY.finditer(t):
        s = re.sub(r"\s+", " ", m.group(0)).strip()
        if s not in out:
            out.append(s)
    return out


def card_rates(card):
    """Every price the corpus card asserts, as (label, value) pairs."""
    vals = []
    for m in card.get("modes") or []:
        for k in ("vcpu_h", "ram_gib_h"):
            if isinstance(m.get(k), (int, float)):
                vals.append(("%s.%s/h" % (m.get("key"), k), m[k]))
        for s in m.get("sizes") or []:
            if isinstance(s, dict) and isinstance(s.get("hour"), (int, float)):
                vals.append(("%s/%s" % (m.get("key"), s.get("name")), s["hour"]))
    for p in card.get("plans") or []:
        if isinstance(p.get("fee"), (int, float)):
            vals.append(("plan %s" % p.get("name"), p["fee"]))
    f = card.get("free") or {}
    for k in ("monthly_credit", "one_time_credit"):
        if isinstance(f.get(k), (int, float)):
            vals.append(("free.%s" % k, f[k]))
    return vals


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cards_dir = os.path.join(root, "references", "battleships", "research", "cards")
    if not os.path.isdir(cards_dir):
        print("could not run: %s missing; run 10-fetch-corpus.sh" % cards_dir, file=sys.stderr)
        return 2

    print("== conditions ==")
    print("date_utc : %s" % NOW())
    print("sample   : %d providers" % len(SAMPLE))
    print("method   : fetch the vendor pricing page, strip tags, list every $ figure")
    print("           found, and compare against every rate the corpus card asserts.")
    print("strength : MATCH is weak (both may quote one vendor page).")
    print("           DISAGREE is strong and is the row to read.")
    print()

    agree = disagree = unreachable = shell = 0
    rows = []
    for cid, why in SAMPLE:
        path = os.path.join(cards_dir, cid + ".json")
        if not os.path.exists(path):
            rows.append({"id": cid, "status": "no card", "why": why})
            continue
        with open(path, encoding="utf-8") as fh:
            card = json.load(fh)
        url = card.get("url") or ""
        if not url.startswith("http"):
            rows.append({"id": cid, "status": "no url", "why": why})
            continue
        try:
            status, body, eff = fetch(url)
        except Exception as exc:
            unreachable += 1
            rows.append({"id": cid, "status": "fetch failed", "error": str(exc)[:90],
                         "url": url, "why": why})
            continue

        text = strip(body)
        found = money(text)
        rates = card_rates(card)

        # A page with no money in it is a client-rendered shell. Say so; do not
        # score it as agreement.
        if not found:
            shell += 1
            rows.append({"id": cid, "status": "shell (no $ in HTML)", "url": eff,
                         "bytes": len(body), "why": why})
            continue

        # Does every corpus rate appear on the page? Compare as strings with the
        # number rounded the way a page would print it.
        def norm(x):
            for d in (4, 3, 2, 1, 0):
                s = ("%." + str(d) + "f") % float(x)
                if float(s) != 0:
                    s = s.rstrip("0").rstrip(".") if "." in s else s
                    return s.lstrip("0") or "0"
            return str(x)

        page_nums = set()
        for s in found:
            page_nums.add(norm(re.sub(r"[^\d.]", "", s) or 0))
        matched, missing = [], []
        for label, val in rates:
            if norm(val) in page_nums:
                matched.append((label, val))
            else:
                missing.append((label, val))

        st = "match" if not missing else ("partial" if matched else "no match")
        if missing:
            disagree += 1
        else:
            agree += 1
        rows.append({"id": cid, "status": st, "url": eff, "bytes": len(body),
                     "matched": matched, "not_found": missing,
                     "page_money_sample": found[:18], "why": why})

    for r in rows:
        print("-- %-22s %-24s %s" % (r["id"], r["status"], r.get("why", "")))
        if r.get("url"):
            print("   url      : %s" % r["url"])
        if r.get("error"):
            print("   error    : %s" % r["error"])
        if r["status"].startswith("shell"):
            print("   fetched  : %d bytes, no $ figure in the HTML (client-rendered)"
                  % r.get("bytes", 0))
        if r.get("not_found"):
            print("   CORPUS RATES NOT ON THE PAGE (read these first):")
            for label, val in r["not_found"][:8]:
                print("      %-38s %s" % (label, val))
        if r.get("matched"):
            print("   confirmed on page: %d rate(s), e.g. %s"
                  % (len(r["matched"]),
                     ", ".join("%s=%s" % (l, v) for l, v in r["matched"][:4])))
        if r.get("page_money_sample"):
            print("   page $   : %s" % ", ".join(r["page_money_sample"][:10]))
    print()
    print("== summary ==")
    print("  full match          %2d" % agree)
    print("  partial / disagree  %2d" % disagree)
    print("  client-rendered shell (unscored) %2d" % shell)
    print("  fetch failed        %2d" % unreachable)
    print()
    print("A page-rendered shell is NOT a pass and NOT a fail. It means this probe")
    print("could not read that vendor's page with a plain fetch, and the card is")
    print("unconfirmed by this route.")

    dest = os.path.join(root, "data", "firstparty-audit.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump({"at": NOW(), "rows": rows}, fh, indent=1, sort_keys=True,
                  default=str)
    print("wrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
