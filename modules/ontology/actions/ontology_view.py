"""ONT-05 ontology_view: 기체마다 행동 10개의 explain_capability와 계층(GET /ontology)
SPEC: modules/ontology/SPEC.md#ONT-05
"""

from contracts.models import ActionKind, OntologyView, Scenario, VehicleCapabilities
from modules.ontology.actions.explain_capability import explain_capability


def ontology_view(sc: Scenario) -> OntologyView:
    onto = sc.ontology
    vehicles = [
        VehicleCapabilities(
            vehicle_id=v.id,
            kind=v.kind,
            reasons=[explain_capability(v.kind, a, onto) for a in ActionKind],
        )
        for v in sc.vehicles
        if v.kind
    ]
    return OntologyView(ontology=onto, vehicles=vehicles)
