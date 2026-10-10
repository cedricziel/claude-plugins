import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import git, init_repo

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "plugins" / "oss" / "skills" / "pull-request" / "scripts" / "upload-screenshots.sh"
)


class UploadScreenshotsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.remote = self.tmp / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", str(self.remote)], check=True)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        init_repo(self.repo)
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "init")
        git(self.repo, "remote", "add", "origin", "git@github.com:acme/widgets.git")
        git(self.repo, "config", "url." + str(self.remote) + ".insteadOf", "git@github.com:acme/widgets.git")
        self.shot = self.tmp / "before.png"
        self.shot.write_bytes(b"\x89PNG fake")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_script(self, *args):
        return subprocess.run(
            ["bash", str(SCRIPT), *args], cwd=self.repo, capture_output=True, text=True
        )

    def remote_file(self, path):
        return subprocess.run(
            ["git", "--git-dir", str(self.remote), "show", f"pr-assets:{path}"],
            capture_output=True,
        ).stdout

    def test_pushes_to_orphan_branch_and_prints_markdown(self):
        out = self.run_script("feat/login", str(self.shot))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(self.remote_file("feat-login/before.png"), b"\x89PNG fake")
        sha = subprocess.run(
            ["git", "--git-dir", str(self.remote), "rev-parse", "pr-assets"],
            capture_output=True, text=True,
        ).stdout.strip()
        self.assertEqual(
            out.stdout.strip(),
            f"![before](https://github.com/acme/widgets/blob/{sha}/feat-login/before.png?raw=true)",
        )

    def test_appends_to_existing_branch(self):
        self.run_script("one", str(self.shot))
        after = self.tmp / "after.png"
        after.write_bytes(b"\x89PNG two")
        out = self.run_script("two", str(after))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(self.remote_file("one/before.png"), b"\x89PNG fake")
        self.assertEqual(self.remote_file("two/after.png"), b"\x89PNG two")

    def test_leaves_working_tree_and_index_alone(self):
        (self.repo / "wip.txt").write_text("x")
        git(self.repo, "add", "wip.txt")
        self.run_script("feat", str(self.shot))
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=self.repo, capture_output=True, text=True
        ).stdout
        self.assertEqual(status, "A  wip.txt\n")

    def test_links_the_push_url_repository(self):
        git(self.repo, "remote", "set-url", "--push", "origin", "git@github.com:acme/fork.git")
        git(self.repo, "config", "--add", "url." + str(self.remote) + ".insteadOf", "git@github.com:acme/fork.git")
        out = self.run_script("feat", str(self.shot))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("https://github.com/acme/fork/blob/", out.stdout)

    def test_rejects_duplicate_names(self):
        other = self.tmp / "sub"
        other.mkdir()
        (other / "before.png").write_bytes(b"x")
        out = self.run_script("feat", str(self.shot), str(other / "before.png"))
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("duplicate", out.stderr)

    def test_rejects_names_that_need_url_encoding(self):
        odd = self.tmp / "my shot (1).png"
        odd.write_bytes(b"x")
        out = self.run_script("feat", str(odd))
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("rename", out.stderr)

    def test_rejects_non_github_remote(self):
        git(self.repo, "remote", "set-url", "origin", str(self.remote))
        out = self.run_script("feat", str(self.shot))
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("GitHub", out.stderr)


if __name__ == "__main__":
    unittest.main()
