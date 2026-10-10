from contracts.models import Condition, Exit, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_night.json")


def test_the_engine_gives_step_vehicle_the_operation_start():  # decision 0045
    pid = SC.operation.assign["d1"]
    role = next(p for p in SC.roles if p.id == pid)
    entry = next(s for s in role.steps if s.id == role.entry)
    other = next(s.id for s in role.steps if s.id != role.entry)
    at_1s = Exit(cond=Condition(kind="at_time", params={"offset_ms": 1000}), go_step=other)
    timed = entry.model_copy(update={"on": [at_1s, *entry.on]})
    role = role.model_copy(update={"steps": [timed if s.id == entry.id else s for s in role.steps]})
    sc = SC.model_copy(update={"roles": [role if p.id == pid else p for p in SC.roles]})
    es = init_engine(sc)
    steps = []
    for _ in range(10):  # 10 ticks of 200 ms = 2 s
        es, _ = tick(es, TickInputs())
        steps.append(next(v.step_id for v in es.states if v.id == "d1"))
    assert steps[2] == role.entry  # 600 ms
    assert steps[-1] == other
