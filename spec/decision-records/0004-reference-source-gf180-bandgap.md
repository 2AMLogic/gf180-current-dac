# 0004: Reference source: adopt gf180-bandgap

- **Status**: proposed
- **Date**: 2026-10-17
- **Decided by**: pending operator ratification (with DR-0001)

## Context

README scope: the reference current is an input at the block boundary, and
`gf180-bandgap` builds the reference on this PDK. Issue #2 asks for an
adopt-or-keep record. Facts read from `2AMLogic/gf180-bandgap` at
`6fe62e6cb6d037b55d871792e4b7b47e4344fb2a` (origin/main, 2026-10-17): ratified
target 1.20 V +/-2 % untrimmed (3 sigma, mismatch Monte Carlo plus process
corners, -40 to +125 C), < 50 ppm/C, supply 3.3 V +/-10 %, quiescent current
< 50 uA; it is in the schematic-amendment phase with no measured silicon.

## Decision

**Adopt**: this repo consumes `gf180-bandgap` as its reference voltage source
and does not build its own. Pinned in `reuse.lock.json` as a `consumes` edge at
the commit above. The array's reference current is a boundary input of
20 uA +/-10 % (target-spec); the V-to-I conversion that makes it from the
bandgap voltage is this repo's bias loop (DR-0005).

Why this fits: a reference error of +/-2 % and 50 ppm/C is a **gain** error on
the full-scale current. Static INL is endpoint-corrected and depends on unit
matching, not on the reference value, and the spec's full-scale row (2 mA
+/-10 %) already absorbs it. The reference does not enter the linearity budget.

## Alternatives considered

- **Keep (build an own reference in this repo)**: rejected; it would duplicate
  a block that exists, is ratified, and covers the supply and temperature range
  here, and the DAC does not need a better reference than +/-2 %.
- **Take the reference current as a pure external input**: kept as the
  boundary definition; this record says what sits behind it in the in-tree
  design.

## Consequences

- **Not verified**: that the bandgap's output stage can drive the bias loop's
  input, and its load row is still TBD in its own spec. If the load does not
  fit, supersede this record.
- The bandgap's noise and PSRR are open there; they matter here only as the
  low-frequency noise on the full-scale current, which is not rated.
- The bandgap has no measured silicon; this repo's results inherit that.

## Proposed revision note (2026-10-20, increment C of issue #2)

Not a status change; this record stays `proposed`. Reassessed against the
pinned figures in [`../interface-evidence.md`](../interface-evidence.md)
(`gf180-bandgap` @6fe62e6):

- The "reference error is a gain error" argument stands.
- The bandgap load row is still `TBD` and every PSRR and noise bench ran
  unloaded on an earlier DUT revision (I2, I6, I7); "output stage can drive the
  bias loop" stays unverified.
- The 3 sigma untrimmed window (1.176 to 1.224 V) is not contained in the
  opamp's common-mode range (I10); see DR-0005.
- The pin shows no silicon and a layout that predates its latest schematic
  amendment. Adoption stays proposed and is limited to what the table shows.
