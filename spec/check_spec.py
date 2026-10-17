#!/usr/bin/env python3
"""Structural checks on spec/target-spec.md and spec/decision-records/.

  1. every row of the section 1 parameter table has all six cells non-empty
     (parameter, min, typ, max, grading condition, corners);
  2. every decision-records/NNNN-*.md link in target-spec.md resolves;
  3. record filenames are NNNN-<slug>.md, contiguous from 0001, and each has a
     `- **Status**:` line starting proposed | ratified | superseded by NNNN;
  4. spec/README.md has an index row for every record.

    python3 spec/check_spec.py

Stdlib only. Exit 0 on pass, 1 on a failed check. It does not rerun the sizing
(`python3 spec/sizing/size.py --check` does that).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SPEC_DIR = Path(__file__).resolve().parent
FILENAME_RE = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
STATUS_RE = re.compile(r"^- \*\*Status\*\*:\s*(proposed|ratified|superseded by \d{4})\b", re.I | re.M)
LINK_RE = re.compile(r"decision-records/(\d{4}-[a-z0-9-]+\.md)")


def table_rows(text: str, start: str, end: str) -> list[list[str]]:
    a = text.index(start)
    b = text.index(end, a)
    rows = []
    for line in text[a:b].splitlines():
        if line.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", line):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows[1:]  # drop header


def check(spec_dir: Path = SPEC_DIR) -> list[str]:
    errs: list[str] = []
    spec = (spec_dir / "target-spec.md").read_text()
    rows = table_rows(spec, "## 1. Parameter table", "## 2.")
    if not rows:
        errs.append("target-spec.md: parameter table has no rows")
    for r in rows:
        if len(r) != 6 or not all(r):
            errs.append(f"target-spec.md: row {r[0] if r else '?'!r} needs six non-empty cells")
    recdir = spec_dir / "decision-records"
    names = sorted(p.name for p in recdir.glob("*.md") if p.name != "TEMPLATE.md")
    nums = []
    for n in names:
        m = FILENAME_RE.match(n)
        if not m:
            errs.append(f"{n}: filename is not NNNN-<slug>.md")
            continue
        nums.append(int(m.group(1)))
        if not STATUS_RE.search((recdir / n).read_text()):
            errs.append(f"{n}: no valid Status line")
    if nums != list(range(1, len(nums) + 1)):
        errs.append(f"decision records not contiguous from 0001: {nums}")
    for link in sorted(set(LINK_RE.findall(spec))):
        if not (recdir / link).exists():
            errs.append(f"target-spec.md links missing record {link}")
    readme = (spec_dir / "README.md").read_text()
    for n in names:
        if n not in readme:
            errs.append(f"spec/README.md: no index row for {n}")
    return errs


def main() -> int:
    errs = check()
    for e in errs:
        print(f"FAIL: {e}", file=sys.stderr)
    if not errs:
        print("ok")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
