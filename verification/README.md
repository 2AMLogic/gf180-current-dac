# verification

Committed verification evidence, one subdirectory per kind. The verdict of
record is [`manifests/gf180-current-dac.signoff.json`](../manifests/gf180-current-dac.signoff.json).

| Directory | Holds | T1 item |
|---|---|---|
| [`erc/`](erc/README.md) | `klt erc` supply specs and reports, one per partition | 11 (power delivery, structural) |
| [`lvs/`](lvs/README.md) | `klt lvs` requests and reports, one per partition, plus the digital gate netlist | 4 (LVS) |
| `rtl/` | Icarus testbench `tb_dac_digital.v` and its result (`PASS: 1024 codes`) for the digital partition | 1 (digital design sources) |
| [`pex/`](pex/README.md) | One `klt extract --parasitics` probe of the analog array — does extraction complete at array scale, and what does it produce | 7 (post-layout) — not claimed |

Corner, Monte Carlo and post-layout results (items 5–8) are not here yet; they
wait on spec ratification (#2). `pex/` is a probe of the extraction tooling,
not a post-layout result: it runs no simulation and the signoff manifest cites
nothing in it.
