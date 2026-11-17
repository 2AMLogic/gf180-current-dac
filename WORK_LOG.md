# Work Log

Chronological record of merged PRs and closed issues. Maintained by the Guide role; newest first.

### 2026-11-16

- **PR #115**: chore(loom): resync installed Loom to v0.19.1302
- **PR #114**: check: validate WORK_LOG.md citations resolve to real items
- **Issue #113** (closed): Nothing validates WORK_LOG.md citations: PR #112 added 59 entries from another project, all CI green

### 2026-11-15

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

- **PR #82**: docs: name the klt_required_commands record in sim/README.md instead of snapshotting it
- **PR #79**: docs: record a klt extract --parasitics probe of the analog array
- **Issue #72** (closed): Correct the stale klt_required_commands description in sim/README.md
- **Issue #67** (closed): Parasitic extraction probe of the analog array: one klt extract --parasitics run with a committed record
- **PR #81**: docs: split DR-0008's index_2 gloss by liberty table shape
- **Issue #76** (closed): DR-0008: index_2 gloss is wrong for the four setup/hold columns (constraint tables have no load axis)
- **Issue #68** (closed): Propose a decision record for the digital partition's I/O timing budget
- **PR #65**: docs: roadmap as of 2026-11-13
- **PR #74**: docs: add DR-0008 proposing the digital partition's I/O timing budget

### 2026-11-12

- **PR #62**: Bump Repo Skills 0.25.10 -> 0.26.1

### 2026-11-07

- **PR #59**: Bump Repo Skills 0.25.1 -> 0.25.10

### 2026-11-06

- **Issue #57** (closed): Bring README, layout and verification READMEs in line with the 14/22 signoff record
- **PR #58**: docs: align READMEs with the 14/22 signoff record

### 2026-11-05

- **Issue #36** (closed): T1 item 9 (testbenches shipped): testbench inventory over the smoke, sizing and design benches, attested with klt signoff --attest 9
- **PR #56**: feat: attest T1 item 9 testbench inventory and bump klt pin to 0.9.0

### 2026-11-01

- **PR #55**: Bump Repo Skills 0.24.7 -> 0.25.1

### 2026-10-28

- **Issue #35** (closed): T1 item 4 (LVS clean): klt lvs match of the analog array against its schematic netlist and of the decoder against its gate-level netlist
- **Issue #38** (closed): T1 item 11 (power delivery): klt erc supply spec for the array and decoder supplies, PDN and LVS power verdicts
- **Issue #51** (closed): T1 item 2/4 prerequisite: route and pin the analog array (wiring, 72 pins, substrate/well taps) so analog LVS can match
- **PR #52**: feat(layout): route and pin the analog array so extraction yields all 72 reference pins
- **PR #53**: feat(lvs): analog LVS match with the 133-dummy ring; cite item 4 for both partitions
- **PR #54**: feat(erc): supply ERC evidence for both partitions, item 11 met

### 2026-10-27

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

### 2026-10-21

- **PR #17**: Bump Repo Skills 0.24.3 -> 0.24.7

### 2026-10-20

- **PR #14**: docs(spec): add bounded validation plan and pending review record
- **PR #13**: docs(spec): tabulate pinned sibling interfaces, add proposed record revision notes
- **PR #12**: docs(spec): add DR-0003 gradient review and unrun sensitivity plan
- **PR #11**: docs(spec): add classed requirements and source table with structural check

### 2026-10-17

- **PR #9**: feat(spec): propose target spec, sizing model and decision records
- **PR #8**: feat(sim): pin gf180mcuD toolchain and add cold-run corner and Monte Carlo smoke
- **PR #1**: chore(loom): Install Loom 0.19.1181
- **Issue #5** (closed): Behavioural reference model: INL/DNL, yield and switching-sequence gradient cancellation for a segmented array
- **Issue #3** (closed): PDK and simulator bring-up: pin gf180mcu and commit an ngspice smoke run
