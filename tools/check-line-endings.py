#!/usr/bin/env python3
"""Refuse a tracked text file that has CRLF line endings.

    python3 tools/check-line-endings.py

Exit 0 when every tracked text file is LF-only, 1 otherwise.

WHY THIS EXISTS, MEASURED. Five files were committed with CRLF between
2026-10-06 and 2026-10-07 - data/anonymous-vms.json, experiments/96-
always-on-corrections.py, verify/claims.json, verify/probe-hosts.json and
verify/reachability.json - every one of them written from a Windows checkout.
`main` had none of them. The cost was not the bytes: it was that the six-row
correction in data/anonymous-vms.json rendered as a 988-line diff, because all
498 lines differed and not one of them differed in content. A diff that size is
a diff nobody reads, so the change it carried was reviewed by nobody.

.gitattributes now pins `text=auto eol=lf`, which makes the boundary mechanical
for future checkins. This tool is the other half: it reads what is COMMITTED
rather than what a checkout would produce, so a file that got in before the
attribute existed, or through a path that bypasses it, is still caught.

verify/pages/ is deliberately not checked. It is gitignored and holds
third-party HTML captured byte-for-byte; rewriting a vendor's bytes to suit this
repository's line endings would be the opposite of preserving them.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_EXT = (".json", ".md", ".py", ".sh", ".yml", ".yaml", ".txt", ".js", ".cfg",
            ".toml", ".gitignore", ".gitattributes")


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT,
                         capture_output=True)
    if out.returncode != 0:
        return None, "git ls-files failed; is this a git repository?"
    return [f for f in out.stdout.decode("utf-8").split("\0") if f], None


def main():
    files, err = tracked_files()
    if err:
        print(f"cannot run: {err}")
        return 2

    checked = 0
    bad = []
    for rel in files:
        if not rel.endswith(TEXT_EXT):
            continue
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as fh:
            data = fh.read()
        if b"\r" not in data:
            checked += 1
            continue
        n = data.count(b"\r\n")
        lone = data.count(b"\r") - n
        bad.append((rel, n, lone))
        checked += 1

    if not bad:
        print(f"ok line_endings: {checked} tracked text files are LF-only")
        return 0

    if "--fix" in sys.argv:
        fixed = 0
        for rel, _, _ in bad:
            with open(os.path.join(ROOT, rel), "rb") as fh:
                data = fh.read()
            with open(os.path.join(ROOT, rel), "wb") as fh:
                fh.write(data.replace(b"\r\n", b"\n"))
            fixed += 1
        print(f"normalised {fixed} file(s) to LF")
        return 0

    print(f"FAIL ({len(bad)}): tracked text files carrying CR")
    for rel, crlf, lone in bad:
        extra = f", plus {lone} lone CR" if lone else ""
        print(f" - {rel}: {crlf} CRLF{extra}")
    print("\nA CRLF file makes every later edit to it a whole-file diff, which is "
          "how a six-row correction\nbecame a 988-line one and went unread. Fix: "
          "`python3 tools/check-line-endings.py --fix`,\nor `dos2unix <file>`. "
          ".gitattributes pins this for future checkins.")
    return 1


if __name__ == "__main__":
    sys.exit(main())