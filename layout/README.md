# layout

Analog-partition layout stream (T1 item 2). The digital partition's layout is
a separate item. **This stream is device placement only**: every device of the
analog schematic is placed, nothing is wired. There is no cell-internal
routing, no bias, switch-control or output distribution, no pins or labels,
no guard ring and no well ties beyond what the primitives carry. DRC, LVS,
power delivery and extraction are other items and are not claimed here.

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
| `unit_cell` | current source, cascode, two switches (sizes of DR-0006), stacked; 13.34 x 23.24 um, tile pitch 13.94 x 23.84 um |
| `dummy_cell` | same device placement as `unit_cell`, used for the ring and the filler |
| `elem_tNN` (NN = 00..62) | unary element: 16 `unit_cell` in a 4 x 4 block; NN is the switching position |
| `elem_bin` | binary block: `elem_b3` (8 units, rows 0-1), `elem_b2` (4, row 2), `elem_b1` (2), `elem_b0` (1) and one `dummy_cell` filler in row 3 |
| `driver` | three inverters (pfet over nfet) |
| `bias` | 10 current-source and 10 cascode devices, as the schematic's diode stack |
| `dac_analog_layout` | top cell |

Counts, checked by `--check` on the stream itself: 1023 `unit_cell`
(63 x 16 + 15), 133 `dummy_cell` (132 ring + 1 filler), 67 `driver`, 1 `bias`.
Every unit is its own instance, as the spec requires for Monte Carlo and LVS.

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
- The drivers sit in a band below the array in switching order and the bias
  block above it; neither is matched or symmetric with the array.

## Gradient and linearity

The floorplan is argued against the gradient assumption of
[DR-0003](../spec/decision-records/0003-gradient-amplitude-assumption.md):
linear 0.50 % and quadratic 0.20 % peak-to-peak, **assumed, not from the PDK**.
The placement is the one that assumption was run against (point-symmetric
pairs, inout-pairs order). **No INL or DNL number is claimed from this layout.**
The sizing model's 99.92 % yield is a model result with the mismatch and
gradient method in spec section 4 (gradient: assumed, DR-0003); nothing has
been extracted from this stream.

## Known gaps

- The schematic carries 33 `dummy_cell` (32 ring placeholders + 1 filler,
  DR-0006); this layout has 133 (the real one-cell ring). The schematic count
  is a placeholder that DR-0006 defers to this issue; it needs updating before
  LVS.
- Unit-cell device positions inside the cell are a first arrangement
  ([DR-0007](../spec/decision-records/0007-analog-layout-assumptions.md)),
  not optimised for matching or routing.
- Routing, DRC, LVS, extraction: later items. Tool gaps found, filed on
  `2AMLogic/klayout-tools`: [#4251](https://github.com/2AMLogic/klayout-tools/issues/4251)
  (`gen mos_array` child cell name collides across outputs), and already open:
  #4221 / #4188 (no `--attest` producer for item 2, so the envelope is
  written by `gen_array.py`). Not tried, so not claimed as gaps: `gen-compose`
  for the array, symmetric routing, extraction at array scale.

## Files

| Path | Content |
|---|---|
| `gen_array.py` | stream generator and checker |
| `switching_sequence.json` | recorded sequence and site map |
| `prims/` | device primitives from `klt gen mos_array` (GDS plus the tool's report) |
| `gen_prims.sh` | regenerates / re-verifies `prims/` (needs the PDK) |
| `gf180-current-dac-analog.gds` | the stream |
| `toolchain.json` | klt and klayout pins |
