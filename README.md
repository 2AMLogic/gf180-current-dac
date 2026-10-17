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

## License

Apache License 2.0 — see [LICENSE](LICENSE).
