#!/usr/bin/env python3
"""52-apply-posture.py

QUESTION: what do the 183 first-party billing-posture verdicts do to the
published numbers, and which of them is safe to act on automatically?

`51-billing-posture-probe.py` fetches each provider's own page and classifies
what the vendor says about billing a machine that is stopped, paused or idle.
This script takes those verdicts and turns them into keep rates, then says
exactly which rows moved and by how much.

The separation matters. The probe measures; this decides. A verdict is evidence,
not an instruction, and the two are kept apart so that a reader can disagree with
the mapping without re-fetching 183 pages, and so that a change to the mapping
does not require a change to the measurement.

WHAT IT WRITES. data/billing-posture-applied.json, and nothing else. It does not
edit the period model. `53-apply-posture-to-model.py` is the only thing that
changes a keep rate, and it will only do so for a verdict that is BOTH
first-party and non-ambiguous.

THE MAPPING, and why each one is what it is.

    suspends      keep 0.00   the vendor says a stopped machine does not bill.
                             Safe to apply: it is the vendor's own statement
                             about the thing being priced.

    bills_uptime  keep 1.00   the vendor says a stopped machine is still billed.
                             This is a CONFIRMATION of the existing default, so
                             applying it changes no number. It is still worth
                             recording: it converts an assumption into a
                             measurement, which is the difference between "we do
                             not know" and "we checked".

    partial       NOT APPLIED  one resource stops billing and another does not.
                             A single keep rate cannot express it. Applying 0.0
                             would understate the bill by the resource that
                             keeps charging, and applying 1.0 would overstate
                             the saving. The row keeps the conservative default
                             and is listed as needing a split model, which is a
                             real piece of work and not something to fake with
                             one number.

    unstated      NOT APPLIED  the page was read and says nothing. Silence is not
                             evidence of billing for uptime, and treating it as
                             such would be inventing a fact.

    shell         NOT APPLIED  the page renders client-side; nothing was read.

    unreachable   NOT APPLIED  the page could not be fetched from this host.

Exit codes: 0 the verdicts were mapped, 1 the probe artefact is missing or
            unusable, 2 could not run.
"""

import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Only a verdict the vendor actually stated, in prose, about billing a stopped
# machine, and which is not partial, is allowed to move a number.
SAFE_TO_APPLY = {"suspends": 0.0, "bills_uptime": 1.0}


def main():
    probe_path = os.path.join(ROOT, "data", "billing-posture.json")
    model_path = os.path.join(ROOT, "data", "period-model.json")
    if not os.path.isfile(probe_path):
        print("could not run: %s missing; run experiments/51-billing-posture-probe.py"
              % probe_path, file=sys.stderr)
        return 2
    if not os.path.isfile(model_path):
        print("could not run: %s missing; run experiments/70-period-model.py"
              % model_path, file=sys.stderr)
        return 2
    with open(probe_path, encoding="utf-8") as fh:
        probe = json.load(fh)
    with open(model_path, encoding="utf-8") as fh:
        model = json.load(fh)

    verdicts = {r["id"]: r for r in probe["rows"]}

    print("== conditions ==")
    print("date_utc        : %s" % datetime.datetime.now(datetime.timezone.utc)
          .strftime("%Y-%m-%dT%H:%M:%SZ"))
    print("probe_artifact  : %s" % os.path.relpath(probe_path, ROOT))
    print("probed_at       : %s" % probe.get("probed_at"))
    print("providers probed: %d" % len(verdicts))
    print("mapping         : suspends->0.00  bills_uptime->1.00")
    print("                  partial / unstated / shell / unreachable -> NOT applied")
    print()

    applied, confirmed, withheld, moved = [], [], [], []

    for p in model["providers"]:
        v = verdicts.get(p["id"])
        shapes = p.get("shapes") or {}
        rows = [s for s in shapes.values() if s.get("keep_source") == "default"]
        if not v or not rows:
            continue
        rec = {"id": p["id"], "name": p.get("name"), "verdict": v["verdict"],
               "why": v.get("why"), "quote": v.get("quote"), "url": v.get("url"),
               "rows": len(rows), "kept": None, "new_keep": None,
               "moved_usd_at_24h": None}
        if v["verdict"] in SAFE_TO_APPLY:
            new_keep = SAFE_TO_APPLY[v["verdict"]]
            rec["kept"] = new_keep
            rec["new_keep"] = new_keep
            # What the change is worth, on the figure a reader is most likely to
            # act on. It has to be measured at a duty cycle that LEAVES IDLE
            # TIME, because at 24 h/day the machine is never idle and the keep
            # rate cannot change anything. Measuring at 24 h made every
            # suspension show a $0.00 movement, which reads as "this changes
            # nothing" and is true only of the one column where it cannot.
            for s in rows:
                hourly = s.get("hourly")
                pd = s["periods"].get("1h")
                if isinstance(hourly, (int, float)) and pd:
                    held = pd.get("hours_per_day", 1.0)
                    idle = 24.0 - held
                    old_hold = hourly * (held + idle * 1.0) * 30.0
                    new_hold = hourly * (held + idle * new_keep) * 30.0
                    rec["moved_usd_holding_1h_duty"] = round(new_hold - old_hold, 2)
                    rec["held_before"] = round(old_hold, 2)
                    rec["held_after"] = round(new_hold, 2)
                    break
            if new_keep == 0.0:
                moved.append(rec)
            else:
                confirmed.append(rec)
            applied.append(rec)
        else:
            rec["kept"] = None
            rec["reason_not_applied"] = {
                "partial": "one resource stops billing and another does not; a "
                           "single keep rate cannot express it, and 0.0 would "
                           "understate the bill by the resource that keeps "
                           "charging",
                "unstated": "the page was read and does not state a policy; "
                            "silence is not evidence of billing for uptime",
                "shell": "the page renders client-side, so nothing was read",
                "unreachable": "the page could not be fetched from this host",
            }.get(v["verdict"], "not a first-party verdict")
            withheld.append(rec)

    print("-- what moves a number --")
    if not moved:
        print("  nothing")
    for r in sorted(moved, key=lambda x: -abs(x.get("moved_usd_holding_1h_duty") or 0)):
        print("  %-20s %s -> 0.00   holding a 1 h/day box: $%.2f -> $%.2f/mo  %s"
              % (r["id"], r["verdict"], r.get("held_before") or 0.0,
                 r.get("held_after") or 0.0, (r["why"] or "")[:34]))
    print()
    print("-- what confirms the existing default (no number changes) --")
    for r in confirmed:
        print("  %-20s %s -> 1.00   %s" % (r["id"], r["verdict"], (r["why"] or "")[:52]))
    if not confirmed:
        print("  nothing")
    print()
    print("-- verdicts recorded but NOT applied, and why --")
    by_reason = {}
    for r in withheld:
        by_reason.setdefault(r["verdict"], []).append(r["id"])
    for k in sorted(by_reason):
        print("  %-12s %3d  %s" % (k, len(by_reason[k]),
                                    ", ".join(sorted(by_reason[k])[:6])
                                    + (" ..." if len(by_reason[k]) > 6 else "")))
    print()
    print("Rows still on the conservative 1.00 default, of the ones probed:")
    still = sum(r["rows"] for r in withheld)
    print("  %d rows across %d providers" % (still, len(withheld)))
    print("Of those, %d rows across %d providers have a PARTIAL policy the model"
          % (sum(r["rows"] for r in withheld if r["verdict"] == "partial"),
             len(by_reason.get("partial", []))))
    print("cannot express with one number. That is a real modelling gap, and it")
    print("is named here rather than approximated.")

    dest = os.path.join(ROOT, "data", "billing-posture-applied.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump({"at": datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "probed_at": probe.get("probed_at"),
                   "mapping": SAFE_TO_APPLY,
                   "applied": applied, "withheld": withheld,
                   "counts": {"applied": len(applied), "moved": len(moved),
                              "confirmed": len(confirmed),
                              "withheld": len(withheld)}}, fh,
                  indent=1, sort_keys=True)
    print()
    print("wrote %s" % dest)
    print("NOTE: this script does not change the period model. 53 does that, and")
    print("only for the verdicts in `applied`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
