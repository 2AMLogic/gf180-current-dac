# layout/pnr

Digital-partition layout stream (T1 item 2, digital): the synthesized
`dac_digital` netlist (`synth/out/dac_digital/dac_digital_synth.v`) placed,
clock-tree synthesized and routed by `klt place-and-route`. The analog
partition's stream is `layout/gf180-current-dac-analog.gds`; the two are not
merged or abutted here.

## Regenerate

```
layout/pnr/run.sh           # rewrites dac_digital.gds, .report.json, .asbuilt.v and .def
layout/pnr/run.sh --check   # reruns and compares the regenerated GDS and DEF with the
                            # committed copies, and the committed DEF's hash with the
                            # STA report's input digest
```

Run from anywhere; the script changes to the repo root, because the `openroad`
wrapper on the worker mounts only `$PWD`. It uses the klt pinned in
[`../toolchain.json`](../toolchain.json) through `uvx` (klayout pinned to the
same file's `klayout_package_pin`, so the stream hash is the pin's), needs
docker for OpenROAD and the PDK at the revision in `sim/pdk.json`. One run,
one corner of placement; no grid. `.klt/` (scratch) is cleared at startup and
gitignored; the routed DEF is copied out to `dac_digital.def` before the next
invocation clears it. This run omitted `post_route_spef` and produced no
SPEF. The retained DEF is the fixed geometry `klt sta`
([`../../verification/sta/`](../../verification/sta/README.md)) analyses and
`klt extract` reads for [digital LVS](../../verification/lvs/README.md#digital).
The stream was byte-identical on two consecutive runs (OpenROAD
`26Q3-1510-g6cb3f2b704`, seed 1).

`--check` reruns the route into scratch and byte-compares both retained
geometry files — the GDS and the DEF — with their committed copies, then
verifies that the committed DEF's SHA-256 is the
`provenance.input.content_hash` recorded in the committed STA report
([`../../verification/sta/dac_digital.report.json`](../../verification/sta/dac_digital.report.json)).
Any of the three comparisons failing — a drifted stream, a DEF that no longer
matches its route, or a report left stale against a regenerated DEF — exits
nonzero naming the failed comparison. Check mode reads the committed
artifacts and rewrites nothing: after a normal regeneration moves the DEF,
the check fails on the stale report digest until `klt sta` refreshes it.

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
  provisional. This report is the current wire-RC reference. It times
  after `estimate_parasitics -global_routing` at `interconnect_corner: "nom"`.
  On the five shared 3.3 V corners, the zero-wire-RC standalone run reports
  0.28–0.78 ns more setup slack. Adding placement-based wire RC to that run
  closes 72–78 % of the gap. The cause of the remainder is unverified.
  A future item 5 citation needs a wire-RC-inclusive `klt sta` report
  against the ratified budget. See the [five-corner comparison](../../verification/sta/README.md#interconnect-basis-zero-wire-rc-standalone-vs-estimated-wire-rc-in-flow).
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
