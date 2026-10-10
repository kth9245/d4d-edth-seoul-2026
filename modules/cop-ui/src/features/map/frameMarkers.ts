import type { Frame, TargetKind, VehicleStatus } from "../../contracts.gen";

export interface VehicleMarker { id: string; lon: number; lat: number; status: VehicleStatus }
export interface TargetMarker { id: string; kind: TargetKind; lon: number; lat: number; seen: boolean }

// Frame → what the map draws as HTML markers (offline there are no glyphs, so labels cannot be map layers).
export function frameMarkers(frame: Frame): { vehicles: VehicleMarker[]; targets: TargetMarker[] } {
  return {
    vehicles: frame.vehicles.map((v) => ({ id: v.id, lon: v.pos.lon, lat: v.pos.lat, status: v.status })),
    targets: frame.targets.map((t) => ({
      id: t.id, kind: t.kind, lon: t.pos.lon, lat: t.pos.lat, seen: (t.seen_by ?? []).length > 0,
    })),
  };
}
