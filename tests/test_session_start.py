import json
import subprocess
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "toolkit"
HOOK = PLUGIN / "scripts" / "session-start.sh"


def run(env=None):
    e = {"PATH": "/usr/bin:/bin:/opt/homebrew/bin", "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    e.update(env or {})
    r = subprocess.run(["bash", str(HOOK)], input="{}", capture_output=True, text=True, env=e)
    return r


class SessionStartTest(unittest.TestCase):
    def test_emits_additional_context_json(self):
        r = run()
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("Caveman Compression", ctx)
        self.assertIn("context7", ctx.lower())

    def test_fleet_brief_path_is_resolved(self):
        ctx = json.loads(run().stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertNotIn("{{FLEET_BRIEF}}", ctx)
        self.assertIn(str(PLUGIN / "instructions" / "fleet-brief.md"), ctx)

    def test_instruction_files_exist(self):
        self.assertTrue((PLUGIN / "instructions" / "global.md").is_file())
        self.assertTrue((PLUGIN / "instructions" / "fleet-brief.md").is_file())

    def test_disable_env_emits_nothing(self):
        r = run({"TOOLKIT_INSTRUCTIONS_DISABLE": "1"})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
