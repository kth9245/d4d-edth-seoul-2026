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
from modules.sim.actions.update_emission import update_emission

START = 1_791_633_600_000
G = GeoPoint(lat=37.985, lon=124.70)
ZONE = Polygon(points=[G, GeoPoint(lat=37.9, lon=124.7), GeoPoint(lat=37.9, lon=124.8)])
ROLE = Role(id="p", name="p", domains=["sea"], entry="go", approved=True,
            steps=[Step(id="go", name="go", do=Action(kind="hold"))])  # fmt: skip


def enemy(eid: str, appear: int, emit: int | None) -> EnemySpec:
    return EnemySpec(id=eid, kind="boat", speed_mps=1, appear_offset_ms=appear, pos=G,
                     role_id="p", emit_start_offset_ms=emit)  # fmt: skip


SC = Scenario(id="s", vehicles=[], roles=[ROLE],
              operation=Operation(id="op", name="op", area=ZONE, zone=ZONE, vehicle_ids=[],
                                  started_ms=START),
              enemies=[enemy("silent", 1000, None), enemy("now", 1000, 0), enemy("late", 1000, 60_000)])  # fmt: skip


def targets() -> list[Target]:
    return [Target(id=i, kind="boat", pos=G, vel_east_mps=0, vel_north_mps=0,
                   first_seen_ms=0, last_seen_ms=0) for i in ("silent", "now", "late")]  # fmt: skip


def emitting(t_ms: int) -> dict[str, bool]:
    return {t.id: t.emitting for t in update_emission(SC, targets(), START + t_ms)}


def test_nothing_emits_before_it_appears():
    assert emitting(999) == {"silent": False, "now": False, "late": False}


def test_offset_zero_emits_from_appearance_and_none_never_does():
    assert emitting(1000) == {"silent": False, "now": True, "late": False}
    assert emitting(10_000_000)["silent"] is False


def test_late_emitter_starts_exactly_at_its_offset_and_keeps_emitting():
    assert emitting(60_999)["late"] is False
    assert emitting(61_000)["late"] is True
    assert emitting(120_000)["late"] is True
