#!/usr/bin/env bash
# Regenerate the routed digital-partition stream (T1 item 2, digital) with
# `klt place-and-route` on the synthesized netlist from `klt synthesize`.
#   layout/pnr/run.sh           rewrite layout/pnr/dac_digital.gds and report
#   layout/pnr/run.sh --check   rerun to a scratch copy, fail if the stream
#                               hash differs from the committed one
# klt is the one pinned in layout/toolchain.json, run through uvx so the host
# tool is untouched. Needs docker (the `openroad` wrapper) and the PDK at the
# revision in sim/pdk.json. One run, single corner; nothing here is a grid.
# Run from the repo root: the openroad wrapper mounts $PWD only.
set -euo pipefail
cd "$(dirname "$0")/../.."
pin="$(python3 -I -c 'import json;print(json.load(open("layout/toolchain.json"))["klt_install"])')"
# Pin the klayout engine to toolchain.json's klayout_package_pin: uvx alone
# resolves the newest klayout, and a GDS written by a different engine is
# different bytes (toolchain.json claims the byte hash only for the pin).
klayout_pin="$(python3 -I -c 'import json;print(json.load(open("layout/toolchain.json"))["klayout_package_pin"])')"
klt() { uvx --from "$pin" --with "klayout==$klayout_pin" klt "$@"; }
for c in place-and-route signoff sta; do
  klt --help | grep -qw "$c" || { echo "pinned klt lacks '$c'" >&2; exit 1; }
done

work=layout/pnr/.klt
rm -rf "$work"
klt place-and-route layout/pnr/request.json --pdk gf180mcuD --format json \
    > layout/pnr/.report.tmp
gds="$work/place-and-route/dac_digital.gds"
if [ "${1:-}" = "--check" ]; then
  want="$(sha256sum layout/pnr/dac_digital.gds | cut -d' ' -f1)"
  got="$(sha256sum "$gds" | cut -d' ' -f1)"
  rm -f layout/pnr/.report.tmp
  [ "$want" = "$got" ] || { echo "stream differs: committed $want, regenerated $got" >&2; exit 1; }
  echo "stream matches: sha256:$got"
  exit 0
fi
mv layout/pnr/.report.tmp layout/pnr/dac_digital.report.json
cp "$gds" layout/pnr/dac_digital.gds
cp "$work/place-and-route/dac_digital.v" layout/pnr/dac_digital.asbuilt.v
# Retain the routed DEF (and the flow's post-route SPEF, when it emits one)
# at committed paths: .klt/ is cleared at the top of the next invocation, and
# the DEF is the fixed geometry `klt sta` (verification/sta/) analyses and
# `klt extract` (verification/lvs/, digital) reads.
cp "$work/place-and-route/dac_digital.def" layout/pnr/dac_digital.def
if [ -f "$work/place-and-route/dac_digital.spef" ]; then
  cp "$work/place-and-route/dac_digital.spef" layout/pnr/dac_digital.spef
else
  rm -f layout/pnr/dac_digital.spef
fi
echo "sha256:$(sha256sum layout/pnr/dac_digital.gds | cut -d' ' -f1)"
