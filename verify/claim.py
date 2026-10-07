#!/usr/bin/env python3
"""Re-check every vendor quote against the bytes it was taken from.

A quote that does not survive being fetched is not evidence. This reads the
captures in verify/pages/ and reports HIT/MISS per phrase, so a number cannot
drift from its source unnoticed.

    python3 verify/claim.py                 # every claim
    python3 verify/claim.py --show          # with surrounding text
    python3 verify/claim.py <page> [<page>] # named pages only

Exit codes:
  0  every claim verified
  1  a claim MISSED, a capture is missing, OR a named page is not in claims.json

The third case matters. An earlier version returned 0 when a page filter matched
nothing, so `verify/claim.py some-file-that-does-not-exist` printed "0 hit, 0
miss" and exited green having checked nothing - which is precisely the failure
tools/check-quotes.py documents in its own docstring ("a check that verifies
zero rows and reports success is worse than no check"). A filter that selects
nothing is a typo, and it is reported as one.
"""
import html
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
PAGES = ROOT / "pages"
CLAIMS = ROOT / "claims.json"

# Phrases are kept short and free of typographic punctuation so they survive a
# re-render of the source page: one earlier claim used a literal U+00B7 while the
# page served &middot;, and the mismatch read as a quote failure when the quote
# was in fact on the page.


def text(page):
    p = PAGES / f"{page}.html"
    if not p.exists():
        return None
    s = p.read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    t = html.unescape(s)
    t = t.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", t).lower()


def main():
    show = "--show" in sys.argv
    wanted = [a for a in sys.argv[1:] if not a.startswith("--")]
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    claims.pop("_comment", None)

    if wanted:
        unknown = [w for w in wanted if w not in claims]
        if unknown:
            print("no such page in verify/claims.json: " + ", ".join(unknown))
            print("known pages: " + ", ".join(sorted(claims)))
            return 1
        claims = {k: v for k, v in claims.items() if k in wanted}

    if not claims:
        print("no claims selected; nothing was checked")
        return 1

    hits = misses = missing_pages = 0
    problems = []
    for page, phrases in claims.items():
        t = text(page)
        if t is None:
            missing_pages += 1
            problems.append(f"{page}: no capture (run python3 verify/fetch.py)")
            print(f"  [NOPAGE] {page}")
            continue
        for ph in phrases:
            i = t.find(ph.lower())
            if i < 0:
                misses += 1
                problems.append(f"{page}: {ph!r} not in the fetched bytes")
                print(f"  [MISS  ] {page}: {ph!r}")
            else:
                hits += 1
                print(f"  [HIT   ] {page}: {ph!r}")
                if show:
                    print(f"           ...{t[max(0, i - 190):i + 230].strip()}...\n")

    print(f"\n{hits} hit, {misses} miss, {missing_pages} pages with no capture")
    if problems:
        print("\nPROBLEMS (a quote that did not survive the fetch is not evidence):")
        for p in problems:
            print("  " + p)
    return 1 if (misses or missing_pages) else 0


if __name__ == "__main__":
    sys.exit(main())