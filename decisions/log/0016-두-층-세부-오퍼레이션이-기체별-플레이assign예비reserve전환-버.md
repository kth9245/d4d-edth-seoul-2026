---
id: 0016
title: 두 층 세부: 오퍼레이션이 기체별 플레이(assign)·예비(reserve)·전환 버튼(switches), 플레이 선택지가 기체별 새 플레이를 가리킴, 추적 대상은 nearest·운용자 선택·고정, 시연은 가능성을 보이는 수준
status: 확정
decided_by: kth9245
date: 2026-10-09
modules: [contracts, play, runtime, gateway, cop-ui, demo]
supersedes: null
---
## 결정
2026-10-09 자정 무렵 결정 0015(두 층 구조)의 세부를 AI가 AskUserQuestion으로 묻고 사람이 답한 것을 그대로 적는다.

- 기체와 플레이: 사람 "기체마다 직접 플레이" (메모: "그니깐 플레이들을 만들어놓고 그걸 오퍼레이션으로 구성하게 하면 됨")
- 협동 규칙 위치: 사람 "플레이 안 선택지가 직접 가리킴"
- 작전 전체 전환: 사람 "미리 정의한 전환 버튼 (Recommended)"
- 추적 대상: 사람 "대상을 정하는게 워크플로우에 있으면 되잖아 일단 지금 논리적으로 완벽한걸 보여주는게 아니라 이런게 가능하다는걸 보여줄거임", 이어서 "선택지를 주면 되지 nearest, 사용자가 선택, 고정 이런느낌으로"
- 이어받기: 사람 "기체별 예비 한 줄로 살림 (Recommended)" (메모: "이런 논리적으로 완벽한게 필요없다니깐.")
- 일부 전환 뒤: 사람 "끝냄, 되돌리려면 다시 전환 (Recommended)"
- 전환 때 열린 보고 카드: 사람 "이건 또 뭔소리지" → 처리하지 않는다(시연 대본에서 생기지 않음).

(AI 해석)
1. **시연 기준.** 시연은 "이런 게 가능하다"를 보여 주는 수준이다. 모든 경우를 논리적으로 처리하는 것은 목표가 아니다. 대본에서 생기지 않는 예외 경우는 가장 단순하게 두고 따로 처리하지 않는다.
2. **오퍼레이션(작전)** = 임무 틀(`zone`·`vehicle_ids`·`started_ms`) + `assign: dict[기체 id, 플레이 id]`(시작 플레이) + `reserve: dict[기체 id, list[기체 id]]`(그 기체가 빠지면 이어받을 예비 순서, 결정 0005 "배정은 고정"의 새 자리) + `switches: list[Switch]`(운용자가 누르는 전체 전환 버튼). `Switch` = {id, label, `play_by_vehicle: dict[기체 id, 플레이 id]`}.
3. **플레이** = 기체 한 대의 워크플로우: id, name, 쓸 수 있는 영역(domains), steps, 첫 step(`entry: str`), emergency, origin, approved, template. 역할(`Role`)은 없어진다. 보고 카드의 선택지 `Choice` = {id, label, `play_by_vehicle: dict[기체 id, 플레이 id]`}. 선택지가 다른 기체 id를 직접 가리키므로 그 플레이는 그 기체들이 있는 작전에서 쓰인다(사람이 알고 고름).
4. **전환의 세 경로.** (가) 보고 카드 선택지를 누르면 `play_by_vehicle`의 기체들이 각자 새 플레이의 첫 step에서 시작한다. 누른 것 자체가 운용자 결정이므로 바로 적용한다(사건 2: 한 번 눌러 기체 4대 이동). (나) 전환 버튼(`Operation.switches`)과 (다) 기체 하나를 다른 플레이로 바꾸는 일부 전환은 바뀌는 배정을 먼저 보여 주고 승인해야 적용한다(결정 0015, 하한선 규칙 1, 사건 4). 어느 경로든 원래 플레이는 끝나고 자동 복귀는 없다. 복귀 칸(`resume_*`)은 직접 조종(사건 6) 뒤 복귀에만 쓴다.
5. **추적 대상**: 표적이 필요한 행동(watch_target, approach_target)의 `params.target`에 세 값 중 하나를 적는다. `"nearest"` = step에 들어갈 때 그 기체에서 가장 가까운 표적, `"operator"` = step에 들어갈 때 표적 목록을 선택지로 단 카드를 띄우고 운용자가 고를 때까지 기다림, 그 밖의 문자열 = 고정 표적 id. 정해진 표적은 `VehicleState.target_id`에 둔다.
6. **이어받기**: 기체가 빠지면(returning·lost·maintenance) `reserve`의 첫 가용 기체가 그 기체의 플레이와 현재 step을 이어받는다. 지표 이름은 역할이 없어졌으므로 `vehicle_gap_ms`(기체 공백 시간), 카드 종류는 `vehicle_gap`으로 바꾼다. 뜻은 결정 0003 지표 3 그대로.

## 이유
- 사람이 "플레이를 만들어 놓고 오퍼레이션으로 구성"하는 흐름을 원했다.
- 협동을 선택지에 바로 적으면 편집기에서 한 카드만 보고 결과를 알 수 있다.
- 전환 버튼과 선택지가 같은 형식(`play_by_vehicle`)이라 runtime 처리 함수가 하나로 끝난다.
- 예비 한 줄로 사건 3과 결정 0003의 공백 지표를 살린다.
- 시연 목적은 가능성 증명이므로 단순한 쪽이 맞다.

## 버린 대안
- 오퍼레이션의 역할(이름·기체 순서·플레이): 사람이 기체 직접 배정을 골랐다.
- 협동 규칙을 오퍼레이션에 두고 플레이는 선택지 id만: 플레이 재사용에 유리하지만 사람이 플레이 안에 직접 적는 쪽을 골랐다.
- 다른 오퍼레이션 파일로 통째 교체: 작전 구역이 바뀌면 하한선 규칙 2와 부딪친다.
- 이어받기·공백 지표 삭제: 결정 0003을 바꿔야 한다.
- 일부 전환 뒤 자동 복귀: 플레이의 "끝" 조건을 새로 정해야 한다.

## 영향
- contracts: `Role` 삭제, `Play.entry: str`, `Play.domains`, `Choice.play_by_vehicle`, `Operation.assign·reserve·switches`, `Switch` 추가, `VehicleState.role_id` 삭제·`target_id` 추가, `Assignment`는 (기체, 플레이, 이유)로, `ReportKind.role_gap`→`vehicle_gap`, `Metrics.role_gap_ms`→`vehicle_gap_ms`. 09 문서 2절·3절·6절을 이 결정과 0015에 맞춘다.
- runtime: `assign_roles` → 예비 이어받기 함수, `apply_decision`은 `play_by_vehicle` 적용(전환 버튼·일부 전환 승인도 같은 함수), step 진입 때 `target` 해석.
- play: 검사가 플레이 검사(step 연결·`play_by_vehicle`의 플레이 존재)와 작전 검사로 나뉜다.
- demo: 해안 경계 템플릿(역할 4개)을 기체별 플레이 여러 개(순찰 A, 보고 대기, 감시, 접근, 상륙 지점, 순찰 B, 대기, 귀환, 고속 보트 추적)와 오퍼레이션 하나로 다시 쓴다.
