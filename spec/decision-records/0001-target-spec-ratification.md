# 0001: Target spec ratification

- **Status**: proposed
- **Date**: 2026-10-17
- **Decided by**: pending. Ratification is the operator's act, not the authoring agent's; the EE key and market key review first, as input (see Amendment 2026-10-24).

## Context

The README target table was a DRAFT; every row was a proposal (issue #2).
`spec/target-spec.md` now carries a min/typ/max, a grading condition and a
corner set for each row, the segmentation trade, the mismatch method and the
sizing, reproducible with `python3 spec/sizing/size.py`.

## Decision

Ratify `spec/target-spec.md` as the specification for the 10 bit / 100 MS/s
target, with 8 bit / 50 MS/s as the fallback and 12 bit / 200 MS/s as a
stretch that is not sized. After ratification agents may not relax a row; a
change goes through a superseding record.

**This record is Proposed.** It flips to `ratified` only when the operator
approves or merges the pull request and edits the Status line (or approves the
change that does). The README keeps a PROPOSED marker until that same change.

## Alternatives considered

- **Ratify before the sizing is reproducible**: rejected; the criteria would
  be unfalsifiable.
- **Size the 12 bit stretch first**: rejected; 10 bits closes before 12 bits
  drives array size (CLAUDE.md).
- **Agent ratifies**: rejected; the spec rows are the standard agents are
  held to.

## Consequences

- Layout, schematic and array-generator issues can cite the rows.
- Rows that are budgets, not derivations (power, reference current), are
  ratified as budgets; the spec says so.
- The gradient amplitude is an assumption (DR-0003); a ratified spec with an
  assumed gradient means INL yield is a model result until extraction.

## Proposed revision note (2026-10-20, increment C of issue #2)

Not a status change; this record stays `proposed`. Coupled assumptions
reassessed against [`../interface-evidence.md`](../interface-evidence.md): the
power row (R12) and reference-current row (R13) remain budgets with no
schematic, and the reference chain has an unresolved common-mode conflict (I10)
and an unaccounted 10 uA opamp bias (I9). Ratifying this record would ratify
those rows as budgets only; it would not ratify sibling compatibility.
Unresolved loading, common-mode and output drive, noise and PSRR requirements
stay explicit open items, not requirements.

## Amendment 2026-10-24: review route (process text only)

Per the 2026-10-22 ruling (2am#5864), the EE key and the market key
(non-author agent reviewers, installed under `ratification/`) both review the
proposal first, as input; the operator then ratifies. Earlier wording in this
record and in `spec/` that called the review a "human act" is superseded. No
numeric row, target or decision in this record changed.
