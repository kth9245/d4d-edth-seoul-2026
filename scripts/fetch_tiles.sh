#!/usr/bin/env bash
# Download Seoul metro basemap tiles once (needs internet). Demo then runs offline.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
OUT=modules/cop-ui/public/tiles/seoul.pmtiles
BBOX="126.6,37.35,127.3,37.75"
VER=1.31.2
if [ -s "$OUT" ]; then echo "tiles already present: $OUT"; exit 0; fi
mkdir -p .tools "$(dirname "$OUT")"
if [ ! -x .tools/pmtiles ]; then
  arch=$(uname -m); [ "$arch" = "aarch64" ] && arch=arm64
  curl -fsSL "https://github.com/protomaps/go-pmtiles/releases/download/v${VER}/go-pmtiles_${VER}_Linux_${arch}.tar.gz" \
    | tar -xz -C .tools pmtiles
fi
BUILD=$(curl -fsSL https://build-metadata.protomaps.dev/builds.json | python3 -c "import json,sys; print(json.load(sys.stdin)[-1]['key'])")
.tools/pmtiles extract "https://build.protomaps.com/${BUILD}" "$OUT" --bbox="$BBOX" --maxzoom=14
ls -lh "$OUT"
