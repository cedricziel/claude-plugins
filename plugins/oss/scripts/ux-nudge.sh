#!/usr/bin/env bash
# UX lint hook (oss plugin). Two modes:
#
#   ux-nudge.sh gate               PreToolUse(Edit|Write): block the four
#                                  unambiguous slop defects before they land.
#   ux-nudge.sh advise [host]      PostToolUse(Edit|Write) / apply_patch /
#                                  OpenCode execute.after: attach up to six
#                                  findings to the next model step, once each.
#
# Silent for non-UI files, outside git repos, and when python3 or jq is missing.
# Off switches: UX_LINT_DISABLE=1 or a .no-ux-lint file at the repo root.
set -u
[ "${UX_LINT_DISABLE:-0}" = "1" ] && exit 0

mode="${1:-advise}"
host="${2:-}"
case "$host" in
  codex) export UX_LINT_STATE_DIR="${UX_LINT_STATE_DIR:-${CODEX_HOME:-$HOME/.codex}/hooks/oss/ux}" ;;
  opencode) export UX_LINT_STATE_DIR="${UX_LINT_STATE_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/opencode/plugins/oss/ux}" ;;
esac
state="${UX_LINT_STATE_DIR:-${HOME:+$HOME/.claude/hooks/oss/ux}}"

here="$(cd "$(dirname "$0")" && pwd)"
lint="$here/../skills/ux-design/scripts/ux-lint.py"
command -v python3 >/dev/null 2>&1 || exit 0
command -v jq >/dev/null 2>&1 || exit 0
[ -f "$lint" ] || exit 0

is_ui() {
  case "$1" in
    *.html|*.htm|*.css|*.scss|*.sass|*.less|*.jsx|*.tsx|*.js|*.ts|*.vue|*.svelte|*.astro) return 0 ;;
    *) return 1 ;;
  esac
}

# True the first time KEY is seen in this session; false if state cannot be kept.
once() {
  [ -n "${state:-}" ] || return 0
  grep -qxF "$1" "$state/$session" 2>/dev/null && return 1
  { mkdir -p "$state" && echo "$1" >>"$state/$session"; } 2>/dev/null
  return 0
}

input=$(cat)
f=$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null)
session=$(printf '%s' "$input" | jq -r '.session_id // "none"' 2>/dev/null)

if [ "$mode" = "gate" ]; then
  text=$(printf '%s' "$input" | jq -r '.tool_input.content // .tool_input.new_string // empty' 2>/dev/null)
  [ -n "${f:-}" ] && [ -n "${text:-}" ] || exit 0
  is_ui "$f" || exit 0
  root="$(git -C "$(dirname "$f")" rev-parse --show-toplevel 2>/dev/null)" || exit 0
  [ -e "$root/.no-ux-lint" ] && exit 0

  findings="$(printf '%s' "$text" | python3 "$lint" --snippet --filename "$f" 2>/dev/null)"
  rc=$?
  [ "$rc" -eq 2 ] || exit 0
  {
    echo "ux-lint blocked this edit: a defect the ux-design skill treats as unambiguous."
    printf '%s\n' "$findings" | sed 's/^/  /'
    echo "Fix it in the same edit. If the project genuinely intends this, put 'ux-lint-ignore' on the preceding line and say why in your reply."
  } >&2
  exit 2
fi

# advise mode
if [ "$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null)" = "apply_patch" ]; then
  cwd=$(printf '%s' "$input" | jq -r '.cwd // empty')
  [ -n "$cwd" ] && cd "$cwd" 2>/dev/null || exit 0
  files=$(printf '%s' "$input" | jq -r '.tool_input.command // "" | split("\n")[] | select(test("^\\*\\*\\* (Add File: |Update File: |Move to: )")) | sub("^\\*\\*\\* (Add File: |Update File: |Move to: )"; "")' 2>/dev/null)
else
  files="${f:-}"
fi
[ -n "${files:-}" ] || exit 0
session="$(printf '%s' "${session:-}" | tr -cd 'A-Za-z0-9_-')"; session="${session:-none}"

body=""
while IFS= read -r f; do
  [ -n "$f" ] && [ -f "$f" ] || continue
  is_ui "$f" || continue
  root="$(git -C "$(dirname "$f")" rev-parse --show-toplevel 2>/dev/null)" || continue
  [ -e "$root/.no-ux-lint" ] && continue
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    once "$line" || continue
    body="${body}${line}"$'\n'
    [ "$(printf '%s' "$body" | wc -l)" -ge 6 ] && break 2
  done < <(python3 "$lint" "$f" 2>/dev/null)
done <<< "$files"

[ -n "${body:-}" ] || exit 0
context="<ux_findings>
${body}Fix these, or say in one line why this project intends it. Do not echo this list.
</ux_findings>"
jq -n --arg c "$context" '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
