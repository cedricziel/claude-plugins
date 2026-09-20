#!/usr/bin/env python3
"""Pin a Claude Code plugin marketplace to its latest commit in a settings file.

Creates the settings file, the marketplace entry, and the enabledPlugins entries
when they are missing; otherwise only moves the pinned sha forward.

Usage: update_settings.py --settings PATH --marketplace NAME --repo OWNER/REPO
           [--plugins a,b] [--ref REF] [--sha SHA]
Prints `changed=true|false`, `bootstrapped=true|false` and `sha=<sha>` on stdout.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def resolve_sha(repo, ref):
    """Latest commit of a branch or tag on GitHub; peeled tag beats tag beats branch."""
    out = subprocess.run(
        ["git", "ls-remote", f"https://github.com/{repo}.git",
         f"refs/heads/{ref}", f"refs/tags/{ref}", f"refs/tags/{ref}^{{}}"],
        check=True, capture_output=True, text=True,
    ).stdout
    found = {}
    for line in out.splitlines():
        sha, name = line.split("\t")
        found[name] = sha
    for name in (f"refs/tags/{ref}^{{}}", f"refs/tags/{ref}", f"refs/heads/{ref}"):
        if name in found:
            return found[name]
    raise SystemExit(f"ref '{ref}' not found in {repo}")


def update(settings, marketplace, repo, plugins, ref, sha):
    """Mutate settings in place; returns (changed, bootstrapped)."""
    markets = settings.setdefault("extraKnownMarketplaces", {})
    entry = markets.get(marketplace)
    bootstrapped = entry is None
    changed = bootstrapped

    if bootstrapped:
        source = {"source": "github", "repo": repo, "ref": ref, "sha": sha}
        markets[marketplace] = {"source": source}
    else:
        source = entry.setdefault("source", {})
        if source.get("source") != "github" or source.get("repo") != repo:
            raise SystemExit(
                f"marketplace '{marketplace}' already points at {source}, not github:{repo}"
            )
        if source.get("sha") != sha:
            source["sha"] = sha
            changed = True

    if bootstrapped:
        enabled = settings.setdefault("enabledPlugins", {})
        for plugin in plugins:
            enabled.setdefault(f"{plugin}@{marketplace}", True)

    return changed, bootstrapped


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--settings", default=".claude/settings.json")
    p.add_argument("--marketplace", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--plugins", default="")
    p.add_argument("--ref", default="main")
    p.add_argument("--sha", default="")
    args = p.parse_args()

    path = Path(args.settings)
    settings = json.loads(path.read_text()) if path.is_file() else {}
    sha = args.sha or resolve_sha(args.repo, args.ref)
    plugins = [x.strip() for x in args.plugins.split(",") if x.strip()]

    changed, bootstrapped = update(settings, args.marketplace, args.repo, plugins, args.ref, sha)
    if changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(settings, indent=2) + "\n")

    print(f"changed={str(changed).lower()}")
    print(f"bootstrapped={str(bootstrapped).lower()}")
    print(f"sha={sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
