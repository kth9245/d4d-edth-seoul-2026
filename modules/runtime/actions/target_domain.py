"""RT-15 target_domain: 발견한 표적이 공중·지상·해상 중 어디인지(결정 0055). drone이면 공중, 아니면
지금 위치가 섬 안이면 지상, 밖이면 해상. 해안을 오가는 표적은 부를 때마다 지금 위치로 다시 판단한다.
SPEC: modules/runtime/SPEC.md#RT-15
"""

from collections.abc import Sequence
from typing import Literal

from contracts.models import Polygon, Target
from shared.land import inside

DOMAIN_LABEL = {"air": "공중", "ground": "지상", "sea": "해상"}


def target_domain(tg: Target, land: Sequence[Polygon]) -> Literal["air", "ground", "sea"]:
    if tg.kind.value == "drone":
        return "air"
    return "ground" if inside(tg.pos, land) else "sea"
