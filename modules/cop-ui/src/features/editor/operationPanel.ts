import type { Operation, VehicleSpec } from "../../contracts.gen";
import { kstTime } from "../cards/kstTime";
import { DOMAIN_LABEL } from "./describe";

// What the operation panel (Part3-14, display only) shows above the editor's overview.

export type VehicleRow = { id: string; name: string; domain: string; roleId: string | null; roleName: string | null; reserves: string[] };
export type SwitchRow = { id: string; label: string; moves: { vehicle: string; roleId: string; roleName: string | null }[] };

// One row per operation vehicle, in the operation's order: its kind, the role it starts with and its reserves.
export function vehicleRows(op: Operation, vehicles: VehicleSpec[], roleName: (id: string) => string | null): VehicleRow[] {
  return op.vehicle_ids.map((id) => {
    const spec = vehicles.find((v) => v.id === id);
    const roleId = op.assign?.[id] ?? null;
    return { id, name: spec?.name ?? id, domain: spec ? DOMAIN_LABEL[spec.domain] : "", roleId,
      roleName: roleId ? roleName(roleId) : null, reserves: op.reserve?.[id] ?? [] };
  });
}

// Each whole-operation switch button with the vehicle -> role moves it asks for.
export function switchRows(op: Operation, roleName: (id: string) => string | null): SwitchRow[] {
  return (op.switches ?? []).map((s) => ({
    id: s.id, label: s.label,
    moves: Object.entries(s.role_by_vehicle).map(([vehicle, roleId]) => ({ vehicle, roleId, roleName: roleName(roleId) })),
  }));
}

export function startText(started: number | null | undefined): string {
  return started == null ? "시작 시각 없음" : `${kstTime(started).slice(0, 5)} KST`;
}
