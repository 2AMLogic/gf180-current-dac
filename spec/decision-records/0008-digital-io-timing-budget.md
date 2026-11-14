# 0008: Digital I/O timing budget

- **Status**: proposed
- **Date**: 2026-11-14
- **Decided by**: pending operator review (issue #68)

## Context

The update-rate row of [`../target-spec.md`](../target-spec.md) grades
"decoder, retiming latches and cell switches meet timing at this clock" at PVT,
but the spec states no timing at the digital partition's boundary. The
manifest's `partition_boundary` text for that partition
(`manifests/gf180-current-dac.signoff.json`) is "thermometer decoder and
retiming latches: the synthesized logic that turns the input code into per-cell
switch controls, **ending at the switch-driver inputs**".

`dac_digital` has no register-to-register path. Every path is a primary input
to a flop `D`, or a flop `Q` to a primary output. So a clock alone constrains
nothing: `layout/pnr/request.json` gives `clock_port: clk` and
`clock_period_ns: 10.0` and no I/O delays, and
`layout/pnr/dac_digital.report.json` reports `timing_status: unconstrained` in
all 35 places it appears, with `worst_setup_slack_ns` and
`worst_hold_slack_ns` both at the `1e+39` sentinel and `clock_skew_ns` 0.
`rtl/README.md` records that `klt synthesize` reports `timing: null` and that
no STA has been run. There is nothing to run static timing against.

CLAUDE.md: do not substitute an assumed value without a decision record. This
record is that decision record. It ratifies nothing, changes no row of
`../target-spec.md`, edits no request, and runs nothing.

Structural facts below are as of `d64d4bc`, 2026-11-14. Library figures are
from the PDK revision pinned in `sim/pdk.json`
(`f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7`).

## Decision

The 10 ns update period is split three ways: an arrival allowance for the
input code, an equal required-time reservation for the outputs, and what is
left inside the block.

| Field | Value | Where it lands | Source |
|---|---|---|---|
| clock period | 10.0 ns | `constraints.clock_period_ns` (already set) | **sourced**: the 100 MS/s update-rate row of [`../target-spec.md`](../target-spec.md), itself still PROPOSED per [DR-0001](0001-target-spec-ratification.md) |
| input arrival window, `din[9:0]` | 3.0 ns after the `clk` edge | `constraints.input_delay_ns` | **assumed, no source** |
| required output time, `t_q[62:0]` and `b_q[3:0]` | valid 3.0 ns before the next `clk` edge, at the switch-driver inputs | `constraints.output_delay_ns` | **assumed, no source** |
| internal allowance, each side | 10.0 - 3.0 = 7.0 ns | derived, not a field | arithmetic of the three rows above |

**Assumed, no source** — what the two 3.0 ns figures rest on, stated plainly:

| Figure | Why there is no source | Why 3.0 ns |
|---|---|---|
| `input_delay_ns` = 3.0 | `din[9:0]` is a boundary input. No upstream block exists in this repo or in a pinned sibling, and no spec row says when the code arrives. | 30 % of the period, a conventional allowance for an undesigned off-block source. |
| `output_delay_ns` = 3.0 | The consumer is the analog switch drivers, whose sizing is itself assumed ([DR-0006](0006-analog-schematic-sizing-assumptions.md)) and whose crossing point is not designed. There is no driver model to derive a required time from. | Symmetric with the input side; generous for the 2-to-3 inverter stages DR-0006 describes, and so safe for the digital side to meet. |

Neither number is measured, simulated, or derived from a driver model. They
are a decision about how to divide the period, taken so that static timing can
run at all, and they are the first thing to revisit once either neighbour is
designed.

### One scalar per side is sufficient here

The pinned `klt` applies a single `input_delay_ns` to every non-clock input and
a single `output_delay_ns` to every output; per-port maps are deliberately out
of scope at that interface. That is sufficient for this block, for structural
reasons rather than by luck:

- **Outputs.** All 67 flops in `synth/out/dac_digital/dac_digital_synth.v` are
  `gf180mcu_fd_sc_mcu7t5v0__dffq_1`, and all 67 of their `Q` pins drive a
  `t_q`/`b_q` bit **directly** — no buffer and no logic in between. So the
  required output time is the same for `t_q[62:0]` and `b_q[3:0]` because both
  groups launch from the same cell type on the same edge through nothing. This
  is one number for one reason, not two numbers that happen to coincide.
- **Inputs.** The input side genuinely has two different paths: `din[9:4]`
  through the combinational `thermo_decoder`, and `din[3:0]` straight to four
  flop `D` pins with no logic at all (`.D(din[0])` through `.D(din[3])`). One
  scalar governs both because the decoder path is the tighter of the two; the
  binary path is slack by comparison.

### Hold

A single scalar `set_input_delay` with no `-min`/`-max` sets min and max
alike, so the input hold check is `3.0 ns + t_comb >= t_hold`. The worst
`dffq_1` hold requirement in the table below is 0.097 ns, so hold is met by the
arrival allowance alone and this budget carries no min-delay padding. If the
input delay is ever reduced towards zero, hold stops being free and must be
re-checked.

### Library figures these numbers were graded against

`gf180mcu_fd_sc_mcu7t5v0__dffq_1`, the only flop in the netlist (67
instances), from
`<PDK_ROOT>/ciel/gf180mcu/versions/f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__<corner>.lib`.
Library units are `time_unit : 1ns` and `capacitive_load_unit(1, pf)`. Values
are the **first entry of each 10x10 NLDM table**, in ns. Two table shapes are in
play and their second axes are not the same quantity. The two delay columns come
from a `tmg_ntin_oload_10x10` table, whose axes are `input_net_transition`
(`index_1` = 0.02 ns, the sharpest input transition) and
`total_output_net_capacitance` (`index_2` = 0.001 pF, the minimum output load).
The four constraint columns come from a `cnst_ctin_rtin_10x10` table, which has
no load axis at all: its axes are `constrained_pin_transition` (`index_1` =
0.02 ns, the sharpest `D` transition) and `related_pin_transition` (`index_2` =
0.02 ns, the sharpest transition on the related pin, `CLK`). The figures are:

| corner | `clk`->`Q` rise | `clk`->`Q` fall | `D` setup rise | `D` setup fall | `D` hold rise | `D` hold fall |
|---|---|---|---|---|---|---|
| `tt_025C_3v30` | 0.9773 | 0.858 | 0.372 | 0.389 | 0.034 | 0.069 |
| `ss_n40C_3v00` | 1.446 | 1.238 | 0.521 | 0.550 | 0.029 | 0.097 |
| `ss_125C_3v00` | 2.000 | 1.722 | 0.801 | 0.870 | 0.052 | 0.097 |
| `ff_125C_3v60` | 0.7779 | 0.6961 | 0.292 | 0.315 | 0.046 | 0.080 |
| `ff_n40C_3v60` | 0.5483 | 0.4946 | 0.189 | 0.195 | 0.029 | 0.057 |

The decoder is three levels of logic deep. Walking the `thermo_decoder` module
of `synth/out/dac_digital/dac_digital_synth.v` back from each of its 63 `t[i]`
outputs (100 cells in that module), 61 outputs sit at 3 levels, one at 2 and
one at 0, and the deepest chain is `nor2_4` -> `buf_2` -> `nand2_1`. Summing
those three cells' first table entries gives 0.4858 ns at `tt_025C_3v30` and
0.9419 ns at `ss_125C_3v00`.

Only the `3v00` / `3v30` / `3v60` triplet of the 15 corners in that directory
is at the 3.3 V supply [DR-0002](0002-device-flavor-and-supply.md) fixes; the
`1v62`/`1v80`/`1v98` and `4v50`/`5v00`/`5v50` corners are other supplies and
are not part of this budget's PVT set. The 15 corners in the report are exactly
the 15 `.lib` files in that directory.

### These figures do not confirm the budget, and cannot

The first entry is the optimistic end of either table shape — minimum load for
the delay tables, sharpest transitions for the constraint tables — not a worst
case, so the figures above are indicative of order of magnitude only. The other
end of the delay tables is no better as a bound: at `ss_125C_3v00` the three
chain cells' table **maxima** sum to 37.5 ns, and `clk`->`Q` reaches 11.5 ns,
because `index_1` there runs out to a 15.6 ns input transition and `index_2` to
0.3545 pF — neither of which a routed 3-level decoder driving a single `D` pin
of 0.002342 pF presents.

So neither end of the NLDM tables bounds the real paths. Whether 7.0 ns per
side is actually met is answerable only by static timing on the routed design
with the actual transitions and loads — which is exactly the run this record
exists to make possible. **Nothing here is a timing-closure claim.**

## What this budget does not cover

The budget stops at the switch-driver **inputs**, as the manifest's boundary
text does. Two effects past that point are disclosed as unmodelled elsewhere in
the repo and are **not** inside this budget:

- **Skew across the 134 element-to-driver wires.** `layout/README.md`: "The 134
  element-to-driver nets have different lengths (42 + 38 channel tracks, M5
  slots at different x), so the gate-drive skew between elements is unequal and
  unmodelled. The drivers are not part of the matched array." (134 is two nets,
  `sp` and `sn`, for each of the 67 `driver` instances the same file counts off
  the stream.)
- **Driver crossing point.** [DR-0006](0006-analog-schematic-sizing-assumptions.md):
  "sp has two inverter stages, sn three, so sn lags sp by one stage. Crossing
  point is not designed."

Consequently a met `output_delay_ns` is **not** a claim about when current
actually steers at a cell. It says only that the decoder's outputs are stable
at the partition boundary with 3.0 ns to spare. Also outside this budget:
clock-tree insertion delay and skew beyond what place-and-route reports
(`clock_skew_ns` is 0 in the unconstrained report, which is a consequence of
there being no timing to analyse, not a measurement), input transition times at
`din`, and the analog cell switches themselves.

## What must be re-run once this is accepted

None of this was run for this record, and the committed evidence is unchanged
by it:

1. **Place-and-route with the constraints** — add `input_delay_ns` and
   `output_delay_ns` to `constraints` in `layout/pnr/request.json` and rerun
   `layout/pnr/run.sh`, producing a new `dac_digital.gds`,
   `dac_digital.report.json` (where `timing_status` should no longer be
   `unconstrained`) and `dac_digital.asbuilt.v`.
2. **Static timing** over the 3.3 V corners, for the constrained slacks the
   spec row needs. `klt sta` exists at the pinned klt commit
   (`layout/toolchain.json`, `f9039fd7244e977325c351a5780acbf1cee383fb`) but is
   **not** in that file's `klt_required_commands`, whose contract is that every
   `layout/` runner looks each entry up in `klt --help` and fails loudly. Adding
   `sta` there is a prerequisite of this run, not part of this record.
3. **DRC** of the new digital stream (`layout/drc/run.sh`, `evidence/item3-digital.json`).
4. **LVS** of the new stream against the new as-built netlist
   (`verification/lvs/`, the `4.digital` evidence item).
5. **ERC** of the new stream (`verification/erc/`, `digital.spec.json`, the
   `11.digital` evidence item).

Steps 3 to 5 are required because step 1 rewrites the stream: constrained
timing will change placement and routing, so the existing clean DRC, matching
LVS and clean ERC verdicts do not carry over. Do not cite the current
`fmax_mhz` from the unconstrained report as evidence for any of this; it is not
slack-checked.

## Alternatives considered

- **Derive the delays from the unconstrained report's `fmax_mhz`**: rejected.
  With every slack at the `1e+39` sentinel that figure is not slack-checked,
  and `layout/pnr/README.md` already says not to cite it.
- **Add the delays straight to `layout/pnr/request.json` and rerun**: rejected.
  That is this issue's out-of-scope, and a budget with no record is the gap
  this record closes — the numbers are assumptions and must be visible as such.
- **Per-port delay maps**: rejected. Not expressible at the pinned klt
  interface, and unnecessary: one scalar per side is correct here for the
  structural reasons given above.
- **Wait for `klt sta` results and write the budget from them**: rejected. The
  constraints are the input to that run, not its output. Circular.
- **Derive the delays from the liberty tables instead of assuming them**:
  rejected. Neither end of the NLDM tables bounds a routed path, as shown
  above; a figure derived that way would look sourced while being no better
  grounded than the stated assumption.
- **Relax the 100 MS/s row to whatever the block turns out to meet**: rejected.
  CLAUDE.md: agents do not relax the ratified spec to make results pass, and
  the fallback tier is a spec decision, not a timing-budget one.

## Consequences

Static timing becomes runnable on the digital partition for the first time, and
the update-rate row becomes gradeable rather than vacuous. In exchange, two of
the three numbers behind every future slack figure are assumptions, so any
slack reported against them inherits that status: it is a slack against an
assumed boundary, not against a characterised one. Every such figure must say
so and cite this record.

The budget is deliberately conservative on both sides, which means the block
may be reported as failing timing it would in fact meet against a real
neighbour. That is the right direction for an assumption to err, but it is a
reason to revisit these numbers — not to loosen them silently — once
`gf180-bandgap`, `gf180-opamp` or an upstream code source fixes the real
arrival and required times. Revisiting them means a new record superseding this
one, and re-running all five steps above.
