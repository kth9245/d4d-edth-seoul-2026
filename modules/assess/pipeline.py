"""assess pipeline: classify -> score per track. No logic here."""

from contracts.models import Assessment, Track
from modules.assess.actions.classify_track import classify_track
from modules.assess.actions.score_threat import score_threat


def assess(tracks: list[Track], protected_lat: float, protected_lon: float) -> list[Assessment]:
    out = []
    for t in tracks:
        cls = classify_track(t)
        threat, reason = score_threat(t, cls, protected_lat, protected_lon)
        out.append(Assessment(track_id=t.id, object_class=cls, threat=threat, reason=reason))
    return out
