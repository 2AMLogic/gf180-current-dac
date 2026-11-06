# verification

Committed verification evidence, one subdirectory per kind. The verdict of
record is [`manifests/gf180-current-dac.signoff.json`](../manifests/gf180-current-dac.signoff.json).

| Directory | Holds | T1 item |
|---|---|---|
| [`erc/`](erc/README.md) | `klt erc` supply specs and reports, one per partition | 11 (power delivery, structural) |
| [`lvs/`](lvs/README.md) | `klt lvs` requests and reports, one per partition, plus the digital gate netlist | 4 (LVS) |
| `rtl/` | Icarus testbench `tb_dac_digital.v` and its result (`PASS: 1024 codes`) for the digital partition | 1 (digital design sources) |

Corner, Monte Carlo and post-layout results (items 5–8) are not here yet; they
wait on spec ratification (#2).
