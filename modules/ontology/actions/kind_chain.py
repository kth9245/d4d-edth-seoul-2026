"""ONT-01 kind_chain: 종류에서 is_a를 따라 맨 위 종류까지
SPEC: modules/ontology/SPEC.md#ONT-01
"""

from contracts.models import Ontology, VehicleKind


def kind_chain(kind: str, onto: Ontology) -> list[VehicleKind]:
    by_id = {k.id: k for k in onto.kinds}
    chain = [by_id[kind]]
    while chain[-1].is_a is not None:
        chain.append(by_id[chain[-1].is_a])
    return chain
