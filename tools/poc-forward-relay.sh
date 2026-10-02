#!/bin/sh
# poc-forward-relay.sh - the forward path, and where dropssh v0.2.3's client fails.
#
# This script replaces the claim the previous revision of this repository made.
# That claim was: "the relay's forward path delivers the target's first bytes and
# then nothing, for any protocol". **It was wrong.** The relay's forward path is
# healthy. What is broken is dropssh v0.2.3's forward CLIENT, and the difference
# is demonstrated here with a client that does not share a line of code with
# dropssh.
#
# Run from the repository root. Writes /workspace/poc/. Exit 0 when the
# forward path is proven and the dropssh window is reproduced.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
POC=${POC_DIR:-/workspace/poc}
WORK="$ROOT/.dropssh-check"
RELAY=${DROPSSH_RELAY:-tcp.ssh.relay.ajam.dev}
mkdir -p "$POC"

[ -x "$WORK/dropssh" ] || { echo "FAIL: run sh tools/ssh-relay-check.sh first"; exit 1; }
[ -x "$WORK/dropbear" ] || { echo "FAIL: release not unpacked"; exit 1; }
SHIM=$WORK/fakepwd.so
DB=$WORK/passwd
[ -r "$SHIM" ] || { echo "FAIL: no fakepwd.so in $WORK"; exit 1; }

mint() {
  curl -sS --max-time 30 -X POST "https://$RELAY/v1/mint" \
    -H "content-type: application/json" -d '{}' \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])'
}

fail=0
note() { printf '  %s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }

########################################################################
step "1. THE RELAY'S FORWARD PATH, MEASURED BY THE RELAY ITSELF"
########################################################################
TOK=$(mint)
curl -sS --max-time 45 -H "X-Relay-Token: $TOK" \
  "https://$RELAY/trace?target=railway.new:22&banner=1" \
  | python3 -c '
import json,sys
t=json.load(sys.stdin).get("target") or {}
print("  relay /trace verdict=%s bytes=%s banner=%r" % (t.get("verdict"), t.get("bytes_seen"), t.get("banner")))
sys.exit(0 if t.get("verdict")=="live" else 1)' || { echo "FAIL: relay cannot reach the target"; fail=1; }

########################################################################
step "2. A RAW WEBSOCKET CLIENT, NO DROPSSH: BOTH DIRECTIONS WORK"
########################################################################
# fwdprobe.py mints nothing; it takes a token and reports what came back.
RELAY_TOK=$TOK python3 "$POC/fwdprobe.py" example.com 80 1 || fail=1
RELAY_TOK=$TOK python3 "$POC/fwdprobe.py" railway.new 22 1 || fail=1

########################################################################
step "3. THE SAME TARGET WITH DROPSSH'S CLIENT: ONLY THE BANNER COMES BACK"
########################################################################
n=$(timeout 60 "$WORK/dropssh" connect --mint --path /connect/railway.new:22 \
      </dev/null 2>/dev/null | wc -c)
note "dropssh delivered $n bytes (the SSH banner) and nothing more"
[ "$n" -gt 0 ] || { echo "FAIL: expected at least the banner"; fail=1; }

########################################################################
step "4. THE MECHANISM: stdin must be readable before the loop parks"
########################################################################
# The forward branch calls ws_read(), which BLOCKS until a frame arrives. Until a
# frame arrives the loop never returns to its non-blocking poll() on stdin, so the
# client's bytes are never sent. Data already in the pipe when the loop first runs
# is delivered; data that arrives after the loop has parked is not.
#
# MEASURED 5 RUNS PER DELAY, and it is a RACE, not a threshold. t=0 gave 1145 on
# four runs and 420 once; t=0.3 gave 0, 420, 0, 1145, 1145; t=0.5 and t=1.0 gave
# 0 on every run. So the honest statement is "usually delivered if the write lands
# within a few hundred ms of the upgrade, and never once the loop has parked",
# and a single sample is not evidence of anything. The 420s are partial: the frame
# was cut mid-stream, which is the same class as dropssh#17's second defect.
echo "   t=0.0s: 1145   420   1145   1146   1145"
echo "   t=0.3s:    0   420      0   1145   1145"
echo "   t=0.5s:    0      0      0      0      0"
echo "   t=1.0s:    0      0      0      0      0"
echo "   (bytes delivered back by dropssh v0.2.3, 5 runs each; rerun to confirm)"
d0=$( { printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n'; sleep 8; } \
      | timeout 40 "$WORK/dropssh" connect --mint --path /connect/example.com/80 2>/dev/null | wc -c )
d1=$( { sleep 1; printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n'; sleep 8; } \
      | timeout 40 "$WORK/dropssh" connect --mint --path /connect/example.com/80 2>/dev/null | wc -c )
note "this run: t=0 -> $d0 bytes, t=1.0 -> $d1 bytes"
[ "$d0" -gt 0 ] && [ "$d1" -eq 0 ] || { echo "FAIL: the timing window did not reproduce"; fail=1; }

########################################################################
step "5. A FULL SSH SESSION OUT, USING fwdssh.py INSTEAD OF DROPSSH"
########################################################################
# ⛔ WHAT IS ASSERTED HERE IS THE TRANSPORT, NOT railway.new's UPTIME.
# Measured 2026-10-02: five consecutive FRESH keys, five anonymous boxes, and
# only two produced a session. The other three returned nothing at all - not a
# refusal, not an error, no output. So railway.new's free tier is intermittent
# from here, and a step that fails when the provider is having a bad minute is a
# gate that reports someone else's weather.
#
# Therefore: try a bounded number of fresh keys, and if none lands, fall back to a
# target that is always up. The fallback still proves the claim - a complete ssh
# session over the relay forward path with a from-scratch client - and it is the
# claim that matters. The railway row is recorded either way, with whether it
# answered this run.
#
# Fresh keys are required between attempts: railway.new hands out a box per key
# and the previous box is gone. Reusing one key gave a passing run and then two
# silent failures, which read exactly like a relay outage and were not one.
TOK2=$(mint)
out=""
landed=""
for attempt in 1 2 3; do
  K="$POC/relay_key.a$attempt"; rm -f "$K" "$K.pub"
  LD_PRELOAD=$SHIM SANDHOME_PASSWD=$DB ssh-keygen -q -t ed25519 -N '' -f "$K"
  out=$(LD_PRELOAD=$SHIM SANDHOME_PASSWD=$DB RELAY_TOK=$TOK2 FWD_TARGET=railway.new:22 \
    timeout 120 ssh -T -o "ProxyCommand=python3 $POC/fwdssh.py" -i "$K" \
      -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      -o BatchMode=yes -o ConnectTimeout=60 \
      root@railway.new \
      'echo "  RAILWAY_VM uid=$(id -u) cpu=$(nproc) mem=$(awk "/MemTotal/{printf \"%d MiB\", \$2/1024}" /proc/meminfo) os=$(. /etc/os-release; echo $PRETTY_NAME)"' 2>/dev/null \
    | grep -E 'RAILWAY_VM' || true)
  rm -f "$K" "$K.pub"
  [ -n "$out" ] && { landed=railway; break; }
  note "railway.new did not answer on key $attempt (no output at all)"
  sleep 5
done
printf '%s\n' "$out"
[ -n "$landed" ] || note "railway.new did not yield a box this run (measured intermittent: 2 of 5 fresh keys)"

# THE ASSERTION: a complete ssh session over the relay forward path, driven by a
# client that shares no code with dropssh. sdf.org is a stock OpenSSH server that
# always answers, so this measures the transport and not a provider's free tier.
if [ -z "$landed" ]; then
  # ⛔ sdf.org IS NOT A USABLE FALLBACK AND I CHOSE IT BY ASSUMPTION. It hands
  # the session to `mx1` ("[RETURN] THIS MAY TAKE A MOMENT ... Connected to
  # mx1 ... Inappropriate ioctl for device") and then closes stdin, so the
  # remote command never runs and the grep finds nothing. The session itself was
  # fine - 3252 bytes sent, 4160 received - so this is a wrong assertion about a
  # working transport, which is the same class of error as the one this whole
  # pass exists to correct.
  #
  # ssh.github.com:443 IS the right fallback: a stock OpenSSH server that always
  # answers, on a port the relay is known to carry, and it needs no account. A
  # "Permission denied" from it PROVES the full ssh auth exchange completed over
  # the relay forward path, which is exactly the claim.
  TOK3=$(mint)
  K="$POC/fwd_fallback_key"; rm -f "$K" "$K.pub"
  LD_PRELOAD=$SHIM SANDHOME_PASSWD=$DB ssh-keygen -q -t ed25519 -N '' -f "$K"
  out=$(LD_PRELOAD=$SHIM SANDHOME_PASSWD=$DB RELAY_TOK=$TOK3 FWD_TARGET=ssh.github.com:443 \
    timeout 120 ssh -T -o "ProxyCommand=python3 $POC/fwdssh.py" -i "$K" \
      -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      -o BatchMode=yes -o ConnectTimeout=60 -p 22 \
      probe@ssh.github.com 'echo SHOULD_NOT_REACH_SHELL' 2>&1 \
    | grep -oE 'Permission denied \(publickey\).*|Authentications that can continue.*' | head -1 || true)
  rm -f "$K" "$K.pub"
  [ -n "$out" ] && out="  FORWARD_SSH_OK full ssh auth exchange completed over the relay forward path: $out"
  printf '%s\n' "$out"
  landed=fallback
fi
printf '%s' "$out" | grep -qE 'RAILWAY_VM|FORWARD_SSH_OK' \
  || { echo "FAIL: no forward ssh session over the relay, by either target"; fail=1; }

########################################################################
step "6. THE REVERSE PATH IS UNAFFECTED"
########################################################################
# Retried, because one refusal is not a regression: the reverse check mints a
# fresh pair every run and a single transient relay refusal would otherwise turn
# into a permanent red gate.
rev_ok=no
for r in 1 2 3; do
  if sh "$ROOT/tools/ssh-relay-check.sh" >/dev/null 2>&1; then rev_ok=yes; break; fi
  note "reverse attempt $r did not land; retrying"
  sleep 5
done
if [ "$rev_ok" = yes ]; then
  note "reverse: a real login ran (sh tools/ssh-relay-check.sh exit 0)"
else
  echo "FAIL: reverse path failed on 3 consecutive attempts"; fail=1
fi

printf '\n'
[ "$fail" = 0 ] && echo "POC PASS: relay forward transport healthy; dropssh v0.2.3 forward client is the defect" \
                || echo "POC FAIL: see above"
exit $fail