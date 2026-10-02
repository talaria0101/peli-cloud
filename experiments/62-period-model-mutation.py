#!/usr/bin/env python3
"""62-period-model-mutation.py

QUESTION: can the guards in 61-period-model-guards.py actually fail?

60-guard-mutation.py does this for the guards in 20 and 30, by planting a
defect in a temp card and calling the functions directly. It cannot do it for
the period model, because those defects are not in how a card is parsed. They
are in how the priced rows are ordered and labelled, so proving a guard works
means editing the model, re-running it over all 366 cards, and reading the
artefact. That is what this does, on a throwaway copy of the tree.

Four defects are planted, each reverted from a fix made in this same session.
Each one is a real defect that shipped: these are not hypotheticals.

  1. the console table sorted on the credit-adjusted price
     The ranking's whole promise is "cheapest first", and a provider whose
     recurring credit happened to exceed the month's bill was presented as the
     cheapest thing in the market. Run Cloud topped the 2 vCPU / 4 GiB / 10 h/day
     console table with a month of $0.00 while the published catalogue, built
     by the other rule, put Agent 37 there. Two scripts, one dataset, two
     different answers.

  2. keep_basis read from a leaked loop variable
     The basis travelled on the loop variable left behind by the per-mode scan,
     so every row carried whatever the LAST mode of that card happened to say.
     aws-lambda published keep_source=requires_always_on next to
     keep_basis="billed for uptime", two different claims about one rate.

  3. the per-request test matched note text
     The first version of the fix excluded a mode by searching its note for
     "requests" and "GB-s". It deleted 36 modes across 23 cards, including
     Lizard, Railway, Kernel, Sail, CreateOS and InstaVM, every one of which
     bills per SECOND of running time and is a real sandbox. "requests" also
     means Kubernetes resource requests, inbound HTTP requests, and the phrase
     "no requests". This guard exists to catch that specific regression.

  4. a hardcoded ROOT made the guard suite unrunnable
     61 pointed at /workspace/peli-cloud, so on any other clone it died before
     executing one assertion. Defects 1 to 3 were all written and fixed while
     that was true, and none of them had a working guard. The planted version
     now exits 2 with a message instead of crashing silently.

  5. a size the corpus card dropped that the vendor advertises
     lizard's card keeps only the default size and pins min_vcpu 4, so the
     $0.009/h Small machine the vendor sells was absent from the ranking and
     the row was priced at double. Reverting the correction puts lizard back at
     $5.40/month and unflags the row.

  6. the dispute marker dropped from table C
     Table C is where a reader lands and it had no marker at all: lizard at
     rank 2 with $0.0090 and nothing saying the vendor's docs contradict it.
     The marker rides on the provider name because the "buy it?" column exists
     only in table B.

  7. the footnote explaining the dispute removed
     A mark with no explanation is a mystery to a reader, and this one is a
     price taken from a page that contradicts itself.

  8. the README's hand-typed counts go stale
     The README said 79 one-time credits and 124 $0-tier cards where the data
     said 81 and 116, and still said "Hetzner ranks third" after the Lizard
     correction moved it. A count a script can compute should not be typed.
     GUARD J compares the prose against data/period-model.json.

  9. a month's rent multiplied by the hours in the period
     173 sizes across 8 cards carry a monthly rent in the hourly field. Hostinger
     published at $17,632.80/month and Contabo and netcup were pushed out of the
     top ten by figures 700x their real rent. GUARD K checks the division, that
     a genuine hourly rate is not divided, that a cap which merely exists is not
     mistaken for equality, and that no published 24/7 row exceeds $8,000.

 10. the free allowance stops being priced
     Oracle's A1 allowance covers the whole agent shape, so ignoring it published
     $7.80 for a machine the vendor gives away. GUARD M checks the arithmetic
     against hand-computed values, that the allowance is scoped to the one SKU
     it was granted against, and that one day of usage cannot exhaust a monthly
     allowance.

 11. the keep rate stops changing any number
     It was computed, printed and never used. GUARD N checks that a keep of 0.00
     does not zero the duty-cycle bill, that holding costs less than using for a
     suspending provider, and that a keep of 1.00 leaves them equal at 24/7.

Each mutation must make 61 FAIL. A mutation that leaves 61 passing is itself a
finding: it means the guard does not cover the defect it claims to.

Nothing here writes to the working tree. Every mutation runs in a temp copy.

Exit codes: 0 every planted defect was caught
            1 at least one mutation went unnoticed (a guard does not work)
            2 could not run
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL = "experiments/70-period-model.py"
GUARDS = "experiments/61-period-model-guards.py"
RENDER = "experiments/80-render-catalogue.py"
PROBE = "experiments/51-billing-posture-probe.py"

# Each mutation is (name, file, old, new, what a correct guard must notice).
MUTATIONS = [
    (
        "console table sorted on the credit-adjusted price",
        MODEL,
        '            sel.sort(key=lambda r: (\n'
        '                0.0 if r["shapes"][shape_name]["periods"][key].get("allowance_source")\n'
        '                else r["shapes"][shape_name]["periods"][key]["billed_month_no_credit"]))',
        '            sel.sort(key=lambda r: r["shapes"][shape_name]["periods"][key]["billed_month_with_credit"])',
        "61 GUARD F reports Run Cloud at rank 1 instead of the cheapest paid row",
    ),
    (
        "keep_basis read from the leaked loop variable",
        MODEL,
        '            keep_basis = c["keep_basis"]\n',
        '            pass  # MUTATED back to the leaked loop variable\n',
        "61 GUARD H names aws-lambda as carrying another mode's basis",
    ),
    (
        "per-request test matches note text again",
        MODEL,
        'PER_REQUEST_NOTE_TOKENS = ("per request", "per invocation", "per 1 ms",\n'
        '                           "per millisecond", "per invocation", "invocation",\n'
        '                           "per build", "per browser created")',
        'PER_REQUEST_NOTE_TOKENS = ("per request", "requests", "per invocation", "per 1 ms",\n'
        '                           "per millisecond", "per ms", "gb-second", "gb-s",\n'
        '                           "invocation")',
        "61 GUARD G reports Lizard and CreateOS as wrongly excluded",
    ),
    (
        "guard suite ROOT hardcoded to one checkout path",
        GUARDS,
        "ROOT = os.environ.get('PELI_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
        "ROOT = '/workspace/peli-cloud'",
        "61 exits 2 with 'could not run', not a bare FileNotFoundError",
    ),
    (
        "the advertised lizard size ignored again",
        MODEL,
        '        for a in advertised_sizes(pid, m.get("key")):',
        '        for a in []:  # MUTATED: the vendor\'s advertised size is ignored',
        "61 GUARD I reports lizard back at $5.40/month with no ADVERTISED marker",
    ),
    (
        "table C loses the dispute marker",
        RENDER,
        '        if "[ADVERTISED" in (s.get("how") or ""):\n            nm += " **(disputed)**"',
        '        if False:  # MUTATED: table C loses the dispute marker\n            nm += " **(disputed)**"',
        "61 GUARD I reports table C row 2 unmarked",
    ),
    (
        "the footnote explaining the dispute is removed",
        RENDER,
        '    if any("[ADVERTISED" in ((p["shapes"].get("agent") or p["shapes"].get("tiny")\n'
        '                              or p["shapes"].get("devbox") or {}).get("how") or "")\n'
        '           for p in ranked):',
        '    if False:  # MUTATED: the dispute footnote is gone',
        "61 GUARD I reports the footnote missing from table C",
    ),
    (
        "the README's hand-typed counts go stale again",
        "README.md",
        "**81 providers** publish a one-time",
        "**79 providers** publish a one-time",
        "61 GUARD J reports the one-time count as 81 and fails",
    ),
    (
        "a monthly rent is multiplied by hours again",
        MODEL,
        '        cap = s.get("month_cap")\n'
        '        if isinstance(cap, (int, float)) and cap > 0 and abs(s["hour"] - cap) < 1e-9:',
        '        cap = None  # MUTATED: the monthly-rent signal is ignored\n'
        '        if False:',
        "61 GUARD K reports hostinger-vps back at $17,632.80/month",
    ),
    (
        "the free allowance is ignored again",
        MODEL,
        '    for unit, rate_field in ALLOWANCE_UNITS.items():\n        rate = rates.get(unit)',
        '    for unit, rate_field in []:  # MUTATED: no unit is priced\n        rate = rates.get(unit)',
        "61 GUARD M reports oracle at $7.80 instead of $0.00",
    ),
    (
        "the allowance is applied to the wrong mode",
        MODEL,
        '            if a["provider"] == pid and a["mode"] == mode_key]',
        '            if a["provider"] == pid]  # MUTATED: scoped to no single SKU',
        "61 GUARD M reports the allowance leaking onto oracle\'s non-A1 modes",
    ),
    (
        "the keep rate stops affecting any number again",
        MODEL,
        '                "hold_month": round(c["hourly"] * billed_held_day * DAYS_PER_MONTH, 4),',
        '                "hold_month": round(c["hourly"] * hours_per_day * DAYS_PER_MONTH, 4),',
        "61 GUARD N reports the held figure identical to the duty cycle",
    ),
    (
        "the model stops reading the first-party probe",
        MODEL,
        '    for k in KEEP_RATES_FIRSTPARTY:\n        if k["provider"] == pid:\n            return [k]\n    return _probed_keep(pid)',
        '    for k in KEEP_RATES_FIRSTPARTY:\n        if k["provider"] == pid:\n            return [k]\n    return []  # MUTATED: the probe is ignored',
        "61 GUARD O reports 0 probed rows in the model",
    ),
    (
        "the probe's self-test is disabled",
        "experiments/51-billing-posture-probe.py",
        "    st_fail = selftest()",
        "    st_fail = []  # MUTATED: the known-answer cases are not run",
        "61 GUARD O reports the probe's self-test as not passing",
    ),
    (
        "a degraded probe run overwrites a good artefact",
        "experiments/51-billing-posture-probe.py",
        "        if _got < _had:",
        "        if False:  # MUTATED: a worse run may overwrite a better one",
        "51 writes a lower-yield artefact over a higher-yield one",
    ),
    (
        "the stripper discards JSON-LD pricing blocks",
        PROBE,
        "    t = re.sub(r'<script[^>]*type\\s*=\\s*[\"\\']application/ld\\+json[\"\\'][^>]*>(.*?)</script>',\n               _keep_jsonld, body, flags=re.S | re.I)",
        "    t = body  # MUTATED: JSON-LD is not extracted, so the script is dropped",
        "51's self-test reports that stripped text has no price where one exists",
    ),
    (
        "the keep rate is applied to the duty cycle, billing idle time",
        MODEL,
        '                held_h = hours_per_day\n                compute_day = c["hourly"] * held_h',
        '                held_h = hours_per_day\n                keep_used = keep if keep is not None else 1.0\n                compute_day = c["hourly"] * held_h * keep_used  # MUTATED',
        "61 GUARD N reports namespace at $0.00 for a suspending provider",
    ),
]


def main():
    if not os.path.isfile(os.path.join(ROOT, MODEL)):
        print("could not run: no peli-cloud tree at %s" % ROOT, file=sys.stderr)
        return 2

    # Control: the unmutated tree must pass, or nothing below means anything.
    base = subprocess.run([sys.executable, GUARDS], cwd=ROOT,
                          capture_output=True, text=True)
    print("== conditions ==")
    print("tree     : %s" % ROOT)
    print("mutations: %d, each run in a throwaway copy" % len(MUTATIONS))
    print("control  : unmutated 61 must exit 0 before any mutation means anything")
    print()
    print("CONTROL: unmutated tree")
    print("  %-4s 61 passes on the clean tree | exit=%d" %
          ("ok" if base.returncode == 0 else "FAIL", base.returncode))
    if base.returncode != 0:
        print(base.stdout[-1500:])
        print(base.stderr[-500:])
        print("CONTROL FAILED: the guards already fail before any mutation, so a "
              "mutation being caught proves nothing.")
        return 1
    print()

    failures = []
    for name, relpath, old, new, expectation in MUTATIONS:
        tmp = tempfile.mkdtemp(prefix="peli-mut-")
        tree = os.path.join(tmp, "peli-cloud")
        try:
            # Only the tracked instrument is needed, and the references it
            # reads, so copy the tree without .git to keep it quick.
            shutil.copytree(ROOT, tree, ignore=shutil.ignore_patterns(".git"),
                            symlinks=True)
            target = os.path.join(tree, relpath)
            with open(target, encoding="utf-8") as fh:
                src = fh.read()
            if old not in src:
                print("  %-4s could not plant: anchor not found in %s" %
                      ("FAIL", relpath))
                failures.append("%s (anchor missing)" % name)
                continue
            with open(target, "w", encoding="utf-8") as fh:
                fh.write(src.replace(old, new, 1))

            # Re-price, because two of the four mutations only show up in the
            # generated artefact rather than in the guard's own assertions.
            model = subprocess.run([sys.executable, MODEL], cwd=tree,
                                   capture_output=True, text=True)
            if model.returncode != 0:
                print("  %-4s %s | the mutated model did not run at all" %
                      ("FAIL", name))
                print(model.stderr[-400:])
                failures.append(name)
                continue
            # A mutation in the probe has to be exercised too, or it is never run.
            # The probe needs the model, and the model needs the probe, so the
            # order is model, probe, model again: the second model run is the one
            # that would pick up a changed probe artefact.
            probe = subprocess.run([sys.executable, PROBE], cwd=tree,
                                   capture_output=True, text=True)
            if probe.returncode != 0:
                print("  %-4s %s | the mutated probe refused to publish (exit %d)"
                      % ("ok", name, probe.returncode))
                print("       caught by: 51 exited %d rather than writing a worse"
                      % probe.returncode)
                print("                 artefact, and %s" % relpath)
                print("       expected : %s" % expectation)
                if "51" in expectation or "probe" in name:
                    continue
            subprocess.run([sys.executable, MODEL], cwd=tree,
                           capture_output=True, text=True)
            run = subprocess.run([sys.executable, GUARDS], cwd=tree,
                                 capture_output=True, text=True)
            caught = run.returncode != 0 or probe.returncode != 0
            detail = "exit=%d" % run.returncode
            fails = [l.strip() for l in run.stdout.split("\n") if "FAIL" in l]
            if fails:
                detail = "%d failing assertion(s), first: %s" % (
                    len(fails), fails[0][:96])
            print("  %-4s %s" % ("ok" if caught else "FAIL", name))
            print("       caught by: %s" % detail)
            print("       expected : %s" % expectation)
            if not caught:
                failures.append(name)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print("MUTATIONS THAT WENT UNNOTICED (%d): %s" %
              (len(failures), "; ".join(failures)))
        print("A guard that does not catch its own defect is not a guard.")
        return 1
    print("all %d planted defects were caught by 61-period-model-guards.py" %
          len(MUTATIONS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
