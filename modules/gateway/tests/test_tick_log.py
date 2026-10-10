from contracts.models import (
    Block,
    Command,
    Decision,
    DirectControl,
    GeoPoint,
    Injection,
    Operation,
    PassedCommand,
    Polygon,
    Provenance,
    Report,
    Scenario,
    ScenarioEvent,
    TickInputs,
)
from modules.gateway.actions.tick_log import tick_log

START = 1_791_633_600_000  # 2026-10-10 21:00:00 KST
G = GeoPoint(lat=37, lon=126)
ZONE = Polygon(points=[G, GeoPoint(lat=37, lon=126.1), GeoPoint(lat=37.1, lon=126.1)])
SC = Scenario(id="s", vehicles=[], roles=[],
              operation=Operation(id="op1", name="op", area=ZONE, zone=ZONE, vehicle_ids=[],
                                  started_ms=START),
              events=[ScenarioEvent(offset_ms=660_000, kind="spawn_target", params={"id": "boat1"})])  # fmt: skip
T = START + 660_000  # 21:11:00


def test_scenario_event_line_only_in_its_tick():
    assert tick_log(SC, T, 200, TickInputs(), []) == ["[대본] 21:11:00 spawn_target boat1"]
    assert tick_log(SC, T + 200, 200, TickInputs(), []) == []


def test_decision_line():
    inp = TickInputs(decisions=[Decision(id="dec-1", t_ms=T, report_id="r1", choice_id="approach")])
    assert "[계산] 21:11:00 결정 dec-1 → approach" in tick_log(SC, T, 200, inp, [])


def test_injection_line():
    inj = Injection(id="inj-1", t_ms=T, label="x", role_by_vehicle={}, status="approved")
    assert "[계산] 21:11:00 전환 inj-1 approved" in tick_log(
        SC, T, 200, TickInputs(injections=[inj]), []
    )


def test_direct_control_line():
    inp = TickInputs(direct=[DirectControl(id="dir-1", vehicle_id="d2", target=G, t_ms=T)])
    assert "[계산] 21:11:00 직접 조종 dir-1 d2" in tick_log(SC, T, 200, inp, [])


def test_block_line():
    blk = Block(command_id="c", vehicle_id="d2", reason="outside_zone", detail="x", t_ms=T)
    assert "[계산] 21:11:00 차단 d2 outside_zone" in tick_log(SC, T, 200, TickInputs(), [blk])


def test_strike_pass_and_neutralized_lines():
    prov = Provenance(source="role_step", issued_ms=T, decision_id="dec-3")
    cmd = Command(id="c1", vehicle_id="d2", kind="strike", params={"target_id": "fast1"},
                  provenance=prov)  # fmt: skip
    hit = Report(id="r", t_ms=T, kind="target_neutralized", vehicle_id="d2", target_id="fast1",
                 text="fast1 무력화(d2)")  # fmt: skip
    lines = tick_log(SC, T + 200, 200, TickInputs(), [],
                     [PassedCommand(command=cmd, checks=[], passed_ms=T)], [hit])  # fmt: skip
    assert lines == [
        "[계산] 21:11:00 타격 명령 통과: d2 → fast1, 운용자 결정 dec-3 확인",
        "[계산] 21:11:00 fast1 무력화(d2)",
    ]


def test_enemy_appearance_is_a_script_line():
    from contracts.models import EnemySpec

    sc = SC.model_copy(update={"events": [], "enemies": [
        EnemySpec(id="boat1", kind="boat", speed_mps=1, appear_offset_ms=660_000, pos=G,
                  role_id="p")]})  # fmt: skip
    assert tick_log(sc, T, 200, TickInputs(), []) == ["[대본] 21:11:00 적 등장 boat1"]
