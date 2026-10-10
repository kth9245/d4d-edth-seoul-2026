# 카드 하나당 드론 하나 흐름 복원 + 이어받기·함께 감시 덧붙이기 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 야간 시연의 시작을 `d1=patrol_a`, `d2=patrol_b`로 되돌려 보트마다 담당 드론이 정해진 카드 흐름을 복원하고, 그 카드의 정해진 선택지 뒤에 "발생 지역 순찰 이어받기"와 "함께 감시"를 덧붙인다. 로직만 바꾸고 cop-ui는 건드리지 않는다.

**Architecture:** 시나리오 데이터(`assign`·`reserve`·세 보고 step의 `auto_choices`)를 복원하고, runtime `fleet_choices`가 정해진 선택지(`step.report.choices`) 뒤에 동적 선택지를 덧붙이되 자기 카드가 열린 드론은 후보에서 뺀다. gateway `engine.py`는 열린 자동 선택지 카드를 매 틱 다시 만들게 호출 한 줄만 더한다.

**Tech Stack:** Python, pydantic 계약, pytest(`uv run pytest modules/<m>`, 디버깅 `-n 0`).

**Spec:** `docs/superpowers/specs/2026-10-10-card-per-drone-design.md`, 결정 0046.

## Global Constraints

- **cop-ui는 수정하지 않는다.** `contracts/models/**`, 위협도 로직(`score_target`, `score_targets`)도 수정하지 않는다.
- 액션 파일은 공개 함수 1개, 80줄 이하. `engine.py`는 호출 순서만.
- 모든 코드 변경은 실패하는 테스트를 먼저 쓰고 실패를 확인한 뒤 구현한다(결정 0014).
- 결정 0024: happy path만. 엣지 케이스를 이유로 코드·테스트를 늘리지 않는다. 운영자가 누르는 틱과 선택지 갱신 사이의 한 틱 시차는 막지 않는다.
- JSON은 `json.dumps(data, indent=1, ensure_ascii=False) + "\n"`으로 저장하면 원래 서식과 바이트 단위로 같다(확인함). 그 방식으로 고쳐서 불필요한 diff를 만들지 않는다.
- 24시간 작전(`baengnyeong_24h`)과 `coast_a`/`coast_b` 플레이는 바꾸지 않는다.
- runtime·시나리오·`test_demo_timeline` 등은 황승주 영역이다. 이 설계는 황승주가 동의했고, 마지막에 무엇을 바꿨는지 알린다.
- 결정 번호가 겹친 적이 두 번 있다. 새 결정이 필요하면 `git fetch` 뒤 비어 있는 번호를 쓴다.

## Review Focus

- 정해진 선택지("근접 확인", "수상정 인계", "감시 유지")가 덧붙인 선택지보다 **앞에** 오고 그대로 동작한다(Task 1, 3).
- 자기 카드가 열린 드론은 후보에 없다. 이미 카드가 열려 있는 상태에서 선택지가 다시 만들어져도 중복되지 않는다(Task 1, 2).
- 정해진 선택지가 없는 카드(`coast_a`, 24시간 작전)는 지금과 똑같이 "전 기체 현 임무 유지"까지 나온다(Task 1).
- 보트마다 담당 드론이 정해진 카드 시각이 이전과 같다: boat1 16:30.2(d1), boat2 16:32.8(d2), boat3 18:33.2(d2, 운영자가 앞 카드에 답한 경우)(Task 3). 사전 확인에서 `relieve_hover`가 켜져도 같았다.
- boat2가 17:00에 방출하며 점수 0.42 → 0.72가 되고 boat1(0.50) 카드 위로 올라간다(Task 3).

---

### Task 1: `fleet_choices` — 정해진 선택지 뒤에 덧붙이고 열린 카드 드론은 뺀다

**Files:**
- Modify: `modules/runtime/actions/fleet_choices.py` (RT-11)
- Test: `modules/runtime/tests/test_fleet_choices.py`

**Interfaces:**
- Produces: `fleet_choices(rep, states, op, plays) -> Report`는 서명이 그대로다. 동작만 바뀐다: ① 결과 선택지 = `step.report.choices`(정해진 것) + take + join, "keep"은 정해진 선택지가 **없을 때만** 끝에 붙는다. ② 후보 `others`는 `s.pending_report_id is None`인 드론만이다. ③ 정해진 선택지는 카드(`rep.choices`)가 아니라 그 드론의 현재 step에서 읽는다(매 틱 다시 만들어도 중복되지 않는다).

- [ ] **Step 1: 실패하는 테스트** — `test_fleet_choices.py`에 추가한다(기존 테스트는 그대로 둔다).

```python
def static_play(pid: str, name: str) -> Play:  # an old-flow patrol: a card with its own choice
    p = coast(pid, name)
    rep = p.steps[1].model_copy(update={"report": ReportSpec(
        text="미식별 선박 접근", auto_choices=True,
        choices=[Choice(id="approach", label="근접 확인", play_by_vehicle={"d1": "watch"})])})
    return p.model_copy(update={"steps": [p.steps[0], rep]})


STATIC_PLAYS = {**PLAYS, "coast_a": static_play("coast_a", "해안 순찰 A")}


def test_planned_choices_stay_first_and_the_fleet_choices_follow_without_keep():
    states = [vs("d1", "coast_a", "report", target="boat1"), vs("d3", None, None, "ready")]
    rep = fleet_choices(CARD, states, OP, STATIC_PLAYS)
    assert labels(rep) == ["approach", "take_d3", "join_d3_d1"]  # no 'keep': the card has its own


def test_choices_are_the_same_when_made_again_for_an_open_card():  # decision 0046: rebuilt every tick
    states = [vs("d1", "coast_a", "report", target="boat1"), vs("d3", None, None, "ready")]
    once = fleet_choices(CARD, states, OP, STATIC_PLAYS)
    assert labels(fleet_choices(once, states, OP, STATIC_PLAYS)) == labels(once)


def test_a_drone_with_its_own_open_card_is_not_asked():  # decision 0046: never drop a card
    states = [vs("d1", "coast_a", "report", target="boat1"), vs("d3", None, None, "ready"),
              vs("d4", None, None, "ready").model_copy(update={"pending_report_id": "rep-d4-1"})]  # fmt: skip
    rep = fleet_choices(CARD, states, OP, STATIC_PLAYS)
    assert labels(rep) == ["approach", "take_d3", "join_d3_d1"]  # nothing for d4
```

- [ ] **Step 2: 실패 확인** — `uv run pytest modules/runtime/tests/test_fleet_choices.py -n 0 -q` → 새 테스트 3개가 실패한다(현재 `labels`가 `["take_d3", "join_d3_d1", "keep"]` 형태이고 d4가 들어간다).
- [ ] **Step 3: 구현** — `fleet_choices.py`의 `others` 조건과 마지막 줄을 바꾼다.

```python
    others = [
        s
        for s in crew
        if s.id not in busy
        and s.pending_report_id is None  # decision 0046: its own card stays; apply_decision would close it
        and s.play_id != coast.id
        and (
            (s.status.value == "active" and s.play_id in op.rotation_plays)
            or (s.status.value == "ready" and s.battery_pct >= 99.9)
        )
    ]
    ...
    planned = list(step.report.choices)  # the card's own choices, read from the step each time
    keep = [] if planned else [Choice(id="keep", label="전 기체 현 임무 유지")]
    return rep.model_copy(update={"choices": [*planned, *take, *join, *keep]})
```
  모듈 docstring 한 줄도 "정해진 선택지가 있으면 그 뒤에 덧붙인다"로 고친다.
- [ ] **Step 4: 통과 확인** — 같은 명령. 기존 테스트(`test_choices_for_every_other_drone_then_keep` 등)도 모두 통과해야 한다(정해진 선택지가 없는 카드는 그대로).
- [ ] **Step 5: 커밋** (`uv run pytest modules/runtime -q`로 runtime 전체 확인 후).

---

### Task 2: `engine.py` — 열린 자동 선택지 카드를 매 틱 다시 만든다

**Files:**
- Modify: `modules/gateway/engine.py` (5.2 바로 아래 한 줄)
- Modify: `contracts/API.md` §3 틱 순서 표에 `5.3` 한 줄
- Test: `modules/gateway/tests/test_engine_choices.py` (새 파일)

**Interfaces:**
- Consumes: Task 1의 `fleet_choices`.
- Produces: 매 틱, 열려 있는(`resolved_ms` 없음) `target_detected` 카드를 `fleet_choices(r, stepped, sc.operation, plays)`로 다시 만든다. 자동 선택지가 아닌 카드는 `fleet_choices`가 그대로 돌려준다.

- [ ] **Step 1: 실패하는 테스트**

```python
"""Decision 0046: the choices of an open contact card follow the fleet every tick."""

from dataclasses import replace

from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

SC0 = load_scenario_json("demo/scenarios/baengnyeong_night.json")
OLD_START = SC0.operation.model_copy(update={"assign": {**SC0.operation.assign, "d1": "patrol_a", "d2": "patrol_b"},
                                              "reserve": {"d1": ["d3"]}})  # the old flow (Task 4 puts it in the JSON)
PLAYS = [p.model_copy(update={"steps": [
    s.model_copy(update={"report": s.report.model_copy(update={"auto_choices": True})}) if s.report else s
    for s in p.steps]}) if p.id in ("patrol_a", "patrol_b") else p for p in SC0.plays]
SC = SC0.model_copy(update={"operation": OLD_START, "plays": PLAYS})


def _first_contact_card():
    es = init_engine(SC)
    while not any(r.kind == "target_detected" for r in es.reports):
        es, _ = tick(es, TickInputs())
    return es, next(r for r in es.reports if r.kind == "target_detected")


def test_a_drone_that_opens_its_own_card_leaves_the_open_cards_choices_next_tick():
    es, card = _first_contact_card()
    assert "take_d4" in [c.id for c in card.choices]
    busy = [s.model_copy(update={"pending_report_id": "rep-d4-x"}) if s.id == "d4" else s for s in es.states]
    es, _ = tick(replace(es, states=busy), TickInputs())
    now = next(r for r in es.reports if r.id == card.id)
    ids = [c.id for c in now.choices]
    assert ids[0] == "approach" and "take_d3" in ids and not any(i.endswith("_d4") for i in ids)
```
  (이 테스트는 JSON 복원 전에도 돌게 모델을 복사해 만든 시나리오를 쓴다. Task 4 뒤에는 JSON과 같아진다.)
- [ ] **Step 2: 실패 확인** — `uv run pytest modules/gateway/tests/test_engine_choices.py -n 0 -q` → `take_d4`가 아직 남아 있어 마지막 assert가 실패한다(카드의 선택지가 한 번만 만들어지므로).
- [ ] **Step 3: 구현** — `engine.py`에서 5.2 줄 바로 아래에 추가한다.

```python
    new_reports = [fleet_choices(r, stepped, sc.operation, plays) for r in new_reports]  # 5.2
    reports = [
        fleet_choices(r, stepped, sc.operation, plays)
        if r.kind == "target_detected" and not r.resolved_ms
        else r
        for r in reports
    ]  # 5.3 open cards follow the fleet (decision 0046)
```
  `contracts/API.md` §3 표에 `| 5.3 | runtime | 열려 있는 \`target_detected\` 카드 선택지를 \`fleet_choices\`로 다시 만든다(결정 0046) |`를 5.2 아래에 추가한다(5.2 줄이 있으면 그 아래).
- [ ] **Step 4: 통과 확인** — 같은 명령과 `uv run pytest modules/gateway -q`.
- [ ] **Step 5: 커밋.**

---

### Task 3: 이전 흐름 기준 테스트 복원 (먼저 실패하는 상태가 된다)

현재 main의 시나리오 데이터가 아직 해안 순찰이라서, 이 Task가 끝난 시점에는 이 테스트들이 **실패해야 한다**(RED). Task 4가 데이터를 복원해 통과시킨다.

**Files:** (모두 `88992a3` 이전 모습으로 되돌린다. 그 커밋 이후 건드린 사람이 없는 파일은 통째로, 나머지는 해당 부분만)
- Restore whole file: `tests/test_demo_scenario.py`, `modules/gateway/tests/test_app.py`, `modules/gateway/tests/test_check_saved_play.py`, `modules/play/tests/test_check_operation.py`, `modules/play/tests/test_check_play.py`, `modules/gateway/tests/test_demo_threat.py`
- Restore + keep later additions: `modules/gateway/tests/test_engine.py`, `modules/gateway/tests/test_demo_timeline.py`

- [ ] **Step 1: 통째로 되돌릴 파일**

```bash
git checkout 88992a3^ -- tests/test_demo_scenario.py modules/gateway/tests/test_app.py \
  modules/gateway/tests/test_check_saved_play.py modules/play/tests/test_check_operation.py \
  modules/play/tests/test_check_play.py modules/gateway/tests/test_demo_threat.py
```
  (사전 확인: 이 파일들은 `88992a3` 이후 다른 커밋이 건드리지 않았다. `test_demo_threat.py`의 RF 드론 확인은 `d4: 2000`을 이미 포함한다.)
- [ ] **Step 2: `test_demo_timeline.py`** — 이전 파일을 가져오되 리드가 나중에 더한 `test_fast1_graph…`는 보존한다.

```bash
git show HEAD:modules/gateway/tests/test_demo_timeline.py > /tmp/timeline_now.py
git checkout 88992a3^ -- modules/gateway/tests/test_demo_timeline.py
```
  그다음 파일 맨 끝에 `/tmp/timeline_now.py`의 `test_fast1_graph_shows_the_decision_behind_the_strikes` 함수(이 함수 하나)를 그대로 붙인다. 되돌린 파일은 `range(35 * MIN …)`, `s2` = 결정 `dec-1`이 3대(d1·usv·ugv)를 옮김, `s3` = `vehicle_gap`, 순서 `s1 s2 s3 s5 s6 s4 s7 s8`, 세 보트 카드가 각자 담당 드론에서 뜨는 테스트를 가진다.
- [ ] **Step 3: `test_engine.py`** — 이전 파일로 되돌리고 새 흐름 테스트를 이전 흐름용으로 바꿔 추가한다.

```bash
git checkout 88992a3^ -- modules/gateway/tests/test_engine.py
```
  파일에 추가:

```python
def test_fleet_choice_sends_a_standby_drone_to_watch_with_the_finder():  # decision 0046
    es, _ = _until(init_engine(SC), lambda e: any(r.kind == "target_detected" for r in e.reports))
    rep = next(r for r in es.reports if r.kind == "target_detected")
    ids = [c.id for c in rep.choices]
    assert ids[0] == "approach" and "join_d3_d1" in ids and "keep" not in ids
    dec = Decision(id="dec-1", t_ms=es.t_ms + SC.tick_ms, report_id=rep.id, choice_id="join_d3_d1")
    es, fr = tick(es, TickInputs(decisions=[dec]))
    for _ in range(5):
        es, fr = tick(es, TickInputs())
    by = {v.id: v for v in fr.vehicles}
    assert (by["d3"].play_id, by["d3"].target_id) == ("watch", rep.target_id)
    assert (by["d1"].play_id, by["d1"].step_id) == ("patrol_a", "report")  # still over the boat
```
- [ ] **Step 4: RED 확인** — `uv run pytest tests/test_demo_scenario.py modules/gateway modules/play -n 0 -q`가 이전 흐름 기대(시작 배정, `["d1","d3"]`, 세 보트 카드 등)로 **실패**하는지 본다. 실패 이유가 데이터(`assign`=coast) 때문이어야 한다(코드 오류가 아니라).
- [ ] **Step 5: 커밋하지 않고 Task 4로** (RED 상태로 push하지 않는다. 같은 브랜치에서 Task 4와 한 커밋으로 묶거나 연속 커밋 후 ship한다).

---

### Task 4: 야간 시나리오 데이터 복원 (GREEN)

**Files:**
- Modify: `demo/scenarios/baengnyeong_night.json`, `demo/plays/patrol_a.json`, `demo/plays/patrol_b.json`

- [ ] **Step 1: 데이터 수정** — 서식을 유지하는 방식으로 고친다.

```python
import json
def save(p, d):
    open(p, "w", encoding="utf-8").write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")

p = "demo/scenarios/baengnyeong_night.json"
d = json.load(open(p, encoding="utf-8"))
d["operation"]["assign"].update({"d1": "patrol_a", "d2": "patrol_b"})
d["operation"]["reserve"] = {"d1": ["d3"]}
for play in d["plays"]:
    if play["id"] in ("patrol_a", "patrol_b"):
        for s in play["steps"]:
            if s.get("report"):
                s["report"]["auto_choices"] = True
save(p, d)
for pid in ("patrol_a", "patrol_b"):
    q = f"demo/plays/{pid}.json"
    play = json.load(open(q, encoding="utf-8"))
    for s in play["steps"]:
        if s.get("report"):
            s["report"]["auto_choices"] = True
    save(q, play)
```
- [ ] **Step 2: diff 확인** — `git diff --stat demo/`가 세 파일만, 시나리오는 `assign` 두 줄, `reserve`, `auto_choices` 줄만 바뀌었는지 본다(그 밖의 서식 변화가 없어야 한다).
- [ ] **Step 3: 예시 재생성** — `uv run python scripts/gen_examples.py`. 예시가 바뀌면 함께 커밋하고 `tests/test_contracts.py`가 통과하는지 확인한다.
- [ ] **Step 4: GREEN 확인** — `uv run pytest tests/test_demo_scenario.py modules/gateway modules/play modules/runtime -n 0 -q`. Task 3에서 RED였던 테스트가 모두 통과해야 한다. 시연 타임라인(`test_demo_timeline`)에서 카드 시각이 달라져 실패하면 **멈추고 알린다**(설계 7절의 위험).
- [ ] **Step 5: 커밋.**

---

### Task 5: 전체 검증, 기록, ship

- [ ] **Step 1: 전체 검증**(각각 실제 출력을 읽는다) — `uv run pytest`, `uv run python scripts/smoke.py`, `scripts/check.sh --all`, cop-ui는 **수정 없이** `npx tsc -b`, `npx vitest run`, `npx oxlint`가 통과해야 한다(`git diff --stat`에 `modules/cop-ui`가 없는지도 확인).
- [ ] **Step 2: 실제 서버 확인** — UI 빌드 후 서버를 띄우고 점프로 16:35에 카드 두 장(d1 boat1: `approach`+덧붙인 선택지, d2 boat2: `handoff`+덧붙인 선택지), 17:05에 boat2 0.72를 WebSocket Frame으로 확인한다. 선택지에 `take_d3`, `join_d3_d1`이 있고 `keep`이 없는지 본다.
- [ ] **Step 3: 기록** — `demo/BUILT_HERE.md`에 한 줄(결정 0046, 이전 흐름 복원과 이어받기·함께 감시 덧붙이기), `modules/runtime/SPEC.md` RT-11 설명을 "정해진 선택지 뒤에 덧붙이고 자기 카드가 열린 드론은 제외"로 갱신, 설계 문서 상태를 "구현됨"으로 고친다.
- [ ] **Step 4: ship** — `scripts/ship.sh`. rebase 충돌이 `BUILT_HERE.md`뿐이면 양쪽 줄을 모두 살린다.
- [ ] **Step 5: 알림** — 황승주에게: `fleet_choices` 덧붙이기·열린 카드 제외, 야간 시나리오 `assign` 복원, `test_demo_timeline`·`test_engine` 등 되돌린 테스트 목록. 리드에게: 카드 시각이 `runStops.ts`·QA 기대값과 일치하는지(UI는 수정하지 않았다).

---

## Self-Review

- 스펙 커버: 시작 흐름 복원(Task 3·4), 덧붙이기(Task 1), 열린 카드 드론 제외(Task 1), 매 틱 다시 만들기(Task 2), 후보는 대기 드론만(기존 규칙, Task 1에서 변경 없음), 로직만·UI 제외(Global Constraints, Task 5 Step 1), 검증·기록(Task 5).
- 타입 일관성: `fleet_choices(rep, states, op, plays) -> Report`는 서명이 그대로다. Task 2의 호출은 Task 1의 같은 함수를 쓴다.
- 위험: Task 4 Step 4에서 시연 시각이 달라지면 멈춘다. 사전 확인(임시 JSON으로 실제 틱 루프 실행)에서는 boat1 16:30.2, boat2 16:32.8, boat3 18:33.2로 이전과 같았다.
