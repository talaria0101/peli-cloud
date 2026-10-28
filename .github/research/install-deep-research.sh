#!/usr/bin/env bash
# Install Weizhena/Deep-Research-skills into kage's user config directory.
#
#   .github/research/install-deep-research.sh [CONFIG_DIR]
#
# CONFIG_DIR defaults to ~/.config/kage. The upstream project documents Claude
# Code, OpenCode and Codex layouts; kage reads skills from <config>/skills/<name>/
# and agents from <config>/agents/*.md, so the English skill set goes to the
# first and the web-search agent to the second. Two upstream strings do not
# survive the move and are rewritten here:
#
#   * `~/.claude/...` paths inside the skills and the agent, which point at
#     Claude Code's directories. They become CONFIG_DIR paths.
#   * `python <path>` commands, which become `python3`; Ubuntu runners have no `python`.
#   * `model: opus` in the agent's frontmatter. kage skips an agent file whose
#     model is not `provider/model` or `inherit`, so it becomes `inherit`.
#
# DRS_REF pins the upstream commit. Bump it on purpose, after reading the diff.
set -euo pipefail

DRS_REPO="${DRS_REPO:-https://github.com/Weizhena/Deep-Research-skills.git}"
DRS_REF="${DRS_REF:-6ce38f60e3f8b22502c29873f96503a4e0c5addb}"
CFG="${1:-$HOME/.config/kage}"
SRC="$(mktemp -d)"
trap 'rm -rf "$SRC"' EXIT

git init -q "$SRC"
git -C "$SRC" fetch -q --depth 1 "$DRS_REPO" "$DRS_REF"
git -C "$SRC" checkout -q FETCH_HEAD
got="$(git -C "$SRC" rev-parse HEAD)"
if [ "$got" != "$DRS_REF" ]; then
  echo "pinned $DRS_REF but fetched $got" >&2
  exit 1
fi

mkdir -p "$CFG/skills" "$CFG/agents"
cp -r "$SRC"/skills/research-en/* "$CFG/skills/"
cp "$SRC/agents/web-search-agent.md" "$CFG/agents/web-search-agent.md"
rm -rf "$CFG/agents/web-search-modules"
cp -r "$SRC/agents/web-search-modules" "$CFG/agents/web-search-modules"

# Rewrite Claude Code paths and the model line, in the copies only.
grep -rlF '~/.claude/' "$CFG/skills" "$CFG/agents" | while read -r f; do
  sed -i "s#~/\\.claude/#$CFG/#g" "$f"
done
sed -i 's/^model: opus$/model: inherit/' "$CFG/agents/web-search-agent.md"
# The skills say `python`; the runner image provides python3 only.
grep -rlE '^python /' "$CFG/skills" | while read -r f; do
  sed -i 's#^python /#python3 /#' "$f"
done

if grep -rF '~/.claude' "$CFG/skills" "$CFG/agents" >/dev/null; then
  echo "a ~/.claude path survived the rewrite" >&2
  exit 1
fi
if ! grep -qx 'model: inherit' "$CFG/agents/web-search-agent.md"; then
  echo "agent model line was not rewritten" >&2
  exit 1
fi

if ! python3 -c 'import yaml' 2>/dev/null; then
  python3 -m pip install --quiet pyyaml
fi
python3 -c 'import yaml'
echo "deep-research-skills $got installed into $CFG"
