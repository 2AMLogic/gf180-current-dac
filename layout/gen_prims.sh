#!/usr/bin/env bash
# Regenerate the device primitives in layout/prims/ with `klt gen mos_array`.
# Local-only: needs the pinned PDK (PDK_ROOT, see sim/pdk.json). The committed
# prims/*.gds are the inputs of layout/gen_array.py, so CI re-runs the array
# generator without a PDK; run this script to refresh or re-verify them.
#   layout/gen_prims.sh          rewrite layout/prims/
#   layout/gen_prims.sh --check  regenerate to a temp dir, compare geometry
#                                with `klt diff`, exit 1 on any difference
set -euo pipefail
cd "$(dirname "$0")/.."
: "${PDK_ROOT:?set PDK_ROOT to the pinned gf180mcu PDK (sim/pdk.json)}"

out=layout/prims
if [ "${1:-}" = "--check" ]; then
  out="$(mktemp -d)"
  trap 'rm -rf "$out"' EXIT
fi

gen() { # name params-json
  klt gen mos_array --pdk gf180mcuD --params "$2" --cell-name "$1" \
      -o "$out/$1.gds" --format json > "$out/$1.report.json"
}

# Sizes are design/gen_analog.py's (DR-0006), read from the generator itself
# so no second copy of the numbers can drift: CS = unit current source,
# CAS = cascode, SW = steering switch, INV_N / INV_P = driver inverters.
for name in prim_cs prim_cas prim_sw prim_drvn prim_drvp; do
  gen "$name" "$(python3 design/gen_analog.py --prim-params "$name")"
done

if [ "${1:-}" = "--check" ]; then
  rc=0
  for f in prim_cs prim_cas prim_sw prim_drvn prim_drvp; do
    klt diff "layout/prims/$f.gds" "$out/$f.gds" > /dev/null || { echo "differs: $f" >&2; rc=1; }
  done
  exit $rc
fi
