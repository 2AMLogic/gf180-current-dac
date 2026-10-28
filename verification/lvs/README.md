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
| analog | `layout/gf180-current-dac-analog.gds`, extracted inline (gf180mcu deck, ~6 min) | `design/analog/dac_analog.spice`, `form: subckt-call` | `mismatch` (hierarchical reference vs flat layout, 0 nets matched); 72 of 72 pins extracted |
| digital | `layout/pnr/dac_digital.gds`, extracted to `dac_digital.gate.spice` | `layout/pnr/dac_digital.asbuilt.v`, `form: gate-level-verilog` | `match`, 0 errors, `power_connectivity` = `match` |

## Analog

**The routed and pinned stream (`layout/gen_array.py`, issue #51) extracts to
72 pins against the reference's 72, 5046 devices and 2586 nets, with the body
terminals resolved to real taps (`body_verification: verified`); the verdict
is still `mismatch`, and the `match` is #35's gate.** The committed
[`analog.report.json`](analog.report.json) is the unchanged
[`analog.request.json`](analog.request.json) run on that stream (about 6 min,
one core, one compare). It reads `mismatch` for a structural reason, not a
connectivity one: the reference netlist is hierarchical (`bias`, `driver`,
`elem_*`, `unit_cell`, ...) and the layout is extracted flat, so no circuit
pairs ("circuit could not be matched", 10 errors) and 0 nets match.

To see the residual under the compare, the same request with
`flatten_reference: true` is committed as
[`analog.flatref.request.json`](analog.flatref.request.json). It is a
diagnostic run, one compare, about 6 min; its 1.0 MB report is not committed.
Result, as the tool counts it:

| | layout | reference | matched |
|---|---|---|---|
| devices | 5046 | 4646 | 4646 |
| nets | 2586 | 2386 | 2385 |
| pins | 72 | 72 | 72 |

All 600 errors are layout-only: 400 `device.unmatched` (nfets) and 200
`net.split`. They are 100 dummy cells: the layout has 133
`dummy_cell` (132 ring + 1 filler) and the schematic 33 (32 ring placeholders
+ 1 filler), the placeholder `layout/README.md` lists under "Known gaps" and
DR-0006 defers to the layout; 100 dummies x 4 nfets = 400 devices, and 100 x
2 internal nets (`n1`, `n2`) = 200 nets. The 1056 `topology` warnings are
ambiguous pairings among identical, symmetric units that the comparer resolved
structurally. All 4646 reference devices found a layout device. Per-cell compares of `unit_cell`, `dummy_cell` and `driver`
against their reference subcircuits are `match` (scratch requests, not
committed); `bias` alone is not meaningful because its ten pairs only join at
the top-level rails.

The report gives no hint that `flatten_reference` is the fix; filed as
2AMLogic/klayout-tools#4548.

Nothing was edited, shrunk or waived to move a verdict: the reference netlist
is the committed one. What closes it is outside this issue: the reference
dummy count and the compare option (#35).

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
