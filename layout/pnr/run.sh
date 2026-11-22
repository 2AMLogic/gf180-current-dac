#!/usr/bin/env bash
# Regenerate the routed digital-partition stream (T1 item 2, digital) with
# `klt place-and-route` on the synthesized netlist from `klt synthesize`.
#   layout/pnr/run.sh           rewrite layout/pnr/dac_digital.gds and report
#   layout/pnr/run.sh --check   rerun to a scratch copy, fail if the stream
#                               or the retained DEF differs from the committed
#                               one, or if the STA report's input digest does
#                               not identify the committed DEF
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
  rm -f layout/pnr/.report.tmp
  # Compare one committed artifact with its regenerated counterpart.
  # compare <what> <committed path> <regenerated path>
  compare() {
    [ -f "$2" ] || { echo "$1 mismatch: committed file missing: $2" >&2; exit 1; }
    [ -f "$3" ] || { echo "$1 mismatch: regenerated file missing: $3" >&2; exit 1; }
    local want got
    want="$(sha256sum "$2" | cut -d' ' -f1)"
    got="$(sha256sum "$3" | cut -d' ' -f1)"
    [ "$want" = "$got" ] || { echo "$1 differs: committed $want, regenerated $got" >&2; exit 1; }
    echo "$1 matches: sha256:$got"
  }
  compare stream layout/pnr/dac_digital.gds "$gds"
  compare "routed DEF" layout/pnr/dac_digital.def "$work/place-and-route/dac_digital.def"
  # The committed STA report (verification/sta/) must have analysed exactly
  # that committed DEF: its provenance.input.content_hash is the DEF digest.
  python3 -I - "$(sha256sum layout/pnr/dac_digital.def | cut -d' ' -f1)" <<'PY'
import json, re, sys
want = "sha256:" + sys.argv[1]
try:
    report = json.load(open("verification/sta/dac_digital.report.json"))
    digest = report["provenance"]["input"]["content_hash"]
except (OSError, ValueError, KeyError, TypeError):
    sys.exit("STA report mismatch: no readable .provenance.input.content_hash "
             "in verification/sta/dac_digital.report.json")
if not isinstance(digest, str) or re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is None:
    sys.exit(f"STA report mismatch: malformed input digest {digest!r}")
if digest != want:
    sys.exit(f"STA report mismatch: input digest {digest} does not identify "
             f"the committed DEF ({want})")
print(f"STA report input digest matches the committed DEF: {want}")
PY
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
