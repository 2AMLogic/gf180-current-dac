#!/usr/bin/env python3
"""Checks shared by `npm run check:ci` and the CI workflow.

Stdlib only. Run from anywhere; paths resolve against the repo root.

1. Every committed JSON config / evidence file parses; a missing file is an
   error.
2. The harness, spec, design and gen_array unit tests and the spec
   structural check pass. Only an entry explicitly marked skippable may report SKIP (child
   exit 2 — today only gen_array --check, whose klayout import may be
   absent as a provisioning gap); any other entry exiting 2 is an error,
   not a skip.
3. Relative links in README.md resolve.
4. Every `**Issue #N**` / `**PR #N**` citation in WORK_LOG.md resolves to a
   real item of the same kind with the same title. Resolution needs
   GITHUB_TOKEN; without it the gate prints an explicit SKIP line and
   never silently passes (issue #113 — a docs-only PR once added 59
   entries from another project, all gates green).
5. The CI workflow declares a bare `merge_group:` trigger (issue #127 —
   the chip merge queue cannot run the required checks without it, and
   repo-ruleset-policy.py refuses the queue until the trigger exists).
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Committed JSON files whose *absence* is caught by no other job — not cited
# by the manifests (which byte-compare in check_signoff.sh), not passed to
# `klt signoff --attest` in ci.yml, and not loaded by any TESTS entry.
# `git ls-files` reads the index, so a committed deletion drops a path from
# the enumeration silently; these must fail loudly instead.
REQUIRED_JSON = [
    "layout/toolchain.json",
    "design/inventory-item1-digital.json",
    "synth/decoder.request.json",
    "synth/decoder.report.json",
    "synth/dac_digital.request.json",
    "synth/dac_digital.report.json",
    "layout/pnr/request.json",
]
# Entries carry the right to skip explicitly: exit 2 means SKIP only where
# may_skip is True, so a broken invocation (an argparse usage error after a
# flag rename, say) fails the gate instead of passing as a skip. New entries
# default to False.
TESTS = [
    ([sys.executable, "-m", "unittest", "design.tests.test_gen_analog",
     "sim.harness.test_check", "spec.tests.test_check_spec",
     "layout.tests.test_gen_array_check", "scripts.tests.test_check_ci",
     "scripts.tests.test_check_signoff", "design.tests.test_prim_params"], False),
    ([sys.executable, "spec/check_spec.py"], False),
    ([sys.executable, "design/gen_analog.py", "--check"], False),
    # klayout absent at import time is a provisioning gap, not a failure (#87).
    ([sys.executable, "layout/gen_array.py", "--check"], True),
]
LINK_DOCS = ["README.md"]
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")

# Work Log citation gate (issue #113). A citation is `**Issue #N**` or
# `**PR #N**`; the entry usually continues with an optional `(closed)`/
# `(open)` annotation and the item title after `: `. The annotation is
# deliberately NOT checked against the real state: an entry may be written
# by the very PR that closes its issue, so the item can still be open at
# CI time even though the log truthfully records the outcome.
WORK_LOG = "WORK_LOG.md"
CITE_RE = re.compile(r"\*\*(Issue|PR) #(\d+)\*\*")
CITE_TITLE_RE = re.compile(r"(?: \((?:closed|open)\))?: (\S.*)")


def check_json(errors):
    out = subprocess.run(
        ["git", "ls-files", "*.json"], cwd=ROOT, capture_output=True, text=True
    )
    if out.returncode != 0:
        errors.append(f"git ls-files failed: {out.stderr.strip()}")
        return
    # Installed tooling trees, not hand-written here; nothing in them is a
    # parse target of this repo's gate.
    skip = (".loom/", ".claude/", ".agents/", ".github/")
    files = sorted(p for p in out.stdout.split() if not p.startswith(skip))
    if not files:
        errors.append("git ls-files discovered no JSON files; nothing to parse")
        return
    before = len(errors)
    for rel in REQUIRED_JSON:
        if rel not in files:
            errors.append(f"{rel}: required JSON file is not in the git index")
    parsed = 0
    for rel in files:
        try:
            json.loads((ROOT / rel).read_text())
        except (OSError, ValueError) as exc:
            errors.append(f"{rel}: unreadable or invalid JSON: {exc}")
            continue
        parsed += 1
    if len(errors) == before:
        print(f"ok     {parsed} JSON files parse")


def check_tests(errors):
    for cmd, may_skip in TESTS:
        label = " ".join(cmd[1:])
        rc = subprocess.run(cmd, cwd=ROOT).returncode
        if rc == 2 and may_skip:
            print(f"SKIP   {label}")
        elif rc != 0:
            errors.append(f"{label} failed")
        else:
            print(f"ok     {label}")


def check_links(errors):
    for rel in LINK_DOCS:
        doc = ROOT / rel
        for target in LINK_RE.findall(doc.read_text()):
            if re.match(r"[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            if not (doc.parent / target.split("#")[0]).exists():
                errors.append(f"{rel}: dead relative link: {target}")
        print(f"ok     links in {rel}")


def _norm_title(title):
    return re.sub(r"\s+", " ", title.lower().strip())


def _repo_slug():
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo:
        return repo
    out = subprocess.run(
        ["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True
    )
    if out.returncode != 0:
        return None
    m = re.search(r"[:/]([^/:]+/[^/:\s]+?)(?:\.git)?/?$", out.stdout.strip())
    return m.group(1) if m else None


def _fetch_all_items():
    """Fetch every issue and PR of this repository, paginated (issue #116).

    `GET /repos/{slug}/issues?state=all&per_page=100` lists both kinds,
    so one listing covers every citation a run can make; a page shorter
    than the page size ends the walk. Any non-2xx or network error
    raises — strictness is unchanged from the per-number resolver.
    """
    repo = _repo_slug()
    if not repo:
        raise RuntimeError("cannot determine the repository slug for forge lookups")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "check_ci.py"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    items = {}
    page = 1
    while True:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/issues"
            f"?state=all&per_page=100&page={page}",
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            batch = json.load(resp)
        for data in batch:
            kind = "PR" if data.get("pull_request") is not None else "Issue"
            items[data["number"]] = (kind, data["title"])
        if len(batch) < 100:
            return items
        page += 1


_ITEMS = None
_ITEMS_ERROR = None


def _fetch_item(number):
    """Resolve one item: (kind, title), or None when it does not exist.

    The item map is fetched once per process and memoized in `_ITEMS`
    (issue #116): O(pages) requests per run, not one per distinct
    citation. A failed walk is memoized too, in `_ITEMS_ERROR`, so the
    listing is attempted at most once per process — during a rate-limit
    outage each further citation must not hammer the forge again. A
    number absent from the map answers None; anything else (no slug,
    rate limit, network down) raises, so a token-carrying run can never
    silently pass.
    """
    global _ITEMS, _ITEMS_ERROR
    if _ITEMS_ERROR is not None:
        raise _ITEMS_ERROR
    if _ITEMS is None:
        try:
            _ITEMS = _fetch_all_items()
        except Exception as exc:
            _ITEMS_ERROR = exc
            raise
    return _ITEMS.get(number)


def check_work_log(errors, resolve=None, path=None):
    """Every WORK_LOG.md citation resolves to a real item of the same kind
    and title (issue #113). `resolve` is injectable so tests stub the forge."""
    doc = Path(path) if path is not None else ROOT / WORK_LOG
    try:
        text = doc.read_text()
    except OSError as exc:
        errors.append(f"{doc}: unreadable: {exc}")
        return
    if not os.environ.get("GITHUB_TOKEN"):
        print(f"SKIP   {WORK_LOG} citations (GITHUB_TOKEN not set)")
        return
    resolve = resolve or _fetch_item
    cites = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for m in CITE_RE.finditer(line):
            title = CITE_TITLE_RE.match(line, m.end())
            cites.append(
                (line_no, m.group(1), int(m.group(2)),
                 title.group(1) if title else None)
            )
    if not cites:
        errors.append(
            f"{WORK_LOG}: no **Issue #N**/**PR #N** citations found; "
            "the citation extractor sees nothing to check"
        )
        return
    cache = {}
    before = len(errors)
    for line_no, kind, number, title in cites:
        if number not in cache:
            try:
                cache[number] = resolve(number)
            except Exception as exc:
                cache[number] = ("lookup-error", str(exc))
        item = cache[number]
        if item is None:
            errors.append(
                f"{WORK_LOG}:{line_no}: cites {kind} #{number}, "
                "which does not exist in this repository"
            )
        elif item[0] == "lookup-error":
            errors.append(
                f"{WORK_LOG}:{line_no}: {kind} #{number}: forge lookup failed: {item[1]}"
            )
        elif item[0] != kind:
            errors.append(
                f"{WORK_LOG}:{line_no}: cites {kind} #{number} "
                f"but #{number} is a {item[0]} ({item[1]})"
            )
        elif title is not None and _norm_title(title) != _norm_title(item[1]):
            errors.append(
                f"{WORK_LOG}:{line_no}: {kind} #{number} title does not match: "
                f"log says {title!r}, forge says {item[1]!r}"
            )
    if len(errors) == before:
        print(f"ok     {len(cites)} {WORK_LOG} citations resolve")


# Merge-queue readiness gate (issue #127; rollout 2AMLogic/2am#7605). The
# queue runs this workflow per group entry, and a missing or filtered
# trigger either skips the checks or silently narrows what the queue gates
# on. Text-parsed on purpose: the module is stdlib-only and the assertions
# it needs are line-shaped, so a yaml dependency is not warranted.
CI_WORKFLOW = ".github/workflows/ci.yml"
ON_BLOCK_RE = re.compile(r'^(?:on|"on"):\s*$')
# Any leading indent: the trigger is matched relative to the file's own
# `on:` layout, not a pinned two-space convention (issue #131).
MERGE_GROUP_RE = re.compile(r"^\s+merge_group:\s*(?:#.*)?$")


def _on_block(text):
    """The indented body of the workflow's top-level `on:` block, or None.

    The block runs from the line after a bare `on:` to the first
    non-indented, non-blank, non-comment line. A flow-style `on: [push]`
    does not match and returns None — fail closed; the caller reports it.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if ON_BLOCK_RE.match(line):
            block = []
            for body in lines[i + 1:]:
                if body.strip() == "" or body.lstrip().startswith("#"):
                    block.append(body)
                elif body[:1].isspace():
                    block.append(body)
                else:
                    break
            return block
    return None


def check_merge_queue_trigger(errors, path=None):
    """`ci.yml` declares a bare `merge_group:` trigger (issue #127).

    Bare means no `paths`/`branches-ignore` filter and no inline value:
    the queue must run the required checks on every group entry for the
    default branch, so any filter would silently narrow what the queue
    gates on. `path` is injectable so tests run against synthetic files;
    the default reads the committed workflow as the regression guard.
    """
    doc = Path(path) if path is not None else ROOT / CI_WORKFLOW
    try:
        text = doc.read_text()
    except OSError as exc:
        errors.append(f"{doc}: unreadable: {exc}")
        return
    block = _on_block(text)
    if block is None:
        errors.append(f"{CI_WORKFLOW}: no block-style top-level `on:` block found")
        return
    code = [
        line for line in block
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not [line for line in code if MERGE_GROUP_RE.match(line)]:
        errors.append(
            f"{CI_WORKFLOW}: `on:` does not declare a bare `merge_group:` "
            "trigger; the merge queue cannot run the required checks and "
            "repo-ruleset-policy.py refuses the queue (issue #127)"
        )
        return
    i = next(i for i, line in enumerate(code) if MERGE_GROUP_RE.match(line))
    # Indent-relative: a filter is any code line indented deeper than the
    # trigger line itself, whatever the file's `on:` layout (issue #131).
    indent = len(code[i]) - len(code[i].lstrip())
    filters = []
    for line in code[i + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) > indent:
            filters.append(line.strip())
        else:
            break
    if filters:
        errors.append(
            f"{CI_WORKFLOW}: `merge_group:` declares filters {filters}; "
            "the queue trigger must stay unfiltered (issue #127)"
        )
        return
    print(f"ok     {CI_WORKFLOW} declares a bare merge_group trigger")


def main():
    errors = []
    check_json(errors)
    check_tests(errors)
    check_links(errors)
    check_merge_queue_trigger(errors)
    check_work_log(errors)
    for err in errors:
        print(f"FAIL   {err}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
