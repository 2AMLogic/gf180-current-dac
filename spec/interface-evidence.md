# Sibling interface evidence

- **Status**: PROPOSED, increment C of issue #2 (`Part of #2`). Ratifies nothing.
  `reuse.lock.json` is not edited, no numeric row of
  [`target-spec.md`](target-spec.md) is changed, and no simulation was run.
- **Date drafted**: 2026-10-20
- **Reviewer**: none yet (see increment D). This is the Builder's tabulation,
  not a reviewed conclusion.
- **Method**: read-only `git show <pin>:<path>` on local clones of the two
  siblings. Nothing was taken from memory or from the siblings' tip of `main`.

| Sibling | Pinned commit (`reuse.lock.json`) | Pin short |
|---|---|---|
| `gf180-bandgap` | `6fe62e6cb6d037b55d871792e4b7b47e4344fb2a` | `@6fe62e6` |
| `gf180-opamp` | `687c03b3aca2c41f2aa591595574f702c3e1ec2e` | `@687c03b` |

Both pins date from 2026-10-17. Both siblings are schematic level: no measured
silicon exists for either, and no sibling number below is a measurement of a
chip. Where a sibling quotes a simulated figure, it stays a simulated figure
here.

## 1. What this array needs from the pair

The array's boundary input is a 20 uA reference current (18 to 22 uA,
[`target-spec.md`](target-spec.md) section 1), mirrored 100:1. The adopted
chain (DR-0004, DR-0005) is: bandgap voltage, then a V-to-I bias loop built on
the opamp, then the mirror. This repo has no bias schematic yet, so every
"needs" cell below states what the chain would have to tolerate, not a
requirement derived from a design.

## 2. Interface table

Status values: `shown` (the pin documents it and it fits), `open` (not
documented in the pin, or documented but not benched for this use), `conflict`
(the pinned figures do not fit as stated). `shown` means shown at the
sibling's own conditions, which are cited, not shown in this repo's chain.

| ID | Item | What this array needs | What the pin shows | Source | Status |
|---|---|---|---|---|---|
| I1 | Bandgap output value | A reference voltage near 1.2 V into the bias loop; the 20 uA mirror input sets the loop resistor, so a voltage error is a gain error on full scale | Ratified target 1.20 V +/-2 % untrimmed (3 sigma, mismatch Monte Carlo N>=300 plus process corners, -40 to 125 C), i.e. a window of 1.176 to 1.224 V. A separate corner-only leg reads 1.18142 to 1.20185 V over 81 points (record `20260803-024632-294fb1d`) | `README.md`, `design/bandgap_operating_point.md` @6fe62e6 | shown |
| I2 | Bandgap load | Gate of an opamp input device, or a resistor divider; DC load not yet known | Load row is `TBD`, pending output-stage design: either a maximum DC load plus load regulation, or "unbuffered, high-Z load only". No load-regulation bench exists. Every PSRR and noise bench ran unloaded | `README.md` target table; `spec/tbd-row-evidence.md` @6fe62e6 | open |
| I3 | Bandgap pins | At minimum a reference output; whether an enable or startup control is needed is not decided | `bandgap_top` exposes `vdd`, `vss`, `vref` only | `design/bandgap_operating_point.md` section 5 @6fe62e6 | shown |
| I4 | Supply range | 2.97 to 3.63 V, 3.3 V devices (DR-0002) | Bandgap: 3.3 V +/-10 %. Opamp: 3.3 V +/-10 %, 3.3 V devices. Both 5 V stretch rows are not opened | `README.md` @6fe62e6; `spec/target-spec.md` section 1 @687c03b | shown |
| I5 | Bandgap quiescent current | Counted in the power budget (R12) | Ratified target below 50 uA; simulated worst corner 34.01 uA at ff / 125 C / 3.63 V (after the issue #61 co-scaling) | `design/bandgap_operating_point.md` section 6 @6fe62e6 | shown |
| I6 | Bandgap PSRR | No code-dependent requirement exists (R14); supply ripple from a 100 MS/s decoder on the same rail is not quantified | Ratified target above 60 dB from DC to 1 kHz, stretch above 30 dB at 1 MHz, load condition `TBD`. The newest schematic record (`sim/psrr-dc/records/20260816-145206-1ca1c95`) shows 77.61 / 77.40 / 28.96 dB worst at 1 Hz / 1 kHz / 1 MHz, unloaded, against an earlier DUT revision, from a dirty tree; the sibling's own packet labels it HISTORICAL | `spec/tbd-row-evidence.md` @6fe62e6 | open |
| I7 | Bandgap noise | Low-frequency noise on the reference is a noise term on full-scale current; no rating exists (R14) | Row says "not yet quantified"; threshold `TBD`. The recorded 0.1 to 10 Hz bench values (record `20260910-060222-a6f8b96`) are against an earlier DUT, unloaded, and their magnitude (thousands of uV rms) looks too large to be a physical bandgap figure; no bench review was done here, so this repo does not use them | `README.md`; `spec/tbd-row-evidence.md` @6fe62e6 | open |
| I8 | Opamp pins | A differential input pair and one output into a mirror gate, plus a bias pin | Pins `vdd vss vinp vinn vout ibias`. `ibias` takes an **externally supplied 10 uA reference**; the opamp does not make its own | `design/README.md`; `design/opamp_sizing.md` @687c03b | shown |
| I9 | Opamp bias current | A 10 uA source for `ibias`, on top of the 20 uA array reference | 10 uA external, quiescent about 80.7 uA total at typical; worst simulated power 310.98 uW at FF / -40 C / 3.63 V. Neither DR-0004 nor DR-0005 accounts for the 10 uA source or where it comes from | `design/opamp_sizing.md` sections 6, 7; `spec/target-spec.md` section 2 @687c03b | open |
| I10 | Opamp input common-mode range | The loop's inputs sit at the bandgap voltage, nominally 1.2 V | Proposed (not ratified) bound 1.20 V <= VCM <= 2.70 V at all 45 PVT points. Measured intersection is 1.185 to 2.705 V; low edge set by SS / -40 C / 2.97 V (tail headroom); smallest device margin at 1.20 V is +11.1 mV. Follower-biased test, systematic only, mismatch not covered | `spec/decision-records/0005-input-common-mode-range-row.md` @687c03b | conflict |
| I11 | Opamp offset | Offset on the loop becomes a reference error | Worst `abs(mean) + 3 sigma` 15.458 mV (mismatch Monte Carlo, N=300 per point, 45-point grid); no offset bound is ratified (row is `TBD`). 15.458 mV on 1.2 V is 1.29 % | `spec/target-spec.md` section 2 @687c03b | shown |
| I12 | Opamp output drive | Output must reach the mirror gate voltage that gives 20 uA, and settle a capacitive gate | Output swing target at least 2.3 Vpp (ratified as target); worst simulated 2.46 Vpp at SS / 125 C / 2.97 V into the sibling's own 2 pF load. The gate voltage the bias loop needs is a bias-schematic result that does not exist | `spec/target-spec.md` section 2 @687c03b | open |
| I13 | Opamp noise | Noise on the loop is noise on full-scale current; no rating exists (R14) | Row `TBD`, candidate bands only: highest 62.90 uV rms over 100 Hz to 1 MHz at SS / 125 C / 3.63 V (record `20261010-163507-0127eb7`); no ratified band or bound | `spec/target-spec.md` section 2 @687c03b | open |
| I14 | Opamp PSRR | The loop is a supply path into the cell array bias line | Proposed (not ratified) PSRR+ and PSRR- each at least 60 dB at the DC plateau and 1 kHz, 50 dB at 10 kHz, input-referred, one rail at a time | `spec/target-spec.md` section 2; `spec/decision-records/0006-cmrr-psrr-bounds.md` @687c03b | open |
| I15 | Opamp stability in a V-to-I loop | Loop stable with a gate load, not the sibling's 2 pF unity-gain test | Phase margin worst 71.99 deg, GBW worst 11.91 MHz, into 2 pF, unity-gain bench, 45 points. The V-to-I loop gain and load differ and are not benched | `README.md`; `spec/target-spec.md` section 2 @687c03b | open |

## 3. Findings

1. **I10 is a conflict.** The bandgap's untrimmed 3 sigma window reaches
   1.176 V, and its corner-only worst point is 1.18142 V. The opamp's measured
   common-mode intersection starts at 1.185 V, with only +11.1 mV of margin at
   1.20 V, and its proposed bound is 1.20 V. The two ranges overlap but neither
   contains the other. Whether the bandgap's low points and the opamp's low
   edge occur at the same process, temperature and supply is not shown in
   either pin (the bandgap minimum is at 125 C on `res_ff` / `bjt_ss` corners;
   the opamp edge is at SS / -40 C / 2.97 V), so a joint failure is neither
   shown nor excluded. DR-0005's statement that common-mode range is "not
   verified" is therefore too mild: the pinned figures already put the low end
   of the reference window outside the opamp's proposed bound.
2. **I9 is a missing item.** The opamp needs a 10 uA external bias that neither
   adoption record mentions. The bias loop would need a second current source
   before it can make the first.
3. **I2, I6, I7, I12, I13, I14, I15 are open** and are listed so the R14 items
   (noise, PSRR, reference loading, common-mode and output drive) each have a
   source or the words "not documented in pin". None is resolved here.
4. **Nothing in this table is a measurement of this array's bias chain.** The
   chain does not exist as a schematic.

## 4. What the table supports

- Adoption of `gf180-bandgap` and `gf180-opamp` stays **proposed**. The table
  supports "both siblings are on the same PDK, flavor and supply range, and
  their documented reference error (+/-2 %) and opamp offset (about 1.3 %) are
  gain errors on full scale, inside the +/-10 % full-scale row". It does not support "the opamp can bias from the bandgap
  output", which I10 contradicts at the stated figures.
- The compatible claim rests on the siblings' simulated figures, which are
  schematic level with no silicon, and on two sibling target sets that are
  themselves only partly ratified.
- What would change the picture (not authorized here): a bias-loop schematic
  with a joint bandgap and opamp corner run, a bandgap load-regulation bench,
  and a decision from the bandgap tracker on its load row.
