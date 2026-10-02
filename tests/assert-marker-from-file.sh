#!/bin/sh
# assert-marker-from-file.sh - the relay check must read ssh's exit status from
# ssh itself, and its marker from a file.
#
# The defect this forbids: `MARK=$( ... ssh ... )` puts ssh in a command
# substitution subshell, so `$?` afterwards is the status of the assignment -
# always 0. A run where the login failed therefore printed ssh_exit=0, and the
# script's own FAIL branch was unreachable through that path. Measured
# 2026-10-02 on this repository before the fix.
#
# These patterns live in their own file because a literal `$(` written through
# `sh -c '...'` inside the suite is itself a command substitution.
set -u
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT" || exit 1
f=tools/ssh-relay-check.sh

fail() { echo "assert-marker-from-file: FAIL $*" >&2; exit 1; }

grep -q 'marker.out' "$f" || fail "no marker file; the marker is captured in a subshell"
grep -q '^RC=$?' "$f"     || fail "the exit code is not read immediately after ssh"
grep -q '>marker.out 2>ssh.err' "$f" || fail "ssh does not write its marker to a file"

# Any `VAR=$(` on a line that also mentions ssh is the forbidden shape.
if grep -n 'ssh' "$f" | grep -q '=\$(.*timeout\|=\$(.*LD_PRELOAD'; then
  fail "a line assigns ssh output through a command substitution"
fi

# And the verdict must not be taken from a file that could be stale: the case
# statement reads the same file the run just wrote.
grep -q 'cat marker.out' "$f" || fail "the verdict does not re-read the marker file"
echo "assert-marker-from-file: ok"
exit 0