---
id: 0025
title: MAVLink 변환(compile_mavlink)은 리드 담당, 새 모듈 modules/mavlink로 분리, 통합 2 뒤
status: 확정
decided_by: kth9245
date: 2026-10-10
modules: [mavlink, play, infra]
supersedes: null
---
## 결정
2026-10-10 0시 반, 역할 분담을 설명받은 뒤 사람이 말한 것을 그대로 적는다.

사람: "흠 황승주쪽에서 워크플로우에서 실행파일로 바꾸는 컴파일 쪽만 내쪽으로 옮겨올 수 있나"
AI가 위치·시점을 물음 → 사람: 위치 "새 모듈로 분리(리드 소유)", 시점 "계획대로 통합 2 뒤 (Recommended)", 이어서 "ㅇㅇ 나한테 바꾸고"

(AI 해석)
1. 결정 0011의 플레이 → MAVLink 프로그램 변환(QGC `.plan` + pymavlink 스크립트)은 리드 kth9245가 맡는다. 결정 0011의 내용(무엇을 만드는가)은 그대로이고, 위치와 담당만 바뀐다.
2. 코드는 play 모듈이 아니라 새 모듈 `modules/mavlink`(SPEC 접두어 MAV)에 둔다. 액션 `compile_mavlink`(MAV-01). play의 PLY-10 예정 행은 지운다.
3. play는 공개 API(`from modules.play import expand_action`)로만 쓴다.
4. 시점은 통합 2(00:00) 뒤, 동결(06:00) 전. 통합 경로 밖이라 밀리면 가장 먼저 뺀다.

## 이유
- 황승주 담당(safety·runtime·play)이 액션 수가 가장 많다.
- 두 층 구조(결정 0015)에서 기체 하나 = 플레이 하나 = 임무 파일 하나라 변환이 독립적이다.
- 새 모듈로 나누면 소유가 뚜렷하고 play 파일과 겹치지 않는다.

## 버린 대안
- play 모듈에 두고 담당만 리드: 구조 변경은 없지만 남의 모듈 안에서 일하게 된다.
- 오늘 밤 구현: 수면이 줄고 통합 경로와 무관하다.

## 영향
- `modules/mavlink/`(새 모듈), `modules/play/SPEC.md`(PLY-10 삭제), AGENTS.md 담당 표, contracts/API.md, 09 문서 6절 Part3-15, `modules/play/AGENTS.md` 공개 API.
