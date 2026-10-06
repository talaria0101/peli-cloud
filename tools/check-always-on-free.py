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
import json
import os
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


def provenance(row):
    """Return the weight a row's verification carries.

    'read'    - a human fetched the page and quoted the bytes
    'carried' - a research agent fetched it; accepted, but labelled as such
    'unknown' - unattributed, which is the failure this guard exists to catch
    """
    vb = row.get("verified_by") or ""
    if vb.startswith(PROV_ME):
        return "read"
    if PROV_AGENT in vb or "unverified" in vb.lower():
        return "carried"
    return "unknown"


def check(doc):
    fails = []
    rows = doc["rows"]
    ids = [r.get("id") for r in rows]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        fails.append(f"duplicate row ids: {sorted(dupes)}")

    hits = [r for r in rows if r.get("tier") in COUNTABLE]
    if len(hits) < MIN_HITS:
        fails.append(f"only {len(hits)} rows reach T1/T2/T3; the brief asks for >= {MIN_HITS}")

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

        if not r.get("source"):
            fails.append(f"{rid}: counted as a hit but carries no source URL")
        if not r.get("verified_by"):
            fails.append(f"{rid}: counted as a hit but does not say who verified it")
        if provenance(r) == "unknown":
            fails.append(f"{rid}: verified_by is unattributed (start with 'me, ' or name a research pass)")
        if provenance(r) == "read":
            how = ("verify/pages", "curl", "fetched", "github raw", "probed live", "openapi", "api")
            if not any(k in r["verified_by"].lower() for k in how):
                fails.append(f"{rid}: claims 'me, ...' verification but does not say how the evidence was captured")
        if not r.get("quote"):
            fails.append(f"{rid}: counted as a hit but carries no primary vendor quote")
        if tier == "T2" and not r.get("keepalive"):
            fails.append(f"{rid}: tier T2 means 'always-on with a keepalive' but names no keepalive")
        if tier == "T3" and not r.get("relay"):
            fails.append(f"{rid}: tier T3 means 'needs a relay' but names no relay path")
        if tier in ("T1", "T2") and r.get("relay"):
            fails.append(f"{rid}: tier {tier} is reachable without a relay but names one")

    declared = doc.get("counts", {})
    for tier in sorted(TIERS):
        actual = sum(1 for r in rows if r.get("tier") == tier)
        if declared.get(tier) != actual:
            fails.append(f"counts.{tier} says {declared.get(tier)}, rows array has {actual}")

    return fails


MUTATIONS = [
    ("drop the census below the ten-row floor",
     lambda d: d.__setitem__("rows", [r for r in d["rows"] if r["tier"] != "T1"])),
    ("promote a DEAD row (Railway Free VM) to a counted hit",
     lambda d: [r.__setitem__("tier", "T2") for r in d["rows"] if r["id"] == "railway-free-vm"]),
    ("strip the source and verification from a hit",
     lambda d: [(r.pop("source"), r.pop("verified_by")) for r in d["rows"] if r["id"] == "oracle-a1-alwaysfree"]),
    ("strip the primary quote from a hit",
     lambda d: [r.pop("quote", None) for r in d["rows"] if r["id"] == "gcp-e2-micro"]),
    ("claim a relay on a row that needs no relay",
     lambda d: [r.__setitem__("relay", "localhost.run") for r in d["rows"] if r["id"] == "render-free-web-service"]),
    ("strip the hard wall from a DEAD row",
     lambda d: [r.pop("hard_wall", None) for r in d["rows"] if r["id"] == "aws-free-tier"]),
    ("leave a T2 row with no keepalive",
     lambda d: [r.__setitem__("keepalive", None) for r in d["rows"] if r["id"] == "render-free-web-service"]),
    ("desync the declared counts from the rows",
     lambda d: d["counts"].__setitem__("T1", 99)),
    ("invent a duplicate row id",
     lambda d: d["rows"].append(dict(d["rows"][0]))),
    ("make a hit's verification unattributed (fake provenance)",
     lambda d: [r.__setitem__("verified_by", "checked, looks good") for r in d["rows"] if r["id"] == "oracle-a1-alwaysfree"]),
    ("claim first-hand verification with no capture method",
     lambda d: [r.__setitem__("verified_by", "me, 2026-10-06 - confirmed it is fine") for r in d["rows"] if r["id"] == "gcp-e2-micro"]),
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
        caught = 0
        for name, mutate in MUTATIONS:
            import copy
            trial = copy.deepcopy(doc)
            mutate(trial)
            got = check(trial)
            if got:
                caught += 1
                print(f"  CAUGHT   {name}\n           -> {got[0]}")
            else:
                print(f"  MISSED   {name}  <-- the check does not catch this")
        print(f"\n{caught}/{len(MUTATIONS)} mutations caught")
        return 0 if caught == len(MUTATIONS) else 1

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