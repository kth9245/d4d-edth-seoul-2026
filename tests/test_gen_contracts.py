import importlib.util
import json
from pathlib import Path

from contracts.models import ALL_MODELS

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("gen", ROOT / "scripts/gen_contracts.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


def test_typescript_output():
    ts = gen.to_typescript(ALL_MODELS)
    assert 'export type SensorType = "rf" | "eoir" | "radar";' in ts
    assert "export interface Detection {" in ts
    assert "  strength: number;" in ts
    assert "  sensor: SensorType;" in ts
    assert "  tracks: Track[];" in ts
    assert "  vel_east_mps?: number;" in ts
    assert ts.count("export interface Track {") == 1


def test_cli_writes_files(tmp_path):
    (tmp_path / "modules/cop-ui/src").mkdir(parents=True)
    gen.main(["--root", str(tmp_path)])
    schema = json.loads((tmp_path / "contracts/schema/frame.json").read_text())
    assert schema["title"] == "Frame"
    assert (tmp_path / "modules/cop-ui/src/contracts.gen.ts").read_text().startswith("// 자동 생성")


def test_typescript_dicts_and_literals():
    ts = gen.to_typescript(ALL_MODELS)
    assert "  role_by_vehicle?: Record<string, string>;" in ts
    assert '  origin?: "human" | "ai_draft";' in ts
    assert "  params?: Record<string, unknown>;" in ts
    assert "export interface LegacyFrame {" in ts
