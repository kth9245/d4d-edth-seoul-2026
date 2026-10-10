---
id: 0035
title: 시연 시나리오 원본은 손으로 고친 baengnyeong_night.json: example_world.py가 이 JSON을 읽고 gen_examples.py는 demo/를 쓰지 않는다
status: 확정
decided_by: kth9245
date: 2026-10-10
modules: [demo, contracts, infra]
supersedes: null
---
## 결정

2026-10-10 14:20 Part1-20 세션에서 AI가 묻고 사람이 답했다.

- 질문: 시연 시나리오의 원본을 어느 쪽으로 할까요? (JSON이 원본 / example_world.py가 원본(Part2-19.1이 옮김) / example_world.py가 원본(이 세션이 옮김))
- 사람: "JSON이 원본 (추천)"

(AI 해석)
1. 시연 시나리오의 원본은 `demo/scenarios/baengnyeong_night.json`과 `demo/plays/*.json`이다. 숫자·플레이 수정은 이 JSON을 직접 고친다(Part1-19·Part2-19가 이미 이렇게 했다).
2. `scripts/example_world.py`는 이 JSON을 읽어 `SCENARIO`·`OPERATION`·`SPECS`·`PLAYS`·`ZONE` 등 예시 세계를 만든다. 코드로 시나리오를 따로 정의하지 않는다.
3. `scripts/gen_examples.py`는 `contracts/examples/`만 쓰고 `demo/`는 쓰지 않는다. `contracts/examples/scenario.json`은 시연 시나리오와 같아진다.
4. 예시 장면(`scripts/example_scenes.py`)은 손 계산 그대로이고, 시연 시나리오와 같은 플레이 id를 쓴다.

## 이유
- Part1-19·Part2-19(최동호)가 JSON을 직접 고쳐(적, track_fast_sea·strike 플레이, '고속 보트 추적' 버튼, 좌표 튜닝) `example_world.py`와 갈라졌다. 이 상태에서 `gen_examples.py`를 돌리면 그 변경이 덮어써진다.
- 예시 프레임 s7·s8(Part1-20)이 track_fast_sea·strike를 쓰는데 `test_examples_share_one_world`는 예시 시나리오에 그 플레이가 있어야 통과한다. JSON을 읽으면 예시 세계 = 시연 세계라 바로 맞는다.
- 정의를 한 곳(JSON)에 두면 코드와 JSON 사이에서 값이 다시 갈라질 일이 없다.

## 버린 대안
- `example_world.py`를 원본으로 두고 최동호의 JSON 변경(약 340줄)을 코드로 옮김(Part2-19.1 세션 또는 Part1-20 세션이). 옮기는 일이 크고, 같은 파일을 두 세션이 고쳐 충돌하며, 정의가 두 곳에 남는다.

## 영향
- `scripts/example_world.py`(JSON 읽기로 교체), `scripts/gen_examples.py`(demo/ 쓰기 제거), `contracts/examples/*.json` 재생성(시나리오·장면 값이 시연 JSON 기준으로 바뀜).
- Part2-19.1 계획(`docs/superpowers/plans/2026-10-10-sea-avoids-land.md`) 6·8단계와 설계 5번의 "시나리오 JSON은 손으로 고치지 않는다: example_world.py가 … gen_examples.py가 다시 만든다"가 뒤집힌다. 섬 다각형(`land`)·수상정 home·적 좌표는 `baengnyeong_night.json`을 직접 고친다. 그 세션에 알린다.
- `contracts/API.md`·`contracts/README.md`의 예시 생성 설명.
