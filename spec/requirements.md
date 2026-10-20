# Requirements and budget derivation

- **Status**: PROPOSED, increment A of issue #2 (`Part of #2`). Ratifies nothing.
  No numeric row of [`target-spec.md`](target-spec.md) is changed here.
- **Date drafted**: 2026-10-20
- **Reviewer**: none yet. The engineering and market review is a human act and
  is recorded in `spec/reviews/0001-engineering-and-market.md` (increment D).
  Until a human names an outcome there, the market reading below is the
  Builder's reading of public material, not a reviewed conclusion.
- **Evidence class**: each requirement row below is classed `requirement`,
  `model output`, `design choice` or `provisional budget`, and cites a source
  row or says `none, provisional`. A source was cited only if its page was read
  in this session; anything else is listed as `not retrieved` and no claim is
  taken from it.

## 1. Intended use case

The repository is a canary block for the open-source gf180mcu flow
(`CLAUDE.md`, `README.md`): its purpose is to exercise the tools on a
common-centroid array, not to serve a named product. The 10 bit / 100 MS/s
target, the 8 bit / 50 MS/s fallback and the 12 bit stretch come from the
project's own instructions, not from a customer or a standard. So:

- **There is no market-derived requirement set.** No customer, standard or
  datasheet in this repo says the block must be 10 b / 100 MS/s. The target is
  a `design choice` made by the operator (`CLAUDE.md`), kept unchanged.
- The source table below is used for something narrower: showing that the
  target is a plausible point for a general-purpose current-steering DAC (a
  commercial 10 bit part at this rate exists, S1) and what published
  implementations report at this resolution and rate (S2, S3). That is context
  for the reviewer, not a derivation.
- **Market review is outstanding.** Whether any use case (direct digital
  synthesis, communications transmit, waveform generation) justifies the
  numbers is for the human reviewer. This document does not claim it.

## 2. Sources

Retrieval date for every row: 2026-10-20.

| ID | Source | Claim used | Applicability to a 10 b / 100 MS/s gf180mcu DAC | Limitation |
|---|---|---|---|---|
| S1 | Texas Instruments DAC900 product page, <https://www.ti.com/product/de-de/DAC900> (manufacturer, primary for that part). Datasheet SBAS505 itself was fetched but its PDF text could not be read here. | 10 bit, segmented current-source output; full-scale current adjustable 2 mA to 20 mA by one external resistor; SFDR 68 dBc at 5 MHz output, 100 MSPS; 200 kohm output impedance; 2.7 V to 5.5 V supply; 170 mW typical at 5 V; -40 to 85 C | Shows a commercial 10 bit current-steering part spans the target rate and that 2 mA is the low end of a normal full-scale range | Page summary only: no INL/DNL on the page, the update-rate figures on the page disagree (165 vs 200 MSPS), SFDR test conditions are partly missing. 5 V-class bipolar-era power and a different process; not a gf180mcu comparison |
| S2 | Xu et al., "Design and verification of a 10-bit 1.2-V 100-MSPS D/A IP core based on a 0.13-um low power CMOS process", J. Semicond. 31(9) 095007, 2010, <https://www.jos.ac.cn/article/doi/10.1088/1674-4926/31/9/095007> (peer-reviewed paper; abstract page read) | 10 bit, 100 MSPS, 1.2 V; reported SFDR 70 dB at 1-5 MHz output; INL < 1 LSB, DNL < 0.5 LSB; 10 mW; about 0.2 mm^2; centrally symmetric layout routing for the current sources | Same resolution and rate, so a published existence point for the target | Different node and supply. The abstract gives no full-scale current, load or unit-cell sizing, so none of it transfers to current budgets. SFDR is quoted at 1-5 MHz, not near Nyquist. Figures are the authors' reported results; this repo has not reproduced them |
| S3 | Jorgensen and Tunheim, "A 10-bit 100 MSamples/s BiCMOS D/A Converter", ISCAS 1996 pp. 425-428, <https://orbit.dtu.dk/en/publications/a-10-bit-100-msampless-bicmos-da-converter-2/> (conference paper; repository record read) | 0.8 um BiCMOS, 5 V, 650 mW; measured INL/DNL about 2 LSB and SFDR about 43 dB at about 0.3 fs | A 100 MS/s 10 bit design with SFDR falling short of 60 dB at high output frequency, so dynamic SFDR at this rate is the hard part | Old process and bipolar steering; record-page summary, not the full paper. Shows a risk, not a threshold |
| S4 | Pelgrom, Duinmaijer, Welbers, "Matching properties of MOS transistors", IEEE JSSC 24(5), 1989 | Area-scaled random mismatch, sigma proportional to 1/sqrt(WL), plus a distance term | Underlies the mismatch scaling used in `spec/sizing/size.py` | **not retrieved.** Only bibliographic details were seen in search results; no claim is taken from the paper itself. The PDK's own formulas are traced from `sm141064.spice` in `target-spec.md` section 4, which is the evidence actually used |
| S5 | Van den Bosch, Steyaert, Sansen, work on SFDR-bandwidth limits of current-steering DACs (book, Springer 2004) | Source of the output-impedance and code-dependent capacitance SFDR argument | Would back `target-spec.md` section 5 | **not retrieved.** Authorship and title are from memory plus a search listing of the book's table of contents; not read. `target-spec.md` section 5 is therefore a first-order derivation by this repo, not a cited result |
| S6 | Analog Devices AD9750 datasheet, <https://www-cce.cldnet.analog.com/media/en/technical-documentation/data-sheets/AD9750.pdf> | 10 bit, 2-20 mA scalable full-scale (from a search listing only) | Would give a second manufacturer data point | **not retrieved.** Connection refused on 2026-10-20; nothing taken from it |

## 3. Requirements and budgets

Classes: `requirement` (an external constraint a source or the operator
imposes), `model output` (derived by `spec/sizing/size.py` under its stated
assumptions), `design choice` (picked by this project among alternatives),
`provisional budget` (a placeholder no schematic supports yet). Row values are
quoted from `target-spec.md`; nothing here changes them.

| ID | Item | Value as in target-spec.md | Class | Source |
|---|---|---|---|---|
| R1 | Resolution and update rate | 10 bit, 100 MS/s (fallback 8 bit / 50 MS/s, stretch 12 bit / 200 MS/s) | design choice | none, provisional. Operator target in `CLAUDE.md`; S1 and S2 show the point exists elsewhere, which does not make it a requirement |
| R2 | INL and DNL | within 0.5 LSB, endpoint-corrected | design choice | none, provisional. Project target; S2 reports DNL < 0.5 LSB and INL < 1 LSB for a different design |
| R3 | SFDR near Nyquist | 60 dBc at 45 MHz | design choice | none, provisional. Project target; S3 shows 60 dB at high output frequency is not automatic |
| R4 | INL yield criterion | >= 99.7 % of Monte Carlo samples within 0.5 LSB | design choice | none, provisional |
| R5 | Unit-cell source sigma | 0.50 % | model output | none, provisional. From the PDK mismatch formulas and `size.py`; assumes only the current-source device contributes and a 0.75 % total budget |
| R6 | INL yield at sizing point | 99.92 % | model output | none, provisional. Assumed-model yield (10,000 samples, seed 20261017, assumed gradient of DR-0003); not demonstrated chip yield and not a full-array SPICE Monte Carlo |
| R7 | Unit output impedance | >= 12.8 Mohm | model output | none, provisional. First-order single-ended bound for 60 dBc into 50 ohm (`target-spec.md` section 5); S5 not retrieved |
| R8 | Code-dependent output capacitance | <= 283 fF per output | model output | none, provisional. Same first-order model as R7 |
| R9 | Full-scale current | 2.0 mA typ (1.8 to 2.2 mA) | design choice | S1. Within the 2-20 mA range of a commercial part, at its low end; chosen for the 50 ohm, +/-100 mV swing and for power, not required by any source |
| R10 | Output load | 50 ohm | design choice | none, provisional |
| R11 | Supply and device flavor | 3.3 V -/+10 %, 3.3 V devices | design choice | none, provisional. DR-0002; the node's device set bounds the choice, no application imposes it |
| R12 | Power at full scale, 100 MS/s | 25 mW typ, 30 mW max | provisional budget | none, provisional. Output stage alone is 2 mA x 3.3 V = 6.6 mW; the rest has no schematic. S2 reports 10 mW at 1.2 V and S1 170 mW at 5 V, neither comparable |
| R13 | Reference current input | 20 uA typ (18 to 22 uA), mirrored 100:1 | provisional budget | none, provisional. Interface to `gf180-bandgap` is not yet checked against the pinned commit (increment C) |
| R14 | Code-dependent noise, PSRR, reference loading, common-mode and output drive | no value | provisional budget | none, provisional. Unresolved; carried as open items, see section 4 |

## 4. What stays unresolved

- No use case or standard fixes any row; all are `design choice`,
  `model output` or `provisional budget`. The market review must either
  supply a source for R1 to R4 or accept them as project choices.
- R12 and R13 have no schematic behind them; they move only through a
  superseding decision record after ratification.
- Noise, PSRR, reference loading and output common-mode drive (R14) have no
  requirement yet. Increment C tabulates what the pinned siblings expose.
- S4 to S6 are not retrieved. If the reviewer wants them cited, someone must
  fetch the documents; the claims are not taken from memory in the meantime.
