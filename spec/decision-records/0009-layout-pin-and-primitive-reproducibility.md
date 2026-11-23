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
means either regenerating `layout/prims/` (accepting the new child-cell
names) or first making the `gen_prims.sh` gate hierarchy-insensitive with
`klt diff --flattened` (see Alternatives considered). The rewrite is a
consequence of the gate's *current* cell-by-cell comparison, not of the pin
move as such. Per the measurement below the array stream itself is
unchanged either way; that choice is a separate decision when a pin move is
actually warranted.

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
  the name alone. The rename is the implemented resolution of
  klayout-tools #4251 (child-cell name collides across `gen mos_array`
  outputs), a gap this repo asked upstream to fix: #4251 is CLOSED
  (completed 2026-10-27), it reported the collision at
  `0.8.1.dev61+gb5c72a9333ff` — the build that wrote `layout/prims/` —
  and its accepted criterion is to rename the variant cell to
  `<cell_name>__core`, i.e. `prim_cs` → `prim_cs__core`. It is therefore
  permanent going forward, an expected consequence of our own request
  rather than unexplained drift; the introducing commit was not bisected —
  the release-level boundary above is what the pin decision needs. `0.9.1` was not
  rename-isolated separately; it sits between two re-checked neighbours
  with the identical `--check` result.
- At git main (`0.9.3.dev3673`) there is a second, geometry-affecting
  change: after the same rename, `prim_cs` still differs — `dbu_um:
  a=0.0005 b=0.001`, with shape differences on layers 22/0, 30/0, 31/0,
  32/0, 33/0, 34/0 of cell `mos_array` — and the report gains
  `subcell_naming_scheme: "core-suffix-v1"`. `layout/gen_array.py`
  hard-asserts primitive dbu 0.0005 (`DBU`), so primitives from that build
  are refused outright, not just rediffed. This is an unreleased dev line, and
  the dbu change is deliberate: klayout-tools #5721 (CLOSED, completed
  2026-11-22) reports that the default 0.0005 writer dbu is rejected by
  the gf180mcu native runset's own DBU rule (needs 0.001), filed against
  this PDK revision (`open_pdks f6eeac7dad08…`), and asks that the writer
  default to each PDK's required dbu. The blocker on a future pin move is
  on this repo's side: `layout/gen_array.py` hard-asserts `DBU = 0.0005`.

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

- `gen_prims.sh --check`, as written today (`klt diff` without
  `--flattened`), is meaningful only at the 0.8.1-lineage pin; read a
  five-primitive `differs:` at 0.9.x against this record before touching
  sizes (DR-0006 is unaffected by all of this).
- With the gate as it stands, a pin move to released 0.9.x needs a
  primitives-file rewrite plus report update. If the call site adopts
  `klt diff --flattened` first, the committed geometry can be verified
  against a 0.9.x regeneration without rewriting `layout/prims/` (at 0.9.0
  all five are `equivalent` once the child is renamed, measured above). The
  array stream, its envelope and the switching table are unaffected either
  way (measured above). A move to the current dev line additionally
  needs `layout/gen_array.py` moved off its hard-coded `DBU = 0.0005`
  (upstream #5721 already settled that the runset requires 0.001).
- The grading pin (`scripts/check_signoff.sh`) and `klt_install` remain
  separate facts that move independently (toolchain.json, issue #56 note).
- No claim in this repo changes: no INL/DNL or extraction number exists,
  and none is added here.

## Alternatives considered

- Regenerate `layout/prims/` at 0.9.x now: rejected — rewrites committed
  geometry files (and their reports) for no current need; the pin move gets
  its own record when something needs 0.9.x features.
- Adopt `klt diff --flattened` in `gen_prims.sh` (compares instantiated
  geometry, drawn layer set, bounding box and labels; ignores cell names and
  hierarchy, which is what `layout/gen_array.py` consumes via
  `begin_shapes_rec`): not adopted in this record, and not adoptable at the
  current pin. Measured: `klt diff --help` at the `f9039fd7244e` pin (via
  `uvx --from <klt_install> klt diff --help`) lists only `--top`,
  `--max-items` and `--format`; there is no `--flattened`. It becomes
  available only with a pin move to a klt that carries it (present at
  0.9.x per the review's reading of its help text). The call-site change is
  therefore part of the pin-move decision, so it is out of scope here. If
  adopted then, `layout/README.md` and `layout/toolchain.json` need the same
  edit.
- Leave the behaviour unrecorded: rejected — the next `differs:` reads as a
  size drift and sends someone hunting DR-0006 regressions that are not
  there.
- Bisect the exact introducing commit between `f9039fd7244e` and 0.9.0:
  not done; the measured release-level boundary answers the pin question.
  A PDK-revision explanation was ruled out by measurement: the pinned PDK
  (same revision as the committed reports) passes at the pin and differs
  only across the klt version axis.
