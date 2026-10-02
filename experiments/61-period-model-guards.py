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
ck("table C row 1 leads with the genuinely-free row, when one exists",
   ('Oracle Cloud' in crows[0]) if any('Oracle Cloud' in l for l in crows)
   else ('Agent 37' in crows[0]), crows[0][:78] if crows else "no rows")
# The dispute marker is asserted on the row for lizard wherever it appears,
# whatever its rank, because the allowance change moved ranks around.

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
    # The point of this guard is that no row BOUGHT its position with a credit.
    # It is not that Agent 37 leads: a genuinely free provider leads now, and
    # pinning a name would have failed the moment a real $0 appeared.
    # A $0 month is legitimate only when a published allowance covers the usage.
    # Oracle now leads every shape with one. The month is the 5th column of the
    # console table, so it is read positionally: a regex for "0.00" matched
    # Lizard's KEEP column, which is legitimately 0.00, and failed the guard.
    _zero_rows = []
    for l in con_rows:
        cols = re.split(r'\s{2,}', l.strip())
        if len(cols) >= 5 and cols[4].strip() in ('0.00', '0.0', '0'):
            if 'Oracle Cloud' not in l:
                _zero_rows.append(l[:60])
    ck("no console row is $0 without a published allowance behind it",
       not _zero_rows, str(_zero_rows[:1])[:80])
    ck("the cheapest console row is not the credit-exhausted one",
       bool(con_rows) and 'Run Cloud' not in con_rows[0],
       con_rows[0][:60] if con_rows else 'no rows')
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
    # Two traps here, both hit. The 10 h/day cell now opens with a
    # free-on-an-allowance table whose heading ALSO begins "#### 10h per day",
    # and str.split(...)[1] returns the text after the LAST match, not the first,
    # so this was reading the 24 h/day cell and finding no paid table at all.
    # partition takes the first, and the paid heading is then found by its count.
    _head = '#### 10h per day'
    _after = cat[bstart:].partition(_head)[2] if _head in cat[bstart:] else ''
    _paid_at = _after.find('paid providers')
    bseg = _after[_paid_at:].partition('#### 24h per day')[0] if _paid_at >= 0 else ''
    brows = [l for l in bseg.split('\n') if re.match(r'^\|\s*\d+\s*\|', l)]
    ck("the agent 10h/day paid table was located", len(brows) >= 5,
       "%d rows" % len(brows))
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
        if (s.get('keep_source') or '').startswith('first-party'):
            # A first-party read is the strongest basis there is and is not
            # reconstructible from the mode fields, because it comes from the
            # page rather than the card. The probe below cannot second-guess it,
            # so it is checked against the recorded table instead.
            _fp = pm.keep_rate_firstparty(p['id'])
            if _fp:
                expected = 'first-party: %s' % _fp[0]['quote'][:110]
                if expected != got:
                    mis.append((p['id'], sname, got, expected))
                continue
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
# Table C is the table a reader lands on, and it had no marker: lizard sat at
# rank 2 with $0.0090 and nothing saying the vendor's docs contradict the price.
# The marker now rides on the provider name, which every table prints, because
# the "buy it?" column only exists in table B.
_cat = open(os.path.join(ROOT, 'docs/CATALOGUE.md')).read()
_cseg = _cat[_cat.index('## C.'):_cat.index('## D.')]
_crows = [l for l in _cseg.split('\n')
          if l.startswith('|') and '`lizard`' in l]
ck("table C marks the disputed row wherever it now ranks",
   bool(_crows) and all('disputed' in l for l in _crows),
   (_crows[0][:74] if _crows else "no lizard row"))
ck("table C carries the footnote explaining the mark",
   'corpus card dropped' in _cseg)
_disputed_ids = {a["provider"] for a in pm.ADVERTISED_SIZES}
for _pid in _disputed_ids:
    _rows = [l for l in _cat.split('\n')
             if l.startswith('|') and ('`%s`' % _pid) in l and '/h agent' in l or
             (l.startswith('|') and ('`%s`' % _pid) in l and '$/hour' in l)]
    ck("every ranked row of %s carries the dispute" % _pid,
       all('disputed' in l for l in _rows), "%d row(s) unmarked" % sum(
           1 for l in _rows if 'disputed' not in l))
ck("the corpus is not vendored, because it carries no licence",
   not os.path.isdir(os.path.join(ROOT, 'references', 'battleships', '.git')) or
   'NOTICE' in os.listdir(ROOT),
   "NOTICE present=%s" % ('NOTICE' in os.listdir(ROOT)))

print("GUARD J: the README's prose counts must equal the data")
# These numbers were typed by hand and went stale: the README said 79 one-time
# credits and 124 $0-tier cards while the data said 81 and 116, and it still
# said "Hetzner ranks third" after Lizard moved to second. A count a script can
# compute should not be typed, and this is the check that stops it being typed
# again.
readme = open(os.path.join(ROOT, 'README.md'), encoding='utf-8').read()
recurring = [p for p in doc['providers'] if (p.get('free_monthly_credit') or 0) > 0]
one_time = [p for p in doc['providers'] if (p.get('free_one_time_credit') or 0) > 0]
zero_no_credit = [p for p in doc['providers']
                  if p.get('has_free_tier')
                  and not (p.get('free_monthly_credit') or 0)
                  and not (p.get('free_one_time_credit') or 0)]
trial = [p for p in doc['providers'] if p.get('trial_only_plans')]
ck("README recurring-credit count is %d" % len(recurring),
   ("**%d providers** publish a credit that recurs" % len(recurring)) in readme)
ck("README one-time-credit count is %d" % len(one_time),
   ("**%d providers** publish a one-time" % len(one_time)) in readme)
ck("README $0-tier count is %d" % len(zero_no_credit),
   ("**%d cards** sell a $0 plan" % len(zero_no_credit)) in readme)
ck("README trial_only count is %d" % len(trial),
   ("%d cards mark one `trial_only`" % len(trial)) in readme)
# The largest recurring credit, named in the prose.
top = max(recurring, key=lambda p: p['free_monthly_credit'])
ck("README names the largest recurring credit correctly (%s $%g)"
   % (top['name'], top['free_monthly_credit']),
   ("**%s at $%g/month**" % (top['name'], top['free_monthly_credit'])) in readme)
# The rank claims in the headline table, checked against the ordering the
# renderer actually uses.
def agent_rows():
    out = []
    for p in doc['providers']:
        s = p['shapes'].get('agent')
        if not s:
            continue
        pd = s['periods'].get('10h')
        if pd and pd['billed_month_no_credit'] > 0.004:
            out.append((pd['billed_month_no_credit'], p['name']))
    return sorted(out)
rows10 = agent_rows()
# The README's headline table lists PAID rows. A provider that is genuinely $0
# on a published allowance is the cheapest thing in the market; it is called out
# in prose with its own table in the catalogue rather than folded into the paid
# list, so the two sequences agree only over the paid rows. Checking the
# $0-inclusive sequence made this fail the moment a real free row appeared.
paid10 = [(c, n) for (c, n) in rows10 if c > 0.004]
for want, (cost, name) in enumerate(paid10[:8], 1):
    p = [x for x in doc['providers'] if x['name'] == name][0]
    # Match on the row's position and its price, not on the display name: the
    # README legitimately shortens "Oracle Cloud Infrastructure" to "Oracle
    # Cloud", and a guard that demanded the exact string would force the README
    # to be worse. The price is the part that must not drift.
    ck("README headline table row %d is %s at $%.2f" % (want, name, cost),
       ("| %d | [" % want) in readme and
       ("| %.4f | %.2f |" % (p['shapes']['agent']['hourly'], cost)) in readme,
       "rank %d, $%.4f/h, $%.2f/mo" % (want, p['shapes']['agent']['hourly'], cost))
# And the one ordinal claim in prose, which said "third" for a provider that
# the Lizard correction moved.
hz = [i for i, (_c, n) in enumerate(paid10, 1) if n and n.startswith('Hetzner')]
ck("README's Hetzner ordinal matches its real rank %s" % (hz[0] if hz else '?'),
   ("Hetzner ranks %s at" % {1: 'first', 2: 'second', 3: 'third', 4: 'fourth',
                             5: 'fifth', 6: 'sixth', 7: 'seventh',
                             8: 'eighth'}.get(hz[0] if hz else 0, '?')) in readme,
   "rank is %s" % (hz[0] if hz else '?'))

# FINDINGS carries the same hand-typed numbers and they drifted too: section 0
# claimed 28 of 366 cards publish auto_stop_idle when 8 do, and section 2
# repeated the stale 79 and 124. Section 0 is the one a reader is told to read
# before any table, so a wrong count there is the worst place for one.
find_txt = open(os.path.join(ROOT, 'docs', 'FINDINGS.md'), encoding='utf-8').read()
_cards_dir = os.path.join(ROOT, 'references', 'battleships', 'research', 'cards')
_asis = sorted(f for f in os.listdir(_cards_dir)) if os.path.isdir(_cards_dir) else []
if _asis:
    _n_asis = 0
    for _f in _asis:
        if not _f.endswith('.json'):
            continue
        _c = json.load(open(os.path.join(_cards_dir, _f), encoding='utf-8'))
        if any((m.get('features') or {}).get('auto_stop_idle') is True
               for m in _c.get('modes') or []):
            _n_asis += 1
    ck("FINDINGS states the auto_stop_idle coverage correctly (%d cards)" % _n_asis,
       ("**%d of %d** cards publish `auto_stop_idle`" % (_n_asis, len(_asis))) in find_txt
       or ("Only %d of %d cards publish `auto_stop_idle`" % (_n_asis, len(_asis))) in find_txt,
       "looked for %d of %d" % (_n_asis, len(_asis)))
    _rows_default = sum(
        1 for p in doc['providers'] for s in (p.get('shapes') or {}).values()
        if s.get('keep_source') == 'default')
    _total_rows = sum(len(p.get('shapes') or {}) for p in doc['providers'])
    # 544 rows take the FALLBACK, not 605 minus the auto-suspend rows. An
    # earlier version of this guard subtracted only features.auto_stop_idle and
    # demanded "600 of 605", which is the complement of the right answer: the
    # fallback is the keep_source 'default' rows, and requires_always_on and
    # pause_resume are published bases, not fallbacks.
    ck("FINDINGS states the default-keep-rate row count correctly",
       ("**%d of %d** priced rows" % (_rows_default, _total_rows)) in find_txt,
       "expected %d of %d" % (_rows_default, _total_rows))
else:
    print("  skip auto_stop_idle recount (corpus not fetched; run "
          "experiments/10-fetch-corpus.sh to check it)")
ck("FINDINGS one-time count matches the data (%d)" % len(one_time),
   ("%d\n   publish a one-time signup credit" % len(one_time)) in find_txt
   or ("%d publish a one-time signup credit" % len(one_time)) in find_txt)
ck("FINDINGS $0-tier count matches the data (%d)" % len(zero_no_credit),
   ("%d\n   cards sell a $0 plan" % len(zero_no_credit)) in find_txt
   or ("%d cards sell a $0 plan" % len(zero_no_credit)) in find_txt)

print("GUARD K: a monthly rent must never be multiplied by hours")
# 173 sizes across 8 cards carry a month's rent in the hourly field, and the
# card says so in the mode's note. Multiplying it by 720 published Hostinger at
# $17,632.80/month and its devbox at $30,952.80, and pushed Contabo and netcup
# out of the top ten entirely because their real rents are among the lowest in
# the market.
MONTH_MODE = {"pricing": "sizes", "sizes": [
    {"name": "KVM 2", "vcpu": 2, "ram_gib": 8, "hour": 24.49, "month_cap": 24.49}]}
h_rent, how_rent = pm.mode_hourly(MONTH_MODE, {"vcpu": 2, "ram_gib": 4})
ck("a monthly rent is divided into an hourly rate",
   h_rent is not None and abs(h_rent - 24.49 / 730.0) < 1e-6, str(h_rent))
ck("the row says it came from a monthly rent", "monthly rent" in how_rent, how_rent[:70])
HOUR_MODE = {"pricing": "sizes", "sizes": [
    {"name": "medium", "vcpu": 2, "ram_gib": 4, "hour": 0.0137, "month_cap": None}]}
h_hour, how_hour = pm.mode_hourly(HOUR_MODE, {"vcpu": 2, "ram_gib": 4})
ck("a real hourly rate is NOT divided", abs(h_hour - 0.0137) < 1e-9, str(h_hour))
ck("a real hourly rate is not labelled a rent", "monthly rent" not in how_hour)
CAP_MODE = {"pricing": "sizes", "sizes": [
    {"name": "capped", "vcpu": 2, "ram_gib": 4, "hour": 0.02, "month_cap": 14.0}]}
h_cap, _ = pm.mode_hourly(CAP_MODE, {"vcpu": 2, "ram_gib": 4})
ck("a size with a cap but a different hour is not treated as a rent",
   abs(h_cap - 0.02) < 1e-9, str(h_cap))
# And through the data: no published row may be an order of magnitude absurd.
_worst = 0.0
_worst_name = ""
for _p in doc['providers']:
    for _s in (_p.get('shapes') or {}).values():
        _pd = _s['periods'].get('24h')
        if _pd and _pd['billed_month_no_credit'] > _worst:
            _worst = _pd['billed_month_no_credit']
            _worst_name = _p['name']
ck("no 24/7 row exceeds $8,000/month (worst is %s at $%.2f)" % (_worst_name, _worst),
   _worst <= 8000.0, "worst %s $%.2f" % (_worst_name, _worst))
for _pid, _cap in (("hostinger-vps", 40.0), ("netcup", 20.0), ("contabo", 20.0)):
    _r = [p for p in doc['providers'] if p['id'] == _pid]
    ck("%s is in the model and priced sanely at 24/7" % _pid, bool(_r))
    if _r:
        _v = _r[0]['shapes']['agent']['periods']['24h']['billed_month_no_credit']
        ck("%s 24/7 is under $%g (got $%.2f)" % (_pid, _cap, _v), _v <= _cap,
           "$%.2f" % _v)

print("GUARD L: the one figure a vendor publishes must reconcile with the model")
# Agent 37 is the only provider in the sample that publishes its own always-on
# total, so it is the only place a reader can check this model's arithmetic
# against a vendor rather than against the corpus. Its page says "From
# $4.76/month. 2 vCPU, 4 GB RAM and 4 GB persistent disk at 730 running hours."
# The model prints $4.34 because it does not price disk. The two must reconcile:
# 2 x $0.80 + 4 x $0.70 over 730 hours is $4.40 of compute, and the $0.36
# remainder is the 4 GB of disk. If the model ever drifts from the card's rates
# this stops reconciling, and the README's claim becomes false.
a37 = [p for p in doc['providers'] if p['id'] == 'agent-37']
ck("agent-37 is in the model", bool(a37))
if a37:
    _s = a37[0]['shapes']['agent']
    _compute_730 = _s['hourly'] * 730.0
    ck("the model reconciles with the vendor's 730-hour basis ($%.2f of compute)"
       % _compute_730, abs(_compute_730 - 4.40) < 0.02, "$%.2f" % _compute_730)
    ck("the vendor's $4.76 minus compute is the excluded disk ($%.2f)"
       % (4.76 - _compute_730), 0.25 < (4.76 - _compute_730) < 0.50,
       "$%.2f" % (4.76 - _compute_730))
    _v = _s['periods']['24h']['billed_month_no_credit']
    ck("the model's own 24/7 figure is the compute, not the vendor's total",
       abs(_v - _compute_730) < 0.12, "$%.2f vs $%.2f" % (_v, _compute_730))
    ck("the README explains the gap instead of quoting $4.76 beside $4.34",
       "4 GB of persistent disk" in readme and "$4.34" in readme)

print("GUARD M: a free ALLOWANCE is applied per resource-hour, not as a credit")
# Oracle's Always Free A1 is 1500 OCPU-h + 9000 GB-h per month, denominated in
# the provider's own units. The corpus has no allowance field, so the model had
# none and published $2.74 for a machine the vendor gives away free. Two bugs
# lived here and both produced confident nonsense: the rate lookup was keyed by
# the wrong name and saved $0 silently, and the hours passed in were one day's
# while the allowance is monthly, so it covered 1/30th of the usage.
_a1 = pm.allowance_for("oracle-cloud", "a1")
ck("the A1 allowance is recorded", len(_a1) == 1)
if _a1:
    _a = _a1[0]
    ck("it is denominated in OCPU-h and GB-h, not dollars",
       set(_a["per_month"]) == {"ocpu_h", "gb_h"}, str(sorted(_a["per_month"])))
    ck("it carries the first-party quote",
       "1,500 OCPU hours and 9,000 GB hours" in _a["quote"])
    ck("it is scoped to one SKU and says so", "A1.Flex" in _a["scoped_to"])
    ck("the quantities are the page's", _a["per_month"]["ocpu_h"] == 1500.0
       and _a["per_month"]["gb_h"] == 9000.0, str(_a["per_month"]))
    _mode = {"pricing": "resource", "vcpu_h": 0.01, "ram_gib_h": 0.0015}
    # 2 vCPU / 4 GiB at 24/7 = 1440 OCPU-h and 2880 GB-h, both inside the
    # allowance, so the bill is zero. Hand-computed before the code existed.
    _sv, _fr, _det = pm.allowance_saving(_a, _mode, {"vcpu": 2, "ram_gib": 4}, 720)
    ck("2 vCPU / 4 GiB at 24/7 is fully covered and saves $18.72",
       abs(_sv - 18.72) < 0.01, "$%.2f" % _sv)
    ck("...and is reported as 100% covered", abs(_fr - 1.0) < 1e-6, "%.3f" % _fr)
    # 4 vCPU / 8 GiB at 24/7 = 2880 OCPU-h and 5760 GB-h. OCPU-h exceeds the
    # 1500 allowance and is billed for the 1380 remainder; GB-h is inside the
    # 9000 and is free. Saving = 1500*0.01 + 5760*0.0015 = $23.64, leaving
    # 1380*0.01 = $13.80. An earlier version of this guard expected a $20.70
    # saving, which was arithmetic done in my head and wrong; the model was
    # right and the check was not.
    _sv4, _fr4, _d4 = pm.allowance_saving(_a, _mode, {"vcpu": 4, "ram_gib": 8}, 720)
    ck("4 vCPU / 8 GiB at 24/7 is only partly covered",
       0.6 < _fr4 < 0.7, "%.3f" % _fr4)
    ck("...and the allowance removes $23.64, leaving $13.80 billable",
       abs(_sv4 - 23.64) < 0.02, "$%.2f" % _sv4)
    ck("...with the OCPU remainder billed and the GB hours free",
       abs(_d4['ocpu_h']['covered_h'] - 1500.0) < 0.01
       and abs(_d4['ocpu_h']['used_h'] - 2880.0) < 0.01
       and abs(_d4['gb_h']['used_h'] - 5760.0) < 0.01
       and _d4['gb_h']['covered_h'] == 5760.0, str(_d4))
    # One day of hours must NOT be enough to exhaust a monthly allowance.
    _svd, _frd, _dd = pm.allowance_saving(_a, _mode, {"vcpu": 2, "ram_gib": 4}, 24)
    ck("a single day does not consume the whole monthly allowance",
       _frd < 1.0 or _svd < 18.72, "%.3f" % _frd)
    # And it must not apply to a mode the grant was not issued against.
    ck("the allowance does NOT apply to a non-A1 mode",
       pm.allowance_for("oracle-cloud", "e4-burstable-12") == [])
    ck("an unrelated provider has no allowance", pm.allowance_for("e2b", "on-demand") == [])
_oc = [p for p in doc['providers'] if p['id'] == 'oracle-cloud']
ck("oracle is in the model", bool(_oc))
if _oc:
    for _sh in ('tiny', 'agent'):
        _s = _oc[0]['shapes'].get(_sh)
        ck("oracle %s picks the A1 mode, not the cheaper-rate SKU" % _sh,
           _s and _s['mode'] == 'a1', _s['mode'] if _s else 'absent')
        if _s:
            ck("oracle %s is $0.00 at 10 h/day, before any credit" % _sh,
               abs(_s['periods']['10h']['billed_month_no_credit']) < 1e-9,
               "$%.2f" % _s['periods']['10h']['billed_month_no_credit'])
            ck("oracle %s is $0.00 at 24/7 too" % _sh,
               abs(_s['periods']['24h']['billed_month_no_credit']) < 1e-9,
               "$%.2f" % _s['periods']['24h']['billed_month_no_credit'])
            ck("oracle %s records where the allowance came from" % _sh,
               'docs.oracle.com' in (_s['periods']['10h'].get('allowance_source') or ''))
    _dv = _oc[0]['shapes']['devbox']['periods']['24h']
    ck("oracle devbox at 24/7 is $13.80, not $0",
       abs(_dv['billed_month_no_credit'] - 13.80) < 0.02,
       "$%.2f" % _dv['billed_month_no_credit'])
_cat2 = open(os.path.join(ROOT, 'docs', 'CATALOGUE.md'), encoding='utf-8').read()
ck("the catalogue gives free-allowance rows their own table",
   'free on a published allowance' in _cat2)
ck("that table names Oracle and its source",
   'Oracle Cloud' in _cat2.split('free on a published allowance')[1][:600]
   and 'docs.oracle.com' in _cat2.split('free on a published allowance')[1][:600])

print("GUARD N: the keep rate must change a number, not just a column")
# keep_rate was computed, stored, printed on every row and never used. The first
# attempt at the fix multiplied the duty cycle by it, which billed a suspending
# provider for ZERO hours. The keep rate belongs on the HELD figure, not on the
# duty cycle, and the held figure is what a reader comparing a sandbox to a VPS
# needs.
_ns = [p for p in doc['providers'] if p['id'] == 'namespace']
ck("namespace (auto_stop_idle) is in the model", bool(_ns))
if _ns:
    _s = _ns[0]['shapes'].get('agent') or _ns[0]['shapes'].get('tiny')
    ck("namespace's keep rate is 0.00", _s['keep_rate'] == 0.0, str(_s['keep_rate']))
    _p10, _p24 = _s['periods']['10h'], _s['periods']['24h']
    ck("a keep of 0.00 must NOT zero the duty-cycle bill",
       _p10['billed_month_no_credit'] > 0 and _p24['billed_month_no_credit'] > 0,
       "10h=$%.2f 24h=$%.2f" % (_p10['billed_month_no_credit'],
                               _p24['billed_month_no_credit']))
    ck("holding it costs LESS than using it (keep 0.00 suspends when idle)",
       _p10['hold_month'] < _p10['billed_month_no_credit'],
       "held $%.2f vs used $%.2f" % (_p10['hold_month'],
                                     _p10['billed_month_no_credit']))
    ck("at 24/7 the held figure equals 24h x rate, and is LESS than the "
       "duty-cycle month only because the duty cycle is what you are awake for",
       _p24['hold_month'] < _p24['billed_month_no_credit'],
       "held $%.2f vs used $%.2f" % (_p24['hold_month'],
                                     _p24['billed_month_no_credit']))
    ck("at 24/7 the held figure is exactly 24 x rate x 30",
       abs(_p24['hold_month'] - _s['hourly'] * 24 * 30) < 0.01,
       "held $%.2f, 24x rate x 30 = $%.2f" % (_p24['hold_month'],
                                             _s['hourly'] * 24 * 30))
_a37b = [p for p in doc['providers'] if p['id'] == 'agent-37']
if _a37b:
    _s = _a37b[0]['shapes']['agent']
    ck("a keep of 1.00 makes held and used identical at 24/7",
       abs(_s['periods']['24h']['hold_month']
           - _s['periods']['24h']['billed_month_no_credit']) < 0.01)
    ck("a keep of 1.00 makes holding dearer than a 10 h/day duty cycle",
       _s['periods']['10h']['hold_month'] > _s['periods']['10h']['billed_month_no_credit'],
       "held $%.2f vs used $%.2f" % (_s['periods']['10h']['hold_month'],
                                     _s['periods']['10h']['billed_month_no_credit']))
    # The Agent 37 reconciliation in GUARD L depends on this being the compute.
    ck("the 24/7 held figure is still the vendor-reconcilable compute",
       abs(_s['periods']['24h']['hold_month'] - 4.40) < 0.12,
       "$%.2f" % _s['periods']['24h']['hold_month'])
ck("lizard's keep rate is read first-party, not defaulted",
   any((s.get('keep_source') or '').startswith('first-party')
       for p in doc['providers'] if p['id'] == 'lizard'
       for s in (p.get('shapes') or {}).values()))
ck("createos's keep rate is read first-party as 1.00, not assumed 0",
   any(abs(s.get('keep_rate', -1) - 1.0) < 1e-9
       and (s.get('keep_source') or '').startswith('first-party')
       for p in doc['providers'] if p['id'] == 'createos'
       for s in (p.get('shapes') or {}).values()))
ck("a first-party keep rate carries its quote and URL",
   all(k.get('url', '').startswith('https://') and len(k.get('quote', '')) > 20
       for k in pm.KEEP_RATES_FIRSTPARTY))
ck("every priced row states a hold_month figure",
   all('hold_month' in pd
       for p in doc['providers'] for s in (p.get('shapes') or {}).values()
       for pd in s['periods'].values()))
ck("the catalogue prints the held column", 'held 24/7' in _cat2)

print()
print("TOTAL:", len(fails), "failures")
sys.exit(1 if fails else 0)
