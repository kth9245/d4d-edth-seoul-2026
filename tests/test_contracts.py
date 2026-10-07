import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts.models import ALL_MODELS, Detection

EXAMPLES = Path(__file__).resolve().parent.parent / "contracts" / "examples"


@pytest.mark.parametrize("name", sorted(ALL_MODELS))
def test_example_matches_model(name):
    data = json.loads((EXAMPLES / f"{name}.json").read_text(encoding="utf-8"))
    ALL_MODELS[name].model_validate(data)


def test_strength_out_of_range_rejected():
    with pytest.raises(ValidationError):
        Detection(id="d", sensor="radar", t_ms=0, lat=37.0, lon=127.0, alt_m=10, strength=1.5)


def test_unknown_sensor_rejected():
    with pytest.raises(ValidationError):
        Detection(id="d", sensor="sonar", t_ms=0, lat=37.0, lon=127.0, alt_m=10, strength=0.5)
