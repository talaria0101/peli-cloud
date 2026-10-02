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


def norm(x):
    for d in (4, 3, 2, 1, 0):
        s = ("%." + str(d) + "f") % float(x)
        if float(s) != 0:
            s = s.rstrip("0").rstrip(".") if "." in s else s
            return s.lstrip("0") or "0"
    return str(x)


# Every page that renders a price also renders the UNIT, and vendors publish
# per-second and per-hour rates for the same machine freely: e2b.dev/pricing
# prints $0.000014 per vCPU-second, which is the corpus's $0.0504/hour exactly
# ($0.000014 x 3600 = 0.0504). Comparing the printed strings alone scored that
# as a disagreement, and the same fault produced 481 "not found" figures across
# the 19-provider sample, which reads as a first-party audit that found almost
# nothing wrong with the corpus. It is not evidence either way: it is a unit
# mismatch. So each page figure is also converted to an hourly equivalent
# before the comparison, and a corpus rate is matched by EITHER its own printed
# form or its hourly equivalent.
PER_SECOND = 3600.0
PER_MINUTE = 60.0
PER_DAY = 24.0
PER_MONTH = 30.0 * 24.0


def page_rate_variants(raw):
    """The numeric forms a page figure should be allowed to match.

    A page may print the rate per second, per minute, per hour, per day or per
    month, and may print it rounded to fewer significant figures than the corpus
    holds. The corpus value is what we are trying to corroborate, so every unit
    equivalent of every page figure is offered to the comparison.
    """
    out = set()
    try:
        v = float(re.sub(r"[^\d.]", "", raw))
    except (TypeError, ValueError):
        return out
    for scale in (1.0, PER_SECOND, PER_MINUTE, PER_DAY, PER_MONTH,
                  1.0 / PER_SECOND, 1.0 / PER_MINUTE, 1.0 / PER_DAY, 1.0 / PER_MONTH):
        x = v * scale
        for d in (6, 4, 3, 2, 1, 0):
            s = ("%." + str(d) + "f") % x
            try:
                if abs(float(s) - round(float(s), 6)) > 1e-9:
                    continue
            except ValueError:
                continue
            out.add(norm(s))
    return {o for o in out if o}


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

        # Does every corpus rate appear on the page, in any unit the page might
        # reasonably print it in? Compare as strings with the number rounded the
        # way a page would print it.
        page_nums = set()
        for s in found:
            page_nums.add(norm(re.sub(r"[^\d.]", "", s) or 0))
            page_nums |= page_rate_variants(s)
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
        # A figure the card DERIVES from a published bundled price cannot appear
        # on the page, because the page prints the bundle, not the difference.
        # fly-machines is the case: vcpu_h 0.02916 is the performance vCPU price
        # of $0.043056/h MINUS the 2 GB of RAM bundled with it at $0.006948/GB-h,
        # and the note says so. The page publishes $0.043056 and $0.006948; the
        # probe is right that 0.02916 is not printed and wrong to read that as a
        # disagreement. So a rate is labelled derived when the card's own note
        # shows the arithmetic that produced it, and those are counted apart.
        note_all = " ".join((m.get("note") or "") for m in (card.get("modes") or []))
        has_derivation = bool(re.search(
            r"minus|derived|backed out|net of|excluding the (bundled|included)", note_all))
        derived, unverifiable = [], []
        for label, val in missing:
            if label.endswith("vcpu_h/h") or label.endswith("ram_gib_h/h"):
                # Derived means the note shows a SUBTRACTION that yields this
                # figure, so the page prints the bundle and not the difference.
                # The arithmetic is checked numerically rather than by matching
                # the mode key, which need not appear in the note at all
                # (fly-machines says "performance-4x/8GB", not
                # "performance-us"). Collect every "A minus B" pair in the
                # note and see whether one of them lands on the card's value.
                pairs = re.findall(
                    r"([0-9]*\.?[0-9]+)\s*(?:/h)?[^)]*\)\s*minus\s*"
                    r"(?:([0-9]*\.?[0-9]+)\s*x\s*)?\$?([0-9]*\.?[0-9]+)",
                    note_all)
                hit = any(abs((float(a) - float(mult or 1) * float(b)) - float(val))
                          < 5e-4 for a, mult, b in pairs)
                if has_derivation and hit:
                    derived.append((label, val))
                else:
                    unverifiable.append((label, val))
            else:
                unverifiable.append((label, val))
        rows.append({"id": cid, "status": st, "url": eff, "bytes": len(body),
                     "matched": matched, "not_found": missing,
                     "not_found_derived": derived,
                     "not_found_unverifiable": unverifiable,
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
            der = r.get("not_found_derived") or []
            unver = r.get("not_found_unverifiable") or []
            print("   CORPUS RATES NOT PRINTED ON THE PAGE (read these first):")
            for label, val in der[:8]:
                print("      %-38s %s   [derived in the card, page prints the bundle]"
                      % (label, val))
            for label, val in unver[:8]:
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
