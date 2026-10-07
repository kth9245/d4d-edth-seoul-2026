# sensing — 센서 입력 정규화

- 책임: 센서별 원시 탐지를 공통 Detection으로 정리하고 잘못된 값을 걸러낸다.
- 입력/출력: `list[Detection]` → `list[Detection]`
- 공개 API: `normalize`
- 실제 센서·보드(SC2) 연동 어댑터는 이 모듈의 액션으로 추가한다.
- 담당: 팀원 2. 브랜치 `sensing/<주제>`.
