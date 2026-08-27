import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import git, init_repo

SCRIPT = Path(__file__).resolve().parent.parent / "plugins" / "toolkit" / "scripts" / "issue-ref.sh"


class IssueRefTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        init_repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_script(self, ref):
        r = subprocess.run(["bash", str(SCRIPT), ref], cwd=self.tmp, capture_output=True, text=True)
        return r.returncode, dict(kv.split("=", 1) for kv in r.stdout.split()), r.stderr

    def test_github_url(self):
        rc, kv, _ = self.run_script("https://github.com/acme/widgets/issues/42")
        self.assertEqual(rc, 0)
        self.assertEqual(kv, {"forge": "github", "host": "github.com", "repo": "acme/widgets", "number": "42", "cli": "gh"})

    def test_forgejo_url(self):
        rc, kv, _ = self.run_script("https://code.example.org/acme/widgets/issues/7")
        self.assertEqual(kv["forge"], "forgejo"); self.assertEqual(kv["cli"], "fj")
        self.assertEqual(kv["host"], "code.example.org"); self.assertEqual(kv["number"], "7")

    def test_owner_repo_hash_uses_origin_host(self):
        git(self.tmp, "remote", "add", "origin", "git@code.example.org:me/other.git")
        rc, kv, _ = self.run_script("acme/widgets#9")
        self.assertEqual(kv["repo"], "acme/widgets"); self.assertEqual(kv["forge"], "forgejo")

    def test_bare_number_github_ssh_remote(self):
        git(self.tmp, "remote", "add", "origin", "git@github.com:acme/widgets.git")
        rc, kv, _ = self.run_script("123")
        self.assertEqual(kv, {"forge": "github", "host": "github.com", "repo": "acme/widgets", "number": "123", "cli": "gh"})

    def test_bare_number_https_remote(self):
        git(self.tmp, "remote", "add", "origin", "https://code.example.org/acme/widgets")
        rc, kv, _ = self.run_script("5")
        self.assertEqual(kv["repo"], "acme/widgets"); self.assertEqual(kv["cli"], "fj")

    def test_bare_number_without_remote_fails(self):
        rc, kv, err = self.run_script("5")
        self.assertNotEqual(rc, 0); self.assertIn("remote", err)

    def test_garbage_fails(self):
        rc, kv, err = self.run_script("not-a-ref")
        self.assertNotEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
