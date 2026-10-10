import type { EnemySpec, Role, VehicleSpec } from "../../contracts.gen";
import { startRoleOptions } from "../editor/startRoleOptions";

// The live board's partial switch (QA finding 2): the roles offered for the picked vehicle follow the editor's
// start role rule, the vehicle's domain and never an enemy's role. No vehicle picked yet offers nothing.
export function switchRoleOptions(roles: Role[], vehicles: VehicleSpec[], enemies: EnemySpec[], vehicleId: string): { id: string; name: string }[] {
  const v = vehicles.find((x) => x.id === vehicleId);
  return v ? startRoleOptions(roles, v, enemies.map((e) => e.role_id)) : [];
}
