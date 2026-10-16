import json
import subprocess
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "toolkit"
HOOK = PLUGIN / "scripts" / "session-start.sh"


def run(env=None, args=()):
    e = {"PATH": "/usr/bin:/bin:/opt/homebrew/bin", "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    e.update(env or {})
    r = subprocess.run(["bash", str(HOOK), *args], input="{}", capture_output=True, text=True, env=e)
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
        self.assertIn("`sonnet`", ctx)
        self.assertIn("oss:technical-writer", ctx)

    def test_fleet_brief_path_is_resolved(self):
        ctx = json.loads(run().stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertNotIn("{{FLEET_BRIEF}}", ctx)
        self.assertIn(str(PLUGIN / "instructions" / "fleet-brief.md"), ctx)

    def test_instruction_files_exist(self):
        for name in ("shared.md", "claude.md", "codex.md"):
            self.assertTrue((PLUGIN / "instructions" / name).is_file())
        self.assertTrue((PLUGIN / "instructions" / "fleet-brief.md").is_file())

    def test_codex_context_uses_openai_model_guidance(self):
        r = run({"PLUGIN_ROOT": str(PLUGIN)}, ("codex",))
        self.assertEqual(r.returncode, 0, r.stderr)
        ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Caveman Compression", ctx)
        self.assertIn("`gpt-6.1-sol`", ctx)
        self.assertIn("`gpt-6-luna`", ctx)
        self.assertNotIn("{{FLEET_BRIEF}}", ctx)
        self.assertNotIn("context7", ctx)

    def test_reflect_data_directory_uses_host_plugin_data(self):
        for env, args in (
            ({"CLAUDE_PLUGIN_DATA": "/tmp/claude toolkit data"}, ()),
            ({"PLUGIN_DATA": "/tmp/codex toolkit data"}, ("codex",)),
        ):
            with self.subTest(args=args):
                ctx = json.loads(run(env, args).stdout)["hookSpecificOutput"]["additionalContext"]
                self.assertIn(next(iter(env.values())), ctx)

    def test_disable_env_emits_nothing(self):
        r = run({"TOOLKIT_INSTRUCTIONS_DISABLE": "1"})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()


class ReflectNudgeTest(unittest.TestCase):
    def setUp(self):
        import tempfile

        self.tmp = Path(tempfile.mkdtemp())
        self.data = self.tmp / "data"
        (self.data / "reflect").mkdir(parents=True)
        self.marker = self.data / "reflect" / "last-reviewed.json"
        self.env = {"CLAUDE_PLUGIN_DATA": str(self.data), "REFLECT_NUDGE_STATE_DIR": str(self.tmp / "state")}

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp)

    def ctx(self, source="startup"):
        e = {"PATH": "/usr/bin:/bin:/opt/homebrew/bin", "CLAUDE_PLUGIN_ROOT": str(PLUGIN), **self.env}
        r = subprocess.run(
            ["bash", str(HOOK)], input=json.dumps({"source": source}), capture_output=True, text=True, env=e
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]

    def review(self, days_ago):
        import os
        import time

        self.marker.write_text("{}")
        t = time.time() - days_ago * 86400
        os.utime(self.marker, (t, t))

    def test_nudges_when_reflect_never_ran(self):
        self.assertIn("/reflect", self.ctx())

    def test_nudges_when_last_review_is_overdue(self):
        self.review(days_ago=10)
        self.assertIn("/reflect", self.ctx())

    def test_quiet_after_a_recent_review(self):
        self.review(days_ago=2)
        self.assertNotIn("/reflect", self.ctx())

    def test_nudges_at_most_once_a_day(self):
        self.assertIn("/reflect", self.ctx())
        self.assertNotIn("/reflect", self.ctx())

    def test_quiet_when_context_is_reinjected_after_compaction(self):
        self.assertNotIn("/reflect", self.ctx(source="compact"))

    def test_quiet_when_nudge_state_cannot_be_recorded(self):
        blocker = self.tmp / "state"
        blocker.write_text("not a directory")
        self.assertNotIn("/reflect", self.ctx())

    def test_threshold_with_leading_zero_is_decimal(self):
        self.env["REFLECT_NUDGE_DAYS"] = "08"
        self.review(days_ago=10)
        self.assertIn("/reflect", self.ctx())
