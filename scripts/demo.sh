#!/usr/bin/env bash
# Demo run (offline): build UI, serve UI + /ws from one process on :8000.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
(cd modules/cop-ui && npm run build --silent)
[ -s modules/cop-ui/public/tiles/seoul.pmtiles ] || echo "[demo] 경고: 지도 타일 없음 (배경 없이 표적만 표시)"
export KDTH_SCENARIO="${1:-demo/scenarios/seoul_mixed.yaml}"
export KDTH_UI_DIST="$PWD/modules/cop-ui/dist"
echo "http://localhost:8000"
exec .venv/bin/uvicorn modules.gateway.app:app --port 8000
