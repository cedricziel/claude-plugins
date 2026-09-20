import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "actions" / "update-plugin" / "update_settings.py"
SHA_A = "a" * 40
SHA_B = "b" * 40


class UpdateSettingsTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.settings = self.dir / ".claude" / "settings.json"

    def tearDown(self):
        shutil.rmtree(self.dir)

    def run_script(self, sha, plugins="toolkit,oss"):
        out = subprocess.run(
            ["python3", str(SCRIPT), "--settings", str(self.settings), "--marketplace", "cedricziel",
             "--repo", "cedricziel/claude-plugins", "--plugins", plugins, "--sha", sha],
            capture_output=True, text=True,
        )
        return out, dict(line.split("=", 1) for line in out.stdout.splitlines())

    def read(self):
        return json.loads(self.settings.read_text())

    def test_bootstraps_missing_file(self):
        _, out = self.run_script(SHA_A)
        self.assertEqual((out["changed"], out["bootstrapped"], out["sha"]), ("true", "true", SHA_A))
        cfg = self.read()
        self.assertEqual(
            cfg["extraKnownMarketplaces"]["cedricziel"]["source"],
            {"source": "github", "repo": "cedricziel/claude-plugins", "ref": "main", "sha": SHA_A},
        )
        self.assertEqual(cfg["enabledPlugins"], {"toolkit@cedricziel": True, "oss@cedricziel": True})

    def test_bootstrap_preserves_unrelated_settings(self):
        self.settings.parent.mkdir()
        self.settings.write_text(json.dumps({"enabledPlugins": {"x@y": True}, "model": "opus"}))
        self.run_script(SHA_A)
        cfg = self.read()
        self.assertEqual(cfg["model"], "opus")
        self.assertTrue(cfg["enabledPlugins"]["x@y"])
        self.assertTrue(cfg["enabledPlugins"]["toolkit@cedricziel"])

    def test_updates_sha_only_and_keeps_ref_and_plugins(self):
        self.run_script(SHA_A)
        cfg = self.read()
        cfg["extraKnownMarketplaces"]["cedricziel"]["source"]["ref"] = "v1"
        del cfg["enabledPlugins"]["oss@cedricziel"]
        self.settings.write_text(json.dumps(cfg))

        _, out = self.run_script(SHA_B)
        self.assertEqual((out["changed"], out["bootstrapped"]), ("true", "false"))
        cfg = self.read()
        source = cfg["extraKnownMarketplaces"]["cedricziel"]["source"]
        self.assertEqual((source["sha"], source["ref"]), (SHA_B, "v1"))
        self.assertEqual(cfg["enabledPlugins"], {"toolkit@cedricziel": True})

    def test_noop_when_already_latest(self):
        self.run_script(SHA_A)
        before = self.settings.read_text()
        _, out = self.run_script(SHA_A)
        self.assertEqual(out["changed"], "false")
        self.assertEqual(self.settings.read_text(), before)

    def test_refuses_marketplace_pointing_elsewhere(self):
        self.settings.parent.mkdir()
        self.settings.write_text(json.dumps({"extraKnownMarketplaces": {
            "cedricziel": {"source": {"source": "github", "repo": "someone/else"}}}}))
        out, _ = self.run_script(SHA_A)
        self.assertNotEqual(out.returncode, 0)


if __name__ == "__main__":
    unittest.main()
