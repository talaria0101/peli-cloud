#!/bin/sh
# assert-passwd-name.sh - the passwd line's first field must be the NAME the
# operator logs in with.
#
# Both cells of the 2x2 are driven over the live relay, because the rule is
# real and its refusal has TWO distinct log lines, so a clause that matches
# either string proves nothing on its own. Measured 2026-10-02:
#
#   passwd line names `subjectname`, ssh offers `subjectname`
#       -> "Pubkey auth succeeded for 'subjectname'", exit 0
#   passwd line names `someoneelse`,  ssh offers `subjectname`
#       -> "no entry for that name", exit 255
#
# Exactly one word differs between the two runs. A control whose name also
# exists in the system passwd database cannot show this: here every login is
# uid 0 and "root" exists in the shim's database, so a control that only
# removed the file entry would still authenticate for the wrong reason.
#
# This file exists rather than an inline `sh -c` because a clause this long
# needs quoting that survives; getting that wrong produces a syntax error in
# the suite, which reads as a suite failure rather than as a quoting mistake.
set -u
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OL="$ROOT/tests/one-login.sh"
[ -r "$OL" ] || { echo "assert-passwd-name: no $OL" >&2; exit 1; }

LOGIN=subjectname

# --- subject: the line names the login ssh will offer ------------------------
a=$(sh "$OL" "$LOGIN" 2>&1)
case "$a" in
  *"SERVER_SAW=Pubkey auth succeeded for"*"$LOGIN"* ) : ;;
  *) echo "assert-passwd-name: subject did not authenticate" >&2
     echo "$a" >&2; exit 1 ;;
esac
case "$a" in
  *"LOGIN_OK=0"*) : ;;
  *) echo "assert-passwd-name: subject exit code was not 0" >&2
     echo "$a" >&2; exit 1 ;;
esac

# --- control: same login, only the passwd line's name differs ---------------
c=$(PASSWD_NAME=someoneelse sh "$OL" "$LOGIN" 2>&1)
case "$c" in
  *"SERVER_SAW=no entry for that name"*|\
  *"SERVER_SAW=Login attempt for nonexistent user"*) : ;;
  *) echo "assert-passwd-name: control did not fail as claimed" >&2
     echo "$c" >&2; exit 1 ;;
esac
case "$c" in
  *"LOGIN_OK=0"*) echo "assert-passwd-name: the control authenticated, so it is not a control" >&2
                  exit 1 ;;
esac

echo "assert-passwd-name: ok (subject authenticated, control refused by name)"
exit 0