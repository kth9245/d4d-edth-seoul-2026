import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ignored(rel: str) -> bool:
    return subprocess.run(["git", "check-ignore", "-q", rel], cwd=ROOT).returncode == 0


def test_env_example_committable_but_secrets_ignored():
    assert not ignored(".env.example")
    assert ignored(".env") and ignored(".env.local")


def test_tiles_file_is_bundled_not_ignored():
    assert not ignored("modules/cop-ui/public/tiles/seoul.pmtiles")
