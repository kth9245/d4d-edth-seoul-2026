# sensing — 센서 입력 정규화

- 책임: 센서별 원시 탐지를 공통 Detection으로 정리하고 잘못된 값을 걸러낸다.
- 입력/출력: `list[Detection]` → `list[Detection]`
- 공개 API: `normalize`
- 실제 센서·보드(SC2) 연동 어댑터는 이 모듈의 액션으로 추가한다.
- **ROLECALL 전환(2026-10-10):** 새 역할은 `docs/research/09` 3.6: 기체 센서 범위 안 표적을 `Target.seen_by`에 표시(`observe`). 레거시 `normalize`·`drop_invalid_detections`는 파이프라인에서만 빼고 지우지 않는다.
- 담당: 최동호(파트 2A, 결정 0009). 브랜치 `sensing/<주제>`.
