import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import git, init_repo

SCRIPT = Path(__file__).resolve().parent.parent / "plugins" / "toolkit" / "scripts" / "default-branch.sh"


class DefaultBranchTest(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        init_repo(self.repo)

    def tearDown(self):
        shutil.rmtree(self.repo)

    def run_script(self):
        return subprocess.run(["bash", str(SCRIPT)], cwd=self.repo, capture_output=True, text=True).stdout.strip()

    def test_origin_head_wins(self):
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "init")
        git(self.repo, "branch", "develop")
        git(self.repo, "update-ref", "refs/remotes/origin/develop", "HEAD")
        git(self.repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/develop")
        self.assertEqual(self.run_script(), "develop")

    def test_falls_back_to_main(self):
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "init")
        self.assertEqual(self.run_script(), "main")

    def test_falls_back_to_master_without_main(self):
        self.assertEqual(self.run_script(), "master")


if __name__ == "__main__":
    unittest.main()
