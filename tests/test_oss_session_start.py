import json
import subprocess
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "oss"
HOOK = PLUGIN / "scripts" / "session-start.sh"


def run(env=None):
    e = {"PATH": "/usr/bin:/bin:/opt/homebrew/bin", "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    e.update(env or {})
    return subprocess.run(["bash", str(HOOK)], input="{}", capture_output=True, text=True, env=e)


class OssSessionStartTest(unittest.TestCase):
    def test_emits_additional_context_json(self):
        r = run()
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("oss:technical-writer", ctx)
        self.assertIn("technical-writing", ctx)

    def test_instruction_file_exists(self):
        self.assertTrue((PLUGIN / "instructions" / "global.md").is_file())

    def test_disable_env_emits_nothing(self):
        r = run({"OSS_INSTRUCTIONS_DISABLE": "1"})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
