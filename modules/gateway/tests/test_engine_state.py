from dataclasses import fields

from modules.gateway.engine_state import EngineState


def test_engine_state_fields_match_contract_section_3():
    names = {f.name for f in fields(EngineState)}
    assert names == {"t_ms", "scenario", "specs", "plays", "states", "targets", "reports",
                     "assignments", "blocks", "injections", "metrics", "run"}  # fmt: skip
