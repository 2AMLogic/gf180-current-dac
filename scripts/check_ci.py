#!/usr/bin/env python3
"""Checks shared by `npm run check:ci` and the CI workflow.

Stdlib only. Run from anywhere; paths resolve against the repo root.

1. Every committed JSON config / evidence file parses; a missing file is an
   error.
2. The harness, spec and gen_array unit tests and the spec structural check
   pass. Only an entry explicitly marked skippable may report SKIP (child
   exit 2 — today only gen_array --check, whose klayout import may be
   absent as a provisioning gap); any other entry exiting 2 is an error,
   not a skip.
3. Relative links in README.md resolve.
"""
import json
import re
import subprocess
import sys
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
    ([sys.executable, "-m", "unittest", "sim.harness.test_check", "spec.tests.test_check_spec",
     "layout.tests.test_gen_array_check", "scripts.tests.test_check_ci"], False),
    ([sys.executable, "spec/check_spec.py"], False),
    ([sys.executable, "design/gen_analog.py", "--check"], False),
    # klayout absent at import time is a provisioning gap, not a failure (#87).
    ([sys.executable, "layout/gen_array.py", "--check"], True),
]
LINK_DOCS = ["README.md"]
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")


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


def main():
    errors = []
    check_json(errors)
    check_tests(errors)
    check_links(errors)
    for err in errors:
        print(f"FAIL   {err}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
