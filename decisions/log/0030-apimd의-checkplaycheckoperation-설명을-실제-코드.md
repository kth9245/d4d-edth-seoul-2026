---
id: 0030
title: API.md의 check_play·check_operation 설명을 실제 코드에 맞추고 POST /plays 동작을 적음(함수는 그대로)
status: 확정
decided_by: kth9245
date: 2026-10-10
modules: [contracts, play, gateway, cop-ui]
supersedes: null
---
## 결정
2026-10-10 11시, Part3-11(편집기 저장) 리뷰 뒤. AI가 "함수는 그대로 두고 API.md 문구를 실제 동작에 맞추자(58행과 5절 POST /plays)"고 제안하자 사람이 답했다.

사람: "ㅇㅇ 그렇게 하셈"

(AI 해석, 반영 내용)
1. `contracts/API.md` 3절 play 공개 API 설명을 코드대로 고친다.
   - `check_play(play, op, specs)`: 플레이 하나만 본다. step 연결, 보고 지점, 작전 구역, 이 플레이를 assign·switches·reserve로 받는 기체의 영역·능력, 귀환 배터리. 다른 플레이를 받지 않으므로 선택지가 가리키는 플레이의 존재는 보지 않는다.
   - `check_operation(op, plays, specs)`: 작전 전체. assign·reserve·switches·보고 선택지가 만드는 (기체, 플레이) 쌍마다 check_play, 없는 플레이를 가리키면 `missing_play`. issue 메시지 앞에 `[플레이 id] `가 붙는다.
2. 5절에 `POST /plays`·`POST /plays/check` 동작을 적는다. 검사 = check_play + 이 저장으로 새로 생긴 check_operation 오류(gateway GW-08 `check_saved_play`). `POST /plays`는 통과할 때만 gateway 메모리에 저장하고 실행을 작전 시작 직전(일시정지)으로 되돌린다(Part3-11 작업 중 결정, 리드 답 "저장하고 오퍼레이션 시작을 해야 실행되는거 아님?"). 파일에는 쓰지 않는다. 실패면 아무것도 바꾸지 않고, 응답은 둘 다 항상 `PlayCheck`.
3. play 모듈 함수(황승주)는 바꾸지 않는다.

## 이유
- 기존 58행은 두 함수의 역할을 거의 반대로 적었다(check_play에 "play_by_vehicle의 플레이 존재", check_operation에 "보고 지점·배터리·구역"). 정본 문서가 틀리면 Part3-12·3-13과 엔진 쪽이 잘못된 함수를 부른다.
- check_play는 플레이 목록을 받지 않아 선택지 대상 존재를 원리상 검사할 수 없다. 넣으려면 공개 함수 서명을 바꿔야 하고 황승주 테스트와 호출처(GW-08)가 같이 바뀐다. 그 검사는 check_operation이 이미 한다.
- 저장 경로는 GW-08이 두 함수를 합쳐 이미 막고 있다(main 반영 11:09).

## 버린 대안
- check_play에 plays 인자를 추가해 선택지 대상까지 검사: 서명 변경이 통합 중에 황승주 모듈·테스트·GW-08을 함께 흔든다. 같은 검사가 check_operation에 이미 있다.
- 문구를 그대로 두기: 정본이 코드와 달라 다음 작업자가 잘못 부른다.

## 영향
- `contracts/API.md` 3절 play 줄, 5절 표 아래 POST /plays 설명.
- 황승주: 코드 변경 없음. check_play·check_operation의 서명이나 issue 메시지 형식(`[플레이 id] ` 접두어)을 바꾸면 `modules/gateway/tests/test_check_saved_play.py`도 볼 것(GW-08이 접두어를 떼고 같은 오류를 비교한다). 채팅으로 알린다.
- cop-ui 편집기(Part3-12·3-13)는 저장에 `POST /plays`를 쓴다.
