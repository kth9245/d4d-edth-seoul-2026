# d4d-edth-seoul-2026 — 에이전트 공통 규칙

KDTH 2026 해커톤 팀 저장소. 24시간 안에 **로컬에서 작동하는 데모**(ROLECALL, 백령도 야간 작전)를 만든다. 문제: `docs/problem.md`.

## 먼저 읽을 것
1. `decisions/INDEX.md` — 사람이 확정한 결정. 반드시 따른다. 다르게 해야 한다고 판단되면 멈추고 사람에게 묻는다.
2. `docs/research/09-rolecall-implementation-foundation.md` — 설계(2절 데이터 형식, 3절 모듈, 4절 통합 기준)와 **6절 사람별 할 일**. 6절 머리의 "통합 1 배정" 표에서 자기 줄을 찾는다.
3. 작업할 모듈의 `modules/<m>/AGENTS.md`와 `SPEC.md`. `knowledge/INDEX.md`는 조사가 필요할 때만.

우선순위: 확정 결정·정책 > SPEC.md > 09 문서 > 지식 카드 > 너의 판단.

## 정책 (decisions/POLICY.md 자동 복사본 — 여기서 수정하지 말 것)
<!-- POLICY:BEGIN -->
1. 시연은 인터넷 없이 동작한다. 지도 타일은 로컬 파일을 쓰고, 시연 경로에서 외부 API를 호출하지 않는다.
2. 공개 데이터·가상(synthetic) 데이터만 쓴다. 비밀·수출통제 정보, 실제 개인 식별·표적화 금지.
3. 좌표는 WGS84 위경도(도), 고도는 m, 시간은 UTC epoch 밀리초(`t_ms`).
4. API 키·비밀값은 커밋하지 않는다(`.env`는 gitignore).
5. 해커톤 중 새로 만든 부분은 `demo/BUILT_HERE.md`에 기록한다.
<!-- POLICY:END -->

## 담당 (결정 0007·0009)
| 모듈 | 담당 |
|---|---|
| contracts, gateway REST/WS, cop-ui 전부, demo, infra(scripts·tools·shared·docs) | 리드 kth9245 |
| sim, sensing, gateway `engine.py` 틱 루프 | 최동호 (파트 2A) |
| safety, runtime, play | 황승주 (파트 2B) |
| tracking, assess, respond | 휴면. 손대지 않음 |

남의 영역을 고치면 담당자에게 알린다.

## 할 일 기록 (결정 0013) — `uv run python scripts/task.py`, 자세히는 task 스킬
- 처음 한 번 `git config user.name <한글 이름>`(리드는 kth9245). 팀 명단 밖 이름은 기록이 거부된다.
- 작업 전 `task.py show`. 번호표 항목을 시작하면 `task.py start <번호>`(액션은 new_action.py가 대신). 남이 진행중이면 `task.py add <번호> "<제목>"`으로 하위 항목을 만들어 그것을 start.
- ship 성공 뒤 `task.py done <번호>`. 막히면 5분 안에 `task.py block <번호> "<증상>"`, 채팅에도 번호.
- 작업 중 결정: 내 항목 안에서 끝나는 선택은 `task.py decide <번호> "<결정>"`, 계약·남의 모듈·정책을 바꾸면 `/decide`.
- 현황 기준은 `task.py show`·`tasks/NOW.md`(SPEC 상태 칸은 액션 파일 관리용). `tasks/log.jsonl`·`NOW.md`는 task.py만 쓴다.

## 액션 규칙 (1 액션 = 1 파일 = 1 테스트)
- 액션 파일: 공개 함수 1개, 이름 = 파일 이름, 80줄 이하. 다른 .py/.ts/.tsx는 200줄 이하. `pipeline.py`·`engine.py`는 호출 순서만.
- 시작: `uv run python scripts/new_action.py <m> <verb_noun> "<설명>"`. SPEC.md에 `예정` 행이 있으면 같은 명령이 그 행을 가져간다(담당 = 내 git 이름, 파일·실패 테스트 생성). 남이 `진행중`인 행은 `--take`. SPEC.md에 없는 액션 파일은 guard가 막는다.
- TDD(결정 0014): 모든 코드 변경은 실패하는 테스트를 먼저 쓰고, 실패를 확인하고, 구현해 통과시킨다. 액션은 생성된 실패 테스트를 진짜 테스트로 바꾸는 것부터. 문서·데이터만 바꾸면 예외.
- 다른 모듈은 `from modules.<m> import <공개 API>`로만. `modules.<m>.actions...` import 금지.
- 통합 1(10/10 18:00) 전에는 sim·gateway 레거시 공개 API(`load_scenario`·`simulate`·`Engine`)를 바꾸지 않는다(smoke가 깨져 전원 ship 불가). 새 동작은 새 이름으로 추가.
- 로깅(결정 0010): 실행 경계(gateway app, 틱 루프, REST, 스크립트)는 `from shared.log import setup_logging, get_logger`로 stderr와 `logs/<이름>.log`에 남긴다. 순수 함수 액션 안에는 넣지 않는다.
- 새 모듈이 필요하면 `uv run python scripts/new_module.py <이름> <PREFIX>`.

## 반영 (결정 0010)
- 작업은 항상 자기 git worktree에서(결정 0014). 메인 폴더에서는 파일을 고치지 않는다. Claude Code는 시작할 때 `EnterWorktree`(이름 = 작업 번호). 그 뒤 `git rev-parse --path-format=absolute --git-common-dir`가 출력한 경로의 상위 폴더(메인 폴더)를 M이라 하고 `ln -s M/.venv .venv`(UI면 `ln -s M/modules/cop-ui/node_modules modules/cop-ui/node_modules`도). 명령은 `$(...)` 없이 따로 실행한다(worktree 세션이 겹친 git 명령을 거부함). ship은 worktree에서 그대로.
- 액션 하나가 끝날 때마다 `scripts/ship.sh`: origin/main에 rebase → 바뀐 모듈 테스트 → smoke → main에 push. 원격 브랜치·PR 없음.
- 실패 테스트가 있는 액션은 ship하지 않는다(같은 모듈 전원의 ship이 막힌다). 남의 실패 테스트를 skip으로 바꾸지 않는다.
- 작업 중인 액션은 가져갈 수 없다(그 사람 노트북에만 있다). 가져가는 사람은 `예정` 행이나 스파이크에서 다시 시작한다.
- rebase 충돌: SPEC.md 한 줄이면 두 줄 다 살리고 `git rebase --continue`. 같은 id가 두 번 생기면 한쪽 번호를 올린다. `uv.lock`은 `uv lock` 뒤 add.

## 명령
- 설치: `scripts/setup.sh <모듈>` · 개발: `scripts/dev.sh` · 시연: `scripts/demo.sh` · 테스트: `uv run pytest modules/<m>` · 의존성: `uv add <패키지>`
- 결정: 사람이 결정을 말하면 `/decide`로 적고, 사람이 답한 것은 같은 턴에 `uv run python scripts/decide.py accept NNNN --by <이름>`(승인 창이 뜬다). AI는 `확정`을 직접 쓰지 못한다. 조사 결과는 `/kb-save`.
- 스킬: 개발·디버깅은 superpowers(brainstorming → test-driven-development → systematic-debugging → verification-before-completion), 되돌리기 비싼 결정 전에는 `/devil-advocate:devil-advocate`. 없으면 `/plugin install superpowers@claude-plugins-official`, `/plugin marketplace add hadicancatak-coder/devils-advocate` 뒤 `/plugin install devil-advocate@devil-advocate`.

## 하지 말 것
- CLAUDE.md 생성. 자동 생성 파일 수정(`tasks/BOARD.md`, `knowledge/INDEX.md`, `decisions/INDEX.md`, `contracts/schema/`, `contracts.gen.ts`). `decisions/POLICY.md` 수정.
- 비공개·수출통제 데이터, 실제 개인 식별 정보.

## 시간이 급할 때
- `git commit --no-verify` 허용(ship의 smoke는 유지). 일요일 06:00 이후 `KDTH_FREEZE=1`: 구조 검사는 경고만, smoke만 차단.
