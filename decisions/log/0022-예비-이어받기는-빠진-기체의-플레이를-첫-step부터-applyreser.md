---
id: 0022
title: 예비 이어받기는 빠진 기체의 플레이를 첫 step부터: apply_reserves에 plays 추가, TickOutcome.reports 추가
status: 확정
decided_by: kth9245
date: 2026-10-09
modules: [runtime, contracts, gateway]
supersedes: null
---
## 결정
2026-10-10 0시 무렵 스파이크를 두 층 구조로 고치던 중(Part1-16, 사람 지시 "이것도 고쳐놔야지 당연히 이거 일단 고치고") AI가 묻고 사람이 답했다.

AI: "예비 이어받기 함수 서명을 apply_reserves(states, op, plays, assignments, t_ms)로 바꾸고 결정으로 남길까요?"
사람: "바꾸고 결정 0022로 남김 (Recommended)"

(AI 해석)
1. 예비 기체는 빠진 기체의 플레이를 **그 플레이의 첫 step(entry)부터** 시작한다. contracts/API.md의 원래 문장("현재 step을 이어받는다")대로면 드론 1이 이미 "귀환" step에 들어가 있어 예비 드론 3도 귀환한다(스파이크에서 확인).
2. 그래서 서명은 `apply_reserves(states, op, plays, assignments, t_ms) -> (states, assignments, Report | None)`. 결정 0017의 이 함수 서명만 바뀐다.
3. `TickOutcome`에 `reports: list[Report]`(그 틱 뒤의 전체 카드)를 더한다. `update_metrics`가 "동시에 떠 있던 경보 최대"를 세려면 새 카드(`new_reports`)만으로는 모자라다.

## 이유
- 사건 3(예비 이어받기, 기체 공백 지표)이 시연의 남겨야 할 장면이다.
- 첫 step부터 시작하는 규칙이 가장 단순하고 플레이 하나만 보면 된다.

## 버린 대안
- 귀환 step 직전 step을 찾아 이어받기: 플레이의 탈출 조건을 거꾸로 찾아야 해서 복잡하다.
- 서명을 그대로 두고 step_id를 비워 step_vehicle이 entry로 채우기: step_id 없음은 직접 조종 중 상태와 겹친다.

## 영향
- contracts/API.md 3·4절, modules/runtime/SPEC.md RT-02, docs/research/09 6절 Part2-11, `contracts/models/frame.py`(TickOutcome).
- 스파이크 `knowledge/spikes/rolecall_engine_proto/engine_proto.py`의 `apply_reserves`가 이 서명이다.
