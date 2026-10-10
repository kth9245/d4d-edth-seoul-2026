# 해커톤 저장소 구조 설계 (AI 병렬 개발용)

- 날짜: 2026-10-07
- 대상 행사: Korean Defense Tech Hackathon 2026 (D4D × EDTH SEOUL), 2026-10-10 10:00 개발 시작 ~ 10-11 10:00 제출
- 저장소: https://github.com/kth9245/d4d-edth-seoul-2026 (private)
- 상태: 설계 승인됨

## 1. 목적과 제약

### 목적
4명이 각자 AI 코딩 도구(Claude Code, Codex 등)로 동시에 개발할 때, 서로 충돌하지 않고 빠르게 기능을 쌓을 수 있는 저장소 골격을 대회 전에 만들어 둔다.

### 성공 기준
1. 기능이 **모듈 → 액션(1 액션 = 1 파일 = 1 테스트)** 단위로 쪼개지고, 이 쪼개기가 문서 권고가 아니라 도구로 강제된다.
2. 부가 작업(기록·검사)이 개발과 push를 늦추지 않는다. 커밋 검사 2초 이하, push 검사 20초 이하.
3. Claude Code와 Codex(GPT) 어느 쪽을 써도 같은 규칙이 적용된다.
4. 대회 어느 시점에 멈춰도 로컬에서 돌아가는 데모가 있다.
5. 조사로 얻은 지식과 사람이 내린 결정이 쌓이고, AI가 다음 작업에서 그것을 다시 쓴다.

### 행사 제약 (참가자 안내 시트 기준)
- 팀당 최대 4명, 트랙 하나의 문제 하나를 해결. 예상 트랙은 T1(자율·무인 시스템 및 대드론).
- 심사 원칙 NO SLIDES: 작동하는 결과물로 평가, 팀당 5분 현장 심사. 해커톤 중 새로 만든 부분을 구분해서 발표.
- 공개 데이터·가상(synthetic) 데이터만 사용. 비밀·수출통제 정보, 개인 식별·표적화 금지.
- 시연은 로컬 노트북에서 한다. HDMI 송출 지원.

### 범위 밖 (넣지 않는 것)
- CI(원격 검사 서비스), 배포 파이프라인. 시연이 로컬이고 대기 시간이 개발을 늦추기 때문.
- 벡터 DB·RAG·MCP 기반 지식 검색. 24시간 동안 쌓이는 카드 수십~백여 장은 목차 파일과 grep으로 충분.
- 작업 선점용 잠금 파일. 모듈별 브랜치 소유로 이미 겹치지 않음.

## 2. 기술 스택 (기본값, 교체 가능)

| 영역 | 기본값 | 비고 |
|---|---|---|
| 백엔드·엔진 | Python 3.11+, FastAPI, pydantic v2, uv(패키지 관리) | 수치·AI 라이브러리 활용 |
| 화면 | React + Vite + TypeScript, MapLibre GL | 지도 타일은 로컬 파일로 동봉 |
| 모듈 연결 | gateway가 파이프라인을 실행하고 WebSocket으로 화면에 송출 | |
| 검사 도구 | ruff, pytest, `tools/check_imports.py`(모듈 경계), eslint(max-lines) | |

팀원이 다른 스택을 고르면 `modules/*/` 내부와 lint 도구만 바뀐다. 규칙 문서, 계약, SPEC, 지식·결정 저장소, 차단 스크립트의 구조는 그대로 유지한다.

## 3. 폴더 구조

```
d4d-edth-seoul-2026/
├── AGENTS.md              # 공통 규칙 (Claude·Codex 공통). 150줄 이하. CLAUDE.md는 두지 않음
├── README.md              # 실행법, 데모 요약
│
├── docs/
│   ├── problem.md         # 고른 문제 원문, 심사 기준, 데이터 제약
│   ├── glossary.md        # T1 관련 용어
│   └── superpowers/specs/ # 설계 문서
│
├── contracts/             # 모듈 간 데이터 형식. 리드만 수정
│   ├── README.md          # 데이터 흐름도
│   ├── models.py          # pydantic 모델 (원본)
│   ├── schema/*.json      # models.py에서 자동 생성한 JSON Schema
│   └── examples/*.json    # 형식별 예시 데이터 (가짜 데이터로 먼저 개발할 때 사용)
│
├── modules/               # 파이프라인 순서. 서로의 내부를 import하지 않음
│   ├── sim/               # 가상 시나리오·센서 데이터 생성
│   ├── sensing/           # 센서 입력을 Detection 형식으로 정규화
│   ├── tracking/          # Detection → Track (예측·연관·갱신·생성·삭제)
│   ├── assess/            # Track 분류(드론/풍선/조류)와 위협도
│   ├── respond/           # 대응 옵션 추천 (교전규칙·부수피해 고려)
│   ├── gateway/           # 파이프라인 실행 + WebSocket 송출
│   ├── cop-ui/            # 지도 관제 화면 (TypeScript). public/tiles/seoul.pmtiles(29MB)는 저장소에 커밋
│   └── edge/              # (선택, 필요 시 생성) SC1 온디바이스 AI / SC2 NUCODE 보드 코드
│
├── shared/                # 최소 공통 코드: 좌표 계산, 시계. 비대해지지 않게 유지
│
├── knowledge/             # AI가 조사·정리한 지식 (참고용, 틀릴 수 있음)
│   ├── INDEX.md           # 자동 생성 목차
│   ├── inbox/             # 원문 보관함 (가공하지 않음)
│   ├── cards/             # 지식 카드 (1장 = 결론 1개)
│   └── spikes/            # 버리는 실험 코드 (import 금지)
│
├── decisions/             # 사람이 확정한 결정·정책 (AI는 반드시 따름)
│   ├── POLICY.md          # 항상 지키는 정책
│   ├── INDEX.md           # 자동 생성 목록
│   └── log/NNNN-*.md      # 결정 기록 (ADR 형식)
│
├── demo/
│   ├── scenarios/*.yaml   # 발표용 시나리오 (모든 브랜치에서 수정 가능)
│   ├── BUILT_HERE.md      # 해커톤 중 새로 만든 부분 (심사 요구사항, 모든 브랜치에서 수정 가능)
│   └── RUNBOOK.md         # 5분 시연 순서, 실패 시 대체 절차
│
├── tasks/
│   └── BOARD.md           # 자동 생성 작업판 (모든 모듈 SPEC.md에서 생성)
│
├── tools/guard/           # Claude·Codex 공용 차단 스크립트
├── .agents/skills/        # skill 원본 (Codex가 읽음)
├── .claude/               # settings.json(hook 등록), skills → ../.agents/skills symlink
├── .codex/                # hooks.json(같은 guard 호출)
├── .githooks/pre-commit   # 커밋 검사 (도구 무관)
│
├── scripts/
│   ├── setup.sh           # 대회 당일 1회: 의존성 설치, git hook 연결, 브랜치·worktree 생성
│   ├── new_action.py      # SPEC 행 + 액션 파일 + 실패하는 테스트 생성
│   ├── new_module.py      # 새 모듈 골격(AGENTS.md, SPEC.md, actions/, tests/) 생성. /new-module
│   ├── sync_docs.py       # BOARD·지식 INDEX·결정 INDEX·AGENTS.md 정책 구간 자동 생성
│   ├── gen_contracts.py   # models.py → schema/*.json + cop-ui TS 타입
│   ├── decide.py          # 결정 제안 생성 / 사람이 확정(accept)
│   ├── check.sh           # 커밋 검사 (--all: 전체 테스트)
│   ├── ship.sh            # main 최신 반영 + 검사 + push
│   ├── dev.sh             # 개발용 전체 실행
│   └── demo.sh            # 시연용 전체 실행
└── pyproject.toml         # ruff, pytest 설정 (uv.lock과 함께 모든 브랜치에서 수정 가능: uv add)
```

### 3.1 문제별 모듈 교체
`sim`, `sensing`, `gateway`, `cop-ui`는 T1 문제 공통이다. 중간 모듈만 문제에 맞게 바꾼다.

| 문제 | 변경 |
|---|---|
| T1-3 수도권 소형드론·풍선 대응 | 그대로 |
| T1-4 무선침묵 피아식별 | `assess` → `identify` (challenge-response) |
| T1-1 다중 무인기 통제 | `respond` → `tasking` (임무 배분) |
| T1-2 지형 인지 자율비행 | `planning` (3D 경로 계획) 추가 |

## 4. 모듈과 액션

### 4.1 Python 모듈 내부 구조
```
modules/tracking/
├── AGENTS.md        # 40줄 이하: 책임, 입력·출력 계약, 소유자, 금지사항
├── SPEC.md          # 액션 표. 여기 없는 액션 파일은 만들 수 없음
├── __init__.py      # 공개 API. 다른 모듈은 이것만 import
├── pipeline.py      # 액션을 순서대로 호출만 함 (로직 없음)
├── types.py         # (선택) 모듈 내부에서만 쓰는 타입
├── actions/<verb_noun>.py
└── tests/test_<verb_noun>.py
```

### 4.2 액션 규칙
- 파일 하나에 공개 함수 하나. 함수 이름 = 파일 이름(`verb_noun`).
- 입력·출력 타입 명시. 계약 타입은 `contracts.models`에서 가져온다.
- 80줄 이하. 넘으면 액션을 쪼갠다.
- 파일 첫 docstring에 SPEC id와 한 줄 설명.
- 다른 모듈은 그 모듈의 `__init__.py` 공개 API로만 사용.

생성 뼈대 (`new_action.py` 출력):
```python
"""TRK-01 predict_tracks: 기존 표적의 dt초 뒤 위치를 등속 모델로 예측
SPEC: modules/tracking/SPEC.md#TRK-01
"""

from contracts.models import Track


def predict_tracks(tracks: list[Track], dt: float) -> list[Track]:
    raise NotImplementedError
```
테스트 파일은 `NotImplementedError` 때문에 실패하는 상태로 생성된다.

### 4.3 SPEC.md 형식
| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| TRK-01 | predict_tracks | list[Track], dt | list[Track] | 등속 모델 1초 뒤 오차 1m 이내 | 철수 | 진행중 |

- 상태 값: 예정 / 진행중 / 완료.
- `tasks/BOARD.md`는 모든 SPEC.md 표를 모아 `sync_docs.py`가 생성한다. 손으로 고치지 않으며 git에 올리지 않는다(8.6).

### 4.4 cop-ui (TypeScript) 규칙
- `src/features/<기능>/` 아래 컴포넌트·hook 1개 = 파일 1개, 200줄 이하.
- SPEC.md에 화면 단위(컴포넌트·hook)를 등록한다. 테스트는 화면이 아닌 로직(데이터 변환, hook)에만 요구한다.
- 계약 타입은 `src/contracts.gen.ts`(자동 생성)만 사용.

## 5. 계약 (contracts/)

- 원본은 `contracts/models.py`의 pydantic 모델: Detection, Track, Assessment, Response.
- `gen_contracts.py`가 JSON Schema와 TS 타입을 생성한다. 커밋 시 `contracts/`가 바뀐 경우에만 실행된다.
- `examples/*.json`은 각 형식의 예시 데이터다. 앞 모듈이 완성되기 전에 뒤 모듈이 이 데이터로 개발·테스트한다. 예시가 모델과 맞는지는 테스트로 확인한다.
- 좌표는 WGS84 위경도(도), 고도는 m, 시간은 UTC epoch 밀리초 (POLICY.md에 명시).
- 계약 수정은 리드만 한다. 다른 팀원은 리드에게 요청한다.

## 6. 지식 저장소 (knowledge/)

참고: Karpathy LLM Wiki 패턴(원문 → AI가 정리한 wiki), Zettelkasten atomic note.

흐름:
1. 조사 중 원문·링크·대화는 `inbox/`에 그대로 저장.
2. `/kb-save` 실행 시 AI가 inbox를 읽어 카드로 정리. 비슷한 카드가 있으면 새로 만들지 않고 수정. 출처가 약하면 `confidence: 추정`.
3. `sync_docs.py`가 커밋마다 `INDEX.md`(카드당 한 줄, 모듈별 묶음)를 생성.
4. AGENTS.md 규칙: 조사·구현 전에 `knowledge/INDEX.md`를 먼저 보고 관련 카드만 연다.
5. 사람은 GitHub이나 Obsidian으로 열람(`[[카드id]]` 링크).

카드 형식:
```markdown
---
id: rf-drone-control-bands
title: 상용 드론 조종 신호 주파수 대역
summary: 상용 드론은 주로 2.4GHz·5.8GHz 대역을 쓴다
tags: [rf, detection]
modules: [sensing, sim]
confidence: 확인됨          # 확인됨 / 추정
sources: [https://...]
author: 이름
---
## 결론
## 근거
## 코드에 적용하는 법
## 관련 카드
```
카드는 40줄 이하. `spikes/`는 본 코드에서 import 금지(모듈 경계 검사), 길이 제한 예외.

## 7. 결정·정책 저장소 (decisions/)

참고: ADR(Architecture Decision Record, Michael Nygard).

- `POLICY.md`: 개발 내내 적용되는 규칙. 초기 정책:
  1. (2026-10-08 변경) 인터넷 제약 없음. 시연 중 외부 AI API(Claude, GPT 등) 사용 가능. 키는 `.env`에 두고 커밋하지 않는다.
  2. 공개·가상 데이터만 사용한다.
  3. 좌표 WGS84, 고도 m, 시간 UTC epoch 밀리초.
  4. API 키·비밀값은 커밋하지 않는다(`.env`, gitignore).
- `log/NNNN-*.md`: 한 번 내린 선택과 이유.
```markdown
---
id: 0002
title: 추적은 등속 Kalman filter로 한다
status: 제안            # 제안 / 확정 / 폐기
decided_by: 이름        # 확정 시 필수
date: 2026-10-10
modules: [tracking]
supersedes: null
---
## 결정
## 이유
## 버린 대안
## 영향
```
- 결정을 바꿀 때는 기존 문서를 `폐기`로 두고 새 문서에서 `supersedes`로 가리킨다.
- AI는 `/decide`로 `status: 제안` 문서만 만든다. 확정은 사람이 에디터에서 직접 바꾸거나 터미널에서 `python scripts/decide.py accept NNNN`을 직접 실행한다.
- `sync_docs.py`가 POLICY.md 내용을 루트 AGENTS.md의 표시 구간(`<!-- POLICY:BEGIN -->` ~ `<!-- POLICY:END -->`)에 복사한다. 두 AI 도구 모두 루트 AGENTS.md를 항상 읽으므로 정책이 매 세션 적용된다.
- 우선순위(AGENTS.md에 명시): 확정 결정·정책 > SPEC > 지식 카드 > AI 판단. 확정 결정과 다르게 해야 한다고 판단되면 AI는 멈추고 사람에게 묻는다.

## 8. 강제 장치

원칙: 사람이 손으로 하는 기록 작업은 없다. 고칠 수 있는 문제는 자동으로 고친다. 느린 검사는 커밋에서 뺀다.

### 8.1 소유 규칙 (브랜치 이름 기준)
| 브랜치 접두어 | 수정 가능 경로 |
|---|---|
| `<모듈>/…` (예: `tracking/kalman`) | `modules/<모듈>/**`(디렉터리가 아직 없어도 허용: `new_module.py`로 새 모듈 생성), `knowledge/**`, `decisions/log/**`(새 제안 문서만) |
| `contracts/…` | `contracts/**`, `modules/cop-ui/src/contracts.gen.ts` |
| `infra/…` | 루트 `AGENTS.md`·`README.md`·`.gitignore`, `modules/__init__.py`, `tests/`, `scripts/`, `tools/`, `.claude/`, `.codex/`, `.agents/`, `.githooks/`, `shared/`, `demo/`, `docs/` |
| 어느 브랜치든 (ALWAYS) | `knowledge/**`, `decisions/log/**`(제안만), `demo/BUILT_HERE.md`, `demo/scenarios/*`, `pyproject.toml`, `uv.lock` |
| 그 외 (예: `main`) | 모듈 수정 차단, "브랜치를 `<모듈>/<주제>`로 만들라"고 안내 |

어느 브랜치에서도 AI는 `status: 확정` 결정 문서와 `POLICY.md`를 수정할 수 없다.

### 8.2 1단계: AI가 파일을 수정할 때 (`tools/guard/check_edit.py`)
- Claude Code: `.claude/settings.json`의 PreToolUse(`Edit|Write`)와 PostToolUse에서 호출. 입력의 `tool_input.file_path` 사용.
- Codex: `.codex/hooks.json`의 PreToolUse(`^apply_patch$`)에서 호출. 입력 `tool_input.command`의 patch 본문에서 `*** Add File:` / `*** Update File:` / `*** Delete File:` 줄로 경로 추출. 팀원마다 Codex `/hooks`에서 1회 신뢰 승인.
- Bash 경로: Claude `PreToolUse` 매처 `Bash`, Codex `^(Bash|shell)$`(pre만). `tool_input.command`가 `decide.py accept`이거나 `decisions/POLICY.md`에 리다이렉션·`sed -i`·`tee`로 쓰면 차단하고 사람에게 요청하라고 안내. 그 외 명령은 통과.
- 차단은 exit code 2 + stderr에 이유와 해결 방법. 예상 못 한 예외는 통과시키되 `$(git rev-parse --git-dir)/guard-errors.log`에 한 줄 기록.

| 검사 | 시점 | 결과 |
|---|---|---|
| 소유 경로 (8.1) | 수정 전 | 차단 |
| 새 액션 파일의 SPEC 등록 여부 | 수정 전 | 차단, `new_action.py` 안내 |
| 보호 파일(`.env`, 자동 생성 파일, 확정 결정, POLICY.md) | 수정 전 | 차단 |
| 파일 길이(액션 80줄, 그 외 200줄) | 수정 후 | AI에게 쪼개라는 피드백 |
| Bash로 결정 확정·POLICY.md 쓰기 | 실행 전 | 차단, 사람에게 요청 안내 |

목표 실행 시간 0.1초 이하.

### 8.3 2단계: 커밋 (`.githooks/pre-commit` → `scripts/check.sh`)
1. `ruff check --fix` + `ruff format` 후 결과를 커밋에 자동 포함. 자동 수정 불가 오류만 차단.
2. `tools/check_imports.py`(AST 기반, 의존성 없음): 모듈은 다른 모듈의 루트 공개 API(`from modules.<m> import ...`)와 `shared`, `contracts`만 import. `modules.<다른모듈>.<하위>` import 금지, `knowledge` import 금지, `shared`·`contracts`는 `modules`를 import하지 않음. import-linter에는 '루트 공개 API만 허용' 규칙이 없어서 전용 스크립트로 대체.
3. SPEC 동기화: 모든 액션 파일이 SPEC.md에 있고, 각 액션에 테스트 파일이 있다.
4. 파일 길이.
   2~4번은 스테이징된 파일(과 그 파일이 속한 모듈)만 검사해 남의 미완성 파일로 내 커밋이 막히지 않게 한다. `check.sh --all`과 ship은 전체 검사.
   추가로 스테이징 diff에 비밀값 패턴(`AKIA…`, `sk-…`, 개인 키 헤더)이 있으면 차단.
5. `sync_docs.py` 실행. 정책 구간이 바뀐 루트 AGENTS.md만 커밋에 자동 포함하고, BOARD·INDEX는 로컬 파일만 갱신한다(8.6). 차단하지 않음.
6. `contracts/`가 바뀐 경우에만 `gen_contracts.py`.

테스트는 커밋에서 실행하지 않는다. 목표 2초 이하.

### 8.4 3단계: push (`scripts/ship.sh`)
1. `git fetch` 후 현재 브랜치를 `origin/main` 위로 rebase.
2. 변경된 모듈의 pytest. `tests/`·`tools/`·`scripts/`·`contracts/`·`shared/`가 바뀌면 전체(`tests modules`). `KDTH_FREEZE=1`이면 테스트 실패는 경고로 계속, smoke test만 차단.
3. 데모 smoke test(`scripts/smoke.py`): 화면 없이 기본 시나리오를 시뮬레이션 시간 10초만큼 빠르게 실행해, 예외 없이 모든 프레임이 계약 형식을 만족하는지 확인.
4. `git push origin HEAD:main` 후 작업 브랜치 유지.

실패 시 실패한 테스트와 이유만 짧게 출력한다. 목표 20초 이하. 전체 테스트는 `scripts/check.sh --all`로 필요할 때만.

### 8.5 시간이 급할 때
- `git commit --no-verify`로 커밋 검사 건너뛰기 허용. push 단계 smoke test는 유지.
- 데모 고정 모드 `KDTH_FREEZE=1`: 파일 길이·SPEC 등록 검사가 경고로만 동작. 데모 smoke test만 차단 조건. 일요일 06:00부터 사용.

### 8.6 자동 생성 파일은 git에 올리지 않음
`tasks/BOARD.md`, `knowledge/INDEX.md`, `decisions/INDEX.md`는 `.gitignore`에 넣는다. 4명이 커밋할 때마다 같은 생성 파일이 바뀌면 rebase마다 충돌이 나기 때문이다. 대신 `sync_docs.py`가 pre-commit, post-merge, post-checkout, post-rewrite git hook과 `ship.sh`에서 실행되어 각자 로컬에서 항상 최신 상태로 다시 만든다. 원본(각 SPEC.md, 카드, 결정 문서)만 git에 올라간다.

예외: 루트 AGENTS.md의 정책 구간은 커밋한다. POLICY.md가 바뀔 때만 달라지고 POLICY.md는 사람이 드물게 고치므로 충돌 위험이 낮다.

## 9. AI 도구 호환

| 항목 | Claude Code | Codex |
|---|---|---|
| 루트 AGENTS.md | 읽음 (CLAUDE.md가 없을 때, v2.1.277 이상) | 읽음 |
| 모듈 AGENTS.md | 그 폴더 파일을 열 때 자동 로드 | 실행 위치까지만 로드 → **모듈 폴더에서 실행** (`cd modules/tracking && codex`) |
| 규칙 강제 | `.claude/settings.json` hook → guard | `.codex/hooks.json` hook → 같은 guard |
| 반복 명령 | `.claude/skills/` (`.agents/skills/`를 가리키는 symlink) | `.agents/skills/` (원본) |

- CLAUDE.md, CLAUDE.local.md를 만들지 않는다. 하나라도 있으면 Claude가 AGENTS.md를 무시한다. 개인 설정은 `~/.claude/CLAUDE.md`에 둔다.
- 루트 AGENTS.md에 "모듈 작업 전 그 모듈의 AGENTS.md와 SPEC.md를 먼저 읽는다"를 명시한다(Codex를 루트에서 실행한 경우 대비).
- AGENTS.md 합계는 Codex 한도(32KiB)보다 훨씬 작게 유지한다: 루트 150줄, 모듈 40줄.
- skill(`/new-action`, `/kb-save`, `/decide`, `/ship`)은 `scripts/`의 스크립트를 호출만 한다. 로직은 스크립트에 있으므로 두 도구에서 동작이 같다.
- 팀원은 대회 전에 Claude Code를 v2.1.281 이상으로 업데이트하고 한 번 실행해 둔다.

## 10. 4명 병렬 작업

### 10.1 역할
| 담당 | 소유 | 비고 |
|---|---|---|
| 리드 | contracts, gateway, demo, infra, decisions 확정 | 시연 노트북. gateway 이후 respond 지원 |
| 팀원 2 | sim, sensing, (edge) | 가상 데이터 |
| 팀원 3 | tracking, assess, respond | 핵심 엔진 |
| 팀원 4 | cop-ui | 지도 화면 |

소유표는 루트 AGENTS.md에 두고 당일 조정한다.

### 10.2 작업 방식
- 사람마다 각자 노트북에서 clone. 한 사람이 AI 세션을 여러 개 돌릴 때만 모듈별 git worktree를 쓴다(`setup.sh`가 생성).
- 계약과 예시 데이터를 먼저 확정하고, 각자 예시 데이터로 동시에 시작한다.
- walking skeleton: 처음 3시간 안에 모든 액션을 가짜 로직(입력 전달, 고정값)으로 채워 시나리오부터 화면까지 끝까지 연결한다. 이후 액션을 하나씩 진짜 로직으로 교체한다.
- 최소 1시간마다 `ship.sh`.

### 10.3 팀원 한 명의 작업 순서
1. `/new-action <모듈> <액션> "<설명>"`
2. AI에게 테스트를 통과시키라고 요청
3. `git commit`
4. 몇 개 쌓이면 `scripts/ship.sh`

### 10.4 타임라인
| 시간 | 할 일 |
|---|---|
| 토 10:00–11:00 | 문제 확정, setup.sh, 계약·예시 확정, 모듈별 SPEC 액션 목록 작성 |
| 11:00–14:00 | walking skeleton |
| 14:00–02:00 | 액션을 진짜 로직으로 교체, 1시간마다 ship |
| 02:00–06:00 | 데모 시나리오·화면 완성도·성능 |
| 일 06:00 | `KDTH_FREEZE=1` |
| 08:00–09:30 | 리허설 2회, BUILT_HERE.md 정리, 백업 영상 녹화 |
| 10:00 | 제출 |

## 11. 로컬 시연
- `scripts/demo.sh` 한 줄로 백엔드·화면·시나리오 실행. 대회 전에 시연 노트북에서 시험.
- 로컬 지도 타일(행사장 네트워크 속도와 무관하게 지도 표시): 수도권 범위 지도 타일을 대회 전에 받아 저장소에 동봉(PMTiles 파일 1개, `modules/cop-ui/public/tiles/seoul.pmtiles`를 커밋. 갱신은 `scripts/fetch_tiles.sh`). 파일이 없으면 `demo.sh`가 큰 경고를 출력하고 계속 실행.
- 정상 동작 화면 백업 영상 녹화.
- 리허설 때 HDMI 송출 해상도에서 지도·경보 가독성 확인.

## 12. 대회 전 준비 범위
대회 전(10-09까지)에 만들고 시험까지 끝낼 것:
- 폴더 골격, 루트·모듈 AGENTS.md, SPEC.md 템플릿
- contracts 초안(models.py, examples), gen_contracts.py
- tools/guard, .claude·.codex hook 설정, .githooks/pre-commit
- scripts 전부(setup, new_action, sync_docs, decide, check, ship, dev, demo)
- skill 4종(new-action, kb-save, decide, ship)
- walking skeleton 예시 1개(가짜 로직으로 sim → tracking → gateway → cop-ui 연결)
- 로컬 지도 타일, decisions/POLICY.md 초기 정책

## 13. 참고 자료
- EU JRC C-UAS Sensor Data Fusion (SeDaFuV): https://code.europa.eu/groups/jrc-cuas-sensor-data-fusion
- Stone Soup tracker 구성: https://stonesoup.readthedocs.io/en/v1.9.1/stonesoup.tracker.html
- Vertical slice for AI 코드: https://www.managed-code.com/blog-post/vertical-slice-architecture-for-ai-generated-code
- AI-Sliced Architecture: https://dev.to/vibecodiq/asa-the-first-architecture-built-for-the-ai-coding-era-3g2k
- Claude Code 메모리·AGENTS.md: https://code.claude.com/docs/en/memory
- Codex AGENTS.md: https://learn.chatgpt.com/docs/agent-configuration/agents-md
- Codex hooks: https://learn.chatgpt.com/docs/hooks
- Anthropic 병렬 Claude 실험: https://www.anthropic.com/engineering/building-c-compiler
- Karpathy LLM Wiki: https://venturebeat.com/data/karpathy-shares-llm-knowledge-base-architecture-that-bypasses-rag-with-an
- Zettelkasten for coding agents: https://dev.to/argenkiwi/zettelkasten-as-a-note-taking-method-for-coding-agents-53gb
- ADR: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
