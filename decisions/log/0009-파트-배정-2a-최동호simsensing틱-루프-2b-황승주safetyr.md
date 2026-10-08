---
id: 0009
title: 파트 배정: 2A 최동호(sim·sensing·틱 루프), 2B 황승주(safety·runtime·play). 경험 차이 없어 무작위
status: 확정
decided_by: kth9245
date: 2026-10-09
modules: [sim, sensing, gateway, safety, runtime, play, cop-ui]
supersedes: null
---
## 결정
2026-10-09 사람이 말한 것을 그대로 적는다. AI가 docs/research/09 12절 검토 끝에 물은 두 질문에 대한 답이다.

질문 1(React 또는 프런트엔드 코드를 써 본 사람): 사람: "그런거 없는데."
질문 2(pydantic·pytest 포함 Python 작업을 더 많이 해 본 사람): 사람: "이것도 딱히 없음. 그냥 랜덤으로 두명이서 나누셈"

(AI 해석과 실행)
1. 두 사람의 React·Python 경험은 "없음"으로 기록한다(09 11절의 "아직 문서에 없다"를 이 문서가 닫는다).
2. 무작위 추첨(세션에서 `random.Random(secrets.randbits(64))`로 두 이름을 섞음) 결과:
   - **Part 2A = 최동호**: sim·sensing·gateway 틱 루프. 09 6절 번호 Part2-20, 2-17, 2-1~2-6, 2-18(통합 1), 2-19(통합 2).
   - **Part 2B = 황승주**: safety·runtime·play 순수 함수. 09 6절 번호 Part2-7~2-13, 3-7, 3-1, 3-2(통합 1), 2-14~2-16·3-3~3-9(통합 2).
3. React 경험자가 없으므로 편집기(Part3-10~3-14)는 09 9절의 기본값, 즉 **읽기 전용 카드 + "보고 카드 끼워 넣기" 버튼 하나**로 고정한다. 18:00 뒤 편집기 화면 작업은 cop-ui를 이미 만든 리드가 맡고, 황승주는 play 검사 4종(3-3~3-6)·템플릿·`draft_play`(3-8·3-9)까지만 맡는다. 09 6절 "통합 1 배정" 표의 "편집기는 18:00 뒤 2B 사람이 이어서"를 이렇게 고친다.

## 이유
- 사람의 결정: 강점 차이가 없다고 답했고 무작위로 나누라고 했다.
- 09 12절 검토에서 통합 1 구간(10/10 12:00~18:00)은 파트 3 없이 A(5.2h)·B(5.7h)·리드(5.5h)로 가를 때만 18:00에 든다. 두 쪽의 양이 비슷해 경험 차이가 없으면 누가 어느 쪽이든 결과가 같다.
- 편집기를 리드로 옮기는 이유: React를 처음 쓰는 사람이 18:00 뒤 6시간 안에 카드 편집기를 만드는 것은 09 9절이 이미 "파트 3이 막힌다"로 적어 둔 위험이다. 리드는 cop-ui의 map·live·basemap을 이미 만들었다.

## 버린 대안
- 강점 조사 뒤 배정: 조사할 정보가 없다고 답했다.
- 한 사람이 엔진(파트 2) 전부, 다른 사람이 play+편집기(파트 3): 09 12절 검사 1에서 엔진 한 사람 7.4h로 18:00을 넘긴다.
- 황승주가 18:00 뒤 편집기까지: React 경험 없음. 읽기 전용 카드라도 리드가 하는 쪽이 빠르다.

## 영향
- AGENTS.md 모듈 담당 표: sim·sensing·gateway(engine.py) → 최동호(파트 2A), safety·runtime·play → 황승주(파트 2B), cop-ui editor/setup → 리드(읽기 전용 카드). `modules/sim·sensing·gateway/AGENTS.md` 담당 줄도 같이.
- docs/research/09 6절 "통합 1 배정" 표에 이름, Part3-10~3-14 담당을 리드로, 12절 미결 (2) 닫힘.
- 10/10 12:00 첫 액션: 최동호 `new_action.py sim load_scenario_json`, 황승주 `new_action.py safety point_in_polygon`(둘 다 리드가 밤에 `--planned`로 적어 둔 행을 가져가는 것).
