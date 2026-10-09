"""GW-03 record_injections: 이번 틱의 전환 요청·승인·거부를 기록하고 카드를 만든다
새 요청(pending)은 injection_pending 카드, 승인·거부는 그 카드를 닫는다. 승인된 것을 돌려줘
틱 루프가 runtime.apply_injection을 부른다(결정 0015·0016).
SPEC: modules/gateway/SPEC.md#GW-03
"""

from contracts.models import Injection, Report


def record_injections(
    injections: list[Injection], reports: list[Report], requests: list[Injection], t_ms: int
) -> tuple[list[Injection], list[Report], list[Report], list[Injection]]:
    cards, approved = [], []
    for inj in requests:
        if inj.status == "pending":
            vid = next(iter(inj.play_by_vehicle), None)
            cards.append(Report(id=f"rep-{vid}-{t_ms}-i", t_ms=t_ms, kind="injection_pending",
                                vehicle_id=vid, text=f"전환 승인 대기: {inj.label}"))  # fmt: skip
        else:
            reports = [
                r.model_copy(update={"resolved_ms": t_ms})
                if r.kind == "injection_pending"
                and not r.resolved_ms
                and r.text.endswith(inj.label)
                else r
                for r in reports
            ]
            approved += [inj] if inj.status == "approved" else []
        injections = [i for i in injections if i.id != inj.id] + [inj]
    return injections, reports, cards, approved
