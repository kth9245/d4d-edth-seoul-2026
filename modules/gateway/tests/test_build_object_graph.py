from dataclasses import replace

import pytest

from contracts.models import (
    Block,
    Choice,
    Command,
    Decision,
    GeoPoint,
    PassedCommand,
    Provenance,
    Report,
    Target,
)
from modules.gateway.actions.build_object_graph import build_object_graph
from modules.gateway.engine import init_engine
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_night.json")
P = GeoPoint(lat=37.98, lon=124.70)
CHECKS = ["no_provenance", "outside_zone", "battery_insufficient"]


def _cmd(cid, vid, kind, target=None, dec=None):
    prov = Provenance(source="play_step", decision_id=dec, issued_ms=2000)
    params = {"target_id": target} if target else {}
    return Command(id=cid, vehicle_id=vid, kind=kind, params=params, provenance=prov)


def _target(tid, kind, **kw):
    return Target(id=tid, kind=kind, pos=P, vel_east_mps=0, vel_north_mps=0,
                  first_seen_ms=1000, last_seen_ms=3000, **kw)  # fmt: skip


def _world():
    choice = Choice(
        id="strike_both", label="함께 타격", play_by_vehicle={"d2": "strike", "usv": "strike"}
    )
    rep = Report(id="rep-d2-1", t_ms=1500, kind="target_detected", vehicle_id="d2",
                 target_id="fast1", text="고속정 발견", choices=[choice])  # fmt: skip
    dec = Decision(id="dec-4", t_ms=1800, report_id="rep-d2-1", choice_id="strike_both")
    cmds = [
        _cmd("cmd-d2-1", "d2", "strike", "fast1", "dec-4"),
        _cmd("cmd-usv-1", "usv", "strike", "fast1", "dec-4"),
        _cmd("cmd-d1-1", "d1", "orbit", "boat1", "dec-1"),
        _cmd("cmd-d2-0", "d2", "follow_route"),
        _cmd("cmd-d2-9", "d2", "move"),
    ]
    passed = [PassedCommand(command=c, checks=CHECKS, passed_ms=2000) for c in cmds[:4]]
    blk = Block(command_id="cmd-d2-9", vehicle_id="d2", reason="outside_zone",
                detail="작전 구역 밖", t_ms=2500)  # fmt: skip
    targets = [_target("fast1", "fast_boat", neutralized_ms=3000), _target("boat1", "boat")]
    return replace(init_engine(SC), targets=targets, reports=[rep], decisions=[dec],
                   commands=cmds, passed=passed, blocks=[blk])  # fmt: skip


def test_from_the_struck_target_to_the_decision_and_the_strikers():
    g = build_object_graph(_world(), "fast1")
    assert {n.id for n in g.nodes} == {
        "fast1", "rep-d2-1", "d2", "dec-4", "cmd-d2-1", "cmd-usv-1", "usv",
    }  # fmt: skip
    rels = {(lk.src, lk.rel, lk.dst) for lk in g.links}
    assert {
        ("dec-4", "answers", "rep-d2-1"),
        ("cmd-d2-1", "from_decision", "dec-4"),
        ("cmd-d2-1", "aims_at", "fast1"),
        ("d2", "reported", "rep-d2-1"),
    } <= rels
    label = {n.id: n.label for n in g.nodes}
    assert label["d2"] == "d2 · 무장 드론" and label["fast1"] == "fast1 · 고속정 · 무력화"
    assert label["dec-4"] == "dec-4 '함께 타격'"
    assert label["cmd-d2-1"] == "strike · d2 · 출처·구역·배터리 통과"


def test_a_block_hangs_on_its_command():
    g = build_object_graph(_world(), "blk-cmd-d2-9")
    assert {n.id for n in g.nodes} == {"blk-cmd-d2-9", "cmd-d2-9", "d2"}
    assert next(n for n in g.nodes if n.id == "cmd-d2-9").label == "move · d2 · 차단"


def test_unknown_focus_raises():
    with pytest.raises(ValueError):
        build_object_graph(_world(), "nope")
