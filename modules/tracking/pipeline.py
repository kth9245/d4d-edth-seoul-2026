"""tracking pipeline: predict -> associate -> update -> initiate -> delete. No logic here."""

from contracts.models import Detection, Track
from modules.tracking.actions.associate_detections import associate_detections
from modules.tracking.actions.delete_stale_tracks import delete_stale_tracks
from modules.tracking.actions.initiate_tracks import initiate_tracks
from modules.tracking.actions.predict_tracks import predict_tracks
from modules.tracking.actions.update_tracks import update_tracks


def update(tracks: list[Track], detections: list[Detection], t_ms: int) -> list[Track]:
    predicted = predict_tracks(tracks, t_ms)
    assigned, free = associate_detections(predicted, detections)
    updated = update_tracks(predicted, assigned, t_ms)
    new_tracks = initiate_tracks(free, t_ms, existing_ids={t.id for t in updated})
    return delete_stale_tracks(updated + new_tracks, t_ms)
