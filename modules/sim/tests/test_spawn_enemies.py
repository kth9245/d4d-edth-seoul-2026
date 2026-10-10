from contracts.models import (
    Action,
    EnemySpec,
    GeoPoint,
    Operation,
    Polygon,
    Role,
    Scenario,
    Step,
    Target,
)
from modules.sim.actions.spawn_enemies import spawn_enemies

START = 1_791_633_600_000
G = GeoPoint(lat=37.985, lon=124.70)
ZONE = Polygon(points=[G, GeoPoint(lat=37.9, lon=124.7), GeoPoint(lat=37.9, lon=124.8)])
ROLE = Role(id="enemy_boat1", name="b", domains=["sea"], entry="go", approved=True,
            steps=[Step(id="go", name="go", do=Action(kind="hold"))])  # fmt: skip
SC = Scenario(id="s", vehicles=[], roles=[ROLE],
              operation=Operation(id="op1", name="op", area=ZONE, zone=ZONE, vehicle_ids=[],
                                  started_ms=START),
              enemies=[EnemySpec(id="boat1", kind="boat", speed_mps=1, appear_offset_ms=660_000,
                                 pos=G, role_id="enemy_boat1"),
                       EnemySpec(id="fast1", kind="fast_boat", speed_mps=6.3,
                                 appear_offset_ms=1_380_000, from_enemy="boat1",
                                 role_id="enemy_boat1")])  # fmt: skip
T1, T2 = START + 660_000, START + 1_380_000


def test_enemy_appears_only_in_its_tick_with_role_progress():
    assert spawn_enemies(SC, [], T1 - 200, 200) == []
    (tg,) = spawn_enemies(SC, [], T1, 200)
    assert (tg.id, tg.kind.value, tg.pos, tg.vel_east_mps, tg.vel_north_mps) == (
        "boat1", "boat", G, 0, 0,
    )  # fmt: skip
    assert (tg.role_id, tg.step_id, tg.waypoint_idx, tg.step_since_ms) == (
        "enemy_boat1", "go", 0, T1,
    )  # fmt: skip
    assert spawn_enemies(SC, [tg], T1 + 200, 200) == [tg]


def test_from_enemy_appears_at_that_enemys_current_position():
    moved = GeoPoint(lat=37.97, lon=124.70)
    boat1 = Target(id="boat1", kind="boat", pos=moved, vel_east_mps=0, vel_north_mps=-1,
                   first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    out = spawn_enemies(SC, [boat1], T2, 200)
    assert [t.id for t in out] == ["boat1", "fast1"] and out[1].pos == moved


def test_a_spawned_enemy_carries_its_heat_and_noise():  # decision 0071
    def site(i: str, **kw) -> EnemySpec:
        return EnemySpec(id=i, kind="unknown", speed_mps=0, appear_offset_ms=1000, pos=G,
                         role_id="enemy_boat1", **kw)  # fmt: skip

    sc = SC.model_copy(update={"enemies": [site("site_a"), site("site_b", heat=True),
                                           site("site_c", noise=True)]})  # fmt: skip
    out = spawn_enemies(sc, [], START + 1000, 200)
    assert {t.id: (t.heat, t.noise) for t in out} == {
        "site_a": (False, False), "site_b": (True, False), "site_c": (False, True)}  # fmt: skip
