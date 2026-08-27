#!/usr/bin/env bash
# SessionStart hook: inject the toolkit's global instructions as additionalContext.
# Runs on startup|resume|clear|compact so the rules survive compaction.
# Off switch: TOOLKIT_INSTRUCTIONS_DISABLE=1
set -u
[ "${TOOLKIT_INSTRUCTIONS_DISABLE:-0}" = "1" ] && exit 0

root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
global="$root/instructions/global.md"
fleet="$root/instructions/fleet-brief.md"
[ -f "$global" ] || exit 0

body=$(sed "s|{{FLEET_BRIEF}}|$fleet|g" "$global")
jq -n --arg c "<GLOBAL_INSTRUCTIONS source=\"toolkit plugin\">
$body
</GLOBAL_INSTRUCTIONS>" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
exit 0
