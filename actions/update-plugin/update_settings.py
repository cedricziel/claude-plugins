#!/usr/bin/env python3
"""Pin a Claude Code plugin marketplace to its latest commit in a settings file.

Creates the settings file, the marketplace entry, and the enabledPlugins entries
when they are missing; otherwise only moves the pinned sha forward.

Usage: update_settings.py --settings PATH --marketplace NAME --repo OWNER/REPO
           [--plugins a,b] [--ref REF] [--sha SHA] [--session-hook]
Prints `changed=true|false`, `bootstrapped=true|false` and `sha=<sha>` on stdout,
plus `hook=<path>` when a session-start hook script was written.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9._-]+")
REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*")
SHA = re.compile(r"[0-9a-f]{40}")


def check(label, value, pattern):
    """Inputs end up in a committed shell script and in $GITHUB_OUTPUT, so allowlist them."""
    if not pattern.fullmatch(value):
        raise SystemExit(f"invalid {label}: {value!r}")


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


def hook_script(marketplace, repo, plugins):
    installs = "".join(f"claude plugin install {p}@{marketplace} >/dev/null 2>&1\n" for p in plugins)
    return (
        "#!/bin/bash\n"
        'if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then\n  exit 0\nfi\n\n'
        f"claude plugin marketplace add {repo} >/dev/null 2>&1\n"
        f"{installs}"
        "exit 0\n"
    )


def add_session_hook(settings, settings_path, marketplace, repo):
    """Write the install script if absent and register it under SessionStart.

    Returns the script path when anything was added, else None.
    """
    script = settings_path.parent / "hooks" / "install-claude-plugins.sh"
    command = f"$CLAUDE_PROJECT_DIR/{script}"
    added = False

    if not script.exists():
        suffix = f"@{marketplace}"
        plugins = [k[: -len(suffix)] for k, v in settings.get("enabledPlugins", {}).items()
                   if v and k.endswith(suffix)]
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(hook_script(marketplace, repo, plugins))
        script.chmod(0o755)
        added = True

    groups = settings.setdefault("hooks", {}).setdefault("SessionStart", [])
    if not any(h.get("command") == command for g in groups for h in g.get("hooks", [])):
        groups.append({"hooks": [{"type": "command", "command": command}]})
        added = True

    return script if added else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--settings", default=".claude/settings.json")
    p.add_argument("--marketplace", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--plugins", default="")
    p.add_argument("--ref", default="main")
    p.add_argument("--sha", default="")
    p.add_argument("--session-hook", action="store_true")
    args = p.parse_args()

    plugins = [x.strip() for x in args.plugins.split(",") if x.strip()]
    check("marketplace", args.marketplace, NAME)
    check("repo", args.repo, REPO)
    check("ref", args.ref, REF)
    if args.sha:
        check("sha", args.sha, SHA)
    for plugin in plugins:
        check("plugin", plugin, NAME)

    path = Path(args.settings)
    settings = json.loads(path.read_text()) if path.is_file() else {}
    sha = args.sha or resolve_sha(args.repo, args.ref)

    changed, bootstrapped = update(settings, args.marketplace, args.repo, plugins, args.ref, sha)
    hook = add_session_hook(settings, path, args.marketplace, args.repo) if args.session_hook else None
    changed = changed or hook is not None
    if changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(settings, indent=2) + "\n")

    print(f"changed={str(changed).lower()}")
    print(f"bootstrapped={str(bootstrapped).lower()}")
    print(f"sha={sha}")
    if hook:
        print(f"hook={hook}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
