---
id: 0017
title: API·모듈 규약 세부: runtime 서명, TickOutcome은 contracts, 요청 본문 분리·서버가 id와 t_ms, Frame.run, 400/404/409, id 규칙, 정본은 contracts/API.md
status: 확정
decided_by: kth9245
date: 2026-10-09
modules: [contracts, runtime, gateway, cop-ui, infra]
supersedes: null
---
## 결정
2026-10-09 23시 구조 검토(https://claude.ai/artifact/HkS5JxvaV9YonAkuoJVZ26)와 결정 0015·0016 뒤, AI가 남은 기술 세부 7개를 한 묶음 추천안으로 보이고 사람이 답한 것을 적는다.

- 사람: 규약 기록 위치 "별도 문서 contracts/API.md"
- 사람: 함수 서명 "둘다 검토한 다음에 더 맞는 방향으로 가야지" → AI가 09 문서 3절·6절을 함수별로 비교한 표를 보임 → 두 층 구조로 고친 추천안 1~7에 사람 "이대로 (Recommended)"
- 사람: 09 문서 "정본 안내만 + 6절 수정 (Recommended)"
- 사람: 검토 페이지 "그대로 두고 API.md가 대신 (Recommended)"

(AI 해석, 추천안 1~7 그대로)
1. runtime 서명: `step_vehicle(state, spec, play, targets, t_ms) -> (state, Command|None, Report|None)`, `apply_reserves(states, op, assignments, t_ms) -> (states, assignments, Report|None)`(구 `assign_roles`), `apply_decision(states, plays, decision, reports) -> (states, reports)`, `apply_injection(states, plays, injection) -> states`(전환 버튼·일부 전환 승인, 모델 이름 `Injection`·엔드포인트 `/injections` 유지), `apply_direct(states, direct, t_ms) -> (states, Command)`, `apply_emergency(states, plays) -> states`(틱에서 `step_vehicle` 바로 앞), `update_metrics(metrics, outcome) -> Metrics`. sim `apply_events(scenario, ...)`는 3절, 나머지 sim·sensing·safety·play·gateway 서명은 두 절이 같다. 공통 형식: `specs: dict[기체 id, VehicleSpec]`, `plays: dict[플레이 id, Play]`.
2. `TickOutcome`은 contracts에 둔다. gateway에 두면 runtime이 gateway를 import해 순환이 생긴다.
3. 요청 본문은 별도 모델(`DecisionIn`, `DirectIn`, `SwitchIn`, `DraftIn`)이고, 서버가 `id`와 `t_ms`를 붙여 `Decision` 등으로 바꿔 다음 틱 `TickInputs`에 넣는다. 응답은 `Accepted{id, t_ms}`.
4. 실행 상태는 `Frame.run = RunState{status: running|paused|ended, speed}`. `/run/jump`는 `offset_ms`를 받는다.
5. 오류: 형식 400, 없는 id 404, 상태 충돌 409, 본문은 FastAPI 기본 `{"detail": ...}`.
6. id: 엔진이 만드는 것은 `<종류>-<기체>-<t_ms>`(같은 틱 둘째부터 `-2`), 서버가 받는 입력은 `dec-1`·`dir-1`·`inj-1` 순번. 무작위 uuid 금지(같은 seed = 같은 결과).
7. 정본: 모듈 사이·화면과 서버 사이 규약은 `contracts/API.md`, 데이터 형식은 `contracts/models/`. AGENTS.md "먼저 읽을 것"에 `contracts/API.md`를 넣는다. 09 문서 2·3절은 머리에 정본 안내만 적고, 6절(작업 목록)만 새 서명에 맞춘다. 검토 페이지는 갱신하지 않는다.

## 이유
- 3절과 6절이 서로 다른 서명을 적고 있어 18:00 통합에서 어긋날 위험이 있었다.
- 화면은 엔진의 현재 시각을 모르므로 시각과 id는 서버가 붙여야 한다.
- 같은 내용을 두 문서에 두면 어긋나므로 정본을 하나로 정한다.

## 버린 대안
- 3절 서명 그대로: 이어받기·결정이 다른 기체 상태와 카드를 못 바꾼다.
- `TickOutcome`을 gateway에: 순환 import.
- 화면이 `Decision` 전체를 보냄: 화면이 모르는 시각을 채워야 한다.
- WS에 Frame 말고 다른 메시지 종류 추가: 화면 코드가 메시지 분기를 가져야 한다.
- 09 문서 2·3·6절 전체 재작성: 같은 내용이 두 곳에 생기고 1시간이 더 든다.

## 영향
- `contracts/API.md` 새 문서, `contracts/models/api.py`, AGENTS.md 읽을 목록, 09 문서 2·3절 머리와 6절.
- modules/runtime/SPEC.md의 `assign_roles` 예정 행 이름이 `apply_reserves`로 바뀐다.
