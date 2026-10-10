"""SIM-10 resolve_strikes: 타격 중(active가 strike) 기체가 그 표적 100 m 안이면 표적을 무력화한다(결정 0033)
무력화 = neutralized_ms 기록 + 속도 0(다음 틱부터 apply_events가 움직이지 않음). 결과 카드는 알림만, 표적당 한 장.
SPEC: modules/sim/SPEC.md#SIM-10
"""

from contracts.models import CommandKind, Report, Target, VehicleState
from shared.geo import dist_m

STRIKE_RANGE_M = 100.0


def resolve_strikes(
    states: list[VehicleState], targets: list[Target], t_ms: int
) -> tuple[list[Target], list[Report]]:
    by_id = {t.id: t for t in targets}
    cards: list[Report] = []
    for st in states:
        cmd = st.active.command if st.active else None
        if cmd is None or cmd.kind != CommandKind.strike:
            continue
        tg = by_id.get(cmd.params.get("target_id"))
        if tg is None or tg.neutralized_ms is not None or dist_m(st.pos, tg.pos) > STRIKE_RANGE_M:
            continue
        by_id[tg.id] = tg.model_copy(
            update={"neutralized_ms": t_ms, "vel_east_mps": 0.0, "vel_north_mps": 0.0}
        )
        cards.append(Report(id=f"rep-{st.id}-{t_ms}", t_ms=t_ms, kind="target_neutralized",
                            vehicle_id=st.id, target_id=tg.id, text=f"{tg.id} 무력화({st.id})"))  # fmt: skip
    return [by_id[t.id] for t in targets], cards
