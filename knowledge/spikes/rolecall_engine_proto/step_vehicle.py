"""RT-01 step_vehicle (two layers, decisions 0015-0018; contracts/API.md §1, §3 step 5).

One vehicle, its own play. On entering a step: resolve the target, emit one Command for `do` (and the
report card if any). Afterwards the first true `on` exit moves to its go_step. A report with choices,
or target="operator", makes the vehicle wait (pending_report_id) until a Decision arrives.
expand_action below stands in for play.expand_action (Part3-7); its table is the 09 §6 draft.
"""
from contracts.models import (Action, Choice, Command, CommandKind, ConditionKind, Domain, Play,
                              Provenance, Report, Step, Target, VehicleSpec, VehicleState,
                              VehicleStatus)
from geo import dist_m

TARGET_ACTIONS = ("watch_target", "approach_target")
_K = CommandKind
_TABLE = {  # ActionKind -> (air, sea, ground)
    "move_to": (_K.move, _K.move, _K.move), "patrol_route": (_K.follow_route,) * 3,
    "search_area": (_K.zigzag, _K.zigzag, None), "return_home": (_K.return_home,) * 3,
    "watch_target": (_K.orbit, _K.keep_distance, None), "watch_point": (_K.orbit, _K.hold, _K.hold),
    "approach_target": (_K.keep_distance, _K.keep_distance, None), "relay_comms": (_K.relay,) * 3,
    "hold": (_K.hold,) * 3,
}


def expand_action(action: Action, domain: Domain) -> CommandKind | None:
    return _TABLE[action.kind.value][["air", "sea", "ground"].index(Domain(domain).value)]


def _cond_true(cond, st: VehicleState, targets: list[Target], t_ms: int) -> bool:
    if cond.kind == ConditionKind.target_found:
        return any(st.id in tg.seen_by for tg in targets)
    if cond.kind == ConditionKind.arrived:
        return st.waypoint_idx < 0  # sim sets -1 when the current command's destination is reached
    if cond.kind == ConditionKind.battery_below:
        return st.battery_pct < float(cond.params.get("pct", 30))
    return False  # time_elapsed / operator_choice / signal_received: not used by the demo plays


def _target_for(st: VehicleState, step: Step, targets: list[Target]) -> tuple[str | None, bool]:
    """(target id, operator must pick). target = "nearest" | "operator" | <fixed id> | absent.
    Only for target actions: move_to also has params.target, but there it is a GeoPoint destination."""
    if step.do.kind.value not in TARGET_ACTIONS:
        return None, False
    want = step.do.params.get("target")
    if want == "operator":
        return st.target_id, st.target_id is None
    if want == "nearest":
        best = min(targets, key=lambda t: dist_m(st.pos, t.pos), default=None)
        return (best.id if best else None), False
    return want, False


def _enter(st, spec, play, step, targets, t_ms):
    tid, ask = _target_for(st, step, targets)
    upd = {"entered_step": True, "waypoint_idx": 0, "target_id": tid}
    if ask:  # card only; apply_decision sets target_id and re-enters the step
        rep = Report(id=f"rep-{st.id}-{t_ms}", t_ms=t_ms, kind="target_select", vehicle_id=st.id,
                     text=f"추적할 표적 선택({st.id})",
                     choices=[Choice(id=t.id, label=f"{t.id} {t.kind.value}") for t in targets])
        return st.model_copy(update={**upd, "pending_report_id": rep.id}), None, rep
    kind = expand_action(step.do, spec.domain)
    params = dict(step.do.params)
    if step.do.kind.value in TARGET_ACTIONS:
        params = {k: v for k, v in params.items() if k != "target"} | ({"target_id": tid} if tid else {})
    prov = Provenance(source="play_step", play_id=play.id, step_id=step.id, issued_ms=t_ms)
    cmd = None if kind is None else Command(id=f"cmd-{st.id}-{t_ms}", vehicle_id=st.id, kind=kind,
                                            params=params, provenance=prov)
    if step.do.kind == "return_home":
        upd["status"] = VehicleStatus.returning
    rep = None
    if step.report:
        seen = next((tg.id for tg in targets if st.id in tg.seen_by), None)
        rep = Report(id=f"rep-{st.id}-{t_ms}", t_ms=t_ms, kind="target_detected", vehicle_id=st.id,
                     target_id=seen, text=step.report.text, choices=step.report.choices)
        if step.report.choices:
            upd["pending_report_id"] = rep.id
    return st.model_copy(update=upd), cmd, rep


def step_vehicle(st: VehicleState, spec: VehicleSpec, play: Play | None, targets: list[Target], t_ms: int
                 ) -> tuple[VehicleState, Command | None, Report | None]:
    if st.step_id is None and st.resume_step_id and st.waypoint_idx < 0:  # direct control arrived
        return st.model_copy(update={"step_id": st.resume_step_id, "entered_step": False,
                                     "resume_play_id": None, "resume_step_id": None}), None, None
    step = next((s for s in play.steps if s.id == st.step_id), None) if play else None
    if step is None or st.status.value not in ("ready", "active") or st.pending_report_id:
        return st, None, None
    if not st.entered_step:
        return _enter(st, spec, play, step, targets, t_ms)
    for ex in step.on:
        if _cond_true(ex.cond, st, targets, t_ms):
            return st.model_copy(update={"step_id": ex.go_step, "entered_step": False}), None, None
    return st, None, None
