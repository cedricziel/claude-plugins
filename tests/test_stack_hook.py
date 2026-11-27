import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import git, init_repo

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "oss"
HOOK = PLUGIN / "scripts" / "stack-hook.sh"


class StackHookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.repo = self.home / "repo"
        self.repo.mkdir()
        init_repo(self.repo)
        (self.repo / "file.txt").write_text("base\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "base")
        git(self.repo, "checkout", "-q", "-b", "stack")
        self.commit("one")
        self.commit("two")

    def commit(self, message, filename=None):
        if filename:
            (self.repo / filename).write_text(f"{message}\n")
            git(self.repo, "add", ".")
            git(self.repo, "commit", "-q", "-m", message)
        else:
            git(self.repo, "commit", "-q", "--allow-empty", "-m", message)

    def run_hook(self, host="codex", extra_env=None):
        if host == "opencode":
            command = ["bash", str(HOOK), "opencode"]
            shell = False
            timeout = 30
        else:
            config = PLUGIN / ("codex-hooks" if host == "codex" else "hooks") / "hooks.json"
            hook = json.loads(config.read_text())["hooks"]["UserPromptSubmit"][0]["hooks"][0]
            command = hook["command"]
            shell = True
            timeout = hook["timeout"]
        env = {k: v for k, v in os.environ.items() if not k.startswith(("STACK_HOOK_", "XDG_STATE_HOME"))}
        env.update({
            "HOME": str(self.home),
            "CODEX_HOME": str(self.home / ".codex"),
            "PLUGIN_ROOT": str(PLUGIN),
            "CLAUDE_PLUGIN_ROOT": str(PLUGIN),
        })
        env.update(extra_env or {})
        result = subprocess.run(
            command, shell=shell, cwd=self.home, input=json.dumps({"cwd": str(self.repo)}),
            env=env, capture_output=True, text=True, timeout=timeout,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_codex_reminds_and_throttles_in_its_own_state_directory(self):
        output = json.loads(self.run_hook())["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "UserPromptSubmit")
        self.assertIn("2 commit(s) ahead of main", output["additionalContext"])
        self.assertIn("gh stack", output["additionalContext"])
        self.assertIn("git-stacked-prs", output["additionalContext"])
        self.assertTrue((self.home / ".codex/hooks/oss/stack").is_dir())
        self.assertFalse((self.home / ".claude").exists())
        self.assertEqual(self.run_hook(), "")

    def test_opencode_reminds_and_throttles_in_its_own_state_directory(self):
        output = json.loads(self.run_hook("opencode"))["hookSpecificOutput"]
        self.assertIn("2 commit(s) ahead of main", output["additionalContext"])
        self.assertTrue((self.home / ".local/state/opencode/plugins/oss/stack").is_dir())
        self.assertFalse((self.home / ".codex").exists())
        self.assertFalse((self.home / ".claude").exists())
        self.assertEqual(self.run_hook("opencode"), "")

    def test_claude_still_emits_a_reminder(self):
        output = json.loads(self.run_hook("claude"))["hookSpecificOutput"]
        self.assertIn("2 commit(s) ahead of main", output["additionalContext"])
        self.assertTrue((self.home / ".claude/hooks/oss/stack").is_dir())

    def test_new_commit_reminds_again(self):
        self.assertIn("additionalContext", self.run_hook())
        self.assertEqual(self.run_hook(), "")
        self.commit("three")
        self.assertIn("3 commit(s) ahead", self.run_hook())

    def test_quiet_on_default_branch(self):
        git(self.repo, "checkout", "-q", "main")
        self.assertEqual(self.run_hook(), "")

    def test_quiet_below_the_commit_threshold(self):
        git(self.repo, "checkout", "-q", "-b", "single", "main")
        self.commit("only")
        self.assertEqual(self.run_hook(), "")

    def test_threshold_is_configurable(self):
        git(self.repo, "checkout", "-q", "-b", "single", "main")
        self.commit("only")
        output = json.loads(self.run_hook(extra_env={"STACK_HOOK_MIN_COMMITS": "1"}))["hookSpecificOutput"]
        self.assertIn("1 commit(s) ahead", output["additionalContext"])

    def test_quiet_during_a_merge(self):
        (self.repo / ".git" / "MERGE_HEAD").write_text("deadbeef\n")
        self.assertEqual(self.run_hook(), "")

    def test_respects_pause_file(self):
        state = self.home / ".codex/hooks/oss/stack"
        state.mkdir(parents=True)
        (state / "paused").touch()
        self.assertEqual(self.run_hook(), "")

    def test_respects_repo_opt_out(self):
        (self.repo / ".no-stack-nudge").touch()
        self.assertEqual(self.run_hook(), "")


if __name__ == "__main__":
    unittest.main()
