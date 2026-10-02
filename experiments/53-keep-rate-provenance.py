#!/usr/bin/env python3
"""53-keep-rate-provenance.py

QUESTION: for every priced row, where did its keep rate come from, and how much
of the table is measured rather than assumed?

REPORTING ONLY. An earlier version of this script rewrote keep rates into
data/period-model.json. That worked until anyone re-ran 70-period-model.py,
which recomputed every keep rate from the corpus card and silently discarded all
thirty probed rows -- no error, no warning, a smaller number of measured rows
than the run before. A step that has to be remembered is a step that gets
forgotten, and that one failed quietly.

So 70 now reads data/billing-posture.json itself, as an input, and this script
answers the question a reader actually has: how much of this table is evidence.
Keeping it separate from 51 (which measures) and 52 (which decides) means the
mapping can be argued with without re-fetching 183 pages.

THE RULE, and it is deliberately narrow. A keep rate is replaced only when:

  1. the vendor's own page was fetched and read, and
  2. the vendor stated a policy in prose, not inside a JSON blob, not as a
     question, and not with a negation that inverts the sentence, and
  3. the policy is unambiguous in the sense that one resource's billing follows
     from it, and
  4. 51's self-test passed on the same run.

Condition 4 matters: the classifier was wrong about three real pages on its
first run and wrong about a fourth on its second, and every one of those
mistakes would have become a wrong keep rate in the catalogue. A self-test that
did not gate publication would have shipped all four.

`partial` is never applied. boxd, pandastack and superserve each say one
resource stops billing and another does not, and a single scalar keep rate
cannot express that. Setting them to 0.00 would understate the bill by the
resource that keeps charging, which is the direction that gets somebody a
surprise invoice.

It writes data/keep-rate-provenance.json, which names for every priced row
whether its keep rate came from the card, from a hand-checked first-party
entry, from this automated probe, or from the conservative default. That file is
the answer to "how much of this table did you actually measure", and it is
regenerated rather than hand-maintained for exactly that reason.

Exit codes: 0 the model was updated, 1 a precondition failed, 2 could not run.
"""

import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _origin(src):
    """Where a keep rate came from, and the three are not equal.

    The first version of this test was `src.startswith("first-party")` before
    the card test, which lumped the 30 automated probe rows in with the 5
    hand-checked ones and reported 35 hand-checked rows. Both are first-party
    and they are not the same thing: one is a person's reading of one page, the
    other is a classifier's reading of a page it fetched. The count was wrong by
    a factor of six and it was wrong in the flattering direction.
    """
    if src.startswith("first-party probe"):
        return "first-party, probed and quoted"
    if src.startswith("first-party"):
        return "first-party, hand-checked"
    if src == "default":
        return "conservative default (1.00)"
    return "corpus card"


def main():
    model_path = os.path.join(ROOT, "data", "period-model.json")
    applied_path = os.path.join(ROOT, "data", "billing-posture-applied.json")
    for p, script in ((model_path, "70-period-model.py"),
                      (applied_path, "52-apply-posture.py")):
        if not os.path.isfile(p):
            print("could not run: %s missing; run experiments/%s" % (p, script),
                  file=sys.stderr)
            return 2
    with open(model_path, encoding="utf-8") as fh:
        model = json.load(fh)
    with open(applied_path, encoding="utf-8") as fh:
        applied = json.load(fh)

    print("== conditions ==")
    print("date_utc      : %s" % datetime.datetime.now(datetime.timezone.utc)
          .strftime("%Y-%m-%dT%H:%M:%SZ"))
    print("model         : %s (corpus %s)" % (os.path.relpath(model_path, ROOT),
                                              model.get("card_commit")))
    print("verdicts      : probed %s" % applied.get("probed_at"))
    print("rule          : a verdict replaces a keep rate only if it is")
    print("                first-party, in prose, unambiguous, and not partial")
    print()

    # Only the entries 52 marked as applied AND that actually change something.
    changes = {r["id"]: r for r in applied["applied"]
               if r.get("new_keep") is not None}

    prov = {}
    for p in model["providers"]:
        for sname, s in (p.get("shapes") or {}).items():
            key = "%s/%s" % (p["id"], sname)
            src = s.get("keep_source") or "unknown"
            prov[key] = {"keep_rate": s.get("keep_rate"),
                         "keep_basis": s.get("keep_basis"),
                         "origin": _origin(src),
                         "source": src}

    changed = []
    for p in model["providers"]:
        for sname, s in (p.get("shapes") or {}).items():
            src = s.get("keep_source") or ""
            if not src.startswith("first-party probe"):
                continue
            pd10 = (s.get("periods") or {}).get("1h") or {}
            changed.append({"provider": p["id"], "shape": sname,
                            "keep_rate": s.get("keep_rate"),
                            "held_after": pd10.get("hold_month"),
                            "source": src})

    print("-- keep rates that came from the automated probe --")
    if not changed:
        print("  none; data/billing-posture.json is missing or empty, so every")
        print("  probed row fell back to the conservative default. Run 51.")
    for c in sorted(changed, key=lambda x: x["provider"]):
        print("  %-20s %-7s keep %.2f   %s"
              % (c["provider"], c["shape"], c["keep_rate"] or 0.0,
                 (c["source"] or "")[:58]))
    print()
    origins = {}
    for v in prov.values():
        origins[v["origin"]] = origins.get(v["origin"], 0) + 1
    print("-- where every priced row's keep rate comes from --")
    for k in sorted(origins, key=lambda x: -origins[x]):
        print("  %-34s %4d rows" % (k, origins[k]))
    print("  %-34s %4d rows" % ("TOTAL", len(prov)))
    print()
    meas = sum(v for k, v in origins.items() if k != "conservative default (1.00)")
    print("MEASURED: %d of %d rows (%.0f%%). The other %d rows carry the"
          % (meas, len(prov), 100.0 * meas / len(prov), len(prov) - meas))
    print("conservative 1.00 and are an assumption, not a reading. Every one of")
    print("them OVERSTATES what holding costs, so the held column is an upper")
    print("bound on those rows, never a floor.")

    dest = os.path.join(ROOT, "data", "keep-rate-provenance.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump({"at": datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "probed_at": applied.get("probed_at"),
                   "origins": origins, "changed": changed,
                   "rows": prov}, fh, indent=1, sort_keys=True)
    print()
    print("wrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
