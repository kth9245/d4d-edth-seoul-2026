import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _script():
    spec = importlib.util.spec_from_file_location(
        "make_coast_routes", ROOT / "scripts/make_coast_routes.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_rerunning_the_24h_script_keeps_the_route_list_and_route_names():  # decision 0044
    out = _script().build()
    committed = json.loads((ROOT / "demo/scenarios/baengnyeong_24h.json").read_text("utf-8"))
    assert out["routes"] == committed["routes"]
    names = [
        s["do"]["params"].get("route_name")
        for p in out["roles"]
        for s in p["steps"]
        if s["do"]["kind"] == "patrol_route" and not p["id"].startswith("enemy")
    ]
    assert names == [
        "해안 A(북)",
        "해안 B(남)",
        "발견 지점 집중 순찰(800 m)",
    ]  # + raid focus (0055)


def test_the_24h_scenario_takes_the_night_ontology_with_every_drone_armed():  # decision 0051, user 10/10
    night = json.loads((ROOT / "demo/scenarios/baengnyeong_night.json").read_text("utf-8"))
    out = _script().build()
    kinds = json.loads(json.dumps(night["ontology"]))  # decision 0055: 24h ground robots also track
    next(k for k in kinds["kinds"] if k["id"] == "ground_robot")["provides"].append("watch_target")
    assert out["ontology"] == kinds
    drones = [v for v in out["vehicles"] if v["domain"] == "air"]
    assert [v["id"] for v in drones] == ["d1", "d2", "d3", "d4"]
    assert all(v["kind"] == "armed_drone" and "capabilities" not in v for v in drones)
    committed = json.loads((ROOT / "demo/scenarios/baengnyeong_24h.json").read_text("utf-8"))
    assert committed["ontology"] == out["ontology"]
    assert committed["vehicles"] == out["vehicles"]


def test_the_24h_drones_take_off_and_land_on_a_600_m_square():  # user, 10/10: visible at the start zoom; d1 NW, d2 NE, d3 SW, d4 SE
    from contracts.models import GeoPoint
    from shared.geo import dist_m

    committed = json.loads((ROOT / "demo/scenarios/baengnyeong_24h.json").read_text("utf-8"))
    assert committed["vehicles"] == _script().build()["vehicles"]
    h = {v["id"]: GeoPoint(**v["home"]) for v in committed["vehicles"]}
    for a, b in (("d1", "d2"), ("d3", "d4"), ("d1", "d3"), ("d2", "d4")):
        assert abs(dist_m(h[a], h[b]) - 600) < 1, (a, b)
    assert abs(dist_m(h["d1"], h["d4"]) - 600 * 2**0.5) < 1
    assert h["d1"].lat > h["d3"].lat and h["d2"].lon > h["d1"].lon


def test_the_24h_operation_takes_the_night_strike_role_and_all_home_switch():  # user, 10/10
    night = json.loads((ROOT / "demo/scenarios/baengnyeong_night.json").read_text("utf-8"))
    strike = next(r for r in night["roles"] if r["id"] == "strike")
    all_home = next(s for s in night["operation"]["switches"] if s["id"] == "all_home")
    out = _script().build()
    assert strike in out["roles"]
    assert out["operation"]["switches"][0] == all_home
    committed = json.loads((ROOT / "demo/scenarios/baengnyeong_24h.json").read_text("utf-8"))
    assert committed["roles"] == out["roles"]
    assert committed["operation"]["switches"] == out["operation"]["switches"]


def test_the_24h_operation_is_named_for_its_mission():  # Part1-15.2, lead 10/11
    out = _script().build()
    committed = json.loads((ROOT / "demo/scenarios/baengnyeong_24h.json").read_text("utf-8"))
    assert out["operation"]["name"] == committed["operation"]["name"] == "24시간 침투 대응"
