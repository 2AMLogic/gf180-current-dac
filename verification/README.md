# verification

Committed verification evidence, one subdirectory per kind. The verdict of
record is [`manifests/gf180-current-dac.signoff.json`](../manifests/gf180-current-dac.signoff.json).

| Directory | Holds | T1 item |
|---|---|---|
| [`erc/`](erc/README.md) | `klt erc` supply specs and reports, one per partition | 11 (power delivery, structural) |
| [`lvs/`](lvs/README.md) | `klt lvs` requests and reports, one per partition, plus the digital gate netlist | 4 (LVS) |
| `rtl/` | Icarus testbench `tb_dac_digital.v` and its result (`PASS: 1024 codes`) for the digital partition | 1 (digital design sources) |
| `functional/` | `klt functional-verification` cocotb suite for `dac_digital`, its two request documents and both zero-delay reports (RTL and synthesized netlist) | none cited |

Corner, Monte Carlo and post-layout results (items 5–8) are not here yet; they
wait on spec ratification (#2).

## `functional/`

A cocotb regression over `dac_digital`, run through `klt functional-verification`
(Icarus) once against the RTL and once against the synthesized gate-level
netlist. The two requests differ only in `sources`; both run the same test
module, `functional/test_dac_digital.py`.

| File | Content |
|---|---|
| `functional/test_dac_digital.py` | the suite: 4 tests over all 1024 input codes |
| `functional/dac_digital.rtl.request.json` | RTL request (`rtl/thermo_decoder.v`, `rtl/dac_digital.v`) |
| `functional/dac_digital.netlist.request.json` | netlist request (PDK cell models, then `synth/out/dac_digital/dac_digital_synth.v`) |
| `functional/dac_digital.rtl.report.json` | committed RTL report |
| `functional/dac_digital.netlist.report.json` | committed netlist report |

The checks are those of `rtl/tb_dac_digital.v`, which stays in place as the
item-1 design sanity check; this is the `klt functional-verification` path
beside it, not a replacement. Over all 1024 codes: `t_q[i] == (din[9:4] > i)`
for i in 0..62 and `b_q == din[3:0]` read in the same cycle; `t_q ^ prev_t`
exactly `1 << (din[9:4] - 1)` at each of the 63 major carries; outputs lagging
`din` by exactly one clock edge; and codes 0 and 1023 against literal
expectations. Both committed reports record `status: "pass"`, 4 of 4 tests
passed, `failed_count` and `skipped_count` zero.

### What this does **not** claim

- **No timing.** `environment.sdf` is `null` in both reports: these are
  zero-delay functional runs. No SDF is back-annotated and no STA has been run,
  so nothing here says the partition meets 100 MS/s.
- **No signoff-manifest item.** Neither report is cited in
  [`../manifests/gf180-current-dac.json`](../manifests/gf180-current-dac.json).
  T1 item 5 wants bit-exact functional evidence against a ratified spec and
  item 7 an SDF-annotated post-route run; the spec rows these checks exercise
  (6 + 4 segmentation, one-cycle latency) are still **proposed** (DR-0001,
  ratification in #22 / PR #29, as `rtl/README.md` records). The item-7 run on
  `layout/pnr/dac_digital.asbuilt.v` is separate work.
- **Not a measurement.** Simulated, not measured.

### Rerun

Needs `iverilog` on `$PATH`. `klt` runs through a throwaway environment at the
pin in [`../scripts/check_signoff.sh`](../scripts/check_signoff.sh) — note the
`[functional-verification]` extra, without which the command exits with
`cocotb is not installed`, so the bare `$KLT` alias of the root README does not
work here. Run from the repo root:

```
FV="uvx --from klayout-tools[functional-verification]==0.9.0 klt functional-verification"
$FV verification/functional/dac_digital.rtl.request.json --format json \
    > verification/functional/dac_digital.rtl.report.json
```

The netlist request names the PDK cell models relative to `$PDK_ROOT`, which
klt does **not** expand inside `sources`. As with
`synth/out/dac_digital/synth_dac_digital.ys`, the committed file is the artifact
and a machine-local sibling is what runs; it must stay in this directory,
because request-relative source paths resolve against the request's own
directory:

```
export PDK_ROOT=~/.ciel/ciel/gf180mcu/versions/f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
sed "s|\$PDK_ROOT|$PDK_ROOT|g" verification/functional/dac_digital.netlist.request.json \
    > verification/functional/dac_digital.netlist.run.request.json
$FV verification/functional/dac_digital.netlist.run.request.json --format json \
    > verification/functional/dac_digital.netlist.report.json
```

`*.run.request.json` is gitignored, like `*.run.ys`. Run artifacts (results
XML, logs, build directory) land in `.klt/` next to the request, which is also
gitignored; pass `-o <dir>` to put them elsewhere.

The two-file dance is a tool gap, not a design constraint: klt does not expand
environment variables in a request's path fields, so a request naming a
host-specific PDK path cannot be the request that runs. Filed generically as
[`2AMLogic/klayout-tools#5678`](https://github.com/2AMLogic/klayout-tools/issues/5678);
if it is fixed, the committed netlist request becomes directly runnable and the
`sed` step and the ignore rule both go away.

`klt functional-verification` itself runs this design without a workaround, on
both the RTL and the netlist, so no capability gap blocks this evidence. The
mutation-proposals usability gap met while checking that the suite bites is
[`2AMLogic/klayout-tools#5679`](https://github.com/2AMLogic/klayout-tools/issues/5679).

### The suite bites

A suite that passes against a wrong expectation is not evidence, so both
directions were checked (in a scratch directory, nothing written here):

- Perturbing one expected value (`din[9:4] > i` to `> i + 1`) turns the RTL run
  into `status: "fail"`, 2 of 4 tests failing. `test_boundary_codes` keeps
  passing by design — it uses literal expectations, independent of the
  `expected_*` helpers.
- `klt functional-verification --mutations` on three byte-exact design
  mutations — thermometer comparison off by one, binary path on the wrong `din`
  slice, and the retiming flop bank collapsed to combinational — reports
  `killed_count: 3`, `survived_count: 0`, `mutation_score: 1.0`. The
  combinational mutant is killed by `test_one_cycle_latency` specifically, so
  that check is load-bearing rather than redundant.

Run artifacts for both are not committed; the commands are above and in the
pull request that added this directory.
