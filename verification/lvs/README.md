# verification/lvs

T1 item 4 (LVS) runs, one `klt lvs` request per partition, with the klt pinned
in [`layout/toolchain.json`](../../layout/toolchain.json) (run through `uvx`;
engine `klayout` 0.30.12). Both runs were single compares, no grid.

**Both partitions are LVS clean (`status: match`).** Both reports are
committed as they came out, and `manifests/gf180-current-dac.json` cites them
as `4.analog` / `4.digital`. Nothing was shrunk or waived to move a verdict.
`klt lvs --check` exits 0 on both (run it from this directory: the reference
path is relative to the report). Both runs were single compares, no grid.

| Partition | Layout | Reference | Verdict |
|---|---|---|---|
| analog | `layout/gf180-current-dac-analog.gds`, extracted inline (gf180mcu deck, ~6 min) | `design/analog/dac_analog.spice`, `form: subckt-call` | `match` (`flatten_reference: true`, 133 dummies on both sides); 72 of 72 pins extracted |
| digital | `layout/pnr/dac_digital.gds`, extracted to `dac_digital.gate.spice` | `layout/pnr/dac_digital.asbuilt.v`, `form: gate-level-verilog` | `match`, 0 errors, `power_connectivity` = `match` |

## Analog

The routed and pinned stream (`layout/gen_array.py`, issue #51) extracts to 72
pins against the reference's 72, 5046 devices and 2586 nets, with the body
terminals resolved to real taps. [`analog.request.json`](analog.request.json)
is one compare, about 6 min on one core, and reads `match`. Two things moved
it from the earlier `mismatch`, neither a waiver:

- **`options.flatten_reference: true`.** The reference netlist is hierarchical
  (`bias`, `driver`, `elem_*`, `unit_cell`, ...) and the layout is extracted
  flat, so without it no circuit pairs and 0 nets match. The report gives no
  hint of that; filed as 2AMLogic/klayout-tools#4548.
- **Reference dummy count 33 -> 133.** `design/gen_analog.py` carried
  `N_RING_DUMMY = 32` as a placeholder that DR-0006 defers to the layout; the
  layout's one-cell ring is 132 plus the filler. The constant is now 132, the
  schematic and `dac_analog.spice` are regenerated (`klt netlist`) and the
  item-1 attestation is refreshed. The array of 1023 live unit cells is
  unchanged; only the ring placeholders grew. Before this, the flat compare
  left exactly the 100 extra layout dummies unmatched (400 `device.unmatched`,
  200 `net.split`, all layout-only).

`power_connectivity` is `unchecked` for this report: the reference form is
`subckt-call`, whose netlist carries its own supply pins and nets, so they take
part in the ordinary compare and the signal-only power check does not apply.
That is "does not apply", not "verified"; no rail-continuity or IR claim is
made from this report.

### History: the placement-only report

The previous `analog.report.json` (layout hash `bf0643cd...`, placement only)
read `mismatch`, 0 of 207 nets matched, 5046 extracted devices on 15340 nets,
1 pin against 72, `power_connectivity` unchecked, and `body_unverified`
warnings for 4845 NMOS (on the synthesized `vsubs`) and 201 PMOS (anonymous
wells), because nothing was wired and no tap was tied. It is in the git
history; the numbers above replace it for the current stream.

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
