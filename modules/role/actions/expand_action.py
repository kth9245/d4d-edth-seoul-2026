"""PLY-07 expand_action: 행동(ActionKind)을 기체 영역(Domain)의 명령(CommandKind)으로, 없으면 None
표는 09 문서 6절 Part3-7 초안. None이면 그 기체는 그 행동을 못 한다.
SPEC: modules/role/SPEC.md#PLY-07
"""

from contracts.models import Action, CommandKind, Domain

K = CommandKind
TABLE: dict[str, tuple[CommandKind | None, ...]] = {  # (air, sea, ground)
    "move_to": (K.move, K.move, K.move),
    "patrol_route": (K.follow_route,) * 3,
    "search_area": (K.zigzag, K.zigzag, None),
    "return_home": (K.return_home,) * 3,
    "watch_target": (K.orbit, K.keep_distance, None),
    "watch_point": (K.orbit, K.hold, K.hold),
    "approach_target": (K.keep_distance, K.keep_distance, None),
    "relay_comms": (K.relay,) * 3,
    "hold": (K.hold,) * 3,
    "strike_target": (K.strike, K.strike, None),  # decision 0033
}
ORDER = ("air", "sea", "ground")


def expand_action(action: Action, domain: Domain) -> CommandKind | None:
    return TABLE[action.kind.value][ORDER.index(Domain(domain).value)]
