#!/usr/bin/env python3
"""Unit tests for the shared subcircuit pin placement in gen_analog.py
(issue #153).

sym_text and Sch.sub must agree on where every subcircuit pin sits: the
symbol draws the pin there and every instance wire attaches there. The
freshness gate (gen_analog.py --check) cannot catch the two disagreeing —
a generator that moves only the symbol pin stays fresh after regeneration
while its wires miss the pin — so the agreement is asserted here, against
the emitted text of both writers rather than a shared internal.

The subcircuit schematics' own port symbols (Sch.sub_pins, issue #174)
are held to the same contract: their pin names, directions and order must
restate SYMS, the one table the symbol and the instance wiring draw from.

Needs no xschem, PDK or klt: it drives the generator module in memory.
Verify with `python3 -m unittest design.tests.test_gen_analog`.
"""

import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "gen_analog_under_test", ROOT / "design" / "gen_analog.py")
gen_analog = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen_analog)

# xschem pin square: `B 5 x-2.5 y-2.5 x+2.5 y+2.5 {name=pn dir=pd}`
PIN_LINE = re.compile(
    r"^B 5 (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)"
    r" \{name=(\w+) dir=(\w+)\}$")
# Sch.wire pair: bare wire, then the lab_pin naming the net at its far end
WIRE_LINE = re.compile(r"^N (-?\d+) (-?\d+) (-?\d+) (-?\d+) \{\}$")
LAB_LINE = re.compile(
    r"^C \{devices/lab_pin\.sym\} -?\d+ -?\d+ \d 0"
    r" \{name=\w+ sig_type=std_logic lab=(\w+)\}$")
# Sch.top_pin port symbol: `C {devices/ipin.sym} x y 0 0 {name=pN lab=net}`
PORT_LINE = re.compile(
    r"^C \{devices/(ipin|iopin|opin)\.sym\} -?\d+ -?\d+ 0 0"
    r" \{name=\w+ lab=(\w+)\}$")
PORT_KIND = {"in": "ipin", "inout": "iopin", "out": "opin"}


def symbol_pins(mod, cell):
    """pin name -> (x, y) pin origins parsed from the symbol text, plus the
    file order (the order xschem's @pinlist will netlist)."""
    pins, order = {}, []
    for line in mod.sym_text(cell).splitlines():
        m = PIN_LINE.match(line)
        if m:
            x = (float(m.group(1)) + float(m.group(3))) / 2
            y = (float(m.group(2)) + float(m.group(4))) / 2
            pins[m.group(5)] = (x, y)
            order.append(m.group(5))
    return pins, order


def instance_wire_ends(mod, cell, ox, oy):
    """net name -> (x, y) where an instance's wire meets the symbol pin,
    parsed from the schematic text of a lone instance at (ox, oy)."""
    s = mod.Sch()
    conn = {pn: "n_" + pn for pn, _ in mod.SYMS[cell]}
    s.sub("xuut", cell, ox, oy, conn)
    lines = s.text().splitlines()
    ends = {}
    for wire, lab in zip(lines, lines[1:]):
        w, l = WIRE_LINE.match(wire), LAB_LINE.match(lab)
        if w and l:
            ends[l.group(1)] = (int(w.group(1)), int(w.group(2)))
    return ends


class TestSymbolAndWiresSharePinPlacement(unittest.TestCase):
    def test_instance_wires_attach_at_symbol_pins(self):
        for cell in sorted(gen_analog.SYMS):
            with self.subTest(cell=cell):
                pins, _ = symbol_pins(gen_analog, cell)
                ends = instance_wire_ends(gen_analog, cell, 0, 0)
                self.assertEqual(sorted(ends), sorted("n_" + p for p in pins))
                for pn, pos in pins.items():
                    self.assertEqual(ends["n_" + pn], pos,
                                     f"{cell}.{pn}: wire and symbol pin disagree")

    def test_attachment_translates_with_instance_origin(self):
        # a nonzero origin must translate the symbol placement, not
        # re-derive it (the top level places subcircuits off-origin)
        cell, ox, oy = "bias", 600, -1400
        pins, _ = symbol_pins(gen_analog, cell)
        ends = instance_wire_ends(gen_analog, cell, ox, oy)
        for pn, (px, py) in pins.items():
            self.assertEqual(ends["n_" + pn], (ox + px, oy + py))

    def test_symbol_pin_order_is_left_then_right(self):
        # xschem netlists @pinlist in symbol-file pin order; the generator
        # draws left-side (in/inout) pins first, each side in SYMS order
        for cell in sorted(gen_analog.SYMS):
            with self.subTest(cell=cell):
                _, order = symbol_pins(gen_analog, cell)
                syms = gen_analog.SYMS[cell]
                expected = ([pn for pn, d in syms if d != "out"]
                            + [pn for pn, d in syms if d == "out"])
                self.assertEqual(order, expected)


class TestSubcircuitPortsMatchSyms(unittest.TestCase):
    def test_subcircuit_port_symbols_match_syms(self):
        # the third SYMS consumer: each subcircuit schematic's own port
        # symbols must carry the same pin names and directions as SYMS, in
        # the same left-then-right order the symbol draws them — a restated
        # port list here is what let a one-sided SYMS edit drift unseen
        # (the freshness gate regenerates from the same drifted generator)
        texts = gen_analog.files()
        for cell in sorted(gen_analog.SYMS):
            with self.subTest(cell=cell):
                ports = [(m.group(2), m.group(1))
                         for m in map(PORT_LINE.match,
                                      texts[gen_analog.OUT / f"{cell}.sch"].splitlines())
                         if m]
                syms = gen_analog.SYMS[cell]
                expected = [(pn, PORT_KIND[d])
                            for pn, d in ([p for p in syms if p[1] != "out"]
                                          + [p for p in syms if p[1] == "out"])]
                self.assertEqual(ports, expected)


if __name__ == "__main__":
    unittest.main()
