#!/usr/bin/env python3
"""Checks shared by `npm run check:ci` and the CI workflow.

Stdlib only. Run from anywhere; paths resolve against the repo root.

1. Every committed JSON config / evidence file parses; a missing file is an
   error.
2. The harness and spec unit tests and the spec structural check pass.
3. Relative links in README.md resolve.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

JSON_FILES = [
    "sim/pdk.json",
    "sim/toolchain.json",
    "layout/toolchain.json",
    "manifests/gf180-current-dac.json",
    "manifests/gf180-current-dac.signoff.json",
    "design/inventory-item1-analog.json",
    "evidence/item1-analog.json",
    "design/inventory-item1-digital.json",
    "evidence/item1-digital.json",
    "synth/decoder.request.json",
    "synth/decoder.report.json",
    "synth/dac_digital.request.json",
    "synth/dac_digital.report.json",
    "evidence/item2-analog.json",
    "evidence/item2-digital.json",
    "evidence/item3-analog.json",
    "evidence/item3-digital.json",
    "layout/pnr/request.json",
    "layout/pnr/dac_digital.report.json",
    "layout/switching_sequence.json",
    "attest/item10.json",
]
TESTS = [
    [sys.executable, "-m", "unittest", "sim.harness.test_check", "spec.tests.test_check_spec"],
    [sys.executable, "spec/check_spec.py"],
    [sys.executable, "design/gen_analog.py", "--check"],
    [sys.executable, "layout/gen_array.py", "--check"],
]
LINK_DOCS = ["README.md"]
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")


def check_json(errors):
    for rel in JSON_FILES:
        path = ROOT / rel
        try:
            json.loads(path.read_text())
        except (OSError, ValueError) as exc:
            errors.append(f"{rel}: unreadable or invalid JSON: {exc}")
            continue
        print(f"ok     {rel}")


def check_tests(errors):
    for cmd in TESTS:
        label = " ".join(cmd[1:])
        if subprocess.run(cmd, cwd=ROOT).returncode != 0:
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
