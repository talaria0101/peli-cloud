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

Exit codes: 0 every guard held, 1 at least one failed, 2 could not run.
"""

import importlib.util, json, os, sys, subprocess
ROOT='/workspace/peli-cloud'
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
# top row of table C must be Agent 37, not Run Cloud
cstart=cat.index('## C.')
crows=[l for l in cat[cstart:].split('\n') if l.startswith('| ') and '| 1 |' in l[:8]]
ck("table C row 1 is Agent 37", bool(crows) and 'Agent 37' in crows[0], crows[0][:70] if crows else "no rows")

print()
print("TOTAL:",len(fails),"failures")
sys.exit(1 if fails else 0)
