"""Ontology (decision 0038): vehicle kinds in an is-a hierarchy whose capabilities subkinds inherit,
the reasoning shown to the operator, and the graph of objects linked in a run."""

from typing import Literal

from pydantic import BaseModel

from .enums import ActionKind


class ActionGroup(BaseModel):  # e.g. watch: watch_target, watch_point, search_area
    id: str
    label: str
    actions: list[ActionKind]


class VehicleKind(BaseModel):
    id: str
    label: str
    is_a: str | None = None  # parent kind id; None = the root
    provides: list[str] = []  # ActionGroup ids or ActionKind values this kind adds


class Ontology(BaseModel):
    groups: list[ActionGroup]
    kinds: list[VehicleKind]


class CapabilityReason(BaseModel):
    action: ActionKind
    allowed: bool
    path: list[str]  # kind ids walked up from the vehicle's kind: to the giver, or to the root
    via: str | None = None  # the provides entry that matched


class VehicleCapabilities(BaseModel):
    vehicle_id: str
    kind: str
    reasons: list[CapabilityReason]  # one per ActionKind, in enum order


class OntologyView(BaseModel):  # GET /ontology
    ontology: Ontology
    vehicles: list[VehicleCapabilities]


class ObjectNode(BaseModel):
    id: str
    type: Literal["vehicle", "target", "report", "decision", "command", "block"]
    label: str
    t_ms: int | None = None


class ObjectLink(BaseModel):
    src: str
    dst: str
    rel: Literal["reported", "about", "answers", "from_decision", "sent_to", "aims_at", "blocked"]


class ObjectGraph(BaseModel):  # GET /graph?focus=
    focus: str
    nodes: list[ObjectNode]
    links: list[ObjectLink]
