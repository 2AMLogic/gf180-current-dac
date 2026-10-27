# 0007: Analog layout assumptions

- **Status**: proposed
- **Date**: 2026-10-27
- **Decided by**: pending operator review (issue #32)

## Context

The first layout of the analog partition (`layout/gen_array.py`) needs choices
the proposed spec does not make. CLAUDE.md: do not substitute an assumed value
without a decision record. The spec itself is proposed, not ratified (DR-0001),
so this layout is built against the proposed rows.

## Decision

Taken from the spec unchanged: 32 x 32 unit sites as 8 x 8 elements of 4 x 4
units, a dummy ring of one cell on all sides, point-symmetric pairs, the
inout-pairs sequence. The ring depth is not changed.

**Assumed, no source:**

| Item | Choice | Note |
|---|---|---|
| Unit-cell arrangement | current source, cascode, then two switches, stacked vertically | not optimised for matching, routing or parasitics |
| Device spacing | 0.6 um between primitive bounding boxes | the primitives' own boxes include their tap pads; not checked against the DRC deck |
| Device primitives | `klt gen mos_array`, one device each, gate contact on | W/L from DR-0006 |
| Binary block | 8 / 4 / 2 / 1 units in rows 0-1 / 2 / 3 / 3 of a 4 x 4 block, filler last | bits are not common-centroid with each other |
| Binary block site | the 64th (last) site of the sequence | matches the sizing model, which gives it no gradient |
| Driver and bias placement | driver band below, bias block above the array | no matching claim |
| Ring dummies | 132 (34 x 34 - 32 x 32), plus 1 filler | the schematic still has 33 (DR-0006 placeholder) |

## Consequences

Nothing here supports a linearity claim: the gradient is assumed (DR-0003) and
no extraction exists. The schematic dummy count must be raised to match before
LVS. Routing may force a different unit-cell arrangement and a new stream.

## Alternatives considered

- Hand-placing cells: rejected; CLAUDE.md requires a generated array.
- A raster sequence: rejected; 35.66 % yield in the spec's own check.
- A deeper ring: rejected here; the spec allows it only through a decision
  record, and nothing yet shows the need.
