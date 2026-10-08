#!/usr/bin/env bash
# Cache Baengnyeong satellite raster tiles once (decision 0001/0004). The map then serves them as local files.
# Source: EOX Sentinel-2 cloudless (CC BY-NC-SA 4.0, attribution required) — https://s2maps.eu
# Usage: scripts/fetch_tiles_baengnyeong.sh [maxzoom=14]   (env OUT, BBOX override; PAR = parallel downloads)
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
OUT=${OUT:-modules/cop-ui/public/tiles/baengnyeong}
BBOX=${BBOX:-"124.55,37.88,124.85,38.02"}   # W,S,E,N
MINZ=${MINZ:-8}; MAXZ=${1:-14}; PAR=${PAR:-8}
URL='https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/g/{z}/{y}/{x}.jpg'
mkdir -p "$OUT"
list=$(python3 - "$BBOX" "$MINZ" "$MAXZ" <<'PY'
import math, sys
W, S, E, N = map(float, sys.argv[1].split(",")); z0, z1 = int(sys.argv[2]), int(sys.argv[3])
def tx(lon, z): return int((lon + 180) / 360 * 2**z)
def ty(lat, z):
    r = math.radians(lat); return int((1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2**z)
for z in range(z0, z1 + 1):
    for x in range(tx(W, z), tx(E, z) + 1):
        for y in range(ty(N, z), ty(S, z) + 1):
            print(z, x, y)
PY
)
total=$(echo "$list" | wc -l); echo "[tiles] $total tiles z$MINZ-$MAXZ -> $OUT"
echo "$list" | xargs -P "$PAR" -n 3 sh -c '
  z=$0; x=$1; y=$2; f="'"$OUT"'/$z/$x/$y.jpg"
  [ -s "$f" ] && exit 0
  mkdir -p "$(dirname "$f")"
  u=$(echo "'"$URL"'" | sed "s/{z}/$z/;s/{x}/$x/;s/{y}/$y/")
  curl -fsS --retry 3 -o "$f.tmp" "$u" && mv "$f.tmp" "$f" || { rm -f "$f.tmp"; echo "[tiles] FAIL $z/$x/$y" >&2; }'
have=$(find "$OUT" -name '*.jpg' | wc -l); du -sh "$OUT" | awk '{print "[tiles] size " $1}'
echo "[tiles] have $have / $total"
printf '© EOX IT Services GmbH — Sentinel-2 cloudless 2020 (CC BY-NC-SA 4.0), contains modified Copernicus Sentinel data\n' > "$OUT/ATTRIBUTION.txt"
[ "$have" -eq "$total" ] || { echo "[tiles] some tiles missing; rerun to resume" >&2; exit 1; }
