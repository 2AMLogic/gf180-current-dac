#!/usr/bin/env python3
"""Deterministic generator for the analog-partition layout stream (T1 item 2).

    python3 layout/gen_array.py                 # write the stream and the item-2 envelope
    python3 layout/gen_array.py --write-table   # rewrite switching_sequence.json
    python3 layout/gen_array.py --check         # exit 1 on any drift (CI)

Inputs, all committed: layout/switching_sequence.json (the table this reads),
layout/prims/*.gds (device primitives from `klt gen mos_array`, see
gen_prims.sh). Output is a function of those only: no timestamps, fixed
cell order, so the byte hash is meaningful. Needs the pip `klayout` package
(version pinned in layout/toolchain.json); no PDK and no klt.

Scope: placement. Every device is placed; no wiring is drawn (no cell-internal
routing, no bias/switch/output distribution, no pins). See layout/README.md.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import klayout
import klayout.db as db

ROOT = Path(__file__).resolve().parent.parent
LAYOUT = ROOT / "layout"
PRIMS = LAYOUT / "prims"
GDS = LAYOUT / "gf180-current-dac-analog.gds"
TABLE = LAYOUT / "switching_sequence.json"
EVIDENCE = ROOT / "evidence" / "item2-analog.json"
TOP = "dac_analog_layout"
GENERATOR_CMD = "python3 layout/gen_array.py"

SIDE = 8            # elements per array side
EL = 4              # units per element side
RING = 1            # dummy ring depth in unit cells (spec section 4)
GAP_UM = 0.6        # device-to-device bbox gap and tile margin
BAND_UM = 5.0       # gap between array and the driver / bias blocks
DBU = 0.0005
N_UNARY = SIDE * SIDE - 1
BINARY_UNITS = [1, 2, 4, 8]


def dbu(um: float) -> int:
    return round(um / DBU)


# --------------------------------------------------------------- sequence

def model_sequence() -> list[int]:
    spec = importlib.util.spec_from_file_location("size", ROOT / "spec/sizing/size.py")
    size = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(size)
    return size.sequence(SIDE, "inout-pairs")


def table_from_order(order: list[int]) -> dict:
    sites = []
    for pos, s in enumerate(order):
        unary = pos < N_UNARY
        sites.append({
            "position": pos, "site": s, "row": s // SIDE, "col": s % SIDE,
            "role": "unary" if unary else "binary",
            "cell": f"elem_t{pos:02d}" if unary else "elem_bin",
        })
    return {
        "schema_version": 1,
        "description": "Switching sequence and site map of the analog array. "
                       "`order[k]` is the element-grid site (row * 8 + col, row 0 at the "
                       "bottom, col 0 at the left) of the k-th unary element to turn on; "
                       "the last entry is the binary block, never switched as a unary. "
                       "Written by `python3 layout/gen_array.py --write-table` from "
                       "spec/sizing/size.py sequence(8, 'inout-pairs'), the sequence the "
                       "spec's 99.92 % yield was computed for; --check fails if they differ.",
        "sequence": "inout-pairs",
        "grid": {"elements_per_side": SIDE, "units_per_element_side": EL,
                 "dummy_ring_cells": RING},
        "point_symmetry": "site s pairs with site 63 - s; positions 2j and 2j+1 are a pair "
                          "except that the last pair is (unary 62, binary block)",
        "order": order,
        "sites": sites,
    }


# ------------------------------------------------------------- primitives

class Lib:
    """Flattened device primitives, copied into the target layout as cells."""

    def __init__(self, ly: db.Layout):
        self.ly = ly
        self.cells: dict[str, tuple[db.Cell, db.Box]] = {}
        for gds in sorted(PRIMS.glob("prim_*.gds")):
            src = db.Layout()
            src.read(str(gds))
            top = src.cell(gds.stem)
            cell = ly.create_cell(gds.stem)
            for li in src.layer_indexes():
                info = src.get_info(li)
                dst = ly.layer(info.layer, info.datatype)
                cell.shapes(dst).insert(top.begin_shapes_rec(li))
            if abs(src.dbu - DBU) > 1e-12:
                raise SystemExit(f"{gds.name}: dbu {src.dbu}, expected {DBU}")
            self.cells[gds.stem] = (cell, cell.bbox())

    def place(self, parent: db.Cell, name: str, x: int, y: int) -> db.Box:
        """Place prim `name` with its bbox lower-left at (x, y); return placed bbox."""
        cell, bb = self.cells[name]
        parent.insert(db.CellInstArray(cell.cell_index(), db.Trans(x - bb.left, y - bb.bottom)))
        return db.Box(x, y, x + bb.width(), y + bb.height())


def build(table: dict) -> db.Layout:
    ly = db.Layout()
    ly.dbu = DBU
    lib = Lib(ly)
    gap = dbu(GAP_UM)
    w = lambda n: lib.cells[n][1].width()
    h = lambda n: lib.cells[n][1].height()

    # unit cell: current source, cascode above it, switch pair above that.
    # Dummy cell has the same device placement (same proximity environment).
    def device_cell(name: str) -> db.Cell:
        c = ly.create_cell(name)
        y1 = h("prim_cs") + gap
        y2 = y1 + h("prim_cas") + gap
        lib.place(c, "prim_cs", 0, 0)
        lib.place(c, "prim_cas", 0, y1)
        lib.place(c, "prim_sw", 0, y2)
        lib.place(c, "prim_sw", w("prim_sw") + gap, y2)
        return c

    unit = device_cell("unit_cell")
    dummy = device_cell("dummy_cell")
    ub = unit.bbox()
    px, py = ub.width() + gap, ub.height() + gap

    def unit_at(parent: db.Cell, cell: db.Cell, i: int, j: int):
        parent.insert(db.CellInstArray(cell.cell_index(), db.Trans(i * px, j * py)))

    # unary elements: 16 contiguous units, one cell per switching position
    elem_cells = {}
    for s in table["sites"]:
        if s["role"] != "unary":
            continue
        c = ly.create_cell(s["cell"])
        for k in range(EL * EL):
            unit_at(c, unit, k % EL, k // EL)
        elem_cells[s["cell"]] = c

    # binary block (4 x 4): 8 units rows 0-1, 4 units row 2, 2 + 1 + filler row 3
    binary = ly.create_cell("elem_bin")
    plan = {"elem_b3": [(i, j) for j in (0, 1) for i in range(4)],
            "elem_b2": [(i, 2) for i in range(4)],
            "elem_b1": [(0, 3), (1, 3)],
            "elem_b0": [(2, 3)]}
    for name, units in plan.items():
        c = ly.create_cell(name)
        for i, j in units:
            unit_at(c, unit, i, j)
        binary.insert(db.CellInstArray(c.cell_index(), db.Trans()))
    unit_at(binary, dummy, 3, 3)   # the filler site: 1023 units + 1 filler
    elem_cells["elem_bin"] = binary

    top = ly.create_cell(TOP)
    n = SIDE * EL + 2 * RING
    for s in table["sites"]:
        c = elem_cells[s["cell"]]
        top.insert(db.CellInstArray(
            c.cell_index(), db.Trans((RING + EL * s["col"]) * px, (RING + EL * s["row"]) * py)))
    for i in range(n):
        for j in range(n):
            if i < RING or j < RING or i >= n - RING or j >= n - RING:
                unit_at(top, dummy, i, j)

    # drivers (3 inverters, pfet over nfet) in a band below the array, in
    # switching order (unary t00.., then b0..b3); bias mirror above the array.
    pw = max(w("prim_drvp"), w("prim_drvn"))
    ph = h("prim_drvp") + gap + h("prim_drvn")
    drv = ly.create_cell("driver")
    for k in range(3):
        lib.place(drv, "prim_drvn", k * (pw + gap), 0)
        lib.place(drv, "prim_drvp", k * (pw + gap), h("prim_drvn") + gap)
    dbb = drv.bbox()
    dx, dy = dbb.width() + gap, dbb.height() + gap
    per_row = n
    for k in range(N_UNARY + len(BINARY_UNITS)):
        r, c = divmod(k, per_row)
        top.insert(db.CellInstArray(drv.cell_index(),
                                    db.Trans(c * dx, -dbu(BAND_UM) - (r + 1) * dy)))
    bias = ly.create_cell("bias")
    for k in range(10):   # 10 diode-connected pairs, design/gen_analog.py IREF_MIRROR_UNITS
        lib.place(bias, "prim_cs", k * (w("prim_cs") + gap), 0)
        lib.place(bias, "prim_cas", k * (w("prim_cs") + gap), h("prim_cs") + gap)
    top.insert(db.CellInstArray(bias.cell_index(), db.Trans(0, n * py + dbu(BAND_UM))))
    ly.top_cell()  # asserts a single top
    return ly


def write(ly: db.Layout, path: Path) -> None:
    opt = db.SaveLayoutOptions()
    opt.format = "GDS2"
    opt.gds2_write_timestamps = False
    opt.gds2_write_cell_properties = False
    opt.gds2_write_file_properties = False
    ly.write(str(path), opt)


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


# ------------------------------------------------------------------ checks

def read_back(path: Path, table: dict) -> list[str]:
    """Compare the stream itself against the table; return problems."""
    errs = []
    ly = db.Layout()
    ly.read(str(path))
    top = ly.top_cell()
    if top.name != TOP:
        errs.append(f"top cell {top.name}, expected {TOP}")
    unit = ly.cell("unit_cell")
    ub = unit.bbox()
    px, py = ub.width() + dbu(GAP_UM), ub.height() + dbu(GAP_UM)
    placed = {}
    for inst in top.each_inst():
        placed.setdefault(inst.cell.name, []).append((inst.trans.disp.x, inst.trans.disp.y))
    for s in table["sites"]:
        got = placed.get(s["cell"])
        want = ((RING + EL * s["col"]) * px, (RING + EL * s["row"]) * py)
        if got != [want]:
            errs.append(f"{s['cell']} (position {s['position']}): at {got}, table says {want}")
    dummies = placed.get("dummy_cell", [])
    n = SIDE * EL + 2 * RING
    ring = {(i, j) for i in range(n) for j in range(n)
            if min(i, j) < RING or max(i, j) >= n - RING}
    if sorted(dummies) != sorted((i * px, j * py) for i, j in ring):
        errs.append("dummy ring is not the full ring on all four sides")
    # point symmetry of the ring and of each pair, about the array centre
    cx, cy = (n - 1) * px, (n - 1) * py
    if {(cx - x, cy - y) for x, y in dummies} != set(dummies):
        errs.append("dummy ring is not point-symmetric")
    elem = {s["cell"]: placed[s["cell"]][0] for s in table["sites"] if s["cell"] in placed}
    ex, ey = (EL - 1) * px, (EL - 1) * py
    for a, b in zip(table["order"][0::2], table["order"][1::2]):
        sa = next(s for s in table["sites"] if s["site"] == a)["cell"]
        sb = next(s for s in table["sites"] if s["site"] == b)["cell"]
        xa, ya = elem[sa]
        xb, yb = elem[sb]
        if (xa + xb + ex, ya + yb + ey) != (cx, cy):
            errs.append(f"pair ({a}, {b}) is not point-symmetric about the array centre")
    # flat instance counts
    counts = {"unit_cell": 0, "dummy_cell": 0}
    def walk(cell, mult=1):
        for inst in cell.each_inst():
            nm = inst.cell.name
            if nm in counts:
                counts[nm] += mult
            else:
                walk(inst.cell, mult)
    walk(top)
    if counts["unit_cell"] != 1023:
        errs.append(f"{counts['unit_cell']} unit cells, expected 1023")
    if counts["dummy_cell"] != 4 * (n - RING * 2) * RING + 4 * RING * RING + 1:
        errs.append(f"{counts['dummy_cell']} dummy cells, expected ring + 1 filler")
    return errs


def evidence(h: str) -> dict:
    return {
        "schema_version": 1,
        "kind": "generic",
        "status": "pass",
        "t1_item": 2,
        "summary": "analog-partition layout stream regenerated from layout/gen_array.py; "
                   "byte-identical on a second run. Placement only, no routing.",
        "source": GDS.relative_to(ROOT).as_posix(),
        "provenance": {
            "klt_version": None,
            "klayout_version": klayout.__version__,
            "pdk": "gf180mcuD",
            "deck": None,
            "input": {"path": {"path": GDS.relative_to(ROOT).as_posix(), "scope": "repo"},
                      "content_hash": h},
            "regeneration": {"generator": GENERATOR_CMD, "regenerated_hash": h},
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write-table", action="store_true")
    a = ap.parse_args()

    order = model_sequence()
    want_table = table_from_order(order)
    if a.write_table:
        TABLE.write_text(json.dumps(want_table, indent=2) + "\n")
        print(f"wrote {TABLE.relative_to(ROOT)}")
        return 0
    table = json.loads(TABLE.read_text())

    errs = []
    if table != want_table:
        errs.append("switching_sequence.json differs from spec/sizing/size.py "
                    "sequence(8, 'inout-pairs'); run --write-table")
    with tempfile.TemporaryDirectory() as td:
        outs = []
        for k in range(2):
            p = Path(td) / f"run{k}.gds"
            write(build(table), p)
            outs.append(p)
        if outs[0].read_bytes() != outs[1].read_bytes():
            errs.append("two runs produced different bytes (generator not deterministic)")
        h = sha(outs[0])
        errs += read_back(outs[0], table)
        if a.check:
            if not GDS.exists() or sha(GDS) != h:
                errs.append(f"{GDS.relative_to(ROOT)} differs from a fresh run ({h})")
            if not EVIDENCE.exists() or json.loads(EVIDENCE.read_text()) != evidence(h):
                errs.append(f"{EVIDENCE.relative_to(ROOT)} differs from a fresh run")
        elif not errs:
            GDS.write_bytes(outs[0].read_bytes())
            EVIDENCE.write_text(json.dumps(evidence(h), indent=2) + "\n")
            print(f"wrote {GDS.relative_to(ROOT)} {h}")
    for e in errs:
        print(f"FAIL   {e}", file=sys.stderr)
    if a.check and not errs:
        print(f"layout stream fresh: {h}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
