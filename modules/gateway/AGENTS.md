# gateway — 파이프라인 실행과 화면 송출

- 책임: 작전 하나를 메모리에 두고(`live.py`의 `Live`) 0.2초마다 `tick`을 배속만큼 돌려 마지막 Frame을 WebSocket `/ws`로 보낸다. 화면 입력은 REST(`contracts/API.md` 5절)로 받아 다음 틱의 `TickInputs`에 넣는다. 시연 시 빌드된 cop-ui를 `/`에서 서빙.
- 다른 모듈은 공개 API로만 호출한다.
- 실행: `uv run uvicorn modules.gateway.app:create_app --factory --port 8000` (환경변수 KDTH_SCENARIO 기본 `demo/scenarios/baengnyeong_night.json`, KDTH_UI_DIST)
- `engine.py`가 아직 없으면 `stub_engine.py`(예시 Frame, 입력 무시)로 돈다. `engine.py`가 있는데 import가 깨지면 스텁으로 넘어가지 않고 오류를 낸다. 스텁은 통합 2 전에 지운다.
- 연결이 끊겨도 서버는 계속 살아 있어야 한다(종료 감시 task로 연결 루프 정리). 틱에서 예외가 나면 ERROR 로그를 남기고 일시정지한다. 레거시 `pipeline.Engine`은 smoke용으로 Part1-14까지 둔다.
- **ROLECALL 전환(2026-10-10):** `docs/research/09` 3.7. 틱 루프 `engine.py`(`tick`, 호출 순서만)·`engine_state.py`(`EngineState`)·GW-02~07 액션은 최동호(파트 2A, 결정 0009)가 쓴다(Part2-17·2-18). 원본: `knowledge/spikes/rolecall_engine_proto/port/modules/gateway/`. `TickOutcome`은 contracts에 있다(결정 0017). REST·WS(`app.py` 재작성, Part1-7)는 리드. `app.py` 끝의 모듈 수준 `app = create_app(...)`은 import 때 시나리오를 읽으므로 Part1-7에서 factory 방식으로 바꾼다.
- 담당: 리드 kth9245(REST·WS), `engine.py`는 최동호. 작업은 자기 worktree에서 main으로(결정 0010·0014).
