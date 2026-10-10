# Hackathon Repo Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 대회 전에 AI 병렬 개발용 저장소 골격(규칙 문서, 계약, 강제 장치, 스크립트, 가짜 로직으로 끝까지 연결된 walking skeleton, 오프라인 지도 화면)을 완성하고 시험까지 끝낸다.

**Architecture:** Python 패키지 `contracts`(pydantic 계약), `shared`(좌표 계산), `modules.<m>`(파이프라인 모듈, 1 액션 = 1 파일)과 TypeScript `modules/cop-ui`(Vite + React + MapLibre)로 구성한다. `tools/`의 표준 라이브러리 전용 검사 스크립트가 AI 수정 시점(Claude/Codex hook)과 커밋 시점(git hook)에 규칙을 강제하고, `scripts/`가 생성·동기화·ship·실행을 명령 하나로 처리한다. `modules.gateway`가 시나리오를 돌려 프레임을 WebSocket으로 송출하고, 빌드된 UI를 같은 프로세스에서 정적 파일로 서빙한다.

**Tech Stack:** Python 3.12, uv 0.11, FastAPI, uvicorn, pydantic v2, PyYAML, pytest, ruff / Node 22, Vite, React, TypeScript, maplibre-gl 6, pmtiles 4, @protomaps/basemaps 5, vitest, eslint / go-pmtiles 1.31 CLI.

**Spec:** `docs/superpowers/specs/2026-10-07-hackathon-repo-structure-design.md`

## Global Constraints

- CLAUDE.md, CLAUDE.local.md를 저장소에 만들지 않는다. 규칙 파일은 AGENTS.md뿐이다.
- 루트 AGENTS.md 150줄 이하, 모듈 AGENTS.md 40줄 이하.
- 액션 파일: 공개 함수 1개, 함수 이름 = 파일 이름(`verb_noun`), 80줄 이하, 첫 docstring에 `<SPEC id> <name>: <설명>`과 `SPEC: modules/<m>/SPEC.md#<id>`.
- 액션 외 코드 파일(.py/.ts/.tsx) 200줄 이하.
- 좌표 WGS84 위경도(도), 고도 m, 시간 UTC epoch 밀리초(`t_ms`).
- 모듈은 다른 모듈을 루트 공개 API(`from modules.<m> import ...`)로만 import. `knowledge` import 금지. `shared`, `contracts`는 `modules`를 import하지 않음.
- `tools/guard/`, `tools/*.py`는 표준 라이브러리만 사용(hook에서 `python3`로 0.1초 이내 실행).
- 자동 생성 파일 `tasks/BOARD.md`, `knowledge/INDEX.md`, `decisions/INDEX.md`는 `.gitignore`에 넣는다.
- 커밋 검사 2초 이하, ship 검사 20초 이하. 테스트는 커밋에서 실행하지 않는다.
- 시연 중 외부 네트워크 호출 금지. 지도 타일은 로컬 파일.
- 브랜치 소유 규칙: `<모듈>/…` → `modules/<모듈>/**`·`knowledge/**`·`decisions/log/**`, `contracts/…` → `contracts/**`·`modules/cop-ui/src/contracts.gen.ts`, `infra/…` → 루트 `AGENTS.md`·`README.md`·`pyproject.toml`·`.gitignore`·`tests/**`·`scripts/**`·`tools/**`·`.claude/**`·`.codex/**`·`.agents/**`·`.githooks/**`·`shared/**`·`demo/**`·`docs/**`, 그 외 브랜치 → `knowledge/**`·`decisions/log/**`만.
- 커밋 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- 이 계획은 `main` 브랜치에서 실행한다. AI 수정 hook(.claude/.codex)은 마지막 Task 15에서 켠다. 그 전에 켜면 이 계획을 실행하는 세션 자신이 guard에 막힌다. git pre-commit hook은 Task 6부터 켠다.

## Review Focus

1. rebase 충돌 해결 중(detached HEAD)에 AI가 파일을 고치면 guard가 브랜치 이름을 못 읽어 모든 수정을 막을 수 있다 → `.git/rebase-merge/head-name` 또는 `.git/rebase-apply/head-name`에서 원래 브랜치를 읽는다 (Task 5 테스트 `test_branch_during_rebase`).
2. Codex는 모듈 폴더에서 실행되므로 patch 경로가 모듈 폴더 기준 상대 경로다 → hook 입력의 `cwd` 기준으로 해석해야 한다 (Task 5 테스트 `test_codex_relative_path_resolves_from_cwd`).
3. 시나리오 YAML에 잘못된 값(모르는 kind, 음수 duration)이 있으면 시연 도중이 아니라 로딩 시점에 무엇이 틀렸는지 알려줘야 한다 (Task 8 테스트 `test_load_scenario_rejects_unknown_kind`).
4. 시연 중 브라우저를 새로고침하거나 두 번째 탭을 열어도 gateway가 죽지 않고 새 연결에 프레임을 계속 보내야 한다 (Task 10 테스트 `test_websocket_reconnect`).
5. 지도 타일 파일이 없는 노트북에서도 화면이 뜨고 표적은 보여야 한다 (Task 12 `basemapStyle` 테스트 `returns background-only style when tiles missing` + Task 13 Step 2 수동 확인).

---

## File Structure

| 경로 | 책임 |
|---|---|
| `pyproject.toml`, `.gitignore` | Python 의존성, ruff·pytest 설정, 무시 파일 |
| `contracts/models.py` | pydantic 계약: Detection, Track, Assessment, Response, Frame |
| `contracts/examples/*.json` | 계약별 예시 데이터 |
| `contracts/schema/*.json` | 자동 생성 JSON Schema |
| `shared/geo.py` | 위경도 ↔ 동/북 미터 변환, 거리 |
| `tools/spec.py` | SPEC.md 표 파싱·행 추가 (공용 라이브러리) |
| `tools/frontmatter.py` | 마크다운 frontmatter 파싱 (표준 라이브러리, 단순 key: value / [list]) |
| `tools/guard/check_edit.py` | AI 수정 시점 차단 (Claude/Codex 공용) |
| `tools/check_specs.py` | 커밋 시 SPEC 동기화·파일 길이 검사 |
| `tools/check_imports.py` | 커밋 시 모듈 경계 검사 |
| `scripts/new_action.py` | SPEC 행 + 액션 파일 + 실패하는 테스트 생성 |
| `scripts/sync_docs.py` | BOARD·지식 INDEX·결정 INDEX·AGENTS.md 정책 구간 생성 |
| `scripts/decide.py` | 결정 제안 생성 / 확정 |
| `scripts/gen_contracts.py` | JSON Schema + TS 타입 생성 |
| `scripts/smoke.py` | 화면 없는 데모 smoke test |
| `scripts/check.sh`, `ship.sh`, `setup.sh`, `dev.sh`, `demo.sh`, `fetch_tiles.sh` | 셸 진입점 |
| `.githooks/*` | pre-commit, post-merge, post-checkout, post-rewrite |
| `.claude/settings.json`, `.codex/hooks.json` | guard hook 등록 |
| `.agents/skills/*/SKILL.md`, `.claude/skills` (symlink) | new-action, kb-save, decide, ship |
| `AGENTS.md`, `README.md`, `docs/problem.md`, `docs/glossary.md` | 규칙·안내 문서 |
| `decisions/POLICY.md`, `decisions/log/`, `knowledge/{inbox,cards,spikes}/`, `demo/*` | 저장소 골격 |
| `modules/{sim,sensing,tracking,assess,respond,gateway}/` | Python 파이프라인 모듈 |
| `modules/cop-ui/` | 지도 관제 화면 |
| `tests/` | `tools/`, `scripts/`, `contracts`, `shared` 테스트 |

---

### Task 1: Python 프로젝트 기반, 계약, 좌표 유틸

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `contracts/__init__.py`, `contracts/models.py`, `contracts/examples/{detection,track,assessment,response,frame}.json`, `shared/__init__.py`, `shared/geo.py`, `modules/__init__.py`, `tests/__init__.py`, `tests/test_contracts.py`, `tests/test_geo.py`

**Interfaces:**
- Produces:
  - `contracts.models`: `SensorType(str, Enum){RF="rf", EOIR="eoir", RADAR="radar"}`, `Detection(id:str, sensor:SensorType, t_ms:int, lat:float, lon:float, alt_m:float, strength:float∈[0,1])`, `Track(id:str, t_ms:int, lat:float, lon:float, alt_m:float, vel_east_mps:float=0, vel_north_mps:float=0, hits:int=1, last_seen_ms:int)`, `ObjectClass(str, Enum){DRONE="drone", BALLOON="balloon", BIRD="bird", UNKNOWN="unknown"}`, `Assessment(track_id:str, object_class:ObjectClass, threat:float∈[0,1], reason:str)`, `ResponseKind(str, Enum){OBSERVE="observe", SOFT_KILL="soft_kill", HARD_KILL="hard_kill"}`, `Response(track_id:str, kind:ResponseKind, reason:str)`, `Frame(t_ms:int, tracks:list[Track], assessments:list[Assessment], responses:list[Response])`, `ALL_MODELS: dict[str, type[BaseModel]]` (키: `detection`, `track`, `assessment`, `response`, `frame`)
  - `shared.geo`: `offset_latlon(lat, lon, east_m, north_m) -> tuple[float, float]`, `enu_delta_m(lat1, lon1, lat2, lon2) -> tuple[float, float]` (1에서 2로 가는 동/북 미터), `distance_m(lat1, lon1, lat2, lon2) -> float`

- [ ] **Step 1: pyproject.toml과 .gitignore 작성**

`pyproject.toml`:
```toml
[project]
name = "d4d-edth-seoul-2026"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.30",
  "pydantic>=2.8",
  "pyyaml>=6.0",
]

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6", "httpx>=0.27"]

[tool.uv]
package = false

[tool.ruff]
line-length = 100
target-version = "py311"
extend-exclude = ["knowledge/spikes", "modules/cop-ui"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests", "modules"]
pythonpath = ["."]
norecursedirs = ["node_modules", "dist", ".venv", "knowledge"]
addopts = "-q"
```

`.gitignore`:
```gitignore
__pycache__/
*.pyc
.venv/
.pytest_cache/
.ruff_cache/
.env
.env.*
node_modules/
modules/cop-ui/dist/
modules/cop-ui/public/tiles/*.pmtiles
.tools/
tasks/BOARD.md
knowledge/INDEX.md
decisions/INDEX.md
```

- [ ] **Step 2: 의존성 설치**

Run: `uv sync`
Expected: `.venv` 생성, 오류 없음.

- [ ] **Step 3: 실패하는 테스트 작성**

`tests/__init__.py`, `modules/__init__.py`, `contracts/__init__.py`, `shared/__init__.py`: 빈 파일.

`tests/test_geo.py`:
```python
import math

from shared.geo import distance_m, enu_delta_m, offset_latlon


def test_offset_then_delta_roundtrip():
    lat, lon = 37.5665, 126.9780
    lat2, lon2 = offset_latlon(lat, lon, east_m=300.0, north_m=-400.0)
    east, north = enu_delta_m(lat, lon, lat2, lon2)
    assert math.isclose(east, 300.0, abs_tol=0.5)
    assert math.isclose(north, -400.0, abs_tol=0.5)


def test_distance_is_hypot_of_delta():
    lat, lon = 37.5665, 126.9780
    lat2, lon2 = offset_latlon(lat, lon, 300.0, 400.0)
    assert math.isclose(distance_m(lat, lon, lat2, lon2), 500.0, abs_tol=0.5)


def test_zero_offset_is_identity():
    assert offset_latlon(37.0, 127.0, 0.0, 0.0) == (37.0, 127.0)
```

`tests/test_contracts.py`:
```python
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts.models import ALL_MODELS, Detection

EXAMPLES = Path(__file__).resolve().parent.parent / "contracts" / "examples"


@pytest.mark.parametrize("name", sorted(ALL_MODELS))
def test_example_matches_model(name):
    data = json.loads((EXAMPLES / f"{name}.json").read_text(encoding="utf-8"))
    ALL_MODELS[name].model_validate(data)


def test_strength_out_of_range_rejected():
    with pytest.raises(ValidationError):
        Detection(id="d", sensor="radar", t_ms=0, lat=37.0, lon=127.0, alt_m=10, strength=1.5)


def test_unknown_sensor_rejected():
    with pytest.raises(ValidationError):
        Detection(id="d", sensor="sonar", t_ms=0, lat=37.0, lon=127.0, alt_m=10, strength=0.5)
```

- [ ] **Step 4: 테스트가 실패하는지 확인**

Run: `uv run pytest tests/test_geo.py tests/test_contracts.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'shared.geo'` / `contracts.models`.

- [ ] **Step 5: 구현**

`shared/geo.py`:
```python
"""Small-area WGS84 <-> local east/north meter conversions (equirectangular)."""

import math

EARTH_RADIUS_M = 6_371_000.0


def offset_latlon(lat: float, lon: float, east_m: float, north_m: float) -> tuple[float, float]:
    if east_m == 0.0 and north_m == 0.0:
        return (lat, lon)
    dlat = math.degrees(north_m / EARTH_RADIUS_M)
    dlon = math.degrees(east_m / (EARTH_RADIUS_M * math.cos(math.radians(lat))))
    return (lat + dlat, lon + dlon)


def enu_delta_m(lat1: float, lon1: float, lat2: float, lon2: float) -> tuple[float, float]:
    mean_lat = math.radians((lat1 + lat2) / 2)
    east = math.radians(lon2 - lon1) * EARTH_RADIUS_M * math.cos(mean_lat)
    north = math.radians(lat2 - lat1) * EARTH_RADIUS_M
    return (east, north)


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    east, north = enu_delta_m(lat1, lon1, lat2, lon2)
    return math.hypot(east, north)
```

`contracts/models.py`:
```python
"""Data contracts shared by all modules. Only the lead edits this file (branch contracts/*).

Units: WGS84 degrees, meters, UTC epoch milliseconds (t_ms).
"""

from enum import Enum

from pydantic import BaseModel, Field


class SensorType(str, Enum):
    RF = "rf"
    EOIR = "eoir"
    RADAR = "radar"


class Detection(BaseModel):
    id: str
    sensor: SensorType
    t_ms: int
    lat: float
    lon: float
    alt_m: float
    strength: float = Field(ge=0.0, le=1.0)


class Track(BaseModel):
    id: str
    t_ms: int
    lat: float
    lon: float
    alt_m: float
    vel_east_mps: float = 0.0
    vel_north_mps: float = 0.0
    hits: int = 1
    last_seen_ms: int


class ObjectClass(str, Enum):
    DRONE = "drone"
    BALLOON = "balloon"
    BIRD = "bird"
    UNKNOWN = "unknown"


class Assessment(BaseModel):
    track_id: str
    object_class: ObjectClass
    threat: float = Field(ge=0.0, le=1.0)
    reason: str


class ResponseKind(str, Enum):
    OBSERVE = "observe"
    SOFT_KILL = "soft_kill"
    HARD_KILL = "hard_kill"


class Response(BaseModel):
    track_id: str
    kind: ResponseKind
    reason: str


class Frame(BaseModel):
    t_ms: int
    tracks: list[Track]
    assessments: list[Assessment]
    responses: list[Response]


ALL_MODELS: dict[str, type[BaseModel]] = {
    "detection": Detection,
    "track": Track,
    "assessment": Assessment,
    "response": Response,
    "frame": Frame,
}
```

`contracts/examples/detection.json`:
```json
{"id": "D-1", "sensor": "radar", "t_ms": 1760061600000, "lat": 37.5665, "lon": 126.978, "alt_m": 120.0, "strength": 0.8}
```
`contracts/examples/track.json`:
```json
{"id": "T-D-1", "t_ms": 1760061600000, "lat": 37.5665, "lon": 126.978, "alt_m": 120.0, "vel_east_mps": 8.0, "vel_north_mps": -2.0, "hits": 5, "last_seen_ms": 1760061600000}
```
`contracts/examples/assessment.json`:
```json
{"track_id": "T-D-1", "object_class": "drone", "threat": 0.82, "reason": "speed 8.2 m/s, 450 m from protected point"}
```
`contracts/examples/response.json`:
```json
{"track_id": "T-D-1", "kind": "soft_kill", "reason": "drone threat 0.82 >= 0.7"}
```
`contracts/examples/frame.json`:
```json
{"t_ms": 1760061600000,
 "tracks": [{"id": "T-D-1", "t_ms": 1760061600000, "lat": 37.5665, "lon": 126.978, "alt_m": 120.0, "vel_east_mps": 8.0, "vel_north_mps": -2.0, "hits": 5, "last_seen_ms": 1760061600000}],
 "assessments": [{"track_id": "T-D-1", "object_class": "drone", "threat": 0.82, "reason": "speed 8.2 m/s, 450 m from protected point"}],
 "responses": [{"track_id": "T-D-1", "kind": "soft_kill", "reason": "drone threat 0.82 >= 0.7"}]}
```

- [ ] **Step 6: 테스트 통과 확인**

Run: `uv run pytest tests/test_geo.py tests/test_contracts.py`
Expected: PASS (8 passed).

- [ ] **Step 7: 커밋**

```bash
git add pyproject.toml uv.lock .gitignore contracts shared modules/__init__.py tests
git commit -m "feat: add python base, contracts and geo utils

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

---

### Task 2: SPEC 라이브러리, frontmatter 파서, new_action.py

**Files:**
- Create: `tools/__init__.py`, `tools/spec.py`, `tools/frontmatter.py`, `scripts/new_action.py`, `tests/test_spec.py`, `tests/test_frontmatter.py`, `tests/test_new_action.py`

**Interfaces:**
- Produces:
  - `tools.spec.SPEC_HEADER: str` (표 머리 두 줄), `tools.spec.SpecRow` (dataclass: `id, action, inputs, outputs, done, owner, status`), `parse_spec(text: str) -> tuple[str | None, list[SpecRow]]` (prefix, rows), `spec_actions(spec_path: Path) -> set[str]`, `append_row(spec_path: Path, row: SpecRow) -> None`, `next_id(prefix: str, rows: list[SpecRow]) -> str` (예: `TRK-03`)
  - `tools.frontmatter.parse(text: str) -> tuple[dict, str]` (meta, body). 지원 형식: `key: value`, `key: [a, b]`, `key: null`, 값 뒤 `# 주석` 제거
  - CLI `python scripts/new_action.py <module> <action> "<desc>" [--inputs ..] [--outputs ..] [--done ..] [--owner ..] [--root PATH]`
  - SPEC.md 형식 (모든 모듈 공통):
    ```
    <!-- prefix: TRK -->
    # tracking SPEC

    | id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
    |---|---|---|---|---|---|---|
    | TRK-01 | predict_tracks | ... | ... | ... | 철수 | 완료 |
    ```

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_frontmatter.py`:
```python
from tools.frontmatter import parse


def test_parse_scalars_lists_null_and_comments():
    text = (
        "---\nid: 0002\ntitle: 추적은 Kalman\nstatus: 제안   # 제안 / 확정\n"
        "modules: [tracking, assess]\nsupersedes: null\n---\n## 결정\n본문\n"
    )
    meta, body = parse(text)
    assert meta == {
        "id": "0002",
        "title": "추적은 Kalman",
        "status": "제안",
        "modules": ["tracking", "assess"],
        "supersedes": None,
    }
    assert body.startswith("## 결정")


def test_no_frontmatter_returns_empty_meta():
    assert parse("# just text\n") == ({}, "# just text\n")


def test_empty_list():
    meta, _ = parse("---\ntags: []\n---\n")
    assert meta["tags"] == []
```

`tests/test_spec.py`:
```python
from tools.spec import SpecRow, append_row, next_id, parse_spec, spec_actions

SPEC = """<!-- prefix: TRK -->
# tracking SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| TRK-01 | predict_tracks | list[Track], t_ms | list[Track] | 등속 예측 | 철수 | 완료 |
| TRK-02 | associate_detections | tracks, dets | dict | 최근접 | 철수 | 진행중 |
"""


def test_parse_spec_reads_prefix_and_rows():
    prefix, rows = parse_spec(SPEC)
    assert prefix == "TRK"
    assert [r.action for r in rows] == ["predict_tracks", "associate_detections"]
    assert rows[1].status == "진행중"


def test_next_id_increments_max():
    _, rows = parse_spec(SPEC)
    assert next_id("TRK", rows) == "TRK-03"
    assert next_id("TRK", []) == "TRK-01"


def test_append_row_and_spec_actions(tmp_path):
    p = tmp_path / "SPEC.md"
    p.write_text(SPEC, encoding="utf-8")
    append_row(p, SpecRow("TRK-03", "update_tracks", "a", "b", "c", "영희", "진행중"))
    assert spec_actions(p) == {"predict_tracks", "associate_detections", "update_tracks"}
    assert p.read_text(encoding="utf-8").endswith("| 영희 | 진행중 |\n")


def test_pipe_in_cell_is_escaped(tmp_path):
    p = tmp_path / "SPEC.md"
    p.write_text(SPEC, encoding="utf-8")
    append_row(p, SpecRow("TRK-03", "x_y", "a|b", "o", "d", "o", "예정"))
    _, rows = parse_spec(p.read_text(encoding="utf-8"))
    assert rows[-1].inputs == "a/b"


def test_spec_actions_missing_file(tmp_path):
    assert spec_actions(tmp_path / "nope.md") == set()
```

`tests/test_new_action.py`:
```python
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "new_action.py"

SPEC = (
    "<!-- prefix: TRK -->\n# tracking SPEC\n\n"
    "| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |\n|---|---|---|---|---|---|---|\n"
)


def make_module(root: Path) -> Path:
    mod = root / "modules" / "tracking"
    (mod / "actions").mkdir(parents=True)
    (mod / "tests").mkdir()
    (mod / "__init__.py").write_text("")
    (mod / "SPEC.md").write_text(SPEC, encoding="utf-8")
    return mod


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--root", str(root), "--owner", "철수"],
        capture_output=True,
        text=True,
    )


def test_creates_spec_row_action_and_failing_test(tmp_path):
    mod = make_module(tmp_path)
    r = run(tmp_path, "tracking", "predict_tracks", "1초 뒤 위치 예측")
    assert r.returncode == 0, r.stderr
    action = (mod / "actions" / "predict_tracks.py").read_text(encoding="utf-8")
    assert action.startswith(
        '"""TRK-01 predict_tracks: 1초 뒤 위치 예측\nSPEC: modules/tracking/SPEC.md#TRK-01'
    )
    assert "def predict_tracks(" in action and "raise NotImplementedError" in action
    test = (mod / "tests" / "test_predict_tracks.py").read_text(encoding="utf-8")
    assert "from modules.tracking.actions.predict_tracks import predict_tracks" in test
    assert "| TRK-01 | predict_tracks |" in (mod / "SPEC.md").read_text(encoding="utf-8")
    assert (mod / "actions" / "__init__.py").exists()
    assert (mod / "tests" / "__init__.py").exists()


def test_rejects_bad_name(tmp_path):
    make_module(tmp_path)
    r = run(tmp_path, "tracking", "PredictTracks", "x")
    assert r.returncode == 1
    assert "verb_noun" in r.stderr


def test_rejects_existing_action(tmp_path):
    make_module(tmp_path)
    assert run(tmp_path, "tracking", "predict_tracks", "x").returncode == 0
    r = run(tmp_path, "tracking", "predict_tracks", "x")
    assert r.returncode == 1
    assert "이미" in r.stderr


def test_rejects_unknown_module(tmp_path):
    make_module(tmp_path)
    r = run(tmp_path, "nosuch", "do_thing", "x")
    assert r.returncode == 1
    assert "모듈" in r.stderr
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_frontmatter.py tests/test_spec.py tests/test_new_action.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.frontmatter'` 등.

- [ ] **Step 3: 구현**

`tools/__init__.py`: 빈 파일.

`tools/frontmatter.py`:
```python
"""Minimal frontmatter parser (stdlib only): `key: value`, `key: [a, b]`, `key: null`."""


def _value(raw: str):
    raw = raw.split(" #", 1)[0].strip()
    if raw in ("", "null", "~"):
        return None
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [v.strip().strip("'\"") for v in inner.split(",")] if inner else []
    return raw.strip("'\"")


def parse(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, raw = line.split(":", 1)
            meta[key.strip()] = _value(raw)
    body = text[end + 4 :].lstrip("\n")
    return meta, body
```

`tools/spec.py`:
```python
"""SPEC.md table helpers shared by guard, checks and scripts (stdlib only)."""

import re
from dataclasses import astuple, dataclass
from pathlib import Path

SPEC_HEADER = (
    "| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |\n|---|---|---|---|---|---|---|\n"
)
PREFIX_RE = re.compile(r"<!--\s*prefix:\s*([A-Z]+)\s*-->")


@dataclass
class SpecRow:
    id: str
    action: str
    inputs: str
    outputs: str
    done: str
    owner: str
    status: str


def parse_spec(text: str) -> tuple[str | None, list[SpecRow]]:
    m = PREFIX_RE.search(text)
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) != 7:
            continue
        if cells[0] == "id" or set(cells[0]) <= set("-: "):
            continue
        rows.append(SpecRow(*cells))
    return (m.group(1) if m else None), rows


def spec_actions(spec_path: Path) -> set[str]:
    if not spec_path.exists():
        return set()
    return {r.action for r in parse_spec(spec_path.read_text(encoding="utf-8"))[1]}


def next_id(prefix: str, rows: list[SpecRow]) -> str:
    nums = [int(r.id.split("-")[-1]) for r in rows if r.id.split("-")[-1].isdigit()]
    return f"{prefix}-{max(nums, default=0) + 1:02d}"


def append_row(spec_path: Path, row: SpecRow) -> None:
    text = spec_path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    cells = [str(c).replace("|", "/").replace("\n", " ") for c in astuple(row)]
    spec_path.write_text(text + "| " + " | ".join(cells) + " |\n", encoding="utf-8")
```

`scripts/new_action.py`:
```python
"""Create SPEC row + action file + failing test in one step.

Usage: python scripts/new_action.py <module> <verb_noun> "<description>"
       [--inputs ..] [--outputs ..] [--done ..] [--owner ..]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.spec import SpecRow, append_row, next_id, parse_spec  # noqa: E402

NAME_RE = re.compile(r"^[a-z]+(_[a-z0-9]+)+$")

ACTION_TMPL = '''"""{id} {name}: {desc}
SPEC: modules/{module}/SPEC.md#{id}
"""


def {name}(*args, **kwargs):
    raise NotImplementedError
'''

TEST_TMPL = """import pytest

from modules.{module}.actions.{name} import {name}


def test_{name}():
    pytest.fail("{id}: replace with a real test for {name}")
    {name}()
"""


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def git_user() -> str:
    r = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
    return r.stdout.strip() or "?"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("action")
    ap.add_argument("desc")
    ap.add_argument("--inputs", default="")
    ap.add_argument("--outputs", default="")
    ap.add_argument("--done", default="")
    ap.add_argument("--owner", default=None)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    a = ap.parse_args()

    if not NAME_RE.match(a.action):
        fail(f"액션 이름은 verb_noun 형식의 snake_case여야 합니다: {a.action}")
    mod = Path(a.root) / "modules" / a.module
    if not (mod / "__init__.py").exists():
        fail(f"Python 모듈이 없습니다: modules/{a.module}")
    spec = mod / "SPEC.md"
    action_file = mod / "actions" / f"{a.action}.py"
    test_file = mod / "tests" / f"test_{a.action}.py"
    prefix, rows = parse_spec(spec.read_text(encoding="utf-8"))
    if action_file.exists() or any(r.action == a.action for r in rows):
        fail(f"이미 있는 액션입니다: {a.module}.{a.action}")
    if not prefix:
        fail(f"SPEC.md 첫 줄에 <!-- prefix: XXX --> 가 없습니다: {spec}")

    sid = next_id(prefix, rows)
    owner = a.owner or git_user()
    append_row(spec, SpecRow(sid, a.action, a.inputs, a.outputs, a.done, owner, "진행중"))
    for pkg in (mod / "actions", mod / "tests"):
        pkg.mkdir(exist_ok=True)
        (pkg / "__init__.py").touch()
    fmt = {"id": sid, "name": a.action, "desc": a.desc, "module": a.module}
    action_file.write_text(ACTION_TMPL.format(**fmt), encoding="utf-8")
    test_file.write_text(TEST_TMPL.format(**fmt), encoding="utf-8")
    print(f"{sid} 생성: {action_file.relative_to(a.root)}, {test_file.relative_to(a.root)}")
    print("다음: 테스트를 실제 동작으로 고친 뒤 액션을 구현해 통과시키세요.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_frontmatter.py tests/test_spec.py tests/test_new_action.py`
Expected: PASS (12 passed).

- [ ] **Step 5: 커밋**

```bash
git add tools scripts/new_action.py tests
git commit -m "feat: add spec helpers, frontmatter parser and new_action script

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

---

### Task 3: sync_docs.py (BOARD, 지식 INDEX, 결정 INDEX, 정책 구간)

**Files:**
- Create: `scripts/sync_docs.py`, `tests/test_sync_docs.py`

**Interfaces:**
- Consumes: `tools.spec.parse_spec`, `tools.frontmatter.parse`
- Produces:
  - `build_board(root: Path) -> str`, `build_knowledge_index(root: Path) -> str`, `build_decision_index(root: Path) -> str`, `apply_policy(agents_text: str, policy_text: str) -> str`, `sync(root: Path) -> bool` (AGENTS.md가 바뀌었으면 True)
  - CLI `python scripts/sync_docs.py [--stage] [--root PATH]` (`--stage`: AGENTS.md가 바뀌었으면 `git add AGENTS.md`)
  - AGENTS.md 표시 구간: `<!-- POLICY:BEGIN -->` … `<!-- POLICY:END -->`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_sync_docs.py`:
```python
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("sync_docs", ROOT / "scripts" / "sync_docs.py")
sd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sd)

SPEC = (
    "<!-- prefix: TRK -->\n# tracking SPEC\n\n"
    "| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |\n|---|---|---|---|---|---|---|\n"
    "| TRK-01 | predict_tracks | a | b | c | 철수 | 완료 |\n"
)
CARD = (
    "---\nid: rf-bands\ntitle: RF 대역\nsummary: 2.4/5.8GHz\ntags: [rf]\n"
    "modules: [sensing, sim]\nconfidence: 확인됨\n---\n## 결론\n"
)
DECISION = (
    "---\nid: 0001\ntitle: 좌표 WGS84\nstatus: 확정\ndecided_by: 영희\n"
    "date: 2026-10-10\nmodules: [tracking]\nsupersedes: null\n---\n## 결정\n"
)


def make_repo(root: Path) -> None:
    (root / "modules" / "tracking").mkdir(parents=True)
    (root / "modules" / "tracking" / "SPEC.md").write_text(SPEC, encoding="utf-8")
    (root / "knowledge" / "cards").mkdir(parents=True)
    (root / "knowledge" / "cards" / "rf-bands.md").write_text(CARD, encoding="utf-8")
    (root / "decisions" / "log").mkdir(parents=True)
    (root / "decisions" / "log" / "0001-wgs84.md").write_text(DECISION, encoding="utf-8")
    (root / "decisions" / "POLICY.md").write_text("# 정책\n\n1. 오프라인 시연\n", encoding="utf-8")
    (root / "tasks").mkdir()
    (root / "AGENTS.md").write_text(
        "# 규칙\n<!-- POLICY:BEGIN -->\nold\n<!-- POLICY:END -->\n끝\n", encoding="utf-8"
    )


def test_board_lists_rows_with_module(tmp_path):
    make_repo(tmp_path)
    board = sd.build_board(tmp_path)
    assert "| tracking | TRK-01 | predict_tracks | 철수 | 완료 |" in board
    assert "자동 생성" in board


def test_knowledge_index_groups_by_module(tmp_path):
    make_repo(tmp_path)
    idx = sd.build_knowledge_index(tmp_path)
    assert "## sensing" in idx and "## sim" in idx
    assert "- [RF 대역](cards/rf-bands.md) — 2.4/5.8GHz `rf` (확인됨)" in idx


def test_decision_index(tmp_path):
    make_repo(tmp_path)
    idx = sd.build_decision_index(tmp_path)
    assert "| [0001](log/0001-wgs84.md) | 좌표 WGS84 | 확정 | 영희 | tracking |" in idx


def test_apply_policy_replaces_block_only():
    out = sd.apply_policy(
        "a\n<!-- POLICY:BEGIN -->\nold\n<!-- POLICY:END -->\nz\n", "# 정책\n\n1. x\n"
    )
    assert out == "a\n<!-- POLICY:BEGIN -->\n1. x\n<!-- POLICY:END -->\nz\n"


def test_apply_policy_without_markers_is_noop():
    assert sd.apply_policy("no markers\n", "1. x\n") == "no markers\n"


def test_sync_writes_files_and_reports_agents_change(tmp_path):
    make_repo(tmp_path)
    assert sd.sync(tmp_path) is True
    assert (tmp_path / "tasks" / "BOARD.md").exists()
    assert (tmp_path / "knowledge" / "INDEX.md").exists()
    assert (tmp_path / "decisions" / "INDEX.md").exists()
    assert "1. 오프라인 시연" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert sd.sync(tmp_path) is False


def test_sync_tolerates_empty_repo(tmp_path):
    assert sd.sync(tmp_path) is False
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_sync_docs.py`
Expected: FAIL — `FileNotFoundError` (scripts/sync_docs.py 없음).

- [ ] **Step 3: 구현**

`scripts/sync_docs.py`:
```python
"""Regenerate BOARD/INDEX files and the AGENTS.md policy block. Never blocks commits."""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.frontmatter import parse  # noqa: E402
from tools.spec import parse_spec  # noqa: E402

BEGIN, END = "<!-- POLICY:BEGIN -->", "<!-- POLICY:END -->"
GENERATED = "<!-- 자동 생성 파일 (scripts/sync_docs.py). 직접 수정하지 마세요. -->\n"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def build_board(root: Path) -> str:
    lines = [GENERATED, "# 작업판\n", "| 모듈 | id | 액션 | 담당 | 상태 |", "|---|---|---|---|---|"]
    for spec in sorted((root / "modules").glob("*/SPEC.md")):
        for r in parse_spec(_read(spec))[1]:
            lines.append(f"| {spec.parent.name} | {r.id} | {r.action} | {r.owner} | {r.status} |")
    return "\n".join(lines) + "\n"


def build_knowledge_index(root: Path) -> str:
    groups: dict[str, list[str]] = {}
    for card in sorted((root / "knowledge" / "cards").glob("*.md")):
        m, _ = parse(_read(card))
        tags = " ".join(f"`{t}`" for t in m.get("tags") or [])
        line = f"- [{m.get('title', card.stem)}](cards/{card.name}) — {m.get('summary', '')} {tags} ({m.get('confidence', '?')})"
        for mod in m.get("modules") or ["general"]:
            groups.setdefault(mod, []).append(line)
    out = [GENERATED, "# 지식 목차\n"]
    for mod in sorted(groups):
        out += [f"## {mod}", *groups[mod], ""]
    return "\n".join(out)


def build_decision_index(root: Path) -> str:
    out = [
        GENERATED,
        "# 결정 목록\n",
        "| id | 제목 | 상태 | 결정자 | 모듈 |",
        "|---|---|---|---|---|",
    ]
    for doc in sorted((root / "decisions" / "log").glob("*.md")):
        m, _ = parse(_read(doc))
        mods = ", ".join(m.get("modules") or [])
        out.append(
            f"| [{m.get('id', doc.stem)}](log/{doc.name}) | {m.get('title', '')} | "
            f"{m.get('status', '')} | {m.get('decided_by') or ''} | {mods} |"
        )
    return "\n".join(out) + "\n"


def apply_policy(agents_text: str, policy_text: str) -> str:
    if BEGIN not in agents_text or END not in agents_text:
        return agents_text
    body = "\n".join(l for l in policy_text.strip().splitlines() if not l.startswith("# ")).strip()
    head, rest = agents_text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{BEGIN}\n{body}\n{END}{tail}"


def _write(p: Path, text: str) -> None:
    if p.parent.exists() and (not p.exists() or _read(p) != text):
        p.write_text(text, encoding="utf-8")


def sync(root: Path) -> bool:
    _write(root / "tasks" / "BOARD.md", build_board(root))
    _write(root / "knowledge" / "INDEX.md", build_knowledge_index(root))
    _write(root / "decisions" / "INDEX.md", build_decision_index(root))
    agents, policy = root / "AGENTS.md", root / "decisions" / "POLICY.md"
    if not (agents.exists() and policy.exists()):
        return False
    new = apply_policy(_read(agents), _read(policy))
    if new == _read(agents):
        return False
    agents.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    a = ap.parse_args()
    if sync(Path(a.root)) and a.stage:
        subprocess.run(["git", "add", "AGENTS.md"], cwd=a.root, check=False)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_sync_docs.py`
Expected: PASS (7 passed).

- [ ] **Step 5: 커밋**

```bash
git add scripts/sync_docs.py tests/test_sync_docs.py
git commit -m "feat: add sync_docs for board, indexes and policy block

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

---

### Task 4: decide.py (결정 제안·확정)

**Files:**
- Create: `scripts/decide.py`, `tests/test_decide.py`

**Interfaces:**
- Consumes: `tools.frontmatter.parse`
- Produces:
  - CLI `python scripts/decide.py new "<제목>" [--modules a,b] [--root PATH]` → `decisions/log/NNNN-<slug>.md` (status: 제안), 생성 경로 출력
  - CLI `python scripts/decide.py accept NNNN --by <이름> [--root PATH]` → status 확정, decided_by, date(오늘) 기록
  - `slugify(title: str) -> str` (소문자, 공백→`-`, 영숫자·한글·`-`만 유지, 최대 40자, 비면 `decision`)

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_decide.py`:
```python
import subprocess
import sys
from datetime import date
from pathlib import Path

from tools.frontmatter import parse

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "decide.py"


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--root", str(root)], capture_output=True, text=True
    )


def test_new_creates_numbered_proposal(tmp_path):
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    r = run(tmp_path, "new", "추적은 Kalman filter", "--modules", "tracking,assess")
    assert r.returncode == 0, r.stderr
    files = list((tmp_path / "decisions" / "log").glob("*.md"))
    assert [f.name for f in files] == ["0001-추적은-kalman-filter.md"]
    meta, body = parse(files[0].read_text(encoding="utf-8"))
    assert meta["status"] == "제안" and meta["decided_by"] is None
    assert meta["modules"] == ["tracking", "assess"]
    for h in ("## 결정", "## 이유", "## 버린 대안", "## 영향"):
        assert h in body
    assert run(tmp_path, "new", "두번째").returncode == 0
    assert (tmp_path / "decisions" / "log" / "0002-두번째.md").exists()


def test_accept_sets_status_owner_and_date(tmp_path):
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    run(tmp_path, "new", "WGS84")
    r = run(tmp_path, "accept", "0001", "--by", "영희")
    assert r.returncode == 0, r.stderr
    meta, _ = parse((tmp_path / "decisions" / "log" / "0001-wgs84.md").read_text(encoding="utf-8"))
    assert meta["status"] == "확정"
    assert meta["decided_by"] == "영희"
    assert meta["date"] == date.today().isoformat()


def test_accept_unknown_id_fails(tmp_path):
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    r = run(tmp_path, "accept", "0042", "--by", "영희")
    assert r.returncode == 1
    assert "0042" in r.stderr
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_decide.py`
Expected: FAIL (스크립트 없음, returncode 2).

- [ ] **Step 3: 구현**

`scripts/decide.py`:
```python
"""Decision records. AI runs `new` (proposal). Only humans run `accept`.

Usage: python scripts/decide.py new "<title>" [--modules a,b]
       python scripts/decide.py accept NNNN --by <name>
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

TEMPLATE = """---
id: {id}
title: {title}
status: 제안            # 제안 / 확정 / 폐기
decided_by: null        # 확정 시 사람 이름
date: {date}
modules: [{modules}]
supersedes: null
---
## 결정

## 이유

## 버린 대안

## 영향
"""


def slugify(title: str) -> str:
    s = re.sub(r"\s+", "-", title.strip().lower())
    s = re.sub(r"[^0-9a-z가-힣-]", "", s).strip("-")[:40]
    return s or "decision"


def cmd_new(log: Path, title: str, modules: str) -> None:
    nums = [int(p.name[:4]) for p in log.glob("[0-9][0-9][0-9][0-9]-*.md")]
    nid = f"{max(nums, default=0) + 1:04d}"
    mods = ", ".join(m.strip() for m in modules.split(",") if m.strip())
    path = log / f"{nid}-{slugify(title)}.md"
    path.write_text(
        TEMPLATE.format(id=nid, title=title, date=date.today().isoformat(), modules=mods),
        encoding="utf-8",
    )
    print(f"제안 생성: {path}  (확정은 사람이 `python scripts/decide.py accept {nid} --by 이름`)")


def cmd_accept(log: Path, nid: str, by: str) -> None:
    matches = list(log.glob(f"{nid}-*.md"))
    if not matches:
        print(f"결정 {nid} 를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)
    p = matches[0]
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"^status:.*$", "status: 확정", text, count=1, flags=re.M)
    text = re.sub(r"^decided_by:.*$", f"decided_by: {by}", text, count=1, flags=re.M)
    text = re.sub(r"^date:.*$", f"date: {date.today().isoformat()}", text, count=1, flags=re.M)
    p.write_text(text, encoding="utf-8")
    print(f"확정: {p}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("title")
    n.add_argument("--modules", default="")
    n.add_argument("--root", default=argparse.SUPPRESS)
    acc = sub.add_parser("accept")
    acc.add_argument("id")
    acc.add_argument("--by", required=True)
    acc.add_argument("--root", default=argparse.SUPPRESS)
    a = ap.parse_args()
    log = Path(a.root) / "decisions" / "log"
    log.mkdir(parents=True, exist_ok=True)
    if a.cmd == "new":
        cmd_new(log, a.title, a.modules)
    else:
        cmd_accept(log, a.id, a.by)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_decide.py`
Expected: PASS (3 passed).

- [ ] **Step 5: 커밋**

```bash
git add scripts/decide.py tests/test_decide.py
git commit -m "feat: add decide script for decision proposals and acceptance

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

---

### Task 5: guard (Claude·Codex 공용 수정 차단)

**Files:**
- Create: `tools/guard/__init__.py`, `tools/guard/check_edit.py`, `tests/test_guard.py`

**Interfaces:**
- Consumes: `tools.spec.spec_actions`
- Produces:
  - CLI `python3 tools/guard/check_edit.py pre|post` (stdin: hook JSON). exit 0 = 허용, exit 2 = 차단(stderr에 이유)
  - 함수: `extract_edits(payload: dict) -> list[Edit]` (`Edit(path: Path, new_text: str, is_new: bool)`), `current_branch(root: Path) -> str`, `allowed(rel: str, branch: str, modules: set[str]) -> bool`, `check_pre(payload: dict, root: Path, branch: str, freeze: bool) -> str | None` (차단 사유 또는 None), `check_post(payload: dict, root: Path, freeze: bool) -> str | None`
  - 환경변수 `KDTH_FREEZE=1`: SPEC 등록·길이 검사를 건너뜀(소유·보호 검사는 유지)

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_guard.py`:
```python
import json
import subprocess
import sys
from pathlib import Path

from tools.guard import check_edit as g

ROOT = Path(__file__).resolve().parent.parent
SPEC = (
    "<!-- prefix: TRK -->\n| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |\n"
    "|---|---|---|---|---|---|---|\n| TRK-01 | predict_tracks | a | b | c | d | 진행중 |\n"
)


def repo(tmp_path: Path) -> Path:
    for m in ("tracking", "assess", "cop-ui"):
        (tmp_path / "modules" / m / "actions").mkdir(parents=True)
    (tmp_path / "modules" / "tracking" / "SPEC.md").write_text(SPEC, encoding="utf-8")
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    return tmp_path


def claude(path: Path, content: str = "x\n", tool: str = "Write") -> dict:
    key = "content" if tool == "Write" else "new_string"
    return {
        "tool_name": tool,
        "cwd": str(path.parent),
        "tool_input": {"file_path": str(path), key: content},
    }


def codex(cwd: Path, patch: str) -> dict:
    return {"tool_name": "apply_patch", "cwd": str(cwd), "tool_input": {"command": patch}}


def test_owner_branch_can_edit_own_module(tmp_path):
    r = repo(tmp_path)
    p = claude(r / "modules/tracking/pipeline.py")
    assert g.check_pre(p, r, "tracking/kalman", False) is None


def test_other_module_blocked(tmp_path):
    r = repo(tmp_path)
    msg = g.check_pre(claude(r / "modules/assess/pipeline.py"), r, "tracking/kalman", False)
    assert msg and "assess" in msg


def test_main_branch_blocks_modules_but_allows_knowledge(tmp_path):
    r = repo(tmp_path)
    assert g.check_pre(claude(r / "modules/tracking/x.py"), r, "main", False)
    assert g.check_pre(claude(r / "knowledge/cards/a.md"), r, "main", False) is None


def test_contracts_branch(tmp_path):
    r = repo(tmp_path)
    assert g.check_pre(claude(r / "contracts/models.py"), r, "contracts/v2", False) is None
    assert g.check_pre(claude(r / "contracts/models.py"), r, "tracking/x", False)


def test_infra_branch_owns_scripts(tmp_path):
    r = repo(tmp_path)
    assert g.check_pre(claude(r / "scripts/ship.sh"), r, "infra/x", False) is None
    assert g.check_pre(claude(r / "tests/test_x.py"), r, "infra/x", False) is None
    assert g.check_pre(claude(r / "scripts/ship.sh"), r, "tracking/x", False)


def test_unregistered_new_action_blocked(tmp_path):
    r = repo(tmp_path)
    msg = g.check_pre(
        claude(r / "modules/tracking/actions/smooth_tracks.py"), r, "tracking/x", False
    )
    assert msg and "new_action.py" in msg
    ok = claude(r / "modules/tracking/actions/predict_tracks.py")
    assert g.check_pre(ok, r, "tracking/x", False) is None


def test_freeze_skips_spec_registration(tmp_path):
    r = repo(tmp_path)
    p = claude(r / "modules/tracking/actions/smooth_tracks.py")
    assert g.check_pre(p, r, "tracking/x", True) is None


def test_protected_files(tmp_path):
    r = repo(tmp_path)
    for rel in (
        ".env",
        "decisions/POLICY.md",
        "tasks/BOARD.md",
        "knowledge/INDEX.md",
        "modules/cop-ui/src/contracts.gen.ts",
        "contracts/schema/track.json",
    ):
        assert g.check_pre(claude(r / rel), r, "infra/x", False), rel


def test_confirmed_decision_protected(tmp_path):
    r = repo(tmp_path)
    d = r / "decisions/log/0001-a.md"
    d.write_text("---\nid: 0001\nstatus: 확정\n---\n", encoding="utf-8")
    assert g.check_pre(claude(d, tool="Edit"), r, "tracking/x", False)


def test_ai_cannot_write_confirmed_status(tmp_path):
    r = repo(tmp_path)
    p = claude(r / "decisions/log/0002-b.md", "---\nstatus: 확정\n---\n")
    assert g.check_pre(p, r, "tracking/x", False)
    p2 = claude(r / "decisions/log/0002-b.md", "---\nstatus: 제안\n---\n")
    assert g.check_pre(p2, r, "tracking/x", False) is None


def test_codex_relative_path_resolves_from_cwd(tmp_path):
    r = repo(tmp_path)
    patch = "*** Begin Patch\n*** Add File: actions/smooth_tracks.py\n+x\n*** End Patch\n"
    msg = g.check_pre(codex(r / "modules/tracking", patch), r, "tracking/x", False)
    assert msg and "smooth_tracks" in msg
    patch2 = "*** Begin Patch\n*** Update File: pipeline.py\n@@\n-a\n+b\n*** End Patch\n"
    assert g.check_pre(codex(r / "modules/tracking", patch2), r, "tracking/x", False) is None
    patch3 = "*** Begin Patch\n*** Update File: ../assess/pipeline.py\n@@\n+b\n*** End Patch\n"
    assert g.check_pre(codex(r / "modules/tracking", patch3), r, "tracking/x", False)


def test_codex_added_confirmed_status_blocked(tmp_path):
    r = repo(tmp_path)
    patch = "*** Begin Patch\n*** Add File: decisions/log/0003-c.md\n+status: 확정\n*** End Patch\n"
    assert g.check_pre(codex(r, patch), r, "tracking/x", False)


def test_path_outside_repo_allowed(tmp_path):
    r = repo(tmp_path / "repo")
    assert g.check_pre(claude(tmp_path / "elsewhere.py"), r, "main", False) is None


def test_post_length_limits(tmp_path):
    r = repo(tmp_path)
    a = r / "modules/tracking/actions/predict_tracks.py"
    a.write_text("x = 1\n" * 81)
    assert "80" in g.check_post(claude(a), r, False)
    a.write_text("x = 1\n" * 80)
    assert g.check_post(claude(a), r, False) is None
    other = r / "modules/tracking/pipeline.py"
    other.write_text("x = 1\n" * 201)
    assert "200" in g.check_post(claude(other), r, False)
    assert g.check_post(claude(other), r, True) is None


def test_branch_during_rebase(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    rb = tmp_path / ".git" / "rebase-merge"
    rb.mkdir()
    (rb / "head-name").write_text("refs/heads/tracking/kalman\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-q", "--allow-empty", "-m", "x"],
        check=True,
        env={
            "GIT_AUTHOR_NAME": "a",
            "GIT_AUTHOR_EMAIL": "a@a",
            "GIT_COMMITTER_NAME": "a",
            "GIT_COMMITTER_EMAIL": "a@a",
            "PATH": "/usr/bin:/bin",
        },
    )
    subprocess.run(["git", "-C", str(tmp_path), "checkout", "-q", "--detach"], check=True)
    assert g.current_branch(tmp_path) == "tracking/kalman"


def test_cli_exit_codes(tmp_path):
    r = repo(tmp_path)
    subprocess.run(["git", "init", "-q", "-b", "main", str(r)], check=True)
    payload = json.dumps(claude(r / "modules/assess/x.py"))
    res = subprocess.run(
        [sys.executable, str(ROOT / "tools/guard/check_edit.py"), "pre"],
        input=payload,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 2 and "assess" in res.stderr
    res = subprocess.run(
        [sys.executable, str(ROOT / "tools/guard/check_edit.py"), "pre"],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_guard.py`
Expected: FAIL — `ImportError: cannot import name 'check_edit' from 'tools.guard'`.

- [ ] **Step 3: 구현**

`tools/guard/__init__.py`: 빈 파일.

`tools/guard/check_edit.py`:
```python
"""Edit guard for Claude Code (Edit/Write) and Codex (apply_patch). Stdlib only.

Usage (hook): python3 tools/guard/check_edit.py pre|post   < hook JSON on stdin
Exit 0 = allow, exit 2 = block (reason on stderr, shown to the AI).
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.spec import spec_actions  # noqa: E402

PROTECTED = [
    ".env",
    ".env.*",
    "decisions/POLICY.md",
    "tasks/BOARD.md",
    "knowledge/INDEX.md",
    "decisions/INDEX.md",
    "contracts/schema/*",
    "modules/cop-ui/src/contracts.gen.ts",
]
ALWAYS = ["knowledge/*", "decisions/log/*"]
INFRA = [
    "AGENTS.md",
    "README.md",
    "pyproject.toml",
    "uv.lock",
    ".gitignore",
    "tests/*",
    "scripts/*",
    "tools/*",
    ".claude/*",
    ".codex/*",
    ".agents/*",
    ".githooks/*",
    "shared/*",
    "demo/*",
    "docs/*",
]
CONTRACTS = ["contracts/*", "modules/cop-ui/src/contracts.gen.ts"]
PATCH_RE = re.compile(r"^\*\*\* (Add|Update|Delete) File: (.+)$|^\*\*\* Move to: (.+)$", re.M)
CONFIRMED_RE = re.compile(r"^\+?status:\s*확정", re.M)


@dataclass
class Edit:
    path: Path
    new_text: str
    is_new: bool


def extract_edits(payload: dict) -> list[Edit]:
    ti = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or os.getcwd())
    fp = ti.get("file_path") or ti.get("notebook_path")
    if fp:
        p = (cwd / fp).resolve()
        text = ti.get("content") or ti.get("new_string") or ""
        text += "".join(e.get("new_string", "") for e in ti.get("edits") or [])
        return [Edit(p, text, not p.exists())]
    cmd = ti.get("command")
    if isinstance(cmd, list):
        cmd = "\n".join(cmd)
    if not isinstance(cmd, str) or "*** Begin Patch" not in cmd:
        return []
    edits, blocks = [], re.split(r"(?=^\*\*\* (?:Add|Update|Delete) File: )", cmd, flags=re.M)
    for block in blocks:
        for m in PATCH_RE.finditer(block):
            rel = m.group(2) or m.group(3)
            edits.append(Edit((cwd / rel.strip()).resolve(), block, m.group(1) == "Add"))
    return edits


def current_branch(root: Path) -> str:
    for d in ("rebase-merge", "rebase-apply"):
        head = root / ".git" / d / "head-name"
        if head.exists():
            return head.read_text().strip().removeprefix("refs/heads/")
    r = subprocess.run(
        ["git", "-C", str(root), "branch", "--show-current"], capture_output=True, text=True
    )
    return r.stdout.strip()


def allowed(rel: str, branch: str, modules: set[str]) -> bool:
    if any(fnmatch(rel, pat) for pat in ALWAYS):
        return True
    prefix = branch.split("/", 1)[0] if "/" in branch else ""
    if prefix == "infra":
        return any(fnmatch(rel, pat) for pat in INFRA)
    if prefix == "contracts":
        return any(fnmatch(rel, pat) for pat in CONTRACTS)
    return prefix in modules and rel.startswith(f"modules/{prefix}/")


def _block_reason(rel: str, branch: str) -> str:
    owner = rel.split("/")[1] if rel.startswith("modules/") and rel.count("/") >= 2 else None
    need = f"`{owner}/<주제>`" if owner else "`infra/<주제>` 또는 `contracts/<주제>`"
    return (
        f"[guard] 현재 브랜치 `{branch or '(없음)'}`에서는 `{rel}`을 수정할 수 없습니다. "
        f"이 파일은 {need} 브랜치 담당입니다. 다른 사람 영역이면 담당자에게 요청하세요."
    )


def check_pre(payload: dict, root: Path, branch: str, freeze: bool) -> str | None:
    modules = (
        {p.name for p in (root / "modules").iterdir() if p.is_dir()}
        if (root / "modules").is_dir()
        else set()
    )
    for e in extract_edits(payload):
        try:
            rel = e.path.relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        if any(fnmatch(rel, pat) for pat in PROTECTED):
            return (
                f"[guard] `{rel}`은 보호 파일입니다(자동 생성·정책·비밀값). 직접 수정하지 마세요."
            )
        if rel.startswith("decisions/log/"):
            if e.path.exists() and CONFIRMED_RE.search(e.path.read_text(encoding="utf-8")):
                return f"[guard] `{rel}`은 확정된 결정입니다. 바꾸려면 사람에게 요청하세요."
            if CONFIRMED_RE.search(e.new_text):
                return "[guard] AI는 결정을 `확정`으로 쓸 수 없습니다. `제안`으로 두고 사람에게 확정을 요청하세요."
        if not allowed(rel, branch, modules):
            return _block_reason(rel, branch)
        m = re.fullmatch(r"modules/([^/]+)/actions/([a-z0-9_]+)\.py", rel)
        if m and e.is_new and not freeze and m.group(2) != "__init__":
            if m.group(2) not in spec_actions(root / "modules" / m.group(1) / "SPEC.md"):
                return (
                    f"[guard] 액션 `{m.group(2)}`이 modules/{m.group(1)}/SPEC.md에 없습니다. "
                    f'`python scripts/new_action.py {m.group(1)} {m.group(2)} "설명"`으로 만드세요.'
                )
    return None


def check_post(payload: dict, root: Path, freeze: bool) -> str | None:
    if freeze:
        return None
    for e in extract_edits(payload):
        if not e.path.exists() or e.path.suffix not in (".py", ".ts", ".tsx"):
            continue
        rel = (
            e.path.relative_to(root.resolve()).as_posix()
            if e.path.is_relative_to(root.resolve())
            else ""
        )
        limit = 80 if re.fullmatch(r"modules/[^/]+/actions/[^/]+\.py", rel) else 200
        n = len(e.path.read_text(encoding="utf-8").splitlines())
        if rel and n > limit and "knowledge/spikes/" not in rel:
            return (
                f"[guard] `{rel}`이 {n}줄로 기준 {limit}줄을 넘었습니다. "
                "역할별로 액션(새 SPEC 행)이나 파일을 쪼개세요."
            )
    return None


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "pre"
    try:
        payload = json.loads(sys.stdin.read())
    except ValueError:
        sys.exit(0)
    cwd = payload.get("cwd") or os.getcwd()
    r = subprocess.run(
        ["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    if r.returncode != 0:
        sys.exit(0)
    root = Path(r.stdout.strip())
    freeze = os.environ.get("KDTH_FREEZE") == "1"
    msg = (
        check_pre(payload, root, current_branch(root), freeze)
        if mode == "pre"
        else check_post(payload, root, freeze)
    )
    if msg:
        print(msg, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_guard.py`
Expected: PASS (17 passed). `test_branch_during_rebase`가 실패하면 `current_branch`의 rebase 디렉터리 처리 확인.

- [ ] **Step 5: 실행 시간 확인**

Run: `echo '{"tool_name":"Write","cwd":"'$PWD'","tool_input":{"file_path":"'$PWD'/modules/x.py","content":"a"}}' | /usr/bin/time -f %e python3 tools/guard/check_edit.py pre; echo exit=$?`
Expected: 경과 시간 0.1 이하, `exit=2`(main 브랜치에서 modules 수정 차단).

- [ ] **Step 6: 커밋**

```bash
git add tools/guard tests/test_guard.py
git commit -m "feat: add edit guard shared by Claude Code and Codex hooks

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

---

### Task 6: 커밋 검사 (check_specs, check_imports, check.sh, git hooks)

**Files:**
- Create: `tools/check_specs.py`, `tools/check_imports.py`, `scripts/check.sh`, `.githooks/pre-commit`, `.githooks/post-merge`, `.githooks/post-checkout`, `.githooks/post-rewrite`, `tests/test_check_specs.py`, `tests/test_check_imports.py`

**Interfaces:**
- Consumes: `tools.spec.parse_spec`
- Produces:
  - `tools.check_specs.problems(root: Path) -> list[str]`, CLI `python tools/check_specs.py [--root]` (exit 1 if problems, `KDTH_FREEZE=1`이면 경고만 출력하고 exit 0)
  - `tools.check_imports.problems(root: Path) -> list[str]`, CLI 동일 (freeze와 무관하게 차단)
  - `scripts/check.sh [--all]`: 커밋 검사. `--all`이면 전체 pytest 추가

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_check_specs.py`:
```python
from pathlib import Path

from tools.check_specs import problems

HDR = (
    "<!-- prefix: TRK -->\n| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |\n"
    "|---|---|---|---|---|---|---|\n"
)


def mod(root: Path, rows: str) -> Path:
    m = root / "modules" / "tracking"
    (m / "actions").mkdir(parents=True)
    (m / "tests").mkdir()
    (m / "__init__.py").write_text("")
    (m / "actions" / "__init__.py").write_text("")
    (m / "SPEC.md").write_text(HDR + rows, encoding="utf-8")
    return m


def test_clean_module_has_no_problems(tmp_path):
    m = mod(tmp_path, "| TRK-01 | predict_tracks | a | b | c | d | 완료 |\n")
    (m / "actions" / "predict_tracks.py").write_text("x = 1\n")
    (m / "tests" / "test_predict_tracks.py").write_text("x = 1\n")
    assert problems(tmp_path) == []


def test_unregistered_action_and_missing_test(tmp_path):
    m = mod(tmp_path, "")
    (m / "actions" / "smooth_tracks.py").write_text("x = 1\n")
    out = problems(tmp_path)
    assert any("SPEC.md에 없는 액션" in p and "smooth_tracks" in p for p in out)
    assert any("테스트 파일" in p and "test_smooth_tracks.py" in p for p in out)


def test_spec_row_without_file_only_ok_when_planned(tmp_path):
    mod(
        tmp_path,
        "| TRK-01 | a_b | . | . | . | . | 예정 |\n| TRK-02 | c_d | . | . | . | . | 완료 |\n",
    )
    out = problems(tmp_path)
    assert len(out) == 1 and "c_d" in out[0]


def test_length_limits(tmp_path):
    m = mod(tmp_path, "| TRK-01 | big_action | a | b | c | d | 완료 |\n")
    (m / "actions" / "big_action.py").write_text("x = 1\n" * 81)
    (m / "tests" / "test_big_action.py").write_text("x = 1\n")
    (m / "pipeline.py").write_text("x = 1\n" * 201)
    out = problems(tmp_path)
    assert any("big_action.py" in p and "80" in p for p in out)
    assert any("pipeline.py" in p and "200" in p for p in out)


def test_ts_module_without_init_is_length_checked_only(tmp_path):
    ui = tmp_path / "modules" / "cop-ui" / "src"
    ui.mkdir(parents=True)
    (ui / "App.tsx").write_text("x\n" * 201)
    (tmp_path / "modules" / "cop-ui" / "node_modules" / "z").mkdir(parents=True)
    (tmp_path / "modules" / "cop-ui" / "node_modules" / "z" / "big.ts").write_text("x\n" * 999)
    out = problems(tmp_path)
    assert len(out) == 1 and "App.tsx" in out[0]
```

`tests/test_check_imports.py`:
```python
from pathlib import Path

from tools.check_imports import problems


def write(root: Path, rel: str, code: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(code)


def test_public_api_imports_ok(tmp_path):
    write(
        tmp_path,
        "modules/gateway/pipeline.py",
        "from modules.tracking import update\nfrom modules import sim\nimport contracts.models\n"
        "from shared.geo import distance_m\nfrom modules.gateway.actions.x import x\n",
    )
    assert problems(tmp_path) == []


def test_reaching_into_other_module_internals_blocked(tmp_path):
    write(tmp_path, "modules/gateway/pipeline.py", "from modules.tracking.actions.a import a\n")
    write(tmp_path, "modules/assess/x.py", "import modules.tracking.pipeline\n")
    out = problems(tmp_path)
    assert len(out) == 2 and all("modules.tracking" in p for p in out)


def test_knowledge_import_blocked_and_shared_cannot_import_modules(tmp_path):
    write(tmp_path, "modules/sim/x.py", "from knowledge.spikes.t import y\n")
    write(tmp_path, "shared/geo2.py", "from modules.sim import x\n")
    write(tmp_path, "contracts/m.py", "import modules\n")
    assert len(problems(tmp_path)) == 3


def test_relative_imports_inside_module_ok(tmp_path):
    write(tmp_path, "modules/sim/pipeline.py", "from .actions.a import a\n")
    assert problems(tmp_path) == []
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_check_specs.py tests/test_check_imports.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.check_specs'`.

- [ ] **Step 3: 구현**

`tools/check_specs.py`:
```python
"""Commit check: every action is in SPEC.md and has a test; file length limits. Stdlib only."""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.spec import parse_spec  # noqa: E402

SKIP_DIRS = {"node_modules", "dist", ".venv", "__pycache__", "spikes"}
CODE_DIRS = ["modules", "shared", "contracts", "scripts", "tools"]
GENERATED = {"contracts.gen.ts"}


def _spec_problems(mod: Path) -> list[str]:
    out = []
    rows = (
        parse_spec((mod / "SPEC.md").read_text(encoding="utf-8"))[1]
        if (mod / "SPEC.md").exists()
        else []
    )
    registered = {r.action: r for r in rows}
    files = {p.stem for p in (mod / "actions").glob("*.py") if p.stem != "__init__"}
    for name in sorted(files - registered.keys()):
        out.append(
            f"modules/{mod.name}/actions/{name}.py: SPEC.md에 없는 액션입니다 (scripts/new_action.py 사용)."
        )
    for name in sorted(files):
        if not (mod / "tests" / f"test_{name}.py").exists():
            out.append(
                f"modules/{mod.name}: 액션 {name}의 테스트 파일 tests/test_{name}.py가 없습니다."
            )
    for name, row in registered.items():
        if name not in files and row.status != "예정":
            out.append(
                f"modules/{mod.name}/SPEC.md: {row.id} {name} 상태가 '{row.status}'인데 액션 파일이 없습니다."
            )
    return out


def _length_problems(root: Path) -> list[str]:
    out = []
    for d in CODE_DIRS:
        for p in (root / d).rglob("*"):
            if p.suffix not in (".py", ".ts", ".tsx") or p.name in GENERATED:
                continue
            if SKIP_DIRS & set(p.relative_to(root).parts):
                continue
            rel = p.relative_to(root).as_posix()
            limit = (
                80
                if p.parent.name == "actions" and rel.startswith("modules/") and p.suffix == ".py"
                else 200
            )
            n = len(p.read_text(encoding="utf-8").splitlines())
            if n > limit:
                out.append(f"{rel}: {n}줄 (기준 {limit}줄). 쪼개세요.")
    return out


def problems(root: Path) -> list[str]:
    out = []
    for mod in sorted((root / "modules").glob("*/")):
        if (mod / "__init__.py").exists():
            out += _spec_problems(mod)
    return out + _length_problems(root)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    found = problems(Path(ap.parse_args().root))
    if not found:
        return
    freeze = os.environ.get("KDTH_FREEZE") == "1"
    print(("[경고] " if freeze else "[check_specs] ") + "\n".join(found), file=sys.stderr)
    sys.exit(0 if freeze else 1)


if __name__ == "__main__":
    main()
```

`tools/check_imports.py`:
```python
"""Commit check: module boundaries via AST. Stdlib only."""

import argparse
import ast
import sys
from pathlib import Path

SKIP = {"node_modules", ".venv", "__pycache__", "dist"}


def _imports(tree: ast.AST) -> list[str]:
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.append(node.module)
    return names


def _violation(rel: Path, name: str) -> str | None:
    parts, top = name.split("."), rel.parts[0]
    if parts[0] == "knowledge":
        return "knowledge(실험 코드·문서)는 import할 수 없습니다"
    if top in ("shared", "contracts") and parts[0] == "modules":
        return f"{top}는 modules를 import할 수 없습니다"
    if top == "modules" and parts[0] == "modules" and len(parts) >= 3 and parts[1] != rel.parts[1]:
        return f"다른 모듈 내부입니다. `from modules.{parts[1]} import ...`(공개 API)만 쓰세요"
    return None


def problems(root: Path) -> list[str]:
    out = []
    for top in ("modules", "shared", "contracts"):
        for p in (root / top).rglob("*.py"):
            rel = p.relative_to(root)
            if SKIP & set(rel.parts):
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
            except SyntaxError as e:
                out.append(f"{rel}: 문법 오류 {e.msg} (line {e.lineno})")
                continue
            for name in _imports(tree):
                why = _violation(rel, name)
                if why:
                    out.append(f"{rel.as_posix()}: import {name} — {why}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    found = problems(Path(ap.parse_args().root))
    if found:
        print("[check_imports]\n" + "\n".join(found), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

`scripts/check.sh`:
```bash
#!/usr/bin/env bash
# Commit check (target < 2s). Usage: scripts/check.sh [--all]
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=".venv/bin/python"; [ -x "$PY" ] || PY="python3"

staged_py=$(git diff --cached --name-only --diff-filter=ACM -- '*.py' | grep -v '^knowledge/spikes/' || true)
if [ -n "$staged_py" ]; then
  .venv/bin/ruff check --fix --quiet $staged_py
  .venv/bin/ruff format --quiet $staged_py
  git add $staged_py
fi

"$PY" tools/check_imports.py
"$PY" tools/check_specs.py

if git diff --cached --name-only | grep -q '^contracts/models.py$'; then
  "$PY" scripts/gen_contracts.py
  git add contracts/schema modules/cop-ui/src/contracts.gen.ts 2>/dev/null || true
fi

"$PY" scripts/sync_docs.py --stage

if [ "${1:-}" = "--all" ]; then
  .venv/bin/pytest
fi
```

`.githooks/pre-commit`:
```bash
#!/usr/bin/env bash
exec "$(git rev-parse --show-toplevel)/scripts/check.sh"
```

`.githooks/post-merge`, `.githooks/post-checkout`, `.githooks/post-rewrite` (세 파일 같은 내용):
```bash
#!/usr/bin/env bash
root="$(git rev-parse --show-toplevel)"
py="$root/.venv/bin/python"; [ -x "$py" ] || py=python3
"$py" "$root/scripts/sync_docs.py" >/dev/null 2>&1 || true
```

Run: `chmod +x scripts/check.sh .githooks/*`

참고: `scripts/gen_contracts.py`는 Task 11에서 만든다. 그 전까지 `contracts/models.py`를 커밋하면 check.sh가 실패하므로, Task 11 전에는 models.py를 수정하지 않는다.

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_check_specs.py tests/test_check_imports.py`
Expected: PASS (9 passed).

- [ ] **Step 5: git hook 연결 후 실제 커밋으로 시간 확인**

```bash
git config core.hooksPath .githooks
git add tools/check_specs.py tools/check_imports.py scripts/check.sh .githooks tests/test_check_specs.py tests/test_check_imports.py
time git commit -m "feat: add commit checks and git hooks

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```
Expected: 커밋 성공, `real` 2초 이하.

---

---

### Task 7: 규칙·안내 문서와 저장소 골격

**Files:**
- Create: `AGENTS.md`, `README.md`, `docs/problem.md`, `docs/glossary.md`, `decisions/POLICY.md`, `decisions/log/.gitkeep`, `knowledge/inbox/.gitkeep`, `knowledge/cards/stone-soup-tracker-components.md`, `knowledge/spikes/.gitkeep`, `demo/BUILT_HERE.md`, `demo/RUNBOOK.md`, `tasks/.gitkeep`, `tests/test_docs.py`

**Interfaces:**
- Consumes: `scripts/sync_docs.py` (정책 구간 채움)
- Produces: AGENTS.md의 `<!-- POLICY:BEGIN -->`/`<!-- POLICY:END -->` 구간, 모듈 소유표

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_docs.py`:
```python
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_root_agents_md_limits_and_markers():
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 150
    assert "<!-- POLICY:BEGIN -->" in text and "<!-- POLICY:END -->" in text
    assert "knowledge/INDEX.md" in text and "decisions/INDEX.md" in text


def test_module_agents_md_limit():
    for p in (ROOT / "modules").glob("*/AGENTS.md"):
        assert len(p.read_text(encoding="utf-8").splitlines()) <= 40, p


def test_policy_synced_into_agents():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "인터넷 없이" in agents


def test_problem_doc_lists_t1_problems():
    text = (ROOT / "docs/problem.md").read_text(encoding="utf-8")
    for pid in ("T1-1", "T1-2", "T1-3", "T1-4"):
        assert pid in text
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_docs.py`
Expected: FAIL — `FileNotFoundError: AGENTS.md`.

- [ ] **Step 3: 문서 작성**

`AGENTS.md`:
```markdown
# d4d-edth-seoul-2026 — 에이전트 공통 규칙

Korean Defense Tech Hackathon 2026 (D4D × EDTH SEOUL) 팀 저장소. 24시간 안에 **로컬에서 작동하는 데모**를 만든다(NO SLIDES).
설계: `docs/superpowers/specs/2026-10-07-hackathon-repo-structure-design.md`. 문제: `docs/problem.md`.

## 작업 시작 전에 반드시 읽을 것
1. `decisions/INDEX.md` — 사람이 확정한 결정. **반드시 따른다.**
2. `knowledge/INDEX.md` — 이미 조사한 지식. 관련 카드만 연다. 같은 조사를 반복하지 않는다.
3. 작업할 모듈의 `modules/<m>/AGENTS.md`와 `modules/<m>/SPEC.md`.

## 우선순위
확정 결정·정책 > SPEC.md > 지식 카드 > 너의 판단.
확정 결정과 다르게 해야 한다고 판단되면 **멈추고 사람에게 묻는다.**

## 정책 (decisions/POLICY.md 자동 복사본 — 여기서 수정하지 말 것)
<!-- POLICY:BEGIN -->
<!-- POLICY:END -->

## 구조
- `contracts/models.py` 모듈 간 데이터 형식(pydantic). 예시: `contracts/examples/*.json`. 리드만 수정.
- `modules/<m>/` 파이프라인 모듈: sim → sensing → tracking → assess → respond → gateway → cop-ui.
- `shared/` 최소 공통 코드(좌표). `knowledge/` 조사 지식. `decisions/` 사람의 결정. `demo/` 시연.

## 액션 규칙 (1 액션 = 1 파일 = 1 테스트)
- 새 동작은 **반드시** `/new-action` 또는 `python scripts/new_action.py <m> <verb_noun> "<설명>"`으로 시작한다.
  SPEC.md에 없는 액션 파일은 guard가 막는다.
- 액션 파일: 공개 함수 1개, 이름 = 파일 이름, 80줄 이하, 입력·출력 타입 명시.
- 다른 파일(.py/.ts/.tsx)은 200줄 이하. 넘으면 쪼갠다.
- `pipeline.py`는 액션을 순서대로 부르기만 한다(로직 금지).
- 다른 모듈은 `from modules.<m> import <공개 API>`로만 쓴다. 내부(`modules.<m>.actions...`) import 금지.
- 테스트 먼저: 생성된 실패 테스트를 실제 동작 테스트로 바꾸고, 통과시킨다.

## 소유 (브랜치 이름 = 수정 가능 범위)
| 브랜치 | 수정 가능 | 담당 |
|---|---|---|
| `<모듈>/<주제>` | `modules/<모듈>/**`, `knowledge/**`, `decisions/log/**`(제안만) | 아래 표 |
| `contracts/<주제>` | `contracts/**` | 리드 |
| `infra/<주제>` | AGENTS.md, scripts, tools, 설정, shared, demo, docs | 리드 |

| 모듈 | 담당 |
|---|---|
| contracts, gateway, demo, infra | 리드 |
| sim, sensing, edge | 팀원 2 |
| tracking, assess, respond | 팀원 3 |
| cop-ui | 팀원 4 |

남의 영역을 고쳐야 하면 고치지 말고 담당자에게 요청할 내용을 정리해 사람에게 보여준다.

## 명령
- 설치·브랜치: `scripts/setup.sh <모듈>`
- 개발 실행: `scripts/dev.sh` / 시연 실행: `scripts/demo.sh`
- 모듈 테스트: `uv run pytest modules/<m>`
- 반영: `scripts/ship.sh` (/ship) — 최신 main 반영 + 변경 모듈 테스트 + 데모 smoke test + push
- 지식 정리: /kb-save · 결정 제안: /decide

## 지식과 결정
- 조사 결과는 답변으로만 끝내지 말고 `knowledge/inbox/`에 원문을 넣고 /kb-save로 카드를 만든다. 출처 없는 내용은 `confidence: 추정`.
- 사람이 결정을 말하면 /decide로 `제안` 문서를 만들고 확정을 요청한다. 너는 `확정`으로 바꿀 수 없다.

## 하지 말 것
- CLAUDE.md / CLAUDE.local.md 생성 (Claude가 이 파일을 무시하게 됨)
- 자동 생성 파일 수정: `tasks/BOARD.md`, `knowledge/INDEX.md`, `decisions/INDEX.md`, `contracts/schema/`, `contracts.gen.ts`
- 비공개·수출통제 데이터, 실제 개인 식별 정보 사용
- 시연 경로에서 외부 네트워크 호출

## 시간이 급할 때
- `git commit --no-verify` 허용(ship의 smoke test는 유지).
- 일요일 06:00 이후 `KDTH_FREEZE=1`: 구조 검사는 경고만, smoke test만 차단.
```

`decisions/POLICY.md`:
```markdown
# 정책

1. 시연은 인터넷 없이 동작한다. 지도 타일은 로컬 파일을 쓰고, 시연 경로에서 외부 API를 호출하지 않는다.
2. 공개 데이터·가상(synthetic) 데이터만 쓴다. 비밀·수출통제 정보, 실제 개인 식별·표적화 금지.
3. 좌표는 WGS84 위경도(도), 고도는 m, 시간은 UTC epoch 밀리초(`t_ms`).
4. API 키·비밀값은 커밋하지 않는다(`.env`는 gitignore).
5. 해커톤 중 새로 만든 부분은 `demo/BUILT_HERE.md`에 기록한다.
```

`docs/problem.md`: 아래 내용을 그대로 쓴다(참가자 안내 시트 B-1, B-2 탭의 T1 부분 요약).
```markdown
# 해커톤 문제 (T1 중심)

출처: 참가자 안내 시트 https://docs.google.com/spreadsheets/d/1z-knlD7tXlieexed2eHruSseUu6dBYt3K-mT5NAbXHg (B-1, B-2 탭)

## 공통 규칙
- 일정: 10/10(토) 10:00 개발 시작 → 10/11(일) 10:00 제출(d4d.tech) → 10:30 1차 현장 심사(팀당 5분) → 14:30 2차 메인 스테이지 피칭.
- 팀당 최대 4명, 트랙 하나의 문제 하나. 트랙 피켓(T1 카키)을 테이블에 비치.
- NO SLIDES: 작동하는 결과물로 증명. 기존 기술을 써도 되지만 해커톤에서 새로 만든 부분을 구분해 발표.
- 공개·가상 데이터만. 비밀·수출통제 정보, 특정 개인 식별·표적화 금지.
- 스페셜 챌린지: SC1 CLIKA BYOD On-device AI(같은 앱을 2종 이상 기기에서 구동 시 우대), SC2 NUCODE Board, SC3 WAY to OREGON(T1 결과물 중심, 미국 Oregon UAS Accelerator 연결).

## T1 Autonomy, Unmanned Systems & Counter-UAS (자율·무인 시스템 및 대드론)
| No. | 유형 | 문제 | SC |
|---|---|---|---|
| T1-1 | 범용 | 1인 다중 무인기 동시 통제 (Multi-UxV Control): 단일 운용자가 공중·지상·해상 이종 무인체계 3대 이상을 동시에 임무 부여·감시·통제. 인지부하 최소화. | — |
| T1-2 | 특수상황 | 산악·도심 혼재 지형 자율 드론 운용 (Terrain-Aware Autonomy): GPS 음영·통신 단절·전자전 속 지형 활용 이동·통신 유지·임무 지속. | SC1 |
| T1-3 | 특수상황 | 수도권 영공 소형드론·풍선 침투 대응 (Gray-zone C-UAS): RF·EO/IR·레이더 융합 저신호 탐지, 도심 오탐 저감, 드론/풍선/조류 분류·위협도, 부수피해 고려 대응(소프트킬/하드킬) 추천, 다중 표적 추적·경보 시각화. | SC1+SC2 |
| T1-4 | 범용 | 무선침묵 환경 피아식별 (Radio-silent IFF): 저방출 피아식별 프로토콜, 2-컴포넌트 challenge-response, MITM·replay 방어, 식별 실패 시 fail-safe 교전규칙 연동. | SC2 |

## 이 저장소의 기본 가정
T1-3을 기준으로 골격을 만들었다. 다른 T1 문제로 바꿀 때 교체할 모듈은 설계 문서 3.1절 참고.
```

`docs/glossary.md`:
```markdown
# 용어집 (T1 관련, 참가자 안내 시트 B-3 발췌)

| 용어 | 영문 | 설명 |
|---|---|---|
| UxV | Unmanned x Vehicle | 공중·지상·해상 무인 이동체 총칭 |
| UAS | Unmanned Aircraft System | 드론 기체 + 지상통제 + 데이터링크 |
| C-UAS | Counter-UAS | 적 무인기 탐지·추적·식별·무력화 체계 |
| LSS | Low, Slow, Small | 저고도·저속·저신호 소형 비행체 |
| 소프트킬 / 하드킬 | Soft-kill / Hard-kill | 전자적 무력화 vs 물리적 파괴 |
| IFF | Identification Friend or Foe | 피아식별 |
| EW / 재밍 | Electronic Warfare / Jamming | 전자전 / 전파 방해 |
| EMCON | Emission Control | 탐지 회피를 위한 전파 방출 통제 |
| EO/IR | Electro-Optical / Infrared | 주간 영상 / 열영상 센서 |
| RF | Radio Frequency | 무선 주파수 (드론 조종 신호 탐지 대상) |
| ROE | Rules of Engagement | 교전규칙 |
| 부수적 피해 | Collateral Damage | 목표 외 민간·아군·시설 피해 |
| 회색지대 | Gray-zone | 평시도 전시도 아닌 영역의 강압·도발 |
| MUM-T | Manned-Unmanned Teaming | 유무인 복합 운용 |
| COP | Common Operational Picture | 공통상황도 |
| MITM / Replay | Man-in-the-Middle / Replay Attack | 중간자 공격 / 재전송 공격 |
| Fail-safe | Fail-safe | 실패 시 안전한 쪽으로 동작 |
```

`knowledge/cards/stone-soup-tracker-components.md`:
```markdown
---
id: stone-soup-tracker-components
title: 다중표적 추적기의 부품 분리 (Stone Soup)
summary: 추적기는 예측·연관·갱신·생성·삭제 부품으로 나누면 각각 독립 구현·교체할 수 있다
tags: [tracking, architecture]
modules: [tracking]
confidence: 확인됨
sources: [https://stonesoup.readthedocs.io/en/v1.9.1/stonesoup.tracker.html]
author: 리드
---
## 결론
tracking 모듈 액션을 predict_tracks, associate_detections, update_tracks, initiate_tracks, delete_stale_tracks로 나눈다.

## 근거
Stone Soup의 MultiTargetTracker는 data_associator로 예측과 탐지를 짝짓고, 짝이 있으면 updater, 없으면 예측값으로 갱신한 뒤 deleter로 삭제하고 남은 탐지는 initiator로 새 표적을 만든다.

## 코드에 적용하는 법
각 부품을 액션 파일 하나로 두고 pipeline.py에서 위 순서로 호출한다. 알고리즘 교체(최근접 → JPDA 등)는 해당 액션만 바꾼다.

## 관련 카드
```

`demo/BUILT_HERE.md`:
```markdown
# 해커톤 중 새로 만든 부분

심사에서 "해커톤에서 새로 만든 부분"을 구분해 발표해야 한다. 기능을 완성할 때마다 한 줄씩 추가한다.

## 대회 전에 준비한 것 (새로 만든 것 아님)
- 저장소 골격, 규칙 문서, 검사 스크립트, 가짜 로직 walking skeleton, 오프라인 지도 타일

## 해커톤 중 만든 것
| 시각 | 모듈 | 내용 | 담당 |
|---|---|---|---|
```

`demo/RUNBOOK.md`:
```markdown
# 시연 절차 (5분)

## 사전 점검 (심사 30분 전)
1. 시연 노트북 전원·HDMI 연결, 화면 해상도 확인
2. 와이파이 끈 상태에서 `scripts/demo.sh` 실행 → 브라우저 http://localhost:8000
3. 지도 배경·표적·경보가 보이는지 확인
4. 백업 영상 파일 위치 확인: `demo/backup.mp4`

## 순서
| 시간 | 내용 |
|---|---|
| 0:00–0:30 | 문제 한 줄 소개 |
| 0:30–3:30 | 라이브 데모 (시나리오 재생, 분류·위협도·대응 추천 설명) |
| 3:30–4:30 | 해커톤 중 새로 만든 부분 (BUILT_HERE.md) |
| 4:30–5:00 | 다음 단계 |

## 실패 시
- 화면이 안 뜨면: 터미널 오류 확인 → `scripts/demo.sh` 재실행 (10초)
- 그래도 안 되면 백업 영상 재생
```

Run: `touch decisions/log/.gitkeep knowledge/inbox/.gitkeep knowledge/spikes/.gitkeep tasks/.gitkeep`

`README.md`:
```markdown
# d4d-edth-seoul-2026

Korean Defense Tech Hackathon 2026 (D4D × EDTH SEOUL) 팀 저장소.

## 시작하기 (팀원 1회)
1. Claude Code를 최신으로 업데이트하고 한 번 실행해 둔다 (v2.1.281 이상). Codex 사용자는 `/hooks`에서 저장소 hook을 신뢰 승인한다.
2. `git clone https://github.com/kth9245/d4d-edth-seoul-2026 && cd d4d-edth-seoul-2026`
3. `scripts/setup.sh <내 모듈>` — 의존성 설치, git hook 연결, `<모듈>/work` 브랜치 생성
4. AI 도구 실행: Claude Code는 저장소 루트에서, Codex는 `cd modules/<내 모듈> && codex`

## 매일 쓰는 명령
| 명령 | 하는 일 |
|---|---|
| `/new-action` | 액션 시작 (SPEC 행 + 파일 + 실패 테스트) |
| `git commit` | 2초 검사 후 커밋 |
| `scripts/ship.sh` | main 반영 + 테스트 + smoke test + push |
| `scripts/dev.sh` | 개발 실행 (http://localhost:5173) |
| `scripts/demo.sh` | 시연 실행 (http://localhost:8000, 오프라인) |

규칙 전체: `AGENTS.md`. 설계: `docs/superpowers/specs/`.
```

- [ ] **Step 4: 정책 구간 채우기**

Run: `uv run python scripts/sync_docs.py`
Expected: AGENTS.md의 POLICY 구간에 정책 5줄이 들어간다. `tasks/BOARD.md`, `knowledge/INDEX.md`, `decisions/INDEX.md` 생성(gitignore 대상).

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest tests/test_docs.py`
Expected: PASS (4 passed).

- [ ] **Step 6: 커밋**

```bash
git add AGENTS.md README.md docs/problem.md docs/glossary.md decisions knowledge demo tasks/.gitkeep tests/test_docs.py
git commit -m "docs: add agent rules, policy, problem brief and repo skeleton docs

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```
Expected: pre-commit 통과. `git status`에 BOARD.md·INDEX.md가 나타나지 않음(gitignore).

---

---

### Task 8: sim, sensing 모듈

**Files:**
- Create: `modules/sim/{__init__.py,AGENTS.md,SPEC.md,pipeline.py,types.py}`, `modules/sim/actions/{__init__.py,load_scenario.py,object_positions.py,emit_detections.py}`, `modules/sim/tests/{__init__.py,test_load_scenario.py,test_object_positions.py,test_emit_detections.py}`, `modules/sensing/{__init__.py,AGENTS.md,SPEC.md,pipeline.py}`, `modules/sensing/actions/{__init__.py,drop_invalid_detections.py}`, `modules/sensing/tests/{__init__.py,test_drop_invalid_detections.py}`, `demo/scenarios/seoul_mixed.yaml`

**Interfaces:**
- Consumes: `contracts.models.Detection, SensorType`, `shared.geo.offset_latlon`
- Produces:
  - `modules.sim.types`: `Origin(lat: float, lon: float)`, `SimObject(id: str, kind: Literal["drone","balloon","bird"], start_east_m: float, start_north_m: float, alt_m: float = Field(ge=0), vel_east_mps: float, vel_north_mps: float, appear_s: float = Field(default=0, ge=0))`, `Scenario(name: str, start_ms: int, duration_s: float = Field(gt=0), step_ms: int = Field(gt=0), origin: Origin, objects: list[SimObject])`, `TruthPoint(object_id: str, kind: str, lat: float, lon: float, alt_m: float)`
  - `modules.sim` 공개 API: `load_scenario(path: str | Path) -> Scenario`, `simulate(scenario: Scenario, t_ms: int, seed: int = 0) -> list[Detection]`, `Scenario`
  - `modules.sensing` 공개 API: `normalize(detections: list[Detection]) -> list[Detection]`
  - 시나리오 YAML 형식(`demo/scenarios/seoul_mixed.yaml`)

- [ ] **Step 1: 모듈 문서와 SPEC 작성**

`modules/sim/AGENTS.md`:
```markdown
# sim — 가상 시나리오·센서 데이터 생성

- 책임: 시나리오 YAML을 읽어 시각 t_ms의 가상 탐지(Detection) 목록을 만든다. 실제 데이터 금지(가상만).
- 입력: `demo/scenarios/*.yaml` (형식: `modules/sim/types.py`의 Scenario)
- 출력: `list[contracts.models.Detection]`
- 공개 API(`__init__.py`): `load_scenario`, `simulate`, `Scenario`
- 같은 seed와 t_ms면 항상 같은 결과(재현 가능)여야 한다.
- 담당: 팀원 2. 브랜치 `sim/<주제>`.
```

`modules/sim/SPEC.md`:
```markdown
<!-- prefix: SIM -->
# sim SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| SIM-01 | load_scenario | path | Scenario | 잘못된 값은 로딩 시 ValueError로 위치와 이유 표시 | 리드 | 완료 |
| SIM-02 | object_positions | Scenario, t_ms | list[TruthPoint] | 등속 이동, appear_s 이전 객체 제외 | 리드 | 완료 |
| SIM-03 | emit_detections | list[TruthPoint], t_ms, seed | list[Detection] | 레이더 탐지 1개/객체, 위치 잡음 σ≈3m, 재현 가능 | 리드 | 완료 |
```

`modules/sensing/AGENTS.md`:
```markdown
# sensing — 센서 입력 정규화

- 책임: 센서별 원시 탐지를 공통 Detection으로 정리하고 잘못된 값을 걸러낸다.
- 입력/출력: `list[Detection]` → `list[Detection]`
- 공개 API: `normalize`
- 실제 센서·보드(SC2) 연동 어댑터는 이 모듈의 액션으로 추가한다.
- 담당: 팀원 2. 브랜치 `sensing/<주제>`.
```

`modules/sensing/SPEC.md`:
```markdown
<!-- prefix: SNS -->
# sensing SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| SNS-01 | drop_invalid_detections | list[Detection] | list[Detection] | 위경도 범위 밖·음수 고도 제거 | 리드 | 완료 |
```

- [ ] **Step 2: 실패하는 테스트 작성**

`modules/sim/tests/__init__.py`, `modules/sensing/tests/__init__.py`, `modules/sim/actions/__init__.py`, `modules/sensing/actions/__init__.py`: 빈 파일.

`modules/sim/tests/test_load_scenario.py`:
```python
from pathlib import Path

import pytest

from modules.sim.actions.load_scenario import load_scenario

ROOT = Path(__file__).resolve().parents[3]

VALID = """name: t
start_ms: 1760061600000
duration_s: 10
step_ms: 500
origin: {lat: 37.5665, lon: 126.978}
objects:
  - {id: d1, kind: drone, start_east_m: -800, start_north_m: 0, alt_m: 120, vel_east_mps: 10, vel_north_mps: 0}
"""


def test_load_valid(tmp_path):
    p = tmp_path / "s.yaml"
    p.write_text(VALID)
    s = load_scenario(p)
    assert s.objects[0].kind == "drone" and s.step_ms == 500


def test_load_scenario_rejects_unknown_kind(tmp_path):
    p = tmp_path / "s.yaml"
    p.write_text(VALID.replace("kind: drone", "kind: helicopter"))
    with pytest.raises(ValueError) as e:
        load_scenario(p)
    assert "s.yaml" in str(e.value) and "kind" in str(e.value)


def test_load_scenario_rejects_nonpositive_duration(tmp_path):
    p = tmp_path / "s.yaml"
    p.write_text(VALID.replace("duration_s: 10", "duration_s: -1"))
    with pytest.raises(ValueError, match="duration_s"):
        load_scenario(p)


def test_demo_scenario_loads():
    s = load_scenario(ROOT / "demo/scenarios/seoul_mixed.yaml")
    assert {o.kind for o in s.objects} == {"drone", "balloon", "bird"}
```

`modules/sim/tests/test_object_positions.py`:
```python
import math

from modules.sim.actions.object_positions import object_positions
from modules.sim.types import Origin, Scenario, SimObject
from shared.geo import enu_delta_m

ORIGIN = Origin(lat=37.5665, lon=126.978)


def scenario(**kw) -> Scenario:
    obj = SimObject(
        id="d1",
        kind="drone",
        start_east_m=-100,
        start_north_m=50,
        alt_m=100,
        vel_east_mps=10,
        vel_north_mps=0,
        **kw,
    )
    return Scenario(
        name="t", start_ms=1000, duration_s=60, step_ms=500, origin=ORIGIN, objects=[obj]
    )


def test_moves_at_constant_velocity():
    pts = object_positions(scenario(), t_ms=1000 + 5000)
    east, north = enu_delta_m(ORIGIN.lat, ORIGIN.lon, pts[0].lat, pts[0].lon)
    assert math.isclose(east, -50, abs_tol=0.5) and math.isclose(north, 50, abs_tol=0.5)
    assert pts[0].alt_m == 100 and pts[0].kind == "drone"


def test_object_hidden_before_appear():
    assert object_positions(scenario(appear_s=10), t_ms=1000 + 5000) == []
    assert len(object_positions(scenario(appear_s=10), t_ms=1000 + 10000)) == 1
```

`modules/sim/tests/test_emit_detections.py`:
```python
from contracts.models import Detection
from modules.sim.actions.emit_detections import emit_detections
from modules.sim.types import TruthPoint
from shared.geo import distance_m

TRUTH = [TruthPoint(object_id="d1", kind="drone", lat=37.5665, lon=126.978, alt_m=100)]


def test_one_detection_per_object_near_truth():
    dets = emit_detections(TRUTH, t_ms=5000, seed=1)
    assert len(dets) == 1 and isinstance(dets[0], Detection)
    assert dets[0].id == "d1@5000" and dets[0].sensor == "radar" and dets[0].t_ms == 5000
    assert distance_m(37.5665, 126.978, dets[0].lat, dets[0].lon) < 30


def test_reproducible_with_same_seed():
    assert emit_detections(TRUTH, 5000, 1) == emit_detections(TRUTH, 5000, 1)
    assert emit_detections(TRUTH, 5000, 1) != emit_detections(TRUTH, 5000, 2)
```

`modules/sensing/tests/test_drop_invalid_detections.py`:
```python
from contracts.models import Detection
from modules.sensing.actions.drop_invalid_detections import drop_invalid_detections


def det(**kw) -> Detection:
    base = dict(id="d", sensor="radar", t_ms=0, lat=37.5, lon=127.0, alt_m=50, strength=0.5)
    return Detection(**(base | kw))


def test_keeps_valid_and_drops_invalid():
    good = det()
    out = drop_invalid_detections([good, det(lat=95), det(lon=-200), det(alt_m=-1)])
    assert out == [good]
```

- [ ] **Step 3: 실패 확인**

Run: `uv run pytest modules/sim modules/sensing`
Expected: FAIL — `ModuleNotFoundError: No module named 'modules.sim.actions.load_scenario'`.

- [ ] **Step 4: 구현**

`modules/sim/types.py`:
```python
"""sim module internal types (scenario file format)."""

from typing import Literal

from pydantic import BaseModel, Field


class Origin(BaseModel):
    lat: float
    lon: float


class SimObject(BaseModel):
    id: str
    kind: Literal["drone", "balloon", "bird"]
    start_east_m: float
    start_north_m: float
    alt_m: float = Field(ge=0)
    vel_east_mps: float
    vel_north_mps: float
    appear_s: float = Field(default=0.0, ge=0)


class Scenario(BaseModel):
    name: str
    start_ms: int
    duration_s: float = Field(gt=0)
    step_ms: int = Field(gt=0)
    origin: Origin
    objects: list[SimObject]


class TruthPoint(BaseModel):
    object_id: str
    kind: str
    lat: float
    lon: float
    alt_m: float
```

`modules/sim/actions/load_scenario.py`:
```python
"""SIM-01 load_scenario: 시나리오 YAML을 읽고 잘못된 값을 로딩 시점에 알린다
SPEC: modules/sim/SPEC.md#SIM-01
"""

from pathlib import Path

import yaml
from pydantic import ValidationError

from modules.sim.types import Scenario


def load_scenario(path: str | Path) -> Scenario:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    try:
        return Scenario.model_validate(data)
    except ValidationError as e:
        lines = [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()]
        raise ValueError(f"시나리오 파일 오류 {path.name}:\n" + "\n".join(lines)) from None
```

`modules/sim/actions/object_positions.py`:
```python
"""SIM-02 object_positions: 시각 t_ms의 객체 실제 위치(등속 이동)
SPEC: modules/sim/SPEC.md#SIM-02
"""

from modules.sim.types import Scenario, TruthPoint
from shared.geo import offset_latlon


def object_positions(scenario: Scenario, t_ms: int) -> list[TruthPoint]:
    elapsed_s = (t_ms - scenario.start_ms) / 1000
    points = []
    for o in scenario.objects:
        if elapsed_s < o.appear_s:
            continue
        t = elapsed_s - o.appear_s
        lat, lon = offset_latlon(
            scenario.origin.lat,
            scenario.origin.lon,
            o.start_east_m + o.vel_east_mps * t,
            o.start_north_m + o.vel_north_mps * t,
        )
        points.append(TruthPoint(object_id=o.id, kind=o.kind, lat=lat, lon=lon, alt_m=o.alt_m))
    return points
```

`modules/sim/actions/emit_detections.py`:
```python
"""SIM-03 emit_detections: 실제 위치에 잡음을 더한 레이더 탐지 생성 (재현 가능)
SPEC: modules/sim/SPEC.md#SIM-03
"""

import random

from contracts.models import Detection, SensorType
from modules.sim.types import TruthPoint
from shared.geo import offset_latlon

NOISE_M = 3.0


def emit_detections(truth: list[TruthPoint], t_ms: int, seed: int) -> list[Detection]:
    rng = random.Random(f"{seed}:{t_ms}")
    out = []
    for p in truth:
        lat, lon = offset_latlon(p.lat, p.lon, rng.gauss(0, NOISE_M), rng.gauss(0, NOISE_M))
        out.append(
            Detection(
                id=f"{p.object_id}@{t_ms}",
                sensor=SensorType.RADAR,
                t_ms=t_ms,
                lat=lat,
                lon=lon,
                alt_m=max(0.0, p.alt_m + rng.gauss(0, 2)),
                strength=round(rng.uniform(0.4, 1.0), 3),
            )
        )
    return out
```

`modules/sim/pipeline.py`:
```python
"""sim pipeline: calls actions in order. No logic here."""

from contracts.models import Detection
from modules.sim.actions.emit_detections import emit_detections
from modules.sim.actions.object_positions import object_positions
from modules.sim.types import Scenario


def simulate(scenario: Scenario, t_ms: int, seed: int = 0) -> list[Detection]:
    return emit_detections(object_positions(scenario, t_ms), t_ms, seed)
```

`modules/sim/__init__.py`:
```python
from modules.sim.actions.load_scenario import load_scenario
from modules.sim.pipeline import simulate
from modules.sim.types import Scenario

__all__ = ["load_scenario", "simulate", "Scenario"]
```

`modules/sensing/actions/drop_invalid_detections.py`:
```python
"""SNS-01 drop_invalid_detections: 위경도 범위 밖·음수 고도 탐지 제거
SPEC: modules/sensing/SPEC.md#SNS-01
"""

from contracts.models import Detection


def drop_invalid_detections(detections: list[Detection]) -> list[Detection]:
    return [d for d in detections if -90 <= d.lat <= 90 and -180 <= d.lon <= 180 and d.alt_m >= 0]
```

`modules/sensing/pipeline.py`:
```python
"""sensing pipeline: calls actions in order. No logic here."""

from contracts.models import Detection
from modules.sensing.actions.drop_invalid_detections import drop_invalid_detections


def normalize(detections: list[Detection]) -> list[Detection]:
    return drop_invalid_detections(detections)
```

`modules/sensing/__init__.py`:
```python
from modules.sensing.pipeline import normalize

__all__ = ["normalize"]
```

`demo/scenarios/seoul_mixed.yaml`:
```yaml
# 서울시청 주변 보호 지점(origin)으로 접근하는 드론 2, 풍선 1, 새 떼 1. 가상 데이터.
name: seoul_mixed
start_ms: 1760061600000
duration_s: 120
step_ms: 500
origin: {lat: 37.5665, lon: 126.978}
objects:
  - {id: drone-a, kind: drone, start_east_m: -1500, start_north_m: 600, alt_m: 120, vel_east_mps: 14, vel_north_mps: -5}
  - {id: drone-b, kind: drone, start_east_m: 1200, start_north_m: 1400, alt_m: 80, vel_east_mps: -9, vel_north_mps: -12, appear_s: 20}
  - {id: balloon-1, kind: balloon, start_east_m: -400, start_north_m: -1800, alt_m: 900, vel_east_mps: 1.5, vel_north_mps: 2.5}
  - {id: birds-1, kind: bird, start_east_m: 600, start_north_m: -300, alt_m: 40, vel_east_mps: -7, vel_north_mps: 6, appear_s: 10}
```

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest modules/sim modules/sensing`
Expected: PASS (9 passed).

- [ ] **Step 6: 커밋**

```bash
git add modules/sim modules/sensing demo/scenarios
git commit -m "feat: add sim and sensing modules with demo scenario

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```
Expected: pre-commit 통과(SPEC 동기화, 경계, 길이).

---

---

### Task 9: tracking, assess, respond 모듈

**Files:**
- Create: `modules/tracking/{__init__.py,AGENTS.md,SPEC.md,pipeline.py}`, `modules/tracking/actions/{__init__.py,predict_tracks.py,associate_detections.py,update_tracks.py,initiate_tracks.py,delete_stale_tracks.py}`, `modules/tracking/tests/{__init__.py,test_predict_tracks.py,test_associate_detections.py,test_update_tracks.py,test_initiate_tracks.py,test_delete_stale_tracks.py}`, `modules/assess/{__init__.py,AGENTS.md,SPEC.md,pipeline.py}`, `modules/assess/actions/{__init__.py,classify_track.py,score_threat.py}`, `modules/assess/tests/{__init__.py,test_classify_track.py,test_score_threat.py}`, `modules/respond/{__init__.py,AGENTS.md,SPEC.md,pipeline.py}`, `modules/respond/actions/{__init__.py,recommend_response.py}`, `modules/respond/tests/{__init__.py,test_recommend_response.py}`

**Interfaces:**
- Consumes: `contracts.models.*`, `shared.geo.offset_latlon, enu_delta_m, distance_m`
- Produces:
  - `modules.tracking` 공개 API: `update(tracks: list[Track], detections: list[Detection], t_ms: int) -> list[Track]`
  - actions: `predict_tracks(tracks, t_ms) -> list[Track]`, `associate_detections(tracks, detections, gate_m: float = 60.0) -> tuple[dict[str, Detection], list[Detection]]` (track_id → detection, 짝 없는 탐지), `update_tracks(tracks, assigned: dict[str, Detection], t_ms) -> list[Track]`, `initiate_tracks(detections, t_ms) -> list[Track]` (id `T-<object id 앞부분>`: 탐지 id의 `@` 앞), `delete_stale_tracks(tracks, t_ms, max_age_ms: int = 3000) -> list[Track]`
  - `modules.assess` 공개 API: `assess(tracks: list[Track], protected_lat: float, protected_lon: float) -> list[Assessment]`
  - actions: `classify_track(track: Track) -> ObjectClass`, `score_threat(track: Track, object_class: ObjectClass, protected_lat: float, protected_lon: float) -> tuple[float, str]`
  - `modules.respond` 공개 API: `respond(assessments: list[Assessment]) -> list[Response]`
  - action: `recommend_response(assessment: Assessment) -> Response`

- [ ] **Step 1: 모듈 문서와 SPEC 작성**

`modules/tracking/AGENTS.md`:
```markdown
# tracking — 다중 표적 추적

- 책임: 매 프레임 탐지(Detection)를 받아 표적(Track) 목록을 갱신한다.
- 순서(pipeline.update): predict → associate → update → initiate → delete. (지식 카드 stone-soup-tracker-components)
- 입력: 이전 `list[Track]`, 이번 `list[Detection]`, `t_ms` / 출력: `list[Track]`
- 공개 API: `update`
- 상태(이전 표적)는 호출자(gateway)가 보관한다. 이 모듈은 상태를 저장하지 않는다.
- 담당: 팀원 3. 브랜치 `tracking/<주제>`.
```

`modules/tracking/SPEC.md`:
```markdown
<!-- prefix: TRK -->
# tracking SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| TRK-01 | predict_tracks | list[Track], t_ms | list[Track] | 등속 모델로 t_ms 위치 예측 | 리드 | 완료 |
| TRK-02 | associate_detections | list[Track], list[Detection], gate_m | dict[id, Detection], list[Detection] | 최근접(gate 이내) 1:1 짝짓기 | 리드 | 완료 |
| TRK-03 | update_tracks | list[Track], dict, t_ms | list[Track] | 위치=탐지, hits+1, 속도=예측오차 β(0.3) 보정 (첫 갱신은 변위/시간) | 리드 | 완료 |
| TRK-04 | initiate_tracks | list[Detection], t_ms | list[Track] | 짝 없는 탐지마다 새 표적 | 리드 | 완료 |
| TRK-05 | delete_stale_tracks | list[Track], t_ms, max_age_ms | list[Track] | 마지막 탐지 후 3초 지난 표적 삭제 | 리드 | 완료 |
```

`modules/assess/AGENTS.md`:
```markdown
# assess — 분류와 위협도

- 책임: 표적을 드론/풍선/조류/미상으로 분류하고 보호 지점 기준 위협도(0~1)와 근거를 계산한다.
- 입력: `list[Track]`, 보호 지점 위경도 / 출력: `list[Assessment]`
- 공개 API: `assess`
- 현재는 속도·고도 규칙 기반(가짜 로직 수준). 모델로 교체 시 액션 단위로 바꾼다.
- 담당: 팀원 3. 브랜치 `assess/<주제>`.
```

`modules/assess/SPEC.md`:
```markdown
<!-- prefix: ASM -->
# assess SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| ASM-01 | classify_track | Track | ObjectClass | 속도·고도 규칙으로 drone/balloon/bird/unknown | 리드 | 완료 |
| ASM-02 | score_threat | Track, ObjectClass, 보호 지점 | (float, str) | 거리·접근 여부·분류로 0~1 점수와 근거 | 리드 | 완료 |
```

`modules/respond/AGENTS.md`:
```markdown
# respond — 대응 추천

- 책임: 위협 평가를 받아 관찰/소프트킬/하드킬 대응을 근거와 함께 추천한다. 부수피해·교전규칙 고려는 이 모듈에서 확장한다.
- 입력: `list[Assessment]` / 출력: `list[Response]`
- 공개 API: `respond`
- 추천만 한다. 실제 무력화 명령을 내리는 기능은 만들지 않는다.
- 담당: 팀원 3 (gateway 완료 후 리드 지원). 브랜치 `respond/<주제>`.
```

`modules/respond/SPEC.md`:
```markdown
<!-- prefix: RSP -->
# respond SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| RSP-01 | recommend_response | Assessment | Response | drone 0.9↑ hard_kill, 0.7↑ soft_kill, 그 외 observe | 리드 | 완료 |
```

- [ ] **Step 2: 실패하는 테스트 작성**

모든 `actions/__init__.py`, `tests/__init__.py`: 빈 파일.

공통 테스트 보조: 각 테스트 파일 안에 직접 만든다(모듈 간 테스트 공유 금지).

`modules/tracking/tests/test_predict_tracks.py`:
```python
import math

from contracts.models import Track
from modules.tracking.actions.predict_tracks import predict_tracks
from shared.geo import enu_delta_m


def test_constant_velocity_prediction():
    t = Track(
        id="T-a",
        t_ms=0,
        lat=37.5,
        lon=127.0,
        alt_m=100,
        vel_east_mps=10,
        vel_north_mps=-5,
        hits=3,
        last_seen_ms=0,
    )
    (p,) = predict_tracks([t], t_ms=2000)
    east, north = enu_delta_m(37.5, 127.0, p.lat, p.lon)
    assert math.isclose(east, 20, abs_tol=0.1) and math.isclose(north, -10, abs_tol=0.1)
    assert p.t_ms == 2000 and p.last_seen_ms == 0 and p.hits == 3
```

`modules/tracking/tests/test_associate_detections.py`:
```python
from contracts.models import Detection, Track
from modules.tracking.actions.associate_detections import associate_detections
from shared.geo import offset_latlon


def track(tid, east):
    lat, lon = offset_latlon(37.5, 127.0, east, 0)
    return Track(id=tid, t_ms=0, lat=lat, lon=lon, alt_m=50, last_seen_ms=0)


def det(did, east):
    lat, lon = offset_latlon(37.5, 127.0, east, 0)
    return Detection(id=did, sensor="radar", t_ms=0, lat=lat, lon=lon, alt_m=50, strength=0.5)


def test_nearest_within_gate_one_to_one():
    tracks = [track("T-a", 0), track("T-b", 100)]
    dets = [det("x", 5), det("y", 95), det("z", 500)]
    assigned, free = associate_detections(tracks, dets, gate_m=60)
    assert assigned["T-a"].id == "x" and assigned["T-b"].id == "y"
    assert [d.id for d in free] == ["z"]


def test_one_detection_not_shared_by_two_tracks():
    assigned, free = associate_detections([track("T-a", 0), track("T-b", 10)], [det("x", 4)])
    assert list(assigned) == ["T-a"] and free == []
```

`modules/tracking/tests/test_update_tracks.py`:
```python
import math

from contracts.models import Detection, Track
from modules.tracking.actions.update_tracks import update_tracks
from shared.geo import offset_latlon


def det_at(east: float, north: float) -> Detection:
    lat, lon = offset_latlon(37.5, 127.0, east, north)
    return Detection(
        id="a@1000", sensor="radar", t_ms=1000, lat=lat, lon=lon, alt_m=55, strength=0.5
    )


def test_first_update_uses_full_displacement():
    t = Track(id="T-a", t_ms=1000, lat=37.5, lon=127.0, alt_m=50, hits=1, last_seen_ms=0)
    d = det_at(20, 10)
    untouched = Track(id="T-b", t_ms=1000, lat=37.0, lon=127.0, alt_m=1, last_seen_ms=0)
    out = {x.id: x for x in update_tracks([t, untouched], {"T-a": d}, t_ms=1000)}
    a = out["T-a"]
    assert (a.lat, a.lon, a.alt_m, a.hits, a.last_seen_ms) == (d.lat, d.lon, 55, 2, 1000)
    assert math.isclose(a.vel_east_mps, 20, abs_tol=0.1)
    assert math.isclose(a.vel_north_mps, 10, abs_tol=0.1)
    assert out["T-b"] == untouched


def test_later_updates_smooth_velocity():
    t = Track(
        id="T-a", t_ms=1000, lat=37.5, lon=127.0, alt_m=50, hits=3, last_seen_ms=0, vel_east_mps=10
    )
    (a,) = update_tracks([t], {"T-a": det_at(20, 0)}, t_ms=1000)
    assert math.isclose(a.vel_east_mps, 10 + 0.3 * 20, abs_tol=0.1)
```

`modules/tracking/tests/test_initiate_tracks.py`:
```python
from contracts.models import Detection
from modules.tracking.actions.initiate_tracks import initiate_tracks


def test_new_track_per_detection():
    d = Detection(
        id="drone-a@1500", sensor="radar", t_ms=1500, lat=37.5, lon=127.0, alt_m=90, strength=0.5
    )
    (t,) = initiate_tracks([d], t_ms=1500)
    assert t.id == "T-drone-a" and t.hits == 1 and t.last_seen_ms == 1500
    assert (t.lat, t.lon, t.alt_m) == (37.5, 127.0, 90)
```

`modules/tracking/tests/test_delete_stale_tracks.py`:
```python
from contracts.models import Track
from modules.tracking.actions.delete_stale_tracks import delete_stale_tracks


def test_drops_tracks_not_seen_for_too_long():
    fresh = Track(id="a", t_ms=5000, lat=0, lon=0, alt_m=0, last_seen_ms=3000)
    stale = Track(id="b", t_ms=5000, lat=0, lon=0, alt_m=0, last_seen_ms=1000)
    assert delete_stale_tracks([fresh, stale], t_ms=5000, max_age_ms=3000) == [fresh]
```

`modules/assess/tests/test_classify_track.py`:
```python
from contracts.models import ObjectClass, Track
from modules.assess.actions.classify_track import classify_track


def t(speed_e: float, alt: float, hits: int = 5) -> Track:
    return Track(
        id="x",
        t_ms=0,
        lat=0,
        lon=0,
        alt_m=alt,
        vel_east_mps=speed_e,
        vel_north_mps=0,
        hits=hits,
        last_seen_ms=0,
    )


def test_rules():
    assert classify_track(t(2, 900)) == ObjectClass.BALLOON
    assert classify_track(t(9, 40)) == ObjectClass.BIRD
    assert classify_track(t(15, 120)) == ObjectClass.DRONE
    assert classify_track(t(15, 120, hits=1)) == ObjectClass.UNKNOWN
```

`modules/assess/tests/test_score_threat.py`:
```python
from contracts.models import ObjectClass, Track
from modules.assess.actions.score_threat import score_threat
from shared.geo import offset_latlon

P = (37.5665, 126.978)


def track_at(east: float, vel_east: float) -> Track:
    lat, lon = offset_latlon(*P, east, 0)
    return Track(
        id="x",
        t_ms=0,
        lat=lat,
        lon=lon,
        alt_m=100,
        vel_east_mps=vel_east,
        vel_north_mps=0,
        hits=5,
        last_seen_ms=0,
    )


def test_close_approaching_drone_is_high():
    score, reason = score_threat(track_at(-300, 15), ObjectClass.DRONE, *P)
    assert score >= 0.8 and "m" in reason


def test_receding_drone_is_lower_than_approaching():
    near, _ = score_threat(track_at(-300, 15), ObjectClass.DRONE, *P)
    away, _ = score_threat(track_at(-300, -15), ObjectClass.DRONE, *P)
    assert away < near


def test_bird_is_low_and_score_in_range():
    score, _ = score_threat(track_at(-50, 10), ObjectClass.BIRD, *P)
    assert 0.0 <= score <= 0.3
```

`modules/respond/tests/test_recommend_response.py`:
```python
from contracts.models import Assessment, ResponseKind
from modules.respond.actions.recommend_response import recommend_response


def a(cls: str, threat: float) -> Assessment:
    return Assessment(track_id="T-x", object_class=cls, threat=threat, reason="r")


def test_thresholds():
    assert recommend_response(a("drone", 0.95)).kind == ResponseKind.HARD_KILL
    assert recommend_response(a("drone", 0.75)).kind == ResponseKind.SOFT_KILL
    assert recommend_response(a("drone", 0.5)).kind == ResponseKind.OBSERVE
    assert recommend_response(a("balloon", 0.95)).kind == ResponseKind.OBSERVE
    r = recommend_response(a("drone", 0.75))
    assert r.track_id == "T-x" and "0.75" in r.reason
```

- [ ] **Step 3: 실패 확인**

Run: `uv run pytest modules/tracking modules/assess modules/respond`
Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 4: 구현**

`modules/tracking/actions/predict_tracks.py`:
```python
"""TRK-01 predict_tracks: 등속 모델로 t_ms 시점 위치 예측
SPEC: modules/tracking/SPEC.md#TRK-01
"""

from contracts.models import Track
from shared.geo import offset_latlon


def predict_tracks(tracks: list[Track], t_ms: int) -> list[Track]:
    out = []
    for t in tracks:
        dt = (t_ms - t.t_ms) / 1000
        lat, lon = offset_latlon(t.lat, t.lon, t.vel_east_mps * dt, t.vel_north_mps * dt)
        out.append(t.model_copy(update={"lat": lat, "lon": lon, "t_ms": t_ms}))
    return out
```

`modules/tracking/actions/associate_detections.py`:
```python
"""TRK-02 associate_detections: 게이트 안 최근접 탐지를 표적에 1:1로 짝짓기
SPEC: modules/tracking/SPEC.md#TRK-02
"""

from contracts.models import Detection, Track
from shared.geo import distance_m


def associate_detections(
    tracks: list[Track], detections: list[Detection], gate_m: float = 60.0
) -> tuple[dict[str, Detection], list[Detection]]:
    pairs = sorted(
        (distance_m(t.lat, t.lon, d.lat, d.lon), i, j)
        for i, t in enumerate(tracks)
        for j, d in enumerate(detections)
    )
    assigned: dict[str, Detection] = {}
    used: set[int] = set()
    for dist, i, j in pairs:
        if dist > gate_m:
            break
        if tracks[i].id in assigned or j in used:
            continue
        assigned[tracks[i].id] = detections[j]
        used.add(j)
    free = [d for j, d in enumerate(detections) if j not in used]
    return assigned, free
```

`modules/tracking/actions/update_tracks.py`:
```python
"""TRK-03 update_tracks: 짝지어진 탐지로 위치·hits 갱신, 속도는 β 평활
SPEC: modules/tracking/SPEC.md#TRK-03
"""

from contracts.models import Detection, Track
from shared.geo import enu_delta_m

BETA = 0.3


def update_tracks(tracks: list[Track], assigned: dict[str, Detection], t_ms: int) -> list[Track]:
    out = []
    for t in tracks:
        d = assigned.get(t.id)
        if d is None:
            out.append(t)
            continue
        dt = max((t_ms - t.last_seen_ms) / 1000, 1e-3)
        east, north = enu_delta_m(t.lat, t.lon, d.lat, d.lon)
        beta = 1.0 if t.hits == 1 else BETA
        out.append(
            t.model_copy(
                update={
                    "lat": d.lat,
                    "lon": d.lon,
                    "alt_m": d.alt_m,
                    "t_ms": t_ms,
                    "last_seen_ms": t_ms,
                    "hits": t.hits + 1,
                    "vel_east_mps": t.vel_east_mps + beta * east / dt,
                    "vel_north_mps": t.vel_north_mps + beta * north / dt,
                }
            )
        )
    return out
```
`t.lat/lon`은 pipeline에서 predict 후 들어오므로 예측 위치다. 따라서 `east/dt`는 예측 오차로 인한 속도 보정량이고, 첫 갱신(hits=1, 속도 0)에서는 β=1로 변위/시간을 그대로 속도로 쓴다.

`modules/tracking/actions/initiate_tracks.py`:
```python
"""TRK-04 initiate_tracks: 짝 없는 탐지마다 새 표적 생성
SPEC: modules/tracking/SPEC.md#TRK-04
"""

from contracts.models import Detection, Track


def initiate_tracks(detections: list[Detection], t_ms: int) -> list[Track]:
    return [
        Track(
            id=f"T-{d.id.split('@')[0]}",
            t_ms=t_ms,
            lat=d.lat,
            lon=d.lon,
            alt_m=d.alt_m,
            hits=1,
            last_seen_ms=t_ms,
        )
        for d in detections
    ]
```

`modules/tracking/actions/delete_stale_tracks.py`:
```python
"""TRK-05 delete_stale_tracks: 마지막 탐지 후 max_age_ms 지난 표적 삭제
SPEC: modules/tracking/SPEC.md#TRK-05
"""

from contracts.models import Track


def delete_stale_tracks(tracks: list[Track], t_ms: int, max_age_ms: int = 3000) -> list[Track]:
    return [t for t in tracks if t_ms - t.last_seen_ms <= max_age_ms]
```

`modules/tracking/pipeline.py`:
```python
"""tracking pipeline: predict -> associate -> update -> initiate -> delete. No logic here."""

from contracts.models import Detection, Track
from modules.tracking.actions.associate_detections import associate_detections
from modules.tracking.actions.delete_stale_tracks import delete_stale_tracks
from modules.tracking.actions.initiate_tracks import initiate_tracks
from modules.tracking.actions.predict_tracks import predict_tracks
from modules.tracking.actions.update_tracks import update_tracks


def update(tracks: list[Track], detections: list[Detection], t_ms: int) -> list[Track]:
    predicted = predict_tracks(tracks, t_ms)
    assigned, free = associate_detections(predicted, detections)
    updated = update_tracks(predicted, assigned, t_ms)
    return delete_stale_tracks(updated + initiate_tracks(free, t_ms), t_ms)
```

`modules/tracking/__init__.py`:
```python
from modules.tracking.pipeline import update

__all__ = ["update"]
```

`modules/assess/actions/classify_track.py`:
```python
"""ASM-01 classify_track: 속도·고도 규칙으로 drone/balloon/bird/unknown 분류
SPEC: modules/assess/SPEC.md#ASM-01
"""

import math

from contracts.models import ObjectClass, Track


def classify_track(track: Track) -> ObjectClass:
    if track.hits < 3:
        return ObjectClass.UNKNOWN
    speed = math.hypot(track.vel_east_mps, track.vel_north_mps)
    if speed < 4 and track.alt_m > 300:
        return ObjectClass.BALLOON
    if speed < 12 and track.alt_m < 60:
        return ObjectClass.BIRD
    return ObjectClass.DRONE
```

`modules/assess/actions/score_threat.py`:
```python
"""ASM-02 score_threat: 보호 지점까지 거리·접근 여부·분류로 위협도와 근거 계산
SPEC: modules/assess/SPEC.md#ASM-02
"""

from contracts.models import ObjectClass, Track
from shared.geo import distance_m, enu_delta_m

CLASS_WEIGHT = {
    ObjectClass.DRONE: 1.0,
    ObjectClass.UNKNOWN: 0.6,
    ObjectClass.BALLOON: 0.4,
    ObjectClass.BIRD: 0.1,
}


def score_threat(
    track: Track, object_class: ObjectClass, protected_lat: float, protected_lon: float
) -> tuple[float, str]:
    dist = distance_m(track.lat, track.lon, protected_lat, protected_lon)
    east, north = enu_delta_m(track.lat, track.lon, protected_lat, protected_lon)
    closing = (track.vel_east_mps * east + track.vel_north_mps * north) / max(dist, 1.0)
    proximity = max(0.0, 1.0 - dist / 3000)
    approach = 1.0 if closing > 1 else 0.5
    score = round(min(1.0, CLASS_WEIGHT[object_class] * (0.3 + 0.7 * proximity) * approach), 2)
    reason = f"{object_class.value}, 보호지점 {dist:.0f} m, 접근속도 {closing:.1f} m/s"
    return score, reason
```

`modules/assess/pipeline.py`:
```python
"""assess pipeline: classify -> score per track. No logic here."""

from contracts.models import Assessment, Track
from modules.assess.actions.classify_track import classify_track
from modules.assess.actions.score_threat import score_threat


def assess(tracks: list[Track], protected_lat: float, protected_lon: float) -> list[Assessment]:
    out = []
    for t in tracks:
        cls = classify_track(t)
        threat, reason = score_threat(t, cls, protected_lat, protected_lon)
        out.append(Assessment(track_id=t.id, object_class=cls, threat=threat, reason=reason))
    return out
```

`modules/assess/__init__.py`:
```python
from modules.assess.pipeline import assess

__all__ = ["assess"]
```

`modules/respond/actions/recommend_response.py`:
```python
"""RSP-01 recommend_response: 분류·위협도 임계값으로 대응 추천
SPEC: modules/respond/SPEC.md#RSP-01
"""

from contracts.models import Assessment, ObjectClass, Response, ResponseKind


def recommend_response(assessment: Assessment) -> Response:
    kind = ResponseKind.OBSERVE
    if assessment.object_class == ObjectClass.DRONE:
        if assessment.threat >= 0.9:
            kind = ResponseKind.HARD_KILL
        elif assessment.threat >= 0.7:
            kind = ResponseKind.SOFT_KILL
    reason = f"{assessment.object_class.value} 위협도 {assessment.threat:.2f}"
    return Response(track_id=assessment.track_id, kind=kind, reason=reason)
```

`modules/respond/pipeline.py`:
```python
"""respond pipeline. No logic here."""

from contracts.models import Assessment, Response
from modules.respond.actions.recommend_response import recommend_response


def respond(assessments: list[Assessment]) -> list[Response]:
    return [recommend_response(a) for a in assessments]
```

`modules/respond/__init__.py`:
```python
from modules.respond.pipeline import respond

__all__ = ["respond"]
```

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest modules/tracking modules/assess modules/respond`
Expected: PASS (12 passed).

- [ ] **Step 6: 커밋**

```bash
git add modules/tracking modules/assess modules/respond
git commit -m "feat: add tracking, assess and respond modules

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

---

### Task 10: gateway 모듈과 smoke test

**Files:**
- Create: `modules/gateway/{__init__.py,AGENTS.md,SPEC.md,pipeline.py,app.py}`, `modules/gateway/actions/{__init__.py,build_frame.py}`, `modules/gateway/tests/{__init__.py,test_build_frame.py,test_app.py}`, `scripts/smoke.py`, `tests/test_smoke.py`

**Interfaces:**
- Consumes: `modules.sim.load_scenario, simulate, Scenario`, `modules.sensing.normalize`, `modules.tracking.update`, `modules.assess.assess`, `modules.respond.respond`, `contracts.models.Frame`
- Produces:
  - action `build_frame(t_ms: int, tracks, assessments, responses) -> Frame`
  - `modules.gateway.pipeline.Engine(scenario: Scenario, seed: int = 0)`: `.t_ms: int`, `.done: bool`, `.step() -> Frame` (한 step_ms 진행, 끝나면 처음부터 반복하지 않고 done=True)
  - `modules.gateway.app.create_app(scenario_path: str, realtime: bool = True, ui_dist: str | None = None) -> FastAPI` — `GET /health`, `WS /ws` (연결마다 독립 Engine으로 프레임 JSON 송출, 시나리오 끝나면 처음부터 다시), `ui_dist`가 있으면 `/`에 정적 파일 서빙
  - `modules.gateway` 공개 API: `Engine`, `create_app`
  - `scripts/smoke.py [--scenario PATH] [--seconds 10]` exit 0/1
  - 환경변수: `KDTH_SCENARIO`(기본 `demo/scenarios/seoul_mixed.yaml`), `KDTH_UI_DIST`

- [ ] **Step 1: 모듈 문서와 SPEC 작성**

`modules/gateway/AGENTS.md`:
```markdown
# gateway — 파이프라인 실행과 화면 송출

- 책임: 시나리오를 시간 순서로 돌리며 sim → sensing → tracking → assess → respond를 호출해 Frame을 만들고 WebSocket `/ws`로 보낸다. 시연 시 빌드된 cop-ui를 `/`에서 서빙.
- 다른 모듈은 공개 API로만 호출한다.
- 실행: `uv run uvicorn modules.gateway.app:app --port 8000` (환경변수 KDTH_SCENARIO, KDTH_UI_DIST)
- 연결이 끊겨도 서버는 계속 살아 있어야 한다(연결마다 독립 Engine, 종료 감시 task로 루프 정리).
- 담당: 리드. 브랜치 `gateway/<주제>`.
```

`modules/gateway/SPEC.md`:
```markdown
<!-- prefix: GW -->
# gateway SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| GW-01 | build_frame | t_ms, tracks, assessments, responses | Frame | 계약 Frame 생성 | 리드 | 완료 |
```

- [ ] **Step 2: 실패하는 테스트 작성**

`modules/gateway/tests/test_build_frame.py`:
```python
from contracts.models import Frame, Track
from modules.gateway.actions.build_frame import build_frame


def test_build_frame():
    t = Track(id="T-a", t_ms=1, lat=0, lon=0, alt_m=0, last_seen_ms=1)
    f = build_frame(1, [t], [], [])
    assert isinstance(f, Frame) and f.t_ms == 1 and f.tracks == [t]
```

`modules/gateway/tests/test_app.py`:
```python
from pathlib import Path

from fastapi.testclient import TestClient

from contracts.models import Frame
from modules.gateway import Engine, create_app
from modules.sim import load_scenario

ROOT = Path(__file__).resolve().parents[3]
SCENARIO = str(ROOT / "demo/scenarios/seoul_mixed.yaml")


def test_engine_produces_tracks_and_assessments():
    eng = Engine(load_scenario(SCENARIO), seed=1)
    frames = [eng.step() for _ in range(40)]
    last = frames[-1]
    assert len(last.tracks) >= 3
    assert {a.track_id for a in last.assessments} == {t.id for t in last.tracks}
    assert frames[1].t_ms - frames[0].t_ms == 500


def test_engine_done_at_end():
    eng = Engine(load_scenario(SCENARIO))
    for _ in range(240):
        eng.step()
    assert eng.done


def test_health_and_websocket_frames():
    client = TestClient(create_app(SCENARIO, realtime=False))
    assert client.get("/health").json() == {"ok": True}
    with client.websocket_connect("/ws") as ws:
        Frame.model_validate(ws.receive_json())
        Frame.model_validate(ws.receive_json())


def test_websocket_reconnect():
    client = TestClient(create_app(SCENARIO, realtime=False))
    with client.websocket_connect("/ws") as ws:
        first = Frame.model_validate(ws.receive_json())
    with client.websocket_connect("/ws") as ws2:
        again = Frame.model_validate(ws2.receive_json())
    assert again.t_ms == first.t_ms
    assert client.get("/health").status_code == 200


def test_serves_ui_dist(tmp_path):
    (tmp_path / "index.html").write_text("<html>ui</html>")
    client = TestClient(create_app(SCENARIO, realtime=False, ui_dist=str(tmp_path)))
    assert "ui" in client.get("/").text
```

`tests/test_smoke.py`:
```python
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_smoke_passes_on_demo_scenario():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/smoke.py")], capture_output=True, text=True, cwd=ROOT
    )
    assert r.returncode == 0, r.stderr
    assert "smoke OK" in r.stdout


def test_smoke_fails_on_bad_scenario(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "name: x\nstart_ms: 0\nduration_s: 5\nstep_ms: 500\norigin: {lat: 0, lon: 0}\n"
        "objects: [{id: a, kind: tank, start_east_m: 0, start_north_m: 0, alt_m: 1, "
        "vel_east_mps: 0, vel_north_mps: 0}]\n"
    )
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/smoke.py"), "--scenario", str(bad)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert r.returncode == 1 and "kind" in r.stderr
```

- [ ] **Step 3: 실패 확인**

Run: `uv run pytest modules/gateway tests/test_smoke.py`
Expected: FAIL — `ImportError: cannot import name 'Engine' from 'modules.gateway'`.

- [ ] **Step 4: 구현**

`modules/gateway/actions/build_frame.py`:
```python
"""GW-01 build_frame: 한 시점의 결과를 계약 Frame으로 묶기
SPEC: modules/gateway/SPEC.md#GW-01
"""

from contracts.models import Assessment, Frame, Response, Track


def build_frame(
    t_ms: int, tracks: list[Track], assessments: list[Assessment], responses: list[Response]
) -> Frame:
    return Frame(t_ms=t_ms, tracks=tracks, assessments=assessments, responses=responses)
```

`modules/gateway/pipeline.py`:
```python
"""gateway pipeline: run all modules for one time step. No domain logic here."""

from contracts.models import Frame, Track
from modules.assess import assess
from modules.gateway.actions.build_frame import build_frame
from modules.respond import respond
from modules.sensing import normalize
from modules.sim import Scenario, simulate
from modules.tracking import update


class Engine:
    def __init__(self, scenario: Scenario, seed: int = 0):
        self.scenario, self.seed = scenario, seed
        self.t_ms = scenario.start_ms
        self.end_ms = scenario.start_ms + int(scenario.duration_s * 1000)
        self.tracks: list[Track] = []

    @property
    def done(self) -> bool:
        return self.t_ms >= self.end_ms

    def step(self) -> Frame:
        detections = normalize(simulate(self.scenario, self.t_ms, self.seed))
        self.tracks = update(self.tracks, detections, self.t_ms)
        origin = self.scenario.origin
        assessments = assess(self.tracks, origin.lat, origin.lon)
        frame = build_frame(self.t_ms, self.tracks, assessments, respond(assessments))
        self.t_ms += self.scenario.step_ms
        return frame
```

`modules/gateway/app.py`:
```python
"""FastAPI app: WebSocket frame stream + static UI for the demo."""

import asyncio
import os
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from modules.gateway.pipeline import Engine
from modules.sim import load_scenario

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIO = str(ROOT / "demo/scenarios/seoul_mixed.yaml")


def create_app(scenario_path: str, realtime: bool = True, ui_dist: str | None = None) -> FastAPI:
    scenario = load_scenario(scenario_path)
    app = FastAPI(title="kdth gateway")

    @app.get("/health")
    def health() -> dict:
        return {"ok": True}

    @app.websocket("/ws")
    async def ws(websocket: WebSocket) -> None:
        await websocket.accept()
        closed = asyncio.Event()

        async def watch() -> None:
            try:
                while True:
                    await websocket.receive_text()
            except (WebSocketDisconnect, RuntimeError):
                closed.set()

        watcher = asyncio.create_task(watch())
        engine = Engine(scenario)
        try:
            while not closed.is_set():
                if engine.done:
                    engine = Engine(scenario)
                await websocket.send_text(engine.step().model_dump_json())
                await asyncio.sleep(scenario.step_ms / 1000 if realtime else 0)
        except (WebSocketDisconnect, RuntimeError):
            pass
        finally:
            watcher.cancel()

    if ui_dist and Path(ui_dist, "index.html").exists():
        app.mount("/", StaticFiles(directory=ui_dist, html=True), name="ui")
    return app


app = create_app(
    os.environ.get("KDTH_SCENARIO", DEFAULT_SCENARIO), ui_dist=os.environ.get("KDTH_UI_DIST")
)
```

`modules/gateway/__init__.py`:
```python
from modules.gateway.app import create_app
from modules.gateway.pipeline import Engine

__all__ = ["Engine", "create_app"]
```

`scripts/smoke.py`:
```python
"""Headless demo smoke test: run the scenario for N simulated seconds, validate every frame."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from contracts.models import Frame  # noqa: E402
from modules.gateway import Engine  # noqa: E402
from modules.sim import load_scenario  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=str(ROOT / "demo/scenarios/seoul_mixed.yaml"))
    ap.add_argument("--seconds", type=float, default=10)
    a = ap.parse_args()
    try:
        scenario = load_scenario(a.scenario)
        engine = Engine(scenario)
        steps = int(a.seconds * 1000 / scenario.step_ms)
        for _ in range(steps):
            Frame.model_validate(engine.step().model_dump())
    except Exception as e:  # noqa: BLE001 - report any failure briefly
        print(f"smoke FAIL: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"smoke OK: {steps} frames, {len(engine.tracks)} tracks")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest modules/gateway tests/test_smoke.py && time uv run python scripts/smoke.py`
Expected: PASS (7 passed), `smoke OK: 20 frames, ...`, 실행 1초 이하.

- [ ] **Step 6: 커밋**

```bash
git add modules/gateway scripts/smoke.py tests/test_smoke.py
git commit -m "feat: add gateway engine, websocket app and smoke test

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

---

### Task 11: gen_contracts.py (JSON Schema + TS 타입)

**Files:**
- Create: `scripts/gen_contracts.py`, `tests/test_gen_contracts.py`, `contracts/schema/*.json`(생성물), `modules/cop-ui/src/contracts.gen.ts`(생성물)

**Interfaces:**
- Consumes: `contracts.models.ALL_MODELS`
- Produces:
  - `to_typescript(models: dict[str, type[BaseModel]]) -> str` — 각 모델을 `export interface <Name> {...}`, enum을 `export type <Name> = "a" | "b";`로
  - CLI `python scripts/gen_contracts.py [--root PATH]` → `contracts/schema/<name>.json`, `modules/cop-ui/src/contracts.gen.ts`
  - TS 이름: `Detection`, `Track`, `Assessment`, `Response`, `Frame`, `SensorType`, `ObjectClass`, `ResponseKind`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_gen_contracts.py`:
```python
import importlib.util
import json
from pathlib import Path

from contracts.models import ALL_MODELS

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("gen", ROOT / "scripts/gen_contracts.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


def test_typescript_output():
    ts = gen.to_typescript(ALL_MODELS)
    assert 'export type SensorType = "rf" | "eoir" | "radar";' in ts
    assert "export interface Detection {" in ts
    assert "  strength: number;" in ts
    assert "  sensor: SensorType;" in ts
    assert "  tracks: Track[];" in ts
    assert "  vel_east_mps?: number;" in ts
    assert ts.count("export interface Track {") == 1


def test_cli_writes_files(tmp_path):
    (tmp_path / "modules/cop-ui/src").mkdir(parents=True)
    gen.main(["--root", str(tmp_path)])
    schema = json.loads((tmp_path / "contracts/schema/frame.json").read_text())
    assert schema["title"] == "Frame"
    assert (tmp_path / "modules/cop-ui/src/contracts.gen.ts").read_text().startswith("// 자동 생성")
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_gen_contracts.py`
Expected: FAIL — `FileNotFoundError`.

- [ ] **Step 3: 구현**

`scripts/gen_contracts.py`:
```python
"""Generate JSON Schema files and TypeScript types from contracts/models.py."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contracts.models import ALL_MODELS  # noqa: E402

HEADER = "// 자동 생성 파일 (scripts/gen_contracts.py). 직접 수정하지 마세요.\n"
SCALARS = {"string": "string", "number": "number", "integer": "number", "boolean": "boolean"}


def _ts_type(prop: dict) -> str:
    if "$ref" in prop:
        return prop["$ref"].split("/")[-1]
    if prop.get("type") == "array":
        return f"{_ts_type(prop['items'])}[]"
    if "anyOf" in prop:
        return " | ".join(_ts_type(p) if p.get("type") != "null" else "null" for p in prop["anyOf"])
    return SCALARS.get(prop.get("type"), "unknown")


def _emit(name: str, schema: dict, out: dict[str, str]) -> None:
    if "enum" in schema:
        out[name] = (
            f"export type {name} = " + " | ".join(json.dumps(v) for v in schema["enum"]) + ";"
        )
        return
    required = set(schema.get("required", []))
    lines = [f"export interface {name} {{"]
    for key, prop in schema.get("properties", {}).items():
        opt = "" if key in required else "?"
        lines.append(f"  {key}{opt}: {_ts_type(prop)};")
    out[name] = "\n".join(lines + ["}"])


def to_typescript(models: dict) -> str:
    blocks: dict[str, str] = {}
    for model in models.values():
        schema = model.model_json_schema()
        for name, sub in schema.get("$defs", {}).items():
            _emit(name, sub, blocks)
        _emit(schema["title"], schema, blocks)
    return HEADER + "\n\n".join(blocks[k] for k in blocks) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    root = Path(ap.parse_args(argv).root)
    out = root / "contracts" / "schema"
    out.mkdir(parents=True, exist_ok=True)
    for name, model in ALL_MODELS.items():
        (out / f"{name}.json").write_text(
            json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    ts = root / "modules" / "cop-ui" / "src" / "contracts.gen.ts"
    ts.parent.mkdir(parents=True, exist_ok=True)
    ts.write_text(to_typescript(ALL_MODELS), encoding="utf-8")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 통과 확인 후 실제 생성**

Run: `uv run pytest tests/test_gen_contracts.py && uv run python scripts/gen_contracts.py && head -20 modules/cop-ui/src/contracts.gen.ts`
Expected: PASS (2 passed). 생성된 TS에 `export type SensorType`, `export interface Detection` 등이 보인다.

- [ ] **Step 5: 커밋**

```bash
git add scripts/gen_contracts.py tests/test_gen_contracts.py contracts/schema modules/cop-ui/src/contracts.gen.ts
git commit -m "feat: generate JSON schema and TS types from contracts

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

---

### Task 12: cop-ui (지도 관제 화면)

**Files:**
- Create: `modules/cop-ui/` (Vite react-ts 템플릿), `modules/cop-ui/AGENTS.md`, `modules/cop-ui/SPEC.md`, `modules/cop-ui/src/features/map/toGeoJSON.ts`, `modules/cop-ui/src/features/map/toGeoJSON.test.ts`, `modules/cop-ui/src/features/map/basemap.ts`, `modules/cop-ui/src/features/map/basemap.test.ts`, `modules/cop-ui/src/features/map/MapView.tsx`, `modules/cop-ui/src/features/live/useFrames.ts`, `modules/cop-ui/src/features/alerts/AlertList.tsx`, `modules/cop-ui/src/App.tsx`(교체), `modules/cop-ui/src/index.css`(교체), `modules/cop-ui/vite.config.ts`(교체), `modules/cop-ui/eslint.config.js`(수정)
- Delete: 템플릿의 `src/App.css`, `src/assets/`, `public/vite.svg`

**Interfaces:**
- Consumes: `src/contracts.gen.ts` (`Frame`, `Track`, `Assessment`, `Response`, `ObjectClass`, `ResponseKind`), gateway `WS /ws`
- Produces:
  - `toGeoJSON(frame: Frame): FeatureCollection<Point>` (`geojson` 타입) — feature properties: `id`, `cls`(ObjectClass), `threat`(number), `response`(ResponseKind)
  - `useFrames(url: string): { frame: Frame | null; connected: boolean }` — 끊기면 1초 뒤 재연결
  - `MapView({ frame, center }: { frame: Frame | null; center: [number, number] })`
  - `AlertList({ frame }: { frame: Frame | null })` — 위협도 내림차순, observe 아닌 것 강조
  - `basemapStyle(tilesAvailable: boolean): StyleSpecification`, `tilesExist(): Promise<boolean>` (`HEAD /tiles/seoul.pmtiles`)
  - `MapView({ frame, center, tilesAvailable })`
  - dev: Vite 5173에서 `/ws`를 8000으로 proxy

- [ ] **Step 1: 템플릿 생성과 의존성 설치**

Run:
```bash
cd modules
npx --yes create-vite@latest cop-ui-tmp --template react-ts --no-interactive
cp -rn cop-ui-tmp/. cop-ui/ && rm -rf cop-ui-tmp
cd cop-ui
npm install && npm install maplibre-gl@^6 pmtiles@^4 @protomaps/basemaps@^5
npm install -D vitest@^3 @types/geojson
rm -rf src/App.css src/assets public/vite.svg
cd ../..
test -f modules/cop-ui/src/contracts.gen.ts && echo "contracts.gen.ts 유지됨"
```
`cop-ui/`에는 Task 11에서 만든 `src/contracts.gen.ts`가 이미 있어서 템플릿을 직접 만들면 "폴더가 비어 있지 않음" 질문으로 멈춘다. 그래서 임시 폴더에 만든 뒤 덮어쓰지 않고(`cp -n`) 복사한다. 설치 여부를 묻는 질문이 나오면 No로 답한다.
Expected: `modules/cop-ui/package.json` 생성, "contracts.gen.ts 유지됨" 출력.

`modules/cop-ui/package.json`의 `scripts`에 `"test": "vitest run"` 추가.

- [ ] **Step 2: 모듈 문서와 SPEC**

`modules/cop-ui/AGENTS.md`:
```markdown
# cop-ui — 지도 관제 화면 (React + MapLibre)

- 책임: gateway `/ws`의 Frame을 받아 지도에 표적·분류·위협도·대응 추천을 표시한다.
- 데이터 타입은 `src/contracts.gen.ts`(자동 생성)만 쓴다. 직접 수정 금지.
- 구조: `src/features/<기능>/` 아래 컴포넌트·hook 1개 = 파일 1개, 200줄 이하.
- 로직(데이터 변환, hook)은 vitest 테스트를 둔다. 화면 컴포넌트는 테스트 생략 가능.
- 외부 네트워크 금지: 지도 배경은 `public/tiles/seoul.pmtiles`(scripts/fetch_tiles.sh). 글꼴·라벨 없이 그린다.
- 실행: `npm run dev` (5173, /ws는 8000 proxy) / 테스트: `npm test`
- 담당: 팀원 4. 브랜치 `cop-ui/<주제>`.
```

`modules/cop-ui/SPEC.md`:
```markdown
<!-- prefix: UI -->
# cop-ui SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| UI-01 | toGeoJSON | Frame | FeatureCollection | 표적마다 점 1개, 분류·위협도·대응 속성 | 리드 | 완료 |
| UI-02 | useFrames | ws url | {frame, connected} | 끊기면 1초 뒤 재연결 | 리드 | 완료 |
| UI-03 | MapView | frame, center | 지도 | 분류별 색, 위협도별 크기 | 리드 | 완료 |
| UI-04 | AlertList | frame | 목록 | 위협도 내림차순, 대응 추천 표시 | 리드 | 완료 |
| UI-05 | basemapStyle | tilesAvailable | Style | 타일 있으면 로컬 pmtiles(라벨 없음), 없으면 배경만 | 리드 | 완료 |
```

- [ ] **Step 3: 실패하는 테스트 작성**

`modules/cop-ui/src/features/map/toGeoJSON.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import frame from "../../../../../contracts/examples/frame.json";
import type { Frame } from "../../contracts.gen";
import { toGeoJSON } from "./toGeoJSON";

describe("toGeoJSON", () => {
  it("makes one point per track with assessment and response props", () => {
    const fc = toGeoJSON(frame as Frame);
    expect(fc.features).toHaveLength(1);
    const f = fc.features[0];
    expect(f.geometry.coordinates).toEqual([126.978, 37.5665]);
    expect(f.properties).toEqual({ id: "T-D-1", cls: "drone", threat: 0.82, response: "soft_kill" });
  });

  it("defaults when assessment or response is missing", () => {
    const fc = toGeoJSON({ ...(frame as Frame), assessments: [], responses: [] });
    expect(fc.features[0].properties).toMatchObject({ cls: "unknown", threat: 0, response: "observe" });
  });
});
```

`tsconfig.app.json`: `compilerOptions`에 `"resolveJsonModule": true` 추가, 최상위에 `"exclude": ["src/**/*.test.ts"]` 추가(테스트 파일은 tsc 빌드에서 제외, vitest만 실행).

- [ ] **Step 4: 실패 확인**

Run: `cd modules/cop-ui && npx vitest run; cd ../..`
Expected: FAIL — `Failed to resolve import "./toGeoJSON"` / `"./basemap"`.

- [ ] **Step 5: 구현**

`modules/cop-ui/src/features/map/toGeoJSON.ts`:
```ts
import type { FeatureCollection, Point } from "geojson";
import type { Frame } from "../../contracts.gen";

export function toGeoJSON(frame: Frame): FeatureCollection<Point> {
  const assess = new Map(frame.assessments.map((a) => [a.track_id, a]));
  const resp = new Map(frame.responses.map((r) => [r.track_id, r]));
  return {
    type: "FeatureCollection",
    features: frame.tracks.map((t) => ({
      type: "Feature",
      geometry: { type: "Point", coordinates: [t.lon, t.lat] },
      properties: {
        id: t.id,
        cls: assess.get(t.id)?.object_class ?? "unknown",
        threat: assess.get(t.id)?.threat ?? 0,
        response: resp.get(t.id)?.kind ?? "observe",
      },
    })),
  };
}
```

`modules/cop-ui/src/features/live/useFrames.ts`:
```ts
import { useEffect, useState } from "react";
import type { Frame } from "../../contracts.gen";

export function useFrames(url: string): { frame: Frame | null; connected: boolean } {
  const [frame, setFrame] = useState<Frame | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let timer: number | undefined;
    let stopped = false;
    const connect = () => {
      ws = new WebSocket(url);
      ws.onopen = () => setConnected(true);
      ws.onmessage = (e) => setFrame(JSON.parse(e.data) as Frame);
      ws.onclose = () => {
        setConnected(false);
        if (!stopped) timer = window.setTimeout(connect, 1000);
      };
    };
    connect();
    return () => {
      stopped = true;
      window.clearTimeout(timer);
      ws?.close();
    };
  }, [url]);

  return { frame, connected };
}
```

`modules/cop-ui/src/features/map/basemap.ts`:
```ts
import { layers, namedFlavor } from "@protomaps/basemaps";
import type { LayerSpecification, StyleSpecification } from "maplibre-gl";

const TILES_PATH = "/tiles/seoul.pmtiles";
const BG: LayerSpecification = { id: "bg", type: "background", paint: { "background-color": "#0b1320" } };

export async function tilesExist(): Promise<boolean> {
  try {
    const r = await fetch(TILES_PATH, { method: "HEAD" });
    return r.ok;
  } catch {
    return false;
  }
}

export function basemapStyle(tilesAvailable: boolean): StyleSpecification {
  if (!tilesAvailable) return { version: 8, sources: {}, layers: [BG] };
  const origin = typeof location === "undefined" ? "http://localhost" : location.origin;
  const base = layers("protomaps", namedFlavor("dark")).filter((l) => l.type !== "symbol");
  return {
    version: 8,
    sources: { protomaps: { type: "vector", url: `pmtiles://${origin}${TILES_PATH}` } },
    layers: [BG, ...(base as LayerSpecification[])],
  };
}
```
라벨(symbol) 레이어를 빼서 글꼴 파일(glyphs)을 외부에서 받을 필요가 없다. 타일이 없으면 배경만 그린다.

`modules/cop-ui/src/features/map/basemap.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { basemapStyle } from "./basemap";

describe("basemapStyle", () => {
  it("returns background-only style when tiles missing", () => {
    const s = basemapStyle(false);
    expect(Object.keys(s.sources)).toHaveLength(0);
    expect(s.layers.map((l) => l.type)).toEqual(["background"]);
  });

  it("uses local pmtiles without any symbol layers when tiles exist", () => {
    const s = basemapStyle(true);
    const src = s.sources.protomaps as { type: string; url: string };
    expect(src.type).toBe("vector");
    expect(src.url).toMatch(/^pmtiles:\/\/.*\/tiles\/seoul\.pmtiles$/);
    expect(s.layers.some((l) => l.type === "symbol")).toBe(false);
    expect(s.glyphs).toBeUndefined();
    expect(s.layers.length).toBeGreaterThan(5);
  });
});
```

`modules/cop-ui/src/features/map/MapView.tsx`:
```tsx
import maplibregl, { type ExpressionSpecification, type GeoJSONSource } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef } from "react";
import type { Frame } from "../../contracts.gen";
import { basemapStyle } from "./basemap";
import { toGeoJSON } from "./toGeoJSON";

const CLASS_COLOR = ["match", ["get", "cls"], "drone", "#ff4d4f", "balloon", "#faad14",
  "bird", "#52c41a", "#bfbfbf"] as ExpressionSpecification;

export function MapView({ frame, center, tilesAvailable = false }:
  { frame: Frame | null; center: [number, number]; tilesAvailable?: boolean }) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!el.current) return;
    const m = new maplibregl.Map({ container: el.current, style: basemapStyle(tilesAvailable), center, zoom: 13 });
    m.on("load", () => {
      m.addSource("tracks", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      m.addLayer({ id: "tracks", type: "circle", source: "tracks", paint: {
        "circle-color": CLASS_COLOR,
        "circle-radius": ["+", 5, ["*", 10, ["get", "threat"]]],
        "circle-stroke-color": "#fff", "circle-stroke-width": 1 } });
    });
    map.current = m;
    return () => m.remove();
  }, [center, tilesAvailable]);

  useEffect(() => {
    const src = map.current?.getSource("tracks") as GeoJSONSource | undefined;
    if (src && frame) src.setData(toGeoJSON(frame));
  }, [frame]);

  return <div ref={el} className="map" />;
}
```

`modules/cop-ui/src/features/alerts/AlertList.tsx`:
```tsx
import type { Frame } from "../../contracts.gen";

const LABEL: Record<string, string> = { observe: "관찰", soft_kill: "소프트킬", hard_kill: "하드킬" };

export function AlertList({ frame }: { frame: Frame | null }) {
  if (!frame) return <div className="alerts">연결 대기 중…</div>;
  const resp = new Map(frame.responses.map((r) => [r.track_id, r]));
  const rows = [...frame.assessments].sort((a, b) => b.threat - a.threat);
  return (
    <div className="alerts">
      <h2>위협 목록</h2>
      {rows.map((a) => {
        const kind = resp.get(a.track_id)?.kind ?? "observe";
        return (
          <div key={a.track_id} className={`alert ${kind}`}>
            <b>{a.track_id}</b> {a.object_class} · 위협 {a.threat.toFixed(2)} · {LABEL[kind]}
            <div className="reason">{a.reason}</div>
          </div>
        );
      })}
    </div>
  );
}
```

`modules/cop-ui/src/App.tsx`:
```tsx
import { AlertList } from "./features/alerts/AlertList";
import { useFrames } from "./features/live/useFrames";
import { MapView } from "./features/map/MapView";

const WS_URL = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`;
const CENTER: [number, number] = [126.978, 37.5665];

export default function App() {
  const { frame, connected } = useFrames(WS_URL);
  return (
    <div className="layout">
      <MapView frame={frame} center={CENTER} />
      <aside>
        <div className={connected ? "status ok" : "status down"}>{connected ? "LIVE" : "연결 끊김"}</div>
        <AlertList frame={frame} />
      </aside>
    </div>
  );
}
```

`modules/cop-ui/src/index.css`:
```css
html, body, #root { margin: 0; height: 100%; background: #0b1320; color: #e6e6e6; font-family: system-ui, sans-serif; }
.layout { display: grid; grid-template-columns: 1fr 360px; height: 100%; }
.map { width: 100%; height: 100%; }
aside { overflow-y: auto; padding: 12px; border-left: 1px solid #22304a; }
.status { font-weight: 700; margin-bottom: 8px; }
.status.ok { color: #52c41a; } .status.down { color: #ff4d4f; }
.alert { padding: 8px; margin-bottom: 6px; border-radius: 6px; background: #14213a; }
.alert.soft_kill { border-left: 4px solid #faad14; } .alert.hard_kill { border-left: 4px solid #ff4d4f; }
.reason { font-size: 12px; opacity: 0.8; }
```

`modules/cop-ui/vite.config.ts`:
```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/ws": { target: "ws://localhost:8000", ws: true } } },
});
```

`modules/cop-ui/eslint.config.js`: `files: ['**/*.{ts,tsx}']` 블록에 `rules: { "max-lines": ["error", { max: 200 }] }`를 추가하고, `globalIgnores(['dist'])`를 `globalIgnores(['dist', 'src/contracts.gen.ts'])`로 바꾼다.

- [ ] **Step 6: 테스트·빌드·lint 확인**

Run: `cd modules/cop-ui && npm test && npm run build && npx eslint src; cd ../..`
Expected: vitest 4 passed, `dist/` 생성, eslint 오류 없음.

- [ ] **Step 7: 화면 수동 확인**

Run (터미널 2개): `uv run uvicorn modules.gateway.app:app --port 8000` / `cd modules/cop-ui && npm run dev`
브라우저 http://localhost:5173: 어두운 배경 위에 점 3~4개가 움직이고, 오른쪽에 "LIVE"와 위협 목록이 갱신된다. gateway를 끄면 "연결 끊김", 다시 켜면 1초 안에 "LIVE".

- [ ] **Step 8: 커밋**

```bash
git add modules/cop-ui
git commit -m "feat: add cop-ui map view with live frames and alert list

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```
Expected: pre-commit 통과(ts 파일 200줄 이하, node_modules 제외).

---

---

### Task 13: 오프라인 지도 타일

**Files:**
- Create: `scripts/fetch_tiles.sh`, `modules/cop-ui/public/tiles/.gitkeep`
- Modify: `modules/cop-ui/src/App.tsx`, `modules/cop-ui/src/main.tsx`

**Interfaces:**
- Consumes: `basemapStyle`, `tilesExist`, `MapView({ tilesAvailable })` (Task 12)
- Produces: `scripts/fetch_tiles.sh` — go-pmtiles v1.31.2 CLI를 `.tools/`에 받고, 최신 Protomaps 빌드(`https://build-metadata.protomaps.dev/builds.json`의 마지막 key)에서 서울 수도권(bbox `126.6,37.35,127.3,37.75`, maxzoom 14)을 `modules/cop-ui/public/tiles/seoul.pmtiles`로 추출. 이미 있으면 건너뜀.

- [ ] **Step 1: 타일 연결 코드**

`modules/cop-ui/src/main.tsx`에 pmtiles 프로토콜 등록 추가(기존 import 아래):
```tsx
import maplibregl from "maplibre-gl";
import { Protocol } from "pmtiles";

maplibregl.addProtocol("pmtiles", new Protocol().tile);
```

`modules/cop-ui/src/App.tsx` 교체:
```tsx
import { useEffect, useState } from "react";
import { AlertList } from "./features/alerts/AlertList";
import { useFrames } from "./features/live/useFrames";
import { tilesExist } from "./features/map/basemap";
import { MapView } from "./features/map/MapView";

const WS_URL = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`;
const CENTER: [number, number] = [126.978, 37.5665];

export default function App() {
  const { frame, connected } = useFrames(WS_URL);
  const [tiles, setTiles] = useState(false);
  useEffect(() => { tilesExist().then(setTiles); }, []);
  return (
    <div className="layout">
      <MapView frame={frame} center={CENTER} tilesAvailable={tiles} />
      <aside>
        <div className={connected ? "status ok" : "status down"}>{connected ? "LIVE" : "연결 끊김"}</div>
        <AlertList frame={frame} />
      </aside>
    </div>
  );
}
```

- [ ] **Step 2: 타일 없는 상태 확인**

Run: `cd modules/cop-ui && npm test && npm run build && npx eslint src; cd ../..`
Expected: vitest 4 passed, 빌드·lint 통과.

dev 실행(gateway `uv run uvicorn modules.gateway.app:app --port 8000` + `cd modules/cop-ui && npm run dev`): 타일이 없으므로 배경색 위에 표적만 보이고 브라우저 콘솔에 오류가 없어야 한다.

- [ ] **Step 3: 타일 다운로드 스크립트**

`scripts/fetch_tiles.sh`:
```bash
#!/usr/bin/env bash
# Download Seoul metro basemap tiles once (needs internet). Demo then runs offline.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
OUT=modules/cop-ui/public/tiles/seoul.pmtiles
BBOX="126.6,37.35,127.3,37.75"
VER=1.31.2
if [ -s "$OUT" ]; then echo "tiles already present: $OUT"; exit 0; fi
mkdir -p .tools "$(dirname "$OUT")"
if [ ! -x .tools/pmtiles ]; then
  arch=$(uname -m); [ "$arch" = "aarch64" ] && arch=arm64
  curl -fsSL "https://github.com/protomaps/go-pmtiles/releases/download/v${VER}/go-pmtiles_${VER}_Linux_${arch}.tar.gz" \
    | tar -xz -C .tools pmtiles
fi
BUILD=$(curl -fsSL https://build-metadata.protomaps.dev/builds.json | python3 -c "import json,sys; print(json.load(sys.stdin)[-1]['key'])")
.tools/pmtiles extract "https://build.protomaps.com/${BUILD}" "$OUT" --bbox="$BBOX" --maxzoom=14
ls -lh "$OUT"
```

Run: `chmod +x scripts/fetch_tiles.sh && touch modules/cop-ui/public/tiles/.gitkeep && scripts/fetch_tiles.sh`
Expected: `seoul.pmtiles` 생성(수십 MB). macOS 팀원은 `Darwin` 릴리스 파일이 필요하므로, 시연 노트북에서 받은 파일을 USB나 공유 드라이브로 복사한다.

- [ ] **Step 4: 오프라인 확인**

dev 실행 시 서울 도로·하천·건물 윤곽이 보인다. 와이파이를 끄고 새로고침해도 지도가 그대로 보인다.

- [ ] **Step 5: 커밋**

```bash
git add scripts/fetch_tiles.sh modules/cop-ui
git commit -m "feat: add offline Seoul basemap via local pmtiles

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```
Expected: `seoul.pmtiles`는 gitignore로 커밋되지 않음.

---

---

### Task 14: setup / ship / dev / demo 스크립트와 전체 검증

**Files:**
- Create: `scripts/setup.sh`, `scripts/ship.sh`, `scripts/dev.sh`, `scripts/demo.sh`, `tests/test_ship.py`

**Interfaces:**
- Consumes: 모든 이전 Task
- Produces:
  - `scripts/setup.sh <모듈> [--worktree <모듈2>]`: uv sync, cop-ui npm ci, `core.hooksPath=.githooks`, 브랜치 `<모듈>/work` 생성·전환(있으면 전환만), `--worktree`면 `../<repo>-<모듈2>`에 `<모듈2>/work` worktree 생성, sync_docs, 타일 없으면 fetch 시도(실패해도 계속)
  - `scripts/ship.sh`: 깨끗한 작업 트리 확인 → fetch → `rebase origin/main` → 변경 모듈 pytest(contracts·shared 변경 시 전체) → smoke → `push origin HEAD:main`. 실패 시 짧은 메시지와 exit 1
  - `scripts/dev.sh`: gateway(reload, 8000) + vite(5173) 동시 실행, Ctrl+C로 둘 다 종료
  - `scripts/demo.sh [시나리오.yaml]`: UI 빌드 후 gateway 하나로 UI+WS 서빙(8000)

- [ ] **Step 1: 실패하는 테스트 작성 (ship을 임시 원격으로 검증)**

`tests/test_ship.py`:
```python
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_GIT = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.hooksPath=/dev/null"]


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *ENV_GIT, *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def make_clone(tmp_path: Path) -> tuple[Path, Path]:
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(remote))
    work = tmp_path / "work"
    shutil.copytree(
        ROOT,
        work,
        ignore=shutil.ignore_patterns(
            ".git", "node_modules", "dist", ".venv", "*.pmtiles", ".tools", "__pycache__"
        ),
    )
    (work / ".venv").symlink_to(ROOT / ".venv")
    git(work, "init", "-q", "-b", "main")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "base")
    git(work, "remote", "add", "origin", str(remote))
    git(work, "push", "-q", "origin", "main")
    git(work, "switch", "-q", "-c", "tracking/work")
    return remote, work


def test_ship_pushes_rebased_branch_to_main(tmp_path):
    remote, work = make_clone(tmp_path)
    (work / "knowledge/inbox/note.md").write_text("x\n")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "note")
    r = subprocess.run(
        ["bash", "scripts/ship.sh"],
        cwd=work,
        capture_output=True,
        text=True,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(tmp_path),
            "GIT_CONFIG_PARAMETERS": "'core.hookspath=/dev/null'",
        },
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "note" in git(work, "log", "--oneline", "origin/main", "-1")


def test_ship_refuses_dirty_tree(tmp_path):
    _, work = make_clone(tmp_path)
    (work / "README.md").write_text("dirty\n")
    r = subprocess.run(["bash", "scripts/ship.sh"], cwd=work, capture_output=True, text=True)
    assert r.returncode == 1 and "커밋" in r.stdout + r.stderr


def test_ship_fails_on_broken_module_test(tmp_path):
    _, work = make_clone(tmp_path)
    t = work / "modules/tracking/tests/test_delete_stale_tracks.py"
    t.write_text(t.read_text() + "\n\ndef test_broken():\n    assert False\n")
    git(work, "commit", "-qam", "break")
    r = subprocess.run(["bash", "scripts/ship.sh"], cwd=work, capture_output=True, text=True)
    assert r.returncode == 1
    assert "test_broken" in r.stdout + r.stderr
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_ship.py`
Expected: FAIL (scripts/ship.sh 없음).

- [ ] **Step 3: 구현**

`scripts/ship.sh`:
```bash
#!/usr/bin/env bash
# Rebase on origin/main, test changed modules, smoke test, push to main (target < 20s).
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=".venv/bin/python"; PYTEST=".venv/bin/pytest"
fail() { echo "[ship] $*"; exit 1; }

git diff --quiet && git diff --cached --quiet || fail "커밋 안 된 변경이 있습니다. 먼저 커밋하세요."
git fetch -q origin || fail "fetch 실패 (네트워크 확인)"
git rebase -q origin/main || fail "rebase 충돌. 'git status'로 충돌 파일을 확인하고 해결 후 'git rebase --continue', 그다음 다시 ship. 남의 파일이면 담당자에게 문의."

changed=$(git diff --name-only origin/main...HEAD)
if echo "$changed" | grep -qE '^(contracts|shared)/'; then
  targets="tests modules"
else
  targets=$(echo "$changed" | awk -F/ '$1=="modules"{print $2}' | sort -u \
    | while read -r m; do [ -f "modules/$m/__init__.py" ] && echo "modules/$m"; done | tr '\n' ' ')
fi
if [ -n "${targets// /}" ]; then
  out=$("$PYTEST" -q -x $targets 2>&1) || { echo "$out" | tail -25; fail "테스트 실패"; }
fi
out=$("$PY" scripts/smoke.py 2>&1) || { echo "$out"; fail "데모 smoke test 실패"; }
"$PY" scripts/sync_docs.py >/dev/null 2>&1 || true
git push -q origin HEAD:main || fail "push 실패. 누군가 먼저 push했을 수 있습니다. 다시 ship 하세요."
echo "[ship] 완료: $(git log --oneline -1)"
```

`scripts/setup.sh`:
```bash
#!/usr/bin/env bash
# One-time setup. Usage: scripts/setup.sh <module> [--worktree <module2>]
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
mod="${1:?사용법: scripts/setup.sh <모듈> [--worktree <모듈2>]}"
[ -d "modules/$mod" ] || [ "$mod" = "infra" ] || [ "$mod" = "contracts" ] || { echo "모듈 없음: $mod"; exit 1; }

uv sync
(cd modules/cop-ui && npm ci --silent)
git config core.hooksPath .githooks
chmod +x scripts/*.sh .githooks/*
git fetch -q origin
if git show-ref --quiet "refs/heads/$mod/work"; then git switch -q "$mod/work"
else git switch -q -c "$mod/work" origin/main; fi

if [ "${2:-}" = "--worktree" ]; then
  wt="${3:?--worktree 다음에 모듈 이름}"
  dir="../$(basename "$PWD")-$wt"
  git worktree add -q -b "$wt/work" "$dir" origin/main
  ln -s "$PWD/.venv" "$dir/.venv"
  echo "worktree: $dir (브랜치 $wt/work)"
fi

.venv/bin/python scripts/sync_docs.py
scripts/fetch_tiles.sh || echo "[setup] 지도 타일 받기 실패 — 나중에 scripts/fetch_tiles.sh 재실행"
echo "[setup] 완료. 현재 브랜치: $(git branch --show-current)"
```

`scripts/dev.sh`:
```bash
#!/usr/bin/env bash
# Dev run: gateway (8000, reload) + vite (5173). Ctrl+C stops both.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
trap 'kill 0' EXIT
.venv/bin/uvicorn modules.gateway.app:app --port 8000 --reload --reload-dir modules --reload-dir contracts &
(cd modules/cop-ui && npm run dev -- --port 5173) &
echo "http://localhost:5173"
wait
```

`scripts/demo.sh`:
```bash
#!/usr/bin/env bash
# Demo run (offline): build UI, serve UI + /ws from one process on :8000.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
(cd modules/cop-ui && npm run build --silent)
[ -s modules/cop-ui/public/tiles/seoul.pmtiles ] || echo "[demo] 경고: 지도 타일 없음 (배경 없이 표적만 표시)"
export KDTH_SCENARIO="${1:-demo/scenarios/seoul_mixed.yaml}"
export KDTH_UI_DIST="$PWD/modules/cop-ui/dist"
echo "http://localhost:8000"
exec .venv/bin/uvicorn modules.gateway.app:app --port 8000
```

Run: `chmod +x scripts/*.sh`

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_ship.py`
Expected: PASS (3 passed).

- [ ] **Step 5: 전체 테스트와 시간 측정**

Run:
```bash
uv run pytest
(cd modules/cop-ui && npm test)
time scripts/check.sh
time uv run python scripts/smoke.py
```
Expected: 전부 PASS. check.sh `real` 2초 이하, smoke 1초 이하.

- [ ] **Step 6: 시연 경로 수동 확인 (오프라인)**

Run: `scripts/demo.sh` 후 와이파이를 끄고 http://localhost:8000 접속.
Expected: 서울 지도 배경 + 움직이는 표적 + 위협 목록. 탭을 하나 더 열어도 두 탭 모두 갱신. 터미널에 오류 없음.

- [ ] **Step 7: 커밋 후 main 반영**

```bash
git add scripts/setup.sh scripts/ship.sh scripts/dev.sh scripts/demo.sh tests/test_ship.py
git commit -m "feat: add setup, ship, dev and demo scripts

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
scripts/ship.sh
```
Expected: `[ship] 완료`. GitHub `main`에 골격 전체가 올라간다.

- [ ] **Step 8: 새 clone으로 팀원 경험 재현**

```bash
cd /tmp && rm -rf kdth-check && git clone -q https://github.com/kth9245/d4d-edth-seoul-2026 kdth-check && cd kdth-check
scripts/setup.sh tracking
git branch --show-current            # tracking/work
uv run python scripts/new_action.py tracking smooth_tracks "표적 위치 평활화" --owner 테스트
uv run pytest modules/tracking/tests/test_smooth_tracks.py   # 생성된 실패 테스트 → FAIL 확인
git restore --staged . ; git checkout -- . ; git clean -fdq modules/tracking
cd /tmp && rm -rf kdth-check
```
Expected: setup 성공, 브랜치 `tracking/work`, new_action이 SPEC 행·파일·실패 테스트 생성.

---

### Task 15: AI 도구 연결 (Claude·Codex hook, skill)

**Files:**
- Create: `.claude/settings.json`, `.codex/hooks.json`, `.agents/skills/new-action/SKILL.md`, `.agents/skills/kb-save/SKILL.md`, `.agents/skills/decide/SKILL.md`, `.agents/skills/ship/SKILL.md`, `.claude/skills` (symlink → `../.agents/skills`), `tests/test_agent_config.py`

**Interfaces:**
- Consumes: `tools/guard/check_edit.py` CLI, `scripts/new_action.py`, `scripts/decide.py`, `scripts/sync_docs.py`, `scripts/ship.sh`(Task 14)

- [ ] **Step 1: 작성 순서 확인**

`.claude/settings.json`을 쓰는 순간 이 세션에도 guard가 적용될 수 있다(main 브랜치에서는 modules·tests 수정이 막힘). 그래서 테스트 파일, skill, `.codex/hooks.json`, symlink를 먼저 만들고 `.claude/settings.json`을 **맨 마지막**에 쓴다. 이후 수정이 필요하면 `git switch -c infra/fix`에서 한다.

- [ ] **Step 2: 실패하는 테스트 작성**

`tests/test_agent_config.py`:
```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_claude_hooks_call_guard():
    cfg = json.loads((ROOT / ".claude/settings.json").read_text())
    pre = cfg["hooks"]["PreToolUse"][0]
    assert pre["matcher"] == "Edit|Write|MultiEdit|NotebookEdit"
    assert 'check_edit.py" pre' in pre["hooks"][0]["command"]
    assert 'check_edit.py" post' in cfg["hooks"]["PostToolUse"][0]["hooks"][0]["command"]


def test_codex_hooks_call_guard():
    cfg = json.loads((ROOT / ".codex/hooks.json").read_text())
    assert cfg["hooks"]["PreToolUse"][0]["matcher"] == "^apply_patch$"
    assert 'check_edit.py" pre' in cfg["hooks"]["PreToolUse"][0]["hooks"][0]["command"]


def test_skills_shared_via_symlink():
    link = ROOT / ".claude/skills"
    assert link.is_symlink() and link.resolve() == (ROOT / ".agents/skills").resolve()
    for name in ("new-action", "kb-save", "decide", "ship"):
        text = (ROOT / ".agents/skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith(f"---\nname: {name}\ndescription: ")


def test_no_claude_md_anywhere():
    found = [p for p in ROOT.rglob("CLAUDE*.md") if "node_modules" not in p.parts]
    assert found == []
```

- [ ] **Step 3: 실패 확인**

Run: `uv run pytest tests/test_agent_config.py`
Expected: FAIL — `FileNotFoundError: .claude/settings.json`.

- [ ] **Step 4: 설정 파일 작성**

`.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [{"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/tools/guard/check_edit.py\" pre"}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [{"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/tools/guard/check_edit.py\" post"}]
      }
    ]
  }
}
```

`.codex/hooks.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^apply_patch$",
        "hooks": [{"type": "command", "command": "python3 \"$(git rev-parse --show-toplevel)/tools/guard/check_edit.py\" pre"}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "^apply_patch$",
        "hooks": [{"type": "command", "command": "python3 \"$(git rev-parse --show-toplevel)/tools/guard/check_edit.py\" post"}]
      }
    ]
  }
}
```

`.agents/skills/new-action/SKILL.md`:
```markdown
---
name: new-action
description: Start a new action in a module. Use whenever you are about to add new behavior to modules/<m>/ — creates the SPEC.md row, the action file skeleton and a failing test in one step.
---

1. Pick a `verb_noun` name and a one-line Korean description.
2. Run: `python scripts/new_action.py <module> <verb_noun> "<설명>" --inputs "<타입>" --outputs "<타입>" --done "<완료 기준>"`
3. Replace the generated failing test with a real test of the behavior (inputs from `contracts/examples/*.json` when possible).
4. Implement the action until `uv run pytest modules/<module>/tests/test_<verb_noun>.py` passes. Keep the file <= 80 lines; if it grows, split into another action.
5. Wire it into `modules/<module>/pipeline.py` and export from `__init__.py` only if other modules need it.
6. Set the SPEC.md row status to `완료`.
```

`.agents/skills/kb-save/SKILL.md`:
```markdown
---
name: kb-save
description: Turn research findings into knowledge cards. Use after researching anything (web search, docs, experiments) or when knowledge/inbox/ has unprocessed material.
---

1. Read `knowledge/INDEX.md` and the files in `knowledge/inbox/`.
2. For each distinct conclusion, update the existing card if one covers it; otherwise create `knowledge/cards/<kebab-id>.md`:
   frontmatter `id, title, summary (one line), tags [..], modules [..], confidence (확인됨|추정), sources [urls], author`,
   then sections `## 결론`, `## 근거`, `## 코드에 적용하는 법`, `## 관련 카드` (`[[id]]`). Max 40 lines.
3. No source URL → `confidence: 추정`. Never invent sources.
4. Move processed inbox files to `knowledge/inbox/done/`.
5. Run `python scripts/sync_docs.py` to refresh the index.
```

`.agents/skills/decide/SKILL.md`:
```markdown
---
name: decide
description: Record a human decision or policy. Use when a person states a choice ("앞으로 ~로 하자", "~는 쓰지 말자") or when your work needs a decision a person must make.
---

1. Check `decisions/INDEX.md` for an existing decision on the topic.
2. Run: `python scripts/decide.py new "<제목>" --modules <m1,m2>` and fill `## 결정`, `## 이유`, `## 버린 대안`, `## 영향`.
3. Leave `status: 제안`. You cannot set `확정` (the guard blocks it).
4. Tell the person: "확정하려면 `! python scripts/decide.py accept NNNN --by <이름>`을 직접 실행해 주세요."
5. Standing rules (always apply) belong in `decisions/POLICY.md`, which only humans edit — propose the wording in chat.
```

`.agents/skills/ship/SKILL.md`:
```markdown
---
name: ship
description: Push finished work to main. Use when one or more actions are done and committed.
---

1. Make sure everything is committed (`git status` clean).
2. Run `scripts/ship.sh`. It rebases on origin/main, runs tests of changed modules and the demo smoke test, then pushes to main.
3. On failure, read the short failure output, fix it, commit, and run `scripts/ship.sh` again.
4. On rebase conflict in a file you do not own, stop and ask the owner.
```

Run: `ln -s ../.agents/skills .claude/skills`

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest tests/test_agent_config.py`
Expected: PASS (4 passed).

- [ ] **Step 6: Claude Code에서 hook 동작 수동 확인**

새 터미널에서 저장소 루트로 `claude`를 실행하고(브랜치 `main`) 다음을 요청한다: "modules/tracking/pipeline.py 파일에 `x = 1` 한 줄을 만들어줘".
Expected: guard가 차단하고 "`tracking/<주제>` 브랜치 담당" 메시지가 대화에 표시된다. `/hooks`에서 PreToolUse·PostToolUse가 보인다. `/skills`(또는 `/`)에서 new-action, kb-save, decide, ship이 보인다.

- [ ] **Step 7: 커밋**

```bash
git add .claude .codex .agents tests/test_agent_config.py
git commit -m "feat: wire guard hooks and shared skills for Claude Code and Codex

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
scripts/ship.sh
```
Expected: `[ship] 완료`. 이후 저장소의 모든 AI 수정은 브랜치 소유 규칙을 따른다.

- [ ] **Step 8: Codex hook 확인 (Codex 쓰는 팀원 노트북에서)**

이 PC에는 Codex가 없으므로 Codex 사용자 노트북에서 확인한다: `cd modules/tracking && codex` → `/hooks`에서 저장소 hook 신뢰 승인 → "../assess/pipeline.py에 한 줄 추가해줘" 요청.
Expected: guard가 차단하고 이유가 표시된다. 동작하지 않으면 `.codex/hooks.json`의 command를 Codex 공식 문서(https://learn.chatgpt.com/docs/hooks) 형식에 맞게 고치고 결과를 `knowledge/inbox/`에 남긴다.

---
