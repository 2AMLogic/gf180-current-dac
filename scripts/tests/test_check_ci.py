#!/usr/bin/env python3
"""Unit tests for check_ci.py's per-entry SKIP contract (issue #99) and the
WORK_LOG.md citation gate (issue #113).

Exit 2 from a TESTS child reports SKIP only where the entry is explicitly
marked may_skip — today only `layout/gen_array.py --check`, whose klayout
import may legitimately be absent. Any other entry exiting 2 (e.g. an
argparse usage error after a flag rename) is a break and must fail the
gate, never pass silently. The stubs are real child processes (`sys.exit`)
so the actual return-code path is exercised, not a mocked subprocess.

The Work Log tests stub the forge resolver; the default-resolver tests
(issue #116) mock `urllib.request.urlopen` instead. No test here touches
the network, with or without GITHUB_TOKEN.

The merge-queue trigger gate (issue #127) tests are file-injected except
the regression guard, which reads the committed ci.yml.

Verify with `python3 -m unittest scripts.tests.test_check_ci` from the
repo root (or let `python3 scripts/check_ci.py` run it as part of TESTS).
"""

import contextlib
import io
import json
import os
import re
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


def _fake_item(number, title, pr=False):
    data = {"number": number, "title": title}
    if pr:
        data["pull_request"] = {"url": f"https://api.github.com/repos/o/r/pulls/{number}"}
    return data


def _response(payload):
    resp = unittest.mock.MagicMock()
    resp.__enter__.return_value.read.return_value = json.dumps(payload).encode()
    return resp


class TestDefaultResolver(unittest.TestCase):
    """The default resolver `_fetch_item`: paginated, memoized (issue #116).

    The resolver fetches one paginated `issues?state=all` listing per
    process and answers later numbers from the map, so a run costs
    O(pages) requests no matter how many distinct numbers WORK_LOG.md
    cites. urlopen is mocked; no test here touches the network.
    """

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "WORK_LOG.md"
        patcher = unittest.mock.patch.dict(
            os.environ, {"GITHUB_TOKEN": "test-token",
                         "GITHUB_REPOSITORY": "owner/repo"})
        patcher.start()
        self.addCleanup(patcher.stop)
        # Hide the gate's own ok/SKIP prints; unittest reports on stderr.
        self._stdout = contextlib.redirect_stdout(io.StringIO())
        self._stdout.__enter__()
        self.addCleanup(self._stdout.__exit__, None, None, None)
        # Each test starts with a cold per-process memo.
        self._saved_items = check_ci._ITEMS
        check_ci._ITEMS = None
        self.addCleanup(setattr, check_ci, "_ITEMS", self._saved_items)
        self._saved_error = check_ci._ITEMS_ERROR
        check_ci._ITEMS_ERROR = None
        self.addCleanup(setattr, check_ci, "_ITEMS_ERROR", self._saved_error)
        self.urlopen_calls = []
        patcher = unittest.mock.patch.object(
            check_ci.urllib.request, "urlopen", side_effect=self._fake_urlopen)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _fake_urlopen(self, req, timeout=None):
        url = req.get_full_url()
        self.urlopen_calls.append(url)
        # Anchor so `per_page=100` can't match as the page number.
        page = int(re.search(r"[?&]page=(\d+)", url).group(1))
        if page == 1:
            # A full first page (100 items) forces the second request.
            return _response(
                [_fake_item(n, f"item {n}", pr=n % 2 == 1)
                 for n in range(1, 101)])
        return _response([_fake_item(101, "second page item")])

    def run_gate(self, errors, text):
        self.path.write_text(text)
        check_ci.check_work_log(errors, path=self.path)

    def test_two_pages_cover_all_citations(self):
        errors = []
        self.run_gate(errors, "- **Issue #2** (closed): item 2\n"
                              "- **PR #99** (closed): item 99\n"
                              "- **Issue #101** (closed): second page item\n"
                              "- **Issue #2** (closed): item 2\n")
        self.assertEqual(errors, [])
        # One request per page, not per distinct citation.
        self.assertEqual(len(self.urlopen_calls), 2)
        self.assertIn("page=1", self.urlopen_calls[0])
        self.assertIn("page=2", self.urlopen_calls[1])

    def test_absent_number_is_does_not_exist_error(self):
        errors = []
        self.run_gate(errors, "- **Issue #500** (closed): fabricated entry\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("#500", errors[0])
        self.assertIn("does not exist", errors[0])

    def test_kind_comes_from_pull_request_key(self):
        # Odd numbers carry pull_request in the fake listing, so #3 is a PR.
        errors = []
        self.run_gate(errors, "- **Issue #3** (closed): item 3\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("is a PR", errors[0])

    def test_page_failure_is_an_error_not_a_skip(self):
        def failing(req, timeout=None):
            url = req.get_full_url()
            if "page=2" in url:
                self.urlopen_calls.append(url)
                raise check_ci.urllib.error.HTTPError(
                    url, 403, "rate limited", None, None)
            return self._fake_urlopen(req, timeout)

        check_ci.urllib.request.urlopen.side_effect = failing
        # Two distinct citations: the failed walk is memoized, so the
        # second citation re-raises without walking again — 2 requests,
        # not 4.
        errors = []
        self.run_gate(errors, "- **Issue #2** (closed): item 2\n"
                              "- **Issue #99** (closed): item 99\n")
        self.assertEqual(len(errors), 2)
        for err in errors:
            self.assertIn("forge lookup failed", err)
        self.assertEqual(len(self.urlopen_calls), 2)
        self.assertIn("page=1", self.urlopen_calls[0])
        self.assertIn("page=2", self.urlopen_calls[1])


class TestMergeQueueTrigger(unittest.TestCase):
    """check_merge_queue_trigger: ci.yml declares merge_group (issue #127).

    The chip merge queue cannot run the required checks without the
    trigger, so the gate must fail closed on a missing or filtered one.
    """

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "ci.yml"
        # Hide the gate's own ok prints; unittest reports on stderr.
        self._stdout = contextlib.redirect_stdout(io.StringIO())
        self._stdout.__enter__()
        self.addCleanup(self._stdout.__exit__, None, None, None)

    def run_gate(self, errors, text):
        self.path.write_text(text)
        check_ci.check_merge_queue_trigger(errors, path=self.path)

    def test_committed_workflow_declares_merge_group(self):
        # The regression guard against the real file: dropping or
        # filtering the trigger re-breaks the merge queue (issue #127).
        errors = []
        check_ci.check_merge_queue_trigger(errors)
        self.assertEqual(errors, [])

    def test_declared_bare_trigger_passes(self):
        errors = []
        self.run_gate(errors,
                      "name: ci\n"
                      "on:\n"
                      "  push:\n"
                      "    branches: [main]\n"
                      "  pull_request:\n"
                      "  merge_group:\n"
                      "  workflow_dispatch:\n"
                      "jobs:\n"
                      "  checks: {}\n")
        self.assertEqual(errors, [])

    def test_missing_trigger_fails(self):
        errors = []
        self.run_gate(errors,
                      "name: ci\n"
                      "on:\n"
                      "  push:\n"
                      "    branches: [main]\n"
                      "  pull_request:\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("merge_group", errors[0])

    def test_path_filter_fails(self):
        errors = []
        self.run_gate(errors,
                      "on:\n"
                      "  pull_request:\n"
                      "  merge_group:\n"
                      "    paths:\n"
                      '      - "layout/**"\n')
        self.assertEqual(len(errors), 1)
        self.assertIn("filters", errors[0])

    def test_three_space_filter_fails(self):
        # The filter scan is indent-relative: any code line indented more
        # than the trigger line is a filter, not just 4-space lines
        # (issue #131).
        errors = []
        self.run_gate(errors,
                      "on:\n"
                      "  merge_group:\n"
                      "   branches: [main]\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("filters", errors[0])

    def test_four_space_indent_bare_trigger_passes(self):
        # Four-space `on:` members are valid YAML: the trigger itself may
        # sit at four spaces, and must be found there (issue #131).
        errors = []
        self.run_gate(errors,
                      "name: ci\n"
                      "on:\n"
                      "    push:\n"
                      "        branches: [main]\n"
                      "    pull_request:\n"
                      "    merge_group:\n"
                      "    workflow_dispatch:\n"
                      "jobs:\n"
                      "  checks: {}\n")
        self.assertEqual(errors, [])

    def test_four_space_indent_filter_fails(self):
        # Same indent-relative rule at the deeper indent: a filter two
        # levels under a four-space trigger is still a filter (issue #131).
        errors = []
        self.run_gate(errors,
                      "on:\n"
                      "    pull_request:\n"
                      "    merge_group:\n"
                      "      paths:\n"
                      '        - "layout/**"\n')
        self.assertEqual(len(errors), 1)
        self.assertIn("filters", errors[0])

    def test_missing_on_block_fails(self):
        errors = []
        self.run_gate(errors, "name: ci\njobs:\n  checks: {}\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("`on:`", errors[0])


if __name__ == "__main__":
    unittest.main()
