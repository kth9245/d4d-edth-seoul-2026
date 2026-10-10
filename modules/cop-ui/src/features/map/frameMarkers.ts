import type { Frame, TargetKind, VehicleStatus } from "../../contracts.gen";

export type BatteryLevel = "ok" | "mid" | "low";
export interface VehicleMarker {
  id: string; lon: number; lat: number; status: VehicleStatus; battery: BatteryLevel; label: string;
}

// The label right of a drone: a 4-block bar and the percent, red at 30% or less, yellow at 50% or less (user, 10/10).
function batteryLabel(id: string, pct: number): { battery: BatteryLevel; label: string } {
  const full = Math.min(4, Math.max(0, Math.ceil(pct / 25)));
  return {
    battery: pct <= 30 ? "low" : pct <= 50 ? "mid" : "ok",
    label: `${id} ${"▮".repeat(full)}${"▯".repeat(4 - full)} ${Math.round(pct)}%`,
  };
}
export interface TargetMarker {
  id: string; kind: TargetKind; lon: number; lat: number; seen: boolean; neutralized: boolean; rf: boolean; label: string;
}

// Frame → what the map draws as HTML markers (offline there are no glyphs, so labels cannot be map layers).
// A struck target (neutralized_ms, decision 0033) stays on the map as a grey X named "무력화" (Part1-20).
// A target whose emission our vehicles picked up (rf_detected) says "RF" and gets a ring; emitting is the
// simulator's truth and never reaches the screen (decision 0040).
export function frameMarkers(frame: Frame): { vehicles: VehicleMarker[]; targets: TargetMarker[] } {
  return {
    vehicles: frame.vehicles.map((v) => ({
      id: v.id, lon: v.pos.lon, lat: v.pos.lat, status: v.status, ...batteryLabel(v.id, v.battery_pct),
    })),
    targets: frame.targets.map((t) => {
      const neutralized = t.neutralized_ms != null;
      const rf = !neutralized && t.rf_detected === true;
      return {
        id: t.id, kind: t.kind, lon: t.pos.lon, lat: t.pos.lat, seen: (t.seen_by ?? []).length > 0,
        neutralized, rf, label: neutralized ? `${t.id} · 무력화` : rf ? `${t.id} · RF` : t.id,
      };
    }),
  };
}
