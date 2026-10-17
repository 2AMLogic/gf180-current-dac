"""Version and PDK drift check against sim/pdk.json and sim/toolchain.json.

`collect_drift` is pure (found values in, messages out) so the pass and drift
cases are testable without the real tools; `probe_*` read the host.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parent.parent


def load_pins(sim_dir: Path = SIM_DIR) -> tuple[dict, dict]:
    return (
        json.loads((sim_dir / "pdk.json").read_text()),
        json.loads((sim_dir / "toolchain.json").read_text()),
    )


def version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(p) for p in re.findall(r"\d+", text)[:3])


def probe_ngspice() -> str | None:
    exe = shutil.which("ngspice")
    if not exe:
        return None
    out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30)
    m = re.search(r"ngspice-(\d+(?:\.\d+)*)", out.stdout + out.stderr)
    return m.group(1) if m else None


def probe_python() -> str:
    return ".".join(str(p) for p in sys.version_info[:3])


def find_pdk_dir(pdk: dict) -> Path | None:
    """Resolve the variant directory: $PDK_ROOT first, then pdk.json roots."""
    roots = ([os.environ["PDK_ROOT"]] if os.environ.get("PDK_ROOT") else []) + pdk["roots"]
    for root in roots:
        cand = Path(root).expanduser() / pdk["variant"]
        if cand.is_dir():
            return cand
    return None


def pdk_revision(variant_dir: Path) -> str | None:
    """The ciel/volare version hash: the `versions/<hash>` path component."""
    parts = variant_dir.resolve().parts
    return parts[parts.index("versions") + 1] if "versions" in parts else None


def collect_drift(pdk: dict, tc: dict, ngspice: str | None, python: str,
                  variant_dir: Path | None, revision: str | None) -> list[str]:
    drift: list[str] = []
    if ngspice is None:
        drift.append(f"ngspice: not found on PATH (need >= {tc['ngspice_min']})")
    elif version_tuple(ngspice) < version_tuple(tc["ngspice_min"]):
        drift.append(f"ngspice: found {ngspice}, need >= {tc['ngspice_min']}")
    if version_tuple(python) < version_tuple(tc["python_min"]):
        drift.append(f"python: found {python}, need >= {tc['python_min']}")
    if tc["pdk_revision"] != pdk["revision"]:
        drift.append(
            f"pins: toolchain.json pdk_revision {tc['pdk_revision']} != "
            f"pdk.json revision {pdk['revision']}"
        )
    if variant_dir is None:
        drift.append(
            f"pdk: {pdk['variant']} not found (set PDK_ROOT or fetch it: {pdk['fetch']})"
        )
    elif revision != pdk["revision"]:
        drift.append(
            f"pdk: {variant_dir} is revision {revision}, pinned {pdk['revision']} "
            f"(fetch: {pdk['fetch']})"
        )
    return drift


def run_check(sim_dir: Path = SIM_DIR) -> tuple[list[str], dict]:
    pdk, tc = load_pins(sim_dir)
    ngspice, python = probe_ngspice(), probe_python()
    variant_dir = find_pdk_dir(pdk)
    revision = pdk_revision(variant_dir) if variant_dir else None
    found = {
        "ngspice": ngspice,
        "python": python,
        "pdk_variant": pdk["variant"],
        "pdk_dir": str(variant_dir) if variant_dir else None,
        "pdk_revision": revision,
    }
    return collect_drift(pdk, tc, ngspice, python, variant_dir, revision), found
