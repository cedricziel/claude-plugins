#!/usr/bin/env bash
# Deny subagent spawns pinned to the Fable model (PreToolUse: Task|Agent).
# Fable is Claude Code's fast interactive model; it's too weak for
# unsupervised subagent work. This only rejects a call that names an
# explicit fable-family model id. A call with no `model` field is left
# alone — that's the normal way to invoke a subagent_type whose own
# frontmatter already sets `model:` (Explore, Plan, general-purpose, most
# custom agents), and blocking it would reject the common case instead of
# the risky one.
#
# Off switches:
#   MODEL_GUARD_DISABLE=1          — disable everywhere
#   touch <repo>/.no-model-guard   — disable for one repo
set -u

[ "${MODEL_GUARD_DISABLE:-0}" = "1" ] && exit 0

input=$(cat)
model=$(printf '%s' "$input" | jq -r '.tool_input.model // empty' 2>/dev/null)
[ -n "$model" ] || exit 0

case "$model" in
  *[Ff][Aa][Bb][Ll][Ee]*)
    cwd=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
    root=$(git -C "${cwd:-.}" rev-parse --show-toplevel 2>/dev/null || echo "${cwd:-.}")
    [ -e "$root/.no-model-guard" ] && exit 0
    reason='fable subagents are disallowed. Retry this Agent call with model: "sonnet" (haiku is fine for easy/mechanical tasks; opus for judgment-heavy ones).'
    jq -n --arg reason "$reason" \
      '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $reason}}'
    ;;
esac

exit 0
