from contracts.models import VehicleStatus
from modules.gateway.actions.init_engine import init_engine
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_night.json")
START = SC.operation.started_ms


def test_vehicles_start_at_home_ready_at_operation_start():
    es = init_engine(SC)
    homes = {v.id: v.home for v in SC.vehicles}
    assert {s.id for s in es.states} == set(homes)
    for s in es.states:
        assert (s.pos.lat, s.pos.lon) == (homes[s.id].lat, homes[s.id].lon)
        assert s.status == VehicleStatus.ready
        assert s.t_ms == START
    assert es.t_ms == START


def test_role_id_from_operation_assign_and_step_is_role_entry():
    es = init_engine(SC)
    entry = {p.id: p.entry for p in SC.roles}
    for s in es.states:
        assert s.role_id == SC.operation.assign[s.id]
        assert s.step_id == entry[s.role_id]
        assert s.entered_step is False


def test_every_vehicle_gets_an_operation_assignment():
    es = init_engine(SC)
    got = {(a.vehicle_id, a.role_id, a.since_ms, a.reason) for a in es.assignments}
    assert got == {(v, p, START, "작전 배정") for v, p in SC.operation.assign.items()}


def test_lookups_by_id_and_empty_logs():
    es = init_engine(SC)
    assert set(es.specs) == {v.id for v in SC.vehicles}
    assert set(es.roles) == {p.id for p in SC.roles}
    assert es.scenario is SC
    assert (es.targets, es.reports, es.blocks, es.injections) == ([], [], [], [])
