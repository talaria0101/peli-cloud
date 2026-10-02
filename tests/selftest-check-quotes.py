#!/usr/bin/env python3
"""selftest-check-quotes.py - known-answer cases for the quote checker.

Review R23 wrote `tools/check-quotes.py` and then had to fix its splitter THREE
times, each version failing silently in a different direction:

  v1  split on every `...`, so the ellipsis inside "0 EUR/month ... Disk space"
      became a boundary; all 25 quotes fell below the n-gram window, were
      reported "too short to verify", and the run exited 0 having verified
      NOTHING. A checker that verifies zero rows and reports success is worse
      than no checker.
  v2  replaced the ellipsis with `|`, then never split on the `|`, so every part
      it checked still contained the marker it had just inserted.
  v3  split correctly but JOINED the resulting lines back into one phrase,
      asking the page for text that was never there: "signup for shell access
      [unix shell] est. 1987" on a page that plainly carries "Est. 1987".

Each was caught only by reading the output, not by the checker. These cases are
the fix: the splitter is now a function with a table of expected answers, and
`--mutate` runs the same cases through the v1 splitter and they must all fail.

Usage: python3 tests/selftest-check-quotes.py             # the splitter is correct
       python3 tests/selftest-check-quotes.py --mutate   # the naive one is caught

Exit codes, one meaning each, because the first version of this file had one
flag carrying two opposite meanings and my own gate script read it backwards:
`--mutate` exiting 0 means the naive splitter FAILED the cases, which is the
outcome wanted. It does not mean the naive splitter passed. Exit 1 in either
mode means an assertion did not hold.
"""
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKER = os.path.join(ROOT, "tools", "check-quotes.py")

spec = importlib.util.spec_from_file_location("check_quotes", CHECKER)
cq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cq)


def naive_split(quote):
    """The v1 splitter: split on every ellipsis. Kept only so the cases below
    can be shown to fail on it, which is what makes them cases and not
    assertions about my own preferences."""
    return [cq.norm(p) for p in re.split(r"\.\.\.|…", quote) if cq.norm(p)]


CASES = [
    # (quote, expected number of parts, why)
    ("Signup for Shell Access ... [UNIX SHELL] ... Est. 1987", 3,
     "a real row: three spans joined by ellipses"),
    ("Free ... 0 €/month ... Disk space SSD 1 Go gift RAM 256 Mo", 3,
     "a real row: the ellipsis is a transcription gap, not part of a number"),
    ("$0 + compute / month ... $30 / month free credits", 2,
     "a real row: two spans"),
    ("Tiers Sandbox ... Always-on-compute - no sleeping :) 2x free services", 2,
     "a real row: two spans, the second carrying punctuation"),
    ("All tenancies get the first 1,500 OCPU hours", 1,
     "no ellipsis: one part"),
    ("Membership PLUS Includes all from FREE Use scenarios", 1,
     "no ellipsis: one part"),
    ("a | b | c", 3, "an explicit separator is honoured"),
    ("no ellipsis here at all", 1, "plain text"),
    ("Solar...ina is one word", 1, "an ellipsis tight to words is not a gap"),
    ("ends with a trailing ellipsis ...", 1, "a trailing ellipsis is not a gap"),
    ("multi\nline\nquote", 3,
     "each line is its own span; joining them asks for text the page lacks"),
]


def run(name, splitter):
    bad = 0
    for quote, expected, why in CASES:
        got = splitter(quote)
        if len(got) != expected:
            bad += 1
            print(f"  FAIL {name}: expected {expected} parts, got {len(got)}  ({why})")
            print(f"       quote={quote!r}")
            print(f"       got  ={got}")
    return bad


def main():
    mutate = "--mutate" in sys.argv or "--naive" in sys.argv
    if "--naive" in sys.argv:
        print("note: --naive is an alias for --mutate. Exit 0 from --mutate means "
              "the naive splitter WAS caught; it is not an expect-failure flag.",
              file=sys.stderr)
    if mutate:
        bad = run("naive-v1", naive_split)
        print(f"mutate: naive splitter failed {bad} of {len(CASES)} cases")
        if bad == 0:
            print("MUTATE FAIL: the naive splitter passed every case, so these "
                  "cases prove nothing")
            return 1
        print("mutate: ok - the naive splitter is caught")
        return 0

    bad = run("current", cq.split_parts)
    print(f"current: {len(CASES) - bad} of {len(CASES)} cases passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
