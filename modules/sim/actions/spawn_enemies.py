"""SIM-11 spawn_enemies: 적(결정 0032)이 started_ms + appear_offset_ms 틱에 Target으로 나타난다
위치는 pos, 또는 from_enemy 적의 지금 위치. 진행 상태는 그 Role의 entry step에서 시작.
SPEC: modules/sim/SPEC.md#SIM-11
"""

from contracts.models import Scenario, Target


def spawn_enemies(scenario: Scenario, targets: list[Target], t_ms: int, dt_ms: int) -> list[Target]:
    start = scenario.operation.started_ms
    entry = {p.id: p.entry for p in scenario.roles}
    out = list(targets)
    for e in scenario.enemies:
        if not t_ms - dt_ms < start + e.appear_offset_ms <= t_ms:
            continue
        src = next((t for t in out if t.id == e.from_enemy), None)
        if (
            src and src.neutralized_ms is not None
        ):  # nobody comes off a neutralized enemy (user 10/11)
            continue
        out.append(Target(id=e.id, kind=e.kind, pos=src.pos if src else e.pos,
                          vel_east_mps=0, vel_north_mps=0, first_seen_ms=0, last_seen_ms=0,
                          heat=e.heat, noise=e.noise,  # decision 0071: what it gives off
                          role_id=e.role_id, step_id=entry[e.role_id], step_since_ms=t_ms))  # fmt: skip
    return out
