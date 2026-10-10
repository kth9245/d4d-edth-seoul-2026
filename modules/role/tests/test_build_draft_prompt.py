import re

from contracts.models import (
    ActionKind,
    ConditionKind,
    Domain,
    GeoPoint,
    Operation,
    Polygon,
    Switch,
)
from modules.role.actions.build_draft_prompt import build_draft_prompt

TEXT = "드론으로 북쪽 해안을 순찰하다가 고속정을 발견하면 바로 접근해."


def box(lat: float, lon: float, d: float) -> Polygon:
    pts = [(lat, lon), (lat, lon + d), (lat + d, lon + d), (lat + d, lon)]
    return Polygon(points=[GeoPoint(lat=a, lon=b) for a, b in pts])


OP = Operation(
    id="op1",
    name="야간 해안 경계",
    purpose="섬 해안 경계(가상)",
    area=box(37.9, 124.56, 0.3),
    zone=box(37.91, 124.57, 0.2),
    vehicle_ids=["d1", "usv"],
    started_ms=1791633600000,
    assign={"d1": "patrol_a"},
)


def test_same_input_gives_same_prompt():
    assert build_draft_prompt(TEXT, OP) == build_draft_prompt(TEXT, OP)


def test_prompt_has_text_vocabulary_operation_and_output_keys():
    p = build_draft_prompt(TEXT, OP)
    assert TEXT in p and OP.name in p and OP.purpose in p
    # at_time (decision 0045) is set by the operator in the editor, and target_neutralized (decision 0058)
    # by the scenario's strike operation, so the AI draft vocabulary leaves both out.
    not_drafted = (ConditionKind.at_time, ConditionKind.target_neutralized)
    for kind in [*ActionKind, *(k for k in ConditionKind if k not in not_drafted), *Domain]:
        assert kind.value in p
    for kind in not_drafted:
        assert kind.value not in p
    assert "124.56" in p and "124.57" in p  # area and zone corners
    for key in ["situation", "domain_reasoning", "step_plan", "not_in_text", "role"]:
        assert f'"{key}"' in p


def test_prompt_spells_out_the_report_shape():  # eval 10/10: replies used "message", dropped choice ids
    p = build_draft_prompt(TEXT, OP)
    assert '{"text": ' in p and '"choices": [{"id": ' in p and '"choices": []' in p


def test_run_fields_do_not_change_prompt():  # the same request reads the same prompt during a live run
    other = OP.model_copy(
        update={
            "id": "op2",
            "vehicle_ids": ["d2"],
            "started_ms": 1,
            "assign": {"d2": "watch"},
            "reserve": {"d2": ["d1"]},
            "switches": [Switch(id="s", label="s", role_by_vehicle={"d1": "watch"})],
        }
    )
    assert build_draft_prompt(TEXT, other) == build_draft_prompt(TEXT, OP)


def test_zone_and_text_change_prompt():
    moved = OP.model_copy(update={"zone": box(37.92, 124.6, 0.1)})
    assert build_draft_prompt(TEXT, moved) != build_draft_prompt(TEXT, OP)
    assert build_draft_prompt(TEXT + " 귀환해.", OP) != build_draft_prompt(TEXT, OP)


def test_no_placeholder_left():
    assert not re.findall(r"\{[a-z_]+\}", build_draft_prompt(TEXT, OP))
