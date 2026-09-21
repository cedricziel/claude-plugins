import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATE = ROOT / "scripts" / "validate.py"


def run(root):
    return subprocess.run([sys.executable, str(VALIDATE), str(root)], capture_output=True, text=True)


def make_repo(tmp):
    """Minimal valid marketplace with one plugin."""
    (tmp / ".claude-plugin").mkdir()
    (tmp / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
        "name": "t", "owner": {"name": "x"},
        "plugins": [{"name": "p", "source": "./plugins/p", "description": "d", "version": "1.0.0"}],
    }))
    p = tmp / "plugins" / "p"
    (p / ".claude-plugin").mkdir(parents=True)
    (p / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "p", "version": "1.0.0", "description": "d"}))
    (p / "skills" / "s").mkdir(parents=True)
    (p / "skills" / "s" / "SKILL.md").write_text("---\nname: s\ndescription: d\n---\nbody\n")
    (p / "commands").mkdir()
    (p / "commands" / "c.md").write_text("# c\n")
    (p / "hooks").mkdir()
    (p / "scripts").mkdir()
    (p / "scripts" / "h.sh").write_text("#!/bin/sh\n")
    os.chmod(p / "scripts" / "h.sh", 0o755)
    (p / "hooks" / "hooks.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [
        {"type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/scripts/h.sh\" x"}]}]}}))
    (p / "workflows").mkdir()
    (p / "workflows" / "w.js").write_text("export const meta = { name: 'w', description: 'd' }\n")
    return p


class ValidateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.plugin = make_repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_valid_repo_passes(self):
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_real_repo_passes(self):
        r = run(ROOT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_plugin_source_fails(self):
        shutil.rmtree(self.plugin / ".claude-plugin")
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("plugin.json", r.stdout)

    def test_skill_without_frontmatter_fails(self):
        (self.plugin / "skills" / "s" / "SKILL.md").write_text("no frontmatter\n")
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("SKILL.md", r.stdout)

    def test_hook_script_missing_fails(self):
        (self.plugin / "scripts" / "h.sh").unlink()
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("h.sh", r.stdout)

    def test_hook_script_not_executable_fails(self):
        os.chmod(self.plugin / "scripts" / "h.sh", 0o644)
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("executable", r.stdout)

    def test_empty_command_fails(self):
        (self.plugin / "commands" / "c.md").write_text("")
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("c.md", r.stdout)

    def test_workflow_without_meta_fails(self):
        (self.plugin / "workflows" / "w.js").write_text("const x = 1\n")
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("w.js", r.stdout)

    def test_workflow_name_must_match_filename(self):
        (self.plugin / "workflows" / "w.js").write_text("export const meta = { name: 'other', description: 'd' }\n")
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("w.js", r.stdout)

    def test_name_mismatch_fails(self):
        (self.plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "other", "version": "1.0.0", "description": "d"}))
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("name", r.stdout)


def add_codex(tmp, plugin, version="1.0.0"):
    (plugin / ".codex-plugin").mkdir()
    (plugin / ".codex-plugin" / "plugin.json").write_text(json.dumps({"name": "p", "version": version, "description": "d"}))
    (tmp / ".agents" / "plugins").mkdir(parents=True)
    (tmp / ".agents" / "plugins" / "marketplace.json").write_text(json.dumps({
        "name": "t",
        "plugins": [{"name": "p", "source": {"source": "local", "path": "./plugins/p"}}],
    }))


class CodexValidateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.plugin = make_repo(self.tmp)
        add_codex(self.tmp, self.plugin)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_valid_codex_marketplace_passes(self):
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_codex_manifest_fails(self):
        shutil.rmtree(self.plugin / ".codex-plugin")
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(".codex-plugin", r.stdout)

    def test_codex_version_must_match_claude_manifest(self):
        add_codex_manifest = self.plugin / ".codex-plugin" / "plugin.json"
        add_codex_manifest.write_text(json.dumps({"name": "p", "version": "9.9.9", "description": "d"}))
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("version", r.stdout)

    def test_codex_source_must_be_relative_and_exist(self):
        path = self.tmp / ".agents" / "plugins" / "marketplace.json"
        path.write_text(json.dumps({"name": "t", "plugins": [{"name": "p", "source": {"source": "local", "path": "./plugins/nope"}}]}))
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("nope", r.stdout)

    def test_codex_plugin_must_exist_in_claude_marketplace(self):
        path = self.tmp / ".agents" / "plugins" / "marketplace.json"
        path.write_text(json.dumps({"name": "t", "plugins": [{"name": "ghost", "source": {"source": "local", "path": "./plugins/p"}}]}))
        r = run(self.tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ghost", r.stdout)


if __name__ == "__main__":
    unittest.main()
