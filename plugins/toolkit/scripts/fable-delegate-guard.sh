#!/usr/bin/env bash
# Force direct coding out of a fable-model main session (PreToolUse: Edit|Write).
# Fable is a poor fit for hands-on coding. When fable-track.sh has recorded
# the current session's model as fable, deny direct Edit/Write calls and
# push the work onto a subagent instead — model-guard.sh keeps that
# subagent off fable in turn, so the actual edit lands on sonnet/haiku.
#
# Unknown/missing tracked state fails open (allow): we'd rather miss a
# fable edit than block normal editing when we can't tell the model.
#
# Off switches:
#   FABLE_GUARD_DISABLE=1                — disable everywhere (shared with fable-track.sh)
#   touch <repo>/.no-fable-delegate-guard — disable for one repo
set -u

[ "${FABLE_GUARD_DISABLE:-0}" = "1" ] && exit 0

input="$(cat 2>/dev/null || true)"
session_id=$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)
[ -n "$session_id" ] || exit 0

STATE_DIR="${FABLE_GUARD_STATE_DIR:-$HOME/.claude/hooks/toolkit/fable-guard}"
model=""
[ -f "$STATE_DIR/$session_id" ] && model=$(cat "$STATE_DIR/$session_id" 2>/dev/null)
[ -n "$model" ] || exit 0

case "$model" in
  *[Ff][Aa][Bb][Ll][Ee]*)
    cwd=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
    root=$(git -C "${cwd:-.}" rev-parse --show-toplevel 2>/dev/null || echo "${cwd:-.}")
    [ -e "$root/.no-fable-delegate-guard" ] && exit 0
    reason='This session is running on fable, which should not edit code directly. Delegate this change to a subagent instead: use the Agent tool with model: "sonnet" (or "haiku" for a trivial mechanical edit).'
    jq -n --arg reason "$reason" \
      '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $reason}}'
    ;;
esac

exit 0
