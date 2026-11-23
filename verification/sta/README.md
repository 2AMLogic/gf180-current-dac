# verification/sta

This standalone `klt sta` run times the routed digital partition
(`dac_digital`) across five corners with zero wire RC. All slacks below are
**provisional**. DR-0001 awaits spec ratification (#2), and both 3.0 ns I/O
delays in [DR-0008](../../spec/decision-records/0008-digital-io-timing-budget.md)
are assumptions.

**T1 item 5 (digital) remains uncited.** After ratification, cite the two
[functional reports](../functional/) together with a `klt sta` report that
includes wire RC and verifies the ratified budget across its declared corners.
With the functional reports present, the pinned `klt signoff` (0.9.0) grades
this cell-delay-only STA report `met` even against the draft budget. Substituting
the in-flow P&R report gives `unmet / wrong_kind`. The in-flow report is the
current reference for timing with wire RC.
See the [T1 checklist, item 5](../../manifests/design-evidence-tiers.md).

## Command

Run from the repo root (paths in the request resolve relative to it):

```
uvx --from "$(python3 -I -c 'import json;print(json.load(open("layout/toolchain.json"))["klt_install"])')" \
    --with "klayout==$(python3 -I -c 'import json;print(json.load(open("layout/toolchain.json"))["klayout_package_pin"])')" \
    klt sta verification/sta/request.json --pdk gf180mcuD --format json \
    > verification/sta/dac_digital.report.json
```

- klt `0.8.1.dev86+gf9039fd7244e` — the layout pin `f9039fd7244e977325c351a5780acbf1cee383fb`
  from [`layout/toolchain.json`](../../layout/toolchain.json) (`klt_install`); the
  `--with klayout==0.30.12` half reproduces the committed provenance (a bare
  `uvx` resolves a newer klayout and the version field drifts; the timing
  values do not).
- klayout `0.30.12`, OpenROAD `26Q3-1510-g6cb3f2b704` (engine).
- PDK `gf180mcuD`, open_pdks `f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7`.

Re-running the command reproduces the committed report exactly (verified;
only the per-corner `engine_log` invocation ids differ).

## Geometry

`geometry_source: "routed"`: the DEF retained by [`layout/pnr/run.sh`](../../layout/pnr/run.sh)
at `layout/pnr/dac_digital.def` (sha256
`36ea425f3fd0464001f37d400d8e3e62107ef2a2eab3e88fcc00afc381dcae25`, the
report's `provenance.input.content_hash`), from the same run that produced
the committed `dac_digital.gds` (sha256
`93901ab747d6c4ab3a051a3d84d52c869a619018face0dfdbe74259b593aa7f8`) and
`dac_digital.asbuilt.v` (sha256
`bb51f8880448be28aebd37eece82494295dcaf61ea231ba3012f6db8bb1ffa4b`). That binding is checked:
[`layout/pnr/run.sh --check`](../../layout/pnr/README.md#regenerate) reruns the
route, byte-compares the committed GDS and DEF with the regenerated copies,
and fails unless this report's `provenance.input.content_hash` is the
committed DEF's SHA-256 — so a DEF that drifts from its stream, or this
report left stale against a regenerated DEF, cannot pass unnoticed. **Every
interconnect delay in this five-corner run is zero.** The committed P&R run
itself produced no post-route SPEF (the SPEF below comes from a separate `klt extract`). The STA report records a null `spef_path` and
`electrical_checks.parasitics_source: "none"` at every corner. This DEF-mode
session also applies no wire-RC estimate or wire-load model, so the slacks
below include cell delays only. The [interconnect section](#interconnect-basis-zero-wire-rc-standalone-vs-estimated-wire-rc-in-flow)
compares this run with the in-flow timing on the same DEF.
Clock is ideal (`clock_mode: "ideal"`), no uncertainty, no SDF. The
post-route SDF export for item 7 is a separate single-corner run, below.

## Post-route SDF export ([`sdf.request.json`](sdf.request.json))

T1 item 7 digital ([`../functional/`](../functional/)) needs a
post-route SDF, so a second single-corner request re-analyses the same DEF
under the same DR-0008 constraints at the nominal corner with an extracted
SPEF loaded and `sdf: true`. Run from the repo root, at the grading pin
(`scripts/check_signoff.sh --print-pin`, `0.9.0`, with the klayout package
pin from [`layout/toolchain.json`](../../layout/toolchain.json)); the
five-corner report above stays at the layout pin:

```
uvx --from "klayout-tools==0.9.0" --with "klayout==0.30.12" \
    klt sta verification/sta/sdf.request.json --pdk gf180mcuD --format json \
    > verification/sta/dac_digital.sdf.report.json
```

The emitted SDF lands in `.klt/sta/dac_digital.tt_025C_3v30.sdf`
(gitignored) and is copied out to
[`../functional/dac_digital.tt_025C_3v30.sdf`](../functional/dac_digital.tt_025C_3v30.sdf);
OpenSTA stamps a `(DATE ...)` header line, so the bytes are not
reproducible run-to-run — the digest of record is the retained copy's,
`e08b63f84684aabe2f8c5458354887e94eb0c053290b0690e618955ff1aae340`,
matching that run's `corners[0].sdf.content_hash`. Both pins agree on the
`sdf` contract (issue #2886 is in the docs at the layout pin
`f9039fd7244e` and at `0.9.0` alike); the run itself used the grading pin
as issue #140 specifies.

**The SPEF** ([`dac_digital.spef`](dac_digital.spef), sha256
`dffe8f2552f97b682a2915b55cdc82b7f89484a8e7f859c600fe2b8d9145c7a6`) is
`klt extract` on the routed GDS with net names, pins and connections from
the matching DEF — same flags as the digital-LVS extraction plus the
parasitics/SPEF pass, at the same grading pin:

```
uvx --from "klayout-tools==0.9.0" --with "klayout==0.30.12" klt extract \
    layout/pnr/dac_digital.gds --deck gf180mcu \
    --abstract-cells 'gf180mcu_fd_sc_mcu7t5v0__*' \
    --def-net-names --def-pins layout/pnr/dac_digital.def \
    --def-net-connections layout/pnr/dac_digital.def \
    --pdk gf180mcuD --parasitics --spef verification/sta/dac_digital.spef \
    --backend local --format json -o /tmp/dac_digital.spef.spice
```

189 nets carry parasitics (189 R + 189 C, 2187 coupling caps,
5116 ohm / 1541 fF total); the SPEF keeps 182 `*D_NET` blocks — 7
unlabelled `$N` nets the DEF does not know are omitted per the documented
OpenSTA `STA-1650` rule, and the extraction's integrity check reports zero
findings over all 189 nets.

**Result** (`dac_digital.sdf.report.json`): `tt_025C_3v30`,
`timing_status: "constrained"`, 0 setup and 0 hold violations, setup slack
4.85631 ns / hold slack 2.93303 ns — against the five-corner DEF/LEF run's
5.23987 ns at the same corner, i.e. the SPEF is loaded and delays moved
(`delay_changed: true`). SPEF annotation: 182/182 design nets annotated,
`annotation_complete: true`, 0 reader warnings; the 7 `unannotated_driver`
entries are the CTS `clkload*` dummy loads' floating outputs, an inherent
limit, not an extraction defect. The same provisional-budget caveat as
above applies: DR-0008 is `proposed`, so these slacks are provisional too,
and this report is cited for neither item 5 nor timing claims — its product
is the SDF the item-7 functional run consumes.

## Request

[`request.json`](request.json): DR-0008's proposed budget — `clk` at 10.0 ns
(100 MS/s), `input_delay_ns` 3.0, `output_delay_ns` 3.0 — over the five
3.3 V-supply corners DR-0008 names as this budget's PVT set (DR-0002 fixes
the digital supply at 3.3 V ±10 %; the 1v62–1v98 and 4v50–5v50 libraries
are other supplies and are out of the set):

| Corner | Setup slack (ns) | Hold slack (ns) |
|---|---|---|
| `tt_025C_3v30` | 5.23987 | 2.93303 |
| `ss_n40C_3v00` | 4.5442 | 2.90662 |
| `ss_125C_3v00` | 3.48538 | 2.90574 |
| `ff_n40C_3v60` | 5.97088 | 2.94387 |
| `ff_125C_3v60` | 5.50399 | 2.92321 |

Every corner reports `timing_status: "constrained"` with non-negative setup
and hold slack, zero setup and hold violations, and `constraint_completeness:
"complete"` (0 unconstrained endpoints, 0 unclocked registers) — no `1e+39`
sentinel anywhere. In all five corners, the worst setup path starts at
`din[8]` or `din[9]` and ends at a register `D` pin. The worst hold path is
`din[9]` to `_31_/D` in every corner.

DR-0008 allows 7 ns (10 − 3 ns) on each side of the register. On the input
side, the 3 ns input delay sets both the earliest and latest arrival. For a
fixed route, increasing it reduces input setup slack and increases input hold
slack. On the output side, the separate 3 ns reservation leaves 7 ns from
the launching clock edge for a registered output to become valid.

The reported `fmax_mhz` (210.1 at `tt_025C_3v30`) is derived from setup
slack under that provisional budget. `estimated_power_mw` (2.47 at tt) uses
engine-default activity and `estimate_only` parasitics for an order-of-magnitude
power estimate.

## Interconnect basis: zero wire RC (standalone) vs estimated wire RC (in-flow)

The in-flow STA of the P&R run that produced this very DEF
(`layout/pnr/dac_digital.report.json`: same engine build, same ideal clock,
same DR-0008 constraints, timing taken after `estimate_parasitics
-global_routing` at `interconnect_corner: "nom"`) reports **0.28–0.78 ns
less setup slack** than this standalone run on the five shared corners,
while hold differs by at most 0.00011 ns. The middle columns show what
changed when the standalone run added a placement-based wire-RC estimate
on the same DEF. All slacks are in ns. [Measurement on #150](https://github.com/2AMLogic/gf180-current-dac/issues/150#issuecomment-7055322613)

| Corner | Setup: standalone | Setup: +wire RC | Setup: in-flow | Hold: standalone | Hold: +wire RC | Hold: in-flow |
|---|---|---|---|---|---|---|
| `tt_025C_3v30` | 5.23987 | 4.88914 | 4.78186 | 2.93303 | 2.93307 | 2.93313 |
| `ss_n40C_3v00` | 4.5442 | 4.03722 | 3.89598 | 2.90662 | 2.90666 | 2.90671 |
| `ss_125C_3v00` | 3.48538 | 2.88684 | 2.70668 | 2.90574 | 2.90578 | 2.90584 |
| `ff_n40C_3v60` | 5.97088 | 5.76707 | 5.68935 | 2.94387 | 2.94391 | 2.94398 |
| `ff_125C_3v60` | 5.50399 | 5.21942 | 5.11041 | 2.92321 | 2.92324 | 2.92329 |

The **+wire RC** arm is the committed standalone command's own staged
per-corner Tcl (`verification/sta/.klt/sta/sta_dac_digital__<corner>.tcl`
after a run: `read_lef` x2 → `read_def` → `read_liberty` → `create_clock` →
I/O delays → reports) with exactly two lines inserted before the reports —
`set_wire_rc -layer Metal2` and `estimate_parasitics -placement`, the same
wire-RC treatment `klt place-and-route`'s own place/CTS stages apply
(`io.layer_v` is Metal2 in `layout/pnr/request.json`) — run through the
same pinned docker OpenROAD (`26Q3-1510-g6cb3f2b704`), slacks read from
the `-metrics` keys `timing__setup__ws`/`timing__hold__ws` that `klt sta`
itself parses. Everything else is byte-identical to the standalone run;
the standalone column above reproduces the committed report exactly.

Adding placement-based wire RC closes 72–78 % of the setup gap and changes
hold by at most 0.00004 ns across the five corners. Setup slack with that
estimate remains 0.07772–0.18016 ns above the in-flow result. Placement
estimates use bounding boxes and the in-flow estimate uses global-route
topology. That difference could explain the remainder. A direct test on
the routed DEF stopped before it could measure the effect. After
`set_routing_layers -signal Metal2-Metal5`, `global_route` skipped every
net (wirelength 0) and `estimate_parasitics -global_routing` returned
`EST-0005`.

**The current wire-RC reference is the in-flow estimate.** Its worst setup
slack on the five shared corners is 2.70668 ns at `ss_125C_3v00`. For a
future `5.digital` citation, the timing artifact must be a wire-RC-inclusive
`klt sta` report on the routed design under the ratified budget.

The pinned `klt sta` already accepts a routed DEF and a `spef` input.
The committed [P&R request](../../layout/pnr/request.json) omits
`post_route_spef` and selects the GF180 7-track library
(`gf180mcu_fd_sc_mcu7t5v0`). At the layout pin, the exporter's extraction
deck map has a GF180 entry for 9-track only. Requesting SPEF export for
this 7-track library therefore fails at deck lookup. Upstream closed
#7021 because export and STA annotation already work for mapped libraries.
See the [pinned STA guide](https://github.com/2AMLogic/klayout-tools/blob/f9039fd7244e977325c351a5780acbf1cee383fb/docs/cli/sta.md#L37-L49),
[pinned deck map](https://github.com/2AMLogic/klayout-tools/blob/f9039fd7244e977325c351a5780acbf1cee383fb/src/klayout_tools/place_and_route.py#L921-L925),
and [upstream closure](https://github.com/2AMLogic/klayout-tools/issues/7021#issuecomment-7057287126).

## What is and is not claimed

- The slacks above are **provisional**: they check a `proposed` record whose
  3.0 ns figures are assumed. Nothing here meets a ratified spec row; the
  manifest cites nothing in this directory.
- The corner set is the five 3.3 V corners the cited run itself declared —
  `klt signoff` grades exactly that set, nothing wider.
- The five-corner run has no SPEF-annotated result and no wire RC of any kind (every interconnect
  delay is zero — see the
  [interconnect section](#interconnect-basis-zero-wire-rc-standalone-vs-estimated-wire-rc-in-flow)
  above); no clock-tree-real (propagated) clock, no on-chip-variation
  derating: the run is ideal-clock, cell-delay-only STA. The
  single-corner SDF-export run above is SPEF-annotated but inherits the
  ideal clock, no OCV and the same provisional budget.
- The same constraints now also run inside `klt place-and-route`
  ([`layout/pnr/`](../../layout/pnr/README.md)), whose report covers all 15
  library corners including other-supply rows out of this budget's set, and
  whose timing includes estimated wire RC. Its setup slacks on these five
  corners are 0.28–0.78 ns lower. Adding placement-based wire RC to the
  standalone run accounts for 72–78 % of that difference.
