# 0006: Analog schematic sizing assumptions

- **Status**: proposed
- **Date**: 2026-10-27
- **Decided by**: pending operator review (issue #30)

## Context

The first analog schematics (`design/gen_analog.py`) need device sizes the
sizing table (`spec/sizing/sizing-output.md`) does not give. CLAUDE.md: do not
substitute an assumed value without a decision record.

## Decision

Taken from the sizing table: current-source gate area. nfet_03v3 M1 is
W = 2.6 um, L = 10.3 um, 26.78 um^2 against the 26.53 um^2 floor at
Vov = 0.4 V. The W/L of about 0.25 is a square-law estimate for
Iu = 1.955 uA at Vov = 0.4 V; **not** confirmed by simulation.

**Assumed, no source** (all nfet_03v3 / pfet_03v3):

| Device | W / L | Note |
|---|---|---|
| cascode M2 | 5.2 u / 1 u | not sized for the 12.8 Mohm requirement |
| switches Msp, Msn | 2.6 u / 0.28 u | not sized for the 283 fF requirement |
| driver inverters | nfet 1 u / 0.28 u, pfet 2 u / 0.28 u | |

Structural assumptions:

- Cell polarity: n (sinking), outputs loaded to the positive rail.
- Bias: iref is forced into a diode stack (cascode over source), 10 unit
  devices each, so the mirror ratio is 1023:10 = 102.3, not the 100:1 of
  the spec table. At 20 uA that gives about 2.05 mA full scale, inside the
  1.8 to 2.2 mA row. The reference input is the cascode-gate node, `iref`.
- Dummies: 32 ring cells plus 1 filler completing the 16-unit binary site.
  The layout issue sets the real ring.
- Driver: sp has two inverter stages, sn three, so sn lags sp by one stage.
  Crossing point is not designed.

## Bias boundary and sibling reuse

This is not a deviation from DR-0004 and DR-0005; it is the interface to
them. `iref` (the cascode-gate node of the diode stack) is the boundary where
the V-to-I bias loop hands its 20 uA to this schematic. That loop is built
from `gf180-bandgap` (DR-0004, pinned at
`6fe62e6cb6d037b55d871792e4b7b47e4344fb2a`) and `gf180-opamp` (DR-0005, pinned
at `687c03b3aca2c41f2aa591595574f702c3e1ec2e`), both adopted by
`reuse.lock.json`. This schematic holds only the mirror and array side: the
diode stack, unit cells, binary elements, dummies and drivers.

Deferred: the bias-loop integration itself (instantiating the pinned sibling
blocks, the V-to-I resistor, and closing the loop onto `iref`). Until it
lands, `iref` is driven by an ideal source in the testbench, and the
full-scale figure above is an estimate from that ideal 20 uA, not from the
bandgap or opamp.

## Alternatives considered

- Wait for a sizing run: rejected; the schematic is the input to that run.
- One `m=` multiplier per element: rejected; hides per-cell identity from LVS
  and from Monte Carlo (instance-independence probe).

## Consequences

Any sizing change is a generator edit plus regenerated netlists. Cascode and
switch sizes, the mirror ratio and the driver need a PVT and Monte Carlo run
before any impedance, capacitance, full-scale or mismatch claim.
