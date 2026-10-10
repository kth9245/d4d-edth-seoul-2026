import pytest

from contracts.models import (
    Action,
    Condition,
    EnemySpec,
    Exit,
    GeoPoint,
    Play,
    Polygon,
    Step,
    Target,
)
from modules.sim.actions.steer_enemies import steer_enemies
from shared.geo import dist_m, offset_latlon
from shared.land import inside

HOME = GeoPoint(lat=37.98, lon=124.70)
T = 1_000_000


def _at(east_m: float = 0, north_m: float = 0) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


DEST = _at(east_m=1000)
PLAY = Play(id="enemy_fast1", name="f", domains=["sea"], entry="run", approved=True, steps=[
    Step(id="run", name="run", do=Action(kind="move_to", params={"target": DEST.model_dump()}),
         on=[Exit(cond=Condition(kind="arrived"), go_step="wait")]),
    Step(id="wait", name="wait", do=Action(kind="hold"),
         on=[Exit(cond=Condition(kind="time_elapsed", params={"sec": 60}), go_step="run")]),
])  # fmt: skip
ENEMIES = [EnemySpec(id="fast1", kind="fast_boat", speed_mps=5, appear_offset_ms=0,
                     pos=HOME, play_id="enemy_fast1")]  # fmt: skip


def _fast1(pos: GeoPoint = HOME, step: str = "run", **kw) -> Target:
    return Target(id="fast1", kind="fast_boat", pos=pos, vel_east_mps=0, vel_north_mps=0,
                  first_seen_ms=0, last_seen_ms=0, play_id="enemy_fast1", step_id=step,
                  step_since_ms=T - 200, **kw)  # fmt: skip


def steer(tg: Target, t_ms: int = T) -> Target:
    (out,) = steer_enemies(ENEMIES, {PLAY.id: PLAY}, [tg], t_ms, 200)
    return out


def test_move_to_sets_speed_toward_the_destination():
    out = steer(_fast1())
    assert out.vel_east_mps == pytest.approx(5, abs=0.01)
    assert out.vel_north_mps == pytest.approx(0, abs=0.01)


def test_arrival_snaps_to_destination_and_stops():
    out = steer(_fast1(pos=_at(east_m=999.5)))
    assert (out.pos, out.vel_east_mps, out.vel_north_mps, out.waypoint_idx) == (DEST, 0, 0, -1)


def test_arrived_exit_moves_to_the_next_step():
    out = steer(_fast1(pos=DEST, waypoint_idx=-1))
    assert (out.step_id, out.waypoint_idx, out.step_since_ms) == ("wait", 0, T)
    assert (out.vel_east_mps, out.vel_north_mps) == (0, 0)


def test_time_elapsed_exit_waits_for_its_seconds():
    held = _fast1(pos=DEST, step="wait")
    assert steer(held, T + 30_000).step_id == "wait"
    assert steer(held, T - 200 + 60_000).step_id == "run"


def test_neutralized_enemy_stays_still():
    struck = _fast1(neutralized_ms=T - 1000)
    assert steer(struck) == struck


def test_targets_without_a_play_are_left_alone():
    plain = Target(id="boat9", kind="boat", pos=HOME, vel_east_mps=0, vel_north_mps=-1,
                   first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    assert steer_enemies(ENEMIES, {PLAY.id: PLAY}, [plain], T, 200) == [plain]


def test_boats_steer_round_the_island_and_arrive():
    island = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]
    goal = _at(1000, -200)
    play = Play(id="enemy_run", name="r", domains=["sea"], entry="run", approved=True, steps=[
        Step(id="run", name="run", do=Action(kind="move_to", params={"target": goal.model_dump()}))])  # fmt: skip
    enemies = [EnemySpec(id="fast1", kind="fast_boat", speed_mps=10, appear_offset_ms=0,
                         pos=_at(-1000, -200), play_id="enemy_run")]  # fmt: skip
    tg, t = _fast1(_at(-1000, -200)).model_copy(update={"play_id": "enemy_run"}), T
    for _ in range(400):
        (tg,) = steer_enemies(enemies, {"enemy_run": play}, [tg], t, 1000, island)
        if tg.waypoint_idx == -1:
            break
        lat, lon = offset_latlon(tg.pos.lat, tg.pos.lon, tg.vel_east_mps, tg.vel_north_mps)  # 1 s
        tg, t = tg.model_copy(update={"pos": GeoPoint(lat=lat, lon=lon)}), t + 1000
        assert not inside(tg.pos, island)
    assert tg.waypoint_idx == -1 and dist_m(tg.pos, goal) < 1
