#!/usr/bin/env bash
# Usage: upload-screenshots.sh <pr-branch> <image>...
# Commits images to the orphan branch `pr-assets` on origin, under <pr-branch>/,
# without touching the working tree or index. Prints one Markdown image line per
# file, pinned to the commit SHA, ready to paste into a PR body.
set -euo pipefail

[ $# -ge 2 ] || { echo "usage: $0 <pr-branch> <image>..." >&2; exit 2; }
branch=$1; shift
assets=pr-assets
dir=${branch//\//-}

url=$(git config --get remote.origin.url)
case $url in
  git@github.com:*) slug=${url#git@github.com:} ;;
  ssh://git@github.com/*) slug=${url#ssh://git@github.com/} ;;
  https://github.com/*) slug=${url#https://github.com/} ;;
  *) echo "origin is not a GitHub remote: $url" >&2; exit 1 ;;
esac
slug=${slug%.git}

parent=
if git fetch -q origin "refs/heads/$assets" 2>/dev/null; then
  parent=$(git rev-parse FETCH_HEAD)
fi

GIT_INDEX_FILE=$(mktemp -u)
export GIT_INDEX_FILE
trap 'rm -f "$GIT_INDEX_FILE"' EXIT
[ -z "$parent" ] || git read-tree "$parent"

for f in "$@"; do
  git update-index --add --cacheinfo "100644,$(git hash-object -w "$f"),$dir/$(basename "$f")"
done

commit=$(git commit-tree "$(git write-tree)" ${parent:+-p "$parent"} -m "Screenshots for $branch")
git push -q origin "$commit:refs/heads/$assets"

for f in "$@"; do
  name=$(basename "$f")
  echo "![${name%.*}](https://github.com/$slug/blob/$commit/$dir/$name?raw=true)"
done
