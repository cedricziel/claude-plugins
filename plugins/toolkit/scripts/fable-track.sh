#!/usr/bin/env bash
# Track the current session's own model (SessionStart, PostModelSwitch).
# Hooks have no field reporting the main session's live model on most
# events — only SessionStart (sometimes) and PostModelSwitch (to_model)
# carry it. Record it per session_id so fable-delegate-guard.sh (PreToolUse:
# Edit|Write) can tell whether the orchestrating session itself is on fable.
#
# State lives outside the plugin dir since it must survive plugin updates
# and is per-session, not per-repo.
#
# Off switch:
#   FABLE_GUARD_DISABLE=1   — disable everywhere (also disables fable-delegate-guard.sh)
set -u

[ "${FABLE_GUARD_DISABLE:-0}" = "1" ] && exit 0

input="$(cat 2>/dev/null || true)"
session_id=$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)
[ -n "$session_id" ] || exit 0

model=$(printf '%s' "$input" | jq -r '.to_model // .model // empty' 2>/dev/null)
[ -n "$model" ] || exit 0

STATE_DIR="${FABLE_GUARD_STATE_DIR:-$HOME/.claude/hooks/toolkit/fable-guard}"
mkdir -p "$STATE_DIR"
printf '%s' "$model" > "$STATE_DIR/$session_id"

exit 0
