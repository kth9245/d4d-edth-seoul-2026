# mavlink — 플레이를 MAVLink 기체용 프로그램으로 변환

- 책임: 기체마다 그 기체의 플레이(결정 0015: 기체 하나의 워크플로우)를 QGroundControl `.plan`(임무 파일)과 pymavlink 실행 스크립트로 바꾼다(결정 0011). 실제 기체·SITL로 보내지 않는다.
- 입력: `contracts.models`의 Play·Operation·VehicleSpec / 출력: `dict[기체 id, (plan dict, script str)]`.
- 공개 API(`__init__.py`): `compile_mavlink`.
- 다른 모듈 사용: `from modules.play import expand_action`(행동 → 명령 종류). play 내부 파일은 import하지 않는다.
- 시점: 통합 2(00:00) 뒤, 동결 전. 통합 경로 밖이라 밀리면 가장 먼저 뺀다(결정 0025).
- 새 동작은 `uv run python scripts/new_action.py mavlink <verb_noun> "<설명>"`으로 시작한다. 예정 행 MAV-01은 같은 명령을 플래그 없이 돌려 가져간다.
- 담당: 리드 kth9245(결정 0025). 작업은 자기 worktree에서 main으로(결정 0010·0014).
