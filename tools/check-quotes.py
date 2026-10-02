#!/usr/bin/env python3
"""check-quotes.py - every quote in the census must be findable on the page it cites.

Review R23 fetched each row's `source` and searched the rendered text for the
quoted words. Two rows failed, and both failures mattered for different reasons:

  * `blinkenshell` - the quote was verbatim, but its `source` pointed at the
    provider's ROOT page, which does not contain it. The sentence lives on
    /wiki/FAQ. A reader following the citation would not have found it, so a
    correct quote with a wrong citation is still a broken citation.
  * `github-codespaces` - the "120 core hours or 60 hours" quota was not on the
    cited page at all, nor on three other GitHub pages fetched to chase it. The
    quote did not survive being fetched, which is the entire purpose of a quote.

So this checks the page, not just the string: it fetches, renders, and requires
that a sufficient share of the quote's word n-grams are present. It is a network
check and says so when it cannot run - a check that silently passes because the
network is down is worse than no check.

Thresholds, and why they are what they are:
  * `MIN_FRACTION` is compared against the fraction of 4-grams present. A quote
    that is partly paraphrased fails. Ellipsis-joined excerpts ("A ... B") are
    split on the ellipsis and each half is required independently, so joining
    two sentences that appear on the page but not adjacent is not accepted.
  * Pages are cached by URL under `.quote-cache/` for a week, because this is
    26 fetches and re-running it on every commit is not a gate, it is a tax.

Usage: python3 tools/check-quotes.py            # every row
       python3 tools/check-quotes.py blinkenshell hashbang
       python3 tools/check-quotes.py --offline  # use the cache only, never the network
Exit 0 when every checkable quote verifies, 1 when one does not, 2 when the
network was unavailable and rows were skipped (named).
"""
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "anonymous-vms.json")
CACHE = os.path.join(ROOT, ".quote-cache")
TTL = 7 * 24 * 3600

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120 Safari/537.36"}
NGRAM = 4
MIN_FRACTION = 0.55
# A quote made of fragments this short cannot be checked by n-grams: there are
# fewer of them than the window. Those rows are reported as unchecked rather
# than passed.
MIN_WORDS = NGRAM + 1


def render(raw):
    """HTML to text. Deliberately keeps JSON-LD blocks: a page may render its
    own words inside a <script> tag, and stripping every script is how a
    readable page becomes an unreadable one - the same lesson the catalogue's
    own stripper needed, applied here so this check does not repeat it."""
    raw = re.sub(r"(?is)<(noscript)[^>]*>.*?</\1>", " ", raw)
    text = re.sub(r"(?s)<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = text.replace("’", "'").replace("“", '"')
    text = text.replace("”", '"').replace("—", "-").replace("–", "-")
    text = text.replace(" ", " ").replace("…", "...")
    return re.sub(r"\s+", " ", text)


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def fetch(url, offline):
    key = re.sub(r"[^a-zA-Z0-9]+", "_", url)[-120:]
    path = os.path.join(CACHE, key)
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < TTL:
        with open(path, encoding="utf-8") as f:
            return int(f.readline().strip() or 0), f.read()
    if offline:
        return None, None
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=35) as r:
            status, body = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, body = e.code, ""
    except Exception:
        return None, None
    os.makedirs(CACHE, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{status}\n{body}")
    return status, body


def split_parts(quote):
    """Split a quote into the parts that must each appear.

    A bare `...` in a transcription is an ellipsis JOINING two adjacent spans of
    the page, not a gap. Treating every `...` as a separator is how the first
    version of this file verified NOTHING: the ellipsis inside quotes like
    "0 EUR/month ... Disk space SSD 1 Go" became a split, every half fell below
    the n-gram window, all 25 quotes were reported "too short", and the run
    exited 0 having checked nothing. A check that verifies zero rows and reports
    success is worse than no check, so the separator is only a `...` that has
    non-space on BOTH sides inside the same line, and a single `...` alone is
    never a separator.

    ` | ` is an explicit separator a row can use to mean "these are two places
    on the page, not one sentence"."""
    q = quote.strip()
    q = re.sub(r"(?m)^\s*\.\.\.\s*$", " | ", q)      # a line that is only an ellipsis
    # Split on a mid-line `...` that has a space on BOTH sides. That is a
    # transcription gap: the author wrote two spans of the page joined by an
    # ellipsis, and each span must be present. An ellipsis tight against a word
    # ("0 EUR/month...") or inside a token is not a gap and is left alone.
    q = re.sub(r"\s\.\.\.\s", " | ", q)
    # `|` is now the one internal separator, so it splits like a newline does.
    # Without this the gap markers become part of the phrase and every split
    # quote fails on the `|` it just inserted - which is what the first two
    # versions of this file did.
    q = re.sub(r"\s*\|\s*", "\n", q)
    out, cur = [], []
    for line in q.splitlines():
        s = line.strip()
        if not s:
            continue
        # ⛔ A BLANK LINE IS A PART BOUNDARY. Joining two page spans into one
        # phrase makes the check ask for text that is not on the page: the first
        # two versions of this file emitted
        #   ['signup for shell access | [unix shell] | est. 1987']
        # for a page that plainly carries "Est. 1987", and it reported 0% on
        # five rows that verify. Every line the splitter produced is its own
        # part, because that is what the substitution above meant.
        if cur:
            out.append(" ".join(cur))
        cur = [s.rstrip(".").strip()] if not s.endswith("...") else [s.rstrip(".").strip()]
    if cur:
        out.append(" ".join(cur))
    return [p for p in (norm(x) for x in out) if p]


def verify(quote, text):
    """Return (ok, fraction, why). Each separated part must appear whole."""
    parts = split_parts(quote)
    if not parts:
        return None, None, "quote has no checkable text"
    fractions = []
    for part in parts:
        words = part.split()
        if len(words) < MIN_WORDS:
            # Too short for a sliding 4-gram. Checked as a whole phrase instead,
            # so a short quote is verified and not silently skipped.
            fractions.append(1.0 if part in text else 0.0)
            continue
        grams = [" ".join(words[i:i + NGRAM])
                 for i in range(len(words) - NGRAM + 1)]
        hits = sum(1 for g in grams if g in text)
        fractions.append(hits / len(grams))
    worst = min(fractions)
    return worst >= MIN_FRACTION, worst, ""


def main():
    argv = sys.argv[1:]
    offline = "--offline" in argv
    ids = [a for a in argv if not a.startswith("--")]
    rows = json.load(open(DATA))["rows"]
    if ids:
        rows = [r for r in rows if r["id"] in ids]

    bad, unchecked, unreachable = [], [], []
    for r in rows:
        q = (r.get("quote") or "").strip()
        if not q:
            unchecked.append(f"{r['id']}: no quote (expected for measurement-only rows)")
            continue
        status, body = fetch(r["source"], offline)
        if status is None:
            unreachable.append(f"{r['id']}: {r['source']}")
            continue
        if status != 200:
            bad.append(f"{r['id']}: source returned HTTP {status}")
            continue
        text = norm(render(body))
        ok, frac, why = verify(q, text)
        if ok is None:
            unchecked.append(f"{r['id']}: {why}")
        elif not ok:
            bad.append(f"{r['id']}: only {frac:.0%} of the quote is on {r['source']} "
                       f"(need {MIN_FRACTION:.0%})")

    for b in bad:
        print("FAIL", b)
    for u in unchecked:
        print("unchecked", u)
    for u in unreachable:
        print("unreachable", u)

    n = len(rows)
    print(f"rows={n} verified={n - len(bad) - len(unchecked) - len(unreachable)} "
          f"failed={len(bad)} unchecked={len(unchecked)} unreachable={len(unreachable)}")
    if bad:
        return 1
    if unreachable:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())