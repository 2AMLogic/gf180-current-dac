#!/usr/bin/env python3
"""Re-derive every manifest evidence pin from its cited file (issue #170).

`scripts/check_signoff.sh` proves the committed grading record is *fresh*,
not that no T1 item got worse: a wrong `evidence` pin in
`manifests/gf180-current-dac.json` grades its item `unmet`/`stale_evidence`,
and regenerating the record then commits the lower `t1_met_count` as the
new baseline with every CI check green (seen on PR #158 head `e17b358a`:
`1.analog` pinned to the envelope file's own hash instead of its
`provenance.input.content_hash`).

This check is the ratchet: every `evidence` entry — single or list-valued —
must pin its cited file on the basis `klt signoff` grades it on: exactly
the `provenance.input.content_hash` when the file carries a `provenance`
block (a klt-produced report), or the `sha256:` of the file's own raw
bytes when it does not (`content_hash_basis: evidence_file` — the
functional-verification reports, issue #179) — so the "regenerate the
record" remediation can never paper over a pin that silently dropped a T1
item. A provenance-bearing file pinned to its own byte hash stays a
failure: that is the PR #158 class above. Pure stdlib, no klt, PDK,
network or merge base; it runs in the CI `signoff` job before the klt
regrade (precise diagnosis first) and its unit and regression tests run
inside `scripts/check_ci.py` TESTS.

Verify with `python3 scripts/check_signoff_pins.py` from anywhere (an
optional positional argument re-points the check at another tree root, for
the tests).
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = "manifests/gf180-current-dac.json"


def _check_one(errors, root, item, entry):
    file = entry.get("file")
    pin = entry.get("content_hash")
    label = f"{MANIFEST}: evidence[{item!r}]"
    if not isinstance(file, str) or not file:
        errors.append(f"{label}: entry has no `file` to re-derive the pin from")
        return
    if not isinstance(pin, str) or not pin:
        errors.append(f"{label} -> {file}: entry has no `content_hash` pin")
        return
    try:
        raw = (root / file).read_bytes()
        doc = json.loads(raw)
    except (OSError, ValueError) as exc:
        errors.append(
            f"{label} -> {file}: cannot re-derive pin: unreadable or "
            f"invalid JSON: {exc}"
        )
        return
    provenance = doc.get("provenance") if isinstance(doc, dict) else None
    if provenance is None:
        # No `provenance` block: not a klt-produced report, so the pin
        # basis is the file's own bytes (`content_hash_basis:
        # evidence_file`, issue #179).
        derived = "sha256:" + hashlib.sha256(raw).hexdigest()
        if pin != derived:
            errors.append(
                f"{label} -> {file}: pin {pin} does not match the file's "
                f"raw-bytes sha256 {derived} (no `provenance` block; "
                "content_hash_basis: evidence_file)"
            )
        return
    source = provenance.get("input") if isinstance(provenance, dict) else None
    derived = source.get("content_hash") if isinstance(source, dict) else None
    if not isinstance(derived, str) or not derived:
        errors.append(
            f"{label} -> {file}: `provenance` block present but no "
            "`provenance.input.content_hash` to re-derive the pin from"
        )
        return
    if pin != derived:
        errors.append(
            f"{label} -> {file}: pin {pin} does not match the file's "
            f"provenance.input.content_hash {derived}"
        )


def check_evidence_pins(errors, root=None):
    """Every manifest `evidence` pin re-derives from its cited file (issue
    #170): `provenance.input.content_hash` when the file carries a
    `provenance` block, else the sha256 of its raw bytes (issue #179).
    `root` is injectable so tests run against synthetic trees; the default
    is this checkout.
    """
    root = Path(root) if root is not None else ROOT
    try:
        manifest = json.loads((root / MANIFEST).read_text())
    except (OSError, ValueError) as exc:
        errors.append(f"{MANIFEST}: unreadable or invalid JSON: {exc}")
        return
    evidence = manifest.get("evidence") if isinstance(manifest, dict) else None
    if not isinstance(evidence, dict) or not evidence:
        errors.append(
            f"{MANIFEST}: no `evidence` map found; the pin check has "
            "nothing to verify"
        )
        return
    before = len(errors)
    checked = 0
    for item in sorted(evidence):
        val = evidence[item]
        entries = val if isinstance(val, list) else [val]
        if not entries:
            errors.append(f"{MANIFEST}: evidence[{item!r}] is an empty list")
            continue
        if not all(isinstance(e, dict) for e in entries):
            errors.append(
                f"{MANIFEST}: evidence[{item!r}] is not an entry object or "
                "a list of entry objects"
            )
            continue
        for entry in entries:
            _check_one(errors, root, item, entry)
            checked += 1
    if len(errors) == before:
        print(
            f"ok     {checked} evidence pins match their files' "
            "provenance.input.content_hash (klt-produced reports) or "
            "raw-byte sha256 (provenance-less files)"
        )


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) > 1:
        print("usage: scripts/check_signoff_pins.py [root]", file=sys.stderr)
        return 2
    errors = []
    check_evidence_pins(errors, root=argv[0] if argv else None)
    for err in errors:
        print(f"FAIL   {err}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
