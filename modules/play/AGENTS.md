# play — 플레이 읽기·검사·펼치기·AI 초안

- 책임: 플레이 JSON을 읽고(`load_play`), 플레이 검사(`check_play`)와 작전 검사(`check_operation`)를 돌리고, step의 행동을 기체 영역별 명령 종류로 펼치고(`expand_action`, `expand_table.json`), AI 초안을 캐시 우선으로 만든다(`draft_play`). 전부 순수 함수. 설계는 `docs/research/09` 3.2.
- 입력: `contracts.models`의 Play·Operation·VehicleSpec / 출력: Play·PlayCheck·CommandKind.
- 공개 API(`__init__.py`): `load_play`, `check_play`, `check_operation`, `expand_action`, `draft_play`, `list_templates`. MAVLink 변환은 `modules/mavlink`(리드, 결정 0025). 개념(플레이 = 기체 하나의 워크플로우)과 서명은 contracts/API.md. `expand_action` 원본: `knowledge/spikes/rolecall_engine_proto/port/modules/play/`.
- 다른 모듈 사용: `from modules.safety import point_in_polygon, return_feasible`(검사 재사용). runtime이 `expand_action`을 부른다.
- 외부 호출은 `draft_play` 하나뿐. 프롬프트는 `build_draft_prompt(text, op)`(PLY-12, 본문 `draft_prompt.md`)로만 만든다. `demo/plays/cache/<sha256(prompt)>.json`을 먼저 보고, 캐시 미스면 xAI Grok 1회 호출(결정 0028, 키 `.env`의 `GROK_KEY`), 실패하면 템플릿 반환.
- 새 동작은 `/new-action`(= `uv run python scripts/new_action.py play <verb_noun> "<설명>"`)으로 시작한다. SPEC.md의 `예정` 행은 같은 명령을 플래그 없이 돌려 가져간다.
- 담당: 황승주(파트 2B, 결정 0009). 통합 1까지 load_play·check_links·expand_action. 작업은 자기 worktree에서 main으로(결정 0010·0014).
