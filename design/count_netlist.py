#!/usr/bin/env python3
"""Flatten-count a hierarchical SPICE netlist: python3 design/count_netlist.py design/analog/dac_analog.spice

Prints unit-cell, dummy and per-element instance counts as the netlist builds
them (no simulation, no performance claim)."""
import collections
import re
import sys


def parse(path):
    subs, cur = {}, None
    for line in open(path):
        w = line.split()
        if not w:
            continue
        if w[0].lower() == ".subckt":
            cur = subs.setdefault(w[1], collections.Counter())
        elif w[0].lower() == ".ends":
            cur = None
        elif cur is not None and w[0][0].lower() == "x":
            cur[w[-1] if w[0][1].lower() != "m" else "MOS"] += 1
    return subs


def flat(subs, name, mult, acc):
    for child, n in subs[name].items():
        if child in subs:
            flat(subs, child, mult * n, acc)
        else:
            acc[child] += mult * n
    acc[name] += mult


def main(path):
    subs = parse(path)
    top = next(iter(subs))
    acc = collections.Counter()
    flat(subs, top, 1, acc)
    for k in ("unit_cell", "dummy_cell", "driver", "bias"):
        print(f"{k}: {acc[k]}")
    for k in sorted(subs, key=lambda s: (len(s), s)):
        if k.startswith("elem_"):
            print(f"{k}: {acc[k]} elements x {k.split('_')[1]} units = {acc[k] * int(k.split('_')[1])}")
    live = sum(acc[f"elem_{n}"] * n for n in (16, 1, 2, 4, 8))
    print(f"live unit cells (explicit instances): {live}")


if __name__ == "__main__":
    main(sys.argv[1])
