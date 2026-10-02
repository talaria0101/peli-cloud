#!/bin/sh
# assert-doctor-probe.sh - dropssh `doctor`'s server probe resolves a relative
# --server against the probe's own cwd, so a relative path turns a working
# server into "the command could not be started".
#
# Measured 2026-10-02 on this host, dropssh v0.2.3:
#   cwd = work dir,  ./dropbear -i -E -F -r <abs>/hostkey -D <abs>/ak
#       -> ok, "stayed up on a socketpair for 900ms"                     (6/6)
#   cwd = repo root, the SAME relative command
#       -> FAIL, "the command could not be started"                     (2/2)
#   cwd = repo root, the command with an ABSOLUTE binary path
#       -> ok, "stayed up on a socketpair for 900ms"                     (2/2)
#
# src/doctor.c check_server execs the command with execl("/bin/sh","sh","-c",cmd)
# in a child that keeps the parent's cwd, so `./dropbear` resolves wherever the
# operator was standing. The subject and the control below differ in exactly
# that: one word, the binary's path, with the cwd held fixed.
#
# What this clause is FOR: the failure is a false negative about the host. A
# reader who runs doctor from the wrong directory is told their ssh server
# cannot start, on a machine where a real relay login works. The fix under test
# is the absolute path, so a future dropssh that regresses this fails here.
set -u
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
WORK=${SSH_REL_CHECK_WORK:-"$ROOT/.dropssh-check"}
[ -x "$WORK/dropssh" ] && [ -x "$WORK/dropbear" ] || {
  echo "assert-doctor-probe: release not unpacked in $WORK" >&2; exit 1; }

probe() { # cwd, server-command -> one line: ok | not-started | other
  ( cd "$1" || exit 1
    timeout 150 "$WORK/dropssh" doctor --server "$2" 2>&1 \
      | sed -n '/the ssh server/,/the relay/p' \
      | grep -oE 'stayed up on a socketpair|could not be started|exited immediately|was killed by signal' \
      | head -1 )
}

REL="./dropbear -i -E -F -r $WORK/hostkey -D $WORK/ak"
ABS="$WORK/dropbear -i -E -F -r $WORK/hostkey -D $WORK/ak"

# SUBJECT: relative path, cwd is where it resolves.
s=$(probe "$WORK" "$REL")
[ "$s" = "stayed up on a socketpair" ] || {
  echo "assert-doctor-probe: subject did not pass: [$s]" >&2; exit 1; }

# CONTROL: relative path, cwd is somewhere else. This is the false negative.
c=$(probe "$ROOT" "$REL")
[ "$c" = "could not be started" ] || {
  echo "assert-doctor-probe: control did not fail as claimed: [$c]" >&2; exit 1; }

# FIX: absolute path from the same wrong cwd.
f=$(probe "$ROOT" "$ABS")
[ "$f" = "stayed up on a socketpair" ] || {
  echo "assert-doctor-probe: the absolute path did not repair it: [$f]" >&2; exit 1; }

echo "assert-doctor-probe: ok (relative fails off-cwd, absolute works, relative works on-cwd)"
exit 0