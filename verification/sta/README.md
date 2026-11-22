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
the committed `dac_digital.gds` (sha256
`93901ab747d6c4ab3a051a3d84d52c869a619018face0dfdbe74259b593aa7f8`) and
`dac_digital.asbuilt.v` (sha256
`bb51f8880448be28aebd37eece82494295dcaf61ea231ba3012f6db8bb1ffa4b`).
[`layout/pnr/run.sh --check`](../../layout/pnr/README.md#regenerate) reruns
the route, byte-compares the regenerated GDS and DEF with the committed
copies, and checks the five-corner STA report's `provenance.input.content_hash`
against the committed DEF's SHA-256.

No post-route SPEF exists from the P&R flow itself (`spef_path` is null and
every corner's `electrical_checks.parasitics_source` is `"none"` — delays
are OpenROAD's DEF/LEF-based estimates). Clock is ideal
(`clock_mode: "ideal"`), no uncertainty, no SDF.

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

## What is and is not claimed

- The slacks above are **provisional**: they check a `proposed` record whose
  3.0 ns figures are assumed. Nothing here meets a ratified spec row; the
  manifest cites nothing in this directory.
- The corner set is the five 3.3 V corners the cited run itself declared —
  `klt signoff` grades exactly that set, nothing wider.
- The five-corner run is ideal-clock DEF/LEF STA: no SPEF, no
  clock-tree-real (propagated) clock, no on-chip-variation derating. The
  single-corner SDF-export run above is SPEF-annotated but inherits the
  same caveats (ideal clock, no OCV) and the same provisional budget.
- The same constraints now also run inside `klt place-and-route`
  ([`layout/pnr/`](../../layout/pnr/README.md)), whose report covers all 15
  library corners including other-supply rows out of this budget's set.
