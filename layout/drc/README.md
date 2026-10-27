# DRC evidence (T1 item 3)

`klt drc --deck gf180mcu --pdk gf180mcuD` on each partition stream, one
single-unit run per stream, unmodified tool output (no waivers, no rule
selection). Regenerate with `layout/drc/run.sh`; `layout/drc/run.sh --check`
re-hashes the committed GDS and deck against the envelopes. klt is the pin in
`layout/toolchain.json` (`0.8.1.dev86+gf9039fd7244e`); CI grades the manifest
with `klayout-tools==0.8.0`, which accepts these envelopes.

Deck: `gf180mcu`, content hash
`sha256:0eb6df1bafc5106ec50bd58479dbd7cda36bb685f1ef18cd3a2244a6e7e48666`.
The curated deck is klt's own transcription, not the foundry's native deck.

## Result

| Partition | Stream | Envelope | Status |
|---|---|---|---|
| analog | `layout/gf180-current-dac-analog.gds` (`dac_analog_layout`) | `evidence/item3-analog.json` | `clean`, 0 violations |
| digital | `layout/pnr/dac_digital.gds` (`dac_digital`) | `evidence/item3-digital.json` | `clean`, 0 violations |

Item 3 grades **met for both partitions**. Nothing was waived or filtered.

### How the digital stream got to clean

The first digital stream (tapcells every 50 um, klt's `gf180mcu_7t_6M` PDN
preset) reported 1952 violations. Triage, one single-unit run each:

- `comp.tap_distance.{nwell,psub}.mv.1` (101 + 99): the foundry `dffq_1`
  cell fails the same two rules on its own under this deck (6 violations
  running `klt drc` on the cell in the PDK stream), so they depend on tap
  density, not on the router. `tapcell.distance_um` 50 -> 20 in
  `layout/pnr/request.json` cleared them (99 tap cells).
- `metal{2,3,4}.ongrid.1`, `via{2,3}.ongrid.1`, `via{2,3}.width.1` (1752):
  all on the PDN via arrays (`VIA_via2_3_*`) the preset's
  `add_pdn_connect ... -split_cuts {Metal3 0.128}` tuning generates. The
  request now spells the preset's three straps out explicitly (same
  Metal1/Metal4/Metal5 width, pitch, offset) and omits the `connects` tuning
  (`preset` and `connects` are mutually exclusive in klt, so dropping the
  tuning means dropping the preset). That cleared all of them.

Consequence: the PDN no longer carries the platform's `-split_cuts`/`-ongrid`
tuning, which the preset adds for this exact DRC question; the deck here
passes without it. Whether the preset's tuning is wrong for this deck, or
the deck's ongrid/width on merged via arrays is the artefact, was not
established; filed as 2AMLogic/klayout-tools#4348.

## Coverage disclosure (quoted from each envelope's `coverage` block)

`coverage.deck_scope` (both): 10.4.2 MIM Option B, 10.7 DRC_BJT Mark Layer,
7.12 Contact, 7.13 Metaln, 7.14 Vian, 7.15 MetalTop, 7.4 Nwell, 7.5 Comp,
7.7 Poly2, 7.8 Nplus, 7.9 Pplus, 9.1 Bond Pad, ESD, GR, OFFGRID, SB.

### Analog

- `coverage.layers_in_stream_without_rules`: `[]`
- `coverage.layers_checked`: 21/0, 22/0, 30/0, 31/0, 32/0, 33/0, 34/0. The
  skipped list includes the metal2 and higher width/space/enclosure rules, so
  whether this stream draws those layers was not traced here.
- `coverage.rules_skipped` (79): `bjt.separation.comp.1`, `cap_mk.ongrid.1`, `comp.separation.guard_ring_mk.1`, `comp.space.mv.1`, `comp.tap_distance.nwell.mv.1`, `comp.tap_distance.psub.mv.1`, `comp.width.mv.1`, `diode_mk.ongrid.1`, `dnwell.ongrid.1`, `drc_bjt.ongrid.1`, `dualgate.ongrid.1`, `dualgate.space.1`, `dualgate.width.1`, `efuse_mk.ongrid.1`, `esd.area.1`, `esd.holes_area.1`, `esd.overlap.comp.1`, `esd.separation.nplus.1`, `esd.separation.pplus.1`, `esd.space.1`, `esd.width.1`, `fusetop.ongrid.1`, `metal1.enclosing.via1.1`, `metal1.separation.guard_ring_mk.1`, `metal2.enclosing.via1.1`, `metal2.enclosing.via2.1`, `metal2.ongrid.1`, `metal2.separation.guard_ring_mk.1`, `metal2.space.1`, `metal2.width.1`, `metal3.enclosing.via2.1`, `metal3.enclosing.via3.1`, `metal3.ongrid.1`, `metal3.separation.guard_ring_mk.1`, `metal3.space.1`, `metal3.width.1`, `metal4.enclosing.via3.1`, `metal4.enclosing.via4.1`, `metal4.ongrid.1`, `metal4.separation.guard_ring_mk.1`, `metal4.space.1`, `metal4.width.1`, `metal5.enclosing.via4.1`, `metal5.ongrid.1`, `metal5.separation.guard_ring_mk.1`, `metal5.space.1`, `metal5.width.1`, `metaltop.ongrid.1`, `metaltop.separation.guard_ring_mk.1`, `metaltop.space.1`, `metaltop.width.1`, `mim.enclosing.fusetop.1`, `mim.enclosing.via4.1`, `mim.space.1`, `mim_l_mk.ongrid.1`, `nwell.separation.guard_ring_mk.1`, `pad.enclosing.metal5.1`, `pad.ongrid.1`, `plfuse.ongrid.1`, `poly2.enclosing.sab.1`, `poly2.separation.guard_ring_mk.1`, `res_mk.ongrid.1`, `resistor.ongrid.1`, `sab.ongrid.1`, `sab.separation.contact.1`, `sab.space.1`, `sab.width.1`, `via1.ongrid.1`, `via1.space.1`, `via1.width.1`, `via2.ongrid.1`, `via2.space.1`, `via2.width.1`, `via3.ongrid.1`, `via3.space.1`, `via3.width.1`, `via4.ongrid.1`, `via4.space.1`, `via4.width.1`

### Digital

- `coverage.layers_in_stream_without_rules`: 0/0, 21/10, 34/10, 36/10, 63/63,
  81/10, 204/10 (non-empty: the deck has no rule for these drawn layers)
- `coverage.rules_skipped` (42): `bjt.separation.comp.1`, `cap_mk.ongrid.1`, `comp.separation.guard_ring_mk.1`, `comp.tap_distance.nwell.lv.1`, `comp.tap_distance.psub.lv.1`, `diode_mk.ongrid.1`, `dnwell.ongrid.1`, `drc_bjt.ongrid.1`, `efuse_mk.ongrid.1`, `esd.area.1`, `esd.holes_area.1`, `esd.overlap.comp.1`, `esd.separation.nplus.1`, `esd.separation.pplus.1`, `esd.space.1`, `esd.width.1`, `fusetop.ongrid.1`, `metal1.separation.guard_ring_mk.1`, `metal2.separation.guard_ring_mk.1`, `metal3.separation.guard_ring_mk.1`, `metal4.separation.guard_ring_mk.1`, `metal5.separation.guard_ring_mk.1`, `metaltop.ongrid.1`, `metaltop.separation.guard_ring_mk.1`, `metaltop.space.1`, `metaltop.width.1`, `mim.enclosing.fusetop.1`, `mim.enclosing.via4.1`, `mim.space.1`, `mim_l_mk.ongrid.1`, `nwell.separation.guard_ring_mk.1`, `pad.enclosing.metal5.1`, `pad.ongrid.1`, `plfuse.ongrid.1`, `poly2.enclosing.sab.1`, `poly2.separation.guard_ring_mk.1`, `res_mk.ongrid.1`, `resistor.ongrid.1`, `sab.ongrid.1`, `sab.separation.contact.1`, `sab.space.1`, `sab.width.1`
- `coverage.layers_checked`: 21/0, 22/0, 30/0, 31/0, 32/0, 33/0, 34/0, 35/0, 36/0, 38/0, 40/0, 41/0, 42/0, 46/0, 55/0, 81/0, 112/1, 204/0
