import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "plugins" / "oss" / "scripts" / "ux-nudge.sh"
HAS_JQ = shutil.which("jq") is not None


@unittest.skipUnless(HAS_JQ, "jq is required by the hook")
class HookTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / "src").mkdir()
        (self.dir / "tailwind.config.js").write_text("export default {}\n")
        (self.dir / "src" / "Hero.tsx").write_text(
            '<img src="hero.png" />\n<div onClick={save}>Save</div>\n<h1>Seamlessly do things</h1>\n'
        )
        (self.dir / "README.md").write_text("# readme\n")
        self.state = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=self.dir, check=True)

    def tearDown(self):
        shutil.rmtree(self.dir)
        shutil.rmtree(self.state)

    def hook(self, payload, args=("advise",), env=None):
        return subprocess.run(
            ["bash", str(HOOK), *args],
            cwd=self.dir,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "UX_LINT_STATE_DIR": str(self.state),
                "HOME": str(self.state),
                **(env or {}),
            },
        )

    def test_gate_blocks_with_reason(self):
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "src/New.tsx", "content": '<img src="x" />'},
        }
        result = self.hook(payload, args=("gate",))
        self.assertEqual(result.returncode, 2)
        self.assertIn("img-no-alt", result.stderr)

    def test_gate_allows_clean_edit(self):
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": "src/New.tsx", "new_string": '<img src="x" alt="" />'},
        }
        result = self.hook(payload, args=("gate",))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_advise_attaches_findings_once(self):
        payload = {"tool_name": "Edit", "session_id": "ses1", "tool_input": {"file_path": "src/Hero.tsx"}}
        first = self.hook(payload)
        self.assertEqual(first.returncode, 0)
        context = json.loads(first.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("<ux_findings>", context)
        self.assertIn("img-no-alt", context)
        second = self.hook(payload)
        if second.stdout:
            again = json.loads(second.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertNotIn("img-no-alt", again)

    def test_non_ui_file_is_silent(self):
        result = self.hook({"tool_name": "Edit", "session_id": "ses1", "tool_input": {"file_path": "README.md"}})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_apply_patch_is_linted(self):
        payload = {
            "tool_name": "apply_patch",
            "session_id": "ses1",
            "cwd": str(self.dir),
            "tool_input": {"command": "*** Update File: src/Hero.tsx\n"},
        }
        result = self.hook(payload)
        self.assertIn("img-no-alt", result.stdout)

    def test_repo_opt_out_file(self):
        (self.dir / ".no-ux-lint").write_text("")
        result = self.hook({"tool_name": "Edit", "session_id": "ses1", "tool_input": {"file_path": "src/Hero.tsx"}})
        self.assertEqual(result.stdout, "")

    def test_disable_env(self):
        result = self.hook(
            {"tool_name": "Edit", "session_id": "ses1", "tool_input": {"file_path": "src/Hero.tsx"}},
            env={"UX_LINT_DISABLE": "1"},
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
