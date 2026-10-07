from tools.spec import SpecRow, append_row, next_id, parse_spec, spec_actions

SPEC = """<!-- prefix: TRK -->
# tracking SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| TRK-01 | predict_tracks | list[Track], t_ms | list[Track] | 등속 예측 | 철수 | 완료 |
| TRK-02 | associate_detections | tracks, dets | dict | 최근접 | 철수 | 진행중 |
"""


def test_parse_spec_reads_prefix_and_rows():
    prefix, rows = parse_spec(SPEC)
    assert prefix == "TRK"
    assert [r.action for r in rows] == ["predict_tracks", "associate_detections"]
    assert rows[1].status == "진행중"


def test_next_id_increments_max():
    _, rows = parse_spec(SPEC)
    assert next_id("TRK", rows) == "TRK-03"
    assert next_id("TRK", []) == "TRK-01"


def test_append_row_and_spec_actions(tmp_path):
    p = tmp_path / "SPEC.md"
    p.write_text(SPEC, encoding="utf-8")
    append_row(p, SpecRow("TRK-03", "update_tracks", "a", "b", "c", "영희", "진행중"))
    assert spec_actions(p) == {"predict_tracks", "associate_detections", "update_tracks"}
    assert p.read_text(encoding="utf-8").endswith("| 영희 | 진행중 |\n")


def test_pipe_in_cell_is_escaped(tmp_path):
    p = tmp_path / "SPEC.md"
    p.write_text(SPEC, encoding="utf-8")
    append_row(p, SpecRow("TRK-03", "x_y", "a|b", "o", "d", "o", "예정"))
    _, rows = parse_spec(p.read_text(encoding="utf-8"))
    assert rows[-1].inputs == "a/b"


def test_spec_actions_missing_file(tmp_path):
    assert spec_actions(tmp_path / "nope.md") == set()
