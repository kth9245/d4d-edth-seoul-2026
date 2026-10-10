# T1 공격 작전 2단계 Implementation Plan (식별·신뢰도, 식별된 거점에만 타격 선택지)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 정찰 드론이 거점 하나를 RF로 잡고 스캔해 가며 **식별 신뢰도**가 오르고, 신뢰도가 기준(0.70)에 닿은 거점의 발견 카드에만 **타격 승인 선택지**(d2, usv)가 열린다. 운용자가 고르면 기존 엔진의 타격 경로로 거점이 무력화된다.

**Architecture:** 증거를 점수로 바꾸는 순수 함수 `identify_target`(sensing)이 `Target`의 새 필드 4개를 채우고, gateway 액션 둘이 이를 틱 루프에 건다. `identify_targets`는 표적마다 식별 필드를 쓰고, `refresh_strike_cards`는 열린 발견 카드의 문구에 식별 줄을 붙이며 식별된 거점에만 타격 선택지를 더한다. 화면(cop-ui)은 바꾸지 않는다. 카드는 문구와 선택지를 이미 그대로 그리기 때문이다. 식별 대상은 종류가 `unknown`인 표적(고정 거점)뿐이라 야간·24시간 작전은 그대로다.

**Tech Stack:** Python, pydantic 계약(`contracts/models`), pytest(`uv run pytest …`, 디버깅 `-n 0`), 시나리오 JSON, `scripts/gen_contracts.py`.

**Spec:** `docs/superpowers/specs/2026-10-10-t1-coastal-strike-operation-design.md`(6절 흐름 2~4단계, 7.1절 식별·신뢰도, 11절 2단계, 12절 정할 것 5번). 1단계: `docs/superpowers/plans/2026-10-10-strike-op-stage1.md`.

## Global Constraints

- **계약 변경(Task 1)은 `/decide`로 기록하고 사람이 `uv run python scripts/decide.py accept NNNN --by 최동호`로 확정한 뒤에만 한다.** AI는 `확정`을 직접 쓰지 못한다(AGENTS.md). 설계 3절 7항: 계약·정책 결정은 최동호가 정하고 리드에게 승인을 구하지 않는다.
- **cop-ui, `modules/{runtime,safety,role}` 코드는 수정하지 않는다.** 바꾸는 곳은 `contracts/models/events.py`(생성 파일 재생성 포함), `modules/sensing`, `modules/gateway/actions`와 `modules/gateway/engine.py`(호출 순서만), 시나리오 생성 스크립트와 JSON, 테스트, SPEC, 기록 문서다.
- 식별 대상은 **`kind == unknown`이고 무력화되지 않은 표적**뿐이다. 다른 표적·다른 작전의 프레임은 한 글자도 바뀌지 않는다.
- 수치(25·40·15·20·70 등)는 모두 **임의 초안**이다(설계 7.1절). 상수는 `modules/sensing/actions/identify_target.py` 위쪽 한 곳에만 둔다.
- 신뢰도·점수 단위는 `threat`와 같은 **0.01 단위 정수(0~100)**다.
- 용어는 **Role**(결정 0052). 타격은 항상 운용자 승인을 거친다(결정 0033): 선택지를 열 뿐 자동으로 치지 않는다.
- 액션 파일은 공개 함수 1개, 이름 = 파일 이름, 80줄 이하. `engine.py`는 호출 순서만. 새 액션은 SPEC.md에 행을 먼저 쓴다(guard).
- 모든 코드 변경은 실패하는 테스트를 먼저 쓴다(결정 0014). 커밋 메시지 끝에 `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`를 붙인다.
- 작업은 자기 worktree에서, 액션 하나가 끝날 때마다 `scripts/ship.sh`. 단 ship 전에 최신 `origin/main`을 받아 시나리오 JSON을 다시 만든다(Task 5의 Step 5, `test_the_json_is_what_the_script_builds`가 어긋나기 쉽다).

## 범위에서 뺀 것 (이유)

| 설계에 있으나 이 계획에 없는 것 | 이유 |
|---|---|
| 식별 상태 "민간 의심"과 부수피해 검사 | `Operation.no_strike_zones`가 계약에 없다(`grep -rn no_strike contracts` 결과 없음). 12절 3번 결정과 계약 변경이 먼저다. 상태 값은 4개만 둔다(`undetected`, `rf_only`, `identifying`, `identified`) |
| `engagement_feasibility` 별도 함수 | 도달 시간은 선택지 라벨에 한 줄로 넣는다(`거리 / 기체 속도`). 별도 함수·계약은 후속 |
| `Target` 식별 필드의 화면 표시 | 리드(cop-ui) 영역. 카드 문구에 식별 줄이 들어가므로 화면 수정 없이 보인다 |
| 결과 평가·재타격 | 3단계 |

## Review Focus

- **야간·24시간 작전이 그대로다**: 식별 필드는 기본값(`undetected`, 0)에 머물고 카드 문구·선택지가 바뀌지 않는다(Task 3, 4).
- **관측이 끊기면 신뢰도가 내려가고 타격 선택지가 사라진다**: 열린 카드에서 `strike_*` 선택지가 다음 틱에 빠진다(Task 4).
- **응답한(닫힌) 카드와 무력화된 거점의 카드는 건드리지 않는다**: `resolved_ms`가 있거나 `neutralized_ms`가 있으면 그대로(Task 4).
- **타격 가능한 기체가 하나도 없을 때**: 식별됐어도 선택지는 0개이고 카드는 "유지"만 남는다(Task 4).
- **무음 거점(B·C)은 기체 한 대로는 식별되지 않는다**: 스캔 40 + 지속 20 = 60 < 70. 두 기체가 함께 봐야 75로 열린다(Task 2).

---

### Task 1: 결정 기록과 `Target` 식별 필드 (계약)

**Files:**
- Create: `decisions/log/NNNN-타겟-식별-필드.md` (`/decide`가 만든다. 번호는 도구가 정한다)
- Modify: `contracts/models/events.py:12-34` (`Target`)
- Regenerate: `contracts/schema/`, `contracts.gen.ts`, `contracts/examples/` (직접 고치지 않는다)
- Test: `contracts/tests/` 또는 기존 계약 테스트(`uv run pytest contracts -q`로 위치 확인)

**Interfaces:**
- Produces: `Target.ident_state: Literal["undetected", "rf_only", "identifying", "identified"] = "undetected"`, `Target.ident_confidence: int = 0`, `Target.ident_reasons: list[str] = []`, `Target.ident_observed_ms: int = 0`. 이후 모든 작업이 이 이름을 쓴다.

- [ ] **Step 1: 결정 초안을 `/decide`로 적는다**

내용(한 결정으로): "`Target`에 식별 필드 4개를 더한다. 식별 기준값은 0.70(임의). 식별 상태는 4단계(민간 의심은 `no_strike_zones` 계약이 생길 때). 식별 대상은 `unknown` 종류 표적뿐." 근거는 설계 7.1절과 12절 5번. 이어서 사람이 `uv run python scripts/decide.py accept NNNN --by 최동호`로 확정한다. **확정 전에는 Step 2로 가지 않는다.**

- [ ] **Step 2: 실패하는 테스트를 쓴다**

`contracts` 아래 `Target`을 검사하는 기존 테스트 파일에 추가한다(없으면 `modules/sim/tests/`가 아니라 `contracts/tests/test_target_ident.py`를 만든다).

```python
from contracts.models import GeoPoint, Target


def test_a_new_target_has_no_identification():
    t = Target(
        id="site_a",
        kind="unknown",
        pos=GeoPoint(lat=37.9, lon=124.7),
        vel_east_mps=0,
        vel_north_mps=0,
        first_seen_ms=0,
        last_seen_ms=0,
    )
    assert (t.ident_state, t.ident_confidence, t.ident_reasons, t.ident_observed_ms) == (
        "undetected",
        0,
        [],
        0,
    )
```

- [ ] **Step 3: 실패를 확인한다**

Run: `uv run pytest contracts/tests/test_target_ident.py -n 0 -q`
Expected: FAIL (`AttributeError: ... 'ident_state'`)

- [ ] **Step 4: 필드를 더한다**

`contracts/models/events.py`의 `Target` 맨 끝(`last_seen_vel_north_mps` 다음)에 같은 주석 스타일로:

```python
ident_state: Literal["undetected", "rf_only", "identifying", "identified"] = "undetected"
ident_confidence: int = (
    0  # sensing: evidence score in 0.01 units, 0..100 (stage 2, unknown kind only)
)
ident_reasons: list[str] = []
ident_observed_ms: int = 0  # how long it has been seen without a gap (ms); a gap resets it
```

파일 위쪽 import에 `Literal`이 없으면 `from typing import Literal`을 더한다.

- [ ] **Step 5: 생성 파일을 다시 만들고 통과를 확인한다**

Run: `uv run python scripts/gen_contracts.py` 그리고 `uv run python scripts/gen_examples.py`
Run: `uv run pytest contracts tests -n 0 -q`
Expected: PASS. 생성 파일 diff가 `Target`의 새 필드 4개만이면 정상이다.

- [ ] **Step 6: cop-ui가 깨지지 않는지 본다**

Run: `cd modules/cop-ui && npx tsc -b && npx vitest run`
Expected: PASS(필드는 모두 기본값이 있어서 읽는 쪽이 깨지지 않는다). 실패하면 멈추고 리드에게 `tsc` 출력을 전한다.

- [ ] **Step 7: Commit**

```bash
git add contracts decisions
git commit -m "Part2-NN: Target gets ident_state, ident_confidence, ident_reasons, ident_observed_ms (decision NNNN); contracts regenerated"
```

---

### Task 2: `identify_target` 순수 함수 (sensing, SNS-04)

**Files:**
- Modify: `modules/sensing/SPEC.md` (SNS-04 행 추가), `modules/sensing/__init__.py` (공개 API)
- Create: `modules/sensing/actions/identify_target.py`
- Test: `modules/sensing/tests/test_identify_target.py`

**Interfaces:**
- Consumes: 없음(순수 함수).
- Produces:

```python
class Ident(NamedTuple):
    state: str          # "undetected" | "rf_only" | "identifying" | "identified"
    confidence: int     # 0.01 units, 0..100
    reasons: list[str]  # subset of ["rf_emission", "scan", "multi_observer", "sustained"], in this order
    observed_ms: int    # continuous observation so far, including this tick

def identify_target(rf_detected: bool, seen_count: int, age_ms: int | None,
                    observed_ms: int, tick_ms: int) -> Ident
```

`age_ms`는 마지막으로 본 뒤 지난 시간(ms)이고, 한 번도 스캔된 적이 없으면 `None`이다. `seen_count > 0`이면 지금 보고 있으니 `age_ms`는 무시한다.

- [ ] **Step 1: SPEC.md에 행을 쓴다**

`| SNS-04 | identify_target | rf_detected, seen_count, age_ms, observed_ms, tick_ms | Ident(state, confidence, reasons, observed_ms) | 증거(RF +25, 스캔 +40 매초 -1 감쇠, 두 기체 이상 +15, 끊김 없는 관측 매초 +1 최대 +20)를 합쳐 식별 상태 4단계와 신뢰도(0~100)를 낸다. 70 이상이면 식별됨 | 최동호 | 예정 |` (표의 열 순서는 파일의 기존 행을 따른다)

- [ ] **Step 2: 액션 파일과 실패 테스트를 만든다**

Run: `uv run python scripts/new_action.py sensing identify_target "증거로 식별 상태와 신뢰도를 낸다"`

- [ ] **Step 3: 테스트를 진짜 테스트로 바꾼다**

`modules/sensing/tests/test_identify_target.py`:

```python
from modules.sensing.actions.identify_target import identify_target

TICK = 200


def test_no_evidence_is_undetected():
    assert identify_target(False, 0, None, 0, TICK) == ("undetected", 0, [], 0)


def test_rf_alone_is_a_source_not_yet_confirmed():
    r = identify_target(True, 0, None, 0, TICK)
    assert (r.state, r.confidence, r.reasons) == ("rf_only", 25, ["rf_emission"])


def test_rf_plus_a_fresh_scan_is_identifying_not_yet_identified():
    r = identify_target(True, 1, 0, 0, TICK)
    assert (r.state, r.confidence, r.reasons, r.observed_ms) == (
        "identifying",
        65,
        ["rf_emission", "scan"],
        200,
    )


def test_five_seconds_of_unbroken_observation_reaches_the_threshold():
    r = identify_target(True, 1, 0, 4800, TICK)  # 4800 + 200 = 5000 ms -> +5
    assert (r.state, r.confidence, r.observed_ms) == ("identified", 70, 5000)
    assert r.reasons == ["rf_emission", "scan", "sustained"]


def test_a_second_observer_adds_fifteen():
    r = identify_target(True, 2, 0, 0, TICK)
    assert (r.state, r.confidence) == ("identified", 80)
    assert "multi_observer" in r.reasons


def test_a_silent_site_needs_two_observers():
    one = identify_target(False, 1, 0, 19800, TICK)  # scan 40 + sustained 20
    assert (one.state, one.confidence) == ("identifying", 60)
    two = identify_target(False, 2, 0, 19800, TICK)
    assert (two.state, two.confidence) == ("identified", 75)


def test_losing_it_resets_the_duration_and_fades_the_scan():
    r = identify_target(True, 0, 30_000, 6000, TICK)  # 30 s since last seen
    assert (r.state, r.confidence, r.observed_ms) == ("identifying", 35, 0)  # rf 25 + scan 10


def test_after_forty_seconds_only_the_rf_clue_is_left():
    r = identify_target(True, 0, 40_000, 0, TICK)
    assert (r.state, r.confidence, r.reasons) == ("rf_only", 25, ["rf_emission"])
```

- [ ] **Step 4: 실패를 확인한다**

Run: `uv run pytest modules/sensing/tests/test_identify_target.py -n 0 -q`
Expected: FAIL (`NotImplementedError` 또는 반환 값 불일치)

- [ ] **Step 5: 구현한다**

`modules/sensing/actions/identify_target.py`(생성된 뼈대의 본문을 바꾼다):

```python
"""SNS-04 identify_target: 증거(RF·스캔·다중 관측·관측 지속)로 식별 상태와 신뢰도(0.01 단위)를 낸다
위협 점수(score_target)와 별개다: 이쪽은 "이것이 적 거점인가, 얼마나 확신하는가". 수치는 모두 임의 초안(설계 7.1절).
SPEC: modules/sensing/SPEC.md#SNS-04
"""

from typing import NamedTuple

RF_PTS, SCAN_PTS, MULTI_PTS, SUSTAINED_MAX_PTS = 25, 40, 15, 20
SCAN_DECAY_PER_S = 1  # the scan evidence fades one point per second after the target was lost
SUSTAINED_PER_S = 1  # unbroken observation: one point per second, up to SUSTAINED_MAX_PTS
IDENTIFIED_AT = 70


class Ident(NamedTuple):
    state: str
    confidence: int
    reasons: list[str]
    observed_ms: int


def identify_target(
    rf_detected: bool, seen_count: int, age_ms: int | None, observed_ms: int, tick_ms: int
) -> Ident:
    seen = seen_count > 0
    observed = observed_ms + tick_ms if seen else 0  # a gap resets it
    never_scanned = age_ms is None and not seen
    lost_s = 0 if seen else (age_ms or 0) // 1000
    scan = 0 if never_scanned else max(0, SCAN_PTS - lost_s * SCAN_DECAY_PER_S)
    rf = RF_PTS if rf_detected else 0
    multi = MULTI_PTS if seen_count >= 2 else 0
    sustained = min(SUSTAINED_MAX_PTS, observed // 1000 * SUSTAINED_PER_S)
    confidence = min(100, rf + scan + multi + sustained)
    parts = [
        ("rf_emission", rf),
        ("scan", scan),
        ("multi_observer", multi),
        ("sustained", sustained),
    ]
    reasons = [name for name, pts in parts if pts]
    if scan == 0:
        state = "rf_only" if rf else "undetected"
    else:
        state = "identified" if confidence >= IDENTIFIED_AT else "identifying"
    return Ident(state, confidence, reasons, observed)
```

`modules/sensing/__init__.py`: `identify_target`과 `Ident`를 import해 `__all__`에 더한다(예: `from modules.sensing.actions.identify_target import Ident, identify_target`).

- [ ] **Step 6: 통과를 확인한다**

Run: `uv run pytest modules/sensing -n 0 -q`
Expected: PASS

- [ ] **Step 7: Commit과 ship**

```bash
git add modules/sensing
git commit -m "Part2-NN: sensing identify_target (SNS-04): RF, scan, second observer and unbroken observation add up to an identification state and confidence; threshold 0.70"
scripts/ship.sh
```

---

### Task 3: `identify_targets` 게이트웨이 액션과 틱 루프 연결 (GW-12)

**Files:**
- Modify: `modules/gateway/SPEC.md` (GW-12 행), `modules/gateway/engine.py` (2.7단계 호출 한 줄)
- Create: `modules/gateway/actions/identify_targets.py`
- Test: `modules/gateway/tests/test_identify_targets.py`

**Interfaces:**
- Consumes: `modules.sensing.identify_target`(Task 2), `Target.ident_*`(Task 1). `score_targets`가 먼저 돌아 `rf_detected`가 채워져 있어야 한다.
- Produces: `identify_targets(targets: list[Target], t_ms: int, tick_ms: int) -> list[Target]`. `kind == unknown`이고 `neutralized_ms is None`인 표적만 `ident_*`를 쓰고, 나머지는 같은 객체를 돌려준다.

- [ ] **Step 1: SPEC.md에 행을 쓰고 뼈대를 만든다**

`| GW-12 | identify_targets | targets, t_ms, tick_ms | targets | unknown 종류·미무력화 표적마다 sensing identify_target을 불러 ident_state·ident_confidence·ident_reasons·ident_observed_ms를 쓴다. 다른 표적은 그대로 | 최동호 | 예정 |`
Run: `uv run python scripts/new_action.py gateway identify_targets "unknown 표적에 식별 필드를 쓴다"`

- [ ] **Step 2: 실패하는 테스트를 쓴다**

```python
from contracts.models import GeoPoint, Target
from modules.gateway.actions.identify_targets import identify_targets

POS = GeoPoint(lat=37.982, lon=124.722)


def site(**kw) -> Target:
    base = dict(id="site_a", kind="unknown", pos=POS, vel_east_mps=0, vel_north_mps=0,
                first_seen_ms=0, last_seen_ms=0, seen_by=[], rf_detected=True)  # fmt: skip
    return Target(**(base | kw))


def test_an_rf_only_site_is_not_confirmed_yet():
    t = identify_targets([site()], 10_000, 200)[0]
    assert (t.ident_state, t.ident_confidence, t.ident_reasons) == ("rf_only", 25, ["rf_emission"])


def test_a_scanned_site_climbs_tick_by_tick_and_keeps_its_observed_time():
    t = site(seen_by=["d1"], first_seen_ms=9_000, last_seen_ms=10_000)
    t1 = identify_targets([t], 10_000, 200)[0]
    t2 = identify_targets([t1], 10_200, 200)[0]
    assert (t1.ident_confidence, t1.ident_observed_ms) == (65, 200)
    assert t2.ident_observed_ms == 400


def test_a_lost_site_fades_from_its_last_seen_time():
    t = site(seen_by=[], first_seen_ms=9_000, last_seen_ms=10_000, ident_observed_ms=6000)
    r = identify_targets([t], 40_000, 200)[0]  # 30 s later
    assert (r.ident_state, r.ident_confidence, r.ident_observed_ms) == ("identifying", 35, 0)


def test_other_kinds_and_neutralized_sites_are_left_alone():
    boat = site(id="b1", kind="boat", seen_by=["d1"], first_seen_ms=1)
    dead = site(id="site_b", seen_by=["d1"], first_seen_ms=1, neutralized_ms=5)
    out = identify_targets([boat, dead], 10_000, 200)
    assert out == [boat, dead]
```

- [ ] **Step 3: 실패를 확인한다**

Run: `uv run pytest modules/gateway/tests/test_identify_targets.py -n 0 -q`
Expected: FAIL

- [ ] **Step 4: 구현한다**

```python
"""GW-12 identify_targets: unknown 종류 표적마다 sensing identify_target을 불러 ident_* 필드를 쓴다(2단계)
다른 종류와 무력화된 표적은 그대로 둬서 야간·24시간 작전의 프레임이 바뀌지 않는다.
마지막으로 본 뒤 시간은 last_seen_ms로 계산하고, 한 번도 스캔된 적 없으면(first_seen_ms == 0) None.
SPEC: modules/gateway/SPEC.md#GW-12
"""

from contracts.models import Target
from modules.sensing import identify_target


def identify_targets(targets: list[Target], t_ms: int, tick_ms: int) -> list[Target]:
    out = []
    for tg in targets:
        if tg.kind.value != "unknown" or tg.neutralized_ms is not None:
            out.append(tg)
            continue
        scanned = bool(tg.seen_by) or tg.first_seen_ms != 0
        age = None if not scanned else max(0, t_ms - tg.last_seen_ms)
        r = identify_target(tg.rf_detected, len(tg.seen_by), age, tg.ident_observed_ms, tick_ms)
        out.append(tg.model_copy(update={"ident_state": r.state, "ident_confidence": r.confidence,
                                         "ident_reasons": r.reasons,
                                         "ident_observed_ms": r.observed_ms}))  # fmt: skip
    return out
```

- [ ] **Step 5: 통과를 확인한다**

Run: `uv run pytest modules/gateway/tests/test_identify_targets.py -n 0 -q`
Expected: PASS

- [ ] **Step 6: 엔진에 건다 (실패하는 테스트 먼저)**

`modules/gateway/tests/test_engine_ident.py`:

```python
from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json


def test_the_night_operation_never_gets_identification_fields():
    es = init_engine(load_scenario_json("demo/scenarios/baengnyeong_night.json"))
    for _ in range(300):
        es, _ = tick(es, TickInputs())
    assert es.targets and all(t.ident_state == "undetected" for t in es.targets)
```

(`undetected`로 남는 것은 night의 표적이 모두 `unknown`이 아니기 때문이다. 이 작전의 표적 종류가 시작에 따라 `unknown`이 섞이면 `grep -n '"kind"' demo/scenarios/baengnyeong_night.json`으로 확인하고 테스트를 `kind != unknown` 표적으로 좁힌다.)
Run: `uv run pytest modules/gateway/tests/test_engine_ident.py -n 0 -q` → 처음에는 PASS할 수 있다(아직 안 걸었으므로). 이 테스트는 **다음 단계 뒤에도 PASS**해야 하는 안전망이다.

`modules/gateway/engine.py`에서 `score_targets` 호출 바로 아래 한 줄을 더하고 import를 맞춘다:

```python
    targets = identify_targets(targets, t, dt)  # 2.7 stage 2: identification of unknown-kind sites
```

`from modules.gateway.actions.identify_targets import identify_targets`를 import에 더한다.

- [ ] **Step 7: 전체 gateway 테스트가 그대로 통과하는지 본다**

Run: `uv run pytest modules/gateway tests -q`
Expected: PASS(night·24h 관련 기존 테스트가 하나도 깨지지 않아야 한다).

- [ ] **Step 8: Commit과 ship**

```bash
git add modules/gateway
git commit -m "Part2-NN: gateway identify_targets (GW-12) writes the identification of unknown-kind sites every tick (2.7)"
scripts/ship.sh
```

---

### Task 4: `refresh_strike_cards` — 식별 줄과 타격 선택지 (GW-13)

**Files:**
- Modify: `modules/gateway/SPEC.md` (GW-13 행), `modules/gateway/engine.py` (8.6단계 호출)
- Create: `modules/gateway/actions/refresh_strike_cards.py`
- Test: `modules/gateway/tests/test_refresh_strike_cards.py`

**Interfaces:**
- Consumes: `Target.ident_*`(Task 1·3), `VehicleSpec.capabilities`(`strike_target`), `Role` 맵에 `strike` 역할이 있어야 선택지를 만든다(Task 5가 시나리오에 넣는다).
- Produces: `refresh_strike_cards(reports: list[Report], states: list[VehicleState], specs: dict[str, VehicleSpec], targets: list[Target], roles: dict[str, Role]) -> list[Report]`. 열려 있고(`resolved_ms` 없음) `target_id`가 `unknown` 미무력화 표적을 가리키는 `target_detected` 카드만 바꾼다. 문구 끝에 ` · 식별: …` 한 줄을 붙이고(이미 있으면 갈아 끼운다), 선택지에서 `strike_`로 시작하는 것을 모두 빼고 식별됨일 때만 다시 더한다. 선택지 id는 `strike_<기체 id>`(그 기체 하나), 둘 이상이면 `strike_all`.

**왜 카드를 한 번 더 고치는가**: `fleet_choices`(5.3)가 매 틱 열린 카드의 선택지를 다시 만들어 덮어쓴다. 그래서 타격 선택지는 그 뒤, 틱 끝(8.6)에서 모든 열린 카드에 다시 붙인다.

- [ ] **Step 1: SPEC.md에 행을 쓰고 뼈대를 만든다**

`| GW-13 | refresh_strike_cards | reports, states, specs, targets, roles | reports | 열린 unknown 표적 발견 카드의 문구 끝에 식별 줄(상태·신뢰도·이유)을 붙이고, 식별됨이면 타격 가능 기체마다 타격 승인 선택지를 더한다(strike_<id>, 둘 이상이면 strike_all). 식별 전이면 타격 선택지를 모두 뺀다 | 최동호 | 예정 |`
Run: `uv run python scripts/new_action.py gateway refresh_strike_cards "식별 줄과 타격 선택지를 열린 카드에 붙인다"`

- [ ] **Step 2: 실패하는 테스트를 쓴다**

```python
from contracts.models import (
    Choice,
    GeoPoint,
    Report,
    Role,
    Step,
    Action,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.gateway.actions.refresh_strike_cards import refresh_strike_cards

HOME = GeoPoint(lat=37.978, lon=124.70)
SITE = GeoPoint(lat=37.982, lon=124.722)
STRIKE = Role(
    id="strike",
    name="표적 타격",
    domains=["air", "sea"],
    entry="strike",
    steps=[Step(id="strike", name="타격", do=Action(kind="strike_target", params={}))],
)
ROLES = {"strike": STRIKE}
SPECS = {
    "d2": VehicleSpec(id="d2", name="d2", domain="air", speed_mps=15, endurance_min=50,
                      sensor_range_m=800, capabilities=["strike_target"], home=HOME),
    "d3": VehicleSpec(id="d3", name="d3", domain="air", speed_mps=15, endurance_min=50,
                      sensor_range_m=800, capabilities=["watch_target"], home=HOME),
}  # fmt: skip


def vs(vid, **kw):
    return VehicleState(
        id=vid,
        t_ms=0,
        pos=HOME,
        heading_deg=0,
        battery_pct=100,
        status=kw.pop("status", "ready"),
        **kw,
    )


def card(**kw):
    base = dict(
        id="rep-d1-1",
        t_ms=1,
        kind="target_detected",
        vehicle_id="d1",
        target_id="site_a",
        text="미식별 거점 감지 · d1 센서 탐지 · site_a(미상) · 721 m",
        choices=[Choice(id="keep", label="전 기체 현 임무 유지")],
    )
    return Report(**(base | kw))


def site(**kw):
    base = dict(
        id="site_a",
        kind="unknown",
        pos=SITE,
        vel_east_mps=0,
        vel_north_mps=0,
        first_seen_ms=1,
        last_seen_ms=1,
        ident_state="identified",
        ident_confidence=80,
        ident_reasons=["rf_emission", "scan", "multi_observer"],
    )
    return Target(**(base | kw))


def run(rep, tg, states=None):
    states = states or [vs("d2"), vs("d3")]
    return refresh_strike_cards([rep], states, SPECS, [tg], ROLES)[0]


def test_an_identified_site_opens_a_strike_choice_for_each_armed_vehicle():
    out = run(card(), site())
    ids = [c.id for c in out.choices]
    assert ids == ["keep", "strike_d2"]  # d3 cannot strike
    c = out.choices[1]
    assert (c.role_by_vehicle, c.target_by_vehicle) == ({"d2": "strike"}, {"d2": "site_a"})
    assert "식별: 식별됨 0.80" in out.text and "RF 방출" in out.text


def test_two_armed_vehicles_also_get_a_strike_all_choice():
    spec = SPECS["d3"].model_copy(update={"capabilities": ["strike_target"]})
    specs = {**SPECS, "d3": spec}
    out = refresh_strike_cards([card()], [vs("d2"), vs("d3")], specs, [site()], ROLES)[0]
    assert [c.id for c in out.choices] == ["keep", "strike_d2", "strike_d3", "strike_all"]
    assert out.choices[-1].role_by_vehicle == {"d2": "strike", "d3": "strike"}


def test_before_identification_there_is_no_strike_choice_but_the_clue_line_shows():
    out = run(
        card(),
        site(ident_state="identifying", ident_confidence=65, ident_reasons=["rf_emission", "scan"]),
    )
    assert [c.id for c in out.choices] == ["keep"]
    assert "식별: 식별 중 0.65" in out.text


def test_losing_the_site_takes_the_strike_choice_away_again():
    first = run(card(), site())
    assert "strike_d2" in [c.id for c in first.choices]
    lost = run(
        first, site(ident_state="identifying", ident_confidence=35, ident_reasons=["rf_emission"])
    )
    assert [c.id for c in lost.choices] == ["keep"]
    assert lost.text.count("식별:") == 1  # the line is replaced, not stacked


def test_answered_cards_and_neutralized_sites_are_left_alone():
    answered = card(resolved_ms=5, decision_id="dec-1")
    assert run(answered, site()) == answered
    dead = site(neutralized_ms=9)
    assert run(card(), dead) == card()


def test_other_kinds_are_left_alone():
    boat = site(kind="boat")
    assert run(card(), boat) == card()


def test_no_available_striker_leaves_only_keep():
    busy = [vs("d2", pending_report_id="rep-x"), vs("d3")]
    out = run(card(), site(), states=busy)
    assert [c.id for c in out.choices] == ["keep"]
```

- [ ] **Step 3: 실패를 확인한다**

Run: `uv run pytest modules/gateway/tests/test_refresh_strike_cards.py -n 0 -q`
Expected: FAIL (`NotImplementedError` 또는 `ImportError`). 테스트 파일의 `Action` import 이름이 계약과 다르면(`Step.do`의 타입) `contracts.models`에서 실제 이름을 찾아 맞춘다.

- [ ] **Step 4: 구현한다**

```python
"""GW-13 refresh_strike_cards: 열린 unknown 표적 발견 카드에 식별 줄을 붙이고, 식별됨일 때만 타격 승인 선택지를 연다(2단계)
fleet_choices(5.3)가 매 틱 선택지를 덮어쓰므로 틱 끝에서 다시 붙인다. 타격은 여전히 운용자 승인으로만(결정 0033).
선택지 id: strike_<기체 id>, 둘 이상이면 strike_all. 이미 응답한 카드·무력화된 표적·다른 종류는 그대로.
SPEC: modules/gateway/SPEC.md#GW-13
"""

from contracts.models import Choice, Report, Role, Target, VehicleSpec, VehicleState, VehicleStatus
from shared.geo import dist_m

LIVE = (VehicleStatus.ready, VehicleStatus.active)
STATE_KO = {"undetected": "미탐", "rf_only": "방출원 미확인", "identifying": "식별 중",
            "identified": "식별됨"}  # fmt: skip
REASON_KO = {"rf_emission": "RF 방출", "scan": "스캔 확인", "multi_observer": "2기체 관측",
             "sustained": "관측 지속"}  # fmt: skip
MARK = " · 식별:"


def _line(tg: Target) -> str:
    why = ", ".join(REASON_KO.get(r, r) for r in tg.ident_reasons)
    return f"{MARK} {STATE_KO[tg.ident_state]} {tg.ident_confidence / 100:.2f}" + (
        f" · 이유: {why}" if why else ""
    )


def _strikers(states, specs, roles) -> list[VehicleState]:
    if "strike" not in roles:
        return []
    return [s for s in states if s.status in LIVE and s.pending_report_id is None
            and "strike_target" in [c.value for c in specs[s.id].capabilities]]  # fmt: skip


def refresh_strike_cards(
    reports: list[Report],
    states: list[VehicleState],
    specs: dict[str, VehicleSpec],
    targets: list[Target],
    roles: dict[str, Role],
) -> list[Report]:
    by_id = {t.id: t for t in targets}
    out = []
    for r in reports:
        tg = by_id.get(r.target_id or "")
        if (r.kind != "target_detected" or r.resolved_ms or tg is None
                or tg.kind.value != "unknown" or tg.neutralized_ms is not None):  # fmt: skip
            out.append(r)
            continue
        kept = [c for c in r.choices if not c.id.startswith("strike_")]
        add = []
        if tg.ident_state == "identified":
            armed = _strikers(states, specs, roles)
            add = [Choice(id=f"strike_{s.id}", role_by_vehicle={s.id: "strike"},
                          target_by_vehicle={s.id: tg.id},
                          label=f"{s.id} 타격 승인({tg.id}) · 도달 약 "
                                f"{dist_m(s.pos, tg.pos) / specs[s.id].speed_mps:.0f}초")
                   for s in armed]  # fmt: skip
            if len(armed) > 1:
                add.append(Choice(id="strike_all", label=f"전원 타격 승인({tg.id})",
                                  role_by_vehicle={s.id: "strike" for s in armed},
                                  target_by_vehicle={s.id: tg.id for s in armed}))  # fmt: skip
        text = r.text.split(MARK)[0] + _line(tg)
        out.append(r.model_copy(update={"text": text, "choices": [*kept, *add]}))
    return out
```

- [ ] **Step 5: 통과를 확인한다**

Run: `uv run pytest modules/gateway/tests/test_refresh_strike_cards.py -n 0 -q`
Expected: PASS

- [ ] **Step 6: 엔진에 건다**

`modules/gateway/engine.py`에서 `new_reports += cards + hits` 와 `reports += new_reports` 다음, `outcome = TickOutcome(...)` 바로 앞에 한 줄:

```python
    reports = refresh_strike_cards(reports, states, specs, targets, roles)  # 8.6 stage 2
```

import를 더한다. 야간·24h 안전망(Task 3의 `test_engine_ident.py`)과 전체를 다시 돌린다.
Run: `uv run pytest modules/gateway tests -q`
Expected: PASS

- [ ] **Step 7: Commit과 ship**

```bash
git add modules/gateway
git commit -m "Part2-NN: gateway refresh_strike_cards (GW-13): open unknown-site cards show the identification line, and only an identified site opens strike approval choices (8.6)"
scripts/ship.sh
```

---

### Task 5: 시나리오에 `strike` 역할을 넣고 JSON을 다시 만든다

**Files:**
- Modify: `scripts/make_strike_scenario.py` (역할 목록과 작전 목적 문구), `demo/scenarios/baengnyeong_strike.json` (생성물)
- Test: `tests/test_strike_scenario.py`

**Interfaces:**
- Consumes: 야간 시나리오의 `strike` 역할(`roles["strike"]`, `domains: ["air","sea"]`).
- Produces: `baengnyeong_strike.json`의 `roles`에 `strike`가 있다(Task 4의 선택지가 이 역할로 기체를 옮긴다).

- [ ] **Step 1: 실패하는 테스트를 더한다** (`tests/test_strike_scenario.py` 끝)

```python
def test_the_strike_role_is_available_to_the_armed_vehicles(sc):
    roles, specs = {r.id: r for r in sc.roles}, {v.id: v for v in sc.vehicles}
    assert "strike" in roles
    armed = [v for v, s in specs.items() if "strike_target" in [c.value for c in s.capabilities]]
    assert set(armed) == {"d2", "usv"}  # the ontology comes from night
```

- [ ] **Step 2: 실패를 확인한다**

Run: `uv run pytest tests/test_strike_scenario.py::test_the_strike_role_is_available_to_the_armed_vehicles -n 0 -q`
Expected: FAIL (`assert "strike" in roles`)

- [ ] **Step 3: 생성 스크립트를 고친다**

`build()`의 `roles` 목록에 `roles["strike"]`를 더한다:

```python
        "roles": [patrol, roles["standby"], roles["go_home"], roles["watch"], roles["approach"],
                  roles["strike"], site_hold()],
```

`purpose` 문구의 `(1단계)`를 `(2단계: 식별된 거점에만 타격 승인)`으로 바꾼다.

- [ ] **Step 4: JSON을 다시 만들고 테스트한다**

Run: `uv run python scripts/make_strike_scenario.py`
Run: `uv run pytest tests/test_strike_scenario.py tests/test_demo_routes.py modules/gateway -q`
Expected: PASS. `test_the_operation_passes_the_role_checks`가 `strike` 역할 때문에 실패하면 `check_operation`의 메시지를 읽고(역할이 시작 배정에 안 쓰여도 되는지) 보고만 하고 멈춘다. `modules/role`은 고치지 않는다.

- [ ] **Step 5: ship 전에 최신 main과 맞춘다**

Run: `git fetch origin && git rebase origin/main`, 이어서 `uv run python scripts/make_strike_scenario.py && git diff --stat demo/scenarios/baengnyeong_strike.json`
야간 시나리오가 바뀌어 JSON이 달라지면 그대로 커밋한다(`test_the_json_is_what_the_script_builds`가 이것을 잡는다).

- [ ] **Step 6: Commit과 ship**

```bash
git add scripts demo tests
git commit -m "Part2-NN: strike operation gets the strike Role so the identified-site approval choices have something to start"
scripts/ship.sh
```

---

### Task 6: 끝에서 끝까지 — 식별 → 승인 → 무력화 (인수 테스트)

**Files:**
- Test: `tests/test_strike_scenario.py` (또는 `tests/test_strike_stage2.py`)

**Interfaces:**
- Consumes: Task 1~5 전부.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

```python
from contracts.models import Decision, TickInputs
from modules.gateway.engine import init_engine, tick


def _run_until(es, pred, limit=6000):
    for _ in range(limit):
        if pred(es):
            return es
        es, _ = tick(es, TickInputs())
    raise AssertionError("never happened")


def _card(es):
    return next(r for r in es.reports if r.kind == "target_detected" and r.target_id == "site_a")


def _site(es):
    return next(t for t in es.targets if t.id == "site_a")


def test_site_a_is_identified_then_approved_then_neutralized(sc):
    es = init_engine(sc)
    # 1. the RF clue comes first: no scan yet, so no strike choice
    es = _run_until(es, lambda e: _site(e).ident_state == "rf_only")
    # 2. the drone sees it; confidence climbs; the card still has no strike choice
    es = _run_until(es, lambda e: any(r.target_id == "site_a" for r in e.reports))
    assert not any(c.id.startswith("strike_") for c in _card(es).choices)
    # 3. identified: d2 and usv can be approved
    es = _run_until(es, lambda e: _site(e).ident_state == "identified")
    es, _ = tick(es, TickInputs())  # the card is refreshed at the end of the tick
    ids = [c.id for c in _card(es).choices]
    assert {"strike_d2", "strike_usv", "strike_all"} <= set(ids)
    assert "식별: 식별됨" in _card(es).text
    # 4. the operator approves d2 only; the strike runs through the existing engine path
    dec = Decision(id="dec-1", t_ms=es.t_ms, report_id=_card(es).id, choice_id="strike_d2")
    es, _ = tick(es, TickInputs(decisions=[dec]))
    es = _run_until(es, lambda e: _site(e).neutralized_ms is not None, limit=9000)
    assert any(r.kind == "target_neutralized" and r.target_id == "site_a" for r in es.reports)
    assert _site(es).ident_state == "identified"  # the record stays; the card is closed


def test_the_silent_sites_stay_unidentified_without_a_clue(sc):
    es = init_engine(sc)
    for _ in range(1500):  # five simulated minutes
        es, _ = tick(es, TickInputs())
    assert [t.ident_state for t in es.targets if t.id in ("site_b", "site_c")] == ["undetected"] * 2
```

- [ ] **Step 2: 실행하고 결과를 읽는다**

Run: `uv run pytest tests/test_strike_scenario.py -n 0 -q`
Expected: PASS. 실패하면 **어느 단계(1~4)에서 멈췄는지**부터 읽는다. 예상되는 어긋남과 원인:
  - 단계 3이 안 오면: 드론이 거점 위에서 계속 관측하는지(`watch_target` 150 m) `es.states`의 d1 `step_id`로 확인하고, 상수(Task 2) 때문이면 **상수를 고치지 말고 테스트 기대를 먼저 의심**한다. 값은 임의이므로 결정 문서와 함께 바꾼다.
  - 단계 4에서 차단되면: `es.blocks`의 사유를 읽는다(구역·귀환 배터리 규칙). 이동 시간 때문에 d2 배터리가 모자라면 보고하고 멈춘다(규칙은 제품 기능이라 풀지 않는다).

- [ ] **Step 3: 서버에서 눈으로 확인한다**

Run: `scripts/demo.sh demo/scenarios/baengnyeong_strike.json` (UI 빌드가 `/mnt/c`에서 막히면 WSL 홈의 worktree에서)
화면: 일시정지에서 시작 → 실행 → 약 5분(시뮬레이션) 뒤 site_a 카드 → 문구 끝의 `식별:` 줄이 `방출원 미확인`에서 `식별 중 0.65`, `식별됨 0.70+`로 바뀌고 그때 타격 승인 선택지가 생긴다.

- [ ] **Step 4: Commit과 ship, 기록**

```bash
git add tests
git commit -m "Part2-NN: strike operation stage 2 acceptance: the RF clue, the scan, identification, d2 approval and the neutralized report"
scripts/ship.sh
uv run python scripts/task.py done Part2-NN
```

`demo/BUILT_HERE.md`에 한 줄(식별·신뢰도, 식별된 거점에만 타격 승인 선택지)을 더한다. 리드(kth9245)에게 알린다: `Target`에 식별 필드 4개가 생겨 `contracts.gen.ts`가 바뀌었다(화면 변경은 필요 없음. 원하면 카드 옆 신뢰도 막대 등을 후속으로).

---

## Self-Review

1. **Spec coverage**: 7.1절의 증거 5개 중 RF·스캔·다중 관측·관측 지속·놓침 감소를 Task 2가 모두 구현한다. 상태 5단계 중 "민간 의심"은 범위에서 뺐고 이유를 표로 적었다(`no_strike_zones` 계약 없음). "식별됨일 때만 타격 대안"은 Task 4, 승인 카드 근거(식별 상태·신뢰도·이유·도달 시간)는 Task 4의 문구와 라벨, "추가 정찰 대안"은 기존 `fleet_choices`의 함께 감시 선택지가 이미 한다. 교전 가능성 별도 함수와 부수피해 표시는 범위에서 뺐다.
2. **Placeholder scan**: `NNNN`/`Part2-NN`은 결정 번호와 작업 번호로, `/decide`와 `task.py`가 정하는 값이라 계획 시점에는 쓸 수 없다. 코드 단계에 TODO는 없다.
3. **Type consistency**: `Ident(state, confidence, reasons, observed_ms)` → `identify_targets`가 `ident_state/ident_confidence/ident_reasons/ident_observed_ms`로 옮기는 이름이 Task 1·2·3·4 모두 같다. 선택지 id `strike_<id>`·`strike_all`은 Task 4와 6이 같다.
4. **Review Focus**: 다섯 줄 모두 테스트가 있다(야간 안전망 Task 3, 끊김 Task 4, 닫힌 카드·무력화 Task 4, 기체 없음 Task 4, 무음 거점 Task 2·6).
5. **확인하지 못한 것**: 이 계획의 코드는 실행해 보지 않았다. `Action`/`Step` 계약 이름, `new_action.py`가 만드는 뼈대, 야간 시나리오의 `unknown` 표적 유무는 Task 안에 "어긋나면 이렇게 확인한다"를 적어 두었다.
