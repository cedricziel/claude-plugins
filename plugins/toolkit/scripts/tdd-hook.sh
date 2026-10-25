#!/usr/bin/env bash
# PostToolUse(Edit|Write) TDD nudge (toolkit plugin, wired via hooks/hooks.json).
#   - Source edit while no test changed on the branch or in the working tree:
#     ask for a failing test first, once per file per session.
#   - First test-file edit in a session: point at the test-hygiene skills.
# Silent outside git repos and on config, generated, and vendored files.
# Off: TDD_NUDGE_DISABLE=1, or a `.no-tdd-nudge` file at the repo root.
set -u
[ "${TDD_NUDGE_DISABLE:-0}" = "1" ] && exit 0

if [ "${1:-}" = "codex" ]; then
  export TDD_STATE_DIR="${TDD_STATE_DIR:-${CODEX_HOME:-$HOME/.codex}/hooks/toolkit/tdd}"
fi
input=$(cat)
if [ "$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null)" = "apply_patch" ]; then
  hook_script="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
  cwd=$(printf '%s' "$input" | jq -r '.cwd // empty')
  [ -n "$cwd" ] && cd "$cwd" 2>/dev/null || exit 0
  contexts=$(
    while IFS= read -r f; do
      [[ "$f" = /* ]] || f="$PWD/$f"
      [ -f "$f" ] || continue
      printf '%s' "$input" | jq --arg f "$f" '.tool_name="Edit" | .tool_input={file_path:$f}' | bash "$hook_script"
    done < <(printf '%s' "$input" | jq -r '.tool_input.command // "" | split("\n")[] | select(test("^\\*\\*\\* (Add File: |Update File: |Move to: )")) | sub("^\\*\\*\\* (Add File: |Update File: |Move to: )"; "")' 2>/dev/null)
  )
  [ -n "$contexts" ] && printf '%s' "$contexts" | jq -s '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:(map(.hookSpecificOutput.additionalContext) | join("\n"))}}'
  exit 0
fi
IFS=$'\t' read -r f session < <(printf '%s' "$input" | jq -r '[.tool_input.file_path // "", .session_id // "none"] | @tsv' 2>/dev/null)
[ -n "${f:-}" ] || exit 0
session="$(printf '%s' "${session:-}" | tr -cd 'A-Za-z0-9_-')"; session="${session:-none}"
state="${TDD_STATE_DIR:-${HOME:+$HOME/.claude/hooks/toolkit/tdd}}"
[ -n "$state" ] || exit 0

# True the first time KEY is seen in this session; false if state can't be kept.
once() {
  grep -qxF "$1" "$state/$session" 2>/dev/null && return 1
  { mkdir -p "$state" && echo "$1" >>"$state/$session"; } 2>/dev/null
}

say() {
  jq -n --arg c "TDD: $1" '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
  exit 0
}

is_test_path() {
  case "$1" in
    *__tests__*|*_test.*|*.test.*|*.spec.*|test_*|*/test_*|*Tests.swift|*Test.java|*Test.kt|*_spec.rb|tests/*|*/tests/*|test/*|*/test/*|spec/*|*/spec/*|e2e/*|*/e2e/*) return 0 ;;
    *) return 1 ;;
  esac
}

is_source_path() {
  case "$1" in
    *.ts|*.tsx|*.js|*.jsx|*.mjs|*.py|*.rs|*.go|*.swift|*.dart|*.php|*.rb|*.java|*.kt|*.scala|*.cs|*.ex|*.exs|*.vue|*.svelte|*.c|*.cc|*.cpp|*.sh) return 0 ;;
    *) return 1 ;;
  esac
}

is_exempt_path() {
  case "$1" in
    *.config.*|*.d.ts|*.pb.go|*_pb2.py|*/migrations/*|migrations/*|*/generated/*|*/vendor/*|vendor/*|*/node_modules/*) return 0 ;;
    *) return 1 ;;
  esac
}

# Paths changed on this branch since the default branch, plus uncommitted ones.
changed_paths() {
  base="$(cd "$root" && "${BASH_SOURCE%/*}/default-branch.sh" 2>/dev/null)"
  git -C "$root" diff --name-only "$base...HEAD" 2>/dev/null
  git -C "$root" status --porcelain 2>/dev/null | sed 's/^...//; s/.* -> //'
}

is_source_path "$f" || exit 0
root="$(git -C "$(dirname "$f")" rev-parse --show-toplevel 2>/dev/null)" || exit 0
[ -e "$root/.no-tdd-nudge" ] && exit 0
rel="${f#"$root"/}"
if is_test_path "$rel"; then
  once "test-hygiene" && say "test file changed. Keep only tests that would catch a real regression, and no tautologies: use test-strategy to pick the level and writing-tests for red-first discipline."
  exit 0
fi
is_exempt_path "$rel" && exit 0
grep -qxF "src:$rel" "$state/$session" 2>/dev/null && exit 0

while IFS= read -r p; do
  [ -n "$p" ] && is_test_path "$p" && exit 0
done <<EOF
$(changed_paths)
EOF
once "src:$rel" && say "source changed, no test changed on this branch yet. Write a failing test first (writing-tests), or say why existing tests cover this."
exit 0
