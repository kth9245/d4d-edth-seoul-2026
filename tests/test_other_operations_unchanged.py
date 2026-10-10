"""Decision NNNN guard: night and 24h run exactly as before the infrared/acoustic sensors.

Every frame of a fixed run is hashed with the keys the sensors add taken out, so the hash was recorded on the code
before the sensors existed. The new keys themselves must stay off (False / 0) in these operations.
"""

import hashlib
import json

import pytest

from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

NEW_KEYS = {"heat", "noise", "ir_detected", "sound_detected", "ir_range_m", "acoustic_range_m"}
# 9000 ticks = 30 minutes: targets exist from 3300, are seen from about 4900, night hears its first RF at 5100
BASELINE = {  # path -> (ticks, sha256 recorded before the sensors)
    "demo/scenarios/baengnyeong_night.json": (
        9000,
        "7eceb6325179429109cb333cfa81d721761dbef2ee78705b6805a3dec77d5cbe",
    ),
    "demo/scenarios/baengnyeong_24h.json": (
        9000,
        "2c1d27c497917167f99e7808748d678edba298567e85a2ca021881a25afeef67",
    ),
}


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in NEW_KEYS}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def run(path: str, ticks: int):
    es, h, new_keys_on = init_engine(load_scenario_json(path)), hashlib.sha256(), []
    for _ in range(ticks):
        es, frame = tick(es, TickInputs())
        dump = frame.model_dump(mode="json")
        h.update(json.dumps(strip(dump), sort_keys=True, ensure_ascii=False).encode("utf-8"))
        new_keys_on += [
            t["id"]
            for t in dump["targets"]
            if t.get("heat") or t.get("noise") or t.get("ir_detected") or t.get("sound_detected")
        ]
    return h.hexdigest(), new_keys_on


@pytest.mark.parametrize("path", list(BASELINE))
def test_every_frame_is_what_it_was_before_the_sensors(path):
    ticks, want = BASELINE[path]
    got, _ = run(path, ticks)
    assert got == want


@pytest.mark.parametrize("path", list(BASELINE))
def test_the_sensor_fields_stay_off_and_no_vehicle_has_a_sensor_range(path):
    _, on = run(path, 9000)
    assert on == []
    sc = load_scenario_json(path)
    assert all(
        getattr(v, "ir_range_m", 0) == 0 and getattr(v, "acoustic_range_m", 0) == 0
        for v in sc.vehicles
    )
