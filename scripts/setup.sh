#!/usr/bin/env bash
# One-time setup. Usage: scripts/setup.sh <module> [--worktree <module2>]
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
mod="${1:?사용법: scripts/setup.sh <모듈> [--worktree <모듈2>]}"
[ -d "modules/$mod" ] || [ "$mod" = "infra" ] || [ "$mod" = "contracts" ] || { echo "모듈 없음: $mod"; exit 1; }

uv sync
(cd modules/cop-ui && npm ci --silent)
git config core.hooksPath .githooks
chmod +x scripts/*.sh .githooks/*
git fetch -q origin
if git show-ref --quiet "refs/heads/$mod/work"; then git switch -q "$mod/work"
else git switch -q -c "$mod/work" origin/main; fi

if [ "${2:-}" = "--worktree" ]; then
  wt="${3:?--worktree 다음에 모듈 이름}"
  dir="../$(basename "$PWD")-$wt"
  git worktree add -q -b "$wt/work" "$dir" origin/main
  ln -s "$PWD/.venv" "$dir/.venv"
  echo "worktree: $dir (브랜치 $wt/work)"
fi

.venv/bin/python scripts/sync_docs.py
scripts/fetch_tiles.sh || echo "[setup] 지도 타일 받기 실패 — 나중에 scripts/fetch_tiles.sh 재실행"
echo "[setup] 완료. 현재 브랜치: $(git branch --show-current)"
