"""RT-18 raid_cards: 멸공 단계별 카드의 후보 기체와 선택지(설계 2026-10-10-24h-raid-flow, 사용자 10/10).
격추/관찰(발견·추적 기체), 추적·집중 순찰·대체 순찰은 기체 1대씩 고르고 "대기"로 다음 단계(추적만 "전체 대기"도),
임무가 사라진 기체는 기지 복귀/현재 위치에서 대기. 추적 후보는 어떤 적도 보지 않은 기체, 순찰 후보는 특정 임무 없는 기체.
SPEC: modules/runtime/SPEC.md#RT-18
"""

from collections.abc import Callable, Iterable, Sequence

from contracts.models import Choice, Operation, Report, Target, VehicleSpec, VehicleState

STRIKE, HOME, HOLD = "strike", "go_home", "standby"
TRACK_ROLE = {
    "air": "watch",
    "sea": "track_sea",
    "ground": "track_ground",
}  # own vehicle domain -> role
LIVE = ("ready", "active")
ASK = {"act": "① {v} 행동 선택", "tact": "②' {v} 행동 선택", "track": "② 추적할 아군 선택",
       "focus": "③ 발견 지점 집중 순찰 아군 선택", "cover": "④ 발견 지점 대체 순찰 아군 선택"}  # fmt: skip
NAME = {"track": "추적", "focus": "집중 순찰", "cover": "대체 순찰"}
VERB = {"track": "추적", "focus": "발견 지점 집중 순찰", "cover": "발견 지점 대체 순찰"}


def act_choices(v: str, tid: str) -> list[Choice]:
    return [Choice(id=f"strike_{v}", label=f"{v} → 공격으로 격추({tid})", role_by_vehicle={v: STRIKE},
                   target_by_vehicle={v: tid}),
            Choice(id=f"observe_{v}", label=f"{v} → 추적·관찰 계속({tid})")]  # fmt: skip


def trackers(states: Iterable[VehicleState], specs: dict[str, VehicleSpec], targets: Sequence[Target],
             exclude: set[str], dom: str | None = None) -> list[VehicleState]:  # fmt: skip
    seers = {v for t in targets for v in t.seen_by}
    return [s for s in states if s.status.value in LIVE and s.target_id is None and s.pending_report_id is None
            and s.id not in exclude and s.id not in seers and s.id in specs
            and (dom is None or specs[s.id].domain.value in ("air", dom))]  # fmt: skip


def free(states: Iterable[VehicleState], op: Operation, exclude: set[str]) -> list[VehicleState]:
    routine = (None, HOLD, *op.rotation_roles)
    return [s for s in states if s.status.value in LIVE and s.target_id is None and s.role_id in routine
            and s.id not in exclude]  # fmt: skip


def pick_choices(stage: str, cands: Iterable[VehicleState], tid: str,
                 role_of: Callable[[VehicleState], str]) -> list[Choice]:  # fmt: skip
    out = [Choice(id=f"{stage}_{s.id}", label=f"{s.id} → {tid} {VERB[stage]}", role_by_vehicle={s.id: role_of(s)},
                  target_by_vehicle={s.id: tid}) for s in cands]  # fmt: skip
    out.append(Choice(id=f"{stage}_skip", label="대기"))
    return [*out, Choice(id="track_allstay", label="전체 대기")] if stage == "track" else out


def idle_choices(v: str) -> list[Choice]:
    return [Choice(id=f"home_{v}", label=f"{v} → 기지 복귀", role_by_vehicle={v: HOME}),
            Choice(id=f"hold_{v}", label=f"{v} → 현재 위치에서 대기", role_by_vehicle={v: HOLD})]  # fmt: skip


def summary(tid: str, finder: str, struck: bool, picks: dict[str, list[str]], t_ms: int) -> Report:
    parts = [
        f"{finder} {'격추' if struck else '관찰'}",
        *(f"{NAME[s]} {', '.join(vs)}" for s, vs in picks.items() if vs),
    ]
    return Report(id=f"raid-{tid}-done", t_ms=t_ms, kind="target_neutralized", vehicle_id=finder, target_id=tid,
                  text=f"{tid} 대응: " + " · ".join(parts))  # fmt: skip
