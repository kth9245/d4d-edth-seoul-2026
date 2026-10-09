from pathlib import Path

from tools.check_specs import problems

HDR = (
    "<!-- prefix: TRK -->\n| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |\n"
    "|---|---|---|---|---|---|---|\n"
)


def mod(root: Path, rows: str) -> Path:
    m = root / "modules" / "tracking"
    (m / "actions").mkdir(parents=True)
    (m / "tests").mkdir()
    (m / "__init__.py").write_text("")
    (m / "actions" / "__init__.py").write_text("")
    (m / "SPEC.md").write_text(HDR + rows, encoding="utf-8")
    return m


def test_clean_module_has_no_problems(tmp_path):
    m = mod(tmp_path, "| TRK-01 | predict_tracks | a | b | c | d | 완료 |\n")
    (m / "actions" / "predict_tracks.py").write_text("x = 1\n")
    (m / "tests" / "test_predict_tracks.py").write_text("x = 1\n")
    assert problems(tmp_path) == []


def test_unregistered_action_and_missing_test(tmp_path):
    m = mod(tmp_path, "")
    (m / "actions" / "smooth_tracks.py").write_text("x = 1\n")
    out = problems(tmp_path)
    assert any("SPEC.md에 없는 액션" in p and "smooth_tracks" in p for p in out)
    assert any("테스트 파일" in p and "test_smooth_tracks.py" in p for p in out)


def test_spec_row_without_file_only_ok_when_planned(tmp_path):
    mod(
        tmp_path,
        "| TRK-01 | a_b | . | . | . | . | 예정 |\n| TRK-02 | c_d | . | . | . | . | 완료 |\n",
    )
    out = problems(tmp_path)
    assert len(out) == 1 and "c_d" in out[0]


def test_length_limits(tmp_path):
    m = mod(tmp_path, "| TRK-01 | big_action | a | b | c | d | 완료 |\n")
    (m / "actions" / "big_action.py").write_text("x = 1\n" * 81)
    (m / "tests" / "test_big_action.py").write_text("x = 1\n")
    (m / "pipeline.py").write_text("x = 1\n" * 201)
    out = problems(tmp_path)
    assert any("big_action.py" in p and "80" in p for p in out)
    assert not any("pipeline.py" in p for p in out)  # decision 0023: no limit outside actions


def test_ts_module_without_init_is_not_checked(tmp_path):
    ui = tmp_path / "modules" / "cop-ui" / "src"
    ui.mkdir(parents=True)
    (ui / "App.tsx").write_text("x\n" * 201)
    (tmp_path / "modules" / "cop-ui" / "node_modules" / "z").mkdir(parents=True)
    (tmp_path / "modules" / "cop-ui" / "node_modules" / "z" / "big.ts").write_text("x\n" * 999)
    assert problems(tmp_path) == []


def test_scoped_spec_and_length_checks_only_touched(tmp_path):
    m = mod(tmp_path, "")
    (m / "actions" / "smooth_tracks.py").write_text("x = 1\n")
    other = tmp_path / "modules" / "assess"
    (other / "actions").mkdir(parents=True)
    (other / "__init__.py").write_text("")
    (other / "actions" / "rogue_thing.py").write_text("x = 1\n" * 81)
    (other / "pipeline.py").write_text("x = 1\n" * 201)
    out = problems(tmp_path, ["modules/tracking/actions/smooth_tracks.py"])
    assert out and all("tracking" in p for p in out)
    out = problems(tmp_path, ["modules/assess/pipeline.py"])
    assert not any("pipeline.py" in p for p in out) and not any("81줄" in p for p in out)
    assert any("81줄" in p for p in problems(tmp_path))


def test_duplicate_id_is_reported(tmp_path):
    m = mod(
        tmp_path,
        "| TRK-01 | a_b | . | . | . | . | 완료 |\n| TRK-01 | c_d | . | . | . | . | 완료 |\n",
    )
    for n in ("a_b", "c_d"):
        (m / "actions" / f"{n}.py").write_text("x = 1\n")
        (m / "tests" / f"test_{n}.py").write_text("x = 1\n")
    out = problems(tmp_path)
    assert len(out) == 1 and "TRK-01" in out[0] and "두 번" in out[0]
