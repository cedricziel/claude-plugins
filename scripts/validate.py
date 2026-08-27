#!/usr/bin/env python3
"""Structural validation for this Claude Code plugin marketplace.

Usage: validate.py [REPO_ROOT]   (defaults to the repository containing this script)
Exits non-zero and prints one line per problem.
"""
import json
import os
import re
import sys
from pathlib import Path

problems = []


def err(msg):
    problems.append(msg)


def load_json(path):
    if not path.is_file():
        err(f"missing {path}")
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        err(f"invalid JSON in {path}: {e}")
        return None


def require(obj, keys, where):
    for k in keys:
        if not obj.get(k):
            err(f"{where}: missing required field '{k}'")


def check_skill(skill_md):
    text = skill_md.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(f"{skill_md}: no YAML frontmatter")
        return
    fm = m.group(1)
    for key in ("name", "description"):
        if not re.search(rf"^{key}:\s*\S", fm, re.M):
            err(f"{skill_md}: frontmatter missing '{key}'")


def check_hooks(plugin_dir):
    hooks_json = plugin_dir / "hooks" / "hooks.json"
    if not hooks_json.exists():
        return
    data = load_json(hooks_json)
    if data is None:
        return
    events = data.get("hooks", {})
    if not isinstance(events, dict):
        err(f"{hooks_json}: 'hooks' must be an object keyed by event")
        return
    for event, groups in events.items():
        for group in groups:
            for hook in group.get("hooks", []):
                if hook.get("type") != "command":
                    continue
                cmd = hook.get("command", "")
                for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s\"']+)", cmd):
                    script = plugin_dir / ref
                    if not script.is_file():
                        err(f"{hooks_json}: {event} references missing script {ref}")
                    elif not os.access(script, os.X_OK):
                        err(f"{hooks_json}: {ref} is not executable")


def check_plugin(root, entry):
    name = entry.get("name", "?")
    source = entry.get("source", "")
    plugin_dir = (root / source).resolve()
    if not plugin_dir.is_dir():
        err(f"plugin '{name}': source directory {source} does not exist")
        return
    manifest = load_json(plugin_dir / ".claude-plugin" / "plugin.json")
    if manifest is None:
        return
    require(manifest, ("name", "version", "description"), f"{plugin_dir}/.claude-plugin/plugin.json")
    if manifest.get("name") != name:
        err(f"plugin '{name}': plugin.json name '{manifest.get('name')}' does not match marketplace entry")
    if manifest.get("version") != entry.get("version"):
        err(f"plugin '{name}': version mismatch marketplace={entry.get('version')} plugin.json={manifest.get('version')}")

    for skill_md in sorted((plugin_dir / "skills").glob("*/SKILL.md")):
        check_skill(skill_md)
    for cmd in sorted((plugin_dir / "commands").glob("*.md")):
        if not cmd.read_text().strip():
            err(f"{cmd}: empty command file")
    check_hooks(plugin_dir)


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    marketplace = load_json(root / ".claude-plugin" / "marketplace.json")
    if marketplace is not None:
        require(marketplace, ("name", "owner", "plugins"), "marketplace.json")
        for entry in marketplace.get("plugins", []):
            require(entry, ("name", "source", "description", "version"), f"marketplace.json plugin '{entry.get('name', '?')}'")
            check_plugin(root, entry)

    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s)")
        return 1
    print(f"ok: {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
