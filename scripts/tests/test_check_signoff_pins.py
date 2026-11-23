#!/usr/bin/env python3
"""Unit and integration tests for scripts/check_signoff_pins.py (issue #170).

Fixtures are synthetic trees (a tmp root with a manifest and the files it
cites), covering: matching pins across single, list-valued and shared-file
entries; the PR #158 incident shape (`1.analog` pinned to the envelope
file's own hash rather than its `provenance.input.content_hash`); a wrong
member pin inside a list entry; and the loud-failure paths — a missing
cited file, a cited file without `provenance.input.content_hash`, invalid
JSON, an entry with no pin, a non-entry evidence value. The regression
test runs the check against the committed manifest, which is how
`scripts/check_ci.py` TESTS gates the real pins on every offline run.

The end-to-end cases run the script as a real subprocess (with the tmp root
as its argument), so the actual exit-code and stderr paths are exercised.
No klt install and no network involved.

Verify with `python3 -m unittest scripts.tests.test_check_signoff_pins`
from the repo root (or let `python3 scripts/check_ci.py` run it as part of
TESTS).
"""

import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.check_signoff_pins import check_evidence_pins

SCRIPT = ROOT / "scripts" / "check_signoff_pins.py"


def envelope(input_hash):
    """A minimal klt-report-shaped file: only `provenance.input.content_hash`
    is read by the check."""
    return {"provenance": {"input": {"content_hash": input_hash}}}


def write_manifest(root, evidence):
    (root / "manifests").mkdir(parents=True, exist_ok=True)
    (root / "manifests" / "gf180-current-dac.json").write_text(
        json.dumps({"evidence": evidence})
    )


class PinFixtureTree(unittest.TestCase):
    """A good tree: single entries, a list-valued entry, and two items
    citing one shared file (the 2.analog/3.analog shape)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="check-signoff-pins-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.hashes = {
            "evidence/item1-analog.json": "sha256:" + "1" * 64,
            "evidence/item9.json": "sha256:" + "9" * 64,
            "verification/lvs/analog.report.json": "sha256:" + "a" * 64,
            "verification/erc/digital.report.json": "sha256:" + "d" * 64,
        }
        for name, h in self.hashes.items():
            p = self.tmp / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(envelope(h)))
        self.good = {
            "1.analog": {
                "file": "evidence/item1-analog.json",
                "content_hash": self.hashes["evidence/item1-analog.json"],
            },
            "9": {
                "file": "evidence/item9.json",
                "content_hash": self.hashes["evidence/item9.json"],
            },
            "2.analog": {
                "file": "verification/lvs/analog.report.json",
                "content_hash": self.hashes[
                    "verification/lvs/analog.report.json"
                ],
            },
            "3.analog": {
                "file": "verification/lvs/analog.report.json",
                "content_hash": self.hashes[
                    "verification/lvs/analog.report.json"
                ],
            },
            "11.digital": [
                {
                    "file": "verification/erc/digital.report.json",
                    "content_hash": self.hashes[
                        "verification/erc/digital.report.json"
                    ],
                },
                {
                    "file": "verification/lvs/analog.report.json",
                    "content_hash": self.hashes[
                        "verification/lvs/analog.report.json"
                    ],
                },
            ],
        }

    def run_check(self, evidence="default"):
        if evidence == "default":
            evidence = self.good
        write_manifest(self.tmp, evidence)
        errors = []
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            check_evidence_pins(errors, root=self.tmp)
        return errors, out.getvalue()

    def test_matching_pins_pass(self):
        errors, out = self.run_check()
        self.assertEqual(errors, [])
        self.assertIn("ok     6 evidence pins", out)

    def test_incident_pin_fails_naming_item_file_and_both_hashes(self):
        # PR #158 head e17b358a pinned 1.analog to the envelope file's own
        # hash instead of its provenance.input.content_hash.
        wrong = "sha256:" + hashlib.sha256(
            (self.tmp / "evidence/item1-analog.json").read_bytes()
        ).hexdigest()
        bad = json.loads(json.dumps(self.good))
        bad["1.analog"]["content_hash"] = wrong
        errors, _ = self.run_check(bad)
        self.assertEqual(len(errors), 1)
        self.assertIn("'1.analog'", errors[0])
        self.assertIn("evidence/item1-analog.json", errors[0])
        self.assertIn(wrong, errors[0])
        self.assertIn(self.hashes["evidence/item1-analog.json"], errors[0])

    def test_list_member_mismatch_names_that_member_only(self):
        bad = json.loads(json.dumps(self.good))
        bad["11.digital"][1]["content_hash"] = "sha256:" + "f" * 64
        errors, _ = self.run_check(bad)
        self.assertEqual(len(errors), 1)
        self.assertIn("'11.digital'", errors[0])
        self.assertIn("verification/lvs/analog.report.json", errors[0])
        self.assertNotIn("erc", errors[0])

    def test_missing_file_fails_loudly(self):
        (self.tmp / "evidence/item9.json").unlink()
        errors, _ = self.run_check()
        self.assertEqual(len(errors), 1)
        self.assertIn("'9'", errors[0])
        self.assertIn("evidence/item9.json", errors[0])
        self.assertIn("unreadable", errors[0])

    def test_file_without_provenance_hash_fails_loudly(self):
        (self.tmp / "evidence/item9.json").write_text(
            json.dumps({"result": "fine, but not a klt-produced file"})
        )
        errors, _ = self.run_check()
        self.assertEqual(len(errors), 1)
        self.assertIn("no `provenance.input.content_hash`", errors[0])

    def test_malformed_provenance_input_preserves_other_pin_errors(self):
        cited = "evidence/item1-analog.json"
        (self.tmp / cited).write_text(
            json.dumps({"provenance": {"input": "attest/item1-analog.json"}})
        )
        self.good["9"]["content_hash"] = "sha256:" + "f" * 64
        errors, _ = self.run_check()
        self.assertEqual(len(errors), 2)
        self.assertIn(f"evidence['1.analog'] -> {cited}", errors[0])
        self.assertIn("no `provenance.input.content_hash`", errors[0])
        self.assertIn("evidence['9'] -> evidence/item9.json: pin", errors[1])
        self.assertIn("does not match", errors[1])

    def test_invalid_json_cited_file_fails_loudly(self):
        (self.tmp / "evidence/item9.json").write_text("{not json")
        errors, _ = self.run_check()
        self.assertEqual(len(errors), 1)
        self.assertIn("invalid JSON", errors[0])

    def test_entry_without_pin_fails_loudly(self):
        bad = json.loads(json.dumps(self.good))
        del bad["9"]["content_hash"]
        errors, _ = self.run_check(bad)
        self.assertEqual([e for e in errors if "'9'" in e], [errors[0]])
        self.assertIn("no `content_hash` pin", errors[0])

    def test_non_entry_value_fails_loudly(self):
        bad = json.loads(json.dumps(self.good))
        bad["12"] = "sha256:" + "c" * 64
        errors, _ = self.run_check(bad)
        self.assertEqual(len(errors), 1)
        self.assertIn("'12'", errors[0])
        self.assertIn("not an entry object", errors[0])

    def test_empty_evidence_map_is_an_error(self):
        errors, _ = self.run_check({})
        self.assertEqual(len(errors), 1)
        self.assertIn("no `evidence` map", errors[0])

    def test_missing_manifest_is_an_error(self):
        write_manifest(self.tmp, self.good)
        (self.tmp / "manifests" / "gf180-current-dac.json").unlink()
        errors = []
        check_evidence_pins(errors, root=self.tmp)
        self.assertEqual(len(errors), 1)
        self.assertIn("unreadable or invalid JSON", errors[0])


class ScriptEndToEnd(unittest.TestCase):
    """The script as a real subprocess: exit codes and stderr wording."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="check-signoff-pins-e2e-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        good_hash = "sha256:" + "7" * 64
        cited = self.tmp / "evidence/item1-analog.json"
        cited.parent.mkdir(parents=True)
        cited.write_text(json.dumps(envelope(good_hash)))
        self.good_manifest = {
            "1.analog": {"file": "evidence/item1-analog.json",
                         "content_hash": good_hash}
        }
        self.bad_manifest = {
            "1.analog": {
                "file": "evidence/item1-analog.json",
                "content_hash": "sha256:" + hashlib.sha256(
                    cited.read_bytes()
                ).hexdigest(),
            }
        }

    def run_script(self, manifest):
        write_manifest(self.tmp, manifest)
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.tmp)],
            capture_output=True,
            text=True,
        )

    def test_good_tree_exits_zero(self):
        r = self.run_script(self.good_manifest)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ok     1 evidence pins", r.stdout)
        self.assertEqual(r.stderr, "")

    def test_empty_evidence_list_exits_one_naming_item(self):
        r = self.run_script({**self.good_manifest, "11.digital": []})
        self.assertEqual(r.returncode, 1)
        self.assertIn("evidence['11.digital']", r.stderr)
        self.assertIn("empty list", r.stderr)
        self.assertEqual(r.stdout, "")

    def test_bad_pin_exits_one_naming_item_file_both_hashes(self):
        r = self.run_script(self.bad_manifest)
        self.assertEqual(r.returncode, 1)
        self.assertIn("'1.analog'", r.stderr)
        self.assertIn("evidence/item1-analog.json", r.stderr)
        self.assertIn(self.bad_manifest["1.analog"]["content_hash"], r.stderr)
        self.assertIn(
            self.good_manifest["1.analog"]["content_hash"], r.stderr
        )
        self.assertIn("FAIL", r.stderr)


class RegressionCommittedManifest(unittest.TestCase):
    """The committed manifest's pins re-derive cleanly. This is what makes
    `python3 scripts/check_ci.py` (and the item 10 attestation's audit run
    of it) gate the real evidence pins on every offline run."""

    def test_committed_pins_match(self):
        errors = []
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            check_evidence_pins(errors)
        self.assertEqual(errors, [])
        self.assertIn("evidence pins match", out.getvalue())


if __name__ == "__main__":
    unittest.main()
