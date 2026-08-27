#!/usr/bin/env bash
# Rebase reminder for Claude Code (shipped by the toolkit plugin, wired via hooks/hooks.json).
#   UserPromptSubmit: when the current branch has fallen behind the repo's
#   default branch, inject a note asking the agent to rebase before continuing.
#
# No-ops silently outside git repos, on the default branch itself, in detached
# HEAD, or while a rebase/merge/bisect is already in progress.
#
# Knobs (env):
#   REBASE_HOOK_BASE            base branch name (default: auto-detected, e.g. main)
#   REBASE_HOOK_FETCH_INTERVAL  seconds between `git fetch` calls   (default 900)
#   REBASE_HOOK_NAG_INTERVAL    seconds between repeat nudges       (default 1800)
#   REBASE_HOOK_MIN_BEHIND      commits behind before nudging       (default 1)
# Off switches:
#   touch ~/.claude/hooks/.rebase-state/paused   — disable everywhere
#   touch <repo>/.no-rebase-nudge                — disable for one repo
set -u

INPUT="$(cat 2>/dev/null || true)"
STATE_DIR="${REBASE_HOOK_STATE_DIR:-$HOME/.claude/hooks/.rebase-state}"
FETCH_INTERVAL="${REBASE_HOOK_FETCH_INTERVAL:-900}"
NAG_INTERVAL="${REBASE_HOOK_NAG_INTERVAL:-1800}"
MIN_BEHIND="${REBASE_HOOK_MIN_BEHIND:-1}"
mkdir -p "$STATE_DIR"

[ -f "$STATE_DIR/paused" ] && exit 0

jqr() { printf '%s' "$INPUT" | jq -r "$1" 2>/dev/null; }

# Seconds since a file was last written; huge number if it doesn't exist.
age_of() {
  [ -f "$1" ] || { echo 999999999; return; }
  local m
  m="$(stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null)"
  [ -n "$m" ] || { echo 999999999; return; }
  echo $(( $(date +%s) - m ))
}

TARGET="$(jqr '.cwd // empty')"
[ -n "$TARGET" ] || TARGET="${CLAUDE_PROJECT_DIR:-.}"
cd "$TARGET" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
[ -f "$ROOT/.no-rebase-nudge" ] && exit 0

# Mid-operation: the agent is already dealing with history, don't pile on.
GITDIR="$(git rev-parse --git-dir 2>/dev/null)"
for marker in rebase-merge rebase-apply MERGE_HEAD CHERRY_PICK_HEAD BISECT_LOG; do
  [ -e "$GITDIR/$marker" ] && exit 0
done

BRANCH="$(git symbolic-ref --quiet --short HEAD 2>/dev/null)" || exit 0
[ -n "$BRANCH" ] || exit 0

# ---- resolve the base branch ----
BASE="${REBASE_HOOK_BASE:-}"
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

REPO_KEY="$(printf '%s' "$ROOT" | shasum | cut -c1-12)"

# ---- refresh the remote-tracking ref, throttled ----
HAS_ORIGIN=0
git remote get-url origin >/dev/null 2>&1 && HAS_ORIGIN=1
if [ "$HAS_ORIGIN" = "1" ] && [ "$(age_of "$STATE_DIR/fetch-$REPO_KEY")" -ge "$FETCH_INTERVAL" ]; then
  TIMEOUT_BIN="$(command -v gtimeout || command -v timeout || true)"
  if [ -n "$TIMEOUT_BIN" ]; then
    "$TIMEOUT_BIN" 20 git fetch --quiet origin "+refs/heads/$BASE:refs/remotes/origin/$BASE" >/dev/null 2>&1
  else
    git fetch --quiet origin "+refs/heads/$BASE:refs/remotes/origin/$BASE" >/dev/null 2>&1
  fi
  : > "$STATE_DIR/fetch-$REPO_KEY"
fi

BASE_REF=""
if git show-ref --verify --quiet "refs/remotes/origin/$BASE"; then
  BASE_REF="origin/$BASE"
elif git show-ref --verify --quiet "refs/heads/$BASE"; then
  BASE_REF="$BASE"
fi
[ -n "$BASE_REF" ] || exit 0

BEHIND="$(git rev-list --count "HEAD..$BASE_REF" 2>/dev/null)" || exit 0
[ -n "$BEHIND" ] || exit 0
[ "$BEHIND" -ge "$MIN_BEHIND" ] 2>/dev/null || exit 0

# ---- nudge throttle: once per new upstream tip, or once per NAG_INTERVAL ----
BASE_SHA="$(git rev-parse --short "$BASE_REF" 2>/dev/null)"
NAG_FILE="$STATE_DIR/nag-$REPO_KEY-$(printf '%s' "$BRANCH" | shasum | cut -c1-8)"
LAST_SHA=""
[ -f "$NAG_FILE" ] && LAST_SHA="$(cat "$NAG_FILE" 2>/dev/null)"
if [ "$LAST_SHA" = "$BASE_SHA" ] && [ "$(age_of "$NAG_FILE")" -lt "$NAG_INTERVAL" ]; then
  exit 0
fi
printf '%s' "$BASE_SHA" > "$NAG_FILE"

AHEAD="$(git rev-list --count "$BASE_REF..HEAD" 2>/dev/null || echo 0)"
DIRTY=""
[ -n "$(git status --porcelain 2>/dev/null)" ] && DIRTY=" The working tree has uncommitted changes, so commit or stash them first."

MSG="Branch sync check: '$BRANCH' is $BEHIND commit(s) behind $BASE_REF (and $AHEAD ahead).$DIRTY Rebase onto the base branch before continuing so this work stays current and conflicts surface early: \`git fetch origin $BASE && git rebase $BASE_REF\`. If a rebase is unsafe or unwanted right now (shared branch, mid-review stack, deliberate divergence), skip it and say so in one line instead."

jq -n --arg m "$MSG" '{hookSpecificOutput:{hookEventName:"UserPromptSubmit",additionalContext:$m},suppressOutput:true}'
exit 0
