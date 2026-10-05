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

body=$(cat "$shared" "$specific" | sed "s|{{FLEET_BRIEF}}|$fleet|g")
data="${CLAUDE_PLUGIN_DATA:-${PLUGIN_DATA:-}}"
if [ -n "$data" ]; then
  body="$body
Toolkit plugin data directory for the reflect skill: $data"
fi
jq -n --arg c "<GLOBAL_INSTRUCTIONS source=\"toolkit plugin\">
$body
</GLOBAL_INSTRUCTIONS>" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
exit 0
