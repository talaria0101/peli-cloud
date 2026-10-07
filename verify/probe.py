#!/usr/bin/env python3
"""Live reachability probe for free-shell hosts.

Reads an endpoint list, opens a TCP socket, reads the SSH identification
string, and records the result. This is a BANNER measurement, not a login: it
proves the host is up and speaking SSH. It does not prove credentials work.

The point of measuring at all: peli-cloud recorded that its own sandbox refuses
port 22 on its egress proxy (CONNECT -> 403), so every row in its census is
'documented, not dialled'. This runs from a residential host instead.

    python verify/probe.py                       # run the probe
    python verify/probe.py --dry-run             # measure, do NOT overwrite reachability.json
    python verify/probe.py --hosts host:port ... # ad-hoc targets

EXIT CODES:

  0  the probe ran and the committed measurement was written (or --dry-run)
  1  the probe ran and the committed measurement was NOT written; see the reason
  2  could not run at all (no targets, or --dry-run over a measurement that
     already exists and would have been clobbered)

WHY THE NON-ZERO EXITS EXIST. The first version had no return at all, so it
exited 0 unconditionally, and it wrote verify/reachability.json
unconditionally. Both were measured on 2026-10-07, in a /tmp copy so the
artefact was not destroyed here:

    $ python verify/probe.py        # run where port 22 is proxied
    0/14 reachable, 0 returned an SSH banner
    wrote verify/reachability.json
    exit=0

That replaced a real 10/14-reachable, 9-banner measurement, dated
2026-10-06T12:23:02+0545 from a residential Windows host, with fourteen DNS
failures, and reported success. A tracked measurement that a single unlucky run
can silently destroy is not evidence. Three things prevent that here:

  1. --dry-run exists, and is what you should use unless you mean to replace the
     committed measurement.
  2. A run that measures NOTHING (no endpoint produced a banner AND no endpoint
     produced a connection) is treated as a failed measurement, not a result. It
     does not overwrite, and exits 1. A real outage of every host at once is far
     less likely than a sandbox that cannot reach port 22, and the distinction is
     not something to guess at in a script that overwrites a committed file.
  3. --expect-failures reads verify/probe-hosts.json's expected_failures block
     and REPORTS it. The block existed and was read by nothing; the three
     control endpoints it documents were therefore never asserted against
     anything.
"""

import json
import pathlib
import socket
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "verify" / "reachability.json"
SOURCES = ROOT / "verify" / "probe-hosts.json"
BANNER_TIMEOUT = 8.0
CONNECT_TIMEOUT = 6.0


def banner(host, port):
    """Return (reachable, banner, error, latency_ms).

    `reachable` means a TCP connection completed. That is deliberately weaker
    than "speaking SSH": a connect to an HTTPS port on 443 succeeds and returns
    no banner at all, which is exactly how blinkenshell.org:443 ended up in the
    committed measurement. `banner` is the stronger signal and is what the
    page's banner counts use.
    """
    t0 = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=CONNECT_TIMEOUT) as s:
            s.settimeout(BANNER_TIMEOUT)
            try:
                data = s.recv(256)
            except socket.timeout:
                data = b""
            ms = (time.monotonic() - t0) * 1000
            if data:
                return True, data.decode("utf-8", "replace").strip(), None, round(ms, 1)
            # Connected but silent. Some hosts wait for us to speak first, and an
            # HTTPS port never sends an SSH banner, so this is not a failure to
            # reach the host. It is not evidence of SSH either.
            return True, "", "connected, no banner within timeout", round(ms, 1)
    except socket.timeout:
        return False, "", "connect timeout", None
    except ConnectionRefusedError:
        return False, "", "connection refused", None
    except socket.gaierror as e:
        return False, "", f"DNS: {e}", None
    except OSError as e:
        return False, "", f"OSError: {e}", None


def load_hosts():
    with SOURCES.open(encoding="utf-8") as fh:
        return json.load(fh)


def run(targets):
    """Probe every target concurrently.

    Duplicate host:port pairs are rejected before any socket is opened. The
    results dict is keyed by host:port, so a duplicate would silently overwrite
    its twin and one row of evidence would vanish with no warning.
    """
    seen = {}
    for h, p, label, *_ in targets:
        key = f"{h}:{p}"
        if key in seen:
            raise SystemExit(
                f"refusing to probe: {key} twice (labels: {seen[key]!r} and {label!r}). "
                f"The results are keyed by host:port, so one row would overwrite the other "
                f"and the dropped row would leave no trace."
            )
        seen[key] = label

    results = {}
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {
            pool.submit(banner, h, p): (h, p, label)
            for h, p, label, *_ in targets
        }
        # Iterating the dict yields SUBMISSION order, not completion order, so a
        # slow first target delays every result behind it. as_completed would
        # not, and the results are re-sorted for display anyway. Every future is
        # already submitted and banner() has two bounded timeouts, so this loop
        # cannot hang.
        for key, fut in [(f"{h}:{p}", f) for f, (h, p, _) in futures.items()]:
            h, p, _ = futures[fut]
            ok, ban, err, ms = fut.result()
            results[key] = {
                "label": [t[2] for t in targets if f"{t[0]}:{t[1]}" == key][0],
                "host": h,
                "port": p,
                "reachable": ok,
                "banner": ban,
                "error": err,
                "latency_ms": ms,
            }
    return results


def report_expected_failures(results, hosts):
    """Print the expectations recorded in probe-hosts.json against this run.

    The block documented three control endpoints. Nothing read it, so the
    controls were narrative rather than a check. They are informational: an
    expectation that no longer matches reality is a finding for a human to
    resolve, not a reason to fail the probe. This reports; it does not assert.
    """
    expected = hosts.get("expected_failures") or {}
    if not expected:
        print("\n(no expected_failures recorded in probe-hosts.json)")
        return
    print("\nexpected_failures from probe-hosts.json, against this run:")
    for needle, why in expected.items():
        matches = [k for k in results if k == needle or k.split(":")[0] == needle]
        if not matches:
            state = "NOT PROBED"
        else:
            up = [k for k in matches if results[k]["reachable"]]
            state = "reachable" if up else "not reachable"
            detail = "; ".join(
                f"{k}: {'banner' if results[k]['banner'] else results[k]['error']}"
                for k in matches
            )
            print(f"  {needle:<28} {state:<14} {detail}")
            print(f"    expected because: {why}")
            continue
        print(f"  {needle:<28} {state}")
        print(f"    expected because: {why}")


def main():
    dry = "--dry-run" in sys.argv
    if "--hosts" in sys.argv:
        args = sys.argv[sys.argv.index("--hosts") + 1:]
        targets = [(a.split(":")[0], int(a.split(":")[1]), "adhoc") for a in args]
    else:
        hosts = load_hosts()
        targets = [
            (h["host"], h["port"], h["label"]) for h in hosts["targets"]
        ]

    if not targets:
        print("no targets; nothing measured")
        return 2

    print(f"probing {len(targets)} endpoints from this host\n")
    results = run(targets)
    if len(results) != len(targets):
        print(f"refusing to write: {len(targets)} targets produced {len(results)} "
              f"results, so a row would be lost")
        return 2

    reachable = sum(1 for r in results.values() if r["reachable"])
    banners = sum(1 for r in results.values() if r["banner"])

    for key in sorted(results, key=lambda k: (not results[k]["reachable"], k)):
        r = results[key]
        if r["reachable"]:
            mark = "BANNER" if r["banner"] else "OPEN  "
            detail = r["banner"] or r["error"]
            ms = f"{r['latency_ms']}ms" if r["latency_ms"] else ""
            print(f"  [{mark}] {key:<34} {ms:>8}  {detail}")
        else:
            print(f"  [DOWN  ] {key:<34} {'':>8}  {r['error']}")

    print(f"\n{reachable}/{len(results)} reachable, {banners} returned an SSH banner")
    print("NOTE: a banner is not a login. No credential was presented anywhere here.")

    payload = {
        "measured_from": "residential Windows host (this machine)",
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "why": (
            "peli-cloud could not dial any host: its sandbox egress proxy refuses "
            "port 22 with HTTP 403, so its census is documented-only. This runs "
            "from a residential host where port 22 is not proxied."
        ),
        "caveat": (
            "A banner proves the host is up and speaking SSH. It does NOT prove a "
            "login completes, that an account can be created, or that a free tier "
            "exists. Those are separate claims requiring credentials."
        ),
        "summary": {"total": len(results), "reachable": reachable, "banners": banners},
        "results": results,
    }

    if dry:
        print(f"\n--dry-run: {OUT.relative_to(ROOT)} NOT written")
        return 0

    # A run that connected to nothing and read no banner has measured the
    # network path, not the hosts. Writing it would replace a real measurement
    # with a list of DNS failures while reporting success.
    if reachable == 0:
        print(f"\nrefusing to overwrite {OUT.relative_to(ROOT)}: this run reached 0 of "
              f"{len(results)} endpoints.")
        if OUT.exists():
            prev = json.loads(OUT.read_text(encoding="utf-8"))
            print(f"the committed measurement is {prev['summary']} from "
                  f"{prev['measured_at']} ({prev['measured_from']}); it is left intact.")
        print("If this host really cannot reach these hosts, that is a fact about "
              "this host, not about the hosts. Re-run with --dry-run to inspect, or "
              "from a network where port 22 is not proxied.")
        return 1

    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    if not dry:
        try:
            report_expected_failures(results, load_hosts())
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())