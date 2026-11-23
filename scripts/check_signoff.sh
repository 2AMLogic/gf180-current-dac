#!/usr/bin/env bash
# Regenerate the klt signoff verdict and fail if it differs from the committed
# record. KLT_PIN below is the release pin's single home; resolve it elsewhere
# with `scripts/check_signoff.sh --print-pin`. Exit 3 from klt (some item
# unmet) is a valid grading run; any other non-zero is a hard error.
set -uo pipefail
cd "$(dirname "$0")/.."
KLT_PIN="${KLT_PIN:-0.9.0}"
if [ "$#" -eq 1 ] && [ "$1" = "--print-pin" ]; then
  printf '%s\n' "$KLT_PIN"
  exit 0
fi
if [ "$#" -gt 0 ]; then
  echo "usage: scripts/check_signoff.sh [--print-pin]" >&2
  exit 2
fi
fresh="$(mktemp)"
trap 'rm -f "$fresh"' EXIT
rc=0
uvx --from "klayout-tools==${KLT_PIN}" klt signoff \
    --manifest manifests/gf180-current-dac.json \
    --format json > "$fresh" || rc=$?
if [ "$rc" -ne 0 ] && [ "$rc" -ne 3 ]; then
  echo "klt signoff exited $rc (expected 0 or 3)" >&2
  exit 1
fi
if ! cmp -s "$fresh" manifests/gf180-current-dac.signoff.json; then
  # A drifted attestation envelope (grading reason stale_evidence) also makes
  # the record differ, but the record is not what is wrong: the fix is
  # re-attesting the item, not regenerating the record (which would commit
  # the regression as the new baseline). Name the drifted item(s) and print
  # the per-item re-attest command before the regenerate message; print
  # nothing extra when no stale_evidence is present, so a genuinely stale
  # record's output is unchanged. Only envelope items -- those whose stale
  # detail actually carries artifact_binding.members -- are named; other
  # stale_evidence shapes keep the regenerate message.
  FRESH="$fresh" KLT_PIN="$KLT_PIN" python3 <<'PYEOF' >&2 || true
import json, os, sys

fresh = json.load(open(os.environ["FRESH"]))
drift = {}
for it in fresh.get("items", []):
    if it.get("reason") != "stale_evidence" or it.get("id") is None:
        continue
    paths = set()
    binding = (it.get("detail") or {}).get("artifact_binding") or {}
    for m in binding.get("members") or []:
        if isinstance(m, dict) and m.get("status") == "stale":
            p = m.get("path")
            if isinstance(p, dict):
                p = p.get("path")
            if p:
                paths.add(str(p))
    # Only an attestation envelope carries stale artifact_binding.members;
    # the other stale_evidence shapes (a drifted provenance.input artifact,
    # a stale content-hash pin) have no envelope to re-attest, so printing
    # a --attest command for them would point at the wrong fix.
    if not paths:
        continue
    drift.setdefault(it["id"], set()).update(paths)

if not drift:
    sys.exit(0)

pin = os.environ["KLT_PIN"]
evidence = json.load(open("manifests/gf180-current-dac.json")).get("evidence", {})
print("Attestation envelope drifted: the item(s) below cite a stale member hash,")
print("which is why the record differs. Re-attest first -- regenerating the record")
print("alone would commit the regression as the new baseline.")
for n in sorted(drift):
    where = sorted(drift[n])
    print("  T1 item %d (drifted member: %s)" % (n, ", ".join(where)))
    files = []
    for key, val in evidence.items():
        if key == str(n) or key.startswith("%d." % n):
            for e in (val if isinstance(val, list) else [val]):
                if isinstance(e, dict) and e.get("file"):
                    files.append(e["file"])
    if not files:
        files = ["evidence/item%d.json" % n]
    for f in files:
        inv = None
        try:
            inv = json.load(open(f)).get("source")
        except Exception:
            pass
        print("  uvx --from klayout-tools==%s klt signoff --attest %d --inventory %s -o %s"
              % (pin, n, inv or "attest/item%d.json" % n, f))
print()
PYEOF
  echo "Committed signoff record is stale. Regenerate:" >&2
  echo "  uvx --from klayout-tools==${KLT_PIN} klt signoff --manifest manifests/gf180-current-dac.json --format json > manifests/gf180-current-dac.signoff.json" >&2
  diff <(python3 -m json.tool "$fresh") <(python3 -m json.tool manifests/gf180-current-dac.signoff.json) >&2 || true
  exit 1
fi
python3 -c "import json; d=json.load(open('manifests/gf180-current-dac.signoff.json')); print('signoff record fresh: tier', d['tier'], '(T1 met %d/%d)' % (d['t1_met_count'], d['t1_item_count']))"
