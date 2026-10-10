# contracts — 모듈 간 데이터 형식

- 데이터 형식의 정본: `contracts/models/` 패키지(pydantic). `from contracts.models import X`로만 쓴다.
- 규약(개념, 함수 서명, 틱 순서, REST·WS, id·시간): `contracts/API.md`.
- 자동 생성(직접 수정 금지): `contracts/schema/*.json`, `modules/cop-ui/src/contracts.gen.ts` ← `scripts/gen_contracts.py`.
- 예시: `contracts/examples/<모델 snake_case>.json`, 3분 대본 8장면 `contracts/examples/frames/` ← `scripts/gen_examples.py`(세계는 시연 시나리오 JSON, 결정 0035. 레거시 T1-3 예시 5개는 손으로 쓴 것).

| 파일 | 모델 |
|---|---|
| `enums.py` | Domain, VehicleStatus, ActionKind, ConditionKind, CommandKind, CommandSource, BlockReason, ReportKind, TargetKind, EmergencyKind, RunStatus |
| `world.py` | GeoPoint, Polygon, VehicleSpec, VehicleState, Operation |
| `play.py` | Condition, Action, Exit, Choice, Switch, ReportSpec, Step, EmergencyRules, Play, ValidationIssue, PlayCheck |
| `command.py` | Provenance, Command, PassedCommand, Block |
| `events.py` | Target, Report, Decision, Assignment, Injection, DirectControl |
| `frame.py` | Metrics, RunState, Frame, ScenarioEvent, Scenario, TickInputs, TickOutcome |
| `api.py` | DecisionIn, DirectIn, SwitchIn, DraftIn, Accepted, ScenarioInfo |
| `legacy.py` | T1-3 골격(휴면): Detection, Track, Assessment, Response, LegacyFrame |

## 수정 방법
- 리드만 고친다. `contracts/models/`를 커밋하면 `scripts/check.sh`가 스키마와 TS를 다시 만든다. 수동: `uv run python scripts/gen_contracts.py`.
- 모델을 바꾸면 `uv run python scripts/gen_examples.py`로 예시를 다시 만들고 `uv run pytest tests/test_contracts.py`.
