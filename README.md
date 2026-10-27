# gf180-current-dac

A segmented current-steering digital-to-analog converter on the
[gf180mcu](https://github.com/google/gf180mcu-pdk) open PDK — an array of
matched current cells, laid out in common centroid and switched by a
thermometer-decoded control word — designed by AI agents driving
[klayout-tools](https://github.com/2AMLogic/klayout-tools), xschem + ngspice
on the analog side and cocotb + Icarus, Yosys/OpenROAD for the decoder.

**Status: just opened, specification phase.** Nothing is designed yet.

**Built agent-native.** Every specification, decision record, testbench, and
line of documentation here is produced by AI agents working from a ratified
spec and an append-only evidence trail — not human-authored work that agents
merely assisted with. Verification is the product: every claim traces to a
recorded result under PVT corners. Where the agents hit friction with the
open-source tooling — most often
[klayout-tools](https://github.com/2AMLogic/klayout-tools) — that friction is
filed as a public issue against the tool itself, so the fix benefits everyone
using gf180mcu, not just this repo.

## Why this block, on this node

A current-steering DAC is the converter whose accuracy is drawn rather than
calibrated. Static linearity comes from how well the unit current cells
match, and the residual error is mostly systematic: process and thermal
gradients across the array. Common-centroid placement and a switching
sequence that cancels those gradients are the standard answer, and both are
layout work at array scale — hundreds of identical cells, dummy rows, and
matched routing to every cell.

That makes it a direct test of what the tools can generate and check:
parameterized arrays, symmetric placement, matched interconnect, and
extraction of a large regular structure. Dynamic performance adds the
other half: the switch drivers, the output impedance of each cell, and the
timing skew of the decoder all show up in the spectrum.

## Scope

- **In scope**: the unit current-cell array (unary MSBs and binary LSBs),
  the cell switches and their drivers, the thermometer decoder and
  retiming latches, the bias of the array from a reference current, and the
  differential output.
- **Not in scope**: the reference current source itself, which is an input
  at the block boundary, and any output reconstruction filter.
- **Same-PDK siblings**: `gf180-bandgap` builds the reference this array is
  biased from and `gf180-opamp` an amplifier a bias loop may need. Adopt them
  or record why not.

## Target specification (PROPOSED — awaiting operator ratification, see issue #1)

Full table with min/typ/max, grading conditions and corners:
[`spec/target-spec.md`](spec/target-spec.md). It becomes ratified when the
operator approves [DR-0001](spec/decision-records/0001-target-spec-ratification.md);
until then each row is a proposal.

| Parameter | Target | Fallback | Stretch |
|---|---|---|---|
| Resolution | 10 bits | 8 bits | 12 bits |
| Update rate | 100 MS/s | 50 MS/s | 200 MS/s |
| Segmentation | 6 unary MSBs + 4 binary LSBs | 4 + 4 | not sized |
| INL / DNL (simulated, with mismatch) | ≤ 0.5 LSB, ≥ 99.7 % yield | ≤ 1 LSB | ≤ 0.25 LSB |
| SFDR near Nyquist (simulated, 0.45 fs tone) | ≥ 60 dBc | ≥ 50 dBc | ≥ 70 dBc |
| Full-scale output | 2 mA per output (±10 %) into 50 Ω per output | — | — |
| Supply / devices | 3.3 V devices on 3.3 V ±10 %; 5 V devices not used (DR-0002) | — | — |
| Layout | common-centroid unary array with dummies | — | — |
| Signoff | DRC + LVS clean, post-layout re-verified | — | — |

Maturity ladder: spec ratified → array sizing and switching sequence
recorded → schematic simulated across PVT and mismatch → array layout
DRC/LVS-clean → post-layout re-verification → shuttle seat → measured
silicon. **Current position: spec drafted, proposed, not ratified.**

## Repo layout

```
spec/          ratified spec + decision records
design/        current cell, switch, and bias schematics (xschem)
rtl/           thermometer decoder and retiming
sim/           testbenches + PVT and mismatch results (ngspice)
verification/  cocotb testbenches for the decoder
layout/        GDS + DRC/LVS reports, including the array generator output
measurements/  silicon characterization (empty until tape-out)
```

## Reproduce

Every committed record, with the command that regenerates or re-checks it.
Run from the repo root. `klt` is used through a throwaway environment at the
pinned version (`KLT_PIN`, currently 0.8.0, set in
[`scripts/check_signoff.sh`](scripts/check_signoff.sh)); do not rely on a
host-installed `klt`.

```
KLT="uvx --from klayout-tools==0.8.0 klt"
```

| Record | Command |
|---|---|
| Repo checks: JSON validity, harness and spec tests, spec structure, schematic generator freshness, README links | `python3 scripts/check_ci.py` (or `npm run check:ci`, which also runs the signoff freshness check) |
| Toolchain pins (ngspice, Python, PDK revision) | `python3 -m sim.harness check` |
| Smoke record [`sim/smoke/records/20261017-215406.md`](sim/smoke/records/20261017-215406.md) with its [corners](sim/smoke/records/20261017-215406-corners.json) and [Monte Carlo](sim/smoke/records/20261017-215406-mc.json.gz) reports | `$KLT sim sim/smoke/request-corners.json --format json --report-out <corners.json>` and `$KLT sim sim/smoke/request-mc.json --format json --report-out <mc.json>`. Multi-corner and Monte Carlo requests go to the batch fleet; the commands as run are in the record. Needs the PDK from [`sim/README.md`](sim/README.md) |
| Sizing model [`spec/sizing/sizing-output.md`](spec/sizing/sizing-output.md) (model results, not SPICE) | `python3 spec/sizing/size.py` (`--check` verifies the committed file) |
| Instance-independence probe [`spec/sizing/instance-independence-probe.md`](spec/sizing/instance-independence-probe.md) | Netlists in `spec/sizing/probe/`; method and substitutions are in the record. One single-process `ngspice -b` per run |
| Spec structure and tests | `python3 spec/check_spec.py` and `python3 -m unittest spec.tests.test_check_spec` |
| Analog schematics, symbols and netlists under `design/analog/` | `python3 design/gen_analog.py` (`--check` verifies); netlists via `$KLT netlist <sch> -o <spice> --rcfile design/analog/xschemrc` |
| Item 1 attestation [`evidence/item1-analog.json`](evidence/item1-analog.json) | `$KLT signoff --attest 1 --inventory design/inventory-item1-analog.json -o evidence/item1-analog.json` |
| Item 10 attestation `evidence/item10.json` | `$KLT signoff --attest 10 --inventory attest/item10.json -o evidence/item10.json`; verify with `--check evidence/item10.json` |
| Signoff verdict [`manifests/gf180-current-dac.signoff.json`](manifests/gf180-current-dac.signoff.json) | `scripts/check_signoff.sh` regrades the manifest and fails if the record is stale |

## License

Apache License 2.0 — see [LICENSE](LICENSE).
