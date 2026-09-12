import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "plugins" / "toolkit" / "scripts" / "model-guard.sh"


class ModelGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_hook(self, model, env=None):
        e = {"PATH": "/usr/bin:/bin", "HOME": str(self.tmp)}
        e.update(env or {})
        payload = json.dumps(
            {
                "tool_name": "Agent",
                "tool_input": {"model": model} if model is not None else {},
                "cwd": str(self.repo),
            }
        )
        r = subprocess.run(["bash", str(HOOK)], input=payload, capture_output=True, text=True, env=e, cwd=self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_denies_fable(self):
        out = json.loads(self.run_hook("fable"))
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_denies_fable_family_id(self):
        out = json.loads(self.run_hook("claude-fable-5-1"))
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_allows_sonnet(self):
        self.assertEqual(self.run_hook("sonnet"), "")

    def test_allows_haiku(self):
        self.assertEqual(self.run_hook("haiku"), "")

    def test_allows_opus(self):
        self.assertEqual(self.run_hook("opus"), "")

    def test_allows_missing_model(self):
        self.assertEqual(self.run_hook(None), "")

    def test_repo_optout_file(self):
        (self.repo / ".no-model-guard").write_text("")
        self.assertEqual(self.run_hook("fable"), "")

    def test_env_optout(self):
        self.assertEqual(self.run_hook("fable", {"MODEL_GUARD_DISABLE": "1"}), "")


if __name__ == "__main__":
    unittest.main()
