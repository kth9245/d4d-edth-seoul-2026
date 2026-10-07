from pathlib import Path

from tools.check_imports import problems


def write(root: Path, rel: str, code: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(code)


def test_public_api_imports_ok(tmp_path):
    write(
        tmp_path,
        "modules/gateway/pipeline.py",
        "from modules.tracking import update\nfrom modules import sim\nimport contracts.models\n"
        "from shared.geo import distance_m\nfrom modules.gateway.actions.x import x\n",
    )
    assert problems(tmp_path) == []


def test_reaching_into_other_module_internals_blocked(tmp_path):
    write(tmp_path, "modules/gateway/pipeline.py", "from modules.tracking.actions.a import a\n")
    write(tmp_path, "modules/assess/x.py", "import modules.tracking.pipeline\n")
    out = problems(tmp_path)
    assert len(out) == 2 and all("modules.tracking" in p for p in out)


def test_knowledge_import_blocked_and_shared_cannot_import_modules(tmp_path):
    write(tmp_path, "modules/sim/x.py", "from knowledge.spikes.t import y\n")
    write(tmp_path, "shared/geo2.py", "from modules.sim import x\n")
    write(tmp_path, "contracts/m.py", "import modules\n")
    assert len(problems(tmp_path)) == 3


def test_relative_imports_inside_module_ok(tmp_path):
    write(tmp_path, "modules/sim/pipeline.py", "from .actions.a import a\n")
    assert problems(tmp_path) == []


def test_scoped_paths_only_check_given_files(tmp_path):
    write(tmp_path, "modules/gateway/pipeline.py", "from modules.tracking.actions.a import a\n")
    write(tmp_path, "modules/assess/ok.py", "x = 1\n")
    assert problems(tmp_path, ["modules/assess/ok.py"]) == []
    assert len(problems(tmp_path, ["modules/gateway/pipeline.py"])) == 1
    assert len(problems(tmp_path)) == 1
