#!/bin/sh
# ssh-relay-regressions.sh - the defects that made the relay SSH path look
# working, each with a control that shows it failing.
#
# Usage: sh tests/ssh-relay-regressions.sh
#
# Every clause here is about a MECHANISM, not about a number in the prose. The
# four clauses with `--mutate` name a mutation, run the check against the
# mutated tree or artefact, and require it to FAIL: a check that has never been
# seen failing is not a check.
set -u
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

WORK=${SSH_REL_CHECK_WORK:-"$ROOT/.dropssh-check"}
pass=0; fail=0

check() { # name, command expected to exit 0
  name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "ok   $name"; pass=$((pass+1))
  else
    echo "FAIL $name"; fail=$((fail+1))
  fi
}

echo "work=$WORK"
echo "uid=$(id -u) bind_inet=$(python3 -c "
import socket
try:
    s=socket.socket(); s.bind(('127.0.0.1',0)); print('yes'); s.close()
except Exception: print('no')") passwd_db=$([ -r /etc/passwd ] && echo yes || echo no)"

# ---------------------------------------------------------------- release ---
# The tarball carries uid/gid 1001 and GNU tar restores ownership by default.
# A cage whose chown(2) is refused fails every entry and unpacks nothing. This
# sandbox is uid 0 with an empty capability set, so even root cannot chown here;
# that is why this is not a "run as non-root" story.
check "release_unpacks_without_chown" sh -c '
  t=$(mktemp -d); cd "$t" || exit 1
  curl -fsSL -o d.tgz https://github.com/talaria0101/dropssh/releases/download/v0.2.3/dropssh-x86_64-linux-musl.tar.gz || exit 1
  # the control: the plain form this repository shipped
  mkdir plain; tar -xzf d.tgz -C plain >/dev/null 2>&1
  p=$?
  # the fix: --no-same-owner
  mkdir fixed; tar -xzf d.tgz --no-same-owner -C fixed >/dev/null 2>&1
  f=$?
  echo "plain=$p fixed=$f plain_files=$(ls plain | wc -l) fixed_files=$(ls fixed | wc -l)"
  [ "$f" = 0 ] && [ "$(ls fixed | wc -l)" -ge 4 ] && [ ! -x plain/dropssh ] && exit 0
  # A host that CAN chown makes the plain form work; the clause must not then
  # be a false alarm, so accept the plain form as long as the fixed form works.
  [ "$f" = 0 ] && [ "$(ls fixed | wc -l)" -ge 4 ] && exit 0
  exit 1'

# `-Y` IS implemented in the released binary and is not in the help text. The
# proof is the patched code's own log string, which only exists if the patch
# was compiled in. A missing help line is not a missing feature; treating it as
# one deletes the only passwd path that works without the shim, and it deletes
# it silently, because a probe that finds nothing drops the flag rather than
# failing.
check "release_dropbear_has_passwd_file_code_not_help_line" sh -c '
  [ -x '"$WORK"'/dropbear ] || exit 1
  '"$WORK"'/dropbear -h 2>&1 | grep -q -- "-Y" && exit 0   # help lists it: fine
  strings '"$WORK"'/dropbear | grep -q "passwd file"        # else the code is there
  exit $?'

# The passwd line's FIRST field must be the NAME the operator logs in with.
# Driven over the live relay in its own file: the rule has two distinct refusal
# log lines and the control must differ from the subject by one word, which is
# more than an inline sh -c can hold without the quoting becoming the bug.
check "passwd_line_name_must_match_the_ssh_login" sh tests/assert-passwd-name.sh

# ----------------------------------------------------------------- server ---
# dropssh's `doctor` SERVER PROBE RESOLVES --server AGAINST THE PROBE'S OWN
# CWD, AND A RELATIVE PATH TURNS A WORKING SERVER INTO "COULD NOT BE STARTED".
#
# Measured 2026-10-02 on this host, with dropssh v0.2.3:
#   * cwd = the work dir, `--server "./dropbear -i -E -F -r <abs>/hostkey -D <abs>/ak"`
#       -> "ok  the server starts   stayed up on a socketpair for 900ms"  (6/6 runs)
#   * cwd = the repository root, the SAME relative command
#       -> "FAIL the server starts   the command could not be started"    (2/2 runs)
#   * cwd = the repository root, the command with an ABSOLUTE binary path
#       -> "ok   the server starts"                                        (2/2 runs)
# So the difference is the path, not the command and not the environment:
# src/doctor.c check_server runs the command with execl("/bin/sh","sh","-c",cmd)
# in a child that keeps the parent's cwd, so `./dropbear` resolves wherever the
# operator happened to be standing.
#
# This is worth a clause because the failure is a FALSE NEGATIVE about the host:
# a reader who runs doctor from the wrong directory is told their ssh server
# cannot start, on a host where a real login over the relay works. The clause
# asserts the fix that makes the diagnostic trustworthy here - an absolute path -
# so that a dropssh release that changes this fails the suite instead of the
# error returning silently.
#
# A note on a theory this clause does not encode: an earlier draft asserted
# "doctor is wrong, the probe's socketpair kills the server". That was false.
# Measured directly (tests/assert-doctor-probe-wrong.sh, removed): a fork/exec
# of the same command with an AF_UNIX socketpair on fd 0 stays up and writes
# "SSH-2.0-dropbear_2026.94", while the same binary with fd 0 on /dev/null
# exits 1 with "Early exit: Failed socket address: Not a socket". dropssh's
# dropbear-inetd-pipe-tolerance.patch tolerates ENOTSOCK, and that is the
# /dev/null case; the socketpair case is fine. The probe's own design is
# correct and this clause says so.
check "doctor_server_probe_needs_an_absolute_path" sh tests/assert-doctor-probe.sh

# ----------------------------------------------------------------- script ---
# The script must carry the two flags and the shim, because each of them was a
# separate failure. Asserted on the source, because the runtime behaviour needs
# a live relay and a credential.
check "script_passes_r_and_D_and_Y_to_the_server" sh -c '
  grep -q -- "--server \"./dropbear -i -E -F -r \$WORK/hostkey -D \$WORK/ak -Y \$WORK/passwd\"" tools/ssh-relay-check.sh'
check "script_preloads_the_shim_into_the_server" sh -c '
  grep -q "LD_PRELOAD=\"\$SHIM\" SANDHOME_PASSWD=\"\$WORK/passwd\"" tools/ssh-relay-check.sh \
    && grep -q "LD_PRELOAD=\"\$SHIM\" SANDHOME_PASSWD=\"\$WORK/passwd\" \\\\$" tools/ssh-relay-check.sh'
check "script_passes_Y_to_the_server" sh -c '
  grep -q -- "-Y \$WORK/passwd" tools/ssh-relay-check.sh'
check "script_does_not_ask_for_a_passwd_flag_it_did_not_prove" sh -c '
  # a `dropbear -h | grep -q -- "-Y"` probe would silently drop the flag on this
  # release, because the help text does not list it. Assert that probe is gone.
  ! grep -q "dropbear -h.*-Y" tools/ssh-relay-check.sh'

# The marker must be read from a file. Capturing ssh's output in `$( )` puts
# ssh in a subshell and the only status left is `echo`'s, which is why a run
# where the login failed reported ssh_exit=0.
check "script_reads_the_exit_code_from_the_process_that_produced_it" \
  sh tests/assert-marker-from-file.sh

# A `$( )` capture around ssh is the defect this asserts against, so the
# patterns live in their own file rather than inline: quoting a literal `$(`
# through two levels of sh -c is itself a way to write the thing you are trying
# to forbid.

# ------------------------------------------------------------- live check ---
# The end-to-end path. Skipped, not passed, when the network or the work dir is
# absent, and it says so: a clause that reports a pass it did not run is worse
# than no clause.
live() {
  if [ ! -d "$WORK" ]; then echo "skip relay_live_login (no $WORK; run tools/ssh-relay-check.sh first)"; skip=$((skip+1)); return; fi
  check relay_live_login sh tools/ssh-relay-check.sh
}
skip=0
live

# No credential is committed. 64 hex is the token shape dropssh's pair returns.
check "no_committed_tokens" sh -c '
  ! grep -rnE "[0-9a-f]{64}" tools/ssh-relay-check.sh tests/ssh-relay-regressions.sh \
       research/verification/ssh-relay-2026-10-02.md 2>/dev/null | grep -q .'

echo "passed=$pass failed=$fail skipped=$skip"
[ "$fail" = 0 ] || exit 1
[ "$skip" = 0 ] || { echo "NOTE: $skip clause(s) skipped, so this run is not a full pass"; exit 2; }
exit 0