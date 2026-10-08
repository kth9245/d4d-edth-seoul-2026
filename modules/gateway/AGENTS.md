# gateway — 파이프라인 실행과 화면 송출

- 책임: 시나리오를 시간 순서로 돌리며 sim → sensing → tracking → assess → respond를 호출해 Frame을 만들고 WebSocket `/ws`로 보낸다. 시연 시 빌드된 cop-ui를 `/`에서 서빙.
- 다른 모듈은 공개 API로만 호출한다.
- 실행: `uv run uvicorn modules.gateway.app:app --port 8000` (환경변수 KDTH_SCENARIO, KDTH_UI_DIST)
- 연결이 끊겨도 서버는 계속 살아 있어야 한다(연결마다 독립 Engine, 종료 감시 task로 루프 정리).
- **ROLECALL 전환(2026-10-10):** `docs/research/09` 3.7. 틱 루프 `engine.py`(`tick`, `EngineState`, `TickOutcome`)는 최동호(파트 2A, 결정 0009)가 쓴다(Part2-17·2-18). REST·WS(`app.py` 재작성, Part1-7)는 리드. `app.py` 끝의 모듈 수준 `app = create_app(...)`은 import 때 시나리오를 읽으므로 Part1-7에서 factory 방식으로 바꾼다.
- 담당: 리드 kth9245(REST·WS), `engine.py`는 최동호. 브랜치 `gateway/<주제>`.
