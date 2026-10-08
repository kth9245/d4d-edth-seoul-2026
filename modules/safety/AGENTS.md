# safety — 하한선(명령 검사) 규칙 3개

- 책임: 모든 `Command`에 규칙 3개(출처 없음, 작전 구역 밖, 배터리 부족)를 순서대로 적용해 `PassedCommand` 또는 `Block`(대안 포함)을 돌려준다. 예외 허가 없음(결정 0003). 설계는 `docs/research/09` 3.4.
- 입력: Command·VehicleState·VehicleSpec·Operation·plays·injections / 출력: PassedCommand | Block.
- 공개 API(`__init__.py`): `check_command`, `point_in_polygon`, `return_feasible`.
- **`PassedCommand`는 이 모듈의 `check_command`만 만든다.** 다른 곳에서 생성하는 코드가 없음을 grep 테스트로 지킨다.
- 원본: `knowledge/spikes/rolecall_engine_proto/engine_proto.py`의 point_in_polygon·check_command(배터리 대안은 스파이크에 없음, 09 6절 Part2-8 공식).
- 새 동작은 `/new-action`(= `uv run python scripts/new_action.py safety <verb_noun> "<설명>"`)으로 시작한다. SPEC.md의 `예정` 행은 같은 명령을 플래그 없이 돌려 가져간다.
- 담당: 황승주(파트 2B, 결정 0009). 브랜치 `safety/<주제>`.
