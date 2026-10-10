import type { Frame, Report, Target, VehicleState } from "../../contracts.gen";
import type { Card } from "../cards/frameCards";

// Small Frames and cards for the board tests (Part1-32). Only tests import this file.
export const T0 = 1_791_634_000_000;
export const at = (lat: number, lon: number) => ({ lat, lon, alt_m: 0 });

export function mkTarget(p: Partial<Target> & { id: string }): Target {
  return { kind: "boat", pos: at(37.99, 124.72), vel_east_mps: 0, vel_north_mps: 0, first_seen_ms: 0,
    last_seen_ms: 0, seen_by: [], threat: 0, threat_reasons: [], ...p };
}
export function mkVehicle(p: Partial<VehicleState> & { id: string }): VehicleState {
  return { t_ms: T0, pos: at(37.95, 124.7), heading_deg: 0, battery_pct: 100, status: "ready", ...p };
}
export function mkReport(p: Partial<Report> & { id: string }): Report {
  return { t_ms: T0, kind: "target_detected", text: "보고", choices: [], ...p };
}
export function mkFrame(p: Partial<Frame> = {}): Frame {
  return { t_ms: T0, run: { status: "paused", speed: 1 }, vehicles: [], targets: [], reports: [], assignments: [],
    blocks: [], injections: [], metrics: {}, ...p };
}
export function mkCard(p: Partial<Card> & { id: string }): Card {
  return { source: "report", kind: "target_detected", vehicle: null, t_ms: T0, time: "21:00:00", text: "",
    choices: [], done: null, ...p };
}
