#!/usr/bin/env python3
"""Segmentation constants for the DAC current array — the single owner.

spec/target-spec.md section 3 ratifies 6 unary bits (63 elements of 2^4 unit
cells) plus 4 binary bits (1/2/4/8 units). Both generators load every
segmentation number from this module — design/gen_analog.py and
layout/gen_array.py — so a resize (SIDE; 8-bit fallback, 10-bit target,
12-bit stretch) is one edit instead of four restated constants that can
drift: commit 4eec471 repaired exactly such a drift (schematic ring 32 vs
layout ring 132) that neither generator's --check could catch.

Stdlib only; design/gen_analog.py must stay free of the klayout import.

    python3 spec/segmentation.py    # print the derived counts
"""

SIDE = 8            # array side in element sites
EL = 4              # units per element side
RING = 1            # dummy ring depth in unit cells (spec section 4)
BINARY_UNITS = [1, 2, 4, 8]

# Derived counts. The ring has two independent derivations — an area
# difference and a per-edge sum — and they must agree, or the schematic and
# the layout describe different arrays. The two formulas are algebraically
# identical (both reduce to 4*R*SIDE*EL + 4*R^2), so the check below cannot
# fire on any SIDE/EL/RING resize; what it catches is a hand-hardcoded
# replacement of either formula, which no resize exercises.
_N = SIDE * EL + 2 * RING                        # array side in unit cells, ring included
N_UNARY = SIDE * SIDE - 1                        # 63 unary elements
UNITS_PER_UNARY = EL * EL                        # 16 units per element
N_RING_DUMMY = _N ** 2 - (SIDE * EL) ** 2        # 132 ring cells (area difference)
N_DUMMY_CELLS = 4 * (_N - 2 * RING) * RING + 4 * RING * RING + 1  # ring + 1 filler: 133
N_LIVE_UNITS = N_UNARY * UNITS_PER_UNARY + sum(BINARY_UNITS)      # 1023

if N_DUMMY_CELLS != N_RING_DUMMY + 1:
    raise ValueError(
        f"dummy-ring derivations disagree: area {N_RING_DUMMY} vs per-edge "
        f"{N_DUMMY_CELLS - 1}; the schematic and the layout would diverge (issue #80)")

if __name__ == "__main__":
    for k in ("N_UNARY", "UNITS_PER_UNARY", "N_RING_DUMMY", "N_DUMMY_CELLS",
              "N_LIVE_UNITS"):
        print(f"{k} = {globals()[k]}")
