# DR-0003 gradient review and sensitivity plan

- **Status**: PROPOSED, increment B of issue #2 (`Part of #2`). Ratifies nothing.
  No numeric row of [`target-spec.md`](target-spec.md) is changed and no
  simulation is run for this document.
- **Date drafted**: 2026-10-20
- **Reviewer**: none yet (see `spec/reviews/0001-engineering-and-market.md`,
  increment D). This is the Builder's proposal, not a reviewed conclusion.
- **Every cell of section 3 is unrun.** The matrix is a plan. Running any part
  of it needs separate authorization and is bounded by the caps in the
  validation plan (increment D).

## 1. What the 0.50 % and 0.20 % gradients are

[DR-0003](decision-records/0003-gradient-amplitude-assumption.md) uses a
linear gradient of 0.50 % and a quadratic gradient of 0.20 % peak-to-peak
across the unary array. Reviewed independently here:

- They are **identified test scenarios**, selected so a raster switching
  sequence fails and a point-symmetric one passes. They are **not measured**
  from the gf180mcu process and no process data was used to choose them.
- That they separate the sequences shows only that the model can tell the
  sequences apart. It is **not validation of a real process distribution**.
  A real gradient may be smaller (the sequence matters less) or larger or
  differently shaped (the sequence may not be enough).
- The PDK models carry per-instance random mismatch only (`sm141064.spice`,
  `target-spec.md` section 4). They have no spatial term, so the PDK cannot
  supply a gradient. A nominal layout extraction of the array also cannot: it
  reports the drawn geometry, not how oxide thickness, doping or stress vary
  across a die or wafer.
- The 99.92 % result stays what `target-spec.md` says it is: an
  **assumed-model yield** (seed 20261017, 10,000 samples per scenario, the
  assumed gradient above, the current-source device alone for sigma_u). It is
  not a demonstrated chip yield, not a full-array SPICE Monte Carlo, and not
  evidence of achieved silicon performance.

## 2. Axes and fixed points

Fixed at the existing model unless a row below varies it: 10 bit, U = 6 / B = 4,
8 x 8 unary grid, inout-pairs sequence, sigma_u total 0.75 %, gradient acting on
the unary sites only, endpoint-corrected INL, yield criterion 99.7 % within
0.5 LSB. The one-corner SPICE probe stays what it is (one corner, its own
simulator version and model bin, see `sizing/instance-independence-probe.md`)
and the unit-cell Monte Carlo campaign stays **unrun**.

## 3. Sensitivity matrix (proposed, not run)

| ID | Axis | Variation | Question | Evidence that would support a process or yield reading | Stays unavailable |
|---|---|---|---|---|---|
| G1 | Gradient amplitude | linear and quadratic scaled by 0.25x, 0.5x, 1x, 2x, 4x of the DR-0003 values | At what amplitude does each sequence cross 99.7 %? Is the break-even amplitude a plausible one? | Gradient amplitudes from a source about this process (foundry statement, published matching study on the same node, or measured test structures) | gf180mcu spatial-gradient data: none found in the PDK; a break-even amplitude can be reported but not judged plausible |
| G2 | Gradient direction | linear direction fixed at 0, 45 and 90 degrees against the random direction of the model | Is the random-direction average hiding a worst-case angle for a given sequence or array aspect? | None needed to answer the model question; a process reading needs the layout-relative orientation of the real gradient | Orientation of the process gradient relative to the die and the array |
| G3 | Gradient shape | linear, quadratic (bowl and saddle), a radial (stress-like) term, an edge-rolloff term | Do the sequences that cancel linear and quadratic terms survive other shapes? | A measured or published profile shape for this process | Which shapes occur in gf180mcu; the radial and edge terms are placeholders |
| G4 | Gradient on the binary block | extend the gradient to the 64th site, the dummies and the reference branch | Does ignoring the binary block's location bias the result? | Placement from the array generator | Final placement of the binary block and reference |
| M1 | Random mismatch | sigma_u at 0.25, 0.40, 0.50, 0.75, 1.00 % (already tabulated), plus 1.25 and 1.50 % | How much margin does sigma_u have before random mismatch alone fails? | The unit-cell Monte Carlo (unrun) giving the simulated sigma against the analytic one | Simulated unit-cell sigma and its dependence on the W/L bin actually used |
| M2 | Spatial correlation of random mismatch | add a distance-dependent term (Pelgrom form, S4 in `requirements.md` is not retrieved) | Does correlation between neighbours change the gradient-like part of the error? | The PDK or foundry correlation length for this process | Correlation length: the PDK draws instances independently |
| O1 | Switch contribution | add switch-device mismatch and charge-injection error to sigma_u, in quadrature, at 0 to 0.56 % (the budget left after the 0.50 % source) | Is the 0.56 % left over enough for switch, cascode and routing together? | Schematic-level simulation of the switch cell (unrun) | Switch sizing; no schematic exists |
| O2 | Cascode contribution | add cascode-device mismatch at 0 to 0.3 % | Same question for the cascode | Schematic-level simulation of the cascoded cell (unrun) | Cascode sizing and its gain contribution |
| O3 | Routing and bias-line resistance | systematic current error from IR drop along the bias line across 1023 cells, modelled as a linear then a quadratic term of 0.05 to 0.5 % | How large can bias-line drop be before it acts as an extra gradient that the sequence must cancel? | Post-layout resistance extraction of the real bias route (needs the array generator) | Routing resistance: no routing exists; extraction at array scale is itself an open `klt` question |
| P1 | Placement | 8 x 8 as modelled, a 16 x 4 grid, one and two dummy rings, point-symmetric versus line-symmetric | Do aspect ratio and dummies change the gradient seen by the active cells? | Layout from the array generator | Whether `klt` can generate and extract each arrangement |
| P2 | Switching sequence | raster, centroid-pairs, inout-pairs (modelled), plus a hierarchical symmetric order and a randomized-within-pairs order | Is inout-pairs the best choice or only the best of three? Does a randomized order trade INL for spurious tones? | Dynamic simulation of the decoder and glitch behaviour (unrun) | SFDR consequence of each sequence; the model is static INL only |
| Y1 | Yield interpretation | a yield figure per scenario above, reported with its scenario | Which of these may be called process yield? | All of: gradient data about this process, simulated unit-cell sigma, extracted layout parasitics, and silicon or a foundry-qualified model | Process yield stays unavailable until those exist; until then every yield is an assumed-model yield and is labelled so |

## 4. Interpretation rules for any future run

- Report each result with its scenario ID, the seed, the sample count and the
  gradient assumptions in the same table row, so a number never travels without
  its model (`CLAUDE.md`).
- A result is called a **model output** (assumed-model yield). It is never
  called measured, and never process yield, while the Y1 conditions are unmet.
- A sequence is recommended only if it passes across G1 to G3 at the amplitudes
  the reviewer accepts, not only at the DR-0003 values.
- A row that cannot be run (missing input in the last column) stays listed as
  unavailable and is not filled by an assumption without a decision record.

## 5. Proposed change to DR-0003

A proposed revision note is added to DR-0003; its `Status` stays `proposed`.
The note restates the gradients as identified test scenarios and points here.
