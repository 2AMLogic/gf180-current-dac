"""Run: python -m unittest sim.harness.test_check"""

import unittest
from pathlib import Path

from sim.harness import check

PDK = {"variant": "gf180mcuD", "revision": "abc", "fetch": "ciel enable abc"}
TC = {"ngspice_min": "46", "python_min": "3.12", "pdk_revision": "abc"}
D = Path("/x/ciel/gf180mcu/versions/abc/gf180mcuD")


class Drift(unittest.TestCase):
    def drift(self, **kw):
        a = dict(ngspice="46", python="3.12.3", variant_dir=D, revision="abc")
        a.update(kw)
        return check.collect_drift(PDK, TC, **a)

    def test_pass(self):
        self.assertEqual(self.drift(), [])
        self.assertEqual(self.drift(ngspice="46.1"), [])

    def test_ngspice_old(self):
        (msg,) = self.drift(ngspice="45")
        self.assertIn("ngspice: found 45, need >= 46", msg)

    def test_ngspice_missing(self):
        (msg,) = self.drift(ngspice=None)
        self.assertIn("ngspice: not found", msg)

    def test_python_old(self):
        (msg,) = self.drift(python="3.11.9")
        self.assertIn("python: found 3.11.9", msg)

    def test_pdk_revision_drift(self):
        (msg,) = self.drift(revision="def")
        self.assertIn("pdk:", msg)
        self.assertIn("revision def, pinned abc", msg)

    def test_pdk_missing(self):
        (msg,) = self.drift(variant_dir=None, revision=None)
        self.assertIn("gf180mcuD not found", msg)

    def test_pin_files_disagree(self):
        msgs = check.collect_drift(PDK, {**TC, "pdk_revision": "zzz"}, "46", "3.12.3", D, "abc")
        self.assertEqual(len(msgs), 1)
        self.assertIn("pins:", msgs[0])

    def test_committed_pins_agree(self):
        pdk, tc = check.load_pins()
        self.assertEqual(pdk["revision"], tc["pdk_revision"])
        self.assertRegex(pdk["revision"], r"^[0-9a-f]{40}$")

    def test_revision_from_path(self):
        self.assertEqual(check.pdk_revision(D), "abc")


if __name__ == "__main__":
    unittest.main()
