#!/usr/bin/env python3
"""Re-check every vendor quote against the bytes it was taken from.

A quote that does not survive being fetched is not evidence. This reads the
captured pages in verify/pages/ and reports HIT/MISS per phrase, so a number
cannot drift from its source without the tool noticing.

    python verify/claim.py                 # all claims, HIT/MISS summary
    python verify/claim.py --show          # with the surrounding text
    python verify/claim.py <page>          # one page
"""

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
PAGES = ROOT / "pages"
CLAIMS = ROOT / "claims.json"


def text(page):
    p = PAGES / f"{page}.html"
    if not p.exists():
        return None
    s = p.read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s))


def main():
    show = "--show" in sys.argv
    wanted = [a for a in sys.argv[1:] if not a.startswith("--")]
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    claims.pop("_comment", None)

    hits = misses = missing_pages = 0
    problems = []
    for page, phrases in claims.items():
        if wanted and page not in wanted:
            continue
        t = text(page)
        if t is None:
            missing_pages += 1
            problems.append(f"{page}: capture missing from verify/pages/")
            print(f"[NOPAGE] {page}")
            continue
        for ph in phrases:
            i = t.lower().find(ph.lower())
            if i < 0:
                misses += 1
                problems.append(f"{page}: {ph!r} NOT FOUND in the fetched bytes")
                print(f"  [MISS ] {page}: {ph!r}")
            else:
                hits += 1
                print(f"  [HIT  ] {page}: {ph!r}")
                if show:
                    print(f"          ...{t[max(0,i-190):i+230].strip()}...\n")

    print(f"\n{hits} hit, {misses} miss, {missing_pages} pages with no capture")
    if problems:
        print("\nPROBLEMS (a quote that did not survive the fetch is not evidence):")
        for p in problems:
            print(f"  {p}")
    return 1 if (misses or missing_pages) else 0


if __name__ == "__main__":
    sys.exit(main())