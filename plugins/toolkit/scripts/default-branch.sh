#!/usr/bin/env bash
# Print the repository's default branch: origin/HEAD → main → master.
set -euo pipefail
git symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||' \
  || { git show-ref -q --verify refs/heads/main && echo main; } \
  || echo master
