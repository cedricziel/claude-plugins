import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugins" / "oss" / "skills" / "ux-design"
REFS = SKILL / "references"

SOURCE_RE = re.compile(r"^\[(\d+)\]\s+\[([^\]]+)\]\((https?://[^)\s]+)\)", re.M)
MARKER_RE = re.compile(r"\[(\d+)\]")
REF_LINK_RE = re.compile(r"(?:\(|`)references/([\w.-]+\.md)(?:\)|`)")


def references():
    return sorted(REFS.glob("*.md"))


def split_sources(path):
    text = path.read_text()
    if "## Sources" not in text:
        return text, []
    body, tail = text.split("## Sources", 1)
    return body, SOURCE_RE.findall(tail)


class UxDesignSkillTest(unittest.TestCase):
    def test_skill_has_frontmatter(self):
        text = (SKILL / "SKILL.md").read_text()
        self.assertRegex(text, r"^---\nname: ux-design\n")
        self.assertRegex(text, r"\ndescription:")

    def test_routing_targets_exist(self):
        text = (SKILL / "SKILL.md").read_text()
        self.assertTrue(REF_LINK_RE.findall(text), "SKILL.md names no reference files")
        for name in set(REF_LINK_RE.findall(text)):
            self.assertTrue((REFS / name).is_file(), f"SKILL.md routes to missing references/{name}")

    def test_every_reference_is_routed(self):
        routed = set(REF_LINK_RE.findall((SKILL / "SKILL.md").read_text()))
        for path in references():
            if path.name == "index.md":
                continue
            self.assertIn(path.name, routed, f"references/{path.name} exists but SKILL.md never routes to it")

    def test_reference_has_cited_sources(self):
        for path in references():
            if path.name == "index.md":
                continue
            _, sources = split_sources(path)
            self.assertGreaterEqual(len(sources), 5, f"{path.name} needs at least 5 cited sources")

    def test_source_entries_are_dated_and_linked(self):
        for path in references():
            _, sources = split_sources(path)
            for number, title, url in sources:
                self.assertTrue(title.strip(), f"{path.name} source {number} has no title")
                self.assertTrue(url.startswith("http"), f"{path.name} source {number} has no URL")
                self.assertNotRegex(url, r"example\.com|localhost|TBD|TODO")

    def test_source_numbers_are_unique(self):
        for path in references():
            _, sources = split_sources(path)
            numbers = [int(n) for n, _, _ in sources]
            self.assertEqual(len(numbers), len(set(numbers)), f"{path.name} repeats a source number")

    def test_inline_markers_resolve(self):
        for path in references():
            if path.name == "index.md":
                continue
            body, sources = split_sources(path)
            highest = max((int(n) for n, _, _ in sources), default=0)
            for number in MARKER_RE.findall(body):
                self.assertLessEqual(
                    int(number), highest, f"{path.name} cites [{number}] but lists only {highest} sources"
                )

    def test_no_placeholder_text(self):
        for path in [SKILL / "SKILL.md", *references()]:
            text = path.read_text()
            for marker in ("TODO", "FIXME", "TBD", "lorem ipsum"):
                self.assertNotIn(marker, text, f"{path.name} contains {marker}")


if __name__ == "__main__":
    unittest.main()
