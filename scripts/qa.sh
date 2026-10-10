#!/usr/bin/env bash
# Screen QA: headless Chrome clicks through the editor, the live screen (real engine) and the example scenes,
# and checks each step (scripts/qa/*.json). Needs scripts/dev.sh running (gateway 8000, UI 5173).
#   scripts/qa.sh                      all checklists
#   scripts/qa.sh scripts/qa/live.json one checklist
# Changes the dev server's state: resets the run and saves two plays in its memory (gone when it restarts).
# Output: logs/qa/qa.log and screenshots in logs/qa/. Exit 1 when any step fails.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
PORT="${QA_PORT:-9339}"
export QA_PORT="$PORT" QA_OUT="${QA_OUT:-logs/qa}"
mkdir -p "$QA_OUT"

curl -sf -o /dev/null http://localhost:8000/operation || { echo "[qa] gateway(8000)가 꺼져 있습니다. scripts/dev.sh 먼저."; exit 1; }
curl -sf -o /dev/null http://localhost:5173/ || { echo "[qa] UI(5173)가 꺼져 있습니다. scripts/dev.sh 먼저."; exit 1; }

if ! curl -sf -o /dev/null "http://127.0.0.1:$PORT/json/version"; then
  chrome=$(command -v google-chrome || command -v chromium || command -v chromium-browser) \
    || { echo "[qa] Chrome이 없습니다 (google-chrome 또는 chromium 설치)."; exit 1; }
  profile=$(mktemp -d)
  # swiftshader gives MapLibre WebGL without a GPU.
  "$chrome" --headless=new --no-sandbox --user-data-dir="$profile" --use-angle=swiftshader --enable-unsafe-swiftshader \
    --window-size=1600,900 --remote-debugging-port="$PORT" about:blank >/dev/null 2>&1 &
  chrome_pid=$!
  trap 'kill "$chrome_pid" 2>/dev/null; rm -rf "$profile"' EXIT
  for _ in $(seq 50); do curl -sf -o /dev/null "http://127.0.0.1:$PORT/json/version" && break; sleep 0.2; done
fi

if [ "$#" -gt 0 ]; then lists=("$@"); else lists=(scripts/qa/editor.json scripts/qa/draft_to_live.json scripts/qa/live.json scripts/qa/scenes.json); fi
node scripts/qa/run.mjs "${lists[@]}" 2>&1 | tee "$QA_OUT/qa.log"
rc=${PIPESTATUS[0]}
[ "$rc" = 0 ] && echo "[qa] 전부 통과. 스크린샷: $QA_OUT/" || echo "[qa] 실패 있음. FAIL 줄과 $QA_OUT/qa.log 확인."
exit "$rc"
