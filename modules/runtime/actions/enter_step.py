"""RT-08 enter_step: step에 들어갈 때 한 번 — 표적을 정하고 do를 명령 하나로, report가 있으면 카드 한 장
표적(watch_target·approach_target의 params.target): "nearest" | "operator"(카드로 운용자가 고름) | 고정 id.
move_to의 params.target은 목적지 좌표라 손대지 않는다. 귀환 step이면 status=returning.
카드 문구 뒤에 근거(누가 보았나·어느 표적·거리)를 붙인다(에이전트 투명성 SAT 2단계, Mercado 2016).
SPEC: modules/runtime/SPEC.md#RT-08
"""

from contracts.models import (
    Choice,
    Command,
    Provenance,
    Report,
    Role,
    Step,
    Target,
    VehicleSpec,
    VehicleState,
    VehicleStatus,
)
from modules.runtime.actions.route_command import route_command
from shared.geo import dist_m

TARGET_ACTIONS = ("watch_target", "approach_target", "strike_target")
KIND_KO = {"boat": "보트", "fast_boat": "고속정", "person": "사람", "unknown": "미상"}


def _target(st: VehicleState, step: Step, targets: list[Target]) -> tuple[str | None, bool]:
    want = step.do.params.get("target")
    if want == "operator":
        return st.target_id, st.target_id is None
    if want == "nearest":  # decision 0036: a boat nobody reported yet comes first
        new = [t for t in targets if t.reported_by is None]
        best = min(new or targets, key=lambda t: dist_m(st.pos, t.pos), default=None)
        return (best.id if best else None), False
    return want, False


def _basis(st: VehicleState, targets: list[Target], tid: str | None) -> str:
    tg = next((t for t in targets if t.id == tid), None)
    if tg is None:
        return ""
    who = "센서 탐지" if st.id in tg.seen_by else "추적 중"
    kind = KIND_KO.get(tg.kind.value, tg.kind.value)
    return f" · {st.id} {who} · {tg.id}({kind}) · {dist_m(st.pos, tg.pos):.0f} m"


def enter_step(
    st: VehicleState, spec: VehicleSpec, role: Role, step: Step, targets: list[Target], t_ms: int
) -> tuple[VehicleState, Command | None, Report | None]:
    upd: dict = {"entered_step": True, "waypoint_idx": 0}
    params, rid = dict(step.do.params), f"rep-{st.id}-{t_ms}"
    if step.do.kind.value in TARGET_ACTIONS:
        tid, ask = _target(st, step, targets)
        upd["target_id"] = tid
        if ask:  # card only; apply_decision sets target_id and re-enters this step
            picks = [Choice(id=t.id, label=f"{t.id} {t.kind.value}") for t in targets]
            rep = Report(id=rid, t_ms=t_ms, kind="target_select", vehicle_id=st.id,
                         text=f"추적할 표적 선택({st.id})", choices=picks)  # fmt: skip
            return st.model_copy(update={**upd, "pending_report_id": rid}), None, rep
        params = {k: v for k, v in params.items() if k != "target"} | {"target_id": tid}
        if step.do.kind.value == "strike_target":  # decision 0033: safety rules 2·3 see where
            tg = next((t for t in targets if t.id == tid), None)
            params |= {"target": tg.pos.model_dump()} if tg else {}
    spot = next((t.last_seen_pos or t.pos for t in targets if t.id == st.target_id), None)
    kind, params = route_command(step.do, spec.domain, st.pos, params, spot)  # 0055: focus orbit
    prov = Provenance(source="role_step", role_id=role.id, step_id=step.id, issued_ms=t_ms,
                      decision_id=st.decision_id)  # fmt: skip
    cmd = None if kind is None else Command(id=f"cmd-{st.id}-{t_ms}", vehicle_id=st.id,
                                            kind=kind, params=params, provenance=prov)  # fmt: skip
    if step.do.kind.value == "return_home":
        upd["status"] = VehicleStatus.returning
    rep = None
    if step.report:
        seen = upd.get("target_id") or next((tg.id for tg in targets if st.id in tg.seen_by), None)
        rep = Report(id=rid, t_ms=t_ms, kind="target_detected", vehicle_id=st.id, target_id=seen,
                     text=step.report.text + _basis(st, targets, seen),
                     choices=step.report.choices)  # fmt: skip
        if step.report.choices:
            upd["pending_report_id"] = rid
    return st.model_copy(update=upd), cmd, rep
