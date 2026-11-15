#!/usr/bin/env python3
"""Unit tests for check_ci.py's per-entry SKIP contract (issue #99).

Exit 2 from a TESTS child reports SKIP only where the entry is explicitly
marked may_skip — today only `layout/gen_array.py --check`, whose klayout
import may legitimately be absent. Any other entry exiting 2 (e.g. an
argparse usage error after a flag rename) is a break and must fail the
gate, never pass silently. The stubs are real child processes (`sys.exit`)
so the actual return-code path is exercised, not a mocked subprocess.

Verify with `python3 -m unittest scripts.tests.test_check_ci` from the
repo root (or let `python3 scripts/check_ci.py` run it as part of TESTS).
"""

import contextlib
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import scripts.check_ci as check_ci


def stub(entry):
    return [sys.executable, "-c", entry]


class TestPerEntrySkipContract(unittest.TestCase):
    def setUp(self):
        self._saved = check_ci.TESTS
        # check_tests() prints its own SKIP/ok lines, and this module runs
        # inside the gate's own TESTS entry — let nothing reach the gate's
        # stdout. unittest reports results on stderr, so this hides only the
        # synthetic lines.
        self._stdout = contextlib.redirect_stdout(io.StringIO())
        self._stdout.__enter__()
        self.addCleanup(self._stdout.__exit__, None, None, None)

    def tearDown(self):
        check_ci.TESTS = self._saved

    def test_skippable_exit2_is_skip(self):
        check_ci.TESTS = [(stub("import sys; sys.exit(2)"), True)]
        errors = []
        check_ci.check_tests(errors)
        self.assertEqual(errors, [])

    def test_non_skippable_exit2_is_error(self):
        check_ci.TESTS = [(stub("import sys; sys.exit(2)"), False)]
        errors = []
        check_ci.check_tests(errors)
        self.assertEqual(len(errors), 1)
        self.assertIn("failed", errors[0])

    def test_nonzero_exit1_is_error_even_when_skippable(self):
        # A bad unittest module name exits 1; SKIP never applies to it.
        check_ci.TESTS = [(stub("import sys; sys.exit(1)"), True)]
        errors = []
        check_ci.check_tests(errors)
        self.assertEqual(len(errors), 1)

    def test_zero_exit_is_ok(self):
        check_ci.TESTS = [(stub("pass"), False)]
        errors = []
        check_ci.check_tests(errors)
        self.assertEqual(errors, [])

    def test_only_gen_array_may_skip(self):
        # The allowlist must not widen silently: gen_array's klayout
        # provisioning gap is the only sanctioned reason to skip.
        marked = [" ".join(cmd[1:]) for cmd, may_skip in check_ci.TESTS if may_skip]
        self.assertEqual(len(marked), 1)
        self.assertIn("layout/gen_array.py --check", marked[0])


if __name__ == "__main__":
    unittest.main()
