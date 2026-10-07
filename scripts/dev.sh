#!/usr/bin/env bash
# Dev run: gateway (8000, reload) + vite (5173). Ctrl+C stops both.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
trap 'kill 0' EXIT
.venv/bin/uvicorn modules.gateway.app:app --port 8000 --reload --reload-dir modules --reload-dir contracts &
(cd modules/cop-ui && npm run dev -- --port 5173) &
echo "http://localhost:5173"
wait -n || true
echo "[dev] 프로세스 하나가 종료되어 전체를 중지합니다 (포트 8000/5173 사용 중인지 확인)."
exit 1
