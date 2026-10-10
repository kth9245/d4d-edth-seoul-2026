"""GW-04 run_checks: 이번 틱 명령 전부를 safety.check_command에 통과시킨다
막히면 command_blocked 카드를 만들고, 막힌 직접 조종이면 그 기체를 apply_direct 전 상태로 되돌린다.
SPEC: modules/gateway/SPEC.md#GW-04
"""

from contracts.models import (
    Block,
    Command,
    Injection,
    Operation,
    PassedCommand,
    Play,
    Report,
    VehicleSpec,
    VehicleState,
)
from modules.safety import check_command


def run_checks(
    cmds: list[Command],
    before_direct: dict[str, VehicleState],
    states: list[VehicleState],
    specs: dict[str, VehicleSpec],
    op: Operation,
    plays: dict[str, Play],
    injections: list[Injection],
    t_ms: int,
) -> tuple[list[VehicleState], list[PassedCommand], list[Block], list[Report]]:
    passed, blocks, cards = [], [], []
    for cmd in cmds:
        st = next(s for s in states if s.id == cmd.vehicle_id).model_copy(update={"t_ms": t_ms})
        res = check_command(cmd, st, specs[cmd.vehicle_id], op, plays, injections)
        if isinstance(res, PassedCommand):
            passed.append(res)
            continue
        blocks.append(res)
        cards.append(Report(id=f"rep-{cmd.vehicle_id}-{t_ms}-b", t_ms=t_ms, kind="command_blocked",
                            vehicle_id=cmd.vehicle_id, text=f"차단 {res.reason.value}: {res.detail}"))  # fmt: skip
        if cmd.id in before_direct:
            states = [before_direct[cmd.id] if s.id == cmd.vehicle_id else s for s in states]
    return states, passed, blocks, cards
