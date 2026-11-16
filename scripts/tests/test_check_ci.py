#!/usr/bin/env python3
"""Unit tests for check_ci.py's per-entry SKIP contract (issue #99) and the
WORK_LOG.md citation gate (issue #113).

Exit 2 from a TESTS child reports SKIP only where the entry is explicitly
marked may_skip — today only `layout/gen_array.py --check`, whose klayout
import may legitimately be absent. Any other entry exiting 2 (e.g. an
argparse usage error after a flag rename) is a break and must fail the
gate, never pass silently. The stubs are real child processes (`sys.exit`)
so the actual return-code path is exercised, not a mocked subprocess.

The Work Log tests stub the forge resolver: no test here touches the
network, with or without GITHUB_TOKEN.

Verify with `python3 -m unittest scripts.tests.test_check_ci` from the
repo root (or let `python3 scripts/check_ci.py` run it as part of TESTS).
"""

import contextlib
import io
import os
import sys
import unittest
import unittest.mock
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


REAL_ITEMS = {
    1: ("PR", "feat: real pull request title"),
    2: ("Issue", "real issue title"),
    3: ("Issue", "still-open issue title"),
}


class StubResolver:
    """Resolver double: answers from REAL_ITEMS, records every call."""

    def __init__(self, missing=()):
        self.missing = set(missing)
        self.calls = []

    def __call__(self, number):
        self.calls.append(number)
        if number in self.missing:
            return None
        return REAL_ITEMS[number]


class TestWorkLogGate(unittest.TestCase):
    """check_work_log: every WORK_LOG.md citation resolves (issue #113)."""

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "WORK_LOG.md"
        self.resolver = StubResolver()
        env = {"GITHUB_TOKEN": "test-token"}
        patcher = unittest.mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        # Hide the gate's own ok/SKIP prints; unittest reports on stderr.
        self._stdout = contextlib.redirect_stdout(io.StringIO())
        self._stdout.__enter__()
        self.addCleanup(self._stdout.__exit__, None, None, None)

    def run_gate(self, errors, text):
        self.path.write_text(text)
        check_ci.check_work_log(errors, resolve=self.resolver, path=self.path)

    def test_clean_file_passes(self):
        errors = []
        self.run_gate(errors, "- **PR #1**: feat: real pull request title\n"
                              "- **Issue #2** (closed): real issue title\n")
        self.assertEqual(errors, [])

    def test_nonexistent_number_fails(self):
        errors = []
        self.resolver = StubResolver(missing={124})
        self.run_gate(errors, "- **Issue #124** (closed): fabricated entry\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("#124", errors[0])
        self.assertIn("does not exist", errors[0])

    def test_wrong_title_fails_and_names_real_title(self):
        errors = []
        self.run_gate(errors, "- **PR #1**: wrong title\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("wrong title", errors[0])
        self.assertIn("feat: real pull request title", errors[0])

    def test_kind_mismatch_fails(self):
        errors = []
        self.run_gate(errors, "- **Issue #1** (closed): feat: real pull request title\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("PR", errors[0])

    def test_no_token_is_explicit_skip(self):
        del os.environ["GITHUB_TOKEN"]
        failing = StubResolver()
        failing.__call__ = lambda number: (_ for _ in ()).throw(
            AssertionError("resolver must not run without a token"))
        errors = []
        self.path.write_text("- **PR #1**: feat: real pull request title\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            check_ci.check_work_log(errors, resolve=failing, path=self.path)
        self.assertEqual(errors, [])
        self.assertIn("SKIP", out.getvalue())

    def test_resolver_failure_is_an_error_not_a_skip(self):
        errors = []

        def raising(number):
            raise OSError("network down")

        self.path.write_text("- **PR #1**: feat: real pull request title\n")
        check_ci.check_work_log(errors, resolve=raising, path=self.path)
        self.assertEqual(len(errors), 1)
        self.assertIn("forge lookup failed", errors[0])

    def test_closed_annotation_is_lenient_about_state(self):
        # An entry may be written by the very PR that closes the issue, so
        # the (closed) annotation is not checked against the real state.
        errors = []
        self.run_gate(errors, "- **Issue #3** (closed): still-open issue title\n")
        self.assertEqual(errors, [])

    def test_untitled_citation_checks_number_and_kind_only(self):
        errors = []
        self.run_gate(errors, "see **Issue #2** for context\n")
        self.assertEqual(errors, [])
        errors = []
        self.run_gate(errors, "see **PR #2** for context\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("Issue", errors[0])

    def test_each_distinct_number_is_resolved_once(self):
        errors = []
        self.run_gate(errors, "- **Issue #2** (closed): real issue title\n"
                              "- **Issue #2** (closed): real issue title\n")
        self.assertEqual(errors, [])
        self.assertEqual(self.resolver.calls, [2])

    def test_missing_file_is_an_error(self):
        errors = []
        check_ci.check_work_log(errors, resolve=self.resolver,
                                path=Path(self._tmp.name) / "absent.md")
        self.assertEqual(len(errors), 1)

    def test_no_citations_is_an_error(self):
        errors = []
        self.run_gate(errors, "# Work Log\n\nno entries yet\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("no **Issue", errors[0])


if __name__ == "__main__":
    unittest.main()
