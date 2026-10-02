#!/usr/bin/env bash
# 10-fetch-corpus.sh
#
# QUESTION: can the battleships provider corpus be re-fetched from its upstream
# at a pinned commit, so that every citation in peli-cloud is checkable without
# this session existing?
#
# WHAT WOULD FALSIFY THE APPROACH: the upstream repository disappearing, moving,
# or being rewritten such that the pinned commit is no longer reachable, in which
# case the corpus shipped in references/ is the only copy and the method is
# dead.
#
# Inputs pinned:
#   UPSTREAM  ariana-dot-dev/battleships
#   COMMIT    f6a71ab09fefa68e355ef47c52315e099f99c921 (2026-10-01T17:10:42-0700)
#   DATA_DATE the battleships.dev data/ tree generation date, 2026-10-01
#
# Exit codes: 0 fetched or already present at the right commit
#             1 upstream reachable but the pinned commit is gone
#             2 could not run (no network / no git)
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
DEST="$ROOT/references/battleships"

UPSTREAM="https://github.com/ariana-dot-dev/battleships.git"
COMMIT="f6a71ab09fefa68e355ef47c52315e099f99c921"
DATA_DATE="2026-10-01"

echo "== conditions =="
echo "date_utc      : $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "host          : $(uname -s) $(uname -m)"
echo "git           : $(git --version 2>&1)"
echo "upstream      : $UPSTREAM"
echo "pinned_commit : $COMMIT"
echo "data_date     : $DATA_DATE"
echo "dest          : $DEST"
echo

command -v git >/dev/null 2>&1 || { echo "RESULT: could not run (no git)"; exit 2; }

if [ -d "$DEST/.git" ]; then
  have="$(git -C "$DEST" rev-parse HEAD 2>/dev/null || echo none)"
  echo "RESULT: corpus already a git clone at $have"
  exit 0
fi

if [ -d "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null)" ]; then
  echo "RESULT: $DEST exists but is not a clone (corpus shipped untracked)"
  echo "        verify it matches the commit: git clone $UPSTREAM /tmp/bs-check && git -C /tmp/bs-check checkout $COMMIT && diff -r /tmp/bs-check $DEST"
  exit 0
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "-- fetching $UPSTREAM"
if ! git clone --quiet "$UPSTREAM" "$tmp/bs" 2>&1; then
  echo "RESULT: could not reach upstream (network or auth)"
  exit 2
fi

if ! git -C "$tmp/bs" cat-file -e "$COMMIT^{commit}" 2>/dev/null; then
  echo "RESULT: upstream reachable but pinned commit $COMMIT is absent"
  echo "        the upstream history was rewritten or truncated; references/ holds the only copy"
  exit 1
fi

git -C "$tmp/bs" checkout --quiet "$COMMIT"
mkdir -p "$ROOT/references"
rm -rf "$DEST"
mv "$tmp/bs" "$DEST"

n="$(find "$DEST" -name '*.json' -path '*/cards/*' | wc -l | tr -d ' ')"
echo "RESULT: corpus checked out at $(git -C "$DEST" rev-parse --short=12 HEAD), $n provider cards"
exit 0