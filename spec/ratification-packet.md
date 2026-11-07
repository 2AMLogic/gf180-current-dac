# Ratification packet

A pointer index for the EE key, the market key and the operator. It lists what
to read and what ratification would edit. **Nothing in this file ratifies
anything**: every record stays `proposed`, every spec row stays a proposal, and
the PROPOSED markers stay. It restates no numbers; read them at the source.

Tracker: issue #2 (the operator keeps it open). Ratification is the operator's
act, after the key reviews.

## Decision records

All are `proposed` as of this packet.

| Record | Path | Status |
|---|---|---|
| DR-0001 | [`decision-records/0001-target-spec-ratification.md`](decision-records/0001-target-spec-ratification.md) | proposed |
| DR-0002 | [`decision-records/0002-device-flavor-and-supply.md`](decision-records/0002-device-flavor-and-supply.md) | proposed |
| DR-0003 | [`decision-records/0003-gradient-amplitude-assumption.md`](decision-records/0003-gradient-amplitude-assumption.md) | proposed |
| DR-0004 | [`decision-records/0004-reference-source-gf180-bandgap.md`](decision-records/0004-reference-source-gf180-bandgap.md) | proposed |
| DR-0005 | [`decision-records/0005-bias-loop-amplifier-gf180-opamp.md`](decision-records/0005-bias-loop-amplifier-gf180-opamp.md) | proposed |

## Spec rows under review

The 18 rows of the parameter table in [`target-spec.md`](target-spec.md)
section 1, by name:

1. Resolution
2. Update rate
3. Segmentation
4. INL, endpoint-corrected
5. DNL
6. SFDR
7. Full-scale current
8. Output load
9. Output compliance
10. Unit output impedance (DC)
11. Code-dependent output capacitance
12. Unit-cell source mismatch
13. Unit-cell gate area (Leff x Weff)
14. Supply and devices
15. Power
16. Reference current input
17. Switching sequence
18. Signoff

## Evidence to read

| Document | What it gives the keys |
|---|---|
| [`requirements.md`](requirements.md) | sources and the class of each requirement |
| [`sensitivity-plan.md`](sensitivity-plan.md) | review of the gradient assumption (DR-0003); proposed, unrun |
| [`interface-evidence.md`](interface-evidence.md) | what the pinned `gf180-bandgap` and `gf180-opamp` expose (DR-0004, DR-0005) |
| [`validation-plan.md`](validation-plan.md) | bounded, unrun validation items; each needs separate authorization |
| [`sizing/`](sizing/) | sizing model, its generated output, and the instance-independence probe |

## Review record

[`reviews/0001-engineering-and-market.md`](reviews/0001-engineering-and-market.md)
is a template with outcome `pending`. Its outcomes belong to the keys, not to
this packet or to a Builder. The key verdicts are posted on the PR that carries
this packet, by `ratify-key.sh` from the `2AMLogic/2am` checkout.

## What the operator's ratification edits

Not done by this packet; listed so the edit set is explicit.

- The `- **Status**:` line of each of DR-0001..DR-0005 (`proposed` to `ratified`).
- The PROPOSED marker in [`README.md`](README.md) (line 4) and in the
  repository `README.md` target specification heading.
- The outcome fields of [`reviews/0001-engineering-and-market.md`](reviews/0001-engineering-and-market.md).
- `spec/check_spec.py` currently requires the records to stay `proposed` and the
  PROPOSED marker to remain once `requirements.md` exists; ratification must
  update that check in the same change.
