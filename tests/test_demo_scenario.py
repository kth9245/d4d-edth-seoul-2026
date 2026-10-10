import json
from pathlib import Path

from contracts.models import Decision, Frame, GeoPoint, Role, Scenario, TargetKind, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json
from shared.geo import dist_m
from shared.land import inside

ROOT = Path(__file__).resolve().parent.parent
SCENARIO = ROOT / "demo" / "scenarios" / "baengnyeong_night.json"
ROLES = ROOT / "demo" / "roles"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_scenario_validates_and_has_a_start_time():
    sc = Scenario.model_validate(_load(SCENARIO))
    assert sc.operation.started_ms is not None
    assert set(sc.operation.assign.values()) <= {p.id for p in sc.roles}


def test_role_files_match_the_scenario_roles():
    sc = Scenario.model_validate(_load(SCENARIO))
    files = {p.stem: Role.model_validate(_load(p)) for p in ROLES.glob("*.json")}
    assert files == {p.id: p for p in sc.roles}


def test_fast_boat_tracking_lets_the_operator_pick_the_target():
    sc = Scenario.model_validate(_load(SCENARIO))
    track = next(p for p in sc.roles if p.id == "track_fast")
    assert track.steps[0].do.params["target"] == "operator"


def test_strike_approval_scene_follows_a_target_select_card_per_tracker():
    s7 = Frame.model_validate(_load(ROOT / "contracts/examples/frames/s7_strike_approval.json"))
    picks = [r for r in s7.reports if r.kind == "target_select"]
    assert [(p.vehicle_id, p.decision_id) for p in picks] == [("d2", "dec-2"), ("usv", "dec-3")]


def test_vehicle_homes_are_apart_on_the_map():
    # At the default map zoom one pixel is about 22-26 m; marker and label need about 18 px.
    sc = Scenario.model_validate(_load(SCENARIO))
    homes = [(s.id, s.home) for s in sc.vehicles]
    for i, (a, pa) in enumerate(homes):
        for b, pb in homes[i + 1 :]:
            assert dist_m(pa, pb) >= 500, f"{a} and {b} homes are {dist_m(pa, pb):.0f} m apart"


def test_fast_boat_enemy_comes_out_of_boat1():  # decision 0032: enemies, not split_target
    sc = Scenario.model_validate(_load(SCENARIO))
    fast = next(e for e in sc.enemies if e.id == "fast1")
    assert (fast.kind, fast.from_enemy) == ("fast_boat", "boat1")


def test_scenario_has_the_island_traced_from_the_tiles():
    sc = Scenario.model_validate(_load(SCENARIO))
    assert len(sc.land) == 1 and 30 <= len(sc.land[0].points) <= 100
    assert inside(GeoPoint(lat=37.95, lon=124.70), sc.land)  # the drone pads are on the island
    assert not inside(GeoPoint(lat=38.0, lon=124.70), sc.land)  # NLL side is open sea


def test_sea_vehicles_and_boats_start_at_sea():
    sc = Scenario.model_validate(_load(SCENARIO))
    assert [v.id for v in sc.vehicles if v.domain == "sea" and inside(v.home, sc.land)] == []
    assert [e.id for e in sc.enemies if e.pos and inside(e.pos, sc.land)] == []


def test_nothing_at_sea_crosses_the_island():
    # smoke's operator: the first card's first choice ('근접 확인' sends the USV), then run to T+45 min
    sc = load_scenario_json(str(SCENARIO))
    es, card, frame = init_engine(sc), None, None
    sea = {v.id for v in sc.vehicles if v.domain == "sea"}
    boats = (TargetKind.boat, TargetKind.fast_boat)
    while es.t_ms < sc.operation.started_ms + 45 * 60_000:
        inputs = TickInputs()
        if card is None:
            card = next((r for r in es.reports if r.kind == "target_detected" and r.choices), None)
            if card:
                inputs = TickInputs(decisions=[Decision(id="dec-1", t_ms=es.t_ms, report_id=card.id,
                                                        choice_id=card.choices[0].id)])  # fmt: skip
        es, frame = tick(es, inputs)
        wet = [v.id for v in frame.vehicles if v.id in sea and inside(v.pos, sc.land)]
        wet += [t.id for t in frame.targets if t.kind in boats and inside(t.pos, sc.land)]
        assert not wet, (
            f"{wet} on the island at T+{(frame.t_ms - sc.operation.started_ms) // 1000} s"
        )
    assert card is not None
    assert next(v for v in frame.vehicles if v.id == "usv").role_id == "approach"
    assert any(t.id == "fast1" for t in frame.targets)


def test_the_patrol_assignment_rotates_the_three_drones():  # decision 0037; the button is gone (0060)
    from contracts.models import Injection, TickInputs
    from modules.gateway.engine import init_engine, tick
    from modules.role import check_operation

    sc = load_scenario_json(str(SCENARIO))
    assert [s.id for s in sc.operation.switches] == [
        "all_home"
    ]  # track_fast, patrol_all removed (0060)
    roles_by = {"d1": "coast_a", "d2": "coast_b", "d3": "go_home", "d4": "go_home"}
    assert sc.operation.rotation == ["d1", "d2", "d3", "d4"]
    assert sc.operation.rotation_pools == {"coast_a": ["d1", "d3"], "coast_b": ["d2", "d4"]}
    assert sc.operation.rotation_roles == ["coast_a", "coast_b"]
    specs = {v.id: v for v in sc.vehicles}
    assert check_operation(sc.operation, {p.id: p for p in sc.roles}, specs).ok
    es, t = init_engine(sc), sc.operation.started_ms
    inj = Injection(id="inj-1", t_ms=t + sc.tick_ms, label="순찰 배정", role_by_vehicle=roles_by)  # fmt: skip
    es, _ = tick(es, TickInputs(injections=[inj]))
    es, f = tick(es, TickInputs(injections=[inj.model_copy(update={"status": "approved"})]))
    roles = {v.id: v.role_id for v in f.vehicles}
    assert (roles["d1"], roles["d2"], roles["d3"], roles["d4"]) == (
        "coast_a",
        "coast_b",
        "go_home",
        "go_home",
    )
