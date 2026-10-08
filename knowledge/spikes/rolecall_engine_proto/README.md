# ROLECALL 엔진 스파이크 (2026-10-09, 대회 전)

docs/research/09 2절 형식이 실제로 시뮬레이션되는지 확인한 일회용 코드. **대회 전 사전 준비분이므로 제출 설명에 밝힌다.**
모듈 코드가 아니다. 10/10에 `new_action.py`로 만든 액션에 함수 단위로 옮겨 쓴다.

- `models09.py` — 09 2절을 pydantic으로 그대로 옮긴 것 + 검토에서 추가된 필드 2개(`VehicleState.active`, `pending_report_id`), `Line.params: dict[str, Any]`.
- `step_vehicle.py` — runtime "한 줄 진행" 액션 뼈대. 58줄(80줄 제한 안).
- `engine_proto.py` — sim 이동(move·follow_route·orbit·keep_distance·return_home)·사건 적용·센서·safety 규칙 3개·이어받기·지표를 한 파일에 넣고 백령도 사건 대본(표적 출현, 결정, 배터리 귀환·이어받기, 구역 밖 직접 조종 차단)을 35분 돌린다.

실행: `uv run python knowledge/spikes/rolecall_engine_proto/engine_proto.py` (같은 디렉터리의 models09를 import하므로 그 디렉터리에서 실행하거나 sys.path에 추가).
`--no-active`를 주면 09 원문(현재 명령 필드 없음)대로 돌아가며, 드론이 첫 틱 뒤 멈추는 것을 재현한다.

결과(2026-10-09): 10,500틱(200ms × 35분) 0.53초, 틱당 0.05ms. 보고 카드 1, 결정 1로 역할 4개 전이, 19분 배터리 귀환 뒤 드론 3 이어받기, 31분 구역 밖 차단 + 대안 적용.
