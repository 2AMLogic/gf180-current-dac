# Work Log

Chronological record of merged PRs and closed issues. Maintained by the Guide role; newest first.

### 2026-11-16

- **Issue #174** (closed): T1 item 7 (digital): SDF-annotated klt functional-verification re-run on the as-built controller netlist
- **Issue #176** (closed): Assert engine_versions in the program-select summarizer self-test: an empty list is the silent failure mode of the new provenance field
- **Issue #196** (closed): Bind the decision-0005 PVT grid in sim/lib/pdk_env.sh to the spec in CI, as check-item6-digital.sh does for the digital extract
- **Issue #201** (closed): Wire sim/sense-margin/test_summarize.py into check:ci: 209 lines of green regression test whose docstring cites a stale 'not run' precedent

### 2026-11-15

- **Issue #133** (closed): Root README understates which signoff checks CI runs
- **Issue #150** (closed): Remove the local ngspice -v probe from the batch benches: 4 of 14 records name ngspice 42 while every corner ran on the fleet's ngspice 46
- **Issue #151** (closed): Remove the stale 'not simulated' sense statements from the corner-bench summarizers: new records still name closed #36 for effects sim/sense-mc now simulates
- **Issue #154** (closed): Establish the digital stream on the pinned klt 0.9.0, folding in the hand-written PDN block -> preset: gf180mcu_7t_6M
- **Issue #155** (closed): sim/controller-fv reports are klt schema_version 1; the pinned klt now emits 2
- **Issue #161** (closed): rtl/synth.sh reports twice the real latch count: replace the hand-rolled log scraper with a Yosys assertion
- **Issue #167** (closed): Single-source the fleet-checked model-file list: pdk_env.sh loops one copy while every record's variant_simulated names another
- **Issue #173** (closed): T1 item 4 (digital): klt lvs of the routed controller against its as-built netlist
- **Issue #175** (closed): Wire sim/program-select/test_summarize.py into check:ci: 141 lines of regression test that nothing runs
- **Issue #177** (closed): Refuse an empty report in sim/program-select/summarize.py: after #146 a present-but-empty report still records complete: true and selects the narrowest width
- **Issue #181** (closed): README still reads "spec ratified" at both line 13 and line 80 — the committed evidence reaches the "sense path simulated across PVT" rung
- **Issue #182** (closed): Drop the redundant 'Item 2 (analog) stream matches its record' CI step: layout/attest.sh --check already covers both its failure modes
- **Issue #187** (closed): Single-source the ratified decision-0005 PVT grid: four benches retype the corner set with no binding to the spec
- **Issue #188** (closed): Single-source the pinned-klt incantation: 8 scripts hand-roll it in 4 shapes and 8 of 9 give no diagnosable error when uvx is absent
- **Issue #191** (closed): Remove dead --emit-klt-requests mode from verification/runner.py: no caller since #148
- **Issue #205** (closed): CI never runs the sim/* summarizer unit tests (discovery is scoped to scripts/ci)
- **PR #109**: test: silence check_tests' synthetic SKIP/ok prints in test_check_ci
- **Issue #106** (closed): check_ci.py gate output now carries two synthetic SKIP/ok lines from its own test module
- **PR #104**: docs: name klayout_package_pin in README instead of restating the pip klayout version
- **PR #103**: ci: honor exit 2 as SKIP only for the allowlisted TESTS entry
- **PR #102**: fix: derive the last restated segmentation literals (size.py cross-check, table self-description)
- **Issue #100** (closed): Root README.md:109 is the last restatement of the klayout pip pin, now that ci.yml reads klayout_package_pin
- **Issue #99** (closed): check_ci.py treats ANY child exit 2 as SKIP, so an argparse-level break on a non-skippable check silently drops that gate
- **Issue #96** (closed): Finish the segmentation ownership sweep: three 1023 literals in spec/sizing/size.py and the hardcoded 8/63/62 in the switching-table self-description
- **PR #86**: refactor(spec): one owner for the array segmentation constants
- **Issue #80** (closed): Remove the restated segmentation constants in gen_analog.py: the layout generator already derives all of them, and they drifted once already
- **PR #98**: docs: scope DR-0008 first-entry optimism claim to the delay tables
- **PR #94**: docs: pin pex verify block to the record's klt version, not the live pin
- **PR #93**: chore: drop unreferenced design/count_netlist.py; cite enforced count checks in README
- **PR #91**: fix: gen_array --check degrades to SKIP/relaxed off the klayout pin
- **PR #75**: test: add cocotb functional suite for dac_digital with zero-delay RTL and netlist reports
- **PR #71**: docs: separate the klt release that wrote the ERC reports from the one grading now
- **Issue #97** (closed): Root README 'Repo layout' block omits verification/pex/
- **Issue #90** (closed): Remove design/count_netlist.py: unreferenced script whose counts LVS and gen_array already assert
- **Issue #87** (closed): check_ci.py cannot pass on the dispatch workers: no klayout matching klayout_package_pin is importable by system python3
- **Issue #84** (closed): DR-0008: "first entry is the optimistic end" holds only for the delay tables, not for any of the four constraint columns
- **Issue #83** (closed): verification/pex/README.md: the Verify block reads the live KLT_PIN, so a pin bump reports 'drifted' on an unchanged record
- **Issue #69** (closed): Correct stale klt pin and testbench wording in the ERC README, layout toolchain notes and root README
- **Issue #66** (closed): Decoder functional suite as a cocotb regression run through klt functional-verification (RTL and synthesized netlist)
- **PR #92**: build: single-source the klt release pin via check_signoff.sh --print-pin
- **PR #88**: ci: enumerate committed JSON in check_ci instead of a hand-maintained allowlist
- **Issue #73** (closed): Remove the six restated copies of the klt release pin: KLT_PIN is the declared home but CI hardcodes 0.9.0
- **Issue #70** (closed): Remove the hand-maintained JSON_FILES allowlist in check_ci.py: enumerate committed JSON from git

### 2026-11-14

- **Issue #144** (closed): Remove the copied bench body and subcircuits from sim/sense-margin/probe/probe.cir.in: build the 14 probe decks from sense.cir.in and the committed netlist
- **Issue #146** (closed): Remove the report glob in sim/program-select/summarize.py: a partial result set is recorded as complete and can select a narrower width
- **Issue #147** (closed): Remove the retyped tool versions from sim/README.md's testbench inventory: the analog rows say klt 0.8.0, the attested item 9 inventory pins 0.9.0
- **Issue #148** (closed): Remove the second controller-bench execution path: runner.py runs cocotb directly while the committed evidence comes from klt functional-verification
- **Issue #149** (closed): Correct two false statements in layout/README.md about the gf180mcu_7t_6M PDN preset: it does combine with overrides, and the pinned klt no longer emits split_cuts
- **Issue #160** (closed): probe/README.md:20 claims `both` sizing is what the schematic carries; the netlist carries the 8u/2.24u pair
- **Issue #163** (closed): Re-evaluate T1 item 3's EF coverage disclosure: the pinned klt deck gained an EF scope and now checks five eFuse-layer rules
- **Issue #164** (closed): check_evidence_format.py grades zero sim records: the glob misses records/<stamp>/record.json and reports a vacuous pass
- **Issue #169** (closed): Remove the report glob in sim/sense-margin/summarize.py: a partial set is recorded and the negative control can be graded over half its requests
- **PR #82**: docs: name the klt_required_commands record in sim/README.md instead of snapshotting it
- **PR #79**: docs: record a klt extract --parasitics probe of the analog array
- **Issue #72** (closed): Correct the stale klt_required_commands description in sim/README.md
- **Issue #67** (closed): Parasitic extraction probe of the analog array: one klt extract --parasitics run with a committed record
- **PR #81**: docs: split DR-0008's index_2 gloss by liberty table shape
- **Issue #76** (closed): DR-0008: index_2 gloss is wrong for the four setup/hold columns (constraint tables have no load axis)
- **Issue #68** (closed): Propose a decision record for the digital partition's I/O timing budget
- **PR #65**: docs: roadmap as of 2026-11-13
- **PR #74**: docs: add DR-0008 proposing the digital partition's I/O timing budget

### 2026-11-13

- **Issue #108** (closed): Migrate sim/program-select and sim/sense-margin run.sh to shared bench helpers
- **Issue #112** (closed): Hoist duplicated klt batch dry-run and submit blocks from sim/*/run.sh into sim/lib
- **Issue #115** (closed): Remove dead dry-run cleanup in sim/cold-start.sh: program-select dry runs no longer write under records/
- **Issue #117** (closed): Hoist duplicated record-provenance boilerplate from sim/*/summarize.py into sim/lib
- **Issue #124** (closed): Replace the four always-green placeholder scripts in package.json with one real check:ci
- **Issue #125** (closed): Remove the stale duplicate 'Re-attest item 8' section and the contradicted item 1 pin instructions from signoff/README.md
- **Issue #128** (closed): Remove the documented Yosys version gate that rtl/synth.sh never had, and the leftover 'cold start needs Yosys' statements
- **Issue #129** (closed): Repair the stale 1.analog manifest pin and the drifted record hash in the item 8 envelope
- **Issue #134** (closed): Correct the 135-corner statements for sim/corner-verification: each request runs 45 corners (supplies paired, not crossed)
- **Issue #137** (closed): Remove two stale provenance statements from sim/sense-mc: the 'comparator never resolves' reason in run.sh and the hand-typed PDK variant strings in summarize.py
- **Issue #139** (closed): layout/README.md 'What is not claimed' says neither partition is DRC clean; the DRC section below it reports both clean
- **Issue #140** (closed): Stop retyping sim/sense-mc/run.sh's run constants in summarize.py: the decision limit, fuse values, control references and corner count reach record.json as separate literals

### 2026-11-12

- **PR #62**: Bump Repo Skills 0.25.10 -> 0.26.1

### 2026-11-10

- **Issue #62** (closed): T1 item 8 (characterization report): per-ratified-row report with controller Fmax/area/power, attested with --attest 8

### 2026-11-09

- **Issue #40** (closed): Remove rtl/synth.sh: superseded by regen-gl.sh latch check, plus dead Yosys gate in cocotb runner
- **Issue #88** (closed): Re-cite sense row P10 for items 5 and 6 (analog) to the post-#85 comparator records

### 2026-11-07

- **PR #59**: Bump Repo Skills 0.25.1 -> 0.25.10

### 2026-11-06

- **Issue #57** (closed): Bring README, layout and verification READMEs in line with the 14/22 signoff record
- **PR #58**: docs: align READMEs with the 14/22 signoff record

### 2026-11-05

- **Issue #74** (closed): Refresh README status line: sense path, DRC and controller routing exist
- **Issue #77** (closed): Sense comparator does not resolve a decision for resistive fuses; comparator offset unevidenced
- **Issue #36** (closed): T1 item 9 (testbenches shipped): testbench inventory over the smoke, sizing and design benches, attested with klt signoff --attest 9
- **PR #56**: feat: attest T1 item 9 testbench inventory and bump klt pin to 0.9.0

### 2026-11-01

- **PR #55**: Bump Repo Skills 0.24.7 -> 0.25.1

### 2026-10-30

- **Issue #28** (closed): T1 item 9 (testbenches shipped): sense-margin bench, testbench inventory and --attest 9

### 2026-10-28

- **Issue #35** (closed): T1 item 4 (LVS clean): klt lvs match of the analog array against its schematic netlist and of the decoder against its gate-level netlist
- **Issue #38** (closed): T1 item 11 (power delivery): klt erc supply spec for the array and decoder supplies, PDN and LVS power verdicts
- **Issue #51** (closed): T1 item 2/4 prerequisite: route and pin the analog array (wiring, 72 pins, substrate/well taps) so analog LVS can match
- **PR #52**: feat(layout): route and pin the analog array so extraction yields all 72 reference pins
- **PR #53**: feat(lvs): analog LVS match with the 133-dummy ring; cite item 4 for both partitions
- **PR #54**: feat(erc): supply ERC evidence for both partitions, item 11 met

### 2026-10-27

- **Issue #25** (closed): T1 item 1 (design sources, analog): schematics and derived netlist for the fuse array, program drivers and sense path
- **Issue #26** (closed): T1 item 1 (design sources, digital): klt synthesize efuse_otp_ctrl to a committed gf180mcu gate-level netlist
- **Issue #27** (closed): T1 item 10 (repo hygiene): README reproduction steps, controller bench in CI, klt signoff --attest 10
- **Issue #29** (closed): T1 item 2 (layout, analog): generated GDS for the fuse bitcell, 32x8 array, drivers and sense path
- **Issue #48** (closed): T1 item 3 (DRC), analog partition: grid-snap cell placement in gen_efuse_otp.py to clear 2560 *.ongrid.1 hits
- **Issue #49** (closed): T1 item 3 (DRC), digital partition: classify the 2525 hits by source and fix or document each
- **Issue #52** (closed): Single-source the controller parameter sets (runner.py CONFIGS, klt-fv.sh table, 9 request JSONs)
- **Issue #30** (closed): T1 item 1 (design sources, analog partition): xschem schematic and derived netlist for the 6+4 segmented current-cell array, switches, drivers and bias
- **Issue #31** (closed): T1 item 1 (design sources, digital partition): thermometer decoder and retiming latch RTL with its synthesized gf180mcu netlist
- **Issue #32** (closed): T1 item 2 (layout, analog partition): common-centroid unary array with dummies, switches and bias, generated GDS
- **Issue #33** (closed): T1 item 2 (layout, digital partition): place-and-route of the decoder and retiming latches, committed routed GDS
- **Issue #34** (closed): T1 item 3 (DRC clean): digital partition klt drc clean (analog delivered in #44)
- **Issue #37** (closed): T1 item 10 (repo hygiene): hygiene inventory attested with klt signoff --attest 10 and README reproduction section
- **Issue #45** (closed): Digital LVS: clknet_3_5__leaf_clk is split in the extracted layout
- **Issue #47** (closed): Stop tracking machine-local synth *.run.ys files (self-declared not commit-safe)
- **PR #39**: feat(design): generate analog xschem schematics and attest T1 item 1
- **PR #40**: feat(hygiene): attest T1 item 10 and add per-record reproduce table
- **PR #41**: feat(rtl): add thermometer decoder and retiming bank with synthesized netlist, attest digital item 1
- **PR #42**: feat(layout): generate analog array stream with recorded switching sequence
- **PR #43**: feat(layout): route the digital partition and attest item 2 (digital)
- **PR #44**: feat(layout): run klt drc on both partitions and cite item 3 evidence
- **PR #46**: feat(verification): record klt lvs runs for both partitions (both mismatch)
- **PR #48**: fix(layout): reach klt drc clean on the digital stream
- **PR #49**: fix: rerun digital klt lvs on the current stream and classify the earlier clock-net open
- **PR #50**: chore(synth): stop tracking machine-local *.run.ys

### 2026-10-25

- **PR #23**: ratification: install ee-key and market-key reviewer trees; align spec review wording
- **Issue #21** (closed): Install the EE-key and market-key ratification reviewer trees (2am#5346 stage 2)

### 2026-10-24

- **PR #26**: ci: run harness and spec tests in check_ci.py, drop inert hooks
- **Issue #24** (closed): Replace inert selftest/schema hooks in check_ci.py with the real test runs
- **PR #7**: ci: add repo checks, graded klt signoff manifest and README Reproduce section
- **Issue #4** (closed): Repo hygiene and CI (T1 item 10): real CI checks, a graded klt signoff manifest, README spec-issue fix

### 2026-10-23

- **Issue #14** (closed): rtl: synchronous OTP controller with arm-after-reset protection and cocotb bench (T1 items 1, 9, digital partition)
- **Issue #15** (closed): sim: size the nfet_06v0 program-select device for >= 10 mA across the decision-0005 corner set (T1 items 1, 5 groundwork, analog partition)
- **Issue #18** (closed): Cite the PDK numeric voltage limit for nfet_06v0 (follow-on from PR #17)
- **Issue #20** (closed): Remove dead --backend flag from sim/program-select/run.sh (parsed, never used, contradicts batch-only header)

### 2026-10-21

- **PR #17**: Bump Repo Skills 0.24.3 -> 0.24.7

### 2026-10-20

- **PR #14**: docs(spec): add bounded validation plan and pending review record
- **PR #13**: docs(spec): tabulate pinned sibling interfaces, add proposed record revision notes
- **PR #12**: docs(spec): add DR-0003 gradient review and unrun sensitivity plan
- **PR #11**: docs(spec): add classed requirements and source table with structural check

### 2026-10-17

- **Issue #2** (closed): Draft and ratify the target spec
- **PR #9**: feat(spec): propose target spec, sizing model and decision records
- **PR #8**: feat(sim): pin gf180mcuD toolchain and add cold-run corner and Monte Carlo smoke
- **PR #1**: chore(loom): Install Loom 0.19.1181
- **Issue #5** (closed): Behavioural reference model: INL/DNL, yield and switching-sequence gradient cancellation for a segmented array
- **Issue #3** (closed): PDK and simulator bring-up: pin gf180mcu and commit an ngspice smoke run
