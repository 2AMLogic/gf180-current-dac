# Target specification

- **Status**: PROPOSED. Becomes ratified only when the operator approves
  [DR-0001](decision-records/0001-target-spec-ratification.md). Until then every
  row is a proposal, and the README says so.
- **Date drafted**: 2026-10-17 (issue #2)
- **Evidence class**: every number below is a requirement, a budget, or the
  output of the sizing model (`spec/sizing/size.py`). **Nothing here is
  measured, and nothing here is a SPICE result** except the one probe in
  `spec/sizing/instance-independence-probe.md`, which is a single-corner
  simulation and says so.
- **PDK**: gf180mcuD, revision pinned in `sim/pdk.json`
  (`f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7`).

## 1. Parameter table

Corner set `PVT` means: process `tt/ff/ss/fs/sf` (PDK sections
`typical/ff/ss/fs/sf`), supply 2.97 to 3.63 V (3.3 V -/+10 %), temperature -40
to +125 C, plus local mismatch where the row says so. The README target tier
is the graded tier; fallback and stretch values are in section 2.

| Parameter | Min | Typ | Max | Grading condition | Corners |
|---|---|---|---|---|---|
| Resolution | 10 bit | 10 bit | 10 bit | monotonic transfer over all 1024 codes | n/a (architecture) |
| Update rate | 100 MS/s | 100 MS/s | 100 MS/s | decoder, retiming latches and cell switches meet timing at this clock | PVT |
| Segmentation | 6 unary + 4 binary | 6 + 4 | 6 + 4 | 63 unary elements of 16 LSB, binary bits of 1/2/4/8 LSB (section 3) | n/a (architecture) |
| INL, endpoint-corrected | -0.5 LSB | 0 | +0.5 LSB | sigma-yield: >= 99.7 % of Monte Carlo samples have max abs INL <= 0.5 LSB (section 4) | PVT x mismatch x gradient |
| DNL | -0.5 LSB | 0 | +0.5 LSB | same samples, max abs DNL <= 0.5 LSB; model p99.7 is 0.20 LSB at the sizing point | PVT x mismatch x gradient |
| SFDR | 60 dBc | n/a | n/a | tone at 45 MHz (0.45 fs, coherent bin), amplitude 0 dBFS and -6 dBFS, 100 MS/s; also graded at 10 MHz; differential, into the load below | PVT, mismatch on |
| Full-scale current | 1.8 mA | 2.0 mA | 2.2 mA | per output, all unary and binary cells on, calibrated reference current | PVT (the +/-10 % includes untrimmed reference error) |
| Output load | 50 ohm | 50 ohm | 50 ohm | resistor from each output to the rail opposite the cell polarity; differential full scale +/-100 mV across 2 x 50 ohm at typ | n/a |
| Output compliance | rail -0.15 V | rail -0.1 V | rail | cell stack stays saturated with the output node anywhere in this range; at 2.97 V the node sits at 2.82 V at the low end | PVT |
| Unit output impedance (DC) | 12.8 Mohm | n/a | n/a | one LSB cell, all cells on gives >= 12.5 kohm total; derived from SFDR (section 5) | PVT |
| Code-dependent output capacitance | n/a | n/a | 283 fF | per output, the part that changes with code, at 45 MHz (section 5) | PVT |
| Unit-cell source mismatch | n/a | n/a | 0.50 % sigma | current-source device alone, relative drain-current sigma from the PDK mismatch model (section 4) | typical, 27 C (mismatch is corner-independent in the PDK terms) |
| Unit-cell gate area (Leff x Weff) | 26.5 um^2 (nfet_03v3) or 22.4 um^2 (pfet_03v3) | n/a | n/a | at Vov = 0.4 V; larger Vov may trade down per the sizing table | n/a |
| Supply and devices | 2.97 V | 3.3 V | 3.63 V | 3.3 V devices only (nfet_03v3 / pfet_03v3); 5 V devices not used (DR-0002) | PVT |
| Power | n/a | 25 mW | 30 mW | budget at full scale, 100 MS/s, whole block excluding the reference input; output stage alone is 6.6 mW at typ (2 mA x 3.3 V); remainder is bias, drivers and decoder | typ at tt/27 C/3.3 V; max at ff/125 C/3.63 V |
| Reference current input | 18 uA | 20 uA | 22 uA | boundary input, mirrored 100:1 into the array; the reference is an input here (README scope) | PVT |
| Switching sequence | n/a | inout-pairs | n/a | section 6 | n/a |
| Signoff | DRC + LVS clean, post-layout re-verified | n/a | n/a | gate for the layout issues, not a result | PVT for the re-verification |

Rows marked `n/a` for min or max are one-sided requirements. Power and
reference-current numbers are **budgets proposed here, not derived**: no
schematic exists yet. They are open to revision only through a superseding
decision record after ratification.

## 2. Tiers (README reconciliation)

| Parameter | Target | Fallback | Stretch |
|---|---|---|---|
| Resolution | 10 bit | 8 bit | 12 bit |
| Update rate | 100 MS/s | 50 MS/s | 200 MS/s |
| INL / DNL (simulated, with mismatch) | <= 0.5 LSB | <= 1 LSB | <= 0.25 LSB |
| SFDR near Nyquist (simulated) | >= 60 dBc | >= 50 dBc | >= 70 dBc |
| Segmentation | 6 unary + 4 binary | 4 unary + 4 binary | not segmented |

The stretch tier appears only in the analytic tables of the sizing output. It
is not sized, and 12-bit matching does not drive the array size until 10 bits
closes.

## 3. Segmentation

Unary part: the U most significant bits drive 2^U - 1 equal elements, each
16 LSB (2^B unit cells). Binary part: B bits of 1, 2, 4, 8 unit cells. Total
unit cells are 2^N - 1 = 1023 for every split. What the split changes
(`spec/sizing/sizing-output.md`, section 2):

| U / B | Decoder outputs | Largest single step | sigma(DNL) at the major carry, sigma_u = 1 % |
|---|---|---|---|
| 4 / 6 | 15 | 64 LSB | 0.113 LSB |
| 5 / 5 | 31 | 32 LSB | 0.079 LSB |
| **6 / 4** | **63** | **16 LSB** | **0.056 LSB** |
| 7 / 3 | 127 | 8 LSB | 0.039 LSB |
| 8 / 2 | 255 | 4 LSB | 0.026 LSB |

**Chosen 6 + 4.** Area: the unit-cell count is the same for every split, so
the difference is decoder and driver area: 6 + 4 needs 63 switch pairs and
drivers for the unary part and 4 for the binary part. Decoder: a 6-to-63
thermometer decoder with retiming latches, against 255 outputs for 8 + 2.
Glitch: the largest single step is 16 LSB, half the 32 LSB of 5 + 5, and the
step falls as U rises while the decoder grows as 2^U; 6 + 4 is where the
major-carry sigma(DNL) is 0.056 LSB (about a ninth of the 0.5 LSB limit at
sigma_u = 1 %) with a decoder that stays small. 7 + 3 buys little more DNL
margin because INL, not DNL, binds (section 4). The glitch column is a proxy
(largest LSB step per control change), not a simulated glitch energy; glitch
energy comes from transient simulation later and is not rated in this spec.

## 4. Mismatch method

**Model the PDK provides.** `sm141064.spice` (PDK revision above) defines,
for each of `nfet_03v3`, `pfet_03v3`, `nfet_06v0`, `pfet_06v0`, a per-instance
Gaussian draw of threshold shift and mobility scale:

    delvto = mis_vth * sw_stat_mismatch        mis_vth = agauss(0, var_vth, 1)
    mulu0  = 1 - mis_k * sw_stat_mismatch      mis_k   = agauss(0, var_k, 1)
    var_vth = 0.7071 * par_vth * 1e-6 / sqrt(Leff * Weff)
    var_k   = 0.7071 * par_k   * 1e-6 / sqrt(Leff * Weff)
    Leff = L - par_l,   Weff = par * (W - par_w)

That is Pelgrom area scaling with the PDK's own coefficients: sigma(Vth) per
device is 0.7071 * A_VT / sqrt(area), so a pair difference is A_VT / sqrt(area).
Coefficients (bin 1 of each flavor): A_VT = 7.148 / 6.660 / 11.55 / 10.51
mV*um and A_K = 0.7008 / 0.2833 / 0 / 0.517 %*um for nfet_03v3 / pfet_03v3 /
nfet_06v0 / pfet_06v0. The 5 V devices carry the same hooks; there is no gap
that needs an assumption record for device mismatch itself.

**What was traced, and what was not.**

- Traced: the formulas above, read from `sm141064.spice`; the switch
  semantics (`design.ngspice`: `sw_stat_mismatch=1`, `sw_stat_global=0` gives
  local mismatch only, which is what `sim/smoke/cs_tb_mc.spice` sets).
- Traced by probe (`spec/sizing/instance-independence-probe.md`, ngspice-42,
  one corner): each subcircuit instance draws independently, and `m=N` on one
  instance does **not** average (total-current spread 1.30 % for `m=40` vs
  0.13 % for 40 instances). **Every unit cell must therefore be its own
  instance in Monte Carlo**, and the array generator must emit them that way.
- Not traced: only bin 1 of each flavor was read; other W/L bins carry their
  own coefficients and the sizing must be re-checked against the bin of the
  drawn device. The drawn W and L set which bin applies.
- Not covered by the PDK: spatial correlation. The PDK terms are
  per-instance independent, so a gradient is **not** in the PDK (below).
- ngspice-42 was the local build; the pin is ngspice-46 and a fleet runner has
  its own build (`sim/README.md`). The probe's mean and spread are not claimed
  to carry across builds.

**What the SPICE-level mismatch run will be.** Unit-cell Monte Carlo through
`klt sim` with the fleet backend, `sw_stat_mismatch=1`, `sw_stat_global=0`, at
`tt/27 C/3.3 V`, N = 500 samples per request, to check the analytic sigma of
section 4 against the simulated sigma of the unit cell. Array-level INL is
**not** a SPICE Monte Carlo of 1023 cells; it is the model of
`spec/sizing/size.py` fed by the sigma the unit-cell run reports. That
substitution is part of the method and is stated next to every linearity
number.

**Yield criterion.** Max abs INL (endpoint-corrected, over all codes) <= 0.5
LSB in >= 99.7 % of samples. Sizing model sample count: 10,000 per scenario,
seed 20261017. The model draws unit errors N(0, sigma_u) independently, builds
each unary element from 16 units and each binary bit from 2^k units (sigma
scales by sqrt of the unit count), and adds the gradient below.

**Gradient model (assumed, not from the PDK).** Linear 0.50 % and quadratic
0.20 % peak-to-peak across the unary array, direction and quadratic sign
random per sample. These amplitudes are assumptions chosen to stress the
sequence; decision record
[DR-0003](decision-records/0003-gradient-amplitude-assumption.md) records
them as such. They are replaced by extracted values when post-layout data
exists. The model's gradient acts on unary sites only (an 8 x 8 grid of
elements; the 64th site holds the binary block and is not switched).

**Result at the sizing point** (`spec/sizing/sizing-output.md`, section 3a,
sigma_u total = 0.75 %, inout-pairs sequence): yield 99.92 %, p99.7 max abs
INL 0.446 LSB, p99.7 max abs DNL 0.199 LSB. With the raster sequence the same
point yields 35.66 %: the sequence, not the mismatch, is what the gradient
punishes. The current-source device alone gets 0.50 %; the other 0.56 %
(quadrature) is left for cascode, switch and bias-line IR drop, which this
repository has not yet modelled.

**Sizing.** With sigma_I/I = sqrt((2/Vov * sigma_Vth)^2 + sigma_K^2) and
square-law gm/Id, sigma = 0.50 % needs Leff * Weff >= 26.5 um^2 for
`nfet_03v3` at Vov = 0.4 V (22.4 um^2 for `pfet_03v3`; both for other Vov in
the sizing output). Unit current is 2 mA / 1023 = 1.955 uA. Array gate area
at the nfet point is 1023 x 26.5 um^2 = 0.027 mm^2 of gate; layout area is
several times that and is not estimated here.

**Array size.** 1023 unit cells plus one filler as 32 x 32 sites (8 x 8
elements of 4 x 4 units), a dummy ring of at least one cell on all sides
(34 x 34 = 1156 cells including dummies). This is a proposal for the array
generator; the generator may change the ring depth through a decision record.

## 5. Output impedance for SFDR

First-order model (derivation in the sizing script docstring and output
section 5): per-code current I(x) = Ifs (x - eps x^2), x = code/1023,
eps = R_L / Z_T, Z_T = Z_u / 1023. Second harmonic is eps/4, so
SFDR = 20 log10(4 / eps). It is a **single-ended-equivalent** bound. A
differential output cancels the even-order term to first order; this spec does
not take credit for that, because the cancellation depends on matching the two
output halves, which is not modelled.

At R_L = 50 ohm, SFDR >= 60 dBc needs eps <= 0.004, so Z_T >= 12.5 kohm and
**Z_u >= 12.8 Mohm per unit cell** at DC. The same expression with the
code-dependent output capacitance (eps = omega * R_L * dC at 45 MHz) bounds
that capacitance at **283 fF** per output. Both are requirements on the
cell design; neither is a result.

## 6. Switching sequence and placement

- Placement: common-centroid, point-symmetric pairs on the 8 x 8 element grid.
- Sequence: **inout-pairs**: point-symmetric pairs, taken alternately from the
  innermost and outermost remaining radius, so the linear term cancels every
  two steps and the quadratic term cancels progressively.
- Checked against: the gradient model of section 4. At sigma_u = 0.75 %:
  raster 35.66 %, centroid-pairs (inside-out) 94.45 %, inout-pairs 99.92 %.
- Whether `klt` can generate and extract this arrangement is the array
  generator's question and is not answered here. If it cannot, that is a
  `2AMLogic/klayout-tools` issue worded generically.

## 7. Device, supply and topology

- 3.3 V devices and a 3.3 V -/+10 % supply (DR-0002). The 5 V devices need
  about 2.5x more gate area for the same sigma (sizing output section 4),
  need a 5 V supply the README does not offer, and the issue asks for them
  only if they help output impedance enough to justify it; with a cascode the
  3.3 V stack reaches the 12.8 Mohm requirement without that cost, to be
  confirmed in the cell schematic.
- Topology: cascoded current source with a switch above the cascode, so the
  switch drain capacitance sits behind the cascode. Required outputs:
  Z_u >= 12.8 Mohm, code-dependent C <= 283 fF per output, all at PVT.
- Cell polarity (n or p) is left to the cell schematic. Area is sized on the
  larger of the two (nfet).

## 8. Open items (not decided here)

1. Other contributors to unit-cell sigma: cascode, switch, and bias-line IR
   drop across 1023 cells.
2. Other W/L bins of the PDK mismatch coefficients.
3. Gradient amplitudes: assumed (DR-0003) until extraction exists; the
   proposed, unrun sensitivity matrix is in
   [`sensitivity-plan.md`](sensitivity-plan.md).
4. Power and reference-current budgets: no schematic yet.
5. Whether `klt` generates and extracts the common-centroid array: owned by
   the array generator issue.
6. Fleet vs local ngspice build for the unit-cell Monte Carlo.

## 9. Reproducing the numbers

    python3 spec/sizing/size.py            # rewrites spec/sizing/sizing-output.md
    python3 spec/sizing/size.py --check    # exit 1 if the file differs from a fresh run

The command is stdlib-only, seeded, single process, about one to two minutes
on one core. Every number in sections 3 to 6 is in `sizing-output.md`.
Structure and cross-references of this spec are checked by
`python3 spec/check_spec.py`.

## 10. Decision records

- [DR-0001](decision-records/0001-target-spec-ratification.md): ratification
  (Proposed; operator ratifies).
- [DR-0002](decision-records/0002-device-flavor-and-supply.md): 3.3 V devices.
- [DR-0003](decision-records/0003-gradient-amplitude-assumption.md): gradient
  amplitude is an assumption.
- [DR-0004](decision-records/0004-reference-source-gf180-bandgap.md):
  `gf180-bandgap` adopted as the reference source.
- [DR-0005](decision-records/0005-bias-loop-amplifier-gf180-opamp.md):
  `gf180-opamp` adopted for the bias loop.
