---
id: 0052
title: play를 role로 이름 변경: 코드·API·계약·데이터·화면 전부, 화면 표기는 Role
status: 확정
decided_by: kth9245
date: 2026-10-10
modules: [contracts, gateway, cop-ui, demo, play, runtime, safety, sim, mavlink]
supersedes: null
---
## 결정
사람(kth9245): "그 rolecall이 이름이니깐 play가 아니라 role로 이름 변경 하자". 범위를 묻자 "코드·API까지 전부", 화면 표기를 묻자 "Role (Recommended)".

AI 해석:
1. 개념 이름 play(기체 하나의 행동 흐름)를 role로 바꾼다. 계약 모델(Play→Role, PlayCheck→RoleCheck 등), REST 경로(/plays→/roles), JSON 키(plays→roles, play_id→role_id, play_by_vehicle→role_by_vehicle, rotation_plays→rotation_roles 등), 모듈 이름(modules/play→modules/role), 파일·함수·변수·테스트 이름, 시연 데이터(demo/plays→demo/roles, 시나리오 JSON)를 모두 바꾼다.
2. 화면 글자 "플레이"는 "Role"로 쓴다(조사도 맞춘다: Role을·Role이·Role은·Role과).
3. 기록은 바꾸지 않는다: decisions/log, knowledge, docs/research·docs/superpowers, tasks 기록. 자동 생성 파일(contracts/schema, contracts.gen.ts, 예시)은 생성기로 다시 만든다.
4. 바꾸기는 저장소에 넣는 변환 스크립트(scripts/rename_play_role.py) 하나로 한 번에 한다. 팀원은 rebase 뒤 자기 작업에 같은 스크립트를 돌려 맞춘다.
5. AI 초안 캐시는 요청 문장 해시로 찾으므로, 바꾼 뒤 같은 데모 문장이 같은 초안을 찾도록 캐시 파일을 새 해시 이름으로 옮긴다(정책 1: 시연 경로에서 외부 호출 금지).
6. 바꾸지 않는 것: "display"·"replay" 같은 다른 단어, 외부 API 형식의 "role": "user".

## 이유
- 제품 이름이 ROLECALL이라 핵심 개념 이름을 Role로 맞춘다(사람 요청).
- 화면만 바꾸면 코드·API의 play와 화면의 Role이 어긋난다. 사람이 코드까지 전부를 골랐다.

## 버린 대안
- 화면 글자만 바꾸기: 위험은 작지만 사람이 고르지 않음.
- 표기 "역할"·"롤": 사람이 Role을 고름.

## 영향
- 모든 모듈(약 3,000곳, 이름에 play가 든 파일 77개). 황승주(play·runtime·safety), 최동호(sim·engine.py) 모듈을 고치므로 반영 전에 알리고, 진행 중인 작업을 먼저 push하게 한다. push 못 한 작업은 rebase 뒤 변환 스크립트를 돌려 맞춘다.
- 시나리오 JSON 형식과 WS Frame 필드 이름이 바뀐다(contracts/API.md 갱신).
- 이 결정 이후 새 결정·문서는 Role 이름을 쓴다.
