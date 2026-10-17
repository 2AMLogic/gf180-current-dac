#!/usr/bin/env python3
"""Checks shared by `npm run check:ci` and the CI workflow.

Stdlib only. Run from anywhere; paths resolve against the repo root.

1. Every committed JSON config / evidence file parses. A file that does not
   exist yet (sim/pdk.json etc. arrive with the sim harness) is skipped.
2. A file is also checked against a schema when a sibling `<name>.schema.json`
   is committed; none exist yet, so this is a parse-only check today.
3. The harness self-test runs if `sim/selftest.sh` exists (no-op until then).
4. Relative links in README.md resolve.
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
]
SELFTEST = "sim/selftest.sh"
LINK_DOCS = ["README.md"]
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")


def check_json(errors):
    for rel in JSON_FILES:
        path = ROOT / rel
        if not path.exists():
            print(f"skip   {rel} (not present)")
            continue
        try:
            json.loads(path.read_text())
        except ValueError as exc:
            errors.append(f"{rel}: invalid JSON: {exc}")
            continue
        print(f"ok     {rel}")
        schema = path.with_suffix(".schema.json")
        if schema.exists():
            errors.extend(validate_schema(path, schema))


def validate_schema(path, schema):
    try:
        import jsonschema
    except ImportError:
        return [f"{schema.relative_to(ROOT)} exists but the jsonschema package is not installed"]
    try:
        jsonschema.validate(json.loads(path.read_text()), json.loads(schema.read_text()))
    except jsonschema.ValidationError as exc:
        return [f"{path.relative_to(ROOT)}: schema violation: {exc.message}"]
    return []


def check_selftest(errors):
    script = ROOT / SELFTEST
    if not script.exists():
        print(f"skip   {SELFTEST} (no harness yet)")
        return
    if subprocess.run(["bash", str(script)], cwd=ROOT).returncode != 0:
        errors.append(f"{SELFTEST} failed")
    else:
        print(f"ok     {SELFTEST}")


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
    check_selftest(errors)
    check_links(errors)
    for err in errors:
        print(f"FAIL   {err}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
