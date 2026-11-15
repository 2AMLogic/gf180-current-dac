#!/usr/bin/env python3
"""Unit tests for gen_array.py --check's three-way klayout decision (issue #87).

Must run on hosts where klayout is not importable at all: nothing here
imports klayout, and gen_array.py's guarded import tolerates its absence.
Verify with `python3 -s -m unittest layout.tests.test_gen_array_check`.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "gen_array_under_test", ROOT / "layout" / "gen_array.py")
gen_array = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen_array)


def envelope(version="0.30.12", content_hash="abc123"):
    return {
        "schema_version": 1,
        "status": "pass",
        "source": "layout/gf180-current-dac-analog.gds",
        "provenance": {
            "klayout_version": version,
            "input": {"content_hash": content_hash},
        },
    }


class TestCheckMode(unittest.TestCase):
    def test_absent_is_skip(self):
        self.assertEqual(gen_array.check_mode(None, "0.30.12"), "skip")

    def test_mismatch_is_relaxed(self):
        self.assertEqual(gen_array.check_mode("0.30.10", "0.30.12"), "relaxed")

    def test_pin_is_strict(self):
        self.assertEqual(gen_array.check_mode("0.30.12", "0.30.12"), "strict")


class TestMaskedComparison(unittest.TestCase):
    def test_version_drift_is_ignored_under_mask(self):
        a = envelope(version="0.30.10")
        b = envelope(version="0.30.12")
        self.assertEqual(
            gen_array.mask_klayout_version(a),
            gen_array.mask_klayout_version(b))

    def test_content_hash_drift_is_caught_under_mask(self):
        a = envelope(version="0.30.10")
        b = envelope(version="0.30.10", content_hash="drifted")
        self.assertNotEqual(
            gen_array.mask_klayout_version(a),
            gen_array.mask_klayout_version(b))

    def test_other_field_drift_is_caught_under_mask(self):
        a = envelope()
        b = envelope()
        b["source"] = "elsewhere.gds"
        self.assertNotEqual(
            gen_array.mask_klayout_version(a),
            gen_array.mask_klayout_version(b))

    def test_mask_does_not_mutate_its_argument(self):
        ev = envelope()
        gen_array.mask_klayout_version(ev)
        self.assertIn("klayout_version", ev["provenance"])

    def test_mask_tolerates_missing_provenance(self):
        self.assertEqual(gen_array.mask_klayout_version({}), {})


class TestReadPin(unittest.TestCase):
    def test_reads_pin(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "toolchain.json"
            path.write_text(json.dumps({"klayout_package_pin": "0.30.12"}))
            self.assertEqual(gen_array.read_pin(path), "0.30.12")

    def test_absent_pin_fails_loudly(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "toolchain.json"
            path.write_text(json.dumps({"klt_install": "x"}))
            with self.assertRaises(SystemExit):
                gen_array.read_pin(path)

    def test_malformed_json_fails_loudly(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "toolchain.json"
            path.write_text("{not json")
            with self.assertRaises(SystemExit):
                gen_array.read_pin(path)


if __name__ == "__main__":
    unittest.main()
