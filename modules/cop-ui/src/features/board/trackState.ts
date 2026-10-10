import type { GeoPoint, Target } from "../../contracts.gen";

export type TrackKind = "seen" | "rf" | "lost" | "never" | "gone";
export type LostDir = "still" | "approach" | "away";
export interface Track { k: TrackKind; pos: GeoPoint; est?: GeoPoint; agoMs?: number; dir?: LostDir; speed?: number }

const M_PER_DEG = 111_320;
const STILL_MPS = 0.3;

// What our side knows about a target (decision 0047): seen now, RF only, lost (drawn where it was last seen,
// moving on at the velocity it had then), never detected, or struck. A moving lost target heading toward the
// expected landing point is "approach", away from it "away"; with no landing point it is assumed to approach.
export function trackState(t: Target, tMs: number, watch: GeoPoint | null): Track {
  if (t.neutralized_ms != null) return { k: "gone", pos: t.pos };
  if ((t.seen_by ?? []).length > 0) return { k: "seen", pos: t.pos };
  if (t.rf_detected) return { k: "rf", pos: t.pos };
  if (!t.first_seen_ms) return { k: "never", pos: t.pos };
  const pos = t.last_seen_pos ?? t.pos;
  const ve = t.last_seen_vel_east_mps ?? 0;
  const vn = t.last_seen_vel_north_mps ?? 0;
  const speed = Math.hypot(ve, vn);
  const agoMs = tMs - t.last_seen_ms;
  if (speed < STILL_MPS) return { k: "lost", pos, agoMs, dir: "still", speed };
  const mLon = M_PER_DEG * Math.cos((pos.lat * Math.PI) / 180);
  const sec = agoMs / 1000;
  const est = { lat: pos.lat + (vn * sec) / M_PER_DEG, lon: pos.lon + (ve * sec) / mLon };
  const away = !!watch && ve * (watch.lon - pos.lon) * mLon + vn * (watch.lat - pos.lat) * M_PER_DEG <= 0;
  return { k: "lost", pos, est, agoMs, dir: away ? "away" : "approach", speed };
}
