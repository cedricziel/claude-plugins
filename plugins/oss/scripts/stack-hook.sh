#!/usr/bin/env bash
# GitHub-native stack nudge for Claude, Codex, and OpenCode; pass `codex` or
# `opencode` to use that host's state.
#   UserPromptSubmit: when the current branch carries several commits on top of
#   the default branch, ask the agent to ship a GitHub native stack (`gh stack`)
#   instead of one oversized PR or a hand-rolled chain.
#
# No-ops silently outside git repos, on the default branch, in detached HEAD,
# while a rebase/merge/bisect is in progress, and below the commit threshold.
#
# Knobs (env):
#   STACK_HOOK_BASE            base branch name (default: auto-detected, e.g. main)
#   STACK_HOOK_MIN_COMMITS     commits ahead before nudging          (default 2)
#   STACK_HOOK_NAG_INTERVAL    seconds between repeat nudges         (default 1800)
# Off switches:
#   touch ~/.claude/hooks/oss/stack/paused                     — disable for Claude
#   touch ~/.codex/hooks/oss/stack/paused                      — disable for Codex
#   touch ~/.local/state/opencode/plugins/oss/stack/paused     — disable for OpenCode
#   touch <repo>/.no-stack-nudge                               — disable for one repo
set -u

INPUT="$(cat 2>/dev/null || true)"
HOST_STATE="$HOME/.claude/hooks/oss/stack"
case "${1:-}" in
  codex) HOST_STATE="${CODEX_HOME:-$HOME/.codex}/hooks/oss/stack" ;;
  opencode) HOST_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/opencode/plugins/oss/stack" ;;
esac
STATE_DIR="${STACK_HOOK_STATE_DIR:-$HOST_STATE}"
MIN_COMMITS="${STACK_HOOK_MIN_COMMITS:-2}"
NAG_INTERVAL="${STACK_HOOK_NAG_INTERVAL:-1800}"
mkdir -p "$STATE_DIR" 2>/dev/null || true

[ -f "$STATE_DIR/paused" ] && exit 0

jqr() { printf '%s' "$INPUT" | jq -r "$1" 2>/dev/null; }

# Seconds since a file was last written; huge number if it doesn't exist.
age_of() {
  [ -f "$1" ] || { echo 999999999; return; }
  local m
  m="$(stat -f %m "$1" 2>/dev/null)" || m="$(stat -c %Y "$1" 2>/dev/null)"
  [ -n "$m" ] || { echo 999999999; return; }
  echo $(( $(date +%s) - m ))
}

TARGET="$(jqr '.cwd // empty')"
[ -n "$TARGET" ] || TARGET="${CLAUDE_PROJECT_DIR:-.}"
cd "$TARGET" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
[ -f "$ROOT/.no-stack-nudge" ] && exit 0

# Mid-operation: the agent is already dealing with history, don't pile on.
GITDIR="$(git rev-parse --git-dir 2>/dev/null)"
for marker in rebase-merge rebase-apply MERGE_HEAD CHERRY_PICK_HEAD; do
  [ -e "$GITDIR/$marker" ] && exit 0
done

BRANCH="$(git symbolic-ref --quiet --short HEAD 2>/dev/null)" || exit 0
[ -n "$BRANCH" ] || exit 0

# ---- resolve the base branch ----
BASE="${STACK_HOOK_BASE:-}"
if [ -z "$BASE" ]; then
  BASE="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')"
fi
if [ -z "$BASE" ]; then
  for cand in main master; do
    if git show-ref --verify --quiet "refs/remotes/origin/$cand" || git show-ref --verify --quiet "refs/heads/$cand"; then
      BASE="$cand"; break
    fi
  done
fi
[ -n "$BASE" ] || exit 0
[ "$BRANCH" = "$BASE" ] && exit 0

BASE_REF=""
if git show-ref --verify --quiet "refs/remotes/origin/$BASE"; then
  BASE_REF="origin/$BASE"
elif git show-ref --verify --quiet "refs/heads/$BASE"; then
  BASE_REF="$BASE"
fi
[ -n "$BASE_REF" ] || exit 0

AHEAD="$(git rev-list --count "$BASE_REF..HEAD" 2>/dev/null)" || exit 0
[ -n "$AHEAD" ] || exit 0
[ "$AHEAD" -ge "$MIN_COMMITS" ] 2>/dev/null || exit 0

# ---- nudge throttle: once per head commit, and at most every NAG_INTERVAL ----
REPO_KEY="$(printf '%s' "$ROOT" | shasum | cut -c1-12)"
NAG_FILE="$STATE_DIR/nag-$REPO_KEY-$(printf '%s' "$BRANCH" | shasum | cut -c1-8)"
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null)"
LAST_SHA=""
[ -f "$NAG_FILE" ] && LAST_SHA="$(cat "$NAG_FILE" 2>/dev/null)"
if [ "$LAST_SHA" = "$HEAD_SHA" ] && [ "$(age_of "$NAG_FILE")" -lt "$NAG_INTERVAL" ]; then
  exit 0
fi
printf '%s' "$HEAD_SHA" > "$NAG_FILE"

STAT="$(git diff --shortstat "$BASE_REF...HEAD" 2>/dev/null | sed 's/^ *//')"
CHANGE=" $AHEAD commit(s) ahead of $BASE_REF"
[ -n "$STAT" ] && CHANGE="$CHANGE, $STAT"

MSG="Stack check: '$BRANCH' is$CHANGE. If that is more than one reviewable change, ship a GitHub native stack instead of one oversized PR or a hand-rolled chain: \`gh stack init\`, then \`gh stack add\` per layer, then \`gh stack submit\` (\`gh stack link\` adopts branches that already exist). Read the \`git-stacked-prs\` skill for splitting, ordering, and merge behavior. If this is genuinely one reviewable change, continue as a single PR and say so in one line."

jq -n --arg m "$MSG" '{hookSpecificOutput:{hookEventName:"UserPromptSubmit",additionalContext:$m},suppressOutput:true}'
exit 0
