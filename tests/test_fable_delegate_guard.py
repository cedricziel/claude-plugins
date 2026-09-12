import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "plugins" / "toolkit" / "scripts"
TRACK = ROOT / "fable-track.sh"
GUARD = ROOT / "fable-delegate-guard.sh"


class FableDelegateGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self.state_dir = self.tmp / "state"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def env(self, extra=None):
        e = {"PATH": "/usr/bin:/bin", "HOME": str(self.tmp), "FABLE_GUARD_STATE_DIR": str(self.state_dir)}
        e.update(extra or {})
        return e

    def track(self, session_id, model=None, to_model=None, env=None):
        payload = {"session_id": session_id, "cwd": str(self.repo)}
        if model is not None:
            payload["model"] = model
        if to_model is not None:
            payload["to_model"] = to_model
        r = subprocess.run(
            ["bash", str(TRACK)], input=json.dumps(payload), capture_output=True, text=True, env=self.env(env), cwd=self.repo
        )
        self.assertEqual(r.returncode, 0, r.stderr)

    def guard(self, session_id, env=None):
        payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": "x.py"}, "session_id": session_id, "cwd": str(self.repo)})
        r = subprocess.run(["bash", str(GUARD)], input=payload, capture_output=True, text=True, env=self.env(env), cwd=self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_denies_edit_when_session_tracked_as_fable(self):
        self.track("s1", model="fable")
        out = json.loads(self.guard("s1"))
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_post_model_switch_updates_tracked_model(self):
        self.track("s1", model="claude-fable-5-1")
        self.track("s1", to_model="sonnet")
        self.assertEqual(self.guard("s1"), "")

    def test_allows_when_session_tracked_as_sonnet(self):
        self.track("s1", model="sonnet")
        self.assertEqual(self.guard("s1"), "")

    def test_allows_unknown_session_fail_open(self):
        self.assertEqual(self.guard("never-tracked"), "")

    def test_repo_optout_file(self):
        self.track("s1", model="fable")
        (self.repo / ".no-fable-delegate-guard").write_text("")
        self.assertEqual(self.guard("s1"), "")

    def test_env_optout(self):
        self.track("s1", model="fable")
        self.assertEqual(self.guard("s1", {"FABLE_GUARD_DISABLE": "1"}), "")


if __name__ == "__main__":
    unittest.main()
