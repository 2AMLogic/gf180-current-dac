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

Scope: placement, routing and pins. Every device is placed and wired to the
connectivity of design/analog/dac_analog.spice (M1 local, M2 horizontal, M3
vertical, M4 horizontal, M5 vertical), the 72 reference pins are labelled on
the top cell, and substrate / well taps are tied. Nothing here is extracted or
simulated; see layout/README.md for what is and is not claimed.
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
BAND_UM = 5.0       # gap between the array's top ring row and the bias block
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

M = {1: (34, 0), 2: (36, 0), 3: (42, 0), 4: (46, 0), 5: (81, 0)}   # metal levels
V = {1: (35, 0), 2: (38, 0), 3: (40, 0), 4: (41, 0)}               # V[i] joins M[i], M[i+1]
LABEL_DT = 10       # pin/label purpose of every metal level (klt deck gf180mcu)
CUT = 520           # via cut size (fixed by the deck)
PAD = 720           # metal pad around a cut
W = 560             # metal width, M2 and up (deck minimum 0.28 um)
EXT = 600           # half the tile gap: shapes that must abut a neighbour reach this far
PITCH_TRACK = 1280  # M4 track pitch in the channels
PITCH_M5 = 1200     # M5 slot pitch


class Dev:
    """One placed primitive: terminal boxes in the coordinates of the parent cell."""

    def __init__(self, bbox, S, D, G, taps):
        self.bbox, self.S, self.D, self.G = bbox, S, D, G
        self.BL, self.TL, self.BR, self.TR = taps


def cx(b: db.Box) -> int:
    return (b.left + b.right) // 2


def cy(b: db.Box) -> int:
    return (b.bottom + b.top) // 2


class Lib:
    """Flattened device primitives, copied into the target layout as cells."""

    def __init__(self, ly: db.Layout):
        self.ly = ly
        self.cells: dict[str, tuple[db.Cell, db.Box]] = {}
        self.terms: dict[str, dict[str, db.Box]] = {}
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
            bb = cell.bbox()
            self.cells[gds.stem] = (cell, bb)
            self.terms[gds.stem] = self._terminals(src, top, bb)

    @staticmethod
    def _terminals(src: db.Layout, top: db.Cell, bb: db.Box) -> dict[str, db.Box]:
        """Metal1 terminals of a primitive, relative to its bbox lower-left."""
        r = db.Region(top.begin_shapes_rec(src.layer(*M[1])))
        r.merge()
        boxes = [p.bbox().moved(-bb.left, -bb.bottom) for p in r.each()]
        strips = sorted((b for b in boxes if b.height() > 840), key=lambda b: b.left)
        squares = [b for b in boxes if b.height() == 840 and b.width() == 840]
        if len(strips) != 2 or len(squares) != 5:
            raise SystemExit("primitive metal1 is not 2 strips + 5 pads")
        s, d = strips
        g = [b for b in squares if s.left < b.left < d.right and b.bottom > s.top]
        if len(g) != 1:
            raise SystemExit("primitive gate pad not found")
        t = {"S": s, "D": d, "G": g[0]}
        midx, midy = bb.width() // 2, bb.height() // 2
        for b in squares:
            if b is g[0] or b == g[0]:
                continue
            t[("T" if b.bottom > midy else "B") + ("R" if b.left > midx else "L")] = b
        return t

    def place(self, parent: db.Cell, name: str, x: int, y: int) -> Dev:
        """Place prim `name` with its bbox lower-left at (x, y); return the placed terminals."""
        cell, bb = self.cells[name]
        parent.insert(db.CellInstArray(cell.cell_index(), db.Trans(x - bb.left, y - bb.bottom)))
        t = {k: b.moved(x, y) for k, b in self.terms[name].items()}
        return Dev(db.Box(x, y, x + bb.width(), y + bb.height()), t["S"], t["D"], t["G"],
                   (t["BL"], t["TL"], t["BR"], t["TR"]))


class Ink:
    """Drawing helpers for the metal stack. Levels are the ints 1..5."""

    def __init__(self, ly: db.Layout):
        self.m = {i: ly.layer(*M[i]) for i in M}
        self.vias = {i: ly.layer(*V[i]) for i in V}
        self.lab = {i: ly.layer(M[i][0], LABEL_DT) for i in M}

    def box(self, cell: db.Cell, m: int, x0: int, y0: int, x1: int, y1: int) -> None:
        cell.shapes(self.m[m]).insert(db.Box(x0, y0, x1, y1))

    def cut(self, cell: db.Cell, v: int, x: int, y: int) -> None:
        cell.shapes(self.vias[v]).insert(db.Box(x - CUT // 2, y - CUT // 2, x + CUT // 2, y + CUT // 2))

    def pad(self, cell: db.Cell, m: int, x: int, y: int) -> None:
        self.box(cell, m, x - PAD // 2, y - PAD // 2, x + PAD // 2, y + PAD // 2)

    def stack(self, cell: db.Cell, x: int, y: int, lo: int, hi: int) -> None:
        """Cuts and pads from level lo (existing metal) up to level hi."""
        for i in range(lo, hi):
            self.cut(cell, i, x, y)
        for i in range(max(lo, 2), hi + 1):     # no pad on M1: the cut sits on existing M1
            self.pad(cell, i, x, y)

    def h(self, cell: db.Cell, m: int, x0: int, x1: int, y: int, w: int = W) -> None:
        self.box(cell, m, min(x0, x1), y - w // 2, max(x0, x1), y + w // 2)

    def v(self, cell: db.Cell, m: int, x: int, y0: int, y1: int, w: int = W) -> None:
        self.box(cell, m, x - w // 2, min(y0, y1), x + w // 2, max(y0, y1))

    def label(self, cell: db.Cell, m: int, name: str, x: int, y: int) -> None:
        cell.shapes(self.lab[m]).insert(db.Text(name, x, y))


# ------------------------------------------------------- unit-cell geometry
# x of the unit's vertical M3 tracks. The six vss tracks sit over the M1 tap
# rails and the cs source; the four signal tracks are right of everything the
# switch row draws. Consecutive entries are at least 2 * W apart.
TRK_VBN, TRK_OUTP, TRK_OUTN, TRK_IREF = 15000, 16200, 17400, 18600
XSPV, XSNV = 9000, 10200          # element-level sp / sn M3 (join and pin) x in a unit


class Geom:
    """Unit tile size and the y of the element-level nets, from the primitives."""

    def __init__(self, lib: Lib):
        w = lambda n: lib.cells[n][1].width()
        h = lambda n: lib.cells[n][1].height()
        self.gap = dbu(GAP_UM)
        self.y1 = h("prim_cs") + self.gap
        self.y2 = self.y1 + h("prim_cas") + self.gap
        self.uw = w("prim_cs")                      # unit width (the cs is the widest row)
        self.uh = self.y2 + h("prim_sw")            # unit height
        self.px = self.uw + self.gap
        self.py = self.uh + self.gap
        self.x_sw2 = w("prim_sw") + self.gap
        sw_g_top = self.y2 + lib.terms["prim_sw"]["G"].top
        sw_d_top = self.y2 + lib.terms["prim_sw"]["D"].top
        self.y_sp = sw_g_top + 480 + W // 2         # sp row centre (above the gate pads)
        self.y_sn = sw_d_top + 600                  # sn row centre (below the gate pads)


def mid10(a: int, b: int) -> int:
    return (a + b) // 2 // 10 * 10


def wire_cs_cas(ink: Ink, c: db.Cell, g: Geom, cs: Dev, cas: Dev, mode: str,
                trk: dict[str, int]) -> None:
    """Wiring of the current source and cascode: n1, tap rails, vbn / iref / vss."""
    # n1 = cs drain to cas source, M1 only: up the cs drain, across the corridor, up to the cas source
    y_n1 = mid10(cs.TL.top, cas.BL.bottom)
    ink.box(c, 1, cs.D.left, cs.D.top, cs.D.right, y_n1 + W // 2)
    ink.box(c, 1, cas.S.left, y_n1 - W // 2, cs.D.right, y_n1 + W // 2)
    ink.box(c, 1, cas.S.left, y_n1 - W // 2, cas.S.right, cas.S.bottom)
    if mode == "pair":
        # bias diode pair: cs gate and cas gate are tied to their own drains
        ink.box(c, 1, cs.G.left, cs.G.bottom, cs.D.right, cs.G.bottom + W)
        ink.box(c, 1, cas.D.left, cas.D.top, cas.D.right, cas.G.top)
        ink.box(c, 1, cas.G.left, cas.G.top - W, cas.D.right, cas.G.top)
    # tap rails (M1), one per tap column
    ink.box(c, 1, cs.BR.left, cs.BR.bottom, cs.TR.right, cs.TR.top)          # B
    ink.box(c, 1, cas.BR.left, cas.BR.bottom, cas.TR.right, cas.TR.top)      # C
    # vss tracks over the rails (A and, in a unit, D and E are drawn by the caller)
    ink.stack(c, cx(cs.S), cy(cs.S), 1, 3)
    ink.stack(c, cx(cs.BR), (cs.BR.top + cs.TR.bottom) // 2 // 10 * 10, 1, 3)
    ink.stack(c, cx(cas.BR), mid10(cas.bbox.bottom, cas.bbox.top), 1, 3)

    def link(src_x: int, y: int, tx: int) -> None:
        ink.cut(c, 1, src_x, y)
        ink.pad(c, 2, src_x, y)
        ink.h(c, 2, src_x, tx, y)
        ink.stack(c, tx, y, 2, 3)

    t_vss_e = trk["vss_e"] if "vss_e" in trk else trk["vss_s"]
    t_vss_d = trk["vss_d"] if "vss_d" in trk else trk["vss_s"]
    if mode == "dummy":
        link(cx(cs.G), cy(cs.G), t_vss_e)
        link(cx(cas.G), cy(cas.G), t_vss_d)
    else:
        link(cx(cs.G), cy(cs.G), trk["vbn"])
        link(cx(cas.G), cy(cas.G), trk["iref"])


def wire_sw(ink: Ink, c: db.Cell, g: Geom, sw1: Dev, sw2: Dev, cas: Dev, mode: str,
            trk: dict[str, int]) -> None:
    """Wiring of the switch row: n2, tap rails, outputs and the element-level gates."""
    # n2 = cas drain to both switch sources, M1: up from the cas drain, across, up to each source
    y_n2 = mid10(cas.TL.top, sw1.BL.bottom)
    ink.box(c, 1, cas.D.left, cas.D.top, cas.D.right, y_n2 + W // 2)
    ink.box(c, 1, sw1.S.left, y_n2 - W // 2, sw2.S.right, y_n2 + W // 2)
    ink.box(c, 1, sw1.S.left, y_n2 - W // 2, sw1.S.right, sw1.S.bottom)
    ink.box(c, 1, sw2.S.left, y_n2 - W // 2, sw2.S.right, sw2.S.bottom)
    # tap rails: D joins sw1's right pads to sw2's left pads, E is sw2's right pair
    ink.box(c, 1, sw1.BR.left, sw1.BR.bottom, sw2.BL.right, sw2.BL.top)
    ink.box(c, 1, sw1.TR.left, sw1.TR.bottom, sw2.TL.right, sw2.TL.top)
    ink.box(c, 1, sw1.BR.left, sw1.BR.bottom, sw1.TR.right, sw1.TR.top)
    ink.box(c, 1, sw2.BR.left, sw2.BR.bottom, sw2.TR.right, sw2.TR.top)
    ink.stack(c, cx(sw1.BR), mid10(sw1.BR.top, sw1.TR.bottom), 1, 3)
    ink.stack(c, cx(sw2.BR), sw2.BR.top + 320, 1, 3)

    def link(src_x: int, y: int, tx: int) -> None:
        ink.cut(c, 1, src_x, y)
        ink.pad(c, 2, src_x, y)
        ink.h(c, 2, src_x, tx, y)
        ink.stack(c, tx, y, 2, 3)

    y_outp = cy(sw1.D) // 10 * 10
    y_outn = sw2.D.top - 1200
    t_d = trk["vss_d"]
    t_e = trk["vss_e"]
    if mode == "dummy":
        link(cx(sw1.D), y_outp, t_d)
        link(cx(sw2.D), y_outn, t_e)
        link(cx(sw1.G), cy(sw1.G), t_d)
        link(cx(sw2.G), cy(sw2.G) - 160, t_e)
        return
    link(cx(sw1.D), y_outp, trk["outp"])
    link(cx(sw2.D), y_outn, trk["outn"])
    # sp row above the gate pads, sn row below them; both end at the tile edge
    ink.cut(c, 1, cx(sw1.G), cy(sw1.G))
    ink.pad(c, 2, cx(sw1.G), cy(sw1.G))
    ink.v(c, 2, cx(sw1.G), cy(sw1.G), g.y_sp, PAD)
    ink.h(c, 2, 0, g.uw, g.y_sp)
    gy = cy(sw2.G) - 160
    ink.cut(c, 1, cx(sw2.G), gy)
    ink.pad(c, 2, cx(sw2.G), gy)
    ink.v(c, 2, cx(sw2.G), gy, g.y_sn, PAD)
    ink.h(c, 2, 0, g.uw, g.y_sn)


def make_unit(ink: Ink, lib: Lib, g: Geom, name: str, mode: str) -> db.Cell:
    """unit_cell (mode 'unit') or dummy_cell (mode 'dummy', every port tied to vss)."""
    c = lib.ly.create_cell(name)
    cs = lib.place(c, "prim_cs", 0, 0)
    cas = lib.place(c, "prim_cas", 0, g.y1)
    sw1 = lib.place(c, "prim_sw", 0, g.y2)
    sw2 = lib.place(c, "prim_sw", g.x_sw2, g.y2)
    trk = {"vss_a": cx(cs.BL), "vss_s": cx(cs.S), "vss_d": cx(sw1.BR),
           "vss_c": cx(cas.BR), "vss_e": cx(sw2.BR), "vss_b": cx(cs.BR),
           "vbn": TRK_VBN, "outp": TRK_OUTP, "outn": TRK_OUTN, "iref": TRK_IREF}
    # tap rail A runs up the left edge of all three rows
    ink.box(c, 1, cs.BL.left, cs.BL.bottom, sw1.TL.right, sw1.TL.top)
    ink.stack(c, cx(cs.BL), mid10(cas.bbox.bottom, cas.bbox.top), 1, 3)
    wire_cs_cas(ink, c, g, cs, cas, mode, trk)
    wire_sw(ink, c, g, sw1, sw2, cas, mode, trk)
    tracks = [trk[k] for k in ("vss_a", "vss_s", "vss_d", "vss_c", "vss_e", "vss_b")]
    if mode == "unit":
        tracks += [TRK_VBN, TRK_OUTP, TRK_OUTN, TRK_IREF]
    xs = sorted(tracks)
    if any(b - a < 2 * W for a, b in zip(xs, xs[1:])):
        raise SystemExit("unit M3 tracks closer than 2 * W")
    for x in tracks:
        ink.v(c, 3, x, -EXT, g.uh + EXT)
    # one M2 bus ties the six vss tracks (and, through the extension, the row)
    y_bus = 11480
    ink.h(c, 2, -EXT, g.uw + EXT, y_bus)
    for k in ("vss_a", "vss_s", "vss_d", "vss_c", "vss_e", "vss_b"):
        ink.cut(c, 2, trk[k], y_bus)
    return c


def make_bias(ink: Ink, lib: Lib, g: Geom) -> db.Cell:
    """Ten diode-connected cascode / source pairs (design/gen_analog.py IREF_MIRROR_UNITS)."""
    c = lib.ly.create_cell("bias")
    for k in range(10):
        x = k * g.px
        cs = lib.place(c, "prim_cs", x, 0)
        cas = lib.place(c, "prim_cas", x, g.y1)
        trk = {"vss_s": cx(cs.S), "vbn": x + TRK_VBN, "iref": x + TRK_IREF}
        ink.box(c, 1, cs.BL.left, cs.BL.bottom, cas.TL.right, cas.TL.top)
        ink.stack(c, cx(cs.BL), mid10(cas.bbox.bottom, cas.bbox.top), 1, 3)
        wire_cs_cas(ink, c, g, cs, cas, "pair", trk)
        tops = [cx(cs.BL), cx(cs.S), cx(cs.BR), cx(cas.BR), trk["vbn"], trk["iref"]]
        for t in tops:
            ink.v(c, 3, t, -EXT, cas.bbox.top + EXT)
        for t in tops[:4]:
            ink.cut(c, 2, t, 11480)
        ink.h(c, 2, x - EXT, x + g.uw + EXT, 11480)
    return c


def make_driver(ink: Ink, lib: Lib, g: Geom) -> tuple[db.Cell, dict]:
    """Three inverters in a row (d -> na -> sp -> sn); M1 devices, M2 buses, M3 nets."""
    gap = g.gap
    c = lib.ly.create_cell("driver")
    pw = max(lib.cells["prim_drvp"][1].width(), lib.cells["prim_drvn"][1].width())
    hn = lib.cells["prim_drvn"][1].height()
    cols = []
    for k in range(3):
        n = lib.place(c, "prim_drvn", k * (pw + gap), 0)
        p = lib.place(c, "prim_drvp", k * (pw + gap), hn + gap)
        cols.append((n, p))
    width = c.bbox().width()
    n0, p0 = cols[0]
    y_vss = cy(n0.BL)
    y_vdd = mid10(n0.TL.top, p0.BL.bottom)
    ink.h(c, 2, -EXT, width + EXT, y_vss)
    ink.h(c, 2, -EXT, width + EXT, y_vdd)
    for n, p in cols:
        for a, b in ((n.BL, n.TL), (n.BR, n.TR), (p.BL, p.TL), (p.BR, p.TR)):
            ink.box(c, 1, a.left, a.bottom, b.right, b.top)       # tap rail
        for t in (n.BL, n.BR):
            ink.cut(c, 1, cx(t), cy(t))
            ink.pad(c, 2, cx(t), cy(t))
        for t in (p.BL, p.BR):
            ink.cut(c, 1, cx(t), cy(t))
            ink.pad(c, 2, cx(t), cy(t))
            ink.v(c, 2, cx(t), y_vdd, cy(t))
        ys = n.S.bottom + 700
        ink.cut(c, 1, cx(n.S), ys)
        ink.pad(c, 2, cx(n.S), ys)
        ink.v(c, 2, cx(n.S), y_vss, ys)
        yp = p.S.bottom + 700
        ink.cut(c, 1, cx(p.S), yp)
        ink.pad(c, 2, cx(p.S), yp)
        ink.v(c, 2, cx(p.S), y_vdd, yp)
        # gate: nfet pad up to the pfet pad on an M3 line
        ink.stack(c, cx(n.G), cy(n.G), 1, 3)
        gy = cy(p.G)
        ink.cut(c, 1, cx(p.G), gy)
        ink.pad(c, 2, cx(p.G), gy)
        ink.h(c, 2, cx(p.G), cx(n.G), gy)
        ink.stack(c, cx(n.G), gy, 2, 3)
        ink.v(c, 3, cx(n.G), cy(n.G), gy)
        # output: nfet drain across to the pfet drain's M3 line
        yd = cy(n.D) // 10 * 10
        ink.cut(c, 1, cx(n.D), yd)
        ink.pad(c, 2, cx(n.D), yd)
        ink.h(c, 2, cx(n.D), cx(p.D), yd)
        ink.stack(c, cx(p.D), yd, 2, 3)
        ypd = cy(p.D) // 10 * 10
        ink.stack(c, cx(p.D), ypd, 1, 3)
        ink.v(c, 3, cx(p.D), yd, ypd)
    # out of inverter k feeds the gates of k + 1
    y_link = mid10(cols[0][0].G.bottom, cols[0][0].G.top) + 620
    for k in range(2):
        ink.h(c, 3, cx(cols[k][1].D), cx(cols[k + 1][0].G), y_link)
    info = {
        "width": width, "height": c.bbox().height(),
        "x_d": cx(cols[0][0].G), "y_d": 12000,
        "x_sp": cx(cols[1][1].D), "x_sn": cx(cols[2][1].D),
        "y_out_top": cy(cols[1][1].D) // 10 * 10 + PAD // 2,
        "y_out_bot": cy(cols[1][0].D) // 10 * 10 - PAD // 2,
        "y_vss": y_vss, "y_vdd": y_vdd,
    }
    return c, info


# --------------------------------------------------------- element groups

def join_group(ink: Ink, c: db.Cell, g: Geom, units: list[tuple[int, int]],
               pin: tuple[int, int]) -> None:
    """Join the sp / sn rows of a group's units and draw the pin pads at `pin`."""
    us = set(units)
    for kind, y, xv in (("sp", g.y_sp, XSPV), ("sn", g.y_sn, XSNV)):
        for i, j in sorted(us):
            if (i + 1, j) in us:
                ink.box(c, 2, i * g.px + g.uw - 100, y + j * g.py - W // 2,
                        (i + 1) * g.px + 100, y + j * g.py + W // 2)
        for j in sorted({j for _, j in us})[1:]:
            below = [i for i, jj in us if jj == j - 1 and (i, j) in us]
            if not below:
                raise SystemExit(f"group row {j} has no unit above a unit of row {j - 1}")
            i = min(below)
            x = i * g.px + xv
            ya, yb = y + (j - 1) * g.py, y + j * g.py
            ink.v(c, 3, x, ya - W // 2, yb + W // 2)
            ink.cut(c, 2, x, ya)
            ink.cut(c, 2, x, yb)
        px_, py_ = pin[0] * g.px + xv, y + pin[1] * g.py
        ink.cut(c, 2, px_, py_)
        ink.pad(c, 3, px_, py_)


def pin_xy(g: Geom, origin: tuple[int, int], unit: tuple[int, int], kind: str) -> tuple[int, int]:
    xv, y = (XSPV, g.y_sp) if kind == "sp" else (XSNV, g.y_sn)
    return origin[0] + unit[0] * g.px + xv, origin[1] + unit[1] * g.py + y


# ---------------------------------------------------------- channel routing

def assign_tracks(spans: list[tuple[int, int, object]]) -> dict[object, int]:
    """Left-edge track assignment; spans are (left, right, key). Deterministic."""
    tracks: list[int] = []
    out = {}
    for lo, hi, key in sorted(spans, key=lambda s: (s[0], s[1], str(s[2]))):
        for t, end in enumerate(tracks):
            if end < lo:
                tracks[t] = hi
                out[key] = t
                break
        else:
            tracks.append(hi)
            out[key] = len(tracks) - 1
    return out


def drive_nets(table: dict, g: Geom, drv: dict, dx: int, per_row: int) -> list[dict]:
    """One record per sp / sn net: driver lane, element pin, M5 slot."""
    units = {f"elem_b{b}": u for b, u in ((0, (2, 3)), (1, (1, 3)), (2, (0, 2)), (3, (0, 0)))}
    nets = []
    for k in range(N_UNARY + len(BINARY_UNITS)):
        pos = table["sites"][min(k, N_UNARY)]
        if k < N_UNARY:
            unit = (0, 0)
        else:
            unit = units[f"elem_b{k - N_UNARY}"]
        origin = ((RING + EL * pos["col"]) * g.px, (RING + EL * pos["row"]) * g.py)
        xo = (k % per_row) * dx
        for kind in ("sp", "sn"):
            xp, yp = pin_xy(g, origin, unit, kind)
            nets.append({"k": k, "kind": kind, "row": k // per_row, "col": pos["col"],
                         "erow": pos["row"], "xo": xo,
                         "x_d": xo + drv["x_" + kind], "xp": xp, "yp": yp, "unit": unit})
    for col in range(SIDE):
        mine = sorted((n for n in nets if n["col"] == col),
                      key=lambda n: (n["erow"], n["k"], n["kind"]))
        x0 = (RING + EL * col) * g.px
        slot = 0
        for n in mine:
            if n["k"] == N_UNARY:        # b0: pin unit (2, 3), stub goes right of the pins
                n["xt"] = x0 + 2 * g.px + XSNV + 1800 + (0 if n["kind"] == "sp" else PITCH_M5)
            else:
                n["xt"] = x0 + 1000 + slot * PITCH_M5
                slot += 1
    return nets


RAIL_TOP = {"vbn": 2400, "iref": 3600, "vss": 4800}       # M4 rail centres above the array top edge
RAIL_BOT = {"outp": -3000, "outn": -4200, "vss": -5400}   # M4 rail centres, y = 0 is the array bottom
Y_TRACK0 = -6800                                          # first M4 track of the upper channel
STRAP_VSS, STRAP_VDD = -4000, -6000                       # M3 straps left of the driver rows
PIN_NAMES = (["iref", "vdd", "vss", "outp", "outn"] + [f"t{k}" for k in range(N_UNARY)]
             + [f"b{k}" for k in range(len(BINARY_UNITS))])
GROUPS = {"elem_b0": [(2, 3)], "elem_b1": [(0, 3), (1, 3)],
          "elem_b2": [(i, 2) for i in range(4)],
          "elem_b3": [(i, j) for j in (0, 1) for i in range(4)]}
GROUP_PIN = {"elem_b0": (2, 3), "elem_b1": (1, 3), "elem_b2": (0, 2), "elem_b3": (0, 0)}


def build(table: dict) -> db.Layout:
    ly = db.Layout()
    ly.dbu = DBU
    lib = Lib(ly)
    ink = Ink(ly)
    g = Geom(lib)
    px, py = g.px, g.py
    unit = make_unit(ink, lib, g, "unit_cell", "unit")
    dummy = make_unit(ink, lib, g, "dummy_cell", "dummy")
    trk_vss_s = cx(lib.terms["prim_cs"]["S"])

    def unit_at(parent: db.Cell, cell: db.Cell, i: int, j: int):
        parent.insert(db.CellInstArray(cell.cell_index(), db.Trans(i * px, j * py)))

    # unary elements: 16 contiguous units, one cell per switching position
    full = [(i, j) for j in range(EL) for i in range(EL)]
    elem_cells = {}
    for s in table["sites"]:
        if s["role"] != "unary":
            continue
        c = ly.create_cell(s["cell"])
        for i, j in full:
            unit_at(c, unit, i, j)
        join_group(ink, c, g, full, (0, 0))
        elem_cells[s["cell"]] = c

    # binary block (4 x 4): 8 units rows 0-1, 4 units row 2, 2 + 1 + filler row 3
    binary = ly.create_cell("elem_bin")
    for name in ("elem_b3", "elem_b2", "elem_b1", "elem_b0"):
        c = ly.create_cell(name)
        for i, j in GROUPS[name]:
            unit_at(c, unit, i, j)
        join_group(ink, c, g, GROUPS[name], GROUP_PIN[name])
        binary.insert(db.CellInstArray(c.cell_index(), db.Trans()))
    unit_at(binary, dummy, 3, 3)   # the filler site: 1023 units + 1 filler
    for t in (TRK_VBN, TRK_OUTP, TRK_OUTN, TRK_IREF):    # the column's tracks pass the filler
        ink.v(binary, 3, 3 * px + t, 3 * py - EXT, 3 * py + g.uh + EXT)
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

    # --- column rails: vbn / iref collected above the array, outp / outn below, vss both
    y_edge = (n - 1) * py + g.uh
    last = (n - 1) * px
    for name, t in (("vbn", TRK_VBN), ("iref", TRK_IREF)):
        y = y_edge + RAIL_TOP[name]
        ink.h(top, 4, t - W // 2, last + t + W // 2, y)
        for i in range(n):
            x = i * px + t
            if RING <= i < n - RING:
                ink.v(top, 3, x, (n - 1) * py - 700, y + W // 2)      # through the top ring row
            if i < 10 or RING <= i < n - RING:
                ink.cut(top, 3, x, y)
    for name, t in (("outp", TRK_OUTP), ("outn", TRK_OUTN)):
        y = RAIL_BOT[name]
        ink.h(top, 4, px + t - W // 2, (n - 2) * px + t + W // 2, y)
        for i in range(RING, n - RING):
            x = i * px + t
            ink.v(top, 3, x, y - W // 2, py - 500)                    # through the bottom ring row
            ink.cut(top, 3, x, y)
    for yr, ya, yb in ((y_edge + RAIL_TOP["vss"], (n - 1) * py - 700, None),
                       (RAIL_BOT["vss"], None, -500)):
        ink.h(top, 4, STRAP_VSS - W // 2, last + trk_vss_s + W // 2, yr)
        for i in range(n):
            x = i * px + trk_vss_s
            if ya is not None:
                ink.v(top, 3, x, ya, yr + W // 2)
            else:
                ink.v(top, 3, x, yr - W // 2, yb)
            ink.cut(top, 3, x, yr)

    # --- bias block above the array, its tracks reach the same rails
    bias = make_bias(ink, lib, g)
    y_bias = n * py + dbu(BAND_UM)
    top.insert(db.CellInstArray(bias.cell_index(), db.Trans(0, y_bias)))
    for k in range(10):
        for name, x in (("vbn", k * px + TRK_VBN), ("iref", k * px + TRK_IREF),
                        ("vss", k * px + trk_vss_s)):
            ink.v(top, 3, x, y_edge + RAIL_TOP[name] - W // 2, y_bias + 100)

    # --- drivers in two rows below the array, nets routed through the channels
    drv, info = make_driver(ink, lib, g)
    dx = info["width"] + g.gap
    per_row = n
    nets = drive_nets(table, g, info, dx, per_row)
    for net in nets:
        net["lo"] = min(net["xt"], net["x_d"]) - 700
        net["hi"] = max(net["xt"], net["x_d"]) + 700
    up = assign_tracks([(m["lo"], m["hi"], (m["k"], m["kind"])) for m in nets if m["row"] == 0])
    dn = assign_tracks([(m["lo"], m["hi"], (m["k"], m["kind"])) for m in nets if m["row"] == 1])
    n_up = max(up.values()) + 1
    y_low_up = Y_TRACK0 - (n_up - 1) * PITCH_TRACK
    yb0 = y_low_up - 2500 - info["height"]
    dy = info["height"] + g.gap
    yb1 = yb0 - dy
    rows_y = (yb0, yb1)
    for k in range(N_UNARY + len(BINARY_UNITS)):
        r, c = divmod(k, per_row)
        top.insert(db.CellInstArray(drv.cell_index(), db.Trans(c * dx, rows_y[r])))
    for net in nets:
        key = (net["k"], net["kind"])
        if net["row"] == 0:
            yn = Y_TRACK0 - up[key] * PITCH_TRACK
        else:
            yn = yb1 - 2500 - dn[key] * PITCH_TRACK
        xt, xd, xp, yp = net["xt"], net["x_d"], net["xp"], net["yp"]
        ink.cut(top, 3, xp, yp)                       # element pin -> M4 stub -> M5 slot
        ink.pad(top, 4, xp, yp)
        ink.h(top, 4, xp, xt, yp)
        ink.cut(top, 4, xt, yp)
        ink.pad(top, 4, xt, yp)
        ink.pad(top, 5, xt, yp)
        ink.v(top, 5, xt, yn - W // 2, yp + W // 2)   # M5 down to the net's track
        ink.cut(top, 4, xt, yn)
        ink.pad(top, 4, xt, yn)
        ink.h(top, 4, xt, xd, yn)                     # M4 track to the driver lane
        ink.cut(top, 3, xd, yn)
        ink.pad(top, 4, xd, yn)
        ink.pad(top, 3, xd, yn)
        if net["row"] == 0:
            ink.v(top, 3, xd, rows_y[0] + info["y_out_top"] - PAD // 2, yn + W // 2)
        else:
            ink.v(top, 3, xd, yn - W // 2, rows_y[1] + info["y_out_bot"] + PAD // 2)
    # supply straps joining the two driver rows, vss on to the bottom vss rail
    for r in (0, 1):
        ink.h(top, 2, STRAP_VSS - W // 2, -EXT, rows_y[r] + info["y_vss"])
        ink.cut(top, 2, STRAP_VSS, rows_y[r] + info["y_vss"])
        ink.h(top, 2, STRAP_VDD - W // 2, -EXT, rows_y[r] + info["y_vdd"])
        ink.cut(top, 2, STRAP_VDD, rows_y[r] + info["y_vdd"])
    ink.v(top, 3, STRAP_VSS, rows_y[1] + info["y_vss"] - W // 2, RAIL_BOT["vss"] + W // 2)
    ink.cut(top, 3, STRAP_VSS, RAIL_BOT["vss"])
    ink.v(top, 3, STRAP_VDD, rows_y[1] + info["y_vdd"] - W // 2, rows_y[0] + info["y_vdd"] + W // 2)

    # --- the 72 reference pins
    for k in range(N_UNARY + len(BINARY_UNITS)):
        r, c = divmod(k, per_row)
        ink.label(top, 3, PIN_NAMES[5 + k], c * dx + info["x_d"], rows_y[r] + info["y_d"])
    ink.label(top, 4, "iref", 2 * px, y_edge + RAIL_TOP["iref"])
    ink.label(top, 4, "vss", 2 * px, y_edge + RAIL_TOP["vss"])
    ink.label(top, 4, "outp", 2 * px + TRK_OUTP, RAIL_BOT["outp"])
    ink.label(top, 4, "outn", 2 * px + TRK_OUTN, RAIL_BOT["outn"])
    ink.label(top, 3, "vdd", STRAP_VDD, rows_y[0] + info["y_vdd"])
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
    scratch = db.Layout()
    scratch.dbu = DBU
    g = Geom(Lib(scratch))
    px, py = g.px, g.py
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
    errs += read_back_routing(ly, top, table, g)
    return errs


def read_back_routing(ly: db.Layout, top: db.Cell, table: dict, g: Geom) -> list[str]:
    """Pins, routed units and routed nets, counted from the stream itself."""
    errs = []
    # the 72 reference pins: each name exactly once, as a label on a metal level
    names = []
    for i in M:
        li = ly.find_layer(M[i][0], LABEL_DT)
        if li is not None:
            names += [s.text_string for s in top.shapes(li).each() if s.is_text()]
    if sorted(names) != sorted(PIN_NAMES):
        missing = sorted(set(PIN_NAMES) - set(names))
        extra = sorted(n for n in set(names) if names.count(n) > 1 or n not in PIN_NAMES)
        errs.append(f"{len(names)} pin labels, expected {len(PIN_NAMES)}; "
                    f"missing {missing[:5]}, extra {extra[:5]}")
    # every unit is joined into its group's sp and sn nets (union-find over the join shapes)
    m2, m3 = ly.find_layer(*M[2]), ly.find_layer(*M[3])
    groups = [s["cell"] for s in table["sites"] if s["role"] == "unary"] + list(GROUPS)
    routed = 0
    for name in groups:
        cell = ly.cell(name)
        units = sorted((inst.trans.disp.x // g.px, inst.trans.disp.y // g.py)
                       for inst in cell.each_inst() if inst.cell.name == "unit_cell")
        boxes2 = {(b.left, b.bottom, b.right, b.top) for b in
                  (s.box for s in cell.shapes(m2).each() if s.is_box())}
        boxes3 = {(b.left, b.bottom, b.right, b.top) for b in
                  (s.box for s in cell.shapes(m3).each() if s.is_box())}
        for y0, xv in ((g.y_sp, XSPV), (g.y_sn, XSNV)):
            parent = {u: u for u in units}

            def find(u):
                while parent[u] != u:
                    parent[u] = parent[parent[u]]
                    u = parent[u]
                return u
            for i, j in units:
                if (i + 1, j) in parent and (i * g.px + g.uw - 100, y0 + j * g.py - W // 2,
                                             (i + 1) * g.px + 100, y0 + j * g.py + W // 2) in boxes2:
                    parent[find((i, j))] = find((i + 1, j))
                x = i * g.px + xv
                if (i, j - 1) in parent and (x - W // 2, y0 + (j - 1) * g.py - W // 2,
                                             x + W // 2, y0 + j * g.py + W // 2) in boxes3:
                    parent[find((i, j))] = find((i, j - 1))
            if len({find(u) for u in units}) != 1:
                errs.append(f"{name}: units are not all joined on the "
                            f"{'sp' if y0 == g.y_sp else 'sn'} net")
            elif y0 == g.y_sp:
                routed += len(units)
    if routed != 1023:
        errs.append(f"{routed} units joined into their element's gate nets, expected 1023")
    m5 = ly.find_layer(*M[5])
    n_m5 = sum(1 for s in top.shapes(m5).each() if s.is_box() and s.box.height() > PAD)
    if n_m5 != 2 * (N_UNARY + len(BINARY_UNITS)):
        errs.append(f"{n_m5} M5 element-to-driver wires, expected {2 * (N_UNARY + len(BINARY_UNITS))}")
    return errs


def evidence(h: str) -> dict:
    return {
        "schema_version": 1,
        "kind": "generic",
        "status": "pass",
        "t1_item": 2,
        "summary": "analog-partition layout stream regenerated from layout/gen_array.py; "
                   "byte-identical on a second run. Placed, routed and pinned; "
                   "not extracted or simulated.",
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
