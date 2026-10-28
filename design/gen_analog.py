#!/usr/bin/env python3
"""Generate the analog-partition xschem schematics, symbols and inventory.

    python3 design/gen_analog.py          # rewrites design/analog/*.sch, *.sym,
                                          # design/inventory-item1-analog.json
    python3 design/gen_analog.py --check  # exit 1 if the committed files differ

The array is generated, not drawn: every unit cell is an explicit instance
(1023 live cells plus dummies), never an `m=` multiplier, so layout and LVS can
match instance for instance and a Monte Carlo run draws mismatch per instance
(spec/sizing/instance-independence-probe.md).

Device sizes are ASSUMPTIONS, recorded in
spec/decision-records/0006-analog-schematic-sizing-assumptions.md. Only the
current-source gate area comes from the sizing table (spec/sizing/sizing-output.md
section 4). Nothing here is a performance result.
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "design" / "analog"
INVENTORY = ROOT / "design" / "inventory-item1-analog.json"

# ---- segmentation (spec/target-spec.md section 3) --------------------------
N_UNARY = 63            # 6 unary bits -> 2^6 - 1 elements
UNITS_PER_UNARY = 16    # 2^4 unit cells each
BINARY_UNITS = [1, 2, 4, 8]
N_RING_DUMMY = 132      # one-cell ring of the real layout (layout/gen_array.py); was a 32 placeholder, DR-0006
IREF_MIRROR_UNITS = 10  # reference leg: 10 unit sources (see DR-0006)

# ---- device sizes (ASSUMED, DR-0006) ---------------------------------------
CS = {"W": "2.6u", "L": "10.3u"}    # 26.78 um^2 >= 26.53 um^2 (nfet, Vov 0.4 V)
CAS = {"W": "5.2u", "L": "1u"}
SW = {"W": "2.6u", "L": "0.28u"}
INV_N = {"W": "1u", "L": "0.28u"}
INV_P = {"W": "2u", "L": "0.28u"}

HDR = "v {xschem version=3.4.4 file_version=1.2\n}\nG {}\nV {}\nS {}\nE {}\n"
PARASITIC = (
    "ad=\"'int((nf+1)/2) * W/nf * 0.18u'\" pd=\"'2*int((nf+1)/2) * (W/nf + 0.18u)'\" "
    "as=\"'int((nf+2)/2) * W/nf * 0.18u'\" ps=\"'2*int((nf+2)/2) * (W/nf + 0.18u)'\" "
    "nrd=\"'0.18u / W'\" nrs=\"'0.18u / W'\" sa=0 sb=0 sd=0"
)

# subcircuit pin lists: (name, dir). Left side = in/inout, right side = out.
SYMS = {
    "unit_cell": [("vbn", "in"), ("vcas", "in"), ("sp", "in"), ("sn", "in"),
                  ("vss", "inout"), ("outp", "inout"), ("outn", "inout")],
    "dummy_cell": [("vss", "inout")],
    "driver": [("d", "in"), ("vdd", "inout"), ("vss", "inout"),
               ("sp", "out"), ("sn", "out")],
    "bias": [("iref", "inout"), ("vss", "inout"), ("vbn", "out")],
}
for _n in [UNITS_PER_UNARY] + BINARY_UNITS:
    SYMS[f"elem_{_n}"] = list(SYMS["unit_cell"])


def sym_text(name):
    pins = SYMS[name]
    left = [p for p in pins if p[1] != "out"]
    right = [p for p in pins if p[1] == "out"]
    h = 20 * max(len(left), len(right), 1) + 20
    out = [
        "v {xschem version=3.4.4 file_version=1.2\n}",
        "G {}",
        'K {type=subcircuit\nformat="@name @pinlist @symname"\ntemplate="name=x1"\n}',
        "V {}", "S {}", "E {}",
        f"B 4 -60 -10 60 {h} {{}}",
    ]
    for side, plist, x, sign in (("l", left, -80, 1), ("r", right, 80, -1)):
        for i, (pn, pd) in enumerate(plist):
            y = 10 + 20 * i
            out.append(f"L 4 {x} {y} {x + sign * 20} {y} {{}}")
            out.append(f"B 5 {x - 2.5} {y - 2.5} {x + 2.5} {y + 2.5} {{name={pn} dir={pd}}}")
            tx = -55 if side == "l" else 55
            out.append(f"T {{{pn}}} {tx} {y - 4} 0 {0 if side == 'l' else 1} 0.2 0.2 {{}}")
    out.append(f"T {{@symname}} -40 {h + 5} 0 0 0.3 0.3 {{}}")
    out.append(f"T {{@name}} 0 -25 0 0 0.3 0.3 {{}}")
    return "\n".join(out) + "\n"


class Sch:
    def __init__(self):
        self.lines = []
        self.n = 0

    def _id(self, p):
        self.n += 1
        return f"{p}{self.n}"

    def wire(self, x1, y1, x2, y2, net):
        # unlabelled wire plus a lab_pin at the far end names the net; a bare
        # `lab=` on a wire does not name it in the netlist
        self.lines.append(f"N {x1} {y1} {x2} {y2} {{}}")
        rot = 0 if x2 < x1 or y2 < y1 else 2
        if x1 == x2:
            rot = 3 if y2 < y1 else 1
        self.lines.append(
            f"C {{devices/lab_pin.sym}} {x2} {y2} {rot} 0 {{name={self._id('l')} sig_type=std_logic lab={net}}}")

    def top_pin(self, kind, x, y, net):
        """kind ipin|opin|iopin. Pin origin at (x, y); wire leaves to the side
        the symbol artwork does not occupy."""
        d = 20 if kind in ("ipin",) else -20
        if kind == "iopin":
            d = -20
        # ipin artwork extends left of its origin -> wire goes right; opin and
        # iopin extend right -> wire goes left.
        self.lines.append(f"C {{devices/{kind}.sym}} {x} {y} 0 0 {{name={self._id('p')} lab={net}}}")
        self.wire(x, y, x + d, y, net)

    def mos(self, sym, name, x, y, d, g, s, b, w, l):
        """3.3 V gf180mcu MOS; D/S rows differ for n/p (D top for n, S top for p)."""
        self.lines.append(
            f"C {{{sym}.sym}} {x} {y} 0 0 {{name={name} L={l} W={w} nf=1 m=1 {PARASITIC} "
            f"model={sym} spiceprefix=X}}")
        top, bot = (d, s) if sym.startswith("nfet") else (s, d)
        self.wire(x + 20, y - 30, x + 20, y - 50, top)
        self.wire(x + 20, y + 30, x + 20, y + 50, bot)
        self.wire(x - 20, y, x - 40, y, g)
        self.wire(x + 20, y, x + 40, y, b)

    def sub(self, name, cell, x, y, conn):
        """Instance of a generated subcircuit symbol; `conn` pin->net."""
        pins = SYMS[cell]
        left = [p for p in pins if p[1] != "out"]
        right = [p for p in pins if p[1] == "out"]
        self.lines.append(f"C {{{cell}.sym}} {x} {y} 0 0 {{name={name}}}")
        for plist, px, d in ((left, -80, -20), (right, 80, 20)):
            for i, (pn, _) in enumerate(plist):
                py = y + 10 + 20 * i
                self.wire(x + px, py, x + px + d, py, conn[pn])

    def text(self):
        return HDR + "\n".join(self.lines) + "\n"


def ifmt(x):
    return int(x) if float(x).is_integer() else x


def unit_cell(prefix_dummy=False):
    s = Sch()
    if prefix_dummy:
        g = dict(vbn="vss", vcas="vss", sp="vss", sn="vss", outp="vss", outn="vss")
    else:
        g = dict(vbn="vbn", vcas="vcas", sp="sp", sn="sn", outp="outp", outn="outn")
    s.mos("nfet_03v3", "M1", 0, 300, "n1", g["vbn"], "vss", "vss", **{k.lower(): v for k, v in CS.items()})
    s.mos("nfet_03v3", "M2", 0, 160, "n2", g["vcas"], "n1", "vss", **{k.lower(): v for k, v in CAS.items()})
    s.mos("nfet_03v3", "Msp", -120, 20, g["outp"], g["sp"], "n2", "vss", **{k.lower(): v for k, v in SW.items()})
    s.mos("nfet_03v3", "Msn", 120, 20, g["outn"], g["sn"], "n2", "vss", **{k.lower(): v for k, v in SW.items()})
    pins = [("vbn", "ipin"), ("vcas", "ipin"), ("sp", "ipin"), ("sn", "ipin"),
            ("vss", "iopin"), ("outp", "iopin"), ("outn", "iopin")]
    if prefix_dummy:
        pins = [("vss", "iopin")]
    for i, (pn, kind) in enumerate(pins):
        s.top_pin(kind, -400, 20 * i, pn)
    return s.text()


def inv(s, tag, x, y, a, z):
    s.mos("pfet_03v3", f"Mp{tag}", x, y - 70, z, a, "vdd", "vdd", **{k.lower(): v for k, v in INV_P.items()})
    s.mos("nfet_03v3", f"Mn{tag}", x, y + 70, z, a, "vss", "vss", **{k.lower(): v for k, v in INV_N.items()})


def driver():
    # sp = d (two stages), sn = ~d (three stages). Crossing point is NOT
    # designed here; see DR-0006 open items.
    s = Sch()
    inv(s, "1", 0, 0, "d", "na")
    inv(s, "2", 200, 0, "na", "sp")
    inv(s, "3", 400, 0, "sp", "sn")
    for i, (pn, kind) in enumerate([("d", "ipin"), ("vdd", "iopin"), ("vss", "iopin")]):
        s.top_pin(kind, -400, 20 * i, pn)
    s.top_pin("opin", 700, 0, "sp")
    s.top_pin("opin", 700, 20, "sn")
    return s.text()


def element(n_units):
    s = Sch()
    for k in range(n_units):
        col, row = k % 4, k // 4
        s.sub(f"xu{k}", "unit_cell", 260 * col, 200 * row,
              dict(vbn="vbn", vcas="vcas", sp="sp", sn="sn", vss="vss",
                   outp="outp", outn="outn"))
    for i, (pn, kind) in enumerate([("vbn", "ipin"), ("vcas", "ipin"), ("sp", "ipin"),
                                    ("sn", "ipin"), ("vss", "iopin"),
                                    ("outp", "iopin"), ("outn", "iopin")]):
        s.top_pin(kind, -400, 20 * i, pn)
    return s.text()


def bias():
    # iref is pushed into the vcas node: Mc (diode, drain=gate=iref) stacked on
    # Mb (diode, drain=gate=vbn). Cascode drain of every unit cell then sits at
    # the same Vgs as the reference leg. Mb/Mc are IREF_MIRROR_UNITS explicit
    # unit-sized devices each.
    s = Sch()
    for k in range(IREF_MIRROR_UNITS):
        x = 120 * k
        s.mos("nfet_03v3", f"Mc{k}", x, 0, "iref", "iref", "vbn", "vss", **{a.lower(): b for a, b in CAS.items()})
        s.mos("nfet_03v3", f"Mb{k}", x, 200, "vbn", "vbn", "vss", "vss", **{a.lower(): b for a, b in CS.items()})
    s.top_pin("iopin", -400, 0, "iref")
    s.top_pin("iopin", -400, 20, "vss")
    s.top_pin("opin", 1400, 0, "vbn")
    return s.text()


def top():
    s = Sch()
    ctrl = [f"t{i}" for i in range(N_UNARY)] + [f"b{i}" for i in range(len(BINARY_UNITS))]
    s.sub("xbias", "bias", 0, 0, dict(iref="iref", vss="vss", vbn="vbn"))
    cell_w = 700
    k = 0
    for i, c in enumerate(ctrl):
        units = UNITS_PER_UNARY if i < N_UNARY else BINARY_UNITS[i - N_UNARY]
        x, y = 600 + cell_w * (i % 8), 600 * (i // 8) + 300
        s.sub(f"xdrv_{c}", "driver", x, y, dict(d=c, vdd="vdd", vss="vss", sp=f"sp_{c}", sn=f"sn_{c}"))
        s.sub(f"xel_{c}", f"elem_{units}", x, y + 200,
              dict(vbn="vbn", vcas="iref", sp=f"sp_{c}", sn=f"sn_{c}", vss="vss",
                   outp="outp", outn="outn"))
    base = 600 * (len(ctrl) // 8 + 2) + 300
    # one dummy unit completes the 16-unit binary site (1+2+4+8 = 15), then the ring
    for j in range(1 + N_RING_DUMMY):
        tag = "bin" if j == 0 else f"r{j - 1}"
        s.sub(f"xdum_{tag}", "dummy_cell", 300 * (j % 12), base + 100 * (j // 12), dict(vss="vss"))
    pins = [("iref", "iopin"), ("vdd", "iopin"), ("vss", "iopin"),
            ("outp", "iopin"), ("outn", "iopin")] + [(c, "ipin") for c in ctrl]
    for i, (pn, kind) in enumerate(pins):
        s.top_pin(kind, -400, 20 * i, pn)
    return s.text()


def files():
    f = {}
    for name in SYMS:
        f[OUT / f"{name}.sym"] = sym_text(name)
    f[OUT / "unit_cell.sch"] = unit_cell()
    f[OUT / "dummy_cell.sch"] = unit_cell(prefix_dummy=True)
    f[OUT / "driver.sch"] = driver()
    f[OUT / "bias.sch"] = bias()
    for n in [UNITS_PER_UNARY] + BINARY_UNITS:
        f[OUT / f"elem_{n}.sch"] = element(n)
    f[OUT / "dac_analog.sch"] = top()
    f[OUT / "xschemrc"] = XSCHEMRC
    f[INVENTORY] = inventory()
    return f


XSCHEMRC = """\
# Project xschemrc for `klt netlist --rcfile design/analog/xschemrc`.
# Symbol search path: this directory (generated symbols) and the gf180mcuD PDK
# symbols. PDK root: $PDK_ROOT, else ~/.ciel/ciel/gf180mcu/versions/<pin in
# sim/pdk.json>. Generated by design/gen_analog.py; do not edit.
set XSCHEM_LIBRARY_PATH {}
append XSCHEM_LIBRARY_PATH :${XSCHEM_SHAREDIR}/xschem_library/devices
append XSCHEM_LIBRARY_PATH :${XSCHEM_SHAREDIR}/xschem_library
append XSCHEM_LIBRARY_PATH :[file dirname [file normalize [info script]]]
if {[info exists env(PDK_ROOT)] && $env(PDK_ROOT) ne {}} {
  set PDK_ROOT $env(PDK_ROOT)
} else {
  set PDK_ROOT $env(HOME)/.ciel/ciel/gf180mcu/versions/f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
}
append XSCHEM_LIBRARY_PATH :${PDK_ROOT}/gf180mcuD/libs.tech/xschem/symbols
"""


def schematics():
    return ["unit_cell", "dummy_cell", "driver", "bias"] + \
        [f"elem_{n}" for n in [UNITS_PER_UNARY] + BINARY_UNITS] + ["dac_analog"]


def inventory():
    rel = "design/analog"
    derived = []
    for n in schematics():
        argv = ["klt", "netlist", f"{rel}/{n}.sch", "-o", f"{rel}/{n}.spice",
                "--rcfile", f"{rel}/xschemrc"]
        if n == "dac_analog":
            argv.append("--block")
        derived.append({
            "path": f"{rel}/{n}.spice",
            "generator": "klt netlist",
            "check": {"argv": argv + ["--check"], "local_only": True},
        })
    sources = ["design/gen_analog.py", f"{rel}/xschemrc"] + \
        [f"{rel}/{n}.sch" for n in schematics()] + \
        [f"{rel}/{n}.sym" for n in SYMS]
    return json.dumps({
        "schema_version": 1,
        "kind": "t1-attestation-inventory",
        "t1_item": 1,
        "description": "Analog partition design sources: generated xschem "
                       "schematics and symbols, the generator "
                       "(python3 design/gen_analog.py), and netlists derived "
                       "with klt netlist. Existence and freshness only; no "
                       "performance claim.",
        "sources": sources,
        "derived": derived,
    }, indent=2) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    bad = []
    for path, text in files().items():
        if a.check:
            if not path.exists() or path.read_text() != text:
                bad.append(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    if bad:
        print("stale:", *[str(p.relative_to(ROOT)) for p in bad], sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
