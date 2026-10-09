"""Generate JSON Schema files and TypeScript types from the contracts/models/ package."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contracts.models import ALL_MODELS  # noqa: E402

HEADER = "// 자동 생성 파일 (scripts/gen_contracts.py). 직접 수정하지 마세요.\n"
SCALARS = {"string": "string", "number": "number", "integer": "number", "boolean": "boolean"}


def _ts_type(prop: dict) -> str:
    if "$ref" in prop:
        return prop["$ref"].split("/")[-1]
    if "enum" in prop:  # inline Literal
        return " | ".join(json.dumps(v) for v in prop["enum"])
    if "const" in prop:
        return json.dumps(prop["const"])
    if prop.get("type") == "array":
        item = _ts_type(prop["items"])
        return f"({item})[]" if " | " in item else f"{item}[]"
    if "anyOf" in prop:
        return " | ".join(_ts_type(p) if p.get("type") != "null" else "null" for p in prop["anyOf"])
    if prop.get("type") == "object":
        extra = prop.get("additionalProperties", True)
        return f"Record<string, {_ts_type(extra) if isinstance(extra, dict) else 'unknown'}>"
    return SCALARS.get(prop.get("type"), "unknown")


def _emit(name: str, schema: dict, out: dict[str, str]) -> None:
    if "enum" in schema:
        out[name] = (
            f"export type {name} = " + " | ".join(json.dumps(v) for v in schema["enum"]) + ";"
        )
        return
    required = set(schema.get("required", []))
    lines = [f"export interface {name} {{"]
    for key, prop in schema.get("properties", {}).items():
        opt = "" if key in required else "?"
        lines.append(f"  {key}{opt}: {_ts_type(prop)};")
    out[name] = "\n".join(lines + ["}"])


def to_typescript(models: dict) -> str:
    blocks: dict[str, str] = {}
    for model in models.values():
        schema = model.model_json_schema()
        for name, sub in schema.get("$defs", {}).items():
            _emit(name, sub, blocks)
        _emit(schema["title"], schema, blocks)
    return HEADER + "\n\n".join(blocks[k] for k in blocks) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    root = Path(ap.parse_args(argv).root)
    out = root / "contracts" / "schema"
    out.mkdir(parents=True, exist_ok=True)
    for name, model in ALL_MODELS.items():
        (out / f"{name}.json").write_text(
            json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    ts = root / "modules" / "cop-ui" / "src" / "contracts.gen.ts"
    ts.parent.mkdir(parents=True, exist_ok=True)
    ts.write_text(to_typescript(ALL_MODELS), encoding="utf-8")


if __name__ == "__main__":
    main()
