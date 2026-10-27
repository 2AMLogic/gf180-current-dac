#!/usr/bin/env bash
# Regenerate the klt signoff verdict and fail if it differs from the committed
# record. Pin matches .github/workflows/ci.yml. Exit 3 from klt (some item
# unmet) is a valid grading run; any other non-zero is a hard error.
set -uo pipefail
cd "$(dirname "$0")/.."
KLT_PIN="${KLT_PIN:-0.8.0}"
fresh="$(mktemp)"
trap 'rm -f "$fresh"' EXIT
rc=0
uvx --from "klayout-tools==${KLT_PIN}" klt signoff \
    --manifest manifests/gf180-current-dac.json \
    --tiers-doc manifests/design-evidence-tiers.md \
    --format json > "$fresh" || rc=$?
if [ "$rc" -ne 0 ] && [ "$rc" -ne 3 ]; then
  echo "klt signoff exited $rc (expected 0 or 3)" >&2
  exit 1
fi
if ! cmp -s "$fresh" manifests/gf180-current-dac.signoff.json; then
  echo "Committed signoff record is stale. Regenerate:" >&2
  echo "  uvx --from klayout-tools==${KLT_PIN} klt signoff --manifest manifests/gf180-current-dac.json --tiers-doc manifests/design-evidence-tiers.md --format json > manifests/gf180-current-dac.signoff.json" >&2
  diff <(python3 -m json.tool "$fresh") <(python3 -m json.tool manifests/gf180-current-dac.signoff.json) >&2 || true
  exit 1
fi
python3 -c "import json; d=json.load(open('manifests/gf180-current-dac.signoff.json')); print('signoff record fresh: tier', d['tier'], '(T1 met %d/%d)' % (d['t1_met_count'], d['t1_item_count']))"
