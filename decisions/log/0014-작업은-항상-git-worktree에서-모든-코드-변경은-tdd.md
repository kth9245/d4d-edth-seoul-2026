---
id: 0014
title: 작업은 항상 git worktree에서, 모든 코드 변경은 TDD
status: 확정
decided_by: kth9245
date: 2026-10-09
modules: [infra, gateway, sim, sensing, safety, runtime, play, cop-ui]
supersedes: null
---
## 결정
2026-10-09 사람이 말한 것을 그대로 적는다. AI가 "같은 폴더에서 다른 세션이 브랜치를 main으로 바꿨다(22:02:26), 그래서 별도 worktree에서 작업한다"고 알린 뒤의 대화.

사람: "아 항상 워크트리파서 작업하고 TDD 방식으로 작업하는걸로 agent.md에 박으셈"

(AI 해석)
1. 모든 세션은 자기 git worktree에서 작업한다. 메인 폴더(저장소를 처음 받은 폴더)에서는 파일을 고치지 않는다.
2. Claude Code는 작업을 시작할 때 `EnterWorktree`(이름 = 작업 번호 등)를 쓴다. `.claude/worktrees/<이름>`에 origin/main에서 새 브랜치를 만들고 세션의 작업 폴더를 옮긴다. 세션 폴더가 옮겨져야 guard(`tools/guard/check_edit.py`, 세션 cwd의 git 최상위를 root로 씀)가 그 worktree의 편집을 검사한다. 세션은 메인 폴더에 둔 채 다른 폴더에 `git worktree add`만 하고 그 파일을 고치면 guard가 검사하지 않는다.
3. 새 worktree에는 `.venv`가 없으므로 메인 폴더의 것을 링크한다(`package = false`, `pythonpath = ["."]`라 import는 worktree의 코드를 쓴다. `test_ship.make_clone`과 같은 방식). UI 작업이면 `modules/cop-ui/node_modules`도 링크.
4. ship은 worktree 안에서 `scripts/ship.sh` 그대로(어느 브랜치든 rebase 뒤 HEAD를 main에 push).
5. TDD: 모든 코드 변경은 실패하는 테스트를 먼저 쓰고, 실패를 확인하고, 구현해 통과시킨다(superpowers:test-driven-development). 액션은 `new_action.py`가 만든 실패 테스트를 진짜 테스트로 바꾸는 것부터. 문서·데이터 파일만 바꾸는 변경은 테스트할 동작이 없으므로 예외로 본다(AI 해석).

## 이유
- 같은 폴더를 두 세션이 쓰면 브랜치·index·작업 폴더를 공유해 한 세션의 checkout이 다른 세션의 작업을 바꾼다(2026-10-09 22:02:26 실제 발생: 커밋 18초 뒤 폴더 브랜치가 main으로 바뀜).
- TDD는 AGENTS.md에 액션 한정("테스트 먼저")으로만 있었다. 사람이 모든 작업으로 넓혔다.

## 버린 대안
- `scripts/setup.sh <모듈> --worktree <모듈2>`: 모듈당 한 번 쓰는 설치 스크립트라 메인 폴더 브랜치를 바꾸고 uv sync·npm ci·타일 받기까지 돌린다. 세션마다 쓰기엔 무겁다.
- 메인 폴더 옆에 `git worktree add`만 하고 세션은 메인 폴더에 두기: guard가 그 파일들을 검사하지 않는다(2번).

## 영향
- AGENTS.md: `## 반영` 첫 줄에 worktree 규칙, `## 액션 규칙`의 "테스트 먼저" 줄을 TDD 규칙으로.
- `.gitignore`에 `.claude/worktrees/`(메인 폴더 `git status`에 worktree가 안 보이게).
- 강제는 아직 없음(규칙만). guard가 메인 폴더 편집을 막게 하려면 별도 작업.
