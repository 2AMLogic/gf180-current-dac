# verification/lvs

T1 item 4 (LVS) runs, one `klt lvs` request per partition, with the klt pinned
in [`layout/toolchain.json`](../../layout/toolchain.json) (run through `uvx`;
engine `klayout` 0.30.12). Both runs were single compares, no grid.

**Neither partition is LVS clean. Both reports are `status: mismatch` and are
committed as they came out.** Nothing was edited, shrunk or waived to move a
verdict, and no manifest entry cites these reports, so item 4 stays unmet.
`klt lvs --check` exits 0 on both (the inputs still hash as recorded; that says
nothing about the verdict).

| Partition | Layout | Reference | Verdict |
|---|---|---|---|
| analog | `layout/gf180-current-dac-analog.gds`, extracted inline (gf180mcu deck, ~5 min) | `design/analog/dac_analog.spice`, `form: subckt-call` | `mismatch`, 0 of 207 nets matched |
| digital | `layout/pnr/dac_digital.gds`, extracted to `dac_digital.gate.spice` | `layout/pnr/dac_digital.asbuilt.v`, `form: gate-level-verilog` | `mismatch`, `power_connectivity` = `match` |

## Analog

The layout is placement only (`layout/README.md`: nothing wired, no pins, no
labels), so the extraction finds 5046 devices on 15340 nets and one pin against
72 reference pins and 207 nets; the top circuit and every sub-circuit report
"could not be matched". The compare cannot succeed until routing and pins
exist. Extraction at this array size finished (about 5 minutes, one core).
The `body_unverified` warnings (4845 NMOS on the synthesized `vsubs`, 201 PMOS
on anonymous wells) are listed with the claim: no substrate or well taps are
drawn.

## Digital

Reference is the P&R as-built netlist, not `dac_digital_synth.v`: the tool's
gate-level flow compares the layout against the netlist from the same
place-and-route run, and the as-built one carries the clock-tree cells the
layout has. Layout side: `klt extract --deck gf180mcu --abstract-cells
'gf180mcu_fd_sc_mcu7t5v0__*' --def-net-names --def-pins <DEF> --rename-declared-pins
--pdk gf180mcuD` on the committed stream, with the DEF from `layout/pnr/run.sh
--check` (scratch, not committed).

Signal compare: 13 errors, all one defect. Net `clknet_3_5__leaf_clk` is split
in the extracted layout: its buffer, `clkload4` and three flops (`_20_`, `_24_`,
`_28_`) are on one net, flops `_04_` and `_49_` sit on a separate net with
nothing else. The same split appears when extracting without `--def-net-names`.
Whether it is an open in the routed clock leaf or an extraction-deck limit is
not established here. Also reported: `net.split` on `VDD` and `VSS` (supply
islands). Power connectivity: `match`, 725 instances, no findings, but
`expected_nets` was not declared, so it checks only what the library pins imply.
