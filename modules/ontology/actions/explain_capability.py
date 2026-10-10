"""ONT-02 explain_capability: 체인을 아래부터 올라가 그 행동(또는 그 행동을 담은 묶음)을 주는 첫 종류에서 멈춤, 없으면 못 함(닫힌 세계)
SPEC: modules/ontology/SPEC.md#ONT-02
"""

from contracts.models import ActionKind, CapabilityReason, Ontology
from modules.ontology.actions.kind_chain import kind_chain


def explain_capability(kind: str, action: ActionKind, onto: Ontology) -> CapabilityReason:
    groups = {g.id: g.actions for g in onto.groups}
    path: list[str] = []
    for k in kind_chain(kind, onto):
        path.append(k.id)
        for entry in k.provides:
            if entry == action.value or action in groups.get(entry, []):
                return CapabilityReason(action=action, allowed=True, path=path, via=entry)
    return CapabilityReason(action=action, allowed=False, path=path)
