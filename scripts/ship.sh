#!/usr/bin/env bash
# Rebase on origin/main, test changed modules, smoke test, push to main (target < 20s).
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=".venv/bin/python"; PYTEST=".venv/bin/pytest"
fail() { echo "[ship] $*"; exit 1; }

git diff --quiet && git diff --cached --quiet || fail "커밋 안 된 변경이 있습니다. 먼저 커밋하세요."
git fetch -q origin || fail "fetch 실패 (네트워크 확인)"
git rebase -q origin/main || fail "rebase 충돌. 'git status'로 충돌 파일을 확인하고 해결 후 'git rebase --continue', 그다음 다시 ship. 남의 파일이면 담당자에게 문의."

changed=$(git diff --name-only origin/main...HEAD)
if echo "$changed" | grep -qE '^(contracts|shared)/'; then
  targets="tests modules"
else
  targets=$(echo "$changed" | awk -F/ '$1=="modules"{print $2}' | sort -u \
    | while read -r m; do [ -f "modules/$m/__init__.py" ] && echo "modules/$m"; done | tr '\n' ' ')
fi
if [ -n "${targets// /}" ]; then
  out=$("$PYTEST" -q -x $targets 2>&1) || { echo "$out" | tail -25; fail "테스트 실패"; }
fi
out=$("$PY" scripts/smoke.py 2>&1) || { echo "$out"; fail "데모 smoke test 실패"; }
"$PY" scripts/sync_docs.py >/dev/null 2>&1 || true
git push -q origin HEAD:main || fail "push 실패. 누군가 먼저 push했을 수 있습니다. 다시 ship 하세요."
echo "[ship] 완료: $(git log --oneline -1)"
