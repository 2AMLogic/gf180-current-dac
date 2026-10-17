# Probe: does the PDK draw mismatch per instance?

Evidence for one claim in `spec/target-spec.md`: the gf180mcuD `fets_mm`
terms are drawn once per subcircuit instance, so a unit cell must be a
separate instance in Monte Carlo, not `m=N` on one instance.

- Run: 2026-10-17, one corner (`typical`), local, single-process `ngspice -b`.
  ngspice-42 on the dispatch worker, **not** the ngspice-46 pinned in
  `sim/toolchain.json`; a fleet run would use the runner's own build. PDK
  `f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7` (`sim/pdk.json`).
- Switches: `sw_stat_global=0`, `sw_stat_mismatch=1` (local mismatch only).
- Device: `nfet_03v3` W = 2 u, L = 2 u, Vgs = Vds = 1.0 V (a bias point
  chosen for the probe, not a design point). 40 cells in each arrangement.
- Netlists: `probe/instance_m.sp` (one instance, `m=40`) and
  `probe/instance_inst.sp` (40 instances). `$PDK_VERSION_DIR` stands for
  `<PDK_ROOT>/ciel/gf180mcu/versions/<revision>`; substitute it before running.
- Method: 12 independent ngspice invocations of each netlist (ngspice reseeds
  per invocation), reading the total drain current.

| Arrangement | mean total I [uA] | sigma/mean over 12 runs [%] |
|---|---|---|
| 1 instance, `m=40` | 297.96 | 1.30 |
| 40 instances | 297.56 | 0.13 |

Reading: with `m=40` the total keeps the spread of a single device; with 40
instances it falls by about 10x, against 6.3x for an ideal 1/sqrt(40) (12
runs per row, so each sigma is good to roughly 20 %, which does not cover the
gap; the direction is clear, the factor is not established). The `m`
multiplier does not average mismatch; separate instances do.

This is a simulated result, not measured, and it is not a linearity claim.
