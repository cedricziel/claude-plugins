#!/usr/bin/env bash
# SessionStart hook: inject the toolkit's global instructions as additionalContext.
# Runs on startup|resume|clear|compact so the rules survive compaction.
# Off switch: TOOLKIT_INSTRUCTIONS_DISABLE=1
set -u
[ "${TOOLKIT_INSTRUCTIONS_DISABLE:-0}" = "1" ] && exit 0

root="${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}}"
shared="$root/instructions/shared.md"
specific="$root/instructions/claude.md"
[ "${1:-}" = "codex" ] && specific="$root/instructions/codex.md"
fleet="$root/instructions/fleet-brief.md"
[ -f "$shared" ] && [ -f "$specific" ] || exit 0

# Suggest /reflect once a day on a fresh session when the last review is
# REFLECT_NUDGE_DAYS (default 7) old or missing. Off: REFLECT_NUDGE_DISABLE=1
reflect_nudge() {
  [ "${REFLECT_NUDGE_DISABLE:-0}" = "1" ] && return
  source=$(jq -r '.source // "startup"' 2>/dev/null)
  [ "$source" = "startup" ] || return
  days="${REFLECT_NUDGE_DAYS:-7}"
  case "$days" in "" | *[!0-9]*) days=7 ;; esac
  days=$((10#$days)); [ "$days" -ge 1 ] || days=7
  marker="$1/reflect/last-reviewed.json"
  if [ -f "$marker" ]; then
    [ -n "$(find "$marker" -mtime +"$((days - 1))" 2>/dev/null)" ] || return
    when="$days or more days ago"
  else
    when="never"
  fi
  state="${REFLECT_NUDGE_STATE_DIR:-${HOME:+$HOME/.claude/hooks/toolkit/reflect}}"
  [ -n "$state" ] || return
  today=$(date +%Y-%m-%d)
  [ "$(cat "$state/nudged" 2>/dev/null)" = "$today" ] && return
  { mkdir -p "$state" && echo "$today" >"$state/nudged"; } 2>/dev/null || return
  printf '\n%s' "- The last /reflect review ran $when. At a natural break, offer the user to run /reflect once; do not run it unasked."
}

body=$(cat "$shared" "$specific" | sed "s|{{FLEET_BRIEF}}|$fleet|g")
data="${CLAUDE_PLUGIN_DATA:-${PLUGIN_DATA:-}}"
if [ -n "$data" ]; then
  body="$body
Toolkit plugin data directory for the reflect skill: $data"
  body="$body$(reflect_nudge "$data")"
fi
jq -n --arg c "<GLOBAL_INSTRUCTIONS source=\"toolkit plugin\">
$body
</GLOBAL_INSTRUCTIONS>" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
exit 0
