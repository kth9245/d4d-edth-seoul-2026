from contracts.models import Command, GeoPoint, PassedCommand, Target, VehicleState
from modules.sim.actions.resolve_strikes import resolve_strikes
from shared.geo import offset_latlon

HOME = GeoPoint(lat=37.95, lon=124.70)
T = 1_000_000


def _at(north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, 0, north_m)
    return GeoPoint(lat=lat, lon=lon)


def _striker(vid: str, kind: str = "strike", target_id: str = "fast1",
             decision_id: str | None = "dec-3") -> VehicleState:  # fmt: skip
    cmd = Command(id=f"c-{vid}", vehicle_id=vid, kind=kind, params={"target_id": target_id})
    return VehicleState(id=vid, t_ms=T, pos=HOME, heading_deg=0, battery_pct=80, status="active",
                        active=PassedCommand(command=cmd, checks=[], passed_ms=0),
                        decision_id=decision_id)  # fmt: skip


def _fast1(north_m: float, neutralized_ms: int | None = None) -> Target:
    return Target(id="fast1", kind="fast_boat", pos=_at(north_m), vel_east_mps=-2,
                  vel_north_mps=6, first_seen_ms=0, last_seen_ms=0,
                  neutralized_ms=neutralized_ms)  # fmt: skip


def test_within_100_m_neutralizes_and_stops_the_target():
    targets, cards = resolve_strikes([_striker("d2")], [_fast1(60)], T)
    tg = targets[0]
    assert (tg.neutralized_ms, tg.vel_east_mps, tg.vel_north_mps) == (T, 0, 0)
    assert [(c.id, c.kind.value, c.vehicle_id, c.target_id, c.text) for c in cards] == [
        (f"rep-d2-{T}", "target_neutralized", "d2", "fast1", "fast1 무력화(d2)")
    ]
    assert cards[0].choices == []


def test_beyond_100_m_does_nothing():
    targets, cards = resolve_strikes([_striker("d2")], [_fast1(150)], T)
    assert targets[0].neutralized_ms is None and cards == []


def test_already_neutralized_gives_no_card():
    targets, cards = resolve_strikes([_striker("d2")], [_fast1(10, neutralized_ms=T - 200)], T)
    assert targets[0].neutralized_ms == T - 200 and cards == []


def test_other_commands_never_strike():
    targets, cards = resolve_strikes([_striker("d2", kind="keep_distance")], [_fast1(10)], T)
    assert targets[0].neutralized_ms is None and cards == []


def test_two_strikers_in_one_tick_give_one_card():
    targets, cards = resolve_strikes([_striker("d2"), _striker("usv")], [_fast1(10)], T)
    assert targets[0].neutralized_ms == T and [c.vehicle_id for c in cards] == ["d2"]


def test_vehicle_switched_away_without_a_decision_no_longer_strikes():
    # switch_play clears decision_id; a still-active strike command must not neutralize anything
    targets, cards = resolve_strikes([_striker("d2", decision_id=None)], [_fast1(10)], T)
    assert targets[0].neutralized_ms is None and cards == []
