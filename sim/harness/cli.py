"""`python -m sim.harness check | run smoke` (run from the repo root)."""

from __future__ import annotations

import argparse
import datetime
import gzip
import json
import os
import shlex
import statistics
import subprocess
import sys
from pathlib import Path

from . import check

SMOKE = check.SIM_DIR / "smoke"
CORNERS = ["tt", "ff", "ss", "fs", "sf"]


def cmd_check(_args) -> int:
    drift, found = check.run_check()
    print(json.dumps(found, indent=2))
    for d in drift:
        print(f"DRIFT {d}", file=sys.stderr)
    if drift:
        print(f"toolchain check FAILED ({len(drift)} item(s))", file=sys.stderr)
        return 1
    print("toolchain check OK")
    return 0


def klt_sim(request: Path, report: Path, env: dict) -> tuple[dict, list[str]]:
    # No --backend: KLT_SIM_BACKEND (batch on dispatch workers) decides. A
    # failed submit is reported, never retried locally; waiting for fleet
    # capacity is a batch retry, not a local fallback.
    cmd = ["klt", "sim", str(request), "--format", "json", "--report-out", str(report),
           "--wait-for-capacity", "1200"]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if not report.exists():
        sys.exit(f"klt sim failed (rc={proc.returncode}) for {request.name}:\n{proc.stderr[-2000:]}")
    return json.loads(report.read_text()), cmd


def rel(cmd: list[str]) -> list[str]:
    """Repo-relative paths, so the record does not embed a checkout location."""
    root = str(check.SIM_DIR.parent) + os.sep
    return [a.replace(root, "") for a in cmd]


def spread(report: dict, name: str) -> tuple[float, float]:
    vals = [m["value"] for c in report["corners"] for m in c["measurements"]
            if m["name"] == name and m.get("value") is not None]
    return statistics.mean(vals), statistics.stdev(vals)


def worker_provenance(label: str, report: dict) -> list[str]:
    """Record what the runner reported about its PDK and ngspice, verbatim.

    The local pin check covers this host only; a fleet worker carries its own
    PDK and ngspice build, and klt compares them with the submitter's.
    """
    remote = (report["environment"].get("remote") or {})
    if not remote:
        return [f"- {label} runner: local (no environment.remote); the pin check above applies"]
    we = remote.get("worker_environment") or {}
    pdk = we.get("pdk") or {}
    out = []
    for key, what in (("pdk_stamp_comparison", "PDK stamp"), ("engine_build_comparison", "ngspice build")):
        cmp_ = we.get(key) or {}
        status = cmp_.get("status", "not reported")
        line = f"- {label} runner {what} vs local: **{status}**"
        if cmp_.get("warning"):
            line += f" -- {cmp_['warning']}"
        out.append(line)
    out.append(f"- {label} runner PDK: {pdk.get('variant', '?')} at `{pdk.get('root', '?')}`, "
               f"stamp `{pdk.get('stamp_text', 'not reported')}`")
    return out


def cmd_run(args) -> int:
    drift, found = check.run_check()
    if drift:
        for d in drift:
            print(f"DRIFT {d}", file=sys.stderr)
        return 1
    env = dict(os.environ, PDK_ROOT=str(Path(found["pdk_dir"]).parent))
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    rec_dir = SMOKE / "records"
    rec_dir.mkdir(exist_ok=True)

    corners, cmd_c = klt_sim(SMOKE / "request-corners.json", rec_dir / f"{stamp}-corners.json", env)
    mc, cmd_m = klt_sim(SMOKE / "request-mc.json", rec_dir / f"{stamp}-mc.json", env)

    seen = [c["corner_id"].split("/")[0] for c in corners["corners"]]
    if seen != CORNERS or corners["status"] != "pass":
        sys.exit(f"corner run incomplete: corners={seen} status={corners['status']}")
    n_mc = len(mc["corners"])
    mean, sigma = spread(mc, "i_1v65")
    if mc["status"] != "pass" or n_mc != mc["environment"]["monte_carlo"]["n"] or sigma <= 0:
        sys.exit(f"Monte Carlo not usable: status={mc['status']} n={n_mc} sigma={sigma}")
    with open(rec_dir / f"{stamp}-mc.json.gz", "wb") as raw:
        with gzip.GzipFile("", "wb", fileobj=raw, mtime=0) as f:
            f.write((rec_dir / f"{stamp}-mc.json").read_bytes())
    (rec_dir / f"{stamp}-mc.json").unlink()

    def remote(r):
        return (r["environment"].get("remote") or {}).get("job_id", "local (no environment.remote)")

    lines = [
        f"# Smoke record {stamp}", "",
        "Toolchain evidence only: no linearity claim, no design W/L (placeholder 10u/2u).", "",
        f"- PDK: {found['pdk_variant']} revision `{found['pdk_revision']}`",
        f"- ngspice: local {found['ngspice']}; runner {corners['environment']['engine_version']}",
        f"- Python: {found['python']}",
        f"- Corners command: `{shlex.join(rel(cmd_c))}` (backend: `{os.environ.get('KLT_SIM_BACKEND', 'request/default')}`)",
        f"- Corners job id (`environment.remote`): `{remote(corners)}`",
        *worker_provenance("Corners", corners),
        f"- Monte Carlo command: `{shlex.join(rel(cmd_m))}`",
        f"- Monte Carlo job id (`environment.remote`): `{remote(mc)}`",
        *worker_provenance("Monte Carlo", mc), "",
        "## Five corners, 27 C, Vg = 1.0 V, Iout = -i(Vout) (device sinks current)", "",
        "| corner | PDK section | Iout @1.0 V (uA) | Iout @1.65 V (uA) | Iout @3.0 V (uA) | Rout 1.0-3.0 V (kohm) |",
        "|---|---|---|---|---|---|",
    ]
    for c in corners["corners"]:
        v = {m["name"]: m["value"] for m in c["measurements"]}
        name = c["corner_id"].split("/")[0]
        sec = "typical" if name == "tt" else name
        lines.append(f"| {name} | `{sec}` | {-v['i_1v0']*1e6:.3f} | {-v['i_1v65']*1e6:.3f} | "
                     f"{-v['i_3v0']*1e6:.3f} | {v['rout_ohm']/1e3:.1f} |")
    lines += [
        "", "## Monte Carlo (tt, 27 C)", "",
        "- Mismatch model: the PDK's own `fets_mm` per-device terms (`delvto`, `mulu0`), "
        "enabled with `sw_stat_mismatch=1`, `sw_stat_global=0` (local mismatch only).",
        f"- Samples: N = {n_mc}, seed {mc['environment']['monte_carlo']['seed']}.",
        "- Gradient: **none modelled** in this run.",
        f"- Iout @1.65 V: mean {-mean*1e6:.3f} uA, sigma {sigma*1e6:.4f} uA "
        f"({100*sigma/abs(mean):.2f} %) -- non-zero spread, so the MC path ran.",
        f"- Full per-sample report: `{stamp}-mc.json.gz`; corner report: `{stamp}-corners.json`.",
        "- This is one bias point on a placeholder device; it says nothing about array INL/DNL.", "",
    ]
    (rec_dir / f"{stamp}.md").write_text("\n".join(lines))
    print(f"record written: {rec_dir / (stamp + '.md')}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m sim.harness")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="fail non-zero on toolchain / PDK drift").set_defaults(fn=cmd_check)
    run = sub.add_parser("run", help="run a harness target")
    run.add_argument("target", choices=["smoke"])
    run.set_defaults(fn=cmd_run)
    args = ap.parse_args(argv)
    return args.fn(args)
