"""Baengnyeong night coast-watch world for contracts/examples (decisions 0004, 0015, 0016, 0018, 0035).

The demo scenario JSON is the source (decision 0035): this module reads
demo/scenarios/baengnyeong_night.json so the examples and the demo share one world. Change numbers and
plays in that JSON (and demo/plays/), not here; gen_examples.py writes contracts/examples only.
"""

from pathlib import Path

from contracts.models import GeoPoint, Scenario
from modules.ontology import fill_vehicle_kinds

DEMO = Path(__file__).resolve().parent.parent / "demo" / "scenarios" / "baengnyeong_night.json"
# Raw, so the scenario example equals the demo JSON; SPECS are filled as the loader does (decision 0038).
SCENARIO = Scenario.model_validate_json(DEMO.read_text(encoding="utf-8"))
OPERATION = SCENARIO.operation
ZONE = OPERATION.zone
START_MS = OPERATION.started_ms  # 2026-10-10 21:00 KST
MIN = 60_000
SPECS = {v.id: v for v in fill_vehicle_kinds(SCENARIO).vehicles}
PLAYS = {p.id: p for p in SCENARIO.plays}
LANDING = GeoPoint(**PLAYS["landing"].steps[0].do.params["target"])


def gp(lat: float, lon: float) -> GeoPoint:
    return GeoPoint(lat=lat, lon=lon)
