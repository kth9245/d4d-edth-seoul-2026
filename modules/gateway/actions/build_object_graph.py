"""GW-11 build_object_graph: 객체 하나에서 링크를 따라 연결된 객체를 모은다(기체·다른 표적은 끝)
SPEC: modules/gateway/SPEC.md#GW-11
"""

from contracts.models import ObjectGraph, ObjectLink, ObjectNode
from modules.gateway.engine_state import EngineState

TARGET_KO = {"boat": "보트", "fast_boat": "고속정", "person": "사람", "unknown": "미상"}
CHECK_KO = {"no_provenance": "출처", "outside_zone": "구역", "battery_insufficient": "배터리"}
LEAF = ("vehicle", "target")  # a vehicle links to all its commands; never expand through it


def _all(es: EngineState) -> tuple[dict[str, ObjectNode], list[ObjectLink]]:
    n: dict[str, ObjectNode] = {}
    ln: list[tuple] = []
    for sp in es.specs.values():
        kind = (sp.kind_path or [sp.name])[0]
        n[sp.id] = ObjectNode(id=sp.id, type="vehicle", label=f"{sp.id} · {kind}")
    for tg in es.targets:
        gone = " · 무력화" if tg.neutralized_ms else ""
        label = f"{tg.id} · {TARGET_KO[tg.kind.value]}{gone}"
        n[tg.id] = ObjectNode(id=tg.id, type="target", label=label,
                              t_ms=tg.neutralized_ms or tg.first_seen_ms)  # fmt: skip
    reps = {r.id: r for r in es.reports}
    for r in es.reports:
        n[r.id] = ObjectNode(id=r.id, type="report", label=r.text, t_ms=r.t_ms)
        ln += [(r.vehicle_id, r.id, "reported"), (r.id, r.target_id, "about")]
    for d in es.decisions:
        choice = next(
            (c.label for c in reps[d.report_id].choices if c.id == d.choice_id), d.choice_id
        )
        n[d.id] = ObjectNode(id=d.id, type="decision", label=f"{d.id} '{choice}'", t_ms=d.t_ms)
        ln.append((d.id, d.report_id, "answers"))
    passed = {p.command.id: p for p in es.passed}
    for c in es.commands:
        p, prov = passed.get(c.id), c.provenance
        res = "·".join(CHECK_KO.get(x, x) for x in p.checks) + " 통과" if p else "차단"
        n[c.id] = ObjectNode(id=c.id, type="command", label=f"{c.kind.value} · {c.vehicle_id} · {res}",
                             t_ms=prov.issued_ms if prov else None)  # fmt: skip
        ln += [(c.id, c.vehicle_id, "sent_to"), (c.id, prov and prov.decision_id, "from_decision"),
               (c.id, c.params.get("target_id"), "aims_at")]  # fmt: skip
    for b in es.blocks:
        bid = f"blk-{b.command_id}"
        n[bid] = ObjectNode(id=bid, type="block", label=b.detail, t_ms=b.t_ms)
        ln.append((bid, b.command_id, "blocked"))
    return n, [ObjectLink(src=s, dst=d, rel=r) for s, d, r in ln if s in n and d in n]


def build_object_graph(es: EngineState, focus: str) -> ObjectGraph:
    n, links = _all(es)
    if focus not in n:
        raise ValueError(f"없는 객체: {focus}")
    near: dict[str, list[str]] = {}
    for lk in links:
        near.setdefault(lk.src, []).append(lk.dst)
        near.setdefault(lk.dst, []).append(lk.src)
    seen, todo = {focus}, [focus]
    while todo:
        cur = todo.pop()
        if cur != focus and n[cur].type in LEAF:
            continue
        for nxt in near.get(cur, []):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    nodes = [x for x in n.values() if x.id in seen]
    links = [lk for lk in links if lk.src in seen and lk.dst in seen]
    return ObjectGraph(focus=focus, nodes=nodes, links=links)
