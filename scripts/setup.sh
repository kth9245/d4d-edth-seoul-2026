#!/usr/bin/env bash
# One-time setup. Usage: scripts/setup.sh <module> [--worktree <module2>]
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
mod="${1:?사용법: scripts/setup.sh <모듈> [--worktree <모듈2>]}"
if [ ! -d "modules/$mod" ] && [ "$mod" != "infra" ] && [ "$mod" != "contracts" ]; then
  echo "[setup] modules/$mod 가 아직 없습니다. 브랜치 $mod/work 를 만든 뒤 새 모듈을 만드세요:"
  echo "        uv run python scripts/new_module.py $mod <PREFIX>   (예: edge EDG)"
fi
if [ $# -gt 3 ] || { [ $# -gt 1 ] && [ "${2:-}" != "--worktree" ]; }; then
  echo "사용법: scripts/setup.sh <모듈> [--worktree <모듈2>]"; exit 1
fi

git config core.hooksPath .githooks
chmod +x scripts/*.sh .githooks/*
git fetch -q origin
if git show-ref --quiet "refs/heads/$mod/work"; then git switch -q "$mod/work"
else git switch -q -c "$mod/work" origin/main; fi

uv sync
(cd modules/cop-ui && npm ci --silent) || echo "[setup] 경고: npm ci 실패 — UI 작업 전에 'cd modules/cop-ui && npm ci' 재실행"

if [ "${2:-}" = "--worktree" ]; then
  wt="${3:?--worktree 다음에 모듈 이름}"
  dir="../$(basename "$PWD")-$wt"
  if [ -d "$dir" ]; then
    echo "worktree 이미 있음: $dir (건너뜀)"
  else
    if git show-ref --quiet "refs/heads/$wt/work"; then git worktree add -q "$dir" "$wt/work"
    else git worktree add -q -b "$wt/work" "$dir" origin/main; fi
    echo "worktree: $dir (브랜치 $wt/work)"
  fi
  ln -sfn "$PWD/.venv" "$dir/.venv"
fi

.venv/bin/python scripts/sync_docs.py
scripts/fetch_tiles.sh || echo "[setup] 지도 타일 받기 실패 — 나중에 scripts/fetch_tiles.sh 재실행"
echo "[setup] 완료. 현재 브랜치: $(git branch --show-current)"
