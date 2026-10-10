"""SIM-09 apply_events: 이번 틱에 걸린 사건 대본을 적용하고 표적을 속도대로 움직인다
사건 시각 = operation.started_ms + offset_ms (결정 0018). params 키는 09 문서 2.2 ScenarioEvent.
SPEC: modules/sim/SPEC.md#SIM-09
"""

from contracts.models import GeoPoint, Scenario, Target, TargetKind, VehicleState, VehicleStatus
from shared.geo import offset_latlon


def _event(kind: str, p: dict, states: list, targets: list) -> tuple[list, list]:
    if kind == "spawn_target":
        new = Target(id=p["id"], kind=p["kind"], pos=GeoPoint(**p["pos"]),
                     vel_east_mps=p.get("ve", 0), vel_north_mps=p.get("vn", 0),
                     first_seen_ms=0, last_seen_ms=0)  # fmt: skip
        return states, [*targets, new]
    if kind == "split_target":
        src = next(t for t in targets if t.id == p["id"])
        upd = {"id": p["new_id"], "kind": TargetKind(p.get("kind", src.kind)), "seen_by": [],
               "vel_east_mps": p["ve"], "vel_north_mps": p["vn"], "first_seen_ms": 0}  # fmt: skip
        return states, [*targets, src.model_copy(update=upd)]
    if kind == "target_move":
        vel = {"vel_east_mps": p["ve"], "vel_north_mps": p["vn"]}
        return states, [t.model_copy(update=vel) if t.id == p["id"] else t for t in targets]
    if kind == "vehicle_battery_set":
        upd = {"battery_pct": float(p["pct"])}
    else:  # vehicle_link_lost
        upd = {"status": VehicleStatus.lost}
    return [s.model_copy(update=upd) if s.id == p["id"] else s for s in states], targets


def apply_events(
    scenario: Scenario, states: list[VehicleState], targets: list[Target], t_ms: int, dt_ms: int
) -> tuple[list[VehicleState], list[Target]]:
    start = scenario.operation.started_ms
    for ev in scenario.events:
        if t_ms - dt_ms < start + ev.offset_ms <= t_ms:
            states, targets = _event(ev.kind, ev.params, states, targets)
    dt = dt_ms / 1000
    moved = []
    for t in targets:
        lat, lon = offset_latlon(t.pos.lat, t.pos.lon, t.vel_east_mps * dt, t.vel_north_mps * dt)
        moved.append(t.model_copy(update={"pos": GeoPoint(lat=lat, lon=lon, alt_m=t.pos.alt_m)}))
    return states, moved
