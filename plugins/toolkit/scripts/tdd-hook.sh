#!/usr/bin/env bash
# TDD hooks for Claude Code (shipped by the toolkit plugin, wired via hooks/hooks.json).
#   tdd-hook.sh edit-check  — PostToolUse(Edit|Write): nudge when source changes lack any test change
#   tdd-hook.sh stop-check  — Stop: block finishing while the project's test suite fails
# Both modes no-op silently outside git repos or in projects with no recognized test setup.
# stop-check only blocks on a genuine red suite; timeouts, low disk, an
# already-running build, or environment errors (ENOSPC/OOM) downgrade to a
# non-blocking user warning. A `.tdd-test-cmd` file at the repo root overrides
# the auto-detected test command (first line, e.g. "cargo nextest run").
set -u

MODE="${1:-stop-check}"
INPUT="$(cat 2>/dev/null || true)"
STATE_DIR="${TDD_STATE_DIR:-$HOME/.claude/hooks/toolkit/tdd}"
mkdir -p "$STATE_DIR"

jqr() { printf '%s' "$INPUT" | jq -r "$1" 2>/dev/null; }

# Non-blocking outcome: surface a warning to the user, let the turn end.
warn_skip() {
  jq -n --arg m "$1" '{systemMessage: ("TDD: " + $m)}'
  exit 0
}

is_test_path() {
  case "$1" in
    *__tests__*|*_test.*|*.test.*|*.spec.*|test_*|*/test_*|*Tests.swift|*Test.java|*Test.kt|*_spec.rb|tests/*|*/tests/*|test/*|*/test/*|spec/*|*/spec/*) return 0 ;;
    *) return 1 ;;
  esac
}

is_source_path() {
  case "$1" in
    *.ts|*.tsx|*.js|*.jsx|*.mjs|*.py|*.rs|*.go|*.swift|*.dart|*.php|*.rb|*.java|*.kt|*.c|*.cc|*.cpp|*.h) return 0 ;;
    *) return 1 ;;
  esac
}

if [ "$MODE" = "edit-check" ]; then
  f="$(jqr '.tool_input.file_path // empty')"
  [ -n "$f" ] || exit 0
  is_source_path "$f" || exit 0
  is_test_path "$f" && exit 0
  dir="$(dirname "$f")"
  git -C "$dir" rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
  while IFS= read -r line; do
    [ -n "$line" ] && is_test_path "${line:3}" && exit 0
  done <<EOF
$(git -C "$dir" status --porcelain 2>/dev/null)
EOF
  jq -n '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:"TDD: source changed, no test file touched yet. Write a failing test first, or say why existing tests cover this."}}'
  exit 0
fi

# ---- stop-check ----
# No-op: test suite running is now a manual decision.
exit 0
