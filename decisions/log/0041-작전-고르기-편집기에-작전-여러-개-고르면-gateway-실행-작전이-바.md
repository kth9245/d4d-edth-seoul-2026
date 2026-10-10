---
id: 0041
title: 작전 고르기: 편집기에 작전 여러 개, 고르면 gateway 실행 작전이 바뀌고 시뮬레이션 버튼은 상황판으로(시작 전 멈춤)
status: 확정
decided_by: kth9245
date: 2026-10-10
modules: [contracts, gateway, cop-ui]
supersedes: null
---
## 결정
리드 말: "애초에 플레이에서 작전 여러개가 있고 거기서 시뮬레이션을 누르면 플레이로 넘어갔으면 좋겠는데. 그래서 시나리오 여러개 만든거잖아".
리드 답: 전환 시점은 "고르면 바뀜, 버튼은 상황판 이동 (Recommended)", 넘어간 뒤는 "시작 전에서 멈춤", 가정(플레이 삭제 접기·백업 시나리오 빼기·다음 사건 숨기기)에 "ㄱㄱ".

에이전트 해석:
- gateway는 켤 때 시연 시나리오 여러 개(`baengnyeong_night.json`, `baengnyeong_24h.json`)를 메모리에 읽고 그중 하나가 실행 작전이다. `KDTH_SCENARIO`는 처음 실행 작전을 정한다.
- 편집기 사이드바 맨 위에 작전 목록. 다른 작전을 누르면 gateway 실행 작전이 그것으로 바뀌고 실행은 작전 시작 직전(`paused`). 편집기는 그 작전의 개요·플레이를 다시 읽는다. 기존 엔드포인트(`/plays`·`/operation`·`/vehicles`·`/enemies`)는 그대로 실행 작전을 가리킨다.
- 작전을 바꿔도 앞 작전에 저장한 플레이·작전 수정은 gateway 메모리에 남는다(파일에는 쓰지 않음).
- "시뮬레이션" 버튼: 실행을 시작 전으로 되돌리고(`/run/reset`) 상황판 탭으로 간다. 자동 재생 없음.
- 백업 `baengnyeong_night_before_0036.json`은 시나리오 id가 본편과 같아 목록에서 뺀다.
- "다음 사건" 정지 시각은 야간 시나리오 전용이라 다른 작전에서는 "다음 사건 없음".
- 플레이 삭제 버튼(Part3-12.3)은 이것으로 대체해 접었다.

## 이유
- 시나리오 파일이 여러 개(야간 경계, 24시간 해안 순찰 교대)인데 gateway를 다시 켜야만 바꿀 수 있었다.
- 고르는 순간 바꾸면 기존 엔드포인트가 전부 그대로라 변경이 작다(happy path, 결정 0024). 시연은 운용자 한 명이라 편집기에서 고르는 순간 상황판이 처음으로 돌아가도 문제없다.

## 버린 대안
- 시뮬레이션 버튼을 눌러야 바뀜: 편집 엔드포인트 6개가 전부 작전 id를 받아야 해서 일이 크다.
- 바로 재생 시작: 리드가 시작 전 멈춤을 골랐다.
- 플레이 삭제(DELETE /plays/{id}): 이 기능으로 대체.

## 영향
- contracts: `ScenarioInfo{id, name, purpose, active}`(api.py), TS·예시. API.md 5절 `GET /scenarios`, `POST /scenarios/{id}/activate`(→ `RunState`, 없는 id 404).
- gateway: `Live`가 시나리오 여러 개를 들고 `activate`, app.py 시나리오 목록과 두 엔드포인트.
- cop-ui: vite proxy에 `/scenarios`, 편집기 사이드바 작전 목록, 작전 개요의 "시뮬레이션" 버튼, RunBar 다음 사건이 실행 작전에 따라.
