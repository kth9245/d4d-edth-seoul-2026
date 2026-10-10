"""ONT-04 fill_vehicle_kinds: ontology가 있으면 kind 있는 기체의 capabilities·kind_path를 계층에서 채운 새 Scenario
SPEC: modules/ontology/SPEC.md#ONT-04
"""

from contracts.models import Scenario, VehicleSpec
from modules.ontology.actions.infer_capabilities import infer_capabilities
from modules.ontology.actions.kind_chain import kind_chain


def fill_vehicle_kinds(sc: Scenario) -> Scenario:
    onto = sc.ontology
    if onto is None:
        return sc

    def fill(v: VehicleSpec) -> VehicleSpec:
        if v.kind is None:
            return v
        return v.model_copy(
            update={
                "capabilities": infer_capabilities(v.kind, onto),
                "kind_path": [k.label for k in kind_chain(v.kind, onto)],
            }
        )

    return sc.model_copy(update={"vehicles": [fill(v) for v in sc.vehicles]})
