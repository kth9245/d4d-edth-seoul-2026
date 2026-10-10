from dataclasses import fields

from modules.gateway.engine_state import EngineState


def test_engine_state_fields_match_contract_section_3():
    names = {f.name for f in fields(EngineState)}
    assert names == {"t_ms", "scenario", "specs", "roles", "states", "targets", "reports",
                     "assignments", "blocks", "injections", "metrics", "run",
                     "decisions", "commands", "passed"}  # history for GET /graph (0038)  # fmt: skip
