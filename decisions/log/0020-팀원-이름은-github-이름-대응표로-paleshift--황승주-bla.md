---
id: 0020
title: 팀원 이름은 GitHub 이름 대응표로: Paleshift = 황승주, Blackchoi0624 = 최동호, 이름 설정은 바꾸지 않음
status: 확정
decided_by: kth9245
date: 2026-10-09
modules: [infra, tools]
supersedes: 0013
---
## 결정
(번호 변경: 처음 0019로 만들었으나 다른 세션의 결정 0019(배정된 항목은 묻기)가 먼저 main에 올라가 0020으로 바꿈. 사람 승인 2026-10-09.)
2026-10-09 23시 반, AI가 팀원에게 보낼 메시지 초안에 "git config user.name <한글 이름>"을 넣자 사람이 말한 것을 그대로 적는다.

사람: "2) git config user.name <한글 이름>  (할 일 기록이 명단 밖 이름을 거부함) 이거는 하지마셈 그리고 Paleshift 이게 황승주, Blackchoi0624 이게 최동호"

(AI 해석)
1. 팀원에게 git user.name을 바꾸게 하지 않는다. 결정 0013의 6번("이름은 각자 `git config user.name <한글 이름>`")만 이 결정으로 바뀐다. 0013의 나머지는 그대로다.
2. `tools/tasks.py`의 `GIT_NAMES`가 git user.name(대소문자 무시)을 팀원 이름으로 바꾼다: `Paleshift` → 황승주, `Blackchoi0624` → 최동호. 리드는 `kth9245` 그대로다.
3. 이 대응은 할 일 기록(`scripts/task.py`, `tools/ledger.py`)과 액션 생성(`scripts/new_action.py`의 SPEC 담당 칸) 두 곳에 쓰인다. 그래서 기록과 SPEC 담당 칸에는 계속 한글 이름이 적힌다.
4. 명단 밖 이름은 지금처럼 기록이 거부되고, 안내 문구는 "리드에게 GIT_NAMES 추가 요청"이다.

## 이유
- 팀원의 git 설정을 바꾸게 하는 것은 대회 시작 때 불필요한 일이고, 다른 저장소 커밋 이름까지 바뀔 수 있다.
- SPEC.md 예정 행의 담당 칸이 이미 한글 이름이라, 대응표가 있어야 `new_action.py`가 그 행을 같은 사람의 것으로 가져간다.

## 버린 대안
- 명단(TEAM)을 GitHub 이름으로 바꿈: SPEC 담당 칸, 할 일 기록 48개 항목의 배정, 09 문서가 모두 한글 이름이라 함께 바꿔야 한다.

## 영향
- `tools/tasks.py`(`GIT_NAMES`, `person_of`), `tools/ledger.py`, `scripts/new_action.py`, AGENTS.md 할 일 기록 절, `docs/superpowers/specs/2026-10-09-task-ledger-design.md`, 테스트 `tests/test_team.py`·`tests/test_task_cli.py`.
