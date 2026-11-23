# Roadmap

A 10-bit segmented current-steering DAC on the gf180mcu open PDK, built to
test array generation, matched layout and extraction in
[klayout-tools](https://github.com/2AMLogic/klayout-tools) (`klt`).

Status as of 2026-11-21, `main` @ `ff16f23`. The verdict of record is
[`manifests/gf180-current-dac.signoff.json`](manifests/gf180-current-dac.signoff.json);
where this file and that record disagree, the record wins.

## Where it stands

`klt signoff` (0.9.0) grades **15 of 22** T1 items met, tier `None`, against
[`manifests/design-evidence-tiers.md`](manifests/design-evidence-tiers.md).
Tracker #6 still shows the 2026-10-17 state; the signoff record supersedes it.

| Item | Analog (array, switches, drivers, bias) | Digital (decoder, retiming) |
|---|---|---|
| 1 Design sources | met: `design/gen_analog.py`, `design/analog/` (PR #39) | met: `rtl/`, `synth/out/` (PR #41) |
| 2 Layout | met: `layout/gen_array.py`, routed and pinned, 72 pins (PRs #42, #52) | met: `layout/pnr/` (PR #43) |
| 3 DRC | met: clean (PR #44) | met: clean (PR #48) |
| 4 LVS | met: match, 133 dummies both sides (PR #53) | met: match (PR #49) |
| 5 Corners vs ratified spec | unmet, no evidence | unmet, no evidence |
| 6 Monte Carlo | unmet, no evidence | unmet, no evidence |
| 7 Post-layout | unmet, no evidence | met: SDF-annotated run cited (`verification/functional/`, #140) |
| 8 Characterization report | unmet, no evidence | unmet, no evidence |
| 9 Testbenches shipped | met: `evidence/item9.json` (PR #56) | met (same record) |
| 10 Repo hygiene | met: `evidence/item10.json` (PR #40) | met (same record) |
| 11 Power delivery | met: `verification/erc/` (PR #54) | met (PR #54) |

What the met items do not say, in the repo's own words:

- **The spec is proposed, not ratified.** All seven decision records read
  `proposed`; items 1 to 4 were built against proposed rows (DR-0007).
- **No linearity, SFDR or timing number is claimed.** The 99.92 % yield is an
  assumed-model yield (`spec/sizing/size.py`, gradient assumed in DR-0003).
- **The schematic is not sized against the spec.** DR-0006 lists the cascode
  and switch sizes as assumed, not sized for the 12.8 Mohm and 283 fF rows.
- **Digital timing is constrained but provisional.** Against DR-0008's
  proposed I/O budget (3.0 ns in / 3.0 ns out), `layout/pnr/dac_digital.report.json`
  reports `timing_status: constrained` at every corner, and the standalone
  five-corner run is committed (`verification/sta/`, all corners positive) —
  but DR-0008 is `proposed` with assumed figures, so no slack is claimed
  against a ratified row and item 5 stays uncited.
- **The cocotb decoder suite exists** (`verification/functional/`, run on the
  RTL, the synthesized netlist and the SDF-annotated as-built netlist; the
  plain-Verilog bench in `verification/rtl/` remains the item-1 sanity check).
- **Analog parasitic extraction is only a probe, and no analog post-layout
  simulation exists**: the digital partition has a SPEF (extracted for the
  item-7 annotated run, [`verification/sta/`](verification/sta/)); the analog
  `klt pex` probe on the array is complete (`verification/pex/`: 20,184
  resistors, 2,586 ground and 8,683 coupling capacitors) but its netlist has
  not been simulated, and the two partitions are separate
  streams with no pad ring and no bias loop (DR-0006: `iref` is an ideal source).

## Now

Can start today; each is one PR.

1. **Review PR #29 and post both key reviews** (#22). PR #29 adds
   `spec/ratification-packet.md` and has waited since 2026-10-25. Done when:
   it carries an EE-key and a market-key review from sessions that authored
   neither the PR nor the design, and #2 points at it. Agents do not ratify.
2. **Done — decoder functional suite through `klt functional-verification`.** Port
   the exhaustive 1024-code check to cocotb and run it on the RTL and the
   synthesized netlist. Done when: the suite and its JSON report are committed
   under `verification/` (done: three requests, 4/4 each). Prerequisite for digital items 5 and 7.
3. **Done — parasitic extraction probe of the analog array.** Run
   `klt extract --parasitics` once on `layout/gf180-current-dac-analog.gds`.
   Done when: `verification/pex/README.md` records the command, run time and
   element counts with the output or its hash, or the failure is filed as a
   generic klayout-tools issue and linked (done: see `verification/pex/README.md`). No simulation; the analog post-layout simulation is still outstanding.
4. **Propose the digital I/O timing budget as a decision record.** The update
   rate row requires timing to be met at the clock, but no input or output
   delay exists to check it against. Done when: a `proposed` record states the
   clock and the input and output delays at the partition boundary, each with
   its source or "assumed, no source", is indexed in `spec/README.md`, and
   `spec/check_spec.py` passes. No issue yet.
5. **Correct stale tool and bench wording.** `verification/erc/README.md` and
   `layout/toolchain.json` call klayout-tools 0.8.0 the pin CI grades with (it
   is 0.9.0); the root README's layout block says `spec/` holds a ratified
   spec and `verification/` cocotb benches. Done when: each statement matches
   `main` and `python3 scripts/check_ci.py` passes. No issue yet.

## Next

- **Cite the digital timing evidence for item 5.** Multi-corner `klt sta` on
  the routed decoder is done (`verification/sta/`: five 3.3 V corners, all
  `constrained`, positive setup/hold slack against DR-0008's proposed
  budget). Citing it needs #2: the checklist requires a ratified spec, and
  `klt signoff` would grade the unratified case `met` today (the probe is
  recorded in `verification/sta/README.md`).
- **Item 6 (digital) "not applicable" statement.** Done when: a committed
  statement accounts for every digital spec row and `klt signoff` reports
  `not_applicable`. The checklist allows this only on a ratified spec: needs #2.

## Blocked and waiting

- **Spec ratification (#2, `loom:operator`).** Order: both key reviews on
  PR #29 (#22), then the operator ratifies DR-0001. Until then items 5 to 8
  cannot be met: verdicts against a draft spec are provisional (signoff record).
- **Every analog simulation beyond the smoke run.**
  [`spec/validation-plan.md`](spec/validation-plan.md) marks V1 to V8
  `unrun, needs separate authorization`, including the reading-only V2 and V6:
  the unit-cell Monte Carlo (V1), the model sensitivity runs (V3 to V5) and
  any schematic-level simulation. Waiting on the operator authorizing items
  of that plan, within its caps.
- **Analog items 5 to 8**, in order once both of the above clear: design
  testbenches for the unit cell and array; cascode and switch sizing against
  the 12.8 Mohm and 283 fF rows (replacing DR-0006's assumed values); corner
  matrix (5); Monte Carlo with `klt yield` (6); `klt pex` re-simulation (7);
  characterization report (8).
- **Digital item 8** (Fmax, area, power across corners): the STA report and #2.

Outside Now 1 to 5 the repo has nothing dispatchable: #2 is operator-held, #6
is a tracker, #22 is in progress, #64 is an automated digest.

## Later (each with the question to answer first)

- **Bias loop from the pinned siblings** (`gf180-bandgap`, `gf180-opamp`;
  DR-0004, DR-0005). First: which decision record resolves the I10 conflict
  in [`spec/interface-evidence.md`](spec/interface-evidence.md) (opamp input
  common-mode range against the bandgap voltage)?
- **One merged top-level stream.** First: which edge of the decoder faces the
  driver band (a placeholder in `layout/pnr/README.md`), and is a pad ring in
  scope?
- **Gradient evidence.** First: does any source about this process give
  gradient amplitude and shape (sensitivity rows G1 to G3)? The PDK has none.
- **Matched routing.** First: do the asymmetries disclosed in
  `layout/README.md` show up in extracted results? Needs Now 3 and item 7.
- **Dynamic performance (SFDR).** First: what decoder and glitch model does
  the bench use? The sizing model is static INL only (sensitivity row P2).
- **Shuttle seat and measured silicon** (README ladder). First: is the
  post-layout re-verification rung closed?

## Not planned

- The reference current source and any reconstruction filter (README scope).
- 5 V devices (DR-0002, proposed).
- Sizing the array for 12 bits before 10 bits closes (`CLAUDE.md`).
- A separate behavioural reference model (#5, closed as not planned).
