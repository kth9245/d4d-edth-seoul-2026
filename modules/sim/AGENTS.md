# sim — 가상 시나리오·센서 데이터 생성

- 책임: 시나리오 YAML을 읽어 시각 t_ms의 가상 탐지(Detection) 목록을 만든다. 실제 데이터 금지(가상만).
- 입력: `demo/scenarios/*.yaml` (형식: `modules/sim/types.py`의 Scenario)
- 출력: `list[contracts.models.Detection]`
- 공개 API(`__init__.py`): `load_scenario`, `simulate`, `Scenario`
- 같은 seed와 t_ms면 항상 같은 결과(재현 가능)여야 한다.
- **ROLECALL 전환(2026-10-10):** 위 설명은 T1-3 레거시(YAML → Detection)다. 새 역할은 `docs/research/09` 3.5: `PassedCommand`대로 기체를 움직이고 사건 대본을 재생한다. 새 액션(`load_scenario_json`·`advance`·`apply_events`·`move_straight`·`follow_route`·`orbit_or_keep`)은 **추가**하고, 레거시 `load_scenario`·`simulate`·`Scenario`는 통합 1(Part1-14)까지 지우지 않는다(smoke가 깨진다).
- 담당: 최동호(파트 2A, 결정 0009). 브랜치 `sim/<주제>`.
