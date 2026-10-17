# gf180-current-dac — agent instructions

Open-source canary block: a segmented current-steering DAC on the gf180mcu
PDK, designed and verified by AI agents. **Mixed-signal** — a matched
analog current array and a synthesized decoder — so both flows apply.

- **PDK**: gf180mcu (open PDK, google/gf180mcu-pdk). Analog: xschem +
  ngspice. Digital: cocotb + Icarus, Yosys, OpenROAD. Layout, DRC, and LVS
  through klayout-tools (`klt`) in both cases.
- **The common-centroid array is the point, and the risk.** Static
  linearity is set by unit-cell matching and by how the placement and the
  switching sequence cancel gradients. Generate the array; do not hand-place
  hundreds of cells. Dummies, matched routing to each cell, and post-layout
  extraction of the whole array are part of the design. Expect the tools to
  be weakest at parameterized array generation, symmetric routing, and
  extraction at array scale, and file accordingly.
- **Mismatch claims need a model and a method.** INL and DNL come from
  random mismatch plus systematic gradient. State which mismatch model the
  PDK provides and which the simulation used, the Monte Carlo sample count,
  and how the gradient was modelled, next to every linearity number. If the
  PDK's models do not carry the mismatch data a claim needs, say so; do not
  substitute an assumed value without a decision record.
- **Scope discipline.** The reference current is an input at the
  boundary. On this PDK, `gf180-bandgap` builds the reference and
  `gf180-opamp` an amplifier; adopt them by pinned reference
  (`reuse.lock.json`) or write the decision record saying why this repo
  keeps its own.
- **Friction protocol (the canary's job)**: every time klayout-tools is
  awkward, missing a capability, or wrong for what you need, file an issue at
  `2AMLogic/klayout-tools` describing the tool gap generically — that tracker
  is scoped to the tool, so keep design-specific detail out of it and describe
  the gap, not the design.
- **Verification is the product**: no claim without a testbench. PVT corners
  on every recorded analog result; recorded results are append-only
  evidence. A simulated number is never called measured.
- Spec changes go through `spec/` with a decision record; agents do not relax
  the ratified spec to make results pass.
- **10 bits at 100 MS/s is the target.** 8 bits at 50 MS/s is the fallback
  and 12 bits a stretch. Do not let 12-bit matching drive the array size
  before 10 bits closes.

<!-- BEGIN LOOM ORCHESTRATION -->
This repository uses [Loom](https://github.com/rjwalters/loom) for AI-powered development orchestration — see the Loom repository for the full guide (roles, labels, worktrees, configuration). When installed, Loom also writes a locally-substituted copy of that guide to `.loom/CLAUDE.md`.

Work is coordinated through `loom:` labels on issues and pull requests, and the same roles run either under `loom-daemon` or by hand in an attended session — daemon mode is optional. Create the labels once with `.loom/scripts/sync-labels.sh` (an install ships `.github/labels.yml` but does not create the labels on the forge). A pull request ready for review carries `loom:review-requested`; Judge reviews it and applies `loom:pr` (approved) or `loom:changes-requested`; Doctor fixes a `loom:changes-requested` pull request and returns it to `loom:review-requested`. Only a `loom:pr` pull request gets merged, and always via this repo's merge script (`.loom/scripts/merge-pr.sh`) — never a raw forge merge command such as `gh pr merge`. Full state machine: `.loom/docs/label-state-machine.md`.
<!-- END LOOM ORCHESTRATION -->
