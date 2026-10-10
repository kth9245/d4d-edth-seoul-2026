"""Strike operation "해안 거점 무력화" (virtual): demo/scenarios/baengnyeong_strike.json.

Three fixed enemy sites on the north coast are unknown-kind targets with speed 0, a hold Role and an emission
start (no contract change, spec 8절). site_a emits from the start and is the first one the north search patrol
meets, so its RF shows before the drone sees it. The JSON is the source afterwards (decision 0035);
rerun only to rebuild. Usage: uv run python scripts/make_strike_scenario.py
"""

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT)]

from contracts.models import Scenario  # noqa: E402

NIGHT = ROOT / "demo" / "scenarios" / "baengnyeong_night.json"
DAY = ROOT / "demo" / "scenarios" / "baengnyeong_24h.json"
OUT = ROOT / "demo" / "scenarios" / "baengnyeong_strike.json"
# (id, lat, lon, emit_start_offset_ms); virtual positions on the island's north coast, inside the zone
SITES = [
    ("site_a", 37.98230, 124.72247, 0),
    ("site_b", 37.96382, 124.74617, None),
    ("site_c", 37.97272, 124.64615, None),
]
# spawn_enemies needs t - dt < start + offset <= t: an offset of 0 would never spawn the enemy
APPEAR_MS = 1000


def site_hold() -> dict:
    step = {
        "id": "hold",
        "name": "대기",
        "do": {"kind": "hold", "params": {}},
        "on": [],
        "report": None,
        "ui": {},
    }
    return {"id": "site_hold", "name": "적: 거점 대기", "domains": ["ground"], "steps": [step],
            "entry": "hold", "origin": "human", "approved": True, "template": False,
            "emergency": {"battery_low_pct": 30.0, "link_lost_step": None, "battery_low_step": None,
                          "operator_call_step": None}}  # fmt: skip


def build() -> dict:
    night = json.loads(NIGHT.read_text(encoding="utf-8"))
    day = json.loads(DAY.read_text(encoding="utf-8"))
    roles = {r["id"]: r for r in night["roles"]}
    patrol = copy.deepcopy(next(r for r in day["roles"] if r["id"] == "coast_a"))
    patrol["id"], patrol["name"] = "site_patrol", "거점 탐색 순찰 · 북"
    patrol["steps"][1]["report"] = {"text": "미식별 거점 감지", "choices": [], "auto_choices": True}
    north = next(r for r in day["routes"] if r["id"] == "coast_a")
    skip = ("patrol_a", "patrol_b", "coast_a", "coast_b")
    op = night["operation"] | {
        "id": "op_strike",
        "name": "해안 거점 무력화(가상)",
        "purpose": "정찰 드론이 가상 해안 거점을 RF 방출로 먼저 찾고 스캔해서 식별한다. 식별된 거점에만 타격 승인을 연다(2단계)",
        "assign": {"d1": "site_patrol", "d2": "standby", "d3": "standby", "d4": "standby",
                   "usv": "standby", "ugv": "standby"},
        "reserve": {}, "switches": [], "rotation": [], "rotation_pools": {}, "rotation_roles": [],
    }  # fmt: skip
    enemies = [
        {"id": i, "kind": "unknown", "speed_mps": 0.0, "appear_offset_ms": APPEAR_MS,
         "pos": {"lat": lat, "lon": lon, "alt_m": 0.0}, "from_enemy": None, "role_id": "site_hold",
         "emit_start_offset_ms": emit}
        for i, lat, lon, emit in SITES
    ]  # fmt: skip
    out = night | {
        "id": "baengnyeong_strike",
        "operation": op,
        "roles": [patrol, roles["standby"], roles["go_home"], roles["watch"], roles["approach"],
                  roles["strike"], site_hold()],
        "events": [],
        "enemies": enemies,
        "routes": [north, *(r for r in night["routes"] if r["id"] not in skip)],
        # same place and radius as night's "상륙 예상 지점" (so the scores below hold), but here it is the
        # target area the sites are measured against, not a place to guard
        "watch_points": [{**night["watch_points"][0], "id": "target_area", "name": "목표 지역 중심"}],
    }  # fmt: skip
    Scenario.model_validate(out)
    return out


def main() -> None:
    out = build()
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(
        f"{OUT.name}: {len(out['enemies'])} sites, {len(out['roles'])} roles, {len(out['routes'])} routes"
    )


if __name__ == "__main__":
    main()
