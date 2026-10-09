---
id: 0014
title: contracts 세부 규칙: 사건 시각은 offset_ms, 작전 시작은 Operation.started_ms 필수, 스파이크 기본값, 다각형 3점 이상, 예시 생성 스크립트, TS 생성기 dict·Literal
status: 확정
decided_by: kth9245
date: 2026-10-09
modules: [contracts, sim, runtime, gateway, cop-ui, demo, infra]
supersedes: null
---
## 결정
2026-10-09 Part1-1(contracts 패키지) 직전, 09 문서 2절에 답이 없는 부분을 AI가 묻고 사람이 고른 것을 그대로 적는다. 질문은 AskUserQuestion 선택지였다.

- 기본값·검증: 사람 "스파이크 기본값 + 다각형 3점 검사 (Recommended)"
- 예시 JSON: 사람 "1,2 둘다 ㄱㄱ 근데 json이 어떤 구조일지는 나하고 얘기" (선택지 1 = 생성 스크립트를 저장소에 둠, 2 = 한 번 만들고 JSON만 커밋)
- TypeScript 생성기: 사람 "dict와 Literal 지원 추가 (Recommended)"
- 시간 기준: 사람 "t_ms는 epoch, 사건은 오프셋 칸 (Recommended)"
- 작전 시작 시각 위치: 사람 "Operation.started_ms + 빈 값 오류 (Recommended)"
- 기록 방식: 사람 "결정 0014에 전부"

(AI 해석)
1. **시간.** 계약의 `t_ms`는 전부 UTC epoch 밀리초다(정책 3, 결정 0012). 예외는 시나리오 사건 하나: `ScenarioEvent.t_ms`를 `offset_ms: int`(작전 시작 후 밀리초)로 바꾼다. 사건이 일어나는 시각은 `scenario.operation.started_ms + offset_ms`다.
2. **작전 시작 시각.** `Operation.started_ms`의 타입은 `int | None` 그대로 둔다(편집기에서 아직 시작 안 한 작전). 시나리오를 읽는 `load_scenario_json`(Part2-20)은 이 값이 비어 있으면 위치를 담은 ValueError를 낸다. 시연 시나리오 값은 2026-10-10 21:00 KST = `1791633600000`.
3. **기본값.** 스파이크 `knowledge/spikes/rolecall_engine_proto/models09.py`의 기본값을 쓴다: `X | None` 칸은 None, `params`·`ui`는 `{}`, 목록 칸(`on`·`choices`·`seen_by`·`log`·TickInputs 목록)은 `[]`, `Metrics` 숫자는 0·`mission_success`는 None, `Play.emergency`는 `EmergencyRules()`, `Play.origin`은 "human", `Decision.operator_id`는 "op1". 09 문서가 스파이크 뒤에 바꾼 것은 09를 따른다: `RunMode`·`Frame.mode`·`TickInputs.mode` 없음, `VehicleState.resume_play_id` 있음.
4. **다각형.** `Polygon.points`는 3개 이상이어야 한다(pydantic `min_length=3`, 어기면 ValidationError).
5. **예시 JSON.** `contracts/examples/`에 `ALL_MODELS`의 모델마다 하나. 만드는 스크립트를 `scripts/`에 커밋하고, 그 스크립트가 만든 JSON도 커밋한다. 모델이 바뀌면 스크립트를 다시 돌린다. 예시가 담을 내용(파일 이름, frame이 보여 줄 시점 등)은 이 결정에 넣지 않고 리드와 따로 정한다.
6. **TypeScript 생성기.** `scripts/gen_contracts.py`가 `dict[str, T]`를 `Record<string, T>`로, 값 타입 없는 dict를 `Record<string, unknown>`로, `Literal`·인라인 enum을 문자열 리터럴 합집합(예: `"human" | "ai_draft"`)으로 낸다. 지금은 각각 `unknown`·`string`이 된다.

## 이유
- 정책 3과 결정 0012가 `t_ms`를 epoch로 정했다. 스파이크는 0부터 세지만 그대로 두면 정책과 어긋난다. 사건 시각만 오프셋으로 두면 시나리오 튜닝(Part2-19)에서 `660000`(11분)처럼 읽고 고칠 수 있다.
- 시작 시각이 없으면 엔진이 사건 시각을 계산할 수 없다. 새 칸을 만들면 같은 뜻의 칸이 두 곳에 생기므로 있는 칸을 쓰고 읽을 때 검사한다.
- 스파이크 기본값은 35분 대본을 끝까지 돌려 확인한 값이다. 09 문서처럼 기본값을 거의 없애면 예시·테스트·런타임 코드가 매번 모든 칸을 채워야 한다.
- 점 2개 이하 다각형은 구역 검사(safety 규칙 2)를 조용히 망가뜨린다. 시나리오 JSON을 읽는 순간 잡는 것이 가장 싸다.
- 예시는 내일 틱 루프(Part2-17)의 임시 함수와 리드의 지도·카드 화면이 그대로 쓴다. 파일끼리 기체·표적 id가 맞아야 하므로 손으로 31개를 쓰지 않고 스크립트 하나에서 만든다.
- 편집기·상황판 코드에서 `step_by_role`·`origin` 같은 칸의 오타를 타입 검사가 잡게 한다.

## 버린 대안
- 사건 시각까지 전부 epoch: 시나리오 파일이 13자리 숫자로 채워져 튜닝이 어렵고 특정 날짜에 묶인다.
- 전부 시작 기준(0부터): 스파이크와 같아 옮기기 쉽지만 정책 3·결정 0012와 충돌한다.
- `Scenario.start_ms` 새 칸: 같은 뜻의 칸이 둘이 된다.
- 09 문서에 적힌 기본값만: 코드가 길어진다.
- 다각형 검증 없음: 잘못된 구역이 시연 중에야 드러난다.
- 예시를 손으로 작성하거나 JSON만 커밋: id가 어긋나거나 모델이 바뀔 때 손으로 고쳐야 한다.
- TS 생성기 그대로: 해당 칸이 `unknown`·`string`이라 화면 코드의 오타를 못 잡는다.

## 영향
- `contracts/models/` 패키지(Part1-1)가 위 규칙으로 만들어진다. 09 문서 2.2의 `ScenarioEvent`(offset_ms)와 `Operation.started_ms` 설명을 고친다.
- sim Part2-5 `apply_events`: `started_ms + offset_ms`로 사건을 판정한다. 스파이크의 `t_ms - dt_ms < ev.t_ms <= t_ms`에서 `ev.t_ms` 자리를 바꾼다.
- sim Part2-20 `load_scenario_json`: `operation.started_ms`가 비면 ValueError.
- gateway Part2-17 틱 루프: 첫 `t_ms`는 `operation.started_ms`. 스파이크가 0을 가정한 곳(`since_ms=0`, `first_seen_ms=0`, 로그의 `t//60000` 분 표시)을 옮길 때 고친다.
- demo Part1-4 시나리오 JSON: `operation.started_ms = 1791633600000`, 사건은 `offset_ms`.
- `scripts/`에 예시 생성 스크립트 추가, `scripts/gen_contracts.py` 수정과 테스트.
