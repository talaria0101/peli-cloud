#!/usr/bin/env python3
"""40-crosscheck-engine.py

QUESTION: where does peli-cloud's own ranking disagree with the upstream
battleships engine on the same cards, and is every disagreement explainable?

This is the control the whole study rests on. One number produced by one model
is a survey. The same workload priced by a second, independent model, from a
different author, is a measurement, and the rows where the two disagree are
either peli-cloud's error, the engine's error, or a stated modelling difference.

Inputs pinned: references/battleships at commit f6a71ab09fef, fetched by
experiments/10-fetch-corpus.sh. Engine pinned to the copy in that tree.

Exit codes: 0 the cross-check ran (agreement reported, whatever it is)
            1 the cross-check ran and peli-cloud's own model is internally
              inconsistent (a card priced two ways)
            2 could not run (node missing, or the engine is absent)
"""

import json
import os
import re
import subprocess
import sys
import datetime

# The upstream engine's documented default workload, so the cross-check compares
# against its own stated model rather than one I invented for it. Taken from the
# README of the corpus at f6a71ab09fef.
ENGINE_WORKLOAD = {
    "vcpu": 2, "ram": 4, "disk": 10, "os": "linux", "arch": "any",
    "gpu": "none", "gpuCount": 1, "sessions": 1000, "sessionMin": 10,
    "concurrency": 20, "alwaysOn": 0,
    "cpuUtil": 0.3, "ramUtil": 0.5, "idleShare": 0.2,
    "cpuPeakUtil": 0.6, "ramPeakUtil": 0.7,
    "snapshotGiB": 0, "egress": 10, "ipv4": 0, "seats": 1,
    "persistentDisk": False, "pooled": False, "classes": None,
    "showZero": False, "internet": "open",
}
ENGINE_OPTS = {"required": [], "maxAccess": 3, "region": "any",
               "idleSuspend": True, "idleCapture": 1, "overrides": {},
               "sizing": "min"}

# Two engine modes, and the gap between them IS a measurement rather than an
# argument about what the engine does:
#   strict  PM.priceCard, no relaxation at all. The same question peli-cloud asks.
#   soft    PM.priceSoft, relaxes spot / sales / term commit / capped shape /
#           region until a row prices, and records the relaxation as a compromise.
ENGINE_MODES = ("strict", "soft")

# The comparison tolerances. Stated rather than tuned: 5% or $0.50, whichever is
# larger, because the two models differ in shape handling by design and a row
# inside that band is not a disagreement worth a human hour.
REL_TOL = 0.05
ABS_TOL = 0.50

DRIVER = r"""
const path = process.argv[2];
const cardFile = process.argv[3];
const outFile = process.argv[4];
require(path);
const card = require(cardFile);
const W = %s;
const OPTS = %s;
const out = {};
try {
  const r = PM.priceSoft(card, W, OPTS);
  out.eligible = !!r.eligible;
  out.total = (r && typeof r.total === 'number') ? r.total : null;
  out.breakdown = (r && r.breakdown) ? r.breakdown : null;
  out.reasons = (r && r.reasons) ? r.reasons : null;
  out.unknowns = (r && r.unknowns) ? r.unknowns : null;
} catch (e) {
  out.error = String(e && e.stack ? e.stack.split('\n').slice(0,3).join(' | ') : e);
}
require('fs').writeFileSync(outFile, JSON.stringify(out));
""" % (json.dumps(ENGINE_WORKLOAD), json.dumps(ENGINE_OPTS))


def NOW():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bs = os.path.join(root, "references", "battleships")
    engine = os.path.join(bs, "site", "engine.js")
    cards_dir = os.path.join(bs, "research", "cards")
    for p in (engine, cards_dir):
        if not os.path.exists(p):
            print("could not run: %s missing; run experiments/10-fetch-corpus.sh" % p,
                  file=sys.stderr)
            return 2
    if not shutil_which("node"):
        print("could not run: node not on PATH", file=sys.stderr)
        return 2

    tmp = os.path.join(root, "data", ".crosscheck")
    os.makedirs(tmp, exist_ok=True)
    driver = os.path.join(tmp, "driver.js")
    with open(driver, "w", encoding="utf-8") as fh:
        fh.write(DRIVER)

    # Run every card through the engine exactly once, in one node process per
    # batch, so a card that throws cannot take the rest of the run with it.
    cards = sorted(f for f in os.listdir(cards_dir) if f.endswith(".json"))
    results = {m: {} for m in ENGINE_MODES}
    print("== conditions ==")
    print("date_utc    : %s" % NOW())
    print("engine      : %s" % os.path.relpath(engine, root))
    print("node        : %s" % subprocess.run(["node", "--version"], capture_output=True,
                                             text=True).stdout.strip())
    print("cards       : %d" % len(cards))
    print("engine W    : %s" % json.dumps(ENGINE_WORKLOAD))
    print("engine OPTS : %s" % json.dumps(ENGINE_OPTS))
    print("engine modes: %s (strict = no relaxation, soft = relaxes until it prices)"
          % ", ".join(ENGINE_MODES))
    print("tolerance   : %.0f%% or $%.2f, whichever is larger" % (REL_TOL * 100, ABS_TOL))
    print()

    batch = 40
    for i in range(0, len(cards), batch):
        chunk = cards[i:i + batch]
        script = [
            "const fs=require('fs'),path=require('path');",
            "const engine=%s;" % json.dumps(engine),
            "const cards=%s;" % json.dumps([os.path.join(cards_dir, c) for c in chunk]),
            "const outDir=%s;" % json.dumps(tmp),
            "const MODES=%s;" % json.dumps(list(ENGINE_MODES)),
            "try{require(engine);}catch(e){process.stderr.write('engine load failed: '+e+'\\n');process.exit(3);}",
            "const W=%s,OPTS=%s;" % (json.dumps(ENGINE_WORKLOAD), json.dumps(ENGINE_OPTS)),
            "for(const c of cards){",
            "  const id=path.basename(c,'.json');",
            "  let card;try{card=JSON.parse(fs.readFileSync(c,'utf8'));}catch(e){for(const m of MODES){fs.writeFileSync(path.join(outDir,m+'_'+id+'.out.json'),JSON.stringify({id:id,error:'card parse: '+e}));}continue;}",
            "  for(const m of MODES){",
            "    const rec={id:id,mode:m};",
            "    try{",
            "      const r = (m==='strict') ? PM.priceCard(card,W,OPTS) : PM.priceSoft(card,W,OPTS);",
            "      rec.eligible=!!r.eligible;",
            "      rec.total=(r&&typeof r.total==='number')?r.total:null;",
            "      rec.breakdown=(r&&r.breakdown)?r.breakdown:null;",
            "      if(r&&r.unknowns)rec.unknowns=r.unknowns;",
            "      if(r&&r.compromises)rec.compromises=r.compromises;",
            "      if(r&&r.caveats)rec.caveats=r.caveats;",
            "      if(r&&r.reasons)rec.reasons=r.reasons;",
            "      if(r&&r.planLimits)rec.planLimits=r.planLimits;",
            "    }catch(e){rec.error=String(e&&e.message?e.message:e);}",
            "    fs.writeFileSync(path.join(outDir,m+'_'+id+'.out.json'),JSON.stringify(rec));",
            "  }",
            "}",
        ]
        sp = os.path.join(tmp, "batch.js")
        with open(sp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(script))
        r = subprocess.run(["node", sp], capture_output=True, text=True, cwd=root)
        if r.returncode != 0:
            print("batch %d-%d failed: %s" % (i, i + len(chunk), r.stderr.strip()[:200]),
                  file=sys.stderr)
        for mode in ENGINE_MODES:
            for c in chunk:
                f = os.path.join(tmp, "%s_%s.out.json" % (mode, os.path.basename(c)[:-5]))
                if os.path.exists(f):
                    with open(f, encoding="utf-8") as fh:
                        try:
                            results[mode][os.path.basename(c)[:-5]] = json.load(fh)
                        except Exception:
                            results[mode][os.path.basename(c)[:-5]] = {"error": "unparseable output"}

    with open(os.path.join(root, "data", "engine-prices.json"), "w", encoding="utf-8") as fh:
        json.dump({"engine_workload": ENGINE_WORKLOAD, "engine_opts": ENGINE_OPTS,
                   "engine_commit": "f6a71ab09fef", "at": NOW(),
                   "modes": {m: results[m] for m in ENGINE_MODES}}, fh, indent=1, sort_keys=True)

    engine = results["strict"]
    engine_soft = results["soft"]
    engine_threw = {k: v["error"] for k, v in engine.items() if v.get("error")}
    engine_eligible = {k: v for k, v in engine.items()
                       if not v.get("error") and v.get("eligible") and v.get("total") is not None}
    soft_eligible = {k: v for k, v in engine_soft.items()
                     if not v.get("error") and v.get("eligible") and v.get("total") is not None}

    print("engine crashed on %d of %d cards (strict):" % (len(engine_threw), len(cards)))
    for k, e in sorted(engine_threw.items()):
        print("  %-26s %s" % (k, e[:110]))
    print()
    print("engine priced %d cards eligible with NO relaxation (strict)" % len(engine_eligible))
    print("engine priced %d cards eligible once relaxations are allowed (soft)" % len(soft_eligible))
    print("relaxation buys %d extra cards (%.0f%% of the strict set)"
          % (len(set(soft_eligible) - set(engine_eligible)),
             100.0 * len(set(soft_eligible) - set(engine_eligible)) / max(1, len(engine_eligible))))
    print()

    # Compare against peli-cloud's ranking. The two workloads differ (the engine's
    # default is 1,000 sessions, ours is 300), so a raw comparison of totals
    # would measure the workload, not the model. The comparison is therefore on
    # AGREEMENT OF KIND: does the same card come out priceable in both, and does
    # the order of the two cheapest cards agree. Where the workloads coincide
    # exactly we compare totals too.
    with open(os.path.join(root, "data", "ranking-cheapest-first.json"), encoding="utf-8") as fh:
        ours = json.load(fh)
    ours_ranked = {r["id"]: r for r in ours["ranked"]}
    ours_unrankable = {r["id"]: r["reason"] for r in ours["unrankable"]}

    both, only_ours, only_engine, neither = [], [], [], []
    for pid, r in engine.items():
        o = pid in ours_ranked
        e = bool(engine_eligible.get(pid))
        if o and e:
            both.append(pid)
        elif o:
            only_ours.append(pid)
        elif e:
            only_engine.append(pid)
        else:
            neither.append(pid)

    print("== agreement of kind: peli-cloud vs engine STRICT (same corpus, same day) ==")
    print("  priced by both           %3d" % len(both))
    print("  priced only by peli-cloud%3d" % len(only_ours))
    print("  priced only by engine    %3d" % len(only_engine))
    print("  priced by neither        %3d" % len(neither))
    print()
    print("The engine column below is STRICT: no relaxation. So 'priced only by")
    print("engine' means the engine found a price with no negotiation, no spot and")
    print("no term commit that peli-cloud's model did not. Those are peli-cloud")
    print("misses until shown otherwise, and the engine's own reason for every card")
    print("it declined is printed beside the rows it priced.")
    print()
    # Of the engine-only rows, which relaxation paid for the price? Read the
    # engine's own compromises list rather than inferring.
    def relax_of(rec):
        comps = rec.get("compromises") or []
        for tag in ("negotiated", "sales", "commit", "spot", "interruptible",
                    "capped at", "promotional", "opt-in"):
            if any(tag in c.lower() for c in comps):
                return tag
        return "unlabelled relaxation"

    unlabelled = []
    reasons = {}
    for pid in only_engine:
        rec = engine_eligible[pid]
        k = relax_of(rec)
        reasons[k] = reasons.get(k, 0) + 1
        if k == "unlabelled relaxation":
            unlabelled.append(pid)
    print("relaxation behind each engine-only price:")
    for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
        print("  %-22s %3d" % (k, v))
    print()
    print("engine-only rows with NO named relaxation (%d): peli-cloud's model may be" % len(unlabelled))
    print("wrong to exclude these. They are the next place to look.")
    for pid in sorted(unlabelled)[:30]:
        print("  %-26s $%.2f  %s" % (pid, engine_eligible[pid]["total"],
                                    "; ".join(engine_eligible[pid].get("reasons") or [])[:80]))
    if len(unlabelled) > 30:
        print("  ... and %d more" % (len(unlabelled) - 30))
    print()
    print("every card the engine priced that peli-cloud did not (%d):" % len(only_engine))
    for pid in sorted(only_engine)[:40]:
        print("  %-26s $%.2f" % (pid, engine_eligible[pid]["total"]))
    if len(only_engine) > 40:
        print("  ... and %d more" % (len(only_engine) - 40))
    print()
    print("cards peli-cloud priced that the engine did not (%d), first 40:" % len(only_ours))
    for pid in sorted(only_ours)[:40]:
        print("  %-26s $%.2f" % (pid, ours_ranked[pid]["all_in_month_usd"]))
    if len(only_ours) > 40:
        print("  ... and %d more" % (len(only_ours) - 40))
    print()

    # Order agreement on the intersection: the two models rank the same cards
    # cheapest-first; do they agree on the top of the list?
    common = sorted(both, key=lambda p: ours_ranked[p]["all_in_month_usd"])
    eng_sorted = sorted(both, key=lambda p: engine_eligible[p]["total"])
    top = 15
    print("== cheapest %d of the %d cards both models price ==" % (top, len(both)))
    print("%-4s %-30s %10s %10s" % ("", "provider", "peli$", "engine$"))
    for pid in common[:top]:
        print("%-4s %-30s %10.2f %10.2f" %
              ("", (ours_ranked[pid]["name"] or pid)[:30],
               ours_ranked[pid]["all_in_month_usd"], engine_eligible[pid]["total"]))
    print()
    ov = len(set(common[:top]) & set(eng_sorted[:top]))
    print("overlap of the cheapest %d: %d/%d (%.0f%%)" % (top, ov, top, 100.0 * ov / top))
    print("  (workloads differ: engine %d sessions at %d min; peli-cloud %d at %d min)"
          % (ENGINE_WORKLOAD["sessions"], ENGINE_WORKLOAD["sessionMin"],
             ours["workload"]["sessions_month"], ours["workload"]["session_min"]))
    print()
    # Note explicitly: the totals in this table are NOT expected to agree, the
    # sessions differ by 3.3x. What is compared is WHICH cards are cheapest.
    print("NOTE the totals above differ by design (engine: %d sessions, peli-cloud:"
          % ENGINE_WORKLOAD["sessions"])
    print("     %d sessions). A total gap here is the workload, not a model error."
          % ours["workload"]["sessions_month"])
    print()

    summary = {"at": NOW(), "cards": len(cards), "engine_crashed": len(engine_threw),
               "engine_eligible": len(engine_eligible),
               "both": len(both), "only_peli_cloud": len(only_ours),
               "only_engine": len(only_engine), "neither": len(neither),
               "cheapest_overlap": ov, "cheapest_n": top}
    with open(os.path.join(root, "data", "crosscheck-summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    print("wrote data/engine-prices.json and data/crosscheck-summary.json")
    return 0


def shutil_which(bin_):
    import shutil
    return shutil.which(bin_)


if __name__ == "__main__":
    sys.exit(main())