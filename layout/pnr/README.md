# layout/pnr

Digital-partition layout stream (T1 item 2, digital): the synthesized
`dac_digital` netlist (`synth/out/dac_digital/dac_digital_synth.v`) placed,
clock-tree synthesized and routed by `klt place-and-route`. The analog
partition's stream is `layout/gf180-current-dac-analog.gds`; the two are not
merged or abutted here.

## Regenerate

```
layout/pnr/run.sh           # rewrites dac_digital.gds, .report.json, .asbuilt.v and .def
layout/pnr/run.sh --check   # reruns and compares the stream hash with the committed one
```

Run from anywhere; the script changes to the repo root, because the `openroad`
wrapper on the worker mounts only `$PWD`. It uses the klt pinned in
[`../toolchain.json`](../toolchain.json) through `uvx` (klayout pinned to the
same file's `klayout_package_pin`, so the stream hash is the pin's), needs
docker for OpenROAD and the PDK at the revision in `sim/pdk.json`. One run,
one corner of placement; no grid. `.klt/` (scratch) is cleared at startup and
gitignored; the routed DEF is copied out to `dac_digital.def` before the next
invocation clears it (the flow emits no post-route SPEF, so none is kept) —
that DEF is the fixed geometry `klt sta`
([`../../verification/sta/`](../../verification/sta/README.md)) analyses and
`klt extract` reads for [digital LVS](../../verification/lvs/README.md#digital).
The stream was byte-identical on two consecutive runs (OpenROAD
`26Q3-1510-g6cb3f2b704`, seed 1).

**The routed stream changed with the I/O constraints.** Adding the DR-0008
delays below changed placement (the router now times the I/O paths), so the
GDS, as-built netlist, DEF and everything bound to the old stream were
regenerated in the same change: `dac_digital.report.json`, the item 2 and 3
evidence, LVS (report and gate netlist), ERC, and the manifest citations.
Old stream sha256 `67068b3c…`, new `93901ab7…`.

Attestation: `evidence/item2-digital.json`, from `klt signoff --attest 2
--input layout/pnr/dac_digital.gds --generator layout/pnr/run.sh
--regenerated-hash <hash of the second run>`.

## Request

[`request.json`](request.json): gf180mcu 7-track 5 V library, `tt_025C_3v30`;
40 % utilization with a 10 um core margin; PDN straps of klt's
`gf180mcu_7t_6M` preset, spelled out without the preset's `connects` via
tuning (see [`../drc/README.md`](../drc/README.md)), and tap cells every 20 um;
clock `clk` at 10 ns (100 MS/s, the update
rate row of `spec/target-spec.md`, which is still PROPOSED: re-check when it is
ratified) with `input_delay_ns` / `output_delay_ns` 3.0 / 3.0 — DR-0008's
proposed I/O budget ([`../../spec/decision-records/0008-digital-io-timing-budget.md`](../../spec/decision-records/0008-digital-io-timing-budget.md),
status `proposed`, both figures assumed); pins on Metal3 (horizontal) and
Metal2 (vertical).

Boundary: `t_q[62:0]` and `b_q[3:0]` (decoder outputs, the switch-driver
inputs of the `partition_boundary` text) on the south edge, `din[9:0]` and
`clk` on the north edge. There is no analog floorplan yet, so which edge faces
the driver band is a placeholder; final abutment belongs to integration.

## What is and is not claimed

Reported by the tool (`dac_digital.report.json`): route reached, 0 route DRC
violations, 0 antenna violations, 0 max-transition/capacitance violations, PDN
audit `complete` (99 tap cells, 62 endcaps, 505 fillers), die 21329 um^2,
utilization 47.9695 %.

- **Timing is constrained, against a proposed budget.** With the DR-0008
  I/O delays in the request, every corner in `dac_digital.report.json`
  reports `timing_status: "constrained"` with real setup/hold slack — but the
  budget is DR-0008 (`proposed`, figures assumed), so the slacks are
  provisional and the report is not cited for item 5. The standalone run
  over the five 3.3 V corners is
  [`../../verification/sta/`](../../verification/sta/README.md); note its
  timing does **not** share this report's interconnect basis: this flow
  times after `estimate_parasitics -global_routing` (wire RC estimated from
  the global route, `interconnect_corner: "nom"`), the standalone run
  applies zero wire RC, so its setup slacks on the shared corners are
  0.28–0.78 ns higher (measured reason and table:
  [verification/sta's interconnect
  section](../../verification/sta/README.md#interconnect-basis-zero-wire-rc-standalone-vs-estimated-wire-rc-in-flow));
  a signoff-grade I/O timing claim rests on the wire-RC-inclusive numbers.
  This flow sweeps all 15 library corners, including 1v62–1v98 and
  4v50–5v50 supply rows that are **outside** DR-0008's 3.3 V PVT set; the
  `ss_*_1v62` rows show negative setup slack (−6.9 ns at `ss_125C_1v62`)
  and are not budget results either way — the digital supply is
  3.3 V ±10 % (DR-0002).
- `klt drc` of this stream is item 3 (`../drc/README.md`: clean, with the
  coverage gaps listed there). LVS and extraction are other T1 items and are
  not claimed. `route_drc_violation_count` is OpenROAD's router DRC, not
  the `klt drc` deck. Metal density is not evaluated.
- The attestation checks only that the stream reads, has a non-empty top cell
  and is on grid, plus the regeneration hash.
