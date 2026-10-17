# 0003: Gradient amplitude is an assumption

- **Status**: proposed
- **Date**: 2026-10-17
- **Decided by**: pending operator ratification (with DR-0001)

## Context

CLAUDE.md: "If the PDK's models do not carry the mismatch data a claim needs,
say so; do not substitute an assumed value without a decision record."
`sm141064.spice` carries per-instance random mismatch only. It has no spatial
correlation or gradient term, so no INL claim that includes a systematic
gradient can come from the PDK.

## Decision

The sizing model uses an assumed gradient: linear 0.50 % and quadratic 0.20 %
peak-to-peak across the unary array, direction and quadratic sign random per
sample. These values are assumptions, chosen large enough that a raster
switching sequence fails (35.66 % yield at sigma_u = 0.75 %) and a symmetric
one passes, so the sequence is what the spec depends on. They are not taken
from any process data. Replace them with values extracted from the layout and
the process when post-layout data exists, by a superseding record.

## Alternatives considered

- **Omit the gradient**: rejected; random mismatch alone would pass a raster
  sequence and hide the reason for common-centroid placement.
- **Take a number from another process**: rejected; no gf180mcu data was
  found, and borrowing one would pass off a number as sourced.

## Consequences

Every linearity number quoted from the sizing model carries "gradient: assumed,
DR-0003". If the real gradient is 2x larger, section 3 of the sizing output
must be rerun (`--check` will show it) and the sequence re-checked.
