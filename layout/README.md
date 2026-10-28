# layout

Analog-partition layout stream (T1 item 2). The digital partition's layout is
a separate item. **This stream is placed, routed and pinned, and nothing
more**: every device of the analog schematic is placed and wired to the
connectivity of [`design/analog/dac_analog.spice`](../design/analog/dac_analog.spice),
the 72 reference pins are labelled on the top cell, and the substrate and well
taps are tied. It is generated, not drawn (see "Wiring"). What is still not
done is listed under "Still not wired". DRC is `clean` on this stream
([`drc/README.md`](drc/README.md)); the LVS verdict is not `match` yet
([`../verification/lvs/README.md`](../verification/lvs/README.md)); power
delivery, post-layout extraction and any INL / DNL number are not claimed.

## Regenerate

```
python3 layout/gen_array.py                # writes the stream and evidence/item2-analog.json
python3 layout/gen_array.py --check        # CI: regenerate twice, compare everything committed
python3 layout/gen_array.py --write-table  # rewrite switching_sequence.json from spec/sizing/size.py
layout/gen_prims.sh [--check]              # device primitives via klt gen; needs the PDK
```

The generator needs the pip `klayout` package at the version in
[`toolchain.json`](toolchain.json) (`klayout_package_pin`), and nothing else:
the primitives in `prims/` are committed, so CI needs no PDK. The stream has
no timestamps and a fixed cell order; `--check` fails if two runs differ or the
committed stream, envelope or table differ from a fresh run. Current hash:
see `evidence/item2-analog.json` (`provenance.input.content_hash`).

## What is in the stream

| Cell | Content |
|---|---|
| `unit_cell` | current source, cascode, two switches (sizes of DR-0006), stacked and wired; devices 13.34 x 23.24 um, tile pitch 13.94 x 23.84 um (the M3 tracks reach 0.3 um into the tile gap) |
| `dummy_cell` | same device placement as `unit_cell`, used for the ring and the filler |
| `elem_tNN` (NN = 00..62) | unary element: 16 `unit_cell` in a 4 x 4 block; NN is the switching position |
| `elem_bin` | binary block: `elem_b3` (8 units, rows 0-1), `elem_b2` (4, row 2), `elem_b1` (2), `elem_b0` (1) and one `dummy_cell` filler in row 3 |
| `driver` | three inverters (pfet over nfet) |
| `bias` | 10 current-source and 10 cascode devices, as the schematic's diode stack |
| `dac_analog_layout` | top cell |

## Wiring

Metal plan: M1 local (devices, internal nets, tap rails), M2 horizontal, M3
vertical, M4 horizontal, M5 vertical. Every cell is built by `gen_array.py`
from the committed primitives; the same pattern is translated to every unit.

- **Inside a unit** (`unit_cell`): `n1` (current-source drain to cascode source)
  and `n2` (cascode drain to both switch sources) are M1 only. The ten
  vertical M3 tracks are at fixed x in every unit and run the full tile
  height, extended half the tile gap so the units of a column abut: six `vss`
  (over the five M1 tap rails and the current-source source, tied by one M2
  bus), `vbn`, `outp`, `outn` and `iref` (the schematic's `vcas`). Each
  terminal reaches its track through a via stack, an M2 stub where it is not
  directly below. The switch gates end in an M2 row each, `sp` above the gate
  pads and `sn` below them, ending at the tile edge.
- **`dummy_cell`** has the same devices, `n1`/`n2` and `vss` tracks; its
  current-source gate, cascode gate, both drains and both switch gates are
  tied to the `vss` tracks, as in the schematic. The four signal tracks pass
  the filler site and the top and bottom ring rows as plain M3 added at the
  level above, so the columns are continuous.
- **Per element** (`elem_tNN`, `elem_b0..b3`): the units of a group are joined
  in M2 across the tile gap (rows) and by one M3 per net in the group's first
  column (between rows), so all 16 / 8 / 4 / 2 / 1 units share one `sp` and
  one `sn`. The group exposes `sp` and `sn` as M3 pads in its first unit (the
  binary groups in their own units: `b3` (0,0), `b2` (0,2), `b1` (1,3), `b0`
  (2,3)).
- **Columns**: `vbn` and `iref` are collected on M4 rails above the array,
  `outp` and `outn` on M4 rails below it, `vss` on both. The bias block sits
  above the array, its ten pairs wired like the cs/cas rows of a unit with the
  gate tied to the drain, and reaches the same rails with M3.
- **Drivers** (67, two rows below the array): `driver` is three inverters with
  M2 `vdd` / `vss` buses and M3 nets; nfet taps go to `vss`, pfet (n-well)
  taps to `vdd`. Each `sp` / `sn` runs from the element pad on an M4 stub to
  its own M5 slot inside the element column, down M5 to a per-net M4 track in
  the channel next to its driver row (upper channel for row 0, lower for row
  1, left-edge track assignment, 42 + 38 tracks), then on M3 to the driver
  output. The channel height is derived from the track count, so the driver
  rows sit lower than in the placement-only stream; the array itself did not
  move. The whole stream is 476.8 x 911.3 um.
- **Pins**: 72 text labels on the top cell, each once, on the metal of its net
  (`t0..t62`, `b0..b3` on the driver inputs; `iref`, `vss`, `outp`, `outn` on
  the rails; `vdd` on the driver supply strap). They are labels for
  extraction, not pads: there is no pad ring and no routing to the die edge.
- **Taps**: the primitives carry four tap pads each; the generator ties every
  pad to `vss` (nfet) or `vdd` (driver pfet) with M1 rails and via stacks.
  `klt lvs` reports `body_verification: verified` on the array.

Counts, checked by `--check` on the stream itself: 1023 `unit_cell`
(63 x 16 + 15), 133 `dummy_cell` (132 ring + 1 filler), 67 `driver`, 1 `bias`.
Every unit is its own instance, as the spec requires for Monte Carlo and LVS.
`--check` also reads the routing back from the stream: the 72 pin labels (each
name once), that every one of the 1023 units is joined into its group's `sp`
and `sn` nets (union-find over the join shapes in each group cell), and the 134
M5 element-to-driver wires. This is a count of what was drawn, not an
extraction; connectivity is `klt lvs`'s job (below).

## Placement and switching sequence

The array is 34 x 34 unit sites: a 32 x 32 core (8 x 8 elements of 4 x 4
units) inside a one-cell dummy ring on all four sides (spec section 4; the ring
depth is unchanged). All units have the same orientation. The 64 element sites
are numbered `site = row * 8 + col`, row 0 at the bottom, col 0 at the left.

The switching sequence is **inout-pairs** (spec section 6), recorded as data in
[`switching_sequence.json`](switching_sequence.json): `order[k]` is the site of
unary element `elem_t{k}`, and the last entry (site 60) is the binary block.
`gen_array.py` reads that table, and `--check` fails if the table differs from
`sequence(8, "inout-pairs")` in `spec/sizing/size.py`, which is the sequence
the spec's 99.92 % yield figure was computed for. Sites `s` and `63 - s` are
point-symmetric partners; consecutive entries `order[2j]`, `order[2j+1]` are
such a pair, taken alternately from the innermost and outermost remaining
radius. `--check` also reads the stream back and verifies each element cell's
position against the table, the full dummy ring, point symmetry of the ring and
of every pair, and the instance counts.

Disclosed asymmetries:

- The last pair is (`elem_t62`, `elem_bin`): the binary block sits at the 64th
  site, so the unary elements are point-symmetric but the binary bits are not
  centred. The sizing model puts no gradient on the binary block either, so
  this matches the model, not a better layout.
- Inside the binary block the 1, 2, 4 and 8 unit groups are not
  common-centroid with each other.
- The drivers sit in two rows below the array in switching order and the bias
  block above it; neither is matched or symmetric with the array.
- Routing is a translation, not a mirror: the unit's output stubs, `sp` / `sn`
  rows and tracks are not mirrored between the point-symmetric partners, so the
  two units of a pair differ in stub direction. Nothing here claims the stubs
  cancel.
- `outp` / `outn` are collected only at the bottom and `vbn` / `iref` only at
  the top, so the IR drop along a column is not balanced between its two ends.
- The 134 element-to-driver nets have different lengths (42 + 38 channel
  tracks, M5 slots at different x), so the gate-drive skew between elements is
  unequal and unmodelled. The drivers are not part of the matched array.

## Gradient and linearity

The floorplan is argued against the gradient assumption of
[DR-0003](../spec/decision-records/0003-gradient-amplitude-assumption.md):
linear 0.50 % and quadratic 0.20 % peak-to-peak, **assumed, not from the PDK**.
The placement is the one that assumption was run against (point-symmetric
pairs, inout-pairs order). **No INL or DNL number is claimed from this layout.**
The sizing model's 99.92 % yield is a model result with the mismatch and
gradient method in spec section 4 (gradient: assumed, DR-0003); no parasitics
have been extracted from this stream (the `klt extract` used for LVS is a
connectivity extraction).

## Still not wired / known gaps

- Not drawn: pad ring and routing to the die edge, a guard ring (the dummy
  ring is the only ring), supply and bias distribution sized for current
  (every M2-M5 wire is the 0.28 um minimum width, with no electromigration or
  IR check), clock and digital-side interface. The
  decoder is not connected to the `t` / `b` inputs: they are pins.
- The schematic carries the same 133 `dummy_cell` as the layout (132 ring + 1
  filler); the DR-0006 placeholder of 32 was replaced in issue #35 and the
  analog LVS reads `match` (see the LVS README).
- Unit-cell device positions inside the cell are a first arrangement
  ([DR-0007](../spec/decision-records/0007-analog-layout-assumptions.md)),
  not optimised for matching or routing.
- The routing adds metal over the matched devices (M2 stubs, M3 tracks over the
  current source and switches). Its effect on matching is not modelled.
- DRC: `clean`, 0 violations (it was `clean` before routing). Two label
  purposes are drawn without rules in the deck: 42/10 and 46/10 (the M3 and M4
  pin labels); this is in the item-3 record's `layers_in_stream_without_rules`.
- Tool gaps found: see the issue list on `2AMLogic/klayout-tools`:
  [#4251](https://github.com/2AMLogic/klayout-tools/issues/4251)
  (`gen mos_array` child cell name collides across outputs) and
  [#4548](https://github.com/2AMLogic/klayout-tools/issues/4548) (a flat
  layout against a hierarchical reference gives no pointer to
  `flatten_reference`), already open:
  #4221 / #4188 (no `--attest` producer for item 2, so the envelope is
  written by `gen_array.py`). Not tried, so not claimed as gaps: `gen-compose`
  for the array, a router for the symmetric array.

## Files

| Path | Content |
|---|---|
| `gen_array.py` | stream generator and checker |
| `switching_sequence.json` | recorded sequence and site map |
| `prims/` | device primitives from `klt gen mos_array` (GDS plus the tool's report) |
| `gen_prims.sh` | regenerates / re-verifies `prims/` (needs the PDK) |
| `gf180-current-dac-analog.gds` | the stream |
| `toolchain.json` | klt and klayout pins |
