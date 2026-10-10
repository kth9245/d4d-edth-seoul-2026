"""RT-08 enter_step: step에 들어갈 때 한 번 — 표적을 정하고 do를 명령 하나로, report가 있으면 카드 한 장
표적(watch_target·approach_target의 params.target): "nearest" | "operator"(카드로 운용자가 고름) | 고정 id.
move_to의 params.target은 목적지 좌표라 손대지 않는다. 귀환 step이면 status=returning.
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
from modules.role import expand_action
from shared.geo import dist_m

TARGET_ACTIONS = ("watch_target", "approach_target")


def _target(st: VehicleState, step: Step, targets: list[Target]) -> tuple[str | None, bool]:
    want = step.do.params.get("target")
    if want == "operator":
        return st.target_id, st.target_id is None
    if want == "nearest":
        best = min(targets, key=lambda t: dist_m(st.pos, t.pos), default=None)
        return (best.id if best else None), False
    return want, False


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
    kind = expand_action(step.do, spec.domain)
    prov = Provenance(source="role_step", role_id=role.id, step_id=step.id, issued_ms=t_ms)
    cmd = None if kind is None else Command(id=f"cmd-{st.id}-{t_ms}", vehicle_id=st.id,
                                            kind=kind, params=params, provenance=prov)  # fmt: skip
    if step.do.kind.value == "return_home":
        upd["status"] = VehicleStatus.returning
    rep = None
    if step.report:
        seen = next((tg.id for tg in targets if st.id in tg.seen_by), None)
        rep = Report(id=rid, t_ms=t_ms, kind="target_detected", vehicle_id=st.id, target_id=seen,
                     text=step.report.text, choices=step.report.choices)  # fmt: skip
        if step.report.choices:
            upd["pending_report_id"] = rid
    return st.model_copy(update=upd), cmd, rep
