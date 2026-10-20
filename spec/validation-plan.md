# Bounded validation plan

- **Status**: PROPOSED, increment D of issue #2 (`Part of #2`). Ratifies nothing.
  No numeric row of [`target-spec.md`](target-spec.md) is changed and no
  simulation, SPICE request or fleet submission was run for this document.
- **Date drafted**: 2026-10-20
- **Reviewer**: none yet. The review record is
  [`reviews/0001-engineering-and-market.md`](reviews/0001-engineering-and-market.md)
  and its outcome is `pending`. This is the Builder's draft, not a reviewed
  conclusion.
- **Every item in section 2 is `unrun, needs separate authorization`.** The
  caps below bound what an authorization may grant; they do not grant it.

## 1. What is kept as it stands

- The sizing result (yield 99.92 % at sigma_u total 0.75 %, inout-pairs) is an
  **assumed-model yield**: seed 20261017, 10,000 samples per scenario, the
  gradient of DR-0003 (identified test scenarios, **not measured**), the
  current-source device alone for sigma_u. It is not a demonstrated chip yield,
  not a full-array SPICE Monte Carlo, and not evidence of achieved silicon
  performance.
- The one-corner probe (`sizing/instance-independence-probe.md`) stays one
  corner, ngspice-42 (the pin is ngspice-46), PDK
  `f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7`, bin 1 of each flavor, 12 runs per
  arrangement. It supports "mismatch is drawn per instance" and nothing about
  linearity.
- The unit-cell Monte Carlo campaign (`target-spec.md` section 4) stays
  **unrun**. Item V1 below is that campaign, with caps.
- No simulated number in this plan or the spec is called measured.

## 2. Validation items

Resource figures are estimates written before any run, not measurements. "Model
run" means `spec/sizing/size.py` or a variant of it (stdlib, single process,
about one to two minutes per 10,000 samples per scenario on one core, per
`target-spec.md` section 9). "Request" means one `klt sim` submission, which
goes to the batch fleet when it has more than one unit.

| ID | Question | Evidence required | Resource estimate | Caps (samples / requests / retries) | Stop condition | Status |
|---|---|---|---|---|---|---|
| V1 | Does the simulated unit-cell sigma match the analytic 0.50 % for the current-source device at the chosen W/L bin? | Unit-cell Monte Carlo, `tt/27 C/3.3 V`, `sw_stat_mismatch=1`, `sw_stat_global=0`, one instance per cell, sigma from the drain current spread, with the W/L bin and PDK revision named | 1 request of 500 samples on the fleet; minutes of fleet time (estimate) | 500 samples / 1 request / 1 retry on infrastructure failure only | Stop after the first completed request. Stop and file a gap if the batch submit fails; do not run locally as a substitute. If simulated sigma differs from analytic by more than the sample error, record it and stop; do not re-run to narrow it | unrun, needs separate authorization |
| V2 | Which other W/L bins and the 5 V flavors carry different mismatch coefficients, and does the sizing point change? | Read the coefficients from the PDK model files for the bins the drawn device could use; no simulation | Reading only; under an hour (estimate) | 0 samples / 0 requests / 0 retries | Stop when each candidate bin has a coefficient or is marked `not traced`. Do not infer an untraced bin | unrun, needs separate authorization |
| V3 | Sensitivity of yield to gradient amplitude, direction and shape (matrix rows G1 to G4) | Model runs of `size.py` variants, one result row per scenario with seed, sample count and gradient assumption | About 15 to 40 model runs (5 amplitudes x 3 sequences, plus direction and shape variants), 1 to 2 minutes each: under 2 hours on one core (estimate) | 10,000 samples per scenario / 0 SPICE requests / 0 retries (deterministic, seeded) | Stop when every G row has a result or a stated reason it cannot run. Stop early on the first scenario where inout-pairs falls below 99.7 %: report the amplitude and do not tune the scenario to rescue it | unrun, needs separate authorization |
| V4 | Is the 0.56 % left after the current source enough for switch, cascode and bias-line drop (rows O1 to O3, M1)? | Model runs with extra sigma terms added in quadrature, then schematic-level numbers once cell schematics exist | Model runs: 5 to 10, about 15 minutes (estimate). Schematic-level part: not estimable, no schematic exists | 10,000 samples per scenario / 0 requests until a schematic exists / 0 retries | Stop the model part when O1 to O3 and M1 each have a result. Stop the schematic part before it starts: it is a later issue and needs its own authorization | unrun, needs separate authorization |
| V5 | Do placement and sequence choices (rows P1, P2) change the yield, and does a randomized order cost spurious tones? | Model runs for P1 and P2 static INL; dynamic SFDR of any sequence needs a decoder and glitch model that do not exist | Static part: 5 to 10 model runs, about 15 minutes (estimate). Dynamic part: not estimable | 10,000 samples per scenario / 0 requests / 0 retries | Stop the static part when each arrangement has a result. The dynamic part is out of this plan and stays unavailable | unrun, needs separate authorization |
| V6 | Do the pinned `gf180-bandgap` and `gf180-opamp` meet the open or conflicting interface rows (I2, I6, I7, I9, I10 and I12 to I15 of `interface-evidence.md`)? | Per open row: the sibling's own documented number at the pin, or a sibling-side simulation owned by the sibling; any conflict (I10) resolved by a decision record, not by an assumption | Reading: under an hour. Any simulation belongs to a sibling issue, not this repository | 0 samples / 0 requests / 0 retries here | Stop when each open row is `shown` or marked `not documented in pin`. Do not bump the pin or edit `reuse.lock.json` under this plan | unrun, needs separate authorization |
| V7 | What would let any result be called process yield? | The Y1 conditions of `sensitivity-plan.md`: gradient data about this process, the simulated unit-cell sigma (V1), extracted layout parasitics, and silicon or a foundry-qualified model | A written list, no run | 0 samples / 0 requests / 0 retries | Stop when the list is reviewed. Until all four exist every yield stays an assumed-model yield | unrun, needs separate authorization |
| V8 | Can `klt` generate and extract the common-centroid array with dummies and matched routing at this scale? | Owned by the array-generator issue; if it cannot, a generic `2AMLogic/klayout-tools` issue with no design detail | Not part of this plan | 0 samples / 0 requests / 0 retries | Out of scope here; listed so it is not mistaken for covered | unrun, needs separate authorization |

## 3. Plan-wide caps and stop rules

- **Total ceiling if everything above were authorized**: 500 SPICE samples in
  1 fleet request (V1), and model runs only elsewhere. Any figure above these
  needs a new authorization, not an extension of this one.
- **No local fallback for a fleet job.** If the V1 submit fails, report the
  error and stop. The host rules forbid running a grid locally as a substitute.
- **No scenario shopping.** A scenario is chosen before it is run and written in
  the plan. Choosing gradients that make one sequence fail and another pass does
  not validate a process distribution (DR-0003).
- **Report with the model.** Every result carries its scenario ID, seed, sample
  count, gradient assumption, simulator and version, PDK revision and W/L bin in
  the same row.
- **Order**: V2 and V6 (reading only) before V1; V1 before any V3 to V5 result
  is interpreted against a simulated sigma; V3 to V5 do not need V1 to run but
  are labelled with the analytic sigma until V1 exists.

## 4. Review record

[`reviews/0001-engineering-and-market.md`](reviews/0001-engineering-and-market.md)
holds the reviewer name, date, scope and outcome. It is a template with outcome
`pending`. The engineering and marketing review is done only when it names a
human reviewer and an outcome other than `pending`. A Builder cannot fill or
self-approve it. Ratification of DR-0001 stays the operator's separate act and
is blocked until then.
