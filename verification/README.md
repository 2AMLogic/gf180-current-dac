# verification

Committed verification evidence, one subdirectory per kind. The verdict of
record is [`manifests/gf180-current-dac.signoff.json`](../manifests/gf180-current-dac.signoff.json).

| Directory | Holds | T1 item |
|---|---|---|
| [`erc/`](erc/README.md) | `klt erc` supply specs and reports, one per partition | 11 (power delivery, structural) |
| [`lvs/`](lvs/README.md) | `klt lvs` requests and reports, one per partition, plus the digital gate netlist | 4 (LVS) |
| `rtl/` | Icarus testbench `tb_dac_digital.v` and its result (`PASS: 1024 codes`) for the digital partition | 1 (digital design sources) |
| `functional/` | `klt functional-verification` cocotb suite for `dac_digital`, its three request documents, the two zero-delay reports (RTL and synthesized netlist) and the SDF-annotated post-route report | 7 (digital) |
| [`sta/`](sta/README.md) | multi-corner `klt sta` on the routed `dac_digital` DEF over DR-0008's five 3.3 V corners, plus the extracted SPEF and the single-corner SDF export the item-7 run consumes | 5 (digital) — not cited: budget is `proposed` |
| [`pex/`](pex/README.md) | One `klt extract --parasitics` probe of the analog array — does extraction complete at array scale, and what does it produce | 7 (post-layout) — not claimed |

Corner and Monte Carlo results (items 5–8, analog) and the analog
post-layout runs are not here yet; they wait on spec ratification (#2). The
digital timing half of item 5 exists ([`sta/`](sta/README.md)) but is
provisional — it checks a `proposed` budget (DR-0008), so the manifest cites
nothing in it; the citation waits on #2. The digital post-layout functional
run (item 7) is the SDF-annotated report in [`functional/`](functional/),
cited; `pex/` remains a probe of the extraction tooling, not a post-layout
result: it runs no simulation and the signoff manifest cites nothing in it.

## `functional/`

A cocotb regression over `dac_digital`, run through `klt functional-verification`
(Icarus) once against the RTL, once against the synthesized gate-level
netlist, and once against the routed as-built netlist with SDF
back-annotation. The three requests differ in `sources`; the annotated one
adds `options.sdf` and selects the DR-0008 drive/sample schedule through the
request's `env` field (`DAC_TB_TIMING=dr0008`). All three run the same test
module, `functional/test_dac_digital.py`.

| File | Content |
|---|---|
| `functional/test_dac_digital.py` | the suite: 4 tests over all 1024 input codes, two timing schedules |
| `functional/dac_digital.rtl.request.json` | RTL request (`rtl/thermo_decoder.v`, `rtl/dac_digital.v`) |
| `functional/dac_digital.netlist.request.json` | netlist request (PDK cell models, then `synth/out/dac_digital/dac_digital_synth.v`) |
| `functional/dac_digital.asbuilt.request.json` | post-route request (PDK cell models, then `layout/pnr/dac_digital.asbuilt.v`, `options.sdf`, `env` DR-0008 schedule) |
| `functional/dac_digital.rtl.report.json` | committed RTL report (zero delay) |
| `functional/dac_digital.netlist.report.json` | committed netlist report (zero delay) |
| `functional/dac_digital.asbuilt.report.json` | committed annotated report — cited for `7.digital` |
| `functional/dac_digital.tt_025C_3v30.sdf` | the retained nominal-corner post-route SDF the annotated run loads |

The checks are those of `rtl/tb_dac_digital.v`, which stays in place as the
item-1 design sanity check; this is the `klt functional-verification` path
beside it, not a replacement. Over all 1024 codes: `t_q[i] == (din[9:4] > i)`
for i in 0..62 and `b_q == din[3:0]` read in one cycle; `t_q ^ prev_t`
exactly `1 << (din[9:4] - 1)` at each of the 63 major carries; outputs lagging
`din` by exactly one clock edge; and codes 0 and 1023 against literal
expectations. All three committed reports record `status: "pass"`, 4 of 4
tests passed, `failed_count` and `skipped_count` zero.

### Timing schedules

`test_dac_digital.py` carries two schedules, selected by the request's
top-level `env` (`DAC_TB_TIMING`):

- **Zero delay** (unset; the RTL and netlist requests): drive on the falling
  edge, sample 1 ns after the capturing rising edge. No SDF, no timing
  checked — the two original reports' schedule, unchanged.
- **DR-0008** (`dr0008`; the as-built request, per
  [`0008-digital-io-timing-budget.md`](../spec/decision-records/0008-digital-io-timing-budget.md),
  status `proposed`): on consecutive 10.0 ns cycles, drive the next code at
  +3.0 ns after each rising edge and check the code captured at that edge at
  +7.0 ns after it — one code per cycle, so throughput is unchanged and the
  one-edge latency is exercised while the next code is already present
  (drive A at 3 ns, capture A at 10 ns, drive B at 13 ns, check A at 17 ns,
  capture B at 20 ns, check B at 27 ns). Bring-up ends on a rising edge so the
  first +3 ns drive is edge-anchored, the testbench asserts every drive is
  3 ns after an edge and consecutive drives 10 ns apart, and the +7 ns sample
  is taken in the read-only phase of that timestep, after updates scheduled
  at +7 ns have settled. The `test_one_cycle_latency` check runs the same
  budget on explicit consecutive pairs.

### The annotated run and its SDF

The SDF is the nominal-corner post-route SDF from
[`sta/sdf.request.json`](sta/README.md#post-route-sdf-export-sdfsdfrequestjson):
`klt sta` (`sdf: true`, grading pin `0.9.0`) over the routed DEF retained
from the same P&R run as the committed GDS and as-built Verilog
(`36ea425f…` / `93901ab7…` / `bb51f888…`), with the SPEF extracted from that
GDS (`dffe8f25…`, 182 `*D_NET` blocks, annotation complete 182/182 in the
STA session). Retained copy sha256
`e08b63f84684aabe2f8c5458354887e94eb0c053290b0690e618955ff1aae340`,
equal to the producing report's `corners[0].sdf.content_hash`; OpenSTA
stamps a `(DATE …)` header, so a re-export's bytes differ — always compare
digests against the producing report, not a re-run. The functional request
names it request-relative (`dac_digital.tt_025C_3v30.sdf`), corner `typ`.

**Annotation coverage** — entries present in the input vs confirmed applied,
by class:

| Class | In the SDF | Dropped before/during annotation |
|---|---|---|
| `IOPATH` (cell delays, `min:typ:max`) | 469 | 0 — this population carries the run's real delay (e.g. `CLK→Q` 0.98–1.05 ns typ) |
| `INTERCONNECT` | 454 | 47 dropped as `zero_delay_bus_port_source_interconnect` (bit-selected top-level input ports, every `min:typ:max` member zero) |
| `TIMINGCHECK` sections (469 individual SETUP/HOLD/WIDTH/PERIOD checks) | 67 sections | `timingcheck` = 66 well-formed `TIMINGCHECK not supported` simulator warnings observed in the committed run (Icarus implements SDF delays but no SDF timing checks); a re-run by review observed 67 |

Limits of those counts, stated: Icarus exposes **no positive
"entries applied" count**, and the tool's counts are not an applied tally.
At the 0.9.0 pin the `timingcheck` figure is the number of recognized benign
simulator diagnostics (`TIMINGCHECK not supported` warnings) found in the
simulator log, not a count of sections the tool removed during
normalization; the 47 `zero_delay_bus_port_source_interconnect` entries, by
contrast, are the ones removed from the SDF before annotation. The SDF has
67 `TIMINGCHECK` sections; the committed run observed 66 such warnings and a
review re-run observed 67 on the same inputs. The cause of that one-count
variation is not established and is disclosed rather than explained. The
absence of other (malformed) `SDF WARNING`/`SDF ERROR` diagnostics is the
only applied-annotation evidence: the tool fails the run on any, so a
returned report passed that gate; it is not a simulator-reported tally.
Every `INTERCONNECT` triple in this SDF — dropped and kept alike
— is `(0.000:0.000:0.000)`: under the extraction's first-order lumped-RC
star model (median net R·C ≈ 0.05 ps, largest signal net ≈ 4.3 ps), the
net propagation delays OpenSTA computes are below the SDF timescale's
printed resolution, so the run's back-annotated delay content is the
SPEF-informed cell (`IOPATH`) delays; net delays are annotated as zero.
Known tool gap, disclosed not worked around: the raw report echoes
`options.sdf.file` as the producer's absolute path
([2AMLogic/klayout-tools#5784](https://github.com/2AMLogic/klayout-tools/issues/5784));
the committed request keeps the portable relative path.

**What the annotated pass does and does not claim.** The report records
`environment.sdf.annotated: true`, `corner: "typ"`, `entries: "all"`,
`partial: true` with exactly the two dropped classes above, and 4 of 4
tests passing on the DR-0008 schedule — the manifest cites it for T1 item 7
digital and `klt signoff` (0.9.0) grades that item `met`. The schedule it
checks is DR-0008's, a **proposed** record with assumed figures, and the
spec rows behind the logical checks (6 + 4 segmentation, one-cycle latency)
are proposed like the rest of DR-0001: the pass is a simulation against
proposed spec rows, not a ratified-spec verdict, and no setup/hold
*violation reporting* exists on this path (Icarus models SDF delays only;
slack numbers remain STA's job — see [`sta/README.md`](sta/README.md)).
Simulated, not measured.

### What the zero-delay runs do **not** claim

- **Functional timing model.** Both zero-delay reports have `environment.sdf`
  set to `null`. The separate [routed STA](sta/README.md) checks the proposed
  100 MS/s budget; the annotated report above is the post-route delay leg.
- **No signoff-manifest item.** Neither zero-delay report is cited in
  [`../manifests/gf180-current-dac.json`](../manifests/gf180-current-dac.json).
  T1 item 5 wants bit-exact functional evidence against a ratified spec, and
  the spec rows these checks exercise (6 + 4 segmentation, one-cycle latency)
  are still **proposed** (DR-0001, ratification in #22 / PR #29, as
  `rtl/README.md` records). The annotated report is the one cited (item 7
  digital).
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
sed "s|\$PDK_ROOT|$PDK_ROOT|g" verification/functional/dac_digital.asbuilt.request.json \
    > verification/functional/dac_digital.asbuilt.run.request.json
$FV verification/functional/dac_digital.asbuilt.run.request.json --format json \
    > verification/functional/dac_digital.asbuilt.report.json
```

The as-built request needs `iverilog` 13.0 or newer (it probes `-V`): the
SDF build compiles with `-gspecify -ginterconnect`, and the latter flag does
not exist before 13.0. Its SDF input is the retained
`dac_digital.tt_025C_3v30.sdf` beside it — no environment variable, so only
the PDK cell-model paths go through the `sed`. If the SDF is regenerated
(see [`sta/README.md`](sta/README.md#post-route-sdf-export-sdfsdfrequestjson)),
update the digest recorded there and re-run; the report's
`environment.sdf.dropped` classes are the quick check that the annotation
shape is unchanged.

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
