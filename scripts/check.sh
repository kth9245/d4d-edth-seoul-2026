#!/usr/bin/env bash
# Commit check (target < 2s). Usage: scripts/check.sh [--all]
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=".venv/bin/python"; [ -x "$PY" ] || PY="python3"

staged_py=$(git diff --cached --name-only --diff-filter=ACM -- '*.py' | grep -v '^knowledge/spikes/' || true)
if [ -n "$staged_py" ]; then
  .venv/bin/ruff check --fix --quiet $staged_py
  .venv/bin/ruff format --quiet $staged_py
  git add $staged_py
fi

"$PY" tools/check_imports.py
"$PY" tools/check_specs.py

if git diff --cached --name-only | grep -q '^contracts/models.py$'; then
  "$PY" scripts/gen_contracts.py
  git add contracts/schema modules/cop-ui/src/contracts.gen.ts 2>/dev/null || true
fi

"$PY" scripts/sync_docs.py --stage || echo "[check] sync_docs 경고: 문서 목차 갱신 실패 (커밋은 계속)"

if [ "${1:-}" = "--all" ]; then
  .venv/bin/pytest
fi
