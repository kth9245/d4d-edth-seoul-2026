"""REST request and response bodies. The server stamps id and t_ms (decision 0017)."""

from pydantic import BaseModel

from .world import GeoPoint


class DecisionIn(BaseModel):  # POST /decisions
    report_id: str
    choice_id: str


class DirectIn(BaseModel):  # POST /direct
    vehicle_id: str
    target: GeoPoint


class SwitchIn(BaseModel):  # POST /injections: a switch button id, or vehicles -> plays
    switch_id: str | None = None
    play_by_vehicle: dict[str, str] = {}
    target_by_vehicle: dict[str, str] = {}  # pointing at a target on the map (decision 0048)
    approve: bool = False  # the press is the approval, no pending card (decision 0049)


class DraftIn(BaseModel):  # POST /plays/draft
    text: str


class Accepted(BaseModel):  # reply to an operator input; it applies on the next tick
    id: str
    t_ms: int


class ScenarioInfo(BaseModel):  # GET /scenarios: an operation the gateway can run (decision 0042)
    id: str  # Scenario.id
    name: str  # Operation.name
    purpose: str = ""  # Operation.purpose
    active: bool = False  # the running operation
