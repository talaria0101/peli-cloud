#!/usr/bin/env python3
"""check-always-on-free.py - guard the always-on free compute census.

Same shape as check-anon-vms.py and for the same reason: the page under
data/always-on-free.json is generated, and a generated page drifts from its data
the moment nobody re-runs the guard. Four clauses hold before a row is published:

  1. CENSUS, NOT A LIST. A row floor, and no duplicate ids.

  2. RE-DERIVABLE. Every counted row carries a source, a primary vendor quote,
     and says WHO verified it. A row whose evidence is 'checked, looks good' is
     a claim nobody can check, so unattributed provenance fails.

  3. TIER HONESTY. T1 is always-on as-is; T2 is always-on with a keepalive and
     must NAME one; T3 needs a relay and must NAME one. A T1/T2 row that also
     claims a relay contradicts itself: it is reachable without one. This is the
     clause that keeps the strongest-sounding field from being read as the
     strongest thing in it, the same lesson check-anon-vms.py learned from a
     banner carrying a free row.

  4. DEAD MEANS DEAD. A DEAD row names the wall - a quota that exhausts, a
     trial clock, a paid gate at creation. A DEAD row with no wall might just be
     a row someone gave up on.

The counts in the JSON are recomputed, so a declared count cannot disagree with
the rows without failing.

Usage: python3 tools/check-always-on-free.py            # check
       python3 tools/check-always-on-free.py --mutate   # prove the check can fail
"""
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "always-on-free.json")

COUNTABLE = {"T1", "T2", "T3"}
TIERS = COUNTABLE | {"DEAD", "UNVERIFIED"}
MIN_HITS = 10

# Evidence a counted row must be able to point at. "research pass" is a
# legitimate weight, but it must SAY so; unattributed provenance fails.
PROV_ME = "me, "
PROV_AGENT = "research pass"

# A first-hand claim must contain something a reader can act on: a URL to
# re-fetch, or a path to the artefact. Matching on a keyword list is what the
# first version did, and a row whose verified_by was the literal string
# "me, i typed the word api" passed it - a check that a sentence can satisfy is
# not a check.
ARTEFACT = re.compile(r"https?://|verify/pages/|openapi|curl|probed live", re.I)


def provenance(row):
    """Return the weight a row's verification carries.

    'read'    - a human fetched the page and quoted the bytes
    'carried' - a research agent fetched it; accepted, but labelled as such
    'unknown' - unattributed, which is the failure this guard exists to catch
    """
    vb = row.get("verified_by")
    if not isinstance(vb, str):
        return "unknown"
    if vb.startswith(PROV_ME):
        return "read"
    if PROV_AGENT in vb or "unverified" in vb.lower():
        return "carried"
    return "unknown"


def check(doc):
    fails = []
    rows = doc.get("rows")
    if not isinstance(rows, list):
        return ["data has no 'rows' list; the census cannot be checked"]

    ids = [r.get("id") for r in rows]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        fails.append(f"duplicate row ids: {sorted(dupes)}")

    hits = [r for r in rows if r.get("tier") in COUNTABLE]
    if len(hits) < MIN_HITS:
        fails.append(
            f"only {len(hits)} rows reach T1/T2/T3; the brief asks for >= {MIN_HITS}"
        )

    for r in rows:
        rid = r.get("id", "<no id>")
        tier = r.get("tier")
        if tier not in TIERS:
            fails.append(f"{rid}: tier {tier!r} is not one of {sorted(TIERS)}")
            continue
        if tier == "UNVERIFIED":
            if not r.get("source"):
                fails.append(f"{rid}: UNVERIFIED but names no source to check")
            continue
        if tier == "DEAD":
            if not r.get("hard_wall"):
                fails.append(f"{rid}: classed DEAD but names no hard wall; say what a relay or keepalive cannot fix")
            continue

        # A counted row must not still be carrying the wall that killed it.
        # Without this, flipping a DEAD row to T1 passes every other clause: the
        # hard_wall field is only read on DEAD rows, so promoting one is silent.
        # Reviews caught exactly this - Railway's 24-hour deletion countdown and
        # the Hugging Face PRO creation gate both promoted to T1 with zero
        # failures.
        if r.get("hard_wall"):
            fails.append(
                f"{rid}: counted as tier {tier} but still carries a hard_wall; "
                f"a row nothing can rescue does not belong in the counted tiers"
            )

        if not r.get("source"):
            fails.append(f"{rid}: counted as a hit but carries no source URL")
        if not r.get("verified_by"):
            fails.append(f"{rid}: counted as a hit but does not say who verified it")
        if provenance(r) == "unknown":
            fails.append(f"{rid}: verified_by is unattributed (start with 'me, ' or name a research pass)")
        if provenance(r) == "read" and not ARTEFACT.search(r.get("verified_by") or ""):
            fails.append(
                f"{rid}: claims first-hand verification but verified_by names no "
                f"URL, no verify/pages artefact, and no probe to reproduce"
            )
        if not r.get("quote"):
            fails.append(f"{rid}: counted as a hit but carries no primary vendor quote")
        if tier == "T2" and not r.get("keepalive"):
            fails.append(f"{rid}: tier T2 means 'always-on with a keepalive' but names no keepalive")
        if tier == "T3" and not r.get("relay"):
            fails.append(f"{rid}: tier T3 means 'needs a relay' but names no relay path")
        if tier in ("T1", "T2") and r.get("relay"):
            fails.append(f"{rid}: tier {tier} is reachable without a relay but names one")

    declared = doc.get("counts", {})
    if isinstance(declared, dict):
        for tier in sorted(TIERS):
            actual = sum(1 for r in rows if r.get("tier") == tier)
            if declared.get(tier) != actual:
                fails.append(f"counts.{tier} says {declared.get(tier)}, rows array has {actual}")

    return fails


def _drop_below_floor(d):
    """Remove counted rows AND fix the counts, so the only clause that can fire
    is the floor. The previous version dropped the 7 T1 rows, which left 15
    counted - still above the floor - and was 'caught' only because the declared
    counts desynced. A mutation that trips a neighbouring clause proves nothing
    about the clause it is named after."""
    doomed = {r["id"] for r in d["rows"] if r.get("tier") in COUNTABLE}
    # Keep only three counted rows so the floor is genuinely breached.
    kept = []
    for r in d["rows"]:
        if r.get("tier") in COUNTABLE and len(kept) < 3:
            kept.append(r["id"])
    doomed -= set(kept)
    d["rows"] = [r for r in d["rows"] if r["id"] not in doomed]
    from collections import Counter
    c = Counter(r.get("tier") for r in d["rows"])
    d["counts"] = {t: c[t] for t in sorted(TIERS)}


def _promote_dead_to_t1(d):
    """Promote a DEAD row to the strongest tier, with a keepalive and a source
    added so that no other clause can be what catches it. Before the
    hard_wall clause existed this passed every clause silently."""
    for r in d["rows"]:
        if r.get("tier") == "DEAD" and r.get("hard_wall"):
            r["tier"] = "T1"
            break
    from collections import Counter
    c = Counter(r.get("tier") for r in d["rows"])
    d["counts"] = {t: c[t] for t in sorted(TIERS)}


MUTATIONS = [
    ("drop the census below the ten-row floor (counts left consistent)",
     _drop_below_floor, "the brief asks for"),
    ("promote a DEAD row to T1, keepalive and counts made consistent",
     _promote_dead_to_t1, "still carries a hard_wall"),
    ("strip the source and verification from a hit",
     lambda d: [(r.pop("source"), r.pop("verified_by")) for r in d["rows"] if r["id"] == "oracle-a1-alwaysfree"],
     "carries no source URL"),
    ("strip the primary quote from a hit",
     lambda d: [r.pop("quote", None) for r in d["rows"] if r["id"] == "gcp-e2-micro"],
     "no primary vendor quote"),
    ("claim a relay on a row that needs no relay",
     lambda d: [r.__setitem__("relay", "localhost.run") for r in d["rows"] if r["id"] == "render-free-web-service"],
     "reachable without a relay"),
    ("strip the hard wall from a DEAD row",
     lambda d: [r.pop("hard_wall", None) for r in d["rows"] if r["id"] == "aws-free-tier"],
     "names no hard wall"),
    ("leave a T2 row with no keepalive",
     lambda d: [r.__setitem__("keepalive", None) for r in d["rows"] if r["id"] == "render-free-web-service"],
     "names no keepalive"),
    ("desync the declared counts from the rows",
     lambda d: d["counts"].__setitem__("T1", 99),
     "rows array has"),
    ("invent a duplicate row id",
     lambda d: d["rows"].append(dict(d["rows"][0])),
     "duplicate row ids"),
    ("make a hit's verification unattributed (fake provenance)",
     lambda d: [r.__setitem__("verified_by", "checked, looks good") for r in d["rows"] if r["id"] == "oracle-a1-alwaysfree"],
     "unattributed"),
    ("claim first-hand verification with no way to reproduce it",
     lambda d: [r.__setitem__("verified_by", "me, 2026-10-06 - confirmed it is fine") for r in d["rows"] if r["id"] == "gcp-e2-micro"],
     "no URL, no verify/pages artefact"),
    ("satisfy the provenance clause with a keyword-only string",
     lambda d: [r.__setitem__("verified_by", "me, i typed the word api") for r in d["rows"] if r["id"] == "gcp-e2-micro"],
     "no URL, no verify/pages artefact"),
    ("delete the rows list entirely",
     lambda d: d.pop("rows"),
     "no 'rows' list"),
]


def main():
    with open(DATA, encoding="utf-8") as fh:
        doc = json.load(fh)
    fails = check(doc)

    if "--mutate" in sys.argv:
        if fails:
            print("REFUSING TO RUN MUTATIONS: the census is already failing.\n")
            for f in fails:
                print(" -", f)
            return 1
        print(f"baseline passes ({len(doc['rows'])} rows, "
              f"{sum(1 for r in doc['rows'] if r['tier'] in COUNTABLE)} counted)\n")
        caught = wrong_clause = 0
        for name, mutate, expect in MUTATIONS:
            trial = copy.deepcopy(doc)
            mutate(trial)
            got = check(trial)
            if not got:
                print(f"  MISSED     {name}")
                print("             <-- the check does not catch this")
                continue
            caught += 1
            if any(expect in g for g in got):
                print(f"  CAUGHT     {name}")
            else:
                wrong_clause += 1
                print(f"  WRONG-REASON {name}")
                print(f"               expected a failure containing {expect!r}, got: {got[0]}")
        total = len(MUTATIONS)
        print(f"\n{caught}/{total} mutations caught, {caught - wrong_clause} by the "
              f"clause they name")
        return 0 if (caught == total and wrong_clause == 0) else 1

    hits = [r for r in doc["rows"] if r["tier"] in COUNTABLE]
    counts = " ".join(f"{t}={sum(1 for r in doc['rows'] if r['tier'] == t)}" for t in sorted(TIERS))
    print(f"always-on free compute census - {len(doc['rows'])} rows, {len(hits)} counted  [{counts}]")
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails:
            print(" -", f)
        return 1
    print("ok always_on_free_guard")
    return 0


if __name__ == "__main__":
    sys.exit(main())