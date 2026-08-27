import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import git

SCRIPT = Path(__file__).resolve().parent.parent / "plugins" / "toolkit" / "scripts" / "review-target.sh"


class ReviewTargetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"; self.repo.mkdir()
        self.bin = self.tmp / "bin"; self.bin.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@t"); git(self.repo, "config", "user.name", "t")
        (self.repo / "a.txt").write_text("one\n")
        git(self.repo, "add", "."); git(self.repo, "commit", "-qm", "init")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_script(self, *args):
        env = {"PATH": f"{self.bin}:/usr/bin:/bin:/opt/homebrew/bin", "HOME": str(self.tmp)}
        out = self.tmp / "diff.patch"
        r = subprocess.run(["bash", str(SCRIPT), *args, str(out)], cwd=self.repo, capture_output=True, text=True, env=env)
        return r, out

    def test_working_tree_diff(self):
        (self.repo / "a.txt").write_text("two\n")
        r, out = self.run_script("")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("+two", out.read_text())
        self.assertIn("kind=working-tree", r.stdout)

    def test_working_tree_includes_untracked(self):
        (self.repo / "new.txt").write_text("hello\n")
        r, out = self.run_script("")
        self.assertIn("+hello", out.read_text())

    def test_branch_diff_against_main(self):
        git(self.repo, "checkout", "-qb", "feat")
        (self.repo / "a.txt").write_text("three\n")
        git(self.repo, "commit", "-qam", "change")
        r, out = self.run_script("feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("+three", out.read_text())
        self.assertIn("kind=branch", r.stdout)

    def test_pr_number_uses_gh(self):
        gh = self.bin / "gh"
        gh.write_text('#!/bin/sh\necho "gh $*" >> "$HOME/gh.log"; echo "+from-pr"\n'); gh.chmod(0o755)
        r, out = self.run_script("42")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("pr diff 42", (self.tmp / "gh.log").read_text())
        self.assertIn("+from-pr", out.read_text())
        self.assertIn("kind=pr", r.stdout)

    def test_empty_diff_fails(self):
        r, out = self.run_script("")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("empty", r.stderr.lower())


if __name__ == "__main__":
    unittest.main()
