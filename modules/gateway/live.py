"""One operation in process memory: run state, queued operator inputs and the last Frame.

The app calls `period()` every 0.2 s. Inputs queued between periods go into the next tick
(contracts/API.md §5). Pause = speed 0, which keeps the last speed (decision 0026).
Depends only on `init(scenario) -> state` and `tick(state, inputs) -> (state, Frame)`.
"""

from collections.abc import Callable
from typing import Any

from contracts.models import (
    Accepted,
    Decision,
    DecisionIn,
    DirectControl,
    DirectIn,
    Frame,
    Injection,
    Operation,
    Play,
    PlayCheck,
    RunState,
    Scenario,
    SwitchIn,
    TickInputs,
)
from modules.gateway.actions.check_saved_play import check_saved_play


class Live:
    def __init__(
        self,
        scenario: Scenario,
        init: Callable[[Scenario], Any],
        tick: Callable[[Any, TickInputs], tuple[Any, Frame]],
    ):
        self.scenario, self._init, self._tick = scenario, init, tick
        self.reset()

    def reset(self) -> RunState:
        self.state = self._init(self.scenario)
        self.run = RunState(status="paused", speed=self.scenario.speed)
        self.inputs, self.injections, self._later = TickInputs(), {}, []
        self._n, self._due = {"dec": 0, "dir": 0, "inj": 0}, 0.0
        self.log: list[str] = []  # every log line since reset; connections read it by cursor
        self.epoch = getattr(self, "epoch", 0) + 1
        self._step()  # a first Frame so the map shows the start positions
        return self.run

    def _step(self) -> None:
        inputs, self.inputs, self._later = self.inputs, TickInputs(injections=self._later), []
        self.state, frame = self._tick(self.state, inputs)
        self.log += frame.log
        self.frame = frame.model_copy(update={"run": self.run})

    def frame_for(self, cursor: tuple[int, int] | None) -> tuple[Frame, tuple[int, int]]:
        """The last Frame with the log lines this connection has not seen yet (all ticks)."""
        start = cursor[1] if cursor and cursor[0] == self.epoch else 0
        frame = self.frame.model_copy(update={"log": self.log[start:]})
        return frame, (self.epoch, len(self.log))

    def period(self) -> None:
        if self.run.status != "running":
            return
        self._due += self.run.speed
        while self._due >= 1:
            self._due -= 1
            self._step()

    def set_speed(self, speed: float) -> RunState:
        if speed == 0:
            self.run = RunState(status="paused", speed=self.run.speed)
        else:
            self.run = RunState(status="running", speed=speed)
        self.frame = self.frame.model_copy(update={"run": self.run})
        return self.run

    def jump(self, offset_ms: int) -> RunState:
        end = self.scenario.operation.started_ms + offset_ms
        while self.frame.t_ms < end:
            self._step()
        return self.run

    def set_operation(self, op: Operation) -> Operation:
        self.scenario = self.scenario.model_copy(update={"operation": op})
        self.reset()
        return op

    def check_play(self, play: Play) -> PlayCheck:
        return check_saved_play(play, self.scenario)

    def save_play(self, play: Play) -> PlayCheck:
        """Saved (in memory, same id replaced in place) only when the check passes; then reset like
        set_operation, so the next run start uses it. A failing play changes nothing."""
        chk = self.check_play(play)
        if chk.ok:
            plays = [play if p.id == play.id else p for p in self.scenario.plays]
            if all(p.id != play.id for p in self.scenario.plays):
                plays.append(play)
            self.scenario = self.scenario.model_copy(update={"plays": plays})
            self.reset()
        return chk

    def _next(self, kind: str) -> tuple[str, int]:
        self._n[kind] += 1
        return f"{kind}-{self._n[kind]}", self.frame.t_ms + self.scenario.tick_ms

    def decide(self, body: DecisionIn) -> Accepted:
        id_, t = self._next("dec")
        self.inputs.decisions.append(Decision(id=id_, t_ms=t, **body.model_dump()))
        return Accepted(id=id_, t_ms=t)

    def direct(self, body: DirectIn) -> Accepted:
        id_, t = self._next("dir")
        self.inputs.direct.append(DirectControl(id=id_, t_ms=t, **body.model_dump()))
        return Accepted(id=id_, t_ms=t)

    def request_switch(self, body: SwitchIn) -> Injection:
        id_, t = self._next("inj")
        if body.switch_id:
            sw = next(s for s in self.scenario.operation.switches if s.id == body.switch_id)
            label, pbv = sw.label, sw.play_by_vehicle
        else:
            names = {p.id: p.name for p in self.scenario.plays}
            pbv = body.play_by_vehicle
            label = ", ".join(f"{names[p]}: {v}" for v, p in pbv.items())
        inj = Injection(id=id_, t_ms=t, label=label, play_by_vehicle=pbv, switch_id=body.switch_id)
        return self._queue(inj, self.inputs.injections)

    def settle_injection(self, inj_id: str, approve: bool) -> Injection:
        status = "approved" if approve else "rejected"
        inj = self.injections[inj_id].model_copy(update={"status": status})
        # the engine opens the pending card in the request's tick, so settle one tick later
        waiting = any(i.id == inj_id for i in self.inputs.injections)
        return self._queue(inj, self._later if waiting else self.inputs.injections)

    def _queue(self, inj: Injection, into: list[Injection]) -> Injection:
        self.injections[inj.id] = inj
        into.append(inj)
        return inj
