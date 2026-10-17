# sim

Pinned PDK and simulator toolchain, plus a smoke run that proves the models
load and the corner and Monte Carlo paths run. Toolchain evidence only: it
makes no linearity claim and the placeholder device is not a design choice
(cell topology and sizing belong to the spec, issue #2).

## Pins

| File | Pins |
|---|---|
| `pdk.json` | gf180mcu variant `gf180mcuD` (same as `gf180-bandgap`) and the exact PDK revision (ciel/volare hash), with the fetch command |
| `toolchain.json` | ngspice floor, Python floor, PDK revision |
| `../layout/toolchain.json` | `klt` at a full klayout-tools commit SHA; `klt_required_commands: ["drc"]` |

`python -m sim.harness check` compares the installed ngspice, Python and PDK
revision with these files and exits non-zero, naming each drifted item.
`run smoke` runs the same check first. Pin verification covers the local host
only: a batch-fleet runner has its own PDK and ngspice build. `run smoke`
copies the runner's `pdk_stamp_comparison` and `engine_build_comparison`
(status and worker stamp) from `environment.remote` into the record, and does
not fail on a `mismatch`; read those lines before trusting a fleet number as
coming from the pinned revision.

## Fetch the PDK

```
ciel enable --pdk gf180mcu f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
export PDK_ROOT=~/.ciel      # the directory that holds gf180mcuD
```

The hash was read from a host that already had it; that `ciel` fetches this
revision on a clean machine is not yet confirmed.

## Run (from the repo root)

```
python -m sim.harness check
python -m sim.harness run smoke
python -m unittest sim.harness.test_check      # harness tests
```

`run smoke` hands two requests in `smoke/` to `klt sim`: the five MOS corners
`tt/ff/ss/fs/sf` (PDK sections `typical/ff/ss/fs/sf`) and an N = 50 Monte
Carlo at `tt`. It passes no `--backend`, so `KLT_SIM_BACKEND` decides: on a
dispatch worker both go to the batch fleet and the job id lands in
`environment.remote`. A failed submit is an error, never a local fallback.
Output goes to `smoke/records/` as an append-only record (`<stamp>.md`, the
corner report, and the gzipped per-sample Monte Carlo report).

## Mismatch model

Monte Carlo uses the PDK's own `fets_mm` per-device terms, switched on by
`sw_stat_mismatch=1` with `sw_stat_global=0` (local mismatch only).
`klt sim` does not set these gf180mcu switches, so `smoke/cs_tb_mc.spice` does.
No gradient is modelled. The smoke run fails if the spread is zero.
