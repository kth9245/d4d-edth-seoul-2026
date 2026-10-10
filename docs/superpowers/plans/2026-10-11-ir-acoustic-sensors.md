# T1 공격 작전 적외선·소리 센서 Implementation Plan (가상 센서, 공격 작전에만 켬)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 정찰 드론에 가상 적외선 센서를, 지상 로봇에 가상 음향 센서를 달고, 공격 작전의 site_b에 열 신호, site_c에 소음을 줘서 위험도 +0.10·식별 신뢰도 +0.10을 얻게 한다. site_b는 정찰 한 대로 식별되고, site_c는 드론의 스캔과 운용자가 보낸 지상 로봇의 소음이 같이 있어야 식별된다. **야간·24시간 작전은 한 프레임도 달라지지 않아야 한다.**

**Architecture:** RF(결정 0039·0040)와 같은 구조다. 적 사양에 정답 플래그(`heat`, `noise`), 기체 사양에 수신 범위(`ir_range_m`, `acoustic_range_m`), 표적에 정답 복사본과 감지 결과(`ir_detected`, `sound_detected`)를 둔다. sensing의 순수 함수 `score_target`·`identify_target`이 키워드 전용 인자(기본값 꺼짐)로 새 단서를 더하고, gateway 액션이 연결한다. 새 필드와 인자는 모두 기본값이 "없음"이라 다른 작전의 계산은 그대로다. 시작 전에 야간·24시간의 프레임 해시 기준선을 잡아 두고, 마지막까지 같은지 비교한다.

**Tech Stack:** Python(pydantic 계약, pytest), TypeScript(cop-ui, vitest), 시나리오 JSON, `scripts/gen_contracts.py`.

**Spec:** `docs/superpowers/specs/2026-10-11-ir-acoustic-sensors-design.md`(4절 설계, 5절 변경 대장, 6절 다른 작전을 지키는 방법, 7절 추천값과 다른 곳). 관련: `docs/superpowers/specs/2026-10-10-strike-op-carrier-fleet-design.md`.

## Global Constraints

- **야간(`baengnyeong_night`)·24시간(`baengnyeong_24h`) 시나리오 JSON은 한 글자도 바꾸지 않는다.** `git diff --stat -- demo/scenarios`에 `baengnyeong_strike.json`만 나와야 한다.
- 새 필드와 인자의 기본값은 모두 "없음/꺼짐"(`False`, `0`, 빈 목록). 기존 호출·기존 테스트 코드는 한 줄도 고치지 않고 통과해야 한다. 고쳐야 하는 기존 테스트가 생기면 **멈추고** 이유를 원장에 적는다(예외: 공격 작전의 무음 거점 식별을 가정한 테스트 둘, Task 8에 명시).
- 센서 값은 모두 가상·임의다(정책 2). `ir_range_m = 800`, `acoustic_range_m = 500`, 점수 +0.10(0.01 단위 정수 10), 식별 증거 +10.
- 새 이유 코드: `ir_signature`, `sound`. 이유 코드 순서: `kind_*` → 기준점 → `rf_emission` → `ir_signature` → `sound` → `speed`. 식별 이유 순서: `rf_emission` → `ir_signature` → `sound` → `scan` → `multi_observer` → `sustained`.
- 공격 작전 시나리오 데이터: `r1`·`r2`·`r3`에 `ir_range_m: 800.0`, `ugv`에 `acoustic_range_m: 500.0`과 `home = {"lat": 37.95923, "lon": 124.64615, "alt_m": 0.0}`(site_c 정남쪽 1500 m, 육지 위), site_b `heat: true`, site_c `noise: true`. 나머지는 기본값.
- JSON은 생성 결과가 정본이다(결정 0035): `scripts/make_strike_scenario.py`를 고치고 `uv run python scripts/make_strike_scenario.py`로 다시 만든다.
- 액션 파일은 80줄 이하(`tools/check_specs.py`). 새 액션 파일은 만들지 않는다(기존 액션만 고친다).
- 모든 코드 변경은 실패하는 테스트를 먼저 쓴다(결정 0014). 커밋 메시지 끝에 `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- 작업은 `/home/dongho/d4d-strike-s2`(브랜치 `strike-carrier`). `scripts/ship.sh`와 push는 사람이 시키기 전에 하지 않는다.
- 계약 변경은 `/decide` 결정 하나로 기록한다(`uv run python scripts/decide.py new "<제목>"`, 초안만 쓰고 `accept`는 하지 않는다). 코드 주석의 결정 번호는 도구가 준 번호(`NNNN`)를 쓰고, **push 직전에** 번호가 main과 겹치지 않는지 다시 확인한다(번호가 세 번 겹친 적이 있다).
- 테스트 로그가 `/tmp`을 채우지 않게, 전체 테스트 전에 `: > logs/gateway.log; : > logs/smoke.log`로 로그를 비운다.
- 용어는 **Role**(결정 0052).

## Review Focus

- **야간·24시간이 그대로다**: Task 1의 기준선 해시가 마지막 Task까지 같다. 새 키를 뺀 프레임이 같고, 새 키는 전부 꺼짐/0이다(Task 1, 9).
- **범위 경계**: 적외선 800 m·음향 500 m 경계에서 정확히 같은 거리는 잡히고(`<=`), 1 m 더 멀면 안 잡힌다(Task 4).
- **센서 범위 0은 못 듣는다, 살아 있지 않은 기체는 수신기가 아니다**: `ir_range_m=0`, `returning`·`lost` 기체는 단서를 만들지 못한다(Task 4, 6).
- **단서만으로는 절대 식별되지 않는다**: 스캔이 없으면 RF 25 + 열 10 + 소음 10 = 45로 70에 못 닿고 상태는 `rf_only`다(Task 5).
- **합계 상한 1.00과 무력화된 표적**: 모든 단서가 겹쳐도 100에서 자르고, 무력화된 표적의 점수·플래그는 그대로 둔다(Task 4, 6).

---

### Task 1: 야간·24시간 기준선 (코드를 바꾸기 전에)

**Files:**
- Create: `tests/test_other_operations_unchanged.py`

**Interfaces:**
- Produces: `digest(path: str, ticks: int) -> str`(새 키를 뺀 프레임의 해시), `BASELINE: dict[str, tuple[int, str]]`. 이후 모든 Task가 이 테스트를 그대로 통과해야 한다.

- [ ] **Step 1: 비교 테스트를 쓴다 (해시 자리는 비워 둔다)**

```python
"""Decision NNNN guard: night and 24h run exactly as before the infrared/acoustic sensors.

Every frame of a fixed run is hashed with the keys the sensors add taken out, so the hash was recorded on the code
before the sensors existed. The new keys themselves must stay off (False / 0) in these operations.
"""

import hashlib
import json

import pytest

from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

NEW_KEYS = {"heat", "noise", "ir_detected", "sound_detected", "ir_range_m", "acoustic_range_m"}
BASELINE = {  # path -> (ticks, sha256 recorded before the sensors)
    "demo/scenarios/baengnyeong_night.json": (4000, "RECORD_ME"),
    "demo/scenarios/baengnyeong_24h.json": (4000, "RECORD_ME"),
}


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in NEW_KEYS}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def run(path: str, ticks: int):
    es, h, new_keys_on = init_engine(load_scenario_json(path)), hashlib.sha256(), []
    for _ in range(ticks):
        es, frame = tick(es, TickInputs())
        dump = frame.model_dump(mode="json")
        h.update(json.dumps(strip(dump), sort_keys=True, ensure_ascii=False).encode("utf-8"))
        new_keys_on += [t["id"] for t in dump["targets"]
                        if t.get("heat") or t.get("noise") or t.get("ir_detected") or t.get("sound_detected")]  # fmt: skip
    return h.hexdigest(), new_keys_on


@pytest.mark.parametrize("path", list(BASELINE))
def test_every_frame_is_what_it_was_before_the_sensors(path):
    ticks, want = BASELINE[path]
    got, _ = run(path, ticks)
    assert got == want


@pytest.mark.parametrize("path", list(BASELINE))
def test_the_sensor_fields_stay_off_and_no_vehicle_has_a_sensor_range(path):
    _, on = run(path, 600)
    assert on == []
    sc = load_scenario_json(path)
    assert all(
        getattr(v, "ir_range_m", 0) == 0 and getattr(v, "acoustic_range_m", 0) == 0
        for v in sc.vehicles
    )
```

- [ ] **Step 2: 지금(변경 전) 코드에서 해시를 기록한다**

Run: `uv run python - <<'E'` 로 `from tests.test_other_operations_unchanged import run, BASELINE; for p,(n,_) in BASELINE.items(): print(p, n, run(p, n)[0])` 를 실행한다(스크립트는 `E`로 닫는다).
Expected: 경로마다 64자리 해시 하나. 두 해시를 `RECORD_ME` 자리에 붙여 넣는다. **같은 명령을 두 번 돌려 해시가 같은지 확인한다**(같지 않으면 비결정 요소가 있다는 뜻이니 멈추고 보고한다).

- [ ] **Step 3: 통과를 확인한다**

Run: `uv run pytest tests/test_other_operations_unchanged.py -n 0 -q`
Expected: PASS 4개. (기준선 테스트는 처음부터 통과한다. 이 테스트가 정말 실패할 수 있는지는 다음 단계가 확인한다.)

- [ ] **Step 4: 기준선이 실제로 변화를 잡는지 본다**

야간 시나리오의 점수를 일부러 바꾼다: `modules/sensing/actions/score_target.py`의 `RF = 30`(상수 줄의 `RF`)을 `31`로 일시적으로 바꾸고 `uv run pytest tests/test_other_operations_unchanged.py -n 0 -q`를 돌린다. 야간·24시간 해시 테스트가 FAIL해야 한다. 확인 뒤 `git checkout modules/sensing/actions/score_target.py`로 되돌리고 다시 PASS를 확인한다.

- [ ] **Step 5: Commit**

```bash
git add tests/test_other_operations_unchanged.py
git commit -m "Part2-sensors: guard that night and 24h frames stay byte-identical (hash recorded before the infrared and acoustic sensors)"
```

---

### Task 2: 계약 필드와 결정 초안

**Files:**
- Create: `decisions/log/NNNN-…md` (`decide.py new`가 만든다)
- Modify: `contracts/models/world.py`(`VehicleSpec`, `EnemySpec`), `contracts/models/events.py`(`Target`)
- Regenerate: `contracts/schema/`, `contracts/examples/`, `modules/cop-ui/src/contracts.gen.ts`
- Test: `tests/test_contracts_threat.py`

**Interfaces:**
- Produces: `EnemySpec.heat: bool = False`, `EnemySpec.noise: bool = False`; `Target.heat: bool = False`, `Target.noise: bool = False`, `Target.ir_detected: bool = False`, `Target.sound_detected: bool = False`; `VehicleSpec.ir_range_m: float = 0`, `VehicleSpec.acoustic_range_m: float = 0`.

- [ ] **Step 1: 결정 초안을 쓴다**

`uv run python scripts/decide.py new "가상 적외선·음향 센서: 적 거점의 열 신호·소음과 기체의 수신 범위, 공격 작전에만 켬"`. 본문(결정/이유/버린 대안/영향)은 설계 문서 3·4·6절 내용으로 채운다. 버린 대안: 모든 작전에 켜기(검증된 점수·시연 타이밍이 달라짐). 영향: contracts, sim, sensing, gateway, cop-ui(리드·황승주 알림은 최종 보고에). `accept`는 하지 않는다. 커밋한다.

- [ ] **Step 2: 실패하는 테스트를 쓴다**

`tests/test_contracts_threat.py` 끝에 더한다.

```python
def test_the_sensor_fields_default_to_off():  # decision NNNN
    from contracts.models import EnemySpec, GeoPoint, Target, VehicleSpec

    home = GeoPoint(lat=37.9, lon=124.7)
    v = VehicleSpec(id="r1", name="r1", domain="air", speed_mps=15, endurance_min=100,
                    sensor_range_m=800, home=home)  # fmt: skip
    assert (v.ir_range_m, v.acoustic_range_m) == (0, 0)
    e = EnemySpec(id="s", kind="unknown", speed_mps=0, appear_offset_ms=1000, pos=home, role_id="r")
    assert (e.heat, e.noise) == (False, False)
    t = Target(id="s", kind="unknown", pos=home, vel_east_mps=0, vel_north_mps=0,
               first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    assert (t.heat, t.noise, t.ir_detected, t.sound_detected) == (False, False, False, False)
```

- [ ] **Step 3: 실패를 확인한다**

Run: `uv run pytest tests/test_contracts_threat.py -n 0 -q`
Expected: FAIL (`AttributeError: ... 'ir_range_m'`).

- [ ] **Step 4: 필드를 더한다**

`VehicleSpec`의 `rf_range_m` 줄 아래:
```python
    ir_range_m: float = 0  # infrared receive range (decision NNNN); 0 = cannot
    acoustic_range_m: float = 0  # sound receive range (decision NNNN); 0 = cannot
```
`EnemySpec`의 `emit_start_offset_ms` 항목 아래:
```python
    heat: bool = False  # gives off a heat signature (decision NNNN)
    noise: bool = False  # gives off noise (decision NNNN)
```
`Target`의 `rf_detected` 줄 아래:
```python
    heat: bool = False  # sim: it gives off heat (the truth, not shown on screen; decision NNNN)
    noise: bool = False  # sim: it gives off noise (the truth, not shown on screen)
    ir_detected: bool = False  # sensing: heat and a live vehicle's infrared range covers it
    sound_detected: bool = False  # sensing: noise and a live vehicle's acoustic range covers it
```

- [ ] **Step 5: 생성 파일을 다시 만들고 통과를 확인한다**

Run: `uv run python scripts/gen_contracts.py && uv run python scripts/gen_examples.py`
Run: `uv run pytest tests contracts -q -p no:cacheprovider`
Expected: PASS. 생성 파일 diff는 새 필드 추가뿐이어야 한다(`git diff --stat contracts modules/cop-ui/src/contracts.gen.ts`).
Run: `uv run pytest tests/test_other_operations_unchanged.py -n 0 -q` → PASS(새 키를 빼고 비교하므로 해시가 같다).

- [ ] **Step 6: cop-ui 타입이 깨지지 않는지 본다**

Run: `cd modules/cop-ui && npx tsc -b && npx vitest run`
Expected: tsc 오류 0, vitest PASS. 실패하면 멈추고 출력을 보고한다.

- [ ] **Step 7: Commit**

```bash
git add contracts decisions modules/cop-ui/src/contracts.gen.ts tests
git commit -m "Part2-sensors: heat, noise, ir_detected, sound_detected on Target; heat, noise on EnemySpec; ir_range_m, acoustic_range_m on VehicleSpec, all off by default (decision NNNN draft)"
```

---

### Task 3: sim — 적이 나타날 때 신호를 표적에 복사

**Files:**
- Modify: `modules/sim/actions/spawn_enemies.py`
- Test: `modules/sim/tests/test_spawn_enemies.py`

**Interfaces:**
- Consumes: `EnemySpec.heat/noise`(Task 2). Produces: `spawn_enemies`가 만든 `Target`의 `heat`·`noise`가 `EnemySpec`과 같다.

- [ ] **Step 1: 실패하는 테스트를 쓴다** (`modules/sim/tests/test_spawn_enemies.py`의 기존 시나리오 만들기 방식을 읽고 같은 방식으로)

```python
def test_a_spawned_enemy_carries_its_heat_and_noise():  # decision NNNN
    sc = scenario_with(
        enemies=[enemy("site_b", heat=True), enemy("site_c", noise=True), enemy("site_a")]
    )
    out = spawn_enemies(sc, [], appear_tick_ms(sc), sc.tick_ms)
    flags = {t.id: (t.heat, t.noise) for t in out}
    assert flags == {"site_b": (True, False), "site_c": (False, True), "site_a": (False, False)}
```
(`scenario_with`·`enemy`·`appear_tick_ms`는 그 파일에 이미 있는 도우미를 쓰거나, 없으면 같은 파일 위쪽에 같은 모양으로 만든다. 도우미 이름이 다르면 맞춘다.)

- [ ] **Step 2: 실패를 확인한다**

Run: `uv run pytest modules/sim/tests/test_spawn_enemies.py -n 0 -q`
Expected: FAIL (복사하지 않아 모두 `(False, False)`).

- [ ] **Step 3: 구현한다**

`spawn_enemies.py`의 `Target(...)` 호출에 `heat=e.heat, noise=e.noise,`를 더한다(`role_id=…` 앞).

- [ ] **Step 4: 통과를 확인한다**

Run: `uv run pytest modules/sim -n 0 -q -p no:cacheprovider && uv run pytest tests/test_other_operations_unchanged.py -n 0 -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/sim
git commit -m "Part2-sensors: spawn_enemies gives the target its heat and noise (decision NNNN)"
```

---

### Task 4: sensing `score_target` — 열·소음 단서가 위험도에 +0.10

**Files:**
- Modify: `modules/sensing/actions/score_target.py`
- Test: `modules/sensing/tests/test_score_target.py`

**Interfaces:**
- Produces:
```python
class ThreatScore(NamedTuple):
    score: int; reasons: list[str]; rf_detected: bool; accum: int
    ir_detected: bool = False; sound_detected: bool = False

def score_target(kind, pos, speed_mps, observed, emitting, receivers, watch_points, accum, tick_ms,
                 *, heat: bool = False, noise: bool = False,
                 ir_receivers: Sequence = (), sound_receivers: Sequence = ()) -> ThreatScore
```
`ir_receivers`·`sound_receivers`는 `(GeoPoint, range_m)` 목록(`receivers`와 같은 모양). 기존 위치 인자는 그대로.

- [ ] **Step 1: 실패하는 테스트를 쓴다** (`test_score_target.py` 끝, 기존 `score()` 도우미 뒤)

```python
def sig(**kw):  # a silent unknown site with the new signals; no RF
    base = dict(
        kind="unknown", pos=INSIDE, speed=0.0, observed=True, emitting=False, rx=(), accum=0
    )
    return score_target(base["kind"], base["pos"], base["speed"], base["observed"], base["emitting"],
                        [], WATCH, base["accum"], 200, **kw)  # fmt: skip


def test_heat_in_infrared_range_adds_ten_with_its_reason_in_order():  # decision NNNN
    plain = sig()
    r = sig(heat=True, ir_receivers=[(INSIDE, 800.0)])
    assert (r.score, r.ir_detected) == (plain.score + 10, True)
    assert r.reasons == [*plain.reasons, "ir_signature"]


def test_noise_in_acoustic_range_adds_ten_and_comes_after_infrared_before_speed():
    r = sig(
        heat=True, noise=True, ir_receivers=[(INSIDE, 800.0)], sound_receivers=[(INSIDE, 500.0)]
    )
    assert r.reasons[-2:] == ["ir_signature", "sound"] and (r.ir_detected, r.sound_detected) == (
        True,
        True,
    )
    moving = score_target("unknown", INSIDE, 1.0, True, True, [(INSIDE, 2000.0)], WATCH, 0, 200,
                          heat=True, noise=True, ir_receivers=[(INSIDE, 800.0)], sound_receivers=[(INSIDE, 500.0)])  # fmt: skip
    assert (
        moving.reasons.index("rf_emission")
        < moving.reasons.index("ir_signature")
        < moving.reasons.index("sound")
        < moving.reasons.index("speed")
    )


def test_the_range_edge_counts_and_one_metre_more_does_not():
    from shared.geo import dist_m

    far = GeoPoint(lat=INSIDE.lat + 0.004, lon=INSIDE.lon)
    d = dist_m(INSIDE, far)
    assert sig(heat=True, ir_receivers=[(far, d)]).ir_detected  # exactly at the edge
    assert not sig(heat=True, ir_receivers=[(far, d - 1)]).ir_detected
    assert sig(noise=True, sound_receivers=[(far, d)]).sound_detected
    assert not sig(noise=True, sound_receivers=[(far, d - 1)]).sound_detected


def test_no_signal_no_receiver_or_range_zero_gives_nothing():
    base = sig()
    assert sig(heat=False, ir_receivers=[(INSIDE, 800.0)]) == base
    assert sig(heat=True) == base  # nobody listens
    assert sig(heat=True, ir_receivers=[(INSIDE, 0.0)]) == base  # range 0 = cannot
    assert sig(noise=True, sound_receivers=[(INSIDE, 0.0)]) == base


def test_every_signal_together_is_still_capped_at_100():
    r = score_target("fast_boat", INSIDE, 6.3, True, True, [(INSIDE, 2000.0)], WATCH, 0, 200,
                     heat=True, noise=True, ir_receivers=[(INSIDE, 800.0)], sound_receivers=[(INSIDE, 500.0)])  # fmt: skip
    assert r.score == 100


def test_calling_it_the_old_way_still_works_and_reports_no_new_signals():
    r = score()
    assert (r.ir_detected, r.sound_detected) == (False, False)
```

- [ ] **Step 2: 실패를 확인한다**

Run: `uv run pytest modules/sensing/tests/test_score_target.py -n 0 -q`
Expected: FAIL (`TypeError: ... unexpected keyword argument 'heat'`). 기존 6개 테스트는 계속 통과해야 한다.

- [ ] **Step 3: 구현한다**

`score_target.py`: 상수 줄 아래에 `IR, SOUND = 10, 10`. `ThreatScore`에 기본값 있는 두 필드를 더한다. 범위 판정을 도우미 하나로 묶는다.

```python
def _heard(on: bool, receivers, pos: GeoPoint) -> bool:
    return on and any(r > 0 and dist_m(p, pos) <= r for p, r in receivers)
```
`rf = emitting and any(...)` 줄을 `rf = _heard(emitting, receivers, pos)`로 바꾼다(동작 동일). `if rf:` 블록 바로 뒤, 속도 계산 앞에:
```python
    ir = _heard(heat, ir_receivers, pos)
    if ir:
        score, reasons = score + IR, reasons + ["ir_signature"]
    sound = _heard(noise, sound_receivers, pos)
    if sound:
        score, reasons = score + SOUND, reasons + ["sound"]
```
함수 서명 끝에 `*, heat: bool = False, noise: bool = False, ir_receivers=(), sound_receivers=()`를 더하고, 마지막 `return ThreatScore(score, reasons, rf, grown)`을 `ThreatScore(score, reasons, rf, grown, ir, sound)`로 바꾼다.

- [ ] **Step 4: 통과를 확인한다**

Run: `uv run pytest modules/sensing -n 0 -q -p no:cacheprovider && uv run pytest tests/test_other_operations_unchanged.py -n 0 -q`
Expected: PASS (기존 + 새 6개, 기준선 포함).

- [ ] **Step 5: Commit**

```bash
git add modules/sensing
git commit -m "Part2-sensors: score_target adds ir_signature and sound (+0.10 each) from keyword-only inputs that default to off (decision NNNN)"
```

---

### Task 5: sensing `identify_target` — 열·소음 단서가 식별 증거 +10

**Files:**
- Modify: `modules/sensing/actions/identify_target.py`
- Test: `modules/sensing/tests/test_identify_target.py`

**Interfaces:**
- Produces: `identify_target(rf_detected, seen_count, age_ms, observed_ms, tick_ms, *, ir_detected: bool = False, sound_detected: bool = False) -> Ident`.

- [ ] **Step 1: 실패하는 테스트를 쓴다** (`test_identify_target.py` 끝)

```python
def test_a_heat_clue_with_a_fresh_scan_reaches_the_threshold_alone():  # decision NNNN
    r = identify_target(
        False, 1, 0, 19800, TICK, ir_detected=True
    )  # scan 40 + heat 10 + sustained 20
    assert (r.state, r.confidence, r.reasons) == (
        "identified",
        70,
        ["ir_signature", "scan", "sustained"],
    )


def test_a_sound_clue_does_the_same_and_both_clues_stack():
    r = identify_target(False, 1, 0, 19800, TICK, sound_detected=True)
    assert (r.state, r.confidence, r.reasons[0]) == ("identified", 70, "sound")
    both = identify_target(
        False, 1, 0, 0, TICK, ir_detected=True, sound_detected=True
    )  # scan 40 + 10 + 10
    assert both.confidence == 60 and both.reasons == ["ir_signature", "sound", "scan"]


def test_clues_alone_never_identify_and_the_state_is_rf_only():
    r = identify_target(
        True, 0, None, 0, TICK, ir_detected=True, sound_detected=True
    )  # 25 + 10 + 10, no scan
    assert (r.state, r.confidence) == ("rf_only", 45)
    only_sound = identify_target(False, 0, None, 0, TICK, sound_detected=True)
    assert (only_sound.state, only_sound.confidence, only_sound.reasons) == (
        "rf_only",
        10,
        ["sound"],
    )


def test_the_old_calls_are_unchanged_and_the_total_is_capped():
    assert identify_target(True, 2, 0, 19800, TICK).confidence == 100  # 25 + 40 + 15 + 20
    assert (
        identify_target(True, 2, 0, 19800, TICK, ir_detected=True, sound_detected=True).confidence
        == 100
    )
```

- [ ] **Step 2: 실패를 확인한다**

Run: `uv run pytest modules/sensing/tests/test_identify_target.py -n 0 -q`
Expected: FAIL (`unexpected keyword argument 'ir_detected'`). 기존 10개 테스트는 통과.

- [ ] **Step 3: 구현한다**

`identify_target.py`: 상수에 `IR_PTS, SOUND_PTS = 10, 10`. 서명 끝에 `*, ir_detected: bool = False, sound_detected: bool = False`. 본문:
```python
    ir = IR_PTS if ir_detected else 0
    sound = SOUND_PTS if sound_detected else 0
    confidence = min(100, rf + ir + sound + scan + multi + sustained)
    parts = [("rf_emission", rf), ("ir_signature", ir), ("sound", sound), ("scan", scan),
             ("multi_observer", multi), ("sustained", sustained)]  # fmt: skip
    ...
    if scan == 0:
        state = "rf_only" if (rf or ir or sound) else "undetected"
```
(`if scan == 0` 분기만 `rf`를 `rf or ir or sound`로 넓힌다.) 파일은 80줄 이하를 유지한다.

- [ ] **Step 4: 통과를 확인한다**

Run: `uv run pytest modules/sensing -n 0 -q -p no:cacheprovider && uv run pytest tests/test_other_operations_unchanged.py -n 0 -q && wc -l modules/sensing/actions/identify_target.py`
Expected: PASS, 80줄 이하.

- [ ] **Step 5: Commit**

```bash
git add modules/sensing
git commit -m "Part2-sensors: identify_target counts a heat or sound clue as +10 evidence (a clue alone never identifies; decision NNNN)"
```

---

### Task 6: gateway — 수신기 목록을 만들어 연결

**Files:**
- Modify: `modules/gateway/actions/score_targets.py`, `modules/gateway/actions/identify_targets.py`
- Test: `modules/gateway/tests/test_score_targets.py`, `modules/gateway/tests/test_identify_targets.py`

**Interfaces:**
- Consumes: Task 2 필드, Task 4·5의 키워드 인자. Produces: `score_targets`가 `Target.ir_detected`·`sound_detected`를 쓰고, `identify_targets`가 둘을 `identify_target`에 넘긴다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`test_score_targets.py` 끝(그 파일의 `STATES`, `SPECS`, `WATCH`, `run`, `fast` 도우미를 읽고 같은 방식으로; 기체 사양 도우미에 `ir_range_m`·`acoustic_range_m`을 줄 수 있어야 하니 `SPECS`를 복제해 값을 바꾼다):

```python
def test_infrared_and_sound_are_heard_only_by_live_vehicles_in_range():  # decision NNNN
    spec = SPECS["d2"].model_copy(update={"ir_range_m": 800.0, "acoustic_range_m": 500.0})
    specs = {"d2": spec}
    t = fast(kind="unknown", seen_by=[], emitting=False, heat=True, noise=True)
    out = score_targets(STATES, specs, [t], WATCH, 200)[0]
    assert (out.ir_detected, out.sound_detected) == (True, True)
    assert "ir_signature" in out.threat_reasons and "sound" in out.threat_reasons
    gone = [STATES[0].model_copy(update={"status": "returning"})]
    out2 = score_targets(gone, specs, [t], WATCH, 200)[0]
    assert (out2.ir_detected, out2.sound_detected) == (
        False,
        False,
    )  # a returning vehicle is not a receiver
    none = score_targets(STATES, SPECS, [t], WATCH, 200)[0]  # ranges 0 in SPECS
    assert (none.ir_detected, none.sound_detected) == (False, False)


def test_a_neutralized_target_keeps_its_old_scores():
    spec = SPECS["d2"].model_copy(update={"ir_range_m": 800.0})
    t = fast(heat=True, neutralized_ms=5, threat=33)
    out = score_targets(STATES, {"d2": spec}, [t], WATCH, 200)[0]
    assert (out.threat, out.ir_detected) == (33, False)
```
`test_identify_targets.py` 끝:
```python
def test_the_detected_clues_reach_the_identification():  # decision NNNN
    t = site(seen_by=["d1"], first_seen_ms=9_000, last_seen_ms=10_000, rf_detected=False,
             ir_detected=True, sound_detected=True)  # fmt: skip
    r = identify_targets([t], 10_000, 200)[0]
    assert (
        r.ident_reasons[:2] == ["ir_signature", "sound"] and r.ident_confidence == 60
    )  # scan 40 + 10 + 10
```

- [ ] **Step 2: 실패를 확인한다**

Run: `uv run pytest modules/gateway/tests/test_score_targets.py modules/gateway/tests/test_identify_targets.py -n 0 -q`
Expected: FAIL.

- [ ] **Step 3: 구현한다**

`score_targets.py`: `receivers` 만드는 줄 아래에
```python
    ir = [(s.pos, specs[s.id].ir_range_m) for s in states if s.status in LIVE]
    sound = [(s.pos, specs[s.id].acoustic_range_m) for s in states if s.status in LIVE]
```
`score_target(...)` 호출 끝에 `heat=tg.heat, noise=tg.noise, ir_receivers=ir, sound_receivers=sound`를 더하고, `model_copy(update={...})`에 `"ir_detected": r.ir_detected, "sound_detected": r.sound_detected`를 더한다. `identify_targets.py`: `identify_target(...)` 호출 끝에 `ir_detected=tg.ir_detected, sound_detected=tg.sound_detected`.

- [ ] **Step 3: 통과를 확인한다**

Run: `uv run pytest modules/gateway -n 0 -q -p no:cacheprovider && uv run pytest tests/test_other_operations_unchanged.py -n 0 -q`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add modules/gateway
git commit -m "Part2-sensors: score_targets builds the infrared and acoustic receivers from live vehicles and identify_targets passes the clues on (decision NNNN)"
```

---

### Task 7: cop-ui — 화면이 열·소음 단서를 안다

**Files:**
- Create: `modules/cop-ui/src/features/board/clueTags.ts`, `modules/cop-ui/src/features/board/clueTags.test.ts`
- Modify: `modules/cop-ui/src/features/board/trackState.ts`, `QueueCard.tsx`, `RosterPanel.tsx`, `modules/cop-ui/src/features/map/frameMarkers.ts`, `modules/cop-ui/src/features/cards/frameCards.ts`
- Test: `trackState.test.ts`, `frameMarkers.test.ts`, `modules/cop-ui/src/features/cards/frameCards.test.ts`(없으면 그 폴더의 기존 테스트 파일에)

**Interfaces:**
- Produces: `clueTags(t: Pick<Target, "rf_detected" | "ir_detected" | "sound_detected">): string[]` — 순서 `RF`, `열`, `소음`.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`clueTags.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { clueTags } from "./clueTags";

describe("clueTags", () => {
  it("names each clue our sensors picked up, RF first (decision NNNN)", () => {
    expect(clueTags({})).toEqual([]);
    expect(clueTags({ rf_detected: true })).toEqual(["RF"]);
    expect(clueTags({ sound_detected: true })).toEqual(["소음"]);
    expect(clueTags({ rf_detected: true, ir_detected: true, sound_detected: true })).toEqual(["RF", "열", "소음"]);
  });
});
```
`trackState.test.ts`에: `expect(trackState(mkTarget({ id: "b", sound_detected: true }), T0, LANDING).k).toBe("rf");`와 `ir_detected: true`도 `"rf"`, 그리고 아무 단서 없는 표적은 지금처럼 `"never"`. `frameMarkers.test.ts`에: `at({ sound_detected: true })`의 `rf`가 `true`이고 `label`이 `"boat1 · 소음"`, `at({ rf_detected: true, ir_detected: true }).label`이 `"boat1 · RF·열"`. 기존 `"boat1 · RF"` 단언은 그대로 통과해야 한다. `frameCards` 테스트에: 이유 코드 `["kind_unknown", "near_watch_radius", "ir_signature", "sound"]`인 표적의 카드 설명 `parts`에 `"열 신호 감지 +0.10"`, `"소음 감지 +0.10"`이 있다.

- [ ] **Step 2: 실패를 확인한다**

Run: `cd modules/cop-ui && npx vitest run src/features`
Expected: FAIL (`clueTags` 없음, `"never"`가 나옴 등).

- [ ] **Step 3: 구현한다**

`clueTags.ts`:
```ts
import type { Target } from "../../contracts.gen";

// The clues our sensors picked up on a target: radio, heat or sound (decisions 0039, NNNN). RF first.
export function clueTags(t: Pick<Target, "rf_detected" | "ir_detected" | "sound_detected">): string[] {
  return [t.rf_detected && "RF", t.ir_detected && "열", t.sound_detected && "소음"].filter((x): x is string => !!x);
}
```
`trackState.ts`: `if (t.rf_detected) return …`를 `if (clueTags(t).length > 0) return { k: "rf", pos: t.pos };`로(import 추가). `frameMarkers.ts`: `const tags = neutralized ? [] : clueTags(t); const rf = tags.length > 0;`, 라벨 끝 `${rf ? " · RF" : ""}`를 `${rf ? ` · ${tags.join("·")}` : ""}`로. `RosterPanel.tsx`: `{t.rf_detected && !quiet && <span className="rf-tag">RF</span>}`를 `{!quiet && clueTags(t).map((tag) => <span key={tag} className="rf-tag">{tag}</span>)}`로. `QueueCard.tsx`: `{t?.rf_detected ? " RF" : ""}`를 `{t && clueTags(t).length ? ` ${clueTags(t).join("·")}` : ""}`로. `frameCards.ts`의 `threatOf`에 `else if (r === "ir_signature") parts.push("열 신호 감지 +0.10"); else if (r === "sound") parts.push("소음 감지 +0.10");`(`rf_emission` 줄 다음).

- [ ] **Step 4: 통과를 확인한다**

Run: `cd modules/cop-ui && npx tsc -b && npx vitest run`
Expected: tsc 오류 0, vitest 전체 PASS (기존 단언 포함).

- [ ] **Step 5: Commit**

```bash
git add modules/cop-ui
git commit -m "Part2-sensors: the screen treats a heat or sound clue like an RF clue (known target, tag text, score line; decision NNNN)"
```

---

### Task 8: 공격 작전 데이터와 변경 대장

**Files:**
- Modify: `scripts/make_strike_scenario.py`, `demo/scenarios/baengnyeong_strike.json`(생성), `tests/test_strike_scenario.py`

**Interfaces:**
- Consumes: Task 2~6. Produces: 설계 5절 변경 대장의 모든 칸이 테스트로 고정된다.

- [ ] **Step 1: 데이터가 맞는지 검사하는 테스트를 쓴다** (`tests/test_strike_scenario.py` 끝)

```python
SITE_C = (37.97272, 124.64615)


def test_the_sensor_ranges_and_signatures_are_on_the_strike_operation(sc):  # decision NNNN
    by = {v.id: v for v in sc.vehicles}
    for d in ("r1", "r2", "r3"):
        assert (by[d].ir_range_m, by[d].acoustic_range_m) == (800.0, 0.0), d
    assert (by["ugv"].ir_range_m, by["ugv"].acoustic_range_m) == (0.0, 500.0)
    for d in ("usv", "a1", "a2", "a3"):
        assert (by[d].ir_range_m, by[d].acoustic_range_m) == (0.0, 0.0), d
    sig = {e.id: (e.heat, e.noise) for e in sc.enemies}
    assert sig == {"site_a": (False, False), "site_b": (True, False), "site_c": (False, True)}


def test_the_ground_robot_waits_on_land_outside_the_ears_of_site_c(sc):
    ugv = next(v for v in sc.vehicles if v.id == "ugv").home
    c = GeoPoint(lat=SITE_C[0], lon=SITE_C[1])
    assert inside(ugv, sc.land)
    assert 500 < dist_m(ugv, c) < 2000  # silent at the start, a few minutes away
    assert all(
        dist_m(ugv, e.pos) > 500 for e in sc.enemies
    )  # hears nothing before the operator sends it
    assert dist_m(ugv, c) > 300  # and cannot see it either (its sensor is 300 m)
```
그리고 변경 대장의 실행 검사 (파일에 이미 있는 `_run_until`, `_card`, `_site`, `_answer`, `_open_card`, `Decision`, `TickInputs`, `init_engine`, `tick`을 쓴다. `DirectControl`은 `from contracts.models import DirectControl`을 import에 더한다):

```python
def test_site_b_is_identified_by_one_scout_with_infrared(sc):  # change ledger: 0.60 limit -> 0.70
    es = init_engine(sc)
    es = _run_until(es, lambda e: _open_card(e, "r3", "site_b") is not None, limit=9000)
    es = _run_until(es, lambda e: _site(e, "site_b").ident_state == "identified", limit=400)
    es, _ = tick(es, TickInputs())
    b = _site(es, "site_b")
    assert b.ir_detected and "ir_signature" in b.threat_reasons and b.threat == 55
    assert b.ident_reasons == ["ir_signature", "scan", "sustained"] and b.ident_confidence == 70
    assert {"strike_a1", "strike_a2", "strike_a3", "strike_all"} <= {
        c.id for c in _open_card(es, "r3", "site_b").choices
    }


def test_site_c_needs_the_ground_robot_to_hear_it(sc):  # change ledger: drone alone stays at 0.60
    es = init_engine(sc)
    es = _run_until(es, lambda e: _open_card(e, "r2", "site_c") is not None)
    for _ in range(60 * 1000 // sc.tick_ms):  # a minute of the scout alone
        es, _ = tick(es, TickInputs())
    c = _site(es, "site_c")
    assert (c.ident_state, c.ident_confidence, c.sound_detected) == ("identifying", 60, False)
    assert not any(x.id.startswith("strike_") for x in _open_card(es, "r2", "site_c").choices)
    goal = GeoPoint(
        lat=SITE_C[0] - 0.0036, lon=SITE_C[1]
    )  # 400 m south of the site, inside its 500 m ears
    dec = DirectControl(id="dir-1", vehicle_id="ugv", target=goal, t_ms=es.t_ms + sc.tick_ms)
    es, _ = tick(es, TickInputs(direct=[dec]))
    es = _run_until(
        es, lambda e: _site(e, "site_c").sound_detected, limit=1500
    )  # about 3.5 minutes
    es = _run_until(es, lambda e: _site(e, "site_c").ident_state == "identified", limit=50)
    es, _ = tick(es, TickInputs())
    c = _site(es, "site_c")
    assert (
        c.sound_detected
        and "sound" in c.ident_reasons
        and c.ident_confidence == 70
        and c.threat == 55
    )
    assert {"strike_a1", "strike_a2", "strike_a3", "strike_all"} <= {
        x.id for x in _open_card(es, "r2", "site_c").choices
    }


def test_site_a_is_exactly_as_before(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _open_card(e, "r1", "site_a") is not None, limit=9000)
    a = _site(es, "site_a")
    assert (a.threat, a.threat_reasons) == (
        75,
        ["kind_unknown", "near_watch_radius", "rf_emission"],
    )
    assert (a.ir_detected, a.sound_detected) == (False, False)
```

- [ ] **Step 2: 실패를 확인한다**

Run: `uv run pytest tests/test_strike_scenario.py -n 0 -q -p no:cacheprovider`
Expected: 새 테스트 5개 FAIL(데이터 없음), **기존 두 테스트도 FAIL하기 시작하지 않는다**(아직 데이터가 안 바뀌었으니 통과).

- [ ] **Step 3: 생성 스크립트를 고친다**

`make_strike_scenario.py` 위쪽 상수 근처에:
```python
# decision NNNN: virtual infrared on the scouts, virtual hearing on the ground robot, a heat and a noise site
IR_RANGE_M, ACOUSTIC_RANGE_M = 800.0, 500.0
# the ground robot waits 1500 m south of site_c on land, outside its 500 m ears: the operator sends it
UGV_START = {"lat": 37.95923, "lon": 124.64615, "alt_m": 0.0}
SIGNATURES = {"site_b": {"heat": True}, "site_c": {"noise": True}}
```
`fleet()`에서 정찰 드론 만드는 줄을 `recon = [drone("d1", …) | {"ir_range_m": IR_RANGE_M} for …]`로, 반환의 ugv를 `copy.deepcopy(by_id["ugv"]) | {"acoustic_range_m": ACOUSTIC_RANGE_M, "home": dict(UGV_START)}`로 바꾼다. `enemies` 만드는 사전 끝에 `| SIGNATURES.get(i, {})`를 더한다. `Scenario.model_validate(out)`이 그대로 통과해야 한다.

- [ ] **Step 4: JSON을 다시 만들고 새 테스트를 본다**

Run: `uv run python scripts/make_strike_scenario.py && uv run pytest tests/test_strike_scenario.py -n 0 -q -p no:cacheprovider`
Expected: 새 5개 PASS. **기존 테스트 중 아래 둘이 FAIL한다. 이것이 변경 대장이 예고한 변화다**:
  - `test_a_silent_site_seen_by_one_drone_never_reaches_identified`: site_b가 이제 열 신호로 식별된다.
  - `test_two_scouts_on_a_silent_site_identify_it_and_open_the_strike_choices`: site_b가 두 번째 기체 없이도 먼저 식별되므로 `multi_observer`가 이유에 없다.
  그 밖의 실패는 예상 밖이다. **멈추고** 원인을 읽어 보고한다.

- [ ] **Step 5: 예고된 두 테스트를 새 사실에 맞게 고친다**

`test_a_silent_site_seen_by_one_drone_never_reaches_identified`를 이름과 단언까지 바꾼다:
```python
def test_a_silent_site_without_a_clue_never_reaches_identified_with_one_scout(sc):
    # site_b now gives off heat (infrared identifies it alone), site_c is heard only by the ground robot
    es = init_engine(sc)
    for _ in range(7500):  # 25 simulated minutes
        es, _ = tick(es, TickInputs())
    assert _site(es, "site_c").ident_state in ("identifying", "rf_only")  # the robot was never sent
    assert _site(es, "site_b").ident_state == "identified"
```
`test_two_scouts_on_a_silent_site_identify_it_and_open_the_strike_choices`에서 `assert "multi_observer" in site_b.ident_reasons`를 `assert {"ir_signature", "scan"} <= set(site_b.ident_reasons)`로 바꾸고 이름을 `test_two_scouts_on_site_b_both_see_it_and_the_strike_choices_open`로. 나머지 단언(두 기체가 봄, 신뢰도 70 이상, 타격 선택지)은 그대로. 이 둘은 계획된 변경이다. 같은 이유를 원장에 `Ruling:`으로 적는다.

- [ ] **Step 6: 변경 대장의 시각을 다시 재서 적는다**

Run: `uv run python - <<'E'`로 기본 흐름(`r1` 시계, `r2` 반시계, `r3` 반시계)을 25분 돌려 첫 카드 시각과 식별 시각을 출력한다(`ev.setdefault(f"card {r.vehicle_id}->{r.target_id}", (es.t_ms - T0)//1000)` 방식, `E`로 닫는다).
Expected: site_a 941초 그대로. site_b·site_c 카드 시각이 설계 문서 5절의 "약 1444초", "338초 그대로"와 몇 초 안에서 맞는다. 다르면 `docs/superpowers/specs/2026-10-11-ir-acoustic-sensors-design.md`의 5절 표 숫자를 **측정값으로** 고친다.

- [ ] **Step 7: 전체 확인과 Commit**

Run: `uv run pytest tests/test_strike_scenario.py modules/gateway tests/test_other_operations_unchanged.py -q -p no:cacheprovider`
Expected: PASS.
```bash
git add scripts demo tests docs
git commit -m "Part2-sensors: strike operation gets infrared on the scouts, hearing on the ground robot (moved 1.5 km from site_c), heat on site_b and noise on site_c (decision NNNN)"
```

---

### Task 9: 전체 검증과 기록

**Files:**
- Modify: `modules/sim/SPEC.md`, `modules/sensing/SPEC.md`, `modules/gateway/SPEC.md`(완료 기준 문구), `demo/BUILT_HERE.md`

- [ ] **Step 1: 다른 작전이 그대로인지 확인한다**

Run: `git diff origin/main --stat -- demo/scenarios | cat` — `baengnyeong_strike.json`만 나와야 한다.
Run: `uv run pytest tests/test_other_operations_unchanged.py -n 0 -q` — PASS(해시 그대로, 새 키 꺼짐).

- [ ] **Step 2: 전체 테스트와 정적 검사**

Run: `: > logs/gateway.log; : > logs/smoke.log; uv run pytest -p no:cacheprovider`
Expected: 실패 0. 이어서 `uv run ruff check . && uv run ruff format --check modules tests scripts && uv run python tools/check_specs.py`, `cd modules/cop-ui && npx tsc -b && npx vitest run`.
Expected: 모두 통과. `step_vehicle`·`conditions.py` 등 이번에 안 건드린 파일의 diff는 없어야 한다(`git diff --stat origin/main...HEAD -- modules/runtime`는 비어 있다).

- [ ] **Step 3: SPEC과 기록**

`modules/sim/SPEC.md`의 SIM-11 행에 "heat·noise도 표적에 복사(결정 NNNN)", `modules/sensing/SPEC.md`의 SNS-03 행에 "열·소음 단서 +10씩, 키워드 전용 기본 꺼짐", SNS-04 행에 "열·소음 증거 +10", `modules/gateway/SPEC.md`의 GW-10·GW-12 행에 "ir/acoustic 수신기, 단서 전달"을 한 문장씩 더한다. `demo/BUILT_HERE.md` 끝에 한 줄:
```
| 10/11 HH:MM | contracts·sim·sensing·gateway·cop-ui·demo·tests | 공격 작전 가상 적외선·음향 센서: 정찰 드론 적외선 800 m, 지상 로봇 음향 500 m(site_c 정남쪽 1.5 km로 옮김, 운용자가 보냄), site_b 열 신호·site_c 소음으로 위험도 +0.10·식별 +0.10, 화면이 열·소음 단서를 단서로 인정(결정 NNNN 초안, 리드·황승주 알림 필요) | 최동호 |
```

- [ ] **Step 4: 눈으로 확인한다 (선택)**

UI를 빌드(`cd modules/cop-ui && npm run build --silent`)하고 `scripts/demo.sh demo/scenarios/baengnyeong_strike.json`(로그는 `> ~/scratch/server.log 2>&1`). 확인할 것: site_c 카드가 뜬 뒤 지도에서 `ugv`를 직접 조종으로 site_c 근처에 보내면, 약 3분 반 뒤 site_c의 태그에 `소음`이 붙고 식별이 0.70이 되어 타격 선택지가 열린다. site_b는 `r3`가 가까이 갈 때 태그 `열`.

- [ ] **Step 5: Commit**

```bash
git add modules demo
git commit -m "Part2-sensors: SPEC and BUILT_HERE lines for the infrared and acoustic sensors (decision NNNN)"
```

---

## Self-Review

1. **Spec coverage**: 4.1 데이터(Task 2), 4.2 계산(Task 4·5), 4.3 연결(Task 3·6), 4.4 시나리오 데이터와 ugv 이동(Task 8), 4.5 화면(Task 7), 5 변경 대장(Task 8 Step 1·5·6), 6 다른 작전 보호(Task 1·9와 모든 Task의 기준선 재실행), 7 추천값과 다른 곳(Global Constraints의 값, Task 8의 ugv 테스트), 8 결정·알림(Task 2 Step 1, Task 9 Step 3).
2. **Placeholder scan**: `NNNN`은 `decide.py`가 주는 번호라 계획 시점에는 쓸 수 없다. 해시 `RECORD_ME`는 Task 1 Step 2에서 기록하는 값이다. 그 밖의 TODO·TBD는 없다. `scenario_with`·`enemy`·`appear_tick_ms`(Task 3)는 기존 테스트 도우미 이름을 따라 맞추라고 적었다.
3. **Type consistency**: `heat`/`noise`(적·표적 정답), `ir_detected`/`sound_detected`(감지 결과), `ir_range_m`/`acoustic_range_m`(기체), 이유 코드 `ir_signature`/`sound`, `clueTags`의 `RF`/`열`/`소음`이 모든 Task에서 같다. `score_target`·`identify_target` 키워드 인자 이름은 Task 4·5·6에서 같다.
4. **Review Focus**: 다섯 줄 모두 테스트가 있다(기준선 Task 1, 범위 경계와 0·비활성 기체·상한·무력화 Task 4·6, 단서만 식별 안 됨 Task 5).
5. **확인하지 못한 것**: 이 계획의 코드는 실행해 보지 않았다. (a) `test_spawn_enemies.py`의 도우미 이름, (b) `frameCards`·`QueueCard`의 기존 테스트 파일 위치, (c) 기준선 4000틱의 실행 시간(24시간 시나리오)은 Task 안에서 확인하라고 적었다. (d) Task 8 Step 6의 카드 시각이 설계 문서의 "약 1444초/338초"와 같을지는 측정해서 문서를 고치는 단계가 있다. (e) 기준선이 새 키를 빼고 비교하므로, 새 필드가 기존 필드의 값을 바꾸는 실수(예: `threat` 계산)는 잡지만 새 필드 자체의 오류는 Task 4~8의 테스트가 잡는다.
