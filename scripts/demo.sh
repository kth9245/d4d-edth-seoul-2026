#!/usr/bin/env bash
# Demo run (offline): build UI, serve UI + /ws from one process on :8000.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
if ! (cd modules/cop-ui && npm run build --silent); then
  if [ -f modules/cop-ui/dist/index.html ]; then
    echo "[demo] 경고: UI 빌드 실패 — 이전에 빌드된 dist를 그대로 서빙합니다 (최신 UI 변경은 반영 안 됨)."
  else
    echo "[demo] UI 빌드 실패이고 이전 dist도 없습니다. 'cd modules/cop-ui && npm ci && npm run build' 확인."; exit 1
  fi
fi
if [ ! -s modules/cop-ui/public/tiles/seoul.pmtiles ]; then
  echo "################################################################"
  echo "# [demo] 경고: 지도 타일(seoul.pmtiles)이 없습니다!"
  echo "#   지도 배경 없이 표적만 표시됩니다. 인터넷 되는 곳에서:"
  echo "#   scripts/fetch_tiles.sh   (또는 git pull 로 저장소의 파일 받기)"
  echo "################################################################"
fi
export KDTH_SCENARIO="${1:-demo/scenarios/seoul_mixed.yaml}"
export KDTH_UI_DIST="$PWD/modules/cop-ui/dist"
echo "http://localhost:8000"
exec .venv/bin/uvicorn modules.gateway.app:app --port 8000
