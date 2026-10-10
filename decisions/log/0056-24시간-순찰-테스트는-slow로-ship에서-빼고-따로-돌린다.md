---
id: 0056
title: 24시간 순찰 테스트는 slow로 ship에서 빼고 따로 돌린다
status: 확정
decided_by: kth9245
date: 2026-10-10
modules: [infra, runtime, demo]
supersedes: null
---
## 결정
리드 답: "ship에서 빼고 따로 (Recommended)" — 선택지 문구는 "slow 표시를 붙여 ship은 건너뛴다. 교대 로직이나 24시간 시나리오를 바꿀 때, 그리고 프리즈 전에 `uv run pytest -m slow`로 따로 돌린다. 황승주에게 알린다."

- `tests/test_patrol_rotation_24h.py`(결정 0037, 24시간 432,000틱, 약 68초)에 `slow` 표시를 붙인다.
- `scripts/ship.sh`는 `slow` 테스트를 돌리지 않는다.
- 교대 로직(`modules/runtime`의 교대)·`demo/scenarios/baengnyeong_24h.json`·`demo/roles/coast_*.json`을 바꾸는 사람과 프리즈(일요일 06:00) 전에는 `uv run pytest -m slow`로 직접 돌린다.

(AI 해석) 다른 테스트에 `slow`를 붙이는 기준은 이번 결정 범위 밖이다. 붙이려면 따로 정한다.

## 이유
- ship.sh는 `tests/`·`tools/`·`scripts/`·`contracts/`·`shared/`가 바뀔 때만 전체 테스트를 돌려 이 테스트가 그때만 돈다. 리드 ship의 `tests/`가 117초(ship.sh 목표 20초 미만)이고, `test_ship`의 복제 저장소 ship 테스트(72초)도 안에서 이 테스트를 한 번 더 돈다.
- 정작 이 테스트가 지키는 교대 로직(`modules/runtime`)만 바꾸면 ship이 이 테스트를 돌리지 않는다. ship에 두어도 필요한 때 지켜 주지 못한다.

## 버린 대안
- 관련 파일(runtime·sim·gateway·demo)이 바뀔 때만 ship에서 돌리기: 시점은 맞지만 지금 이 테스트를 안 내는 황승주·최동호의 ship이 매번 68초씩 늘어난다.
- 그대로 두고 `test_ship` 복제 저장소에서만 빼기: 리드 ship이 여전히 약 70초.

## 영향
- `pyproject.toml`(pytest markers), `tests/test_patrol_rotation_24h.py`, `scripts/ship.sh`, `tests/test_ship*.py`. 테스트 작성자 황승주에게 알린다.
- 24시간 교대가 깨져도 ship이 막지 않는다. 바꾸는 사람이 직접 돌려야 한다.
