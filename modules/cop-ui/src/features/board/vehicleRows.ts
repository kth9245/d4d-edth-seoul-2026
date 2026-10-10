import type { Frame, VehicleSpec, VehicleStatus } from "../../contracts.gen";

export interface VehicleRow {
  id: string; status: VehicleStatus; doing: string; kind: string; target: string | null;
  striking: boolean; battery: number; low: boolean; waiting: boolean;
}

const KIND_KO: Record<string, string> = {
  recon_drone: "정찰 드론", armed_drone: "무장 드론", armed_usv: "무장 수상정", ground_robot: "지상 로봇",
};
const LOW_PCT = 35;

// Left column (Part1-32): what each of our vehicles does now. A returning or parked vehicle keeps target_id in
// the engine, so only a vehicle on a mission shows a target.
export function vehicleRows(f: Frame, playNames: Record<string, string>, specs: VehicleSpec[]): VehicleRow[] {
  return f.vehicles.map((v) => {
    const spec = specs.find((s) => s.id === v.id);
    const doing = v.status === "returning" ? "귀환 중" : v.status === "maintenance" ? "기지 정비"
      : v.play_id ? playNames[v.play_id] ?? v.play_id : "대기";
    const onMission = v.status === "active";
    return {
      id: v.id, status: v.status, doing,
      kind: (spec?.kind && KIND_KO[spec.kind]) || "",
      target: onMission ? v.target_id ?? null : null,
      striking: onMission && v.active?.command.kind === "strike",
      battery: Math.round(v.battery_pct), low: v.battery_pct < LOW_PCT,
      waiting: f.reports.some((r) => r.vehicle_id === v.id && !r.resolved_ms && (r.choices ?? []).length > 0),
    };
  });
}
