import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "bench" / "review-lens.js"
FIXTURE = ROOT / "bench" / "fixtures" / "review-lens" / "src"

# The line each planted bug lives on; the bench's [lo, hi] range must cover it.
PLANTED = {
    "wait-time-negative": "return missing / self.rate",
    "shared-mutable-overrides": "overrides={}",
    "page-count-floor": "return total // size",
    "grace-multiplier": "return used > quota * grace",
    "decoy-deltas": "range(len(samples) - 1)",
}


class ReviewLensBenchTest(unittest.TestCase):
    def test_lens_matches_adversarial_review(self):
        lens = re.search(r"const LENS =\s*['\"]([^'\"]+)['\"]", BENCH.read_text()).group(1)
        self.assertIn(lens, (ROOT / "plugins" / "toolkit" / "workflows" / "adversarial-review.js").read_text())

    def test_answer_key_covers_each_planted_line(self):
        key = {m[0]: (m[1], int(m[2]), int(m[3])) for m in re.findall(
            r"id: ['\"]([\w-]+)['\"],\s*file: ['\"]([\w/.]+)['\"],\s*lo: (\d+),\s*hi: (\d+)", BENCH.read_text())}
        self.assertEqual(set(key), set(PLANTED))
        for bug, needle in PLANTED.items():
            file, lo, hi = key[bug]
            lines = (FIXTURE / file).read_text().splitlines()
            line = next(i for i, text in enumerate(lines, 1) if needle in text)
            self.assertTrue(lo <= line <= hi, f"{bug}: planted on line {line}, key says {lo}-{hi}")


if __name__ == "__main__":
    unittest.main()
