"""SIM-12 steer_enemies: 적(결정 0032)의 지금 step 행동대로 속도만 정하고 arrived·time_elapsed로 step을 넘긴다
위치는 다음 틱 apply_events가 속도로 옮긴다. 이번 틱 안에 닿으면 위치를 목적지로 맞추고 멈춘다.
행동은 move_to·patrol_route·hold만. runtime·safety를 거치지 않는다. 무력화된 적은 그대로.
배(boat·fast_boat·usv)는 land를 받아 섬을 돌아가고 육지 위 목적지는 해안 바다 점으로 본다(결정 0034).
SPEC: modules/sim/SPEC.md#SIM-12
"""

import math
from collections.abc import Sequence

from contracts.models import ConditionKind, EnemySpec, GeoPoint, Polygon, Role, Step, Target
from modules.sim.actions.sea_aim import sea_aim
from shared.geo import dist_m, enu_delta_m
from shared.land import to_sea

STOP = {"vel_east_mps": 0.0, "vel_north_mps": 0.0}
BOATS = ("boat", "fast_boat", "usv")  # TargetKinds that go round islands (decisions 0034, 0055)


def _dest(step: Step, idx: int) -> GeoPoint | None:
    p = step.do.params
    if step.do.kind.value == "move_to":
        return GeoPoint(**p["target"])
    if step.do.kind.value == "patrol_route":
        return GeoPoint(**p["route"][idx % len(p["route"])])
    return None  # hold


def _next_step(step: Step, tg: Target, t_ms: int) -> str | None:
    waited_ms = t_ms - (tg.step_since_ms or t_ms)
    for ex in step.on:
        if ex.cond.kind == ConditionKind.arrived and tg.waypoint_idx < 0:
            return ex.go_step
        sec = float(ex.cond.params.get("sec", 0))
        if ex.cond.kind == ConditionKind.time_elapsed and waited_ms >= sec * 1000:
            return ex.go_step
    return None


def _steer(tg: Target, step: Step, speed: float, dt_ms: int, land: Sequence[Polygon]) -> Target:
    dest = _dest(step, tg.waypoint_idx) if tg.waypoint_idx >= 0 else None
    if dest is None:
        return tg.model_copy(update=STOP)
    dest = to_sea(dest, land)
    if dist_m(tg.pos, dest) <= speed * dt_ms / 1000:
        idx = -1 if step.do.kind.value == "move_to" else tg.waypoint_idx + 1
        return tg.model_copy(update={**STOP, "pos": dest, "waypoint_idx": idx})
    aim = sea_aim(tg.pos, dest, land)
    east, north = enu_delta_m(tg.pos.lat, tg.pos.lon, aim.lat, aim.lon)
    s = speed / (math.hypot(east, north) or 1.0)
    return tg.model_copy(update={"vel_east_mps": s * east, "vel_north_mps": s * north})


def steer_enemies(
    enemies: list[EnemySpec],
    roles: dict[str, Role],
    targets: list[Target],
    t_ms: int,
    dt_ms: int,
    land: Sequence[Polygon] = (),
) -> list[Target]:
    speed = {e.id: e.speed_mps for e in enemies}
    out = []
    for tg in targets:
        role = roles.get(tg.role_id or "")
        if role is None or tg.neutralized_ms is not None:
            out.append(tg)
            continue
        step = next(s for s in role.steps if s.id == tg.step_id)
        nxt = _next_step(step, tg, t_ms)
        if nxt:
            tg = tg.model_copy(update={"step_id": nxt, "waypoint_idx": 0, "step_since_ms": t_ms})
            step = next(s for s in role.steps if s.id == nxt)
        sea = land if tg.kind in BOATS else ()
        out.append(_steer(tg, step, speed.get(tg.id, 0.0), dt_ms, sea))
    return out
