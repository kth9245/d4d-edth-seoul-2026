# runtime — 플레이 실행(step 진행·배정·결정·주입·직접 조종·비상·지표)

- 책임: 틱마다 기체별 현재 (플레이, step)을 진행해 `Command`를 만들고, 보고·결정·이어받기·주입·직접 조종·비상을 처리하며 지표를 센다. 결정 0006 단순형: step = 행동 하나 + 탈출 조건 목록. 설계는 `docs/research/09` 3.3.
- 상태 기계는 `VehicleState`의 play_id/step_id/entered_step/pending_report_id 필드다. 클래스 상속·콜백 없음. 전부 순수 함수, 시간은 `t_ms` 인자로만.
- 입력: VehicleState·VehicleSpec·Play·Target·Decision·Injection·DirectControl / 출력: VehicleState·Command·Report·Assignment·Metrics.
- 공개 API(`__init__.py`): `step_vehicle`, `apply_reserves`, `apply_decision`, `apply_injection`, `apply_direct`, `apply_emergency`, `update_metrics`. 교대 `rotate_patrols`(결정 0037). 발견 카드 선택지 `fleet_choices`, 감시 교대 `relieve_hover`.
- 다른 모듈 사용: `from modules.play import expand_action`. `PassedCommand`는 만들지 않는다(safety만).
- 원본: `knowledge/spikes/rolecall_engine_proto/port/modules/runtime/`를 그대로 복사(SPEC 행 RT-01~09 = 파일 하나씩). 개념·서명은 contracts/API.md.
- 새 동작은 `/new-action`(= `uv run python scripts/new_action.py runtime <verb_noun> "<설명>"`)으로 시작한다. SPEC.md의 `예정` 행은 같은 명령을 플래그 없이 돌려 가져간다.
- 담당: 황승주(파트 2B, 결정 0009). 작업은 자기 worktree에서 main으로(결정 0010·0014).
