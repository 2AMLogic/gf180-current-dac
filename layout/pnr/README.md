# layout/pnr

Digital-partition layout stream (T1 item 2, digital): the synthesized
`dac_digital` netlist (`synth/out/dac_digital/dac_digital_synth.v`) placed,
clock-tree synthesized and routed by `klt place-and-route`. The analog
partition's stream is `layout/gf180-current-dac-analog.gds`; the two are not
merged or abutted here.

## Regenerate

```
layout/pnr/run.sh           # rewrites dac_digital.gds, dac_digital.report.json, dac_digital.asbuilt.v
layout/pnr/run.sh --check   # reruns and compares the stream hash with the committed one
```

Run from anywhere; the script changes to the repo root, because the `openroad`
wrapper on the worker mounts only `$PWD`. It uses the klt pinned in
[`../toolchain.json`](../toolchain.json) through `uvx`, needs docker for
OpenROAD and the PDK at the revision in `sim/pdk.json`. One run, one corner of
placement; no grid. `.klt/` (scratch) is gitignored. The stream was
byte-identical on two consecutive runs (OpenROAD `26Q3-1510-g6cb3f2b704`,
seed 1).

Attestation: `evidence/item2-digital.json`, from `klt signoff --attest 2
--input layout/pnr/dac_digital.gds --generator layout/pnr/run.sh
--regenerated-hash <hash of the second run>`.

## Request

[`request.json`](request.json): gf180mcu 7-track 5 V library, `tt_025C_3v30`;
40 % utilization with a 10 um core margin; PDN from klt's `gf180mcu_7t_6M`
preset with tap cells every 50 um; clock `clk` at 10 ns (100 MS/s, the update
rate row of `spec/target-spec.md`, which is still PROPOSED: re-check when it is
ratified); pins on Metal3 (horizontal) and Metal2 (vertical).

Boundary: `t_q[62:0]` and `b_q[3:0]` (decoder outputs, the switch-driver
inputs of the `partition_boundary` text) on the south edge, `din[9:0]` and
`clk` on the north edge. There is no analog floorplan yet, so which edge faces
the driver band is a placeholder; final abutment belongs to integration.

## What is and is not claimed

Reported by the tool (`dac_digital.report.json`): route reached, 0 route DRC
violations, 0 antenna violations, 0 max-transition/capacitance violations, PDN
audit `complete` (33 tap cells, 62 endcaps, 454 fillers), die 21329 um^2,
utilization 46.5 %.

- **Timing is not closed, it is unconstrained.** The request has a clock but
  no input/output delays, and the spec has no I/O timing, so the tool reports
  `timing_status: unconstrained` and slack `1e39` at every corner. The
  `fmax_mhz` of 168.36 it prints is not a slack-checked result. Do not cite it
  as meeting 100 MS/s.
- Layout-level DRC, LVS and extraction of this stream are other T1 items and
  are not claimed. `route_drc_violation_count` is OpenROAD's router DRC, not
  the `klt drc` deck. Metal density is not evaluated.
- The attestation checks only that the stream reads, has a non-empty top cell
  and is on grid, plus the regeneration hash.
