import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINT = ROOT / "plugins" / "oss" / "skills" / "ux-design" / "scripts" / "ux-lint.py"


def run(args, cwd, stdin=""):
    return subprocess.run(
        [sys.executable, str(LINT), *args], cwd=cwd, input=stdin, capture_output=True, text=True
    )


class LintTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / "src").mkdir()
        (self.dir / "tailwind.config.js").write_text("export default {}\n")
        subprocess.run(["git", "init", "-q"], cwd=self.dir, check=True)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write(self, name, text):
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_img_without_alt_blocks(self):
        self.write("src/a.tsx", '<img src="hero.png" />\n')
        result = run(["src/a.tsx"], self.dir)
        self.assertEqual(result.returncode, 2)
        self.assertIn("img-no-alt", result.stdout)

    def test_empty_alt_passes(self):
        self.write("src/a.tsx", '<img src="hero.png" alt="" />\n')
        result = run(["src/a.tsx"], self.dir)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("img-no-alt", result.stdout)

    def test_alt_expression_passes(self):
        self.write("src/a.tsx", "<img src={src} alt={name} />\n")
        self.assertEqual(run(["src/a.tsx"], self.dir).returncode, 0)

    def test_non_semantic_click_blocks(self):
        self.write("src/a.tsx", '<div onClick={save}>Save</div>\n')
        result = run(["src/a.tsx"], self.dir)
        self.assertEqual(result.returncode, 2)
        self.assertIn("non-semantic-click", result.stdout)

    def test_click_with_role_passes(self):
        self.write("src/a.tsx", '<div role="button" tabIndex={0} onClick={save}>Save</div>\n')
        self.assertNotIn("non-semantic-click", run(["src/a.tsx"], self.dir).stdout)

    def test_removed_outline_blocks(self):
        self.write("src/a.css", ".btn { outline: none; }\n")
        result = run(["src/a.css"], self.dir)
        self.assertEqual(result.returncode, 2)
        self.assertIn("focus-removed", result.stdout)

    def test_removed_outline_with_focus_passes(self):
        self.write("src/a.css", ".btn { outline: none; }\n.btn:focus-visible { outline: 2px solid; }\n")
        self.assertNotIn("focus-removed", run(["src/a.css"], self.dir).stdout)

    def test_placeholder_copy_blocks_only_in_ui(self):
        self.write("src/a.tsx", '<input placeholder="John Doe" />\n')
        self.assertEqual(run(["src/a.tsx"], self.dir).returncode, 2)
        self.write("src/__tests__/a.tsx", '<input placeholder="John Doe" />\n')
        result = run(["src/__tests__/a.tsx"], self.dir)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("placeholder-copy", result.stdout)

    def test_marketing_copy_warns_without_blocking(self):
        self.write("src/a.tsx", "<h1>Seamlessly supercharge your work</h1>\n")
        result = run(["src/a.tsx"], self.dir)
        self.assertEqual(result.returncode, 0)
        self.assertIn("slop-copy", result.stdout)

    def test_raw_colour_only_with_tokens(self):
        self.write("src/a.tsx", '<p style={{ color: "#6C5CE7" }}>Hi</p>\n')
        self.assertIn("raw-color", run(["src/a.tsx"], self.dir).stdout)
        (self.dir / "tailwind.config.js").unlink()
        self.assertNotIn("raw-color", run(["src/a.tsx"], self.dir).stdout)

    def test_off_scale_spacing_warns(self):
        self.write("src/a.css", ".a { padding: 13px; }\n.b { padding: 12px; }\n")
        out = run(["src/a.css"], self.dir).stdout
        self.assertIn("off-scale-spacing", out)
        self.assertEqual(out.count("off-scale-spacing"), 1)

    def test_motion_without_reduced_motion_warns(self):
        self.write("src/a.css", ".a { transition: opacity 200ms; }\n")
        self.assertIn("motion-no-reduced", run(["src/a.css"], self.dir).stdout)

    def test_snippet_mode_lints_stdin(self):
        result = run(["--snippet", "--filename", "src/new.tsx"], self.dir, stdin='<img src="x" />\n')
        self.assertEqual(result.returncode, 2)
        self.assertIn("src/new.tsx:1", result.stdout)

    def test_ignore_comment_suppresses_file(self):
        self.write("src/a.tsx", "// ux-lint-ignore\n<img src=\"x\" />\n")
        self.assertEqual(run(["src/a.tsx"], self.dir).returncode, 0)

    def test_json_output_shape(self):
        self.write("src/a.tsx", '<img src="x" />\n')
        data = json.loads(run(["src/a.tsx", "--json"], self.dir).stdout)
        self.assertEqual(data[0]["rule"], "img-no-alt")
        self.assertEqual(data[0]["severity"], "block")
        self.assertEqual(set(data[0]), {"file", "line", "rule", "severity", "message"})


if __name__ == "__main__":
    unittest.main()
