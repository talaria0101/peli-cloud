#!/usr/bin/env python3
"""check-all.py - run every gate in this repository, once, and say which failed.

There is no CI here. The README lists the guards in two separate blocks, and a
reader who has just edited data/always-on-free.json has no way to learn which
of the eleven gates are about to disagree with what they just wrote. This runs
all of them and prints one table.

    python3 tools/check-all.py             # run every gate; exit 0 iff every REQUIRED gate returned 0
    python3 tools/check-all.py --list      # print the gates and their commands; run nothing
    python3 tools/check-all.py --strict    # also fail when an OPTIONAL gate could not pass here
    python3 tools/check-all.py --verbose   # echo every gate's own output, not just the failures

WHY A REQUIRED/OPTIONAL SPLIT AND NOT A PASS/FAIL SPLIT

Five of the eleven gates read an evidence store this repository does not track.
`verify/pages/` is in .gitignore, so a fresh clone has no captures: the two
verify/ gates then exit 1 for that reason alone, and three gates classified
REQUIRED fail too (see the section on reads_captures below). Two more gates are
OPTIONAL for a different reason - tools/render-anon-vms.py REWRITES A TRACKED
FILE (docs/ANONYMOUS-VMS.md), which is a side effect a status check must not
have, so it is run with ANON_VMS_OUT pointed at a temporary path, which
tools/render-anon-vms.py:25 supports for exactly this.

Calling those "failures" would make this script permanently red on any host
without the captures, and a red script that nothing can turn green gets ignored.
The untrackable ones are therefore OPTIONAL: reported, with the reason they
could not pass, and counted only under --strict.

On the specific case this was written for: verify/claim.py and
verify/fetch.py --check exit 1 here because 2 of the 35 claims
(sdf_members01, sdf_members05) have no capture in verify/pages/. That is an
absent evidence store, not a broken guard. verify/fetch.py:110-113 records the
cause in KNOWN_UNREACHABLE - "sdf.org does not resolve through some egress
proxies (502/504 observed)" - and `check` prints that note beside each claim it
cannot account for. This script does NOT assert that sdf.org is unreachable
from wherever you are reading this: it reports what it measured, which is which
claims have no capture, and points at fetch.py for the rest.

WHAT "COULD NOT RUN" MEANS, AND WHY --strict IS THE ANSWER

Two ways an OPTIONAL gate can go wrong, and they are not the same:

  * it could not be RUN   - the script is absent (MISSING) or would not launch
  * it RAN and returned non-zero - the evidence store is not there

--strict fails on both, because a maintainer asking "is this repo fully
verified on this host" wants to know about either. Without --strict only the
REQUIRED gates decide the exit code, so the two verify/ gates above are
reported and explained rather than turned red.

THREE GATES CLASSIFIED REQUIRED ALSO READ verify/pages/

tools/check-always-on-free-extended.py (:107), its --mutate run, and
tools/check-rendered-page.py --mutate therefore cannot pass on a fresh clone:
with the capture store absent they print "no captures" and refuse or fail. They
stay REQUIRED here because that is the classification they were given, and a
verdict is never softened because it would turn the run red. Instead, a failure
of a gate that reads captures prints the store's measured state next to it, so
a fresh-clone red is legible instead of mysterious. Measured: with
verify/pages/ removed, 3 of the 8 REQUIRED gates fail (see the
"reads_captures" entries in GATES).

EXIT CODES

  0  lenient: every REQUIRED gate returned 0. strict: every gate returned 0.
  1  at least one gate in scope for this mode was not PASS.
  2  check-all.py itself could not run (unreadable gate table, unwritable temp
     dir). Never used for a gate failing.

    In both modes a REQUIRED gate that is not PASS is always exit 1, whatever
    --strict says.

The table's EXIT column is the subprocess returncode, read from the process
itself. Nothing here infers success from output text, and no gate's output is
piped, so the exit code cannot be a pipe's status or another program's.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Seconds before a gate is declared hung. check-rendered-page.py --mutate is the
# slowest thing here at ~4 s; 600 is slack, not a measurement.
GATE_TIMEOUT = 600

CAPTURES = os.path.join(ROOT, "verify", "pages")
CLAIMS = os.path.join(ROOT, "verify", "claims.json")

# Each gate is one subprocess, run with cwd=ROOT so the relative paths in the
# README's own reproduction block work as written.
#
#   script  path relative to the repo root
#   args    extra argv, passed after the script path
#   required  True = the repo is unhealthy without it
#   why     why it is OPTIONAL, or what it is for. Printed in full below the
#           table, and on its own for every OPTIONAL gate that did not pass.
#   short   one short clause for the table, so the row stays readable
#   side    a name in ENV that this script sets to keep the gate off the tree
#   reads_captures  True if the gate reads verify/pages/ and therefore cannot
#           pass on a fresh clone. Used only to EXPLAIN a failure, never to
#           change a verdict: the classification above is the contract.
GATES = [
    {
        "name": "line-endings",
        "script": "tools/check-line-endings.py",
        "args": [],
        "required": True,
        "short": "no tracked text file has CRLF",
        "why": "five files were committed with CRLF from a Windows checkout, "
               "which turned a six-row correction into a 988-line diff",
    },
    {
        "name": "anon-vms-guard",
        "script": "tools/check-anon-vms.py",
        "args": [],
        "required": True,
        "why": "guards the anonymous census against data/anonymous-vms.json",
        "short": "anonymous census guard",
    },
    {
        "name": "always-on-guard",
        "script": "tools/check-always-on-free.py",
        "args": [],
        "required": True,
        "why": "guards the always-on census: tiers, keepalives, relays",
        "short": "always-on census guard",
    },
    {
        "name": "always-on-extended",
        "script": "tools/check-always-on-free-extended.py",
        "args": [],
        "required": True,
        "reads_captures": True,
        "why": "the deeper clauses over the same census. NOTE: this one reads "
               "verify/pages/ (tools/check-always-on-free-extended.py:107) and "
               "cannot pass on a fresh clone - see the note printed under it.",
        "short": "extended clauses; reads verify/pages/",
    },
    {
        "name": "rendered-page",
        "script": "tools/check-rendered-page.py",
        "args": [],
        "required": True,
        "why": "docs/ALWAYS-ON-FREE.md is what the renderer would write",
        "short": "committed page == rendered page",
    },
    {
        "name": "quote-selftest",
        "script": "tests/selftest-check-quotes.py",
        "args": [],
        "required": True,
        "why": "the quote checker's own known answers",
        "short": "quote checker selftest",
    },
    {
        "name": "guard-mutation",
        "script": "experiments/60-guard-mutation.py",
        "args": [],
        "required": True,
        "why": "plant each defect the ranking guards exist to catch",
        "short": "can the ranking guards fail",
    },
    {
        "name": "always-on-extended-mutate",
        "script": "tools/check-always-on-free-extended.py",
        "args": ["--mutate"],
        "required": True,
        "reads_captures": True,
        "why": "prove the extended guard can still fail. NOTE: reads "
               "verify/pages/, so a fresh clone cannot run the mutations.",
        "short": "extended guard can fail; reads verify/pages/",
    },
    {
        "name": "rendered-page-mutate",
        "script": "tools/check-rendered-page.py",
        "args": ["--mutate"],
        "required": True,
        "reads_captures": True,
        "why": "prove the rendered-page guard can still fail. NOTE: refuses to "
               "run its mutations without verify/pages/.",
        "short": "page guard can fail; reads verify/pages/",
    },
    {
        "name": "render-anon-vms",
        "script": "tools/render-anon-vms.py",
        "args": [],
        "required": False,
        "side": "ANON_VMS_OUT",
        "short": "renders docs/ANONYMOUS-VMS.md; redirected to a temp path",
        "why": "REWRITES THE TRACKED FILE docs/ANONYMOUS-VMS.md, so it is run "
               "with ANON_VMS_OUT pointed at a temp path (supported at "
               "tools/render-anon-vms.py:25). Run it with no env var to rewrite "
               "the page for real.",
    },
    {
        "name": "captures-fresh",
        "script": "verify/fetch.py",
        "args": ["--check"],
        "required": False,
        "short": "needs verify/pages/ captures",
        "why": "needs verify/pages/, which is GITIGNORED (.gitignore) and absent "
               "from a fresh clone. --check reads the store; it does not fetch.",
    },
    {
        "name": "quotes-vs-captures",
        "script": "verify/claim.py",
        "args": [],
        "required": False,
        "short": "needs verify/pages/ captures",
        "why": "needs the same verify/pages/ captures; it re-checks each quote "
               "against the bytes it was taken from.",
    },
]

CAPTURE_GATES = ("captures-fresh", "quotes-vs-captures")


def hand_command(gate, tmpdir):
    """The command a reader can paste into a shell to run this gate by hand."""
    parts = ["python3", gate["script"]] + list(gate["args"])
    if gate.get("side") and tmpdir:
        out = os.path.join(tmpdir, os.path.basename(gate["script"]).replace(".py", ".md"))
        return "ANON_VMS_OUT=%s %s" % (out, " ".join(parts))
    return " ".join(parts)


def capture_status():
    """How complete the capture store is, counted here from claims.json and the
    directory listing, never read off a gate's exit code. Always a sentence."""
    if not os.path.isdir(CAPTURES):
        return "verify/pages/ is absent (gitignored build input; run python3 verify/fetch.py)"
    try:
        claims = json.load(open(CLAIMS, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return "verify/claims.json unreadable: %s" % (exc,)
    claims.pop("_comment", None)
    have = {f[: -len(".html")] for f in os.listdir(CAPTURES) if f.endswith(".html")}
    missing = sorted(set(claims) - have)
    if not missing:
        return "%d of %d claims HAVE a capture in verify/pages/" % (len(claims), len(claims))
    return ("%d of %d claims have a capture in verify/pages/; %d have none: %s"
            % (len(claims) - len(missing), len(claims), len(missing), ", ".join(missing)))


def run_gate(gate, tmpdir):
    """Run one gate as a subprocess. Returns (exit_code, output, verdict).

    verdict is one of PASS / FAIL / MISSING / ERROR / TIMEOUT. The exit code is
    None for the three that never produced a process.
    """
    path = os.path.join(ROOT, gate["script"])
    if not os.path.isfile(path):
        return None, "", "MISSING"

    env = dict(os.environ)
    if gate.get("side") and tmpdir:
        env[gate["side"]] = os.path.join(
            tmpdir, os.path.basename(gate["script"]).replace(".py", ".md"))

    cmd = [sys.executable, gate["script"]] + list(gate["args"])
    try:
        proc = subprocess.run(
            cmd, cwd=ROOT, env=env, capture_output=True, text=True,
            errors="replace", timeout=GATE_TIMEOUT)
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        return None, out, "TIMEOUT"
    except OSError as exc:
        return None, str(exc), "ERROR"

    out = proc.stdout + proc.stderr
    # The returncode, not the output. Nothing above inspects out to decide.
    return proc.returncode, out, ("PASS" if proc.returncode == 0 else "FAIL")


def pad(s, width):
    return s + " " * max(0, width - len(s))


def excerpt(out, head=3, tail=3):
    """A few lines of a failing gate's own output, so a non-zero exit code is
    accompanied by what the gate said. Up to `head` leading and `tail` trailing
    non-blank lines, with a marker when anything was left out.

    This is for the human reading the report. No verdict anywhere in this file
    is derived from it.
    """
    lines = [ln.rstrip() for ln in out.splitlines() if ln.strip()]
    if len(lines) <= head + tail:
        return lines
    return lines[:head] + ["    ... %d lines elided ..." % (len(lines) - head - tail)] \
        + lines[-tail:]


def print_table(results):
    """results: list of (gate, exit_code, verdict, note, output)."""
    name_w = max(len(g["name"]) for g, _, _, _, _ in results)
    cls_w = len("CLASS")
    exit_w = max(len("EXIT"), len("n/a"))
    verdict_w = max(len("VERDICT"), max(len(v) for _, _, v, _, _ in results))

    head = "%s  %s  %s  %s  %s" % (pad("GATE", name_w), pad("CLASS", cls_w),
                                  pad("EXIT", exit_w), pad("VERDICT", verdict_w), "NOTE")
    print(head)
    print("-" * len(head))
    for gate, code, verdict, note, _ in results:
        print("%s  %s  %s  %s  %s" % (
            pad(gate["name"], name_w),
            pad("REQUIRED" if gate["required"] else "OPTIONAL", cls_w),
            pad("n/a" if code is None else str(code), exit_w),
            pad(verdict, verdict_w),
            note))


def main(argv):
    ap = argparse.ArgumentParser(
        prog="tools/check-all.py",
        description="Run every gate in this repo and report each exit code.")
    ap.add_argument("--list", dest="list_gates", action="store_true",
                    help="print the gates and the exact command for each, then exit")
    ap.add_argument("--strict", action="store_true",
                    help="also exit non-zero when an OPTIONAL gate could not pass")
    ap.add_argument("--verbose", action="store_true",
                    help="echo every gate's own output, not only the failures")
    args = ap.parse_args(argv)

    tmpdir = tempfile.mkdtemp(prefix="check-all-")
    try:
        if args.list_gates:
            print("%d gates: %d REQUIRED, %d OPTIONAL\n"
                  % (len(GATES), sum(1 for g in GATES if g["required"]),
                     sum(1 for g in GATES if not g["required"])))
            for i, gate in enumerate(GATES, 1):
                present = "present" if os.path.isfile(os.path.join(ROOT, gate["script"])) \
                    else "MISSING FROM THIS TREE"
                print("%2d. %-28s %s" % (i, gate["name"],
                                         "REQUIRED" if gate["required"] else "OPTIONAL"))
                print("    command : %s" % hand_command(gate, tmpdir))
                print("    script  : %s (%s)" % (gate["script"], present))
                print("    purpose : %s" % gate["why"])
                print("")
            print("verify/pages/ : %s" % capture_status())
            print("")
            print("No gate was run. Drop --list to run all of them; the table then")
            print("carries each gate's exit code.")
            return 0

        print("check-all: %d gates, %d REQUIRED, %d OPTIONAL%s"
              % (len(GATES), sum(1 for g in GATES if g["required"]),
                 sum(1 for g in GATES if not g["required"]),
                 ", --strict (OPTIONAL gates count)" if args.strict else ""))
        print("repo: %s" % ROOT)
        print("")
        print("commands, in run order (copy-pasteable):")
        for i, gate in enumerate(GATES, 1):
            print("  %2d  %s" % (i, hand_command(gate, tmpdir)))
        print("")

        captures = capture_status()
        results = []
        try:
            for gate in GATES:
                code, out, verdict = run_gate(gate, tmpdir)
                note = gate["short"]
                if not gate["required"] and gate["name"] in CAPTURE_GATES:
                    note += " | observed: " + captures
                results.append((gate, code, verdict, note, out))
                if args.verbose and out.strip():
                    print("---- %s output ----" % gate["name"])
                    print(out.rstrip())
                    print("---- end %s ----" % gate["name"])
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

        print_table(results)
        print("")

        required = [r for r in results if r[0]["required"]]
        optional = [r for r in results if not r[0]["required"]]
        req_bad = [r for r in required if r[2] != "PASS"]
        opt_bad = [r for r in optional if r[2] != "PASS"]

        print("REQUIRED: %d of %d passed" % (len(required) - len(req_bad), len(required)))
        print("OPTIONAL: %d of %d passed%s"
              % (len(optional) - len(opt_bad), len(optional),
                 "" if args.strict else "  (not counted; use --strict to count them)"))

        for gate, code, verdict, _, out in req_bad:
            print("FAILED REQUIRED: %s  exit %s  %s"
                  % (gate["name"], "n/a" if code is None else code, verdict))
            print("    run it yourself: %s" % hand_command(gate, None))
            if gate.get("reads_captures"):
                print("    this gate reads verify/pages/ (%s)" % captures)
            for line in excerpt(out):
                print("    | %s" % line)
        if opt_bad:
            print("")
            print("OPTIONAL gates that did not pass here (%d):" % len(opt_bad))
            for gate, code, verdict, _, out in opt_bad:
                print("  %-24s %-7s exit %s" % (gate["name"], verdict,
                                                "n/a" if code is None else code))
                print("      why it is OPTIONAL: %s" % gate["why"])
                for line in excerpt(out):
                    print("      | %s" % line)
            print("")
            if args.strict:
                print("Under --strict these count towards the exit code.")
            else:
                print("These are not counted as defects unless --strict is given.")
                print("They need an evidence store or a side effect this check must")
                print("not have; the reason for each is above and, for the capture")
                print("gates, was measured here.")

        if req_bad or (args.strict and opt_bad):
            if not req_bad:
                print("")
                print("--strict: every REQUIRED gate passed, but %d OPTIONAL gate(s)"
                      % len(opt_bad))
                print("did not. That is the only thing --strict changes, and it is why")
                print("it exists: it is the mode for a host that HAS the captures.")
            return 1

        print("")
        print("OK: every REQUIRED gate returned 0.")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(130)
    except SystemExit:
        raise
    except BaseException as exc:
        # Exit 2: check-all.py could not run. A gate failing is exit 1, so this
        # is never confused with a red repo.
        print("check-all.py could not run: %s: %s" % (type(exc).__name__, exc),
              file=sys.stderr)
        sys.exit(2)