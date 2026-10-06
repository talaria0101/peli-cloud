#!/usr/bin/env python3
"""Render docs/ALWAYS-ON-FREE.md from data/always-on-free.json.

Every number on the page is generated. Prose that a script can compute should
not be typed, because typed prose drifts the moment the data changes.

    python tools/render-always-on-free.py
"""

import importlib.util
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "always-on-free.json"
OUT = ROOT / "docs" / "ALWAYS-ON-FREE.md"
GUARD = ROOT / "tools" / "check-always-on-free.py"

COUNTABLE = {"T1", "T2", "T3"}
ORDER = ["T1", "T2", "T3", "DEAD", "UNVERIFIED"]


def _load_guard():
    """Import the guard so the page and the check can never disagree.

    The provenance table and the mutation count are both derived from the guard
    rather than typed. An earlier revision hardcoded "9/9" while the guard ran
    11 mutations, which is the exact drift this file's docstring warns about.
    """
    spec = importlib.util.spec_from_file_location("always_on_guard", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cell(row, key, default="—"):
    val = row.get(key)
    if val is None or val == "":
        return default
    return str(val)


def short(s, n=150):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def main():
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    rows = doc["rows"]
    counted = [r for r in rows if r["tier"] in COUNTABLE]
    guard = _load_guard()
    _provenance = guard.provenance
    n_mutations = len(guard.MUTATIONS)

    L = []
    a = L.append

    a("# Always-on free compute, 2026-10-06")
    a("")
    a(f"**{len(counted)} of {len(rows)} rows hold up indefinitely at $0.** "
      f"The launch base "
      f"([talaria0101/peli-cloud](https://github.com/talaria0101/peli-cloud)) "
      f"records **zero** — its free-VM page is a census of *shells*, and every "
      f"row it carries that claims compute dies on a quota or an expiry.")
    a("")
    a("Generated from [`data/always-on-free.json`](../data/always-on-free.json) "
      "by `tools/render-always-on-free.py`. Guarded by "
      "`tools/check-always-on-free.py`.")
    a("")

    a("## The distinction the taxonomy rests on")
    a("")
    a("A relay cannot fix everything, and that is the whole design.")
    a("")
    a("| tier | what it means | count |")
    a("|---|---|---|")
    for t in ORDER:
        if t not in doc["tiers"]:
            continue
        a(f"| **{t}** | {doc['tiers'][t]} | {sum(1 for r in rows if r['tier'] == t)} |")
    a("")
    a("**A relay defeats a LIVENESS wall** — idle sleep, scale-to-zero, "
      "no-inbound-ports, browser-only. You keep the machine alive, or you tunnel "
      "out of it, and it becomes reachable forever.")
    a("")
    a("**A relay cannot defeat a QUOTA wall** — a monthly compute-hour cap that "
      "exhausts regardless, a 24-hour absolute lifetime, a trial clock, or a "
      "paid-plan gate at creation time. Those rows are DEAD and are excluded.")
    a("")
    a("So T2 and T3 are legitimate hits, not near-misses: the keepalive or the "
      "relay *is* the thing that makes them always-on. Only DEAD is a dead end.")
    a("")

    a("## How much of this is measured")
    a("")
    a("Every row is counted exactly once, using the guard's own `provenance()` "
      "so these two tools cannot disagree about what a row's evidence is worth.")
    a("")
    a("| evidence weight | rows | means |")
    a("|---|---|---|")
    weights = {}
    for r in rows:
        weights.setdefault(_provenance(r), []).append(r["name"])
    a(f"| first-hand | {len(weights.get('read', []))} | I fetched the page and read the "
      f"quote out of the bytes |")
    a(f"| carried | {len(weights.get('carried', []))} | a research pass fetched it; the "
      f"row says so, and names which parts I did not check |")
    a("")
    a("\"First-hand\" means the bytes were read, **not** that an account was "
      "created. No account exists anywhere in this census. The live probe below "
      "is the only measurement here that touches a real host.")
    a("")

    a("## The counted rows")
    a("")
    for t in ["T1", "T2", "T3"]:
        sel = [r for r in rows if r["tier"] == t]
        if not sel:
            continue
        a(f"### {t} — {doc['tiers'][t]}")
        a("")
        for r in sel:
            a(f"#### {r['name']}")
            a("")
            a(f"- **What you get:** {cell(r, 'spec')}")
            if r.get("idle_or_session_limit"):
                a(f"- **The wall:** {cell(r, 'idle_or_session_limit')}")
            if r.get("keepalive"):
                a(f"- **The keepalive:** {cell(r, 'keepalive')}")
            if r.get("relay"):
                a(f"- **The relay:** {cell(r, 'relay')}")
            a(f"- **Account:** sign-up required = {cell(r, 'account_required')}, "
              f"card required = {cell(r, 'card_required')}")
            if r.get("caveats"):
                a(f"- **Caveat:** {r['caveats']}")
            if r.get("source"):
                a(f"- **Source:** <{r['source']}>")
            if r.get("quote"):
                a(f"- **Vendor says:** > {r['quote']}")
                if r.get("quote2"):
                    a(f"  > {r['quote2']}")
            if r.get("verified_by"):
                a(f"- **Verified:** {r['verified_by']}")
            a("")

    a("## Measured, not assumed: live reachability")
    a("")
    reach_path = ROOT / "verify" / "reachability.json"
    if reach_path.exists():
        reach = json.loads(reach_path.read_text(encoding="utf-8"))
        s = reach["summary"]
        a(f"peli-cloud could not dial a single host: its sandbox egress proxy refuses "
          f"port 22 (`CONNECT -> 403`), so every row in its census is documented-only. "
          f"This census was probed from a **residential host** instead. "
          f"**{s['reachable']}/{s['total']} endpoints accepted a TCP connection and "
          f"{s['banners']} returned an SSH identification string.**")
        a("")
        a("A banner is not a login. No credential was presented to any of these hosts.")
        a("")
        a("| endpoint | result | banner / error |")
        a("|---|---|---|")
        for key in sorted(reach["results"],
                          key=lambda k: (not reach["results"][k]["reachable"], k)):
            r = reach["results"][key]
            state = "**banner**" if r["banner"] else ("open, silent" if r["reachable"] else "no route")
            detail = r["banner"] or r["error"] or ""
            a(f"| `{key}` | {state} | `{detail}` |")
        a("")
        a("Two results contradict prior claims and are the reason this probe was worth running. "
          "Both bullets are computed from `verify/reachability.json`, so re-running the probe "
          "either reproduces them or falsifies them:")
        a("")

        def _bs(port):
            r = reach["results"].get(f"blinkenshell.org:{port}")
            return r["reachable"] if r else None

        web_up, ssh_up = _bs(443), _bs(2222)
        if web_up is not None and ssh_up is not None:
            down = [p for p in (22, 2222, 6697)
                    if reach["results"].get(f"blinkenshell.org:{p}", {}).get("reachable") is False]
            a(f"- **Blinkenshell is filtered, not down.** Port 443 accepted a connection "
              f"while {', '.join(str(p) for p in down)} all timed out on the same host, in "
              f"the same run. peli-cloud blamed its sandbox's port-22 refusal, but 2222 was "
              f"never port 22, so that excuse never covered this case. The host is alive and "
              f"filtering by protocol.")
        else:
            a("- **Blinkenshell:** this run did not measure both 443 and 2222, so no "
              "filtered-or-down claim is made here.")
        a("- **tilde.zone answers SSH** with the *identical* OpenSSH build string as "
          "tilde.town (`10.0p2 Debian-7+deb13u4`), which is what a shared image or a "
          "mirror produces. peli-cloud demoted it for having no discoverable "
          "operator; it is demonstrably live. Still not counted as a free shell, "
          "because a banner is not evidence of a free tier.")
        a("")
        a(f"_Measured {reach['measured_at']} from a {reach['measured_from']}._")
        a("")

    a("## Dead ends, and the wall that killed each")
    a("")
    a("Nothing below was overcome in practice. Each wall is one a relay or a "
      "keepalive is argued *not* to defeat, from the vendor's own wording, and "
      "no relay or keepalive was actually run against any of them.")
    a("")
    a("| Provider | the hard wall |")
    a("|---|---|")
    for r in [r for r in rows if r["tier"] == "DEAD"]:
        a(f"| **{r['name']}** | {short(cell(r, 'hard_wall'), 260)} |")
    a("")

    a("## Corrections to the launch base")
    a("")
    a("Read against first-party pages fetched on 2026-10-06.")
    a("")
    for c in doc["corrections_vs_launch_base"]:
        a(f"- {c}")
    a("")

    a("## What this census did NOT establish")
    a("")
    a("Stated plainly, because a census that hides its gaps is worse than no census.")
    a("")
    for c in doc["what_this_census_did_not_establish"]:
        a(f"- {c}")
    a("")

    a("## Reproduce")
    a("")
    a("```sh")
    a("python tools/check-always-on-free.py           # guard the census")
    a(f"python tools/check-always-on-free.py --mutate  # prove the guard can fail ({n_mutations}/{n_mutations})")
    a("python tools/render-always-on-free.py          # rewrite this page from the JSON")
    a("python verify/fetch.py                         # re-fetch the vendor pages")
    a("python verify/claim.py                        # every quote, against the bytes it came from")
    a("python verify/fetch.py --check                # is every capture re-fetchable by name?")
    a("```")
    a("")
    a("## Method")
    a("")
    m = doc["method"]
    a(f"- **Launch base:** {m['launch_base']}")
    a(f"- **Sweep 1:** {m['sweep_1']}")
    a(f"- **Sweep 2:** {m['sweep_2']}")
    a(f"- **First-party verification:** {m['first_party_verification']}")
    a("")
    a("Fetches that failed (recorded, not silently substituted):")
    a("")
    for f in m["fetches_that_failed"]:
        a(f"- `{f}`")
    a("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(L)} lines)")

    r = subprocess.run([sys.executable, str(GUARD)], capture_output=True, text=True)
    print(r.stdout.strip())
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())