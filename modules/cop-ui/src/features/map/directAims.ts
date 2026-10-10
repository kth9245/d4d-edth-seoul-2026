import type { Frame, GeoPoint } from "../../contracts.gen";

export type Aim = { label: string; lat: number; lon: number };
// The order the operator just sent, with the frame time it was sent at.
export type PendingAim = Aim & { sentAt: number };

// Direct-control crosses on the map. The frame is the truth: a vehicle off its play step that is executing an
// operator_direct move gets a cross at that move's target, so a blocked order never shows one, an alternative
// moves it, and arrival (back on the step) drops it. The order just sent shows until a newer frame arrives,
// because a paused run has not taken it yet.
export function directAims(frame: Frame | null, pending: PendingAim | null): Aim[] {
  const fresh = pending && (!frame || frame.t_ms <= pending.sentAt) ? pending : null;
  const fromFrame = (frame?.vehicles ?? []).flatMap((v) => {
    const cmd = v.active?.command;
    const target = cmd?.params?.target as GeoPoint | undefined;
    if (v.step_id || cmd?.provenance?.source !== "operator_direct" || !target) return [];
    return [{ label: v.id, lat: target.lat, lon: target.lon }];
  });
  const aims = fromFrame.filter((a) => a.label !== fresh?.label);
  return fresh ? [...aims, { label: fresh.label, lat: fresh.lat, lon: fresh.lon }] : aims;
}
