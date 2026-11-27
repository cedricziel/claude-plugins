import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def context(plugin, host):
    result = subprocess.run(
        ["bash", str(ROOT / "plugins" / plugin / "scripts/session-start.sh"), host],
        input="{}",
        capture_output=True,
        text=True,
        check=True,
        env={"PATH": "/usr/bin:/bin:/opt/homebrew/bin"},
    )
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


class InstructionBoundaryTest(unittest.TestCase):
    def test_public_dependency_chain_excludes_personal_workflow(self):
        for host in ("claude", "codex", "opencode"):
            with self.subTest(host=host):
                public = context("common", host) + context("oss", host)
                personal = context("toolkit", host)
                markers = [
                    "Caveman Compression",
                    "micro-commits",
                    "exactly one item in progress",
                ]
                markers += {
                    "claude": ["`sonnet`", "`opus`", "/simplify", "oss:technical-writer"],
                    "codex": ["`gpt-6-luna`", "`gpt-6.1-sol`", "`gpt-6-astra`"],
                    "opencode": ["`gpt-6.2-sol`", "`glm-5.3-flash`", "`grok-4.7`"],
                }[host]
                for marker in markers:
                    self.assertNotIn(marker, public, marker)
                    self.assertIn(marker, personal, marker)
                self.assertNotIn("toolkit", public)
                self.assertIn("semantic commits", public)
                self.assertIn("technical-writing", public)
                self.assertIn("test-strategy", public)


if __name__ == "__main__":
    unittest.main()
