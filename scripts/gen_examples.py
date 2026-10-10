"""Write contracts/examples/*.json (one per model) and contracts/examples/frames/*.json (eight scenes).

All examples come from one world (example_world.py, which reads the demo scenario JSON: decision 0035)
so ids match across files. It never writes demo/: the demo JSON is edited by hand. Legacy T1-3 examples
(detection, track, assessment, response, legacy_frame) are hand-written and left alone.
Usage: uv run python scripts/gen_examples.py [--root DIR]
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

from example_scenes import BLK1, INJ, REP1, T1, T2, at, scenes  # noqa: E402
from example_world import OPERATION, PLAYS, SCENARIO, SPECS, ZONE, gp  # noqa: E402

from contracts.models import (  # noqa: E402
    ALL_MODELS,
    Accepted,
    CapabilityReason,
    DecisionIn,
    DirectControl,
    DirectIn,
    DraftIn,
    EnemySpec,
    ObjectGraph,
    ObjectLink,
    ObjectNode,
    OntologyView,
    PlayCheck,
    RouteDef,
    RouteOffset,
    ScenarioInfo,
    SwitchIn,
    TickInputs,
    TickOutcome,
    ValidationIssue,
    VehicleCapabilities,
    WatchPoint,
)

LEGACY = {"detection", "track", "assessment", "response", "legacy_frame"}


def examples() -> dict[str, object]:
    frames = scenes()
    s1, s2 = frames["s1_report_wait"], frames["s2_after_decision"]
    watch = PLAYS["watch"].steps[0]
    decision = DecisionIn(report_id=REP1.id, choice_id="approach")
    issue = ValidationIssue(
        code="report_missing",
        step_id="approach",
        message="표적 발견 뒤 선택지 있는 보고 없이 접근 step에 닿습니다",
    )
    direct = DirectControl(
        id="dir-1", vehicle_id="d2", target=BLK1.alternative.params["target"], t_ms=at(20, 5)
    )
    inputs = TickInputs(decisions=[{"id": "dec-1", "t_ms": T2, **decision.model_dump()}])
    outcome = TickOutcome(
        inputs=inputs,
        commands=[v.active.command for v in s2.vehicles if v.active and v.active.passed_ms == T2],
        passed=[v.active for v in s2.vehicles if v.active and v.active.passed_ms == T2],
        assignments=s2.assignments,
        states=s2.vehicles,
        targets=s2.targets,
        plays=PLAYS,
    )
    onto = SCENARIO.ontology  # decision 0038
    reason = CapabilityReason(action="strike_target", allowed=False,
                              path=["recon_drone", "air_vehicle", "vehicle"])  # fmt: skip
    caps = VehicleCapabilities(vehicle_id="d1", kind="recon_drone", reasons=[reason])
    dec_node = ObjectNode(
        id="dec-1", type="decision", label=f"dec-1 '{REP1.choices[0].label}'", t_ms=T2
    )
    answers = ObjectLink(src="dec-1", dst=REP1.id, rel="answers")
    graph = ObjectGraph(focus=REP1.target_id, nodes=[
        ObjectNode(id=REP1.target_id, type="target", label=f"{REP1.target_id} · 보트"),
        ObjectNode(id=REP1.id, type="report", label=REP1.text, t_ms=REP1.t_ms), dec_node,
    ], links=[ObjectLink(src=REP1.id, dst=REP1.target_id, rel="about"), answers])  # fmt: skip
    return {
        "action_group": onto.groups[0],
        "vehicle_kind": onto.kinds[3],
        "ontology": onto,
        "capability_reason": reason,
        "vehicle_capabilities": caps,
        "ontology_view": OntologyView(ontology=onto, vehicles=[caps]),
        "object_node": dec_node,
        "object_link": answers,
        "object_graph": graph,
        "geo_point": SPECS["d1"].home,
        "polygon": ZONE,
        "vehicle_spec": SPECS["d1"],
        "vehicle_state": s2.vehicles[0],
        "operation": OPERATION,
        "enemy_spec": EnemySpec(
            id="boat1",
            kind="boat",
            speed_mps=1.0,
            appear_offset_ms=660_000,
            pos=gp(37.985, 124.70),
            play_id="enemy_boat1",
        ),  # fmt: skip
        "watch_point": WatchPoint(
            id="landing", name="상륙 예상 지점", pos=gp(37.978, 124.70), radius_m=2000
        ),
        "condition": watch.on[0].cond,
        "action": watch.do,
        "exit": watch.on[0],
        "choice": REP1.choices[0],
        "switch": OPERATION.switches[0],
        "report_spec": PLAYS["patrol_a"].steps[1].report,
        "step": watch,
        "emergency_rules": PLAYS["watch"].emergency,
        "play": PLAYS["patrol_a"],
        "validation_issue": issue,
        "play_check": PlayCheck(ok=False, issues=[issue], est_return_battery={"d1": 41.0}),
        "provenance": s2.vehicles[0].active.command.provenance,
        "command": s2.vehicles[0].active.command,
        "passed_command": s2.vehicles[0].active,
        "block": BLK1,
        "target": s1.targets[0],
        "report": REP1,
        "decision": inputs.decisions[0],
        "assignment": s2.assignments[0],
        "injection": INJ,
        "direct_control": direct,
        "metrics": s2.metrics,
        "run_state": s1.run,
        "frame": s1,
        "scenario_event": SCENARIO.events[0],
        "scenario": SCENARIO,
        "tick_inputs": inputs,
        "tick_outcome": outcome,
        "decision_in": decision,
        "direct_in": DirectIn(vehicle_id="d2", target=direct.target),
        "switch_in": SwitchIn(play_by_vehicle={"d2": "track_fast"}),
        "draft_in": DraftIn(text="고속 보트가 나타나면 가장 가까운 드론이 300m 거리에서 추적"),
        "accepted": Accepted(id="dec-1", t_ms=T1),
        "scenario_info": ScenarioInfo(
            id=SCENARIO.id, name=OPERATION.name, purpose=OPERATION.purpose, active=True
        ),
        "route_offset": RouteOffset(north_m=300, east_m=0),
        "route_def": RouteDef(
            id="square_300",
            name="사각형 수색 300m",
            offsets=[
                RouteOffset(north_m=300, east_m=0),
                RouteOffset(north_m=300, east_m=300),
                RouteOffset(north_m=0, east_m=300),
                RouteOffset(north_m=0, east_m=0),
            ],
        ),
    }


def _write(path: Path, model) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=1) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    root = Path(ap.parse_args(argv).root)
    out = root / "contracts" / "examples"
    ex = examples()
    missing = set(ALL_MODELS) - LEGACY - set(ex)
    if missing:
        raise SystemExit(f"[gen_examples] no example for: {sorted(missing)}")
    for name, value in ex.items():
        _write(out / f"{name}.json", ALL_MODELS[name].model_validate(value))
    for name, frame in scenes().items():
        _write(out / "frames" / f"{name}.json", frame)
    print(f"[gen_examples] {len(ex)} models + {len(scenes())} scenes -> {out}")


if __name__ == "__main__":
    main()
