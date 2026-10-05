import json
import subprocess
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "common"
HOOK = PLUGIN / "scripts" / "session-start.sh"


def run(env=None, args=()):
    e = {"PATH": "/usr/bin:/bin:/opt/homebrew/bin", "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    e.update(env or {})
    r = subprocess.run(["bash", str(HOOK), *args], input="{}", capture_output=True, text=True, env=e)
    return r


class CommonSessionStartTest(unittest.TestCase):
    def test_emits_additional_context_json(self):
        r = run()
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("semantic commits", ctx.lower())
        self.assertIn("delegation models", ctx.lower())
        self.assertIn("code-comments", ctx)
        self.assertIn("`sonnet`", ctx)

    def test_instruction_file_exists(self):
        for name in ("shared.md", "claude.md", "codex.md"):
            self.assertTrue((PLUGIN / "instructions" / name).is_file())

    def test_codex_context_uses_codex_instructions(self):
        r = run({"PLUGIN_ROOT": str(PLUGIN)}, ("codex",))
        self.assertEqual(r.returncode, 0, r.stderr)
        ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("semantic commits", ctx)
        self.assertIn("supported tools and subagent interface", ctx)
        self.assertNotIn("sonnet", ctx)

    def test_claude_context_does_not_switch_on_plugin_root_env(self):
        ctx = json.loads(run({"PLUGIN_ROOT": str(PLUGIN)}).stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("`sonnet`", ctx)
        self.assertNotIn("supported tools and subagent interface", ctx)

    def test_disable_env_emits_nothing(self):
        r = run({"COMMON_INSTRUCTIONS_DISABLE": "1"})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
