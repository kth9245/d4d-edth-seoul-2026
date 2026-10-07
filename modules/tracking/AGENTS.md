# tracking — 다중 표적 추적

- 책임: 매 프레임 탐지(Detection)를 받아 표적(Track) 목록을 갱신한다.
- 순서(pipeline.update): predict → associate → update → initiate → delete. (지식 카드 stone-soup-tracker-components)
- 입력: 이전 `list[Track]`, 이번 `list[Detection]`, `t_ms` / 출력: `list[Track]`
- 공개 API: `update`
- 상태(이전 표적)는 호출자(gateway)가 보관한다. 이 모듈은 상태를 저장하지 않는다.
- 담당: 팀원 3. 브랜치 `tracking/<주제>`.
