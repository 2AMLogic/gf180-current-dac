#!/usr/bin/env bash
# Regenerate the klt drc envelopes (T1 item 3) for the two partition streams.
#   layout/drc/run.sh           rewrite evidence/item3-{analog,digital}.json
#   layout/drc/run.sh --check   verify the committed envelopes still match the
#                               committed GDS and deck (klt drc --check, cheap mode)
# Unmodified tool output: no waivers, no rule selection, no deck changes. klt is
# the one pinned in layout/toolchain.json, run through uvx so the host tool is
# untouched. Two single-unit runs; nothing here is a grid. Exit 3 from klt drc
# means violations found, which is a valid result to record, not a failure.
set -euo pipefail
cd "$(dirname "$0")/../.."
pin="$(python3 -I -c 'import json;print(json.load(open("layout/toolchain.json"))["klt_install"])')"
klt() { uvx --from "$pin" klt "$@"; }
klt --help | grep -qw drc || { echo "pinned klt lacks 'drc'" >&2; exit 1; }

# name  stream  top-cell
parts=(
  "analog layout/gf180-current-dac-analog.gds dac_analog_layout"
  "digital layout/pnr/dac_digital.gds dac_digital"
)
for p in "${parts[@]}"; do
  read -r name gds top <<<"$p"
  out="evidence/item3-$name.json"
  if [ "${1:-}" = "--check" ]; then
    klt drc --check "$out" "$gds"
    continue
  fi
  rc=0
  klt drc "$gds" --deck gf180mcu --top "$top" --pdk gf180mcuD --format json \
      > "$out.tmp" || rc=$?
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 3 ]; then
    rm -f "$out.tmp"; echo "klt drc $name exited $rc" >&2; exit 1
  fi
  mv "$out.tmp" "$out"
  echo "$name: $(python3 -I -c "import json;d=json.load(open('$out'));print(d['status'],d['violation_count'])") sha256:$(sha256sum "$out" | cut -d' ' -f1)"
done
