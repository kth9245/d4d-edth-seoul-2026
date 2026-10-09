---
id: 0018
title: 테스트는 병렬 실행이 기본(pytest-xdist, -n auto)
status: 확정
decided_by: kth9245
date: 2026-10-09
modules: [infra]
supersedes: null
---
## 결정
2026-10-09 사람이 말한 것을 그대로 적는다. AI가 "할 일 기록 도구 테스트 때문에 인프라 파일을 바꾸는 ship이 약 30초 늘었다"고 보고하고 줄이는 방법(병렬 실행 / 관련 없을 때 건너뜀 / 둘 다)을 물은 뒤의 대화.

사람: "이거 시간 아껴야함."
사람(방법을 고르며): "모든 테스트나 오래걸리는 것들은 병렬 실행이 기본이 되어야함"

(AI 해석)
1. dev 의존성에 `pytest-xdist`를 넣고 `pyproject.toml`의 pytest `addopts`에 `-n auto`를 넣는다. 그래서 `uv run pytest`, `scripts/ship.sh`, `scripts/check.sh --all`이 모두 CPU 수만큼 병렬로 돈다.
2. 테스트 하나를 디버깅할 때처럼 병렬이 방해되면 `-n 0`으로 끈다.
3. 테스트는 병렬로 돌아도 서로 영향을 주지 않게 쓴다(`tmp_path`만 쓰고 저장소 파일·전역 상태를 바꾸지 않는다).

## 이유
- 측정(이 노트북, 6코어): ship이 돌리는 테스트(`tests modules`, test_ship 제외) 순차 54초, 기록 도구 통합 테스트를 빼면 16초, 병렬이면 전부 포함 12.8초·실패 0.
- 테스트를 빼지 않고도 기록 도구를 넣기 전보다 빨라진다.

## 버린 대안
- 관련 없을 때 기록 도구 테스트 건너뛰기: 건너뛴 쪽에서 깨진 것을 못 잡고, 기록 도구를 바꾸는 ship은 여전히 54초.

## 영향
- `pyproject.toml`(addopts, dev 의존성), `uv.lock`. 팀원은 다음 `uv sync`(또는 `uv run`)에서 자동 설치.
- AGENTS.md "명령"의 테스트 줄에 `-n 0` 안내.
