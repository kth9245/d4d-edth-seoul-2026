"""RT-19 raid_next: 멸공 적 대응을 한 번에 질문 하나씩 띄운다(설계 2026-10-10-24h-raid-flow, 사용자 10/10).
흐름 상태는 따로 두지 않고 raid 카드(id raid-{적}-{단계}-{n})와 그 결정으로 매 틱 다시 계산한다. 열린 raid 질문이 있으면 없음.
적은 위협 높은 순, 같으면 처음 본 순. ① 발견 기체 격추/관찰(격추·무력화면 ⑤) → ② 추적 1대씩(고를 때마다 ②' 그 기체 격추/관찰,
전체 대기면 ②' 뒤 ⑤) → ③ 집중 순찰 → ④ 대체 순찰(발견 기체의 순찰 Role) → ⑤ 개요(선택지 없는 알림). 후보 없는 단계는 건너뜀.
SPEC: modules/runtime/SPEC.md#RT-19
"""

from contracts.models import Decision, Operation, Report, Role, Target, VehicleSpec, VehicleState
from modules.runtime.actions.raid_cards import TRACK_ROLE, act_choices, free, pick_choices, trackers

ASK = {"act": "① {v} 행동 선택", "tact": "②' {v} 행동 선택", "track": "② 추적할 아군 선택",
       "focus": "③ 발견 지점 집중 순찰 아군 선택", "cover": "④ 발견 지점 대체 순찰 아군 선택"}  # fmt: skip
NAME = {"track": "추적", "focus": "집중 순찰", "cover": "대체 순찰"}


def raid_next(reports: list[Report], decisions: list[Decision], states: list[VehicleState], targets: list[Target],
              op: Operation, roles: dict[str, Role], specs: dict[str, VehicleSpec], t_ms: int) -> Report | None:  # fmt: skip
    if "focus_orbit" not in roles:
        return None
    raid = {r.id: r for r in reports if r.id.startswith("raid-")}
    if any(r.choices and not r.resolved_ms for r in raid.values()):
        return None
    chose = {d.id: d.choice_id for d in decisions}
    pick = {rid: chose.get(r.decision_id or "", "") for rid, r in raid.items() if r.resolved_ms}
    live = [t for t in targets if t.seen_by or t.reported_by]
    for t in sorted(live, key=lambda t: (-t.threat, t.first_seen_ms)):
        if f"raid-{t.id}-done" not in raid:
            return _next(t, raid, pick, states, targets, op, specs, t_ms)
    return None


def _next(t, raid, pick, states, targets, op, specs, t_ms) -> Report:
    p, finder = f"raid-{t.id}-", (t.seen_by[0] if t.seen_by else t.reported_by)

    def card(stage, choices, v=finder, n=None):
        rid = p + stage + ("" if n is None else f"-{n}")
        return Report(id=rid, t_ms=t_ms, kind="target_detected", vehicle_id=v, target_id=t.id, choices=choices,
                      text=f"{t.id} 발견({finder}) · {ASK[stage.split('-')[0]].format(v=v)}")  # fmt: skip

    if p + "act" not in raid:
        return card("act", act_choices(finder, t.id))
    struck = pick[p + "act"].startswith("strike_")
    picks = {s: [] for s in NAME}
    allstay = struck or t.neutralized_ms is not None
    me = next((s for s in states if s.id == finder), None)
    cover = me.role_id if me and me.role_id in op.rotation_roles else None
    role_of = {"track": lambda s: TRACK_ROLE[specs[s.id].domain.value], "focus": lambda s: "focus_orbit",
               "cover": lambda s: cover}  # fmt: skip
    for i, stage in enumerate(NAME):
        if allstay or (stage == "cover" and not cover):
            break
        n, ended = 0, False
        while (rid := f"{p}{stage}-{n}") in raid:
            c = pick.get(rid, "")
            if not c.startswith(stage + "_") or c in (f"{stage}_skip", "track_allstay"):
                ended, allstay = True, c == "track_allstay"
                break
            picks[stage].append(c[len(stage) + 1 :])
            n += 1
        for v in picks["track"] if stage == "track" else []:
            if f"{p}tact-{v}" not in raid:
                return card(f"tact-{v}", act_choices(v, t.id), v)
        later = any(k.startswith(f"{p}{s}-") for s in list(NAME)[i + 1 :] for k in raid)
        taken = {finder, *(v for vs in picks.values() for v in vs)}
        cands = (
            trackers(states, specs, targets, taken) if stage == "track" else free(states, op, taken)
        )
        if not (ended or later or allstay) and cands:
            return card(stage, pick_choices(stage, cands, t.id, role_of[stage]), n=n)
    parts = [f"{finder} {'격추' if struck else '관찰'}"]
    parts += [f"{NAME[s]} {', '.join(vs)}" for s, vs in picks.items() if vs]
    return Report(id=p + "done", t_ms=t_ms, kind="target_neutralized", vehicle_id=finder, target_id=t.id,
                  text=f"{t.id} 대응: " + " · ".join(parts))  # fmt: skip
