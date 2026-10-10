import type { Frame, TargetKind, VehicleStatus } from "../../contracts.gen";
import type { Track, TrackKind } from "../board/trackState";
import { mmss } from "../run/mmss";
import { clueTags } from "../board/clueTags";

export type BatteryLevel = "ok" | "mid" | "low";
export interface VehicleMarker {
  id: string; lon: number; lat: number; status: VehicleStatus; battery: BatteryLevel; label: string;
}

// The label right of a drone: the percent only (no block bar), red at 30% or less, yellow at 50% or less (user, 10/10).
function batteryLabel(id: string, pct: number): { battery: BatteryLevel; label: string } {
  return { battery: pct <= 30 ? "low" : pct <= 50 ? "mid" : "ok", label: `${id} ${Math.round(pct)}%` };
}
export interface TargetMarker {
  id: string; kind: TargetKind; lon: number; lat: number; seen: boolean; neutralized: boolean; rf: boolean; label: string;
  track: TrackKind; tone: "hi" | "mid" | "lo";
}

const DIR_KO = { still: "정지", approach: "접근 추정", away: "이탈(도주) 추정" } as const;
const tone = (r: number) => (r >= 0.7 ? "hi" : r >= 0.4 ? "mid" : "lo");

// Frame → what the map draws as HTML markers (offline there are no glyphs, so labels cannot be map layers).
// A struck target (neutralized_ms, decision 0033) stays on the map as a grey X named "무력화" (Part1-20).
// A target whose emission our vehicles picked up (rf_detected) says "RF" and gets a ring; emitting is the
// simulator's truth and never reaches the screen (decision 0040). With tracks (Part1-32, decision 0047) a target
// sits where our side knows it (a lost one at its last seen spot), says its risk, and a never-detected one says
// "미탐" without a risk.
export function frameMarkers(frame: Frame, tracks: Record<string, Track> = {}):
  { vehicles: VehicleMarker[]; targets: TargetMarker[] } {
  return {
    vehicles: frame.vehicles.map((v) => ({
      id: v.id, lon: v.pos.lon, lat: v.pos.lat, status: v.status, ...batteryLabel(v.id, v.battery_pct),
    })),
    targets: frame.targets.map((t) => {
      const tr = tracks[t.id];
      const neutralized = t.neutralized_ms != null;
      const seen = (t.seen_by ?? []).length > 0;
      const k: TrackKind = tr?.k ?? (neutralized ? "gone" : seen ? "seen" : "never");
      const tags = neutralized ? [] : clueTags(t);
      const rf = tags.length > 0;
      const r = (t.threat ?? 0) / 100;
      const score = r > 0 ? ` ${r.toFixed(2)}` : "";
      const label = neutralized ? `${t.id} · 무력화` : tr && k === "never" ? `${t.id} · 미탐`
        : tr && k === "lost" ? `${t.id}${score} · 놓침 ${mmss(tr.agoMs ?? 0)} · ${DIR_KO[tr.dir ?? "still"]}`
        : `${t.id}${score}${rf ? ` · ${tags.join("·")}` : ""}`;
      const pos = tr?.pos ?? t.pos;
      return { id: t.id, kind: t.kind, lon: pos.lon, lat: pos.lat, seen, neutralized, rf, label, track: k, tone: tone(r) };
    }),
  };
}
