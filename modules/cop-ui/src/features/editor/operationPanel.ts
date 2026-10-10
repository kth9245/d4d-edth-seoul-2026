import type { Operation, VehicleSpec } from "../../contracts.gen";
import { kstTime } from "../cards/kstTime";
import { DOMAIN_LABEL } from "./describe";

// What the operation panel (Part3-14, display only) shows above the editor's overview.

export type VehicleRow = { id: string; name: string; domain: string; playId: string | null; playName: string | null; reserves: string[] };
export type SwitchRow = { id: string; label: string; moves: { vehicle: string; playId: string; playName: string | null }[] };

// One row per operation vehicle, in the operation's order: its kind, the play it starts with and its reserves.
export function vehicleRows(op: Operation, vehicles: VehicleSpec[], playName: (id: string) => string | null): VehicleRow[] {
  return op.vehicle_ids.map((id) => {
    const spec = vehicles.find((v) => v.id === id);
    const playId = op.assign?.[id] ?? null;
    return { id, name: spec?.name ?? id, domain: spec ? DOMAIN_LABEL[spec.domain] : "", playId,
      playName: playId ? playName(playId) : null, reserves: op.reserve?.[id] ?? [] };
  });
}

// Each whole-operation switch button with the vehicle -> play moves it asks for.
export function switchRows(op: Operation, playName: (id: string) => string | null): SwitchRow[] {
  return (op.switches ?? []).map((s) => ({
    id: s.id, label: s.label,
    moves: Object.entries(s.play_by_vehicle).map(([vehicle, playId]) => ({ vehicle, playId, playName: playName(playId) })),
  }));
}

export function startText(started: number | null | undefined): string {
  return started == null ? "시작 시각 없음" : `${kstTime(started).slice(0, 5)} KST`;
}
