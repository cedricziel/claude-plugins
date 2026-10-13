import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import git, init_repo

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "toolkit"
HOOK = PLUGIN / "scripts" / "tdd-hook.sh"


class TddEditCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"; self.repo.mkdir()
        init_repo(self.repo)
        (self.repo / "src").mkdir()
        (self.repo / "src" / "app.py").write_text("x = 1\n")
        git(self.repo, "add", "."); git(self.repo, "commit", "-qm", "init")
        git(self.repo, "checkout", "-qb", "feature")
        self.env = {"PATH": "/usr/bin:/bin:/opt/homebrew/bin", "TDD_STATE_DIR": str(self.tmp / "state")}

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def edit(self, rel, session="s1"):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(path.read_text() + "y = 2\n" if path.exists() else "y = 2\n")
        payload = {"session_id": session, "tool_input": {"file_path": str(path)}}
        r = subprocess.run(
            ["bash", str(HOOK), "edit-check"], input=json.dumps(payload),
            capture_output=True, text=True, env=self.env, cwd=self.repo,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout and json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"] or ""

    def test_source_edit_without_test_points_at_writing_tests(self):
        self.assertIn("writing-tests", self.edit("src/app.py"))

    def test_nudges_once_per_file_per_session(self):
        self.edit("src/app.py")
        self.assertEqual(self.edit("src/app.py"), "")
        self.assertIn("writing-tests", self.edit("src/app.py", session="s2"))

    def test_test_committed_on_the_branch_counts(self):
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_app.py").write_text("def test_x(): pass\n")
        git(self.repo, "add", "."); git(self.repo, "commit", "-qm", "test")
        self.assertEqual(self.edit("src/app.py"), "")

    def test_config_files_are_not_source(self):
        self.assertEqual(self.edit("vite.config.ts"), "")

    def test_first_test_edit_in_a_session_points_at_test_hygiene(self):
        ctx = self.edit("tests/test_app.py")
        self.assertIn("test-strategy", ctx)
        self.assertEqual(self.edit("tests/test_other.py"), "")

    def test_repo_opt_out_file_silences_it(self):
        (self.repo / ".no-tdd-nudge").write_text("")
        self.assertEqual(self.edit("src/app.py"), "")


class TddWiringTest(unittest.TestCase):
    def test_no_stop_hook_runs_the_tdd_script(self):
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())["hooks"]
        commands = [h["command"] for e in hooks.get("Stop", []) for h in e["hooks"]]
        self.assertFalse([c for c in commands if "tdd-hook" in c])
