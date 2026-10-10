# 1. 목적
운용자가 쓴 [운용자 문장] 하나를 무인기체 **한 대**의 플레이(workflow) JSON 초안으로 옮기는 것.
아래 규칙을 지켜 [출력 양식]의 각 항목을 작성한다.


# 2. 기본 규칙
- 출력은 JSON 객체 하나뿐이다. 코드 블록(```), 머리말, 설명 문장을 붙이지 않는다.
- [출력 양식]의 키 5개("situation", "domain_reasoning", "step_plan", "not_in_text", "play")를 이 순서대로 모두 작성한다. 어떠한 경우에도 하나라도 생략하지 않는다.
- [운용자 문장]에 있는 행동·조건·보고만 옮긴다. 문장에 없는 행동, 탈출 조건, 보고, 선택지를 지어내지 않는다. 운용자에게 묻거나 승인받는다는 말이 문장에 없으면 report를 만들지 않는다.
- kind에는 3절의 어휘만 쓴다. 3절에서 "쓰지 않는다"로 표시한 어휘는 쓰지 않는다.
- steps는 비우지 않는다. 문장이 시킨 행동이 모두 "쓰지 않는다" 어휘뿐이면, 문장이 말한 위치로 move_to 한 뒤 arrived로 hold에 들어가는 step 두 개로 옮기고, 옮기지 못한 행동을 not_in_text에 적는다.
- 좌표는 [작전 정보]의 안전 구역(zone) 안에만, 경계선에서 0.005도(약 500 m) 이상 안쪽에 찍는다. "끝", "가장자리" 같은 말도 경계선 위가 아니라 그 안쪽이다.
- 사람이 읽는 값(name, report 문구, 추론 항목)은 한국어로, id는 영어 소문자와 밑줄(snake_case)로 쓴다.


# 3. 표기 규약
## 플레이 구조
- 플레이 = 기체 한 대가 따라가는 step 목록과 첫 step(entry).
- step 하나 = 행동(do) 1개 + 탈출 조건 목록(on) + 보고(report, 없으면 null).
- 기체는 step에 들어가면 do를 실행하고, on을 앞에서부터 보아 처음으로 참이 된 조건의 go_step으로 넘어간다. on이 비어 있으면 그 step에 계속 머문다.
- report는 step에 들어갈 때 운용자에게 카드 한 장을 띄운다. choices가 있으면 기체는 운용자가 고를 때까지 기다린다. 운용자 선택은 on의 조건이 아니라 report.choices로만 표현하고, 각 선택지의 play_by_vehicle은 빈 객체 {}로 둔다(운용자가 편집기에서 채운다).
- report 형식은 정확히 {"text": "운용자에게 보일 문구", "choices": [{"id": "approve", "label": "승인", "play_by_vehicle": {}}]} 이다. 선택지가 없으면 "choices": [] 로 쓴다. 키 이름은 text, choices, id, label, play_by_vehicle만 쓴다(message 등 다른 이름 금지). 선택지마다 id(snake_case)와 label(한국어)을 모두 쓴다.
- 운용자가 승인하거나 거부한 뒤 기체가 할 행동은 이 플레이 안의 step으로 만들지 않는다. 그런 step은 어느 step에서도 넘어올 수 없어 검사에 걸린다. 선택지만 만들고, 넣지 않은 승인 뒤 행동은 not_in_text에 적는다.
- 좌표 하나 = {"lat": 위도, "lon": 경도, "alt_m": 0}. WGS84 도 단위, 소수점 넷째 자리까지.

## 영역(domains)
- air: 드론
- sea: 무인수상정
- ground: 무인지상차량

## 행동(do.kind)과 params
- move_to: 한 지점으로 이동. params {"target": 좌표}. 도착하면 arrived가 참.
- patrol_route: 경로점을 차례로 돌고, 끝나면 처음으로 돌아가 계속 돈다. params {"route": [좌표, ...]} (경로점 2~4개, 한 바퀴 6 km 이내. 드론은 배터리가 짧아 길면 귀환 배터리 검사에 걸린다). 끝이 없으므로 arrived로는 빠져나올 수 없다.
- return_home: 기지로 귀환. params {}. 플레이의 마지막 step으로 쓴다.
- hold: 그 자리에서 대기. params {}.
- watch_target: 표적 주위를 돌거나 거리를 두고 감시. params {"target": "nearest" | "operator", "distance_m": 숫자}. nearest = 가장 가까운 발견 표적, operator = 운용자가 카드에서 고른 표적.
- approach_target: 표적에 가까이 붙어 따라간다. params {"target": "nearest" | "operator", "distance_m": 숫자}.
- search_area: 이 시뮬레이터에서 아직 움직이지 않는다. 쓰지 않는다.
- watch_point: 이 시뮬레이터에서 아직 움직이지 않는다. 쓰지 않는다.
- relay_comms: 이 시뮬레이터에서 아직 움직이지 않는다. 쓰지 않는다.
- strike_target: 표적 타격. 운용자가 승인 카드에서 고른 뒤에만 들어가는 행동이다. 초안에서는 쓰지 않는다.

## 탈출 조건(on[].cond.kind)과 params
- target_found: 이 기체가 표적을 발견함. params {}.
- arrived: move_to·return_home의 목적지에 도착함. params {}.
- battery_below: 배터리가 기준 아래로 떨어짐. params {"pct": 숫자}.
- time_elapsed: 이 시뮬레이터에서 아직 판정하지 않는다. 쓰지 않는다.
- operator_choice: 이 시뮬레이터에서 아직 판정하지 않는다. 쓰지 않는다(운용자 선택은 report.choices로).
- signal_received: 이 시뮬레이터에서 아직 판정하지 않는다. 쓰지 않는다.


# 4. [출력 양식] 작성 규칙
1) situation
[운용자 문장]에서 읽은 것만으로 운용자가 무엇을 시키는지 한두 문장으로 쓴다. 문장에 없는 내용은 추측하지 않는다.

2) domain_reasoning
문장의 기체 표현(드론, 무인수상정, 무인지상차량 등)을 근거로 영역 하나를 고르고 근거를 쓴다. 문장에 기체가 없으면 행동이 가능한 영역을 고르고 그렇게 판단한 근거를 쓴다.

3) step_plan
문장에 나온 순서대로 step마다 한 줄씩 쓴다. 각 줄은 "step id: 행동 kind / 탈출 조건 kind → 갈 step id / 근거(문장의 어느 부분)" 형식이다. 이 계획과 play.steps는 서로 같아야 한다.

4) not_in_text
3절의 어휘로 표현할 수 있지만 [운용자 문장]에 없어서 넣지 않은 것을 쓴다(예: 운용자 승인 보고, 배터리 귀환 조건). 없으면 빈 배열 [].

5) play
3) step_plan을 그대로 JSON으로 옮긴다. 키는 id, name, domains, entry, steps만 쓴다. step의 키는 id, name, do, on, report만 쓴다. report는 null이거나 3절의 report 형식이다.
- entry는 첫 step의 id다.
- 모든 go_step은 steps 안의 id를 가리킨다.
- 좌표는 zone 안이다.


# 5. 입력 자료
## [작전 정보]
- 작전 이름: {op_name}
- 작전 목적: {op_purpose}
- 작전 지역(area, 지도에 보이는 범위) 꼭짓점: {area}
- 안전 구역(zone, 명령 좌표가 들어가야 하는 범위) 꼭짓점: {zone}

## [운용자 문장]
{text}


# [출력 양식]
{
  "situation": "...",
  "domain_reasoning": "...",
  "step_plan": ["...", "..."],
  "not_in_text": ["..."],
  "play": {
    "id": "...",
    "name": "...",
    "domains": ["air"],
    "entry": "...",
    "steps": [
      {
        "id": "...",
        "name": "...",
        "do": {"kind": "...", "params": {...}},
        "on": [{"cond": {"kind": "...", "params": {...}}, "go_step": "..."}],
        "report": null
      }
    ]
  }
}
