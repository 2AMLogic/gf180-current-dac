#!/usr/bin/env python3
"""Fail unless a committed netlist hashes to the netlist_sha256 recorded in its
`klt synthesize --format json` report. `klt synthesize --check` (cheap mode)
covers RTL and liberty drift but not the netlist bytes; this closes that gap.

usage: check_netlist_hash.py REPORT.json NETLIST.v
"""
import hashlib
import json
import sys

report, netlist = sys.argv[1:3]
want = json.load(open(report))["netlist_sha256"]
got = hashlib.sha256(open(netlist, "rb").read()).hexdigest()
if got != want:
    sys.exit(f"{netlist}: sha256 {got} != {want} recorded in {report}")
print(f"ok {netlist}")
