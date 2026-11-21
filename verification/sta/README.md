# verification/sta

Multi-corner `klt sta` on the routed digital partition (`dac_digital`), the
timing half of T1 item 5 (digital). The functional half is
[`verification/functional/`](../functional/); the two reports there
and this one are item 5's evidence set when the spec is ratified.

**This report is not cited in the signoff manifest.** The budget it checks is
[`spec/decision-records/0008-digital-io-timing-budget.md`](../../spec/decision-records/0008-digital-io-timing-budget.md),
status `proposed`: both 3.0 ns I/O delays are marked "assumed, no source", and
DR-0001 (the spec) is itself unratified. The T1 checklist requires a ratified
spec for item 5 ("verdicts against a draft spec are provisional by
construction"). Probing `klt signoff` (0.9.0, the grading pin) with this
report cited grades item 5 (digital) `met` anyway — the ratification note is
prose the tool does not enforce — so the manifest stays uncited and the
citation waits on #2. Every slack below is **provisional** until then.

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
the committed `dac_digital.gds`. **Zero wire RC — every interconnect delay
is exactly zero.** The P&R flow emits no post-route SPEF (`spef_path` null,
every corner's `electrical_checks.parasitics_source` `"none"`), and `klt
sta`'s DEF-mode session issues no `set_wire_rc`, no `estimate_parasitics`
and no wire-load model, so the slacks below carry **cell delays only** —
not "DEF/LEF-based estimates", no wire delay of any kind. The measured
consequence, against the in-flow P&R run on this same DEF, is the
[interconnect section](#interconnect-basis-zero-wire-rc-standalone-vs-estimated-wire-rc-in-flow)
below. Clock is ideal (`clock_mode: "ideal"`), no uncertainty, no SDF. The
post-route SDF back-annotated functional run is item 7 and belongs to #140.

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
while hold agrees to 0.0001 ns. The reason is interconnect, measured on
this DEF (issue #150): the standalone session applies zero wire RC, the
in-flow one applies an estimate. Three arms, one DEF:

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

That arm recovers 72–78 % of the setup gap at every corner; the remainder
is estimate fidelity (bounding-box RC vs the global-route-topology RC the
in-flow run uses). Hold moves ≤ 0.0001 ns at every corner — the worst
hold path is an input pad to a nearby register with almost no wire (the
worst short path can shift between input pads; the magnitude does not).
The in-flow treatment itself **cannot** be applied standalone: on an
already-routed DEF `global_route` skips every net (wirelength 0) and
`estimate_parasitics -global_routing` refuses with `EST-0005` — measured
by inserting `set_routing_layers -signal Metal2-Metal5` + `global_route` +
`estimate_parasitics -global_routing` into the same staged Tcl.

**Basis for a signoff-grade I/O timing claim**: wire-RC-inclusive timing.
Of the two committed reports that is the in-flow one (worst shared-corner
setup 2.70668 ns at `ss_125C_3v00`); this standalone report overstates
setup margin by 0.28–0.78 ns and stays labeled zero-wire-RC until `klt sta`
can annotate a post-route SPEF — a capability gap filed upstream at
[2AMLogic/klayout-tools#7021](https://github.com/2AMLogic/klayout-tools/issues/7021)
(the flow emits no SPEF and `klt sta` def mode takes no interconnect
setting). When #2 ratifies the spec and the `5.digital` citation lands, it
must cite wire-RC-inclusive numbers on these five corners — not this
report's as they stand.

## What is and is not claimed

- The slacks above are **provisional**: they check a `proposed` record whose
  3.0 ns figures are assumed. Nothing here meets a ratified spec row; the
  manifest cites nothing in this directory.
- The corner set is the five 3.3 V corners the cited run itself declared —
  `klt signoff` grades exactly that set, nothing wider.
- No SPEF-annotated result and no wire RC of any kind (every interconnect
  delay is zero — see the
  [interconnect section](#interconnect-basis-zero-wire-rc-standalone-vs-estimated-wire-rc-in-flow)
  above); no clock-tree-real (propagated) clock, no on-chip-variation
  derating: the run is ideal-clock, cell-delay-only STA.
- The same constraints now also run inside `klt place-and-route`
  ([`layout/pnr/`](../../layout/pnr/README.md)), whose report covers all 15
  library corners including other-supply rows out of this budget's set, and
  whose timing **includes** estimated wire RC — so its setup slacks on
  these five corners are 0.28–0.78 ns lower than this run's (measured
  reason: interconnect, above).
