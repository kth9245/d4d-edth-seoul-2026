# sim — 가상 시나리오·센서 데이터 생성

- 책임: 시나리오 YAML을 읽어 시각 t_ms의 가상 탐지(Detection) 목록을 만든다. 실제 데이터 금지(가상만).
- 입력: `demo/scenarios/*.yaml` (형식: `modules/sim/types.py`의 Scenario)
- 출력: `list[contracts.models.Detection]`
- 공개 API(`__init__.py`): `load_scenario`, `simulate`, `Scenario`
- 같은 seed와 t_ms면 항상 같은 결과(재현 가능)여야 한다.
- 담당: 팀원 2. 브랜치 `sim/<주제>`.
