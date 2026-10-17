# 0005: Bias-loop amplifier: adopt gf180-opamp

- **Status**: proposed
- **Date**: 2026-10-17
- **Decided by**: pending operator ratification (with DR-0001)

## Context

The 20 uA reference current is made from the bandgap voltage by a V-to-I
bias loop (DR-0004), which needs an amplifier. `gf180-opamp` is the same-PDK
amplifier. Facts read from `2AMLogic/gf180-opamp` at
`687c03b3aca2c41f2aa591595574f702c3e1ec2e` (origin/main, 2026-10-17): schematic
level, 45-point PVT grid, DC gain worst 93.79 dB, GBW worst 11.9 MHz, phase
margin worst 71.99 degrees, quiescent power worst 311 uW, input offset mismatch
worst |mean| + 3 sigma 15.458 mV; its target spec is partially ratified, no
layout evidence, area open.

## Decision

**Adopt** `gf180-opamp` for the bias loop; pinned in `reuse.lock.json` as a
`consumes` edge at the commit above.

Why this fits: the bias loop is a DC loop on a quiet node. A 15.5 mV worst
offset on a 1.2 V reference is about 1.3 % of the reference current, a gain
error absorbed by the full-scale row (see DR-0004), not an INL term. The loop
bandwidth is not a requirement here, and 93.8 dB of DC gain is more than a
static bias needs.

## Alternatives considered

- **Keep (own amplifier in this repo)**: rejected; it would duplicate a block
  with a worse evidence trail, for a function that has no tight requirement.
- **Skip the amplifier (resistor + mirror reference)**: not rejected on the
  merits; a simple mirror-based reference is a legitimate cell topology. It is
  left to the bias schematic. If the schematic drops the loop, this record is
  superseded and the `reuse.lock.json` edge removed.

## Consequences

- **Not verified**: input common-mode range at 1.2 V and whether its output
  drives the mirror gate; both are bias-schematic results that do not exist
  yet. If either fails, supersede.
- The bias loop is a supply-ripple path into the 1023 cells; its PSRR is the
  adopted amplifier's, which that repo lists as systematic-only and ungraded.
