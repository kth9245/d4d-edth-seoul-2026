"""SIM-01 load_scenario: 시나리오 YAML을 읽고 잘못된 값을 로딩 시점에 알린다
SPEC: modules/sim/SPEC.md#SIM-01
"""

from pathlib import Path

import yaml
from pydantic import ValidationError

from modules.sim.types import Scenario


def load_scenario(path: str | Path) -> Scenario:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    try:
        return Scenario.model_validate(data)
    except ValidationError as e:
        lines = [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()]
        raise ValueError(f"시나리오 파일 오류 {path.name}:\n" + "\n".join(lines)) from None
