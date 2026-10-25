import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import git, init_repo

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "toolkit"


class RebaseHookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.repo = self.home / "repo"
        self.repo.mkdir()
        init_repo(self.repo)
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "base")
        git(self.repo, "checkout", "-q", "-b", "fix")
        git(self.repo, "checkout", "-q", "main")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "advance")
        git(self.repo, "checkout", "-q", "fix")

    def run_hook(self, host="codex"):
        config = PLUGIN / ("codex-hooks" if host == "codex" else "hooks") / "hooks.json"
        hook = json.loads(config.read_text())["hooks"]["UserPromptSubmit"][0]["hooks"][0]
        result = subprocess.run(
            hook["command"], shell=True, cwd=self.home, input=json.dumps({"cwd": str(self.repo)}),
            env={**os.environ, "HOME": str(self.home), "CODEX_HOME": str(self.home / ".codex"), "PLUGIN_ROOT": str(PLUGIN),
                 "CLAUDE_PLUGIN_ROOT": str(PLUGIN)},
            capture_output=True, text=True, timeout=hook["timeout"],
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_codex_reminds_and_throttles_in_its_own_state_directory(self):
        output = json.loads(self.run_hook())["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "UserPromptSubmit")
        self.assertIn("1 commit(s) behind main", output["additionalContext"])
        self.assertTrue((self.home / ".codex/hooks/toolkit/rebase").is_dir())
        self.assertFalse((self.home / ".claude").exists())
        self.assertEqual(self.run_hook(), "")

    def test_codex_is_quiet_on_default_branch(self):
        git(self.repo, "checkout", "-q", "main")
        self.assertEqual(self.run_hook(), "")

    def test_codex_respects_pause_file(self):
        state = self.home / ".codex/hooks/toolkit/rebase"
        state.mkdir(parents=True)
        (state / "paused").touch()
        self.assertEqual(self.run_hook(), "")

    def test_claude_still_emits_a_reminder(self):
        output = json.loads(self.run_hook("claude"))["hookSpecificOutput"]
        self.assertIn("1 commit(s) behind main", output["additionalContext"])
        self.assertTrue((self.home / ".claude/hooks/toolkit/rebase").is_dir())
