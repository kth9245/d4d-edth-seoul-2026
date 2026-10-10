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
        for p in out["plays"]
        for s in p["steps"]
        if s["do"]["kind"] == "patrol_route"
    ]
    assert names == ["해안 A(북)", "해안 B(남)"]


def test_the_24h_scenario_takes_the_night_ontology_and_drone_kinds():  # decision 0051
    night = json.loads((ROOT / "demo/scenarios/baengnyeong_night.json").read_text("utf-8"))
    kinds = {v["id"]: v["kind"] for v in night["vehicles"]}
    out = _script().build()
    assert out["ontology"] == night["ontology"]
    assert all(v["kind"] == kinds[v["id"]] and "capabilities" not in v for v in out["vehicles"])
    committed = json.loads((ROOT / "demo/scenarios/baengnyeong_24h.json").read_text("utf-8"))
    assert committed["ontology"] == out["ontology"]
    assert committed["vehicles"] == out["vehicles"]


def test_the_24h_drones_take_off_and_land_on_a_2400_m_square():  # user, 10/10: visible at the start zoom; d1 NW, d2 NE, d3 SW, d4 SE
    from contracts.models import GeoPoint
    from shared.geo import dist_m

    committed = json.loads((ROOT / "demo/scenarios/baengnyeong_24h.json").read_text("utf-8"))
    assert committed["vehicles"] == _script().build()["vehicles"]
    h = {v["id"]: GeoPoint(**v["home"]) for v in committed["vehicles"]}
    for a, b in (("d1", "d2"), ("d3", "d4"), ("d1", "d3"), ("d2", "d4")):
        assert abs(dist_m(h[a], h[b]) - 2400) < 1, (a, b)
    assert abs(dist_m(h["d1"], h["d4"]) - 2400 * 2**0.5) < 1
    assert h["d1"].lat > h["d3"].lat and h["d2"].lon > h["d1"].lon
