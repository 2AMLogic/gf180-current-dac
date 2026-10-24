# spec

The target specification, its sizing, and the decision records behind it.
Status of the whole set: **PROPOSED** until the operator ratifies
[DR-0001](decision-records/0001-target-spec-ratification.md).

| File | What |
|---|---|
| [`target-spec.md`](target-spec.md) | parameter table (min/typ/max, condition, corners), tiers, segmentation, mismatch method, output-impedance requirement |
| [`requirements.md`](requirements.md) | use case, source table, and each requirement classed as requirement / model output / design choice / provisional budget (proposal; review outcome pending) |
| [`sensitivity-plan.md`](sensitivity-plan.md) | review of DR-0003's gradient assumption and a proposed (unrun) sensitivity matrix over gradient, random mismatch, omitted contributions, placement and sequence |
| [`interface-evidence.md`](interface-evidence.md) | what the pinned `gf180-bandgap` and `gf180-opamp` commits expose (reference, loading, common-mode, output drive, noise, PSRR) against what the array needs; open items and one conflict (proposal; review outcome pending) |
| [`validation-plan.md`](validation-plan.md) | bounded validation plan: per question the evidence, resource estimate, sample/request/retry caps and stop condition; every item unrun and needing separate authorization |
| [`reviews/0001-engineering-and-market.md`](reviews/0001-engineering-and-market.md) | engineering and market review record; template, outcome `pending`, to be filled by the EE key and the market key (non-author agent reviewers) before the operator ratifies |
| [`sizing/size.py`](sizing/size.py) | sizing model; `python3 spec/sizing/size.py` regenerates [`sizing/sizing-output.md`](sizing/sizing-output.md), `--check` diffs against it |
| [`sizing/instance-independence-probe.md`](sizing/instance-independence-probe.md) | one-corner probe: PDK mismatch is drawn per instance, `m=N` does not average |
| [`check_spec.py`](check_spec.py) | structural check; tests in `tests/` (`python3 -m unittest discover -s spec/tests`) |

## Decision records

A ratified record is never deleted or rewritten; supersede it with a new one.

| Record | Title | Status |
|---|---|---|
| [0001](decision-records/0001-target-spec-ratification.md) | Target spec ratification | proposed |
| [0002](decision-records/0002-device-flavor-and-supply.md) | 3.3 V devices and supply | proposed |
| [0003](decision-records/0003-gradient-amplitude-assumption.md) | Gradient amplitude is an assumption | proposed |
| [0004](decision-records/0004-reference-source-gf180-bandgap.md) | Reference source: adopt gf180-bandgap | proposed |
| [0005](decision-records/0005-bias-loop-amplifier-gf180-opamp.md) | Bias-loop amplifier: adopt gf180-opamp | proposed |
