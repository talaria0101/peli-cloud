#!/usr/bin/env python3
"""60-guard-mutation.py

QUESTION: can the guards that keep the catalogue honest actually fail, and do
they still accept correct input?

A guard nobody has seen refuse is a guard nobody knows works. This plants each
defect the guards exist to catch, runs the instrument, reads the exit code, and
then proves the guard still accepts a correct input so it is not merely a
filter that refuses everything.

Defects planted, and what each found when it was written:
  1. a $0/hour size beside a real one        (found defect 3, 2026-10-02)
  2. a shape smaller than the request         (must be flagged, not silently priced)
  3. a beta-flagged plan                       (must stay in the universe)
  4. a nested list inside `sizes`              (must flatten, not crash)
  5. known() vs rate_known(): $0 plan fee      (must NOT be filtered as a rate)

Exit codes: 0 every guard refused its planted defect and accepted correct input
            1 at least one guard failed
            2 could not run
"""

import importlib.util
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(relpath, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, relpath))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    try:
        ex = load("experiments/20-extract-provider-universe.py", "ex")
        rk = load("experiments/30-rank-providers.py", "rk")
    except Exception as exc:
        print("could not run: %s" % exc, file=sys.stderr)
        return 2

    tmp = tempfile.mkdtemp(prefix="peli-guard-")
    failures = []

    def card(name, obj):
        p = os.path.join(tmp, name + ".json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh)
        return ex.extract_card(p)

    def check(label, cond, detail=""):
        print("  %-4s %s%s" % ("ok" if cond else "FAIL", label,
                              (" | " + detail) if detail else ""))
        if not cond:
            failures.append(label)

    print("== conditions ==")
    print("date_utc : (see git log for this run)")
    print("planting : one defect per guard, in a temp card, never in references/")
    print()

    print("GUARD 1: known() vs rate_known()")
    check("plan fee $0 is a real free tier", ex.known(0) is True)
    check("$0 hourly rate is NOT a price", ex.rate_known(0) is False)
    check("positive rate is a price", ex.rate_known(0.5) is True)
    check("None is not a price", ex.known(None) is False and ex.rate_known(None) is False)
    check("NaN is not a price", ex.rate_known(float("nan")) is False)
    check("string is not a price", ex.rate_known("0.05") is False)

    print("GUARD 2: a $0/hour size beside a real one must not win, must not drop the card")
    rows = card("zero", {"id": "zero", "name": "Z", "category": "agent-sandbox",
                         "plans": [{"name": "p", "fee": 0, "flags": []}],
                         "modes": [{"key": "m", "pricing": "sizes", "gpu_only": False,
                                    "sizes": [{"name": "free?", "vcpu": 4, "ram_gib": 16, "hour": 0},
                                              {"name": "real", "vcpu": 4, "ram_gib": 16, "hour": 0.5}]}]})
    m = rows["modes"][0]
    check("the $0 size is dropped from the list",
          all(s["hour"] > 0 for s in (m.get("sizes") or [])), str([s["hour"] for s in (m.get("sizes") or [])]))
    check("the dropped count is reported", m.get("n_zero_priced_sizes") == 1)
    p = {"id": "zero", "modes": rows["modes"], "category_class": "agent-sandbox"}
    best, reason, _ = rk.all_in_month(p, p)
    check("the card still prices, at the real rate", best is not None and best["hour"] == 0.5,
          "got %s" % (None if best is None else best["hour"]))

    print("GUARD 3: a shape smaller than the request is flagged, not priced as a fit")
    rows = card("small", {"id": "small", "name": "S", "category": "agent-sandbox",
                          "plans": [{"name": "p", "fee": 0, "flags": []}],
                          "modes": [{"key": "m", "pricing": "sizes",
                                     "sizes": [{"name": "tiny", "vcpu": 1, "ram_gib": 1, "hour": 0.1}]}]})
    p = {"id": "small", "modes": rows["modes"], "category_class": "agent-sandbox"}
    best, _, comp = rk.all_in_month(p, p)
    check("it is flagged as too small",
          any("smallest usable size" in c for c in comp), str(comp))

    print("GUARD 4: a beta-flagged plan stays in the universe")
    rows = card("beta", {"id": "beta", "name": "B", "category": "agent-sandbox",
                         "plans": [{"name": "Beta", "fee": 49, "flags": ["beta"]}],
                         "modes": [{"key": "m", "pricing": "resource", "vcpu_h": 0.05,
                                    "ram_gib_h": 0.01, "flags": []}]})
    check("entry price is $49, not None", rows["entry_month_usd"] == 49, str(rows["entry_month_usd"]))
    check("the beta flag is recorded", rows.get("entry_plan_is_beta") is True)

    print("GUARD 5: a nested list inside sizes must flatten, not crash")
    rows = card("nested", {"id": "nested", "name": "N", "category": "agent-sandbox",
                           "plans": [{"name": "p", "fee": 0, "flags": []}],
                           "modes": [{"key": "m", "pricing": "sizes",
                                      "sizes": [{"name": "A", "vcpu": 2, "ram_gib": 4, "hour": 0.1},
                                                [{"name": "B", "vcpu": 4, "ram_gib": 8, "hour": 0.2}]]}]})
    sizes = rows["modes"][0].get("sizes") or []
    check("both sizes survive the flatten", len(sizes) == 2, "%d sizes" % len(sizes))
    check("the nesting is reported", rows["modes"][0].get("nested_size_rows") == 1)

    print("GUARD 6: a correct input is still accepted (a guard that refuses everything)")
    rows = card("good", {"id": "good", "name": "G", "category": "agent-sandbox",
                         "plans": [{"name": "Pro", "fee": 20, "flags": []}],
                         "modes": [{"key": "m", "pricing": "sizes",
                                    "sizes": [{"name": "S", "vcpu": 2, "ram_gib": 4, "hour": 0.02}]}]})
    p = {"id": "good", "modes": rows["modes"], "category_class": "agent-sandbox",
         "entry_month_usd": 20}
    best, _, _ = rk.all_in_month(p, p)
    check("a normal card still prices", best is not None and best["hour"] == 0.02)
    check("a normal card keeps its entry fee", p["entry_month_usd"] == 20)

    print()
    if failures:
        print("GUARD FAILURES (%d): %s" % (len(failures), "; ".join(failures)))
        return 1
    print("all guards refused their planted defect and accepted correct input")
    return 0


if __name__ == "__main__":
    sys.exit(main())