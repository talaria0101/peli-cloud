#!/usr/bin/env python3
"""Live reachability probe for free-shell hosts.

Reads an endpoint list, opens a TCP socket, reads the SSH identification
string, and records the result. This is a BANNER measurement, not a login: it
proves the host is up and speaking SSH. It does not prove credentials work.

The point of measuring at all: peli-cloud recorded that its own sandbox refuses
port 22 on its egress proxy (CONNECT -> 403), so every row in its census is
'documented, not dialled'. This runs from a residential host instead.

    python verify/probe.py                       # run the probe
    python verify/probe.py --hosts host:port ... # ad-hoc targets
"""

import json
import pathlib
import socket
import ssl
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
    """Return (reachable, banner, error, latency_ms)."""
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
            # Connected but silent. Some hosts wait for us to speak first.
            return True, "", "connected, no banner within timeout", round(ms, 1)
    except socket.timeout:
        return False, "", "connect timeout", None
    except ConnectionRefusedError:
        return False, "", "connection refused", None
    except socket.gaierror as e:
        return False, "", f"DNS: {e}", None
    except OSError as e:
        return False, "", f"OSError: {e}", None


def resolve_mdns_stub(host):
    """Some tilde hosts publish *.local names; note it rather than pretending."""
    return host.endswith(".local") or host.startswith("ssh-")


def load_hosts():
    with SOURCES.open(encoding="utf-8") as fh:
        return json.load(fh)


def run(targets):
    results = {}
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {
            pool.submit(banner, h, p): (h, p, label)
            for h, p, label, *_ in targets
        }
        for fut, (h, p, label) in futures.items():
            ok, ban, err, ms = fut.result()
            results[f"{h}:{p}"] = {
                "label": label,
                "host": h,
                "port": p,
                "reachable": ok,
                "banner": ban,
                "error": err,
                "latency_ms": ms,
            }
    return results


def main():
    if "--hosts" in sys.argv:
        args = sys.argv[sys.argv.index("--hosts") + 1:]
        targets = [(a.split(":")[0], int(a.split(":")[1]), "adhoc") for a in args]
    else:
        hosts = load_hosts()
        targets = [
            (h["host"], h["port"], h["label"]) for h in hosts["targets"]
        ]

    print(f"probing {len(targets)} endpoints from this host\n")
    results = run(targets)

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
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()