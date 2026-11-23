# 0009: Layout klt pin and primitive reproducibility

- **Status**: proposed
- **Date**: 2026-11-23
- **Decided by**: pending operator review (issue #164)

## Context

`layout/gen_prims.sh --check` is the only gate tying the committed
primitives in `layout/prims/` to the size owner (`design/gen_analog.py`,
DR-0006): it regenerates all five primitives and compares geometry with
`klt diff`. The committed primitives were written by klt
`0.8.1.dev61+gb5c72a9333ff` (`klayout_version 0.30.12`, PDK `open_pdks
f6eeac7dad08…`; recorded in each `layout/prims/prim_*.report.json`), while
`layout/toolchain.json` pins `klt_install` at commit `f9039fd7244e` (klt
`0.8.1.dev86`) and the manifest grading pin is `klayout-tools==0.9.0`
(`scripts/check_signoff.sh`). Nothing in the repo said what `--check` does
at a 0.9.x klt, so a future pin move would turn the gate red on all five
primitives at once and read as a geometry regression when it is a
tool-version change.

## Decision

The layout/ `klt_install` pin stays on the 0.8.1 lineage (`f9039fd7244e`).
`gen_prims.sh --check` reporting `differs:` for **all five** primitives at
once under klayout-tools 0.9.x or later is the expected tool-version
difference measured below, not a size drift against DR-0006. Moving the pin
means regenerating `layout/prims/` (accepting the new child-cell names),
which per the measurement below leaves the array stream itself unchanged
but rewrites the committed primitive files and reports; that regeneration
is a separate decision when a pin move is actually warranted.

Any INL/DNL or extraction claim resting on `layout/prims/` is pinned to
klt `0.8.1.dev61+gb5c72a9333ff` geometry: the committed `.gds` files are
that build's output (re-verified equivalent at the `f9039fd7244e` pin,
below), and no such claim exists yet (no extraction, no INL/DNL number —
`layout/README.md`).

## Measurement

Everything in this section is a **measured** run on the builder host,
2026-11-23; nothing is simulated. PDK revision
`f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7` (the `sim/pdk.json` pin, the
same revision the committed reports record), resolved from the `~/.ciel`
root; only `PDK_ROOT` needed exporting. klt was run from throwaway venvs,
never the host tool.

| klt build (how installed) | `layout/gen_prims.sh --check` | per-primitive result |
|---|---|---|
| `0.8.1.dev86+gf9039fd7244e` (pin, git `@f9039fd7244e`) | exit 0 | all five pass |
| `0.9.0` (PyPI) | exit 1 | `differs:` all five |
| `0.9.1` (PyPI) | exit 1 | `differs:` all five |
| `0.9.2` (PyPI) | exit 1 | `differs:` all five |
| `0.9.3.dev3673+g8848cc30fe52` (git main, 2026-11-23) | exit 1 | `differs:` all five |

So the committed primitives reproduce at the pin (this re-run also closes
the dev61-wrote / dev86-pins gap: the pin passes, not just the writer), and
do not reproduce under any released 0.9.x — the issue's premise, confirmed.

Cause, isolated on `prim_cs` and re-checked as noted:

- At 0.9.0 the raw `klt diff` is a child-cell rename and nothing else:

  ```
  status: different
  cells only in a: mos_array
  cells only in b: prim_cs__core
  cell prim_cs:
    instances: 1 only in a, 1 only in b
  ```

  Renaming the regenerated child cell `prim_cs__core` back to `mos_array`
  (klayout Python API, `gds2_write_timestamps = False`) makes `klt diff`
  report `status: equivalent` (exit 0) — **measured for all five
  primitives at 0.9.0, and for `prim_cs` at 0.9.2** (dbu still 0.0005
  there). `klt diff` "never ignores … cell names", so the gate is red on
  the name alone. The rename is consistent with the already-open
  klayout-tools #4251 (child-cell name collides across `gen mos_array`
  outputs); the introducing commit was not bisected — the release-level
  boundary above is what the pin decision needs. `0.9.1` was not
  rename-isolated separately; it sits between two re-checked neighbours
  with the identical `--check` result.
- At git main (`0.9.3.dev3673`) there is a second, geometry-affecting
  change: after the same rename, `prim_cs` still differs — `dbu_um:
  a=0.0005 b=0.001`, with shape differences on layers 22/0, 30/0, 31/0,
  32/0, 33/0, 34/0 of cell `mos_array` — and the report gains
  `subcell_naming_scheme: "core-suffix-v1"`. `layout/gen_array.py`
  hard-asserts primitive dbu 0.0005 (`DBU`), so primitives from that build
  are refused outright, not just rediffed. This is an unreleased dev line;
  it was not checked against any upstream announcement.

Downstream effect, measured in a scratch checkout: with `layout/prims/`
regenerated at 0.9.0, `layout/gen_array.py --check` exits 0 and the array
stream is byte-identical to the committed one (relaxed klayout mode,
0.30.14 vs the 0.30.12 pin, `provenance.klayout_version` excluded with the
NOTE). `gen_array.py` flattens each primitive's top cell, so the
child-cell rename does not propagate; only `layout/prims/*.gds` and
`*.report.json` change.

Commands as run (from the repo root; `<tag>` per row above):

```
uv venv /tmp/klt-<tag>
uv pip install --python /tmp/klt-<tag>/bin/python "klayout-tools @ git+https://github.com/2AMLogic/klayout-tools@f9039fd7244e977325c351a5780acbf1cee383fb"   # the pin
uv pip install --python /tmp/klt-<tag>/bin/python "klayout-tools==0.9.0"   # likewise 0.9.1, 0.9.2; git main for the dev build
PATH=/tmp/klt-<tag>/bin:$PATH \
  PDK_ROOT=$HOME/.ciel/ciel/gf180mcu/versions/f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7 \
  layout/gen_prims.sh --check
```

Isolation (0.9.0 row): `klt gen mos_array --pdk gf180mcuD --params
"$(python3 design/gen_analog.py --prim-params prim_cs)" --cell-name prim_cs
-o /tmp/primdiff/prim_cs.gds --format json`, rename `prim_cs__core` to
`mos_array` via `Layout.rename_cell`, then `klt diff
layout/prims/prim_cs.gds /tmp/primdiff/prim_cs_renamed.gds`.

## Consequences

- `gen_prims.sh --check` is meaningful only at the 0.8.1-lineage pin; read
  a five-primitive `differs:` at 0.9.x against this record before touching
  sizes (DR-0006 is unaffected by all of this).
- A pin move to released 0.9.x is a primitives-file rewrite plus report
  update; the array stream, its envelope and the switching table are
  unaffected (measured above). A move to the current dev line additionally
  needs the dbu question answered first.
- The grading pin (`scripts/check_signoff.sh`) and `klt_install` remain
  separate facts that move independently (toolchain.json, issue #56 note).
- No claim in this repo changes: no INL/DNL or extraction number exists,
  and none is added here.

## Alternatives considered

- Regenerate `layout/prims/` at 0.9.x now: rejected — rewrites committed
  geometry files (and their reports) for no current need; the pin move gets
  its own record when something needs 0.9.x features.
- Leave the behaviour unrecorded: rejected — the next `differs:` reads as a
  size drift and sends someone hunting DR-0006 regressions that are not
  there.
- Bisect the exact introducing commit between `f9039fd7244e` and 0.9.0:
  not done; the measured release-level boundary answers the pin question.
  A PDK-revision explanation was ruled out by measurement: the pinned PDK
  (same revision as the committed reports) passes at the pin and differs
  only across the klt version axis.
