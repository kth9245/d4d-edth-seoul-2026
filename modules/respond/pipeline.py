"""respond pipeline. No logic here."""

from contracts.models import Assessment, Response
from modules.respond.actions.recommend_response import recommend_response


def respond(assessments: list[Assessment]) -> list[Response]:
    return [recommend_response(a) for a in assessments]
