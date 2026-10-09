"""Baengnyeong night coast-watch world for contracts/examples (decisions 0004, 0015, 0016, 0018).

Values come from the spike (knowledge/spikes/rolecall_engine_proto/engine_proto.py), regrouped into
one-vehicle plays and one operation. gen_examples.py and the demo scenario build on this module.
"""

from contracts.models import (
    Action,
    ActionKind,
    Choice,
    Condition,
    Exit,
    GeoPoint,
    Operation,
    Play,
    Polygon,
    ReportSpec,
    Scenario,
    ScenarioEvent,
    Step,
    Switch,
    VehicleSpec,
)

START_MS = 1791633600000  # 2026-10-10 21:00 KST
MIN = 60_000


def gp(lat: float, lon: float) -> GeoPoint:
    return GeoPoint(lat=lat, lon=lon)


ZONE = Polygon(points=[gp(37.90, 124.56), gp(37.90, 124.84), gp(38.00, 124.84), gp(38.00, 124.56)])
HOME = gp(37.95, 124.70)
ROUTE_A = [gp(37.98, 124.66), gp(37.98, 124.74)]
ROUTE_B = [gp(37.93, 124.60), gp(37.93, 124.80)]
LANDING = gp(37.975, 124.70)
BOAT1_SPAWN = gp(37.985, 124.70)


def _spec(vid, name, domain, speed, endurance, sensor, home=HOME):
    return VehicleSpec(
        id=vid, name=name, domain=domain, speed_mps=speed, endurance_min=endurance,
        sensor_range_m=sensor, capabilities=list(ActionKind), home=home,
    )  # fmt: skip


SPECS = {
    s.id: s
    for s in [
        _spec("d1", "드론1", "air", 15, 40, 800),
        _spec("d2", "드론2", "air", 15, 40, 800),
        _spec("d3", "드론3", "air", 15, 40, 800),
        _spec("usv", "수상정", "sea", 8, 720, 500, gp(37.94, 124.71)),
        _spec("ugv", "지상로봇", "ground", 5, 480, 300, gp(37.955, 124.72)),
    ]
}


def _play(pid, name, domains, steps, template=True):
    return Play(
        id=pid, name=name, domains=domains, steps=steps, entry=steps[0].id,
        approved=True, template=template,
    )  # fmt: skip


def _route(points):
    return [p.model_dump() for p in points]


APPROACH = Choice(
    id="approach",
    label="근접 확인",
    play_by_vehicle={"d1": "watch", "usv": "approach", "ugv": "landing", "d2": "patrol_b"},
)
PLAYS = {
    p.id: p
    for p in [
        _play("standby", "대기", ["air", "sea", "ground"], [
            Step(id="wait", name="대기", do=Action(kind="hold")),
        ]),
        _play("patrol_a", "해안 순찰 A", ["air"], [
            Step(id="patrol", name="경로 A 순찰",
                 do=Action(kind="patrol_route", params={"route": _route(ROUTE_A)}),
                 on=[Exit(cond=Condition(kind="target_found"), go_step="report")]),
            Step(id="report", name="보고", do=Action(kind="hold"),
                 report=ReportSpec(text="미식별 선박 접근", choices=[APPROACH])),
        ], template=False),
        _play("watch", "표적 감시", ["air"], [
            Step(id="watch", name="선회 감시",
                 do=Action(kind="watch_target", params={"target": "nearest", "distance_m": 150}),
                 on=[Exit(cond=Condition(kind="battery_below", params={"pct": 30}), go_step="return")]),
            Step(id="return", name="귀환", do=Action(kind="return_home")),
        ]),
        _play("approach", "근접 확인", ["sea"], [
            Step(id="approach", name="접근",
                 do=Action(kind="approach_target", params={"target": "nearest", "distance_m": 200})),
        ]),
        _play("landing", "상륙 지점 감시", ["ground"], [
            Step(id="move", name="상륙 예상 지점",
                 do=Action(kind="move_to", params={"target": LANDING.model_dump()})),
        ], template=False),
        _play("patrol_b", "해안 순찰 B", ["air"], [
            Step(id="patrol", name="경로 B 순찰",
                 do=Action(kind="patrol_route", params={"route": _route(ROUTE_B)})),
        ], template=False),
        _play("track_fast", "고속 보트 추적", ["air"], [
            Step(id="track", name="추적",
                 do=Action(kind="watch_target", params={"target": "operator", "distance_m": 300})),
        ]),
        _play("go_home", "귀환", ["air", "sea", "ground"], [
            Step(id="return", name="귀환", do=Action(kind="return_home")),
        ]),
    ]
}  # fmt: skip

OPERATION = Operation(
    id="op1",
    name="백령도 야간 해안 경계",
    purpose="서해 접경 섬 야간 해안 경계(가상)",
    area=ZONE,
    zone=ZONE,
    vehicle_ids=list(SPECS),
    started_ms=START_MS,
    assign={"d1": "patrol_a", "d2": "standby", "d3": "standby", "usv": "standby", "ugv": "standby"},
    reserve={"d1": ["d3"]},
    switches=[
        Switch(id="all_home", label="전 기체 귀환", play_by_vehicle={v: "go_home" for v in SPECS})
    ],
)

EVENTS = [
    ScenarioEvent(
        offset_ms=11 * MIN,
        kind="spawn_target",
        params={
            "id": "boat1",
            "kind": "boat",
            "pos": BOAT1_SPAWN.model_dump(),
            "ve": 0,
            "vn": -1.0,
        },
    ),
    ScenarioEvent(offset_ms=19 * MIN, kind="vehicle_battery_set", params={"id": "d1", "pct": 21}),
    ScenarioEvent(
        offset_ms=23 * MIN,
        kind="split_target",
        params={"id": "boat1", "new_id": "fast1", "ve": -2.0, "vn": 6.0},
    ),
]

SCENARIO = Scenario(
    id="baengnyeong_night",
    operation=OPERATION,
    vehicles=list(SPECS.values()),
    plays=list(PLAYS.values()),
    events=EVENTS,
    seed=7,
)
