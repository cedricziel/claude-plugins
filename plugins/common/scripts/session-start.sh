#!/usr/bin/env bash
# SessionStart hook: inject common's baseline instructions as additionalContext.
# Runs on startup|resume|clear|compact so the rules survive compaction.
# Off switch: COMMON_INSTRUCTIONS_DISABLE=1
set -u
[ "${COMMON_INSTRUCTIONS_DISABLE:-0}" = "1" ] && exit 0

root="${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}}"
shared="$root/instructions/shared.md"
specific="$root/instructions/claude.md"
[ "${1:-}" = "codex" ] && specific="$root/instructions/codex.md"
[ -f "$shared" ] && [ -f "$specific" ] || exit 0

body=$(cat "$shared" "$specific")
jq -n --arg c "<GLOBAL_INSTRUCTIONS source=\"common plugin\">
$body
</GLOBAL_INSTRUCTIONS>" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
exit 0
