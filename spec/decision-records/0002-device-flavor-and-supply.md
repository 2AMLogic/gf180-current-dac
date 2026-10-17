# 0002: 3.3 V devices and supply

- **Status**: proposed
- **Date**: 2026-10-17
- **Decided by**: pending operator ratification (with DR-0001)

## Context

README: "3.3 V devices; 5 V option argued if used". The open question in issue
#2 is whether the 5 V devices help output impedance enough to justify them.

## Decision

Use `nfet_03v3` / `pfet_03v3` on a 3.3 V -/+10 % supply. Do not use the 5 V
devices.

Evidence: the PDK carries the same mismatch hooks on the 5 V devices
(`sm141064.spice`), so mismatch data is not the deciding factor. For the same
0.50 % unit sigma the 5 V devices need about 2.5x the gate area
(`spec/sizing/sizing-output.md`, section 4; for example `nfet_06v0` 66.7 vs
`nfet_03v3` 26.5 um^2 at Vov = 0.4 V), and the README offers no 5 V supply.
The output-impedance requirement is 12.8 Mohm per 1.955 uA unit cell; whether
a 3.3 V cascode meets it at all corners is a cell-schematic result that does
not yet exist.

## Alternatives considered

- **5 V devices**: about 2.5x array area; needs a supply the block does not
  have; the benefit (higher intrinsic output resistance from longer minimum L)
  is not shown to be needed.
- **Mixed (5 V cascode over 3.3 V source)**: not evaluated; the issue asks to
  argue 5 V only if used.

## Consequences

If the cell schematic cannot reach 12.8 Mohm with a 3.3 V cascode across PVT,
this record is superseded and the array area grows by about 2.5x; that risk is
open, not closed.
