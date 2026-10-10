"""ontology (decision 0038): vehicle kinds in an is-a hierarchy; capabilities inferred along it."""

from modules.ontology.actions.explain_capability import explain_capability
from modules.ontology.actions.fill_vehicle_kinds import fill_vehicle_kinds
from modules.ontology.actions.infer_capabilities import infer_capabilities
from modules.ontology.actions.kind_chain import kind_chain
from modules.ontology.actions.ontology_view import ontology_view

__all__ = [
    "explain_capability",
    "fill_vehicle_kinds",
    "infer_capabilities",
    "kind_chain",
    "ontology_view",
]
