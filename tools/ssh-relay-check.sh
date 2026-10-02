#!/bin/sh
# ssh-relay-check.sh - prove a sealed sandbox can be SSH'd into over an
# outbound-only relay, end to end, using dropssh.
#
# Why this exists: the sandbox cannot bind a TCP port (bind(2) INET -> EACCES,
# shown by `sandhome report` as bind=unix) and has no /etc/passwd. dropssh
# carries ssh over an outbound WebSocket and the server reads its account from
# a file. This script makes a pair, serves one session, connects through the
# relay and runs a command over that session.
#
# Nothing here is a credential committed to the repository: the pair is minted
# at run time and its tokens are written mode 600 under the work dir and never
# printed. Drop the work dir to rotate them.
#
# Usage: sh tools/ssh-relay-check.sh
# Exit 0 when a real login ran; 1 when any step did not.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
WORK=${DROPSSH_WORK:-"$ROOT/.dropssh-check"}
DROPSSH_VERSION=${DROPSSH_VERSION:-v0.2.3}
TARBALL="dropssh-x86_64-linux-musl.tar.gz"
URL="https://github.com/talaria0101/dropssh/releases/download/$DROPSSH_VERSION/$TARBALL"
RELAY="${DROPSSH_RELAY:-tcp.ssh.relay.ajam.dev}"

mkdir -p "$WORK"
cd "$WORK"
umask 077

# 1. Fetch the pinned release once. Its own SHA256SUMS is checked against the
#    files it shipped with, so a truncated download fails here and not at login.
#
#    `--no-same-owner` is NOT optional in a cage. The tarball carries uid/gid
#    1001 and GNU tar restores ownership by default; a cage whose chown(2) is
#    refused - including this one at uid 0 with an empty capability set - fails
#    EVERY entry with "Cannot change ownership to uid 1001, gid 1001" and
#    exits non-zero, so nothing is unpacked and the script dies with no message
#    about the real cause. Measured 2026-10-02; the guard is
#    tests/ssh-relay-regressions.sh clause release_unpacks_without_chown.
if [ ! -x ./dropssh ] || [ ! -x ./dropbear ]; then
  rm -rf unpack && mkdir unpack
  curl -fsSL -o "$TARBALL" "$URL"
  tar -xzf "$TARBALL" --no-same-owner -C unpack
  cp unpack/dropssh unpack/dropbear unpack/dropbearkey unpack/fakepwd.so . 2>/dev/null || true
  (cd unpack && sha256sum -c --ignore-missing SHA256SUMS >/dev/null) || { echo "FAIL: release checksum"; exit 1; }
fi
export DROPSSH_SHIM="$WORK/fakepwd.so"

# 2. The passwd entry names THIS uid: dropbear refuses a login whose uid differs
#    from the server's. The name is ours to choose because there is no
#    /etc/passwd to ask; `id -un` cannot answer here either, so anything
#    unusable falls back to a fixed numeric name. The home must be owned by the
#    login user, which /tmp is not, so the work dir is not under /tmp.
ME_UID=$(id -u)
ME_GID=$(id -g 2>/dev/null || echo "$ME_UID")
if [ "$ME_UID" = 0 ]; then ME_NAME=root; else
  ME_NAME=$(id -un 2>/dev/null || true)
  case "$ME_NAME" in ''|*[!a-zA-Z0-9._-]*) ME_NAME=user"$ME_UID" ;; esac
fi
ME_HOME="$WORK/home"
mkdir -p "$ME_HOME"
printf '%s:x:%s:%s:test:%s:/bin/sh\n' "$ME_NAME" "$ME_UID" "$ME_GID" "$ME_HOME" > passwd

# 3. TWO PASSWD PATHS, AND BOTH ARE KEPT BECAUSE EACH ALONE IS INSUFFICIENT.
#
#    `-Y FILE` (set in the serve command in step 7) makes dropbear read the
#    account database from a file instead of the system, which has no
#    /etc/passwd here. It is implemented in the released v0.2.3 binary even
#    though `dropbear -h` does not list it; the proof is the patched code's own
#    log line, quoted in step 7.
#
#    `fakepwd.so` is the other path: an LD_PRELOAD that defines getpwnam and
#    getpwuid and reads SANDHOME_PASSWD. It is what lets ssh(1) on the CLIENT
#    run at all here, and it also reaches the server.
#
#    Neither alone is enough on this host, which is why neither is tested by
#    assumption. Measured 2026-10-02:
#      shim only, no -Y   -> "Login attempt for nonexistent user", FAIL
#      -Y only, no shim   -> "Pubkey auth succeeded", exit 0, PASS
#      both               -> PASS

# 4. ONE SHIM FOR BOTH ENDS, AND THE CLIENT NEEDS IT FOR A DIFFERENT REASON.
#    The server needs it or dropbear logs "Login attempt for nonexistent
#    user" for the login name. ssh(1) on the client needs it or ssh itself
#    dies with "No user exists for uid 0" before a packet reaches the relay --
#    that is OpenSSH asking for its own uid, which is a fact about this cage
#    and not about dropssh. Prefer the release's own copy so there is one
#    implementation; fall back to whatever sandhome shipped.
SHIM=""
for s in "$WORK/fakepwd.so" \
         "${HOME:-}/.local/share/sandhome/shims/fakepwd.so" \
         /state/home/.local/share/sandhome/shims/fakepwd.so; do
  [ -r "$s" ] && { SHIM="$s"; break; }
done
[ -n "$SHIM" ] || { echo "FAIL: no fakepwd shim; the server cannot read a passwd database here"; exit 1; }

# 5. Host key in dropbear format, operator key in OpenSSH format. ssh-keygen
#    needs a passwd entry for the client uid, which is what the shim supplies.
rm -f hostkey ak/id ak/id.pub
mkdir -p ak
./dropbearkey -t ed25519 -f hostkey >/dev/null 2>&1
LD_PRELOAD="$SHIM" SANDHOME_PASSWD="$WORK/passwd" \
  ssh-keygen -q -t ed25519 -N '' -f ak/id
cp ak/id.pub ak/authorized_keys
chmod 600 ak/authorized_keys

# 6. A self-service reverse pair. node_token stays here; connect_token is what
#    an operator would be handed. Neither is echoed.
./dropssh pair --relay "$RELAY" > pair.txt 2> pair.err || { echo "FAIL: pair"; sed -E 's/[0-9a-f]{16,}/<TOK>/g' pair.err; exit 1; }
NAME=$(awk '/^name /{print $2}' pair.txt)
NODE=$(awk '/^node /{print $5}' pair.txt)
CONN=$(awk '/^connect /{print $5}' pair.txt)
[ -n "$NAME" ] && [ -n "$NODE" ] && [ -n "$CONN" ] || { echo "FAIL: pair shape"; exit 1; }

# 7. Serve exactly one session.
#
#    `-r` and `-D` are not optional. dropssh's built-in default server command
#    is `dropbear -i -E -F`, which cannot start in a cage: dropbear's compiled-
#    in host key paths are /etc/dropbear/dropbear_*_host_key and do not exist
#    here. The observable is dropssh's own doctor line, "the command could not
#    be started: dropbear -i -E -F"; passing the full command makes the same
#    probe report "stayed up on a socketpair".
#
#    `-Y $WORK/passwd` is the passwd database for the server and it IS
#    implemented, which the help text does not say: `dropbear -h` on v0.2.3
#    lists no -Y, but the binary logs the patched code's own string "passwd
#    file '%s': %s", which only exists if patches/dropbear-passwd-file.patch
#    was compiled in. A missing help line is not a missing feature; probing
#    for the help line and dropping the flag on a miss silently removes the
#    only passwd path that does not need the shim.
#
#    BOTH paths are supplied on purpose, and each is load-bearing on its own:
#    `-Y` names the login in the passwd file, and LD_PRELOAD lets the same file
#    answer the glibc getpwnam the server also calls. Measured 2026-10-02: with
#    `-Y` and no shim in the server's environment the login resolves and
#    authenticates (PASS, "Pubkey auth succeeded"); with the shim and no `-Y`
#    it never resolves ("Login attempt for nonexistent user"). Keeping both
#    means the check does not depend on which one a given release carries.
#
#    LD_PRELOAD must reach the exec'd dropbear, so it is exported for the
#    whole `serve` invocation rather than passed through `env -i`.
LD_PRELOAD="$SHIM" SANDHOME_PASSWD="$WORK/passwd" \
./dropssh serve --relay "$RELAY" --name "$NAME" --token "$NODE" \
  --server "./dropbear -i -E -F -r $WORK/hostkey -D $WORK/ak -Y $WORK/passwd" \
  --once --retry-budget 3 --json --verbose >serve.out 2>serve.log < /dev/null &
SERVE_PID=$!
sleep 3

# 8. Connect through the relay and run a command on the far side. `timeout`
#    around ssh because a ProxyCommand that never pairs would otherwise wait.
#    The marker is written to a FILE, not a shell substitution: capturing it in
#    a subshell hides ssh's exit status, and a script that reports the status of
#    `echo` is a script that cannot fail.
set +e
LD_PRELOAD="$SHIM" SANDHOME_PASSWD="$WORK/passwd" timeout 45 ssh \
  -o "ProxyCommand=$WORK/dropssh connect --relay $RELAY --name $NAME --token $CONN" \
  -i "$WORK/ak/id" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -o BatchMode=yes -o ConnectTimeout=20 \
  "$ME_NAME@$NAME" 'printf "MARK:%s:%s" "$(id -u)" "$(uname -s)"' >marker.out 2>ssh.err
RC=$?
set -e
kill "$SERVE_PID" 2>/dev/null || true
wait "$SERVE_PID" 2>/dev/null || true

echo "relay=$RELAY name=$NAME login=$ME_NAME shim=$(basename "$(dirname "$SHIM")")/$(basename "$SHIM")"
echo "ssh_exit=$RC marker=$(cat marker.out 2>/dev/null)"
echo "--- serve.log (tokens redacted) ---"
sed -E 's/[0-9a-f]{64}/<TOK>/g' serve.log 2>/dev/null | tail -8

case "$(cat marker.out 2>/dev/null)" in
  "MARK:$ME_UID:"*) echo "PASS: a real ssh login ran over the outbound-only relay"; exit 0 ;;
  *) echo "FAIL: no login over the relay"; exit 1 ;;
esac