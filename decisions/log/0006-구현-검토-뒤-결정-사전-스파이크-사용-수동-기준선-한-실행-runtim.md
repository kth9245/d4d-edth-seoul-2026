---
id: 0006
title: 구현 검토 뒤 결정: 사전 스파이크 사용, 수동 기준선 한 실행, runtime 단순형, 타일 EOX
status: 확정
decided_by: kth9245
date: 2026-10-09
modules: [play, runtime, sim, safety, contracts, cop-ui, demo]
supersedes: null
---
## 결정
2026-10-09 devil-advocate 검토(docs/research/09 대상) 뒤 AI가 네 가지를 물었고 사람이 선택지로 답한 것을 그대로 적는다.

1. **대회 전 스파이크 코드 사용**: 사람: "쓴다, 밝힌다". `knowledge/spikes/rolecall_engine_proto/`(약 400줄)를 10/10에 함수 단위로 액션에 옮겨 쓴다. 제출 설명과 `demo/BUILT_HERE.md`에 사전 준비분으로 밝힌다.
2. **수동 기준선 숫자**: 사람: "한 실행에서 둘 다 센다". 같은 실행에서 엔진이 낸 명령 수 + 보고 카드 수를 "수동이었다면 필요한 명령 수"로 센다. 수동 모드를 따로 돌리지 않는다. (AI 해석: 결정 0003의 "수동 모드로 돌려 나란히"는 이 세는 방식으로 충족한다.)
3. **runtime 형태**: 사람: "처음부터 단순형". step = 행동 하나(`do`) + 탈출 조건 목록(`on`) + 보고 선택지. step 안에 줄 목록과 줄 해석기를 두지 않는다. 10/8 실행안 PDF의 step 형식과 같다. (AI 해석: 편집기 카드 하나 = step 하나, AI 초안 어휘는 step 단위의 ActionKind·ConditionKind로 유지.)
4. **백령도 위성 타일**: 사람: "EOX Sentinel-2 z8~14". `scripts/fetch_tiles_baengnyeong.sh`로 199장 캐시, 출처 표기(CC BY-NC-SA 4.0). Esri·VWorld는 쓰지 않는다.

## 이유
- 1: 통합 1(10/10 18:00)에 팀원 2가 11개 액션을 6시간에 만들어야 하는데, 스파이크 없이는 성립하지 않는다(검토 결과). 규정은 사전 코드를 밝히면 허용한다.
- 2: 두 번 돌리면 운용자 결정 시각을 대본에 넣는 형식과 `/mode` 경로가 더 필요하다(리드 약 2시간). 한 실행 집계는 정의가 같고 구현이 없다.
- 3: 사람의 선택. 줄 해석기(한 틱에 한 줄, 보고 대기 상태, if_cond 분기)가 검토에서 가장 많이 꼬인 지점이었다. 단순형은 명령이 step 진입 때 한 번만 나가므로 지표 정의가 그대로 선다.
- 4: 10m 해상도라 군사시설이 식별되지 않아 정책 2번에 맞고, 비상업 허용 약관이며, 199장 1.2MB로 캐시 부담이 없다. Esri는 오프라인 캐시가 약관상 제한되고 실제 시설이 보인다.

## 버린 대안
- 스파이크를 참고만 하고 새로 쓰기: 통합 1 위험이 커진다. 저장소에서 빼기: 검사 근거가 문서에만 남는다.
- 수동 모드 재실행: 결정 재생 형식·/mode 경로 추가.
- 줄 해석기(09 원안, 15:00 판단 시점을 두고 단순형으로 내려가는 안): 사람이 처음부터 단순형을 선택.
- Esri World Imagery(선명하지만 약관·시설 노출), VWorld(키 발급·도메인 등록이 오늘 밤 안에 될지 불확실).

## 영향
- contracts: `Line`을 없애고 `Step`에 `do: Action`(kind·params)과 `on: list[Exit]`(cond·go_step)를 둔다. `VehicleState.line_idx` 삭제. `active`·`pending_report_id`·`resume_play_id`는 유지.
- runtime: `step_vehicles`가 step 진입 시 명령 1개를 내고, 매 틱 `on` 조건을 순서대로 평가해 첫 참인 것으로 전이한다. 보고는 step의 `report` 필드로 표현한다.
- play: 검사 4종이 step 단위로 바뀐다(끊긴 go_step, 닿을 수 없는 step, report 없는 approach 경로, 구역 밖 경로점). AI 초안 스키마도 step 단위.
- cop-ui 편집기: 카드 하나 = step 하나(행동 1 + 조건 목록). 줄 목록 UI 없음.
- docs/research/09: 2.2·3.2·3.3·4·10절 수정. 같은 커밋.
- demo: 타일 199장 커밋, ATTRIBUTION.txt, BUILT_HERE에 사전 준비분 기재.
