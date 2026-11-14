# verification/pex

**A probe, not a result.** One `klt extract --parasitics` run on the analog
array, recorded to answer a single question: does parasitic extraction complete
at this array's scale, and what does it produce. Nothing here is simulated,
nothing here is cited by the signoff manifest, and nothing here supports an
INL, DNL or SFDR number. See "What this evidence does and does not say" below
before using any figure in it.

Run at the klt pin of [`scripts/check_signoff.sh`](../../scripts/check_signoff.sh)
(read the pin from that file; it is deliberately not restated here so this
record cannot go stale against it), deck `gf180mcu`, `--backend local`, as a
single local process. No grid, no batch submission.

| | |
|---|---|
| Layout | [`layout/gf180-current-dac-analog.gds`](../../layout/gf180-current-dac-analog.gds), top `dac_analog_layout` |
| Input `content_hash` | `sha256:0a66ac7d1fb8605866e0c41a1de57af18d2f8aa85a4a04d19b1fcfece626510a` — byte-identical to the stream the committed LVS report graded |
| klt / KLayout | `0.9.0` (git `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`) / KLayout `0.30.13` |
| Deck | `gf180mcu`, `content_hash` `sha256:cf44de63…d97e1`, `options_hash` `sha256:6a7dc766…7cb05` (`metal_top 9K`, `mim_cap cap_mim_2f0_m4m5_noshield`, `poly_res 1k` — all deck defaults, none passed explicitly) |
| PDK | **none resolved** (`pdk: null`; no `--pdk` passed) — see the device-model caveat below |
| Parasitic model revision | `parasitics.model_revision: 2`; report `schema_version: 4` |
| Status | `extracted` — the run completed, exit 0 |
| Wall time | **1046.7 s** (17 min 27 s), 1019.7 s user, 97 % of one core — single-threaded |
| Peak memory | **296.8 MiB** maximum resident set (`/usr/bin/time -v`) |

Host: shared 16-vCPU AWS worker under concurrent load, so the wall time is an
upper bound rather than a clean benchmark. Memory is not a constraint at this
size; time is, and it is all in one core.

## Counts

Device and connectivity counts, and the parasitic elements built on top of them:

| | Count | Cross-check |
|---|---|---|
| Devices | 5046 (4845 `nfet`, 201 `pfet`) | **equals** the committed LVS report's `counts.devices.layout` |
| Nets | 2586 | **equals** LVS's `counts.nets.layout` |
| Pins | 72 | **equals** LVS's `counts.pins.layout` |
| Dummy devices dropped | 0 | |
| Parasitic resistors | 20184 | one per net star-leg; see "the resistor count" below |
| Ground capacitors | 2586 | exactly one per net |
| Coupling capacitors | 8683 | net-to-net, vertical overlap only |
| Inductors | 0 | not modelled by this deck |
| Total series resistance | 931.56 kΩ | |
| Total ground capacitance | 44.985 pF | |
| Total coupling capacitance | 314.90 fF | |

The counts reconcile against the netlist's own cards, which is the check that
the JSON summary and the written SPICE agree:

| Card | In netlist | Accounted for |
|---|---|---|
| `R` | 20185 | 20184 star legs + 1 `Rvsubs_dctie` substrate tie |
| `C` | 11269 | 2586 ground + 8683 coupling |
| `M` | 5046 | one per extracted device |
| `X` | 0 | no subckt wrappers — consistent with `pdk: null` |

**The resistor count is not a defect.** `klt extract --parasitics` is summarised
in `--help` as "one series R + one ground C per net", which predicts ~2586 of
each. The capacitors match that exactly; the resistors are 7.8× higher because
the report's own fuller model statement is the accurate one: the single lumped
per-net resistance is *distributed as a star across that net's device
terminals*. Summing each net's terminal count over all 2586 nets gives 20184 —
exactly `parasitics.r_count`. So `--help` is a simplification of the model, not
a contract the run violated. Every net came out `rc_model: "lumped"` (2586 of
2586); none is a distributed ladder, because `--distributed-rc` was not used.

`parasitics.integrity` reports 2586 nets checked and **zero** findings — 0 open
nets, 0 island components, 0 orphan nodes, 0 suspicious resistors, 0 short
candidates, 0 capacitance mismatches. The report carries no `warnings`, no
`unsupported_devices`, no `missing_flavour_markers` and no
`unbiased_pmos_body_nets`. On its own terms the netlist is self-consistent, so
the issue's "unusable output" path did not trigger.

## The model statement

Recorded verbatim from `parasitics.model` in the report, because the numbers
above mean nothing without it:

> - **capacitance**: net-to-ground for every net's own (non-coupled)
>   area/perimeter, plus net-to-net for the vertical-overlap coupling
>   `coupling` describes below — a coupled net pair gets a direct capacitor
>   between their two hub nodes, not just capacitors to the deck's
>   ground/substrate net
> - **coupling**: vertical overlap (crossover) unconditionally — where one
>   net's conductor on an adjacent metal level sits directly over another
>   *distinct* net's conductor, that overlap area is charged between the two
>   nets instead of to ground (issue #760) — plus lateral (same-layer,
>   sidewall) coupling, but only for a net pair naming one of the caller's
>   declared `--critical-net` nets (issue #976): facing-edge length within that
>   layer's own minimum-spacing lookback is charged between the two nets,
>   *additively* (not deducted from either net's substrate fringe term, unlike
>   the vertical case — a known simplification). Any same-layer pair with
>   neither side named `--critical-net`, and fringe shielding in general, are
>   still not modelled
> - **resistance**: single lumped series resistance per net, distributed as a
>   star across that net's device terminals (issue #592) — not a per-segment,
>   distributed RC ladder, *unless* `--distributed-rc` names this net via
>   `--critical-net` (issue #977, Epic #709 Phase 2b) […]
> - **frequency**: quasi-static — one frequency-independent R and C per net; no
>   skin effect, no distributed transmission-line behavior

No `--critical-net` was declared on this run, so **no lateral coupling was
modelled anywhere** and the 314.90 fF of coupling capacitance is vertical
crossover only.

The parasitic R/C coefficients come from **the deck's** curated
sheet-resistance/capacitance table, not from the PDK — the deck `content_hash`
in the table above is the thing that determined these numbers. Note it differs
from the `content_hash` in the committed LVS report (`sha256:0eb6df1b…`): the
deck content changed between the klt version that produced that report and the
pin used here, while `options_hash` is identical in both. The repo's PDK pin
([`sim/pdk.json`](../../sim/pdk.json): `gf180mcuD`, revision
`f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7`) did **not** participate in this
run at all.

## What this evidence does and does not say

- **Not simulated.** No SPICE run was made on this netlist. No `klt pex`
  re-simulation, no operating point, no transient, no corner, no Monte Carlo.
- **Not cited for any T1 item.** This is the prerequisite for T1 item 7
  (post-layout), not item 7 itself. Nothing in
  `manifests/gf180-current-dac.json` references anything in this directory, and
  the signoff verdict is unchanged by this record.
- **Supports no INL, DNL or SFDR number.** It cannot: there is no simulation,
  and the mismatch and gradient questions that set static linearity are
  untouched by an extraction. The layout's standing statement — no INL or DNL
  is claimed from this stream — is unaffected.
- **It does not answer open question O3.** [`spec/sensitivity-plan.md`](../../spec/sensitivity-plan.md)
  row O3 asks about the bias line's IR-drop profile. A **single lumped series
  resistance per net, starred to its terminals**, cannot produce a distributed
  drop along a conductor — the model has no per-segment geometry to drop across.
  `--distributed-rc` (with `--critical-net`) is the flag that would, and it was
  deliberately not run here. O3 stays open; do not cite this record for it.
- **Devices are bare `M` cards and are not mismatch-capable.** Because no
  `--pdk` was resolved, the netlist has 5046 `M` cards and zero `X` subckt
  calls. `klt extract --help` is explicit that bare `M` cards "are not
  mismatch-capable under Monte Carlo". Any future Monte Carlo use of an
  extracted netlist needs a re-run with `--pdk`; this one cannot serve.
- **The substrate is capacitively floating, by documented default.**
  `parasitics.substrate_dc_tie` is a single `Rvsubs_dctie` of 1e12 Ω from
  `vsubs` to ground (`mode: shunt`, `node_scope: global`) — the documented
  `--substrate-tie-ohms` default, which `--help` describes as "the substrate is
  only capacitively held, i.e. floating in transient analysis". This is a
  default with a flag to change it, **not** a missing bias path and **not** a
  tool gap; it was not filed as one. A transient run on this netlist would need
  `--substrate-tie-ohms` set deliberately.
- **Nothing was waived, shrunk or re-run to move a verdict.** This was one run,
  recorded as it came out.

## Tool friction filed

The run succeeded, so the issue's failure path did not apply. Two genuine gaps
surfaced anyway and were filed generically on the tool tracker per the friction
protocol:

- **[2AMLogic/klayout-tools#5716](https://github.com/2AMLogic/klayout-tools/issues/5716)** —
  the parasitics build is an unnamed stage. `timing.stages` accounts for only
  397.7 s of the 1046.7 s run and the report self-reports
  `unattributed_seconds: 648.936`; `--progress` emits its documented 30 s
  heartbeat through `device_extraction`, then goes silent for the 649 s that
  dominate the run. With no client-side wall-clock bound on a local extraction
  (`--timeout-s` is `--backend batch` only), an array-scale run is
  indistinguishable from a hang for eleven minutes. This run was bounded with
  coreutils `timeout` for that reason.
- **[2AMLogic/klayout-tools#5717](https://github.com/2AMLogic/klayout-tools/issues/5717)** —
  `klt extract --check` on a gzipped report tracebacks with
  `UnicodeDecodeError` instead of exiting 1 with a clean error. This one bites
  directly here: the artifacts below are committed gzipped, so `--check` has to
  be handed a decompressed copy.

## Committed artifacts

Both artifacts are committed **gzipped**. Uncompressed they are 3.0 MiB and
15.2 MiB, well past anything else tracked here; gzipped they are 486 KiB and
428 KiB, under the repo's largest existing tracked blob
(`verification/lvs/analog.report.json`, 785 KB). There is no git-lfs in this
repo, and `sim/smoke/records/*.json.gz` is the existing precedent for a
committed compressed record.

| File | Committed | Uncompressed | `sha256` of the uncompressed bytes |
|---|---|---|---|
| [`analog.pex.spice.gz`](analog.pex.spice.gz) | 497 839 B | 3 161 612 B | `0e7d222b84086ff18138f3067ecb62fada813cf8ec63adf36dcdf640245bad96` |
| [`analog.pex.report.json.gz`](analog.pex.report.json.gz) | 438 397 B | 15 944 220 B | `69ffd2cf108a550a46cb8c19f588e33ad877b337ef4a5caa7ee30a0584c5395c` |

The netlist hash above is the value the report itself carries in
`netlist_sha256`, so the two artifacts pin each other. The report also records
`netlist_normalized_sha256`
(`a49881fc48ce0a721796c5ea18c219d2367d5b8d9abef3ce7119db17c2897b0b`); prefer it
for any cross-environment comparison, because `klt extract` warns that raw
anonymous net numbering (`$N` labels) is not a stable contract across KLayout
versions or host platforms.

## Verify the committed record

Cheap verification — re-hashes the input layout and the deck against the
report's `provenance` block, no extraction re-run, about a second. Run from
this directory:

```
gunzip -c analog.pex.report.json.gz > /tmp/analog.pex.report.json
uvx --from "klayout-tools==$(sed -n 's/^KLT_PIN=.*:-\([0-9.]*\)}.*/\1/p' ../../scripts/check_signoff.sh)" \
    klt extract --check /tmp/analog.pex.report.json ../../layout/gf180-current-dac-analog.gds
```

Exits 0 and prints `status: match` with `[OK]` on
`provenance.input.content_hash` and `provenance.deck.content_hash`; exits 3 if
either drifted. The decompression step is needed only until
klayout-tools#5717 is fixed. The positional layout path is passed explicitly so
the check resolves the input regardless of the directory it is run from.

Confirm the artifacts themselves are intact:

```
gunzip -c analog.pex.spice.gz      | sha256sum   # 0e7d222b…5bad96
gunzip -c analog.pex.report.json.gz | sha256sum   # 69ffd2cf…c5395c
```

## Regenerate

One local process, ~17 min, single-threaded, ~300 MiB peak. Run from this
directory. The `timeout` is the wall-clock bound that `--timeout-s` does not
provide for `--backend local` (klayout-tools#5716); `--progress` gives a
stderr heartbeat while stdout stays the pure JSON response.

```
KLT_PIN="$(sed -n 's/^KLT_PIN=.*:-\([0-9.]*\)}.*/\1/p' ../../scripts/check_signoff.sh)"
timeout --kill-after=60 2400 \
uvx --from "klayout-tools==${KLT_PIN}" klt extract \
    ../../layout/gf180-current-dac-analog.gds \
    --deck gf180mcu --top dac_analog_layout \
    --parasitics --backend local --progress \
    --format json -o analog.pex.spice > analog.pex.report.json
gzip -9 -n analog.pex.spice analog.pex.report.json
```

`--backend local` is passed explicitly rather than relied on: `--backend`
defaults to `$KLT_EXTRACT_BACKEND` and only then to `local`, so naming it keeps
the single-process claim true in the recorded command regardless of the
environment it is re-run in. Rerun after any change to
`layout/gf180-current-dac-analog.gds`; the `--check` above is what detects that
drift.
