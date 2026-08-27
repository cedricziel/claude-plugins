#!/usr/bin/env bash
# Resolve an issue reference to forge, repo and number.
#   issue-ref.sh <ref>      ref: 123 | owner/repo#123 | https://<host>/owner/repo/issues/123
# Prints: forge=<github|forgejo> host=<host> repo=<owner/repo> number=<n> cli=<gh|fj>
# Bare numbers and owner/repo#N take the host from the origin remote of the cwd.
set -euo pipefail
ref="${1:?usage: issue-ref.sh <ref>}"

origin_host_repo() {
  local url; url=$(git remote get-url origin 2>/dev/null) || { echo "issue-ref: no origin remote to infer the forge from" >&2; exit 1; }
  url="${url%.git}"
  case "$url" in
    *://*) url="${url#*://}"; url="${url#*@}"; host="${url%%/*}"; repo="${url#*/}" ;;
    *@*:*) host="${url#*@}"; host="${host%%:*}"; repo="${url#*:}" ;;
    *) echo "issue-ref: cannot parse origin url '$url'" >&2; exit 1 ;;
  esac
}

if [[ "$ref" =~ ^https?://([^/]+)/([^/]+/[^/]+)/(issues|pulls?)/([0-9]+) ]]; then
  host="${BASH_REMATCH[1]}"; repo="${BASH_REMATCH[2]}"; number="${BASH_REMATCH[4]}"
elif [[ "$ref" =~ ^([^/#[:space:]]+/[^/#[:space:]]+)#([0-9]+)$ ]]; then
  origin_host_repo; repo="${BASH_REMATCH[1]}"; number="${BASH_REMATCH[2]}"
elif [[ "$ref" =~ ^#?([0-9]+)$ ]]; then
  origin_host_repo; number="${BASH_REMATCH[1]}"
else
  echo "issue-ref: unrecognised reference '$ref'" >&2; exit 1
fi

if [ "$host" = "github.com" ]; then forge=github; cli=gh; else forge=forgejo; cli=fj; fi
echo "forge=$forge host=$host repo=$repo number=$number cli=$cli"
