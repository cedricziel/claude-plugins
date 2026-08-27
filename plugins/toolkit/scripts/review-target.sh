#!/usr/bin/env bash
# Resolve a review target to a unified diff file.
#   review-target.sh <target> <out-file>
#   target: ""            working tree vs HEAD (staged + unstaged + untracked)
#           <number>      GitHub PR via `gh pr diff`
#           <branch>      branch vs merge-base with the default branch
# Prints "kind=<working-tree|pr|branch> base=<ref>" on stdout. Exits 1 on an empty diff.
set -euo pipefail
target="${1:-}"; out="${2:?out-file required}"

default_base() {
  git symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||' \
    || { git show-ref -q --verify refs/heads/main && echo main; } \
    || echo master
}

if [ -z "$target" ]; then
  { git diff HEAD; git ls-files --others --exclude-standard -z | xargs -0 -I{} git diff --no-index /dev/null {} 2>/dev/null || true; } > "$out"
  kind=working-tree; base=HEAD
elif [[ "$target" =~ ^[0-9]+$ ]]; then
  gh pr diff "$target" > "$out"
  kind=pr; base="pr/$target"
else
  base=$(default_base)
  git diff "$(git merge-base "$base" "$target")".."$target" > "$out"
  kind=branch
fi

if [ ! -s "$out" ]; then echo "review-target: empty diff for target '${target:-working tree}'" >&2; exit 1; fi
echo "kind=$kind base=$base lines=$(wc -l < "$out" | tr -d ' ')"
