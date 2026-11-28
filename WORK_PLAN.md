# Work Plan

Backlog snapshot from current GitHub label state, maintained by the Guide role.
Direction lives in the hand-written roadmap: [`ROADMAP.md`](ROADMAP.md).

The body below is a snapshot of GitHub label state as of the last merged docs-maintenance PR — it may lag live labels until the next one merges. The `_Generated:` stamp at the top of the generated region dates the snapshot; `git log -1 -- WORK_PLAN.md` finds the merge that wrote it.

<!-- Maintained automatically by the Guide triage agent. Manual edits are fine but may be overwritten. -->

<!-- guide:plan-body:start -->
_Generated: 2026-11-28T11:45:36Z (snapshot; compare against live labels)_
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — a human merge decision, or the prerequisite shown, is missing.

- **#186**: chore: resync installed Loom surfaces *(held: champion critical-file hold)*

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

- **#22**: Open the spec ratification PR for DR-0001..DR-0005 and get both key reviews

## Important

`loom:important`; taken before unlabelled work.

- **#2**: Draft and ratify the target spec *(held)*

## Ready

Human-approved issues (`loom:issue`) ready for implementation — excluding held (`loom:blocked`/`loom:operator`/`loom:frozen`), `loom:building`, and issues with an open linked PR (native admission `OPEN_PR`; listed under Issues with Open PRs).

_None._

## Issues with Open PRs (Not Dispatchable)

`loom:issue` issues an open linked PR already holds — native admission would refuse them (`OPEN_PR`); listed with the PR and its stage, not counted above.

_None._

## In Progress

Issues currently being built (`loom:building`).

- **#22**: Open the spec ratification PR for DR-0001..DR-0005 and get both key reviews

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#29**: docs(spec): add ratification packet for the key reviews *(held)*

## Approved (Awaiting Merge)

PRs that passed review (`loom:pr`); unmarked PRs are queued for Champion auto-merge, PRs marked `*(held …)*` are not (the hold decides).

- **#186**: chore: resync installed Loom surfaces *(held: champion critical-file hold)*

## Proposed

Issues carrying `loom:curated`.

- **#2**: Draft and ratify the target spec *(curated)* *(held)*
- **#6**: Track the gap to T1 (klayout-tools design-evidence-tiers.md) *(curated)*
- **#22**: Open the spec ratification PR for DR-0001..DR-0005 and get both key reviews *(curated)*
- **#127**: Merge queue: add the merge_group trigger to the required-check workflow(s) *(curated)* *(held)*

## Proposed (Architect / Hermit)

- **#146**: Scope the work-log citation cache to one check *(hermit)* *(held)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 1 |
| Very important | 1 |
| Important | 1 |
| Ready (`loom:issue`, net of holds/building/open-linked-PRs) | 0 |
| In Progress (`loom:building`) | 1 |
| Held, no other bucket | 1 |
| PRs awaiting review | 1 |
| Approved PRs awaiting merge | 1 |
| Curated | 4 |
| Architect / Hermit proposals | 1 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
