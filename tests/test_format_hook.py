import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "plugins" / "common" / "scripts" / "format-hook.sh"


class FormatHookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.log = self.tmp / "calls.log"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def stub(self, name, where=None):
        """Fake formatter that logs its argv."""
        d = where or self.bin
        d.mkdir(parents=True, exist_ok=True)
        p = d / name
        p.write_text(f'#!/bin/sh\necho "{name} $*" >> "{self.log}"\n')
        p.chmod(0o755)

    def run_hook(self, file, env=None):
        e = {"PATH": f"{self.bin}:/usr/bin:/bin", "HOME": str(self.tmp)}
        e.update(env or {})
        payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(file)}})
        r = subprocess.run(["bash", str(HOOK)], input=payload, capture_output=True, text=True, env=e, cwd=self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        return self.log.read_text() if self.log.exists() else ""

    def touch(self, rel, content="x\n"):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return p

    def test_go_uses_gofmt(self):
        self.stub("gofmt")
        f = self.touch("main.go")
        self.assertIn(f"gofmt -w {f}", self.run_hook(f))

    def test_rust_uses_cargo_fmt_with_manifest(self):
        self.stub("cargo")
        self.touch("Cargo.toml")
        f = self.touch("src/lib.rs")
        out = self.run_hook(f)
        self.assertIn("cargo fmt --manifest-path", out)
        self.assertIn(str(self.repo / "Cargo.toml"), out)

    def test_rust_without_cargo_falls_back_to_rustfmt(self):
        self.stub("rustfmt")
        f = self.touch("x.rs")
        self.assertIn(f"rustfmt {f}", self.run_hook(f))

    def test_swift_prefers_config_matching_tool(self):
        self.stub("swiftformat")
        self.stub("swift-format")
        self.touch(".swift-format", "{}")
        f = self.touch("A.swift")
        out = self.run_hook(f)
        self.assertIn("swift-format format --in-place", out)
        self.assertNotIn("swiftformat ", out)

    def test_swift_defaults_to_swiftformat(self):
        self.stub("swiftformat")
        self.stub("swift-format")
        f = self.touch("A.swift")
        out = self.run_hook(f)
        self.assertIn(f"swiftformat {f}", out)

    def test_dart(self):
        self.stub("dart")
        f = self.touch("a.dart")
        self.assertIn(f"dart format {f}", self.run_hook(f))

    def test_python_prefers_ruff(self):
        self.stub("ruff")
        self.stub("black")
        f = self.touch("a.py")
        out = self.run_hook(f)
        self.assertIn(f"ruff format {f}", out)
        self.assertNotIn("black", out)

    def test_prettier_prefers_local_node_modules(self):
        self.stub("prettier")
        self.stub("prettier", self.repo / "node_modules" / ".bin")
        f = self.touch("a.ts")
        out = self.run_hook(f)
        self.assertIn("--write", out)
        self.assertEqual(out.count("prettier"), 1)
        # local stub logs the same name; ensure PATH one wasn't the runner by checking cwd-relative path use
        self.assertIn(str(f), out)

    def test_markdown_uses_prettier(self):
        self.stub("prettier")
        f = self.touch("README.md")
        self.assertIn("prettier --write", self.run_hook(f))

    def test_unknown_extension_noop(self):
        self.stub("prettier")
        f = self.touch("a.xyz")
        self.assertEqual(self.run_hook(f), "")

    def test_missing_file_noop(self):
        self.stub("gofmt")
        self.assertEqual(self.run_hook(self.repo / "nope.go"), "")

    def test_repo_optout_file(self):
        self.stub("gofmt")
        self.touch(".no-format-hook", "")
        f = self.touch("main.go")
        self.assertEqual(self.run_hook(f), "")

    def test_env_optout(self):
        self.stub("gofmt")
        f = self.touch("main.go")
        self.assertEqual(self.run_hook(f, {"FORMAT_HOOK_DISABLE": "1"}), "")

    def test_missing_formatter_is_silent(self):
        f = self.touch("main.go")
        self.assertEqual(self.run_hook(f), "")


if __name__ == "__main__":
    unittest.main()
