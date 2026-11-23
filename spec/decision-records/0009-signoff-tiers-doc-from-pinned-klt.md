# 0009: Signoff tiers checklist comes from the pinned klt

- **Status**: proposed
- **Date**: 2026-11-23
- **Decided by**: operator ruling 2026-11-23 (attended `/fleet:decide` session,
  round 20261121-r19, q103), issued on issue #78

## Context

Until this record, this repo carried a vendored copy of klayout-tools'
`docs/design-evidence-tiers.md` at `manifests/design-evidence-tiers.md`
(1054 lines, header pinned to upstream commit `fc02bdf0`) and passed it to
`klt signoff` via `--tiers-doc`, overriding the copy every packaged klt
install ships as wheel package data. Nothing re-vendored the file
automatically; "Do not edit; re-vendor to update" was a manual chore that had
already lapsed — the vendored copy was 87 changed lines behind the copy inside
the pinned 0.9.0 wheel, missing (among others) the T1 item 4 LVS runset
allowlist update, the item 6 analog-partition ruling, and the item 3
foundry-cell disclosed-exception rule. Every lapse made the recorded tier
claim quote an older ladder than the tool grades against, with no check
catching it.

Vendoring was a deliberate choice (single commit `118eb4b`, provenance header
plus two wired call sites) with no decision record stating its rationale, so
removing it reversed that choice and needed an operator ruling — obtained
2026-11-23 on issue #78.

## Decision

**Remove the vendored copy and the `--tiers-doc` override. The pinned
klayout-tools release alone selects the checklist.**

- `manifests/design-evidence-tiers.md` is deleted; the ladder the record is
  graded against is the one bundled inside the `klayout-tools==${KLT_PIN}`
  wheel that `scripts/check_signoff.sh` already resolves via `uvx`.
- No caller passes `--tiers-doc`.
- `manifests/gf180-current-dac.signoff.json` records the bundled doc's own
  path (`docs/design-evidence-tiers.md`) and content hash, so a `KLT_PIN`
  bump that changes the ladder changes the record and fails
  `scripts/check_signoff.sh`'s byte-compare — that CI comparison is retained
  and is what catches a checklist change at a pin bump.
- Prose that described the vendoring (ROADMAP.md, rtl/README.md) now says the
  checklist comes from the pinned tool and links the document in
  klayout-tools at the pinned tag
  ([`docs/design-evidence-tiers.md` at `v0.9.0`](https://github.com/2AMLogic/klayout-tools/blob/v0.9.0/docs/design-evidence-tiers.md)).

The evidence record is therefore no longer self-contained: reading the ladder
an item was graded against means reading the pinned tool's bundled copy, not a
file in this repo. The operator ruling accepted that tradeoff — the pin is the
single thing to review, and the fresh-vs-committed comparison in
`scripts/check_signoff.sh` is the mechanism that surfaces a ladder change.

## Verification of the reversal

Both runs at `klayout-tools==0.9.0` on this manifest, before the removal was
committed: identical exit code (3), identical `tier` (`null`), identical
`t1_item_count` (22) and `t1_met_count` (14), and identical `status`/`reason`
on all 25 graded items. The only differences in the regenerated record are
`source_doc`, `source_doc_content_hash`, and the item prose quoted from
whichever doc was read — exactly the fields the ruling permits to change.

## Alternatives considered

- **Keep the copy and fix the staleness instead** (re-vendor to the 0.9.0
  bytes and add a CI check that the vendored bytes equal the bundled bytes at
  `KLT_PIN`): rejected by the operator ruling of 2026-11-23. It would keep
  1054 lines and a standing manual chore to preserve a self-contained record
  the ruling judged not worth that cost.
- **Keeping the current state** (a stale copy overriding a fresher one with no
  check): rejected by everyone; the original report on issue #78 shows a
  reader of the vendored copy would conclude no gf180mcu LVS runset can grade
  `met`, which stopped being true upstream.
