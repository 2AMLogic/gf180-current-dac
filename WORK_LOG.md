# Work Log

Chronological record of merged PRs and closed issues. Maintained by the Guide role; newest first.

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
