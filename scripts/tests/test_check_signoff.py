#!/usr/bin/env python3
"""Integration tests for scripts/check_signoff.sh's remediation output
(issue #129).

The script's only external dependency, `uvx ... klt signoff`, is stubbed:
a fake `uvx` first on PATH cats a fixture "fresh" grading JSON, so the three
remediation paths run offline --

- a stale_evidence item with attestation binding members prints the
  per-item re-attest command, before the record-regeneration message,
  while a stale_evidence item with no members (a stale pin, a drifted
  provenance input) gets no --attest hint at all;
- a genuinely stale record with no stale_evidence keeps the old
  regenerate-only message;
- a matching record exits 0 with the `signoff record fresh` line.

No klt install and no network involved.

Verify with `python3 -m unittest scripts.tests.test_check_signoff` from the
repo root (or let `python3 scripts/check_ci.py` run it as part of TESTS).
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_signoff.sh"


def stale_item(item_id, members):
    return {
        "tier": "T1",
        "id": item_id,
        "title": "Repo hygiene",
        "status": "unmet",
        "reason": "stale_evidence",
        "graded_by_build": True,
        "citation": None,
        "detail": {
            "artifact_binding": {
                "members": [
                    {"path": p, "content_hash": "sha256:" + "0" * 64, "status": "stale"}
                    for p in members
                ]
            }
        },
    }


def non_attest_stale_item(item_id):
    """A stale_evidence item whose detail has no attestation binding (the
    stale-pin shape): there is no envelope to re-attest, so the hint block
    must leave it to the regenerate message."""
    return {
        "tier": "T1",
        "id": item_id,
        "title": "Layout artifacts exist",
        "status": "unmet",
        "reason": "stale_evidence",
        "graded_by_build": True,
        "citation": None,
        "detail": {
            "content_hash_pin": "stale",
            "hash_check": {"path": "layout/gf180-current-dac-analog.gds"},
        },
    }


def grading(met, items):
    return {
        "schema_version": 1,
        "block": "fixture",
        "kind": "mixed-signal",
        "tier": "T1",
        "t1_item_count": 2,
        "t1_met_count": met,
        "items": items,
    }


class TestCheckSignoffHints(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="check-signoff-test-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / "scripts").mkdir()
        shutil.copy(SCRIPT, self.tmp / "scripts" / "check_signoff.sh")
        for d in ("manifests", "evidence", "attest", "bin"):
            (self.tmp / d).mkdir()
        # The manifest's evidence map and the envelope's source field are what
        # the hint block walks to build the re-attest command.
        (self.tmp / "manifests" / "gf180-current-dac.json").write_text(
            json.dumps({"evidence": {"10": {"file": "evidence/item10.json"}}})
        )
        (self.tmp / "evidence" / "item10.json").write_text(
            json.dumps({"source": "attest/item10.json"})
        )
        stub = self.tmp / "bin" / "uvx"
        self.fresh = self.tmp / "fresh.json"
        stub.write_text("#!/bin/sh\ncat '%s'\n" % self.fresh)
        stub.chmod(0o755)
        self.committed = self.tmp / "manifests" / "gf180-current-dac.signoff.json"
        self.env = dict(os.environ, PATH=f"{self.tmp / 'bin'}:{os.environ['PATH']}")

    def run_script(self):
        return subprocess.run(
            [str(self.tmp / "scripts" / "check_signoff.sh")],
            capture_output=True,
            text=True,
            env=self.env,
        )

    def write_fixtures(self, fresh, committed):
        self.fresh.write_text(json.dumps(fresh))
        self.committed.write_text(json.dumps(committed))

    def test_drift_names_item_and_attest_command_first(self):
        self.write_fixtures(
            grading(1, [stale_item(10, ["README.md", "ci.yml"])]), grading(2, [])
        )
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        attest = r.stderr.index(
            "--attest 10 --inventory attest/item10.json -o evidence/item10.json"
        )
        self.assertIn("T1 item 10", r.stderr)
        self.assertIn("README.md", r.stderr)
        self.assertLess(attest, r.stderr.index("Committed signoff record is stale"))
        # both remediations appear: re-attest, then the regenerate command
        self.assertIn(
            "--manifest manifests/gf180-current-dac.json", r.stderr[attest:]
        )

    def test_multiple_drifted_items_each_get_a_command(self):
        (self.tmp / "manifests" / "gf180-current-dac.json").write_text(json.dumps(
            {"evidence": {
                "9": {"file": "evidence/item9.json"},
                "10": {"file": "evidence/item10.json"},
            }}
        ))
        (self.tmp / "evidence" / "item9.json").write_text(
            json.dumps({"source": "attest/item9.json"})
        )
        self.write_fixtures(
            grading(0, [stale_item(9, ["sim/smoke/cs_tb.spice"]), stale_item(10, ["LICENSE"])]),
            grading(2, []),
        )
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("--attest 9 --inventory attest/item9.json -o evidence/item9.json", r.stderr)
        self.assertIn("--attest 10 --inventory attest/item10.json -o evidence/item10.json", r.stderr)
        self.assertLess(
            r.stderr.index("--attest 9"), r.stderr.index("--attest 10")
        )

    def test_non_attest_stale_item_gets_no_attest_hint(self):
        self.write_fixtures(
            grading(1, [non_attest_stale_item(2)]), grading(2, [])
        )
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("--attest", r.stderr)
        self.assertNotIn("Attestation envelope drifted", r.stderr)
        self.assertIn("Committed signoff record is stale. Regenerate:", r.stderr)

    def test_genuinely_stale_record_output_unchanged(self):
        self.write_fixtures(grading(2, []), grading(1, []))
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("Committed signoff record is stale. Regenerate:", r.stderr)
        self.assertNotIn("--attest", r.stderr)
        self.assertNotIn("stale_evidence", r.stderr)

    def test_clean_tree_exits_zero(self):
        same = grading(2, [])
        self.write_fixtures(same, same)
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("signoff record fresh: tier T1 (T1 met 2/2)", r.stdout)
        self.assertEqual(r.stderr, "")


if __name__ == "__main__":
    unittest.main()
