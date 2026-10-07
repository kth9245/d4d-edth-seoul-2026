#!/usr/bin/env bash
# Commit check (target < 2s). Usage: scripts/check.sh [--all]
# Default: only staged files / the modules they touch. --all: whole repo + full pytest.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=".venv/bin/python"; [ -x "$PY" ] || PY="python3"
all=0; [ "${1:-}" = "--all" ] && all=1

secret_re='AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----'
if git diff --cached -U0 --diff-filter=ACM | grep -E '^\+[^+]' | grep -qE "$secret_re"; then
  echo "[check] 커밋 차단: 비밀값(API 키·개인 키)으로 보이는 줄이 추가됐습니다. 제거하고 .env를 쓰세요." >&2
  exit 1
fi

staged=$(git diff --cached --name-only --diff-filter=ACM || true)
staged_py=$(echo "$staged" | grep '\.py$' | grep -v '^knowledge/spikes/' || true)
if [ -n "$staged_py" ]; then
  .venv/bin/ruff check --fix --quiet $staged_py
  .venv/bin/ruff format --quiet $staged_py
  git add $staged_py
fi

if [ "$all" = 1 ]; then
  "$PY" tools/check_imports.py
  "$PY" tools/check_specs.py
elif [ -n "$staged" ]; then
  echo "$staged" | xargs "$PY" tools/check_imports.py
  echo "$staged" | xargs "$PY" tools/check_specs.py
fi

if git diff --cached --name-only | grep -q '^contracts/models.py$'; then
  "$PY" scripts/gen_contracts.py
  git add contracts/schema modules/cop-ui/src/contracts.gen.ts 2>/dev/null || true
fi

"$PY" scripts/sync_docs.py --stage || echo "[check] sync_docs 경고: 문서 목차 갱신 실패 (커밋은 계속)"

if [ "$all" = 1 ]; then
  .venv/bin/pytest
fi
