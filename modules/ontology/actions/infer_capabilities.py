"""ONT-03 infer_capabilities: 행동 enum 순서로 explain_capability가 허용한 것만
SPEC: modules/ontology/SPEC.md#ONT-03
"""

from contracts.models import ActionKind, Ontology
from modules.ontology.actions.explain_capability import explain_capability


def infer_capabilities(kind: str, onto: Ontology) -> list[ActionKind]:
    return [a for a in ActionKind if explain_capability(kind, a, onto).allowed]
