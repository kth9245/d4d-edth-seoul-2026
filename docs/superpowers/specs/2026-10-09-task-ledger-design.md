# 할 일 기록 도구(task ledger) 설계

2026-10-09 KST · 결정 0012(KST), 0013(이 설계) · 담당 리드(infra)

## 1. 목적

09 문서 6절 번호표(Part1-1 ~ Part3-15)의 항목마다 시작·완료를 기록하고, 항목을 하위 항목으로 더 나누고, 작업 중 나온 결정을 그 항목에 붙인다. 사람이 고른 용도(결정 0013):

1. 리드가 진행 상황을 한 장으로 본다.
2. 실시간 중복 방지: 남이 시작한 항목은 명령이 거부한다.
3. 남의 일을 쉽게 돕는다: 하위 항목을 만들어 그것만 시작한다.
4. 지금 진행 중인 것을 빠르게 본다.

현재 빈 곳: SPEC `진행중`은 ship 때만 main에 올라가고(실시간 아님), `완료`는 아무 스크립트도 쓰지 않으며, 액션이 아닌 항목(Part1-7·1-9·2-17·2-19·3-10~14 등)은 적을 곳이 없다. 작은 결정은 커밋 메시지에 흩어진다.

## 2. 데이터

### 2.1 `tasks/log.jsonl` (정본)

한 줄 = 기록 하나. 덧붙이기만 한다. 키 순서는 아래대로, `ensure_ascii=False`.

| op | 필드(공통 `at`, `by`, `op`, `id` 뒤에) |
|---|---|
| `add` | `title`, `parent`(상위 id 또는 null), `assign`(배정 이름 또는 null = 누구나), `slot`(`"1"`·`"2"`·`"밤"`·`"뒤"` 또는 null), `spec`(SPEC id 또는 null) |
| `start` | `take`(bool), `from`(넘겨받은 이전 담당 또는 null) |
| `done` | `take`(bool) |
| `block` · `decide` · `note` · `drop` | `text` |

- `at`: KST ISO 8601 초 단위, 예 `2026-10-10T12:03:15+09:00`. 고정 오프셋 `timezone(timedelta(hours=9))`로 만든다(한국은 서머타임 없음, 기계 시간대와 무관 — 결정 0012).
- `by`: `git config user.name`. 팀 명단 `TEAM = ("kth9245", "황승주", "최동호")`에 없으면 모든 쓰기 명령을 거부하고 `git config user.name <한글 이름>`을 안내한다.

### 2.2 다시 읽어 얻는 상태(항목마다)

`id, title, parent, assign, owner(지금 하는 사람), status, slot, spec, since(마지막 상태 변경 at), entries[(at, by, kind, text)]`. kind는 `note`·`decide`·`block`·`drop`.

상태 다섯: `예정`(add 직후) · `진행중` · `막힘` · `완료` · `뺌`.

### 2.3 번호

- 최상위: `Part<n>-<k>`. 하위: `<상위 id>.<N>`, 깊이 제한 없음(`Part2-17.1.2`도 가능).
- 입력 줄임: `2-17` → `Part2-17`, `2-17.1` → `Part2-17.1`.
- `add <상위> "제목"`: N = 그 상위의 기존 하위 중 최대 + 1. `add Part2 "제목"`: 새 최상위 `Part2-<기존 최대 k + 1>`.
- 번호는 push 직전 최신 main 상태로 계산한다(5절). 그래서 동시에 추가해도 겹치지 않는다.

### 2.4 `tasks/NOW.md` (읽기용, 같은 커밋에서 다시 만듦)

머리: 자동 생성 표시, 마지막 기록 시각(KST), "상세(입력·출력·완료 기준)는 docs/research/09 6절". 이어서 절 순서대로:

1. **진행중** — `- **Part2-17** 틱 루프 — 최동호, 10/10 12:03부터 · 하위 1/3 완료 · SIM-08` (한 사람이 진행중 2개 이상이면 절 끝에 "최동호 진행중 2개" 한 줄)
2. **막힘** — 위 형식 + 마지막 block 문장
3. **예정** — 배정별 소절(`kth9245`·`황승주`·`최동호`·`누구나`), 번호순
4. **최근 결정** — decide 기록 최신 10개: `- 10/10 13:20 황승주 · Part3-7 · watch_point/sea를 hold로`
5. **완료** — 최신순, 완료 시각과 사람
6. **뺌** — 이유

메모(note)는 NOW.md에 쓰지 않고 `show <번호>`로 본다.

### 2.5 처음 채우기(seed)

09 6절 표를 한 번 읽어 `add` 기록을 만든다. 줄 그은 Part1-6·1-8은 뺀다. 상위 없음, `slot`은 `통합` 열.

- 배정: Part1-* → kth9245. Part2-1~2-6, 2-17~2-20 → 최동호. Part2-7~2-16 → 황승주. Part3-1~3-9 → 황승주. Part3-10~3-14 → kth9245. Part3-15 → null(누구나, "통합 1 먼저 끝낸 사람").
- spec: 항목 열의 액션 이름으로 SPEC 행을 찾는다. Part2-1~2-5 → SIM-05~09, 2-6 → SNS-02, 2-7~2-9 → SFT-01~03, 2-10~2-16 → RT-01~07, 2-20 → SIM-04, 3-1~3-9 → PLY-01~09, 3-15 → PLY-10. Part2-18(build_frame 재작성)은 GW-01이 이미 `완료`라 null.
- 이미 끝난 것: Part1-3(2026-10-09 main) → `start` + `done` 기록. 나머지는 `예정`. 커밋 전에 리드가 목록을 확인한다.
- `task.py seed <파일>`: origin/main에 `tasks/log.jsonl`이 이미 있으면 거부. 파일의 줄을 그대로(at·by 포함) 한 커밋으로 올린다. 만드는 스크립트는 일회용이라 저장소에 넣지 않는다.

## 3. 명령 `uv run python scripts/task.py <명령>`

쓰기 명령은 성공하면 한 줄을 출력한다: `Part2-17 시작: 최동호 12:03 KST (main abc1234)`. 거부는 이유와 함께 exit 1, 아무것도 올리지 않는다.

| 명령 | 효과 | 거부 |
|---|---|---|
| `show [번호] [--all]` | 번호 없으면 진행중 · 막힘 · 내 예정(assign = 나) · 누구나 예정 개수 · 최근 결정 5개. 번호가 있으면 그 항목과 하위 항목, entries 전부. `--all`은 NOW.md 전체 | 없음 |
| `start <번호> [--take]` | status `진행중`, owner = 나. 예정 항목의 assign이 남이면 "배정: X — 채팅에 알리세요" 경고만(결정 0008: 누구든 시작 가능) | 없는 번호. owner가 남인 `진행중`·`막힘`(--take면 허용, `from` 기록). `완료`·`뺌`(--take면 다시 엶). 내가 이미 `진행중` |
| `done <번호> [--take]` | status `완료`, owner = 나(owner가 없었으면). `예정`에서 바로 done도 허용(작은 하위 항목). **ship 성공 뒤** 쓴다 | 없는 번호. 하위 중 `완료`·`뺌` 아닌 것이 있음(목록 출력). owner가 남(--take면 허용). 이미 `완료`·`뺌` |
| `add <상위> "제목" [--assign 이름]` | 하위(또는 새 최상위) 항목 `예정`. assign 기본 null(누구나) | 없는 상위. `--assign`이 TEAM 밖 |
| `block <번호> "막힌 것"` | status `막힘`, entries에 block. owner는 그대로 | owner가 내가 아니거나 status가 `진행중`·`막힘`이 아님 |
| `decide <번호> "결정 한 줄"` | entries에 decide | 없는 번호 |
| `note <번호> "메모"` | entries에 note | 없는 번호 |
| `drop <번호> "이유"` | status `뺌`, entries에 drop | 없는 번호. 이미 `완료` |

`막힘`에서 owner가 다시 `start`하면 `진행중`으로 돌아간다(내가 `막힘`인 항목의 start는 거부 대상 "이미 진행중"이 아니다).

## 4. 작업 중 결정을 어디에 적나

- 내 항목 안에서 끝나는 선택 → `task.py decide <번호> "..."`. 예: 펼치기 표 칸 하나, 내부 함수 나누기, 테스트 범위.
- 계약(contracts)·남의 모듈·정책을 바꾸는 것 → `/decide`(결정 문서 + 사람 확정). 그 결정 번호를 `task.py decide <번호> "결정 0014 참조"`로 항목에도 남긴다.

## 5. 즉시 push 경로 (`tools/gitpush.py`)

`push_tasks(root, op_fn, message, retries=5)`:

1. `git fetch -q origin main`. 실패하면 `OfflineError` → task.py가 "기록 못 올림: 네트워크"로 exit 1. 로컬에 아무것도 쓰지 않는다.
2. `git show origin/main:tasks/log.jsonl`(없으면 빈 문자열)을 읽어 `op_fn(old_log_text) -> (new_log_text, now_md)`를 부른다. op_fn 안에서 다시 읽기·검사·번호 계산·NOW.md 생성을 한다. 거부는 `Refused` 예외로 올라온다.
3. 임시 index 파일로(`GIT_INDEX_FILE=<tmp>`): `git read-tree origin/main` → `git hash-object -w --stdin` ×2 → `git update-index --add --cacheinfo 100644,<sha>,tasks/log.jsonl`(NOW.md도) → `git write-tree` → `git commit-tree <tree> -p <origin/main sha> -m "task: <op> <id> <by>"`.
4. 검사: `git diff-tree --no-commit-id --name-only -r <origin/main> <new>`가 `tasks/log.jsonl`·`tasks/NOW.md` 밖의 경로를 포함하면 `AssertionError`(push 안 함).
5. `git push -q origin <new>:refs/heads/main`. 거절되면 1로(최대 retries번). 다 실패하면 "push 재시도 실패" exit 1.
6. 작업 폴더, 현재 브랜치, 로컬 `main` ref, 실제 index는 건드리지 않는다. 원격 추적 ref는 push가 갱신한다.

`show`는 1에서 실패하면 마지막으로 받은 `origin/main`을 쓰고 "오프라인: N분 전 기준"(FETCH_HEAD 수정 시각)을 붙인다.

origin 원격이 없으면(`git remote get-url origin` 실패) `OfflineError`와 같은 취급.

## 6. 기존 도구 연결

1. **guard**: `tools/guard/edits.py` PROTECTED에 `tasks/log.jsonl`, `tasks/NOW.md`. 로컬 커밋이 두 파일을 건드리지 않으므로 rebase 충돌이 없다.
2. **ship.sh**: push가 거절되면 최대 3번: `git fetch -q origin` → `git diff --name-only HEAD...origin/main`(내가 없는 새 커밋들이 바꾼 파일)이 전부 `tasks/`면 `git rebase -q origin/main` 후 테스트 없이 다시 push. 하나라도 다른 경로면 지금처럼 "다시 ship 하세요"로 실패.
3. **new_action.py**: 기존 행을 가져갈 때(`예정`, 또는 `--take`) `replace_row` **전에** 원격 기록에서 `spec == row.id`인 항목을 찾아 같은 start(--take 그대로)를 부른다. `Refused`면 SPEC·파일을 바꾸지 않고 exit 1. `OfflineError`면 경고 한 줄 뒤 계속. 그런 항목이 없거나 새 행이면 "번호표에 없으면 task.py add" 안내만.
4. **AGENTS.md**: "## 할 일 기록 (결정 0013)" 절, 행동을 바꾸는 줄만:
   - 작업 시작 전 `task.py show`. 번호표 항목을 시작하면 `task.py start <번호>`(액션은 new_action.py가 대신). 남이 진행중이면 `add`로 하위 항목을 만들어 그것을 start.
   - ship 성공 뒤 `task.py done <번호>`.
   - 막히면 5분 안에 `task.py block <번호> "<증상>"` + 채팅에 번호(기존 "막힘:" 줄을 이것으로 바꿈).
   - 작업 중 결정은 4절 기준.
   - 현황의 기준은 `task.py show`·`tasks/NOW.md`. SPEC 상태 칸은 액션 파일 관리용. 두 파일 직접 수정 금지.
   - 처음 한 번 `git config user.name <한글 이름>`(리드는 kth9245).
5. **스킬**: `.claude/skills/task/SKILL.md`(설명: 번호표 항목 시작·완료·막힘·하위 항목·작업 중 결정 때 사용) 10줄 안팎. new-action 스킬 6단계 뒤에 "ship 뒤 `task.py done <번호>`".
6. **결정 0012 반영(같은 계획에 포함)**: `scripts/decide.py`의 날짜를 KST로(`datetime.now(KST).date()`), `shared/log.py` Formatter 시각을 KST로(converter 지정, `+0900` 표시). cop-ui 시각 표시는 화면 작업 때 리드.

## 7. 파일과 크기 (저장소 규칙: 액션 아닌 .py 200줄 이하)

| 파일 | 내용 |
|---|---|
| `tools/tasks.py` | 순수 함수: `now_kst()`, `normalize_id()`, `replay(lines) -> dict[id, Item]`, `apply(items, op, args, by) -> event`(검사 + `Refused`), `render_now(items, events) -> str`, `render_show(...)` |
| `tools/gitpush.py` | `push_tasks`, `read_remote_log`, `OfflineError` |
| `scripts/task.py` | argparse, `by` 확인, 명령 → apply → push_tasks, 출력 |
| `tests/test_tasks.py` | 순수 함수 테스트 |
| `tests/test_task_cli.py` | 원격 저장소·복제본 통합 테스트 |

## 8. 테스트

순수(`tests/test_tasks.py`): replay가 상태 다섯 가지를 만든다 · start 거부 규칙 전부(남의 진행중/막힘, 완료, 뺌, 이미 내 진행중) · --take가 from을 남긴다 · done이 열린 하위를 거부 · 하위 번호 N과 새 최상위 k · `2-17` 줄임 · `TZ=UTC` 환경에서도 at이 `+09:00` · render_now 절 순서와 "진행중 2개" 줄.

통합(`tests/test_task_cli.py`, `test_ship.make_clone` 방식, hooks 끔):
1. 커밋 안 된 파일이 있는 복제본에서 `start` → 원격 main에 기록 1줄, 작업 폴더 `git status`·HEAD 그대로.
2. 올라간 커밋이 바꾼 파일이 두 개뿐.
3. 두 번째 복제본(다른 user.name)에서 같은 항목 `start` → exit 1, `--take` → 성공·from 기록.
4. 원격 URL이 틀리면 exit 1, 원격에 변화 없음.
5. TEAM 밖 이름 → exit 1.
6. new_action: 연결된 항목이 남의 진행중이면 SPEC·파일 변화 없이 exit 1.
7. ship 재시도(`tests/test_ship.py`): 복제본의 `scripts/smoke.py`를 "tasks만 바꾼 커밋을 원격에 push하고 exit 0"으로 바꿔 ship 도중 끼어들기를 재현 → ship 성공, 원격에 두 커밋 다 있음.
8. 기존 `tests/` 전부 통과(특히 test_new_action·test_guard·test_ship).

## 9. 넣지 않은 것

- BUILT_HERE 자동 작성(`tasks/` 밖을 고치게 됨). Part1-15에서 NOW.md 완료 시각을 옮긴다.
- 상위 상태 자동 계산(하위 개수만 표시), 진행중 개수 제한(경고만), 알림(채팅이 맡음), SPEC 상태 칸·BOARD.md 변경.

## 10. 남은 위험

- main에 `task:` 커밋이 수백 개 쌓인다. `git log --invert-grep --grep='^task:'`.
- 오프라인이면 기록을 못 한다(로컬 대기열 없음). ship도 같은 조건이라 새 제약은 아니다.
- 사람이 `done`을 잊으면 NOW.md가 틀린다. AGENTS.md 규칙과 스킬로만 막는다.
