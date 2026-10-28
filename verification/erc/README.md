# verification/erc

T1 item 11 (power delivery, structural): one `klt erc` supply run per
partition, because the two streams are not merged. Run with
`klayout-tools==0.8.0` (the pin `scripts/check_signoff.sh` and CI grade the
manifest with), deck `gf180mcu`, `--findings-only --omit-antenna-tables`
(connectivity half only). Both runs are single checks, no grid, about 3 s each.

| Partition | Layout | Spec | Verdict |
|---|---|---|---|
| analog | `layout/gf180-current-dac-analog.gds`, top `dac_analog_layout` | [`analog.spec.json`](analog.spec.json) | `erc_status: clean`, 0 findings; `vdd` and `vss` 1 island each |
| digital | `layout/pnr/dac_digital.gds`, top `dac_digital` | [`digital.spec.json`](digital.spec.json) | `erc_status: clean`, 0 findings; `VDD` and `VSS` 1 island each |

The reports are committed as `klt erc` emitted them. With the LVS reports
(item 4) and the P&R response, `manifests/gf180-current-dac.json` cites them
as `11.analog` / `11.digital` and `klt signoff` grades both `met`. Nothing was
waived or shrunk to move a verdict.

## Regenerate

```
python3 verification/erc/gen_analog_spec.py [--check]   # needs pip klayout; rewrites analog.spec.json
cd verification/erc
uvx --from klayout-tools==0.8.0 klt erc ../../layout/gf180-current-dac-analog.gds analog.spec.json \
    --top dac_analog_layout --deck gf180mcu --findings-only --omit-antenna-tables --format json > analog.report.json
uvx --from klayout-tools==0.8.0 klt erc ../../layout/pnr/dac_digital.gds digital.spec.json \
    --top dac_digital --deck gf180mcu --findings-only --omit-antenna-tables --format json > digital.report.json
uvx --from klayout-tools==0.8.0 klt erc --check analog.report.json     # run from this directory
uvx --from klayout-tools==0.8.0 klt erc --check digital.report.json
```

`klt erc` exits 4 on these runs (`--findings-only` leaves the antenna verdict
`not_checked`); gate on `erc_status`. Rerun after any change to either layout
stream, then update the `content_hash` pins in the manifest and regenerate
`manifests/gf180-current-dac.signoff.json`.

## What the evidence does and does not say

- **Analog supplies** are the labels `vdd` (Metal3 label layer) and `vss`
  (Metal4 label layer); stackup is Poly2 + Metal1..Metal5 with contact and
  Via1..Via4. The n-well tie (`Comp & Nplus` in `Nwell`, to `vdd`) is checked
  for all 201 wells.
- **The analog substrate tie rests on asserted regions.** The stream draws no
  p-well (the nfets sit in native substrate), so `substrate_tie` uses
  `well_layer: null` with `well_boxes`: one box per top-cell instance, shrunk
  0.1 um so the boxes stay separate, each of which must hold a `Comp & Pplus`
  tap reaching `vss`. The verdict-of-record states it under
  `ties_checked_by_well_assertion`. A box with no tap does fail (checked
  with an extra empty box: `erc.missing_tie`). The boxes come from the
  generator, not from a drawn layer.
- **No `nets[].roles` are declared**, so `erc.unlabelled_conductor` cannot
  fire and `supply_unlabelled_islands` is `{}`: "exactly one island" counts
  labelled islands only. Metal1..Metal5 of the analog array carry many signal
  nets, so claiming a role as the supply's own would not be true. A severed
  unlabelled supply fragment is therefore not excluded by this evidence.
- **Analog LVS half** is a participation test (`vdd`/`vss` paired in
  `net_correspondence`), not a second opinion; `power_connectivity` is
  `unchecked` there.
- **Digital** also needs `power.pdn: true`, `tapcell_master` `filltie`,
  straps on Metal1/4/5 (all in the stackup) and LVS `power_connectivity:
  match`; all read as expected. The p-well tie uses the drawn 204/0 layer.
- Not claimed: IR drop, rail resistance, electromigration, antenna checks,
  or any merged-chip supply check.
