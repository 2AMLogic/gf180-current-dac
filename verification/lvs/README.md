# verification/lvs

T1 item 4 (LVS) runs, one `klt lvs` request per partition, with the klt pinned
in [`layout/toolchain.json`](../../layout/toolchain.json) (run through `uvx`;
engine `klayout` 0.30.12). Both runs were single compares, no grid.

**The digital partition is LVS clean (`status: match`); the analog partition
is not (`status: mismatch`).** Both reports are committed as they came out.
Nothing was edited, shrunk or waived to move a verdict, and no manifest entry
cites these reports yet, so item 4 stays unmet until the analog half closes.
`klt lvs --check` exits 0 on both (run it from this directory: the reference
path is relative to the report).

| Partition | Layout | Reference | Verdict |
|---|---|---|---|
| analog | `layout/gf180-current-dac-analog.gds`, extracted inline (gf180mcu deck, ~5 min) | `design/analog/dac_analog.spice`, `form: subckt-call` | `mismatch`, 0 of 207 nets matched |
| digital | `layout/pnr/dac_digital.gds`, extracted to `dac_digital.gate.spice` | `layout/pnr/dac_digital.asbuilt.v`, `form: gate-level-verilog` | `match`, 0 errors, `power_connectivity` = `match` |

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

Signal compare: `status: match`, 0 errors, 344 nets matched (189 layout and 182
reference nets as counted by the tool). Two warnings: `topology.power_only_pruned` (fill, endcap and
tap cells, which the gate-level Verilog never carries) and
`topology.top_level_pins_anchored` (78 top-level pins anchored by name).
Power connectivity: `match`, 725 instances, no findings, but `expected_nets`
was not declared, so it checks only what the library pins imply. The compare
is of abstracted standard cells (no devices extracted), so it establishes
connectivity of the placed-and-routed netlist, not device-level LVS.

### History: the earlier `mismatch` was a real open in a superseded stream

The first digital report (commit `5315874`) was `mismatch`, 13 errors:
`clknet_3_5__leaf_clk` split in two, plus `net.split` on `VDD` and `VSS`. It
was extracted from the stream committed in `1318c76`, which `8b7a4e0` then
regenerated (new PDN straps and a 20 um tap pitch in `layout/pnr/request.json`
to reach `klt drc` clean) without rerunning LVS. The committed report was
therefore against a stream that no longer existed (the as-built netlist hash
differs too).

Classification (issue #45), measured:

- Extracting the `1318c76` stream with the same deck and flags reproduces the
  split: nine flop-clock nets (2, 3, 6, 7, 8, 9, 9, 9, 14 flops) against eight
  in the netlist (5, 5, 8, 8, 8, 10, 10, 13).
- An independent flat connectivity pass over that stream (Metal1 to Metal5
  through Via1 to Via4, no cell abstraction, the deck's own layer numbers) also
  gives nine clock nets, so it is not an artifact of the cell abstraction or
  of `--def-net-names` (the same split appears with and without it). It is a
  real open in the routed clock tree of that stream.
- The same extraction and the same independent pass on the current stream give
  eight clock nets with exactly the netlist's flop counts, with and without
  `--def-net-names`.

The open went away with the regenerated stream; this issue's investigation did
not isolate which of the request changes closed it (PDN straps, tap pitch, or
the changed placement and routing that followed) and does not claim one. The
`VDD`/`VSS` `net.split` findings are absent from the current report; they
belonged to the same superseded stream and were not separately attributed.
No tool gap was found (the extraction and compare behaved correctly on both
streams), so no `klayout-tools` issue is filed. Process gap: nothing ties an
LVS report to the stream hash it was run on, so regenerating the stream
silently staled it; rerun `klt extract` + `klt lvs` after any
`layout/pnr/run.sh`.
