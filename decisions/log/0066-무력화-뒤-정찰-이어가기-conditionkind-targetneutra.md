---
id: 0066
title: 무력화 뒤 정찰 이어가기: ConditionKind target_neutralized와 VehicleState 순찰 위치 기억(patrol_step_id, patrol_idx)
status: 확정
decided_by: 최동호
date: 2026-10-10
modules: [contracts, runtime, demo]
supersedes: null
---
## 결정

1. `ConditionKind`에 `target_neutralized`를 더한다. 내 표적(`target_id`)이 무력화되었으면(`neutralized_ms`가 있으면) 참이다.
2. `VehicleState`에 `patrol_step_id: str | None = None`과 `patrol_idx: int = 0`을 더한다. `patrol_route` 단계를 출구로 떠날 때 그 단계 id와 그때 `waypoint_idx`를 적고, 같은 단계로 다시 들어올 때 `waypoint_idx`를 0이 아니라 적어 둔 값으로 시작한 뒤 지운다. 다른 단계로 처음 들어올 때는 지금처럼 0이다.
3. 공격 작전(`baengnyeong_strike`)의 정찰 순찰 Role은 발견 단계에서 `target_neutralized`로 새 `after_strike` 단계로 가서 카드를 올린다. 선택지는 "더 정찰"(순찰을 떠난 곳부터 이어서)과 "수상정으로 복귀"(`go_home`)다.

## 이유

무력화된 거점 위에 정찰 드론이 계속 머물러 다른 거점을 찾지 못한다. 운용자가 무력화 직후 더 정찰할지 복귀할지 고르게 하려면 무력화된 순간을 알려 주는 조건이 필요하다. "더 정찰"이 구간 경로를 처음 점부터 다시 도는 것은 맞지 않아 떠난 위치를 기억해야 한다. 최동호 요청(2026-10-10).

## 버린 대안

- 타격 승인 선택지에 순찰 복귀 출구를 달기: 데이터만으로 되지만 정찰이 거점을 보지 않은 채 무력화 전에 떠난다.
- 재진입 때 경로에서 가장 가까운 점부터 시작하기: 처음 시작도 바뀌고(수상정 서쪽 출발점에서 가장 가까운 점이 경로 중간이 됨) 왕복 경로의 같은 좌표를 구별할 수 없다.

## 영향

contracts(`ConditionKind`, `VehicleState`, 생성 파일 schema·examples·contracts.gen.ts), runtime(`step_vehicle`, `enter_step`; 황승주 영역이라 알려야 한다), demo(`baengnyeong_strike`의 정찰 Role). 야간·24시간 작전에서 순찰을 떠났다가 같은 단계로 되돌아오는 Role이 있으면 처음이 아니라 이어서 간다(전체 테스트로 확인). 새 필드는 기본값이 있어 읽는 쪽은 깨지지 않는다.
