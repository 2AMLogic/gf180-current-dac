#!/usr/bin/env python3
"""Write verification/erc/analog.spec.json (the analog `klt erc` supply spec).

    python3 verification/erc/gen_analog_spec.py          # write the spec
    python3 verification/erc/gen_analog_spec.py --check  # exit 1 if it differs

Everything but the substrate tie is fixed text. The stream draws no p-well
layer (the nfets sit in the native substrate), so the substrate tie is
declared with `well_layer: null` plus `well_boxes` (klt erc "A block with no
drawn well at all"). One box per top-cell instance (each unary element, the
binary block, the bias block, each driver, each ring dummy), shrunk by
INSET_UM so the boxes stay separate polygons: each one must independently
hold a p+ tap that reaches `vss`. One box over the whole array would be
rejected as degenerate by klt erc and would only ask for any tap anywhere.
Needs the pip `klayout` package; reads layout/gf180-current-dac-analog.gds.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import klayout.db as db

HERE = Path(__file__).resolve().parent
GDS = HERE.parent.parent / "layout" / "gf180-current-dac-analog.gds"
SPEC = HERE / "analog.spec.json"
TOP = "dac_analog_layout"
INSET_UM = 0.1


def boxes() -> list[list[float]]:
    ly = db.Layout()
    ly.read(str(GDS))
    out = []
    for inst in ly.cell(TOP).each_inst():
        b = inst.bbox().to_dtype(ly.dbu)
        out.append([round(b.left + INSET_UM, 3), round(b.bottom + INSET_UM, 3),
                    round(b.right - INSET_UM, 3), round(b.top - INSET_UM, 3)])
    return sorted(out, key=lambda r: (r[1], r[0]))


def spec() -> dict:
    return {
        "stackup": [
            {"name": "poly", "layer": "30/0", "role": "gate"},
            {"name": "metal1", "layer": "34/0"},
            {"name": "metal2", "layer": "36/0"},
            {"name": "metal3", "layer": "42/0", "label_layer": "42/10"},
            {"name": "metal4", "layer": "46/0", "label_layer": "46/10"},
            {"name": "metal5", "layer": "81/0"},
        ],
        "vias": [
            {"name": "contact", "layer": "33/0", "between": ["poly", "metal1"]},
            {"name": "via1", "layer": "35/0", "between": ["metal1", "metal2"]},
            {"name": "via2", "layer": "38/0", "between": ["metal2", "metal3"]},
            {"name": "via3", "layer": "40/0", "between": ["metal3", "metal4"]},
            {"name": "via4", "layer": "41/0", "between": ["metal4", "metal5"]},
        ],
        "nets": [
            {"name": "vdd", "kind": "supply"},
            {"name": "vss", "kind": "supply"},
        ],
        "ties": [
            {"name": "nwell_tie", "well_layer": "21/0", "tap_layer": "22/0",
             "tap_requires": ["32/0"], "connect_to": "metal1", "net": "vdd"},
            {"name": "substrate_tie", "well_layer": None, "well_boxes": boxes(),
             "tap_layer": "22/0", "tap_requires": ["31/0"],
             "connect_to": "metal1", "net": "vss"},
        ],
    }


def main() -> int:
    text = json.dumps(spec(), indent=1) + "\n"
    if "--check" in sys.argv:
        if SPEC.read_text() != text:
            print(f"{SPEC} is stale; rerun without --check", file=sys.stderr)
            return 1
        return 0
    SPEC.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
