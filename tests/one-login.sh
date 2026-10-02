#!/bin/sh
# one-login.sh - serve exactly one relay session and log in once, with the
# login NAME under the caller's control. Both halves of the passwd-name rule
# are drivable from here, and the caller asserts on them.
#
# Usage: sh tests/one-login.sh <login-name> [work-dir]
#   PASSWD_NAME=<n>  writes the passwd line under this name instead of the
#                    login name, which is how the mismatch cell is expressed:
#                    the only difference between two runs is one word.
#   work-dir must already hold dropssh, dropbear, dropbearkey, fakepwd.so,
#   hostkey and ak/ (tools/ssh-relay-check.sh builds those).
#
# Exit 0 only when a real login ran. Prints, one per line, so a caller can grep:
#   LOGIN_OK=<exit code>
#   SERVER_SAW=<the server's verdict line>
# Tokens are never printed.
set -eu

LOGIN=${1:?usage: one-login.sh <login-name> [work-dir]}
# The name the passwd LINE carries. Defaults to the login name; the mismatch
# cell overrides it so that exactly one word differs between a passing and a
# failing run.
PASSWD_NAME=${PASSWD_NAME:-$LOGIN}
WORK=${2:-"$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)/.dropssh-check"}
RELAY="${DROPSSH_RELAY:-tcp.ssh.relay.ajam.dev}"
umask 077

cd "$WORK"
for f in dropssh dropbear fakepwd.so hostkey ak/authorized_keys; do
  [ -r "$f" ] || { echo "LOGIN_OK=99 SERVER_SAW=missing $f"; exit 1; }
done

# The passwd line names THIS uid (dropbear refuses a login whose uid differs
# from the server's) and its first field is PASSWD_NAME, which is the thing
# under test. The home is owned by the login user, which /tmp is not.
ME_UID=$(id -u); ME_GID=$(id -g 2>/dev/null || echo "$ME_UID")
mkdir -p home
printf '%s:x:%s:%s:test:%s/home:/bin/sh\n' "$PASSWD_NAME" "$ME_UID" "$ME_GID" "$WORK" > passwd.probe
echo "PASSWD_LINE=$(cut -d: -f1 passwd.probe) SSH_LOGIN=$LOGIN"

# An operator key the login will actually offer. ssh-keygen itself needs a
# passwd entry for this uid, which is what the shim supplies.
rm -f ak/probe ak/probe.pub
LD_PRELOAD="$WORK/fakepwd.so" SANDHOME_PASSWD="$WORK/passwd.probe" \
  ssh-keygen -q -t ed25519 -N '' -f ak/probe
cp ak/probe.pub ak/authorized_keys
chmod 600 ak/authorized_keys

./dropssh pair --relay "$RELAY" > pair.probe 2>/dev/null || { echo "LOGIN_OK=98 SERVER_SAW=pair failed"; exit 1; }
NAME=$(awk '/^name /{print $2}' pair.probe)
NODE=$(awk '/^node /{print $5}' pair.probe)
CONN=$(awk '/^connect /{print $5}' pair.probe)
[ -n "$NAME" ] && [ -n "$NODE" ] && [ -n "$CONN" ] || { echo "LOGIN_OK=97 SERVER_SAW=pair shape"; exit 1; }

setsid env LD_PRELOAD="$WORK/fakepwd.so" SANDHOME_PASSWD="$WORK/passwd.probe" \
  ./dropssh serve --relay "$RELAY" --name "$NAME" --token "$NODE" \
  --server "./dropbear -i -E -F -r $WORK/hostkey -D $WORK/ak -Y $WORK/passwd.probe" \
  --once --retry-budget 3 </dev/null >/dev/null 2>serve.probe.log &
SERVE_PID=$!
sleep 3

set +e
LD_PRELOAD="$WORK/fakepwd.so" SANDHOME_PASSWD="$WORK/passwd.probe" timeout 40 ssh \
  -o "ProxyCommand=$WORK/dropssh connect --relay $RELAY --name $NAME --token $CONN" \
  -i "$WORK/ak/probe" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -o BatchMode=yes -o ConnectTimeout=20 \
  "$LOGIN"@"$NAME" 'printf "MARK:%s" "$(id -u)"' >marker.probe 2>/dev/null
RC=$?
set -e
kill "$SERVE_PID" 2>/dev/null || true
wait "$SERVE_PID" 2>/dev/null || true

SAW=$(grep -oE 'Pubkey auth succeeded for .[a-zA-Z0-9._-]+.|no entry for that name|Login attempt for nonexistent user' serve.probe.log 2>/dev/null | tail -1)
echo "LOGIN_OK=$RC"
echo "SERVER_SAW=${SAW:-<no verdict line>}"
echo "MARKER=$(cat marker.probe 2>/dev/null)"
[ "$RC" = 0 ] || exit 1
exit 0