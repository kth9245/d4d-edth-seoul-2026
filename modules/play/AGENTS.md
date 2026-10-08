# play — 플레이 읽기·검사·펼치기·AI 초안

- 책임: 플레이 JSON을 읽고(`load_play`), 저장 전 검사 4종을 돌리고(`check_play`), step의 행동을 기체 영역별 명령 종류로 펼치고(`expand_action`, `expand_table.json`), AI 초안을 캐시 우선으로 만든다(`draft_play`). 전부 순수 함수. 설계는 `docs/research/09` 3.2.
- 입력: `contracts.models`의 Play·Operation·VehicleSpec / 출력: Play·PlayCheck·CommandKind.
- 공개 API(`__init__.py`): `load_play`, `check_play`, `expand_action`, `draft_play`, `list_templates`.
- 다른 모듈 사용: `from modules.safety import point_in_polygon, return_feasible`(검사 재사용). runtime이 `expand_action`을 부른다.
- 외부 호출은 `draft_play` 하나뿐. `demo/plays/cache/<sha256(prompt)>.json`을 먼저 보고, 캐시 미스면 1회 호출, 실패하면 템플릿 반환. API 키는 `.env`.
- 새 동작은 `/new-action`(= `uv run python scripts/new_action.py play <verb_noun> "<설명>"`)으로 시작한다. SPEC.md의 `예정` 행은 같은 명령을 플래그 없이 돌려 가져간다.
- 담당: 황승주(파트 2B, 결정 0009). 통합 1까지 load_play·check_links·expand_action. 브랜치 `play/<주제>`.
