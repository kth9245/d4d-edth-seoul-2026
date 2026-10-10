"""RT-13 route_command: 경로 비행 카드의 명령 종류와 params (결정 0044·0045)
상대 경로(offsets)는 지금 기체 위치를 기준점으로 실제 좌표 route로 바꾼다. 경로를 가진 move_to는
한 번만 따라가는 follow_route(loop false)로 내고, 끝점에서 sim이 도착을 낸다. 그 밖은 expand_action 그대로.
SPEC: modules/runtime/SPEC.md#RT-13
"""

from contracts.models import Action, CommandKind, Domain, GeoPoint
from modules.play import expand_action
from shared.geo import offset_latlon


def route_command(
    action: Action, domain: Domain, pos: GeoPoint, params: dict
) -> tuple[CommandKind | None, dict]:
    kind = expand_action(action, domain)
    if "offsets" in params:
        pts = [
            offset_latlon(pos.lat, pos.lon, o["east_m"], o["north_m"]) for o in params["offsets"]
        ]
        route = [GeoPoint(lat=lat, lon=lon).model_dump() for lat, lon in pts]
        params = {k: v for k, v in params.items() if k != "offsets"} | {"route": route}
    if kind is not None and action.kind.value == "move_to" and "route" in params:
        return CommandKind.follow_route, params | {"loop": False}
    return kind, params
