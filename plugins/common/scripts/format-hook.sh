#!/usr/bin/env bash
# Auto-format the file Claude just wrote or edited (PostToolUse: Edit|Write).
# Picks a formatter by extension, prefers project-local tools, and never fails
# the tool call: missing formatters and formatter errors are swallowed.
#
#   .rs                  cargo fmt (repo Cargo.toml) or rustfmt
#   .go                  goimports or gofmt
#   .swift               swift-format if the repo has .swift-format, else swiftformat
#   .dart                dart format
#   .py                  ruff format or black
#   web/config/markdown  prettier (node_modules/.bin > PATH > npx --yes)
#
# Off switches:
#   FORMAT_HOOK_DISABLE=1          — disable everywhere
#   touch <repo>/.no-format-hook   — disable for one repo
set -u

[ "${FORMAT_HOOK_DISABLE:-0}" = "1" ] && exit 0

f=$(jq -r '.tool_response.filePath // .tool_input.file_path // empty' 2>/dev/null)
[ -n "$f" ] && [ -f "$f" ] || exit 0

dir=$(dirname "$f")
root=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null || echo "$dir")
[ -e "$root/.no-format-hook" ] && exit 0

has() { command -v "$1" >/dev/null 2>&1; }
quiet() { "$@" >/dev/null 2>&1 || true; }

prettier_bin() {
  if [ -x "$root/node_modules/.bin/prettier" ]; then echo "$root/node_modules/.bin/prettier"
  elif has prettier; then echo prettier
  elif has npx; then echo "npx --yes prettier"
  fi
}

case "$f" in
  *.rs)
    if [ -f "$root/Cargo.toml" ] && has cargo; then
      quiet cargo fmt --manifest-path "$root/Cargo.toml" -- "$f"
    elif has rustfmt; then
      quiet rustfmt "$f"
    fi ;;
  *.go)
    if has goimports; then quiet goimports -w "$f"
    elif has gofmt; then quiet gofmt -w "$f"; fi ;;
  *.swift)
    if [ -f "$root/.swift-format" ] && has swift-format; then
      quiet swift-format format --in-place "$f"
    elif has swiftformat; then
      quiet swiftformat "$f"
    elif has swift-format; then
      quiet swift-format format --in-place "$f"
    fi ;;
  *.dart)
    has dart && quiet dart format "$f" ;;
  *.py)
    if has ruff; then quiet ruff format "$f"
    elif has black; then quiet black -q "$f"; fi ;;
  *.js|*.cjs|*.mjs|*.jsx|*.ts|*.cts|*.mts|*.tsx|*.json|*.jsonc|*.json5|*.css|*.scss|*.sass|*.less|*.html|*.vue|*.svelte|*.md|*.mdx|*.yaml|*.yml|*.graphql|*.gql)
    p=$(prettier_bin)
    [ -n "$p" ] && quiet $p --write --ignore-unknown "$f" ;;
esac

exit 0
