from contracts.models import (
    Action,
    Choice,
    GeoPoint,
    Report,
    Role,
    Step,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.gateway.actions.refresh_strike_cards import refresh_strike_cards

HOME = GeoPoint(lat=37.978, lon=124.70)
SITE = GeoPoint(lat=37.982, lon=124.722)
STRIKE = Role(id="strike", name="표적 타격", domains=["air", "sea"], entry="strike",
              steps=[Step(id="strike", name="타격", do=Action(kind="strike_target", params={}))])  # fmt: skip
ROLES = {"strike": STRIKE}
SPECS = {
    "d2": VehicleSpec(id="d2", name="d2", domain="air", speed_mps=15, endurance_min=50,
                      sensor_range_m=800, capabilities=["strike_target"], home=HOME),
    "d3": VehicleSpec(id="d3", name="d3", domain="air", speed_mps=15, endurance_min=50,
                      sensor_range_m=800, capabilities=["watch_target"], home=HOME),
}  # fmt: skip


def vs(vid, **kw):
    return VehicleState(id=vid, t_ms=0, pos=HOME, heading_deg=0, battery_pct=100,
                        status=kw.pop("status", "ready"), **kw)  # fmt: skip


def card(**kw):
    base = dict(id="rep-d1-1", t_ms=1, kind="target_detected", vehicle_id="d1", target_id="site_a",
                text="미식별 거점 감지 · d1 센서 탐지 · site_a(미상) · 721 m",
                choices=[Choice(id="keep", label="전 기체 현 임무 유지")])  # fmt: skip
    return Report(**(base | kw))


def site(**kw):
    base = dict(id="site_a", kind="unknown", pos=SITE, vel_east_mps=0, vel_north_mps=0,
                first_seen_ms=1, last_seen_ms=1, ident_state="identified", ident_confidence=80,
                ident_reasons=["rf_emission", "scan", "multi_observer"])  # fmt: skip
    return Target(**(base | kw))


def run(rep, tg, states=None):
    states = states or [vs("d2"), vs("d3")]
    return refresh_strike_cards([rep], states, SPECS, [tg], ROLES)[0]


def test_an_identified_site_opens_a_strike_choice_for_each_armed_vehicle():
    out = run(card(), site())
    ids = [c.id for c in out.choices]
    assert ids == ["keep", "strike_d2"]  # d3 cannot strike
    c = out.choices[1]
    assert (c.role_by_vehicle, c.target_by_vehicle) == ({"d2": "strike"}, {"d2": "site_a"})
    assert "식별: 식별됨 0.80" in out.text and "RF 방출" in out.text


def test_two_armed_vehicles_also_get_a_strike_all_choice():
    spec = VehicleSpec.model_validate(
        {**SPECS["d3"].model_dump(), "capabilities": ["strike_target"]}
    )
    specs = {**SPECS, "d3": spec}
    out = refresh_strike_cards([card()], [vs("d2"), vs("d3")], specs, [site()], ROLES)[0]
    assert [c.id for c in out.choices] == ["keep", "strike_d2", "strike_d3", "strike_all"]
    assert out.choices[-1].role_by_vehicle == {"d2": "strike", "d3": "strike"}


def test_before_identification_there_is_no_strike_choice_but_the_clue_line_shows():
    out = run(card(), site(ident_state="identifying", ident_confidence=65,
                           ident_reasons=["rf_emission", "scan"]))  # fmt: skip
    assert [c.id for c in out.choices] == ["keep"]
    assert "식별: 식별 중 0.65" in out.text


def test_losing_the_site_takes_the_strike_choice_away_again():
    first = run(card(), site())
    assert "strike_d2" in [c.id for c in first.choices]
    lost = run(first, site(ident_state="identifying", ident_confidence=35,
                           ident_reasons=["rf_emission"]))  # fmt: skip
    assert [c.id for c in lost.choices] == ["keep"]
    assert lost.text.count("식별:") == 1  # the line is replaced, not stacked


def test_answered_cards_and_neutralized_sites_are_left_alone():
    answered = card(resolved_ms=5, decision_id="dec-1")
    assert run(answered, site()) == answered
    dead = site(neutralized_ms=9)
    assert run(card(), dead) == card()


def test_other_kinds_are_left_alone():
    boat = site(kind="boat")
    assert run(card(), boat) == card()


def test_no_available_striker_leaves_only_keep():
    busy = [vs("d2", pending_report_id="rep-x"), vs("d3")]
    out = run(card(), site(), states=busy)
    assert [c.id for c in out.choices] == ["keep"]


def test_the_identification_line_names_the_heat_and_noise_clues_in_korean():  # decision 0071
    tg = site(ident_reasons=["ir_signature", "sound", "scan", "sustained"], ident_confidence=70)
    out = run(card(), tg)
    assert "열 신호" in out.text and "소음" in out.text
    assert "ir_signature" not in out.text and "sound" not in out.text  # no raw codes on the card
