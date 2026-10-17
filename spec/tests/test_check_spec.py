"""Run: python3 -m unittest discover -s spec/tests"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_spec  # noqa: E402

GOOD_SPEC = """# s
## 1. Parameter table
| Parameter | Min | Typ | Max | Condition | Corners |
|---|---|---|---|---|---|
| A | 1 | 2 | 3 | c | PVT |
## 2. Tiers
[r](decision-records/0001-x.md)
"""
REC = "# 0001\n\n- **Status**: proposed\n- **Date**: d\n"


def build(spec=GOOD_SPEC, rec=REC, readme="0001-x.md", name="0001-x.md"):
    d = Path(tempfile.mkdtemp())
    (d / "decision-records").mkdir()
    (d / "target-spec.md").write_text(spec)
    (d / "README.md").write_text(readme)
    if rec is not None:
        (d / "decision-records" / name).write_text(rec)
    return d


class Check(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(check_spec.check(build()), [])

    def test_empty_cell(self):
        bad = GOOD_SPEC.replace("| A | 1 | 2 | 3 | c | PVT |", "| A | 1 | 2 | 3 | c |  |")
        self.assertTrue(any("six non-empty" in e for e in check_spec.check(build(spec=bad))))

    def test_missing_record(self):
        errs = check_spec.check(build(rec=None))
        self.assertTrue(any("missing record" in e for e in errs))

    def test_bad_status(self):
        errs = check_spec.check(build(rec="# x\n- **Status**: maybe\n"))
        self.assertTrue(any("Status" in e for e in errs))

    def test_gap_in_numbering(self):
        errs = check_spec.check(build(name="0002-x.md", readme="0002-x.md"))
        self.assertTrue(any("contiguous" in e for e in errs))

    def test_missing_index_row(self):
        errs = check_spec.check(build(readme="empty"))
        self.assertTrue(any("index row" in e for e in errs))

    def test_real_spec(self):
        self.assertEqual(check_spec.check(), [])


if __name__ == "__main__":
    unittest.main()
