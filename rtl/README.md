# rtl

Digital partition (T1 item 1): 6-to-63 thermometer decoder, 4-bit binary path
and one retiming register bank, ending at the switch-driver inputs. The
analog partition is `design/`.

| File | Content |
|---|---|
| `thermo_decoder.v` | combinational, `t[i] = (code > i)` for i = 0..62 |
| `dac_digital.v` | top: decoder on `din[9:4]`, binary `din[3:0]`, one flop bank on `clk`, latency one cycle |

Rows used are the **proposed** ones (6 + 4 segmentation, 100 MS/s; DR-0001,
ratification in #22 / PR #29); rerun if they change.

Thermometer and binary bits are registered in the same bank, so all outputs
launch from a flop on one edge. No delay chain is inserted to match decoder
depth (synthesis would remove it). The spec row "decoder, retiming latches and
cell switches meet timing at 100 MS/s" is **not** shown here: `klt synthesize`
reports no timing (`timing: null`) and no STA has been run. The retiming
elements are edge-triggered flops, not level-sensitive latches.

## Simulate

```
iverilog -g2005 -o /tmp/tb.vvp rtl/thermo_decoder.v rtl/dac_digital.v verification/rtl/tb_dac_digital.v && vvp /tmp/tb.vvp
```

Exhaustive over 1024 input codes (all 64 decoder codes x 16 binary codes):
thermometer value, binary bits in the same cycle, and exactly one thermometer
line flipping at each major carry. Committed result:
`verification/rtl/tb_dac_digital.result`. Design sanity check only, not the
item-9 testbench inventory.

## Synthesize

`synth/*.request.json` target `gf180mcu_fd_sc_mcu7t5v0` at `tt_025C_3v30`
(7-track, 3.3 V) from the PDK revision in `sim/pdk.json`; no timing target.
Synthesis scratch (logs, memory-evidence files) is not committed; netlists,
Yosys scripts and stats are under `synth/out/`.

```
export PDK_ROOT=~/.ciel/ciel/gf180mcu/versions/f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
rm -rf synth/out
klt synthesize synth/decoder.request.json --pdk gf180mcuD --verify-equivalence --format json > synth/decoder.report.json
klt synthesize synth/dac_digital.request.json --pdk gf180mcuD --format json > synth/dac_digital.report.json
klt signoff --attest 1 --inventory design/inventory-item1-digital.json -o evidence/item1-digital.json
klt signoff --manifest manifests/gf180-current-dac.json --tiers-doc manifests/design-evidence-tiers.md --format json > manifests/gf180-current-dac.signoff.json
```

Equivalence (`--verify-equivalence`, `klt equiv`) was run on the combinational
`thermo_decoder` only and returned `equivalent`; it is combinational-only, so
the sequential `dac_digital` top is not covered by an equivalence proof.
Freshness: `klt synthesize <request> --check <report>` (needs the PDK, so
`local_only` in the inventory) and `synth/check_netlist_hash.py` for the
netlist bytes. Pruning the scratch leaves the report's `script_path` and
similar fields pointing at files that were deleted; `--check` does not read them.
