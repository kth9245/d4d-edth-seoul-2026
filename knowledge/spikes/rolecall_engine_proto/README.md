# ROLECALL 엔진 스파이크 (2026-10-09, 대회 전)

docs/research/09 2절 형식이 실제로 시뮬레이션되는지 확인한 일회용 코드. **대회 전 사전 준비분이므로 제출 설명에 밝힌다.**
모듈 코드가 아니다. 10/10에 `new_action.py`로 만든 액션에 함수 단위로 옮겨 쓴다.

- `models09.py` — 09 2절을 pydantic으로 옮긴 것. 검토·결정 0006 반영: `VehicleState.active`·`pending_report_id`·`entered_step`, 단순형 `Step(do, on, report)`(줄 목록 없음), `ActionKind` 9개.
- `step_vehicle.py` — runtime step 진행 액션 뼈대(결정 0006 단순형: step 진입 때 명령·카드 한 번, 그 뒤 `on` 조건으로 전이). 51줄(80줄 제한 안).
- `engine_proto.py` — sim 이동(move·follow_route·orbit·keep_distance·return_home)·사건 적용·센서·safety 규칙 3개·이어받기·지표를 한 파일에 넣고 백령도 사건 대본(표적 출현, 결정, 배터리 귀환·이어받기, 구역 밖 직접 조종 차단)을 35분 돌린다.

실행: `uv run python knowledge/spikes/rolecall_engine_proto/engine_proto.py` (같은 디렉터리의 models09를 import하므로 그 디렉터리에서 실행하거나 sys.path에 추가).
`--no-active`를 주면 09 원문(현재 명령 필드 없음)대로 돌아가며, 드론이 첫 틱 뒤 멈추는 것을 재현한다.

결과(2026-10-09, 단순형): 10,500틱(200ms × 35분) 0.54초, 틱당 0.05ms. 보고 카드 1, 결정 1로 역할 4개 전이, 19분 배터리 귀환 뒤 드론 3 이어받기, 31분 구역 밖 차단. 예비 드론의 순찰 경로(routeB)가 40분 기체로는 귀환 배터리 부족으로 차단되는데, 이는 시나리오 데이터 조정 대상이자 play `check_play`의 귀환 배터리 검사가 저장 전에 잡아야 할 사례다.
