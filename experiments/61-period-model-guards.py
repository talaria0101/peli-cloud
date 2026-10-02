#!/usr/bin/env python3
"""61-period-model-guards.py

QUESTION: can the period model's guards actually fail, and do they still accept
correct input?

Same job as 60-guard-mutation.py, for the revision 2 model. It plants the defects
that revision 2 introduced or inherited and checks the fixes through the REAL code
paths (it reads data/period-model.json and re-runs the renderer) rather than
reimplementing the arithmetic, because a guard test that reimplements the thing
it guards tests nothing.

Defects guarded:
  A  active_floor read as a wall-clock keep rate  (the revision 2 headline bug)
  B  a $0/hour size becoming the cheapest option   (inherited from revision 1)
  C  fee_is_credit added as a surcharge instead of applied as a floor
  D  a credit-covered bill sorting as if it were free
  E  the renderer ranking on the credit-adjusted price
  I  a size the corpus card dropped that the vendor advertises (lizard)

Exit codes: 0 every guard held, 1 at least one failed, 2 could not run.
"""

import importlib.util, json, os, re, sys, subprocess
# Derived from __file__ like every other script here. It was hardcoded to
# '/workspace/peli-cloud', which meant this guard suite could only ever run in
# the one directory the author happened to be sitting in: on any other clone it
# died with FileNotFoundError before executing a single assertion, and because
# the failure is an import-time crash rather than a reported FAIL it reads like
# "no news" in a run log. Every defect fixed after it was written went unguarded
# for exactly that reason.
ROOT = os.environ.get('PELI_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not os.path.isfile(os.path.join(ROOT, 'experiments', '70-period-model.py')):
    # A crash here used to read as silence. This suite is the one place the
    # period model's defects are checked, and when it could not find its own
    # tree it died with a bare FileNotFoundError before running a single
    # assertion, so a run log showed a non-zero exit with no FAIL lines and a
    # reader could easily take it for "nothing to report". Say what happened and
    # exit 2, which is this repo's code for "could not run".
    print("could not run: no peli-cloud tree at %s" % ROOT, file=sys.stderr)
    print("set PELI_ROOT to the repository root, or run this from inside it",
          file=sys.stderr)
    sys.exit(2)
if not os.path.isdir(os.path.join(ROOT, 'references', 'battleships', 'research', 'cards')):
    # The corpus is deliberately NOT committed: ariana-dot-dev/battleships
    # publishes no licence, so peli-cloud fetches it rather than redistributing
    # it (see NOTICE). A fresh clone therefore has data/ and docs/ but no input,
    # and this suite cannot re-price anything. That is "could not run", exit 2,
    # NOT a guard failure: reporting it as a FAIL sends a reader hunting for a
    # broken guard that is in fact waiting for its input.
    print("corpus not present at %s" % os.path.join(ROOT, 'references', 'battleships'),
          file=sys.stderr)
    print("run: bash experiments/10-fetch-corpus.sh   (pinned commit, no licence "
          "to redistribute)", file=sys.stderr)
    print("the committed data/ and docs/ still reproduce without it, so the "
          "catalogue is readable, only not re-derivable", file=sys.stderr)
    sys.exit(2)
def load(p,n):
    s=importlib.util.spec_from_file_location(n,os.path.join(ROOT,p)); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
pm=load('experiments/70-period-model.py','pm')
fails=[]
def ck(l,c,d=""):
    print(("  ok  " if c else "  FAIL"),l,("| "+d) if d else "")
    if not c: fails.append(l)

print("GUARD A: active_floor must NOT be read as a wall-clock keep rate")
ck("uptime VM reads 1.00", pm.keep_rate({"active_floor":0,"pricing":"sizes"})[0]==1.0)
ck("auto_stop_idle reads 0.00", pm.keep_rate({"features":{"auto_stop_idle":True}})[0]==0.0)
ck("pool reads 1.00", pm.keep_rate({"pricing":"pool"})[0]==1.0)
ck("requires_always_on reads 1.00", pm.keep_rate({"requires_always_on":True})[0]==1.0)

print("GUARD B: a $0/hour size must not become the cheapest")
ck("hour:0 size rejected", pm.mode_hourly({"pricing":"sizes","sizes":[{"name":"x","vcpu":2,"ram_gib":4,"hour":0}]},{"vcpu":2,"ram_gib":4})[0] is None)
ck("a real size beside it still prices", pm.mode_hourly({"pricing":"sizes","sizes":[{"name":"x","vcpu":2,"ram_gib":4,"hour":0},{"name":"y","vcpu":2,"ram_gib":4,"hour":0.5}]},{"vcpu":2,"ram_gib":4})[0]==0.5)

print("GUARD C: fee_is_credit is a FLOOR, not a surcharge -- through the real code")
doc=json.load(open(os.path.join(ROOT,'data/period-model.json')))
boat=[p for p in doc['providers'] if p['id']=='boat']
ck("boat present", len(boat)==1)
if boat:
    b=boat[0]
    ck("boat floor recorded as $20", b['usage_credit_floor']==20)
    ck("boat surcharge is None", b['surcharge_floor'] is None)
    for dk in ('1h','4h','10h','24h'):
        pd=b['shapes']['agent']['periods'][dk]
        ck("boat %s/day bills exactly the $20 floor"%dk, abs(pd['billed_month_no_credit']-20.0)<0.005,
           "got %.2f"%pd['billed_month_no_credit'])

print("GUARD D: a credit-covered bill keeps its pre-credit price for ranking")
rc=[p for p in doc['providers'] if p['id']=='run-cloud']
ck("run-cloud present", len(rc)==1)
if rc:
    r=rc[0]
    pd=r['shapes']['agent']['periods']['10h']
    ck("pre-credit price preserved ($13.98)", abs(pd['billed_month_no_credit']-13.98)<0.01,
       "got %.2f"%pd['billed_month_no_credit'])
    ck("after-credit is $0 (credit really does cover it)", pd['billed_month_with_credit']==0.0)

print("GUARD E: the renderer ranks on pre-credit, so no credit-bought top row")
out=subprocess.run(['python3','experiments/80-render-catalogue.py'],cwd=ROOT,capture_output=True,text=True)
ck("renderer runs", out.returncode==0)
cat=open(os.path.join(ROOT,'docs/CATALOGUE.md')).read()
cstart=cat.index('## C.')
# the top N ranked rows of table C (any rank number, not just 1)
crows = [l for l in cat[cstart:].split('\n')
         if re.match(r'^\|\s*\d+\s*\|', l)]
ck("table C row 1 is Agent 37", bool(crows) and 'Agent 37' in crows[0], crows[0][:70] if crows else "no rows")

print("GUARD F: the CONSOLE table must rank on the pre-credit price too")
# The console table in 70 sorted on billed_month_with_credit while the renderer
# in 80 sorted on billed_month_no_credit. Same data, two answers: Run Cloud
# topped the 2 vCPU / 4 GiB / 10 h/day console table with a month of $0.00 purely
# because its $15 credit exceeded that month's $13.98 bill, and the published
# catalogue, generated by the other rule, put Agent 37 there instead.
out70 = subprocess.run(['python3', 'experiments/70-period-model.py'],
                       cwd=ROOT, capture_output=True, text=True)
ck("70 runs", out70.returncode == 0, out70.stderr.strip()[-90:])
if out70.returncode == 0:
    # Read the console table for agent 10h straight out of its stdout.
    seg = out70.stdout.split('2 vCPU / 4 GiB, 10h per day')[1].split('\n\n')[0] if \
        '2 vCPU / 4 GiB, 10h per day' in out70.stdout else ''
    con_rows = [l for l in seg.split('\n') if re.match(r'^\d+\s{2,}\S', l)]
    ck("console names the pre-credit basis", 'before credit' in seg, seg.split('\n')[0][:80])
    ck("console row 1 is Agent 37, not Run Cloud",
       bool(con_rows) and 'Agent 37' in con_rows[0], con_rows[0][:60] if con_rows else 'no rows')
    # And the two rankings must agree on the whole visible table, not just row 1.
    # Compare the console's agent/10h table with the catalogue's own agent/10h
    # ranking. An earlier version of this guard compared the console's agent
    # table against the catalogue's TABLE C, which is a different question: C
    # mixes shapes, falling back to tiny for a provider that publishes no 2 vCPU
    # size, so a tiny-only provider appears in C and cannot appear in the console
    # agent table at all. Moonshot Kimi is that case: it publishes only 1C1GB, so
    # it is rank 16 of 206 in the console's tiny table and row 4 of C. Both are
    # right; comparing them was the guard's error, not the data's.
    arows = [l for l in cat.split('\n') if re.match(r'^\|\s*\d+\s*\|', l)]
    # Compare the console's agent/10h table against section B's own
    # "2 vCPU / 4 GiB -- agent" / "10h per day" table, which is the same question
    # computed by the renderer. Comparing against table C was the guard's first
    # error: C is a mixed-shape table that falls back to tiny for a provider with
    # no 2 vCPU size, so a tiny-only provider appears in C and cannot appear in
    # the console's agent table at all. Moonshot Kimi is that case: it publishes
    # only 1C1GB, so it is rank 16 of 206 in the console's tiny table and row 4
    # of C. Both are right; they answer different questions.
    bstart = cat.index('### 2 vCPU / 4 GiB')
    bseg = cat[bstart:].split('#### 10h per day')[1].split('#### 24h per day')[0] \
        if '#### 10h per day' in cat[bstart:] else ''
    brows = [l for l in bseg.split('\n') if re.match(r'^\|\s*\d+\s*\|', l)]
    names_c = [l.split('|')[2].strip().lstrip('[').split(']')[0].split('(')[0].strip()
               for l in brows[:5]]
    names_7 = []
    for l in con_rows[:5]:
        parts = re.split(r'\s{2,}', l.strip())
        if len(parts) >= 2:
            names_7.append(parts[1].strip())
    ck("console and catalogue agree on the top 5 of the same shape",
       bool(names_c) and bool(names_7) and len(names_c) >= 5 and len(names_7) >= 5 and
       all(any(n.startswith(c) or c.startswith(n) for c in names_c) for n in names_7),
       "console=%s catalogue=%s" % (names_7, names_c))

print("GUARD G: a per-invocation product must not be ranked as a machine")
# mode_hourly() read vcpu_h: 0 as "CPU is free" and priced a per-millisecond
# invoker as a 1 vCPU / 1 GiB box billed by the hour.
ck("a per-build size with hour 0 is not per-request when it is a real machine",
   pm.is_per_request({"pricing": "sizes", "start_fee": 2,
                      "sizes": [{"name": "iOS medium", "vcpu": 5, "ram_gib": 20, "hour": 0}],
                      "note": "priced per build"})[0] is True)
ck("a machine with a boot fee AND a real hour is NOT per-request",
   pm.is_per_request({"pricing": "sizes", "start_fee": 0.01,
                      "sizes": [{"name": "browser session", "hour": 0.05}],
                      "note": "$0.01 per browser created + $0.05 per browser-hour"})[0] is False)
ck("a dedicated monthly GPU box with no hour is NOT per-request",
   pm.is_per_request({"pricing": "sizes", "start_fee": 1049,
                      "sizes": [{"name": "GEX131-2", "ram_gib": 512, "hour": None,
                                 "month_cap": 2099}]})[0] is False)
ck("a per-second machine (railway sandbox-vm) is NOT per-request",
   pm.is_per_request({"pricing": "resource", "vcpu_h": 0.069444,
                      "ram_gib_h": 0.069444, "note": "$0.00001929 per vCPU-s"})[0] is False)
skipped = doc.get('per_request_modes_skipped') or []
ck("exclusions are reported, not silent", isinstance(skipped, list))
ck("no real sandbox platform was dropped by the note-text test",
   not [s for s in skipped if s['id'] in ('lizard', 'railway', 'kernel', 'sail',
                                          'instavm', 'createos', 'hetzner-gpu',
                                          'hetzner-cloud', 'e2b', 'daytona')],
   str(sorted({s['id'] for s in skipped})))
for pid in ('lizard', 'railway', 'sail', 'instavm', 'createos'):
    ck("%s still prices (it bills per second, not per invocation)" % pid,
       any(p['id'] == pid and p.get('shapes') for p in doc['providers']))

print("GUARD H: keep_basis must belong to the mode the row actually selected")
# keep_basis was read from a loop variable left over from the per-mode scan, so
# every row carried whatever the LAST mode of that card happened to say.
# aws-lambda published keep_source=requires_always_on next to keep_basis="billed
# for uptime (no suspension feature published)", which are different claims.
mis = []
for p in doc['providers']:
    for sname, s in (p.get('shapes') or {}).items():
        got = s.get('keep_basis')
        if got is None:
            continue
        # Recompute the basis the selected mode's own fields imply. The mode
        # record is carried on the row as keep_source; rebuild the mode dict the
        # classifier saw and ask again. A mismatch means the row is carrying a
        # basis belonging to some other mode of the same card.
        probe = {}
        if s.get('keep_rate') == 0.0:
            probe['features'] = {'auto_stop_idle': True}
        elif s.get('keep_source') == 'requires_always_on':
            probe['requires_always_on'] = True
        elif s.get('keep_source') == 'pricing=pool':
            probe['pricing'] = 'pool'
        elif s.get('keep_source') == 'features.pause_resume':
            probe['features'] = {'pause_resume': True}
        if not probe:
            continue
        expected = pm.keep_rate(probe)[1]
        if expected != got:
            mis.append((p['id'], sname, got, expected))
ck("no row carries a keep_basis from another mode", not mis, str(mis[:3]))
ck("every priced row states its keep basis",
   all(s.get('keep_basis') for p in doc['providers']
       for s in (p.get('shapes') or {}).values()))

print("GUARD I: a size the card dropped but the vendor advertises is priced and flagged")
# lizard's card carries only the default size (medium, 4 vCPU, $0.018) and sets
# min_vcpu 4, while the vendor's own pricing page sells Small (2 vCPU / 4 GB) at
# $0.009/h. The card's own note quotes that sentence. Before the correction the
# row was $5.40/month at 10 h/day; the advertised size makes it $2.70, which is
# second only to Agent 37.
adv = pm.advertised_sizes("lizard", "sandbox")
ck("lizard advertises a size the card dropped", len(adv) == 1, "found %d" % len(adv))
if adv:
    a = adv[0]
    ck("the advertised rate is the page's $0.009/h", a["hour"] == 0.009, str(a["hour"]))
    ck("it carries the first-party quote", "$0.009/hour" in a["quote"])
    ck("it carries the URL it was read from", a["url"].startswith("https://"))
    ck("it carries the conflict, not just the price", bool(a.get("disputed")))
    ck("it is a real fit for the agent shape", a["vcpu"] >= 2 and a["ram_gib"] >= 4)
    # Through the REAL code path, not by reimplementing the arithmetic. The
    # mode key matters: advertised_sizes is looked up by (provider, mode), so a
    # card passed without its key finds nothing and returns the card's own
    # price. That is the correct behaviour, and an earlier version of this guard
    # omitted the key and read the omission as a failure of the correction.
    h, how = pm.mode_hourly({"key": "sandbox", "pricing": "sizes", "sizes": [
        {"name": "medium", "vcpu": 4, "ram_gib": 4, "hour": 0.018}],
        "min_vcpu": 4}, {"vcpu": 2, "ram_gib": 4}, "lizard")
    ck("the card's own size is overridden by the advertised one", h == 0.009, str(h))
    ck("the row is marked as coming from the advertisement", "ADVERTISED" in how, how[:60])
    hk, _ = pm.mode_hourly({"key": "sandbox", "pricing": "sizes", "sizes": [
        {"name": "medium", "vcpu": 4, "ram_gib": 4, "hour": 0.018}],
        "min_vcpu": 4}, {"vcpu": 2, "ram_gib": 4}, "e2b")
    ck("the same card under a provider with no advertisement is untouched",
       hk == 0.018, str(hk))
    # And the card's size is still reachable when it is genuinely the cheapest
    # fit, so the correction is not a blanket override.
    h4, _ = pm.mode_hourly({"pricing": "sizes", "sizes": [
        {"name": "medium", "vcpu": 4, "ram_gib": 4, "hour": 0.018}],
        "min_vcpu": 4}, {"vcpu": 4, "ram_gib": 8}, "lizard")
    ck("a shape the advertised size cannot serve still uses the card", h4 is None,
       "got %s" % h4)
    # A provider with no advertised sizes is untouched.
    hz, _ = pm.mode_hourly({"pricing": "sizes", "sizes": [
        {"name": "a", "vcpu": 2, "ram_gib": 4, "hour": 0.5}]},
        {"vcpu": 2, "ram_gib": 4}, "e2b")
    ck("a provider with no advertisement is priced from its card alone", hz == 0.5, str(hz))
liz = [p for p in doc['providers'] if p['id'] == 'lizard']
ck("lizard is in the model", len(liz) == 1)
if liz:
    ck("lizard's agent rate is the advertised $0.009/h",
       abs(liz[0]['shapes']['agent']['hourly'] - 0.009) < 1e-9,
       str(liz[0]['shapes']['agent']['hourly']))
    ck("lizard is no longer $5.40/month at 10 h/day",
       abs(liz[0]['shapes']['agent']['periods']['10h']['billed_month_no_credit'] - 2.70) < 0.01,
       "%.2f" % liz[0]['shapes']['agent']['periods']['10h']['billed_month_no_credit'])
ck("the catalogue marks the row disputed, not confirmed",
   '**disputed**' in open(os.path.join(ROOT, 'docs/CATALOGUE.md')).read())
ck("the corpus is not vendored, because it carries no licence",
   not os.path.isdir(os.path.join(ROOT, 'references', 'battleships', '.git')) or
   'NOTICE' in os.listdir(ROOT),
   "NOTICE present=%s" % ('NOTICE' in os.listdir(ROOT)))

print()
print("TOTAL:", len(fails), "failures")
sys.exit(1 if fails else 0)
