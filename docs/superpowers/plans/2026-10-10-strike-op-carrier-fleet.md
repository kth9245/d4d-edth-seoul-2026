# T1 공격 작전 모선 편대 Implementation Plan (1번: 수상정 한 척에서 정찰 3대·공격 3대)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `baengnyeong_strike` 시나리오의 기체를 "육지 패드의 드론 4대 + 수상정 + 지상 로봇"에서 "정지한 수상정 1척 + 정찰 드론 `r1`~`r3` + 공격 드론 `a1`~`a3`(모두 수상정 자리에서 출발·귀환) + 지상 로봇"으로 바꾼다. 식별된 거점의 카드에는 `a1`·`a2`·`a3`와 전원 타격 승인만 나온다.

**Architecture:** 데이터만 바꾼다. `scripts/make_strike_scenario.py`가 야간 시나리오의 기체를 복사해 새 기체 목록을 만들고, `demo/scenarios/baengnyeong_strike.json`을 다시 만든다. 타격 선택지를 만드는 `refresh_strike_cards`는 능력(`strike_target`)으로 기체를 찾으므로 코드 변경이 없다. 기체 id를 쓰던 테스트만 새 id로 맞춘다.

**Tech Stack:** Python, pytest(`uv run pytest …`, 디버깅 `-n 0`), 시나리오 JSON.

**Spec:** `docs/superpowers/specs/2026-10-10-strike-op-carrier-fleet-design.md`(4절 기체 구성, 6절 바뀌는 파일, 7절 위험). 앞 단계 계획: `docs/superpowers/plans/2026-10-10-strike-op-stage2.md`.

## Global Constraints

- **코드·계약·정책은 바꾸지 않는다.** 바꾸는 것은 `scripts/make_strike_scenario.py`, 그 결과 `demo/scenarios/baengnyeong_strike.json`, 테스트, `demo/BUILT_HERE.md`뿐이다. cop-ui와 `modules/*` 코드는 건드리지 않는다.
- JSON은 생성 결과가 정본이다(결정 0035). **JSON을 직접 고치지 않고** 스크립트를 고친 뒤 `uv run python scripts/make_strike_scenario.py`로 다시 만든다. `tests/test_strike_scenario.py::test_the_json_is_what_the_script_builds`가 어긋남을 잡는다.
- 기체 id는 정확히 `usv`, `r1`, `r2`, `r3`, `a1`, `a2`, `a3`, `ugv`(이 순서). 야간·24시간 작전의 `d1~d4`는 그대로다.
- 수상정 자리 `home` = `{"lat": 37.981, "lon": 124.691, "alt_m": 0.0}`(야간 시나리오 수상정의 `home`와 같은 값, 육지 밖). `r1~r3`, `a1~a3`의 `home`은 모두 이 값이다. `ugv`의 `home`은 그대로.
- 수상정 종류는 `sea_vehicle`(타격 불가). 정찰은 `recon_drone`, 공격은 `armed_drone`. 온톨로지는 바꾸지 않는다.
- 시작 배정: `r1`은 `site_patrol`, 나머지 7대는 `standby`.
- 모든 코드 변경은 실패하는 테스트를 먼저 쓴다(결정 0014). 커밋 메시지 끝에 `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`를 붙인다.
- 작업은 자기 worktree에서(`/home/dongho/d4d-strike-s2`, 브랜치 `strike-carrier`). `scripts/ship.sh`와 push는 사람이 시키기 전에 하지 않는다.
- 용어는 **Role**(결정 0052).

## Review Focus

- **공중 기체의 `home`이 바다여도 작전 검사가 통과한다**: `check_operation(...).ok`와 인수 테스트(타격이 막히지 않음, `es.blocks` 비어 있음)가 잡는다(Task 1, 2).
- **수상정은 타격 선택지를 만들지 않는다**: 카드의 선택지 id가 정확히 `strike_a1`, `strike_a2`, `strike_a3`, `strike_all`이다(Task 2).
- **고른 공격 드론만 움직인다**: `a2`만 승인하면 `a1`·`a3`는 수상정 자리에 그대로 있고 대기 Role이다(Task 2).
- **야간·24시간 작전이 그대로다**: 두 시나리오 파일이 바뀌지 않고, `tests/test_demo_routes.py`의 세 시나리오 검사가 통과한다(Task 1, 3).
- **옛 id가 JSON에 남지 않는다**: `d1`~`d4`가 strike JSON의 기체·배정·카드 어디에도 없다(Task 1).

---

### Task 1: 생성 스크립트가 모선 편대를 만들고, 기체 id를 쓰는 테스트를 맞춘다

**Files:**
- Modify: `scripts/make_strike_scenario.py` (기체 목록, 작전의 `vehicle_ids`·`assign`, 작전 목적 문구)
- Regenerate: `demo/scenarios/baengnyeong_strike.json` (직접 고치지 않는다)
- Test: `tests/test_strike_scenario.py`, `modules/gateway/tests/test_strike_threat.py`, `modules/gateway/tests/test_engine_ident.py`

**Interfaces:**
- Produces: `fleet(night_vehicles: list[dict]) -> list[dict]`(스크립트 안의 함수, 위 Global Constraints의 8대를 이 순서로 돌려준다). 이후 작업은 JSON의 기체 id만 쓴다.

- [ ] **Step 1: 새 구성을 검사하는 테스트를 `tests/test_strike_scenario.py`에 더한다**

기존 `test_one_drone_starts_on_the_north_search_patrol`을 아래로 **바꾸고**(함수 이름도 새 이름), 끝에 두 테스트를 더한다. 파일 위쪽 import에 `from shared.land import inside`가 이미 있다.

```python
def test_the_fleet_is_one_usv_three_recon_three_attack_and_the_ugv(sc):
    assert [v.id for v in sc.vehicles] == ["usv", "r1", "r2", "r3", "a1", "a2", "a3", "ugv"]
    kinds = {v.id: v.kind for v in sc.vehicles}
    assert kinds == {"usv": "sea_vehicle", "r1": "recon_drone", "r2": "recon_drone",
                     "r3": "recon_drone", "a1": "armed_drone", "a2": "armed_drone",
                     "a3": "armed_drone", "ugv": "ground_robot"}  # fmt: skip
    assert sc.operation.vehicle_ids == [v.id for v in sc.vehicles]


def test_every_drone_starts_and_returns_at_the_usv_spot_on_the_sea(sc):
    by_id = {v.id: v for v in sc.vehicles}
    spot = by_id["usv"].home
    assert (spot.lat, spot.lon) == (37.981, 124.691)
    assert not inside(spot, sc.land)
    for vid in ("r1", "r2", "r3", "a1", "a2", "a3"):
        assert by_id[vid].home == spot, vid


def test_one_recon_drone_starts_on_the_north_search_patrol(sc):
    assert sc.operation.assign["r1"] == "site_patrol"
    assert {v for k, v in sc.operation.assign.items() if k != "r1"} == {"standby"}
    assert set(sc.operation.assign) == {v.id for v in sc.vehicles}
```

그리고 `test_the_strike_role_is_available_to_the_armed_vehicles`의 마지막 줄을 아래로 바꾼다(수상정은 타격하지 못한다).

```python
    assert set(armed) == {"a1", "a2", "a3"}  # the usv is a carrier now
```

그리고 파일 끝에 옛 id가 남지 않았는지 보는 테스트를 더한다.

```python
def test_no_old_vehicle_id_is_left_in_the_json():
    text = (ROOT / "demo/scenarios/baengnyeong_strike.json").read_text(encoding="utf-8")
    for old in ('"d1"', '"d2"', '"d3"', '"d4"'):
        assert old not in text, old
```

- [ ] **Step 2: 실패를 확인한다**

Run: `uv run pytest tests/test_strike_scenario.py -n 0 -q`
Expected: FAIL 다수(`['d1', 'd2', …] != ['usv', 'r1', …]` 등).

- [ ] **Step 3: 스크립트에 편대 만드는 함수를 더하고 `build()`에서 쓴다**

`scripts/make_strike_scenario.py`의 `site_hold()` 아래에 추가:

```python
def fleet(night_vehicles: list[dict]) -> list[dict]:
    """One stationary carrier USV, three recon and three attack drones that start and return at its spot."""
    by_id = {v["id"]: v for v in night_vehicles}
    usv = copy.deepcopy(by_id["usv"]) | {"name": "수상정(모선)", "kind": "sea_vehicle"}

    def drone(src: str, vid: str, name: str) -> dict:
        return copy.deepcopy(by_id[src]) | {"id": vid, "name": name, "home": dict(usv["home"])}

    recon = [drone("d1", f"r{i}", f"정찰 드론{i}") for i in (1, 2, 3)]
    armed = [drone("d2", f"a{i}", f"공격 드론{i}") for i in (1, 2, 3)]
    return [usv, *recon, *armed, copy.deepcopy(by_id["ugv"])]
```

`build()`에서 `op = ...` 바로 앞에 `vehicles = fleet(night["vehicles"])`를 넣고, `op`의 덮어쓰기 부분 `"assign": {...}`을 아래로 바꾸고 `vehicle_ids`를 더하며 `purpose`에 편대 설명을 붙인다.

```python
        "vehicle_ids": [v["id"] for v in vehicles],
        "assign": {v["id"]: ("site_patrol" if v["id"] == "r1" else "standby") for v in vehicles},
```

`purpose`는 `"…식별된 거점에만 타격 승인을 연다(2단계)"` 뒤에 `. 수상정 한 척에서 정찰 드론 3대와 공격 드론 3대가 출발한다`를 붙인다. `out = night | {` 딕셔너리에 `"vehicles": vehicles,`를 더한다.

- [ ] **Step 4: JSON을 다시 만든다**

Run: `uv run python scripts/make_strike_scenario.py`
Expected: `baengnyeong_strike.json: 3 sites, 7 roles, 6 routes`

- [ ] **Step 5: 기체 id를 쓰던 나머지 테스트를 새 id로 맞춘다**

`tests/test_strike_scenario.py`의 인수 테스트 `test_site_a_is_identified_then_approved_then_neutralized`:
- 주석 `# 3. identified: d2 and usv can be approved…`를 `# 3. identified: the three attack drones can be approved…`로 바꾼다.
- 선택지 검사를 `assert {"strike_a1", "strike_a2", "strike_a3", "strike_all"} <= {c.id for c in _card(es).choices}`로, 주석 `# 4. the operator approves d2 only…`를 `a1 only`로, `choice_id="strike_d2"`를 `choice_id="strike_a1"`로 바꾼다.

`modules/gateway/tests/test_strike_threat.py`: `[("d1", "site_a")]`를 `[("r1", "site_a")]`로 바꾼다.

`modules/gateway/tests/test_engine_ident.py`:
- `test_the_tick_loop_opens_strike_choices_only_after_identification`에서 `night = …`, `strike = …`, `sc = sc.model_copy(…)` 세 줄(야간의 `strike` Role을 끼워 넣던 임시 처리)을 지운다. JSON에 `strike` Role이 이미 있다.
- 같은 테스트의 마지막 줄을 `assert before == set() and {"strike_a1", "strike_a2", "strike_a3"} <= after`로 바꾼다.
- `test_a_click_on_a_strike_choice_that_just_vanished_does_not_stop_the_loop`에서도 같은 세 줄을 지운다.

- [ ] **Step 6: 통과를 확인한다**

Run: `uv run pytest tests/test_strike_scenario.py tests/test_demo_routes.py modules/gateway -q`
Expected: PASS. 안 되면 **어느 단계(기체 검사, 식별, 승인, 무력화)에서 멈췄는지**부터 읽는다. 예상되는 어긋남: 수상정 자리에서 출발해 첫 탐지 시각이 앞당겨져 `test_engine_ident`의 틱 수 제한을 넘는 일은 없지만(오히려 빨라짐), 인수 테스트의 `limit=9000`이 모자라면(`a1`이 거점까지 약 3 km, 15 m/s) 값을 늘린다. `check_operation`이 실패하면 메시지를 읽고 멈춘다(Task 2의 위험 항목).

- [ ] **Step 7: Commit**

```bash
git add scripts demo tests modules/gateway/tests
git commit -m "Part2-carrier: strike operation fleet is one stationary USV carrying recon drones r1-r3 and attack drones a1-a3 (all start and return at the USV spot); JSON rebuilt"
```

---

### Task 2: 카드가 공격 드론 1~3번을 고르게 하고, 고른 드론만 움직임을 확인한다

**Files:**
- Test: `tests/test_strike_scenario.py`

**Interfaces:**
- Consumes: Task 1의 기체 id(`a1~a3`, `r1`, `usv`), `refresh_strike_cards`의 선택지 id(`strike_<기체 id>`, `strike_all`).

- [ ] **Step 1: 실패 여부를 보려고 먼저 테스트를 쓴다**

`tests/test_strike_scenario.py` 끝에 더한다.

```python
def _identified_card_state(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: any(t.id == "site_a" and t.ident_state == "identified" for t in e.targets))
    return es


def test_the_card_offers_exactly_the_three_attack_drones_and_not_the_usv(sc):
    es = _identified_card_state(sc)
    ids = [c.id for c in _card(es).choices if c.id.startswith("strike_")]
    assert ids == ["strike_a1", "strike_a2", "strike_a3", "strike_all"]  # no strike_usv


def test_only_the_chosen_attack_drone_flies_to_the_site(sc):
    es = _identified_card_state(sc)
    dec = Decision(id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=_card(es).id, choice_id="strike_a2")
    es, _ = tick(es, TickInputs(decisions=[dec]))
    es = _run_until(es, lambda e: _site(e).neutralized_ms is not None, limit=9000)
    states = {s.id: s for s in es.states}
    home = next(v for v in sc.vehicles if v.id == "usv").home
    assert states["a2"].role_id == "strike"
    for idle in ("a1", "a3"):
        assert states[idle].role_id == "standby", idle
        assert dist_m(states[idle].pos, home) < 1.0, idle  # still at the usv spot
    assert not es.blocks  # no safety rule (zone, battery, provenance) stopped the strike
```

- [ ] **Step 2: 실행하고 결과를 읽는다**

Run: `uv run pytest tests/test_strike_scenario.py -n 0 -q`
Expected: PASS (Task 1이 구현을 이미 만들었으므로 이 테스트는 **처음부터 통과할 수 있다**. 이것은 통합 동작 확인이다). 통과하면 **망가뜨려 보는 확인**을 한다: `modules/gateway/actions/refresh_strike_cards.py`의 `_strikers`가 돌려주는 목록에서 `a2`를 일시적으로 뺀 뒤(예: `armed = [s for s in armed if s.id != "a2"]`) 이 파일 테스트가 실패하는 것을 보고, `git checkout modules/gateway/actions/refresh_strike_cards.py`로 되돌린다.
실패하면 원인을 읽는다. `states["a2"].role_id`가 `strike`가 아니면 `apply_decision`의 이동 결과를, `blocks`가 비어 있지 않으면 사유(귀환 배터리 규칙, 구역)를 읽고, 규칙은 풀지 말고 보고하고 멈춘다.

- [ ] **Step 3: Commit**

```bash
git add tests
git commit -m "Part2-carrier: the card offers a1, a2, a3 and strike all but never the usv, and only the chosen attack drone leaves the usv spot"
```

---

### Task 3: 전체 확인과 기록

**Files:**
- Modify: `demo/BUILT_HERE.md`

- [ ] **Step 1: 전체 테스트와 린트**

Run: `uv run pytest -q`
Expected: 실패 0. `uv run ruff check . && uv run ruff format --check modules tests scripts`는 이번 변경 파일에서 새 경고가 없어야 한다(`scripts/sync_docs.py`, `tests/test_sync_docs.py`의 기존 포맷 경고는 이번 변경과 무관하다).

- [ ] **Step 2: 다른 작전이 그대로인지 본다**

Run: `git diff origin/main --stat -- demo/scenarios`
Expected: `baengnyeong_strike.json`만 바뀌어 있고 `baengnyeong_night.json`, `baengnyeong_24h.json`은 없다.

- [ ] **Step 3: BUILT_HERE에 한 줄**

`demo/BUILT_HERE.md` 끝에 더한다.

```
| 10/10 23:00 | demo·scripts·tests | 공격 작전 모선 편대(1번): 정지한 수상정(sea_vehicle, 타격 불가) 한 척에서 정찰 드론 r1~r3와 공격 드론 a1~a3가 같은 자리에서 출발·귀환, 식별된 거점 카드에 a1·a2·a3·전원 타격 승인만 나옴(2~4번: 탐색 경로 선택, 공격 드론 선택 다듬기, 비행 중 재지정은 후속) | 최동호 |
```

- [ ] **Step 4: 눈으로 확인한다 (선택, 사람이 보고 싶을 때)**

`modules/cop-ui`를 한 번 빌드한 worktree에서 `scripts/demo.sh demo/scenarios/baengnyeong_strike.json`. 서버 로그는 `/tmp`이 아니라 홈 디스크로 보낸다(`> ~/scratch/server.log 2>&1`). 확인할 것: 지도에서 기체 6대가 수상정 자리에 겹쳐 있고(spec 7절의 알려진 한계), 약 몇 분 뒤 site_a 카드에 `a1·a2·a3` 타격 승인이 뜬다.

- [ ] **Step 5: Commit**

```bash
git add demo/BUILT_HERE.md
git commit -m "Part2-carrier: BUILT_HERE line for the carrier fleet"
```

---

## Self-Review

1. **Spec coverage**: 4절 기체 구성 표(Task 1 Step 1·3, Global Constraints), 초기 임무(Task 1 Step 1·3), 타격 선택지(Task 1 Step 5, Task 2), 6절 바뀌는 파일(Task 1 Step 5가 테스트 3개, Task 3이 BUILT_HERE; `tests/test_demo_routes.py`와 `test_app.py`는 기체 id를 쓰지 않아 변경 없음을 grep으로 확인함), 7절 위험 중 `home`이 바다인 공중 기체(Task 1 `check_operation`·Task 2 `es.blocks`), 도달 시간(Task 1 Step 6의 `limit` 안내), 겹침(Task 3 Step 4에서 눈으로). 2~4번은 spec대로 범위 밖이다.
2. **Placeholder scan**: TODO/TBD 없음. `Part2-carrier`는 작업 번호가 정해지기 전의 커밋 접두어다.
3. **Type consistency**: 기체 id `usv, r1~r3, a1~a3, ugv`, 선택지 id `strike_a1~a3`/`strike_all`, 함수 `fleet(night_vehicles)`가 모든 Task에서 같다.
4. **Review Focus**: 다섯 줄 모두 테스트가 있다(바다 `home`: Task 1·2, 수상정 선택지 없음과 고른 드론만 이동: Task 2, 야간·24h 불변: Task 3 Step 2와 `tests/test_demo_routes.py`, 옛 id 없음: Task 1 Step 1).
5. **확인하지 못한 것**: 이 계획의 코드는 실행해 보지 않았다. 확인한 것: `Operation.vehicle_ids`는 계약(`contracts/models/world.py:93`)에 있다. `tests/test_demo_routes.py`는 기체 id를 쓰지 않고, `modules/gateway/tests/test_app.py`는 시나리오 id만 본다. 확인하지 못한 것: 수상정 자리에서 출발했을 때 `check_operation`·귀환 배터리 규칙이 통과하는지는 Task 1 Step 6과 Task 2가 확인한다.
