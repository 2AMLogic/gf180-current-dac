# design

Analog-partition design sources. The digital partition is `rtl/`.

## Regenerate

```
python3 design/gen_analog.py            # schematics, symbols, xschemrc, inventory
export PDK_ROOT=~/.ciel/ciel/gf180mcu/versions/f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
for n in unit_cell dummy_cell driver bias elem_16 elem_1 elem_2 elem_4 elem_8 dac_analog; do
  klt netlist design/analog/$n.sch -o design/analog/$n.spice \
      --rcfile design/analog/xschemrc $( [ $n = dac_analog ] && echo --block )
done
klt signoff --attest 1 --inventory design/inventory-item1-analog.json -o evidence/item1-analog.json
```

`python3 design/gen_analog.py --check` (run in CI) fails if a committed
schematic, symbol or the inventory differs from the generator. Netlist
freshness (`klt netlist ... --check`) needs xschem and the PDK, so it runs
locally; `klt signoff --attest 1 --inventory ... --check evidence/item1-analog.json`
re-runs it. Netlist from `klt netlist` only, never raw `xschem`.

## What is here

| Path | Content |
|---|---|
| `gen_analog.py` | schematic generator (the source of truth) |
| `analog/*.sch`, `*.sym` | generated xschem sources, committed |
| `analog/*.spice` | netlists derived by `klt netlist` |
| `analog/xschemrc` | symbol path (this directory, gf180mcuD PDK symbols) |
| `inventory-item1-analog.json` | T1 item 1 inventory for `klt signoff --attest` |
| `count_netlist.py` | flattened instance count of a netlist |

Hierarchy: `unit_cell` (nfet current source M1, cascode M2, switch pair
Msp/Msn above the cascode) -> `elem_16` (unary element, 16 explicit unit
cells) and `elem_1/2/4/8` (binary) -> `dac_analog` (63 + 4 elements, a
`driver` each, `bias`, dummies). Every unit cell is its own instance; there
is no `m=` multiplier on the array, so layout and LVS can match instance for
instance.

```
$ python3 design/count_netlist.py design/analog/dac_analog.spice
unit_cell: 1023
dummy_cell: 33
driver: 67
bias: 1
elem_1: 1 elements x 1 units = 1
elem_2: 1 elements x 2 units = 2
elem_4: 1 elements x 4 units = 4
elem_8: 1 elements x 8 units = 8
elem_16: 63 elements x 16 units = 1008
live unit cells (explicit instances): 1023
```

## What this does not claim

Existence and freshness only (T1 item 1, analog). No INL, DNL, impedance,
power or timing number comes from here. Device sizes other than the
current-source gate area are assumptions: see
[DR-0006](../spec/decision-records/0006-analog-schematic-sizing-assumptions.md).
The one simulation run (single corner `typical`, one operating point, all
cells on, local ngspice) only showed the netlist loads and converges:
each output carries about 2.05 mA at a 20 uA reference. That is a toolchain
check, not a full-scale-current result.

Placement and switching sequence are not in the netlist; the layout issue
assigns thermometer index to site. Dummy count (32 ring + 1 binary-site
filler) is a placeholder.
