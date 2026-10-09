#!/usr/bin/env bash
# Rebase on origin/main, test changed modules, smoke test, push to main (target < 20s).
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=".venv/bin/python"; PYTEST=".venv/bin/pytest"
fail() { echo "[ship] $*"; exit 1; }
# Under KDTH_FREEZE=1 test failures only warn; the smoke test still blocks.
soft_fail() {
  if [ "${KDTH_FREEZE:-}" = "1" ]; then echo "[ship] 경고(FREEZE): $*"; else fail "$*"; fi
}

for d in rebase-merge rebase-apply; do
  [ -e "$(git rev-parse --git-path $d)" ] && fail "rebase 진행 중입니다. 충돌 해결 후 git rebase --continue 하고 다시 ship."
done
git diff --quiet && git diff --cached --quiet || fail "커밋 안 된 변경이 있습니다. 먼저 커밋하세요."
git fetch -q origin || fail "fetch 실패 (네트워크 확인)"
git rebase -q origin/main || fail "rebase 충돌. 'git status'로 충돌 파일을 확인하고 해결 후 'git rebase --continue', 그다음 다시 ship. 남의 파일이면 담당자에게 문의."

changed=$(git diff --name-only origin/main...HEAD)
if echo "$changed" | grep -qE '^(tests|tools|scripts|contracts|shared)/'; then
  targets="tests modules"
else
  targets=$(echo "$changed" | awk -F/ '$1=="modules"{print $2}' | sort -u \
    | while read -r m; do [ -f "modules/$m/__init__.py" ] && echo "modules/$m"; done | tr '\n' ' ')
fi
if [ -n "${targets// /}" ]; then
  out=$("$PYTEST" -q -x --ignore=tests/test_ship.py $targets 2>&1); rc=$?
  if [ "$rc" = 5 ]; then echo "[ship] 경고: $targets 에 테스트가 없습니다 (SPEC 행만 바뀐 새 모듈)";
  elif [ "$rc" != 0 ]; then echo "$out" | tail -25; soft_fail "테스트 실패"; fi
fi
if echo "$changed" | grep -q '^modules/cop-ui/'; then
  if [ -d modules/cop-ui/node_modules ]; then
    out=$(cd modules/cop-ui && npm test --silent 2>&1) || { echo "$out" | tail -25; soft_fail "cop-ui 테스트 실패"; }
  else
    echo "[ship] 경고: modules/cop-ui/node_modules 없음 - UI 테스트 건너뜀 (scripts/setup.sh 실행)"
  fi
fi
out=$("$PY" scripts/smoke.py 2>&1) || { echo "$out"; fail "데모 smoke test 실패"; }
# A task.py record (tasks/ only, decision 0013) may land while tests run: rebase over it and retry.
# Retry only when origin moved; otherwise show git's own reason (e.g. a rejected large file).
pushed=0
for _ in 1 2 3; do
  if err=$(git push -q origin HEAD:main 2>&1); then pushed=1; break; fi
  git fetch -q origin || { err="$err"$'\n'"(fetch도 실패: 네트워크 확인)"; break; }
  git merge-base --is-ancestor origin/main HEAD && break
  [ -n "$(git diff --name-only HEAD...origin/main | grep -v '^tasks/')" ] && break
  git rebase -q origin/main || fail "rebase 충돌(기록 커밋 위). 'git status' 확인 후 다시 ship."
done
[ "$pushed" = 1 ] || { echo "$err"; fail "push 실패. 위 git 메시지를 확인하세요. 누군가 먼저 push했다면 다시 ship 하세요."; }
git fetch -q origin main:main 2>/dev/null || true  # keep local main in sync (no-op when main is checked out)
echo "[ship] 완료: $(git log --oneline -1)"
