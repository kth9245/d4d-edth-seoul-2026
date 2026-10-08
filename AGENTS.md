# d4d-edth-seoul-2026 — 에이전트 공통 규칙

Korean Defense Tech Hackathon 2026 (D4D × EDTH SEOUL) 팀 저장소. 24시간 안에 **로컬에서 작동하는 데모**를 만든다(NO SLIDES).
설계: `docs/superpowers/specs/2026-10-07-hackathon-repo-structure-design.md`. 문제: `docs/problem.md`.

## 작업 시작 전에 반드시 읽을 것
1. `decisions/INDEX.md` — 사람이 확정한 결정. **반드시 따른다.**
2. `knowledge/INDEX.md` — 이미 조사한 지식. 관련 카드만 연다. 같은 조사를 반복하지 않는다.
3. 작업할 모듈의 `modules/<m>/AGENTS.md`와 `modules/<m>/SPEC.md`.
4. **자기 할 일**: `docs/research/09-rolecall-implementation-foundation.md` 6절. 머리의 "통합 1 배정" 표(결정 0009: Part 2A 최동호, Part 2B 황승주, 리드 kth9245)에서 자기 줄을 찾고, 그 번호(Part2-7 등)의 행에서 입력·출력·완료 기준·앞선 항목을 읽는다. 같은 액션이 `modules/<m>/SPEC.md`에 `예정` 행으로 있으면 `new_action.py`로 가져가 시작한다(아래 액션 규칙). 왜 이렇게 나눴는지는 같은 문서 12절.

## 우선순위
확정 결정·정책 > SPEC.md > 지식 카드 > 너의 판단.
확정 결정과 다르게 해야 한다고 판단되면 **멈추고 사람에게 묻는다.**

## 정책 (decisions/POLICY.md 자동 복사본 — 여기서 수정하지 말 것)
<!-- POLICY:BEGIN -->
1. 시연은 인터넷 없이 동작한다. 지도 타일은 로컬 파일을 쓰고, 시연 경로에서 외부 API를 호출하지 않는다.
2. 공개 데이터·가상(synthetic) 데이터만 쓴다. 비밀·수출통제 정보, 실제 개인 식별·표적화 금지.
3. 좌표는 WGS84 위경도(도), 고도는 m, 시간은 UTC epoch 밀리초(`t_ms`).
4. API 키·비밀값은 커밋하지 않는다(`.env`는 gitignore).
5. 해커톤 중 새로 만든 부분은 `demo/BUILT_HERE.md`에 기록한다.
<!-- POLICY:END -->

## 구조
- `contracts/models.py` 모듈 간 데이터 형식(pydantic). 예시: `contracts/examples/*.json`. 리드만 수정.
- `modules/<m>/` 파이프라인 모듈: sim → sensing → tracking → assess → respond → gateway → cop-ui.
- `shared/` 최소 공통 코드(좌표). `knowledge/` 조사 지식. `decisions/` 사람의 결정. `demo/` 시연.

## 액션 규칙 (1 액션 = 1 파일 = 1 테스트)
- 새 동작은 **반드시** `/new-action` 또는 `uv run python scripts/new_action.py <m> <verb_noun> "<설명>"`으로 시작한다.
  SPEC.md에 없는 액션 파일은 guard가 막는다.
- SPEC.md에 `예정` 행이 이미 있으면 같은 명령을 그대로 돌린다: 담당이 내 git 이름으로 바뀌고 파일·실패 테스트가 생긴다.
  리드가 미리 적을 때는 `--planned`(행만, 파일 없음). 남이 `진행중`인 행을 가져갈 때는 `--take`(담당 칸만 바뀜). 둘 다 채팅에 번호를 적는다.
- 액션 하나가 끝날 때마다 ship한다. 끝나지 않은 액션(실패 테스트)을 ship하지 않는다 — 같은 모듈 사람 전원의 ship이 막힌다. 남의 실패 테스트를 skip으로 바꿔 ship하지 않는다.
- 로깅은 항상 켠다(결정 0010): 실행 경계(gateway app, 틱 루프, REST 핸들러, 스크립트)는 `from shared.log import setup_logging, get_logger`로 stderr와 `logs/<이름>.log`에 남긴다. 틱마다 명령·차단·보고 수와 Frame.log 줄을 DEBUG로, 예외는 traceback과 함께 ERROR로. 순수 함수 액션 안에는 로깅을 넣지 않는다.
- 통합 1(10/10 18:00) 전에는 sim·gateway의 레거시 공개 API(`load_scenario`·`simulate`·`Engine`)를 지우거나 서명을 바꾸지 않는다. smoke가 깨져 전원 ship이 막힌다. 새 동작은 새 이름으로 추가한다.
- 모듈 자체가 아직 없으면(edge, identify, planning 등) 먼저 `/new-module` 또는
  `uv run python scripts/new_module.py <이름> <PREFIX>`로 만든다. 브랜치는 `<이름>/<주제>`.
- 액션 파일: 공개 함수 1개, 이름 = 파일 이름, 80줄 이하, 입력·출력 타입 명시.
- 다른 파일(.py/.ts/.tsx)은 200줄 이하. 넘으면 쪼갠다.
- `pipeline.py`는 액션을 순서대로 부르기만 한다(로직 금지).
- 다른 모듈은 `from modules.<m> import <공개 API>`로만 쓴다. 내부(`modules.<m>.actions...`) import 금지.
- 테스트 먼저: 생성된 실패 테스트를 실제 동작 테스트로 바꾸고, 통과시킨다.

## 소유 (담당 안내. guard가 브랜치로 막지 않는다 — 2026-10-09 리드 지시로 브랜치별 수정 제한 훅 제거)
| 브랜치 | 주로 고치는 곳 | 담당 |
|---|---|---|
| `<모듈>/<주제>` | `modules/<모듈>/**`, `knowledge/**`, `decisions/log/**`(제안만) | 아래 표 |
| `contracts/<주제>` | `contracts/**` | 리드 |
| `infra/<주제>` | AGENTS.md, scripts, tools, 설정, shared, demo, docs | 리드 |

| 모듈 | 담당 (결정 0007·0009: 리드 kth9245, 파트 2A 최동호, 파트 2B 황승주. 무작위 배정, 편집기는 읽기 전용 카드로 리드) |
|---|---|
| contracts, gateway REST/WS, demo, infra, cop-ui 전부(map/live + editor/setup 읽기 전용 카드) | 리드 kth9245 |
| sim, sensing, gateway `engine.py` 틱 루프 | 파트 2A 최동호 |
| safety, runtime, play | 파트 2B 황승주 |
| tracking, assess, respond | 휴면(T1-3용). 손대지 않음 |

항상 수정 가능(어느 브랜치에서든): `demo/BUILT_HERE.md`, `demo/scenarios/*`, `pyproject.toml`, `uv.lock`.

남의 영역을 고쳐야 하면 고칠 수는 있지만, 고친 내용을 담당자에게 알린다(rebase 충돌은 고친 사람이 푼다).

## 명령
- 설치·브랜치: `scripts/setup.sh <모듈>`
- 개발 실행: `scripts/dev.sh` / 시연 실행: `scripts/demo.sh`
- 모듈 테스트: `uv run pytest modules/<m>`
- 반영: `scripts/ship.sh` (/ship) — 최신 main 반영 + 변경 모듈 테스트 + 데모 smoke test + push
- 원격 브랜치는 만들지 않는다. 작업 브랜치는 로컬에만 두고, 끝나면 main에 병합해 main만 push한다(ship.sh가 이 순서: rebase → 검사 → origin main에 push → 로컬 main 맞춤). PR과 원격 브랜치 push는 쓰지 않는다.
- 지식 정리: /kb-save · 결정 제안: /decide

## 의존성 추가
- 셸에서 `uv add <패키지>`(pyproject.toml·uv.lock은 어느 브랜치에서든 수정 가능). 직접 편집 금지.
- rebase 중 `uv.lock` 충돌이 나면 `uv lock`을 실행하고 `git add uv.lock && git rebase --continue`.

## 지식과 결정
- 조사 결과는 답변으로만 끝내지 말고 `knowledge/inbox/`에 원문을 넣고 /kb-save로 카드를 만든다. 출처 없는 내용은 `confidence: 추정`.
- 사람이 결정을 말하면 /decide로 `제안` 문서를 만든다. 결정 문서의 목적은 사람이 말한 것을 잊지 않는 것이다(2026-10-09 리드 지시). AI가 질문해서 사람이 답한 것은 그 자체가 확정이므로, 같은 턴에 `decide.py accept`를 실행한다. 별도의 "확정해 주세요" 요청은 하지 않는다. `결정` 절에는 사람이 한 말을 인용하고 AI의 해석은 구분해 적는다. 결정 파일에 직접 `확정`을 쓰는 것은 여전히 guard가 막는다(accept 명령만 허용).
- `decide.py accept`는 사람이 승인해야 실행된다. 사람이 그 결정을 확정하라고 말했을 때만 AI가 단독 명령으로 실행하고, Claude Code는 guard hook이, Codex는 `.codex/rules/decide.rules`가 승인 창을 띄운다. AI가 `decisions/POLICY.md`를 고치거나 결정 파일에 직접 `확정`을 쓰면 guard가 막는다.

## 하지 말 것
- CLAUDE.md / CLAUDE.local.md 생성 (Claude가 이 파일을 무시하게 됨)
- 자동 생성 파일 수정: `tasks/BOARD.md`, `knowledge/INDEX.md`, `decisions/INDEX.md`, `contracts/schema/`, `contracts.gen.ts`
- 비공개·수출통제 데이터, 실제 개인 식별 정보 사용

## 시간이 급할 때
- `git commit --no-verify` 허용(ship의 smoke test는 유지).
- 일요일 06:00 이후 `KDTH_FREEZE=1`: 구조 검사는 경고만, smoke test만 차단.
