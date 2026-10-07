#!/usr/bin/env python3
"""check-anon-vms.py - guard the anonymous/free VM census.

Four things must hold before a row is published:

  1. The list is a census, not a two-row list: a row floor, and no duplicate
     ids.
  2. Every row is re-derivable: a source, and either a first-party quote or an
     explicit measurement note saying why there is no quote. A row with neither
     is a claim nobody can check.
  3. The reachability field is honest. `banner-verified` means a relay DIALED the
     host and read an SSH banner; it does NOT mean a login completed, and the
     page says so where the distinction matters. This is the clause that stops
     the strongest-sounding field in the file from being read as the strongest
     thing in it.
  4. A FREE row may not rest on a banner alone. This clause exists because one
     did: review R22 found tilde.zone carrying `class: free-account` with an
     empty quote, a `cost_usd` of 0 and nothing but a live SSH banner behind it,
     and its first-party page turned out to be a Mastodon instance that mentions
     neither a shell nor an operator. A host answering SSH is evidence of a
     HOST, not of a FREE SHELL. So: a row in a free class must carry a
     first-party quote that says so, OR a `cost_usd` that is not a bare number
     with a first-party basis. A row that wants to be free has to say free in
     words somebody else wrote.
  5. The SSH floor: at least ten free-or-anonymous machines that answer SSH, and
     at least one genuinely anonymous row.

Exit 0 when every clause holds, 1 when one does not, and it names which.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "anonymous-vms.json")
FREE_CLASSES = {"anonymous", "free-account", "free-tier-card"}
ALL_CLASSES = FREE_CLASSES | {"changed", "dead"}
REACHABILITY = {"banner-verified", "not-verified", "provider-documented"}
# A free row that has been dialled must ALSO carry first-party words saying it
# is free. Set after review R22, which found a live banner carrying a row.
FREE_CLASS_REQUIRES_QUOTE = FREE_CLASSES

MIN_SSH = 10
MIN_ROWS = 20

problems = []
d = json.load(open(DATA, encoding="utf-8"))
rows = d["rows"]

if len(rows) < MIN_ROWS:
    problems.append(f"only {len(rows)} rows; a census wants >= {MIN_ROWS}")

seen = set()
for r in rows:
    rid = r.get("id", "<no id>")
    if rid in seen:
        problems.append(f"{rid}: duplicate id")
    seen.add(rid)
    for field in ("id", "name", "class", "source", "verification", "caveats"):
        if not r.get(field):
            problems.append(f"{rid}: missing {field}")
    # A row must carry EITHER a quote OR a measurement note. The note is what
    # makes a banner-only row auditable instead of decorative.
    if not r.get("quote") and "measured" not in (r.get("verification") or "").lower():
        problems.append(f"{rid}: no quote and no measurement in verification")
    if r.get("class") not in ALL_CLASSES:
        problems.append(f"{rid}: unknown class {r.get('class')!r}")
    if r.get("ssh") not in (True, False):
        problems.append(f"{rid}: ssh must be true or false")
    if not isinstance(r.get("account_required"), bool) or not isinstance(r.get("card_required"), bool):
        problems.append(f"{rid}: account_required/card_required must be booleans")
    reach = r.get("ssh_reachability")
    if reach not in REACHABILITY:
        problems.append(f"{rid}: ssh_reachability must be one of {sorted(REACHABILITY)}, got {reach!r}")
    # A row claiming a banner-verified endpoint must name one. Without the
    # host:port the claim is unfalsifiable from the file alone.
    if reach == "banner-verified" and not r.get("ssh_endpoint"):
        problems.append(f"{rid}: banner-verified but no ssh_endpoint")
    if reach == "not-verified" and not r.get("ssh_endpoint") and not r.get("ssh_how"):
        problems.append(f"{rid}: not-verified and no endpoint or how")

# R22. A free row may not rest on reachability. If it was dialled and carries no
# quote, then the ONLY thing supporting "free" is that something answered on
# port 22 - which is evidence of a host, not of a free shell. Review R22 found
# exactly that: a row classed free-account, cost 0, no quote, one live banner,
# and a first-party page that never mentioned a shell.
for r in rows:
    if r.get("class") in FREE_CLASS_REQUIRES_QUOTE and not r.get("quote"):
        problems.append(
            f"{r.get('id')}: free class with no first-party quote. A banner proves a "
            f"host, not a free shell; a free row needs words its provider wrote "
            f"(see review R22)")

# The point of the brief: free-or-anonymous machines that answer SSH.
ssh_rows = [r for r in rows if r.get("class") in FREE_CLASSES and r.get("ssh") is True]
if len(ssh_rows) < MIN_SSH:
    problems.append(f"only {len(ssh_rows)} free/anon rows with ssh=true; the brief asks for >= {MIN_SSH}")

anonymous = [r for r in rows if r.get("class") == "anonymous"]
if not anonymous:
    problems.append("no row is class=anonymous; the brief names anonymous VMs explicitly")

banner = [r for r in ssh_rows if r.get("ssh_reachability") == "banner-verified"]

print(f"rows={len(rows)} ssh_free_or_anon={len(ssh_rows)} banner_verified={len(banner)} "
      f"anonymous={len(anonymous)} classes={sorted({r.get('class') for r in rows})}")
if problems:
    print("FAIL anon_vms_guard")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("ok anon_vms_guard")
sys.exit(0)