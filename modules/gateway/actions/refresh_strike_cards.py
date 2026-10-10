"""GW-13 refresh_strike_cards: 열린 unknown 표적 발견 카드에 식별 줄을 붙이고, 식별됨일 때만 타격 승인 선택지를 연다(2단계, 결정 0056)
fleet_choices(5.3)가 매 틱 선택지를 덮어쓰므로 틱 끝에서 다시 붙인다. 타격은 여전히 운용자 승인으로만(결정 0033).
선택지 id: strike_<기체 id>, 둘 이상이면 strike_all. 이미 응답한 카드·무력화된 표적·다른 종류는 그대로.
SPEC: modules/gateway/SPEC.md#GW-13
"""

from contracts.models import Choice, Report, Role, Target, VehicleSpec, VehicleState, VehicleStatus
from shared.geo import dist_m

LIVE = (VehicleStatus.ready, VehicleStatus.active)
STATE_KO = {"undetected": "미탐", "rf_only": "방출원 미확인", "identifying": "식별 중",
            "identified": "식별됨"}  # fmt: skip
REASON_KO = {"rf_emission": "RF 방출", "scan": "스캔 확인", "multi_observer": "2기체 관측",
             "sustained": "관측 지속"}  # fmt: skip
MARK = " · 식별:"


def _line(tg: Target) -> str:
    why = ", ".join(REASON_KO.get(r, r) for r in tg.ident_reasons)
    return f"{MARK} {STATE_KO[tg.ident_state]} {tg.ident_confidence / 100:.2f}" + (
        f" · 이유: {why}" if why else ""
    )


def _strikers(states, specs, roles) -> list[VehicleState]:
    if "strike" not in roles:
        return []
    return [s for s in states if s.status in LIVE and s.pending_report_id is None
            and "strike_target" in [c.value for c in specs[s.id].capabilities]]  # fmt: skip


def refresh_strike_cards(
    reports: list[Report],
    states: list[VehicleState],
    specs: dict[str, VehicleSpec],
    targets: list[Target],
    roles: dict[str, Role],
) -> list[Report]:
    by_id = {t.id: t for t in targets}
    out = []
    for r in reports:
        tg = by_id.get(r.target_id or "")
        if (r.kind != "target_detected" or r.resolved_ms or tg is None
                or tg.kind.value != "unknown" or tg.neutralized_ms is not None):  # fmt: skip
            out.append(r)
            continue
        kept = [c for c in r.choices if not c.id.startswith("strike_")]
        add = []
        if tg.ident_state == "identified":
            armed = _strikers(states, specs, roles)
            add = [Choice(id=f"strike_{s.id}", role_by_vehicle={s.id: "strike"},
                          target_by_vehicle={s.id: tg.id},
                          label=f"{s.id} 타격 승인({tg.id}) · 도달 약 "
                                f"{dist_m(s.pos, tg.pos) / specs[s.id].speed_mps:.0f}초")
                   for s in armed]  # fmt: skip
            if len(armed) > 1:
                add.append(Choice(id="strike_all", label=f"전원 타격 승인({tg.id})",
                                  role_by_vehicle={s.id: "strike" for s in armed},
                                  target_by_vehicle={s.id: tg.id for s in armed}))  # fmt: skip
        text = r.text.split(MARK)[0] + _line(tg)
        out.append(r.model_copy(update={"text": text, "choices": [*kept, *add]}))
    return out
